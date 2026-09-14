---
name: wayfinder-maintainer
description: Maintain, version, test, certify, freeze, or prepare activation of the Wayfinder executable contract and adapters. Use only for work on Wayfinder itself; do not use to initialize, update, validate, or consult an ordinary project record.
---

# Wayfinder Maintainer

Maintain the Wayfinder skill without treating passing hashes or fixture counts as proof that its contract artifacts agree semantically.

## Required workflow

1. Read the applicable repository instructions and [the maintainer design record](references/design-record.md).
2. Run `python3 plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py doctor` with a verified Python 3.11+ interpreter before editing. If the default `python3` is older, select a supported configured runtime once and reuse it.
3. Read [the maintenance workflow](references/workflow.md) for candidate changes, evidence generation, certification, freeze, or activation work.
4. Keep each change bounded by the user's authorization. Passing a tranche does not authorize parity, freeze, publication, activation, Git mutation, external access, or live project-record changes.
5. Run the canonical maintainer command instead of reconstructing audit one-liners. Use its adapter selector and parity command for parity work. Never hand-edit or implicitly overwrite accepted evidence.
6. Present material behavior or contract changes for explicit approval and record only the accepted result.

Use `maintain.py expect` for demonstrations that are supposed to return nonzero. Do not mask failures with unconditional success operators.

The source-repository topology is discovered automatically. When the maintainer plugin is installed separately or must target another checkout, set `WAYFINDER_SKILL_ROOT` to the exact `wayfinder` skill directory and, if needed, `WAYFINDER_REPOSITORY_ROOT` to the working repository root. Record those paths in the maintenance handoff; never infer or download a target package.

This skill owns Wayfinder's design record, research, tooling, demonstrations, and certification evidence. `$wayfinder` contains only runtime instructions and the executable contract package; it remains the project-record workflow.
