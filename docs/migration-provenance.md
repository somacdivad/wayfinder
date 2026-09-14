# Migration provenance

- **Status:** Published; initial repository validation passed
- **Last updated:** 2026-09-14
- **Source repository:** `somacdivad/mypond`
- **Source paths:** `skills/wayfinder` and `skills/wayfinder-maintainer`
- **Import date:** 2026-09-14

The two source directories were untracked in MyPond and had no Git history to extract. This repository therefore begins with an initial content import rather than fabricated subtree history. [`migration-manifest.json`](migration-manifest.json) records every imported source path, destination path, source digest, destination digest, and whether the bytes were preserved or intentionally changed for the new repository topology.

Frozen governed contract bytes, the release registry, all three registered adapters, accepted historical evidence, accepted parity evidence, and the existing macOS matrix evidence are imported byte-for-byte. Historical reports retain their original paths and environment descriptions because they describe the run that created them.

The only imported files intentionally changed during migration are maintainer-owned orchestration or documentation needed for path discovery, hosted provenance, and the accepted repository decision. Those changes do not alter governed semantics, registered adapters, package bytes, or prior evidence.

## Publication result

The public repository is [`somacdivad/wayfinder`](https://github.com/somacdivad/wayfinder). Initial commit `6f8a311be0d8c98d557db64ed3263acd4b92ffe3` was published to `main` on 2026-09-14. Its first hosted validation exposed a maintainer-harness path-normalization defect on Linux; a bounded maintainer-only correction preserved all frozen governed and adapter bytes, and the ordinary repository-validation workflow subsequently passed on `main`. The manual certification and evidence-publication workflows were not run as part of migration.
