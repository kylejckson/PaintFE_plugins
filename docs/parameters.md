# Controls and dialogs

Parameters are declared as data in `manifest.json`; opening a menu or reading metadata never executes effect source. In PaintFE, the Properties form edits the same declaration. Do not maintain a separate UI implementation.

Each parameter has `id`, `label`, `kind`, `default` and optional `help` and `group`. IDs must be stable lowercase identifiers without dots or hyphens.

| Kind | Default | Additional fields |
| --- | --- | --- |
| number | JSON number | min, max, step |
| integer | whole JSON number | min, max, step |
| boolean | true or false | none |
| text | string, up to 2048 characters | none |
| choice | one of the choice strings | choices |
| colour | [r,g,b,a], integers 0 through 255 | none |

Scripts read values through `params`, for example `params.radius` or `params.colour[0]`. Controls use PaintFE's theme, numeric editor, keyboard interaction and reset behaviour. Set `histogram: true` on an effect to request a bounded luminance histogram below the preview.

Previews always begin from the original input. Changing a value cancels obsolete work. Apply commits a validated final result once. Cancel belongs to PaintFE and cannot be hidden by the script. The app offers manual Preview as well as Live preview. Arbitrary custom windows, shaders and executable widgets are outside API 1.

Consecutive parameters with the same non-empty group label share a section heading.
