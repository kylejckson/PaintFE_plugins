# Themes and icon packs

Appearance packs require PaintFE 1.5.0 or a compatible preview. Installing a pack does not apply it. The browser's Preview and apply action offers Keep appearance and Restore previous appearance. These packs cannot contain scripts or change agent permissions.

## Create a theme

1. Configure the appearance in Preferences > Interface. Check text, controls, dialogs and menus, including compact windows.
2. Use Export theme to save a `.paintfe-theme` file, then copy its text into the pack's `theme.txt`. Exported theme data does not include your documents, storage location or MCP permissions.
3. Copy `plugins/paintfe/frosted-glass-dark` or `frosted-glass-light` into `plugins/<publisher>/<pack>`. Use your own stable ID, name, author, licence and description.
4. Replace `theme.txt` and the artwork. Capture the real theme in PaintFE using an image and background you have permission to distribute. State any platform-specific effects in the description.

Glass is optional. Native blur is managed by the OS and can look different on Windows, macOS and Linux. Include readable surface colours for systems without the effect. Test with blur off as well as on.

## Create an icon pack

Start from PaintFE's icon-pack template in Preferences > Interface. Keep its filenames and light/dark variants, replace the PNG artwork, and test the folder or ZIP with the existing custom icon-pack importer. Missing icons use the built-in fallback. Keep the files at the ZIP root rather than nesting them inside a containing folder.

For the community wrapper, copy the format example under `examples/legacy/luminous-icons` into your publisher folder and replace its artwork and identity. This example is not a downloadable catalogue pack. Set `kind` to `icons` and `appearance` to the icon ZIP filename. Use an empty `effects` list.

Community icon ZIPs are limited to 1,024 entries, 16 MiB expanded files and 64 MiB decoded pixels. Each PNG is at most 1,024 by 1,024. Theme text is limited to 512 KiB. The outer pack also has the limits described in [Package format](packaging.md).

## Manifest and submission

A source theme manifest uses these fields, plus its artwork:

```json
{
  "schema": 1,
  "api": 1,
  "kind": "theme",
  "appearance": "theme.txt",
  "id": "yourname.charcoal",
  "version": "1.0.0",
  "name": "Charcoal",
  "author": "Your name",
  "description": "A charcoal theme with clear, quiet controls.",
  "license": "MIT",
  "tags": ["Dark"],
  "effects": [],
  "icon": "art/icon.png",
  "screenshot": "art/preview.png"
}
```

Do not copy the example's licence declaration unless you can license all your submitted material that way. Include the licence file and credit third-party artwork where required. Do not add generated resource hashes by hand.

Run the validation commands in [Contributing](../CONTRIBUTING.md), then submit a pull request. The submission issue form also accepts exported packs with source and licence links. No signing key or paid account is needed. Maintainers review, sign and publish approved packs. Later changes require a new pack version; existing published files are immutable.

Before submission, test installation, preview, Keep, Restore, persistence after restart and removal. Removing a theme leaves its kept appearance settings in place. Removing an active community icon pack restores the built-in icons.
