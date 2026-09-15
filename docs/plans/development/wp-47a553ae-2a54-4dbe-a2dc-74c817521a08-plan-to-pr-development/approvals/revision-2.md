<!-- WAYFINDER-PLAN:BEGIN -->
```json
{"approval":{"locator":"conversation:current/plan-to-pr-development/implementation-authorization","quotation":"Implement the proposed plan."},"approvalHistory":{},"approvedRevision":2,"approvedSha256":null,"format":"wayfinder-plan","id":"wp-47a553ae-2a54-4dbe-a2dc-74c817521a08","records":["wr-0026","wr-0034"],"revision":2,"schemaVersion":1,"slug":"plan-to-pr-development","status":"approved","subject":"development","summary":"Research-backed interviews, durable approved plans, plan CLI, continuous implementation and owner-reviewed native PR stacks.","title":"Plan-to-PR Development","updated":"2026-09-15"}
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
