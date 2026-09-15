# Wayfinder repository instructions

## Scope

- This repository contains two plugin packages: `plugins/wayfinder` for runtime use and `plugins/wayfinder-maintainer` for maintenance and certification.
- `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/current-state.md` is the sole authority for the current candidate, evidence, activation, and authorized-tranche status. Do not duplicate that mutable status here.
- A public repository, installable plugin metadata, or a green workflow does not activate Wayfinder or establish full-family certification.

## Maintenance routing

- For changes to Wayfinder itself, first read the complete maintainer `SKILL.md` and `references/current-state.md`.
- Read `references/workflow.md` when changing, testing, certifying, publishing, or activating Wayfinder. Discover maintainer history with `maintain.py record list`; read exact routed records with `record read --id ID --history`. Before reopening a decision, changing evidence governance, or recording acceptance, read the complete affected history and decisive linked authority/evidence, expanding on conflicts or missing dependencies. Unrelated chronology is not a routine prerequisite.
- Add historical outcomes with `maintain.py record add --input FILE`; never silently rewrite accepted history. Persist accepted decisions and closures together with an explicit current-state routing update in the authorized record task. See the maintainer `references/design-record/README.md` for input fields, completeness, and migration integrity.
- Before requesting or processing an explicit acceptance, authorization, or approval, follow the maintainer [approval-response protocol](plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/approval-response.md). An affirmative requires the bounded new-session handoff and stop; a rejection requires the facilitated one-material-question-per-turn interview. Never begin the next task automatically.
- Treat current state as the default boundary. A later explicit owner instruction may authorize a named bounded tranche; quote its scope and exclusions before acting, and do not infer authority for a later tranche.
- Run the canonical maintainer doctor with Python 3.11 or newer before and after maintenance work.
- Preserve accepted evidence and frozen governed bytes. Never overwrite or relabel an evidence file.

## Tool and authorization discipline

- Before network mutation, authentication, artifact download, publication, dispatch, destructive work, or another consequential external action, verify the exact action and target against the active tranche. Explicit exclusions always win.
- After a tool reset, session compaction, or interface error, refresh the tool documentation and current state before another action. Classify a failed call as interface, sandbox/network, authentication, authorization, external-state, truncation, incomplete-discovery, or side-effect contamination; do not repeat the same path without a materially different reason.
- Resolve runtimes and inspect command help once per uninterrupted session and reuse them while the executable and checkout remain unchanged. Parallelize only independent read-only work.

## Repository boundaries

- Keep the two plugin packages independently installable. Do not copy a skill into client-specific directories.
- Keep portable metadata in each plugin's root `plugin.json`; compatibility manifests must agree with it.
- Do not edit frozen contract assets, registered adapters, accepted historical evidence, or accepted parity evidence without explicit authorization to reopen the candidate.
- Do not treat CI artifacts as durable accepted evidence. Publication of evidence is a separate, approval-gated workflow.
- Do not add dependencies, network services, hooks, or MCP servers without an accepted design decision.

## Verification

- Use `python3 scripts/validate_repository.py` for repository and manifest validation.
- Use `python3 plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py doctor` for contract and evidence integrity.
- Run focused conformance checks proportional to the changed surface.
- Keep all governed text UTF-8 without BOM and LF-only on every platform.
