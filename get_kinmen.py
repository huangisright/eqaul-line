import urllib.request
import json
import os

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
area["name"="金門縣"]->.searchArea;
(
  relation["admin_level"="6"](area.searchArea);
);
out geom;
"""

try:
    req = urllib.request.Request(overpass_url, data=overpass_query.encode('utf-8'), headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
        with open("kinmen_boundary.json", "w") as f:
            json.dump(data, f)
        print("Success! Got boundary data. Size:", len(data.get('elements', [])))
except Exception as e:
    print("Error:", e)
