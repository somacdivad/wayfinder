# Repository architecture

- **Status:** Accepted
- **Last updated:** 2026-09-14

The repository is a marketplace and source container, not a plugin itself. It contains two independently installable packages:

```text
plugins/wayfinder/skills/wayfinder
plugins/wayfinder-maintainer/skills/wayfinder-maintainer
```

`wayfinder` contains runtime instructions, the frozen executable contract, and registered adapters. `wayfinder-maintainer` contains design history, research, conformance tooling, and certification evidence. This boundary prevents ordinary runtime installations from receiving high-authority maintainer instructions or the larger evidence corpus.

Each plugin has one skill-content source. The root `plugin.json` is the portable Agent Plugins 1.0 manifest. `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` are compatibility projections validated against the portable identity. Client-specific skill copies and symlink indirection are prohibited.

The package version `1.0.0-rc.8` is distribution metadata only. It does not modify the semantic contract version, candidate revision, governed release registry, certification state, or activation state.
