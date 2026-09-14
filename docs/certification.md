# Certification

- **Status:** Bounded matrix incomplete; hosted execution not yet run
- **Last updated:** 2026-09-14

The current target is the owner-accepted, frozen, unactivated `v1-candidate-revision-9`. Its local candidate and parity evidence is accepted; hosted certification remains separately unauthorized. The exact required matrix contains eight entries:

| Adapter runtime | macOS | Linux | Windows |
| --- | --- | --- | --- |
| CPython 3.14.7 | Required | Required | Required |
| Node.js 24.21.0 | Required | Required | Required |
| PowerShell 7.6.6 | Not in matrix | Required | Required |

Every entry must verify the native runtime implementation and exact version, OS family, architecture, locale, timezone, filesystem encoding, executable identity, and observed filesystem case behavior before running the exact registered adapter. Passing requires all 305 cases. The matrix must collectively observe both case-sensitive and case-insensitive filesystems.

The manual `certify.yml` workflow uses a fixed eight-row include list and `fail-fast: false`. Each successful entry creates immutable report filenames and a uniquely named Actions artifact. The aggregate job creates a passing matrix report only when every required entry passes and all bindings agree; otherwise it preserves an explicit inventory and reports the matrix incomplete.

Actions artifacts are review evidence, not durable accepted evidence. `publish-evidence.yml` is separate, manual, and environment-gated. It re-verifies a selected run and prepares a draft evidence release. The repository owner must configure the `evidence-publication` environment and GitHub immutable releases before publishing that draft.

This matrix is not independent evaluation, forward testing, cross-adapter recovery, or full-family certification. It cannot add release certification entries and does not authorize runtime guidance or activation.
