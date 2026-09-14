# Initialization research 01: invariant structure versus adaptation

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** Should initialization reproduce one fixed MyPond-like tree, create a stable semantic kernel plus selected modules, or let each project define its own structure?
- **Decision status:** Option B, semantic kernel plus capability-driven modules, accepted by the skill owner on 2026-09-13.

## Executive conclusion

The strongest design is a **stable semantic kernel with capability-driven modules**. Wayfinder should standardize how readers enter and interpret a project record—one map, explicit authority and lifecycle rules, distinct evidence/current-state/decision roles, indexed collections, and visible open questions—while generating only the subject modules justified by the project's type and current needs.

This conclusion is a synthesis, not a direct experimental result. Human-factors research supports visible hierarchical structure, small guided steps, and external representations that reduce memory work. Personal-information-management studies also show that project folders carry useful meaning, while strict hierarchies become overloaded when information has several legitimate classifications. Systems and software documentation standards deliberately specify information roles and relationships while allowing projects to combine or subdivide concrete documents. Together, this argues for fixed semantics and navigation contracts without fixing every folder forever.

## Scope and limitations

The evidence spans cognitive psychology, information architecture, personal information management, software documentation, requirements engineering, and architecture description. None of the reviewed studies directly tests an LLM skill that generates repository planning records. Human navigation studies are therefore **adjacent evidence** for agent navigation, not proof of agent performance.

Standards establish mature professional conventions but are not controlled evidence that a particular Markdown tree is optimal. The MyPond repository is one rich local case, not a representative sample. Wayfinder should treat the recommended structure as a testable design and later evaluate it with realistic initialization and retrieval tasks.

Sources were accessed on 2026-09-13.

## Local case: what the MyPond structure accomplishes

The current MyPond record implements several separable functions:

| Function | Current realization | Why it matters |
| --- | --- | --- |
| Orientation | `docs/README.md` knowledge map | Gives readers one stable entry point and explains where information belongs. |
| Current product state | `docs/product/product-brief.md` plus focused subject documents | Keeps a concise synthesis separate from detail. |
| Evidence | Dated research briefs and an index | Preserves sources, applicability, uncertainty, and validation needs without silently creating requirements. |
| Authority and history | Globally numbered decision records grouped by subject | Records accepted outcomes and rationale without rewriting history. |
| Technical view | Architecture and development entry points | Connects implementation guidance to governing decisions. |
| Consistency | Templates, statuses, dates, relative links, and folder indexes | Makes conventions inspectable and partially machine-checkable. |

Decision 0032 documents why the repository moved from flat or monolithic organization to shallow subject folders and layered indexes: growth had made scanning harder, while deep taxonomies and classification-dependent identifiers would create navigation and migration costs. This is direct evidence about MyPond's current needs, but it does not establish that every new project begins with the same subjects.

## Evidence synthesis

### 1. External structure changes the cognitive task

Zhang and Norman's distributed-representation framework treats cognition as jointly performed by internal and external representations. Their experiments analyze a hierarchical task by decomposing its levels and show that representation affects the operations a solver must perform.^1 Applied cautiously, a visible project map, explicit document roles, and status metadata do more than store prose: they externalize distinctions an author or reader would otherwise need to remember.

**Implication:** initialization should create an explicit interpretive structure, not merely empty folders. The structure should expose the record's authority model and navigation paths.

**Limit:** the experiments used the Tower of Hanoi, not documentation repositories or language models.

### 2. Guidance is most valuable while the schema is unfamiliar

Chen, Kalyuga, and Sweller report that useful instructional guidance depends on element interactivity. Their cognitive-load account explains why worked examples can outperform unguided problem solving for novices, while generation can help in other conditions.^2 A new project record requires simultaneous reasoning about audiences, evidence, decisions, architecture, open questions, and document placement. A blank-slate initializer therefore imposes avoidable search and coordination load.

**Implication:** Wayfinder should supply a recognizable starting schema and staged choices. It should not ask the user to invent the taxonomy, naming rules, metadata, and authority relations at once.

**Limit:** this is instructional-learning research. Applying it to assisted project planning is an inference.

### 3. Project folders represent understanding, not only storage

Jones and colleagues observed that people's folders for projects often resembled a divide-and-conquer decomposition of the work. Folder structures represented participants' evolving understanding of a project and its components, not just locations for later retrieval.^3 This supports using subject folders as meaningful views into the plan.

The same work also identifies a limitation: a strict hierarchy gives an item only one natural home and becomes awkward for material with several independent properties.^3 Requirements can relate simultaneously to an audience, workflow, architectural component, risk, and decision. A deep universal taxonomy would encode one contestable interpretation as if it were intrinsic.

**Implication:** preserve a shallow primary home for each canonical item and use links, indexes, stable identifiers, or explicit relationships for cross-cutting meaning.

**Limit:** the study examined personal project information and was a late-breaking CHI report, not a comparative trial of software-project knowledge bases.

### 4. Familiar hierarchy supports re-finding, but taxonomy is not sufficient

Bergman and colleagues found a strong preference for folder navigation across two studies: participants estimated that navigation handled 56–68% of personal-file retrievals, compared with 4–15% for search. Improved search produced limited and inconsistent changes in this preference.^4 This argues against replacing navigable hierarchy with an opaque search- or embedding-only store.

Pak, Pautz, and Iden experimentally compared hierarchical taxonomy and tagging. Participants experienced greater frustration during organization with tagging; the broader results show tradeoffs rather than a universal winner.^5 The important design lesson is not “folders always win,” but that deterministic primary placement reduces authoring ambiguity while secondary relationships can compensate for hierarchy's limits.

**Implication:** every generated record should be browsable from stable indexes. Tags or machine metadata may supplement that path later, but should not be the only organization mechanism.

**Limits:** these studies concern human personal-information behavior, and reported usage preferences do not by themselves establish accuracy or efficiency for agents.

### 5. User-derived categories evolve

Kumpulainen and Kärkkäinen used card sorting to evaluate a health-protocol website one year after launch. The original user-derived categories remained broadly robust, but new categories emerged from actual search queries; the authors recommend recurrent evaluation of structure as information needs evolve.^6

**Implication:** initialization should offer a tested default and an explicit extension rule. Validation and update workflows should detect growing or incoherent indexes and propose a structural decision rather than allowing silent sprawl.

**Limit:** this was a website study with healthcare workers and the public, not a repository study.

### 6. Standards prescribe semantics while allowing project tailoring

ISO/IEC/IEEE 15289 defines generic life-cycle information-item types and explicitly allows information items to be combined or subdivided for project or organizational purposes.^7 ISO/IEC/IEEE 26514 defines information architecture as both the structure of an information space and the semantics for accessing task, function, and other information; it covers audience analysis, content management, maintenance, version control, and change control.^8

ISO/IEC/IEEE 42010 avoids prescribing one architecture-document format. It instead standardizes concepts and relationships such as stakeholders, concerns, viewpoints, and views.^9 ISO/IEC/IEEE 29148 similarly defines requirements management as identifying, documenting, maintaining, communicating, tracing, and tracking requirements through the lifecycle; it distinguishes validation of whether the requirements describe the intended system from mere document completion.^10

**Implication:** Wayfinder should define stable semantic roles and integrity rules, then allow concrete documents to be combined, split, or omitted according to project concerns. “All folders exist” is a weak completion criterion; coverage, traceability, and stakeholder fit are stronger criteria.

**Limit:** these standards are broader and often more formal than a small product repository needs. Wayfinder should borrow principles, not claim full standards conformance.

### 7. Modular context has emerging support for LLM use

Knoll organizes external knowledge into modules selected for particular prompts. In a public deployment and a 100-query evaluation, annotators preferred module-augmented responses when external knowledge was needed, while the authors also observed that models can over-rely on related but unnecessary context.^11

**Implication:** a modular record with explicit summaries and boundaries is compatible with Wayfinder's future selective-consumption workflow. The initializer should avoid a single monolithic plan that forces every task to load everything.

**Limit:** Knoll is a recent system study, not a comparison of repository folder schemes, and its evaluation does not validate Wayfinder's proposed module boundaries.

## Design requirements supported by the evidence

The research supports the following requirements at moderate confidence:

1. Create one stable, human- and agent-readable entry point.
2. Externalize authority, lifecycle, and document-role distinctions.
3. Provide a guided starting schema rather than a blank directory.
4. Keep the primary hierarchy shallow and navigable through indexes.
5. Give each canonical fact or decision one primary home; represent cross-cutting relationships with links and stable identifiers.
6. Permit modules and documents to be added, split, or combined when stakeholder concerns justify it.
7. Initialize only honest content and visible unknowns; do not use empty sections as evidence that planning is complete.
8. Preserve a future path for selective context loading.

The evidence does **not** determine exact folder names, whether a manifest should be JSON or Markdown, which modules are mandatory for every project, or how much content the initializer should elicit before writing files. Those are subsequent decisions.

## Options

### Option A: fixed Wayfinder blueprint

Every project receives the MyPond topology: `product/`, `research/`, `decisions/`, `architecture/`, `development/`, and `templates/`, with the same entry points and metadata.

**Implementation:** one deterministic scaffold script copies a fixed tree. Validation asserts every path and heading exists. Interviewing fills the predefined documents.

**Benefits:** simplest to explain, script, validate, and test; provides the strongest worked example; gives consuming agents identical paths in every repository.

**Costs and risks:** assumes every project has the same concerns; creates empty or ceremonial documents; encourages agents to force cross-cutting material into one category; makes future non-software or differently governed projects second-class.

**Best fit:** Wayfinder is intentionally limited to early-stage software-product plans closely resembling MyPond.

### Option B: semantic kernel plus capability modules

Every record obeys a small semantic and navigation contract. Initialization then selects a profile and only the modules justified by the project's concerns. A software-product profile can reproduce the useful MyPond shape without declaring it universal.

**Invariant kernel:** stable record entry point, authority/lifecycle explanation, indexed collections, open-question visibility, relative internal links, and an explicit distinction among evidence, current synthesis, and accepted decisions.

**Selectable modules:** product, research, decisions, architecture, development, operations, policy, or future domain-specific modules. Module indexes follow a common contract; their internal subject folders emerge only when content volume or distinct stakeholder concerns justify them.

**Implementation:** a deterministic initializer accepts an explicit profile and module set, writes a planned file manifest, refuses to overwrite existing content, and validates the generated topology. The interview recommends modules from stakeholder concerns but shows the selection before writing.

**Benefits:** preserves predictable semantics and retrieval while avoiding empty bureaucracy; follows the standards' combine/subdivide principle; supports shallow growth and future profiles; retains a MyPond-like default.

**Costs and risks:** requires a module registry and more validation logic; consuming agents cannot rely only on hard-coded paths and must begin at the entry point; poorly designed module selection could hide needed topics.

**Best fit:** Wayfinder should serve software-product planning first but remain reusable for adjacent project types.

### Option C: project-defined structure with a Wayfinder manifest

Wayfinder requires only a root manifest or map. The interview derives all document types and paths from the user's terminology and mental model.

**Implementation:** initialization elicits categories, writes a manifest describing each path's purpose and authority, then generates the user-defined tree. Validation checks the manifest rather than a standard module registry.

**Benefits:** maximum fit to local vocabulary and stakeholder mental models; minimal imposed ontology; can adapt to mature repositories without restructuring them.

**Costs and risks:** high initialization burden; harder deterministic generation; weaker cross-project predictability; more opportunity for semantic overlap and missing roles; each consuming agent must learn a novel schema.

**Best fit:** Wayfinder primarily adapts heterogeneous established knowledge bases rather than initializing new ones.

## Recommendation

Choose **Option B: semantic kernel plus capability modules**.

It captures the strongest part of MyPond—the explicit knowledge map, authority separation, indexed focused documents, visible uncertainty, and decision history—without mistaking MyPond's current subject list for a universal ontology. It also creates the cleanest contract for the later “use” workflow: start at one known entry point, read module summaries, and follow only links relevant to the task.

The recommended boundary for this decision is intentionally narrow. Accepting Option B would not yet decide:

- the exact files in the kernel;
- the initial profile and module catalog;
- the selection interview;
- metadata serialization;
- generated wording;
- environment detection;
- script language or portability targets.

Those should be separate decisions because each changes observable runtime behavior and can be evaluated independently.

## Next decision if Option B is accepted

Define the smallest universal kernel: compare (a) a Markdown-only knowledge map, (b) a map plus a machine-readable manifest, and (c) a map generated from per-document metadata. This will determine what the initializer writes first and what later validation and selective retrieval can inspect deterministically.

## Sources

1. Zhang, J., and Norman, D. A. “[Representations in Distributed Cognitive Tasks](https://doi.org/10.1016/0364-0213(94)90021-3).” *Cognitive Science* 18(1), 1994, pp. 87–122.
2. Chen, O., Kalyuga, S., and Sweller, J. “[When Instructional Guidance Is Needed](https://doi.org/10.1017/edp.2016.16).” *The Educational and Developmental Psychologist* 33(2), 2016, pp. 149–162.
3. Jones, W., Phuwanartnurak, A. J., Gill, R., and Bruce, H. “[Don't Take My Folders Away! Organizing Personal Information to Get Things Done](https://doi.org/10.1145/1056808.1056952).” CHI Extended Abstracts, 2005.
4. Bergman, O., Beyth-Marom, R., Nachmias, R., Gradovitch, N., and Whittaker, S. “[Improved Search Engines and Navigation Preference in Personal Information Management](https://doi.org/10.1145/1402256.1402259).” *ACM Transactions on Information Systems* 26(4), 2008.
5. Pak, R., Pautz, S., and Iden, R. “[Information Organization and Retrieval: An Assessment of Taxonomical and Tagging Systems](https://blogs.clemson.edu/catlab/files/2021/09/Pak-et-al.-2007-Information-organization-and-retrieval-A-comparison-of-taxonomical-and-tagging-systems.pdf).” *Cognitive Technology* 12(1), 2007, pp. 31–44.
6. Kumpulainen, S., and Kärkkäinen, L. “[Card Sorting to Evaluate the Robustness of the Information Architecture of a Protocol Website](https://doi.org/10.1016/j.ijmedinf.2015.12.003).” *International Journal of Medical Informatics* 86, 2016, pp. 71–81.
7. ISO/IEC/IEEE. “[ISO/IEC/IEEE 15289:2019—Content of Life-Cycle Information Items](https://www.iso.org/standard/74909.html).” 2019; reviewed and confirmed 2025.
8. ISO/IEC/IEEE. “[ISO/IEC/IEEE 26514:2022—Design and Development of Information for Users](https://www.iso.org/standard/77451.html).” 2022.
9. ISO/IEC/IEEE. “[ISO/IEC/IEEE 42010:2022—Architecture Description](https://www.iso.org/standard/74393.html).” 2022.
10. ISO/IEC/IEEE. “[ISO/IEC/IEEE 29148:2018—Requirements Engineering](https://www.iso.org/standard/72089.html).” 2018.
11. Jiang, E., et al. “[Knoll: Creating a Knowledge Ecosystem for Large Language Models](https://doi.org/10.1145/3746059.3747711).” Proceedings of UIST 2025.
