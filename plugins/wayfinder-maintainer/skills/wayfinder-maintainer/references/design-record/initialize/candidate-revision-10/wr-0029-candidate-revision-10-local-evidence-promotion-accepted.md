<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":10,"date":null,"format":"wayfinder-design-record","id":"wr-0029","kind":"decision","legacy":{"sourceSectionSha256":"9b4588d96cc9b61b2e77a12f2b57f1b0e47479d854f069d1bc706d351f0bcff7"},"outcome":"accepted","predecessors":["wr-0028"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 10 local evidence promotion — accepted.","title":"Candidate revision 10 local evidence promotion — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 10 local evidence promotion — accepted

The owner accepted the hosted-artifact verification and promotion-readiness packet and authorized only this bounded local implementation:

- Promoted exactly 27 previously verified, uniquely resolved, non-symbolic regular files from the temporary extraction for GitHub Actions run `34921918384`, attempt `1`, source commit `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54`, into `certification/v1/hosted/run-34921918384-attempt-1/` without replacing any prior evidence. The exact file set and every SHA-256 are pinned by doctor and `maintain.py describe`.
- Re-ran the offline matrix reviewer before promotion. It found all eight execution records and eight report pairs, zero failing environments, zero binding issues, and a passing strict aggregate. Aggregate JSON `be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50`, aggregate Markdown `ffe1fe3dc6ae9ed1b21356943ea8f98451221a5e8248043d74cf21c5a0b3cf18`, and matrix `2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0` retain their accepted bindings.
- Corrected `scripts/prepare_evidence_release.py` to accept only candidate revision 10 and the exact source commit, run ID, attempt, 27-file membership and digests, eight execution records, eight JSON/Markdown report pairs, aggregate entries, inventory, and recomputed matrix binding. Missing, extra, nested/ambiguous, symbolic, non-regular, changed-during-read, malformed, or digest-mismatched input fails before output creation.
- Corrected `.github/workflows/publish-evidence.yml` to require the exact accepted run, attempt, source, and matrix before checkout; pass those bindings to the preparation script; and use candidate-revision-10 tag, title, and bounded-evidence notes.
- The durable claim remains exact maintainer-run bounded matrix evidence for the eight named environments at this one source/run/attempt. It is not independent evaluation, generalized Windows certification, adapter-family certification, full-family certification, forward testing, cross-adapter recovery, runtime guidance, or activation.
- The release registry and its empty `certifications` array, all governed bytes, historical evidence, runtime instructions, adapter registry, activation state, Git state, external state, and live-project data remain unchanged. No workflow was dispatched and no release was created.
- On 2026-09-14, the owner explicitly accepted the exact 34-path implementation and authorized only a separate new-session source-publication tranche for those paths on `candidate-revision-9-certification`. This acceptance does not begin source publication or authorize workflow dispatch, protected-environment evidence publication, release creation, release-registry changes, runtime guidance, activation, live-project work, or a later tranche.

### Revision 10 local evidence-promotion checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact 27-file local evidence-promotion implementation | Accepted 2026-09-14; exact 34-path source publication authorized | The owner accepted the complete local implementation and authorized only a separate new-session source-publication tranche for the enumerated paths. Acceptance did not stage, commit, push, dispatch, publish evidence, create a release, alter the release registry, broaden certification, add runtime guidance, activate Wayfinder, or begin later work. |

