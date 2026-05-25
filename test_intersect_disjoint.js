const turf = require('@turf/turf');
const poly = turf.polygon([[[0,0], [0,10], [10,10], [10,0], [0,0]]]);
const multi = turf.multiPolygon([
  [[[-2,-2], [-2,2], [2,2], [2,-2], [-2,-2]]],
  [[[8,8], [8,12], [12,12], [12,8], [8,8]]]
]);
const res = turf.intersect(poly, multi);
console.log(res.type);
console.log(res.geometry.type);
