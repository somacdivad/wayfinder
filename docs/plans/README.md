# Development plans

Repository development plans are plugin-agnostic Markdown documents organized by subject, then stable plan ID and descriptive slug. They are not runtime Wayfinder project records and require no runtime activation.

```text
docs/plans/<subject>/<wp-UUID>-<slug>/
  plan.md
  approvals/revision-N.md
```

The living plan owns task scope, PR sequencing, and progress. Exact approved versions remain immutable snapshots. Accepted decisions and closures live in maintainer design history; current candidate facts, evidence, activation, and authorization remain solely in the maintainer current-state reference. Documents link to each other rather than duplicate those authorities.

Use `maintain.py plan list/read/create/update` with Python 3.11+ from the resolved source repository. CLI help and [plan management](../../plugins/wayfinder-maintainer/skills/wayfinder-maintainer/resources/plan-to-pr-development/plan-management.md) document inputs, bounded reads, safe writes, progress/material revision handling, and approval provenance. Start with the [plan template](../../plugins/wayfinder-maintainer/skills/wayfinder-maintainer/resources/plan-to-pr-development/plan-template.md). Listings are derived from plan metadata, not an independently maintained authoritative catalog.

Do not rewrite approved snapshots, infer approval from lifecycle metadata, or create plans inside an installed plugin package. Explicit approval of the complete plan precedes implementation.
