const fs = require('fs');
let html = fs.readFileSync('kinmen_isochrones.html', 'utf8');
let match = html.match(/const storesData = (\[[\s\S]*?\]);/);
const storesData = JSON.parse(match[1]);

const chunkStartIndex = 2 * 5;
const chunkEndIndex = Math.min(chunkStartIndex + 5, storesData.length);
const chunk = storesData.slice(chunkStartIndex, chunkEndIndex);

const body = {
    locations: chunk.map(s => [s.lng, s.lat]),
    range: [900]
};

fetch('https://api.openrouteservice.org/v2/isochrones/foot-walking', {
    method: 'POST',
    headers: {
        'Authorization': '5b3ce3597851110001cf6248981d3f947ee14022a106f376f92634de',
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
})
.then(res => res.json())
.then(data => {
    if (data.features) {
        console.log(`Fetched ${data.features.length} features. Group indices:`, data.features.map(f => f.properties.group_index));
    } else {
        console.log("No features. Error:", data);
    }
});
