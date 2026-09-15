# Ordinary verification performance

`maintain.py test --jobs N` runs up to N whole cases in separate spawned Python
processes. The default is `--jobs 1`. Each case keeps its own temporary workspace;
its adapter invocations remain sequential, fresh subprocesses with the existing
15-second timeout. The parent emits results in fixture order, including failures
for crashed workers. Case filtering and the conformance result format are unchanged.

Use `--timings /new/path.json` to collect wall time per case and the number of
adapter invocations. Timings are a separate diagnostic report, never certification
evidence or part of the conformance result digest. Existing timing files are refused.
Parallel evidence writing and observation collection are rejected. Parity,
certification, and evidence commands retain their serial execution paths.

`scripts/run_repository_verification.py --powershell-jobs 2 --output /new/directory`
runs repository validation, doctor, canonical self-test, and the complete suite for
each adapter. Only PowerShell uses parallel workers. It stores full conformance
results and diagnostic timings separately, emits bounded failure details, and
reports setup/check/total durations in the ordinary CI log and job summary.
GitHub job metadata supplies the complete job duration, including checkout/setup
step boundaries; diagnostic total time begins at the first workflow step.

## Measurement checkpoint

The target is complete ordinary verification under ten minutes on the existing
Ubuntu 24.04 runner, preserving all 305 cases for every adapter. The existing
30-minute timeout remains. No speedup is claimed from source inspection alone.

During development only, the validation workflow enables a temporary benchmark
switch. Attempts 1, 2, and 3 of the same ordinary PR workflow run select PowerShell
worker counts 1, 2, and 4 respectively. This permits same-source, same-runner-class
comparisons without a certification or publication dispatch. Every attempt runs
all ordinary checks. A cancelled serial baseline remains incomplete, not passed;
its elapsed lower bound can still be reported explicitly.

After comparing results and timings, replace the temporary switch with the
smallest of 2 and 4 workers that can meet the full-job target. Require three
consecutive full passing validations under ten minutes with that fixed configuration.
If neither meets the target, stop and revise the approved plan with the measured
results. Job sharding, smaller coverage, larger runners, and adapter edits require
a new decision. Diagnostic reports do not promote or alter accepted evidence.

Local PowerShell is unavailable. Hosted pinned-runtime verification and the timing
checkpoint are required before this PR is ready for owner review.
