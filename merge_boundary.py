import json
import os
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

with open("kinmen_towns.js", "r", encoding="utf-8") as f:
    content = f.read()

# Extract json string
json_str = content.replace("const kinmenTownsData = ", "").strip()
if json_str.endswith(";"):
    json_str = json_str[:-1]

data = json.loads(json_str)

polygons = []
for feature in data.get("features", []):
    geom = shape(feature["geometry"])
    if geom.is_valid:
        polygons.append(geom)

merged = unary_union(polygons)

output_feature = {
    "type": "Feature",
    "properties": {"name": "Kinmen Land Boundary"},
    "geometry": mapping(merged)
}

with open("kinmen_boundary.js", "w", encoding="utf-8") as f:
    f.write("const kinmenBoundaryData = ")
    json.dump(output_feature, f, ensure_ascii=False)
    f.write(";")

print("Merged Kinmen boundary from kinmen_towns.js saved to kinmen_boundary.js")
