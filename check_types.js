const fs = require('fs');
let html = fs.readFileSync('kinmen_isochrones.html', 'utf8');
let match = html.match(/const storesData = (\[[\s\S]*?\]);/);
const stores = JSON.parse(match[1]);
stores.forEach((s, i) => {
    if (s.type !== '711' && s.type !== 'FamilyMart') {
        console.log(`Store ${i} has weird type: ${s.type}`);
    }
});
console.log("Done checking types.");
