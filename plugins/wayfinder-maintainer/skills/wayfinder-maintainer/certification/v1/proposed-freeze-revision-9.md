# Wayfinder candidate revision 9 proposed freeze packet

- **Status:** Proposed; pending explicit owner approval
- **Prepared:** 2026-09-14
- **Release:** `v1-candidate-revision-9`
- **Contract status:** Frozen pending owner review
- **Release status:** Unactivated frozen
- **Runtime activation:** Disabled

## Correction scope

Revision 9 reopens revision 8 only for the approved Windows process-existence and unsupported-special-file corrections. The version-1 safety meaning is preserved.

## Exact identity

- Contract SHA-256: `3c79c6e1d2eae7c6016d789c9ade75125a2ec1dcc43f458541f9d7c63654bdd9`
- Release SHA-256: `1826fa1c1323561001565fe4bd635c0432306ced078320f1eecdad81ff268ffb`
- Fixture-index SHA-256: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`
- Expected-output-set SHA-256: `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`
- python-reference-v1 SHA-256: `f8fe1a0987a37e8a9a43003ede1bcb9eda590c88511daebaafcdd5d13932337a`
- node-v1 SHA-256: `df0f3c2a000454b2f7aaa8fcf6762b670aab34b9cb721da571fe334ae29f10ac`
- powershell-v1 SHA-256: `b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9`

## Local evidence

- Candidate report: `candidate-revision-9-local.json` (`b7c9b046d2970c308530d2ba05893213fbf81445e96c4b355a9c3863c4fe734a`), 305/305.
- Parity report: `parity-revision-9-local.json` (`3643fe1fb86a1c1fa99e7f47489e0f0c4965c56dbe86c6c01622d31887de9d4c`), all three adapters 305/305 with 900 normalized observations agreeing.
- Node.js 22.22.3 was used locally and is not the pinned Node.js 24.21.0 matrix runtime.
- No Windows or hosted matrix result is claimed; every revision-9 matrix entry remains missing.

## Approval checkpoint

- **Option A:** Accept the exact revision-9 frozen bytes and local evidence. This does not dispatch hosted certification, publish evidence, add certification entries, or activate Wayfinder.
- **Option B:** Request changes and leave revision 9 unaccepted.
