for_each_pixel(|x, y, r, g, b, a| {
    let pos = if params.vertical { x } else { y };
    if pos % params.spacing == 0 {
        let s = 1.0 - params.strength;
        [(r*s).to_int(), (g*s).to_int(), (b*s).to_int(), a]
    } else { [r,g,b,a] }
});
