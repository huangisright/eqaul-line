const fs = require('fs');
const turf = require('@turf/turf');

// 讀取 precomputed_data.js
let rawPre = fs.readFileSync('precomputed_data.js', 'utf8');
rawPre = rawPre.replace('const precomputedIsochrones = ', '').replace(/;$/, '');
const precomputedIsochrones = JSON.parse(rawPre);

// 讀取 kinmen_isochrones.html 取得 storesData
let html = fs.readFileSync('kinmen_isochrones.html', 'utf8');
let match = html.match(/const storesData = (\[[\s\S]*?\]);/);
const storesData = JSON.parse(match[1]);

const timeSeconds = 900;
const selectedMode = 'foot-walking';
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
const points = turf.featureCollection(
    storesData.map(s => turf.point([s.lng, s.lat], { store: s }))
);
const voronoiPolygons = turf.voronoi(points, { bbox: bbox });

let nullCount = 0;
let successCount = 0;

turf.featureEach(voronoiPolygons, function(currentVoronoi, currentIndex) {
    if (!currentVoronoi) return;
    
    const store = points.features[currentIndex].properties.store;
    const storeIsochrone = allFeatures.find(f => f.properties.store.name === store.name);
    
    if (storeIsochrone) {
        try {
            const intersection = turf.intersect(currentVoronoi, storeIsochrone);
            if (intersection) {
                successCount++;
            } else {
                console.log(`Intersect returned null for ${store.name}`);
                nullCount++;
            }
        } catch (e) {
            console.log(`Intersect threw error for ${store.name}: ${e.message}`);
        }
    } else {
        console.log(`No isochrone found for ${store.name} (Probably chunk 2)`);
    }
});

console.log(`Success: ${successCount}, Null: ${nullCount}`);
