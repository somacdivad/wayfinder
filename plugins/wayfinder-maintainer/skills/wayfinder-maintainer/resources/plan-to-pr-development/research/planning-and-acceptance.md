# Planning, acceptance, and durable decisions

Research question: What should every plan contain, how should planning depth scale, and when is an implementable plan ready for approval?

Researched 2026-09-15. Inspected official GOV.UK user-story guidance and NASA Requirements Management section 6.2, including process activities and change/verification traceability. Neither source studies this exact owner-agent workflow.

## Findings and strength

**Practitioner guidance:** GOV.UK connects user stories to needs and acceptance criteria, with criteria defining how to recognize completed behavior. This supports observable success rather than task completion as the sole acceptance test. It does not prescribe our complete plan format. [Original Service Manual](https://www.gov.uk/service-manual/agile-delivery/writing-user-stories)

**Systems-engineering guidance:** NASA describes managing requirements baselines, ownership, approved changes, and links between expectations, design, and verification. Its process provides a basis for maintaining decision provenance and checking change impact. The aerospace context can carry much more documentation and oversight than a local plugin change needs. [Original NASA section 6.2](https://www.nasa.gov/reference/6-2-requirements-management/)

The common principle is traceability: explain the desired outcome, the chosen behavior, and how evidence will establish it. These are authoritative practitioner methods, not proof that one particular Markdown heading set improves software outcomes.

## Recommended adaptation

Use a mandatory small core: problem/outcome, scope/authority, decisions/rationale, implementation/PR sequence, acceptance/verification, and risks/unresolved questions. Save every plan outside either plugin so project planning does not become runtime package content. Add migration, interfaces, compatibility, rollout, experiments, and coordination only where their absence would leave consequential choices unresolved.

Scale effort by uncertainty and cost of being wrong. Known localized behavior needs concise planning. Shared interfaces, governance changes, compatibility, uncertain assumptions, and hard-to-reverse effects need stronger evidence and more explicit boundaries. Avoid treating an expanded template as a requirement to invent policy for surfaces the change does not touch.

Finish when observable criteria have credible checks, consequential decisions are resolved, PR dependencies are clear, and remaining questions are explicitly deferred without making implementation depend on their answers. A saved plan and explicit complete-version approval form the boundary. Approval snapshots preserve what was authorized; routine progress remains editable. Material revisions require approval before dependent work.

Separate document authority to avoid stale duplication: the living plan owns task scope and progress, historical records own accepted decisions/closures, and current state owns candidate/evidence/activation/current authorization. Links connect them. This architecture and optimistic-concurrency CLI updates are repository design choices rather than direct findings of the sources.

## Alternatives and revisit triggers

Do not impose a standalone traceability matrix on every small change; criteria-to-PR/test links can suffice. Add a matrix or companion specification if many requirements cross PRs or audit obligations make implicit links unreliable. Revisit the template if reviewers cannot determine the intended outcome, accepted scope is lost across routine updates, or excessive planning detail delays feedback without resolving uncertainty.
