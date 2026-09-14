# Initialization research 12: kernel, profiles, and module selection

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** What universal planning roles, named starter profiles, module-selection rules, and software-product layout should initialization provide as one coherent system?
- **Prior decisions:** Wayfinder uses a stable semantic kernel plus capability modules, distributed document metadata, generated indexes, and a strict root manifest that explicitly lists enabled modules.
- **Decision status:** Option E, a profile-seeded and bounded taxonomy interview, accepted by the skill owner on 2026-09-13.

## Executive conclusion

Use a **small semantic kernel, disclosed starter profiles, and a bounded taxonomy interview**. Every record should contain a human knowledge map, a concise current-plan brief, a visible open-question register, and an indexed decision history. The initial registry should add four optional capabilities—product, research, architecture, and development—around the required decision capability. Named `foundation`, `evidence-led`, and `software-product` profiles should supply tested starting bundles. After a profile is selected, a hybrid elicitation step should let the user retain, rename, or add project-specific subjects and, when no standard authority boundary fits, propose a governed local module.

The software-product profile should create the useful top-level shape of MyPond without manufacturing empty subject documents: product, research, decisions, architecture, and development each receive an entrypoint; detailed subject documents arise later from actual interview content. Project-local templates should not be copied in this decision. Runtime construction templates belong to the skill until a later template-governance decision shows that checked-in copies provide more value than drift risk.

This is the hybrid Option E added below. It combines the reusable semantic layer of Option A with a constrained form of Option D. It is a design synthesis rather than a directly tested result. Requirements-engineering studies support tailoring artifact sets to project parameters; standards support stable information roles that can be combined or subdivided; scaffolding research supports guided starting structures for unfamiliar work; card-sorting and taxonomy-development research supports testing proposed categories while permitting grounded additions; and default-effect research requires that recommended bundles be transparent and actively confirmed. No reviewed study directly compares profile-seeded taxonomy interviews for an LLM-maintained Markdown planning record.

Sources were accessed on 2026-09-13.

## Skill-owner direction

The skill owner proposed combining Options A and D on 2026-09-13: select a starter profile, then interview the user to discover additional taxonomy. The refined Option E and its extension boundary were subsequently accepted. Taxonomy evolution after initialization will be handled by the future general update workflow.

## Terms and boundaries

- A **kernel** is the invariant set of semantic roles every valid record must satisfy. It is not a fixed domain taxonomy.
- A **module** is a registered capability with an ID, purpose, entrypoint contract, allowed document roles, validation rules, and optional dependencies.
- A **profile** is a named, versioned initializer preset: a module set plus default paths and starter documents. It is an authoring convenience, not a permanent classification of the project.
- A **concern** is an explicit project need that justifies enabling a module. Concern assessment can guide a recommendation, but the deterministic script receives an explicit profile and final module set.
- A **starter document** contains truthful orientation, scope, and visible unknowns. An empty heading collection is not evidence that a topic has been planned.

Profiles exist only at initialization time. The manifest records the resulting modules and paths, not the profile name, so later updates can evolve the record without misrepresenting its origin as current policy.

## Local case: the useful shape of MyPond

MyPond's current record separates five forms of knowledge:

| Capability | Current entrypoint | Semantic role |
| --- | --- | --- |
| Product | `product/product-brief.md` | Current product hypothesis, scope, audiences, workflows, and links to focused details. |
| Research | `research/README.md` | External evidence, provenance, uncertainty, and validation needs. |
| Decisions | `decisions/README.md` | Accepted choices, rationale, global chronology, and supersession history. |
| Architecture | `architecture/README.md` | Current technical shape, boundaries, and links to governing decisions. |
| Development | `development/README.md` | Implementation environment and workflow guidance. |

The root `README.md` explains authority and routes readers among those capabilities. Product open questions are separately visible. Subject folders under decisions appeared when volume and stakeholder concerns justified them; they are not evidence that a new record should pre-create the same subfolders. MyPond's `templates/` directory currently supports local authoring, but template placement and versioning are separable from the profile topology.

The profile recommendation therefore reproduces MyPond's **layering and entrypoints**, not its current number of subject documents or decision categories.

## Proposed universal kernel

Every profile must satisfy these semantic roles:

| Role | Required behavior | Default path in `foundation` |
| --- | --- | --- |
| Machine anchor | Declares roots, baseline, modules, and generated outputs. | `<workspace-root>/.wayfinder/manifest.json` |
| Knowledge map | Human and agent entrypoint; states scope, authority/lifecycle rules, module map, and navigation cues. | `<recordRoot>/README.md` |
| Current-plan brief | Concise synthesis of purpose, intended outcomes, boundaries, stakeholders, and current direction; links to details rather than absorbing them. | `<recordRoot>/plan-brief.md` |
| Open-question register | Makes consequential unknowns, their impact, and their next resolution step visible. | `<recordRoot>/open-questions.md` |
| Decision history | Indexes accepted and superseded choices without erasing rationale. | `<recordRoot>/decisions/README.md` |

The roles are invariant; their paths may be profile-specific. The metadata catalog and entrypoint links, rather than hard-coded filenames, let later consumers find them. Exact `Kind` vocabulary and document content schemas remain a later decision.

The decision capability is part of the kernel because a durable plan must distinguish current synthesis and unresolved questions from accepted choices. A project with no accepted decisions still has an honest decision index stating that fact and explaining how decisions will enter the record.

## Proposed version 1 module registry

| Module ID | Enable when | Default entrypoint | Initial contents |
| --- | --- | --- | --- |
| `decisions` | Always; it realizes a kernel role. | `decisions/README.md` | Authority rule, empty-state message, and decision navigation contract. |
| `research` | External evidence, user research, experiments, or source uncertainty materially informs the plan. | `research/README.md` | Evidence method, strength vocabulary, source rules, and an honest empty-state index. |
| `product` | The work defines a product or service through audiences, outcomes, workflows, and scope. | `product/product-brief.md` | Product hypothesis, boundaries, subject map, and open-question link. |
| `architecture` | A system's structure, interfaces, quality attributes, deployment, data, security, or other technical tradeoffs need durable guidance. | `architecture/README.md` | Scope, current shape or explicit unknown state, governing decisions, and architectural concerns. |
| `development` | Builders need durable setup, tooling, testing, contribution, or delivery guidance. | `development/README.md` | Agreed workflow constraints and explicitly undecided implementation details. |

`product`, `research`, `architecture`, and `development` have no hard dependency on one another in version 1. They all depend only on the kernel and decision capability. This permits, for example, an evidence-led policy plan with no software architecture or a technical library plan with architecture and development but no product-market material.

Operations, policy/compliance, delivery, data-governance, and other plausible capabilities should remain unregistered until Wayfinder has a concrete use case and can define their authority boundaries. Extension is safer than speculative empty scaffolding.

## Proposed starter profiles

### `foundation`

For a general project whose domain-specific needs are not yet established.

```text
<recordRoot>/
├── README.md
├── plan-brief.md
├── open-questions.md
└── decisions/
    └── README.md
```

Enabled modules: `decisions`.

### `evidence-led`

For a plan in which external sources, observation, user research, or experiments are already known to be material.

```text
<recordRoot>/
├── README.md
├── plan-brief.md
├── open-questions.md
├── decisions/
│   └── README.md
└── research/
    └── README.md
```

Enabled modules: `decisions`, `research`.

### `software-product`

For a software-enabled product or service that needs product discovery and an implementation handoff.

```text
<recordRoot>/
├── README.md
├── product/
│   ├── product-brief.md
│   └── open-questions.md
├── research/
│   └── README.md
├── decisions/
│   └── README.md
├── architecture/
│   └── README.md
└── development/
    └── README.md
```

Enabled modules: `product`, `research`, `decisions`, `architecture`, `development`.

Here the product brief and product open-question file realize the corresponding kernel roles. Focused product documents, decision subject folders, dated research briefs, and technical detail files are added only when content exists. This keeps initialization honest while allowing the interview workflow to grow toward MyPond's present form.

## Concern-based selection contract

The agent may recommend a profile using a short concern screen, but the script must not infer the choice from prose or directory names.

| Explicit concern | Resulting recommendation |
| --- | --- |
| Only purpose, scope, unknowns, and decision history are presently known. | Start with `foundation`. |
| Material claims will depend on external evidence, observation, user research, or experiments. | Enable `research`; `evidence-led` is the smallest matching profile. |
| The plan defines audiences, outcomes, workflows, positioning, or product scope. | Enable `product`. |
| Technical structure or system-quality tradeoffs must guide later work. | Enable `architecture`. |
| Builders need durable environment or implementation workflow guidance. | Enable `development`. |
| All four optional concerns apply to a software-enabled product. | Recommend `software-product`. |

Binding selection rules:

1. The agent shows the profile, exact enabled modules, paths, and one-sentence rationale before any write.
2. The user actively confirms or edits that proposal. A recommendation is never silently applied.
3. The deterministic initializer accepts explicit `--profile`, `--enable`, and `--disable` values; it validates the final set but does not interpret interview prose.
4. Kernel roles and `decisions` cannot be disabled. Optional overrides are order-independent and duplicate selections are errors.
5. A dry run emits a stable operation plan containing every directory, file, manifest module, and skipped optional module.
6. Initialization refuses to overwrite or adopt existing files. Adoption and reconciliation belong to a later, separately authorized workflow.
7. Disabling a profile's optional module removes it only from the not-yet-applied operation plan. Once initialized, module removal is an update/migration operation and never deletes content implicitly.
8. Profiles and module descriptors are versioned with the skill. The manifest stores the resulting explicit structure, so routine use does not need to load profile definitions.
9. Generated starter documents state what is known, what is not known, and where the next interview will continue. They do not contain fabricated sample requirements or ceremonial empty sections.

## Proposed profile-seeded taxonomy interview

Profile selection establishes a proposed structure, not the final project taxonomy. Before writing, the interview should work in four passes:

1. **Inventory:** elicit the project's intended planning concerns, recurring knowledge objects, likely readers, and tasks those readers will perform. Capture examples before asking the user to name folders.
2. **Place:** map each item to a kernel role, standard module, or existing proposed subject. Ask the user where they would expect to create and retrieve it.
3. **Extend:** expose the profile's categories and let the user retain, rename, split, merge, or add subject categories. Propose a local module only when the concern has a genuinely different authority or lifecycle from every standard module.
4. **Challenge and confirm:** show the complete proposed tree plus a concern-to-home map. Surface overlaps, empty categories, ambiguous names, and unplaced concerns; then require active confirmation before the deterministic initializer receives the structure.

This resembles a hybrid card sort—seeded categories with permission to create new ones—but it is not a formal card-sorting study. A one-person conversational interview cannot provide population-level evidence about a wider audience's mental model. It captures the plan owner's current working model and should label broader usability assumptions for later validation.

### Two extension levels

Wayfinder should distinguish two types of project-owned taxonomy:

- A **subject** is a shallow primary navigation category inside a module. It does not change authority or lifecycle semantics. Examples include `authentication` inside product knowledge or `data-platform` inside decisions.
- A **local module** is a separate authority boundary with its own purpose and entrypoint because no standard module governs the content honestly. Examples might eventually include regulatory compliance, clinical safety, or field operations.

The interview should prefer subjects. A local module is justified only when all of these are true:

1. Its purpose can be stated independently of existing modules.
2. Its content has a distinct authority, lifecycle, or maintenance audience that would be obscured inside an existing module.
3. At least one real planned knowledge object belongs there; speculative empty modules are rejected.
4. Its boundary does not duplicate another module. Cross-cutting relationships are represented with links and stable IDs.
5. The user explicitly approves the module after seeing its boundary and examples.

Local modules should use a reserved project-owned ID form such as `local-<slug>` and the same manifest fields—`id`, `root`, and `entrypoint`—as built-in modules. Acceptance of Option E would therefore refine the manifest contract: built-in IDs remain closed and versioned, while values matching the reserved local-module grammar are structurally valid but carry no built-in module semantics. The local entrypoint must state the module's purpose, authority, lifecycle, audience, and relationship to standard modules.

### Deterministic boundary

The interview and agent may perform semantic discovery; scripts must not pretend that taxonomy inference is deterministic. The deterministic layer should instead:

- accept an explicit final taxonomy proposal;
- validate names, containment, uniqueness, shallowness, required entrypoints, and module-ID grammar;
- ensure every elicited concern in the proposal has exactly one declared primary home or is explicitly unresolved;
- render a stable preview of the resulting tree and concern-to-home mapping;
- reject a local module without its required boundary declaration;
- apply only the user-confirmed proposal.

The manifest records modules, while generated indexes and document relationships expose subjects. The originating interview transcript and profile name are not runtime requirements.

## Evidence synthesis

### 1. Stable information roles can coexist with project-specific packaging

ISO/IEC/IEEE 15289 defines generic lifecycle information-item purposes while explicitly allowing information items to be combined or subdivided to suit a project's lifecycle and organizational needs.^1 This does not prescribe Wayfinder's kernel, but it supports defining durable semantic roles without imposing one physical document package on every project.

**Implication:** validate required roles and relationships, then let profiles place them in a domain-appropriate shallow hierarchy.

### 2. Artifact needs vary with project parameters

Méndez Fernández and colleagues studied requirements-engineering artifacts across 12 industrial projects, identified distinct artifact patterns, and related those patterns to project parameters and execution strategies.^2 Xu and Ramesh's two case studies likewise describe tailoring as an interaction among project goals, environmental factors, challenges, and process strategies.^3 These studies concern software processes rather than repository plans, and neither establishes Wayfinder's particular module list. They do undermine the assumption that maximum artifact completeness is universally appropriate.

**Implication:** select modules from explicit concerns and project characteristics. Do not use a comprehensive tree as the default measure of maturity.

### 3. A guided starting structure reduces blank-slate burden

Wood, Bruner, and Ross introduced the tutoring functions later summarized as scaffolding: support can recruit attention, reduce degrees of freedom, mark critical features, and help a learner complete a task initially beyond unaided performance.^4 Cognitive-load work similarly finds that the usefulness of guidance depends on task complexity and prior knowledge; guidance can help novices while becoming redundant for more experienced learners.^5

Wayfinder initialization is not a teaching experiment, so this is adjacent evidence. Still, choosing audiences, evidence boundaries, decision governance, architecture scope, and file placement simultaneously creates a coordination problem that named, inspectable profiles can reduce.

**Implication:** offer a few worked starting bundles plus an explicit custom path. Do not require every user to assemble an ontology module by module.

### 4. Defaults are influential and must be disclosed

Jachimowicz and colleagues' meta-analysis of 58 studies found a substantial average default effect but also considerable heterogeneity. Effects partly reflected perceived endorsement and status-quo mechanisms.^6 The domain is choice architecture broadly, not documentation tooling.

**Implication:** label profiles as recommendations, expose their contents and rationale, and require active confirmation. Do not silently translate a user description into a hidden module set or describe a profile as objectively complete.

### 5. Capabilities should correspond to stakeholder concerns

ISO/IEC/IEEE 42010 specifies architecture-description concepts around stakeholders, concerns, viewpoints, and views without prescribing one recording format.^7 ISO/IEC/IEEE 26514 likewise makes audience and task analysis part of information architecture and development.^8 These standards concern architecture descriptions and user information, respectively, but converge on selecting representations because particular people need particular information.

**Implication:** enable `architecture`, `development`, and other modules because named stakeholder concerns require them, not because every serious project is expected to fill every folder.

### 6. Shallow primary homes support navigation, but the schema must evolve

Personal-information-management research observed that project folders often express a divide-and-conquer understanding of the work, while strict hierarchy becomes awkward for items with multiple legitimate classifications.^9 MyPond's own accepted organization decision similarly favors shallow subject folders, indexes, and stable identifiers over deep classification-dependent paths.^15

**Implication:** profiles create module entrypoints and let subject folders emerge with content. Cross-cutting relationships use links and stable IDs rather than pre-building a deep taxonomy.

### 7. Hybrid elicitation can test a seed while discovering missing categories

Card sorting is used to elicit or evaluate how people group information. Kumpulainen and Kärkkäinen's repeated open card sort found that an earlier user-derived structure remained broadly robust while new categories emerged from actual search needs.^10 Research comparing information architectures across cultures also found material differences in participants' mental models.^11 These studies involve website navigation and multiple participants, not a project owner working with an agent.

**Implication:** show the starter taxonomy as a revisable seed, ask for concrete placement examples, and preserve new user categories when they have a clear boundary. Treat a single interview's result as a working hypothesis rather than proof that every stakeholder will retrieve information the same way.

### 8. Taxonomy construction needs a recorded method and stopping conditions

Usman and colleagues' systematic mapping of 270 software-engineering taxonomy studies found that most taxonomies used qualitative classification, but 86.53% did not describe the procedure sufficiently; few taxonomies were later extended or revised.^12 Nickerson, Varshney, and Muntermann propose iterative conceptual-to-empirical taxonomy development with explicit objective and subjective ending conditions.^13 Wayfinder does not need their full classification formalism, but their central governance lesson applies.

**Implication:** record the input concerns, category operations, boundary rationales, unresolved placements, and explicit confirmation. Initialization stops when all known items have one primary home or are marked unresolved, every proposed category has a real example, and the user judges the result concise, comprehensible, and extendible. Later taxonomy changes belong to a governed update workflow.

### 9. Plausible classifications are not necessarily domain-valid

An experimental comparison of knowledge-elicitation techniques found that even participants ignorant of a domain could construct plausible-looking knowledge bases from common sense.^14 This older expert-systems research used small samples and does not evaluate LLMs, but it provides a useful warning against equating coherence with correctness.

**Implication:** the agent may synthesize and challenge a taxonomy, but it must trace categories to user-provided concerns or identified evidence, label speculative additions, and obtain user confirmation. Fluent naming alone is insufficient justification.

## Options

### Option A: semantic kernel, disclosed starter profiles, and concern overrides

Adopt the kernel, five-module registry, three profiles, software-product layout, and binding selection rules above.

**Benefits:** gives novices a concrete starting point; preserves an expert/custom route; produces a MyPond-like record for the primary use case; avoids empty subject trees; makes module choice inspectable and deterministic at the script boundary; supports future non-software profiles without weakening the kernel.

**Costs and risks:** requires versioned profile and module descriptors; path variation means consumers must use the manifest, catalog, and document roles rather than assume `plan-brief.md`; the concern screen still relies on human or agent judgment; a recommended profile can anchor choices even when disclosed.

**Best fit:** Wayfinder begins with software-product planning but is intended to become reusable across adjacent planning domains.

### Option B: one comprehensive software-product scaffold

Always initialize product, research, decisions, architecture, development, templates, and a predefined set of subject documents matching MyPond.

**Benefits:** one highly predictable tree; simplest initializer and validator; strongest worked example; consuming agents can rely on hard-coded paths.

**Costs and risks:** conflates artifact count with completeness; creates empty or invented content; makes non-software projects awkward; bakes MyPond's current decomposition into the universal ontology; increases maintenance and retrieval noise.

**Best fit:** Wayfinder is permanently scoped to early-stage software products almost identical to MyPond.

### Option C: kernel plus fully à-la-carte modules

Keep the proposed kernel and registry, but provide no named profiles. Every initialization explicitly selects optional modules one by one.

**Benefits:** maximum transparency; no profile anchoring; small registry remains composable; every enabled capability has an explicit user decision.

**Costs and risks:** repeats the same coupled choices; increases initial interview burden; gives inexperienced users no worked configuration; produces less consistent software-product records; makes it harder to test a blessed end-to-end path.

**Best fit:** users are expert process designers and project types are highly heterogeneous.

### Option D: interview-generated taxonomy

Require only abstract kernel roles. The agent derives module names, paths, relationships, and starter documents from each user's language and concerns.

**Benefits:** closest fit to local terminology; can model domains not anticipated by the registry; avoids forcing software concepts into unrelated projects.

**Costs and risks:** highest cognitive and conversational burden; weakest determinism and cross-project predictability; difficult validation and selective retrieval; greater risk of overlapping authority; every new plan effectively designs a new method.

**Best fit:** Wayfinder primarily adapts mature, heterogeneous knowledge systems and initialization time is not constrained.

### Option E: profile-seeded, bounded taxonomy interview — revised recommendation

Select one of Option A's profiles, then run the proposed four-pass taxonomy interview. Permit project-owned subjects within modules and governed `local-<slug>` modules when their authority or lifecycle genuinely differs. Show the resulting tree and concern-to-home map before any write. Defer all later taxonomy changes to the update workflow.

**Benefits:** retains a reliable cross-project kernel and tested software-product path while reflecting the project's language and working model; reduces blank-slate burden; lets unanticipated domains participate without pretending every category is universal; creates explicit evidence and validation targets for later taxonomy evolution.

**Costs and risks:** takes longer than selecting a profile alone; user and agent may overfit the taxonomy to one interview; local modules reduce cross-project predictability; a reserved custom-ID space and boundary schema add validation work; seeded categories may anchor the user despite explicit revision prompts.

**Best fit:** Wayfinder should be immediately useful for familiar project types while supporting new domains through governed, inspectable extension.

## Recommendation

Choose **Option E** as a complete policy bundle:

1. Require the five kernel roles: machine anchor, knowledge map, current-plan brief, open-question register, and decision history.
2. Register `decisions` as required and `research`, `product`, `architecture`, and `development` as optional version 1 modules.
3. Provide `foundation`, `evidence-led`, and `software-product` starter profiles.
4. After profile selection, inventory concrete concerns and knowledge objects, map them to the seed, and let the user revise or extend the subject taxonomy.
5. Prefer subjects within standard modules; allow a `local-<slug>` module only under the five boundary tests above.
6. Use the exact software-product entrypoint tree shown above as a seed while deferring unsupported subject documents until interview content warrants them.
7. Show the final tree, boundary rationales, and concern-to-home map; require active confirmation.
8. Pass only the explicit confirmed proposal to deterministic tooling; never ask a script to infer semantics from prose.
9. Store the resulting modules and paths in the manifest, not the originating profile name or interview transcript.
10. Keep construction templates in the skill for now and decide project-local template governance separately.

This is broad enough to establish a coherent user-visible initialization model while leaving independently consequential questions—document schemas, initial content depth, safe-write mechanics, and runtime portability—for later decisions.

## What acceptance would change now

The runtime skill would record the kernel roles, module vocabulary, profiles, bounded taxonomy-interview behavior, and explicit-confirmation policy. The design record would also reserve taxonomy evolution for the update workflow. No initializer should be made operational yet: the next decision must define what truthful content each starter document receives and how initialization coordinates the profile/taxonomy interview with the first write.

## Deferred decisions

- Exact `Kind` values and module-specific metadata extensions.
- Required and optional sections within each starter document.
- Whether initialization writes skeletal documents immediately or elicits a minimum brief first.
- Subject-folder split thresholds and index formats.
- Project-local template generation and template-version drift.
- Module and subject renaming, splitting, merging, addition, retirement, and migration after initialization; these belong to the update workflow.
- Script runtime/adapters and one-time environment detection.
- Existing-record adoption.

## Next decision if Option E is accepted

Define the **initialization content transaction** as one bundle: minimum domain interview before profile/taxonomy selection, starter-document content contracts, unknown/placeholder policy, preview and confirmation, and atomic no-overwrite application.

## Sources

1. ISO/IEC/IEEE. “[ISO/IEC/IEEE 15289:2019—Content of Life-Cycle Information Items](https://www.iso.org/standard/74909.html).” 2019; reviewed and confirmed 2025.
2. Méndez Fernández, D., Wagner, S., Lochmann, K., Baumann, A., and de Carne, H. “[Field Study on Requirements Engineering: Investigation of Artefacts, Project Parameters, and Execution Strategies](https://doi.org/10.1016/j.infsof.2011.09.001).” *Information and Software Technology* 54(2), 2012, pp. 162–178.
3. Xu, P., and Ramesh, B. “[Software Process Tailoring: An Empirical Investigation](https://doi.org/10.2753/MIS0742-1222240211).” *Journal of Management Information Systems* 24(2), 2007, pp. 293–328.
4. Wood, D., Bruner, J. S., and Ross, G. “[The Role of Tutoring in Problem Solving](https://doi.org/10.1111/j.1469-7610.1976.tb00381.x).” *Journal of Child Psychology and Psychiatry* 17(2), 1976, pp. 89–100.
5. Chen, O., Kalyuga, S., and Sweller, J. “[When Instructional Guidance Is Needed](https://doi.org/10.1017/edp.2016.16).” *The Educational and Developmental Psychologist* 33(2), 2016, pp. 149–162.
6. Jachimowicz, J. M., Duncan, S., Weber, E. U., and Johnson, E. J. “[When and Why Defaults Influence Decisions: A Meta-Analysis of Default Effects](https://doi.org/10.1017/bpp.2018.43).” *Behavioural Public Policy* 3(2), 2019, pp. 159–186.
7. ISO/IEC/IEEE. “[ISO/IEC/IEEE 42010:2022—Architecture Description](https://www.iso.org/standard/74393.html).” 2022.
8. ISO/IEC/IEEE. “[ISO/IEC/IEEE 26514:2022—Design and Development of Information for Users](https://www.iso.org/standard/77451.html).” 2022.
9. Jones, W., Phuwanartnurak, A. J., Gill, R., and Bruce, H. “[Don't Take My Folders Away! Organizing Personal Information to Get Things Done](https://doi.org/10.1145/1056808.1056952).” CHI Extended Abstracts, 2005.
10. Kumpulainen, S., and Kärkkäinen, L. “[Card Sorting to Evaluate the Robustness of the Information Architecture of a Protocol Website](https://doi.org/10.1016/j.ijmedinf.2015.12.003).” *International Journal of Medical Informatics* 86, 2016, pp. 71–81.
11. Petrie, H., Power, C., Cairns, P., and Seneler, C. “[Using Card Sorts for Understanding Website Information Architectures: Technological, Methodological and Cultural Issues](https://doi.org/10.1007/978-3-642-23768-3_26).” *INTERACT 2011*, pp. 309–322.
12. Usman, M., Britto, R., Börstler, J., and Mendes, E. “[Taxonomies in Software Engineering: A Systematic Mapping Study and a Revised Taxonomy Development Method](https://doi.org/10.1016/j.infsof.2017.01.006).” *Information and Software Technology* 85, 2017, pp. 43–59.
13. Nickerson, R. C., Varshney, U., and Muntermann, J. “[A Method for Taxonomy Development and Its Application in Information Systems](https://doi.org/10.1057/ejis.2012.26).” *European Journal of Information Systems* 22(3), 2013, pp. 336–359.
14. Burton, A. M., Shadbolt, N. R., Rugg, G., and Hedgecock, A. P. “[The Efficacy of Knowledge Elicitation Techniques: A Comparison Across Domains and Levels of Expertise](https://doi.org/10.1016/S1042-8143(05)80010-X).” *Knowledge Acquisition* 2(2), 1990, pp. 167–178.
15. MyPond. “[Decision 0032: Organize Canonical Documents by Subject](../../../../docs/decisions/project-governance/0032-organize-canonical-documents-by-subject.md).” Local project decision, 2026-09-12.
