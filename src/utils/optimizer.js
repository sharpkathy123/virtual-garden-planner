function isInsideBoundary(x, y, shape, dimensions) {
    if (shape === "Circle") return Math.sqrt(x*x + y*y) <= dimensions.radius_ft;
    if (shape === "Rectangle") return x >= -(dimensions.length_ft/2) && x <= (dimensions.length_ft/2) && y >= -(dimensions.width_ft/2) && y <= (dimensions.width_ft/2);
    return false;
}
export function generateUniversalEmitters(config) {
    const emitters = [];
    const spacingFt = config.irrigation.emitter_spacing_inches / 12;
    const { garden_shape, dimensions } = config;
    if (config.irrigation.type === "Grid Lines" && garden_shape === "Rectangle") {
        const rowSpacingFt = config.irrigation.row_spacing_inches / 12;
        let id = 0;
        for (let x = -(dimensions.length_ft/2) + 0.5; x <= (dimensions.length_ft/2) - 0.5; x += rowSpacingFt) {
            for (let y = -(dimensions.width_ft/2) + 0.5; y <= (dimensions.width_ft/2) - 0.5; y += spacingFt) {
                if (isInsideBoundary(x, y, garden_shape, dimensions)) emitters.push({ id: id++, x, y, distanceFromCenter: Math.sqrt(x*x + y*y) });
            }
        }
    }
    return emitters;
}
