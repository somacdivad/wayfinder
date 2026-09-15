# Wayfinder revision 9 environment evidence — node-v1 on macOS

- **Status:** passing-environment-entry-not-full-family-certification
- **Generated:** 2026-09-15T02:41:09Z
- **JSON report SHA-256:** `60528f64e878d9a11054b9457a3bf0e578139abec27c41633a7e69e7d57e589e`
- **Result-set SHA-256:** `5bcfc75e48252a3711b9ca9778434eddf08e6e2918de4a4b3d576372593d2a44`

## Exact target and observed environment

| Field | Required | Observed |
| --- | --- | --- |
| Adapter | `node-v1` | `node-v1` |
| Runtime | `Node.js 24.21.0` | `Node.js 24.21.0` |
| OS family | `macOS` | `macOS` |
| Architecture | — | `x64` (host `x86_64`) |
| Locale | — | `C/en_US.UTF-8/C/C/C/C` |
| Timezone | — | `UTC` (UTC offset 0 seconds) |
| Filesystem encoding | — | `utf-8` with `surrogateescape` errors |
| Filesystem case behavior | matrix requires both collectively | `case-insensitive` (observed by exclusive create) |
| Runtime executable | exact identity required | `/Users/runner/hostedtoolcache/node/24.21.0/x64/bin/node` (`7abcf39bd37ab251015337ff75304d7555f0d8e88c6e0fbf04bce8ce34636f49`) |
| Source commit | exact workflow checkout | `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54` |
| Workflow run | hosted provenance | `34921918384` attempt `1` |

## Conformance and bindings

- Cases: 305/305 passed; 0 failed.
- Contract: `0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341`
- Release: `581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083`
- Adapter: `f6d695e60e5964448947ed9f835526efa0f84e3764fb8acdd7f765e3bbe4fa3e`
- Fixture index: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`
- Expected-output set: `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`
- Invocation observations: 900 at `ccc23ed1d3b1548c0237376365b36d371b84392eda6dbfd46dcaa14d2865a1e4`

## Limitations and unavailable observations

- This is maintainer-run evidence for one exact matrix entry, not independent validation.
- This environment report is not the aggregate matrix and is not full-family certification.
- It does not authorize runtime guidance, activation, forward tests, cross-adapter recovery, live-project work, or Git operations.
- the Python standard library does not expose a portable filesystem type or stable volume serial
