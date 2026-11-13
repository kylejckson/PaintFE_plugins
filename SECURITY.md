# Security

Report a suspected malicious plugin or sensitive vulnerability privately using the repository security reporting channel when enabled. For ordinary bugs, use Issues. Do not include credentials or personal images in public reports.

Catalogue signatures establish provenance and integrity, not a guarantee that an effect is safe or produces the expected image. Plugins use a bounded Rhai API, run in a disposable worker and cannot choose filesystem paths, execute shell commands or contact a network service. General module imports are disabled.

Only reviewed source on the protected publishing path may be signed. Never run contributor scripts in a workflow that has publishing secrets. The private catalogue key must remain outside Git. Its public counterpart is in `catalogue-public-key.hex` and the compatible PaintFE build.
