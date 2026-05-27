const turf = require('@turf/turf');
let pt = turf.point([118.3, 24.4]);
let buf = turf.buffer(pt, 1, {units: 'kilometers'});
let pts = turf.featureCollection([turf.point([118.3, 24.4]), turf.point([118.31, 24.41])]);
let voronoi = turf.voronoi(pts, {bbox: [118.150, 24.350, 118.500, 24.550]});
let currentVoronoi = voronoi.features[0];
let intersection = turf.intersect(currentVoronoi, buf);
console.log("Intersection type:", intersection ? intersection.geometry.type : "null");
