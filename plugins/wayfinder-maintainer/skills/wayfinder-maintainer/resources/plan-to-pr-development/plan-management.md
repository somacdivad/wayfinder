# Plan management

Read this resource when creating, retrieving, updating, or recording approval of a development plan. Plans are repository documents, not runtime Wayfinder project records. They require neither a `.wayfinder` manifest nor runtime activation.

## Location and authority

Use `docs/plans/<subject>/<wp-UUID>-<slug>/plan.md` in the explicitly resolved source repository. Subjects may have shallow slash-separated subsubjects. IDs remain stable when wording changes; subject and slug are immutable in the v1 writer. Keep the readable current plan here and exact approved versions in `approvals/revision-N.md` beneath its folder. Preserve all prior approvals.

The plan owns task scope, intended PR sequence, assumptions, verification criteria, and execution progress. The design record retains accepted decisions and closures. `references/current-state.md` alone owns current candidate/evidence/activation facts and current authorization, linking to the active plan and its governing record. A plan's lifecycle or approval metadata does not independently authorize a candidate reopening or external action.

Use `record add` for required accepted outcomes and explicitly update current-state routing in the same authorized task. Do not rewrite historical decisions or request the same acceptance again solely to persist it.

## Commands

Run the canonical maintainer command with Python 3.11+. Inspect `maintain.py plan --help` and selected help before use. Abbreviated examples:

```text
maintain.py plan list --subject development --status approved --format json
maintain.py plan read --id wp-01234567-89ab-4cde-8f01-23456789abcd --format json
maintain.py plan read --id wp-01234567-89ab-4cde-8f01-23456789abcd --revision 2
maintain.py plan read --id wp-01234567-89ab-4cde-8f01-23456789abcd --history
maintain.py plan create --input /private/tmp/plan.json --dry-run
maintain.py plan create --input /private/tmp/plan.json
maintain.py plan update --id wp-01234567-89ab-4cde-8f01-23456789abcd --input /private/tmp/update.json --expected-sha256 CURRENT_HASH --dry-run
```

Writers take explicit JSON and never run Git, access the network, update current state, or authenticate owner approval. Dry-run previews exact prospective bytes and targets without writes. Writes refuse unsafe paths, symbolic/nonregular files, existing create targets, concurrent changes, and unfinished writer state. The expected SHA-256 is the current `plan.md` digest supplied by a complete read, not an approval snapshot or a body-only digest. Do not retry a stale update by substituting a new hash without rereading and reconciling the current plan.

`list` derives metadata from documents instead of maintaining an authoritative catalog. Reads support summary/full/json, response classes, configurable byte budgets, and digest-bound cursors. Summary reads still retain exact text. Follow continuations with unchanged selector/class/budget, reconstruct exact ordered UTF-8 bytes, and verify source SHA-256 before relying on a partial sequence. Discovery previews route work; they do not replace a complete authority read. History contains approved snapshots and the current revision, with scope/completeness explicit. Changed stores invalidate cursors.

## Closed input

Create takes exactly `id`, `subject`, `slug`, `title`, `summary`, `status`, `updated`, `body`, `records`, and `approval`. Generate a standard-library UUID once and supply the same lowercase `wp-UUID` in preview and apply. New plans start as `draft` with `approval: null`. Dates are explicit ISO dates; content is UTF-8 without BOM and LF-only.

```json
{
  "id": "wp-01234567-89ab-4cde-8f01-23456789abcd",
  "subject": "development",
  "slug": "focused-change",
  "title": "Focused change",
  "summary": "The concrete problem and resulting behavior.",
  "status": "draft",
  "updated": "2026-09-15",
  "body": "# Focused change\n\nUse the plan template, scaling detail with the task.\n",
  "records": [],
  "approval": null
}
```

Update uses the same explicit fields plus `changeKind`: `progress`, `material`, or `approval`. Revision, approved revision, snapshot digest, and approval-history digests are allocated by the writer; do not supply generated fields. Preserve identity and location. `records` contains unique existing design-record IDs; link relevant decisions in the body as well. Every current revision binds earlier approval snapshots by exact digests. Each approval also binds its predecessors, avoiding a self-referential hash while detecting historical snapshot tampering.

- **Progress:** record completed steps, PR links, checks, blockers, or review feedback while preserving approved scope and decisions. Use `approval: null`. It cannot promote a draft or changes-requested plan into implementation authority.
- **Material:** explain changes to scope, behavior, design, assumptions that affect acceptance, PR dependencies, or authority. Use `approval: null`; the resulting plan is `changes-requested`, preserving its last approved revision. Pause affected implementation.
- **Approval:** after an explicit owner decision, supply `approval: {"locator": "conversation:...", "quotation": "exact owner words"}` and `changeKind: "approval"`. The resulting approved revision is preserved byte-for-byte as a new snapshot. Bind the quotation to the reviewed plan and its authority; do not infer approval from praise, silence, routine acknowledgments, or requests to continue.

Lifecycles are `draft`, `approved`, `implementing`, `awaiting-review`, `changes-requested`, `completed`, and `abandoned`. Scripts validate mechanical transitions and provenance shape. Agents must assess whether an asserted progress update changes semantics; the writer cannot authenticate an interview or detect concealed scope changes. `completed` means integrated and closure recorded, not merely implemented or owner-reviewed.

An interrupted write may leave a lock/staging state. Inspect ownership, current bytes, approvals, and writer outcome before proposing authorized recovery. Never steal another writer's lock or delete an accepted snapshot to retry.

## Resumption

Read current state, the active plan, its last approved snapshot, and affected decision history. Inspect worktree/branch and PR head identities. Reconcile progress with actual results before continuing. Existing ephemeral checkpoints may help routing only after verification; they never substitute for plan or current-state authority. At final review handoff, persist progress and routing before tagging the owner, then stop without polling or scheduled monitoring.
