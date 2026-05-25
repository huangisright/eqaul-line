const fs = require('fs');
const turf = require('@turf/turf');

// 讀取 precomputed_data.js 取得真實的 API 資料格式
let raw = fs.readFileSync('precomputed_data.js', 'utf8');
raw = raw.replace('const precomputedIsochrones = ', '');
raw = raw.replace(/;$/, '');
const data = JSON.parse(raw);

const features = data['foot-walking']['900']; // 15分鐘的資料，長度為 41

// 模擬前端的邏輯
let allFeatures = [];
for (let c = 0; c < features.length; c++) {
    const chunkData = features[c];
    if (chunkData && chunkData.features) {
        chunkData.features.forEach(f => {
            allFeatures.push(f);
        });
    }
}

console.log("Total features:", allFeatures.length);

let mergedIsochrones = allFeatures[0];
let successCount = 0;
let failCount = 0;
for (let i = 1; i < allFeatures.length; i++) {
    try {
        let fc = turf.featureCollection([mergedIsochrones, allFeatures[i]]);
        let res = turf.union(fc);
        if (res) {
            mergedIsochrones = res;
            successCount++;
        }
    } catch(e) {
        console.log("Union failed at index", i, e.message);
        failCount++;
    }
}

console.log(`Success: ${successCount}, Fail: ${failCount}`);
