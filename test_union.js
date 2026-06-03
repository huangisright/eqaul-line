const fs = require('fs');
const turf = require('@turf/turf');

// 讀取 JS 檔案並擷取 JSON
let rawJs = fs.readFileSync('kinmen_villages.js', 'utf8');
let jsonStr = rawJs.replace('const kinmenVillagesData = ', '').replace(/;$/, '');
let kinmenVillagesData = JSON.parse(jsonStr);

console.time("Turf Union Time");
let landBoundary = kinmenVillagesData.features[0];
for(let i=1; i<kinmenVillagesData.features.length; i++) {
    try {
        landBoundary = turf.union(landBoundary, kinmenVillagesData.features[i]);
    } catch (e) {
        console.error("Union error at i=", i, e.message);
    }
}
console.timeEnd("Turf Union Time");
console.log("Land boundary generated successfully.");
