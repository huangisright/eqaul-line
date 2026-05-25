const turf = require('@turf/turf');
const poly1 = turf.polygon([[[125, -15], [113, -22], [154, -27], [144, -15], [125, -15]]]);
const poly2 = turf.polygon([[[115, -15], [103, -22], [144, -27], [134, -15], [115, -15]]]);

console.log("poly1:", typeof poly1, poly1 !== undefined);
console.log("poly2:", typeof poly2, poly2 !== undefined);

try {
  let res = turf.union(poly1, poly2);
  console.log("turf.union(poly1, poly2) success!", res !== undefined);
} catch(e) {
  console.log("turf.union(poly1, poly2) FAILED:", e.message);
}

try {
  let res2 = turf.union(turf.featureCollection([poly1, poly2]));
  console.log("turf.union(fc) success!", res2 !== undefined);
} catch(e) {
  console.log("turf.union(fc) FAILED:", e.message);
}
