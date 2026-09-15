<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":8,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0017","kind":"verification","legacy":{"sourceSectionSha256":"66ca0de87ececf52efb63364d5ac4703540a440b8829e40e4aadcaf98336171b"},"outcome":"accepted","predecessors":["wr-0015"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 8 hosted certification execution — accepted with failed aggregate.","title":"Candidate revision 8 hosted certification execution — accepted with failed aggregate","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 8 hosted certification execution — accepted with failed aggregate

Executed on 2026-09-14 as the separately authorized bounded hosted tranche:

- GitHub Actions workflow run `34867347594`, attempt 1, used the exact source commit `12ca21e6642b2357c78cf09aff1842b03c764e36` and all eight fixed revision-8 entries. The run did not include the pre-existing uncommitted approval-record or repository-validator edits.
- CPython 3.14.7 passed 305/305 cases on macOS and Linux and failed 10 of 305 cases on Windows. Node.js 24.21.0 passed 305/305 on macOS and Linux and failed 4 of 305 cases on Windows. PowerShell 7.6.6 passed 305/305 on Linux and failed 4 of 305 cases on Windows. No runtime, operating-system, or adapter substitution was made.
- The three Windows entries shared failures in `inventory-special-file`, `inventory-exclusions`, `render-output-symlink-component`, and `initialize-minimal`. The CPython Windows entry additionally failed six interruption and rollback recovery cases. The accepted execution record preserves these observed failures without assigning a root cause.
- Every environment report binds to the frozen release, contract, fixture index, expected-output set, registered adapter, source commit, workflow run, and exact runtime identity. Passing reports cover both observed case-sensitive and case-insensitive filesystem behavior, and all eight reports record a successful Unicode filename round trip.
- The strict aggregate rejected the three non-passing Windows reports with `matrix.invalid-entry`, exited 2, and created no aggregate certification JSON or Markdown. Its review-only inventory has SHA-256 `f5b895acd6721657c46969354fcd529f1d0f71bebc846b49361d9ab1aa451086`; the hosted aggregate artifact has SHA-256 `9e5af7d8a7ab046e7632c96ba7acaf25f0c1015e31dea9dd889a5b06f102c327`.
- The eight entry artifacts and aggregate inventory remain GitHub Actions review evidence with 90-day retention through 2026-12-13. They were not copied into accepted durable evidence, published, added to the release certification registry, or used to claim matrix completion or full-family certification.
- This tranche changed no frozen contract, fixture, adapter, parity, or accepted historical-evidence bytes; added no runtime guidance; and did not activate Wayfinder, initialize a live project, run forward tests, or perform cross-adapter recovery.

### Hosted certification-execution approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact eight-entry hosted execution and strict aggregate result | Accepted 2026-09-14 | The skill owner selected Option A and accepted the authentic hosted execution record as five passing entries, three failing Windows entries, and an unsuccessful strict aggregate. The approval preserves the failures and artifact-review boundary and authorizes no investigation, correction, rerun, evidence publication, release certification entry, full-family claim, runtime guidance, activation, or subsequent tranche. |

