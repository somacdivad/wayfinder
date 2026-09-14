# Initialization research 14: document type and lifecycle system

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** What controlled document kinds, lifecycle states, per-kind metadata and content contracts, and authored/generated boundaries should Wayfinder use so that humans and agents can interpret, validate, maintain, and selectively retrieve a project record?
- **Prior decisions:** Every durable document owns the universal `ID`, `Kind`, `Status`, `Updated`, and `Summary` fields. Topic taxonomy is selected separately through modules and subjects. Indexes are deterministic derivations, and initialization publishes a reviewed, attributable, uncertainty-aware record.
- **Decision status:** Option A, a closed purpose-based kind registry with kind-specific lifecycle profiles and explicitly derived navigation, accepted by the skill owner on 2026-09-13.

## Executive conclusion

Prefer **Option A: a closed, purpose-based core kind registry with kind-specific lifecycle profiles and explicitly derived navigation**.

`Kind` should identify a document's communicative job, not its product area or folder. Version 1 should provide seven authored kinds: `map`, `brief`, `register`, `evidence`, `decision`, `guide`, and `index`. Module and subject answer “what is this about?”; `Kind` answers “how should I read and trust it?” Keeping those facets separate avoids a combinatorial vocabulary such as `product-brief`, `architecture-brief`, `security-decision`, and `research-index`.

Each kind should have a versioned application profile declaring its purpose, admissible statuses, conditional metadata, required content roles, initialization eligibility, and validation rules. Living knowledge uses `Draft`, `Active`, `Superseded`, and `Retired`; decisions use `Proposed`, `Accepted`, `Rejected`, and `Superseded`. `Status` expresses authority/lifecycle, not completeness or evidentiary confidence. A document may be `Active` while honestly containing open questions.

Generated navigation should not masquerade as authored authority. Entirely generated artifacts are disposable manifest-listed outputs without durable document identity. An authored `map` or `index` may contain a precisely delimited generated region; prose outside the region remains authoritative, while the region is a reproducible materialized view. Validators should recompute generated content and report drift, and generators should modify only declared generated paths or regions.

This is a design synthesis. Organizational-genre research supports classifying recurrent documents by communicative purpose and form; faceted classification supports separating independent dimensions; metadata application-profile practice supports controlled vocabularies and per-type constraints; structured-authoring standards demonstrate the benefits and costs of specialized information types; formal state/workflow models support explicit transitions; and provenance/view-maintenance research supports treating generated outputs as derivations. No reviewed study compares these exact seven kinds or lifecycle labels for an LLM-maintained Markdown project record.

Sources were accessed on 2026-09-13.

## Local case: what MyPond already distinguishes

The MyPond record contains recurring communicative roles even though it does not yet label them as kinds:

| Existing document pattern | Communicative job | Proposed kind |
| --- | --- | --- |
| Root `docs/README.md` | Explain authority, lifecycle, major knowledge areas, and routing. | `map` |
| Product brief and focused product documents | Synthesize the current maintained understanding of a subject. | `brief` |
| Product open questions | Maintain unresolved questions that require evidence or a decision. | `register` |
| Dated research briefs | Preserve evidence, provenance, limitations, inference, and implications. | `evidence` |
| Numbered decision records | Preserve a consequential choice, context, alternatives, rationale, and consequences. | `decision` |
| Development environment | Tell builders how to work under current constraints. | `guide` |
| Research, decisions, and architecture `README.md` files | State a collection's scope and route readers to members. | `index` |

This mapping preserves the existing hierarchy while replacing path-based inference with explicit semantics. The same `brief` kind can appear in product, architecture, policy, or a local module; its module and subject preserve topical meaning.

## Evidence synthesis

### 1. Document types are recurrent communicative actions, not merely file formats

Yates and Orlikowski define organizational communication genres as typified communicative actions with similar substance and form arising in recurrent situations.^1 The theory is descriptive and predates repository-based planning and LLM agents, but its core distinction is directly useful: a decision record and research brief differ because they accomplish different social actions, even when both are Markdown files about the same feature.

**Implication:** define `Kind` by purpose, authority, expected content, and lifecycle. Do not make `Kind` repeat the module, subject, file extension, or filename.

### 2. Separate independent classification facets

Faceted-classification theory constructs knowledge organization systems from independently combinable characteristics instead of enumerating every compound category. Broughton describes facets alongside hierarchies and other semantic relationships as fundamental structures for knowledge organization.^2

**Implication:** keep communicative kind, topical module/subject, lifecycle status, and document identity as separate axes. A single `architecture-decision-superseded` class would entangle four properties and expand badly as profiles and local modules grow.

### 3. Application profiles reconcile a small shared core with type-specific rules

Dublin Core application-profile guidance defines profiles as declarations of which metadata terms an application uses and how they are constrained. The guidance recommends explicit obligations, cardinalities, value constraints, and controlled vocabularies, while preserving a common semantic base.^3 DCMI also notes that controlled values improve precision for machine processing.^4

**Implication:** give every Wayfinder kind a declared profile layered over the five universal fields. Unknown fields and values fail validation instead of being guessed. Profiles should be versioned with the record schema and readable by both humans and validators.

### 4. Information typing improves consistency, but specialization can become costly

OASIS DITA distinguishes information types such as concept, task, and reference according to reader questions and supplies shared structure plus specialization. The standard prefers typed content when a fitting type exists, while retaining a generic topic when specialization is inappropriate.^5 DITA is an XML technical-documentation system, not evidence that Wayfinder should copy its vocabulary or rigidity.

**Implication:** use a small set of tested kinds with reusable writing/validation contracts. Avoid either one undifferentiated type or a separate type for every project topic. Unlike DITA, v1 should not permit project-local kind specialization because Wayfinder consumers need stable cross-project meanings.

### 5. Formalization should remain proportional to the task

Shipman and Marshall found that users may resist or circumvent systems that force tacit and situational work into premature formal representations. They recommend incremental, system-assisted formalization.^6 Stvilia and colleagues likewise frame information quality in relation to the activities information supports rather than simple field completeness.^7

**Implication:** make only machine-actionable metadata structured. Put rich explanation in readable Markdown. A content profile states the questions a good document must answer; deterministic validation checks what syntax and relationships can prove, while semantic validation reports evidenced concerns without pretending a heading guarantees quality.

### 6. Lifecycle values need explicit, type-valid transitions

Harel's statecharts and later workflow-pattern research show the value of representing admissible states and transitions explicitly rather than as informal labels.^8,9 ISO 15489 addresses controls and processes for creating, capturing, and managing records over time.^10 These works do not prescribe Wayfinder's state names, but they support treating status as a constrained transition system.

**Implication:** define two small lifecycle families, transition preconditions, terminal states, and invalid transitions. Do not allow an arbitrary status string or assume all kinds share the same approval semantics.

### 7. Decision records need a distinct governance lifecycle and content contract

Van Heesch, Avgeriou, and Hilliard's architecture-decision documentation framework identifies distinct stakeholder concerns around decision detail, relationships, chronology, and involvement, and reports an industrial case evaluation for most of its viewpoints.^11 The result is specific to architecture decisions but supports the broader distinction between current explanatory prose and a record that preserves why an authoritative choice was made.

**Implication:** `decision` has `Proposed`/`Accepted`/`Rejected`/`Superseded` states and requires context, options, choice or resolution, rationale, consequences, and relationships. An accepted decision is not silently rewritten into a different outcome; a later decision supersedes it.

### 8. Generated navigation is a derived view, not another source of truth

W3C PROV distinguishes entities, activities, agents, generation, and derivation, providing a vocabulary for provenance chains.^12 Database research treats a materialized view as derived data whose maintenance depends on its base data and view definition.^13

**Implication:** generated catalogs and navigation lists must identify their generator/schema and input digest, be reproducible from authoritative metadata, and be safe to delete and rebuild. Authored prose and generated bytes need an explicit boundary so neither humans nor tools edit the other's authority accidentally.

### 9. Architecture concerns remain topical, not new universal document kinds

ISO/IEC/IEEE 42010 separates an entity's architecture from its architecture description and defines architecture viewpoints and model kinds around stakeholder concerns.^14 Wayfinder need not implement that standard, but the separation warns against declaring one universal `architecture-document` shape for every technical concern.

**Implication:** architecture remains a module/subject facet. Use `brief` for current architectural synthesis, `decision` for consequential choices, `evidence` for investigations, and `guide` for operational instructions. Add a future kind only when its communicative and validation behavior genuinely differs.

## Proposed kind registry

All seven values are lowercase ASCII and closed under schema version 1. A local module must use them; adding a new kind requires a Wayfinder schema revision with migration and consumer support.

| Kind | Primary question answered | Authority behavior | Typical examples |
| --- | --- | --- | --- |
| `map` | How is this record organized and interpreted? | Authoritative for record-level scope, authority rules, lifecycle explanation, and top-level navigation. | Root knowledge map. |
| `brief` | What is the current maintained understanding of this subject? | Mutable current synthesis; points to evidence, questions, and decisions instead of replacing them. | Plan brief, product subject brief, architecture overview. |
| `register` | Which governed items are unresolved or being tracked? | Authoritative collection of typed live items and their resolution state; an empty state must state its basis. | Open-question register. |
| `evidence` | What was investigated, what supports the findings, and how applicable is it? | Preserves sources, method, findings, limitations, uncertainty, and implications; does not itself establish requirements. | Research brief, experiment report, interview synthesis. |
| `decision` | What consequential choice was proposed or resolved, why, and with what consequences? | Governance history; accepted outcomes remain historically stable and are changed through supersession. | Product, architecture, workflow, or policy decision record. |
| `guide` | What should a reader do, under which prerequisites and constraints? | Maintained normative or procedural guidance subordinate to accepted decisions. | Development workflow, setup, release or operational guidance. |
| `index` | What collection does this entrypoint govern, and where are its members? | Authored authority for collection scope and inclusion/ordering rules; member listings may be generated. | Research, decisions, architecture, development, or local-module index. |

### Selection test

Choose the kind from the document's dominant communicative responsibility:

1. If it governs the whole record's interpretation, use `map`.
2. If it records a consequential choice and rationale, use `decision`.
3. If its claims depend on explicit research or observation, use `evidence`.
4. If it governs tracked items, use `register`.
5. If it instructs action, use `guide`.
6. If it governs a collection and routes to members, use `index`.
7. Otherwise, if it synthesizes current understanding of one subject, use `brief`.

If two responsibilities are both substantial, split the document or make one role clearly primary and link to a separate authority. Do not select a kind from the filename alone.

## Proposed lifecycle profiles

### Living-knowledge family

Applies to `map`, `brief`, `register`, `evidence`, `guide`, and `index`.

| Status | Meaning |
| --- | --- |
| `Draft` | Work in progress; informative but not the current authoritative reference. |
| `Active` | Current maintained reference for its declared scope, even if uncertainty is explicitly present. |
| `Superseded` | Historical record replaced by one or more identified durable documents. |
| `Retired` | Historical record intentionally withdrawn without a direct replacement. |

Normal transitions:

```text
Draft ──► Active ──► Superseded
  │          └────► Retired
  └───────────────► Retired
```

A reviewed initialization or update may create a document directly as `Active`; the proposal confirmation supplies the promotion gate. `Superseded` requires `Superseded-By`. `Retired` requires a recorded reason in the body. `Superseded` and `Retired` are terminal under ordinary workflows. A correction of lifecycle metadata is a separately reported repair, not an unrecorded backward transition.

### Decision family

Applies only to `decision`.

| Status | Meaning |
| --- | --- |
| `Proposed` | A concrete choice is under consideration and has no governing authority. |
| `Accepted` | The identified decision authority approved the outcome; it governs within its stated scope. |
| `Rejected` | The proposal was explicitly declined; it remains historical context but never governed. |
| `Superseded` | A formerly accepted decision was replaced by one or more identified decisions. |

Normal transitions:

```text
Proposed ──► Accepted ──► Superseded
    └─────► Rejected
```

Initialization may create a decision directly as `Accepted` only when acceptance and authority are explicit in the reviewed inputs. Rejected alternatives can ordinarily remain inside an accepted decision; create a `Rejected` record only when a separately proposed decision needs durable history. `Accepted`, `Rejected`, and `Superseded` outcomes are not rewritten. Reversing or retiring an accepted decision requires a new accepted decision that supersedes it.

### Cross-cutting rules

- `Status` is not a completeness score, confidence level, work priority, implementation state, or freshness guarantee.
- Exactly one `Active` living document should own a declared singleton scope. Multiple active documents may coexist only when their scopes are non-overlapping.
- A `Draft` cannot be the target of a link claiming current authority.
- A supersession transition is bidirectionally linked and cycle-free.
- Status comparisons are exact and case-sensitive in machine processing.
- Historical content may receive narrowly labeled correction notes and repaired links, but its original conclusion or accepted outcome is preserved. Exact update rules remain for the Update workflow.

## Proposed per-kind metadata profile

Every authored kind requires the accepted five universal fields. Version 1 adds only fields that deterministic lifecycle or ordering behavior consumes:

| Field | Applies to | Obligation and value |
| --- | --- | --- |
| `Decision-Date` | `decision` | Required for `Accepted` and `Rejected`; forbidden for `Proposed`; preserved when later superseded. Exact `YYYY-MM-DD`. |
| `Supersedes` | Any authored kind | Optional one-or-more list of Wayfinder document IDs. Each target must exist, be type-compatible, and link back after application. |
| `Superseded-By` | Any authored kind | Required when `Status` is `Superseded`; one-or-more Wayfinder document IDs. Each target must exist and link back. |

The exact single-line list encoding belongs to the metadata grammar implementation, but it must be unambiguous and restricted to valid Wayfinder IDs. No project-defined metadata fields are accepted in version 1. Rich provenance, stakeholders, ownership, confidence, applicability, and rationale stay in the appropriate body sections until a cross-workflow machine use justifies another field.

## Proposed content profiles

These are semantic contracts. Templates may provide recommended headings, but only kinds with stable record structures require exact section headings in version 1.

### `map`

Must explain purpose/scope, source-of-truth and authority rules, lifecycle meanings, enabled module map, navigation strategy, and how to continue planning. A deterministic validator can prove that every manifest module entrypoint is linked; an agent validates clarity and boundary consistency.

### `brief`

Must state its scope, current synthesis, known boundaries/constraints, and links to governing decisions, supporting evidence, and unresolved questions when they exist. Subject-specific headings remain flexible so the brief can reflect the domain instead of becoming generic boilerplate.

### `register`

Must define the registered item type and item state rules, then list live items or an evidenced empty state. Each open item states why it matters and the next resolution step when known. Exact item syntax and item IDs remain a subsequent design decision.

### `evidence`

Requires these semantic sections, using exact template headings once finalized: question/scope; method and source inventory with access dates; findings; applicability and limitations; evidence/inference/hypothesis separation; implications; unknowns; and next validation. A validator checks required sections, source-link syntax, and dates; an agent assesses whether claims and caveats are supported.

### `decision`

Requires exact sections for context; options considered; decision or resolution; rationale; consequences; references; and supersession. `Accepted` records require a precise outcome and identified decision authority. `Rejected` records require the rejected proposal and rejection rationale. A validator checks headings, lifecycle metadata, and reciprocal supersession; an agent checks whether the choice and tradeoffs are intelligible.

### `guide`

Must identify audience/purpose, prerequisites and constraints, actionable instructions or rules, verification where applicable, and unresolved conditions. Commands must be evidenced by the project rather than invented. Subject-specific organization remains flexible.

### `index`

Must state collection scope, authority, membership rule, ordering rule, and empty-state behavior. Member navigation belongs in a declared generated region unless the membership cannot be derived from authoritative metadata. Explanatory prose remains outside that region.

## Authored and generated boundary

### Authored durable documents

- Carry a Wayfinder metadata block and stable document ID.
- Are not listed as wholly generated artifacts in the manifest.
- May be edited only through a workflow that respects their kind and status.
- May contain declared generated regions where the kind profile permits them.

### Generated regions

- Use exact, nest-free start/end delimiters containing a registered region name, generator/schema version, and input digest.
- Are derived only from authoritative metadata/content under a documented ordering rule.
- Are replaced as whole regions by deterministic tooling; generators never edit bytes outside the delimiters.
- Are validated by recomputation. A mismatch is `stale-generated-content`, not an invitation to accept the edited bytes.
- Cannot introduce a fact or relationship absent from an authoritative source.

### Wholly generated artifacts

- Are enumerated exactly in `manifest.generatedArtifacts` and carry a generated-file marker with generator/schema version and input digest.
- Do not receive a Wayfinder document ID or authoritative `Status` because they are disposable projections, not durable knowledge objects.
- Must be reproducible, safe to delete and rebuild, and must not be the sole target of an authoritative relationship.
- Are never edited manually. A validator distinguishes them by the manifest and marker, not by folder name.

The root `map` and all `index` documents are authored shells. Their authority/lifecycle prose remains human-maintained, while repeated member tables or link lists should be generated. This reproduces MyPond's readable entrypoints while eliminating independently maintained navigation facts.

## Validation boundary

### Deterministic checks

- exact registered `Kind` and kind-valid `Status`;
- required/forbidden conditional fields and value grammar;
- valid state transition against the canonical baseline;
- singleton-scope conflicts where the manifest/profile declares a singleton;
- required exact sections for `evidence` and `decision`;
- internal link existence and typed relationship compatibility;
- reciprocal, acyclic supersession;
- manifest entrypoint/kind agreement;
- generated path/region ownership, marker validity, digest, ordering, and recomputed bytes; and
- prohibition on project-local kinds or unknown metadata fields.

### Semantic checks

An agent assesses whether the selected kind matches the document's dominant purpose, required content roles are substantively answered, claims retain their uncertainty and sources, guidance does not outrun decisions, current briefs do not contradict accepted decisions, and indexes describe their collections accurately. Semantic findings cite exact passages and never auto-reclassify or rewrite documents without user confirmation.

## Options

### Option A: closed purpose-based kinds, lifecycle profiles, and derived navigation — recommended

Adopt the seven-kind registry, two status families, minimal conditional fields, semantic content profiles, and authored/generated boundary above.

**Benefits:** stable meanings across projects; module and kind remain independent; validation and selective retrieval can act on explicit roles; lifecycle authority is clear; local modules remain interoperable; generated listings cannot silently become a second authority; preserves MyPond-like flexible prose.

**Costs and risks:** seven kinds and two lifecycle families require learning; borderline documents may need splitting or judgment; custom domains cannot add kinds locally; semantic content quality still needs agent/human review; generated-region tooling is additional implementation work.

**Best fit:** Wayfinder should support varied project domains while preserving one consumable, testable record model.

### Option B: module-specific kinds and lifecycles

Define kinds such as `product-brief`, `architecture-overview`, `development-guide`, `research-index`, and `architecture-decision`, with each module owning its states and fields.

**Benefits:** highly precise templates and validation; terminology can match each discipline; fewer ambiguous selections inside one module.

**Costs and risks:** combinatorial vocabulary growth; duplicate semantics drift apart; local modules require new consumer logic; cross-project retrieval becomes harder; moving knowledge between modules may require a kind and lifecycle migration even when its communicative role is unchanged.

**Best fit:** Wayfinder supports one tightly controlled domain whose module set is unlikely to grow.

### Option C: small generic kinds with open tags and advisory schemas

Use broad values such as `document`, `record`, and `index`; allow projects to add free-form tags and treat content profiles as optional guidance.

**Benefits:** lowest classification burden; easy adoption of existing documents; almost any content fits without migration.

**Costs and risks:** `Kind` provides little routing or authority information; tags acquire undeclared meanings; validators cannot reliably choose rules; agents must open more files to understand them; inconsistencies become conversational judgments rather than detectable contract violations.

**Best fit:** Wayfinder is primarily a loose personal knowledge base and deterministic cross-project consumption is unimportant.

### Option D: project-extensible kind registry

Ship core kinds but allow each project to declare `local-<kind>` profiles, fields, statuses, templates, and validators in its manifest.

**Benefits:** maximum domain fit; specialized records can express their actual lifecycle; projects need not wait for Wayfinder releases.

**Costs and risks:** every record can become a new schema language; runtime agents must load and interpret local type definitions; safe validation needs executable or declarative extension machinery; malicious or inconsistent schemas expand the trust boundary; selective retrieval loses stable semantics.

**Best fit:** mature organizations have dedicated information architects and are willing to maintain custom schema tooling.

## Recommendation

Choose **Option A** as one policy bundle:

1. Make `Kind` a communicative-purpose facet independent of module and subject.
2. Register exactly `map`, `brief`, `register`, `evidence`, `decision`, `guide`, and `index` for schema version 1.
3. Forbid project-local kinds in v1; local modules compose the core kinds.
4. Use `Draft`/`Active`/`Superseded`/`Retired` for living knowledge and `Proposed`/`Accepted`/`Rejected`/`Superseded` for decisions.
5. Treat status as authority/lifecycle, never confidence or completeness.
6. Enforce explicit forward transitions, reciprocal supersession, and status-kind compatibility.
7. Add only `Decision-Date`, `Supersedes`, and `Superseded-By` as conditional v1 metadata.
8. Apply the per-kind content profiles above, with exact section schemas only where stable structure makes deterministic validation worthwhile.
9. Keep authored shells authoritative and generated regions replaceable; treat wholly generated artifacts as identity-free disposable projections.
10. Divide validation honestly between deterministic contract checks and evidence-citing semantic review.

This decision is broad enough to turn the previously accepted universal metadata into an interpretable document system while leaving item-level schemas, source syntax, relation encoding, and script runtime mechanics for later decisions.

## What acceptance would change now

The runtime `SKILL.md` would record the kind registry, status families, key transitions, minimal conditional fields, content-profile routing, and generated-content authority boundary. A runtime reference would eventually hold the full per-kind schema so ordinary agents load only the profile needed for the document they are creating or updating.

Acceptance would not yet make initialization runnable. Before templates and validators can be implemented, Wayfinder still needs exact item and relationship grammar—especially open-question items, source/provenance entries, typed links, and supersession lists.

## Deferred decisions

- Exact metadata list encoding for `Supersedes` and `Superseded-By`.
- Open-question item IDs, statuses, fields, and transition rules.
- Source/provenance and evidence-strength representation.
- Typed cross-document relationship vocabulary and Markdown syntax.
- Exact template headings and generated-region delimiter grammar.
- Module/subject declaration format outside the root manifest.
- Extension/migration procedure for a future core kind.
- Update-workflow permissions for historical correction notes.
- Runtime schema representation and validator implementation language.
- Existing-record adoption and kind inference.

## Next decision if Option A is accepted

Define the **relationship and tracked-item system** as one bundle: typed cross-document links, supersession list grammar, open-question item identity and lifecycle, evidence/source references, and the deterministic checks that connect briefs, questions, evidence, and decisions without forcing agents to load every document.

## Sources

1. Yates, J., and Orlikowski, W. J. “[Genres of Organizational Communication: A Structurational Approach to Studying Communication and Media](https://doi.org/10.5465/amr.1992.4279545).” *Academy of Management Review* 17(2), 1992, pp. 299–326.
2. Broughton, V. “[Faceted Classification as a General Theory for Knowledge Organization](https://doi.org/10.17821/srels/2013/v50i6/43823).” *SRELS Journal of Information Management* 50(6), 2013, pp. 735–750.
3. Baker, T., Dekkers, M., Fischer, T., and Heery, R. “[Dublin Core Application Profile Guidelines](https://www.dublincore.org/specifications/dublin-core/application-profile-guidelines/).” Dublin Core Metadata Initiative, 2005.
4. Coyle, K., and Baker, T. “[Guidelines for Dublin Core Application Profiles](https://www.dublincore.org/specifications/dublin-core/profile-guidelines/).” Dublin Core Metadata Initiative, 2009.
5. OASIS. “[Darwin Information Typing Architecture (DITA) Version 1.3, Part 1: Base Edition](https://docs.oasis-open.org/dita/dita/v1.3/cos01/part1-base/dita-v1.3-cos01-part1-base.pdf).” Committee Specification 01, 2015.
6. Shipman, F. M., and Marshall, C. C. “[Formality Considered Harmful: Experiences, Emerging Themes, and Directions on the Use of Formal Representations in Interactive Systems](https://doi.org/10.1023/A:1008716330212).” *Computer Supported Cooperative Work* 8, 1999, pp. 333–352.
7. Stvilia, B., Gasser, L., Twidale, M. B., and Smith, L. C. “[A Framework for Information Quality Assessment](https://doi.org/10.1002/asi.20652).” *Journal of the American Society for Information Science and Technology* 58(12), 2007, pp. 1720–1733.
8. Harel, D. “[Statecharts: A Visual Formalism for Complex Systems](https://doi.org/10.1016/0167-6423(87)90035-9).” *Science of Computer Programming* 8(3), 1987, pp. 231–274.
9. van der Aalst, W. M. P., ter Hofstede, A. H. M., Kiepuszewski, B., and Barros, A. P. “[Workflow Patterns](https://doi.org/10.1023/A:1022883727209).” *Distributed and Parallel Databases* 14(1), 2003, pp. 5–51.
10. ISO. “[ISO 15489-1:2016—Information and Documentation: Records Management: Concepts and Principles](https://www.iso.org/standard/62542.html).” 2016; reviewed and confirmed 2021.
11. van Heesch, U., Avgeriou, P., and Hilliard, R. “[A Documentation Framework for Architecture Decisions](https://doi.org/10.1016/j.jss.2011.10.017).” *Journal of Systems and Software* 85(4), 2012, pp. 795–820.
12. W3C. “[PROV-O: The PROV Ontology](https://www.w3.org/TR/prov-o/).” W3C Recommendation, 2013.
13. Gupta, A., and Mumick, I. S. “[Maintenance of Materialized Views: Problems, Techniques, and Applications](https://www.sigmod.org/publications/dblp/db/journals/debu/GuptaM95.html).” *IEEE Data Engineering Bulletin* 18(2), 1995, pp. 3–18.
14. ISO/IEC/IEEE. “[ISO/IEC/IEEE 42010:2022—Software, Systems and Enterprise: Architecture Description](https://www.iso.org/standard/74393.html).” 2022.
