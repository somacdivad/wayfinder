---
name: wayfinder-maintainer
description: Maintain, version, test, certify, freeze, or prepare activation of the Wayfinder executable contract and adapters. Use only for work on Wayfinder itself; do not use to initialize, update, validate, or consult an ordinary project record.
---

# Wayfinder Maintainer

Maintain the Wayfinder skill without treating passing hashes or fixture counts as proof that its contract artifacts agree semantically.

## Start with compact state

1. Read the applicable repository instructions and [current maintainer state](references/current-state.md).
2. Resolve the requested CPython, Node.js, and PowerShell executables once, record unavailable runtimes honestly, and reuse the resolved paths. Do not install dependencies without authorization.
3. Inspect `maintain.py --help` and the selected subcommand help instead of reconstructing commands.
4. Run the canonical pre-edit doctor with a verified Python 3.11+ interpreter: `maintain.py doctor --verbose`. Use the same interpreter for the tranche.
5. Read [the maintenance workflow](references/workflow.md) when changing, testing, certifying, freezing, or preparing activation.

Routine maintenance does not require the full chronological record. Read the exact routed sections in `current-state.md` when prior rationale affects the task. Read the complete [design record](references/design-record.md) only when reopening a decision, changing evidence governance, or recording an accepted outcome; use bounded non-overlapping reads if necessary.

Before asking the owner for acceptance, authorization, or approval, and when processing the owner's response to such a request, read and follow the canonical [approval-response protocol](references/approval-response.md).

## Efficient execution

- Use `maintain.py describe` (or `context`) for canonical paths, candidate identity, case counts, adapter registry, runtime requirements, and the current approval boundary.
- Batch focused cases in one invocation: `maintain.py test --case ID --case ID`. Select one adapter with `--adapter ID`; an unavailable unrelated runtime does not block that focused run.
- Prefer summary or JSON output. Use verbose output when per-check or per-case detail is required.
- Bound parallel read output and keep chunks non-overlapping. Do not repeat a successful check unless inputs changed, scope increased, or a failure creates a new risk.
- Reuse resolved runtime paths, command help, `describe`, and unchanged pre-edit hashes within one uninterrupted session. Refresh them after compaction, tool reset, checkout change, or a relevant file edit.
- Use `maintain.py self-test` for maintainer regressions; it discovers every maintainer-owned `test_*.py` module without leaving bytecode in the repository. Do not invoke individual test modules as the canonical regression run.
- Use `maintain.py record-section --heading HEADING` for one exact design-record section instead of broad ad hoc chronology reads.
- Use `maintain.py matrix-review --artifact-dir DIR` only on already-downloaded artifacts. It is offline, read-only, and cannot accept or publish evidence.
- Use `maintain.py freeze-proposal --output DIR` only after the revision-scoped candidate and parity reports pass; it exclusively creates a pending proposal and never records owner acceptance.
- Use `maintain.py freeze-acceptance --output DIR --accept-option-a` only after the owner explicitly accepts Option A; it binds the exact proposal and exclusively creates the acceptance record without authorizing later work.

## Authority and stopping rules

Keep every change inside the user's authorization. Passing a tranche does not authorize parity, freeze, hosted execution, publication, activation, Git mutation, external access, or live project-record changes. Never hand-edit, overwrite, relabel, promote, or infer acceptance of evidence.

Before authentication, artifact download, hosted dispatch, publication, destructive work, or another consequential external action, explicitly check the exact action and target against the active authorization and exclusions. Use the least-powerful applicable tool. If a call fails, classify the failure before choosing a materially different next action; refresh interface documentation after reset, compaction, or an interface error and never retry through a prohibited route merely to obtain diagnostics.

Run `maintain.py doctor --verbose` as the canonical full post-edit doctor after relevant focused and complete-suite checks. Stop when the authorized deliverable and approval packet are complete, when a required runtime is unavailable, or before any separately approval-gated action. Present material behavior or contract changes for explicit approval and record only an accepted outcome.

Use `maintain.py expect` for demonstrations that are supposed to return nonzero. Do not mask failures with unconditional success operators.

The source-repository topology is discovered automatically. For a separately installed maintainer plugin, set `WAYFINDER_SKILL_ROOT` to the exact `wayfinder` skill directory and, if needed, `WAYFINDER_REPOSITORY_ROOT` to the repository root. Record those paths; never infer or download a target package.

This skill owns Wayfinder's design record, research, tooling, demonstrations, and certification evidence. `$wayfinder` contains only runtime instructions and the executable contract package; it remains the project-record workflow.
