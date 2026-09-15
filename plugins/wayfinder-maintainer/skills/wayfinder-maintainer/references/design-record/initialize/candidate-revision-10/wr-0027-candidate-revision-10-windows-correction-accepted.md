<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":10,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0027","kind":"decision","legacy":{"sourceSectionSha256":"6e03f009a7f2f85fd7fdfc44c7c804332cf23fe5fc5005f1f9e936f0552f3fe4"},"outcome":"accepted","predecessors":["wr-0025"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 10 Windows correction — accepted.","title":"Candidate revision 10 Windows correction — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 10 Windows correction — accepted

Implemented on 2026-09-14 under the separately accepted candidate-revision-10 correction authority:

- The maintainer harness now validates the adapter-emitted existing Windows `workspaceRoot` against the supplied temporary workspace with physical file identity. This accepts physically equivalent spellings such as a short-name/long-name alias, rejects missing, inaccessible, malformed, inconsistent, or divergent roots, and still requires the emitted `recordRoot` to be the exact lexical descendant implied by the portable manifest `recordRoot`.
- The Node.js Windows classifier now consults the already-supplied parent `Dirent` before `lstat`. A reparse candidate is a `symlink` only when metadata-only `readlink` succeeds; `EINVAL` is accepted as `unsupported-file` only while refreshed parent metadata still identifies the object as a reparse candidate. Missing, inaccessible, ambiguous, changed, or unexpected metadata fails closed. No socket content is read and the path is not followed or traversed.
- The candidate advances to `v1-candidate-revision-10` while preserving contract status `frozen`, release status `unactivated-frozen`, disabled activation, all 305 cases, all 96 cited normative rules, the fixture index, and the complete frozen expected-output set. Python changes only its embedded candidate identity; PowerShell bytes and both adapters' observable behavior remain unchanged.
- Deterministic correction tests passed 6/6, the canonical maintainer self-test passed 41/41 with no bytecode, the three focused cases passed 3/3 on each local adapter, and the complete local suites passed 305/305 on each adapter. Dependency-free repository validation and diff hygiene passed. These are local verification results only, not new certification evidence.
- Accepted and historical revision-8 and revision-9 evidence remains byte-for-byte preserved and cannot certify revision 10. No revision-10 evidence, hosted execution, artifact download, evidence promotion, release-certification entry, certification claim, runtime guidance, activation, forward testing, cross-adapter recovery, live-project change, staging, commit, or push is part of this checkpoint.
- Local verification remains verification only. Authentic post-correction Windows execution is absent, and local Node.js 22.22.3 is not the pinned hosted Node.js 24.21.0 target.
- The owner explicitly accepted the exact correction on 2026-09-14 and separately authorized the full eight-entry hosted rerun as the next bounded new-session task. Acceptance makes no Windows, matrix, adapter-family, or full-family certification claim and did not begin publication, hosted execution, artifact download, evidence creation or promotion, a release-certification entry, runtime guidance, activation, forward testing, cross-adapter recovery, live-project work, staging, commit, or push.
- The authorized hosted rerun must use one exact published source commit. Because this acceptance does not itself authorize staging, commit, or push of the broader dirty worktree, the source-publication scope and target must be resolved explicitly at the start of that new-session task before any Git mutation.

### Candidate revision 10 correction checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Candidate revision 10 Windows correction | Accepted 2026-09-14; full eight-entry hosted rerun authorized | The owner accepted the exact correction packet and authorized a separate hosted-execution tranche for all eight entries. Acceptance makes no Windows, matrix, adapter-family, or full-family certification claim and does not itself publish source, dispatch Actions, download or promote artifacts, create evidence, add a release-certification entry, activate Wayfinder, or begin any later tranche. |

