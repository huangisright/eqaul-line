const fs = require('fs');
let raw = fs.readFileSync('precomputed_data.js', 'utf8');
raw = raw.replace('const precomputedIsochrones = ', '');
raw = raw.replace(/;$/, '');
const data = JSON.parse(raw);
const preData = data['foot-walking']['900'];
console.log("Number of chunks:", preData.length);
for (let c = 0; c < preData.length; c++) {
    if (preData[c] && preData[c].features) {
        console.log(`Chunk ${c}: ${preData[c].features.length} features`);
    } else {
        console.log(`Chunk ${c}: no features`);
    }
}
