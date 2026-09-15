# Wayfinder

Wayfinder is a portable agent plugin for building, maintaining, validating, and selectively consulting a durable, repository-owned project record. The repository also contains an independently installable maintainer plugin for contract development, conformance testing, and certification.

> [!IMPORTANT]
> Wayfinder is not activated for runtime use. The `v1-candidate-revision-10` Windows correction is owner-accepted, but it has no revision-10 hosted evidence; accepted revision-9 evidence is historical and cannot certify the revised source. Installing or forking this repository does not change that status.

## Packages

| Package | Audience | Status |
| --- | --- | --- |
| [`wayfinder`](plugins/wayfinder) | End users after activation | Portable package present; runtime instructions intentionally block unfinished workflows |
| [`wayfinder-maintainer`](plugins/wayfinder-maintainer) | Contributors and certifiers | Opt-in package; not listed in the end-user catalog |

Each package uses one canonical skill tree and includes manifests for the Agent Plugins 1.0 format, Codex, and Claude. GitHub Copilot can consume the portable root manifest. No client-specific copy of either skill is maintained.

## Repository status

- Candidate: `v1-candidate-revision-10`
- Contract: frozen
- Release: unactivated
- Common conformance suite: 305 cases
- Accepted local adapter parity: revision 9 only; all three adapters passed 305/305 and 900 normalized invocations agreed
- Environment matrix: revision 10 has no hosted entries; Windows or full-family certification is not claimed

See [architecture](docs/architecture.md), [compatibility](docs/compatibility.md), [certification](docs/certification.md), and [migration provenance](docs/migration-provenance.md).

## Development

Use Python 3.11 or newer:

```sh
python3 scripts/validate_repository.py
python3 plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py doctor
```

The exact eight-entry certification workflow is manual-only. It records authentic hosted observations and cannot activate or publish a runtime release.

## License

Licensed under the [Apache License 2.0](LICENSE).
