# Wayfinder maintenance workflow

Use this reference only while changing, testing, certifying, freezing, or preparing activation of Wayfinder itself.

The canonical source-repository entry point is `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py`; abbreviated `maintain.py` commands below refer to that file.

## Start cleanly

- Read `references/current-state.md` for current status, identities, approval boundaries, pending action, and routes into the chronology. Read only the routed design-record sections relevant to ordinary work. Read the full chronological record only when reopening a decision, changing evidence governance, or recording an accepted outcome.
- Resolve interpreter and adapter runtime paths once, export `WAYFINDER_NODE_RUNTIME` and `WAYFINDER_POWERSHELL_RUNTIME` when needed, and reuse them. Record the requested path, resolved path, observed version, and override variable. Do not retry a known-unsupported interpreter or install an unavailable runtime.
- Inspect `maintain.py --help` and `maintain.py SUBCOMMAND --help` before assembling a command. `maintain.py describe --format json` provides stable machine-readable paths and identities.
- Run `maintain.py doctor --verbose` before feature work. A red baseline is maintenance work, not evidence for a new feature. Routine successful calls use summary output; internal preflight is quiet.
- Do not use `py_compile` for syntax-only checks; the canonical doctor compiles sources in memory and creates no bytecode cache.
- Do not run the bundled skill-creator `quick_validate.py` as a canonical Wayfinder check. It requires PyYAML, which is not a repository dependency. Do not install PyYAML for this purpose; use `maintain.py doctor` and `scripts/validate_repository.py`. If PyYAML is already available, `quick_validate.py` may be used once as an optional secondary check, and its result does not replace either canonical validator.
- In a separately installed maintainer plugin, set `WAYFINDER_SKILL_ROOT` to an explicit local runtime-skill root. Do not fetch or infer a target checkout.

## Change a candidate

- Preserve accepted decisions and historical evidence.
- Change the normative contract before or with implementation behavior; fixtures cannot create semantics by themselves.
- When governed bytes change after acceptance, advance the candidate revision, rebuild package digests, and generate new evidence. Never relabel older evidence as current.
- If a rule can fail in multiple ways, define diagnostic precedence or test the documented acceptable outcomes instead of following accidental implementation order.
- Add adjacent-slice scenarios whenever one slice consumes another slice's output.

## Verify

Run in this order:

```text
maintain.py doctor --verbose
maintain.py test [--adapter ID] [--case ID --case ID]
maintain.py evidence --output DIR
maintain.py freeze-proposal --output DIR
maintain.py freeze-acceptance --output DIR --accept-option-a
```

`test` is read-only outside temporary fixtures and writes no certification evidence. `evidence` requires an explicit destination and refuses to replace an existing report.
`freeze-proposal` requires passing revision-scoped candidate and parity reports, validates their exact package bindings, and exclusively creates a pending proposal pair without recording owner acceptance.
`freeze-acceptance` is permitted only after an explicit owner Option A response. It validates and binds the exact proposal, exclusively creates a new acceptance pair, and does not authorize or begin any later tranche.

Repeat `--case` or `--category` in one `test` invocation rather than launching one process per selection. Summary output is the default; use `--output verbose` only for per-case detail or `--output json` for stable structured results. A focused adapter run still checks all registered adapter bytes and identities, but its quiet preflight probes only the selected adapter runtime, so an unavailable unrelated runtime does not block it. `--case-file` is intentionally omitted because repeated arguments are sufficient for the current 305-case suite and avoid another input format.

For already-downloaded hosted artifacts, use:

```text
maintain.py matrix-review --artifact-dir DIR [--format summary|markdown|json]
```

This command performs no network access and no writes. It verifies source/run bindings, exact registered adapters and report hashes, exact 305-case result sets, result-set digests, distinct aggregate invocation-digest metadata, and coverage summaries. It labels Actions artifacts review-only and never publishes, promotes, or replaces accepted evidence.

For a separately authorized adapter-parity tranche, select each registered
adapter through `maintain.py test --adapter ID`, then run
`maintain.py parity --output DIR`. The parity command runs the complete suite
for all three version-1 adapters and refuses to publish its local comparison
report unless per-adapter results and normalized black-box observations agree.
It does not create an environment-certification entry or a full-family claim.

Use `maintain.py expect --exit N --code CODE -- COMMAND...` for a negative demonstration. The wrapper succeeds only when the command returns the expected exit and result code.

Bound parallel file reads by line range and output budget. Once a check passes, repeat or broaden it only after changed inputs, increased scope, or a failure that creates a new risk. Run one full `maintain.py doctor --verbose` after the final changed input.

## Handoff and approval

Generate factual handoff scaffolding with:

```text
maintain.py handoff --objective "Bounded objective" --exclude "Deferred action"
```

The generator derives the current release identity, digests, and case counts. Add only the slice-specific design context that cannot be derived.

Before approval, report the exact changed surface, observable behavior, verification, unavailable evidence, and what acceptance would authorize. Approval never begins the next tranche automatically.

Stop before any action outside the explicit tranche, before overwriting or promoting evidence, when a required selected runtime remains unavailable after one resolution attempt, or after delivering the requested approval packet. Hosted reruns, evidence publication, candidate reopening, activation, live-project work, commits, and pushes each require their own authorization when the current state says they are closed.
