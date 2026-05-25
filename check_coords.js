const fs = require('fs');

let html = fs.readFileSync('kinmen_isochrones.html', 'utf8');
let match = html.match(/const storesData = (\[[\s\S]*?\]);/);
const stores = JSON.parse(match[1]);

let seen = {};
stores.forEach((s, idx) => {
    let key = s.lat + ',' + s.lng;
    if (seen[key]) {
        console.log(`Duplicate coordinates found for ${s.name} and ${seen[key]}: ${key}`);
    }
    seen[key] = s.name;
});
console.log("Check complete.");
