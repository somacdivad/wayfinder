<!-- WAYFINDER-PLAN:BEGIN -->
```json
{"approval":{"locator":"conversation:2026-09-15/powershell-diagnostic-revision-8/approval","quotation":"yes, I approve"},"approvalHistory":{"2":"a77c853e193ceb7867c14e66d36f1f474ae922edb304c364ddd9598a3459513b"},"approvedRevision":9,"approvedSha256":null,"format":"wayfinder-plan","id":"wp-4b7d5413-86e9-467b-94b3-bc111d3088e2","records":[],"revision":9,"schemaVersion":1,"slug":"faster-full-verification","status":"approved","subject":"development","summary":"Preserve full PR conformance coverage with bounded process-isolated case execution and a ten-minute measurement checkpoint.","title":"Faster full repository verification","updated":"2026-09-15"}
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

Hosted ordinary validation run 34987046636 attempt 1 passed all 305 cases for each adapter on the pinned Ubuntu runner. Complete job duration was 1775 seconds (29m35s). Diagnostic setup was 9.190 seconds; repository validation 0.601, doctor 5.478, self-test 33.015, Python 351.403, Node 50.605, and serial PowerShell 1318.375 seconds. Each adapter suite recorded 900 invocations. Attempt 2 passed all 305 cases per adapter on the same source revision with two PowerShell workers. The full job took 923 seconds (15m23s), missing the ten-minute target; PowerShell took 567.994 seconds, Python 270.710, Node 41.411, self-test 24.974, doctor 4.939, validation 0.326 and diagnostic setup 8.236 seconds. Attempt 3 passed all 305 cases per adapter on the same revision with four PowerShell workers. Complete job duration was 858 seconds (14m18s), also missing the ten-minute target. PowerShell took 508.366 seconds; Python 267.096, Node 39.780, self-test 25.259, doctor 4.272, validation 0.409 and diagnostic setup 8.270 seconds. Four-worker comparison and three consecutive fixed-configuration runs remain pending; review readiness remains blocked. These diagnostic timings are not accepted certification evidence.

## Measurement checkpoint: paused for revision

All three benchmark attempts used Ubuntu 24.04, PR head 28b5d75637d6f30344febb8454de793089e6b07e and the same tested merge revision ce65e3733c309d4d0edc458d1fed24074f9e5de6. Full serial and parallel result data were each checked against the exact ordered 305-case oracle (IDs, categories, rules and passing status), establishing identical coverage and passing outcomes. Every adapter suite recorded 900 invocations. Hosted doctor passed 36/36; local PowerShell remains explicitly unavailable.

Neither two nor four workers achieves the target. The approved measurement checkpoint therefore stops affected implementation and CI execution pending an explicitly approved revised plan. No worker count is selected, no three-run readiness validation is started, and draft PR #9 is not ready for owner review or merging. Existing temporary benchmark switch remains on the published head; local PR-template guidance commit 3a7f43c is not yet pushed, avoiding another automatic validation run while paused.

The next bounded activity is a facilitated plan revision using these measurements. The ten-minute acceptance target remains unchanged until an explicit owner decision. Job sharding, reduced coverage, larger runners, adapter changes and parallelizing other adapters remain outside current implementation authority. No fallback or implementation acceptance is inferred.

## Proposed bounded diagnostic revision

The owner instructed "Let's do it" in response to comparing empty pwsh, adapter invalid-command rejection and real commands on the same runner. This authorizes concrete diagnostic preparation. Because the approved performance checkpoint is paused, the complete revision below awaits explicit approval before commit/push or hosted execution. This does not authorize parallel Python or another performance fallback.

- Add scripts/measure_powershell_startup.py, maintainer regression coverage, diagnostic documentation, and a temporary diagnostic step in the existing validate job on Ubuntu 24.04. Preserve runtime pins, installer checksum, current job and 30-minute timeout. No dependency, adapter, contract or accepted evidence changes.
- Run empty pwsh -NoLogo -NoProfile -NonInteractive -Command 'exit 0'; the unchanged adapter with invalid command initialize-activate (expected exit 2, command.unknown); probe; and discover with a temporary valid manifest fixture. Validate each expected exit, JSON envelope and stderr behavior.
- Record first observations separately, then 16 fresh-process samples per scenario at one/two/four workers: 196 invocations. Fixture creation is outside measured regions. Bound invocation timeout to 15 seconds and the hosted diagnostic step to five minutes. Fail closed on unexpected results, timeouts, existing reports or modified adapter bytes.
- Collect per-invocation wall time, median/p95, batch wall time, aggregate child user/system CPU, major page faults, block I/O counts and context switches. CPU counters are per group, not per parallel invocation. Record CPU count, platform, adapter SHA-256 and source/run binding. First observations are not guaranteed cold-cache samples; differences are estimates, not proof of individual startup components. No cache clearing, settings change or profiler/dependency installation.
- Keep diagnostic JSON/logs separate from governed conformance and accepted evidence. No Actions artifact downloads or evidence promotion/publication.
- Remove the completed attempt-number benchmark switch; accompany diagnostics with ordinary verification using two PowerShell workers. Retain serial Python/Node and all 305 cases per registered adapter. Run full ordinary verification even if the diagnostic step fails. Two workers are a checkpoint configuration, not final selection, and the full-job ten-minute target remains unchanged.
- Approval of this complete revision permits local completion/tests, commits and non-force push of this isolated branch (including already-prepared template guidance and findings), update to draft PR #9 using its template, exactly one automatic ordinary validation attempt with diagnostics, read-only metadata/log inspection, and local measurement/progress/current-state persistence. Additional attempts need an explicit decision if the diagnostic fails. No readiness run series, merging or owner PR-review handoff is implied.
- Run canonical self-test, repository validation, focused Python conformance and pre/post doctor; state local PowerShell unavailable. Hosted measurements supply required diagnostic coverage. Success means all 196 measurements complete with expected outcomes, unchanged adapter bytes and retained full ordinary coverage; report any failures separately. Do not infer that diagnostic success meets performance acceptance.
- After reading and persisting findings, pause for one measured plan-revision decision in chat. Further performance implementation, other adapter parallelism, sharding, reduced coverage, larger runners and adapter changes remain excluded until the owner approves a complete next revision. Existing certification/publication/activation/settings/main exclusions continue.

### Diagnostic preparation verification

The script, regression tests, workflow step and diagnostic documentation are prepared locally and uncommitted. Canonical self-test on final code: 127 test cases, 126 passed, one genuine local PowerShell-unavailable skip, zero failures/errors and bytecode. Repository validation and git diff --check passed. Focused Python command-unknown, command-envelope and discover-explicit conformance passed 3/3. Pre/post doctor retains only the unchanged unavailable pwsh probe (35/36). No hosted diagnostics, commit or push of this revision has occurred. These checks establish local harness preparation; actual PowerShell diagnostics remain required hosted coverage.
