# Wayfinder revision 8 environment evidence — python-reference-v1 on macOS

- **Status:** passing-environment-entry-not-full-family-certification
- **Generated:** 2026-09-14T12:52:08Z
- **JSON report SHA-256:** `6b43c2f0b41e83d76218e363651d6353ab62561426e4c7abf997cb561aa3fd78`
- **Result-set SHA-256:** `3b70db99a1cc2caa40a3e472dbf742b2b10cf2b467a191c124ff9e35685d8757`

## Exact target and observed environment

| Field | Required | Observed |
| --- | --- | --- |
| Adapter | `python-reference-v1` | `python-reference-v1` |
| Runtime | `CPython 3.14.7` | `CPython 3.14.7` |
| OS family | `macOS` | `macOS` |
| Architecture | — | `arm64` (host `arm64`) |
| Locale | — | `C/C.UTF-8/C/C/C/C` |
| Timezone | — | `UTC` (UTC offset 0 seconds) |
| Filesystem encoding | — | `utf-8` with `surrogateescape` errors |
| Filesystem case behavior | matrix requires both collectively | `case-insensitive` (observed by exclusive create) |
| Runtime executable | exact identity required | `/Users/davidamos/.local/share/uv/python/cpython-3.14.7-macos-aarch64-none/bin/python3.14` (`e925fab5e8f595817ff36ff28e214b91520c040d5b7d47249b0199bc5f68015e`) |

## Conformance and bindings

- Cases: 305/305 passed; 0 failed.
- Contract: `75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b`
- Release: `677fa5af49c11532d49875bd8d1138a36903668449188e6358f2d0a5947f2284`
- Adapter: `d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4`
- Fixture index: `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`
- Expected-output set: `c0fad6a47eff844f27135620e07210d081f19fab88aaa962cf5f0a6fb563ed7e`
- Invocation observations: 900 at `6afa780f483dcb081634000b34edfdc5ccef404b3cf75b3560460c53f33a4c16`

## Limitations and unavailable observations

- This is maintainer-run evidence for one exact matrix entry, not independent validation.
- This environment report is not the aggregate matrix and is not full-family certification.
- It does not authorize runtime guidance, activation, forward tests, cross-adapter recovery, live-project work, or Git operations.
- the Python standard library does not expose a portable filesystem type or stable volume serial
