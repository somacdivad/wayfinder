# Initialization research 04: universal metadata fields

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** What is the smallest set of metadata fields that every durable Wayfinder document should own for identity, authority, maintenance, and selective retrieval?
- **Prior decision:** Every durable document uses one constrained, visible Wayfinder metadata block; document-type profiles may extend the universal contract.
- **Decision:** Option B accepted on 2026-09-13: require `ID`, `Kind`, `Status`, `Updated`, and `Summary`; derive title and path.

## Executive conclusion

Require a **retrieval-ready five-field core**: `ID`, `Kind`, `Status`, `Updated`, and `Summary`. Derive the human title from the document's single H1 and derive its path during scanning. Put provenance, responsibility, supersession, relations, tags, and domain-specific dates in document-kind profiles rather than the universal block.

The five fields answer five different routing questions:

| Field | Question answered |
| --- | --- |
| `ID` | Which durable knowledge object is this, independent of its path? |
| `Kind` | What interpretive and validation rules apply? |
| `Status` | How much authority should a reader assign it now? |
| `Updated` | When was its substantive content last reconsidered? |
| `Summary` | Is opening this document likely to satisfy the current information need? |

This is intentionally an application profile, not a universal claim about metadata. Each field must earn its place through a Wayfinder operation. The recommendation is stronger than the current MyPond convention because it adds stable identity, type, and retrieval description; it is narrower because specialized provenance and governance fields do not become universal.

## Decision boundary

This decision chooses which semantic fields are universal. It does not yet choose:

- field spelling or letter case in the rendered block;
- identifier syntax, namespace, or rename rules;
- the controlled `Kind` vocabulary or extension process;
- the `Status` vocabulary and authority semantics;
- the exact definition of a substantive update;
- summary length, style, or quality tests;
- document-kind-specific fields;
- metadata grammar versioning;
- generated catalog contents.

Those are narrower follow-on decisions. If the five-field core is accepted, identifier semantics should be designed next because cross-document links and generated indexes depend on them.

## Functional test for universality

A field belongs in the universal block only if all of these are true:

1. **Every durable document has a meaningful value.** A required placeholder such as `N/A` is evidence that the field is not universal.
2. **A cross-cutting workflow consumes it.** Initialization, update, validation, or selective use must make a concrete decision from the value.
3. **It cannot be derived reliably from the document or repository.** Duplicating the H1 as `Title` or the scan result as `Path` introduces avoidable disagreement.
4. **Its meaning remains stable across document kinds.** A decision's `Decider` and a research brief's `Research question` do not satisfy this condition.
5. **Its maintenance cost is proportionate to the errors it prevents.** More descriptive metadata can improve discovery, but indiscriminate richness creates authoring and staleness costs.

## Evidence synthesis

### 1. Metadata should be selected as an application profile

The Dublin Core Metadata Initiative defines broadly reusable properties including identifier, title, type, description, modified date, relation, source, subject, and provenance. Its terms are designed to be combined with other vocabularies in application profiles, and its guidance explicitly allows non-RDF systems to use the natural-language definitions and usage notes without adopting the full RDF model.^1

This is important because no external vocabulary exactly models a version-controlled project record whose consumers include people and task-oriented agents. Wayfinder should reuse established concepts where they fit, but required fields must be selected from its own functions rather than importing all Dublin Core terms.

**Implication:** define a small Wayfinder application profile. Document mappings to established terms where useful, without claiming semantic equivalence where Wayfinder adds special behavior such as authority status.

### 2. Stable identity is foundational to machine findability

The FAIR principles call for globally unique persistent identifiers, metadata that explicitly contains the described object's identifier, searchable indexing, qualified references, and provenance.^2 McMurry and colleagues likewise characterize unique, persistent, resolvable identifiers plus descriptive metadata as foundational to machine-oriented findability.^3

A repository document does not need a DOI or globally resolvable URI. It does need a repository-unique logical identity if references and generated catalogs are to survive folder changes. A path alone conflates identity with current storage location.

**Implication:** require `ID` for every durable document. Treat repository scope as the initial uniqueness boundary; identifier format and immutability require a separate decision.

**Limit:** FAIR was developed for scholarly digital objects and long-term data reuse. Its global-resolution requirements would be disproportionate for a private repository, so the recommendation adopts the identity principle, not the full infrastructure.

### 3. Type supports interpretation and controlled retrieval

DCMI defines `type` as the nature or genre of a resource and recommends a controlled vocabulary.^1 Empirical work on a metadata-driven e-government collection identified document type, audience, subject, department, and location as potentially useful retrieval facets, while also finding inconsistent and sparsely populated metadata across nearly 481,000 pages.^4

Wayfinder needs a stronger use for type than generic faceted browsing. `Kind` determines which extension schema and semantic checks apply: for example, a decision can require an outcome and supersession rules, while research can require evidence provenance and uncertainty. It also lets a consuming agent restrict retrieval to governing decisions or current-state synthesis.

**Implication:** require `Kind`, use a controlled vocabulary, and make it select a document-kind profile. Do not overload folder paths or filename prefixes as the only type signal.

**Limit:** the e-government study explored a different corpus and its retrieval system was at an early stage. It supports consistent facets generally, not Wayfinder's particular vocabulary.

### 4. Authority status is a project-record requirement

Lifecycle models describe documents and metadata as moving through creation, use, maintenance, sharing, and preservation states rather than remaining static.^5 MyPond makes the operational consequence explicit: Draft material is not authoritative, Active synthesis is current, Accepted decisions govern implementation, and Superseded records remain historical.

The status value therefore changes how a reader may use otherwise relevant content. Neither full-text search nor Git history can infer that policy safely. Status also enables deterministic contradictions such as an accepted decision claiming to be replaced while lacking a supersession relation.

**Implication:** require `Status` universally, while defining legal values and authority meaning separately. The allowed statuses may depend on `Kind`; universality of the field does not require one flat vocabulary.

**Limit:** scholarly lifecycle literature supports explicit state generally. The particular authority model comes from Wayfinder's accepted project-record goals and MyPond's current rules, not from an empirical comparison of status vocabularies.

### 5. A semantic update date cannot be reconstructed from Git

DCMI distinguishes `modified`—the date on which a resource was changed—from the broader lifecycle `date`, and recommends standardized date forms.^1 DataCite similarly treats dates as typed metadata rather than a single ambiguous timestamp.^6 Git can reveal when bytes in a path were committed, but that is not the same claim as when the document's substance was last reconsidered: formatting, link repair, file moves, and bulk generation can all change commit history without changing meaning.

Software-documentation studies show why recency matters but also why it is imperfect. Lethbridge, Singer, and Forward found that software engineers often do not update documentation as timely or completely as prescribed, while outdated documentation can remain useful in some circumstances.^7 A displayed date is therefore a maintenance cue, not proof of correctness.

**Implication:** require an author-maintained `Updated` date meaning “last substantive content change or explicit review.” Validate its syntax and plausible ordering, but never claim that tooling has validated freshness merely because the date is recent.

**Limit:** this field adds manual maintenance and can itself become stale. The update workflow will need deterministic prompts or checks around it.

### 6. A concise summary supplies information scent

Information-foraging theory models people as choosing information paths from proximal cues that suggest expected value and access cost.^8 In an instrumented study of eight Web-use sessions, Card and colleagues observed a strong effect of information scent on paths followed.^9 DataCite likewise calls an abstract especially valuable for deciding whether a found resource merits further investigation, reuse, or validation.^6

For Wayfinder's selective-use workflow, `Summary` is not merely descriptive decoration. It gives the agent a bounded routing representation that can be listed before opening full documents. This supports progressive disclosure and reduces the temptation to load the entire project record.

However, metadata does not universally improve retrieval. In a 61,000-document video corpus, title-only search outperformed search over additional user-generated tags and descriptions.^10 Full-text retrieval research has also found that paragraph-sized passages can outperform both whole-document and abstract-only search.^11 Poor or generic summaries could therefore add noise.

**Implication:** require `Summary` only if Wayfinder later defines and validates a retrieval-oriented writing contract. Retain full-text and section-level search as complementary mechanisms; do not treat summaries as a substitute for content.

**Limit:** the cited studies concern human Web or scholarly search rather than LLM agents reading project plans. The application to agent routing is a reasoned transfer that should be forward-tested.

### 7. Rich provenance and relationships are valuable but not universal fields

The W3C PROV model distinguishes entities, activities, and agents, and represents attribution, derivation, use, generation, and association as different relations.^12 This demonstrates why a universal `Source` or `Owner` scalar would be semantically weak: provenance can involve multiple sources, transformations, responsible agents, and roles.

MyPond already expresses this variation. Research briefs carry a research question and decision status; decisions carry a decider and decision date; product syntheses may carry sources; superseded records carry directional relations. Across 64 current Markdown documents, `Status` appears in all 64 and a date field appears in all 64, while `Decider` appears in 37, `Research question` and `Decision status` in 11 each, and `Source` in six.

**Implication:** model provenance, governance, supersession, and specialized dates in kind-specific profiles and document bodies. A generated catalog may normalize selected extension fields without making them universal authoring requirements.

## Candidate-field assessment

| Candidate | Universal? | Reason |
| --- | --- | --- |
| `ID` | Yes | Stable logical reference and generated-index key; not reliably derivable from a movable path. |
| `Kind` | Yes | Selects interpretation, validation profile, and retrieval facet. |
| `Status` | Yes | Determines current authority; cannot be inferred safely. |
| `Updated` | Recommended yes | Human-visible review cue distinct from byte-level Git history. |
| `Summary` | Recommended yes | Bounded information scent for selective retrieval; quality contract required. |
| `Title` | No; derive | The required H1 is the authoritative title. Duplicating it creates an inconsistency class. |
| `Path` | No; derive | The scanner already knows the current path. |
| `Created` | No | Useful for some record kinds, but Git and kind-specific dates usually suffice. |
| `Owner` | No | Responsibility may be contextual, plural, or absent; use a profile if governance requires it. |
| `Source` | No | Provenance is structurally richer and not meaningful for every index or guidance document. |
| `Relations` | No | Relationship types and cardinalities vary by kind; Markdown links remain universal content. |
| `Tags` / `Topics` | No initially | Free tags easily drift; controlled subject vocabularies should follow demonstrated retrieval needs. |
| `Audience` | No | Useful for selected outputs but often inferable from kind or content and not universal. |
| `Language` | No initially | A repository-level default is cheaper until multilingual content exists. |
| `Schema version` | Block-level, not document meaning | Needed for parser evolution but should be encoded once in the delimiter or registry contract, not maintained as descriptive content. |

## Options

### Option A: minimal governance core

Required fields: `ID`, `Kind`, `Status`.

Derive title from H1, path from scanning, and recency from Git. Make summaries optional or generated into indexes.

**Benefits:** lowest authoring burden; few stale fields; sufficient to choose validation rules and determine authority.

**Costs:** selective retrieval must inspect headings, generated prose, or full text; Git timestamps blur substantive changes with mechanical edits; generated summaries risk becoming an unreviewed competing description.

**Best fit:** small records where agents can cheaply scan every title and opening paragraph.

### Option B: retrieval-ready core — recommended

Required fields: `ID`, `Kind`, `Status`, `Updated`, `Summary`.

Derive title and path. Require kind-specific extensions only when the chosen profile calls for them.

Illustrative envelope; syntax details remain provisional:

```markdown
# Product brief

<!-- wayfinder:metadata -->
- **ID:** product-brief
- **Kind:** current-state
- **Status:** Draft
- **Updated:** 2026-09-13
- **Summary:** Concise entry point for the current product direction and its governing boundaries.
<!-- /wayfinder:metadata -->
```

**Benefits:** provides all cross-cutting routing cues without opening the body; supports generated indexes and task-specific selection; preserves a visible freshness cue; avoids duplicated title and path.

**Costs:** summaries and dates require disciplined updates; a low-quality summary can misroute retrieval; five fields make initial document creation slightly heavier.

**Best fit:** records expected to grow beyond easy manual scanning and to support selective agent context loading.

### Option C: extended universal record

Required fields: the five above plus fields such as `Owner`, `Parent`, `Sources`, `Relations`, and `Topics`.

**Benefits:** richer catalogs and more queries can operate without opening document bodies; responsibility and relationships are highly visible.

**Costs:** many documents will have artificial or empty values; provenance and relationships are flattened prematurely; more fields can become stale; universal complexity duplicates kind-specific semantics.

**Best fit:** homogeneous collections with established governance roles and a stable, shared taxonomy—not the varied project records Wayfinder is meant to support.

## Recommendation

Choose **Option B: the retrieval-ready five-field core**, with these constraints:

1. Treat the H1 as the single title authority and reject documents with zero or multiple H1s.
2. Derive the current repository-relative path; never ask authors to repeat it.
3. Use `ID`, not a path, as the catalog key and relation target.
4. Make `Kind` select a controlled validation profile.
5. Make `Status` carry defined authority semantics, potentially constrained by kind.
6. Define `Updated` as a substantive edit or explicit review date, not an automatically copied file or commit timestamp.
7. Write `Summary` for selection: say what authoritative question the document answers and any decisive scope boundary.
8. Keep specialized provenance and governance in kind-specific extensions.
9. Test summary-assisted retrieval against title, path, headings, and section-level search before relying on it exclusively.

This option is the smallest set that directly serves Wayfinder's promised selective-use workflow as well as initialization, update, and validation. Option A is a defensible fallback if the user values minimal maintenance over preview-based retrieval.

## Next decision

Define stable identifier semantics: scope, syntax, assignment, immutability, rename behavior, collision handling, and whether links in authored Markdown target IDs, paths, or both.

## Sources

1. DCMI Usage Board. “[DCMI Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/).” DCMI Recommendation, issued 2020-01-20; accessed 2026-09-13.
2. Wilkinson, M. D., et al. “[The FAIR Guiding Principles for Scientific Data Management and Stewardship](https://doi.org/10.1038/sdata.2016.18).” *Scientific Data* 3, 160018, 2016.
3. McMurry, J. A., et al. “[Unique, Persistent, Resolvable: Identifiers as the Foundation of FAIR](https://doi.org/10.1162/dint_a_00025).” *Data Intelligence* 2(1–2), 2020, pp. 30–39.
4. Freund, L., Jinglewski, M., and Kessler, K. “[Introducing FRED: Faceted Retrieval of E-government Documents](https://doi.org/10.1002/meet.14504901310).” *Proceedings of the American Society for Information Science and Technology* 49(1), 2013, pp. 1–4.
5. Habermann, T. “[Metadata Life Cycles, Use Cases and Hierarchies](https://doi.org/10.3390/geosciences8050179).” *Geosciences* 8(5), 2018, article 179.
6. DataCite Metadata Working Group. “[DataCite Metadata Schema Documentation for the Publication and Citation of Research Data and Other Research Outputs](https://schema.datacite.org/).” Version 4.7, 2026; accessed 2026-09-13.
7. Lethbridge, T. C., Singer, J., and Forward, A. “[How Software Engineers Use Documentation: The State of the Practice](https://doi.org/10.1109/MS.2003.1241364).” *IEEE Software* 20(6), 2003, pp. 35–39.
8. Pirolli, P., and Card, S. K. “[Information Foraging](https://doi.org/10.1037/0033-295X.106.4.643).” *Psychological Review* 106(4), 1999, pp. 643–675.
9. Card, S. K., Pirolli, P., Van Der Wege, M. M., Morrison, J. B., Reeder, R. W., Schraedley, P. K., and Boshart, J. “[Information Scent as a Driver of Web Behavior Graphs: Results of a Protocol Analysis Method for Web Usability](https://doi.org/10.1145/365024.365331).” *Proceedings of CHI 2001*, pp. 498–505.
10. Magdy, W., Min, J., Leveling, J., and Jones, G. J. F. “[Building a Domain-specific Document Collection for Evaluating Metadata Effects on Information Retrieval](https://aclanthology.org/L10-1242/).” *Proceedings of LREC 2010*, pp. 1288–1295.
11. Lin, J. “[Is Searching Full Text More Effective Than Searching Abstracts?](https://doi.org/10.1186/1471-2105-10-46).” *BMC Bioinformatics* 10, 2009, article 46.
12. W3C Provenance Working Group. “[PROV-O: The PROV Ontology](https://www.w3.org/TR/prov-o/).” W3C Recommendation, 2013.
