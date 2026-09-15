<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":1,"date":"2026-09-13","format":"wayfinder-design-record","id":"wr-0005","kind":"decision","legacy":{"sourceSectionSha256":"449289ae4479c58a73f21acd84521f3dce83269c4b2057efaef4069e9b304afc"},"outcome":"accepted","predecessors":[],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Stage 0 + Slice 1 implementation.","title":"Stage 0 + Slice 1 implementation","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Stage 0 + Slice 1 implementation

Implemented and accepted by the skill owner on 2026-09-13:

- `assets/contract-v1/release.json` is the fixed-path distribution trust root. It hashes the contract manifest and Python adapter but never itself, avoiding circular self-hashing.
- `assets/contract-v1/contract.json` enumerates and hashes the normative reference, schemas, known answers, fixture index, fixture inputs, and expected results beneath closed governed scopes. Maintainer runner code and generated certification evidence are deliberately outside semantic contract authority.
- `references/contracts/v1.md` assigns stable Slice 1 rule identifiers and owns normative semantics. JSON Schemas document closed machine shapes; the standard-library Python runtime performs validation itself.
- Strict JSON rejects BOM, CRLF, malformed UTF-8 and Unicode, duplicate or unknown fields, unsupported versions, floats/exponents, and integers outside the cross-runtime exact range. Canonical JSON uses UTF-16 object-name ordering and the version-1 integer-only subset.
- `probe` verifies the release, adapter, contract, every governed resource, nine fixed known answers, Python 3.11+, and required runtime capabilities. It separates deterministic results from environment evidence.
- `discover` implements exact-root and physical upward discovery, nearest-candidate selection, repository-boundary stopping, invalid-nearest refusal, strict live-manifest validation, containment, and symlink refusal without writes.
- The maintainer harness invokes the adapter as a black box, snapshots fixture trees, provides gated deterministic clock/operation-ID/failure-boundary controls for later slices, exercises seeded properties and mutations, and emits digest-bound local evidence.

Accepted consequential implementation choices:

1. Managed version-1 paths use a conservative portable ASCII segment profile and ASCII case-insensitive identity checks. This excludes otherwise NFC-valid non-ASCII filenames and is intentionally recorded rather than treated as an already accepted capability reduction.
2. Discovery identifies a containing Git worktree through the nearest `.git` directory or regular-file marker and treats a symbolic-link marker as a conservative stop. It does not invoke Git. This is deterministic and network-free but does not authenticate that an arbitrary `.git` marker is a valid worktree.
3. A discovered live manifest requires its record root, all entrypoints, module and collection roots, declared snapshot, and generated artifacts to exist with the required regular-file/directory type. The later initializer's pre-publication missing-path exception remains outside Slice 1.
4. Local evidence covers CPython 3.12 on one macOS host and temporary local filesystems only. It is not independent validation or the accepted multi-platform, multi-adapter certification matrix.

Evidence: [Stage 0 + Slice 1 local report](../../../../certification/v1/slice-1-local.md) and its [machine-readable form](../../../../certification/v1/slice-1-local.json).

### Approval progress

| Checkpoint | Status | Outcome |
| --- | --- | --- |
| 1 — Package and trust model | Accepted 2026-09-13 | The skill owner accepted the current package boundary, authority split, distribution-rooted release descriptor, non-circular digest graph, and adapter-verification model as Option A. No external signature or additional distribution pin is required in this tranche. |
| 2 — Runtime behavior and safety | Accepted 2026-09-13 | The skill owner accepted Option A: the current `probe`, physical nearest-manifest discovery, marker-based Git boundary, strict JSON and manifest parsing, portable ASCII managed-path profile, containment and symlink refusal, stable diagnostics, and read-only guarantees. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Stage 0 plus Slice 1 on the strength of the digest-bound local evidence, with the disclosed cross-platform, independence, adapter-family, and bundled-validator limitations. No follow-up exception was attached to the approval. |

