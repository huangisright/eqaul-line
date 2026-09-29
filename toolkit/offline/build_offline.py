# -*- coding: utf-8 -*-
"""
離線展場版建置腳本
==================
科展展場沒有網路，這支腳本要在【有網路的環境】先跑一次，把需要的東西全部抓下來：

    python build_offline.py            # 全部：複製資料 + 下載圖磚 + 候選點快取
    python build_offline.py tiles      # 只下載地圖圖磚
    python build_offline.py candidates # 只預計算候選點等時線
    python build_offline.py data       # 只複製最新的 site/data.js

跑完後整個 offline/ 資料夾複製到隨身碟，展場電腦用瀏覽器開 index.html 即可，
完全不需要網路。

圖磚下載說明：預設下載 zoom 10~16（16 已可看清街道）。請勿把 zoom 調太高
（每加一級數量 ×4），並保持預設的下載間隔，以遵守 OpenStreetMap 圖磚政策。
"""
import json
import math
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
TOOLKIT = HERE.parent
TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
USER_AGENT = "equal-line-toolkit-offline/1.0 (education; science fair; contact via config)"
ZOOMS = range(10, 17)      # 下載 zoom 10~16
PAD = 0.03                 # 邊界外多抓 0.03 度，避免地圖邊緣空白
ORS_URL = "https://api.openrouteservice.org/v2/isochrones/{profile}"


def read_data_js():
    src = TOOLKIT / "site" / "data.js"
    if not src.exists():
        raise SystemExit("找不到 site/data.js — 請先在 toolkit/ 跑 python pipeline.py")
    text = src.read_text(encoding="utf-8")
    return json.loads(re.sub(r"^const APP_DATA = ", "", text).rstrip("; \n"))


def get_bbox(app):
    """回傳 (南, 西, 北, 東)。優先用行政區邊界，否則用所有點位。"""
    lats, lngs = [], []

    def walk(coords):
        if isinstance(coords[0], (int, float)):
            lngs.append(coords[0]); lats.append(coords[1])
        else:
            for c in coords:
                walk(c)

    if app.get("boundary"):
        for f in app["boundary"]["features"]:
            walk(f["geometry"]["coordinates"])
    else:
        for g in app["pois"]["groups"]:
            for s in g["stores"]:
                lats.append(s["lat"]); lngs.append(s["lng"])
    return min(lats) - PAD, min(lngs) - PAD, max(lats) + PAD, max(lngs) + PAD


def deg2tile(lat, lng, z):
    n = 2 ** z
    x = int((lng + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def step_data():
    app = read_data_js()
    (HERE / "data.js").write_text(
        "const APP_DATA = " + json.dumps(app, ensure_ascii=False) + ";", encoding="utf-8")
    print("已複製最新 data.js")
    return app


def step_tiles():
    app = read_data_js()
    s, w, n, e = get_bbox(app)
    jobs = []
    for z in ZOOMS:
        x0, y1 = deg2tile(s, w, z)   # 南西 → x 最小、y 最大
        x1, y0 = deg2tile(n, e, z)   # 北東 → x 最大、y 最小
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                jobs.append((z, x, y))
    todo = [(z, x, y) for z, x, y in jobs
            if not (HERE / "tiles" / str(z) / str(x) / f"{y}.png").exists()]
    print(f"圖磚共 {len(jobs)} 張，其中 {len(todo)} 張待下載（其餘已有快取）")
    for i, (z, x, y) in enumerate(todo, 1):
        out = HERE / "tiles" / str(z) / str(x) / f"{y}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(TILE_URL.format(z=z, x=x, y=y),
                                     headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                out.write_bytes(r.read())
        except Exception as exc:  # noqa: BLE001
            print(f"  下載失敗 z{z}/{x}/{y}: {exc}（可重跑續傳）")
        if i % 100 == 0 or i == len(todo):
            print(f"  進度 {i}/{len(todo)}")
        time.sleep(0.25)   # 禮貌性間隔，請勿移除
    print("圖磚完成")


def step_candidates():
    cand_file = HERE / "candidates.json"
    if not cand_file.exists():
        print("沒有 candidates.json，略過候選點預計算")
        print("（想在展場示範候選點，請仿照 candidates.example.json 建立此檔後重跑）")
        return
    cfg = json.load(open(TOOLKIT / "config.json", encoding="utf-8"))
    key = cfg.get("ors_api_key", "")
    if not key or "金鑰" in key:
        raise SystemExit("config.json 尚未填入 ors_api_key，無法預計算候選點")
    candidates = json.load(open(cand_file, encoding="utf-8"))
    cache = {}
    total = len(cfg["profiles"]) * len(cfg["ranges_minutes"]) * len(candidates)
    done = 0
    for profile in cfg["profiles"]:
        for minutes in cfg["ranges_minutes"]:
            sec = str(minutes * 60)
            for c in candidates:
                body = json.dumps({"locations": [[c["lng"], c["lat"]]],
                                   "range": [minutes * 60], "range_type": "time"})
                req = urllib.request.Request(
                    ORS_URL.format(profile=profile), data=body.encode(),
                    headers={"Authorization": key, "Content-Type": "application/json",
                             "User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=60) as r:
                    feat = json.loads(r.read())["features"][0]
                cache.setdefault(profile, {}).setdefault(sec, []).append(
                    {"name": c.get("name", "候選點"), "lat": c["lat"], "lng": c["lng"],
                     "feature": feat})
                done += 1
                print(f"  候選點 {done}/{total}")
                time.sleep(3.2)
    (HERE / "candidate_cache.js").write_text(
        "const CANDIDATE_CACHE = " + json.dumps(cache, ensure_ascii=False) + ";",
        encoding="utf-8")
    print("candidate_cache.js 完成")


STEPS = {"data": step_data, "tiles": step_tiles, "candidates": step_candidates}

if __name__ == "__main__":
    names = sys.argv[1:] or ["data", "tiles", "candidates"]
    for name in names:
        if name not in STEPS:
            raise SystemExit(f"未知步驟 {name}，可用：{', '.join(STEPS)}")
        STEPS[name]()
    print("離線包完成。把整個 offline/ 資料夾帶去展場即可。")
