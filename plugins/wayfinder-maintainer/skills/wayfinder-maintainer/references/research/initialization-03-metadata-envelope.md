# Initialization research 03: per-document metadata envelope

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** How should each Markdown document encode its authoritative structural metadata while remaining readable, portable, and deterministically validatable without new dependencies?
- **Prior decision:** Structural metadata is owned by each durable document; indexes are generated derivations.
- **Decision:** Option B accepted on 2026-09-13: use a constrained, visible Wayfinder metadata block.

## Executive conclusion

Use a **constrained, visible Markdown metadata block**, delimited by exact HTML comments and composed of a deliberately small set of one-line fields. This retains the human-readable MyPond presentation, keeps metadata attached to the document, renders acceptably in CommonMark-compatible viewers, and permits a dependency-free parser to recognize an intentionally tiny grammar.

YAML frontmatter is the strongest alternative because it has a mature authoring ecosystem. Its full grammar and type system, however, require a conforming YAML parser that is not part of common language standard libraries. Implementing a partial parser while calling the content YAML would create misleading compatibility. The missing PyYAML dependency encountered while validating the Wayfinder stub demonstrates this portability issue in the target environment.

JSON sidecars offer the strongest standardized parser availability and failure clarity, but they separate metadata from the document, weaken copy/move portability, and turn one conceptual edit into a coordinated two-file change. They also partially undo the accepted decision to co-locate intrinsic metadata with the document it describes.

## Decision boundary

This decision selects the metadata envelope and parsing philosophy. It does not choose:

- required field names;
- status vocabularies;
- identifier format;
- relationship syntax;
- generated index shape;
- the environment-detection contract;
- implementation language.

With the visible Markdown option accepted, the next decision defines the smallest universal field set before a parser is written.

## Evaluation criteria

| Criterion | Meaning for Wayfinder |
| --- | --- |
| Human visibility | A reader can identify role, status, recency, and authority without special tooling. |
| Machine determinism | A parser can accept valid input and reject invalid input without guessing. |
| Zero-install portability | At least one implementation can run in plausible environments using only ubiquitous built-ins. |
| Co-location | Metadata travels with the document during ordinary moves and copies. |
| Failure locality | An error points to one file and field with an actionable correction. |
| Incremental formality | Early documents can be valid without pretending that unknown relationships are known. |
| Ecosystem compatibility | Common Markdown renderers and editors preserve useful behavior. |
| Safe evolution | Future fields can be added without silently changing old meanings. |

## Evidence synthesis

### 1. Serialization syntax is less decisive than its supporting system

He, Cutler, and McNutt studied textual data-serialization usability with 215 crowd workers and nine practitioner interviews. They found no consistent universal advantage from notation choices such as indentation versus braces. YAML and HJSON performed better in some modification tasks, but those advantages disappeared in more realistic settings at the extremes of task complexity. Tooling, documentation, conventions, and community practice were more consequential than syntax alone.^1

**Implication:** choose the envelope based on the whole Wayfinder workflow—templates, generator, validator, diagnostics, and portability—not an unsupported claim that YAML or JSON is intrinsically easier.

**Limit:** this is a recent preprint and did not test Markdown metadata blocks or LLM-generated project records.

### 2. Markdown is readable and standardized, but metadata is an application convention

CommonMark defines Markdown as a plain-text format for structured documents and emphasizes source readability. It specifies headings, lists, emphasis, links, and HTML comments, but it does not define a semantic metadata block.^2 A visible field list inside exact comment delimiters would therefore be valid Markdown plus a Wayfinder-specific convention, not a claim of universal Markdown metadata interoperability.

The fact that any character sequence is a valid CommonMark document creates an important distinction: a Markdown renderer is intentionally permissive, while Wayfinder's metadata validator must be strict. The validator should report a malformed metadata block even if a Markdown renderer can display the file.

**Implication:** if Wayfinder uses Markdown fields, publish an explicit small grammar and parse only that grammar. Never infer near-miss labels or silently repair malformed fields during validation.

### 3. YAML frontmatter has strong adoption but a substantially larger language surface

YAML 1.2.2 is a general serialization language for mappings, sequences, scalars, aliases, tags, block styles, flow styles, and multiple schema choices. The specification aims to make JSON a strict subset and corrected earlier implicit-typing problems, but YAML nodes still have kinds and tags and implementations must select schema behavior.^3

Jekyll, Hugo, and Pandoc all support YAML metadata at the beginning of Markdown documents, demonstrating mature ecosystem adoption. Hugo also supports TOML, YAML, and JSON frontmatter, which illustrates that frontmatter delimiters do not themselves establish one portable metadata semantics.^4

The local Wayfinder scaffold provides direct operational evidence: the bundled `quick_validate.py` could not start because `yaml` was unavailable. Ruby's standard installation on this machine could parse the frontmatter, but relying on Ruby would merely move the environment assumption.

**Implication:** full YAML requires an external parser or environment-specific implementations. A dependency-free “YAML subset” should not be presented as YAML interoperability unless it is formally delimited and rejects every unsupported construct.

**Limit:** parser availability varies by platform. Some target repositories will already have a dependable YAML toolchain.

### 4. JSON has a smaller standardized grammar and broad built-in support

RFC 8259 defines JSON as a lightweight, text-based, language-independent interchange format with a small grammar for objects, arrays, strings, numbers, booleans, and null. It includes concrete interoperability guidance, including unique object names and UTF-8 for exchange.^5 Python, Node.js, Ruby, and PowerShell provide JSON parsing without third-party packages in common installations.

JSON's strict grammar improves parser agreement and error detection, but it requires quotes, commas, braces, and escaping. It also has no standard comment syntax. A sidecar can therefore be reliably parsed but cannot naturally carry human explanations, and the plan maintainer must keep it paired with the Markdown document.

**Implication:** JSON is the strongest machine interchange or derived-catalog format, but not necessarily the strongest authoring envelope for a small amount of document metadata.

### 5. Embedded metadata improves portability and self-description

The U.S. Federal Agencies Digital Guidelines Initiative states that embedded metadata travels with a digital object, enables work across organizational boundaries, supports preservation systems, and can assist disaster recovery. Its guidance is for audiovisual files, not Markdown, but the relationship between an object and its intrinsic identifying metadata is analogous.^6

Sidecars have legitimate uses when a format cannot carry suitable metadata or when metadata must remain independently managed. Markdown can already carry a small visible metadata block, so Wayfinder does not need a sidecar merely to make the document self-describing.

**Implication:** keep identity and routing metadata inside the Markdown document unless a later requirement cannot be represented safely there.

**Limit:** digital-preservation concerns and audiovisual container formats differ materially from version-controlled text repositories.

### 6. Formality should be minimized and assisted

Shipman and Marshall found that users may reject or circumvent systems that require implicit work practices to be made overly explicit. They recommend incremental and system-assisted formalization matched to the user's situation.^7

All three envelopes can become burdensome if Wayfinder demands too many fields. A visible Markdown block has a useful forcing function: its cost remains apparent to readers and maintainers. Hidden or separate metadata can grow without the document visibly communicating that complexity.

**Implication:** the chosen envelope should initially support scalar fields only. Add structured nesting only after a demonstrated workflow cannot be expressed through repeated simple fields, links, or generated relationships.

### 7. Validation feedback matters more than mere syntax acceptance

Stvilia and colleagues connect information quality to the activities information supports rather than treating completeness as field presence.^8 MetaConfigurator's small formative study also found that structured-data editing benefited from clear visual error feedback; participants explicitly requested stronger highlighting of validation problems.^9

**Implication:** Wayfinder's parser must identify the path, field, invalid value, expected form, and exact remediation command. It should accumulate independent errors in one pass instead of stopping after the first syntax problem.

**Limit:** MetaConfigurator's user study had only five participants and evaluated a graphical editor, so it supports diagnostic design only weakly.

## Options

### Option A: YAML frontmatter

Example:

```yaml
---
id: product-brief
kind: current-state
status: draft
summary: Concise entry point for the current product direction.
---
```

**Benefits:** familiar in documentation ecosystems; compact; supports lists and nested relationships; many editors recognize it; keeps metadata in the document.

**Costs:** full parsing normally adds a dependency; YAML versions and schema behavior differ; whitespace and implicit typing can be surprising; metadata may be hidden or specially rendered; a portable custom subset risks being mistaken for general YAML.

**Deterministic implementation:** either require a conforming YAML 1.2 parser and declare that dependency, or define a named Wayfinder YAML profile and ship equivalent parsers with extensive conformance fixtures. The latter is more code than the current metadata needs justify.

**Best fit:** repositories that already guarantee one YAML runtime and want richer nested metadata.

### Option B: constrained visible Markdown block — recommended

Illustrative envelope only; fields remain undecided:

```markdown
# Product brief

<!-- wayfinder:metadata -->
- **ID:** product-brief
- **Kind:** current-state
- **Status:** Draft
- **Summary:** Concise entry point for the current product direction.
<!-- /wayfinder:metadata -->
```

**Benefits:** preserves MyPond's visible presentation; metadata travels with the document; no YAML or JSON dependency; exact one-line fields can be parsed with POSIX-oriented text tools, Python, Node.js, Ruby, or PowerShell; ordinary renderers show a readable list while hiding the delimiters.

**Costs:** Wayfinder owns a small custom grammar; generic Markdown tools do not understand the semantics; multiline or nested data are intentionally awkward; formatters could alter the exact representation; loose regex parsing would be dangerous.

**Deterministic implementation:** require one H1 followed by a uniquely delimited metadata region. Accept only registered field labels, one field per line, exact bullet/emphasis syntax, UTF-8 text, and defined escaping rules. Reject duplicates, unknown required-field spellings, multiline values, and multiple metadata regions. Keep the parser line-oriented and publish input/output fixtures shared across implementations.

**Best fit:** portable, human-visible project records with intentionally compact metadata.

### Option C: JSON sidecars

Example pairing:

```text
product-brief.md
product-brief.wayfinder.json
```

```json
{
  "id": "product-brief",
  "kind": "current-state",
  "status": "draft",
  "summary": "Concise entry point for the current product direction."
}
```

**Benefits:** strict Internet-standard grammar; strong parser availability; straightforward schema validation; handles arrays and nested relationships without inventing syntax; leaves Markdown untouched.

**Costs:** breaks single-file co-location; doubles file count; document and metadata renames must be coordinated; a copied Markdown file becomes non-self-describing; JSON is visually heavier for authors and cannot contain comments; POSIX shell alone still lacks a conforming JSON parser.

**Deterministic implementation:** pair files by a precise naming rule, parse with the first supported standard runtime found during environment detection, validate against an embedded schema implemented in code, and reject orphan documents or sidecars.

**Best fit:** metadata-rich collections whose files cannot embed metadata or where strict machine interoperability dominates human browsing.

## Recommendation

Choose **Option B: constrained visible Markdown**, with these boundaries:

1. Call it the “Wayfinder metadata block,” not generic Markdown metadata.
2. Define a versioned, tiny grammar; do not implement an informal regex that accepts approximations.
3. Keep values single-line and primarily textual until a demonstrated need justifies structure.
4. Use exact HTML-comment delimiters so a parser can locate one region without interpreting the whole Markdown document.
5. Display the fields in ordinary rendered Markdown rather than hiding essential authority information.
6. Ship common conformance fixtures before offering multiple environment-specific parsers.
7. Treat JSON as a candidate derived-catalog format later, not as the authoring source.

This choice best matches the accepted goals: distributed authoritative metadata, MyPond-like readable documents, dependency-light deterministic tools, and one-time environment detection.

## Next decision

Define the minimum universal fields. The leading candidates are document identity, semantic kind, lifecycle status, last substantive update, and a retrieval-oriented summary. The next review should determine which are required at initialization, which can be derived, and which relationships belong only on specialized document types.

## Sources

1. He, S., Cutler, Z., and McNutt, A. M. “[Reading Between the Curly Braces: On Textual Data Serialization Format Usability](https://arxiv.org/abs/2607.26211).” 2026 preprint.
2. MacFarlane, J., et al. “[CommonMark Specification 0.31.2](https://spec.commonmark.org/0.31.2/).” 2024.
3. YAML Language Development Team. “[YAML 1.2.2 Specification](https://yaml.org/spec/1.2.2/).” 2021.
4. Jekyll. “[Front Matter](https://jekyllrb.com/docs/front-matter/).” Accessed 2026-09-13; Hugo. “[Front Matter](https://gohugo.io/content-management/front-matter/).” Accessed 2026-09-13; Pandoc. “[YAML Metadata Blocks](https://pandoc.org/MANUAL.html#extension-yaml_metadata_block).” Accessed 2026-09-13.
5. Bray, T., ed. “[RFC 8259: The JavaScript Object Notation Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259).” IETF Internet Standard STD 90, 2017.
6. Federal Agencies Digital Guidelines Initiative. “[Guidelines: Embedded Metadata in Broadcast WAVE Files](https://www.digitizationguidelines.gov/guidelines/digitize-embedding.html).” Version 3 approved 2021.
7. Shipman, F. M., and Marshall, C. C. “[Formality Considered Harmful: Experiences, Emerging Themes, and Directions on the Use of Formal Representations in Interactive Systems](https://doi.org/10.1023/A:1008716330212).” *Computer Supported Cooperative Work* 8, 1999, pp. 333–352.
8. Stvilia, B., Gasser, L., Twidale, M. B., and Smith, L. C. “[A Framework for Information Quality Assessment](https://doi.org/10.1002/asi.20652).” *Journal of the American Society for Information Science and Technology* 58(12), 2007, pp. 1720–1733.
9. Neubauer, F., Bredl, P., Xu, M., Patel, K., Pleiss, J., and Uekermann, B. “[MetaConfigurator: A User-Friendly Tool for Editing Structured Data Files](https://doi.org/10.1007/s13222-024-00472-7).” *Datenbank-Spektrum* 24, 2024, pp. 161–169.
