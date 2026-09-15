<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":2,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0006","kind":"decision","legacy":{"sourceSectionSha256":"4c46a3229ae4d4c533571f5542b93bff4c08edeeb13d7ef6cd545914c852dcd9"},"outcome":"accepted","predecessors":["wr-0005"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Slice 2 implementation — accepted.","title":"Slice 2 implementation — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Slice 2 implementation — accepted

Implemented as candidate revision 2 and accepted by the skill owner on 2026-09-13:

- Added one public read-only `inventory --workspace-root PATH --request FILE [--ledger FILE]` command. The skill owner selected this interface as Option A after the accepted closed command surface proved insufficient for black-box Slice 2 behavior without prematurely implementing `initialize-plan`.
- The strict request bounds local source selections, target-root exclusions, and deterministic entry, byte, and traversal-depth limits. It never defaults to scanning a repository.
- Traversal uses non-following classification, stable UTF-8 path ordering, normalized workspace-relative paths, overlap de-duplication, explicit exclusion reasons, safe regular-file reads, strict UTF-8 versus opaque-byte classification, ATX Markdown cues, and exact duplicate groups.
- The strict intake ledger validates all four confirmed dispositions, identifier shapes, mappings, transformation notes, evidence keys, question IDs, inventory binding, and current source bytes. It does not infer materiality or any semantic decision.
- Candidate resources and the Python adapter remain unactivated. Slice 1 evidence remains historical and digest-bound to candidate revision 1; Slice 2 receives separate cumulative local evidence and is not full-family certification.

Evidence: [cumulative Stage 0 through Slice 2 local report](../../../../certification/v1/slice-2-local.md) and its [machine-readable form](../../../../certification/v1/slice-2-local.json).

### Slice 2 approval progress

| Checkpoint | Status | Outcome |
| --- | --- | --- |
| 1 — Inventory and intake model | Accepted 2026-09-13 | The skill owner selected Option A and accepted the canonical inventory representation, explicit source selections and limits, normalized deterministic traversal, exclusion model, file classification and hashing, Markdown cues, exact duplicate groups, and closed intake-ledger structure as implemented. No follow-up exception was attached. |
| 2 — Runtime safety and semantic-authority boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted exact physical workspace resolution, lexical containment, intermediate-symlink rejection, non-following classification and file reads, hard and soft exclusion boundaries, explicit limits, stale-source failure, closed deterministic result behavior, read-only guarantees, and the rule that the adapter validates mechanics without making human semantic or authority judgments. No follow-up exception was attached. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Slice 2 on the cumulative 104-case local evidence, with the disclosed local-only, single-adapter, missing-platform, missing-independent-validation, and unavailable bundled-PyYAML-validator limitations. The dependency-free frontmatter check was accepted as the local substitute. No follow-up exception was attached. |

