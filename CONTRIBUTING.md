# Contributing a plugin

Keep your source under `plugins/<publisher>/<pack>/`. Start from an existing example or export a local plugin from PaintFE. Include a licence, a description, a 64px browser icon, light/dark menu icons and a preview screenshot made with your effect.

1. Give the pack and each effect stable IDs. Do not reuse another publisher's identity.
2. Run `python -m pip install -r requirements.txt`, `python tools/catalogue.py validate` and `python -m unittest discover -s tests -v`.
3. Test the default and extreme parameters in a compatible PaintFE build, including selection, alpha, Cancel and Undo. Record the build/API version and expected output in the pull request.
4. Submit a pull request. No signing key is needed by contributors.
5. A maintainer reviews the source, licence, artwork and app results before publication.

A submission issue is available if you cannot prepare a pull request. Attach an exported pack and link its source and licence.

Static CI validation is not proof that an effect is correct or safe. Contributor code never receives publishing credentials. Changed effect code or resources require a new pack version. Keep existing effect and parameter IDs when compatible.
