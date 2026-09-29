"""
補齊 precomputed_data.js 中缺漏的等時線區塊（只補缺的，不重算已有的）。

目前有 6 個「交通方式 × 時間」組合各缺 1 個區塊（5 家店），
所以網頁在這些組合下會想即時向 OpenRouteService 補抓。
補齊之後，公開網頁的所有預設組合都不需要金鑰。

用法（金鑰只放在環境變數，不寫進任何檔案）：
    export ORS_API_KEY=你的新金鑰
    python3 fill_missing_precomputed.py
"""
import json, os, re, shutil, sys, time, urllib.request

KEY = os.environ.get('ORS_API_KEY', '').strip()
if not KEY:
    raise SystemExit('請先設定環境變數 ORS_API_KEY，例如：export ORS_API_KEY=你的金鑰')

HTML = 'isochrones_beta.html'
DATA = 'precomputed_data.js'
PREFIX = 'const precomputedIsochrones = '
CHUNK = 5

html = open(HTML, encoding='utf-8').read()
stores = json.loads(re.search(r'const storesData = (\[.*?\]);', html, re.S).group(1))

raw = open(DATA, encoding='utf-8').read().strip()
assert raw.startswith(PREFIX), '無法辨識 precomputed_data.js 格式'
data = json.loads(raw[len(PREFIX):].rstrip(';'))

def fetch(mode, seconds, chunk):
    body = json.dumps({'locations': [[s['lng'], s['lat']] for s in chunk],
                       'range': [seconds], 'range_type': 'time'}).encode()
    req = urllib.request.Request(
        f'https://api.openrouteservice.org/v2/isochrones/{mode}', data=body,
        headers={'Authorization': KEY, 'Content-Type': 'application/json; charset=utf-8',
                 'Accept': 'application/geo+json, application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))

n_chunks = (len(stores) + CHUNK - 1) // CHUNK
filled = failed = 0
for mode, by_time in data.items():
    for t, arr in by_time.items():
        while len(arr) < n_chunks:
            arr.append(None)
        for c in range(n_chunks):
            if isinstance(arr[c], dict) and arr[c].get('features'):
                continue
            chunk = stores[c * CHUNK:(c + 1) * CHUNK]
            print(f'補抓 {mode} {int(t)//60} 分鐘 第 {c} 區塊（{len(chunk)} 家店）…', end=' ', flush=True)
            for attempt in range(3):
                try:
                    arr[c] = fetch(mode, int(t), chunk)
                    print('完成'); filled += 1
                    break
                except Exception as e:
                    print(f'失敗({e})', end=' ', flush=True)
                    time.sleep(4)
            else:
                print('放棄'); failed += 1
            time.sleep(3.2)  # 免費額度每分鐘 20 次

if filled:
    shutil.copy(DATA, DATA + '.bak')
    with open(DATA, 'w', encoding='utf-8') as f:
        f.write(PREFIX + json.dumps(data, ensure_ascii=False) + ';')
print(f'補齊 {filled} 個區塊，失敗 {failed} 個。' + ('（原檔備份為 precomputed_data.js.bak）' if filled else ''))
if filled and os.path.isdir('離線展場版'):
    print('提醒：離線展場版也用同一份資料，可執行 cp precomputed_data.js 離線展場版/')
