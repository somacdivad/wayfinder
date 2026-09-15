# Wayfinder current maintainer state

> Compact routing reference. `maintain.py doctor` validates these facts against the package, accepted evidence, and chronological record.

## Current identity

- Candidate: `v1-candidate-revision-10` (contract `frozen`, release `unactivated-frozen`).
- Activation: **disabled**. The runtime skill remains non-operational.
- Contract: `0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341`.
- Release: `581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083`.
- Fixture index: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`; expected-output set: `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`.
- Registered adapters: `python-reference-v1` `e0b89ba35f223567efe2545d323d816dbaeeedfa8de8fb784fcc7b1c347cb596`, `node-v1` `f6d695e60e5964448947ed9f835526efa0f84e3764fb8acdd7f765e3bbe4fa3e`, `powershell-v1` `b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9`.
- Historical revision-8 accepted parity evidence: `parity-revision-8-local.json` `28bc61ede21e0b8041c1951b1327c948642d0712170048f17ce2bab9653562ef`, `parity-revision-8-local.md` `840641fd2b2814104a78f7fe0d4106ac70c4688056237003770d7ec7874e97c0`.
- Historical revision-8 accepted macOS matrix evidence: `matrix-revision-8-python-reference-v1-macos-20260914T125208Z.json` `6b43c2f0b41e83d76218e363651d6353ab62561426e4c7abf997cb561aa3fd78`, `matrix-revision-8-python-reference-v1-macos-20260914T125208Z.md` `8a81084ab64a18bac8d59694bc81233035cc0f02434a36d8106dfc0f2cc1c11c`.
- Accepted revision-9 local evidence, proposal, and freeze acceptance: `candidate-revision-9-local.json` `b7c9b046d2970c308530d2ba05893213fbf81445e96c4b355a9c3863c4fe734a`, `candidate-revision-9-local.md` `99a5ef242b1e96e966d1fe9cff3549565008520451921bc1e9d7abfc3237d264`, `freeze-acceptance-revision-9.json` `a934affb933fac7ad994257453afda952b6e81d7852e791f60389ebce4767088`, `freeze-acceptance-revision-9.md` `2f0c4bb8859bb3f7f0356038922678673544ddf45907bcdb680670813a581691`, `parity-revision-9-local.json` `3643fe1fb86a1c1fa99e7f47489e0f0c4965c56dbe86c6c01622d31887de9d4c`, `parity-revision-9-local.md` `11f3f7436b96c2be98e5efeb8fb2fb29bb373ba8826ea38b0594aeba806c00f5`, `proposed-freeze-revision-9.json` `9baf19c1f17848b7f0b1b12ff0e821472358f2aadde3dafa4f423194cb5e916c`, `proposed-freeze-revision-9.md` `b75d8862b47a16b13c4862643e7551d44777c98348cd9608f5c5aebd1ff8855f`.
- Durable revision-10 hosted evidence: `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/hosted/run-34921918384-attempt-1`; 27 exact files pinned by `maintain.py describe` and doctor; aggregate JSON `be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50`; aggregate Markdown `ffe1fe3dc6ae9ed1b21356943ea8f98451221a5e8248043d74cf21c5a0b3cf18`; matrix `2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0`.
- Accepted historical evidence is hash-pinned by [`historical-sha256.json`](../certification/v1/historical-sha256.json).

## Approval boundary

The owner explicitly accepted the exact four-file candidate-revision-10 evidence-publication readiness acceptance-record implementation. The recorded protected-environment readiness result is NOT READY. No evidence-publication dispatch is authorized. The decisive blocker is that publish-evidence.yml at source-publication commit 72da3542f3a7e65f4bcae09943612d8ba09daf3e checks out evidence source commit 82a2bb994e7ef8d2ffda7317e0687b0c7230aa54 before invoking scripts/prepare_evidence_release.py; that older verifier lacks --expected-run-id and --expected-attempt, targets revision 9, and would fail argument parsing before draft-release creation. Acceptance records this not-ready result only and authorizes no workflow or verifier correction, GitHub-settings change, workflow dispatch, artifact download, release or tag mutation, release-registry or runtime-guidance change, activation, or later tranche.

## Pending action and design-record routes

Evidence publication is not ready and is not dispatch-eligible. A correction to the publication workflow/verifier handoff is only a possible future separately authorized task. Do not correct the workflow or verifier, modify GitHub settings, dispatch a workflow, download artifacts, create or alter releases or tags, change the release registry or runtime guidance, activate Wayfinder, touch live-project data, or begin any later task automatically.

Read only the relevant exact section of the [chronological design record](design-record.md):

- `## Candidate revision 8 freeze — accepted` for frozen identity and invalidation rules.
- `## Candidate revision 8 adapter parity — accepted` for adapter and parity authority.
- `## Candidate revision 8 bounded certification matrix — accepted` for matrix requirements.
- `## Candidate revision 8 hosted certification execution — accepted with failed aggregate` for hosted evidence bindings.
- `## Candidate revision 8 Windows certification investigation and correction — accepted` for current blockers.
- `## Candidate revision 8 maintainer-efficiency tranche — accepted` for the current maintainer workflow and tooling baseline.
- `## Candidate revision 9 Windows corrections — accepted` for the current implementation and approval boundary.
- `## Candidate revision 9 hosted certification execution — accepted with failed aggregate` for the accepted bounded hosted result.
- `## Candidate revision 9 maintainer reliability and efficiency — accepted` for the accepted maintainer-only tranche.
- `## Candidate revision 9 Windows failure investigation — accepted` for the active correction authority and unresolved hosted obligations.
- `## Candidate revision 9 maintainer-only Windows correction — accepted` for the accepted correction and authorized hosted-rerun boundary.
- `## Candidate revision 9 corrected-source hosted execution and residual Windows investigation — accepted` for the latest hosted result, accepted root causes, and the candidate-revision-10 correction authority.
- `## Maintainer approval-response governance — accepted` for the accepted governance implementation and its preserved boundaries.
- `## Candidate revision 10 Windows correction — accepted` for the accepted correction and authorized new-session hosted-rerun boundary.
- `## Candidate revision 10 hosted certification execution — accepted` for the accepted passing hosted record and its review-only artifact boundary.
- `## Candidate revision 10 local evidence promotion — accepted` for the accepted durable evidence implementation and authorized source-publication boundary.
- `## Candidate revision 10 evidence-publication readiness — accepted as not ready` for the accepted protected-environment observations, decisive dispatch blocker, and closed publication boundary.

Read the full record before reopening a decision, changing evidence governance, or recording an accepted outcome.
