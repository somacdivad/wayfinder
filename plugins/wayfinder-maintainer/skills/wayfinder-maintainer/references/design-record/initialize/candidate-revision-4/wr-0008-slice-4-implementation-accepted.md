<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":4,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0008","kind":"decision","legacy":{"sourceSectionSha256":"59827da34ee7e4bcad907fb031d1468e0ababad01cf7f0e5aa5c341d53d8cecb"},"outcome":"accepted","predecessors":["wr-0007"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Slice 4 implementation — accepted.","title":"Slice 4 implementation — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Slice 4 implementation — accepted

Implemented as candidate revision 4 on 2026-09-13 and intentionally left unactivated:

- Added the public noninteractive `initialize-plan --workspace-root PATH --proposal FILE --bundle-root PATH` command. The explicit bundle must be absent, non-symbolic, and outside the workspace; the command never writes a target-record path.
- Added closed proposal and canonical-plan schemas. A proposal carries the confirmed profile and final manifest taxonomy, exact authored-document declarations, concern homes, epistemic states, omissions, authority boundary, material inferences, source bindings, material-source declarations, bootstrap readiness, and Interview resumption pointers.
- Normalization validates rather than chooses. Candidate document and question IDs begin at 1, remain consecutive in proposal order, and are checked for token and ordinal collisions. Complete authored content is rendered through the accepted literal templates and validated with the complete Slice 3 graph and containment model.
- Added deterministic virtual generation of authored payloads, generated regions, and the catalog. The plan addresses every authored, generated, and manifest payload by final target, ordinal bundle path, byte length, SHA-256, and producer digest; its declarative operation list creates directories, creates non-manifest files, and publishes the manifest last without executing any operation.
- Source-assisted planning rebuilds and compares the bound inventory, rechecks intake and source bytes, requires a reviewed disposition for each proposal-declared material source, proves target/question/evidence-key bindings, and copies canonical inventory and intake bytes into the external bundle.
- Added target, module-root, workspace, local Git-ref or snapshot baseline, source-digest, namespace, symlink, existing-output, prior-operation, competing-authority, readiness, placeholder, knowledge-map, and Interview-resumption preconditions.
- Resolved an unavoidable digest cycle by making raw canonical `plan.json` the confirmation object. It binds the full normalized plan and all target payload hashes. `preview.md` displays the plan digest and derived operation ID but is a reproducible review projection rather than a digest input or publication payload.
- Added a narrow Slice 3 regression correction: the accepted `foundation` and `evidence-led` profiles place `plan-brief.md` and `open-questions.md` directly under the record root, so root-level authored Markdown is now classified as kernel content with null module/subject. Nested documents still require exactly one module.
- Corrected the Slice 3 renderer's structured-link precheck to use the same owner-relative containment rule as the accepted Markdown parser. This permits normalized `../` links from collection documents to siblings while still rejecting destinations that escape the record.
- Local Git-ref resolution reads loose or packed refs without invoking Git or fetching. Effective date is explicit proposal data. The ordinary operation ID derives from the first 24 hex digits of the plan digest; maintainer injection requires test mode and a reserved visible namespace.
- Slice 4 still performs no application, publication, journaling, rollback, recovery, receipt, completion gate, Node.js or PowerShell work, runtime routing, candidate freeze, or activation.
- The cumulative local suite passes 251/251 cases: all 202 accepted Stage 0–Slice 3 regressions plus 49 Slice 4 cases. The final contract digest is `3b9e4b95db3263d7987e62316eda4329da2990813da8f6a4822b86ff138570df`; the final release descriptor digest is `59a57ebb370a43c059ce141378343b3792eab3892d319a4adfa007792b709915`.

Consequential implementation choices requiring this tranche review:

1. The bundle is external to the workspace, which makes its write boundary unambiguous and prevents a planning output from entering the future record namespace.
2. Materiality remains human authority: the proposal explicitly declares material source paths, and the adapter checks only that each declaration has one confirmed intake disposition.
3. The canonical plan digest excludes the preview to avoid a self-reference cycle; all review facts used to render the preview remain inside the digested plan.
4. Producer digests identify the literal template for authored files, the normative contract for generated projections, and the manifest schema for the manifest payload.
5. Multi-file bundle creation uses exclusive file creation after full semantic preflight. Slice 4 promises rejected-preflight zero writes and no overwrite; journaled interruption recovery belongs only to Slice 5.

Evidence: [cumulative Stage 0 through Slice 4 local report](../../../../certification/v1/slice-4-local.md) and its [machine-readable form](../../../../certification/v1/slice-4-local.json).

### Slice 4 approval checkpoints

| Checkpoint | Status | Decision |
|---|---|---|
| 1 — Proposal and normalized-plan model | Accepted 2026-09-13 | The skill owner selected Option A and accepted the closed proposal schema, semantic-authority boundary, identifier and candidate-ordering rules, virtual validation through the accepted Slice 3 model, and normalized-plan representation as implemented. No follow-up exception was attached. |
| 2 — Bundle, digest, preview, preconditions, and runtime-safety boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted the absent external non-symbolic bundle root, canonical `plan.json` confirmation object, SHA-256 binding of the normalized plan and every target payload, reproducible non-digested preview projection, declarative manifest-last operation order for future application, full preflight before exclusive no-overwrite bundle creation, rejected-preflight zero-write guarantee, and the no-target/source/Git/network/dependency/external-system-mutation boundary. No follow-up exception was attached. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Slice 4 on the cumulative 251-case local evidence, including all 202 accepted Stage 0–Slice 3 regressions and 49 Slice 4 cases, with the disclosed local-only, single-adapter, missing-platform, missing-independent-validation, later-slice, and unactivated-runtime limitations. No follow-up exception was attached. |

