const turf = require('@turf/turf');
const poly1 = turf.polygon([[ [0,0],[10,0],[10,10],[0,10],[0,0] ]]);
// two separate squares that intersect poly1
const poly2 = turf.multiPolygon([
    [[ [1,1],[3,1],[3,3],[1,3],[1,1] ]],
    [[ [7,7],[9,7],[9,9],[7,9],[7,7] ]]
]);
try {
    const res = turf.intersect(poly1, poly2);
    console.log(res.type, res.geometry.type);
} catch (e) {
    console.log("Error:", e.message);
}
