<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":8,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0015","kind":"verification","legacy":{"sourceSectionSha256":"75f1b21832d86c213de460f8e1d3e5b61ebd98cc67946c945896380e7d2f1bb3"},"outcome":"accepted","predecessors":["wr-0014"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 8 bounded certification matrix — accepted.","title":"Candidate revision 8 bounded certification matrix — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 8 bounded certification matrix — accepted

Implemented on 2026-09-14 as maintainer-only orchestration and partial environment evidence for the exact frozen matrix:

- Added `maintain.py matrix-entry` to verify the selected required target, accepted candidate/package/adapter/parity bindings, exact native runtime identity and executable digest, OS family and version, architecture, effective locale and timezone, filesystem encoding, Unicode filename round trip, and actual filesystem case behavior before running the exact registered adapter. A matching environment runs all 305 cases and exclusively creates a timestamped JSON/Markdown evidence pair; runtime, version, or OS substitutions are rejected before the suite begins.
- Added `maintain.py matrix-aggregate` to accept explicit immutable environment-report paths, revalidate every result-set and package binding, require one passing 305/305 report for each of the eight exact entries, require both observed filesystem behaviors, and exclusively create the maintainer-owned aggregate only after all conditions hold. An incomplete selection returns `matrix.incomplete` and writes no aggregate.
- Extended the doctor to pin the accepted candidate, contract, release, fixture-index, expected-output, adapter, and local parity-evidence digests. The accepted parity JSON and Markdown remain byte-for-byte unchanged.
- CPython 3.14.7 on macOS 26.6.2 arm64 passed 305/305 cases, including 213/213 negative and mutation cases and all three summarized interruption-boundary cases. The suite ran with explicit `C.UTF-8` locale and `UTC` timezone controls. The temporary filesystem reported UTF-8 with `surrogateescape`, passed the Unicode filename round trip, and was observed as case-insensitive because exclusive creation of a case-variant name was refused as an existing file.
- Immutable evidence: [macOS CPython 3.14.7 JSON](../../../../certification/v1/matrix-revision-8-python-reference-v1-macos-20260914T125208Z.json) (`6b43c2f0b41e83d76218e363651d6353ab62561426e4c7abf997cb561aa3fd78`) and [Markdown](../../../../certification/v1/matrix-revision-8-python-reference-v1-macos-20260914T125208Z.md) (`8a81084ab64a18bac8d59694bc81233035cc0f02434a36d8106dfc0f2cc1c11c`). The result-set digest is `3b70db99a1cc2caa40a3e472dbf742b2b10cf2b467a191c124ff9e35685d8757`.
- CPython 3.14.7 on Linux and Windows, Node.js 24.21.0 on macOS/Linux/Windows, and PowerShell 7.6.6 on Windows/Linux remain unavailable. The present host is macOS, and its available Node.js is 22.22.3 rather than the pinned 24.21.0. Environment-only maintainer checks rejected all seven exact targets before conformance execution and wrote no evidence for them.
- The aggregate command was exercised with the one passing report and correctly refused publication because seven entries and case-sensitive filesystem coverage are missing. No aggregate matrix report or release certification entry exists.

This tranche is partial passing environment evidence, not a completed matrix, independent validation, cross-adapter recovery, forward testing, or full-family certification. It does not authorize runtime guidance or activation.

### Certification-matrix approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded certification-matrix orchestration and available evidence | Accepted 2026-09-14 | The skill owner selected Option A and accepted the bounded certification-matrix tranche as implemented, preserving one passing environment entry and seven explicitly unavailable entries without a completion claim. No follow-up exception was attached. Hosted matrix execution, evidence publication, forward tests, cross-adapter recovery, full-family certification, runtime guidance, activation, and live-project work remain separately authorized tranches; this approval begins none of them. |

