<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":9,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0023","kind":"decision","legacy":{"sourceSectionSha256":"3312893ca90ead67454dceb7559badc096a92311efb81cad1c70accef4da95c8"},"outcome":"accepted","predecessors":["wr-0021"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 9 Windows failure investigation — accepted.","title":"Candidate revision 9 Windows failure investigation — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 9 Windows failure investigation — accepted

Investigated and accepted by the skill owner on 2026-09-14 against exact source commit `b39203656049ad536ca690086e746ec860d7ba46`, GitHub Actions run `34890622679`, attempt 1:

- The three Windows entries each failed `inventory-special-file`, `inventory-exclusions`, and `initialize-minimal`. The five macOS/Linux entries passed 305/305, while the Windows Python process correction succeeded across all 51 Apply cases, including both failure-boundary matrices and interrupted rollback.
- The two inventory failures occurred before adapter invocation because hosted CPython 3.14.7 did not expose `socket.AF_UNIX`. No pathname socket existed or remained live through assertions, so the shared harness capability assumption—not adapter behavior—was observed to fail.
- `initialize-minimal` completed adapter execution and matched the normalized preview, all six payload hashes, bundle inventory, and mutation snapshots. Only the normalized plan differed because root replacement left the Windows separator in the descendant absolute `recordRoot`. The accepted correction is structural normalization of environment-bound plan fields without modifying the frozen golden projection.
- The offline matrix reviewer found all eight authentic reports and all nine failed observations, and direct hashes matched the attempt-1 bindings. Its three Markdown-binding errors came from applying POSIX `Path.name` semantics to recorded Windows paths. The accepted correction resolves basenames from either separator while preserving missing, ambiguous, malformed, and hash-mismatch rejection.
- The owner authorized Option 1 as a maintainer-only correction: dependency-free native Winsock fixture creation, structural plan normalization, cross-host reviewer path resolution, focused regression tests, complete local adapter suites, local parity, repository validation, and integrity checks. Authentic Windows behavior remains unverified pending a separately authorized hosted execution.
- This authority excludes any frozen contract, release, fixture, expected-output, adapter, registry, manifest, workflow, package-version, governed-byte, or accepted-evidence change; any weakening or waiver; evidence creation or promotion; hosted dispatch or rerun; candidate advancement, certification, release, activation, forward testing, cross-adapter recovery, runtime guidance, live-project work, or Git staging, commit, or push.

### Revision 9 Windows investigation checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Candidate revision 9 Windows failure investigation | Accepted 2026-09-14; correction authorized | The owner accepted the exact investigation findings and authorized only the bounded maintainer correction described above. The correction itself remains pending review and is not accepted by this record. A hosted-execution tranche remains separately approval-gated. |

