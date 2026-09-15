# Wayfinder current maintainer state

> Compact routing reference. `maintain.py doctor` validates these facts against the package, accepted evidence, and chronological record.

<!-- WAYFINDER-STATUS-OBJECT:BEGIN -->
```json
{
  "format": "wayfinder-maintainer-status",
  "schemaVersion": 1,
  "asOf": "2026-09-14",
  "requirements": {"maintainerPythonMinimum": "3.11"},
  "candidate": {
    "releaseId": "v1-candidate-revision-10",
    "candidateRevision": 10,
    "packageVersion": "1.0.0-rc.10",
    "contractStatus": "frozen",
    "releaseStatus": "unactivated-frozen",
    "activation": "disabled",
    "contractSha256": "0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341",
    "releaseSha256": "581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083"
  },
  "conformance": {"caseCount": 305},
  "hostedEvidence": {
    "exists": true,
    "accepted": true,
    "runId": "34921918384",
    "attempt": "1",
    "sourceCommit": "82a2bb994e7ef8d2ffda7317e0687b0c7230aa54",
    "path": "plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/hosted/run-34921918384-attempt-1",
    "fileCount": 27,
    "matrixEntries": 8,
    "casesPerEntry": 305,
    "aggregateJsonSha256": "be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50",
    "aggregateMarkdownSha256": "ffe1fe3dc6ae9ed1b21356943ea8f98451221a5e8248043d74cf21c5a0b3cf18",
    "matrixSha256": "2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0"
  },
  "publication": {
    "readiness": "not-ready",
    "dispatchAuthorized": false,
    "published": false,
    "sourcePublicationCommit": "72da3542f3a7e65f4bcae09943612d8ba09daf3e",
    "blockerCode": "workflow-verifier-handoff",
    "checkedOutSourceCommit": "82a2bb994e7ef8d2ffda7317e0687b0c7230aa54",
    "verifierCandidateRevision": 9,
    "missingArguments": ["--expected-run-id", "--expected-attempt"],
    "failureStage": "argument-parsing-before-draft-release"
  },
  "releaseRegistry": {"updated": false, "certificationEntries": 0},
  "runtimes": [
    {"adapterId": "python-reference-v1", "implementation": "CPython", "version": "3.14.7", "operatingSystems": ["macOS", "Linux", "Windows"]},
    {"adapterId": "node-v1", "implementation": "Node.js", "version": "24.21.0", "operatingSystems": ["macOS", "Linux", "Windows"]},
    {"adapterId": "powershell-v1", "implementation": "PowerShell", "version": "7.6.6", "operatingSystems": ["Windows", "Linux"]}
  ],
  "claims": {"fullFamilyCertification": false, "crossAdapterRecovery": false}
}
```
<!-- WAYFINDER-STATUS-OBJECT:END -->

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

The owner authorized the hierarchical maintainer design-record plan and instructed "Implement the proposed plan." The bounded local scope is history migration, subject folders, `record list/read/add`, the compatible `record-section` reader, affected-history reading policy, durable outcome/closure routing, discovery documentation, integrity validation, and maintainer tests. This later named instruction supersedes the prior no-later-tranche boundary only for this task. The owner subsequently answered "Yes" to the exact implementation-acceptance question. The reviewed migration and CLI implementation are accepted and closed in `wr-0034`; acceptance grants only durable acceptance/closure persistence and no later tranche. No commits, pushes, network actions, dependencies, workflow/verifier correction, certification expansion, frozen contract/adapter or accepted-evidence edits, runtime guidance changes, activation, or live-project changes are authorized.

The bounded-context and claim-integrity tranche, its acceptance record, and both local commits are closed. The separate two-file closure-record correction was committed and pushed as `6e3d1723fd7d3e7def68ca21ae0b0786e031b790`. Record `wr-0031` preserves that prior closure and its exact boundaries; do not request closure of that tranche again.

The owner explicitly accepted the exact four-file candidate-revision-10 evidence-publication readiness acceptance-record implementation. The recorded protected-environment readiness result is NOT READY. No evidence-publication dispatch is authorized. The decisive blocker is that publish-evidence.yml at source-publication commit 72da3542f3a7e65f4bcae09943612d8ba09daf3e checks out evidence source commit 82a2bb994e7ef8d2ffda7317e0687b0c7230aa54 before invoking scripts/prepare_evidence_release.py; that older verifier lacks --expected-run-id and --expected-attempt, targets revision 9, and would fail argument parsing before draft-release creation. Acceptance records this not-ready result only and authorizes no workflow or verifier correction, GitHub-settings change, workflow dispatch, artifact download, release or tag mutation, release-registry or runtime-guidance change, activation, or later tranche.

## Pending action and design-record routes

The hierarchical maintainer design-record implementation is owner-accepted and closed. Design authorization is recorded in `wr-0032`, implementation verification in `wr-0033`, and accepted implementation and terminal closure in `wr-0034`. No implementation-acceptance or closure decision remains pending; do not request acceptance of this same closure again. Provide the terminal read-only verification handoff and stop without beginning it or another task automatically. Evidence publication remains NOT READY and not dispatch-eligible. Do not mutate Git or the network, begin an authentication flow, download artifacts, dispatch workflows, correct the publication workflow/verifier, modify GitHub settings, publish or alter releases/tags, change the release registry, candidate identity, runtime guidance or activation, edit frozen contract/adapters or any evidence, add dependencies, touch live-project data, or begin another tranche.

Discover with `maintain.py record list`; read exact affected history with `record read --id ID --history`. See the [record-store guide](design-record/README.md). Routed record IDs:

- `wr-0013` for frozen identity and invalidation rules.
- `wr-0014` for adapter and parity authority.
- `wr-0015` for matrix requirements.
- `wr-0017` for hosted evidence bindings.
- `wr-0018` for current blockers.
- `wr-0019` for the current maintainer workflow and tooling baseline.
- `wr-0020` for the current implementation and approval boundary.
- `wr-0021` for the accepted bounded hosted result.
- `wr-0022` for the accepted maintainer-only tranche.
- `wr-0023` for the active correction authority and unresolved hosted obligations.
- `wr-0024` for the accepted correction and authorized hosted-rerun boundary.
- `wr-0025` for the latest hosted result, accepted root causes, and the candidate-revision-10 correction authority.
- `wr-0026` for the accepted governance implementation and its preserved boundaries.
- `wr-0027` for the accepted correction and authorized new-session hosted-rerun boundary.
- `wr-0028` for the accepted passing hosted record and its review-only artifact boundary.
- `wr-0029` for the accepted durable evidence implementation and authorized source-publication boundary.
- `wr-0030` for the accepted protected-environment observations, decisive dispatch blocker, and closed publication boundary.
- `wr-0031` for the accepted 17-file implementation, two-local-commit authority, verification limitations, preserved invariants, deferred work, and final closure boundary.

- `wr-0032` for the historical hierarchical record-store design and implementation authorization, superseded by the accepted closure in `wr-0034`.
- `wr-0033` for the completed migration and CLI verification and unavailable PowerShell limitation; its historical pending acceptance is superseded by `wr-0034`.
- `wr-0034` for the accepted reviewed migration and implementation, persisted terminal closure, and no-later-tranche boundary.

Before reopening a decision, changing evidence governance, or recording an accepted outcome, read the complete affected history and decisive linked authority/evidence. Expand on conflicts or missing dependencies; unrelated chronology is not a routine prerequisite. Add new outcomes with `record add --input FILE`, and explicitly update current-state routing when acceptance or closure requires persistence.
