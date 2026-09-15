<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":null,"date":null,"format":"wayfinder-design-record","id":"wr-0016","kind":"context","legacy":{"sourceSectionSha256":"4d2f514579ee74168be336a9ba97fc623a1acc32e0e88539a748eee13ae2e604"},"outcome":"historical","predecessors":[],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Public repository migration — implementation checkpoint (historical context; current-state.md owns current status).","title":"Public repository migration — implementation checkpoint","topic":"distribution"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Public repository migration — implementation checkpoint

Authorized on 2026-09-14 as a delivery and packaging tranche separate from certification and activation:

- The repository root is a source and marketplace container with independently installable `plugins/wayfinder` and `plugins/wayfinder-maintainer` packages.
- Each package has one canonical skill tree, a portable Agent Plugins 1.0 manifest, and thin Codex and Claude compatibility manifests. The end-user catalogs list only `wayfinder`; the maintainer package remains opt-in.
- The frozen contract, release registry, registered adapter bytes, accepted historical evidence, accepted parity evidence, and existing macOS matrix evidence remain unchanged. A migration manifest binds every imported source file to its source and destination SHA-256 digest and labels only maintainer-owned topology changes.
- Repository validation, ordinary conformance, exact eight-entry certification, aggregation, and evidence-publication preparation are separate workflows. Certification and evidence publication are manual-only; the latter is gated by a protected GitHub environment and produces a draft release for final review.
- GitHub Actions use fixed OS labels, exact runtime patch versions, checksum-verified PowerShell archives, full action commit SHAs, least-privilege permissions, and no `pull_request_target` execution.
- The migration does not approve the pending bounded matrix tranche, execute hosted certification, add release certification entries, perform full-family certification, publish a runtime release, add runtime guidance, or activate Wayfinder.

### Migration checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Public two-plugin repository structure and CI route | Published and validated | The owner authorized implementation on 2026-09-14. The public `somacdivad/wayfinder` repository was created and initial commit `6f8a311be0d8c98d557db64ed3263acd4b92ffe3` was published to `main`. The first hosted validation exposed a maintainer-harness path-normalization defect on Linux; a bounded maintainer-only correction preserved all frozen governed and adapter bytes, and ordinary repository validation subsequently passed. The manual certification and evidence-publication workflows were not run. No subsequent certification or activation tranche begins automatically. |

