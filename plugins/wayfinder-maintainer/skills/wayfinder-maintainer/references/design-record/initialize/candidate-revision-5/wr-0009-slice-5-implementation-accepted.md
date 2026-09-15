<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":5,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0009","kind":"decision","legacy":{"sourceSectionSha256":"15bc8e445e0e543e3df65284897c382a5d5dd181c1b3785428f475f3df95bc24"},"outcome":"accepted","predecessors":["wr-0008"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Slice 5 implementation — accepted.","title":"Slice 5 implementation — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Slice 5 implementation — accepted

Implemented as candidate revision 5 and accepted by the skill owner on 2026-09-13; intentionally left unactivated:

- Added public noninteractive `initialize-apply` and `initialize-recover` commands. Apply requires the external bundle, exact plan SHA-256, and the literal `wayfinder-confirm-sha256:<digest>` token; recovery requires an operation ID and an explicit `inspect`, `resume`, or `rollback` action.
- Apply verifies canonical plan bytes, the current contract, workspace binding, closed bundle membership, every payload length and digest, the locally resolved baseline, source inventory/intake/source bytes, target and module-root absence, and manifest absence. It imports exact bundle bytes and never regenerates or reinterprets semantic content.
- The workspace lock is one exclusive `.wayfinder/initialize.lock` with operation, plan, host, process, and owner-token identity. Apply never steals it. Recovery reclaims only same-operation, same-plan, same-host locks whose recorded process is no longer present; malformed, foreign, live, mismatched, and ownership-changed locks block mutation.
- Each operation uses a private `.wayfinder/operations/<operation-id>/` root and same-filesystem staging area. The first immutable hash-chained event records the complete intended target set and digests before staging or publication. Canonical event lines use one-based sequence, UTC whole seconds, predecessor digest, and a digest of the event basis.
- Staging materializes every planned payload byte, verifies its length and hash, and reproduces the Slice 4 validation projection. Publication creates only absent directories, exclusively creates and verifies non-manifest files, then exclusively publishes and verifies the manifest as the final discovery marker.
- Post-publication checks regenerate catalog and region expectations in memory through the accepted validator, compare the complete live target set with the plan, and record separate passed operational-integrity and semantic-readiness gates. A manifest without both gates and a valid receipt remains recovery-required.
- The canonical receipt binds the plan, contract, adapter, baseline, target set, manifest, intake counts, validation, both gates, entrypoint, open questions, and durable Interview handoff. The receipt is written before the terminal `complete` event and remains audit/routing data rather than semantic authority.
- Recovery inspection is read-only and returns `resumable`, `completed`, `rolled-back`, `blocked`, or `manual-recovery`. Resume trusts only a valid imported bundle, hash chain, exact event-owned paths, absent unowned targets, and current baseline/source predicates. Rollback removes an exact operation manifest first, then only exact unchanged event-owned files and empty event-owned directories; modified, missing-unexpected, unowned, nonempty, or symbolic paths are preserved and reported.
- Maintainer-only failure injection covers lock acquisition, bundle recording, every staged payload, staging completion, the second preflight, publication start, each directory, every file pre/post boundary, manifest pre/post, live validation pre/post, receipt, completion, rollback start, and rollback removals. The cumulative fixtures exercise inspection, resume, rollback, completed, blocked, and manual-recovery outcomes without changing MyPond's project record.
- Slice 4's historical evidence remains unchanged. Slice 5 writes separate cumulative local evidence labeled incomplete family certification; Node.js, PowerShell, cross-adapter recovery, the release environment matrix, independent evaluation, contract freeze, runtime guidance, and activation remain deferred.
- The final cumulative local suite passes 302/302 cases: all 251 accepted Stage 0–Slice 4 regressions plus 51 Slice 5 cases. The candidate-revision-5 contract digest is `39c22cfd2ddb39ca1ba043364bc9d916fd9f8236d1fc75c8e3b39e7eb1d7f666`; the release descriptor digest is `5c920381334368a799ad397f146391251cf95fb443824f70421014f6f7a36c7f`; the Python adapter digest is `47fa949e5b329337009d74d7890edf6cfdc636d772f90f6f798a5d4886209693`; and the result-set digest is `1a4a430a3880808da03197bb2a02ee3425d56ae3168f4cf28bdc7ce4ba06f066`.

Accepted consequential Slice 5 implementation choices:

1. The confirmation token is deliberately mechanical and plan-bound: `wayfinder-confirm-sha256:<plan digest>`. It proves explicit caller intent without parsing preview prose.
2. Operation IDs continue to derive from the first 24 plan-digest hex characters; the injected Slice 4 operation ID remains a planning-only test projection because ordinary Apply accepts no unbound operation-ID override.
3. `events.jsonl` is append-only by adapter behavior and tamper-evident through a strict hash chain; version 1 does not claim filesystem-enforced immutability.
4. Directory durability uses file flushes plus best-effort directory `fsync` where the platform permits it. The contract promises detection and conservative recovery, not universal crash-atomic persistence.
5. Staging is private and on the workspace filesystem, but publication uses exclusive creation of final files rather than renaming staged files; this preserves no-clobber behavior consistently across the version-1 portability target.
6. Completed operations retain imported bundle, journal, and receipt. Successful staging bytes are removed. Retention or pruning belongs to a later Update/governance decision.
7. A same-host dead-process check is the only automatic stale-lock proof. Foreign-host locks remain blocked because a local process check cannot establish their owner is gone.

Evidence: [cumulative Stage 0 through Slice 5 local report](../../../../certification/v1/slice-5-local.md) and its [machine-readable form](../../../../certification/v1/slice-5-local.json).

### Slice 5 approval checkpoints

| Checkpoint | Status | Decision |
|---|---|---|
| 1 — Apply, staging, and manifest-last publication model | Accepted 2026-09-13 | The skill owner selected Option A and accepted the confirmation binding, two-stage preflight, same-filesystem staging, exclusive no-clobber publication, and manifest-last visibility boundary as implemented. No follow-up exception was attached. |
| 2 — Journal, interruption recovery, rollback, receipt, and runtime-safety boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted the hash-chained journal, interruption classification, conservative resume and rollback behavior, externally modified-path preservation, completion receipt, Interview handoff, and runtime-safety boundary as implemented. No follow-up exception was attached. |
| 3 — Evidence and explicit Slice 5 tranche approval | Accepted 2026-09-13 | The skill owner selected Option A, accepted the cumulative 302/302 conformance portfolio and independent 251/251 regression run with the documented local macOS/Python evidence boundary, and explicitly approved Slice 5 as implemented. No follow-up exception was attached; parity, freeze, publication, runtime guidance, activation, and live-project initialization remain unauthorized. |

