# Migration provenance

- **Status:** Implemented local import; publication pending
- **Last updated:** 2026-09-14
- **Source repository:** `somacdivad/mypond`
- **Source paths:** `skills/wayfinder` and `skills/wayfinder-maintainer`
- **Import date:** 2026-09-14

The two source directories were untracked in MyPond and had no Git history to extract. This repository therefore begins with an initial content import rather than fabricated subtree history. [`migration-manifest.json`](migration-manifest.json) records every imported source path, destination path, source digest, destination digest, and whether the bytes were preserved or intentionally changed for the new repository topology.

Frozen governed contract bytes, the release registry, all three registered adapters, accepted historical evidence, accepted parity evidence, and the existing macOS matrix evidence are imported byte-for-byte. Historical reports retain their original paths and environment descriptions because they describe the run that created them.

The only imported files intentionally changed during migration are maintainer-owned orchestration or documentation needed for path discovery, hosted provenance, and the accepted repository decision. Those changes do not alter governed semantics, registered adapters, package bytes, or prior evidence.
