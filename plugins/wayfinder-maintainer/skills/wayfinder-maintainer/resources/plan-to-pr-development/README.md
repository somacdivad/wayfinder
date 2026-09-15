# Plan-to-PR Development

Use this workflow for changes to Wayfinder or Wayfinder-maintainer. It connects an owner interview, a durable plan, continuous authorized implementation, and owner-reviewed PRs. It does not activate a candidate, certify a platform family, or turn CI artifacts into accepted evidence.

Start with the maintainer skill and complete current-state authority. A later explicit owner instruction can authorize a named bounded project; quote its scope and exclusions before acting. Research is advice, not authorization.

## Read the resource for the current phase

| Need | Resource |
| --- | --- |
| Establish shared intent and implementation decisions | [Planning interview](planning.md) |
| Investigate options and explain recommendation strength | [Research method](research-method.md) |
| Write the mandatory plan core | [Plan template](plan-template.md) |
| Discover, read, create, update, and preserve approvals | [Plan management](plan-management.md) |
| Decompose work and operate native stacks | [PR boundaries and stacks](prs.md) |
| Implement, delegate, verify, and recognize pauses | [Implementation and checkpoints](implementation.md) |
| Request review, stop, resume, and merge | [Review and integration](review.md) |
| Audit the basis for these defaults | [Research index](research/README.md) |

Read progressively: do not load every research brief for a localized familiar fix. Read the decisive sources completely when they support a consequential decision or authority conclusion.

## Workflow contract

1. Inspect current behavior, relevant history, and governing boundaries.
2. Interview one material question per turn; research consequential options and record decisions.
3. Save a complete plan outside the plugins at `docs/plans/<subject>/<wp-uuid>-<slug>/plan.md`. Obtain explicit approval of that complete version.
4. Implement the approved PR sequence continuously, with tests and necessary documentation in each coherent change. Pause only at required decision boundaries or named checkpoints.
5. Request the owner's review on all ready PRs, present their order and verification, and stop. Do nothing until the owner says review is complete: no polling, scheduled monitor, auto-merge, or extra work.
6. On explicit resumption, inspect feedback. Address changes within approved scope or interview a material revision. Identified, version-bound approval authorizes eligible merges subject to protections; integrate incrementally from the bottom up unless the plan names a merge group.

The living plan owns task scope, sequence, and progress. The design record owns accepted decisions and closures. Current state owns candidate, evidence, activation, and current authorization. Link these authorities; do not repeat mutable status across them.

## Default heuristics

Expand planning for uncertain behavior, interfaces, governance, compatibility, or consequential assumptions. Finish when criteria are observable, consequential choices resolved, PR dependencies clear, and remaining questions explicitly deferred. Split PRs at another independently explainable concern, verification strategy, or rollback boundary; keep behavior, tests, and necessary documentation together. Difficult summaries, interacting concepts, long implementation intervals, and repeated lower-layer rework trigger decomposition review, not arbitrary line limits.

Stack only genuine dependencies and prefer independent PRs otherwise. Delegate only bounded useful work with explicit ownership when parallel benefit exceeds coordination cost; the lead verifies integration. Suggest an early example or experiment when uncertainty could cause substantial rework. Require a pause for material changes to scope, design, authority, or acceptance criteria, and for checkpoints named in the approved plan. Verify each PR and cumulative integration; broaden or repeat checks only when changed surfaces or new concerns justify it.

For immutable approval packets, delivery receipts and shared reporting, read [local reliability CLI](reliability-cli.md) and [owner-accepted synthetic checkpoint examples](reliability-checkpoint-examples.md). These templates confer no live review or platform authority.
