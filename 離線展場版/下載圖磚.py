# -*- coding: utf-8 -*-
"""
下載金門離線地圖圖磚（請在【有網路】的電腦執行一次）
======================================================
    python3 下載圖磚.py

會把金門全島 zoom 10~16 的 OpenStreetMap 圖磚（約 5,300 張、80MB、
20 多分鐘）下載到本資料夾的 tiles/ 之下。中斷可重跑續傳。
沒下載圖磚也能用：地圖會以村里輪廓當底圖，只是沒有街道細節。
"""
import math
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
S, W, N, E = 24.35, 118.11, 24.59, 118.54   # 金門全島（含緩衝）
ZOOMS = range(10, 17)
UA = "kinmen-science-fair-offline/1.0 (education)"


def deg2tile(lat, lng, z):
    n = 2 ** z
    return (int((lng + 180) / 360 * n),
            int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n))


jobs = []
for z in ZOOMS:
    x0, y1 = deg2tile(S, W, z)
    x1, y0 = deg2tile(N, E, z)
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            jobs.append((z, x, y))

todo = [(z, x, y) for z, x, y in jobs
        if not (HERE / "tiles" / str(z) / str(x) / f"{y}.png").exists()]
print(f"共 {len(jobs)} 張，其中 {len(todo)} 張待下載")

for i, (z, x, y) in enumerate(todo, 1):
    out = HERE / "tiles" / str(z) / str(x) / f"{y}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(
        f"https://tile.openstreetmap.org/{z}/{x}/{y}.png", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            out.write_bytes(r.read())
    except Exception as e:  # noqa: BLE001
        print(f"  失敗 z{z}/{x}/{y}: {e}（可重跑續傳）")
    if i % 100 == 0 or i == len(todo):
        print(f"  進度 {i}/{len(todo)}")
    time.sleep(0.25)  # 禮貌性間隔，請勿移除（OSM 圖磚使用政策）

print("完成！整個資料夾即可離線使用。")
