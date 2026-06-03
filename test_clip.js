const fs = require('fs');
const turf = require('@turf/turf');

// Load kinmenBoundaryFC
eval(fs.readFileSync('kinmen_boundary_fc.js', 'utf8'));

function clipToKinmenBoundary(inputFeature) {
    if (typeof kinmenBoundaryFC === 'undefined') return inputFeature;
    let clippedResult = null;
    
    kinmenBoundaryFC.features.forEach(islandPoly => {
        try {
            const intersection = turf.intersect(inputFeature, islandPoly);
            if (intersection) {
                if (clippedResult === null) {
                    clippedResult = intersection;
                } else {
                    try {
                        clippedResult = turf.union(clippedResult, intersection);
                    } catch(e) {
                        console.log("Union error:", e.message);
                    }
                }
            }
        } catch(e) {
            console.log("Intersect error:", e.message);
        }
    });
    
    return clippedResult || inputFeature;
}

const fakeVoronoi = turf.polygon([[
    [118.2, 24.3],
    [118.4, 24.3],
    [118.4, 24.5],
    [118.2, 24.5],
    [118.2, 24.3]
]]);

try {
    let result = clipToKinmenBoundary(fakeVoronoi);
    console.log("Result type:", result.type);
    if (result.type === 'Feature') console.log("Geometry type:", result.geometry.type);
} catch (e) {
    console.log("Main error:", e);
}
