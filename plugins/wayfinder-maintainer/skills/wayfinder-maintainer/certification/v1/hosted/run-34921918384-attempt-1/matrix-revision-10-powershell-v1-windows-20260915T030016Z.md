# Wayfinder revision 9 environment evidence — powershell-v1 on Windows

- **Status:** passing-environment-entry-not-full-family-certification
- **Generated:** 2026-09-15T03:00:16Z
- **JSON report SHA-256:** `9bdcd2a7c38da06f41f6b6a929454b9a0d52ec1c0d165a4f1f4e5b7065dfe418`
- **Result-set SHA-256:** `de6613f623c9413ce5d3dabb27bb5bc8aad281d6efc28a50a8093f0dc9bcf116`

## Exact target and observed environment

| Field | Required | Observed |
| --- | --- | --- |
| Adapter | `powershell-v1` | `powershell-v1` |
| Runtime | `PowerShell 7.6.6` | `PowerShell 7.6.6` |
| OS family | `Windows` | `Windows` |
| Architecture | — | `x64` (host `AMD64`) |
| Locale | — | `LC_COLLATE=C;LC_CTYPE=English_United States.1252;LC_MONETARY=C;LC_NUMERIC=C;LC_TIME=C` |
| Timezone | — | `Coordinated Universal Time` (UTC offset 0 seconds) |
| Filesystem encoding | — | `utf-8` with `surrogatepass` errors |
| Filesystem case behavior | matrix requires both collectively | `case-insensitive` (observed by exclusive create) |
| Runtime executable | exact identity required | `D:\a\_temp\powershell-7.6.6\pwsh.exe` (`bfb46af89433268872ddb43d1ca7a3f433452ee91ed356a9786940f90118e285`) |
| Source commit | exact workflow checkout | `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54` |
| Workflow run | hosted provenance | `34921918384` attempt `1` |

## Conformance and bindings

- Cases: 305/305 passed; 0 failed.
- Contract: `0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341`
- Release: `581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083`
- Adapter: `b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9`
- Fixture index: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`
- Expected-output set: `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`
- Invocation observations: 900 at `3780de2e9f3849177ff2dd10a5ebc131c6893422aab843bb36faa73438d9930b`

## Limitations and unavailable observations

- This is maintainer-run evidence for one exact matrix entry, not independent validation.
- This environment report is not the aggregate matrix and is not full-family certification.
- It does not authorize runtime guidance, activation, forward tests, cross-adapter recovery, live-project work, or Git operations.
- statvfs characteristics are unavailable on this host
- the Python standard library does not expose a portable filesystem type or stable volume serial
