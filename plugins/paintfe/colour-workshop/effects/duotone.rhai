for_each_pixel(|x, y, r, g, b, a| {
    let l = (r * 0.2126 + g * 0.7152 + b * 0.0722) / 255.0;
    let s = params.strength;
    [(r * (1.0-s) + (params.shadow[0] * (1.0-l) + params.light[0] * l) * s).to_int(),
     (g * (1.0-s) + (params.shadow[1] * (1.0-l) + params.light[1] * l) * s).to_int(),
     (b * (1.0-s) + (params.shadow[2] * (1.0-l) + params.light[2] * l) * s).to_int(), a]
});
