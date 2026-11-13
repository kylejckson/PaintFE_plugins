# Maintainer operations

Use Python 3.13 and install requirements.txt. Validate structure and run all repository tests before publishing. Also test actual processing in a compatible PaintFE build; CI structure checks do not execute submitted scripts.

## Signing setup

Create a dedicated Ed25519 key. Store its raw 32-byte seed as hex in the repository secret `PLUGIN_SIGNING_KEY`. Commit only the corresponding hex public key to `catalogue-public-key.hex`. The same public key must be trusted by the compatible PaintFE build. Keep a private backup outside both repositories. Key rotation needs a coordinated PaintFE trust update.

## Publish approved packs

After review and merge to main, run **Publish plugins** with a new v-prefixed catalogue tag. Pack versions are independent from this catalogue release tag. The workflow checks metadata and tests, builds deterministic packages, signs them, publishes new assets, verifies unauthenticated public downloads, then updates the signed catalogue. Existing published assets are never overwritten. Unchanged packs retain their existing URLs. A changed pack must have a new version.

The generated `catalogue` branch contains catalogue.json, metrics.json and a small static landing page. Configure GitHub Pages to publish that branch's root. Publish/statistics workflows request a Pages rebuild explicitly. Statistics updates do not upload duplicate packs.

Publishing uses repository-scoped GITHUB_TOKEN permissions and the signing secret. Contributor pull-request validation receives neither write permissions nor signing secrets. No automatic merge or approval bypass is configured. If signing/branch requirements change, update automation to meet them rather than bypassing them.

## Recovery and withdrawal

If publication fails, inspect the workflow. Re-run with the same tag only when all existing immutable package assets match. The previous catalogue remains available until a complete signed replacement is ready. Check public URLs and the actual app after deployment.

For withdrawal, remove the affected listing from reviewed source and publish an updated catalogue without deleting historical release assets. Existing installations remain local; an explicitly refreshed browser must explain withdrawal rather than silently execute or delete user files. For a security incident, coordinate with a PaintFE maintainer before changing trust keys.

GitHub statistics schedules can be delayed or disabled after inactivity. The catalogue timestamp exposes stale data. Re-enable the workflow and run it manually when necessary. Build artifacts are disposable; release downloads are not Actions-cleanup targets.
