# Initialization research 15: relationships, questions, and evidence references

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** How should Wayfinder represent typed relationships among briefs, evidence, decisions, and open questions; preserve question and supersession identity over time; cite sources with enough provenance; and generate a compact graph for deterministic validation and selective retrieval?
- **Prior decisions:** Durable document metadata is distributed and authoritative; document IDs are stable; `Kind` is a closed communicative-purpose vocabulary; lifecycle transitions are type-specific; supersession is reciprocal and cycle-free; generated navigation is a non-authoritative projection.
- **Decision status:** Option A accepted by the user on 2026-09-13.

## Executive conclusion

Prefer **Option A: a bounded distributed trace graph, first-class question items, document-local source inventories, and one generated catalog**.

Wayfinder should formalize only relationships that change retrieval, authority, or lifecycle decisions. Version 1 should provide two ordinary document edges—`Governed-By` and `Supported-By`—plus the previously accepted `Supersedes`/`Superseded-By` lifecycle edges. Open questions should be stable embedded items with project-wide `wfq-<ordinal>-<mnemonic>` IDs, a small state machine, and typed connections to the documents they affect, evidence addressing them, and authorities resolving them. Research sources should use frozen document-local `src-NN` anchors with citation, original locator, access date, directness-to-project assessment, use, and limitations.

The distributed declarations should compile into a deterministic `.wayfinder/catalog.json` projection containing document routing metadata, typed edges, and question summaries. Runtime agents can query this small artifact first and open only the authoritative documents selected by the graph. The catalog is never edited and never becomes the sole authority.

This recommendation deliberately avoids claim-level traceability. Requirements-traceability research supports explicit links across artifact lifecycles, but also shows that trace models vary with stakeholder practice and purpose. Design-rationale research supports keeping questions connected to positions, arguments, and resolutions. Cognitive research supports externalizing pending goals with useful resumption cues. Citation principles support persistent identification, access, specificity, and provenance; reference-rot research warns that a URL alone is insufficient. Information-foraging theory supports compact summaries and meaningful link labels as routing cues.

No reviewed study evaluates this exact Markdown syntax, relation vocabulary, or LLM retrieval design. The recommendation is a conservative synthesis optimized for Wayfinder's accepted project-record model.

Sources were accessed on 2026-09-13.

## Design boundary

This decision covers four connected layers:

1. **Document trace edges:** machine-readable statements about governance, evidence support, and supersession.
2. **Question items:** stable unresolved units that can be addressed, deferred, resolved, reopened, or retired without becoming separate files prematurely.
3. **Source entries:** local citations that connect research claims to original material and applicability limits.
4. **Derived graph projection:** a compact routing artifact built from those authorities.

It does not attempt to model every semantic relationship, assign IDs to every sentence, trace implementation code or tests, define automated semantic truth, or decide the final Use workflow. Those expansions should require demonstrated retrieval or change-impact needs.

## Evidence synthesis

### 1. Traceability is useful when it follows artifact origins and downstream use

Gotel and Finkelstein define requirements traceability around following a requirement's life in forward and backward directions, including origins, development, deployment, and use.^1 Ramesh and Jarke synthesized reference traceability models from extensive case studies and found materially different practices among lower- and higher-maturity users rather than one universal graph.^2

**Implication:** preserve the few edges needed for Wayfinder's actual work—authority, evidentiary basis, unresolved questions, and supersession—rather than importing a comprehensive systems-engineering trace model.

### 2. Traceability has unresolved maintenance and automation challenges

Winkler and von Pilgrim's broad survey identifies traceability as valuable across requirements and model-driven engineering while also finding unresolved challenges; it highlights the promise of combining formal links with automated recording.^3 The literature does not show that maximal trace granularity is always beneficial.

**Implication:** capture typed edges at document and question-item granularity, automate validation and inverse views, and defer sentence/claim IDs. Every required manual edge must justify its maintenance cost through a concrete query or integrity check.

### 3. Typed issue networks help preserve design rationale

Conklin and Begeman's gIBIS work represents design deliberation as typed networks of issues, positions, and supporting or objecting arguments. Their early experiments were exploratory, but the work demonstrates how relation constraints can preserve the shape of reasoning rather than merely hyperlinking pages.^4 MacLean and colleagues' Questions–Options–Criteria approach similarly treats questions as organizing nodes for alternatives and evaluation criteria.^5

**Implication:** open questions deserve stable identity and explicit connections to evidence and decisions. Wayfinder should not reproduce a complete argumentation system inside the bootstrap record; options and tradeoffs belong in `decision` documents, while question items provide the durable unresolved thread.

### 4. External question records reduce resumption burden

Risko and Gilbert review cognitive offloading: changing the external environment to reduce a task's internal processing demand.^6 Altmann and Trafton's goal-memory model emphasizes associative cues in retrieving suspended goals and discusses task interruption and resumption.^7 These studies do not test project-plan registers, but they support recording more than a terse question title.

**Implication:** each open question should preserve why it matters, its current state, affected knowledge, and the next resolution step or revisit trigger. These fields provide cues for a future session instead of requiring reconstruction from conversation history.

### 5. Identifiers and provenance matter beyond a live URL

The FORCE11 Joint Declaration of Data Citation Principles calls for credit, persistent identification, access, persistence, specificity, verifiability, provenance, and interoperability.^8 Klein and colleagues studied reference rot in scholarly communication and found that link rot plus content drift affected roughly one in five sampled articles, although the estimate is specific to their corpora and 2014 measurement.^9

**Implication:** source entries preserve a bibliographic citation and original locator rather than using a naked URL. They also record access date, project applicability, actual use, and limitations. Wayfinder does not claim to archive external content or guarantee link persistence.

### 6. Provenance and support are different relations

W3C PROV distinguishes derivation, generation, attribution, and use rather than collapsing them into one generic “related” edge.^10 In a planning record, a research source is provenance for an `evidence` document, while an `evidence` document may support a brief or decision. Treating the source URL itself as directly governing a product requirement skips interpretation and authority.

**Implication:** external citations terminate in evidence documents; cross-document `Supported-By` edges target those evidence documents. Research informs decisions but does not silently become a requirement.

### 7. Retrieval depends on information scent and economical navigation

Pirolli and Card's information-foraging theory models information seeking as adaptive behavior that uses environmental cues to pursue valuable information efficiently.^11 The direct mapping to LLM context selection is an inference, but the design lesson is useful: summaries and typed edges give stronger routing cues than filenames or undifferentiated “related” links.

**Implication:** the generated catalog includes titles, summaries, kinds, statuses, module/subject placement, and typed neighbors. A consumer can inspect the small routing layer before loading full bodies.

### 8. Structure should remain incremental rather than exhaustive

Shipman and Marshall warn that premature formalization imposes cognitive overhead and can cause users to resist or work around a system; they advocate incremental, system-assisted formalization.^12

**Implication:** version 1 has no generic `Related-To`, `Depends-On`, claim IDs, argument nodes, confidence scores, or custom edge types. Add an edge only when its meaning produces a reliable validation or retrieval behavior.

## Proposed document relationship model

### Visible relationship block

An authored document may contain one optional, visible Wayfinder relationship block immediately after its metadata block. Illustrative syntax:

```markdown
<!-- wayfinder:relationships -->
- **Governed-By:** [wf-0042-authentication-policy](../decisions/0042-authentication-policy.md)
- **Supported-By:** [wf-0037-authentication-research](../research/2026-09-10-authentication.md)
<!-- /wayfinder:relationships -->
```

The exact grammar should require:

- exact, non-nesting delimiters;
- one relation and target per line;
- a registered relation label;
- link text equal to the target's exact Wayfinder ID;
- a normalized repository-relative Markdown destination;
- target containment inside the declared record root;
- repeated relation labels allowed, but duplicate edges forbidden; and
- canonical ordering by relation registry order and then target ID.

Ordinary prose links remain legal and receive ordinary link validation, but they do not create graph semantics. An agent must not infer a typed edge from nearby language.

### Version 1 relation vocabulary

| Relation | Source | Target | Meaning and validation use |
| --- | --- | --- | --- |
| `Governed-By` | Any living authored document | `decision` with `Accepted` status | The target decision currently constrains or authorizes the source document. A current source pointing only to a superseded decision is invalid until the governing successor is linked. |
| `Supported-By` | Any authored document | `evidence` with `Active` status | Material claims or rationale in the source rely on the target evidence synthesis. The relationship does not imply that all source content is proven. |
| `Supersedes` | Any authored document metadata | Type-compatible authored document | The source replaces the target for an overlapping declared scope. Must be mirrored by `Superseded-By`. |
| `Superseded-By` | Any authored document metadata | Type-compatible authored document | The source has been replaced by the target. Must be mirrored by `Supersedes`. |

`Governed-By` and `Supported-By` are declared from the consuming document because that document owns the claim about its current authority or evidentiary basis. Generated indexes may show inverse `Governs` and `Supports` views, but those are not separately authored edges.

The registry intentionally omits `Related-To`: its meaning is too weak to drive validation or retrieval. It also omits implementation/test trace edges until the Development, Update, and Use workflows establish a concrete need.

## Supersession list grammar

The accepted conditional metadata fields use an ID-only list so moves do not rewrite identity declarations:

```markdown
- **Supersedes:** wf-0010-old-brief, wf-0014-old-scope
- **Superseded-By:** wf-0045-new-brief
```

Version 1 rules:

- one or more complete document IDs separated by exactly comma-plus-one-space;
- no Markdown links, comments, ranges, aliases, or line continuations;
- IDs sorted by numeric ordinal and never repeated;
- every ID resolves uniquely in the canonical-plus-candidate view;
- source and target belong to the same lifecycle family and have compatible communicative purposes;
- the reverse field must exist in the same confirmed transaction;
- the supersession graph is acyclic; and
- a body `Supersession` section provides human-readable links and scope explanation, while metadata remains the machine authority.

A split or merge may name multiple IDs in either direction. The validator checks every reciprocal pair rather than assuming one-to-one replacement.

## Proposed open-question item model

### Identity and containment

An open question is an embedded durable item owned by exactly one `register` document. It receives a project-wide stable ID:

```text
wfq-<global-question-ordinal>-<frozen-mnemonic>
```

Example: `wfq-0007-guest-retention`.

Question ordinals use a sequence separate from document IDs. Allocation, candidate status, canonical integration, collision precedence, re-key safety, and mnemonic constraints follow the accepted document-ID policies. A question may move between registers without changing ID. IDs are never reused.

Each item uses a non-nesting visible block and an explicit stable HTML anchor. Illustrative structure:

```markdown
<!-- wayfinder:question -->
<a id="wfq-0007-guest-retention"></a>
### How long should guest access records be retained?

- **ID:** wfq-0007-guest-retention
- **State:** Open
- **Raised:** 2026-09-13
- **Applies-To:** [wf-0012-sharing-brief](sharing.md)

#### Why it matters

The answer affects privacy expectations and data-lifecycle design.

#### Next step

Identify the applicable policy constraints and interview the product owner.
<!-- /wayfinder:question -->
```

The heading wording may evolve; the explicit ID anchor remains stable. The parser treats the delimited block, not heading-slug behavior, as item containment.

### Question states

| State | Meaning | Conditional content |
| --- | --- | --- |
| `Open` | Unresolved and not currently in a documented investigation. | Why it matters and next step, or `Not yet identified` with an explanation. |
| `Investigating` | Active evidence gathering or stakeholder inquiry is documented. | At least one concrete current activity or `Addressed-By` evidence document. |
| `Deferred` | Still unresolved but intentionally postponed. | Deferral reason and `Revisit-Trigger`. |
| `Resolved` | An answer or governing decision is recorded in authoritative content. | Resolution summary, `Resolution-Date`, and one or more `Resolved-By` targets. |
| `Retired` | No longer relevant and not answered. | Retirement reason. |

Normal transitions:

```text
Open ─────────► Investigating
  │                  │
  ├────► Deferred ◄──┤
  ├────► Resolved ◄──┤
  └────► Retired  ◄──┘

Deferred ──► Open | Investigating | Resolved | Retired
Resolved ──► Open  (explicit reopen event and reason required)
```

`Retired` is terminal under ordinary workflows. Reopening preserves the same ID and earlier resolution history because the underlying question remains recognizable; a materially different question receives a new ID.

### Question relationship fields

Question blocks use repeated clickable lines rather than comma lists:

| Field | Target | Rule |
| --- | --- | --- |
| `Applies-To` | Any authored document | One or more scopes materially affected by the answer. Required unless the question is explicitly record-wide. |
| `Addressed-By` | `evidence` document | Investigation that informs the question without necessarily resolving it. Optional and repeatable. |
| `Resolved-By` | `decision`, `evidence`, or `brief` | Authoritative location of the answer. Required and repeatable only when `Resolved`. |

Each target uses a Markdown link whose label is the target ID and must resolve to the ID declared at that path. A decision target must be `Accepted`; an evidence or brief target must be `Active`. Inverse views such as “open questions affecting this brief” are generated, not manually duplicated.

### Resumption and history content

Every item retains:

- question title;
- why the answer matters;
- next step while open/investigating, or revisit trigger while deferred;
- resolution or retirement rationale when closed;
- raised date; and
- an append-only transition history containing date, prior state, new state, and concise reason.

The exact transition-history line grammar can be finalized with the Update workflow, but initialization must create the opening event and validators must compare current state with the latest event.

## Proposed research-source model

### Document-local source identity

Each `evidence` document owns frozen source keys `src-01`, `src-02`, and so on. Keys are unique within that evidence document, allocated above the local maximum, never renumbered, and addressed through explicit anchors. The same external work may appear in multiple evidence documents because its use and applicability can differ by research question.

Illustrative source entry:

```markdown
<!-- wayfinder:source -->
<a id="src-01"></a>
### src-01 — Requirements traceability reference models

- **Citation:** Ramesh, B., and Jarke, M. “Toward Reference Models for Requirements Traceability.” 2001.
- **Original:** https://doi.org/10.1109/32.895989
- **Published:** 2001
- **Accessed:** 2026-09-13
- **Applicability:** Adjacent

#### Used for

The distinction between smaller and more extensive traceability practices.

#### Limitations

The cases concern software requirements organizations rather than LLM-maintained Markdown plans.
<!-- /wayfinder:source -->
```

Required fields are `Citation`, `Original`, `Accessed`, and `Applicability`. `Published` is included when the source supplies it and is omitted rather than guessed when unknown. `Original` is a DOI/authoritative URL or a contained repository-relative path for local evidence. `Accessed` is exact `YYYY-MM-DD`.

`Applicability` uses:

- `Direct`: substantially the same population, context, decision, or artifact behavior;
- `Adjacent`: materially analogous but requiring an explicit transfer inference; or
- `General`: theory, method, standard, or broad evidence that constrains reasoning without directly testing this context.

Applicability is not a quality or confidence score. Study design, sample, conflicts, sponsorship, uncertainty, and other limitations stay in readable content.

### Claim citations

Material factual claims in an `evidence` document cite the local source anchor with ordinary Markdown, for example `[src-01](#src-01)`. A deterministic validator checks that every cited key has exactly one source entry, every anchor matches its key, locators are syntactically valid, access dates are present, and unused entries are reported. An agent still judges whether a claim is material and whether the cited source actually supports it.

Cross-document relationships target the `evidence` document, not its external sources. This preserves the interpretive layer: sources support findings, evidence documents synthesize those findings, and briefs or decisions declare reliance on that synthesis.

## Generated graph projection

Initialization should register `.wayfinder/catalog.json` as a wholly generated artifact. It contains no independent facts and is regenerated from the manifest, authored metadata, relationship blocks, and question blocks.

Minimum projection:

```text
schema and generator version
canonical input digest
documents:
  id, path, title, kind, status, updated, summary, module, subject
  supersedes, supersededBy, governedBy, supportedBy
questions:
  id, path, anchor, title, state, raised
  appliesTo, addressedBy, resolvedBy, next-step/revisit summary
```

Entries and edge arrays use deterministic ordering. Detailed source inventories and full bodies are excluded so the catalog remains a routing artifact rather than a shadow copy of the record. Evidence entries expose the evidence document's universal summary, letting a consumer decide whether to open it.

The catalog enables future commands such as “resolve ID,” “show active questions affecting this brief,” “show governing decisions,” and “show evidence supporting this decision” without scanning or loading full documents into model context. The future Use workflow will decide query syntax and context budgets.

## Validation contract

### Deterministic checks

- relationship-block location, delimiters, grammar, canonical ordering, and registered labels;
- target ID/path agreement, containment, uniqueness, existence, kind compatibility, and admissible target status;
- supersession list grammar, reciprocal pairs, type compatibility, and acyclicity;
- question-block containment, project-wide ID/ordinal uniqueness, stable anchors, current state, transition legality, and conditional fields;
- question target IDs, paths, kinds, statuses, and absence of duplicate edges;
- source-key uniqueness, frozen ordering, anchors, required citation fields, locator syntax, access dates, and applicability values;
- local citation references and orphan-source diagnostics;
- generated catalog schema, complete projection, canonical ordering, and input digest; and
- comparison with the canonical baseline for unauthorized ID changes, state regressions, or missing history events.

### Semantic checks

An agent assesses whether `Governed-By` truly governs, `Supported-By` actually supports a material claim, a question's affected scope is complete, its next step is actionable, a resolution answers the original question, source applicability and limitations are candid, and a supersession covers the predecessor's scope. Findings cite the relevant text and never add or remove an edge automatically.

## Options

### Option A: bounded distributed graph, first-class questions, local sources, generated catalog — recommended

Adopt the two ordinary document relations, reciprocal supersession encoding, stable question blocks and lifecycle, document-local source entries, and derived catalog above.

**Benefits:** answers the highest-value authority and evidence queries; preserves unresolved work across sessions; gives sources durable context without a global bibliography; keeps relationship declarations near the claims that own them; enables deterministic integrity checks and low-context routing; avoids duplicating inverse relationships manually.

**Costs and risks:** authors must maintain a small number of explicit edges and question transitions; semantic correctness still needs review; question blocks add custom Markdown grammar; the derived catalog and reciprocal supersession validator require implementation; omitted relation types may later need schema evolution.

**Best fit:** Wayfinder needs trustworthy selective retrieval and maintenance without becoming a full requirements-management database.

### Option B: exhaustive claim-level traceability graph

Give every requirement, claim, assumption, question, option, criterion, decision, source, implementation unit, and test a global ID with typed edges.

**Benefits:** strongest theoretical change-impact analysis; precise claim-to-source lineage; rich compliance and coverage matrices; fewer ambiguous document-level support claims.

**Costs and risks:** very high authoring and migration burden; substantial graph churn during ordinary prose editing; premature formalization; difficult human readability; requires sophisticated tooling and governance; likely to incentivize stale or perfunctory links.

**Best fit:** regulated systems with established traceability staff, formal requirements baselines, and compliance-driven artifact coverage.

### Option C: ordinary Markdown links and free-form registers only

Validate link destinations but derive no typed graph. Open questions remain headings or bullets, and sources use ordinary citations without structured entries.

**Benefits:** maximum authoring freedom; no custom relationship or item grammar; easy manual adoption; lowest implementation cost.

**Costs and risks:** cannot distinguish authority from evidence or casual navigation; question identity breaks during moves and rewording; lifecycle consistency is not mechanically testable; consumers must open more documents; source provenance and applicability drift into inconsistent prose.

**Best fit:** small records maintained by one continuously involved person where selective automated use is unimportant.

### Option D: central authoritative graph and source registry

Store all relationships, question records, and source identities in one JSON or Markdown registry; documents contain only prose links or generated backlinks.

**Benefits:** straightforward querying and global deduplication; one graph schema; easier whole-record visualization; source reuse across evidence documents.

**Costs and risks:** separates relationships from the content that asserts them; ordinary document moves/copies lose context; every content update becomes a coordinated central edit; merge contention concentrates in one file; applicability and use are incorrectly treated as global source properties; reintroduces an independently edited catalog contrary to accepted distributed authority.

**Best fit:** a database-backed service owns all writes and Markdown is only a rendered view.

## Recommendation

Choose **Option A** as one policy bundle:

1. Add one optional relationship block with exact, visible, link-based grammar.
2. Register only `Governed-By` and `Supported-By` as ordinary v1 document edges.
3. Encode `Supersedes` and `Superseded-By` as exact, sorted comma-space ID lists and require reciprocal, acyclic relationships.
4. Give open questions project-wide stable `wfq-...` IDs and explicit anchors while keeping them embedded in a `register` until scale justifies splitting.
5. Use `Open`, `Investigating`, `Deferred`, `Resolved`, and `Retired` states with conditional resumption/resolution content and append-only transition history.
6. Let the question item own `Applies-To`, `Addressed-By`, and `Resolved-By`; generate inverse views.
7. Keep research sources local to each evidence document as frozen `src-NN` entries with citation, original locator, access date, applicability, use, and limitations.
8. Cite local source anchors from material claims; relate briefs and decisions to the evidence document rather than directly to URLs.
9. Generate `.wayfinder/catalog.json` as a small identity/status/summary/edge/question projection for validation and later selective retrieval.
10. Keep deterministic syntax/integrity checks separate from evidence-citing semantic judgments.

This provides enough graph structure to resume work, validate authority, and route future agents while keeping the readable Markdown record primary.

## What acceptance would change now

The runtime `SKILL.md` would record the bounded relationship vocabulary, supersession encoding, question identity/lifecycle, source-reference policy, and generated-catalog role. Detailed runtime schemas should later move into focused `references/` files so an agent loads only the document/item contract it needs.

Acceptance would bring the semantic initialization contract close to implementable. Remaining initialization design would still need exact delimiter/template fixtures, module/subject declaration details, the portable runtime/environment contract, the plan/journal serialization, and an existing-record boundary.

## Deferred decisions

- Exact byte grammar and escaping for relationship, question, source, and history blocks.
- Whether question transition history is stored inline or derived partly from version control.
- Question split/archive thresholds and multiple-register rules.
- Claim-level identity if a later compliance use case justifies it.
- Implementation and test trace edges.
- External-link network checking, caching, redirects, and archived copies; primarily a Validate-workflow concern.
- Catalog JSON schema and query CLI details.
- Context-ranking policy for the Use workflow.
- Relationship migration and extension governance.

## Next decision if Option A is accepted

Define the **initialization schema package and portability contract** as one bundle: exact Markdown/JSON grammars and fixtures, module/subject declarations, template ownership, environment detection, runtime adapters, deterministic command surface, and the operation-plan/journal formats needed to implement and test initialization.

## Sources

1. Gotel, O. C. Z., and Finkelstein, A. C. W. “[An Analysis of the Requirements Traceability Problem](https://doi.org/10.1109/ICRE.1994.292398).” *Proceedings of the First International Conference on Requirements Engineering*, 1994, pp. 94–101.
2. Ramesh, B., and Jarke, M. “[Toward Reference Models for Requirements Traceability](https://doi.org/10.1109/32.895989).” *IEEE Transactions on Software Engineering* 27(1), 2001, pp. 58–93.
3. Winkler, S., and von Pilgrim, J. “[A Survey of Traceability in Requirements Engineering and Model-Driven Development](https://doi.org/10.1007/s10270-009-0145-0).” *Software and Systems Modeling* 9, 2010, pp. 529–565.
4. Conklin, J., and Begeman, M. L. “[gIBIS: A Hypertext Tool for Exploratory Policy Discussion](https://doi.org/10.1145/62266.62278).” *Proceedings of CSCW '88*, 1988, pp. 140–152. A longer version appeared in *ACM Transactions on Office Information Systems* 6(4), 1988, pp. 303–331, [doi:10.1145/58566.59297](https://doi.org/10.1145/58566.59297).
5. MacLean, A., Young, R. M., Bellotti, V. M. E., and Moran, T. P. “[Questions, Options, and Criteria: Elements of Design Space Analysis](https://doi.org/10.1207/s15327051hci0603%264_2).” *Human–Computer Interaction* 6(3–4), 1991, pp. 201–250.
6. Risko, E. F., and Gilbert, S. J. “[Cognitive Offloading](https://doi.org/10.1016/j.tics.2016.07.002).” *Trends in Cognitive Sciences* 20(9), 2016, pp. 676–688.
7. Altmann, E. M., and Trafton, J. G. “[Memory for Goals: An Activation-Based Model](https://doi.org/10.1207/S15516709COG2601_2).” *Cognitive Science* 26(1), 2002, pp. 39–83.
8. Data Citation Synthesis Group. “[Joint Declaration of Data Citation Principles](https://doi.org/10.25490/a97f-egyk).” FORCE11, 2014.
9. Klein, M., Van de Sompel, H., Sanderson, R., Shankar, H., Balakireva, L., Zhou, K., and Tobin, R. “[Scholarly Context Not Found: One in Five Articles Suffers from Reference Rot](https://doi.org/10.1371/journal.pone.0115253).” *PLOS ONE* 9(12), 2014, e115253.
10. W3C. “[PROV-O: The PROV Ontology](https://www.w3.org/TR/prov-o/).” W3C Recommendation, 2013.
11. Pirolli, P., and Card, S. “[Information Foraging](https://doi.org/10.1037/0033-295X.106.4.643).” *Psychological Review* 106(4), 1999, pp. 643–675.
12. Shipman, F. M., and Marshall, C. C. “[Formality Considered Harmful: Experiences, Emerging Themes, and Directions on the Use of Formal Representations in Interactive Systems](https://doi.org/10.1023/A:1008716330212).” *Computer Supported Cooperative Work* 8, 1999, pp. 333–352.
