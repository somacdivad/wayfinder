# Initialization research 06: identifier grammar and normal allocation

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** What syntax and ordinary allocation rule should Wayfinder use for stable, readable, project-local document IDs?
- **Prior decision:** An ID names one durable knowledge object, is unique within one project record, survives ordinary moves and retitling, is never reused, and excludes mutable classification facts.
- **Decision:** Option B, a global sequence plus frozen mnemonic.

## Executive conclusion

Use a **global monotonic sequence plus a frozen mnemonic**:

```text
wf-0001-project-map
wf-0002-product-brief
wf-0048-expert-sharing
```

The `wf-` prefix identifies the grammar. The decimal ordinal is the collision-control core and is unique across all document kinds. The final kebab-case component is a non-authoritative recognition aid proposed from the initial H1 and frozen with the identifier. Normal allocation scans the complete record, chooses one greater than the highest existing ordinal, proposes the mnemonic, and refuses to write if the record is already invalid or the candidate collides.

Use lowercase ASCII letters, digits, and hyphens. Require an ordinal of at least four zero-padded digits, beginning at `0001`, and a mnemonic of 1–48 characters. The proposed grammar is:

```regex
^wf-[0-9]{4,}-[a-z0-9]+(?:-[a-z0-9]+)*$
```

The ordinal is never kind-specific, and the mnemonic never changes after assignment. This decision would govern ordinary single-working-tree allocation only. Merge collisions, correction before publication, migration, import, split/merge lineage, and link targeting remain later decisions.

## Why grammar and allocation belong together

A grammar can be syntactically valid while offering no safe way to choose the next value. Conversely, an allocation algorithm cannot be deterministic unless it knows which part of a token controls uniqueness. Evaluating them together avoids approving a readable format whose collision behavior is left to improvisation.

The normal path considered here is deliberately narrow:

1. One initialized project record is available locally.
2. All durable documents can be scanned before assignment.
3. The new document has a proposed H1.
4. No unresolved duplicate IDs or malformed metadata exist.
5. One process performs the write.

Concurrent branches and record merging violate those assumptions and require an explicit recovery policy later.

## Evaluation criteria

| Criterion | Meaning for Wayfinder |
| --- | --- |
| Readability | A person can recognize likely targets and mistakes in diffs and errors. |
| Stable meaning | Mutable project facts are not asserted by the token. |
| Deterministic allocation | The same valid pre-state and H1 produce the same proposed next ID. |
| Collision visibility | Conflicts are detected before writing or explicitly during merge validation. |
| Parser portability | Validation needs only byte/line operations and simple ASCII matching. |
| Sort behavior | Ordinary lexical order remains useful for modest project sizes. |
| International robustness | Titles remain unrestricted even if the technical token uses a restricted repertoire. |
| Migration practicality | Existing records can be assigned identifiers reproducibly. |

## Evidence synthesis

### 1. Keep the alphabet deliberately small

RFC 3986 identifies ASCII letters, digits, hyphen, period, underscore, and tilde as unreserved URI characters.^1 Wayfinder IDs do not initially need to be URIs, but choosing a subset of those characters avoids percent-encoding and reduces quoting problems across shells, Markdown, JSON catalogs, and future URI-shaped representations.

Lowercase ASCII plus hyphen separators provides one byte representation for every valid token. It avoids case-folding differences and the visually dense `camelCase` form. An eye-tracking study of programmer identifiers found no accuracy difference between camel case and underscores but faster recognition for the separated underscore style among its trained participants.^2 This is only adjacent evidence: it studied code identifiers, not hyphenated document IDs, and participant familiarity was a confound. It supports visible word separation, not a universal claim that hyphens are cognitively optimal.

**Implication:** use `[a-z0-9-]`, lowercase only, and hyphens between words. Do not allow spaces, underscores, punctuation, or percent-encoded alternatives.

### 2. Unicode support introduces a real normalization contract

Unicode permits multiple code-point sequences that look equivalent. Unicode Standard Annex #15 defines normalization forms so equivalent strings can receive a unique binary representation and requires conforming producers and tests to follow the specified algorithm.^3 Correct cross-runtime Unicode identifier handling therefore requires normalization, Unicode-version awareness, and decisions about scripts and confusable characters.

Wayfinder documents, H1s, and summaries should support arbitrary UTF-8. Restricting the technical ID mnemonic to ASCII does not restrict authored language, but automatic mnemonic generation will work incompletely for titles without ASCII letters. Silent transliteration is culturally and linguistically unreliable and varies by library.

**Implication:** the generator may propose a mnemonic only from ASCII letters and digits already present in the H1. When that yields no useful value, it must request an explicit ASCII mnemonic rather than inventing a transliteration. A future grammar version may add Unicode only with a complete normalization and confusable-character specification.

### 3. Human-readable components aid inspection but must remain non-authoritative

Alshammry and Lord report that simple numeric ontology identifiers are relatively difficult to read and make misuse harder to detect; their alternative combines semantic opacity with pronounceability and a checksum.^4 Software-comprehension research more broadly finds that identifier wording and segmentation affect developer comprehension, though results depend on task and familiarity.^2

This supports retaining a short mnemonic beside the numeric core. It does not justify inferring document meaning from that mnemonic. Persistent-identifier authorities recommend opacity precisely because embedded meaning can decay; Crossref advises against changeable facts in identifier suffixes.^5

**Implication:** derive the mnemonic once for recognition, freeze it, and direct readers to `Kind`, `Status`, `Summary`, and the H1 for authoritative meaning. A stale mnemonic alone is not a validation error and must not trigger renaming.

### 4. A global sequence is deterministic in the normal local workflow

A monotonic project-wide ordinal can be allocated using a complete scan and integer comparison. It needs no randomness, clock, cryptographic library, registry service, or language-specific Unicode behavior. A fixed minimum width gives useful lexical ordering through `9999`; allowing additional digits prevents an arbitrary terminal capacity.

The cost is coordination. Two branches created from the same state can both select the same next ordinal. Distributed-systems work treats uncoordinated unique-ID generation as a distinct problem because independent generators cannot rely on one shared next value.^6 UUIDs solve this problem probabilistically or structurally but give up the chosen level of inspectability.^7

**Implication:** use a sequence for ordinary local creation, detect duplicate ordinals as a hard validation error, and design merge-collision reallocation separately. Do not pretend the normal allocator is concurrency-safe.

### 5. The sequence must be global across kinds

Per-folder or per-kind counters encode current classification into identity and permit collisions such as `research-0007` and `decision-0007`. They also make a later kind correction look like an identity change. A single project-wide ordinal keeps classification in the `Kind` field and makes duplicate detection trivial.

MyPond's 36 decision records already demonstrate the usability of zero-padded chronological numbers within one class. Extending one global counter to every durable document changes the scope, so existing decision numbers should not automatically be treated as Wayfinder ordinals during migration; mapping policy remains a separate decision.

**Implication:** allocate from one sequence across the complete record, never from the current folder or kind.

### 6. Content hashes identify versions, not evolving logical records

Software Hash Identifiers are intrinsic, content-derived identifiers designed to pinpoint exact versions of software artifacts without a central registry.^8 That is valuable for integrity and reproducibility, but a content hash changes whenever the bytes change. Wayfinder has already defined `ID` as the identity of an evolving logical document, while `Updated` and version control record change over time.

**Implication:** do not hash document content, path, H1, or complete metadata to create the durable ID. Hashes may later identify snapshots or validation manifests, but not the universal document identity.

## Proposed grammar details

If the recommendation is accepted, the initial grammar would be:

| Component | Contract |
| --- | --- |
| Prefix | Literal `wf-`; a syntax marker that remains valid even if the skill is later renamed. |
| Ordinal | Decimal integer `1` or greater, padded to at least four digits; leading zeroes required below 1000. |
| Separator | One ASCII hyphen between prefix, ordinal, and mnemonic words. |
| Mnemonic | 1–48 characters; lowercase ASCII letters and digits in non-empty hyphen-separated words. |
| Total comparison | Byte-for-byte, case-sensitive comparison after syntax validation; no normalization or aliases. |
| Uniqueness | Both the complete token and parsed ordinal must be unique within the project record. |

Examples:

```text
valid:   wf-0001-project-map
valid:   wf-0048-expert-sharing
valid:   wf-10000-api-contract-v2
invalid: wf-0000-reserved
invalid: WF-0001-project-map
invalid: wf-001-product-map
invalid: wf-0001-product--map
invalid: wf-0001-projet_carte
```

The `v2` example is syntactically valid but should be discouraged if it describes a mutable version rather than a permanently distinct referent. Syntax validation cannot establish semantic durability.

## Proposed normal allocator

The eventual deterministic script should:

1. Locate the project-record root using an explicit argument or an already detected Wayfinder environment record.
2. Scan every durable Markdown document, not only the target folder.
3. Parse metadata strictly and stop without writing if any existing ID is malformed, duplicated, or has a duplicated ordinal.
4. Compute `next = maximum ordinal + 1`, using `1` for an empty record.
5. Format `next` with a minimum width of four digits.
6. Propose a mnemonic from the initial H1 by lowercasing ASCII, turning each run of non-ASCII/non-alphanumeric characters into one hyphen, trimming hyphens, and truncating only at a word boundary within 48 characters.
7. If the proposal is empty, misleading, or collides as a complete token, require an explicit valid mnemonic.
8. Show the complete candidate and target path before writing.
9. Re-scan immediately before the atomic write and abort if the state changed.
10. Write the ID once, then run full structural validation.

Steps 3 and 9 make failure deterministic: the script never silently skips a number, rewrites an existing ID, or resolves a collision by guessing another suffix.

## Options

### Option A: plain normalized mnemonic

Examples:

```text
product-brief
trusted-expert-handoff
decision-0032
```

Generate a lowercase ASCII kebab-case candidate from the H1. On collision, request a disambiguating mnemonic or append the next available integer.

**Benefits:** shortest and most readable; no redundant prefix or sequence; existing decision identities can often map naturally; paths and relationships remain pleasant to inspect.

**Costs:** the mnemonic carries all uniqueness pressure; collisions require semantic judgment or order-dependent suffixes; concurrent branches with the same topic collide silently until validation; authors have a stronger impulse to rename IDs when terminology changes.

**Best fit:** small records with centralized authorship and rare conceptual overlap.

### Option B: global sequence plus frozen mnemonic — recommended

Examples:

```text
wf-0001-project-map
wf-0002-product-brief
wf-0048-expert-sharing
```

Scan the complete record, allocate the next global ordinal, and append a proposed mnemonic frozen at creation.

**Benefits:** deterministic zero-dependency allocation; obvious collision core; readable diagnostics; easy sorting; no path or kind encoding; mnemonic collisions do not matter when ordinals differ.

**Costs:** longer IDs; sequence allocation is unsafe on concurrent branches without later collision handling; migration must assign global ordinals; the frozen mnemonic can become dated; global ordering may invite readers to infer chronology even when import order is administrative.

**Best fit:** a repository-owned record normally maintained through one visible working state, with validation at branch integration.

### Option C: mnemonic plus generated entropy or checksum

Examples:

```text
product-brief-k4m2p7
expert-sharing-7xq9da
```

Append a random, hash-derived, or pronounceable suffix to a normalized mnemonic.

**Benefits:** safer disconnected creation; retains some readability; avoids a shared counter; can include typo detection if a formal checksum is used.

**Costs:** randomness conflicts with deterministic reproduction; hashes derived from mutable input either change or must be frozen; short suffixes need quantified collision policy; portable entropy and encoding differ by environment; a custom pronounceable scheme adds code and conformance burden.

**Best fit:** records with frequent independent creation where UUID-like behavior is needed but fully opaque tokens are unacceptable.

## Recommendation

Choose **Option B: `wf-<global-ordinal>-<frozen-mnemonic>`**, with these boundaries:

1. Use one ordinal sequence for all durable document kinds.
2. Start at `0001`; require at least four digits and allow natural growth beyond `9999`.
3. Restrict tokens to lowercase ASCII letters, digits, and single hyphens.
4. Limit the mnemonic to 48 characters and truncate only on a word boundary.
5. Freeze both ordinal and mnemonic after assignment.
6. Treat the mnemonic as a recognition aid, never as current metadata.
7. Reject duplicate complete IDs and duplicate ordinals.
8. Stop allocation when the pre-existing record is structurally invalid.
9. Keep arbitrary-language text in the H1 and `Summary`; request an explicit ASCII mnemonic when safe automatic reduction is not possible.
10. Do not use content-derived hashes for evolving document identity.

This option gives deterministic normal operation and high diagnostic legibility with a small grammar that can be implemented consistently in multiple standard runtimes. Its known weakness—concurrent branches choosing the same ordinal—must be handled explicitly in the next decision rather than hidden behind optimistic retry behavior.

## Next decision

Define the assignment boundary: when an allocated ID becomes immutable and whether a newly created but unintegrated document may be re-keyed. After that boundary is accepted, separately define how merge collisions choose a winner and how a losing candidate is re-keyed without permitting arbitrary renames.

## Sources

1. Berners-Lee, T., Fielding, R., and Masinter, L. “[RFC 3986: Uniform Resource Identifier (URI): Generic Syntax](https://www.rfc-editor.org/rfc/rfc3986).” Internet Standard STD 66, 2005.
2. Sharif, B., and Maletic, J. I. “[An Eye Tracking Study on camelCase and under_score Identifier Styles](https://doi.org/10.1109/ICPC.2010.41).” *18th IEEE International Conference on Program Comprehension*, 2010, pp. 196–205.
3. Unicode Consortium. “[Unicode Standard Annex #15: Unicode Normalization Forms](https://www.unicode.org/reports/tr15/).” Version 17.0.0, revision 57, 2025.
4. Alshammry, N., and Lord, P. “[Identitas: Semantics-free and Human-readable Identifiers](https://doi.org/10.3233/AO-210252).” *Applied Ontology* 16(4), 2021, pp. 379–394.
5. Crossref. “[Constructing Your DOIs](https://www.crossref.org/documentation/member-setup/constructing-your-dois/).” Updated 2024-02-05; accessed 2026-09-13.
6. Dillinger, P. C., Farach-Colton, M., Tagliavini, G., and Walzer, S. “[Optimal Uncoordinated Unique IDs](https://arxiv.org/abs/2304.07109).” 2023 preprint.
7. Davis, K., Peabody, B., and Leach, P. “[RFC 9562: Universally Unique IDentifiers (UUIDs)](https://www.rfc-editor.org/rfc/rfc9562).” IETF Standards Track, 2024.
8. SWHID Working Group. “[SoftWare Hash Identifier Specification, Version 1.2](https://www.swhid.org/specification/v1.2/0.Introduction/).” Accessed 2026-09-13.
