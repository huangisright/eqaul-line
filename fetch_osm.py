import requests
import json
import urllib.parse

# Overpass QL to get Kinmen county boundaries (OSM relation 5506013 for Kinmen)
# Or we can just get natural=coastline inside Kinmen
# Actually, the administrative boundary for Kinmen on OSM is relation 246522
query = """
[out:json];
area["name"="金門縣"]->.searchArea;
relation["boundary"="administrative"]["admin_level"="4"](area.searchArea);
out geom;
"""
url = "http://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query.strip())
resp = requests.get(url)
print("Response size:", len(resp.text))
