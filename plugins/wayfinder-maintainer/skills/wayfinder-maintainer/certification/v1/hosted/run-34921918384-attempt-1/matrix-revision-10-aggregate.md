# Wayfinder candidate revision 9 bounded certification matrix

- **Status:** Passing bounded matrix; not full-family certification
- **Generated:** 2026-09-15T03:00:32Z
- **JSON report SHA-256:** `be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50`
- **Matrix SHA-256:** `2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0`

All eight exact runtime/OS entries passed 305/305 cases and collectively observed case-sensitive and case-insensitive filesystems.

## Entries

- `python-reference-v1:CPython-3.14.7:macOS` — `fc6a9c11fad47699474cf83cc6aa4ceb05ce5d3632712ae7108c9a5cf2744584` — `case-insensitive`
- `python-reference-v1:CPython-3.14.7:Linux` — `93f1d5d274d220310446d827aa15c2a6236086dc8299050f61531e96631fd15c` — `case-sensitive`
- `python-reference-v1:CPython-3.14.7:Windows` — `1fe12a77ebf5c6c1e2ae7f1161f80685473924503fcb210af0d6cb7d0f806e1d` — `case-insensitive`
- `node-v1:Node.js-24.21.0:macOS` — `60528f64e878d9a11054b9457a3bf0e578139abec27c41633a7e69e7d57e589e` — `case-insensitive`
- `node-v1:Node.js-24.21.0:Linux` — `96d41381d0ad5b46cb877523ab6743e85288e571133153b5df86898952147cf4` — `case-sensitive`
- `node-v1:Node.js-24.21.0:Windows` — `0378ac26624fe8f0da50946af03f3332e4603ca6d9f172be984cd82060d50490` — `case-insensitive`
- `powershell-v1:PowerShell-7.6.6:Windows` — `9bdcd2a7c38da06f41f6b6a929454b9a0d52ec1c0d165a4f1f4e5b7065dfe418` — `case-insensitive`
- `powershell-v1:PowerShell-7.6.6:Linux` — `448e55a4eb78d1c36b39fe512ff8a06df52714a8f84a712d0e177b1e653913c7` — `case-sensitive`

## Limitations

- This aggregate covers only the bounded eight-entry environment matrix.
- It is not independent evaluation or full-family certification.
- It does not include forward tests, cross-adapter recovery, runtime guidance, activation, live-project work, or Git operations.
- It does not create release certification entries or authorize activation.
