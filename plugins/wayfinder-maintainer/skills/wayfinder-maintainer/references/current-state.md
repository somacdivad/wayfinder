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

The owner answered "yes" to approval of complete Review and Verification Reliability revision 17. The later named authority in `wr-0037` permits revisions to the existing Plan-to-PR Development PRs, preserving #3 unchanged: research/examples in #4, local review/delivery/verification CLI and tests in #5, and workflow/handoff integration in #6. The target remains somacdivad/wayfinder, candidate-revision-9-certification, through native stack 7. Read the [approved reliability snapshot](../../../../../docs/plans/development/wp-b3ca451d-2e0e-45f1-a709-e38cd9b461b2-review-and-verification-reliability/approvals/revision-18.md) and current plan with `maintain.py plan read --id wp-b3ca451d-2e0e-45f1-a709-e38cd9b461b2 --history`. Snapshot revision 18 adds approval metadata to the unchanged substantive plan reviewed as revision 17. This is plan approval, not implementation acceptance or approval/merge of PRs #3–#6.

The owner accepted the four synthetic sample scenarios in wr-0038. The sample checkpoint is passed; continuous CLI implementation and integration within the approved plan may proceed. After that checkpoint, continuous implementation includes additional commits, non-force pushes, PR updates, applicable PR CI observations, and terminal review delivery. No new delegation authority is requested. Pause for material revisions, insufficient authority, required verification blockers, or unavailable native-stack support. The owner explicitly accepts only the unchanged unavailable-PowerShell doctor limitation for this maintainer-only work; disclose it separately and never label it passed.

The owner's later correction is chat-only: review requests, feedback, and approval remain in chat, with no PR review-request comments, factual tags, or review notifications. The owner also explicitly authorized removing the already-posted review-request comments; all eight identified request/tag comments on PRs #3–#6 were removed. Existing local receipts and accepted history remain historical. The owner approved complete replacement plan revision 24 with “yes”, recorded in wr-0040 and preserved in approved snapshot revision 25. This permits the bounded integration update to PR #6, its additional commit/non-force push and renewed chat review request, preserving #3–#5 unchanged. This does not approve implementation or merging. Finish authorized local persistence before a final chat request, then stop completely until the owner returns: no polling, scheduled monitoring, active waiting, or further implementation. Separate explicit final-version approval permits eligible bottom-up merging subject to checks, protections, and dependencies. Review completion alone is not approval.

The original Plan-to-PR Development approval in `wr-0035` and [its preserved snapshot](../../../../../docs/plans/development/wp-47a553ae-2a54-4dbe-a2dc-74c817521a08-plan-to-pr-development/approvals/revision-2.md) remain historical scope authority. Its implementation delivery in `wr-0036` remains unaccepted and unmerged; the named later reliability plan authorizes only the specified revisions and updated review handoff.

Excluded: integration into `main`, Initialize publication/verifier correction, candidate reopening or advancement, frozen contract/adapter or evidence edits, evidence promotion/publication/downloads, certification expansion or claims, certification/publication dispatch, release/tag/registry mutations, GitHub-settings changes or bypass, authentication flows, dependencies/services/hooks/MCP additions, and live-project changes. Candidate identity, accepted evidence, publication NOT READY and dispatch-unauthorized state, empty certification registry, and disabled activation remain unchanged.

The accepted hierarchical record-store implementation and closure remain preserved in `wr-0032` through `wr-0034`; its exact 53-file accepted implementation is the separate prerequisite PR, not a reopened acceptance. The prior bounded-context/claim-integrity closure remains closed in `wr-0031`, with its final two-file record correction published as `6e3d1723fd7d3e7def68ca21ae0b0786e031b790`. Evidence-publication readiness remains accepted as NOT READY in `wr-0030`; its decisive older-verifier handoff blocker is unchanged and no publication dispatch is authorized.

## Pending action and design-record routes

Plan-to-PR Development is implemented, unaccepted and unmerged. Read wr-0035 for scope, wr-0036 for factual delivery and limitations, and `maintain.py plan read --id wp-47a553ae-2a54-4dbe-a2dc-74c817521a08 --history` for its living plan and preserved approval. Native stack 7 orders [#3](https://github.com/somacdivad/wayfinder/pull/3), [#4](https://github.com/somacdivad/wayfinder/pull/4), [#5](https://github.com/somacdivad/wayfinder/pull/5), and [#6](https://github.com/somacdivad/wayfinder/pull/6) toward candidate-revision-9-certification. The later reliability approval and accepted sample checkpoint are in wr-0037/wr-0038; chat-only correction authority is in wr-0040. Historical local verification retained only the unavailable-PowerShell doctor baseline; old pending-CI observations are not current check results. Preserve all exclusions above. After the final chat request stop until owner return; review completion alone is not merge approval.

Review and Verification Reliability is plan-approved; its four-example checkpoint is owner-accepted in wr-0038. The four synthetic examples are prepared in [reliability checkpoint examples](../resources/plan-to-pr-development/reliability-checkpoint-examples.md). Implementation is complete and verified in wr-0039. The prior request rr-41e4f62c-6d9a-4687-9d44-65705905684e was delivered through PR comments; those comments have now been removed at the owner's explicit request. Preserve its packet and receipts as historical facts and do not resend its notices. Complete material plan revision 24 is owner-approved in wr-0040, preserved as approved snapshot revision 25. The bounded chat-only integration update is implemented locally. Replacement request rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315 is prepared for packet creation and final chat delivery after the approved push and exact-version verification. Prepared state does not assert delivery; on owner return read the actual conversation and packet before repeating a request. Stop after the final chat request until the owner returns. Read `wr-0037`, `wr-0040` and the reliability plan history for the exact authority.

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
- `wr-0035` for the approved Plan-to-PR Development project, superseding named implementation authority, PR target and preserved exclusions.
- `wr-0036` for implemented delivery, exact prerequisite preservation, native stack, local checks, unavailable/runtime and pending-CI limitations, and prior owner-review stop; not implementation acceptance or closure.
- `wr-0037` for the approved reliability revision plan, exact existing-PR allocation, pending sample checkpoint, local-only CLI, required reporting conventions, PowerShell exception, terminal receipts/stop, and separate final-version merge approval.
- `wr-0038` for explicit sample-checkpoint acceptance, superseding the prior pending checkpoint and permitting continuous implementation under wr-0037, without PR approval or merging.
- `wr-0039` for completed reliability implementation, exact local verification and reporting correction, and former renewed review; not implementation acceptance, CI success or merge authority.
- `wr-0040` for approval of complete revision 24, chat-only review communication, completed removal of eight prior request/tag comments, preserved historical receipts/examples, bounded PR #6 update, pre-request persistence/stop and no PR merge approval.

Before reopening a decision, changing evidence governance, or recording an accepted outcome, read the complete affected history and decisive linked authority/evidence. Expand on conflicts or missing dependencies; unrelated chronology is not a routine prerequisite. Add new outcomes with `record add --input FILE`, and explicitly update current-state routing when acceptance or closure requires persistence.
