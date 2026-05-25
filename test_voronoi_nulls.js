const turf = require('@turf/turf');
const fs = require('fs');

let html = fs.readFileSync('kinmen_isochrones.html', 'utf8');
let match = html.match(/const storesData = (\[[\s\S]*?\]);/);
const storesData = JSON.parse(match[1]);

const bbox = [118.150, 24.350, 118.500, 24.550];
const points = turf.featureCollection(storesData.map(s => turf.point([s.lng, s.lat], { store: s })));
const voronoiPolygons = turf.voronoi(points, { bbox: bbox });

let nullCount = 0;
voronoiPolygons.features.forEach((f, i) => {
    if (!f) {
        console.log(`Voronoi returned null for: ${points.features[i].properties.store.name}`);
        nullCount++;
    }
});
console.log("Total nulls:", nullCount);
