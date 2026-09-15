# Research: approval clarity, review handoff reliability, and verification reporting

Research date: 2026-09-15. Status: advisory research and proposed adaptations, not an accepted design or implementation plan. Prepared in response to the owner's request to thoroughly research mitigations for the three session-audit issues. This is a local uncommitted research draft; the four existing PR heads remain intact. No approval, merge, release, evidence promotion, or operational workflow change is inferred.

## Findings and recommendation strength

The strongest immediately applicable mitigations are an explicit approval referent, durable separation of intentions from completed actions, and test summaries derived from framework result data. Human-computer interaction research supports their rationale; technical documentation determines the exact mechanics. Neither establishes an empirically optimal approval sentence or a proven Wayfinder-specific effect size.

| Audit issue | Recommended mitigation | Basis and limitation |
| --- | --- | --- |
| Four separate approval questions make a bare affirmative ambiguous | One active decision packet for the identified PR set, with an exact version manifest and one question; per-PR tags point to it | Grounding theory and evaluated human-AI guidance support clear referents and disambiguation. Exact packet/registry design is a local synthesis. |
| Saved state still says to finish requests that completed | Save truthful preparation/stop conditions before delivery; reconcile returned platform receipts on explicit owner resumption before considering a resend | Human interruption studies support useful resumption cues; distributed-operation guidance supports intent/receipt separation and safe recovery. GitHub plus Git is not one atomic operation. |
| A successful 94-test run was described as 94 passed despite a skip | Preserve separate result categories and generate every summary from the same structured result | Direct Python framework mechanics. A successful suite and complete required verification are distinct propositions. |

The general default should be less ambiguity and stronger evidence binding, without routine added approval friction. Cognitive forcing should be considered only where consequential uncertainty survives the mechanical controls and where its cost is justified.

## Research method and scope

This is a targeted primary-source review, not a registered exhaustive systematic review. Searches covered conversational grounding, evaluated human-AI interaction guidelines, cognitive forcing and overreliance, 2025–2026 published work on AI reliance and interruption/resumption, structured handoff reviews, idempotent external operations, current GitHub review/comment semantics, and Python unittest reporting. Search dates and source inspection are recorded here rather than treating search-result rankings or crawl timestamps as publication dates.

Sources were prioritized as follows: original experiments and author manuscripts; original systematic reviews; official product documentation and reference implementation; first-party operational reports. Secondary commentary and promotional summaries were not used to establish the recommendations. Newer sources were sought to check transferability and contrary results, not to discard older well-established mechanisms solely because they are older.

Relevant local sources inspected: complete maintainer SKILL/current state/approval protocol in the session audit; Plan-to-PR research method and research index; review guidance; the actual self_test_command implementation. The local implementation parses unittest's human-oriented `Ran ...` and `skipped=...` text and exposes `tests`, `skipped`, skip reasons, and exit status. It does not expose an explicit passed counter. That is a reporting improvement opportunity, not evidence that a test failed or that the historical suite was unsuccessful.

## Primary evidence register

### S1. Clark and Brennan, Grounding in Communication (1991)

[Author-hosted chapter](https://web.stanford.edu/~clark/1990s/Clark%2C%20H.H.%20_%20Brennan%2C%20S.E.%20_Grounding%20in%20communication_%201991.pdf). Theoretical synthesis of communication research, published in an APA edited volume. Inspected grounding criterion, contributions/acceptance, repair, least collaborative effort, and reference grounding sections.

Communication requires shared understanding sufficient for the current purpose, not just a question followed by an affirmative. Identifying the referent and repairing misunderstandings are collaborative work. It also matters how much effort both participants expend. This supports making the approval target explicit and reducing avoidable repair turns; it does not experimentally prove one globally active PR approval request is optimal.

### S2. Amershi et al., Guidelines for Human-AI Interaction (CHI 2019)

[Author-hosted paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2019/01/Guidelines-for-Human-AI-Interaction-camera-ready.pdf). Peer-reviewed design-guideline development/evaluation. Inspected abstract, guideline table, validation approach, and applicability discussion. Evaluation included 49 design practitioners and 20 AI-infused products.

The guidelines include communicating capability and uncertainty, presenting task-relevant information, enabling correction/dismissal, and limiting/disambiguating services when intent is uncertain. These support an approval packet with concrete authority, exclusions, and a clear way to revise or approve a subset. This is evaluated design guidance, not a controlled comparison of GitHub merge-approval formats or modern coding agents.

### S3. Buçinca, Malaya, and Gajos, To Trust or to Think (CSCW 2021)

[Author-hosted paper](https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca21trust.pdf). Peer-reviewed experiment, retained sample N=199. Inspected abstract, intervention/results, discussion, and limitations.

Cognitive forcing reduced following incorrect AI suggestions compared with simple explanatory interfaces. The strongest interventions received less favorable usability ratings; benefits differed by motivation for effortful thinking. Overall human-plus-AI performance was not significantly improved relative to simple explanatory conditions. This is a reason to avoid assuming that repeated confirmations or forced deliberation necessarily improve the workflow. The experiment's food-choice task is indirect evidence for code review.

### S4. Mei et al., Passing the Buck to AI (TOCHI listing, 2026)

[Author manuscript, revision 22 January 2026](https://arxiv.org/html/2505.01537v2), [author lab publication listing](https://wildlab.cs.washington.edu/), [publisher DOI](https://doi.org/10.1145/3786326). The lab lists the work in ACM Transactions on Computer-Human Interaction, 2026; the publisher DOI fetch was forbidden. Inspected manuscript abstract, design implications, and limitations; the manuscript retains publishing-template placeholders, so it is not represented as the inspected final publisher version.

In an online nutrition fact/myth task with N=810, decision-making tendencies were associated with seeking AI information, reported reliance, and explanation-reading time. These measures do not establish causal improvement from a specific intervention, and the study did not firmly establish overall decision-performance differences due to buckpassing. It supports adaptable, comprehensible information presentation; it does not justify profiling the owner or diagnosing reliance from brief affirmatives.

### S5. Trafton et al., Preparing to Resume an Interrupted Task (IJHCS 2003)

[Original paper in research-literature archive](https://www.interruptions.net/literature/Trafton-IJHCS03.pdf), [publisher DOI](https://doi.org/10.1016/S1071-5819(03)00023-5). Peer-reviewed experiment. Publisher fetch unavailable; original paper inspected, especially abstract, prospective/retrospective preparation, and discussion.

Participants given an interruption-warning interval prepared more and resumed more quickly; participants also adapted with practice. The paper distinguishes remembering the prior state from encoding what to do upon resumption. This supports a checkpoint that records both completed facts and the next permitted activity. It does not establish that a Markdown summary alone is reliable agent memory, or prescribe a fixed checkpoint frequency.

### S6. Bahnsen, Dischinger, and Grundgeiger, AR Cue Reliability (CHI 2025)

[Author university abstract and citation](https://www.mcm.uni-wuerzburg.de/psyergo/team/pd-dr-habil-tobias-grundgeiger/publikationen/), [publisher DOI](https://doi.org/10.1145/3706598.3713685). Peer-reviewed conference paper; abstract/citation inspected, not full text. N=120 in an interrupted physical sorting task.

Cue reliability changed resumption strategies and speed/error tradeoffs. This supports checking the reliability of resumption cues rather than simply providing more cues. The manipulation was cue presence/absence, not deliberately stale written instructions. Its reliability percentages are not thresholds for trustworthy agent checkpoints.

### S7. Bahnsen and Grundgeiger, AR-Cues Change Users' Strategy (CHI 2026)

[Author university abstract and citation](https://www.mcm.uni-wuerzburg.de/psyergo/team/pd-dr-habil-tobias-grundgeiger/publikationen/), [publisher DOI](https://doi.org/10.1145/3772318.3790673). Peer-reviewed conference paper; abstract/citation inspected, not full text. N=50 in a physical sorting experiment with deferrable interruptions.

Resumption cues changed when participants accepted interruptions and reduced reported stress, while not eliminating the value of task-resumption strategies. This is recent supporting evidence for useful cues combined with appropriate breakpoints, not proof that cues can replace preparation. It does not directly measure LLM compaction or code-review receipts.

### S8. McCarthy et al., Structured Handoff Protocols (BMJ Quality & Safety 2025)

[Original systematic-review abstract](https://pubmed.ncbi.nlm.nih.gov/40306923/), [publisher paper](https://qualitysafety.bmj.com/content/qhc/early/2025/04/29/bmjqs-2024-018385.full.pdf). Peer-reviewed systematic review; original abstract inspected. Full PMC page returned a browser challenge and the AHRQ PDF did not expose substantive text, so full-review inspection is not claimed.

The review found moderate-certainty evidence for I-PASS and low-certainty evidence for SBAR in within-unit clinical handoffs, with other tools insufficiently studied. This is useful corroboration for structured handoffs plus receiver synthesis, but transfer to software/agent work is indirect. Bundled implementation changes and clinical contexts preclude attributing benefits to a particular mnemonic or claiming a software error-reduction effect.

### S9. AWS Builders' Library, Making Retries Safe with Idempotent APIs (2020/2021)

[First-party engineering report](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/). Article copyright 2020; announced January 2021. Inspected caller-supplied request identity, atomic service-side processing, equivalent retry responses, delayed requests, and same-ID/different-intent handling.

AWS describes operation identities, retaining original request parameters, and rejecting changed intent under an existing identity. Crucially, its atomic/idempotent guarantees are supplied by the service contract. A marker in a GitHub comment is not equivalent to that contract. Applying the idea locally can improve reconciliation, but cannot guarantee exactly-once delivery across independent writers or systems.

### S10. GitHub protected branches, current official documentation

[Protected-branch documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches). Inspected required reviews, stale approvals, changed diffs/merge bases, latest reviewable push, and status-check semantics. Access date 2026-09-15.

Approval can become stale when reviewed changes or merge bases change. GitHub also distinguishes status-check success, skipped, and neutral conclusions in its protection mechanics. This supports binding approvals/check observations to reviewed versions and distinguishing platform eligibility from independently established verification. Existing repository settings were not inspected or changed by this research.

### S11. GitHub issue-comment API, current official documentation

[Comment API](https://docs.github.com/en/rest/issues/comments?apiVersion=2026-03-10). Inspected list/get/update/create interface and response identity. Access date 2026-09-15.

Issue comments also apply to PR conversations; responses expose comment identity and URL, and comments can be retrieved/updated by ID. The documented create interface does not expose an AWS-style caller-provided idempotency token. Therefore a deterministic body marker plus explicit resumption-time reconciliation is a client mitigation, not a documented exactly-once API guarantee. No comments were created or edited during this research.

### S12. Python unittest 3.12.14 documentation and reference case implementation

[Official unittest documentation](https://docs.python.org/3.12/library/unittest.html), [reference TestCase implementation](https://raw.githubusercontent.com/python/cpython/v3.12.14/Lib/unittest/case.py). Inspected TestResult counters, skipped/expected-failure/unexpected-success categories, addSuccess/addSkip/addSubTest callbacks, and case lifecycle. The result.py web fetch was unavailable; its behavior was additionally checked with the existing local Python 3.12.14 runtime in an isolated in-memory experiment.

TestResult provides distinct categories; addSuccess offers a direct pass event. TestCase starts framework accounting before checking a skip decorator. A demonstration with one successful test and one skipped test yielded testsRun=2, passed callbacks=1, skipped=1, wasSuccessful=true. This proves that successful suite status is not a count of successfully executed test bodies. It does not reverify Wayfinder or establish coverage.

## Mitigation 1: make the approval target a first-class object

### Recommended interaction

Use one active decision packet for a coherent delivery. Tag the owner on every ready PR with a factual review notice linking to that packet; do not open another approval question in each notice. The packet can cover several PRs while each PR retains independent review and merge eligibility. A coherent stack does not need an all-or-nothing merge group merely because its decision is presented together.

Include a stable request ID, repository, approved plan snapshot identity, PR numbers and URLs, exact head identities, relevant base/diff identities, dependency order, verification observations, scope/exclusions, and precisely what approval permits. Generate the manifest and human question from the same stored object so a sentence cannot silently refer to a different PR set.

Example, using illustrative identities rather than the current PR heads:

> Review request rr-example covers PR #A at head H1 and PR #B at head H2, in that order, toward the named task base. Do you approve these identified versions for eligible incremental integration, subject to required checks and protections?

The owner may approve all identified members, explicitly approve a subset, request changes, or reject. A bare affirmative is acceptable only when it unmistakably answers this sole active decision. If several requests are genuinely pending, require an explicit referent or ask one narrow clarification. The registry is a binding aid; it never authenticates a user or manufactures authority.

Read back the interpreted decision and boundary once when the owner answers. Persist required outcome/routing before eligible action. Do not ask for another approval of the same decision solely because persistence is necessary. Keep plan approval, implementation/PR-version approval, merge eligibility, and actual closure distinct.

### Version binding and change handling

Head SHA is useful but insufficient to fully describe a reviewed diff: base and merge-base changes can alter what is reviewed without a changed head. Capture enough base/diff identity to detect that case. On owner-authorized resumption, inspect the actual heads, review submissions, dependency/base state, and required checks. A changed reviewed version or diff requires the applicable renewed review; the earlier version-bound approval is not silently carried forward. Do not modify GitHub protections or reinterpret conversation approval as satisfying required independent GitHub reviews.

Do not introduce routine forced typing of hashes, timed delays, repeated yes prompts, or a compulsory rationale for every ordinary approval. These might increase friction without solving the underlying referent mismatch. Extra independent review or an explicit consequence check can be suggested for unusually consequential decisions during planning; it remains proportional and task-specific.

### Evaluation criteria

- A bare yes with exactly one clear active packet binds only its members and versions.
- A bare yes with multiple unresolved packets produces no approval or mutation.
- Explicit approval of one member leaves the others unapproved.
- Review-completion, praise, or silence does not become approval.
- A superseding packet retains prior provenance and marks the old request ineligible.
- Changed heads or review-relevant base/diff changes invalidate the applicable prior binding.
- A valid owner decision still cannot bypass platform protections or checks.

Measure ambiguous-response repairs and unintended authority expansion; also measure owner effort and time to locate scope. Fewer prompts is a benefit only if clarity and authority correctness are preserved.

## Mitigation 2: make handoffs truthful across the external-action boundary

### Diagnose the actual failure

The saved document was written before review comments were sent, correctly respecting the final stop. Its future-tense imperative then outlived the operation. This is an intention/completion mismatch, not evidence of duplicate sends, an unauthorized merge, or a broken approval snapshot.

Git/local documents and GitHub comments do not share one transaction. Writing “sent” before sending can create false completion. Writing “send these” and treating it as evergreen can cause duplicates on resumption. Adding an automatic background reconciliation job would contradict the owner's no-polling instruction. These are design constraints that wording alone must acknowledge.

### Recommended minimal design under the current strict stop

Before final delivery, persist facts that are already true:

- implementation and verification complete within their named scopes;
- exact prepared PR/version/request manifest;
- final delivery operation prepared, with its explicit stop boundary;
- completion receipts must be reconciled on owner-authorized resumption;
- no automatic resend, polling, monitoring, or merging.

Replace evergreen “Finish the final review requests” with a conditional routing statement such as:

> Implementation is complete. Owner-review delivery is the final bounded operation. On explicit owner return, reconcile its recorded/platform receipts before considering any resend; do not infer approval or automatically repeat delivery.

Retain each successful tool response's PR number, comment ID/URL, and identified version in the session output. A success receipt demonstrates creation at that time; if continued existence matters later, inspect it only on authorized resumption. If a call fails after it might have taken effect, classify completion as uncertain instead of blindly repeating the mutation. A timeout is not proof that nothing happened.

On owner return, inspect the bounded identified receipts and actual review context. Send only explicitly authorized missing notices after reconciliation. If duplicates exist, report them; don't silently delete or rewrite someone else's communication. Clear known completed work from the next-action route during that authorized reconciliation task.

A deterministic marker containing the request/member/version can help identify an existing notice when a response was lost. Prefer known returned IDs over broad searches. If no ID exists, inspect a bounded complete relevant comment set with pagination as needed. Client markers and a single lead writer reduce duplicate risk; they cannot eliminate races or promise exactly-once semantics without server support.

### Optional stronger delivery journal

If the owner later approves a terminal delivery operation that includes receipt persistence, a local append-only journal can separate prepared, attempted, acknowledged, failed, and uncertain events for every member. A current projection can distinguish prepared/partially delivered/delivered without inventing completed actions. Persisting receipts after tagging must be explicitly included in that terminal operation; it is not an implicit exception to the current “do nothing” stop. Background workers, hooks, new services, or automatic retries are unnecessary defaults and remain separately governed.

Do not pretend such a journal is atomic with GitHub. Preserve operation identity, payload/version digest, and receipt provenance. Recovery reconciles observations; it never relabels accepted historical evidence or infers owner approval.

### Checkpoint and resumption discipline

Use the existing canonical checkpoint create/verify interface before foreseeable compaction when relevant. Record source/HEAD/worktree bindings, already completed facts, unresolved operation states, and the next permitted action. A checkpoint is derived routing, not durable product authority. On reuse, verify it, refresh decisive sources, and rerun only stale checks. Human resumption studies support useful preparation and cues; exact checkpoint design and LLM effectiveness require local behavioral validation.

### Evaluation criteria

- All sends succeed; resumption issues no duplicate sends.
- One send succeeds and another fails; only missing authorized delivery is considered after owner return.
- A send times out after creation; completion stays uncertain until receipts are reconciled.
- A response is lost; matching identity/version evidence is found without a blind resend.
- Another writer or changed PR version is detected; stop/reconcile rather than overwriting state.
- The final owner tag is followed by no autonomous polling or implementation.
- A stale checkpoint does not advance authority or reuse stale validation.

Measure duplicate notices, false completion states, unnecessary retries, resumption time, and stop-boundary violations. Test failures at boundaries, not just the happy-path generated wording.

## Mitigation 3: generate verification claims from one result model

### Reporting contract

Preserve framework-accounted total, successful test-case events, skips and reasons, expected failures, unexpected successes, failures, errors, and interruption/not-executed information where supported. State the accounting unit: test cases, subtests, assertions, adapter/case pairs, or doctor checks. Do not conflate them.

For the recorded ordinary successful run, a precise human summary is:

> Maintainer regression suite: 94 tests accounted for; one skipped because PowerShell is unavailable; no reported failures. Suite status successful. Full doctor: 35/36 passed; the adapter-probe check failed because PowerShell is unavailable.

A direct passed counter would allow a more explicit 93 passed/1 skipped result when supported by the result ledger. The current `tests` plus `skipped` fields alone should not be used to reconstruct every possible unittest outcome. Expected failures and unusual fixture/subtest errors make a universal `passed = total - skipped - len(failures) - len(errors)` formula unreliable.

Use framework callbacks or a dedicated stdlib child runner to emit structured outcomes, preserving the existing subprocess isolation and no-bytecode behavior. Record direct addSuccess events; keep failures/errors and subtest or suite-fixture diagnostics with their appropriate units rather than assuming disjoint one-per-case list entries. Parsing human-oriented `Ran` text is a possible compatibility path but should not be the canonical result source. Missing/malformed output or an interrupted run must be incomplete, not a manufactured all-pass result.

Generate CLI text, JSON, PR verification blocks, plan progress, and final summaries from that same versioned result object. Preserve command/selection, source or tested commit/worktree identity, runtime observations, result digest, and limitations. Do not replace accepted historical records merely to improve future wording; a necessary correction uses the established new linked-record path.

### Suite success, coverage, platform checks, and readiness

These are separate statuses:

1. Did this selected suite succeed under its policy?
2. Which planned cases/adapters/runtimes actually received observations?
3. What does GitHub currently report for the identified tested version?
4. Are all required integration conditions satisfied?

A policy-allowed skip can coexist with suite success, while required verification remains incomplete. A missing executable remains an unavailable observation; if doctor returns failure for it, report that failure rather than changing the result to pass. Distinguish pending, no-check-reported, skipped, neutral, failed, and successful platform outcomes. Never turn absence of a check or a successful skipped CI job into proof that its test body ran. Research on code-review usability cannot change these mechanical semantics.

Freeze the tested input identity before describing a result as applying to a PR head. A later metadata-only description edit does not create a new tested code version, but a source-changing push does. If final state/progress edits change routed inputs, rerun the relevant integrity checks as already required. No test count proves behavioral sufficiency, full-family certification, or activation.

### Evaluation criteria

- One passing plus one skipped test yields separate counts and successful suite status, not two passes.
- Expected failures and unexpected successes retain their distinct meanings.
- Multiple failing subtests do not create negative or inconsistent case pass counts.
- Fixture/import errors and early interruption remain visible and incomplete as appropriate.
- All-skipped or zero-discovered runs do not silently satisfy a required execution obligation.
- A missing required runtime preserves the nonpassing doctor result and observed coverage gap.
- Human/JSON/PR summaries agree on accounting unit, identity, categories, and limitations.
- No-check-reported on a new head is not inherited as a pass from the preceding head.

Measure disagreement between rendered summaries and result facts. Require zero discrepancies in deterministic accounting scenarios. An independent behavioral review should check whether a reader can correctly identify what passed, what was skipped/unavailable, and what remains unverified; prose matching alone is insufficient.

## Alternatives and sequencing

Start with truthful wording and a single consolidated decision packet. These reduce ambiguity without new dependencies or platform services. Then add structured result reporting, which offers a direct measurable correction to a demonstrated semantic problem. Add mechanical packet/journal validation only where repeated use or a demonstrated recovery failure justifies a script.

Approval and handoff guidance can form one coherent documentation concern; structured verification reporting plus its tests/documentation can be an independent behavioral PR. Stack them only if an implemented shared packet actually depends on the new result schema. Keep this advisory draft separate from already requested PR versions until the owner chooses and approves a concrete follow-up plan. Do not automatically restack, push changes, request renewed review, alter settings, or merge based on the research request.

A new follow-up plan should align on the authoritative decision-packet location, how approval subsets and supersession are represented, whether terminal delivery may include receipt persistence, and what verification coverage is mandatory versus a disclosed permissible baseline. These are owner decisions; literature informs but does not settle them.

## Uncertainty, access limitations, and revisit triggers

No directly applicable randomized study was found comparing one consolidated approval question with four PR questions in an autonomous coding workflow. The proposed interface is grounded synthesis and an adaptation of the existing owner approval policy. Most human studies are laboratory or online tasks; their effect sizes and reliability thresholds are not imported into Wayfinder.

The 2026 TOCHI venue listing was verified from an author lab, while the inspected manuscript is an author revision, not the publisher final. The CHI 2025/2026 interruption studies and 2025 handoff review were used at abstract-level scope. Publisher fetch failures and browser challenges were treated as access limitations, not bypassed through authentication. The original Trafton and human-AI guideline/forcing papers were accessible. GitHub/Python docs were inspected for current mechanics. An isolated Python demonstration confirmed the skip-accounting counterexample; it did not execute or alter repository regressions.

Revisit recommendations if GitHub adds documented create-comment idempotency, if the owner changes the terminal stop boundary, if review-version/stack APIs alter identity semantics, if unittest changes reporting contracts, if local scenario tests find false approval/resend/accounting behavior, or if applicable field studies show a material usability or correctness cost. Latest research should refine these controls through measured outcomes rather than replace clear authority and receipts with more narrative instructions.
