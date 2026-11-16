# Theme collection

Author: **kylejckson**. Browse and install through View > Community add-ons.

PaintFE 1.5.0 supports the palettes and layouts. Grain, retro bevels and solid
accent headers require an updated client containing those finishes; 1.5.0
safely ignores the extra settings. Native desktop blur depends on the OS.

1. Charcoal Frosted Aero: neutral charcoal, Signal orange, desktop showing through workspace and all outer surfaces. Start with workspace 12-16%, panels 40-50%, toolbar 35-45%, headers 55-65%, controls 65-75%. Rounded 8-10 px panels, crisp fine borders, restrained shadows. Native blur optional. Includes a faint, static grain texture.
2. Charcoal Sharp Glass: same neutral charcoal and orange, 0-2 px radii, compact padding, straight dividers and stronger edge definition. Panels around 50-60%, toolbar around 40%. Less ornament, inspired by compact Linux desktops.
3. Retro 98: opaque warm system gray #c0c0c0, navy selection/title accents #000080, black text, white highlights, square corners and compact spacing. Separate Retro 98 Icons pack, recommended rather than required. Original small pixel-style art, not extracted Windows assets. Includes opt-in shared bevelled controls and solid navy dialogue headers.
4. Retro XP: opaque pale gray/cream surfaces, royal blue headings and selections, green secondary accents, warmer highlights and 5-7 px corners. No additional icon pack. XP-inspired, without promising native XP title bars or gradients the theme format does not support.
5. Paper Studio: opaque warm ivory, graphite text, burnt-orange accents, 6 px corners and clean thin borders. A bright, quiet everyday editor.
6. Graphite Studio: opaque neutral grays, muted mint focus accents, 4 px corners and subdued borders. No coloured cast around the document.
7. Northern Mist: slate glass with icy teal accents, 65-75% panels and 8 px corners. More legible than Aero. Reference: https://www.nordtheme.com/
8. Moss Terminal: opaque olive charcoal, parchment labels and sage selection accents, compact 1-2 px corners. Restrained Unix-style appearance.
9. Amber Console: almost-black opaque surfaces, amber focus and selections, square outlines and minimal shadows. Sci-fi console styling without extra animation.
10. Pearl Aero: light translucent white and silver, Signal orange accents, 10-12 px corners, 65-75% panels and a lightly tinted desktop workspace. A light counterpart to Charcoal Aero.

One icon pack only: Retro 98 Icons. Inventory production icon names and both light/dark variants first. Cover tools, file actions, layers, history, navigation and menus with a consistent small pixel grid. The original pixel artwork passes silhouette, transparency, filename, fallback and real-size checks. Missing entries must use documented built-in fallbacks.

Each theme is an independent signed add-on, with its own identity, version, original artwork, description, tags and screenshots from actual PaintFE. The Retro 98 theme recommends the separate icon pack; it does not silently install it. Current appearance packs cannot bundle several independent themes/icons in one installable pack.

Before publication: validate manifest and theme import, install through the real browser, check preview/Keep/Restore, restart persistence, removal and deliberate Light/Dark changes. Compare identical photo and transparent pixel-art fixtures, main editor, Preferences, Save As, effect dialog, menus, brush browser and compact/wide layouts. Check blur off fallback. Keep native macOS/Linux visual coverage distinct from Windows checks. Do not modify document pixels, user shortcuts or automation permissions.


## Rebuilding the original artwork

Install `requirements-art.txt`, then run `python tools/theme_collection.py` from
a development checkout placed at PaintFE/target/plugin-repository. The builder
derives canonical icon IDs from PaintFE and draws original pixel artwork on a
24-pixel grid. It does not reuse Windows icon files. Both light and dark variants
are exported, including the double-width Shapes icon. Existing theme preview
images are retained when rebuilding palette files and badges.

The supplied previews are actual app screenshots, captured without the mouse
highlight. The still-life image and neutral desktop backdrop are owned review
fixtures. Keep replacement screenshots authentic and validate the final packaged
bytes. Do not overwrite a published pack version.

The new grain texture, bevels and solid title bands need an updated PaintFE core
before public launch. Native blur remains OS-dependent; colour and geometry
fallbacks work without it.
