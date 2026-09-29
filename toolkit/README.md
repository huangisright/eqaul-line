# equal-line toolkit — 等時線可及性分析工作流

由「請再給我一間便利商店吧——找出金門便利商店最佳拓點」科展系統泛用化而來。
設定檔驅動，換地區、換設施只改 `config.json`，一個指令跑完全部。

## 結構

    toolkit/
      config.json      設定檔（地區、設施、交通方式、時間、ORS 金鑰）
      pipeline.py      管線：抓 POI → 抓邊界 → 預計算等時線 → 產出網頁資料
      data/            管線產出的中繼資料與 API 快取（可續跑）
      site/index.html  分析網頁（Leaflet + Turf.js，讀 site/data.js）
      offline/         離線展場版（科展會場無網路用）：先在有網路處跑
                       `python offline/build_offline.py`，再把整個 offline/
                       資料夾帶去展場，開 index.html 即可
      教學指南.md       給學生的完整操作說明

## 快速開始

1. `config.json` 填入 openrouteservice 金鑰
2. `python pipeline.py`
3. 開啟 `site/index.html`

## 注意

- `config.json` 含金鑰後**不要** commit 或公開；`data/cache/` 也建議加入 `.gitignore`
- `site/` 資料夾本身不含金鑰，可安全發佈到 GitHub Pages（候選點模式由使用者自行貼金鑰）
- 資料來源：OpenStreetMap（Overpass、Nominatim）、openrouteservice；請遵守其使用條款並註明出處
