<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":9,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0021","kind":"verification","legacy":{"sourceSectionSha256":"44a20dbb8435b203046b6b98897e8f97b4a47a2ecb5396031738069add0682a0"},"outcome":"accepted","predecessors":["wr-0020"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 9 hosted certification execution — accepted with failed aggregate.","title":"Candidate revision 9 hosted certification execution — accepted with failed aggregate","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 9 hosted certification execution — accepted with failed aggregate

Authorized by the skill owner on 2026-09-14 as one bounded hosted-execution tranche:

- Publish the complete accepted revision-9 worktree to the dedicated `candidate-revision-9-certification` branch without changing `main`.
- Dispatch the exact eight-entry revision-9 matrix from that branch using CPython 3.14.7, Node.js 24.21.0, and PowerShell 7.6.6 on the accepted operating-system targets.
- Preserve every resulting Actions artifact as review-only, run the strict aggregate, and report the authentic result without promotion or publication.
- Do not add a release-certification entry, claim full-family certification from incomplete or failing results, add runtime guidance, activate Wayfinder, initialize a live project, perform forward testing or cross-adapter recovery, or begin any later tranche.

Executed on 2026-09-14 within that authority:

- Published the complete accepted revision-9 worktree only to `candidate-revision-9-certification` at commit `b39203656049ad536ca690086e746ec860d7ba46`; `main` was not changed. GitHub Actions run `34890622679`, attempt 1, executed from that exact branch and commit.
- Five fixed entries passed 305/305: CPython 3.14.7 on macOS and Linux, Node.js 24.21.0 on macOS and Linux, and PowerShell 7.6.6 on Linux. All 213 required negative and mutation cases and the three interruption-boundary cases passed in each reported entry.
- All three Windows entries completed the 305-case suite and failed three cases each: CPython 3.14.7, Node.js 24.21.0, and PowerShell 7.6.6 each passed 302/305. Their result-set hashes are respectively `895a6ba36ae707dc2da20dec246c466bbfe47e686f2ebc0748587010a01fa5fb`, `ff624bf9193be656809dd7e740af091ed8c96cc8af44d991896fad39e619fd04`, and `cdf25748fa2f1db5b521fa6bb019cc7b8ecb90a3f69c2221885a43ca6465f320`. The workflow log exposes counts and report bindings but not the individual failed case identifiers; the reports were not downloaded under the tranche's explicit exclusion, so no case identity is inferred here.
- The strict aggregate rejected the three non-passing Windows reports with `matrix.invalid-entry`, exited 2, and created no aggregate certification JSON or Markdown. The review-only incomplete-inventory artifact is 697 bytes with SHA-256 `4e25093e7a7aad827cf81e5d85c07031183642caa86c263298259d66d642b9b1`.
- The eight review-only entry artifacts have SHA-256 digests: Node Linux `d1652b1a4dbdbc683eac6adc1e06c77f5c79f70e88ebb62139e5319f8a430e43`; Node macOS `5dca75bb8b1bcf92d8d50557bf8621fe6be4d0633e528a308147cf0261edd4ea`; Node Windows `ef07e9e2de54c76b1aff0efd0e7ccbad1065629240043cb6a8932db2f8188d2d`; PowerShell Linux `b93a28b86d09d0365a0f0e287b19090b2f1877cf1a4de59ac43940e32f1f30b0`; PowerShell Windows `cdb2c56d2c339c3a4b5a3e26242e15c805a351f664053393afcb36a0b2819c47`; Python Linux `1441b5e582c1fbe0e5f8039abf038ff3d0ceb6c2f45af26ea4174445b3108304`; Python macOS `64c9196a7f9ef6a11068b55c50b0928467ef8ca0da16aca24cebbe80ac0e70d5`; Python Windows `74a839b603a839b6a105cceb96884d2ac26aae26321745affb2b963464450c9b`. GitHub reports expiry on 2026-12-13.
- No hosted artifact was downloaded, promoted, copied into durable accepted evidence, published, or added to the release certification registry. No investigation, correction, rerun, full-family claim, runtime guidance, activation, live-project initialization, forward test, or cross-adapter recovery occurred. The owner explicitly accepted the authentic execution record on 2026-09-14; acceptance preserves the failures and review-only artifact boundary and authorizes no later tranche.

### Revision 9 hosted-execution checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact eight-entry revision-9 hosted execution | Accepted 2026-09-14 | The skill owner accepted run `34890622679`, attempt 1, exactly as five passing entries, three failing Windows entries, and no strict aggregate. Acceptance preserves the failures and review-only artifact boundary and authorizes no artifact download or promotion, investigation, correction, rerun, evidence publication, release-certification entry, full-family claim, runtime guidance, activation, or later tranche. |

