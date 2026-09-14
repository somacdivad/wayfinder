# Wayfinder repository instructions

## Scope and status

- This repository contains two plugin packages: `plugins/wayfinder` for runtime use and `plugins/wayfinder-maintainer` for maintenance and certification.
- Wayfinder is currently `v1-candidate-revision-8`: a frozen semantic contract and an unactivated release.
- A public repository, installable plugin metadata, or a green workflow does not activate Wayfinder or establish full-family certification.

## Start with the maintainer record

- For changes to Wayfinder itself, read `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/SKILL.md`, its `references/design-record.md`, and `references/workflow.md` before editing.
- Run the canonical maintainer doctor with Python 3.11 or newer before and after maintenance work.
- Preserve accepted evidence and frozen governed bytes. Never overwrite or relabel an evidence file.

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
