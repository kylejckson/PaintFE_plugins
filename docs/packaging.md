# Package format

A `.pfeplugin` is a ZIP with a signed `manifest.json` envelope and exactly the declared resource files. An envelope contains `payload` (the UTF-8 JSON manifest as a string) and an Ed25519 `signature` in hex. Local exported packs have an empty signature and are explicitly labelled local.

The manifest has schema 1, api 1, a stable publisher-qualified id, independent three-part version, name, author, description, licence, tags, effects, artwork paths and a generated `files` list. Each file record contains path, byte size and SHA-256. Source manifests omit the generated file list; the packaging tool creates it.

Paths are relative and restricted. Absolute paths, traversal, symlinks, duplicate archive entries, undeclared files and executable resources are rejected. Packages are limited to 16 MiB and 64 resources; PNG dimensions and allocations are bounded. Plugins must not contain another runtime or downloaded dependencies.

Menu icons may supply light and dark PNG variants. Use a 64x64 browser icon, 24x24 menu icons and a 16:9 screenshot no larger than 1600x1200. All artwork needs a compatible licence.

Run `python tools/catalogue.py validate` before submission. The trusted publishing workflow creates signed packages. Contributors never need the signing key. A pack update requires a new version, but a PaintFE patch release does not require repackaging if API compatibility remains unchanged.
