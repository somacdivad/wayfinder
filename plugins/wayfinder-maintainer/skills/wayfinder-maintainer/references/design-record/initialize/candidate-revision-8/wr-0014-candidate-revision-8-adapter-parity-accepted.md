<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":8,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0014","kind":"decision","legacy":{"sourceSectionSha256":"4b57a123e1218e58c9906b6ecffe421531c7dae90bd0ffa92c8428461dbd30fe"},"outcome":"accepted","predecessors":["wr-0013"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 8 adapter parity — accepted.","title":"Candidate revision 8 adapter parity — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 8 adapter parity — accepted

Implemented on 2026-09-14 as the bounded, independently assigned Node.js and PowerShell adapter parity tranche:

- Adds dependency-free Node.js and PowerShell adapters against the accepted frozen revision-8 contract and registers both adapters in the closed release registry. The Python reference adapter and every contract-governed semantic resource retain their accepted digests.
- Extends the maintainer runner to launch each native adapter, filter focused cases, capture deterministic differential observations, and apply identical package mutations to the selected adapter.
- Adds an atomic parity command that runs the complete common suite for all three registered adapters, compares frozen observable envelopes and ordered stable diagnostic codes across 900 invocations, and refuses to write evidence on any suite failure or mismatch.
- Compares adapter-independent observations after normalizing temporary paths, runtime and adapter identity, adapter-bound operation and audit digests, and contract-open human prose. The common suite separately asserts every frozen command-data projection, golden output byte sequence, mutation outcome, and stateful filesystem invariant.
- Keeps runtime instructions non-operational and records no certification entry. No later certification-matrix, forward-test, cross-adapter-recovery, runtime-guidance, activation, live-project, MyPond dogfooding, or Git tranche was performed.

Evidence: [candidate revision 8 local adapter parity report](../../../../certification/v1/parity-revision-8-local.md) and its [machine-readable form](../../../../certification/v1/parity-revision-8-local.json). The Python reference, Node.js, and PowerShell adapters each pass 305/305 common cases, their case-result digests agree, and their 900 normalized invocation observations agree at digest `4463448355c7662a09bb2112052179df0e95216e5bd1092968ee4ddc95b6d233`. The contract digest remains `75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b`; the Python adapter digest remains `d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4`; the Node.js adapter digest is `fcd01cfd47c98488eb2e85055924630642ee4093c02272bb67ba961d4e084125`; the PowerShell adapter digest is `9b64624f0c837db6082ce241a3f17f3d05614490e4e721d757588c8fefbe0bce`; and the adapter-registry release descriptor digest is `677fa5af49c11532d49875bd8d1138a36903668449188e6358f2d0a5947f2284`.

This evidence is maintainer-run on one macOS arm64 host with CPython 3.14.7, Node.js 22.22.3, and portable PowerShell 7.6.6. Node.js 22 is not the pinned Node.js 24 matrix target, and portable PowerShell on macOS is not a pinned matrix operating-system entry. The evidence is therefore local adapter parity only: it is not independent validation, an environment certification, or full-family certification.

### Adapter parity approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded Node.js and PowerShell adapter parity | Accepted 2026-09-14 | The skill owner selected Option A and accepted the bounded adapter parity tranche as implemented, including the disclosed local-only, non-independent, non-environment, and non-full-family evidence limits. No follow-up exception was attached. The later certification matrix, forward tests, cross-adapter recovery, runtime guidance, activation, and live-project work remain separately authorized tranches; this approval begins none of them. |

