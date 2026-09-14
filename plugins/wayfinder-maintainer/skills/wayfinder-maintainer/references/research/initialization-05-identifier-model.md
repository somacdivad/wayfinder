# Initialization research 05: document identity model

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** Should a durable Wayfinder document be identified by its current path, a stable human-readable token, or an opaque generated value?
- **Prior decision:** Every durable document requires an `ID` in its visible metadata block. The identifier is unique within one project record and is distinct from the derived current path.
- **Decision:** Option B accepted on 2026-09-13: use a stable, human-readable, location-independent token scoped to one project record.

## Executive conclusion

Use a **stable, human-readable, location-independent token**. Assign it once, keep it when the document moves or its title changes, never reuse it for a different knowledge object, and exclude changeable facts such as folder, status, date, owner, or current technology. Keep the token short enough to inspect in diffs and diagnostics.

This is a deliberately contextual compromise. Large public persistent-identifier systems favor opaque identifiers because recognizable semantics decay. Fully opaque identifiers, however, are harder for people to read, transcribe, remember, and detect when used incorrectly. Wayfinder operates inside a bounded, version-controlled project record where identifiers appear in authoring, review, validation errors, and agent-visible catalogs. Limited recognizability has more operational value here than global, century-scale naming independence.

The exact token grammar, minting algorithm, collision workflow, and relationship syntax remain separate decisions.

## Decision boundary

This decision chooses what an `ID` fundamentally represents and how readable it should be. It decides:

- whether identity survives a file move;
- whether identity survives an ordinary title refinement;
- whether a human should recognize the referent from the token;
- whether mutable classification facts may be encoded in the token.

It does not yet decide:

- the allowed character set or length;
- whether a prefix such as `doc-` is used;
- slug-generation and normalization rules;
- sequential versus content-derived assignment;
- reservation and collision handling;
- concurrency behavior;
- split, merge, duplicate, and import lineage;
- how an authored link names a target;
- whether a generated catalog exposes compound project/document identities.

Those mechanics should follow only after the identity model is accepted.

## Evaluation criteria

| Criterion | Meaning for Wayfinder |
| --- | --- |
| Referential stability | A move, reorganization, or ordinary retitling does not change the logical target. |
| Human inspectability | Reviewers can recognize likely mistakes in metadata, relations, logs, and diagnostics. |
| Semantic durability | The token does not become false when mutable project facts change. |
| Deterministic validation | A scanner can enforce syntax and uniqueness without network services. |
| Portable generation | A new ID can be assigned without installing a package. |
| Concurrency safety | Independent branches are unlikely to assign the same ID. |
| Migration cost | Existing MyPond documents can receive IDs without rewriting unrelated prose. |
| Scope honesty | A repository-local mechanism is not represented as a globally persistent identifier service. |

## Evidence synthesis

### 1. Identity and location serve different functions

RFC 3986 defines an identifier as the information needed to distinguish a resource from other things within a stated scope. It explicitly warns that identifying a resource does not imply that the identifier fully defines its identity, and it distinguishes resource references from access behavior.^1 Relative paths are useful because an entire document tree can move together without changing internal references, but an individual move changes the path relationship.

The DOI model makes the separation more operational: the identifier continues to name the same content when the content moves to a new website or owner, while associated metadata is updated.^2 The W3C's URI guidance similarly emphasizes simplicity, stability, and manageability.^3

**Implication:** a current repository path is a locator and useful derived metadata. It should not be the only logical identity if Wayfinder promises reorganization without semantic breakage.

**Limit:** Wayfinder is not a Web resolver or DOI registry. These standards supply conceptual distinctions, not a requirement for network-addressable IDs.

### 2. Persistence is a maintenance policy, not a property of characters

DOI assignment requires one referent per identifier, no assumed expiration, and enough associated metadata to distinguish the referent.^4 Crossref instructs registrants to continue using the same DOI after moves and changes of responsibility.^2 These guarantees depend on governance and maintained resolution data, not merely the string format.

Wayfinder cannot make a project-local token globally persistent by calling it an ID. It can make narrower enforceable promises: uniqueness inside the record, no reassignment, stable identity across path and title changes, and explicit lineage when one document becomes another.

**Implication:** document the scope as the project record, call the token stable rather than globally persistent, and design update/validation workflows that preserve the promise.

### 3. Encoding mutable semantics creates semantic rot

The DOI Handbook states that no definitive information should be inferred from a DOI name itself and permits an arbitrary registrant-controlled suffix.^4 Crossref recommends opaque suffixes because meaningful components such as dates, page numbers, or ownership can later conflict with metadata.^2 ARK guidance likewise treats semantic opacity as useful for identifiers that must age and travel, particularly when organizational names or other recognizable authorities change.^5

This argues strongly against identifiers such as:

```text
draft/product/backend/postgres-2026
```

Every segment makes a claim likely to change. Keeping such an ID stable would make it misleading; correcting it would break identity.

**Implication:** even a readable Wayfinder token must be semantic-light. Do not encode path, lifecycle status, date, owner, implementation choice, or hierarchy. Put those facts in mutable metadata and relations.

### 4. Total opacity also has human costs

Alshammry and Lord review ontology identifiers, where semantics-free numeric sequences are often recommended for persistence. They identify practical disadvantages: numeric identifiers impede concurrent development, are relatively difficult to read, and make misuse harder to detect. Their Identitas design explores random but pronounceable identifiers plus a checksum.^6

The study concerns ontology development rather than project documentation, and it proposes a more specialized generator than Wayfinder currently needs. The key transferable point is that identifier strings participate in human work. Wayfinder users will see IDs in Markdown, code review, validator errors, and generated catalogs; inspectability can expose an accidental target mismatch before automation does.

**Implication:** do not choose UUIDs merely because collision mathematics are strong. Evaluate the actual scale and review workflow.

### 5. Opaque UUIDs solve decentralized uniqueness well

RFC 9562 defines 128-bit UUID formats intended to provide uniqueness across space and time, including random UUIDv4 and time-ordered UUIDv7.^7 A standard-library or operating-system implementation can often mint them without a shared counter, making UUIDs attractive for concurrent or disconnected authoring.

Wayfinder's initial namespace is a single project record scanned during creation and validation. That bounded scope makes a 36-character UUID operationally disproportionate unless concurrent assignment becomes common or records are frequently merged from unrelated repositories.

**Implication:** retain UUIDs as an escape hatch for import/merge workflows or as a future profile, not the default visible authoring token.

### 6. The MyPond record already mixes locator and identity strategies

MyPond currently uses repository-relative Markdown paths for 501 internal links across 64 documents. Nine different entry-point documents are named `README.md`, so basenames alone are not unique. Decision records use a stronger pattern: a global four-digit sequence remains recognizable while subject folders organize location independently.

This demonstrates both sides of the trade-off. Relative links are pleasant to author and render natively, while stable decision numbers provide identity that survives recategorization. The descriptive filename suffix improves scanning but should not be confused with the permanent part of the decision identity.

**Implication:** assign every durable document a stable metadata ID, while preserving normal Markdown paths as a human- and tool-compatible linking surface. The later link-model decision must define how path links and ID-targeted semantic relations coexist.

## Options

### Option A: current path is the ID

Example:

```markdown
- **ID:** product/product-brief.md
```

The identifier changes whenever the document moves or is renamed.

**Benefits:** no separate namespace or lookup step; naturally unique within the repository; immediately resolvable by ordinary filesystem and Markdown tools; easy migration from existing documents.

**Costs:** location and identity are conflated; reorganization becomes an identity change; every ID-based relation must be rewritten on moves; historical references are ambiguous; copied paths can silently identify different content on branches.

**Best fit:** disposable or location-defined documents whose organizational path is itself part of their identity.

### Option B: stable human-readable token — recommended

Examples are illustrative, not a decided grammar:

```markdown
- **ID:** product-brief
- **ID:** decision-0032
- **ID:** trusted-expert-handoff
```

The token is assigned once and remains unchanged when the path or display title changes. It is recognizable but is not treated as a mutable description.

**Benefits:** location-independent references; readable diagnostics and diffs; modest migration burden; easy dependency-free validation; aligns with MyPond's stable decision-number concept; supports generated resolution from ID to current path.

**Costs:** readable tokens can drift from later terminology; collision avoidance needs a defined creation workflow; authors may be tempted to “correct” an established ID after retitling; manual minting is less concurrency-safe than UUID generation.

**Required discipline:** encode no path, status, date, ownership, parent hierarchy, or current implementation. A misleading token after ordinary evolution remains stable; a true change of referent creates a new document and ID.

**Best fit:** bounded, collaboratively reviewed project records where people and agents both inspect identifiers.

### Option C: opaque generated token

Example:

```markdown
- **ID:** 9f0c8d3e-388b-4ea8-9339-b057aa15240d
```

Use a standardized UUID, preferably a version selected explicitly in a later decision.

**Benefits:** robust decentralized assignment; no semantic rot; safe across unrelated repositories and branches; standard parsers and generators are widely available.

**Costs:** poor information scent; difficult manual comparison and transcription; verbose metadata and diagnostics; wrong-target IDs can look plausible; migrating 64 readable documents produces a catalog no person can navigate unaided.

**Best fit:** high-concurrency or cross-repository aggregation where collision resistance dominates direct authoring usability.

## Recommendation

Choose **Option B: stable human-readable token**, subject to these invariants:

1. Identity is scoped to one Wayfinder project record; global uniqueness is not claimed.
2. One ID names one durable knowledge object.
3. The ID is assigned once and never reused for a different object.
4. Moves, folder reclassification, and ordinary H1 changes preserve the ID.
5. Mutable facts—including path, status, date, owner, parent, and implementation—never appear in the ID.
6. Human recognizability is an operational aid, not permission to infer authoritative facts from the token.
7. The validator rejects duplicate IDs and malformed syntax.
8. A generated catalog resolves the stable ID to the current derived path.
9. Document splitting, merging, importing, and replacement will use explicit lineage rules rather than silent ID reassignment.

This middle course accepts limited semantic longevity in exchange for much better reviewability inside Wayfinder's actual scope. It should be reconsidered if independent repositories routinely merge records or if concurrent offline document creation becomes common enough that collision coordination is costly.

## Next decision

Choose the token grammar and assignment mechanism. Compare a plain normalized slug, a monotonic sequence plus optional mnemonic suffix, and a deterministic slug with collision suffixing. Specify case, character repertoire, maximum length, reservation, collision errors, and whether an assigned ID may ever be corrected before publication.

## Sources

1. Berners-Lee, T., Fielding, R., and Masinter, L. “[RFC 3986: Uniform Resource Identifier (URI): Generic Syntax](https://www.rfc-editor.org/rfc/rfc3986).” Internet Standard STD 66, 2005.
2. Crossref. “[Constructing Your DOIs](https://www.crossref.org/documentation/member-setup/constructing-your-dois/).” Updated 2024-02-05; accessed 2026-09-13.
3. Sauermann, L., Cyganiak, R., and Völkel, M. “[Cool URIs for the Semantic Web](https://www.w3.org/TR/cooluris/).” W3C Interest Group Note, 2008.
4. DOI Foundation. “[DOI Handbook](https://www.doi.org/doi-handbook/html/).” Current online edition; accessed 2026-09-13.
5. ARK Alliance. “[General Identifier Concepts and Conventions](https://arks.org/about/identifier-concepts-and-conventions/).” Accessed 2026-09-13.
6. Alshammry, N., and Lord, P. “[Identitas: Semantics-free and Human-readable Identifiers](https://doi.org/10.3233/AO-210252).” *Applied Ontology* 16(4), 2021, pp. 379–394.
7. Davis, K., Peabody, B., and Leach, P. “[RFC 9562: Universally Unique IDentifiers (UUIDs)](https://www.rfc-editor.org/rfc/rfc9562).” IETF Proposed Standard, 2024.
