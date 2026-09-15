<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":9,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0024","kind":"decision","legacy":{"sourceSectionSha256":"78d7e272dd17e567c6ca61731c1a6aaa0d56d95a53659ac58a61ea181df415b4"},"outcome":"accepted","predecessors":["wr-0023"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 9 maintainer-only Windows correction — accepted.","title":"Candidate revision 9 maintainer-only Windows correction — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 9 maintainer-only Windows correction — accepted

Implemented and accepted by the skill owner on 2026-09-14 as the exact bounded correction authorized by the preceding investigation:

- Replaced the Windows fixture's dependency on CPython `socket.AF_UNIX` with dependency-free `ctypes` interop against `Ws2_32.dll`. The harness declares every Winsock signature, uses a pointer-sized `SOCKET`, initializes Winsock 2.2, binds a null-terminated UTF-8 pathname through the SDK-compatible `SOCKADDR_UN`, verifies the pathname with non-following metadata, and retains explicit socket, Winsock, and pathname ownership through adapter invocation and assertions.
- Cleanup closes each acquired socket and successful Winsock registration exactly once, removes only an owned pathname, handles partial initialization and assertion failures, and reports stable fail-closed diagnostics. POSIX continues to use the existing FIFO fixture. No fallback object, skipped case, conditional pass, or adapter-classification change was introduced.
- `initialize-minimal` now parses and normalizes the plan structurally. Only the temporary physical `workspace.workspaceRoot`, its manifest-bound descendant `workspace.recordRoot`, and the pre-existing contract test marker are changed before canonical serialization. Non-path strings remain byte-semantically unchanged, and malformed, unsafe, outside, or inconsistent record roots fail closed. The frozen golden remains unchanged and retains normalized plan SHA-256 `4663f40f76f135f381feb6a216bf44482d521dfba4c826d937736585fbb3595f`.
- The offline matrix reviewer derives report basenames from either path separator, searches only inside the supplied artifact directory, requires one non-symbolic unambiguous match, binds the recorded JSON basename to the report under review, and still verifies actual JSON and Markdown SHA-256 digests. Empty, malformed, missing, ambiguous, and mismatched paths remain rejected.
- Focused maintainer logic verification passed 36/36 with no repository bytecode. The three focused conformance cases passed 3/3 for Python, Node.js, and PowerShell; all three complete local suites passed 305/305; and 900 normalized observations agreed at `4463448355c7662a09bb2112052179df0e95216e5bd1092968ee4ddc95b6d233`.
- Repository validation and `git diff --check` passed. The canonical doctor passed 33/33 before and after correction. The authentic review-only attempt-1 artifact directory validated all eight reports and execution statuses with zero binding issues while preserving the genuine three failed Windows cases per adapter and the failed strict aggregate.
- Contract `3c79c6e1d2eae7c6016d789c9ade75125a2ec1dcc43f458541f9d7c63654bdd9`, release `1826fa1c1323561001565fe4bd635c0432306ced078320f1eecdad81ff268ffb`, fixture index `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`, expected-output set `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`, all three registered adapters, and every accepted evidence file remain unchanged.
- The macOS tests verify maintainer ownership and normalization logic but do not verify actual Windows AF_UNIX reparse metadata, adapter classification of the live socket, Node.js metadata-only `readlink` behavior, hosted pathname encoding and length behavior, or cleanup on the hosted Windows image. The old hosted execution remains historical and cannot certify corrected source.
- No hosted run, evidence creation or promotion, candidate revision, certification claim, release entry, activation, forward test, cross-adapter recovery, runtime guidance, live-project work, staging, commit, or push occurred during the correction or this acceptance record.
- In the same owner response that accepted the correction, the owner separately authorized a full eight-entry hosted rerun. Per the new-session boundary, that hosted execution was not begun here. It must use one exact published source commit; the publication scope must first be resolved against the broader pre-existing dirty worktree.
- At the start of the separately authorized hosted tranche, the owner resolved that publication boundary as all modified and untracked paths then present in the `candidate-revision-9-certification` worktree. This authorizes one exact commit and push containing that complete set for the eight-entry rerun; it does not authorize evidence promotion or any excluded later tranche.

### Revision 9 maintainer-only Windows correction checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Candidate revision 9 maintainer-only Windows correction | Accepted 2026-09-14; full eight-entry hosted rerun authorized | The owner accepted the exact correction packet and authorized a separate hosted-execution tranche for all eight entries. Acceptance makes no Windows or full-family certification claim and does not itself publish source, dispatch Actions, promote evidence, add a release-certification entry, activate Wayfinder, or begin a later tranche. |

