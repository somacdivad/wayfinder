# Wayfinder current maintainer state

> Compact routing reference. `maintain.py doctor` validates these facts against the package, accepted evidence, and chronological record.

## Current identity

- Candidate: `v1-candidate-revision-9` (contract `frozen`, release `unactivated-frozen`).
- Activation: **disabled**. The runtime skill remains non-operational.
- Contract: `3c79c6e1d2eae7c6016d789c9ade75125a2ec1dcc43f458541f9d7c63654bdd9`.
- Release: `1826fa1c1323561001565fe4bd635c0432306ced078320f1eecdad81ff268ffb`.
- Fixture index: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`; expected-output set: `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`.
- Registered adapters: `python-reference-v1` `f8fe1a0987a37e8a9a43003ede1bcb9eda590c88511daebaafcdd5d13932337a`, `node-v1` `df0f3c2a000454b2f7aaa8fcf6762b670aab34b9cb721da571fe334ae29f10ac`, `powershell-v1` `b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9`.
- Historical revision-8 accepted parity evidence: `parity-revision-8-local.json` `28bc61ede21e0b8041c1951b1327c948642d0712170048f17ce2bab9653562ef`, `parity-revision-8-local.md` `840641fd2b2814104a78f7fe0d4106ac70c4688056237003770d7ec7874e97c0`.
- Historical revision-8 accepted macOS matrix evidence: `matrix-revision-8-python-reference-v1-macos-20260914T125208Z.json` `6b43c2f0b41e83d76218e363651d6353ab62561426e4c7abf997cb561aa3fd78`, `matrix-revision-8-python-reference-v1-macos-20260914T125208Z.md` `8a81084ab64a18bac8d59694bc81233035cc0f02434a36d8106dfc0f2cc1c11c`.
- Accepted revision-9 local evidence, proposal, and freeze acceptance: `candidate-revision-9-local.json` `b7c9b046d2970c308530d2ba05893213fbf81445e96c4b355a9c3863c4fe734a`, `candidate-revision-9-local.md` `99a5ef242b1e96e966d1fe9cff3549565008520451921bc1e9d7abfc3237d264`, `freeze-acceptance-revision-9.json` `a934affb933fac7ad994257453afda952b6e81d7852e791f60389ebce4767088`, `freeze-acceptance-revision-9.md` `2f0c4bb8859bb3f7f0356038922678673544ddf45907bcdb680670813a581691`, `parity-revision-9-local.json` `3643fe1fb86a1c1fa99e7f47489e0f0c4965c56dbe86c6c01622d31887de9d4c`, `parity-revision-9-local.md` `11f3f7436b96c2be98e5efeb8fb2fb29bb373ba8826ea38b0594aeba806c00f5`, `proposed-freeze-revision-9.json` `9baf19c1f17848b7f0b1b12ff0e821472358f2aadde3dafa4f423194cb5e916c`, `proposed-freeze-revision-9.md` `b75d8862b47a16b13c4862643e7551d44777c98348cd9608f5c5aebd1ff8855f`.
- Accepted historical evidence is hash-pinned by [`historical-sha256.json`](../certification/v1/historical-sha256.json).

## Approval boundary

The owner accepted the exact candidate-revision-9 maintainer-only Windows correction and separately authorized a full eight-entry hosted rerun. Acceptance preserves all frozen governed, registered-adapter, and accepted-evidence bytes and does not itself certify Windows or the adapter family, promote evidence, add a release-certification entry, activate Wayfinder, begin forward testing or cross-adapter recovery, add runtime guidance, or initialize a live project. Hosted execution must use one exact published source commit. The owner subsequently clarified that the authorized publication scope is every modified and untracked path present in the candidate-revision-9 certification worktree at the start of the hosted tranche.

## Pending action and design-record routes

Publish the complete owner-authorized dirty worktree as one exact commit on candidate-revision-9-certification, dispatch the full eight-entry hosted rerun from that commit, preserve outputs as review-only, and report the strict aggregate.

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

Read the full record before reopening a decision, changing evidence governance, or recording an accepted outcome.
