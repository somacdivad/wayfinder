<!-- WAYFINDER-PLAN:BEGIN -->
```json
{"approval":{"locator":"conversation:2026-09-15/faster-full-repository-verification/implementation-request","quotation":"PLEASE IMPLEMENT THIS PLAN:"},"approvalHistory":{"2":"a77c853e193ceb7867c14e66d36f1f474ae922edb304c364ddd9598a3459513b"},"approvedRevision":2,"approvedSha256":"a77c853e193ceb7867c14e66d36f1f474ae922edb304c364ddd9598a3459513b","format":"wayfinder-plan","id":"wp-4b7d5413-86e9-467b-94b3-bc111d3088e2","records":[],"revision":4,"schemaVersion":1,"slug":"faster-full-verification","status":"implementing","subject":"development","summary":"Preserve full PR conformance coverage with bounded process-isolated case execution and a ten-minute measurement checkpoint.","title":"Faster full repository verification","updated":"2026-09-15"}
```
<!-- WAYFINDER-PLAN:END -->

# Faster full repository verification

## Summary

Keep all 305 cases for every registered adapter on each PR. Add bounded, process-isolated case execution to ordinary verification, targeting **under 10 minutes for the complete validation job** on the existing Ubuntu runner.

Current evidence establishes serial execution and two 30-minute timeouts during conformance. PowerShell startup is a suspected bottleneck; its contribution remains unmeasured because PowerShell is unavailable locally.

## Implementation

- Add `--jobs N` to `maintain.py test` and the conformance runner, defaulting to `1`. Reject non-positive values before execution.
- Use a spawn-based standard-library process pool for parallel runs. Each task executes one complete case with its existing temporary workspace and fresh adapter subprocesses.
- Keep invocations within each case sequential. Reset case-local observation state between tasks; emit results centrally in original suite order.
- Preserve result schemas, case selection, diagnostics, the 15-second invocation timeout, and nonzero failure behavior. Worker crashes or missing results must fail the run.
- Keep evidence, parity, and certification paths serial. Reject parallel execution with evidence writing or observation collection in this tranche.
- Update ordinary validation to opt into workers for PowerShell only. Retain the current workflow job, other adapter execution, runtime pins, installation checksums, and 30-minute timeout.

## Measurement checkpoint

- Measure setup, doctor, self-test, each adapter suite, and total job duration. Collect case durations and adapter invocation counts separately from governed results.
- Compare full serial PowerShell execution with `--jobs 2` and `--jobs 4` on the same runner class and source revision.
- Choose the smallest worker count that achieves the target, then require three consecutive complete validation runs under 10 minutes with full passing coverage.
- **If neither configuration meets the target, pause and revise the plan with measurements.** Job sharding, reduced coverage, larger runners, and adapter changes are not automatic fallbacks.

## Verification and delivery

- Test serial compatibility, filtered selection, ordered aggregation, workspace isolation, ordinary case failures, subprocess timeouts, worker crashes, and invalid worker counts.
- Compare serial and parallel result sets for all 305 PowerShell cases; require identical coverage and passing outcomes.
- Run canonical maintainer self-tests, repository validation, focused conformance, and pre/post doctor checks. Report local PowerShell coverage as unavailable; require hosted PowerShell verification before review readiness.
- Deliver one PR against `candidate-revision-9-certification`, containing the harness change, regression tests, workflow opt-in, documentation, and timing findings. Stop for version-bound owner review.

## Authority and assumptions

- This is a planning proposal; no repository files or durable plan records have been written in Plan Mode.
- After leaving Plan Mode, persist the complete draft through the maintainer plan CLI and obtain explicit approval before implementation or CI execution.
- The intended approval covers plan persistence, isolated branch work, commits, push, PR creation, and ordinary validation needed for the benchmark.
- Preserve existing local edits, frozen contract and adapter bytes, accepted history and evidence, and current candidate status. Exclude dependency additions, certification dispatch, evidence publication, activation, settings changes, and integration into `main`.

## Execution progress

The owner explicitly approved this complete plan with "PLEASE IMPLEMENT THIS PLAN:" on 2026-09-15. Exact approved snapshot revision 2 remains unchanged. Implementation is on codex/faster-full-verification in an isolated worktree based on cca387cdf63cc4784f6bf2a543b67f17f484e8e8, targeting candidate-revision-9-certification. The owner checkout retains its pre-existing local changes and separately persists approval record wr-0051; unrelated unpublished closure history is excluded from this PR.

Whole-case spawn workers, positive jobs validation, ordered fail-closed aggregation, separate case/invocation timings, ordinary verification timing wrapper, regressions and documentation are implemented. The temporary ordinary CI benchmark switch selects 1/2/4 workers on rerun attempts 1/2/3 of the same revision; it will be removed in favor of the selected fixed count before readiness. No certification/publication dispatch or artifact download is authorized or performed.

Canonical self-test: 123 test cases, 122 passed, one genuine missing-PowerShell skip, zero bytecode. Repository validation and whitespace checks pass. Full local Python serial and two-worker runs each passed all 305 cases with identical complete result data; Node serial also passed all 305. Python timings were 168.766 seconds serial and 90.020 seconds with two workers; Node was 68.370 seconds. Pre-edit doctor passes 35/36 with missing pwsh as the sole unchanged failure. CPython is 3.12.14 and Node.js is 22.22.3 locally; pinned hosted versions remain required. PowerShell coverage and hosted timing checkpoint are pending and block review readiness. No implementation acceptance or merge is claimed.

The owner instructed "We should make it explicit in the wayfinder-maintainer skill that PRs use the PR template". The skill and PR guidance now require reading the target template, preserving its sections and checklists, and checking only verified passing items. Draft PR #9 was corrected to the repository template. This reinforces delivery expectations without changing the approved performance acceptance criteria.

Hosted ordinary validation run 34987046636 attempt 1 passed all 305 cases for each adapter on the pinned Ubuntu runner. Complete job duration was 1775 seconds (29m35s). Diagnostic setup was 9.190 seconds; repository validation 0.601, doctor 5.478, self-test 33.015, Python 351.403, Node 50.605, and serial PowerShell 1318.375 seconds. Each adapter suite recorded 900 invocations. Attempt 2 is running the same source revision with two PowerShell workers. Four-worker comparison and three consecutive fixed-configuration runs remain pending; review readiness remains blocked. These diagnostic timings are not accepted certification evidence.
