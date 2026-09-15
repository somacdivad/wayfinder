<!-- WAYFINDER-PLAN:BEGIN -->
```json
{"approval":{"locator":"conversation:2026-09-15/faster-full-repository-verification/implementation-request","quotation":"PLEASE IMPLEMENT THIS PLAN:"},"approvalHistory":{},"approvedRevision":2,"approvedSha256":null,"format":"wayfinder-plan","id":"wp-4b7d5413-86e9-467b-94b3-bc111d3088e2","records":[],"revision":2,"schemaVersion":1,"slug":"faster-full-verification","status":"approved","subject":"development","summary":"Preserve full PR conformance coverage with bounded process-isolated case execution and a ten-minute measurement checkpoint.","title":"Faster full repository verification","updated":"2026-09-15"}
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
