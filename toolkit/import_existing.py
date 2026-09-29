# -*- coding: utf-8 -*-
"""
從科展舊系統直接匯入資料（不需要網路、不需要 API 金鑰）
========================================================
原本的科展檔案裡已經有店家座標、金門邊界、預計算等時線，
這支腳本把它們轉成 toolkit 的格式，取代 pipeline.py 的前三步：

    python3 import_existing.py

跑完再執行 `python3 pipeline.py build` 即可產出網頁。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
LEGACY = HERE.parent          # 舊科展檔案所在資料夾
DATA = HERE / "data"

GROUP_INFO = {
    "711":        {"id": "711",    "label": "7-ELEVEN",   "color": "#e74c3c"},
    "FamilyMart": {"id": "family", "label": "全家便利商店", "color": "#27ae60"},
}


def read_js(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = [ln for ln in text.splitlines() if not ln.lstrip().startswith("//")]
    text = "\n".join(lines)
    m = re.match(r"^\s*(?:const|var|let)\s+\w+\s*=\s*(.*?);?\s*$", text, re.DOTALL)
    return json.loads(m.group(1) if m else text)


def main():
    DATA.mkdir(parents=True, exist_ok=True)

    # 1. 店家：從舊版 HTML 內嵌的 storesData 取出
    html = (LEGACY / "kinmen_isochrones.html").read_text(encoding="utf-8")
    stores = json.loads(re.search(r"const storesData = (\[.*?\]);", html, re.DOTALL).group(1))
    groups = []
    for typ, info in GROUP_INFO.items():
        members = [{"name": s["name"], "lat": s["lat"], "lng": s["lng"]}
                   for s in stores if s.get("type") == typ]
        groups.append({**info, "stores": members})
        print(f"{info['label']}: {len(members)} 家")
    (DATA / "pois.json").write_text(
        json.dumps({"groups": groups}, ensure_ascii=False), encoding="utf-8")

    # 2. 邊界
    boundary = read_js(LEGACY / "kinmen_boundary_fc.js")
    (DATA / "boundary.geojson").write_text(
        json.dumps(boundary, ensure_ascii=False), encoding="utf-8")
    print("邊界 OK")

    # 3. 等時線：舊格式 {mode:{sec:[FeatureCollection,...]}} → 攤平並依最近店家分組
    pre = read_js(LEGACY / "precomputed_data.js")

    def nearest_group(center):
        lng, lat = center
        best, best_d = None, 1e9
        for s in stores:
            d = abs(s["lat"] - lat) + abs(s["lng"] - lng)
            if d < best_d:
                best_d, best = d, s
        return GROUP_INFO[best["type"]]["id"]

    out = {}
    n = 0
    for mode, by_sec in pre.items():
        for sec, fcs in by_sec.items():
            for fc in fcs:
                if not fc:
                    continue
                for feat in fc.get("features", []):
                    gid = nearest_group(feat["properties"]["center"])
                    out.setdefault(mode, {}).setdefault(sec, {}).setdefault(gid, []).append(feat)
                    n += 1
    (DATA / "isochrones.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"等時線 OK：{n} 條，模式 {list(out)}，"
          f"時間 {sorted(int(s)//60 for s in out[next(iter(out))])} 分鐘")
    print("完成！接著執行：python3 pipeline.py build")


if __name__ == "__main__":
    main()
