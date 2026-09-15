<!-- WAYFINDER-PLAN:BEGIN -->
```json
{"approval":{"locator":"conversation:current/plan-to-pr-development/implementation-authorization","quotation":"Implement the proposed plan."},"approvalHistory":{"2":"d07cb0c542c123499877b3b1497129d87de00956a17fc1fd9e43593d5f7296e3"},"approvedRevision":2,"approvedSha256":"d07cb0c542c123499877b3b1497129d87de00956a17fc1fd9e43593d5f7296e3","format":"wayfinder-plan","id":"wp-47a553ae-2a54-4dbe-a2dc-74c817521a08","records":["wr-0026","wr-0034","wr-0035","wr-0036","wr-0041","wr-0042","wr-0043","wr-0044","wr-0045","wr-0046","wr-0047"],"revision":8,"schemaVersion":1,"slug":"plan-to-pr-development","status":"awaiting-review","subject":"development","summary":"Research-backed interviews, durable approved plans, plan CLI, continuous implementation and owner-reviewed native PR stacks.","title":"Plan-to-PR Development","updated":"2026-09-15"}
```
<!-- WAYFINDER-PLAN:END -->

# Plan-to-PR Development

## Summary

Introduce a research-backed development workflow in Wayfinder-maintainer for changes to either plugin. Every change starts with an interview and saved plan. Explicit plan approval authorizes continuous implementation, verification, and PR delivery within its boundaries.

This project includes the workflow resources, plan storage and CLI, governance integration, and tests. It also publishes the already accepted hierarchical record-store implementation in a separate prerequisite PR.

All PRs target `candidate-revision-9-certification`, directly or through dependent stack layers. Integration into `main`, Initialize publication corrections, certification expansion, releases, activation, and live-project changes remain separate.

## Planning workflow and resources

Create progressively disclosed resources under the maintainer skill’s `resources/plan-to-pr-development/`. Include an entrypoint and focused guides for planning interviews, research synthesis, plan management, PR decomposition and stacks, implementation and checkpoints, and review and merging. Preserve existing research; save new research briefs in this workflow’s `research/` folder.

Research briefs must record questions, original sources, findings, limitations, alternatives, and resulting recommendations. Distinguish empirical findings, practitioner guidance, and design synthesis. Cover:

- Requirements elicitation and neutral interviewing: [systematic review](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/iet-sen.2017.0144) and [GOV.UK interview guidance](https://www.gov.uk/service-manual/user-research/using-in-depth-interviews).
- Acceptance and traceability: [GOV.UK acceptance criteria](https://www.gov.uk/service-manual/agile-delivery/writing-user-stories) and [NASA requirements management](https://www.nasa.gov/reference/6-2-requirements-management/).
- Reviewable batches and integration: [Google small-change guidance](https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md), [DORA](https://dora.dev/capabilities/working-in-small-batches/), and [Microsoft’s review study](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/).
- Stack mechanics and agent coordination: official GitHub stack documentation, [agent scaling research](https://arxiv.org/abs/2512.08296), and Anthropic’s published engineering experience.

The planning subworkflow must:

1. Inspect current state, relevant implementation, affected history, and existing evidence.
2. Establish the problem, audience, success criteria, scope, and authority.
3. Interview one material question at a time, choosing the unresolved question most likely to change the plan. Use concrete examples, neutral probes, and periodic understanding checks.
4. Present research-backed recommendations and meaningful alternatives for consequential decisions.
5. Resolve implementation boundaries, verification, PR dependencies, and checkpoints.
6. Save and present the complete plan for explicit approval.

Scale depth with uncertainty and consequence. Every change still receives a plan. Finish when consequential decisions are resolved, success criteria are observable, implementation dependencies are clear, and remaining questions are explicitly deferred.

The mandatory template contains problem and outcome; scope and authority; decisions and rationale; implementation and PR sequence; acceptance and verification; and risks, assumptions, and unresolved questions. Add interfaces, migrations, compatibility, rollout, experiments, or delegation details when relevant.

## Plan storage, CLI, and authority

Store plugin-agnostic plans under `docs/plans/<subject>/<plan-id>-<slug>/`. Use stable UUID-based `wp-` identifiers, independent of subject and title.

Each folder contains a living `plan.md` and immutable approved snapshots under `approvals/`. Co-locate versioned metadata with the Markdown using a visible JSON block and standard-library parsing. Metadata covers identity, subject, title, summary, revision, lifecycle, dates, and links to governing records. The document includes execution progress and PR links.

Add these interfaces to `maintain.py`:

- `plan list [--subject SUBJECT] [--status STATUS]`
- `plan read --id ID [--revision N | --history]`
- `plan create --input FILE [--dry-run]`
- `plan update --id ID --input FILE --expected-sha256 HASH [--dry-run]`

Use explicit JSON inputs containing metadata and Markdown. Document the closed input format and examples alongside the template. Reuse existing formats, byte budgets, completeness classes, hashes, and digest-bound continuation conventions.

Creates refuse replacement. Updates verify the expected current digest, increment the revision, validate staged content, and replace the current document safely. Approval updates require an explicit owner quotation and source locator and preserve the exact approved document and digest. The CLI records supplied authority; it never authenticates or infers approval.

Routine progress updates preserve the existing approved scope. Material revisions become changes-requested and block dependent implementation until approved. Scripts cannot determine semantic materiality; the agent must classify and explain it.

Keep authority divided:

- The plan owns task scope, intended PR sequence, and progress.
- The design record retains accepted decisions and closures.
- `current-state.md` remains authoritative for current candidate identity, evidence, activation, and authorization.

Link these sources rather than duplicate substantive content. CLI writes do not silently update design history or current state. Required acceptance and routing updates are explicit workflow steps.

Expose plan commands through maintainer startup routing, workflow guidance, CLI help, `describe/context`, repository documentation, and applicable handoff guidance. Installed maintainer packages require an explicitly resolved source repository for plan writes; they must not create plans inside plugin installations.

## PR delivery and implementation rules

Deliver this project as four dependent PRs:

1. **Prerequisite:** publish the accepted hierarchical record-store changes unchanged, preserving their original provenance.
2. **Planning foundations:** research briefs, synthesized planning guidance, template, and this project’s saved plan.
3. **Plan tooling:** plan storage operations, bounded discovery and reads, approval snapshots, integrity validation, and focused regressions.
4. **Workflow integration:** implementation, review, and merge guidance; governance and context routing; updated handoff behavior and integration checks.

Include tests and necessary documentation with each implemented behavior. Freeze and verify the prerequisite file inventory before committing; do not mix newly discovered changes into it.

Document these defaults for future work:

- One coherent behavior or concern per PR. Split at independently explainable changes, verification strategies, or rollback boundaries.
- Independent PRs target the task’s base branch. Genuine dependencies form stacks.
- Difficult summaries, interacting concepts, prolonged implementation, or repeated lower-layer rework trigger decomposition review. No universal line-count limit applies.
- Each PR must leave a coherent, verified repository. Identify merge groups during planning when incremental integration would be unsafe.
- Delegate bounded research, review, or implementation with clear inputs, outputs, and file ownership when benefits exceed coordination costs. The lead owns integration and verification; coupled decisions remain sequential.
- Verify each PR and cumulative integration. Broaden checks when shared surfaces change; repeat successful checks only after relevant changes or new concerns.

Plan approval covers task branches, commits, pushes, PR creation and updates, applicable CI runs, review requests, and selective delegation. Use GitHub native stacks when available. If unavailable, pause to propose a fallback; do not install tooling or substitute an approach silently. Preserve repository protections and stop when stack maintenance requires otherwise excluded actions.

Replace the unconditional new-session stopping rule for approved development plans with continuous execution. Preserve approval interpretation safeguards, decision history, and separately governed action boundaries. Mandatory pauses occur for material scope or design changes, insufficient authority, or checkpoints named in the plan. Recommend early examples or experiments when uncertainty could cause substantial rework.

After completing all PRs, request the owner’s review, provide PR order and verification results, and **stop**. Do not poll, schedule monitoring, enable auto-merge, or perform further work until the owner returns.

After the owner reports review completion, inspect feedback. Explicit GitHub approval or explicit approval here, bound to identified PRs and reviewed versions, authorizes merging. Merge eligible approved PRs incrementally from the bottom up, honoring merge groups, checks, protections, and required renewed reviews. Record integrated outcomes and closure through the established linked-record workflow without creating another acceptance loop.

## Verification and acceptance

Test meaningful scenarios covering:

- Plan creation, discovery, filtering, updates, and exact approved-snapshot retrieval.
- Concurrent-update rejection, immutable approvals, interrupted writes, unsafe paths, duplicate identities, malformed input, and UTF-8/LF preservation.
- Bounded pagination and chunk reconstruction, stale cursors, and complete-source digest verification.
- Routine progress versus pending material revisions; explicit authority provenance without inferred approval.
- Continuous authorized implementation, required pauses, review-handoff stopping, explicit resumption, and merge eligibility.
- Independent PRs, dependent stacks, merge groups, missing native-stack support, and blocked repository protections.
- Discoverable routing and separately installable plugins.

Run canonical maintainer self-tests, repository validation, proportional conformance checks, whitespace checks, and pre/post full doctors. Disclose the existing missing-PowerShell baseline; do not install a runtime or report that check as passed.

Acceptance requires a discoverable workflow, usable plan CLI, preserved approved snapshots and history, documented heuristics, reviewed PR delivery, and unchanged frozen candidate and evidence. Research and plan files will be persisted during implementation; this planning session changes no repository files.

## Execution progress — 2026-09-15

The approved scope and decisions above remain unchanged. Research resources, plan CLI, and workflow integration are implemented. Exact approved revision 2 remains preserved at its original SHA-256 d07cb0c542c123499877b3b1497129d87de00956a17fc1fd9e43593d5f7296e3. This progress does not imply implementation acceptance or integration.

Native GitHub stack 7 delivers:

1. [PR #3 — exact accepted record-store prerequisite](https://github.com/somacdivad/wayfinder/pull/3), head codex/plan-to-pr-01-record-store, base candidate-revision-9-certification.
2. [PR #4 — researched planning foundations](https://github.com/somacdivad/wayfinder/pull/4), head codex/plan-to-pr-02-planning, base PR #3's head.
3. [PR #5 — bounded plan CLI and approval integrity](https://github.com/somacdivad/wayfinder/pull/5), head codex/plan-to-pr-03-plan-cli, base PR #4's head.
4. [PR #6 — workflow/context/handoff integration](https://github.com/somacdivad/wayfinder/pull/6), head codex/plan-to-pr-04-workflow, base PR #5's head.

All phase resources were authored together in the planning layer to keep linked resources coherent. Executable tooling and active governance remain their own upper layers. No scope, acceptance criteria, authority, or dependency changes were made. No merge group is required.

Verification and original authority are preserved in wr-0035 and wr-0036. All 53 prerequisite commit paths/digests match the accepted captured inventory. Isolated exact planning/CLI layers passed repository validation and canonical self-tests (77 and 91 tests). Cumulative implementation passed repository validation, 94 canonical tests with one unavailable PowerShell executable check skipped and zero bytecode, two focused Python conformance cases, whitespace checks, and independent forward scenarios. Full doctor passes 35/36 checks; only the recorded missing pwsh runtime fails, as at baseline. Local Python 3.12.14 and Node 22.22.3 do not establish hosted pinned runtime certification. Applicable validate CI was observed IN_PROGRESS on all PRs; no hosted pass is asserted.

Owner-review requests are the final delivery operation. At that handoff, stop and do nothing until the owner returns: no polling, active waits, scheduled monitoring, auto-merge, or further implementation. Implementation acceptance, approved eligible merging, integrated outcome recording, and closure remain pending. Review completion alone does not authorize merging. Final head/check identities are supplied in the PR review packet; current-state alone owns current authorization/candidate/evidence/activation/publication facts. All approved exclusions remain in force.

## Owner approval and partial integration

The owner explicitly approved request rr-bd2c66d7-af9b-4cb6-9fa4-183fab7dd315 with “yes, I approve”, recorded in wr-0041. PR #3 is verified merged into candidate-revision-9-certification as b01e8e0b2984988092b07c2da56a4cb8cdf38dd4 using the expected-head asynchronous native-stack interface. GitHub automatically restacked #4/#5 heads and changed #6 reviewed diff; all three file trees are unchanged. Further merges stopped at the identity check before submitting #4. PRs #4–#6 remain open and need renewed exact-version approval through request rr-c5c1ed3b-f0e7-4674-8667-f1e99e122407. See wr-0042. Completion/closure is not claimed. Preserve snapshots and exclusions; keep outcome edits local without changing reviewed heads. Finish persistence before the renewed chat request and stop until owner return.

The GitHub-restacked #6 ancestry conflict was repaired as 241c309e18399b37bab8533cefa919f78eca3e9e by joining the identical already-incorporated #5 file tree. Every reviewed file byte remains unchanged, and the remaining per-layer diff hashes match the earlier reviewed content. Exact isolated regression counts are #4 76 passed/one skipped, #5 108 passed/one skipped, #6 111 passed/one skipped. See wr-0043. The changed heads require renewed approval through rr-c5c1ed3b-f0e7-4674-8667-f1e99e122407 before any #4–#6 merge. Outcome/routing edits remain local; the ancestry repair contains none of these persistence edits. A remaining-prefix asynchronous operation through #6 can merge all eligible approved remaining layers bottom-up without leaving open upper layers to be restacked after each separate request; verify individual outcomes and do not claim atomicity.

### Replacement reviewed-version approval

The owner approved replacement request rr-c5c1ed3b-f0e7-4674-8667-f1e99e122407 with “yes”, persisted in wr-0044. This accepts exact current #4–#6 versions for eligible remaining-prefix merging into candidate-revision-9-certification, subject to current checks, protections and dependencies. PR #3 remains verified merged. No #4–#6 merge is yet claimed; adapter CI checks remain in progress. Existing scope approvals and immutable snapshots remain unchanged. Mechanical closure delivery remains outstanding and any new persistence PR requires its own version-bound chat review.

### Current CI recovery checkpoint

wr-0045 records two ordinary validation timeouts on unchanged approved #4/#5 heads. #6 passed; each lower PR also has a successful run. No remaining merge was submitted. Owner authorization is requested to rerun only the two timed-out jobs, then proceed under wr-0044 if checks, protections and exact identities satisfy approval. This is not renewed implementation approval or a workflow/settings change. Closure delivery remains outstanding.

### Current integration and closure delivery

The owner explicitly waived only the two timed-out validation jobs with “We can merge without doing those checks.”, persisted in wr-0046. wr-0047 verifies #4–#6 merged as b5f05c64108ecf59d2e977b05e09a7083f8f8fc0; #3 was already integrated as b01e8e0b2984988092b07c2da56a4cb8cdf38dd4. Cancelled checks remain cancelled. All reviewed implementation is integrated into candidate-revision-9-certification.

Prepare a separate mechanical persistence PR with the immutable review/approval history, actual integration outcome and these living-plan/current-state updates. No new implementation or scope decision is proposed. Closure delivery remains awaiting its own version-bound review and integration; do not label the overall task completed. Prepared request rr-73057793-2d9f-4459-bed3-f69707e04f68 is not delivered until sent in chat. Finish persistence and verification before that request, then stop until owner return without polling or extra work. All scope approvals, snapshots, exclusions and chat-only rules remain unchanged.
