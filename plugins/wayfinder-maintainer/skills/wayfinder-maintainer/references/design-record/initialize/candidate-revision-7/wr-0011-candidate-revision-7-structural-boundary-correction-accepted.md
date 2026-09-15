<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":7,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0011","kind":"decision","legacy":{"sourceSectionSha256":"6a56531d7a01295caa9f98040d0a28113c479221bbc9db78698b9e0e917aaeed"},"outcome":"accepted","predecessors":["wr-0010"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 7 structural boundary correction — accepted.","title":"Candidate revision 7 structural boundary correction — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 7 structural boundary correction — accepted

Implemented on 2026-09-13 as the requested revision to candidate 6:

- `$wayfinder` now contains runtime instructions, its adapter, and the self-contained executable contract package. Governed conformance cases, inputs, and expected outputs moved to `assets/contract-v1/conformance/v1/` because they are part of that package rather than maintainer instructions.
- `$wayfinder-maintainer` now owns the maintainer design record, research, command, runner and package builder, demonstrations, and certification evidence.
- The runtime `SKILL.md` no longer describes or links a maintainer directory. The companion `SKILL.md` is the sole route into maintenance work and remains explicit-only.
- Package building and mutation tests accept an explicit Wayfinder skill root, so maintainer tools can verify both the installed sibling skill and isolated package copies without reintroducing a runtime-maintainer dependency.
- Candidate revision 7 preserves the revision-6 semantic identity check, evidence safeguards, historical pins, supported-runtime selection, no-bytecode checks, and approval boundaries.
- This structural correction adds no runtime capability and does not authorize parity, freeze, certification, publication, runtime activation, or live-project initialization.

Evidence: [candidate revision 7 local report](../../../../certification/v1/candidate-revision-7-local.md) and its [machine-readable form](../../../../certification/v1/candidate-revision-7-local.json). All 303/303 cases pass on local macOS with CPython 3.12.14. The contract digest is `79e5b4f0f89bff5b01c1a302745f8af5a27e17d26f29627b2e0a79f39cd9dc71`; the release descriptor digest is `3b08de7e5db25ea1b0818fa6606d365876ff9ca8e37d05a1e1ee8b293beef74e`; the Python adapter digest is `a4e62f8ce938e87157b964b8aabf061558368299f578695b70d1554241bf7de4`; and the result-set digest is `0281fb4b1d9eec4229f1ee8ca480c80b5308909a607e360955a67cd8c19958c6`. Candidate revision 6 evidence remains preserved and hash-pinned under this companion skill and is not relabeled as accepted evidence. This is maintainer-run local evidence, not independent validation or complete adapter-family certification.

### Candidate revision 7 approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Skill ownership and maintenance safety | Accepted 2026-09-13 | The skill owner selected Option A and accepted the complete removal of `skills/wayfinder/maintainers/`, relocation of governed package fixtures under runtime contract assets, ownership of all maintainer-only resources by `$wayfinder-maintainer`, the preserved revision-6 safeguards, and the 303/303 local revision-7 evidence. No follow-up exception was attached; parity, freeze, certification, publication, runtime guidance, activation, and live-project initialization remain unauthorized. |

