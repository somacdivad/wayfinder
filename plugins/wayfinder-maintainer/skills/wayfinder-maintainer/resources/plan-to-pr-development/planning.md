# Planning interview

Produce shared understanding and a durable implementable plan. A completed checklist alone is insufficient: the owner must be able to recognize the desired result and assess what approval authorizes.

## Ground before interviewing

Read current-state authority and affected history through the maintainer CLI. Inspect likely entrypoints, existing tests, command interfaces, dependencies, and worktree provenance. Resolve discoverable facts locally before asking the owner. Keep current behavior, source-backed facts, owner requirements, recommendations, and assumptions distinct.

Maintain a short uncertainty list: question, consequence if wrong, available evidence, owner decision needed, and whether it blocks implementation. Choose the next unresolved question most likely to change the plan. This priority rule is workflow design synthesis; it is not a statistically proven ranking algorithm.

## Interview sequence

Use the following sequence as a discussion guide, allowing natural follow-ups rather than rigidly marching through headings:

1. **Problem and outcome.** Ask about a recent concrete example, affected users or agents, the present obstacle, and what successful behavior would look like.
2. **Scope and preservation.** Establish inclusions, exclusions, compatibility obligations, governed assets, and action authority.
3. **Consequential choices.** Research options when evidence could alter the decision. Explain the recommendation, alternative, tradeoff, and confidence, then ask the owner to choose or correct it.
4. **Implementation.** Establish interface behavior, data flow, failure cases, PR boundaries and dependencies, verification, and any necessary rollout or migration details.
5. **Approval.** Summarize the agreed result, save the complete plan, and request explicit approval of that version with its implementation authority and exclusions.

Ask **one material question per turn** until the plan is decision complete. Continue useful independent investigation while waiting when it does not depend on the answer. Do not convert unanswered questions or elapsed time into approval.

## Neutral questions and concrete examples

Begin with open questions where intent is unknown: “Walk me through the last change that was difficult to complete” or “What would you need to see to recognize success?” Probe the answer with “What happened next?” or “What made that decision difficult?” Test boundaries with a counterexample when it could change implementation.

Use closed confirmation to lock a decision after exploration, not as the entire interview. “Should the CLI write current state automatically?” is useful only after describing the concrete alternatives and effects. Repeated recommendation-plus-yes questions can hide unstated needs and encourage agreement without discovery. Periodically restate the owner's meaning and invite corrections; do not add an extra ceremonial confirmation after every small answer.

The interview approach adapts [GOV.UK's original interviewing guidance](https://www.gov.uk/service-manual/user-research/using-in-depth-interviews) to an owner-agent planning conversation. See [interview research](research/interviews-and-elicitation.md) for the scholarly basis and limitations. One question per turn is the agreed workflow preference, not a research-established optimum.

## Scale effort and know when to stop

Every change has a saved plan; familiar localized fixes may cover the mandatory core in a few paragraphs. Expand research and interviewing when new behavior, shared interfaces, governance, compatibility, uncertain assumptions, or hard-to-reverse actions make a wrong decision expensive. Recommend a bounded prototype, sample output, or experiment before settling a high-risk uncertain choice. Its authority must be explicit; planning mode permits exploration, not implementation.

Stop interviewing and present the complete plan only when:

- Problem, audience, scope, authority, and preservation constraints are understood.
- Acceptance criteria describe observable behavior and have credible verification methods.
- Consequential choices and PR dependencies are resolved; implementation needs no new product or governance decisions.
- Required checkpoints and merge groups are explicit; remaining questions are safely deferred with reasons.

Do not seek certainty about every minor implementation detail. Also do not call a plan complete while leaving consequential defaults to the implementer. If a later finding materially alters approved scope, design, authority, or acceptance, preserve the last approval and interview the revision before dependent work proceeds.

Use the [template](plan-template.md), [research method](research-method.md), and [plan management](plan-management.md) for the saved result. Trace decisions to their sources and verification using the lightweight approach in [planning research](research/planning-and-acceptance.md).
