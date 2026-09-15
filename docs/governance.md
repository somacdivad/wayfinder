# Governance

- **Status:** Accepted initial public-repository policy
- **Last updated:** 2026-09-14

The maintainer design record is the authority for accepted Wayfinder product and contract decisions. Research is evidence, not an implicit requirement. Material semantic, package, adapter, evidence, release, or activation changes require explicit owner approval and must preserve prior evidence and decision history.

Changes to either plugin use [Plan-to-PR Development](../plugins/wayfinder-maintainer/skills/wayfinder-maintainer/resources/plan-to-pr-development/README.md). Repository-owned [plans](plans/README.md) carry task scope, PR sequence, acceptance criteria, checkpoints, and progress. `maintain.py plan list/read/create/update` supports bounded reads, concurrency checks, and immutable complete approved snapshots. Approval of the complete plan authorizes only its named implementation and delivery actions; material revisions require replacement-plan approval. After requesting owner review, stop without polling until the owner returns. Identified, version-bound approval authorizes eligible integration under checks and protections; review completion alone does not authorize merging.

Maintainer history lives in the [hierarchical record store](../plugins/wayfinder-maintainer/skills/wayfinder-maintainer/references/design-record/README.md). `maintain.py record list/read/add` provides metadata discovery, exact history reads, and exclusive additions. Corrections and later outcomes create new linked records; current status and authorization remain solely in `current-state.md`. Durable acceptance and terminal closure require an outcome record and an explicit current-state routing update in the authorized task, without repeating acceptance of the same decision.

The default branch should require pull requests, repository validation, stale-review dismissal, and code-owner review for workflows, manifests, frozen assets, adapters, and accepted evidence. Force pushes and branch deletion should be blocked. GitHub Actions receive read-only contents permission by default; write permission is isolated to approval-gated release preparation.

All action dependencies are pinned to full commit SHAs. Workflows do not use `pull_request_target`, do not execute untrusted code with write credentials, and do not install application dependencies. Dependabot may propose action-SHA updates, which require source review.

Evidence and plugin identities use separate tag namespaces. A green certification workflow never publishes a plugin, marks a release latest, or changes activation state.
