# Implement an approved plan

Read before implementing a Plan-to-PR Development task, including work on either plugin. Plan approval covers only its named scope, preservation boundaries, repository, and PR targets. Consult current-state authorization and accepted decision history before consequential actions.

## Continuous execution

After explicit approval of the complete plan, persist required approval/decision routing, then implement its PR sequence continuously within authority. Planned delivery includes task branches, commits, pushes, PR creation/updates, applicable CI, and owner review requests; merging follows the separate review decision. New sessions are optional resumption mechanisms, not mandatory approval handoffs for this workflow. An explicitly narrower plan or owner instruction overrides these defaults.

Keep candidate reopening, frozen byte/evidence edits, evidence promotion/publication, releases/tags, activation, GitHub-settings changes, dependencies, authentication, and live-project changes separately bounded. A development plan may explicitly name a separately governed action only after its required decision exists. Convenience, passing CI, or PR merge cannot infer that authority. Ordinary PR-triggered CI is distinct from dispatching certification or publication workflows.

Start with the full doctor and inspect the relevant baseline, resolved runtimes, help, and existing worktree once. Reuse unchanged successful results; refresh after compaction/interface failure/checkout or relevant input changes. Implement coherent behavior with its tests and documentation. Verify the layer and cumulative effects, update plan progress with actual facts, then continue. Use the repository validator, canonical self-test, proportional conformance checks, whitespace checks, and one final full doctor. State unavailable runtime observations; do not install or simulate them to turn a disclosed baseline green.

## Pause on decisions, not routine work

Required pauses: material scope/behavior/design/acceptance changes; an action outside approved authority; a named plan checkpoint; a prerequisite or missing runtime that prevents required verification; or evidence disproving a consequential assumption. Pause affected work and explain what changed, the recommended correction, alternatives, supporting evidence, and authority needed. Ask one material question at a time. Do not reinterpret approval of the old plan as approval of a revision.

Suggest additional checkpoints during planning when an early concrete example, experiment, risky interface review, or migration rehearsal would resolve consequential uncertainty before substantial investment. Record the deliverable and decision to be made. Avoid fixed checkpoints after every PR or arbitrary elapsed intervals. Routine failures that can be corrected within the approved plan stay with the implementer; disclose genuinely unavailable verification and unresolved blockers instead of masking them.

Classify material findings explicitly. PR decomposition can be refined without new approval when it preserves agreed behavior, authority, dependencies, and acceptance; a new merge constraint or design dependency that changes the reviewed plan is material. Preserve approved snapshots while preparing revisions.

## Selective delegation

The lead may delegate bounded independent research, review, or implementation when the approved plan permits it and parallel benefit exceeds coordination cost. Specify inputs, expected outcome, acceptance criteria, file ownership, allowed tools/side effects, and authorization exclusions. Share exact approved plan/current-state routes; subagents cannot infer broader permission. Use available delegation facilities rather than adding services or dependencies.

Keep coupled decisions and overlapping edits sequential. Assign disjoint files or isolated worktrees for implementation, serialize commits/integration, and have the lead verify actual changes and cumulative tests. Reserve independent review for consequential changes where it adds confidence; do not create agents solely to increase a count. Independent review is supporting evidence, not owner approval or certification.

The research includes [coordination experiments](https://arxiv.org/abs/2512.08296) and [published agent engineering experience](https://www.anthropic.com/engineering/harness-design-long-running-apps). Task dependence, overhead, model capability, and evaluator quality limit transfer to this repository. There is no universal optimal agent count.

## Finish and resume

Before requesting owner reviews: make PRs ready, summarize changes and checks, resolve implementation blockers or disclose them, record exact PR order/head identities and progress, and update current-state routing to the review handoff. Use [review and merge](review.md). When expressly included in the approved plan, save returned review-comment receipts or uncertain delivery outcomes within terminal delivery; then stop without polling, background monitoring, scheduling, or further implementation. Otherwise preserve the immediate post-tag stop. Resume only when the owner returns with direction.

Use [local reliability CLI](reliability-cli.md) for version-bound review packets, terminal receipt state and structured verification. Declare required coverage and explicit environment exceptions in the plan; never report a skip as a pass or suite success as complete coverage.
