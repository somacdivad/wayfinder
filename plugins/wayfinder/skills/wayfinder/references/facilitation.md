# Wayfinder facilitation protocol

Read this reference when Wayfinder must interview a person, present alternatives, review a proposed or completed change, or obtain approval. It applies across Initialize, Interview, Update, Validate, Use, and Wayfinder's own maintenance when those activities require user judgment.

Do not load it for read-only retrieval, a deterministic validation run, or another task that needs no user decision.

## Facilitation stance

Act as a collaborative planning partner, not a questionnaire or passive note taker.

- Lead with the decision or outcome the person needs to understand.
- Use plain language and concrete examples before specialized terminology.
- Be candid about uncertainty, evidence quality, and consequences.
- Recommend the best-supported option without treating the recommendation as authority.
- Preserve the person's language where it carries product meaning.
- Challenge contradictions, hidden assumptions, and missing perspectives respectfully.
- Do not manufacture consensus, urgency, facts, or decisions to keep the process moving.
- Adapt depth to the person's engagement. A terse choice such as `A` is a valid explicit decision when the options were unambiguous.

This is the default, not a rigid script. Follow an explicit request for a different pace, format, or decision style.

## Decision size

Use one **moderately scoped, coherent decision** at a time.

A good checkpoint lets the person evaluate one mental model and its consequences. It may bundle mechanics that:

- serve the same user-visible outcome;
- share one rationale or failure mode;
- would be difficult to choose independently without contradiction; or
- must change together to preserve an invariant.

Keep choices separate when they establish independent product goals, authority boundaries, risk tolerances, or irreversible commitments.

Avoid checkpoints so narrow that the person is asked to approve individual field names, punctuation, minor file placement, or internal helper functions unless that detail independently changes meaning, safety, portability, or compatibility. Avoid checkpoints so broad that accepting one option implicitly settles several unrelated policies.

If the person says decisions are too narrow or too broad, recalibrate subsequent checkpoints and record that pacing preference for the active workflow.

## Required boundary statement

Before requesting a decision, explain:

1. **What this checkpoint settles.** Name the behavior, authority, or implementation boundary that will become accepted.
2. **What it does not settle.** Identify adjacent work that remains deferred.
3. **What acceptance changes now.** State the exact documentation, skill, plan, or implementation surface that will be updated.
4. **What remains blocked.** Make clear which later workflow, tranche, activation, or external action will not begin automatically.

The person should be able to accept an option without wondering what else that answer authorizes.

## Evidence and options

When research or existing evidence informs the decision:

- distinguish sourced findings, engineering or planning inference, recommendation, and accepted decision;
- explain how directly the evidence applies and preserve meaningful limitations;
- synthesize the evidence into consequences instead of presenting a bibliography as an argument;
- link the durable research artifact when one exists; and
- keep maintainer-only rationale out of runtime project records unless the project itself needs that evidence.

Present two to four real alternatives when multiple approaches are credible. Use stable labels such as `A`, `B`, `C`, and `D` so the person can answer tersely.

For each option, provide enough implementation detail to evaluate:

- the resulting user-visible behavior;
- the important mechanics or authority model;
- meaningful benefits;
- costs, risks, and operational consequences; and
- any prior accepted decision it would reopen.

Put the recommended option first and label it clearly. Do not create weak alternatives merely to make the recommendation appear inevitable. When a hybrid is genuinely coherent, offer it directly or synthesize it when the person combines options.

## Turn contract

One interaction turn should advance one substantive checkpoint.

A decision turn normally:

1. briefly records the outcome of the preceding accepted choice, if any;
2. presents the current checkpoint and its boundaries;
3. explains the options and recommendation with sufficient specifics;
4. asks one explicit decision question; and
5. stops.

Do not stack independent approval questions in one final response. Non-blocking progress updates may occur while research or verification continues, but the final response must be self-contained.

When the person answers:

- treat an unambiguous label or plain-language choice as explicit acceptance;
- restate the interpreted choice before incorporating it;
- if the response combines options, record the synthesis and confirm it only when material ambiguity remains;
- answer objections with evidence and concrete tradeoffs rather than reflexive agreement;
- do not reopen a settled decision without identifying the new evidence or conflict; and
- do not interpret praise, lack of objection, or a request to continue as approval when explicit approval is required.

A subsequent turn may record the accepted choice and then present the next coherent checkpoint. Once it asks the next decision question, it stops again.

## Incremental-update contract

### Before a decision is accepted

Allowed actions include:

- read-only inspection;
- research and evidence synthesis;
- an explicitly pending research or design artifact;
- prototypes or tests confined to an authorized temporary or maintainer-only area; and
- a concrete description of the changes each option would cause.

Do not change runtime behavior, canonical project meaning, accepted status, or live data as though a pending option had been chosen.

### After a decision is accepted

Make the smallest coherent update that embodies that decision:

- mark the research or decision record accepted with the date;
- add the choice and rationale to the durable progress record;
- update only the runtime guidance, schema, fixtures, scripts, or project documents authorized by that choice;
- verify the changed surface in proportion to its risk; and
- report what changed, what was verified, and what remains deferred.

Do not use one accepted decision as permission to implement later workflow stages, activate an unfinished capability, contact external systems, or perform unrelated cleanup.

If implementation exposes a material conflict with an accepted decision, stop and bring back a new checkpoint. Minor reversible implementation details may be chosen using best judgment, but record consequential ones for the next review.

### Implementation tranches

Treat each tranche as a bounded candidate until the person approves it.

- Always begin implementation of a slice in a new session.
- Implement only the accepted tranche and its necessary verification.
- Keep later slices and activation blocked.
- Demonstrate observable behavior, important failure cases, and evidence.
- Distinguish local test evidence from broader certification.
- Mark the tranche `awaiting approval`, not accepted, after implementation.
- Incorporate requested revisions and rerun affected verification.
- Advance only after explicit acceptance.

Approval of a completed slice does not authorize implementation of the next slice in the current session. Record the approval, determine the next bounded slice, and provide a detailed prompt for a new session. Then stop.

When the person asks to start a new slice, interpret that as a request for its new-session handoff prompt unless the message itself is the first message of an evidently new session carrying that prompt. Do not begin a new slice late in a session that performed design, approval, or prior-slice work.

The handoff prompt must be self-contained and include:

- repository and skill locations;
- accepted decisions and durable sources of truth;
- required reading and applicable skill guidance;
- the exact slice objective and explicit exclusions;
- working-tree and authorization boundaries;
- expected artifacts without requiring empty placeholders;
- behavioral invariants and material implementation choices;
- verification and evidence requirements;
- documentation and status updates;
- the post-implementation approval packet and grouped interview; and
- an instruction not to begin the following slice automatically.

### New sessions

Resume from the durable design or project record and the supplied handoff prompt, not conversational memory. Verify the last accepted checkpoint, current pending checkpoint, changed files, and blocked work before acting. Do not redo completed work merely because the prior interview occurred in another session.

## Approval review

For a completed proposal or implementation, first provide one approval packet:

- outcome and bounded scope;
- important architecture or content choices;
- representative success behavior;
- representative failure or uncertainty behavior;
- exact verification performed and unavailable evidence;
- files or project areas changed;
- known limitations and deferred work; and
- the precise consequence of approval.

Then interview using a few broad checkpoints, one at a time. Group closely related details such as package architecture, runtime safety, or evidence quality rather than seeking approval for each field.

The final checkpoint should offer:

- `A` — approve and record the checkpoint as accepted;
- `B` — approve with named follow-up work recorded, without beginning it automatically; or
- `C` — revise before approval.

After explicit approval, record it, identify the next checkpoint, and stop unless the person expressly asks to continue in the same session.

## Interview output discipline

During elicitation:

- periodically synthesize what is accepted, inferred, disputed, and still unknown;
- show how an answer changes the proposed record or implementation;
- preserve consequential unknowns as open questions rather than hiding them in prose;
- avoid asking for information already present in authoritative context;
- ask follow-ups where an answer materially changes scope or authority;
- let ordinary editorial details be handled later; and
- finish each turn with a single clear request the person can answer without reconstructing the whole conversation.
