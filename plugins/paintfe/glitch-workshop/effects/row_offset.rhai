for_each_pixel(|x, y, r, g, b, a| {
    let band = y / params.band;
    let distance = params.distance;
    let shift = ((band * 97 + params.seed * 31) % (distance*2+1)) - distance;
    let sx = (x + shift + width()) % width();
    get_pixel(sx,y)
});
