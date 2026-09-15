# Plan template

Plans are plugin-agnostic repository documents at `docs/plans/<subject>/<wp-uuid>-<slug>/plan.md`. The CLI manages visible versioned JSON metadata and exact approved snapshots; use [plan management](plan-management.md) for the authoritative closed input schema and command examples. Do not invent metadata fields from this human-content template.

Every plan contains the following core. Scale prose to the change: a small fix can use short paragraphs; a complex project can add focused sections or companion documents. Remove instructional placeholder text from the saved plan.

```markdown
# <Descriptive project title>

## Problem and intended outcome

<Audience, current behavior, obstacle, desired behavior, and a concrete before/after example.>

## Scope and authority

<Included changes, explicit exclusions, preservation and compatibility constraints, and the exact actions approval authorizes. Identify target repository/base branch and separately governed external actions.>

## Decisions and rationale

<Chosen approach, consequential alternatives and tradeoffs, source/research links, accepted owner requirements, and labeled assumptions. Link governing design records and current state without duplicating their mutable content.>

## Implementation and PR sequence

<One or more coherent PRs: intended behavior, dependencies/base, verification, and reason for each boundary. Name required checkpoints, any merge groups, and bounded delegation when useful.>

## Acceptance and verification

<Observable success criteria, checks or demonstrations for each, relevant failure scenarios, cumulative integration checks, and known unavailable evidence.>

## Risks, assumptions, and unresolved questions

<Consequential risks and mitigation, assumptions with validation, blocking questions, explicitly deferred questions with reasons, and what findings would require a material plan revision.>

## Execution progress

<Factual completed/current work, PR links and reviewed revisions, verification results and limitations, next authorized action, and links to approval snapshots and accepted outcome/closure records. Routine updates do not rewrite the approved scope.>
```

Add interfaces, data flow, migration, compatibility, rollout/rollback, experiment, or agent coordination detail only when necessary to prevent a consequential implementation decision being left open. Success criteria must check the outcome, not merely the presence of files or completion of steps. Link each criterion to its PR and verification where useful; no separate requirements bureaucracy is required.

Before approval, distinguish “approved implementation may create branches, commit, push, open/update PRs, run applicable CI, and request owner review” from excluded evidence publication, releases, activation, dependency installation, destructive actions, or unrelated projects. Approval never removes branch protections. If the owner narrows authority, record that narrower boundary.

Preserve an exact snapshot when the complete version is approved. Routine progress can update the living document without another approval. Material changes preserve the prior approval and remain pending until the owner approves the replacement. PR review approval is separately bound to identified PRs and reviewed versions; after review requests, the agent stops until the owner returns.
