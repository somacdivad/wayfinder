# Local review and verification CLI

Read for review-packet preparation, final delivery, or owner-return reconciliation. These records belong to repository plans under docs/plans, outside installed plugins. They are not accepted certification evidence or mutable candidate authority. Commands never use the network, send comments, authenticate approval, execute supplied shell commands, commit, or merge.

Current review handoff is chat-only: no PR review-request comments, factual tags, or review notifications. Use review packets and verification reports to prepare the final chat request. Complete local persistence before sending, then stop until the owner returns. The delivery command's comment ID/URL schema remains available for historical receipt inspection and separately authorized reconciliation; it does not represent chat delivery and grants no permission to send new comments. Establish chat delivery from the actual conversation on owner return, without fabricating a comment receipt.

## Commands

Use maintain.py with Python 3.11+. Inspect selected help. All commands require --plan-id; readers accept --format summary|full|json, --max-bytes, and --cursor. JSON uses maintainer_output.py's existing wayfinder-maintainer-response envelope; human check reporting uses PASS/FAIL/UNAVAILABLE and a final summary.

| Command | Additional selectors/input |
| --- | --- |
| review create | --input FILE [--dry-run] |
| review read | --id REQUEST_ID |
| review validate | --id REQUEST_ID [--observations FILE] |
| review supersede | --id REQUEST_ID --input FILE [--dry-run] |
| delivery append | --request-id REQUEST_ID --input FILE [--dry-run] |
| delivery read | --request-id REQUEST_ID |
| verification capture | --input FILE [--dry-run] |
| verification render | --id REPORT_ID |

Writes require --expected-store-sha256 once artifact history exists. Obtain storeSha256 from a complete read, reconcile facts, then use the same expected digest for preview/apply. Creates are exclusive. No overwrite, auto-retry, or lock stealing. Active/unfinished writers fail closed; after interruption inspect retained lock/staging and any published artifact before authorized recovery. Dry-run creates no managed files. Write output must fit its budget before any mutation; writes reject cursors.

Reader chunks expose ordered UTF-8 ranges, full-source digest and digest-bound continuation. Concatenate data.text chunks and verify sourceSha256 before relying on incomplete output. A final complete chunk alone does not reconstruct preceding chunks. Store changes, selector changes, and non-boundary cursors fail. An unsatisfied readiness validation returns 1; invalid input/incomplete output returns 2; successful complete reads/writes return 0. Reading an unsuccessful report is still a successful read, not successful verification.

## Closed schemas

The preserved [checkpoint examples](reliability-checkpoint-examples.md) are historical synthetic templates. Their former comment/tag handoff is superseded by current chat-only review guidance; do not submit their fictitious identities. Artifact schemaVersion is 1. IDs use nonzero canonical lowercase UUIDs with rr (request), rs (supersession), de (delivery event), or vr (verification) prefixes. Plan IDs retain wp. Dates include a timezone. Git commit identities support lowercase 40/64-digit hex; content digests use SHA-256. Unknown/missing/duplicate JSON fields are errors.

- Packet: format, schemaVersion, id, planId, approvedPlanRevision, approvedPlanSha256, repository, owner, members, verificationIds, limitations, exclusions, requestedAuthority, observedAt. Each member contains number, url, headCommit, baseCommit, mergeBaseCommit, reviewedDiffSha256, dependencies. Dependencies refer to preceding members. Optional retainedApprovals contains memberNumber, requestId, recordId. Retention requires unchanged head/diff and an accepted decision with explicit authority and source review-request:REQUEST_ID/member:NUMBER; a plan approval is insufficient. The caller must substantiate the actual owner decision; the script validates references, not authenticity.
- Supersession: format, schemaVersion, id, requestId, replacementRequestId, reason, at. Create the replacement first, then supersede the prior packet. Until only one active packet remains for the plan, validation blocks review readiness. Prior packets/events stay immutable; cycles and competing replacements fail.
- Delivery: format, schemaVersion, id, requestId, memberNumber, headCommit, operationMarker, phase, at, reason, commentId, commentUrl. Marker is REQUEST_ID/NUMBER/HEAD. Optional reconcilesEventId links an earlier matching uncertain event. Phases are prepared, attempted, acknowledged, failed-with-known-no-effect, uncertain. Only acknowledgment carries comment ID/URL; URLs must match repository/member/ID. Attempts need prepared intent or known-no-effect reconciliation. Uncertainty requires explicit reconciliation before retry. Acknowledged delivery cannot be retried or contradicted.
- Verification: format, schemaVersion, id, planId, provenance, results, suiteSuccessful, coverage, requiredCoverageComplete, readyForReview, bytecodeArtifacts. Provenance has command, selection, testedCommit, worktreeSha256, runtime, startedAt, finishedAt. Results has unit=test-case, testsRun, passed, skipped, expectedFailures, unexpectedSuccesses, caseFailures, caseErrors, subtestEvents, fixtureErrors, interrupted, skipReasons. Event fields are unit, id, outcome, detail. Coverage entries have checkId, outcome, required, exception; exceptions have locator and reason supplied from an explicit owner-accepted plan limitation. Coverage outcomes are passed, failed, skipped, unavailable, pending, not-executed. Exception assertions must be verified against the exact plan/owner authority by the agent; schema validation is not owner acceptance. Only skipped/unavailable checks may carry exceptions. No report can infer broader exemptions.

Capture consumes structured results, never executes provenance.command. Canonical self-test directly captures unittest successful/skip/expected-failure/unexpected-success callbacks; subtests and fixtures remain separate events. testsRun is a framework count, not a discovered-file count. Passes are never computed by subtracting error-list lengths. Suite success, local required coverage, platform checks and merge eligibility remain distinct. Missing/interrupted required coverage blocks readiness; explicit environment exceptions remain visible as unavailable/skipped, never pass.

## Storage and authority

A plan folder receives reviews/REQUEST_ID/packet.json and rs-ID.json supersession events, deliveries/REQUEST_ID/de-ID.json events, and verification/vr-ID.json reports. Prior records are immutable. Derived views and store hashes are not a second mutable catalog. Plan/record operations and integrity checks recognize and validate these auxiliary artifacts.

Packets bind exact approved-plan snapshots and verification references. Read/validate renders one request from the same packet that supplies its version summary. All member commits need referenced ready verification reports; no owner approval or current platform eligibility is inferred. Optional local observations contain repository, observedAt, members with number/headCommit/baseCommit/mergeBaseCommit/reviewedDiffSha256, covering the exact set. Refresh those observations through existing tools on owner return. Changed head or diff requires renewed approval even with unchanged GitHub review badges. Base movement with identical diff is disclosed and rechecked.

Design records retain explicit decisions and closure; current state alone retains current authorization and candidate facts. Do not interpret an acknowledgment, a ready report, receipt, packet or retained-decision shape as new approval. Supersede changed requests and clarify multiple ambiguous questions. Final delivery and owner-return inspection remain governed by the approved plan, not this local CLI.
