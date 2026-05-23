import time
import json
import urllib.request
import re
import sys

html_path = 'kinmen_isochrones.html'
js_out_path = 'precomputed_data.js'
ORS_API_KEY = 'eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImRjNGNkZGY1ZGMxZjQxYmJhNDY1OTcwOWUzZTRmOGMxIiwiaCI6Im11cm11cjY0In0='

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const storesData = (\[.*?\]);', html, re.DOTALL)
if not match:
    print("Cannot find storesData in html")
    exit(1)

storesData = json.loads(match.group(1))

chunkSize = 5
chunks = [storesData[i:i + chunkSize] for i in range(0, len(storesData), chunkSize)]

modes = ['foot-walking', 'cycling-regular', 'driving-car']
times_minutes = [5, 10, 15, 20, 25, 30]

precomputed = {}

total_requests = len(modes) * len(times_minutes) * len(chunks)
req_count = 0

print(f"Total requests to make: {total_requests}")
sys.stdout.flush()

for mode in modes:
    precomputed[mode] = {}
    for t_min in times_minutes:
        t_sec = t_min * 60
        precomputed[mode][str(t_sec)] = []
        for c_idx, chunk in enumerate(chunks):
            locations = [[s['lng'], s['lat']] for s in chunk]
            req_body = {
                "locations": locations,
                "range": [t_sec],
                "range_type": "time"
            }
            url = f"https://api.openrouteservice.org/v2/isochrones/{mode}"
            req = urllib.request.Request(url, data=json.dumps(req_body).encode('utf-8'), headers={
                'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
                'Authorization': ORS_API_KEY,
                'Content-Type': 'application/json; charset=utf-8',
                'User-Agent': 'Mozilla/5.0'
            })
            
            success = False
            retries = 3
            while not success and retries > 0:
                try:
                    with urllib.request.urlopen(req, timeout=15) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        precomputed[mode][str(t_sec)].append(data)
                        success = True
                except Exception as e:
                    print(f"Error fetching mode {mode} time {t_min} chunk {c_idx}: {e}")
                    sys.stdout.flush()
                    retries -= 1
                    time.sleep(3)
            
            if not success:
                print("Failed repeatedly!")
                precomputed[mode][str(t_sec)].append(None)

            req_count += 1
            if req_count % 5 == 0:
                print(f"Progress: {req_count}/{total_requests}")
                sys.stdout.flush()
            
            # Write partially so we don't lose progress if it crashes
            js_content = f"const precomputedIsochrones = {json.dumps(precomputed, ensure_ascii=False)};"
            with open(js_out_path, 'w', encoding='utf-8') as f:
                f.write(js_content)
                
            time.sleep(1.6)

print(f"Done. File saved to {js_out_path}")
