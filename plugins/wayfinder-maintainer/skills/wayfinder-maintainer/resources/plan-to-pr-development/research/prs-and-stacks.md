# Reviewable PRs, stacks, and incremental integration

Research question: How should work be split and integrated without creating incoherent changes or excessive coordination?

Researched 2026-09-15. Inspected Google's original small-change guidance, DORA's first-party capability guidance, the original Microsoft study abstract, and the complete official GitHub stack-merge documentation. Microsoft findings here are abstract-level; no uninspected paper detail or quantitative PR threshold is claimed.

## Findings and strength

**Practitioner guidance:** Google defines a small change through self-contained purpose, related tests, reviewer context, and continued system operation. It gives illustrative sizes but explicitly leaves judgment to reviewers. [Original small-CL guide](https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md)

**Delivery research synthesis:** DORA associates smaller independently testable batches and shorter feedback cycles with delivery and organizational performance. These organizational findings support decomposition, but do not experimentally determine a universal PR size or stack depth. [First-party capability guidance](https://dora.dev/capabilities/working-in-small-batches/)

**Empirical qualitative/mixed-method study:** Bacchelli and Bird (ICSE 2013) observed, interviewed, surveyed, and classified review comments at Microsoft. The study identifies change understanding as central and review benefits beyond defect discovery, including knowledge transfer and alternative solutions. [Original authors' publication page](https://www.microsoft.com/en-us/research/publication/expectations-outcomes-and-challenges-of-modern-code-review/)

**Current mechanics:** GitHub native stacks are public preview. They merge bottom-up, with lower approvals/checks, linear history, and base protections required. Stack API merges require the asynchronous interface; auto-merge is unsupported. Lower merges can automatically rebase the next layer. Merge queues may split oversized groups, so a desired group must be checked against actual tool behavior. [Official stack merge documentation](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests)

## Recommended adaptation

Default to one independently explainable behavior or concern per PR, including its tests and necessary documentation. Split when another concern has its own verification or rollback boundary. Prefer independent PRs targeting the project's base; stack genuine dependencies only. A prerequisite may be worthwhile when it is coherent and useful on its own, not merely an unused interface introduced for arbitrary size reduction.

Use reviewer-understanding triggers: a summary becomes difficult, several interacting concepts require separate explanations, implementation spans a long interval, or lower-layer changes repeatedly rework upper PRs. Reconsider decomposition and uncertainty first; never force an arbitrary line-count cutoff or detach tests from behavior. Generated migrations can be large yet conceptually simple and require integrity/provenance checks instead of ordinary line-by-line reasoning.

Merge eligible approved PRs incrementally bottom-up after the owner returns from review. This follows the feedback principle, but is not a direct experimental result about GitHub stacks. Name merge groups when partial integration would be incoherent or unsafe, and verify platform semantics before relying on grouped integration. Resolve uncertainty that might invalidate an earlier interface before merging it.

Native tooling is the default; verify installed support and repository availability first. If missing, stop to explain and propose ordinary chained PRs as a fallback. Do not install tooling, authenticate, bypass protections, force-push outside authority, or silently substitute a workflow. Preview mechanics must be refreshed when used.

## Alternatives and revisit triggers

A single coherent PR may beat a stack for tightly coupled small work. Independent PRs avoid stack maintenance when dependencies are artificial. Revisit boundaries when review latency, conflict churn, integration failures, or repeated architectural reversals make the current split ineffective. Treat local review experience as calibration rather than announcing a universal optimum.
