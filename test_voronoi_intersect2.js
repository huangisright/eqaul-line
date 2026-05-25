const fs = require('fs');
const turf = require('@turf/turf');

let rawPre = fs.readFileSync('precomputed_data.js', 'utf8').replace('const precomputedIsochrones = ', '').replace(/;$/, '');
const precomputedIsochrones = JSON.parse(rawPre);

let html = fs.readFileSync('kinmen_isochrones.html', 'utf8');
let match = html.match(/const storesData = (\[[\s\S]*?\]);/);
const storesData = JSON.parse(match[1]);

const timeSeconds = 900;
const selectedMode = 'driving-car';
const preData = precomputedIsochrones[selectedMode][timeSeconds];

let allFeatures = [];
for (let c = 0; c < preData.length; c++) {
    const chunkData = preData[c];
    if (chunkData && chunkData.features) {
        chunkData.features.forEach(f => {
            const globalIndex = c * 5 + f.properties.group_index;
            const store = storesData[globalIndex];
            if (store) {
                f.properties.store = store;
                allFeatures.push(f);
            }
        });
    }
}

const bbox = [118.150, 24.350, 118.500, 24.550];
const points = turf.featureCollection(storesData.map(s => turf.point([s.lng, s.lat], { store: s })));
const voronoiPolygons = turf.voronoi(points, { bbox: bbox });

const voronoiFeatures = [];
turf.featureEach(voronoiPolygons, function(currentVoronoi, currentIndex) {
    if (!currentVoronoi) return;
    const store = points.features[currentIndex].properties.store;
    const storeIsochrone = allFeatures.find(f => f.properties.store.name === store.name);
    
    if (storeIsochrone) {
        try {
            const intersection = turf.intersect(currentVoronoi, storeIsochrone);
            if (intersection) {
                intersection.properties = { store: store };
                voronoiFeatures.push(intersection);
            }
        } catch (e) {
            console.log("Error:", e.message);
        }
    }
});

fs.writeFileSync('test_voronoi_output.json', JSON.stringify({ type: "FeatureCollection", features: voronoiFeatures }, null, 2));
console.log("Wrote test_voronoi_output.json with length:", voronoiFeatures.length);
