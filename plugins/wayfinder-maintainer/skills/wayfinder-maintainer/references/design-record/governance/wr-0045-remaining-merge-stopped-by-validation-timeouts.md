<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":null,"date":"2026-09-15","format":"wayfinder-design-record","id":"wr-0045","kind":"verification","legacy":null,"outcome":"recorded","predecessors":["wr-0044"],"schemaVersion":1,"sources":["record:wr-0044","https://github.com/somacdivad/wayfinder/actions/runs/34979671402","https://github.com/somacdivad/wayfinder/actions/runs/34979671565"],"summary":"Exact #4–#6 approval is preserved; two current #4/#5 validation jobs exceeded 30 minutes, so no remaining merge was submitted.","title":"Remaining merge stopped by validation timeouts","topic":"governance"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Remaining merge stopped by validation timeouts

Owner approval wr-0044 remains bound to exact replacement request rr-c5c1ed3b-f0e7-4674-8667-f1e99e122407; all three heads remain unchanged. PR #3 alone is integrated. No #4–#6 merge request has been submitted.

GitHub check-run annotations confirm that job 104416382062 (run 34979671402, PR #4) and job 104416382482 (run 34979671565, PR #5) exceeded the existing 30-minute maximum execution time and were cancelled during all-adapter conformance. This is a hosted timeout, not a reported test assertion failure or a successful coverage result. Each PR also has a separate successful validation run; PR #6 validation passed. Do not treat cancelled current jobs as passed or infer that another passing job removes the missing result.

Local persistence verification passes repository and whitespace validation and canonical self-test (112 cases: 111 passed, one missing-PowerShell skip; zero bytecode). Doctor retains only the unchanged explicitly accepted PowerShell-unavailable baseline. No new certification evidence or activation follows.

The bounded recovery proposal is rerunning only the two timed-out ordinary validation jobs on unchanged reviewed heads, then proceeding under wr-0044 only if every applicable check succeeds and identities/protections/dependencies remain satisfied. This record does not authorize that network mutation. No workflow/settings change, certification dispatch, artifact download or protection bypass is proposed. Existing exclusions and immutable history/snapshots remain unchanged. Closure delivery remains outstanding.
