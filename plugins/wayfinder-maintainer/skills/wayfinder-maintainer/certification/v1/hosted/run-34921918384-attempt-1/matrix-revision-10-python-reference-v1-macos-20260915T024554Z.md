# Wayfinder revision 9 environment evidence — python-reference-v1 on macOS

- **Status:** passing-environment-entry-not-full-family-certification
- **Generated:** 2026-09-15T02:45:54Z
- **JSON report SHA-256:** `fc6a9c11fad47699474cf83cc6aa4ceb05ce5d3632712ae7108c9a5cf2744584`
- **Result-set SHA-256:** `d5e0bb700666142ff5d116f81b5d784525a64f203f131f3354b61abaaf217b59`

## Exact target and observed environment

| Field | Required | Observed |
| --- | --- | --- |
| Adapter | `python-reference-v1` | `python-reference-v1` |
| Runtime | `CPython 3.14.7` | `CPython 3.14.7` |
| OS family | `macOS` | `macOS` |
| Architecture | — | `x86_64` (host `x86_64`) |
| Locale | — | `C/en_US.UTF-8/C/C/C/C` |
| Timezone | — | `UTC` (UTC offset 0 seconds) |
| Filesystem encoding | — | `utf-8` with `surrogateescape` errors |
| Filesystem case behavior | matrix requires both collectively | `case-insensitive` (observed by exclusive create) |
| Runtime executable | exact identity required | `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14` (`81c87d90892fe12428ee3b78a675c57c62d6c479236fb359ad5b2d7f07c38b2c`) |
| Source commit | exact workflow checkout | `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54` |
| Workflow run | hosted provenance | `34921918384` attempt `1` |

## Conformance and bindings

- Cases: 305/305 passed; 0 failed.
- Contract: `0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341`
- Release: `581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083`
- Adapter: `e0b89ba35f223567efe2545d323d816dbaeeedfa8de8fb784fcc7b1c347cb596`
- Fixture index: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`
- Expected-output set: `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`
- Invocation observations: 900 at `3fa39b2c741a5c2a095614f0a930638ccd553cc6f2624c5891af080c926ca7b3`

## Limitations and unavailable observations

- This is maintainer-run evidence for one exact matrix entry, not independent validation.
- This environment report is not the aggregate matrix and is not full-family certification.
- It does not authorize runtime guidance, activation, forward tests, cross-adapter recovery, live-project work, or Git operations.
- the Python standard library does not expose a portable filesystem type or stable volume serial
