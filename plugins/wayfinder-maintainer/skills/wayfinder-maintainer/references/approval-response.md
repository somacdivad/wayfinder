# Maintainer approval-response protocol

Use this maintainer-only protocol for every explicit acceptance, authorization, or approval checkpoint. Apply it both when asking the decision question and when interpreting the owner's response. It does not turn an ordinary acknowledgment into approval, broaden the active tranche, or authorize adjacent work.

## Development-plan mode

For [Plan-to-PR Development](../resources/plan-to-pr-development/README.md), explicit approval of the complete plan authorizes continuous implementation and the named Git/PR delivery actions within that plan. Planned checkpoints and material revisions still require explicit decisions. The living plan and its exact approval snapshot carry task scope; design records preserve accepted decisions; current state alone owns current authorization and candidate facts.

Read [plan management](../resources/plan-to-pr-development/plan-management.md) when persisting a plan approval or revision, [implementation](../resources/plan-to-pr-development/implementation.md) when continuing approved work, and [review](../resources/plan-to-pr-development/review.md) at PR handoff or on the owner's return. Do not apply the legacy new-session stop to an approved development plan. Outside that plan or when an owner specifies a narrower tranche, retain the bounded handoff and stop below. Passing a checkpoint never authorizes another project, candidate reopening, publication, activation, or a separately governed action.

Use one consolidated request in chat bound to exact PR heads and reviewed diffs, with explicit subset decisions. Review requests, feedback, and approval stay in chat. Do not post PR review-request comments, factual tags, or review notifications. Preserve superseded packets and retained unchanged-member decision provenance through the [local reliability CLI](../resources/plan-to-pr-development/reliability-cli.md). Multiple active or ambiguous requests require clarification. Neither local validation nor delivery acknowledgment infers approval.

Complete authorized packet/progress persistence before sending the chat review request. Do not fabricate a GitHub comment receipt for a chat message or save an acknowledgment before the message exists. After sending, stop and do nothing until the owner returns: no polling, active waits, scheduled monitoring, auto-merge, or extra implementation. Review completion alone permits inspection, not merging. Explicit approval in chat must bind identified PRs and reviewed versions; merging remains subject to checks, protections, dependencies, and plan merge groups.

## Before asking for approval

State all of the following in one self-contained approval packet:

1. What exact proposal, implementation, result, or record is being accepted.
2. What exact authority acceptance grants.
3. What remains excluded.
4. The next bounded activity acceptance makes eligible, when one exists, and whether it remains within the approved plan.
5. Whether approval permits continuous work within the named development plan, or requires a detailed new-session handoff and stop outside it. State the final review stop explicitly.
6. One explicit decision question.

A changed PR head or reviewed diff requires a replacement packet and renewed approval; prior explicit approval covers only unchanged named versions. Base/merge-base movement requires comparing the actual diff, not trusting the head alone.

Identify the next bounded task before asking whenever one exists. If the workflow is terminal, provide a clearly labeled closure or verification handoff instead of inventing unauthorized product work. The handoff may identify final verification, archival, or closure as the next bounded activity only when it is actually authorized or eligible.

## Explicit affirmative response

Process an unambiguous affirmative in this order:

1. Bind it to the single unambiguous unresolved explicit approval question and its identified members/versions. If multiple questions are ambiguously pending, ask for clarification rather than guessing.
2. Restate the exact interpreted decision and boundary.
3. Check the established workflow and current authority to determine whether a durable acceptance record is required.
4. When authorized and required, persist only the accepted outcome with `maintain.py record add --input FILE` and explicitly update `current-state.md` routing in the same authorized record task. Plan approval also uses `maintain.py plan update` to preserve the exact approved snapshot. Persistence of an already accepted decision does not require another acceptance of that decision. Read the complete affected history and decisive authority/evidence first, using `record list` and `record read --id ID --history`; see [the record-store guide](design-record/README.md). Do not infer acceptance of implementation from plan approval. Commits and pushes require authority from the approved plan or exact tranche.
5. In development-plan mode, reconcile the decision with the reviewed plan/PR identities, persist required progress and authorization, and continue only the approved activity. For a material revision, preserve the previous snapshot, resolve the revision interview, and obtain approval of the complete replacement before affected implementation resumes. PR approval authorizes eligible merging after the owner returns; it cannot bypass repository protections.
6. Outside an approved development plan, determine the next bounded task or terminal handoff and provide a detailed, self-contained, copy-ready prompt for starting it in a new session.
7. Outside that plan, stop without beginning the prompt's task. At a development review handoff, stop until the owner returns. Record actual integration and durable closure with explicit routing; if closure delivery requires a new PR, that artifact needs its own version-bound review, not another acceptance of the prior implementation decision.

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

Bind an answer only to the single unambiguous unresolved explicit approval question. If multiple decisions are pending, do not guess which one the owner answered; ask one concise clarification question.

A later explicit owner correction supersedes an earlier interpretation. If affected implementation has begun, stop it, reconcile the changed scope and worktree, and prepare a material plan revision rather than silently continuing. Never treat approval of one checkpoint as approval of adjacent work outside the approved plan.

## Historical external delivery uncertainty

The following describes recovery of already-existing external comment deliveries only. It does not authorize new PR comments or tags. Current review handoff is chat-only; persist the packet and prepared state before the final chat message, and use the actual conversation on owner return to establish whether it was sent.

Persist prepared intent before sending; save only acknowledged facts returned by the tool. If a submission times out, save uncertain delivery and stop, without blind retries or polling. On explicit owner return, reconcile actual comment receipts through existing authorized tools and append the observation before considering a resend. An operation marker aids discovery but does not provide server-side idempotency or exactly-once delivery. If local receipt saving fails after a successful submission, retain the tool acknowledgment in the handoff and stop; never claim the receipt was saved. Outside a plan that explicitly includes receipt persistence, retain the immediate post-request stop.
