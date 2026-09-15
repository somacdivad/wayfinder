# Maintainer approval-response protocol

Use this maintainer-only protocol for every explicit acceptance, authorization, or approval checkpoint. Apply it both when asking the decision question and when interpreting the owner's response. It does not turn an ordinary acknowledgment into approval, broaden the active tranche, or authorize adjacent work.

## Before asking for approval

State all of the following in one self-contained approval packet:

1. What exact proposal, implementation, result, or record is being accepted.
2. What exact authority acceptance grants.
3. What remains excluded.
4. The single next bounded task that acceptance will make eligible, when one exists.
5. That the next task will start only from a detailed prompt in a new session and will not begin automatically.
6. One explicit decision question.

Identify the next bounded task before asking whenever one exists. If the workflow is terminal, provide a clearly labeled closure or verification handoff instead of inventing unauthorized product work. The handoff may identify final verification, archival, or closure as the next bounded activity only when it is actually authorized or eligible.

## Explicit affirmative response

Process an unambiguous affirmative in this order:

1. Bind it to the most recent unresolved explicit approval question.
2. Restate the exact interpreted decision and boundary.
3. Check the established workflow and current authority to determine whether a durable acceptance record is required.
4. When authorized and required, persist only the accepted outcome with `maintain.py record add --input FILE` and explicitly update `current-state.md` routing in the same authorized record task. This includes terminal closure: a conversation-only handoff must not leave the same closure pending in repository routing. Persistence of an already accepted decision does not require another acceptance of that decision. Read the complete affected history and decisive authority/evidence first, using `record list` and `record read --id ID --history`; see [the record-store guide](design-record/README.md). Do not infer or record acceptance of adjacent work; commit and push remain separately authorized.
5. Determine the single next bounded task, or the terminal closure or verification handoff.
6. Provide a detailed, self-contained, copy-ready prompt for starting that task in a new session.
7. Stop without beginning the prompt's task.

The new-session prompt must include:

- repository and applicable skill paths;
- accepted decisions and their durable sources of truth;
- required reading;
- current identity and relevant hashes when applicable;
- the exact objective;
- explicit inclusions and exclusions;
- working-tree and preservation boundaries;
- expected implementation files or areas;
- behavioral invariants;
- validation and evidence requirements;
- the required final packet;
- the next explicit approval question; and
- an instruction not to begin later work automatically.

## Explicit rejection or revision request

An explicit rejection or material request for revision leaves the checkpoint pending or changes-requested. Do not record acceptance, advance status, or execute the proposed next task.

Use the Wayfinder facilitation stance. Restate the apparent objection as a tentative interpretation, then ask one material question per turn. Continue across turns until these four items are sufficiently understood:

1. The reason for rejection.
2. The required correction.
3. The evidence or demonstration needed.
4. The acceptance criteria.

Classify concerns where useful as scope, behavior, safety or risk, authority, evidence, verification, wording or presentation, or operational consequences. Periodically summarize what is accepted, disputed, inferred, and unresolved. Answer objections with concrete evidence and tradeoffs. Do not stack a questionnaire into one response: "interview until understood" means continuing across turns.

Present a revised packet only when the correction and its boundaries can be stated coherently. End that packet with one new explicit approval question.

## Conditional response

Treat "approve with follow-up" as accepted only when the condition is explicit follow-up work that does not alter the approved behavior or authority. Record the follow-up without beginning it automatically, then follow the affirmative algorithm.

If a condition changes scope, behavior, safety or risk, evidence sufficiency, or authority, the decision remains pending. When classification is uncertain, ask one concise clarification question and do not advance status.

## Ambiguous response

The following are not explicit approval:

- praise;
- silence;
- "Looks good";
- "Continue";
- acknowledgment that does not answer the approval question; or
- a response that could refer to more than one pending question.

For material ambiguity, leave the checkpoint pending and ask one concise clarification question.

## Conflicting or superseding responses

Bind an answer only to the most recent unresolved explicit approval question. If multiple decisions are pending, do not guess which one the owner answered; ask one concise clarification question.

A later explicit owner correction supersedes an earlier interpretation if implementation has not begun. Never treat approval of one checkpoint as approval of adjacent work.
