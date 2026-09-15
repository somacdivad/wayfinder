<!-- WAYFINDER-PLAN:BEGIN -->
```json
{"approval":{"locator":"conversation:current/review-and-verification-reliability/revision-17-approval","quotation":"yes"},"approvalHistory":{"18":"8504aa40ba4b72e1e1f8e546ee3f5fae33476d9eb7fe44f6715e4cc9e81787c0"},"approvedRevision":18,"approvedSha256":"8504aa40ba4b72e1e1f8e546ee3f5fae33476d9eb7fe44f6715e4cc9e81787c0","format":"wayfinder-plan","id":"wp-b3ca451d-2e0e-45f1-a709-e38cd9b461b2","records":["wr-0035","wr-0036","wr-0037","wr-0038"],"revision":20,"schemaVersion":1,"slug":"review-and-verification-reliability","status":"implementing","subject":"development","summary":"Reduce ambiguous PR approvals, stale review-handoff instructions, and misleading verification summaries.","title":"Review and Verification Reliability","updated":"2026-09-15"}
```
<!-- WAYFINDER-PLAN:END -->

# Review and Verification Reliability

## Problem and outcome

The session audit found competing PR approval questions, saved instructions to finish review requests after delivery, and a summary counting a skipped test as passing. Revise the existing Plan-to-PR Development stack so owners can identify what an approval covers, resumed agents can distinguish completed from uncertain delivery, and all verification summaries accurately describe results and coverage.

## Scope and authority

The owner requested planning and chose revisions to the existing PRs. The owner explicitly approved complete revision 17; snapshot revision 18 preserves its substantive body with approval metadata. Approval is recorded in wr-0037. This does not approve PRs #3–#6 for merging.

Complete-plan approval will authorize local resources, templates, CLI modules and tests, workflow/context integration, approval/progress persistence, and additional commits and non-force pushes to the existing task branches in somacdivad/wayfinder. The target remains candidate-revision-9-certification through existing native stack 7. Prepare the sample checkpoint first; continue CLI implementation only after its explicit acceptance. Thereafter implement continuously, pausing for material deviations, authority gaps, required verification blockers, or new consequential uncertainty.

Final delivery includes updated PR descriptions, applicable PR CI observation, one consolidated version-bound review request, per-PR factual owner tags, and immediately saving returned comment IDs/URLs or an uncertain outcome. Then stop completely until the owner returns: no polling, scheduled monitoring, active waiting, or further implementation. Separate explicit approval of final PR versions is required for eligible merging, subject to checks, protections, and dependencies. Review completion alone cannot authorize merging.

Preserve PR #3's accepted prerequisite, frozen candidate/contract/adapters, accepted history/evidence and approval snapshots, disabled activation, publication NOT READY and dispatch-unauthorized state, and empty certification registry. Excluded: main integration, Initialize correction, candidate reopening/advancement, evidence edits/promotion/publication/downloads, certification expansion/claims/dispatch, releases/tags/registry/settings changes or bypass, authentication flows, dependencies/services/hooks/MCP additions, and live-project changes. New CLI commands are local-only. No new delegation authority is requested; the lead performs this follow-up.

## Decisions and rationale

Owner decisions from this interview:

- Revise the existing PRs rather than create follow-up PRs.
- Use one consolidated request identifying all ready PRs and their exact reviewed versions. An unambiguous plain affirmative approves that set; explicit subset approval covers only named members. Per-PR notices introduce no competing decision questions.
- Replace a packet when member commits or reviewed diffs change. Preserve the superseded packet. Prior approval remains valid only for unchanged versions explicitly covered, never for other members or changed diffs.
- Save returned review-comment IDs and URLs within the terminal handoff, then stop. An uncertain submission is saved as uncertain and stops delivery. Reconcile whether the comment exists on owner return before considering any resend.
- Provide local CLI support for packet validation, receipt saving, and verification summaries. Existing GitHub tools submit comments and check delivery on owner return; no new network, authentication, or background behavior.
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

create takes --plan-id and --input; read and validate select --plan-id and --id; supersede takes --plan-id, --id, and --input specifying the replacement and reason. A packet binds a stable request ID, repository, approved plan revision and snapshot digest, exact owner, member PR numbers/URLs, head commits, base and merge-base identities and reviewed-diff digest, actual dependencies, required verification references, explicit limitations/exclusions, and authority requested. The generated consolidated question names the set. Each PR notice references that same request ID and contains no independent approval question.

Validation is local: it checks schema, references, packet consistency, supplied observation freshness/provenance, and verification coverage; it cannot assert current GitHub state without supplied observations. On owner return, refresh platform identities through existing authorized tools. A changed head or reviewed diff makes the affected approval ineligible; replace the packet and request renewed review. Base movement with an identical reviewed diff is disclosed without inventing changed semantics. Exact algorithms and sample fields are made concrete at the checkpoint.

Owner decisions remain explicit quotations linked to the packet and named members in accepted design records, with current-state routing as required. A packet or receipt is delivery information, not an accepted decision. Multiple ambiguous pending requests require clarification; supersession cannot manufacture approval. Unchanged partial approvals may retain their original decision provenance in a replacement packet.

### delivery append/read

append takes --plan-id, --request-id, and --input; read uses the same selectors. Events identify the request/member/version, operation marker, time, and phase: prepared, attempted, acknowledged, failed-with-known-no-effect, or uncertain. Acknowledgments require returned comment IDs/URLs and the submitted version. Contradictory outcomes fail validation; later reconciliation appends a linked observation rather than rewriting an uncertain event.

Persist prepared intent before sending. Save attempted facts when known, and acknowledgments immediately after successful submission. A timeout or lost response is uncertain, not proof of no effect. Stop on uncertain delivery. On owner return, inspect actual comments using existing tools and the stable marker; append reconciliation facts before considering a resend. A marker assists discovery but provides neither GitHub server-side idempotency nor an exactly-once guarantee. The lead is the single delivery writer. Receipt persistence never authorizes an extra network request, commit, push, or background action after the terminal stop.

Current-state routing distinguishes implementation complete, delivery prepared, and delivery acknowledged/uncertain; it avoids an unconditional stale imperative to finish requests. Local terminal receipts remain available across sessions even when not pushed. If receipt persistence itself fails after a successful submission, retain the tool acknowledgment in the session handoff and stop; reconcile before further delivery. Do not claim a receipt was saved when it was not.

### verification capture/render

capture takes --plan-id and --input containing a structured result and provenance; render selects --plan-id and --id. Reports include command/selection, tested commit and worktree identity, runtime, timestamps, accounting units, explicit successful-test callbacks, skipped tests and reasons, expected failures, unexpected successes, failures/errors, interrupted/not-executed coverage, and required-check mappings. Framework test-case counts and subtest/fixture events are distinct; do not derive passes by subtracting arbitrary nonexclusive error lists.

Instrument canonical maintainer self-test with a standard-library structured unittest result producer, preserving subprocess isolation and the no-bytecode guarantee. Its human and JSON summaries use the same result object. Capture other known check results with explicit provenance and distinct outcome categories; no new generic shell-execution API is introduced. Produce CLI, plan, PR, and final summaries from these objects. Distinguish suite policy success, required coverage completeness, GitHub check state, and merge readiness. Invalid or incomplete reports cannot silently become successful coverage. Report artifacts are advisory verification records, not frozen accepted certification evidence.

## Implementation and PR sequence

1. Preserve PR #3, branch codex/plan-to-pr-01-record-store, and its exact accepted prerequisite bytes. No content revision or new acceptance is planned.
2. Revise PR #4, codex/plan-to-pr-02-planning, based on #3: add the advisory reliability research, resource index routing, and sample templates/record specifications. Prepare all checkpoint examples before CLI implementation. Obtain explicit owner acceptance of the samples.
3. Revise PR #5, codex/plan-to-pr-03-plan-cli, based on #4: implement local review/delivery/verification modules and commands with focused regression coverage and structured canonical self-test accounting. Keep behavior and its tests together. Existing plan and record CLI contracts and immutable history remain intact.
4. Revise PR #6, codex/plan-to-pr-04-workflow, based on #5: integrate resources, maintainer instructions, approval-response protocol, context/help/handoff entrypoints, task plan progress and current-state routing. Replace conflicting questions and stale handoff language. Deliver renewed review notices and one consolidated packet for the identified versions.

Propagate lower-layer additions through the existing dependent branches with additional commits/non-force pushes; verify actual ancestry and per-layer/cumulative diffs. Stop the affected operation if native-stack maintenance would require unauthorized rewriting or another prohibited action. Keep the existing linear stack; no new merge group or atomic multi-PR claim is introduced. Eligible merging remains bottom-up after explicit version-bound approval and platform requirements.

## Sample-review checkpoint

Before building the CLI, present concrete artifacts and generated human output for:

1. Whole-set approval versus explicit subset approval, with one pending question.
2. A revised PR requiring renewed approval while an explicitly approved unchanged member retains provenance.
3. Timed-out submission saved as uncertain and reconciled on owner return without duplicate delivery.
4. Passed tests with skipped or unavailable required coverage blocking readiness, contrasted with the explicitly accepted PowerShell exception.

Owner accepted this scenario set and requested no additions. The checkpoint assesses understandable approval scope, truthful delivery state, recoverable uncertainty, and accurate readiness. Acceptance permits continuous CLI/integration implementation within the complete approved plan. A requested material correction requires a facilitated one-question-per-turn revision and approval before affected work proceeds.

## Acceptance and verification

Required: repository validator; safe local artifact creation/read/validation and dry-run/concurrency checks; canonical maintainer self-test; focused conformance checks proportional to changed maintenance/package discovery surfaces; whitespace/text-profile checks; per-layer and cumulative verification; and all non-PowerShell canonical doctor checks. Run doctor before and after work using verified Python 3.11+. The owner explicitly accepts only the unchanged PowerShell-unavailable adapter-probe limitation, disclosed separately. Any new doctor failure or missing required task coverage blocks ready-for-review handoff.

Regression scenarios cover ambiguous requests, subset membership, changed head/diff, supersession provenance, stale writes and unsafe paths, uncertain and acknowledged receipt recovery, duplicate/contradictory events, genuine passed/skipped/expected-failure/unexpected-success/subtest/fixture/interrupted accounting, coverage exceptions, shared rendering, compatibility with the existing JSON envelope and human-readable reporting conventions, and zero bytecode. Use synthetic local records and test fixtures; no live comment submission or CI dispatch is needed to test mechanics.

Ready handoff requires truthful version-bound coverage, completed implementation, no missing required local coverage, updated PR descriptions/routing, and the terminal delivery process. Applicable ordinary PR CI remains a separately disclosed platform observation; pending/no checks cannot be claimed as passes. Merging additionally requires eligible platform checks and protections. No full-family certification or activation claim follows from these checks.

Never silently correct accepted historical evidence or prior approval snapshots. New factual corrections use linked records. The previous session's headline should be accurately described as 94 tests accounted for with one skipped, rather than all 94 passing.

## Risks, assumptions, and unresolved questions

Git and GitHub cannot be updated atomically. Receipts and explicit uncertain states improve recovery without promising exactly-once effects. Local receipts may remain uncommitted after the final tags; retain them for owner-return reconciliation. Packet validation depends on truthful supplied platform observations and cannot replace owner judgment or branch protections. Structured accounting must preserve distinctions among test cases, subtests, and fixture errors.

Minor field layout and validation algorithms are implementation details to expose in checkpoint samples; consequential schema or authority changes require owner direction. No unresolved product decision is delegated to implementation. The checkpoint itself remains pending and intentionally blocks CLI construction. If current GitHub stack support or actual branch state conflicts with this sequence, pause rather than expanding authority.

## Execution progress

Complete revision 17 was approved with the exact owner response “yes”; immutable approved snapshot revision 18 and accepted decision wr-0037 preserve that authority. Current-state routing names the pending sample checkpoint. The four scenarios are prepared in plugins/wayfinder-maintainer/skills/wayfinder-maintainer/resources/plan-to-pr-development/reliability-checkpoint-examples.md as synthetic advisory templates. The owner accepted the sample checkpoint with “yes”; decision wr-0038 permits continuous implementation. Research, examples, plan and authorization routing remain local, uncommitted changes. Continuous implementation is starting; PR mutation, implementation acceptance, and merging remain pending. PRs #3–#6 remain unaccepted/unmerged; approved revisions await checkpoint acceptance and renewed version-bound handoff.
