const turf = require('@turf/turf');

const points = turf.featureCollection([
    turf.point([118.3, 24.4])
]);

const out = turf.voronoi(points, { bbox: [118.1, 24.3, 118.5, 24.5] });
console.log(out.features.length);
