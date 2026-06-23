import requests
import json

overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json];
(
  node["brand"~"7-ELEVEN|7-Eleven|全家|FamilyMart"](25.0400, 121.5000, 25.0480, 121.5100);
);
out body;
"""
response = requests.post(overpass_url, data={'data': overpass_query})
data = response.json()

stores = []
for element in data['elements']:
    if 'tags' in element and 'name' in element['tags']:
        name = element['tags']['name']
        brand = element['tags'].get('brand', name)
        lat = element['lat']
        lon = element['lon']
        stores.append({"brand": brand, "name": name, "latitude": lat, "longitude": lon})

print(json.dumps(stores, ensure_ascii=False, indent=2))
