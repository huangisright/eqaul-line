const fs = require('fs');
const data = require('./test_voronoi_output.json');
let hasNaN = false;
data.features.forEach((f, i) => {
    let coordsStr = JSON.stringify(f.geometry.coordinates);
    if (coordsStr.includes('null') || coordsStr.includes('NaN')) {
        console.log(`Feature ${i} has invalid coordinates!`);
        hasNaN = true;
    }
});
if (!hasNaN) console.log('No NaN coordinates found.');
