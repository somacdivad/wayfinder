# Client compatibility

- **Status:** Implemented packaging; smoke validation pending hosted repository access
- **Last updated:** 2026-09-14

## Codex

Codex metadata is in `.codex-plugin/plugin.json`, with OpenAI-specific skill presentation and invocation policy in each skill's `agents/openai.yaml`. The repository-local Codex marketplace is `.agents/plugins/marketplace.json`.

## Claude

Claude metadata is in `.claude-plugin/plugin.json` within each package. The repository catalog is `.claude-plugin/marketplace.json`. `CLAUDE.md` imports the shared contributor instructions from `AGENTS.md`.

## GitHub Copilot

Copilot consumes the portable Agent Plugins 1.0 `plugin.json` and fixed `skills/` directory. No Copilot-specific extension is currently necessary.

The public catalog lists only `wayfinder`. `wayfinder-maintainer` remains public and directly installable for contributors but is deliberately absent from the end-user catalog. Packaging compatibility does not imply identical optional-field behavior across clients and does not certify the Wayfinder semantic contract.
