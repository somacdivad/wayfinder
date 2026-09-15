# Owner review and merging

Read at final PR handoff and when the owner returns after reviewing. This is distinct from plan approval: a ready implementation is not an accepted or merged implementation.

## Final handoff: stop

Finish all authorized implementation, verification, plan progress, PR descriptions, and routing before requesting review. Present the PR links and dependency/merge order, concrete changed behavior, verification results, unavailable observations, unresolved risks, and any merge group. Request the named owner's review on every ready PR. Use one consolidated version-bound decision packet; per-PR factual tags link that request without separate approval questions. If GitHub prohibits requesting the PR author's own review, tag the owner in the PR conversation and explain that explicit approval here is supported; do not use a fabricated review or silently substitute another reviewer.

If explicitly included in the approved plan, immediately save returned comment IDs/URLs within the terminal delivery operation, then stop and do nothing until the owner returns. Outside that explicit receipt authority, stop immediately after requesting reviews. Do not poll reviews, wait in an active loop, schedule monitoring, enable auto-merge, or perform follow-up work. A later user status request or review-completion message permits its requested inspection, not an automatic approval.

## Interpret the returned decision

When the owner says review is complete, fetch the identified PR metadata, head identities, review submissions/threads, and required check state through available authorized read interfaces. Bind the decision to named PRs and reviewed versions. "I'm done reviewing" without an approving decision does not authorize merging; inspect feedback and ask one concise question if still ambiguous.

An explicit GitHub approval by the owner or explicit approval here bound to identified reviewed PRs authorizes merging subject to current checks, protections, dependencies, and plan merge groups. GitHub does not allow authors to approve their own PRs; owner approval here records user authority but does not satisfy otherwise-required GitHub approvals. Stop if repository protections prevent merging; never bypass them or change settings. See [GitHub review requirements](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews).

Address requested changes within the approved plan. Interview on material revisions instead of silently expanding scope. Any code/behavior changes after approval require the applicable renewed review and verification before merge; do not carry an approval forward to changed semantics merely because GitHub still displays it. Preserve exact head identity when checking or submitting a merge to prevent races.

## Merge and close

Default to incremental merging of eligible approved PRs from the lowest unmerged layer. Honor declared merge groups: a group requires all affected PRs reviewed and eligible. Native stack merges must use a supported documented stack-aware interface; GitHub's API requires its asynchronous stack merge operation, not an ordinary synchronous PR merge tool. Determine the repository's enabled merge method/queue and preserve it; do not change policy or silently fall back. Verify merge outcome before recording it. See [native-stack merging](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests).

Record actual integrated commits/PRs and verification in the living plan and append accepted decisions or closure through `maintain.py record add` where required. Explicitly update current-state routing together with durable closure. If a final closure update requires a new PR, implementation approval covers creating that mechanical persistence PR, but merging it requires its own version-bound owner PR approval and repository checks. This is review of a new delivery artifact, not another acceptance of the already accepted implementation decision. Never merge a new closure PR under approval of a different PR. Report closure delivery as outstanding until integrated; do not label the task completed prematurely or begin another project automatically.

## Reliable delivery and verification

Use [local reliability CLI](reliability-cli.md) for immutable packets, supplied receipts, and structured reports under the repository plan. Prepare intent first. An uncertain submission stops delivery; reconcile receipts on owner return before considering a resend. Saved routing must distinguish prepared/acknowledged/uncertain facts and avoid unconditional repeat instructions. Persist only completed facts.

Missing required local coverage blocks ready-for-review delivery. Explicit plan-accepted environment limitations remain unavailable/skipped, never passes. Suite success, local coverage, GitHub check state and merge eligibility are separate facts. Render summaries from the same validated result objects using the existing envelope and human reporting conventions. Do not rewrite accepted historical evidence to correct a headline; add a linked factual correction.

On owner return, refresh head, base, merge-base and reviewed-diff identities. Replace a packet for changed head or diff; request renewed approval for changed members. Prior approval remains valid only for explicitly covered unchanged versions. The CLI does not authenticate quotations or fetch current platform state.
