const turf = require('@turf/turf');
const poly = turf.polygon([[[0,0], [0,10], [10,10], [10,0], [0,0]]]);
const multi = turf.multiPolygon([
  [[[2,2], [2,8], [8,8], [8,2], [2,2]]],
  [[[12,12], [12,18], [18,18], [18,12], [12,12]]]
]);
try {
  turf.intersect(poly, multi);
  console.log("Intersect multi worked!");
} catch(e) {
  console.log("Intersect multi failed:", e.message);
}
