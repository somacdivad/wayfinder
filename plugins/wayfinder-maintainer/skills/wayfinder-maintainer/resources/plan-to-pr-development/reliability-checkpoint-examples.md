# Reliability sample-review checkpoint

These are synthetic examples for the required checkpoint in Review and Verification Reliability. They are proposed templates, not live approval packets, platform observations, executable CLI output, accepted evidence, or permission to send comments. The repository, PRs, IDs, commits and digests below are fictitious. The new CLI does not exist yet. Acceptance of these examples permits building it within the approved plan; it does not approve the existing PRs for merging.

## 1. Whole-set versus subset approval

A packet binds the approved plan and two reviewed versions:

```json
{
  "format": "wayfinder-review-packet",
  "schemaVersion": 1,
  "id": "rr-11111111-1111-4111-8111-111111111111",
  "planId": "wp-22222222-2222-4222-8222-222222222222",
  "approvedPlanRevision": 2,
  "approvedPlanSha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "repository": "example/workflow-demo",
  "owner": "example-owner",
  "members": [
    {
      "number": 4,
      "url": "https://github.com/example/workflow-demo/pull/4",
      "headCommit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "baseCommit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "mergeBaseCommit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
      "reviewedDiffSha256": "4444444444444444444444444444444444444444444444444444444444444444",
      "dependencies": []
    },
    {
      "number": 5,
      "url": "https://github.com/example/workflow-demo/pull/5",
      "headCommit": "cccccccccccccccccccccccccccccccccccccccc",
      "baseCommit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "mergeBaseCommit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
      "reviewedDiffSha256": "5555555555555555555555555555555555555555555555555555555555555555",
      "dependencies": [
        4
      ]
    }
  ],
  "verificationIds": [
    "vr-33333333-3333-4333-8333-333333333333"
  ],
  "limitations": [
    "PowerShell unavailable: explicit plan exception; not passed"
  ],
  "exclusions": [
    "No merge approval without current checks/protections",
    "No publication or activation"
  ],
  "requestedAuthority": "Approve only these identified reviewed PR versions for eligible merging under the plan and repository protections",
  "observedAt": "2026-09-15T15:00:00Z"
}
```
Generated consolidated question:

> Do you approve request rr-11111111-1111-4111-8111-111111111111 for PRs #4 and #5 in example/workflow-demo at the identified commits and reviewed diffs, permitting eligible merging subject to the plan and repository checks/protections, with publication and activation excluded?

The visible summary renders each member's URL, full commit, base/merge-base and diff identity from the packet. Each PR receives only a factual notice pointing to this request, with no second approval question.

| Owner response | Interpretation |
| --- | --- |
| “Yes” with this single unresolved request | Approve the identified versions of #4 and #5. |
| “Approve #4 only” | Approve #4 only; #5 remains pending. |
| “I’m done reviewing” | Inspect the requested feedback; no merge approval. |
| “Yes” while two requests are ambiguously pending | Ask which request; approve neither by inference. |

The decision is persisted as an explicit quotation linked to this request and named members in the design record. Validation alone creates no owner decision. Final eligible merging still requires refreshed platform checks/protections and version identities.

## 2. Revision and supersession

Suppose the owner approved #4 only, then #5 gains a commit. Create a replacement packet with a new request ID and #5's new head and diff; preserve the original packet. Append explicit supersession:

```json
{
  "format": "wayfinder-review-supersession",
  "schemaVersion": 1,
  "id": "rs-44444444-4444-4444-8444-444444444444",
  "requestId": "rr-11111111-1111-4111-8111-111111111111",
  "replacementRequestId": "rr-55555555-5555-4555-8555-555555555555",
  "reason": "PR #5 head and reviewed diff changed",
  "at": "2026-09-15T16:00:00Z"
}
```
```text
PASS review #4: unchanged reviewed version; original explicit subset decision retained
FAIL review #5: new head/diff has no owner approval
summary members=2 approved=1 pending=1 mergeReady=false
```

The replacement lists the full current set and retains #4's original decision provenance. Its one question requests approval only of still-pending identified members; a plain affirmative never enlarges that named request. A changed base or merge-base triggers diff comparison: unchanged head with changed reviewed diff also requires renewed approval. If only base identity moves and the reviewed diff stays identical, disclose that movement and recheck eligibility rather than claiming new reviewed semantics. No automatic branch update or merge happens through this local CLI.

## 3. Uncertain submission and reconciliation

Before sending, append prepared intent and an attempted event when submission occurs. If the submission times out, append:

```json
{
  "format": "wayfinder-delivery-event",
  "schemaVersion": 1,
  "id": "de-66666666-6666-4666-8666-666666666666",
  "requestId": "rr-11111111-1111-4111-8111-111111111111",
  "memberNumber": 4,
  "headCommit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "operationMarker": "rr-11111111-1111-4111-8111-111111111111/4/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "phase": "uncertain",
  "at": "2026-09-15T16:05:00Z",
  "reason": "Submission timed out; whether the comment exists is unknown",
  "commentId": null,
  "commentUrl": null
}
```
```text
UNAVAILABLE delivery #4: submission outcome uncertain
summary acknowledged=0 uncertain=1 nextAction=stop-until-owner-return
```

Stop delivery and do not submit remaining notices or retry in the background. When the owner returns, existing GitHub tools inspect comments by member/version/request marker. If the original comment is found, append a linked acknowledged reconciliation observation:

```json
{
  "format": "wayfinder-delivery-event",
  "schemaVersion": 1,
  "id": "de-77777777-7777-4777-8777-777777777777",
  "requestId": "rr-11111111-1111-4111-8111-111111111111",
  "memberNumber": 4,
  "headCommit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "operationMarker": "rr-11111111-1111-4111-8111-111111111111/4/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "phase": "acknowledged",
  "at": "2026-09-15T17:00:00Z",
  "reconcilesEventId": "de-66666666-6666-4666-8666-666666666666",
  "reason": "Owner-return inspection found the original comment",
  "commentId": 123456789,
  "commentUrl": "https://github.com/example/workflow-demo/pull/4#issuecomment-123456789"
}
```
```text
PASS delivery #4: original comment found; receipt appended; no resend
summary acknowledged=1 uncertain=0 duplicateSubmissions=0
```

Keep the earlier uncertain event as history. If discovery is incomplete or ambiguous, remain uncertain. If complete inspection establishes no matching comment, consider a resend only within current owner-return authority and append a new attempt; do not infer permission merely from absence. Markers aid discovery without promising server-side idempotency or exactly-once effects.

On ordinary success, save the returned comment ID/URL immediately and stop after the terminal delivery operation. If receipt saving fails, preserve the acknowledgment in the session handoff and stop; never claim a saved receipt or blindly resend. Terminal receipt saving itself performs no Git/network mutation.

## 4. Accurate results and coverage exceptions

A suite with one successful test, one skipped test, and one expected failure can satisfy the framework's success policy while lacking required coverage. Count successful callbacks directly. Case counts and subtest/fixture events have distinct units.

```json
{
  "format": "wayfinder-verification-report",
  "schemaVersion": 1,
  "id": "vr-33333333-3333-4333-8333-333333333333",
  "planId": "wp-22222222-2222-4222-8222-222222222222",
  "provenance": {
    "command": "maintain.py self-test --format json",
    "selection": "all maintainer-owned test modules",
    "testedCommit": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "worktreeSha256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "runtime": "CPython 3.12.14",
    "startedAt": "2026-09-15T15:00:00Z",
    "finishedAt": "2026-09-15T15:00:01Z"
  },
  "results": {
    "unit": "test-case",
    "testsRun": 3,
    "passed": 1,
    "skipped": 1,
    "expectedFailures": 1,
    "unexpectedSuccesses": 0,
    "caseFailures": 0,
    "caseErrors": 0,
    "subtestEvents": [],
    "fixtureErrors": [],
    "interrupted": false,
    "skipReasons": [
      "Required recovery test unavailable in this fixture"
    ]
  },
  "suiteSuccessful": true,
  "coverage": [
    {
      "checkId": "delivery-recovery",
      "outcome": "skipped",
      "required": true,
      "exception": null
    },
    {
      "checkId": "powershell-adapter-probe",
      "outcome": "unavailable",
      "required": true,
      "exception": {
        "locator": "approved-plan:2",
        "reason": "Explicit unchanged environment limitation accepted by owner; not passed"
      }
    }
  ],
  "requiredCoverageComplete": false,
  "readyForReview": false,
  "bytecodeArtifacts": []
}
```
```text
PASS self-test: framework success policy satisfied
PASS tests: 1 successful test case
UNAVAILABLE tests: 1 skipped test case; required recovery coverage missing
PASS expected-failure policy: 1 expected failure; no claim that its behavior passed
UNAVAILABLE powershell-adapter-probe: explicit owner-accepted plan exception; not passed
FAIL review-readiness: required delivery-recovery coverage missing
summary testsRun=3 passed=1 skipped=1 expectedFailures=1 unexpectedSuccesses=0 caseFailures=0 caseErrors=0 suiteSuccessful=true requiredCoverageComplete=false readyForReview=false
```

The PowerShell exception alone does not block this maintainer-only plan. The unrelated missing required recovery test does block readiness. Once that test genuinely passes and all other required local checks pass, readyForReview may become true while the accepted PowerShell limitation remains visible. Interrupted or incomplete accounting cannot become complete required coverage. Pending, absent, skipped or neutral GitHub checks remain separately disclosed platform states; local readiness is not merge eligibility or certification.

### Shared JSON response shape

The command result uses maintainer_output.py's existing version-1 envelope. Additional details live inside data. Optional counts, byte lengths and source hash may be null where they do not apply; real output populates them from actual serialized sources, not this fixture. No parallel CI envelope is introduced.

```json
{
  "format": "wayfinder-maintainer-response",
  "schemaVersion": 1,
  "command": "verification render",
  "responseClass": "complete-evidence",
  "scope": {
    "kind": "development-verification",
    "id": "vr-33333333-3333-4333-8333-333333333333"
  },
  "complete": true,
  "truncated": false,
  "returnedItems": 1,
  "totalItems": 1,
  "returnedBytes": null,
  "sourceBytes": null,
  "sourceSha256": null,
  "nextCursor": null,
  "error": null,
  "data": {
    "format": "wayfinder-verification-report",
    "schemaVersion": 1,
    "id": "vr-33333333-3333-4333-8333-333333333333",
    "planId": "wp-22222222-2222-4222-8222-222222222222",
    "provenance": {
      "command": "maintain.py self-test --format json",
      "selection": "all maintainer-owned test modules",
      "testedCommit": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
      "worktreeSha256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
      "runtime": "CPython 3.12.14",
      "startedAt": "2026-09-15T15:00:00Z",
      "finishedAt": "2026-09-15T15:00:01Z"
    },
    "results": {
      "unit": "test-case",
      "testsRun": 3,
      "passed": 1,
      "skipped": 1,
      "expectedFailures": 1,
      "unexpectedSuccesses": 0,
      "caseFailures": 0,
      "caseErrors": 0,
      "subtestEvents": [],
      "fixtureErrors": [],
      "interrupted": false,
      "skipReasons": [
        "Required recovery test unavailable in this fixture"
      ]
    },
    "suiteSuccessful": true,
    "coverage": [
      {
        "checkId": "delivery-recovery",
        "outcome": "skipped",
        "required": true,
        "exception": null
      },
      {
        "checkId": "powershell-adapter-probe",
        "outcome": "unavailable",
        "required": true,
        "exception": {
          "locator": "approved-plan:2",
          "reason": "Explicit unchanged environment limitation accepted by owner; not passed"
        }
      }
    ],
    "requiredCoverageComplete": false,
    "readyForReview": false,
    "bytecodeArtifacts": []
  }
}
```
Complete output means this report was fully returned; it does not mean required coverage passed. Here error is null because reading/rendering the report succeeded; data.readyForReview is false because coverage is incomplete. A separate validate/readiness operation returns a nonzero status when required coverage is unsatisfied. Machine and human summaries derive from the same report. Bad input, stale writes or missing references use the existing envelope error/completeness conventions and fail clearly.

## Proposed command examples

```text
maintain.py review create --plan-id PLAN_ID --input packet.json --dry-run
maintain.py review read --plan-id PLAN_ID --id REQUEST_ID --format json
maintain.py review validate --plan-id PLAN_ID --id REQUEST_ID --format json
maintain.py review supersede --plan-id PLAN_ID --id REQUEST_ID --input supersession.json --expected-store-sha256 STORE_HASH
maintain.py delivery append --plan-id PLAN_ID --request-id REQUEST_ID --input receipt.json --expected-store-sha256 STORE_HASH
maintain.py delivery read --plan-id PLAN_ID --request-id REQUEST_ID --format json
maintain.py verification capture --plan-id PLAN_ID --input result.json --dry-run
maintain.py verification render --plan-id PLAN_ID --id REPORT_ID --format json
```

These illustrate the approved command boundaries. Final help documents closed schemas, immutable IDs, reference validation, byte budgets and expected-store binding. Existing GitHub tools handle authorized submission/inspection. Packet validation operates only on supplied observations; it cannot certify current platform state. Owner decisions and mutable current authority retain their existing distinct homes.
