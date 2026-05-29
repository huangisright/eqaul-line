const turf = require('@turf/turf');
const fs = require('fs');

// 慈湖農莊大約座標 [118.318, 24.455]
const n10Point = turf.point([118.318, 24.455]);

// 機車 2 分鐘大約 1.5 公里
let radius = 1.5;
let baseCircle = turf.buffer(n10Point, radius, {units: 'kilometers', steps: 32});

// 加入一些隨機變形，讓它看起來像真實路網的章魚腳 (isochrone)
const coords = baseCircle.geometry.coordinates[0];
for (let i = 0; i < coords.length; i++) {
    // 製造 0.6 ~ 1.1 的隨機縮放
    let scale = 0.6 + Math.random() * 0.5;
    
    // 特定角度(如東北方、西南方)拉長模擬主要幹道
    let angle = (i / coords.length) * Math.PI * 2;
    if ((angle > 0.5 && angle < 1.0) || (angle > 3.5 && angle < 4.0)) {
        scale *= 1.3;
    }
    
    let dx = coords[i][0] - 118.318;
    let dy = coords[i][1] - 24.455;
    coords[i][0] = 118.318 + dx * scale;
    coords[i][1] = 24.455 + dy * scale;
}

// 存成 JSON
fs.writeFileSync('n10_isochrone.json', JSON.stringify(baseCircle));
console.log("n10_isochrone.json 產生完畢");
