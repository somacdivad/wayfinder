<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":6,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0010","kind":"decision","legacy":{"sourceSectionSha256":"6d0b5b1e5177f0ed0564affd6eec3f2e6f2e2bdd92324977428a639baeae4d82"},"outcome":"changes-requested","predecessors":["wr-0009"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 6 maintenance correction — changes requested.","title":"Candidate revision 6 maintenance correction — changes requested","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 6 maintenance correction — changes requested

Implemented on 2026-09-13 as a bounded correction to the unactivated candidate:

- Replaced slice-shaped release identity with `v1-candidate-revision-<positive integer>` and made the contract's `candidateRevision` the single current-revision authority. The release descriptor, release schema, deterministic probe oracle, normative contract, and Python adapter now agree on candidate revision 6.
- Added `WF-PKG-004` and a digest-valid mutation case that proves the adapter rejects semantic disagreement between the release descriptor and release schema. Package hash agreement alone is no longer treated as sufficient.
- Added `maintainers/maintain.py` as the dependency-free entry point for environment checks, package verification, conformance runs, explicit evidence creation, expected-negative demonstrations, and factual handoff scaffolding.
- Changed the conformance runner so ordinary test runs create no certification evidence. Evidence requires `--write-evidence`, is created only after a zero-failure suite, uses revision-scoped filenames, and refuses replacement through exclusive creation.
- Pinned the accepted Slice 1 through Slice 5 evidence hashes in `certification/v1/historical-sha256.json`; maintainer checks fail if those historical reports are missing or altered.
- Added the explicit-only `$wayfinder-maintainer` companion skill to keep maintainer instructions outside the runtime skill and to record the supported-interpreter, no-bytecode, optional-validator, evidence-preservation, and approval boundaries.
- Made the design record the only mutable implementation-progress authority; the research record now links here instead of duplicating a stale current-slice statement.
- This correction does not add Node.js or PowerShell adapters, certify parity, freeze or publish a release, activate runtime guidance, initialize a live project, install dependencies, mutate Git state, or change MyPond's product record.

Evidence: [candidate revision 6 local report](../../../../certification/v1/candidate-revision-6-local.md) and its [machine-readable form](../../../../certification/v1/candidate-revision-6-local.json). All 303/303 cases pass on local macOS with CPython 3.12.14. The contract digest is `df286c2633834814ff67cff79ee95bd46be62a1d5b33b3c5b45a31b8d3bdfccc`; the release descriptor digest is `a15d52f1dffb3342858f056ba6affdc454d8a5db519ad135a59b4fe90926d27a`; the Python adapter digest is `deb68477217e8d831ce5861f5b18e59dcaf4daef8d080c43d93d4f440296e95f`; and the result-set digest is `0074f0babf120639a0affea6be2319d97ebeea0b32a9aa85a13f2bd6af9fd526`. Historical Slice 1 through Slice 5 reports remain unchanged and retain their original candidate bindings. This is maintainer-run local evidence, not independent validation or complete adapter-family certification.

Review outcome: changes requested by the skill owner on 2026-09-13. The maintainer-only material remained inside `$wayfinder`, making the companion-skill boundary confusing. Candidate revision 7 preserves the revision-6 fixes while correcting that topology.

### Candidate revision 6 approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Maintenance safety and cross-artifact consistency | Changes requested 2026-09-13 | The skill owner selected Option B because the separate maintainer skill and an internal Wayfinder `maintainers/` subtree created a confusing ownership boundary. The revision-6 evidence is preserved, but revision 6 was not accepted. |

