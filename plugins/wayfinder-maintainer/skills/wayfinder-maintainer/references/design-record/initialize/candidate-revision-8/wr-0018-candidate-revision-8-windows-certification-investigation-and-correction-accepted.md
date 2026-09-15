<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":8,"date":"2026-09-14","format":"wayfinder-design-record","id":"wr-0018","kind":"decision","legacy":{"sourceSectionSha256":"ae7dfd454818bc7ae2d0319ccd5b20051261a253d2d6a801df58cae7613cdac3"},"outcome":"accepted","predecessors":["wr-0017"],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Candidate revision 8 Windows certification investigation and correction — accepted.","title":"Candidate revision 8 Windows certification investigation and correction — accepted","topic":"initialize"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Candidate revision 8 Windows certification investigation and correction — accepted

Investigated and accepted on 2026-09-14 as a bounded correction tranche against source commit `12ca21e6642b2357c78cf09aff1842b03c764e36` and authentic GitHub Actions run `34867347594`, attempt 1:

- Retrieved and inspected all eight authentic entry artifacts, their execution records, the aggregate inventory, and the complete hosted logs as temporary review evidence. Nothing was copied into accepted durable evidence or added to the release certification registry.
- Established separate causes for every failure group. `inventory-special-file` and `inventory-exclusions` depend on a FIFO fixture created through Unix-only `os.mkfifo`; Windows therefore lacks the requested filesystem node. `render-output-symlink-component` was a harness snapshot-comparison defect caused by platform-specific symbolic-link target spelling. `initialize-minimal` was a harness normalization defect because canonical JSON escapes Windows backslashes. The six CPython recovery failures share a frozen Python-adapter defect: `_process_alive` uses `os.kill(pid, 0)`, which is not a non-mutating Windows process-existence probe and surfaced stale PIDs as `internal.unexpected` before recovery boundaries were reached.
- Corrected only the maintainer-owned harness where evidence supported it: special-file unavailability now fails explicitly rather than masquerading as a missing selection, rejected render output is compared with its actual pre-invocation snapshot, and canonical JSON workspace paths are normalized using their escaped spelling. The repository validator now recognizes the maintainer runner as a mutable post-migration path.
- Preserved all frozen contract, fixture, registered-adapter, parity, and accepted historical-evidence bytes. The exact suite remains 305 cases with all 96 normative rules cited. Initialization remains disabled.
- Focused local checks passed for the four shared cases on Python, Node.js, and PowerShell, and all six listed Python recovery cases passed on macOS. A synthetic Windows JSON-escaping assertion passed. These local checks do not substitute for Windows execution or the pinned Node.js 24.21.0 matrix target.
- Repository validation passed. The final maintainer doctor passed 29/29 checks under CPython 3.14.7 using the existing portable PowerShell 7.6.6 runtime. Optional PyYAML remained unavailable and the accepted dependency-free checks were used.
- Two blockers remain intentionally unresolved: Windows cannot construct the harness's FIFO fixture through the selected standard-library mechanism, and correcting Python recovery requires changing the frozen registered adapter. An exact rerun from the accepted worktree is therefore expected to correct the render and golden-normalization failures but still fail the two inventory cases on all Windows entries and the six recovery cases on CPython Windows.
- No hosted rerun, evidence publication, release-certification entry, forward test, cross-adapter recovery, full-family claim, runtime guidance, activation, live-project initialization, commit, or push was performed.

### Windows investigation/correction approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded Windows certification investigation and maintainer-harness correction | Accepted 2026-09-14 | The skill owner approved the investigation findings and smallest maintainer-only corrections with the disclosed local-test boundary and two remaining Windows blockers. This acceptance records the result only. It does not authorize reopening frozen adapter or contract bytes, committing or pushing the worktree, dispatching the exact hosted rerun, publishing evidence, adding certification entries, claiming full-family certification, adding runtime guidance, or activating Wayfinder. |

