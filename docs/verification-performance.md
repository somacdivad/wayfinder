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

## Measured findings: revision checkpoint

[Ordinary run 34987046636](https://github.com/somacdivad/wayfinder/actions/runs/34987046636)
compared the same PR head `28b5d75637d6f30344febb8454de793089e6b07e` and
tested merge revision `ce65e3733c309d4d0edc458d1fed24074f9e5de6` on Ubuntu 24.04.
Pinned runtime versions and full coverage stayed unchanged.

| PowerShell workers | Complete job | Setup diagnostic | Doctor | Self-test | Python suite | Node suite | PowerShell suite | Outcome |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 29m35s | 9.190s | 5.478s | 33.015s | 351.403s | 50.605s | 1318.375s | Full pass |
| 2 | 15m23s | 8.236s | 4.939s | 24.974s | 270.710s | 41.411s | 567.994s | Full pass |
| 4 | 14m18s | 8.270s | 4.272s | 25.259s | 267.096s | 39.780s | 508.366s | Full pass |

Repository validation took 0.601s, 0.326s and 0.409s respectively. Complete job
durations use GitHub job start/completion timestamps and include post-job work;
setup diagnostics begin at the first workflow step. Each adapter suite passed
all 305 cases, matched the exact ordered fixture oracle, and recorded 900 invocations.
This establishes identical serial/parallel PowerShell case coverage and passing
result data. Hosted doctor passed all 36 checks. Local PowerShell is unavailable.

Four workers shortened PowerShell by 59.628s versus two workers, while both full
jobs exceeded ten minutes. Serial Python also accounted for 267–351s per job.
Runner variation means the observed differences do not isolate startup cost.
PowerShell startup's separate contribution remains unmeasured.

The approved checkpoint requires a pause for plan revision. No fixed worker count
is selected and no three-run readiness validation is started. Draft PR #9 remains
not ready. Sharding, reduced coverage, larger runners, adapter changes and other
adapter parallelism require an explicit revised decision. These logs and timings
are diagnostic observations, not accepted certification evidence.

## Proposed startup diagnostic checkpoint

`scripts/measure_powershell_startup.py --samples 16 --output /new/report.json`
compares an empty `pwsh`, adapter invalid-command rejection, package `probe`, and
discovery in a temporary valid manifest fixture. It uses the same `-NoLogo`,
`-NoProfile`, `-NonInteractive` flags as conformance. Every sample starts a fresh
process; no persistent adapter process or adapter modification is introduced.
The first observation of each scenario is recorded separately, followed by 16
samples each at one, two and four workers: 196 total process invocations.

Each group reports individual wall durations, median/p95, batch wall time and
aggregate child user/system CPU time, major page faults, block I/O counts and
context switches. Fixture preparation is outside measurement. First observations
are not guaranteed cold-cache measurements. Differences between scenarios estimate
additional costs; they do not precisely partition runtime initialization, parsing,
module loading, validation or OS caching. Aggregate CPU and I/O counters provide
clues about contention, not a profiler trace.

The output is exclusively created, reports incomplete until every measurement
passes, and stays separate from governed results. Existing reports, unexpected
results and the unchanged 15-second invocation timeout fail the diagnostic.
Adapter bytes are checked unchanged after measurement. The Ubuntu workflow caps
the diagnostic step at five minutes and still runs ordinary full coverage with
two PowerShell workers, even after diagnostic failure. This is a diagnostic
configuration, not selection of the final worker count or an under-ten-minute claim.

Hosted execution awaits approval of the complete diagnostic revision. That approval
would permit one branch update and ordinary validation attempt, log inspection and
local findings persistence, followed by a pause for the next measured plan decision.
The performance acceptance target and frozen/evidence/certification exclusions stay
unchanged. Local PowerShell coverage remains unavailable.
