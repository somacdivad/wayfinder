# Initialization research 02: authoritative kernel representation

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** Where should the authoritative structural metadata for a Wayfinder project record live?
- **Prior decision:** Wayfinder uses a stable semantic kernel plus capability-driven modules.
- **Decision status:** Option C, distributed per-document metadata with generated indexes, accepted by the skill owner on 2026-09-13.

## Executive conclusion

Use **distributed per-document metadata as the source, with deterministic generation of root and module indexes**. Each durable document should carry the small amount of intrinsic metadata needed to identify and route it. A script should traverse those headers, validate the relationships, and generate navigational views or a queryable catalog. Generated views must never become a second editable authority.

This recommendation best balances four competing needs: human-readable Markdown, machine-assisted selective retrieval, consistency, and gradual planning. It also follows an incremental-formalization principle: make only the metadata necessary for a current operation mandatory, have scripts infer safe values where possible, and allow richer relationships to be added as the plan develops.

The evidence does not prove that distributed metadata is universally superior to a central manifest. This is an engineering judgment derived from research on formalization cost, metadata quality, machine actionability, documentation drift, and documentation-as-code. Wayfinder should forward-test it against realistic authoring, rename, retrieval, and merge scenarios.

## Decision boundary

This decision chooses the **location and authority model** of structural metadata. It does not yet choose:

- YAML, JSON, TOML, or a Markdown field block;
- the required fields;
- generated index formatting;
- whether a derived machine-readable cache is committed;
- identifier syntax;
- the script language;
- exact module names.

Separating these questions prevents a preference for a serialization format from silently deciding the larger source-of-truth model.

## Evidence synthesis

### 1. Machine actionability requires explicit semantics

The FAIR principles emphasize metadata that allow computational agents to identify an object's type and intent, judge whether it is relevant to a task, determine whether it is usable, and take an appropriate action.^1 FAIR addresses scientific data, not project plans, but its machine-actionability analysis maps closely to Wayfinder's selective-consumption goal.

Natural-language headings and folder names provide useful cues but do not form a reliable contract for deterministic tools. Explicit document roles, stable identifiers, summaries, authority states, and relationships can let a query script narrow a task to a few files before an agent loads their prose.

**Supported implication:** Markdown-only navigation is valuable for humans but insufficient as Wayfinder's complete machine contract.

**Limit:** adopting a few FAIR-like principles does not make a Wayfinder record FAIR-compliant, nor does Wayfinder need scientific-data metadata richness.

### 2. Formalization has real cognitive and social costs

Shipman and Marshall synthesize experience from interactive knowledge systems where users rejected or circumvented representations that demanded too much explicit structure. They recommend matching formality to users' goals and situations, including incremental and system-assisted formalization.^2

This cautions against requiring an exhaustive manifest or large metadata header at initialization. Early project understanding is incomplete by definition. If Wayfinder requires users or agents to classify every concern, dependency, audience, and lifecycle relationship before they receive value, they may encode guesses as facts or bypass the schema.

**Supported implication:** require a small intrinsic metadata kernel, make later enrichment demand-driven, and have scripts generate repetitive representations.

**Limit:** the paper studies interactive systems broadly and predates contemporary repository workflows and LLM agents.

### 3. Metadata quality must be evaluated in context

Stvilia and colleagues propose an information-quality framework that connects quality dimensions and problem types to the activities the information supports. They validated and refined the framework against Dublin Core records and encyclopedia articles.^3 The relevant lesson is that field presence alone is not quality: metadata must be accurate, internally consistent, appropriately complete, and useful for the actual retrieval or maintenance operation.

For Wayfinder, a central manifest containing stale descriptions would be worse than sparse but trustworthy metadata. Conversely, per-document metadata that is never aggregated would not satisfy efficient collection-level navigation.

**Supported implication:** validation should test operational invariants—unique identity, allowed states, resolvable relationships, index reproducibility, and sufficient routing descriptions—not merely header syntax.

### 4. Documentation drifts regardless of where it is stored

Theunissen, van Heesch, and Avgeriou's systematic mapping study selected 63 studies on documentation in continuous software development. It reports that documentation is often out of sync with software whether it lives near source code or in wiki-like systems, and that teams frequently retain design knowledge informally.^4 Co-location alone therefore does not solve maintenance.

This is important counterevidence to a simplistic argument for per-document metadata. Distributed metadata is preferable only if deterministic validation and generation turn drift into a visible failure. A central manifest is likewise preferable only if documents cannot change without manifest checks.

**Supported implication:** whichever authority model is selected, generated views must be reproducible and validation must detect stale or conflicting derived artifacts.

### 5. Documentation-as-code can combine editable text, embedded formality, generation, and quality gates

Cadavid, Andrikopoulos, and Avgeriou used technical action research to design and evaluate a documentation-as-code pipeline for interface-control documents. Their proof of concept used lightweight text, version control, embedded machine-readable formalism, generated human-readable material, dependency tracking, and quality gates; practitioners and experts reviewed the approach positively while identifying transferability limits.^5

The case is substantially more complex than Wayfinder and relied on custom tooling. Still, it demonstrates a viable pattern: keep formal source close to the document, generate views from it, and validate dependencies rather than manually synchronizing representations.

**Supported implication:** per-document metadata plus generated indexes is technically coherent, but Wayfinder should implement a much smaller dependency-free subset.

### 6. Structured presentation alone is not a sufficient justification

Ernst and Robillard randomly assigned 65 participants to narrative or structured architecture documentation. In their limited context—about 1,000 words describing a comparatively small system—they observed no significant association between format and architecture-understanding performance. Prior familiarity with source code and the type of information sought mattered more.^6

This bounds the case for generated indexes. They should exist to provide navigation, authority cues, and deterministic routing, not because a table or schema automatically makes readers understand the project. Wayfinder's later “use” workflow must still identify the task's actual information need and connect the record to implementation evidence.

**Supported implication:** retain human-authored explanations and task-oriented summaries; do not let generated metadata views replace substantive documents.

### 7. Standards support single sourcing and lifecycle management

ISO/IEC/IEEE 26514 treats information development as a lifecycle activity involving audience analysis, content management, updating, version control, and change control. Its introduction discusses managed reuse and single-source documentation.^7 ISO/IEC/IEEE 15289 defines reusable information-item semantics while allowing projects to combine and subdivide the concrete documents.^8

These standards do not choose central versus distributed metadata. They do support a more general invariant: a piece of maintained information should have an identifiable authority and controlled derivations rather than two independently edited copies.

**Supported implication:** indexes generated from authoritative metadata are safer than separately authored indexes containing the same facts.

## MyPond consistency audit

The current MyPond record intentionally repeats some information:

- A document's title appears in both the document and its collection index.
- Status appears in the document and often in an index table.
- Research indexes summarize unresolved issues also described in the brief.
- Decision indexes restate decision outcomes.

This duplication makes the repository pleasant to browse, but it creates synchronization work. The current convention depends on an editor remembering to update both the leaf and the index. Wayfinder can preserve the same reader experience while generating the duplicated navigational facts from authoritative document metadata.

Not all repetition should be generated. A root knowledge map's explanation of authority, a product brief's synthesis, and a decision record's rationale are distinct authored information products, even when they link to the same subjects. The source-of-truth rule applies to identical structural facts, not every conceptual overlap.

## Options

### Option A: Markdown map as the sole structural authority

The root knowledge map and module indexes are hand-authored Markdown. Individual documents use visible prose metadata only when their template calls for it. Scripts validate links, headings, filename patterns, and known status labels but do not rely on a formal catalog.

**Benefits:** lowest tooling and schema burden; immediately readable; tolerant of early ambiguity; closest to the current MyPond record.

**Costs:** deterministic tools must infer document roles from paths or prose; renamed or unindexed files are hard to distinguish from intentional omissions; selective retrieval depends heavily on an agent interpreting the map; duplicated index facts can drift.

**Failure mode:** the map remains readable while silently ceasing to reflect the record.

**Best fit:** small, human-maintained records where agent retrieval and semantic validation are secondary.

### Option B: central manifest as authority, generated indexes

A machine-readable manifest lists modules and every durable document with its path, role, status, summary, and relationships. Human-facing maps and indexes are generated from the manifest. Documents contain prose and only the metadata needed for standalone readability.

**Benefits:** one cheap file supports selective retrieval; schema validation is straightforward; global ordering and relationships are easy to inspect; module-level operations have a clear transaction boundary.

**Costs:** editing a document and its manifest is a two-file operation; metadata is separated from the content it describes; concurrent changes concentrate merge conflicts; a copied or moved document loses its catalog context; duplicated title or status fields require strict validation.

**Failure mode:** a valid manifest accurately describes yesterday's document set.

**Best fit:** centrally governed collections where most operations already go through a catalog-aware tool.

### Option C: distributed document metadata as authority, generated indexes — recommended

Each durable document carries a compact, machine-readable description of itself. A deterministic script discovers documents, validates metadata and relationships, and generates root/module indexes plus an optional derived query catalog. Collection-level configuration contains only facts that genuinely belong to the collection, such as schema version or enabled modules.

**Benefits:** metadata changes with the content in one reviewable file; moved documents retain identity and role; independently authored modules do not contend on one catalog; generated indexes cannot drift if validation enforces regeneration; the same metadata can support human navigation and selective agent lookup.

**Costs:** every durable document needs a parseable header; the generator must scan the record; cross-document ordering and collection summaries need explicit rules; schema migrations touch many files; manual editing can introduce syntax errors.

**Failure mode:** authors treat the metadata header as boilerplate and preserve syntactically valid but semantically stale descriptions.

**Best fit:** version-controlled, modular records maintained through scripts and reviewed as ordinary repository changes.

## Recommendation

Choose **Option C**, with four safeguards:

1. Keep the initial required metadata very small. Do not require relationships that the project cannot honestly state yet.
2. Generate repeated index facts; never maintain them independently in both metadata and Markdown.
3. Let human-authored narrative surround generated index sections, but give generated regions unmistakable boundaries and overwrite them deterministically.
4. Make validation compare generated output with committed output, failing with a precise regeneration command when they differ.

The generator may later produce both Markdown indexes and a disposable or committed machine catalog. That choice is not part of this decision: the authority remains the per-document metadata either way.

## Next decision if Option C is accepted

Choose the metadata envelope:

- YAML frontmatter;
- a constrained Markdown metadata block like MyPond currently uses;
- JSON sidecars.

That decision should compare human editability, parser complexity, portability, failure clarity, and the behavior of documents copied outside the repository.

## Sources

1. Wilkinson, M. D., et al. “[The FAIR Guiding Principles for Scientific Data Management and Stewardship](https://doi.org/10.1038/sdata.2016.18).” *Scientific Data* 3, 160018, 2016.
2. Shipman, F. M., and Marshall, C. C. “[Formality Considered Harmful: Experiences, Emerging Themes, and Directions on the Use of Formal Representations in Interactive Systems](https://doi.org/10.1023/A:1008716330212).” *Computer Supported Cooperative Work* 8, 1999, pp. 333–352.
3. Stvilia, B., Gasser, L., Twidale, M. B., and Smith, L. C. “[A Framework for Information Quality Assessment](https://doi.org/10.1002/asi.20652).” *Journal of the American Society for Information Science and Technology* 58(12), 2007, pp. 1720–1733.
4. Theunissen, T., van Heesch, U., and Avgeriou, P. “[A Mapping Study on Documentation in Continuous Software Development](https://doi.org/10.1016/j.infsof.2021.106733).” *Information and Software Technology* 142, 2022, 106733.
5. Cadavid, H., Andrikopoulos, V., and Avgeriou, P. “[Improving Hardware/Software Interface Management in Systems of Systems Through Documentation as Code](https://doi.org/10.1007/s10664-023-10350-7).” *Empirical Software Engineering* 28, article 100, 2023.
6. Ernst, N. A., and Robillard, M. P. “[A Study of Documentation for Software Architecture](https://arxiv.org/abs/2305.17286).” 2023 preprint.
7. ISO/IEC/IEEE. “[ISO/IEC/IEEE 26514:2022—Design and Development of Information for Users](https://www.iso.org/standard/77451.html).” 2022.
8. ISO/IEC/IEEE. “[ISO/IEC/IEEE 15289:2019—Content of Life-Cycle Information Items](https://www.iso.org/standard/74909.html).” 2019; reviewed and confirmed 2025.
