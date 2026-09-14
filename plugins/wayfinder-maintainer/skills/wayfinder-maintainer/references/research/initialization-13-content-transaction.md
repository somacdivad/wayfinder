# Initialization research 13: bootstrap content and recoverable publication

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** How much must initialization learn before writing, what truthful content belongs in each starter document, how should unknowns be represented, what must the user review, and how can dependency-light tooling publish a new multi-file record without overwriting work or presenting partial state as complete?
- **Prior decisions:** Wayfinder uses a strict root manifest, invariant semantic kernel, named starter profiles, and a bounded taxonomy interview. The user must confirm the resulting tree and concern-to-home map before any write.
- **Decision status:** Option A, minimum viable bootstrap followed by one reviewed recoverable publication, accepted by the skill owner on 2026-09-13.

## Executive conclusion

Prefer **Option A: minimum viable bootstrap followed by one reviewed, recoverable publication**.

Initialization should conduct a short semi-structured interview that establishes enough truth to create a coherent, resumable record: project intent, desired outcomes, boundaries, stakeholders and intended readers, constraints and evidence already known, accepted decisions, consequential unknowns, and profile/taxonomy needs. It should not attempt to complete the later Interview workflow. The stopping rule should be evidence-based readiness, not a fixed number of questions: every starter statement is attributable, every known concern has a home or an unresolved marker, important missing perspectives are visible, and the user can review the exact proposed record.

The proposal should use controlled epistemic states instead of blank sections or ambiguous placeholders. The user should see a substantive preview of the complete tree, document purposes and initial content, concern-to-home map, unresolved items, assumptions introduced by synthesis, omitted modules, and target paths. Only explicit confirmation should authorize publication.

A dependency-light tool should then execute a precomputed plan. It stages exact bytes, validates the staged record, rechecks collision and baseline preconditions, creates files without overwriting, publishes the manifest last as the record's discovery marker, validates the live record, and retains a journal until success. Because file-system persistence and rename guarantees vary, Wayfinder should promise **recoverability and no-overwrite behavior**, not universal multi-file atomicity.

This recommendation is a design synthesis. Requirements research supports iterative, context-sensitive interviewing and stakeholder coverage; empirical work warns that analysts co-create requirements; uncertainty-modeling studies support making uncertainty explicit; human-factors research disfavors generic warning dialogs; and file-system research shows that portable crash consistency needs an explicit protocol. No reviewed study evaluates this exact LLM-to-Markdown initialization transaction.

Sources were accessed on 2026-09-13.

## Boundary with the later Interview workflow

Initialization answers: **Is there enough reliable structure and content to create a useful project record that can be developed safely later?**

The Interview workflow will answer: **What does the project actually need, in progressively greater depth, and what additions or changes should enter the record?**

This distinction prevents two failure modes:

- writing an attractive but content-free folder tree before the record can explain itself; and
- making users complete exhaustive product discovery before they gain a durable place to preserve what is already known.

Initialization may discover requirements, but its goal is a trustworthy bootstrap, not elicitation completeness. It should finish with an explicit resumption pointer to the Interview workflow.

## Evidence synthesis

### 1. Interviewing is appropriate, but no single elicitation recipe is sufficient

Pacheco, García, and Reyes reviewed 140 studies of requirements-elicitation techniques. Their synthesis reports that interviews often obtain more and more complete information, while effectiveness still depends on project, stakeholder, domain, and information type. The review recommends selecting techniques for context and notes the value of combining techniques rather than assuming one universal method.^1

**Implication:** use a semi-structured bootstrap interview plus inspection of existing project material and a structured preview. Do not treat a fixed questionnaire as proof of completeness.

### 2. Begin broadly, then probe omissions deliberately

Qualitative-interview guidance recommends starting with open, context-setting questions, proceeding to more specific probes, keeping prompts conversational and neutral, and closing by asking what was missed.^2 Burnay, Jureta, and Faulkner additionally studied what stakeholders are more or less likely to mention during requirements interviews and argue that topics unlikely to be volunteered warrant prepared prompts.^3

**Implication:** the bootstrap begins in the user's language, then uses a coverage screen for easy-to-miss matters such as non-goals, constraints, unavailable stakeholder perspectives, evidence gaps, risks, and consequential unknowns. The screen is a probe, not a template to populate speculatively.

### 3. Stakeholder identification is itself a quality risk

Pacheco and García's systematic review found substantial limitations across stakeholder-identification approaches and emphasized the connection between stakeholder identification and requirements quality.^4 This evidence comes from software requirements engineering, so it applies most directly to software-product profiles, but the general risk of treating one informant as the whole stakeholder system transfers to other plans.

**Implication:** initialization records both known stakeholders/intended readers and important perspectives that are absent or still unidentified. It never converts silence from one participant into consensus.

### 4. Analysts and interviews co-create requirements

Ferrari, Spoletini, and Debnath empirically examined interview-based elicitation. In their study, only 30–38% of post-interview requirements were fully traceable to initial customer ideas; up to 20% described entirely novel features and up to 29% covered novel roles. They conclude that analysts play a material role in co-creation rather than merely transcribing requirements.^5 The setting was a fictional mobile-app exercise with 30 analysts, so the quantities must not be generalized to all projects.

**Implication:** any agent-introduced synthesis, candidate requirement, category, or wording that changes meaning must be exposed in the preview and confirmed. Plausibility is not authority. Accepted decisions require affirmative evidence, not inference.

### 5. Initial scope can be high-level and elaborated iteratively

Inayat and colleagues' systematic review identified 17 agile requirements-engineering practices across 21 papers and describes iterative requirements work rather than a single exhaustive up-front specification.^6 ISO/IEC/IEEE 29148 likewise treats elicitation, analysis, specification, validation, and ongoing requirements management as lifecycle concerns.^7

**Implication:** initialization needs a coherent high-level brief and visible gaps, not a completed specification. Subsequent Interview and Update workflows are expected, not evidence that initialization failed.

### 6. Unknowns should be explicit and typed

Moynihan's study of requirements uncertainty argues that uncertainty has different forms needing different management strategies, cautioning against one generic response.^8 Ahmad and colleagues extended restricted use cases with explicit uncertainty constructs and evaluated the method in two industrial cyber-physical-system cases; explicit modeling surfaced large numbers of previously unspecified uncertainty requirements.^9 The method and reported quantities are domain-specific, but they support the narrower proposition that naming uncertainty helps people inspect and refine it.

**Implication:** distinguish hypotheses, assumptions, open questions, deferrals, exclusions, and areas not yet elicited. A bare `TBD` obscures both why knowledge is absent and what should happen next.

### 7. The preview is an external representation, not a confirmation ritual

Zhang and Norman show that external representations can change the structure and difficulty of cognitive tasks by making information and relationships perceptually available.^10 By contrast, Vance and colleagues found that frequent nonessential notifications can generalize habituation and reduce attention to important warnings.^11

**Implication:** show the actual proposed artifact and its relationships—tree, content, unknowns, sources, and target paths. Do not rely on a generic “Are you sure?” dialog. Confirmation should occur after meaningful review and only once the proposed bytes are stable.

### 8. Portable multi-file atomicity cannot be assumed

Pillai and colleagues studied application crash consistency across six Linux file systems and found materially different persistence properties; their analysis uncovered 60 vulnerabilities in 11 widely used applications.^12 This does not prescribe Wayfinder's exact protocol, but it strongly rejects assuming that a sequence of ordinary writes is universally atomic or durably ordered.

**Implication:** call the guarantee “recoverable publication.” Stage and validate before publication, create without overwrite, treat the manifest as the discovery/commit marker, journal enough information to distinguish Wayfinder-created files from prior work, and surface interrupted operations on the next run. Do not promise a filesystem-independent all-or-nothing commit.

## Proposed bootstrap readiness contract

The interview uses broad-to-specific questioning and may inspect repository documents the user places in scope. It must establish or explicitly mark the following:

| Area | Minimum evidence before preview | If unavailable |
| --- | --- | --- |
| Identity and intent | Working project name and a user-attributable problem, opportunity, or purpose statement. | Block publication if even a working identity and intent cannot be stated. |
| Outcomes | At least one desired change or result; distinguish an outcome from a proposed feature when possible. | Record `Not yet elicited` and make it a prominent open question. |
| Boundaries | Known in-scope work, explicit non-goals, and material constraints. | Preserve omissions as `Not yet elicited`; never infer “no constraints.” |
| People | Plan owner or accountable perspective if known, intended readers, affected stakeholders, and important absent perspectives. | Record the identification gap and how it might be resolved. |
| Current knowledge | User statements, existing local evidence, accepted decisions, assumptions, and hypotheses kept distinct. | Create an honest sparse state; do not manufacture examples or external facts. |
| Consequential unknowns | Questions that could change scope, outcomes, taxonomy, feasibility, or irreversible choices. | Prompt with a coverage screen; unresolved items enter the register. |
| Structure | Confirmed profile, modules, subjects, paths, and concern-to-home map from Decision 12. | Block until each known concern has one primary home or an explicitly unresolved placement. |
| Publication basis | Exact workspace/record roots, a locally resolvable canonical baseline, and collision-free target set. | Block application; preview may still be produced. |

Readiness is met when all eight areas are either supported or represented by an allowed unresolved state, no required semantic role would be misleading, and the user can evaluate the exact proposal. There is no minimum question count, document length, or percentage-complete score.

## Proposed epistemic-state policy

Use these controlled states when omission could be mistaken for knowledge:

| State | Meaning | Required treatment |
| --- | --- | --- |
| **Hypothesis** | A plausible claim that needs evidence. | State the claim, current basis, and validation need. |
| **Assumption** | A working premise currently being relied on. | State the premise and consequence if false. |
| **Open question** | An answer or decision is needed. | State why it matters and the next evidence, person, or action when known. |
| **Deferred** | Work is deliberately postponed. | Record the reason and a trigger for revisiting when known. |
| **Not applicable** | The topic was considered and excluded. | Record the reason; do not use it as an empty default. |
| **Not yet elicited** | The topic has not received adequate inquiry. | Link to the open-question register; never interpret it as absence or agreement. |

Confirmed, source-supported prose does not need a `Known` label on every sentence. Attribution, citations, and decision status carry that load. The special labels are used where a reader could otherwise overestimate certainty.

The initializer must:

- reject bare `TBD`, `TODO`, lorem ipsum, fake examples, and unexplained “none” in generated starter content;
- omit optional empty sections rather than imply they were investigated;
- put `Not yet elicited` in a required but unanswered section and link to the corresponding register item;
- record a decision as accepted only when the user identifies it as accepted or supplies an authoritative record that does;
- label externally derived claims as evidence, inference, or hypothesis and preserve provenance under the applicable module rules; and
- avoid inventing owners, deadlines, priorities, technologies, users, metrics, or success thresholds.

## Proposed starter-document content contracts

These contracts define honest initial usefulness, not final schemas. Exact `Kind` vocabulary and module-specific metadata fields remain a separate decision.

### Knowledge map

Include the record's purpose and scope, source-of-truth/authority rules, lifecycle distinction among current synthesis, research, open questions, and decisions, enabled module map, navigation guidance, and the next recommended workflow. It must let a new reader understand where a kind of knowledge belongs without reading every document.

### Current-plan or product brief

Include only supported project intent, desired outcomes, stakeholders/intended readers, boundaries and non-goals, known constraints, and explicitly confirmed current direction. Link to detail owners rather than duplicating them. Visible unresolved items link to the open-question register.

### Open-question register

For each consequential unknown, record the question, why it matters, related document or concern, and the next evidence/person/action when known. Do not invent an owner or due date. An empty register says when and how it was checked, not merely “none.”

### Decision index

Explain what counts as a decision, current versus superseded authority, and how records are indexed. Include only decisions whose acceptance is evidenced. If none exist, state that no accepted decisions were identified during initialization.

### Research index, when enabled

Explain the evidence/provenance method, uncertainty treatment, and how research informs but does not silently become a requirement. List actual sources or briefs only. An honest empty state is allowed.

### Architecture or development entrypoint, when enabled

State the module's purpose and boundaries, known constraints or confirmed direction, governing decisions, and relevant unresolved questions. Do not select a stack, architecture, test strategy, deployment model, or commands merely to fill a heading.

### Project-local module entrypoint, when approved

State its independent purpose, audience, authority/lifecycle boundary, relationship to standard modules, actual initial content, and the rationale satisfying Decision 12's extension tests.

Every durable document receives the accepted universal metadata and a candidate ID. Generated indexes are constructed from authoritative declarations and are identified as generated.

## Proposed preview contract

Before any project-record write, show one stable proposal containing:

1. exact workspace root, record root, entrypoint, canonical baseline, enabled modules, and generated artifacts;
2. the complete target tree and explicit confirmation that no target currently exists;
3. each document's ID, kind, status, title, summary, purpose, and full proposed initial body or a lossless inspectable rendering of it;
4. the concern-to-home map and module-boundary rationales;
5. all hypotheses, assumptions, open questions, deferrals, not-applicable findings, and not-yet-elicited areas;
6. every agent-introduced inference or material paraphrase that needs confirmation;
7. skipped standard modules and the stated reason for each; and
8. the proposed operation ID and a digest for the complete plan so application can prove it is executing the reviewed version.

The user may revise, confirm, or abandon the proposal. Any content-affecting revision produces a new digest and requires review of the changed proposal. Confirmation authorizes only the exact reviewed plan; it does not authorize overwriting, version-control operations, network fetches, or later plan changes.

## Proposed deterministic publication protocol

The eventual dependency-light initializer should expose two conceptual commands, `plan` and `apply`, even if platform adapters differ.

### Read-only preflight and plan

1. Resolve and normalize the explicit workspace root; verify repository boundary rules.
2. Verify that no discoverable Wayfinder manifest already governs the workspace.
3. Resolve the declared canonical baseline locally without fetching.
4. Enumerate every target path, validate containment and naming, and record whether it is absent.
5. Serialize exact intended bytes using one specified encoding and newline policy.
6. Record document IDs, byte digests, target paths, modules, generated artifacts, tool/schema versions, baseline identity, and preconditions in an operation plan.
7. Run structural, metadata, link, containment, collision, and starter-content validation against a staged virtual record.
8. Emit the substantive preview and plan digest. Do not write within the final record paths.

### Confirmed apply

1. Accept only an explicit plan path/digest and confirmation token; never regenerate semantics during apply.
2. Acquire a narrowly scoped operation lock without treating it as a distributed lock.
3. Recheck the baseline, absence of an existing manifest, target-path absence, and every recorded precondition.
4. Create a journal and private staging area within the workspace on the same filesystem where possible. Record intended targets and hashes before live publication.
5. Materialize and validate every staged byte.
6. Create parent directories only when absent, recording exactly which ones the operation created.
7. Publish non-manifest files with exclusive-create/no-clobber semantics. Verify their bytes after placement.
8. Publish `.wayfinder/manifest.json` last, also with exclusive-create semantics. Its appearance is the discovery marker for a complete candidate record.
9. Validate the live record. On success, mark the journal complete, remove staging data, and retain only the audit data later governance explicitly requires.

### Ordinary failure and recovery

- Before the manifest appears, tools treat the operation as incomplete and do not discover a record.
- If failure occurs after the manifest appears, remove the manifest first only if its bytes still match the operation plan, then remove only files and empty directories created by this operation whose bytes/state remain unchanged.
- Preserve every pre-existing or externally modified path and report it for manual recovery.
- On the next run, detect journals/staging areas, classify the operation from hashes and markers, and offer or report deterministic resume/rollback actions. Never silently assume the prior attempt succeeded.
- Never fetch, commit, merge, push, or invoke external services as part of publication.

The exact journal location, serialization format, durability calls, platform adapters, and recovery CLI remain implementation decisions. The invariant promise is conservative: no overwrites, reviewed bytes only, manifest-last discovery, validation, and evidence-guided recovery.

## Options

### Option A: minimum viable bootstrap plus one reviewed recoverable publication — recommended

Use the readiness contract, content rules, substantive preview, and journaled manifest-last protocol above. Finish initialization with a pointer to the full Interview workflow.

**Benefits:** creates something immediately useful without claiming completeness; exposes analyst contributions and missing perspectives; gives the user one coherent artifact to review; blocks overwrites; bounds deterministic tooling to reviewed bytes; supports recovery from ordinary errors and detectable crashes.

**Costs and risks:** the preview can be substantial; a sparse record still depends on later interviewing; recovery code and platform testing are nontrivial; manifest-last is a discovery convention, not universal durable atomicity; selecting the bootstrap stopping point still requires judgment.

**Best fit:** Wayfinder is both a durable starting mechanism and an iterative planning system.

### Option B: scaffold first, interview later

After profile/taxonomy confirmation, immediately create skeletal documents and conduct all content elicitation in the later Interview workflow.

**Benefits:** shortest time to a visible structure; simplest interview boundary; users can edit familiar files immediately.

**Costs and risks:** produces misleading blanks or boilerplate; the record may not explain its purpose; early structure can anchor later thinking; initialization failure leaves more partial state; “empty” is easily confused with considered and absent.

**Best fit:** the initializer is only a developer-controlled scaffolding tool and all users already understand the record model.

### Option C: complete the full plan interview before the first write

Delay creation until product, research, requirements, architecture, development, risks, and decisions have all been elicited to defined completeness thresholds.

**Benefits:** first publication is rich; fewer placeholder states; one comprehensive review can cover a mature initial record.

**Costs and risks:** high up-front burden; no durable resumption point during discovery; unrealistic completeness claim for evolving requirements; poorly suited to partial stakeholder availability; duplicates the dedicated Interview workflow.

**Best fit:** a bounded plan is being migrated from a known, stable source and can be reviewed in one sitting.

### Option D: write incrementally throughout the conversation

Create and update canonical starter documents after each interview segment, with periodic validation.

**Benefits:** immediate persistence and visible progress; small content deltas; interruption loses little conversational work.

**Costs and risks:** users review fragments rather than one coherent proposal; early statements become canonical before contradictions surface; many confirmation points encourage habituation; rollback and partial-state semantics become much harder; deterministic scripts cannot cleanly separate discovery from application.

**Best fit:** an already initialized record is being developed through the future Interview or Update workflow, not first publication.

## Recommendation

Choose **Option A** as one policy bundle:

1. Separate the minimum bootstrap interview from later full-plan interviewing.
2. Use a semi-structured broad-to-specific interview with deliberate coverage prompts.
3. Stop on the readiness contract, not a question count or artificial completeness score.
4. Generate only attributable content and use controlled epistemic states for consequential gaps.
5. Give each kernel/module entrypoint the honest starter-content contract above.
6. Present one substantive, digest-bound preview of the exact record and obtain active confirmation.
7. Make deterministic tooling consume only that confirmed plan.
8. Stage and validate first; publish files without overwrite; publish the manifest last.
9. Journal the operation and remove only unchanged, operation-created material during recovery.
10. Promise recoverable publication rather than filesystem-independent multi-file atomicity.
11. End with validation results and an explicit next step into the Interview workflow.

This decision is intentionally broader than the earlier low-level choices: interview readiness, content truthfulness, preview semantics, and write safety jointly determine whether the first visible record can be trusted.

## What acceptance would change now

The runtime `SKILL.md` would gain the bootstrap boundary, readiness areas, epistemic-state rules, starter-document expectations, preview contract, and recoverable publication invariants. The design record would mark Decision 13 accepted and point to the next initialization decision.

Acceptance would **not** yet make initialization runnable. The next design work should define the document `Kind` vocabulary and per-kind metadata/content schemas closely enough that validators and templates can be implemented. Portable runtime selection, exact journal format, and command interfaces also remain open.

## Deferred decisions

- Exact `Kind` values and per-kind required/optional metadata extensions.
- Exact Markdown section schemas and template wording.
- Open-question item identifiers and lifecycle.
- Source/provenance schema for research and user assertions.
- Operation-plan and journal serialization formats and locations.
- Filesystem durability calls and Windows/POSIX adapters.
- Lock semantics and stale-lock recovery.
- One-time environment detection and runtime selection.
- Existing-record adoption and migration.
- Version-control checkpoint and integration workflow after initialization.

## Next decision if Option A is accepted

Define the **document type system** as one bundle: the `Kind` registry, status vocabulary and transitions, allowed metadata extensions, required content contracts by kind, and how validators distinguish authored authorities from generated navigation.

## Sources

1. Pacheco, C., García, I., and Reyes, M. “[Requirements Elicitation Techniques: A Systematic Literature Review Based on the Maturity of the Techniques](https://doi.org/10.1049/iet-sen.2017.0144).” *IET Software* 12(4), 2018, pp. 365–378.
2. Busetto, L., Wick, W., and Gumbinger, C. “[How to Use and Assess Qualitative Research Methods](https://doi.org/10.1186/s42466-020-00059-z).” *Neurological Research and Practice* 2, 2020, article 14; supplemented by Moser and Korstjens, “[Practical Guidance to Qualitative Research. Part 3](https://doi.org/10.1080/13814788.2017.1375091),” *European Journal of General Practice* 24(1), 2018, pp. 9–18.
3. Burnay, C., Jureta, I. J., and Faulkner, S. “[What Stakeholders Will or Will Not Say: A Theoretical and Empirical Study of Topic Importance in Requirements Engineering Elicitation Interviews](https://doi.org/10.1016/j.is.2014.05.006).” *Information Systems* 46, 2014, pp. 61–81.
4. Pacheco, C., and García, I. “[A Systematic Literature Review of Stakeholder Identification Methods in Requirements Elicitation](https://doi.org/10.1016/j.jss.2012.04.075).” *Journal of Systems and Software* 85(9), 2012, pp. 2171–2181.
5. Ferrari, A., Spoletini, P., and Debnath, S. “[How Do Requirements Evolve During Elicitation? An Empirical Study Combining Interviews and App Store Analysis](https://doi.org/10.1007/s00766-022-00383-7).” *Requirements Engineering* 27, 2022, pp. 489–519.
6. Inayat, I., Salim, S. S., Marczak, S., Daneva, M., and Shamshirband, S. “[A Systematic Literature Review on Agile Requirements Engineering Practices and Challenges](https://doi.org/10.1016/j.chb.2014.10.046).” *Computers in Human Behavior* 51(B), 2015, pp. 915–929.
7. ISO/IEC/IEEE. “[ISO/IEC/IEEE 29148:2018—Systems and Software Engineering: Life Cycle Processes: Requirements Engineering](https://www.iso.org/standard/72089.html).” 2018; reviewed and confirmed 2024.
8. Moynihan, T. “[Coping with Requirements-Uncertainty: Theories and Practice](https://doi.org/10.1016/S0164-1212(00)00049-2).” *Journal of Systems and Software* 57(2), 2001, pp. 99–109.
9. Ahmad, M., Belloir, N., and Bruel, J.-M. “[Specifying Uncertainty in Use Case Models](https://doi.org/10.1016/j.jss.2018.06.075).” *Journal of Systems and Software* 144, 2018, pp. 573–603.
10. Zhang, J., and Norman, D. A. “[Representations in Distributed Cognitive Tasks](https://doi.org/10.1016/0364-0213(94)90021-3).” *Cognitive Science* 18(1), 1994, pp. 87–122.
11. Vance, A., Jenkins, J. L., Anderson, B. B., Bjornn, D. K., and Kirwan, C. B. “[The Fog of Warnings: How Non-essential Notifications Blur with Security Warnings](https://www.usenix.org/conference/soups2019/presentation/vance).” *Fifteenth Symposium on Usable Privacy and Security*, 2019, pp. 407–420.
12. Pillai, T. S., Chidambaram, V., Alagappan, R., Al-Kiswany, S., Arpaci-Dusseau, A. C., and Arpaci-Dusseau, R. H. “[All File Systems Are Not Created Equal: On the Complexity of Crafting Crash-Consistent Applications](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai).” *11th USENIX Symposium on Operating Systems Design and Implementation*, 2014, pp. 433–448.
