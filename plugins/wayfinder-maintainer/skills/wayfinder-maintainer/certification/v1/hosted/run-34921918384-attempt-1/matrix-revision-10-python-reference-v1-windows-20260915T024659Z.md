# Wayfinder revision 9 environment evidence — python-reference-v1 on Windows

- **Status:** passing-environment-entry-not-full-family-certification
- **Generated:** 2026-09-15T02:46:59Z
- **JSON report SHA-256:** `1fe12a77ebf5c6c1e2ae7f1161f80685473924503fcb210af0d6cb7d0f806e1d`
- **Result-set SHA-256:** `d5e0bb700666142ff5d116f81b5d784525a64f203f131f3354b61abaaf217b59`

## Exact target and observed environment

| Field | Required | Observed |
| --- | --- | --- |
| Adapter | `python-reference-v1` | `python-reference-v1` |
| Runtime | `CPython 3.14.7` | `CPython 3.14.7` |
| OS family | `Windows` | `Windows` |
| Architecture | — | `AMD64` (host `AMD64`) |
| Locale | — | `LC_COLLATE=C;LC_CTYPE=English_United States.1252;LC_MONETARY=C;LC_NUMERIC=C;LC_TIME=C` |
| Timezone | — | `Coordinated Universal Time` (UTC offset 0 seconds) |
| Filesystem encoding | — | `utf-8` with `surrogatepass` errors |
| Filesystem case behavior | matrix requires both collectively | `case-insensitive` (observed by exclusive create) |
| Runtime executable | exact identity required | `C:\hostedtoolcache\windows\Python\3.14.7\x64\python.exe` (`4942b86a6597e5aee0128daa00050ed79bc21f6e709a78eb19cbfeb0c2f39ac9`) |
| Source commit | exact workflow checkout | `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54` |
| Workflow run | hosted provenance | `34921918384` attempt `1` |

## Conformance and bindings

- Cases: 305/305 passed; 0 failed.
- Contract: `0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341`
- Release: `581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083`
- Adapter: `e0b89ba35f223567efe2545d323d816dbaeeedfa8de8fb784fcc7b1c347cb596`
- Fixture index: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`
- Expected-output set: `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`
- Invocation observations: 900 at `a6c59ff1ee542d115a9423748ee3922203dd2128cda3c9d47578f6c50da80372`

## Limitations and unavailable observations

- This is maintainer-run evidence for one exact matrix entry, not independent validation.
- This environment report is not the aggregate matrix and is not full-family certification.
- It does not authorize runtime guidance, activation, forward tests, cross-adapter recovery, live-project work, or Git operations.
- statvfs characteristics are unavailable on this host
- the Python standard library does not expose a portable filesystem type or stable volume serial
