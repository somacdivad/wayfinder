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

## Active performance development plan

The owner explicitly instructed "PLEASE IMPLEMENT THIS PLAN:" on 2026-09-15 for [Faster full repository verification](../../../../../docs/plans/development/wp-4b7d5413-86e9-467b-94b3-bc111d3088e2-faster-full-verification/plan.md), approved snapshot revision 2. This named later authority permits continuous ordinary-test harness/workflow implementation, isolated branch work, commits, non-force push, one PR to candidate-revision-9-certification, and ordinary validation benchmarks. It supersedes prior no-later-project boundaries only for this plan. Keep all 305 cases per adapter; preserve serial certification/evidence/parity paths and frozen bytes. Target full hosted validation under ten minutes; pause for plan revision if two/four workers both miss the target. Local PowerShell remains unavailable. The owner checkout separately preserves the accepted approval record; unpublished prior closure history is excluded from this PR.

The owner additionally instructed "We should make it explicit in the wayfinder-maintainer skill that PRs use the PR template". This bounded delivery clarification permits explicit template guidance in the maintainer skill and PR resource and correction of draft PR #9. The benchmark source remains fixed until comparison completion; the skill guidance belongs in the subsequent task PR update. It changes no performance criteria, frozen assets, evidence or candidate facts.

Next action is implementation and verification in the isolated performance worktree. This is not implementation acceptance or merge authority. Finish local persistence before version-bound owner review in chat, then stop until owner return. Dependencies, certification/publication dispatch, accepted evidence publication/downloads, candidate reopening, activation, settings changes, main integration and unrelated work remain excluded. Embedded candidate/evidence/publication/activation facts are unchanged.

## Approval boundary

The exact implementation versions accepted in wr-0041/wr-0044 are integrated: #3 as b01e8e0b2984988092b07c2da56a4cb8cdf38dd4; #4–#6 as b5f05c64108ecf59d2e977b05e09a7083f8f8fc0, verified individually in wr-0047. The owner waived only the two timed-out #4/#5 validation jobs in wr-0046; they remain cancelled, not passed. All integration targets candidate-revision-9-certification. Mechanical closure persistence may be prepared within the approved workflow, but its new PR requires separate version-bound chat review before merging. Implementation acceptance is not reopened; no later project is authorized.

Complete reliability plan revision 17 and its sample checkpoint were approved in wr-0037/wr-0038; the chat-only correction was approved as complete revision 24 in wr-0040, preserved as snapshot revision 25. Review requests, feedback and approval stay in chat: no PR review-request comments, factual tags or review notifications. The eight earlier request/tag comments were removed at the owner's request. Historical receipts and accepted checkpoint examples remain unchanged. The explicit unchanged missing-PowerShell limitation remains unavailable, never passed. No new delegation authority. At a renewed review request finish local persistence beforehand and stop until owner return, without polling, monitoring, waiting or extra implementation.

The original Plan-to-PR Development approval in `wr-0035` and [its preserved snapshot](../../../../../docs/plans/development/wp-47a553ae-2a54-4dbe-a2dc-74c817521a08-plan-to-pr-development/approvals/revision-2.md) remain historical scope authority. Its implementation delivery in `wr-0036` is historical; wr-0041 and wr-0044 accept only the identified later versions and authorize their eligible integration.

Excluded: integration into `main`, Initialize publication/verifier correction, candidate reopening or advancement, frozen contract/adapter or evidence edits, evidence promotion/publication/downloads, certification expansion or claims, certification/publication dispatch, release/tag/registry mutations, GitHub-settings changes or bypass, authentication flows, dependencies/services/hooks/MCP additions, and live-project changes. Candidate identity, accepted evidence, publication NOT READY and dispatch-unauthorized state, empty certification registry, and disabled activation remain unchanged.

The accepted hierarchical record-store implementation and closure remain preserved in `wr-0032` through `wr-0034`; its exact 53-file accepted implementation is the separate prerequisite PR, not a reopened acceptance. The prior bounded-context/claim-integrity closure remains closed in `wr-0031`, with its final two-file record correction published as `6e3d1723fd7d3e7def68ca21ae0b0786e031b790`. Evidence-publication readiness remains accepted as NOT READY in `wr-0030`; its decisive older-verifier handoff blocker is unchanged and no publication dispatch is authorized.

## Pending action and design-record routes

All four implementation PRs are verified merged in wr-0047. Prepare the mechanical closure persistence PR from b5f05c64108ecf59d2e977b05e09a7083f8f8fc0 with records, review history and plan/routing updates only. Prepare version-bound chat request rr-73057793-2d9f-4459-bed3-f69707e04f68 after verification. Prepared intent is not delivery acknowledgment. Finish authorized local persistence before the final request, then stop completely until owner return. The overall task remains awaiting closure-artifact review/integration. No polling, monitoring, comments/tags or extra work at that handoff; all exclusions remain.

The prior chat request rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315 was delivered and approved in wr-0041; preserve it as historical and supersede for the remaining changed members. Its #3 acceptance/integration remains valid. Earlier PR-comment request rr-41e4f62c-6d9a-4687-9d44-65705905684e remains superseded; do not resend notices. Existing local receipts and approved snapshots remain immutable. Outcome/routing edits remain local and were not included in the ancestry repair. Do not push these persistence edits into the identified review heads. Any later persistence PR requires its own review.

Discover with `maintain.py record list`; read exact affected history with `record read --id ID --history`. See the [record-store guide](design-record/README.md). Routed record IDs:

- `wr-0013` for frozen identity and invalidation rules.
- `wr-0014` for adapter and parity authority.
- `wr-0015` for matrix requirements.
- `wr-0017` for hosted evidence bindings.
- `wr-0018` for current blockers.
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
- `wr-0040` for approval of complete revision 24, chat-only review communication, prior-comment removal and bounded PR #6 update; its historical no-merge boundary is superseded only for the exact wr-0041 versions.
- `wr-0041` for exact whole-stack approval of request rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315; current #4–#6 identities require renewal under wr-0042.
- `wr-0042` for verified #3 merge, GitHub-generated restacking and the initial renewed-review stop.
- `wr-0043` for file-preserving #6 ancestry repair, exact isolated verification, current unchanged diff content and renewed head-bound review.

- `wr-0044` for explicit replacement #4–#6 version approval and eligible remaining-prefix merge authority.

- `wr-0045` for the two verified CI timeouts and bounded ordinary-validation recovery proposal.

- `wr-0046` for the explicit one-off two-timeout waiver and authorized exact remaining-stack merge.

- `wr-0047` for verified integration of all remaining PRs and outstanding mechanical closure delivery.

Older maintainer chronology remains discoverable through `record list` and linked history; inactive wr-0019–wr-0024 routes are omitted from this compact reference.

Before reopening a decision, changing evidence governance, or recording an accepted outcome, read the complete affected history and decisive linked authority/evidence. Expand on conflicts or missing dependencies; unrelated chronology is not a routine prerequisite. Add new outcomes with `record add --input FILE`, and explicitly update current-state routing when acceptance or closure requires persistence.
