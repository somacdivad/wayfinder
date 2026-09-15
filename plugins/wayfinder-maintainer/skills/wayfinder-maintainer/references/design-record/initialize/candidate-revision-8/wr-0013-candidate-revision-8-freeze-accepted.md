<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":8,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0013","kind":"decision","legacy":{"sourceSectionSha256":"dc59b6db5665b28a1c060ceea2e538fd15b269fb3982aa82c57e068603411547"},"outcome":"accepted","predecessors":["wr-0011"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 8 freeze — accepted.","title":"Candidate revision 8 freeze — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 8 freeze — accepted

Implemented on 2026-09-13 as the bounded freeze-readiness correction:

- Separates the semantic contract's `frozen` status from the release's `unactivated-frozen` status. Frozen identifies the parity target; it does not certify the Python adapter, any environment, adapter parity, the adapter family, or runtime activation.
- Generalizes the release descriptor from one fixed Python adapter to a closed ordered adapter registry plus closed certification entries. The frozen release still lists only `python-reference-v1`; Node.js and PowerShell implementations remain absent.
- Adds digest-valid mutations for status/schema disagreement and adapter-registry disagreement. Package verification now rejects both before reporting a successful probe.
- Makes all 96 normative rules directly cited by at least one of 305 conformance cases and records that coverage counts are traceability evidence, not semantic proof.
- Reviews each governed expected-output artifact against named normative rules and records one deterministic expected-output-set digest in the maintainer-owned freeze proposal.
- Pins future matrix targets to CPython 3.14.7, Node.js 24.21.0, and PowerShell 7.6.6 using current primary official sources. These are requirements for future evidence, not claims that the environments exist or have passed.
- Records precise invalidation triggers and actions. Governed-byte or semantic changes reopen the candidate, advance its revision, invalidate affected evidence, and require every adapter to rerun.
- Preserves the Python adapter as an implementation under test and keeps runtime activation disabled.

The proposed-freeze record, acceptance record, and revision-8 local evidence remain maintainer-owned under `certification/v1/`. Candidate revisions 6 and 7 and Slice 1–5 historical evidence remain preserved. The freeze acceptance does not authorize parity implementation.

Evidence: [candidate revision 8 local report](../../../../certification/v1/candidate-revision-8-local.md), its [machine-readable form](../../../../certification/v1/candidate-revision-8-local.json), the [freeze-readiness packet](../../../../certification/v1/proposed-freeze-revision-8.md), and the [Option A acceptance record](../../../../certification/v1/freeze-acceptance-revision-8.md). All 305/305 cases pass on local macOS with CPython 3.12.14. The contract digest is `75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b`; the release descriptor digest is `69d029df64b5ac553aedab0d6127d3b99371f77847a7e41defac459b7e3c773e`; the Python adapter digest is `d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4`; the fixture-index digest is `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`; the expected-output-set digest is `c0fad6a47eff844f27135620e07210d081f19fab88aaa962cf5f0a6fb563ed7e`; and the result-set digest is `6cb5f6f61a5000bd69cd175dd4835feca61366ea0f9c2c9fbb483b8f12cfa022`. This remains maintainer-run local Python evidence, not independent, cross-platform, parity, environment, or full-family certification.

### Revision 8 approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Version-1 freeze readiness | Accepted 2026-09-13 | The skill owner selected Option A and accepted revision 8 as the frozen version-1 parity target. This authorizes later, separately requested Node.js and PowerShell implementations to target the frozen semantics. It does not begin parity work, certify any adapter or environment, authorize cross-adapter comparison, or activate Wayfinder. |

