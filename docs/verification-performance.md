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

## Startup diagnostic checkpoint

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

The complete diagnostic revision was approved and preserved as snapshot revision 9.
That approval permits one branch update and ordinary validation attempt, log inspection
and local findings persistence, followed by a pause for the next measured plan decision.
The performance acceptance target and frozen/evidence/certification exclusions stay
unchanged. Local PowerShell coverage remains unavailable.

## Startup diagnostic observations: run 35009583443

The owner approved the complete diagnostic revision with "yes, I approve";
approval snapshot revision 9 preserves that scope. Commit
`56907814b177425ce5b2b0f06a3ed10c1c29105b` triggered exactly one
[ordinary run](https://github.com/somacdivad/wayfinder/actions/runs/35009583443).
The diagnostic step completed successfully in 119 seconds. Its live step logs
reported all 196 expected observations and unchanged adapter bytes; full ordinary
verification also completed successfully. The completed log was reconciled to all
196 observations, all 305 passing cases per adapter and 900 invocations per suite.
Hosted doctor passed 36/36 and self-test passed 127/127 without skips or bytecode.
Complete job duration was 22m27s, including the 119-second diagnostic step.
Two-worker PowerShell took 786.580s, Python 344.497s and Node 49.312s.
Driver precheck time (126.589s) includes diagnostics, not just runtime setup.
No under-ten-minute success is claimed. Further work is paused pending a new
complete approved revision; no additional run or push is authorized.

| Scenario | Median, 1 worker | Median, 2 workers | Median, 4 workers |
| --- | ---: | ---: | ---: |
| Empty PowerShell | 0.163s | 0.218s | 0.383s |
| Adapter invalid-command rejection | 0.892s | 1.030s | 1.652s |
| Adapter probe | 1.222s | 1.519s | 2.439s |
| Adapter discovery | 1.111s | 1.352s | 2.173s |

For the serial observations, adapter rejection adds approximately 0.729s over an
empty process; probe adds another 0.330s and discovery another 0.220s over rejection.
Bare startup therefore explains about 13% of the probe median. The rejection path
already accounts for roughly 73% of probe and 80% of discovery elapsed time. These
are cross-scenario estimates, not a precise component decomposition or a measurement
of every suite command.

The adapter rejection path parses/loads the complete script, runs top-level
initialization, rejects the command and formats a structured failure. It does not
perform probe's governed-resource verification or discovery's fixture traversal.
The measurements point to repeated adapter loading/initialization and baseline
execution as a larger overhead than starting an otherwise empty PowerShell process.
Further attribution among script parsing, compilation/JIT, module loading,
top-level .NET setup and result formatting remains unmeasured.

At four workers, probe's 16-process batch consumed 38.306 child CPU seconds in
10.022 wall seconds, averaging 3.822 CPU cores. Its median invocation latency
doubled from 1.222s to 2.439s, and involuntary context switches increased from
2,366 to 37,340. Discovery averaged 3.818 cores and also nearly doubled latency.
These observations support CPU contention as the reason additional workers give
diminishing throughput improvements. Repeated groups reported zero input blocks;
output blocks were nonzero. The resource counters do not establish a specific
cache, memory, disk or runtime-internal cause.

Every conformance adapter call still starts a fresh PowerShell process, so this
overhead repeats across 900 invocations. No adapter process reuse, frozen-byte
modification or further optimization is introduced by this diagnostic checkpoint.

## Component diagnostic checkpoint

The approved follow-up runs 27 serial fresh processes: one first observation and
eight repeated samples each for empty PowerShell, a minimal result payload, and
the existing probe payload. An independent wrapper parses the unchanged source,
checks its final dispatch statements, and loads only an in-memory initialization
prefix under the original source path. Path/scoping disagreements fail closed.

Stopwatch intervals cover byte read/decode, full-source parsing, extra diagnostic
prefix parsing, script-block creation, loading/initialization, probe work, first
and three repeated formatter calls, and private UTF-8 file output. Loaded module
inventories and per-process wall/child CPU accompany the timings. Formatter text
and file bytes are checked; registered adapter bytes are checked before/after.

These are diagnostic components, not an exact decomposition of ordinary startup:
compilation can be deferred, the wrapper changes cache/JIT state, a derived script
block differs from `-File`, and private-file output does not measure stdout latency.
The hosted check still runs all 305 cases per adapter, with Python/Node serial and
two PowerShell workers, even if diagnostics fail. One attempt is authorized, then
findings are persisted locally and work pauses. The ten-minute target is unmet.

### Initial component attempt cancelled and corrected

Run [35014663010 attempt 1](https://github.com/somacdivad/wayfinder/actions/runs/35014663010/attempts/1)
on head `c3fb70cb161f37b4f4384d83bf56b5ee0e7991ad` failed before any valid
component observations. Nine empty-process observations passed (median 0.161560s).
The diagnostic guard accessed `Traps.Count` under strict mode, but the SDK defines
[Traps as null when absent](https://learn.microsoft.com/en-us/dotnet/api/system.management.automation.language.namedblockast.traps).
The AST regression omitted strict mode and missed this harness bug. This supplies
no new adapter component attribution. The correction null-checks `Traps` and runs
the actual AST regression under strict mode. Local self-test remains 133 passes
and two PowerShell-unavailable skips; repository and whitespace validation pass.

At the owner's explicit instruction, normal cancellation was requested, then
force-cancellation because the ordinary `always()` step continued running.
Terminal metadata confirms completed/cancelled at 19:48:24 UTC, after 11m35s.
That is an interrupted duration, not a full performance result. Hosted doctor
passed 36/36, self-test 135/135, Python and Node 305/305 with 900 invocations each
(368.274s and 50.959s). PowerShell/full validation were interrupted and unavailable.
Terminal log SHA-256: `c41009c757db2915c9affe239250eee1c5f5aef06ffd97e32af4db6580f703d5`.

The owner authorized pushing this two-line correction to start one replacement
full ordinary validation. The diagnostic design and all coverage constraints stay
unchanged; after that replacement, findings are persisted locally and work pauses.
No further attempt, optimization or merging is implied.

## Completed component diagnostic findings

[Replacement run 35016030202 attempt 1](https://github.com/somacdivad/wayfinder/actions/runs/35016030202/attempts/1) passed on head d5b5bbc4115c1592ad46a520425aa5190b520dd7, tested merge 999aec0fb691c552ffe3dc8b721f05b4c038ba0d. Job 104539566230 ran 19:50:37–20:11:42 UTC: 21m05s. All 27 expected observations were reconciled with exact source/path/runtime bindings, finite nonnegative timings, identical first/repeated formatter text, output byte equality and unchanged frozen adapter bytes. Hosted doctor passed 36/36, canonical self-test 135/135 with zero skips/bytecode, and all 305 cases per adapter passed with 900 invocations each. Complete log SHA-256 f5f5e0821fd8cef4f0f90ac0d8196a63ccced9c1f33c34347650658c5cbf5485. No Actions artifacts were downloaded and none of these diagnostics are accepted certification evidence.

| Median component | Minimal payload | Real probe payload |
| --- | ---: | ---: |
| External process wall | 1.108104s | 1.438942s |
| Source read/decode | 0.006436s | 0.006390s |
| Full source parse | 0.066464s | 0.064836s |
| Extra diagnostic-prefix parse | 0.030864s | 0.029909s |
| Script-block creation | 0.000985s | 0.000961s |
| Loading/initialization | 0.595564s | 0.585764s |
| Probe work | 0 | 0.332729s |
| First display formatter | 0.025961s | 0.017213s |
| Three repeated formatter calls | 0.002779/0.003370/0.002445s | 0.015480/0.007823/0.007574s |
| Private UTF-8 file write | 0.005767s | 0.005017s |

Empty PowerShell median was 0.169829s. Loading/initialization is the largest observed component, roughly nine times full-source parsing in these probes. Probe work is substantial; display formatting and file output are smaller. All 18 component observations had no loaded modules before initialization and Microsoft.PowerShell.Management 7.0.0.0 afterward. Module autoloading is a specific lead inside the loading/initialization interval, but its individual cost versus remaining execution/deferred compilation is not isolated. Do not claim that module import alone causes the full overhead. The wrapper/in-memory prefix changes compilation/cache state, prefix parsing is diagnostic overhead, formatter first-use follows earlier probe work in that scenario, and file output is not stdout latency; these medians are not an exact ordinary-startup decomposition.

Ordinary timings: repository 0.339s, doctor 4.564s, self-test 35.083s, Python 349.863s, Node 50.260s, PowerShell with two workers 789.428s. Setup/precheck 32.682s includes component diagnostics; it is not solely installation setup. Checks total 1229.544s and wrapper total 1262.227s. The full job remains above ten minutes; no final worker count, three-run readiness series, target waiver or owner PR readiness is established.

This bounded diagnostic operation is complete. Findings/progress remain local to avoid triggering another run. Draft PR #9 remains not ready for owner review/merging. No further push, CI, diagnosis or optimization is authorized automatically. Next is one measured revision-scope decision in chat; a complete replacement plan requires explicit approval before implementation/execution. The suggested diagnostic scope is separating Management module autoload from remaining initialization/deferred compilation, preserving adapter/frozen bytes. Local PowerShell remains unavailable; existing candidate/evidence/publication/activation facts and all exclusions are unchanged.

## Management module isolation checkpoint

The approved follow-up measures 54 serial fresh processes: empty PowerShell,
import-only control, and natural/preloaded minimal and real probe payloads. Each
scenario has one first observation and eight subsequent samples; alternating
round order reduces systematic drift. First observations are not cold-cache proof.

In preloaded scenarios, core `Import-Module` runs immediately before the unchanged
in-memory adapter prefix. Import-only controls separately time import and the
same two `Split-Path` parent operations plus `Join-Path` used by adapter setup.
Core `Get-Module` inventories verify Management absence/presence around stages.
No module installation, automatic-variable override, preference/profile change,
modified adapter file or conformance process reuse is introduced.

Versioned diagnostic schemas separately validate component/control stages and
path/module identities. Natural/preloaded payload and formatted text must match;
formatter/file bytes, frozen adapter source, wrapper hash, sample/round ordering
and successful exits are checked. Combined import/initialization medians use
per-observation sums. Whole-process wall and child CPU remain separate measures.

Pre-import may warm shared assemblies, JIT and command discovery or simply move
work earlier. A smaller residual initialization stage is a diagnostic finding,
not a delivered optimization or an exact causal decomposition. Prior component
medians provide context, not a same-source comparison. All prior findings remain
preserved, including the cancelled initial component attempt.

One full ordinary Ubuntu validation attempt is authorized with this five-minute
diagnostic step, 15-second subprocess timeout and existing 30-minute job timeout.
All 305 cases per adapter remain required; Python/Node stay serial and PowerShell
uses two workers. Ordinary checks run after diagnostic failure. After the attempt,
findings are persisted locally and work pauses; ten-minute readiness and merging
remain blocked.

## Diagnostic-only startup-path checkpoint

Owner-cancelled run [35019844575](https://github.com/somacdivad/wayfinder/actions/runs/35019844575/attempts/1) completed all 54 valid module measurements on head `42c77cdbb94872ca8e32c876716bcee7386ce42f`, tested merge `5abaae7b2d08e27f3ed07d964712afee725d3e9d`. Natural/preloaded initialization medians were 0.601765/0.018134s (minimal) and 0.575228/0.017881s (probe); whole-process medians were 1.125818/1.020542s and 1.421205/1.330589s. Explicit import was about 0.089s, standalone control 0.095s and empty process 0.179s. Timed initialization reduction is not equivalent to end-to-end saving. All source/runtime/module/path/paired output checks passed; terminal log SHA-256 `e158697182194333f5b1ae5d1f2c72af23d9dbd479fa38635814d2842c4324c9`. Full validation was cancelled and is unavailable, not passed.

Approved revision 22 adds an independent in-memory prototype replacing only the two startup path expressions with .NET equivalents. Five serial cohorts and nine alternating-order rounds yield 45 observations, including separate first observations. Original and counterfactual prefixes retain original path metadata, strict AST guards, root equality, raw/transformed prefix hashes and exact paired payload/formatter/private-file checks. Module inventories after initialization, probe and formatting distinguish avoided startup loading from loading deferred into later work. No adapter file or package variant is written. The registered adapter and candidate remain frozen.

Hosted performance runs declare their purpose. Measurement-only attempts collect diagnostics then cancel remaining ordinary validation; correctness or complete-validation-performance attempts retain full coverage and timing. Cancellation never constitutes full conformance success or a ten-minute result. This checkpoint allows one diagnostic-only attempt and exact-run cancellation after the diagnostic finishes, success or failure; no automatic retry. All pins/checksum and timeouts remain. After local findings persistence pause for a measured revision decision. Local PowerShell remains unavailable; hosted execution must exercise actual transform/module/path behavior. The ten-minute target and three complete passing-run requirement remain unmet.

## Completed startup-path diagnostic findings — 2026-09-15

Diagnostic-only run 35021476856 attempt 1 on head 9aef6de8851290e94ff16d77bf54e5245dbacea4, tested merge 2c9a83a4b568243c44c9ce40e3537660b2b76500, completed all 45 valid observations. Terminal logs were independently validated against exact closed schemas, hashes, runtime7.6.6, source/variant/round bindings, original-path roots, raw/transformed prefix hashes, module transitions and identical paired payload/formatter/private-file bytes. Adapter bytes remained b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9; wrapper hash cad604a00a7ca348ec86963eaf7e822d2153d7bcf94a43ce86f29101ad2be433. Terminal log SHA-256 9c2617dde0f1f47e49106cf8438d0d906c97f7d443ce177787c591ffea68cdb2. Diagnostic step completed/success.

| Median stage | Original startup | .NET startup |
| --- | ---: | ---: |
| Minimal initialization | 0.586947s | 0.017022s |
| Minimal complete process | 1.147859s | 1.047453s |
| Probe initialization | 0.587983s | 0.015961s |
| Probe work | 0.368969s | 0.888269s |
| Probe complete process | 1.493403s | 1.441741s |

Management was absent after .NET initialization in all 18 variant observations. It remained absent after minimal formatting, but appeared during probe work in all nine .NET probe observations. Original initialization loaded it in all 18 original component observations. The startup change defers module loading for real probe execution; it does not avoid module loading across the whole adapter. Probe stage grew about0.519s while initialization fell about0.572s; complete probe-process median improved only0.052s (about3.5%). Complete minimal median improved0.100s (about8.7%). Individual paired rounds include one slowdown per payload; samples are small. Do not extrapolate stage reduction to 900-invocation/full-job savings or infer the ten-minute target is met. Transformation/guard/report instrumentation is outside ordinary adapter execution and complicates end-to-end attribution.

The ordinary validator finished/failure immediately after diagnostics with `FAIL Python bytecode cache is present`, before diagnostic completion was observed for cancellation. The new independent driver imports its existing component-validation helper through importlib without disabling bytecode; canonical self-test sets no-bytecode controls, so local tests did not expose this standalone diagnostic side effect. This is a harness defect, not evidence of adapter conformance failure. No doctor/self-test/adapter suite/full performance result is claimed for this hosted run. It was already completed/failure when cancellation eligibility was inspected; no cancellation request was sent to a completed run and cancelled status is not claimed. Cancellation acceptance criterion was not met. No additional attempt or corrective push is authorized after this one attempt.

Local pre-delivery validation passed; canonical self-test145/148 with three genuine PowerShell-unavailable skips and no failures/bytecode, focused Python3/3; pre/post doctors35/36 solely unavailable local PowerShell. Actual diagnostic transform/module/path branches are now hosted-verified; the actual transform AST regression in canonical hosted self-test was not reached. Findings remain local to avoid another automatic attempt. Draft PR#9 remains not ready for owner review/merging; full under-ten-minute acceptance remains unmet. Stop for a measured revision decision. A follow-up may address the helper's standalone no-bytecode control and investigate unchanged probe/package calls that load Management, but neither another attempt nor a frozen-adapter change is inferred.

## Probe/package module-avoidance checkpoint

Approved complete revision26 extends the isolated in-memory prototype through the seven path joins and one recursive file enumeration inside `Invoke-WfProbe`. Five cohorts distinguish frozen original, .NET startup, .NET startup/probe paths, and .NET startup/probe paths/enumeration, plus empty baseline; nine alternating rounds yield45 timed observations. One separate untimed fresh compatibility-control process compares .NET enumeration against pinned `Get-ChildItem -LiteralPath -Recurse -File` on real governed scopes and temporary hidden/literal/Unicode/link/cycle/missing/permission fixtures. Permission denial that cannot be enforced is explicitly unavailable. A mismatch stops timing. Schema, digest, text-profile, scope and known-answer checks remain; no registered adapter/package is transformed on disk.

The driver sets process-local no-bytecode controls before helper imports. A fresh Python subprocess regression, without canonical `-B` or inherited `PYTHONDONTWRITEBYTECODE`, checks standalone imports produce no cache files. This addresses the prior hosted helper side effect. Source/path/prefix/helper provenance, module transitions through probe/formatting and exact paired payload/formatter/private-file outputs remain mandatory. The full .NET variant must keep Management absent through formatting; partial variants may defer loading into unchanged commands.

Exactly one diagnostic-only hosted attempt is authorized, with all pins/checksum/timeouts and ordinary validation definition preserved. Cancel the exact run immediately after diagnostics finish, success or failure; if already terminal, preserve its actual outcome and explain why cancellation did not apply. No retry, full-suite benchmark, frozen candidate reopening or delivered adapter optimization is inferred. After local findings pause for a measured revision decision; draft PR9 remains not ready, and full ten-minute acceptance remains unmet. Relevant filesystem behavior is described in [Microsoft Get-ChildItem documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-childitem?view=powershell-7.4); the pinned-runtime compatibility control, rather than documentation alone, verifies this Linux diagnostic helper.
