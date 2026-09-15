<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[{"locator":"conversation:current/rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315/whole-stack-implementation-approval","quotation":"yes, I approve"}],"candidateRevision":null,"date":"2026-09-15","format":"wayfinder-design-record","id":"wr-0041","kind":"decision","legacy":null,"outcome":"accepted","predecessors":["wr-0040"],"schemaVersion":1,"sources":["record:wr-0037","record:wr-0040","file:docs/plans/development/wp-b3ca451d-2e0e-45f1-a709-e38cd9b461b2-review-and-verification-reliability/reviews/rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315/packet.json","review-request:rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315/member:3","review-request:rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315/member:4","review-request:rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315/member:5","review-request:rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315/member:6"],"summary":"Owner accepted request rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315 for PRs #3–#6, authorizing eligible bottom-up merging under checks and protections.","title":"Owner approved exact Plan-to-PR stack versions","topic":"governance"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Owner approved exact Plan-to-PR stack versions

The owner answered “yes, I approve” to the single unresolved chat question approving the exact four versions below for eligible bottom-up merging into candidate-revision-9-certification, subject to checks and protections. This accepts the identified implementation, not any later changed head/diff or new closure artifact.

Request: rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315. Immutable packet SHA-256: d1b4386c7958a12d1865cb221aa9d0970b5ea38928f1e87f35bc5adafe6d1974. Approved development plan snapshot revision 25: 2869d3bf1bda17e3f9de9b4504a7ccf7b6025c83d2d1d6b482d3e31668040aff.

- PR #3: head `53c954422b394a8bb468962eb3208bb158d1382b`, base `6e3d1723fd7d3e7def68ca21ae0b0786e031b790`, merge base `6e3d1723fd7d3e7def68ca21ae0b0786e031b790`, reviewed diff SHA-256 `9282822044774d3def10795d04dcce11af2fb33063d4500718ab5885811b2d02`.
- PR #4: head `7cecf1f137b7f05aaf00d0068c168ec6c30544ab`, base `53c954422b394a8bb468962eb3208bb158d1382b`, merge base `53c954422b394a8bb468962eb3208bb158d1382b`, reviewed diff SHA-256 `38d9867d619d6966cb79422a8884435be1b9a58b641cfb4ab9c81aa7d0b10f7a`.
- PR #5: head `ab98b2197a74ed6adfc10cc46b899057e4e4cd8c`, base `7cecf1f137b7f05aaf00d0068c168ec6c30544ab`, merge base `7cecf1f137b7f05aaf00d0068c168ec6c30544ab`, reviewed diff SHA-256 `845faa0f17e467b8c9d2fffd693586002371e1e2487f99d5b6153a83d2e4f7db`.
- PR #6: head `6615c68c162208ee62fed401282b3c55a02f541f`, base `ab98b2197a74ed6adfc10cc46b899057e4e4cd8c`, merge base `ab98b2197a74ed6adfc10cc46b899057e4e4cd8c`, reviewed diff SHA-256 `b8d0ddb0c46509fa47f4bc0b3908c330818565739aa403cd1aa185e1e43891ea`.

Approval grants only eligible bottom-up merging of these versions through native stack 7 in somacdivad/wayfinder. Preserve repository merge requirements; do not bypass protections or settings. Changed head or reviewed diff requires renewed approval for the affected member. Base/merge-base movement with identical reviewed diff must be disclosed and rechecked, and does not manufacture approval for changed semantics. Use the documented asynchronous stack-aware merge interface with expected heads and the repository-supported merge method/action. Verify actual outcomes before recording integration.

The accepted local verification accounts for 112 tests: 111 passed, one PowerShell skip, zero bytecode; focused checks pass 2/2; repository/whitespace validation pass; doctor retains only the explicit unchanged unavailable-PowerShell exception. Ordinary GitHub checks are separate current observations: #3–#5 validation was passing, #6 pending at owner-return inspection. No pending check is claimed passed and no new certification follows.

Persist actual integration and required closure through the plan/record CLI with explicit current-state routing. If persistence needs a new PR, creating the mechanical closure artifact is within the approved workflow, but merging it requires its own version-bound chat review. Do not change the reviewed PR heads to carry this record before merging. Review communication remains chat-only; stop at any renewed review handoff until owner return.

All packet exclusions remain: main integration, Initialize correction, candidate reopening/advancement, frozen assets/accepted evidence edits/promotion/publication/downloads, certification expansion/claims/dispatch, publication/activation/releases/tags/registry changes, GitHub-settings/protection bypass, authentication/dependencies/services/hooks/MCP and live-project changes. No later project is authorized.
