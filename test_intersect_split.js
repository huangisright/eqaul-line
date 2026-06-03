const turf = require('@turf/turf');

const poly1 = turf.polygon([[
    [0, 0], [10, 0], [10, 10], [0, 10], [0, 0]
]]);

// A U-shaped polygon that will split poly1 into two
const poly2 = turf.polygon([[
    [2, -2], [8, -2], [8, 12], [6, 12], [6, 2], [4, 2], [4, 12], [2, 12], [2, -2]
]]);

let intersection = turf.intersect(poly1, poly2);
console.log("Intersection type:", intersection ? intersection.type : "null");
if (intersection && intersection.type === 'Feature') {
    console.log("Geometry type:", intersection.geometry.type);
} else if (intersection && intersection.type === 'FeatureCollection') {
    console.log("FeatureCollection!");
}
