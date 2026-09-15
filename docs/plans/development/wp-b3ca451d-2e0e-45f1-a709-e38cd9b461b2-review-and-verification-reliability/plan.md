<!-- WAYFINDER-PLAN:BEGIN -->
```json
{"approval":{"locator":"conversation:current/review-and-verification-reliability/revision-24-chat-only-approval","quotation":"yes"},"approvalHistory":{"18":"8504aa40ba4b72e1e1f8e546ee3f5fae33476d9eb7fe44f6715e4cc9e81787c0","25":"2869d3bf1bda17e3f9de9b4504a7ccf7b6025c83d2d1d6b482d3e31668040aff"},"approvedRevision":25,"approvedSha256":"2869d3bf1bda17e3f9de9b4504a7ccf7b6025c83d2d1d6b482d3e31668040aff","format":"wayfinder-plan","id":"wp-b3ca451d-2e0e-45f1-a709-e38cd9b461b2","records":["wr-0035","wr-0036","wr-0037","wr-0038","wr-0039","wr-0040"],"revision":27,"schemaVersion":1,"slug":"review-and-verification-reliability","status":"awaiting-review","subject":"development","summary":"Reduce ambiguous PR approvals, stale review-handoff instructions, and misleading verification summaries.","title":"Review and Verification Reliability","updated":"2026-09-15"}
```
<!-- WAYFINDER-PLAN:END -->

# Review and Verification Reliability

## Problem and outcome

The session audit found competing PR approval questions, saved instructions to finish review requests after delivery, and a summary counting a skipped test as passing. Revise the existing Plan-to-PR Development stack so owners can identify what an approval covers, resumed agents can distinguish completed from uncertain delivery, and all verification summaries accurately describe results and coverage.

## Scope and authority

The owner requested planning and chose revisions to the existing PRs. The owner explicitly approved complete revision 17; snapshot revision 18 preserves its substantive body with approval metadata. Approval is recorded in wr-0037. This does not approve PRs #3–#6 for merging.

Complete-plan approval will authorize local resources, templates, CLI modules and tests, workflow/context integration, approval/progress persistence, and additional commits and non-force pushes to the existing task branches in somacdivad/wayfinder. The target remains candidate-revision-9-certification through existing native stack 7. The sample checkpoint and original CLI implementation are complete. Implement the bounded chat-only correction continuously after approval of this complete replacement, pausing for material deviations, authority gaps, required verification blockers, or new consequential uncertainty.

Final delivery includes updated PR descriptions, applicable PR CI observation, and one consolidated version-bound review request in chat. Keep review requests, feedback, and approval in chat, with no PR review-request comments, factual tags, or review notifications. Finish all authorized packet, verification, progress, and prepared-state persistence before sending the chat request. Do not fabricate a GitHub comment receipt or record acknowledgment before the chat message exists. Then stop completely until the owner returns: no polling, scheduled monitoring, active waiting, or further implementation. Separate explicit approval of final PR versions is required for eligible merging, subject to checks, protections, and dependencies. Review completion alone cannot authorize merging.

Preserve PR #3's accepted prerequisite, frozen candidate/contract/adapters, accepted history/evidence and approval snapshots, disabled activation, publication NOT READY and dispatch-unauthorized state, and empty certification registry. Excluded: main integration, Initialize correction, candidate reopening/advancement, evidence edits/promotion/publication/downloads, certification expansion/claims/dispatch, releases/tags/registry/settings changes or bypass, authentication flows, dependencies/services/hooks/MCP additions, and live-project changes. New CLI commands are local-only. No new delegation authority is requested; the lead performs this follow-up.

## Decisions and rationale

Owner decisions from this interview:

- Revise the existing PRs rather than create follow-up PRs.
- Use one consolidated request identifying all ready PRs and their exact reviewed versions. An unambiguous plain affirmative approves that set; explicit subset approval covers only named members. The current owner correction replaces per-PR notices with chat-only communication.
- Replace a packet when member commits or reviewed diffs change. Preserve the superseded packet. Prior approval remains valid only for unchanged versions explicitly covered, never for other members or changed diffs.
- Keep review requests, feedback, and approval in chat only. Do not post PR review-request comments, factual tags, or review notifications. Persist prepared local state before the final chat request, then stop. Establish whether a chat request was sent from the actual conversation on owner return; never fabricate a comment acknowledgment.
- Provide local CLI support for packet validation, receipt saving, and verification summaries. Existing GitHub tools inspect PR versions and checks within authorized work. The comment-specific delivery CLI remains for historical records and separately authorized reconciliation; no new network, authentication, or background behavior, or chat-receipt schema is introduced.
- Store approval packets and delivery receipts under each repository plan folder, outside plugins, preserving prior versions.
- Report passed, skipped, failed, and unavailable outcomes separately. Declare required checks in the plan. Missing required coverage blocks readiness; explicitly accepted environment limitations remain visible and never become passes.
- Require a sample-review checkpoint before building the CLI, then permit continuous implementation and Git/PR updates within the approved scope.
- Preserve #3; put research/templates in #4, CLI/tests in #5, and workflow/handoff integration in #6, using additional commits and non-force pushes.
- Accept the unchanged missing-PowerShell doctor limitation for this maintainer-only work without blocking review readiness. Require the remaining integrity checks and task checks to pass.

Advisory research: plugins/wayfinder-maintainer/skills/wayfinder-maintainer/resources/plan-to-pr-development/research/session-review-reliability.md. It distinguishes direct research, operational guidance, and repository adaptations. Communication grounding supports explicit referents; idempotency guidance supports distinguishing acknowledgment from uncertain side effects; Python result semantics support structured accounting. These sources do not establish one universally optimal approval packet or prove exactly-once GitHub delivery.

## CLI interfaces and durable records

Use maintain.py command groups review, delivery, and verification. Writers consume closed, versioned JSON, use standard-library dependencies, and exclusively create immutable artifacts. Expose --dry-run and expected-store digest checks on writes to existing plan histories; reads and validation use existing bounded output/completeness conventions. Reuse plan repository resolution and safe-path/concurrency discipline. Reject unknown fields, duplicate IDs, invalid references, unsafe paths, stale digests, and inconsistent state transitions. Never rewrite approval snapshots or infer authority from metadata.

Each plan folder receives reviews/<request-id>/packet.json, deliveries/<request-id>/<event-id>.json, and verification/<report-id>.json. Prior artifacts remain immutable. Supersession is a new explicit linked event under the review request, not an overwrite. Lists/projections derive from records rather than maintaining a second authoritative mutable catalog. Human summaries and the approval question render from the same validated packet or result object. Owner decision: reuse the existing wayfinder-maintainer-response JSON envelope from maintainer_output.py, including its schema version, command, response class, scope, completeness, counts, errors, and continuation fields. Put additional verification details inside data rather than introducing a parallel envelope. Human-readable check reporting follows existing PASS/FAIL/UNAVAILABLE lines and a final summary, preserving truthful outcome distinctions. This applies to the new commands and revised self-test reporting; it does not require unrelated CI commands to be rewritten.

### review create/read/validate/supersede

create takes --plan-id and --input; read and validate select --plan-id and --id; supersede takes --plan-id, --id, and --input specifying the replacement and reason. A packet binds a stable request ID, repository, approved plan revision and snapshot digest, exact owner, member PR numbers/URLs, head commits, base and merge-base identities and reviewed-diff digest, actual dependencies, required verification references, explicit limitations/exclusions, and authority requested. The generated consolidated question names the set. The chat request references that request ID and is the sole pending decision question; no PR notices are sent.

Validation is local: it checks schema, references, packet consistency, supplied observation freshness/provenance, and verification coverage; it cannot assert current GitHub state without supplied observations. On owner return, refresh platform identities through existing authorized tools. A changed head or reviewed diff makes the affected approval ineligible; replace the packet and request renewed review. Base movement with an identical reviewed diff is disclosed without inventing changed semantics. Exact algorithms and sample fields are made concrete at the checkpoint.

Owner decisions remain explicit quotations linked to the packet and named members in accepted design records, with current-state routing as required. A packet or receipt is delivery information, not an accepted decision. Multiple ambiguous pending requests require clarification; supersession cannot manufacture approval. Unchanged partial approvals may retain their original decision provenance in a replacement packet.

### delivery append/read: historical comment receipts

Preserve the existing local comment-delivery schema, immutable receipts, and its validation/reconciliation behavior. These records describe historical external operations and do not represent chat delivery or authorize new PR review-request comments, tags, or notifications. No new chat-delivery CLI schema is required for this bounded correction.

Prepare the version-bound packet, verification references, plan progress, and conditional current-state routing before sending the final chat request. Prepared intent is not delivery acknowledgment. Do not invent a comment ID/URL, claim the final message was sent before it exists, or perform post-request persistence. On owner return, read the actual conversation to establish which request was delivered before considering repetition. Preserve historical packets and receipts; supersede the prior request explicitly when preparing the replacement packet.

The owner authorized deleting all eight previously posted review-request/tag comments on PRs #3–#6. That removal is complete. Do not repost or replace them with factual notices. Accepted history, approval snapshots, and local receipts remain unchanged. Current-state routing records the correction and completed deletion without implying implementation acceptance or merge approval.

### verification capture/render

capture takes --plan-id and --input containing a structured result and provenance; render selects --plan-id and --id. Reports include command/selection, tested commit and worktree identity, runtime, timestamps, accounting units, explicit successful-test callbacks, skipped tests and reasons, expected failures, unexpected successes, failures/errors, interrupted/not-executed coverage, and required-check mappings. Framework test-case counts and subtest/fixture events are distinct; do not derive passes by subtracting arbitrary nonexclusive error lists.

Instrument canonical maintainer self-test with a standard-library structured unittest result producer, preserving subprocess isolation and the no-bytecode guarantee. Its human and JSON summaries use the same result object. Capture other known check results with explicit provenance and distinct outcome categories; no new generic shell-execution API is introduced. Produce CLI, plan, PR, and final summaries from these objects. Distinguish suite policy success, required coverage completeness, GitHub check state, and merge readiness. Invalid or incomplete reports cannot silently become successful coverage. Report artifacts are advisory verification records, not frozen accepted certification evidence.

## Implementation and PR sequence

1. Preserve PR #3, branch codex/plan-to-pr-01-record-store, and its exact accepted prerequisite bytes. No content revision or new acceptance is planned.
2. Revise PR #4, codex/plan-to-pr-02-planning, based on #3: add the advisory reliability research, resource index routing, and sample templates/record specifications. The checkpoint examples were accepted and remain unchanged. This channel correction needs no additions to #4.
3. Revise PR #5, codex/plan-to-pr-03-plan-cli, based on #4: implement local review/delivery/verification modules and commands with focused regression coverage and structured canonical self-test accounting. Keep behavior and its tests together. Existing plan and record CLI contracts and immutable history remain intact.
4. Revise PR #6, codex/plan-to-pr-04-workflow, based on #5: integrate resources, maintainer instructions, approval-response protocol, context/help/handoff entrypoints, task plan progress and current-state routing. Replace conflicting questions and stale handoff language. Deliver one consolidated chat review request for the identified versions, with no PR notices or tags.

Propagate lower-layer additions through the existing dependent branches with additional commits/non-force pushes; verify actual ancestry and per-layer/cumulative diffs. Stop the affected operation if native-stack maintenance would require unauthorized rewriting or another prohibited action. Keep the existing linear stack; no new merge group or atomic multi-PR claim is introduced. Eligible merging remains bottom-up after explicit version-bound approval and platform requirements.

## Sample-review checkpoint

Before building the CLI, present concrete artifacts and generated human output for:

1. Whole-set approval versus explicit subset approval, with one pending question.
2. A revised PR requiring renewed approval while an explicitly approved unchanged member retains provenance.
3. Historical timed-out comment submission saved as uncertain and reconciled on owner return without duplicate delivery. Preserve the accepted example unchanged; it does not instruct current chat-only delivery.
4. Passed tests with skipped or unavailable required coverage blocking readiness, contrasted with the explicitly accepted PowerShell exception.

Owner accepted this scenario set and requested no additions. The checkpoint assesses understandable approval scope, truthful delivery state, recoverable uncertainty, and accurate readiness. Acceptance permits continuous CLI/integration implementation within the complete approved plan. A requested material correction requires a facilitated one-question-per-turn revision and approval before affected work proceeds.

## Acceptance and verification

Required: repository validator; safe local artifact creation/read/validation and dry-run/concurrency checks; canonical maintainer self-test; focused conformance checks proportional to changed maintenance/package discovery surfaces; whitespace/text-profile checks; per-layer and cumulative verification; and all non-PowerShell canonical doctor checks. Run doctor before and after work using verified Python 3.11+. The owner explicitly accepts only the unchanged PowerShell-unavailable adapter-probe limitation, disclosed separately. Any new doctor failure or missing required task coverage blocks ready-for-review handoff.

Regression scenarios cover ambiguous requests, subset membership, changed head/diff, supersession provenance, stale writes and unsafe paths, uncertain and acknowledged receipt recovery, duplicate/contradictory events, genuine passed/skipped/expected-failure/unexpected-success/subtest/fixture/interrupted accounting, coverage exceptions, shared rendering, compatibility with the existing JSON envelope and human-readable reporting conventions, and zero bytecode. Use synthetic local records and test fixtures; no live comment submission or CI dispatch is needed to test mechanics.

Ready handoff requires truthful version-bound coverage, completed implementation, no missing required local coverage, updated PR descriptions/routing, and the terminal delivery process. Applicable ordinary PR CI remains a separately disclosed platform observation; pending/no checks cannot be claimed as passes. Merging additionally requires eligible platform checks and protections. No full-family certification or activation claim follows from these checks.

Never silently correct accepted historical evidence or prior approval snapshots. New factual corrections use linked records. The previous session's headline should be accurately described as 94 tests accounted for with one skipped, rather than all 94 passing.

## Risks, assumptions, and unresolved questions

Git and GitHub cannot be updated atomically. Receipts and explicit uncertain states improve recovery without promising exactly-once effects. Historical receipts remain uncommitted and immutable; retain them as factual history. Finish current local persistence before the final chat review request. Packet validation depends on truthful supplied platform observations and cannot replace owner judgment or branch protections. Structured accounting must preserve distinctions among test cases, subtests, and fixture errors.

The accepted samples expose the former field layout and validation behavior; current review guidance supersedes their PR-comment delivery instructions. Preserve the examples unchanged. Consequential schema or authority changes require owner direction. No unresolved product decision is delegated to implementation. The owner accepted the sample checkpoint in wr-0038; its implementation gate is passed. If current GitHub stack support or actual branch state conflicts with this sequence, pause rather than expanding authority.

## Execution progress

Complete revision 17 was approved with “yes”; immutable approved snapshot revision 18 and wr-0037 preserve its scope. The owner accepted the four-example checkpoint with “yes” in wr-0038. Implementation was completed and verified in wr-0039. The cumulative canonical self-test accounted for 112 cases: 111 passed and one PowerShell skip, zero bytecode. Focused Python conformance passed 2/2; repository and whitespace checks passed. The unavailable-PowerShell doctor exception remained disclosed. These are historical results for the prior implementation, not verification of a future revised commit.

The revised PR stack was pushed and the former review request rr-41e4f62c-6d9a-4687-9d44-65705905684e was delivered with four acknowledged comment receipts. The owner subsequently corrected the handoff to chat-only and authorized removing previously posted review-request/tag comments. All eight identified comments were removed successfully. Preserve historical packets, receipts, examples, and approval snapshots. Implementation acceptance and merging of PRs #3–#6 remain pending.

The owner approved complete material revision 24 with “yes”; approved snapshot revision 25 preserves its unchanged substantive body and predecessor snapshot 18. Decision wr-0040 records the chat-only correction and bounded PR #6 update. The explicit resource wording and generated handoff reminder are implemented locally. The next authorized delivery after that approval is one version-bound chat review request, with local persistence finished beforehand and a complete stop afterward until the owner returns.

## Material revision: chat-only review handoff

The owner said “No, let's just do everything in chat” after declining factual PR tags, then explicitly authorized removal of already-posted review-request comments. This revision changes the review communication channel and terminal persistence sequence, preserving all other approved scope, PR boundaries, verification requirements, limitations, and exclusions.

Draft the explicit rule in SKILL.md, workflow and approval-response references, review/implementation/CLI guidance, PR template, and current-state routing. Preserve the accepted checkpoint example and all approval snapshots byte-for-byte; explain historical comment receipt support in current guidance instead. After complete-revision approval, persist the accepted correction with current-state routing, finish these bounded integration updates in existing PR #6 with an additional commit and non-force push, and refresh its exact version-bound verification/packet. PRs #3–#5 need no changes for this channel correction. Do not poll or merge. The final handoff is a single review question here in chat, followed by a complete stop until the owner returns.

Draft acceptance criteria: agents are explicitly told to keep review requests, feedback, and approval in chat; no PR comments/tags/notifications are sent; all eight old request/tag comments are removed; historical receipts/examples/snapshots remain unchanged; persistence precedes the final chat request; no false chat acknowledgment is recorded. Required checks remain the repository validator, proportional focused checks, canonical self-test, text-profile checks, and the doctor with only the previously accepted missing-PowerShell exception.

The replacement plan was explicitly approved as complete revision 24, preserved in snapshot revision 25. The bounded implementation and renewed chat handoff are proceeding under wr-0040. Previous implementation and delivery are factual history, not current pending review questions. This complete revision supersedes the former canonical PR-comment request; approval authorizes only the bounded correction and renewed chat review delivery, not implementation acceptance or merging of PRs #3–#6.

The bounded correction updates the maintainer skill, workflow/approval/review/implementation/CLI guidance, PR template, generated development handoff and current-state routing. Canonical pre-push self-test accounts for 112 cases: 111 passed, one skipped, zero bytecode. A duplicate routing paragraph was shortened after a context-output budget regression; no budget policy or test assertion was changed. Replacement chat review request rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315 is prepared for packet creation after push and exact-version verification. Prepared intent does not assert chat delivery; final local persistence precedes the final chat request.
