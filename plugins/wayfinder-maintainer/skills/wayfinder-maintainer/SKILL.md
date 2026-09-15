---
name: wayfinder-maintainer
description: Plan and deliver PR-based changes to Wayfinder or Wayfinder-maintainer; maintain, test, certify, freeze, or prepare activation of the executable contract and adapters. Use for either plugin, not an ordinary project record.
---

# Wayfinder Maintainer

Maintain the Wayfinder skill without treating passing hashes or fixture counts as proof that its contract artifacts agree semantically.

## Plan-to-PR Development

For changes to either plugin, use [Plan-to-PR Development](resources/plan-to-pr-development/README.md). Read its planning interview and research guidance before establishing a plan; read plan management for storage and approval; then read PR boundaries, implementation, and review guidance as those phases arise. Interview one material question per turn until the plan is decision-complete. Save every plan outside the plugins in `docs/plans` and obtain explicit approval of the complete version.

Use `maintain.py plan list`, `plan read --id ID --history`, and `plan create/update --input FILE [--dry-run]`; inspect subcommand help and [plan management](resources/plan-to-pr-development/plan-management.md) for inputs and exact snapshot/concurrency rules. The living plan owns task scope and progress; accepted decisions and closure belong in design history, with current authorization routed solely through current state.

Implement the approved PR sequence continuously within its named authority, pausing for material deviations or named checkpoints. Stack only genuine dependencies using native GitHub stacks; if support is unavailable, pause to propose a fallback. Request the owner's review on all ready PRs with one consolidated version-bound question. If the approved plan explicitly includes terminal receipt persistence, save returned receipts or uncertain delivery state, then stop without polling until the owner returns. Version-bound explicit approval permits eligible merging subject to protections and dependencies; review completion alone does not.

## Start with compact state

1. Read the applicable repository instructions and [current maintainer state](references/current-state.md).
2. Resolve the requested CPython, Node.js, and PowerShell executables once, record unavailable runtimes honestly, and reuse the resolved paths. Do not install dependencies without authorization.
3. Inspect `maintain.py --help` and the selected subcommand help instead of reconstructing commands.
4. Run the canonical pre-edit doctor with a verified Python 3.11+ interpreter: `maintain.py doctor --format full`. Use the same interpreter for the tranche.
5. Read [the maintenance workflow](references/workflow.md) when changing, testing, certifying, freezing, or preparing activation.

Routine maintenance starts with the compact state and [design-record guide](references/design-record/README.md). Discover history with `maintain.py record list`, then use `record read --id ID --history` for exact routed records. Before reopening a decision, changing evidence governance, or recording an accepted outcome, read the complete affected history and all decisive linked authority/evidence sources. Expand on conflicts or missing dependencies; unrelated chronology is not a routine prerequisite. The [legacy entrypoint](references/design-record.md) retains old heading anchors as navigation only.

Before asking the owner for acceptance, authorization, or approval, and when processing the owner's response to such a request, read and follow the canonical [approval-response protocol](references/approval-response.md).

## Efficient execution

- Use `maintain.py describe` (or `context`) for canonical paths, candidate identity, case counts, adapter registry, runtime requirements, and the current approval boundary.
- Treat `describe/context` as a discovery preview: routing is not source authority. Use the exact next read command and read every decisive source completely before a consequential conclusion.
- Interactive output uses `--format summary|json|full`; JSON has a versioned response envelope with named scope, response class, completeness, truncation, counts, bytes, source hash, and continuation. Defaults are 16 KiB for previews and 64 KiB for complete output, configurable with `--max-bytes`.
- A `discovery-preview` may be partial only for routing. A `complete-evidence` response must be complete for its named scope or expose digest-bound chunks; reconstruct all chunks and verify the source SHA-256 before relying on a chunked source.
- Never use a truncated or incomplete response to support authorization, mutation, certification, publication, evidence promotion, or activation. Classify truncation, mark dependent conclusions unproven, and use the supplied narrower command or cursor; never repeat the identical broad call.
- `record list` returns bounded metadata and exact next commands; `record read --id ID [--history] --format json --max-bytes N` returns exact source chunks with stable byte ranges, hashes, and continuation. Continue with the same selector, budget, and class. Reconstruct the whole sequence before consequential conclusions; a changed store or cursor binding fails closed. `record-section --heading HEADING` remains a unique-title compatibility alias; old cursors are stale after migration.
- `record add --input FILE [--dry-run]` exclusively creates one new context, proposal, decision, verification, or closure record from explicit metadata and Markdown. See the guide for closed JSON fields. It never infers or authenticates owner approval and never changes current state, Git, or the network. Corrections and later outcomes use new predecessor-linked records. Persist accepted outcomes and closures with an explicit current-state routing update in the same authorized task.
- `describe --format json --field FIELD --sort FIELD` projects its curated routing inventory without source bodies. Repeat `--field`; unknown or duplicate fields are errors.
- `status` checks public projections against the canonical JSON object embedded in `current-state.md`. `status --format full` previews exact changes; only explicitly authorized `status --write` replaces declared regions/fields. Doctor and repository validation never rewrite drift.
- For compaction, use `checkpoint create --input FILE|- [--output PATH]` with explicit session facts. Output files must be new and outside the repository. Checkpoints are ephemeral, derived, non-authoritative, contain no source bodies or secrets, and never enter accepted evidence or current state. Run `checkpoint verify --checkpoint PATH` before reuse; stale checks must be rerun against refreshed authoritative sources.
- Batch focused cases in one invocation: `maintain.py test --case ID --case ID`. Select one adapter with `--adapter ID`; an unavailable unrelated runtime does not block that focused run.
- Prefer summary or JSON output. Use verbose output when per-check or per-case detail is required.
- Bound parallel read output and keep chunks non-overlapping. Do not repeat a successful check unless inputs changed, scope increased, or a failure creates a new risk.
- Reuse resolved runtime paths, command help, `describe`, and unchanged pre-edit hashes within one uninterrupted session. Refresh them after compaction, tool reset, checkout change, or a relevant file edit.
- Use `maintain.py self-test` for maintainer regressions; it discovers every maintainer-owned `test_*.py` module without leaving bytecode in the repository. Do not invoke individual test modules as the canonical regression run.
- Use `maintain.py record list --topic TOPIC` for discovery and `record read --id ID --history` for complete affected history instead of broad ad hoc chronology reads. Inspect `record add --help` before adding records; use dry-run to review exact prospective bytes.
- Use `maintain.py matrix-review --artifact-dir DIR` only on already-downloaded artifacts. It is offline, read-only, and cannot accept or publish evidence.
- Use `maintain.py freeze-proposal --output DIR` only after the revision-scoped candidate and parity reports pass; it exclusively creates a pending proposal and never records owner acceptance.
- Use `maintain.py freeze-acceptance --output DIR --accept-option-a` only after the owner explicitly accepts Option A; it binds the exact proposal and exclusively creates the acceptance record without authorizing later work.

## Authority and stopping rules

Keep every change inside the user's authorization. Passing a tranche does not authorize parity, freeze, hosted execution, publication, activation, Git mutation, external access, or live project-record changes. Never hand-edit, overwrite, relabel, promote, or infer acceptance of evidence.

Before authentication, artifact download, hosted dispatch, publication, destructive work, or another consequential external action, explicitly check the exact action and target against the active authorization and exclusions. Use the least-powerful applicable tool. If a call fails, classify the failure before choosing a materially different next action; refresh interface documentation after reset, compaction, or an interface error and never retry through a prohibited route merely to obtain diagnostics.

Run `maintain.py doctor --format full` as the canonical full post-edit doctor after relevant focused and complete-suite checks. Stop when the authorized deliverable and approval packet are complete, when a required runtime is unavailable, or before any separately approval-gated action. Present material behavior or contract changes for explicit approval and record only an accepted outcome.

Use `maintain.py expect` for demonstrations that are supposed to return nonzero. Do not mask failures with unconditional success operators.

The source-repository topology is discovered automatically. For a separately installed maintainer plugin, set `WAYFINDER_SKILL_ROOT` to the exact `wayfinder` skill directory and, if needed, `WAYFINDER_REPOSITORY_ROOT` to the repository root. Record those paths; never infer or download a target package.

This skill owns Wayfinder's design record, research, tooling, demonstrations, and certification evidence. `$wayfinder` contains only runtime instructions and the executable contract package; it remains the project-record workflow.

For approval packets, delivery recovery, and coverage-aware summaries, read [local review and verification CLI](resources/plan-to-pr-development/reliability-cli.md). Use `maintain.py review`, `delivery`, and `verification`; artifacts live alongside repository plans, and local validation never infers approval or platform eligibility.
