# Wayfinder version-1 proposed freeze readiness packet

- **Status:** Proposed; pending explicit owner approval
- **Prepared:** 2026-09-13
- **Release:** `v1-candidate-revision-8`
- **Contract status:** Frozen parity target proposed
- **Release status:** Unactivated frozen
- **Runtime activation:** Disabled

## Starting readiness

Candidate revision 7 was accepted but was not freeze-ready. Its 303 passing cases and valid hashes established internally consistent local Python evidence, not freeze readiness.

The audit found these blockers and ambiguities:

1. Accepted policy defined freeze semantics but not its physical representation, status transition, or authoritative invalidation metadata.
2. The release descriptor named one fixed Python adapter, so freezing its governed schema would have forced a semantic-contract change when Node.js or PowerShell was added.
3. Five of 96 normative rules had no direct conformance-case citation: `WF-PKG-003`, `WF-PROBE-002`, `WF-PROBE-003`, `WF-INTAKE-004`, and `WF-PLAN-005`.
4. Governed expected outputs lacked one review record mapping each expectation back to normative authority.
5. The required future environment matrix used dynamic “current supported” language rather than pinned runtime versions.
6. Freeze invalidation requirements existed in research prose but were not machine-checked against a proposed freeze identity.

No remaining diagnostic-precedence ambiguity, fixture expectation without recorded normative authority, governed-scope omission, or runtime/maintainer ownership violation was found after the corrections below.

## Decision accepted during this tranche

The owner selected the dual-layer representation on 2026-09-13:

- machine-visible contract and release freeze status in the executable package; and
- a maintainer-owned proposed-freeze record containing review, evidence, matrix, and invalidation metadata.

This decision accepted the representation, not the freeze result. This packet remains proposed.

## Corrections and observable behavior

- Candidate identity advanced from revision 7 to revision 8 because governed bytes changed.
- `contract.json` now reports `frozen`; `release.json` reports `unactivated-frozen`.
- `release.json` now uses a closed ordered adapter registry and an ordered certification array. Only `python-reference-v1` is present and the certification array is empty.
- Package verification rejects digest-valid release-schema status disagreement and adapter-registry disagreement.
- All 96 normative rules are directly cited by at least one of 305 cases. Counts provide traceability, not semantic proof.
- Every governed expected-output file has a recorded review mapping to normative rules.
- The future matrix pins CPython 3.14.7, Node.js 24.21.0, and PowerShell 7.6.6. These are requirements, not availability or certification claims.
- Any governed-byte or semantic change after acceptance must reopen the candidate, advance the revision, invalidate affected evidence, and rerun every adapter.
- The Python adapter remains an implementation under test. No Python behavior is treated as normative authority.

## Proposed identity and digests

- Contract SHA-256: `75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b`
- Release SHA-256: `69d029df64b5ac553aedab0d6127d3b99371f77847a7e41defac459b7e3c773e`
- Python adapter SHA-256: `d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4`
- Fixture-index SHA-256: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`
- Expected-output-set SHA-256: `c0fad6a47eff844f27135620e07210d081f19fab88aaa962cf5f0a6fb563ed7e`
- Result-set SHA-256: `6cb5f6f61a5000bd69cd175dd4835feca61366ea0f9c2c9fbb483b8f12cfa022`

## Conformance and local evidence

All 305 of 305 cases passed:

- `apply`: 51
- `command`: 9
- `discovery`: 10
- `generation`: 10
- `harness`: 1
- `initialize`: 49
- `intake`: 17
- `inventory`: 21
- `json`: 16
- `manifest`: 21
- `package`: 11
- `property`: 6
- `record`: 71
- `render`: 12

The local report used CPython 3.12.14 on macOS 26.6.2 arm64, locale `C.UTF-8`, host-default timezone, and local temporary filesystems whose case sensitivity was not independently characterized. This is maintainer-run local Python evidence only.

PyYAML was unavailable. The accepted dependency-free checks were used once without retrying or installing dependencies.

## Preserved and missing evidence

Slice 1–5 and candidate revisions 6 and 7 evidence remain byte-preserved and hash-pinned. Revision 8 evidence was created separately and a second creation attempt correctly refused to overwrite it.

Still missing:

- Node.js and PowerShell implementations and evidence;
- macOS, Linux, and Windows release-matrix evidence;
- verified case-sensitive and case-insensitive filesystem coverage;
- cross-adapter comparison and cross-adapter recovery;
- independent-agent evaluation;
- full-family certification;
- read-only MyPond dogfood review;
- runtime guidance and activation evidence.

These omissions do not waive future gates and are not reported as passing.

## Files changed

- `skills/wayfinder/SKILL.md`
- `skills/wayfinder/assets/contract-v1/release.json`
- `skills/wayfinder/assets/contract-v1/contract.json`
- `skills/wayfinder/assets/contract-v1/schemas/release.schema.json`
- `skills/wayfinder/assets/contract-v1/conformance/v1/cases.json`
- `skills/wayfinder/assets/contract-v1/conformance/v1/expected/probe-deterministic.json`
- `skills/wayfinder/assets/contract-v1/conformance/v1/expected/initialize-minimal-golden.json`
- `skills/wayfinder/references/contracts/v1.md`
- `skills/wayfinder/scripts/adapters/wayfinder.py`
- `skills/wayfinder-maintainer/scripts/maintain.py`
- `skills/wayfinder-maintainer/scripts/conformance/v1/build_package.py`
- `skills/wayfinder-maintainer/scripts/conformance/v1/run.py`
- `skills/wayfinder-maintainer/references/design-record.md`
- `skills/wayfinder-maintainer/references/research/initialization-18-implementation-certification.md`
- `skills/wayfinder-maintainer/certification/v1/historical-sha256.json`
- `skills/wayfinder-maintainer/certification/v1/candidate-revision-8-local.json`
- `skills/wayfinder-maintainer/certification/v1/candidate-revision-8-local.md`
- `skills/wayfinder-maintainer/certification/v1/proposed-freeze-revision-8.json`
- `skills/wayfinder-maintainer/certification/v1/proposed-freeze-revision-8.md`

`docs/` is unchanged. Nothing was staged, committed, fetched, pushed, published, or installed.

## Approval checkpoint

- **Option A:** Accept candidate revision 8 as the frozen version-1 parity target. This authorizes later, separately requested Node.js and PowerShell implementations to target these frozen semantics. It does not begin that work, certify any adapter or environment, or activate Wayfinder.
- **Option B:** Request changes and leave revision 8 unaccepted. Candidate revision 7 remains the last accepted candidate.
- **Option C:** Reject the proposed freeze correction and preserve candidate revision 7 as the last accepted state.
