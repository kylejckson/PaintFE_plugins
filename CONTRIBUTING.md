# Contributing a community pack

Keep your source under `plugins/<publisher>/<pack>/`. Start from an existing example or export a local plugin from PaintFE. Include a licence, a description, a browser icon and an honest preview screenshot. Effects can provide light/dark menu icons. Themes and icon packs contain appearance data instead of effects; see [the appearance guide](docs/appearance-packs.md).

1. Give the pack and each effect stable IDs. Do not reuse another publisher's identity.
2. Run `python -m pip install -r requirements.txt`, `python tools/catalogue.py validate` and `python -m unittest discover -s tests -v`.
3. For effects, test default and extreme parameters, selection, alpha, Cancel and Undo. For themes and icons, test Preview and apply, both Keep and Restore, readable controls and the built-in fallback for missing icons. Record the build/API version and expected results in the pull request.
4. Submit a pull request. No signing key is needed by contributors.
5. A maintainer reviews the source, licence, artwork and app results before publication.

A submission issue is available if you cannot prepare a pull request. Attach an exported pack and link its source and licence.

Static CI validation is not proof that a pack behaves correctly. Contributor code never receives publishing credentials. Changed code, appearance data or resources require a new pack version. Keep existing pack, effect and parameter IDs when compatible. Contributors submit source or an exported pack; they do not upload signed assets directly to the catalogue. A maintainer reviews and publishes approved submissions.
