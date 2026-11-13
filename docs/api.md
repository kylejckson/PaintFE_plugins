# Script API 1

An effect processes the active 8-bit raster layer and respects the current selection. Alpha is straight RGBA in the scripting API. Keep alpha unless changing it is intentional. Deep/high-precision and editable text layers require an explicit suitable raster target; they are not silently converted.

Useful functions include `width()`, `height()`, `get_pixel(x,y)`, `set_pixel(x,y,r,g,b,a)`, `for_each_pixel(|x,y,r,g,b,a| { [r,g,b,a] })`, `map_channels`, `apply_hsl`, `apply_blur`, `apply_invert`, `rand_int`, `rand_float`, `print_line` and `progress`.

See the original effects for complete examples. A fixed host seed makes repeated previews stable. An explicit seed parameter is useful when the user should choose a different result.

API 1 plugin effects cannot change document dimensions. Canvas-transform scripts remain available through the normal Script Editor/CLI. No filesystem, shell, network, arbitrary modules or native libraries are exposed to a plugin.

Limits: 16 million input pixels, 256 KiB source per effect, 24 parameters, 50 million Rhai operations, bounded nesting/strings/arrays/maps and console output, a 45 second worker deadline and platform memory limits. Per-pixel interpreted scripts may reach the operation limit on large images. Prefer existing native batch operations where appropriate. Exceeding a limit returns an error without changing the document.

`progress()` is advisory; the current isolated dialog uses an indeterminate processing indicator. `sleep()` is for legacy scripting demonstrations and should not be used to implement plugin previews.
