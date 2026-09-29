# -*- coding: utf-8 -*-
"""
可及性分析工作流（等時線分析 toolkit）
=======================================
一個指令從「抓資料」到「產出網頁」全部跑完：

    python pipeline.py            # 依序執行全部步驟
    python pipeline.py pois       # 只抓 POI（Overpass / OpenStreetMap）
    python pipeline.py boundary   # 只抓行政區邊界（Nominatim）
    python pipeline.py isochrones # 只預計算等時線（openrouteservice，可中斷續跑）
    python pipeline.py build      # 只重新組裝 site/data.js

只用 Python 標準函式庫，不需 pip install。
設定都在 config.json，換一個地區 / 換一種設施只要改設定檔。
"""
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "data"
CACHE = DATA / "cache"
SITE = BASE / "site"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
ORS_URL = "https://api.openrouteservice.org/v2/isochrones/{profile}"
USER_AGENT = "equal-line-toolkit/1.0 (education; science fair project)"

ORS_CHUNK = 5          # ORS 等時線一次最多 5 個點
ORS_SLEEP = 3.2        # 免費金鑰每分鐘 20 次 → 每次間隔 3 秒以上


# ---------- 共用工具 ----------

def load_config():
    with open(BASE / "config.json", encoding="utf-8") as f:
        return json.load(f)


def http_json(url, data=None, headers=None, timeout=60, retries=3):
    """送出 HTTP 請求並解析 JSON，失敗自動重試。"""
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    body = data.encode("utf-8") if isinstance(data, str) else data
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=h)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001
            last_err = e
            print(f"  請求失敗（第 {attempt + 1} 次）: {e}")
            time.sleep(5)
    raise RuntimeError(f"重試 {retries} 次仍失敗: {last_err}")


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    print(f"  已寫入 {path.relative_to(BASE)}")


# ---------- 步驟 1：抓 POI ----------

def step_pois(cfg):
    print("[1/4] 從 OpenStreetMap 抓取設施座標…")
    area = cfg["area"]
    groups_out = []
    for g in cfg["poi_groups"]:
        filt = g["overpass_filter"]
        if area.get("bbox"):
            s, w, n, e = area["bbox"]
            scope = f"({s},{w},{n},{e})"
            area_clause = ""
        else:
            name = area["admin_name"]
            area_clause = f'area["name"="{name}"]["boundary"="administrative"]->.a;'
            scope = "(area.a)"
        query = f"""[out:json][timeout:90];
{area_clause}
(
  node{filt}{scope};
  way{filt}{scope};
);
out center;"""
        print(f"  查詢「{g['label']}」…")
        result = http_json(OVERPASS_URL, data="data=" + urllib.parse.quote(query))
        stores = []
        for el in result.get("elements", []):
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lng = el.get("lon") or el.get("center", {}).get("lon")
            if lat is None or lng is None:
                continue
            stores.append({
                "name": el.get("tags", {}).get("name", g["label"]),
                "lat": lat,
                "lng": lng,
            })
        print(f"    找到 {len(stores)} 個點")
        groups_out.append({**{k: g[k] for k in ("id", "label", "color")}, "stores": stores})
        time.sleep(2)  # 對 Overpass 伺服器禮貌一點
    save_json(DATA / "pois.json", {"groups": groups_out})


# ---------- 步驟 2：抓行政區邊界 ----------

def step_boundary(cfg):
    print("[2/4] 從 Nominatim 抓取行政區邊界…")
    area = cfg["area"]
    if not area.get("admin_name"):
        print("  未設定 admin_name，略過（覆蓋率將以 bbox 計算）")
        return
    params = urllib.parse.urlencode({
        "q": area["admin_name"],
        "format": "json",
        "polygon_geojson": 1,
        "limit": 1,
    })
    result = http_json(f"{NOMINATIM_URL}?{params}")
    if not result:
        raise RuntimeError(f"Nominatim 找不到「{area['admin_name']}」")
    geom = result[0]["geojson"]
    fc = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"name": area["admin_name"]}, "geometry": geom}
    ]}
    save_json(DATA / "boundary.geojson", fc)


# ---------- 步驟 3：預計算等時線 ----------

def step_isochrones(cfg):
    print("[3/4] 呼叫 openrouteservice 預計算等時線…")
    key = cfg.get("ors_api_key", "")
    if not key or "金鑰" in key:
        raise RuntimeError("請先在 config.json 填入 ors_api_key（openrouteservice.org 免費註冊）")

    with open(DATA / "pois.json", encoding="utf-8") as f:
        pois = json.load(f)

    jobs = []  # (group_id, profile, seconds, locations)
    for g in pois["groups"]:
        locs = [[s["lng"], s["lat"]] for s in g["stores"]]
        chunks = [locs[i:i + ORS_CHUNK] for i in range(0, len(locs), ORS_CHUNK)]
        for profile in cfg["profiles"]:
            for minutes in cfg["ranges_minutes"]:
                for chunk in chunks:
                    jobs.append((g["id"], profile, minutes * 60, chunk))

    print(f"  共需 {len(jobs)} 次 API 請求（已完成的會用快取跳過）")
    CACHE.mkdir(parents=True, exist_ok=True)
    out = {}
    done = 0
    for gid, profile, sec, chunk in jobs:
        cache_key = hashlib.md5(
            json.dumps([profile, sec, chunk], sort_keys=True).encode()).hexdigest()
        cache_file = CACHE / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, encoding="utf-8") as f:
                result = json.load(f)
        else:
            result = http_json(
                ORS_URL.format(profile=profile),
                data=json.dumps({"locations": chunk, "range": [sec], "range_type": "time"}),
                headers={"Authorization": key, "Content-Type": "application/json"},
            )
            save_json(cache_file, result)
            time.sleep(ORS_SLEEP)
        out.setdefault(profile, {}).setdefault(str(sec), {}).setdefault(gid, [])
        out[profile][str(sec)][gid].extend(result.get("features", []))
        done += 1
        if done % 10 == 0 or done == len(jobs):
            print(f"  進度 {done}/{len(jobs)}")
    save_json(DATA / "isochrones.json", out)


# ---------- 步驟 4：組裝網頁資料 ----------

def _read_maybe_js(path):
    """讀取 .json 或 .js（自動略過開頭 // 註解、剝掉 `const xxx = ` 前綴與結尾分號）。"""
    text = Path(path).read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("//")]
    text = "\n".join(lines)
    m = re.match(r"^\s*(?:const|var|let)\s+\w+\s*=\s*(.*?);?\s*$", text, re.DOTALL)
    return json.loads(m.group(1) if m else text)


def step_build(cfg):
    print("[4/4] 組裝 site/data.js …")
    app = {
        "project_name": cfg["project_name"],
        "profiles": cfg["profiles"],
        "ranges_minutes": cfg["ranges_minutes"],
        "pois": json.load(open(DATA / "pois.json", encoding="utf-8")),
        "isochrones": json.load(open(DATA / "isochrones.json", encoding="utf-8")),
        "boundary": None,
        "population": None,
    }
    if (DATA / "boundary.geojson").exists():
        app["boundary"] = json.load(open(DATA / "boundary.geojson", encoding="utf-8"))
    pop = cfg.get("population") or {}
    if pop.get("geojson"):
        p = (BASE / pop["geojson"]).resolve()
        if p.exists():
            app["population"] = {
                "regions": _read_maybe_js(p),
                "weight_property": pop["weight_property"],
                "name_properties": pop.get("name_properties", []),
            }
            print(f"  已載入人口資料 {p.name}")
        else:
            print(f"  警告：找不到人口檔 {p}，略過人口計算")
    SITE.mkdir(parents=True, exist_ok=True)
    with open(SITE / "data.js", "w", encoding="utf-8") as f:
        f.write("const APP_DATA = ")
        json.dump(app, f, ensure_ascii=False)
        f.write(";")
    print(f"  完成！用瀏覽器開啟 {SITE / 'index.html'} 即可查看")


# ---------- 主程式 ----------

STEPS = {"pois": step_pois, "boundary": step_boundary,
         "isochrones": step_isochrones, "build": step_build}

if __name__ == "__main__":
    cfg = load_config()
    names = sys.argv[1:] or list(STEPS)
    for n in names:
        if n not in STEPS:
            print(f"未知步驟 {n}，可用：{', '.join(STEPS)}")
            sys.exit(1)
        STEPS[n](cfg)
    print("全部完成。")
