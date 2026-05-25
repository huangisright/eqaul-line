const fs = require('fs');

let html = fs.readFileSync('kinmen_isochrones.html', 'utf8');
let match = html.match(/const storesData = (\[[\s\S]*?\]);/);
let stores = JSON.parse(match[1]);
console.log("HTML stores count:", stores.length);

