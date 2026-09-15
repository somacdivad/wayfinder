<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":null,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0019","kind":"decision","legacy":{"sourceSectionSha256":"7708e74c96f7adbd18a40ab80334793208556763343ea231b05f1c0ecbd4fba2"},"outcome":"accepted","predecessors":["wr-0002"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 8 maintainer-efficiency tranche — accepted.","title":"Candidate revision 8 maintainer-efficiency tranche — accepted","topic":"governance"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 8 maintainer-efficiency tranche — accepted

Implemented and accepted by the skill owner on 2026-09-14 as a maintainer-only workflow and tooling tranche:

- Added a compact `references/current-state.md` containing the frozen candidate and activation state, accepted package, adapter, parity, matrix, and historical-evidence identities, the current approval boundary, the pending action, and exact routes into this chronological record. The doctor deterministically rejects drift between the compact reference, package facts, accepted evidence, and required chronology anchors.
- Revised the maintainer skill and workflow for progressive disclosure. Routine work reads the compact state; exact chronology sections are loaded only when prior rationale is relevant; the full record is required when reopening a decision, changing evidence governance, or recording an accepted outcome.
- Added canonical recipes to resolve and reuse runtime paths, inspect CLI help, batch repeated `--case` and `--category` selections, bound reads, avoid unjustified repeat checks, prefer summary or structured output, and stop at approval boundaries.
- Added doctor summary, verbose, stable JSON, and quiet-success internal-preflight modes. Focused tests retain repository, package, evidence, and every registered adapter byte and identity check while probing only the selected adapter runtime.
- Added `describe`/`context` output for canonical paths, candidate identity, conformance counts, adapter registry, runtime requirements, and approval boundaries. Added a dependency-free offline matrix-artifact reviewer that performs no network access or writes, preserves result-set versus aggregate-invocation digest distinctions, validates exact 305-case reports and coverage metadata, summarizes failures by environment, and labels Actions material review-only.
- Added dependency-free maintainer-tool regressions for doctor modes and failures, quiet preflight, multi-case batching, selected-adapter runtime isolation, runtime diagnostics, context output, artifact review, evidence overwrite refusal, output budgets, and accepted-evidence preservation.
- Explicitly excluded the bundled skill-creator `quick_validate.py` from canonical Wayfinder verification because it requires PyYAML, which is not a repository dependency. The canonical doctor and repository validator remain authoritative; an already-available PyYAML environment may run the external validator once only as a secondary check.
- The final routine startup reference set is 12,878 bytes versus 73,565 bytes before the tranche, an 82.49% reduction. Successful doctor output is 29 bytes versus 2,169 bytes, a 98.66% reduction. The representative three-case workflow reduced command output from 7,263 to 2,188 bytes, canonical CLI calls from five to three, and wall time from 4.40 to 1.20 seconds. The initial two failed exploratory setup calls were eliminated in the optimized replay.
- Eight maintainer-tool regression tests passed. The unchanged revision-8 suite passed 305/305 cases under CPython 3.14.7, the repository validator passed, the final full doctor passed 31/31, and `git diff --check` passed. Optional PyYAML remained unavailable and was not installed.
- Frozen contract, fixture, registered-adapter, parity, accepted historical-evidence, and accepted certification-evidence bytes remained unchanged. Initialization remains disabled. No hosted rerun, evidence publication, release-certification entry, forward test, cross-adapter recovery, runtime guidance, activation, live-project initialization, commit, or push was performed.

### Maintainer-efficiency approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded maintainer-efficiency workflow and tooling | Accepted 2026-09-14 | The skill owner approved the tranche as implemented, including the compact validated state, efficient canonical recipes, output and preflight changes, offline review command, regression coverage, measurement caveats, and explicit non-PyYAML canonical-validation boundary. This acceptance records the result only. It does not reopen candidate revision 8, authorize correction of either Windows blocker, dispatch a hosted rerun, publish or promote evidence, add certification entries, claim full-family certification, add runtime guidance, activate Wayfinder, initialize a live project, commit, or push. |

