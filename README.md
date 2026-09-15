# Wayfinder

Wayfinder is a portable agent plugin for building, maintaining, validating, and selectively consulting a durable, repository-owned project record. The repository also contains an independently installable maintainer plugin for contract development, conformance testing, and certification.

<!-- WAYFINDER-GENERATED:README-BANNER:BEGIN -->
> [!IMPORTANT]
> Wayfinder `v1-candidate-revision-10` has accepted passing hosted evidence; evidence publication is **NOT-READY**; dispatch authorized: false. Runtime activation is disabled. Installing or forking this repository does not change that status.
<!-- WAYFINDER-GENERATED:README-BANNER:END -->

## Packages

<!-- WAYFINDER-GENERATED:README-PACKAGES:BEGIN -->
| Package | Audience | Status |
| --- | --- | --- |
| [`wayfinder`](plugins/wayfinder) | Project-record users | Runtime activation: disabled |
| [`wayfinder-maintainer`](plugins/wayfinder-maintainer) | Contributors and certifiers | Opt-in package; not listed in the end-user catalog |
<!-- WAYFINDER-GENERATED:README-PACKAGES:END -->

Each package uses one canonical skill tree and includes manifests for the Agent Plugins 1.0 format, Codex, and Claude. GitHub Copilot can consume the portable root manifest. No client-specific copy of either skill is maintained.

<!-- WAYFINDER-GENERATED:README-STATUS:BEGIN -->
## Repository status

- Candidate: `v1-candidate-revision-10`
- Contract: frozen
- Release: unactivated-frozen
- Activation: disabled
- Common conformance suite: 305 cases
- Hosted evidence exists: true; accepted: true; run `34921918384`, attempt `1`, source `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54`; all 8 entries passed
- Evidence publication: not-ready; dispatch authorized: false
- Evidence published: false
- Release registry updated: false
- Full-family certification claimed: false; cross-adapter recovery claimed: false
<!-- WAYFINDER-GENERATED:README-STATUS:END -->

See [architecture](docs/architecture.md), [compatibility](docs/compatibility.md), [certification](docs/certification.md), and [migration provenance](docs/migration-provenance.md).

## Development

<!-- WAYFINDER-GENERATED:DEVELOPMENT-REQUIREMENTS:BEGIN -->
Use Python 3.11 or newer.
<!-- WAYFINDER-GENERATED:DEVELOPMENT-REQUIREMENTS:END -->

```sh
python3 scripts/validate_repository.py
python3 plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py doctor
```

The certification workflow is manual-only. It records authentic hosted observations and cannot activate or publish a runtime release.

Maintainer history is organized into subject folders. Use `maintain.py record list`, `record read --id ID --history`, and `record add --input FILE [--dry-run]` through the same canonical command path above. See the [record-store guide](plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/design-record/README.md) for input fields and exact bounded reads. Current status and authorization remain in the maintainer's `current-state.md`.

Changes to either plugin use [Plan-to-PR Development](plugins/wayfinder-maintainer/skills/wayfinder-maintainer/resources/plan-to-pr-development/README.md): research-informed interviews, [repository plans](docs/plans/README.md), coherent PRs, and owner review. Use `maintain.py plan list`, `plan read --id ID --history`, and `plan create/update --input FILE [--dry-run]` to manage plans and preserve exact approvals. Approved implementation runs continuously within scope; agents stop without polling once owner reviews are requested.

## License

Licensed under the [Apache License 2.0](LICENSE).
