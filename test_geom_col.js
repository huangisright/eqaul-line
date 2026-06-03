const turf = require('@turf/turf');
// Two polygons that intersect at a single point and a polygon
const poly1 = turf.polygon([[ [0,0],[10,0],[10,10],[0,10],[0,0] ]]);
const poly2 = turf.polygon([[ [10,10],[20,10],[20,20],[10,20],[10,10] ]]); // Intersects at point [10,10]

let intersection = turf.intersect(poly1, poly2);
console.log(intersection ? intersection.geometry.type : "null");
