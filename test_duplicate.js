const turf = require('@turf/turf');

const points = turf.featureCollection([
    turf.point([118.3, 24.4]),
    turf.point([118.3, 24.4]),
    turf.point([118.4, 24.5])
]);

try {
    turf.voronoi(points, { bbox: [118.1, 24.3, 118.5, 24.5] });
    console.log("Success");
} catch(e) {
    console.log("Error:", e.message);
}
