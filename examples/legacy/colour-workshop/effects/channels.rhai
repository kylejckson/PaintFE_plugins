for_each_pixel(|x, y, r, g, b, a| {
    let p = get_pixel(clamp(x + params.offset, 0, width()-1), y);
    [p[0], g, b, a]
});
