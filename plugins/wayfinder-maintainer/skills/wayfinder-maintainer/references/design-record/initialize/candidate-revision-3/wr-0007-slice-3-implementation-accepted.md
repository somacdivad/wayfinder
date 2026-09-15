<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":3,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0007","kind":"decision","legacy":{"sourceSectionSha256":"dd93a4a64d033c3773c53f065bb2889c70454ed50634a1b76aa1e5cf9d62a36f"},"outcome":"accepted","predecessors":["wr-0006"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Slice 3 implementation — accepted.","title":"Slice 3 implementation — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Slice 3 implementation — accepted

Implemented as candidate revision 3 and accepted by the skill owner on 2026-09-13; intentionally left unactivated:

- Added read-only `validate --workspace-root PATH` and file-oriented `generate --workspace-root PATH --request FILE [--output-root PATH]`. The closed generation request has four bounded actions: read-only candidate `allocate`, no-overwrite `render`, manifest-declared `catalog`, and explicit-path `regions`.
- Added strict authored Markdown parsing for global document and question IDs, exact metadata and relationship blocks, kind-specific lifecycles and content profiles, first-class question histories, evidence source records, local citations, and explicit material-claim markers.
- Added record-wide validation for manifest-derived module/subject membership, typed link ID/path bindings, target kind/status, reciprocal acyclic supersession, generated-region ownership and freshness, and catalog freshness. Mechanical checks do not infer semantic meaning or authority.
- Added seven governed literal templates with four closed one-pass slots. Render validates every complete document in memory, preserves supplied prose, rejects existing outputs and symbolic path components, and writes only beneath an explicit existing output root.
- Added deterministic `document-catalog-v1` and `document-index-v1` projections. Generated regions have one exact delimiter carrying the input digest; region updates preserve every authored byte outside the delimited range and are byte-idempotent.
- Chose inline exact question histories and the explicit `Scope: Record-Wide` marker as the smallest portable question representation. Chose `- **Material claim:**` as the only machine-enforced claim boundary; identifying other material prose and assessing source support remain human semantic work.
- Generation uses same-directory temporary files and atomic replacement only for already declared catalogs and explicitly requested existing regions. Slice 3 adds no prompt, network, dependency installation, external-system, Git, publication, journal, receipt, or project-record authority.
- Candidate resources and the standard-library Python adapter remain unactivated. Earlier Slice 1 and Slice 2 evidence remains historical and digest-bound; Slice 3 receives separate cumulative local evidence and is not full-family certification.

Evidence: [cumulative Stage 0 through Slice 3 local report](../../../../certification/v1/slice-3-local.md) and its [machine-readable form](../../../../certification/v1/slice-3-local.json).

### Slice 3 approval progress

| Checkpoint | Status | Outcome |
| --- | --- | --- |
| 1 — Record model and semantic constraints | Accepted 2026-09-13 | The skill owner selected Option A and accepted the implemented document and question ID model, exact metadata and content profiles, kind-specific lifecycles, question state/history rules, evidence-source and explicit material-claim citation model, typed relationships, reciprocal acyclic supersession, manifest-derived membership, contained local-source paths, and the boundary between deterministic mechanical validation and human semantic judgment. No follow-up exception was attached. |
| 2 — Rendering, generation, and runtime-safety boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted read-only validation/allocation, closed one-pass rendering into an explicit existing output root, exclusive no-overwrite creation, manifest-declared catalog replacement, explicit generated-region replacement, authored-byte preservation outside regions, deterministic byte-idempotent projections, and the no-prompt/network/external-system/dependency/Git boundary. Per-file rather than batch atomicity remains an explicitly disclosed Slice 3 limitation deferred to the later journaled transaction work. No follow-up exception was attached. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Slice 3 on the cumulative 202-case local evidence, including all 104 accepted regressions, with the disclosed local-only, single-adapter, missing-platform, missing-independent-validation, per-file atomicity, later-slice, and unactivated-runtime limitations. No follow-up exception was attached. |

