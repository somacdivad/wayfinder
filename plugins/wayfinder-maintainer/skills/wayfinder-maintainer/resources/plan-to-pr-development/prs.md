# PR decomposition and native stacks

Read while sequencing PRs or delivering an approved plan. Recommendations are defaults to refine during planning, not universal thresholds.

## Choose boundaries

One PR should explain one coherent behavior or concern and leave the repository coherent and verified. Keep its tests and necessary documentation with its implementation. Split when another independently explainable concern, verification strategy, compatibility boundary, or rollback boundary appears. Separate mechanical prerequisite/refactoring changes from behavior when each is useful and verifiable independently. Do not separate a contract change from the corresponding behavior merely to achieve a small diff.

Prefer the smallest useful change that answers a concrete question or delivers a verified capability. A diff that is difficult to summarize, introduces several interacting concepts, takes an extended implementation interval, or mixes unrelated risks warrants a decomposition review. Generated files and migrations can dominate line counts without comparable semantic complexity: use counts as signals, never a universal limit. Each PR description explains the trigger, resulting behavior, relevant checks, dependency, and disclosed limitations.

For each planned PR, state its purpose, base/dependencies, implemented outcome, preservation/compatibility constraints, verification, and whether it can merge independently. Record task-specific refinements, not speculative PRs with no known content. Reassess deep stacks when lower-layer changes repeatedly cause rebases or design rework; stabilize the uncertain boundary or split independent work out.

Read and use the target repository's PR template before creating or updating its description. In this repository, start from `.github/pull_request_template.md`, complete every section, and preserve the headings and checklists. Link the living plan and exact approved revision. Check only verified passing items; explain failed, pending, skipped and unavailable outcomes beside unchecked items. An explicit `gh --body-file` replaces automatic template handling, so build that file from the template rather than writing a freeform body.

These recommendations synthesize [Google small-change guidance](https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md), [DORA small-batch research](https://dora.dev/capabilities/working-in-small-batches/), and review-comprehension findings discussed in the workflow research. No cited study validates a universal line-count or stack-depth cutoff for this repository.

## Independent PRs and dependent stacks

Independent PRs target the approved task base branch directly. Stack genuine dependencies: the lowest PR targets that base, and each upper PR targets the previous PR's branch. Respect the plan's exact repository/base; do not silently substitute `main` or include unrelated candidate history. GitHub native stacks currently require same-repository, linear branch dependencies and are in public preview. Verify current official documentation and available interfaces before delivery:

- [Native stacks](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs)
- [Stack REST API](https://docs.github.com/en/rest/pulls/stacks)
- [Stack merging](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests)

Use existing `gh stack` tooling or GitHub's native REST surface through an available authorized interface. REST creates a stack from an ordered bottom-to-top list of existing PR numbers whose bases match the chain. Inspect help/API docs; check branches, PR heads, existing stack membership, and action authority first. Do not guess or automate preview APIs from remembered syntax. Do not install extensions, start authentication, or substitute ordinary chained PRs silently. If native support or permissions are unavailable, stop that delivery operation and propose a concrete fallback; unaffected local work may continue within scope.

Use task branches and explicit GitHub repository/head/base parameters; push only approved branch refs without force. Stack maintenance can rewrite branch histories: prefer permitted native operations and stop if a required mutation exceeds plan authority or repository rules. Never reset, clean, or auto-stash unrelated work. Preserve an inventory of pre-existing changes; make a separate explicitly approved prerequisite PR when the plan depends on accepted but unpublished work.

## Verification and merge groups

Verify each layer's behavior and cumulative integration using proportional checks. Ensure PR filters and required checks actually cover upper layers; a green check on a lower branch does not establish stack correctness. Native stack protection behavior is not authority to change GitHub settings or bypass checks.

Default to incremental merging of eligible approved PRs, bottom-up. A merge group is justified when later work could invalidate an earlier interface/governance decision or partial integration violates a known invariant. Prefer resolving the uncertain design or keeping inseparable behavior together rather than splitting it artificially. Name the group and reason in the plan; review and verification remain per PR. A GitHub group merge produces sequential integration and must not be advertised as an atomic multi-PR transaction.
