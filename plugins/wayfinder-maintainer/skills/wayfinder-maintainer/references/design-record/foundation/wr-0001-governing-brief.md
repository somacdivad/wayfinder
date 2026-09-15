<!-- WAYFINDER-DESIGN-RECORD:BEGIN -->
```json
{"authorities":[],"candidateRevision":null,"date":null,"format":"wayfinder-design-record","id":"wr-0001","kind":"context","legacy":{"sourceSectionSha256":"50f2b5ef14f28ddcd6e275719028de55e7b7bcbd770f54dd5a85048a0b05bf5a"},"outcome":"historical","predecessors":[],"schemaVersion":1,"sources":["legacy:references/design-record.md"],"summary":"Governing brief (historical context; current-state.md owns current status).","title":"Governing brief","topic":"foundation"}
```
<!-- WAYFINDER-DESIGN-RECORD:END -->

## Governing brief

Build a reusable skill that creates and maintains a durable project plan resembling the MyPond project record: a structured hierarchy of focused Markdown documents, stable entry points and indexes, research with provenance and uncertainty, explicit decisions with history, architecture guidance, development guidance, and links between those layers.

Wayfinder must eventually support five workflows:

1. Initialize a new plan structure.
2. Interview the user to develop the plan.
3. Update the plan.
4. Validate the plan, including links and semantic consistency.
5. Use the plan by retrieving only the context needed for another agent's task.

Develop the workflows one at a time. Break each workflow into focused, moderately scoped decision points. Bundle tightly coupled mechanics when they form one coherent policy, but keep independent product or governance choices separate. At every decision point:

1. Research relevant scholarly work, psychology, learning science, information science, requirements methods, and other applicable evidence.
2. Present research-backed implementation options with enough specificity for the user to evaluate them.
3. Stop for the user's decision.
4. Record the accepted choice and its rationale.
5. Make the smallest corresponding update to the skill and verify it.

Research knowledge must remain inside the skill, cite original sources, synthesize their implications, and explain the resulting workflow design. It is maintainer-only context and must never be loaded merely to initialize, interview for, update, validate, consume, or implement from a project record.

Prefer deterministic scripts for repeatable actions. Keep scripts portable and dependency-light. If one portable implementation cannot cover plausible environments, provide explicit alternatives. Runtime agents should detect their environment once when they first load Wayfinder, then reuse that result rather than repeatedly probing it.

