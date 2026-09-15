# Certification

- **Status:** Candidate revision 10 evidence-publication readiness accepted as NOT READY; dispatch unauthorized; activation disabled
- **Last updated:** 2026-09-14

The current target is the frozen, unactivated `v1-candidate-revision-10`. The owner accepted GitHub Actions run `34921918384`, attempt `1`, at source commit `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54`; all eight exact entries passed 305/305 and the strict aggregate passed. The exact 27 verified files are preserved at `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/certification/v1/hosted/run-34921918384-attempt-1/`. The aggregate JSON is `be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50`, the aggregate Markdown is `ffe1fe3dc6ae9ed1b21356943ea8f98451221a5e8248043d74cf21c5a0b3cf18`, and the matrix digest is `2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0`. Accepted revision-8 and revision-9 evidence remains immutable historical evidence. The exact required matrix contains eight entries:

| Adapter runtime | macOS | Linux | Windows |
| --- | --- | --- | --- |
| CPython 3.14.7 | Required | Required | Required |
| Node.js 24.21.0 | Required | Required | Required |
| PowerShell 7.6.6 | Not in matrix | Required | Required |

Every entry must verify the native runtime implementation and exact version, OS family, architecture, locale, timezone, filesystem encoding, executable identity, and observed filesystem case behavior before running the exact registered adapter. Passing requires all 305 cases. The matrix must collectively observe both case-sensitive and case-insensitive filesystems.

The manual `certify.yml` workflow uses a fixed eight-row include list and `fail-fast: false`. Each successful entry creates immutable report filenames and a uniquely named Actions artifact. The aggregate job creates a passing matrix report only when every required entry passes and all bindings agree; otherwise it preserves an explicit inventory and reports the matrix incomplete.

The promoted files are accepted durable maintainer-owned bounded evidence for this exact source, run, and attempt. They do not create a release-registry certification entry or broaden the claim. The protected-environment evidence-publication readiness review is accepted as NOT READY, and no dispatch is authorized. Although source-publication commit `72da3542f3a7e65f4bcae09943612d8ba09daf3e` contains the corrected `publish-evidence.yml`, its checkout step replaces the worktree with evidence source commit `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54`; the next step would therefore invoke the older revision-9 verifier, which does not accept `--expected-run-id` or `--expected-attempt`, and would fail argument parsing before draft-release creation. The `evidence-publication` environment exists with sole required reviewer `somacdivad`, `prevent_self_review: false`, `can_admins_bypass: false`, no wait timer, and no deployment-branch restrictions. Repository-level immutable releases are enabled. These settings do not overcome the workflow/verifier blocker or make publication dispatch-eligible.

This matrix is not independent evaluation, forward testing, cross-adapter recovery, or full-family certification. It cannot add release certification entries and does not authorize runtime guidance or activation.
