# Initialization research 11: project-root manifest

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** What single root contract should let people and portable tools discover, interpret, and validate a Wayfinder project record?
- **Prior decisions:** Each document owns its metadata; indexes are generated; the structure has a stable semantic kernel plus enabled capability modules; integration-dependent ID rules require an explicit canonical baseline.
- **Decision status:** Option A, a strict `.wayfinder/manifest.json` plus a Markdown entrypoint, accepted by the skill owner on 2026-09-13.

## Executive conclusion

Use a strict, versioned JSON manifest at `<workspace-root>/.wayfinder/manifest.json`, while retaining a Markdown document inside the record as the human entrypoint. The manifest declares the record root, entrypoint, canonical baseline, enabled modules, and every generated artifact. Tools find the nearest manifest by walking upward without crossing the containing version-control boundary, then resolve all declared paths relative to the workspace or record root under explicit containment rules.

This is Option A below. It keeps machine control data small, typed, and dependency-light while preserving Markdown for explanation and navigation. The manifest is structural authority; the human entrypoint remains content authority for orientation. Neither duplicates the other's role.

## Proposed v1 shape

For a repository like MyPond, the manifest would resemble:

```json
{
  "format": "wayfinder-project-record",
  "schemaVersion": 1,
  "recordRoot": "docs",
  "entrypoint": "README.md",
  "canonicalBaseline": {
    "kind": "git-ref",
    "ref": "refs/heads/main"
  },
  "modules": [
    {
      "id": "product",
      "root": "product",
      "entrypoint": "product/product-brief.md"
    },
    {
      "id": "research",
      "root": "research",
      "entrypoint": "research/README.md"
    },
    {
      "id": "decisions",
      "root": "decisions",
      "entrypoint": "decisions/README.md"
    },
    {
      "id": "architecture",
      "root": "architecture",
      "entrypoint": "architecture/README.md"
    },
    {
      "id": "development",
      "root": "development",
      "entrypoint": "development/README.md"
    }
  ],
  "generatedArtifacts": [
    {
      "path": ".wayfinder/generated/document-catalog.json",
      "generator": "document-catalog-v1"
    }
  ]
}
```

The example illustrates the contract, not a decision that all five MyPond modules are universal. A later initialization-profile decision will determine which modules a particular project enables.

## Two roots with distinct roles

The recommendation distinguishes:

- **Workspace root:** the directory containing `.wayfinder/manifest.json`; normally the repository root.
- **Record root:** the `recordRoot` directory containing the durable project knowledge, such as `docs/` or `.`.

This lets an agent invoked from implementation code discover a sibling `docs/` record without searching arbitrary directories. It also permits a plan-only repository to use `recordRoot: "."`.

All document, entrypoint, module, and generated-artifact paths are interpreted relative to the record root unless the field explicitly says otherwise. The canonical Git ref is resolved in the version-control repository containing the workspace root.

## Required fields and authority

| Field | Required meaning |
| --- | --- |
| `format` | Literal `wayfinder-project-record`; prevents another JSON file from being mistaken for this contract. |
| `schemaVersion` | Positive integer selecting one exact manifest schema and validation behavior. |
| `recordRoot` | Workspace-relative path to the durable record; `.` is allowed. |
| `entrypoint` | Record-relative Markdown path for human and agent orientation. |
| `canonicalBaseline` | Typed declaration of the history against which integration and immutability are evaluated. |
| `modules` | Ordered list of enabled capability IDs, roots, and entrypoints. |
| `generatedArtifacts` | Ordered list of exact record-relative output paths and registered generator IDs. |

The manifest owns these facts. README tables may explain or link them but do not independently redefine them. Repeated human-facing module maps should eventually be generated or validated against the manifest.

## Canonical-baseline forms

Version 1 should recognize two tagged forms:

### Git ref

```json
{
  "kind": "git-ref",
  "ref": "refs/heads/main"
}
```

- `ref` must be fully qualified rather than relying on ambiguous shorthand.
- Scripts resolve it locally and never fetch implicitly.
- A missing ref is permitted only during the initialize workflow before the first canonical integration; other workflows report it as unavailable.
- The resolved commit, not the mutable ref spelling alone, is captured in operation plans and reports.

### Published snapshot

```json
{
  "kind": "snapshot",
  "path": ".wayfinder/baselines/canonical.json",
  "sha256": "<64 lowercase hexadecimal digits>"
}
```

- `path` is workspace-relative and must remain beneath `.wayfinder/baselines/`.
- The digest authenticates the exact declared snapshot bytes; it is not a document ID.
- Snapshot creation and publication require a later adapter contract.
- A missing snapshot is allowed only during first initialization.

These forms provide the same logical role without pretending Git and non-Git storage have identical mechanics.

## Discovery algorithm

Tools should accept an explicit `--workspace-root`. If omitted, they:

1. Start from the supplied path or current working directory after resolving it physically.
2. Check for `.wayfinder/manifest.json` in that directory.
3. Walk to the parent and repeat.
4. Stop before crossing the containing version-control root; if no version-control root exists, stop at the filesystem root.
5. Select the nearest manifest only.
6. Fail if the selected file is invalid; do not skip it and continue to a parent manifest.
7. Fail clearly if none is found; do not infer a record from a `docs/` directory or README.

An explicit root must contain the exact manifest path. It is not a general search hint.

## Strict parsing and path rules

The v1 parser should:

- Accept UTF-8 JSON without comments or a byte-order mark.
- Reject duplicate object names. RFC 8259 notes that unique object names are necessary for interoperable behavior because duplicate handling differs between implementations.^1
- Reject unknown fields for the selected schema version rather than silently discarding future policy.
- Reject non-integer `schemaVersion`, unsupported versions, and extension values not registered by that version.
- Require arrays to preserve their declared order while enforcing unique module IDs, module roots, module entrypoints, artifact paths, and generator/path pairs where applicable.
- Use `/` as the manifest path separator and reject absolute paths, backslashes, empty segments, `..`, and NUL.
- Permit `.` only as the complete `recordRoot` value, not as a path segment elsewhere.
- Resolve paths physically and prove containment before reading or writing; symlink policy remains an environment-security decision but must never permit escape.
- Serialize generated manifests with UTF-8, two-space indentation, a terminal newline, and one documented key order. JSON object order remains semantically insignificant.

A bundled JSON Schema may document and test the structure, but runtime scripts should implement the small required checks with standard-library JSON parsing rather than require a general JSON Schema package. JSON Schema Draft 2020-12 remains the reference vocabulary for the declarative schema artifact.^2

## Evidence synthesis

### 1. Machine-actionable metadata needs an explicit representation

The FAIR principles emphasize that metadata should support machine discovery and use through formal, shared representations.^3 Later work on machine-actionable metadata models reports that translating prose checklists into schemas makes entities, relationships, attributes, and constraints unambiguous and reusable.^4 Wayfinder is not a scientific data repository, so global FAIR compliance is not the target. The applicable principle is that tools should not have to infer foundational routing and authority facts from prose.

**Implication:** record structural configuration once in a typed manifest and validate it before traversing the record.

### 2. Keep human navigation separate but connected

Information-foraging research models navigation using proximal cues—information scent—that help a reader decide which path is likely to satisfy a goal.^5 A compact JSON manifest is poor explanatory prose even if it is excellent machine input. Conversely, a Markdown knowledge map can provide meaningful labels and summaries but is awkward as a nested typed configuration language.

**Implication:** `entrypoint` must name a human-readable Markdown map. The manifest should route tools to it, not replace it.

### 3. External representations change the work people must perform

Zhang and Norman's representational analysis treats cognition as distributed between internal and external representations and shows that representation affects task structure.^6 Applied cautiously, this supports externalizing facts such as enabled modules and canonical baseline rather than requiring each agent to reconstruct them from directory names and Git conventions.

The research does not select JSON or a hidden-directory name. Those are engineering choices driven by parsing portability and separation of roles.

**Implication:** make foundational state inspectable and stable, while keeping the human representation aligned with the machine contract.

### 4. JSON offers the narrowest portable parsing surface

RFC 8259 defines JSON as a language-independent interchange format and identifies unique object names as the interoperable form.^1 JSON parsing is available in common standard runtimes, including Python and ECMAScript, without installing a YAML or TOML library.^7,8 Its limitations—no comments, insignificant object order, and permissive duplicate handling in some libraries—can be addressed by a strict Wayfinder profile and deterministic writer.

TOML is designed for readable configuration with clear semantics,^9 while YAML is designed as a human-friendly cross-language serialization language.^10 Both are credible formats. Neither is as consistently available in baseline runtimes, and YAML's richer representation model increases the conformance work for multiple dependency-free parsers.

**Implication:** use a deliberately small JSON subset and keep commentary in Markdown rather than extending the manifest syntax.

### 5. Versioning must fail safely

JSON Schema separates core representation from validation vocabularies and uses explicit dialect versions.^2 A runtime that silently ignores a new field could miss a new security, authority, or generation rule while claiming compatibility.

**Implication:** `schemaVersion` selects an exact closed set of keys. Unknown versions and unknown keys fail with actionable diagnostics. Backward-compatible migration should be performed by an explicit future command, never silently during ordinary use.

## Options

### Option A: strict `.wayfinder/manifest.json` plus Markdown entrypoint — recommended

Use the proposed v1 shape and discovery rules. JSON holds machine control data; `entrypoint` points to the human knowledge map.

**Benefits:** dependency-light parsing across runtimes; strict typing and schema versioning; deterministic discovery; explicit canonical baseline; module and generated-output inventory in one place; agents need not load prose to establish machine scope.

**Costs:** JSON does not allow comments; hand editing requires correct punctuation; the strict profile needs custom duplicate-key and path checks; two linked representations must remain aligned; `.wayfinder/` adds a tooling directory to the repository.

**Best fit:** a portable skill whose scripts need one unambiguous contract while people work primarily in Markdown.

### Option B: one visible Markdown control document

Place all root configuration in a constrained block inside `WAYFINDER.md` or the record's README and use the same file as the human entrypoint.

**Benefits:** one visible file; configuration can sit beside explanations; easy for people to discover; consistent with document-level metadata blocks.

**Costs:** nested module, baseline, and artifact records require a bespoke mini-language; prose edits can accidentally affect parsing; every tool must parse Markdown structure; runtime agents load control syntax with orientation text; one file has competing human and machine roles.

**Best fit:** very small records with flat configuration and no complex generation or integration policy.

### Option C: TOML or YAML manifest

Use `wayfinder.toml` or `wayfinder.yaml` at the workspace root.

**Benefits:** comments and friendlier hand editing; TOML has relatively obvious configuration semantics; YAML is familiar in repositories; both can express the required nested data.

**Costs:** standard-library availability varies; multiple implementations have version and duplicate-key differences; YAML has a substantially larger language surface; bundling or writing parsers conflicts with the low-dependency goal; combining TOML and YAML as alternatives would itself create conformance work.

**Best fit:** an environment with one guaranteed runtime and parser dependency.

### Option D: inferred conventions without a manifest

Infer the record from `docs/`, README links, Git's default branch, known folder names, and generated-file headers.

**Benefits:** no control file; familiar repositories may work immediately; minimal initialization ceremony.

**Costs:** ambiguous roots and baselines; impossible to distinguish absent from disabled modules; folder names become accidental schema; non-Git operation lacks an authority boundary; tools repeatedly rediscover state; validation cannot distinguish convention from coincidence.

**Best fit:** exploratory one-off assistance, not a durable multi-workflow record.

## Recommendation

Choose **Option A: strict JSON manifest plus Markdown entrypoint**, with these binding policies:

1. The exact discovery path is `.wayfinder/manifest.json` beneath the workspace root.
2. `recordRoot` locates the project record relative to that workspace.
3. `entrypoint` names its human-readable Markdown knowledge map.
4. `format` and integer `schemaVersion` identify one closed schema.
5. `canonicalBaseline` is a tagged `git-ref` or published `snapshot` declaration.
6. `modules` explicitly lists enabled capabilities, roots, and entrypoints.
7. `generatedArtifacts` lists exact outputs and registered generator IDs; use no globs in v1.
8. The manifest is authoritative for structural facts; prose may explain but not redefine them.
9. Discovery chooses the nearest manifest, stops at the version-control boundary, and never infers a missing one.
10. Parsing rejects duplicate keys, unknown keys, unsafe paths, and unsupported versions.
11. All external actions remain explicit; resolving a Git ref does not authorize fetching.
12. Runtime validation uses standard-library parsing and bundled checks; a JSON Schema artifact is documentation and test evidence, not a mandatory dependency.

This contract supplies the stable anchor needed by initialization, validation, update, retrieval, and collision handling while preserving the user's requirement that ordinary agents load only task-relevant context.

## What acceptance would change now

The skill would record the manifest's role and v1 shape. Implementation should wait until the next decision establishes the kernel documents and module profiles that the initializer will place into `modules`. Once those are accepted, the manifest schema and dependency-free parser become appropriate first scripts.

## Deferred decisions

Accepting Option A would not yet answer:

- Which kernel documents every record contains.
- Which named initialization profiles are provided.
- The complete module vocabulary and module-specific templates.
- Whether nested Wayfinder workspaces are permitted.
- The snapshot adapter's file format and publication command.
- The exact generated catalog and index formats.
- The environment-adapter/runtime matrix.

## Next decision if Option A is accepted

Define initialization profiles as a coherent package: the universal kernel, the initial named profiles, module selection rules, and the software-product profile that should reproduce the useful shape of MyPond.

## Sources

1. Bray, T., ed. “[RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259).” IETF Internet Standard, 2017.
2. JSON Schema Project. “[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12).” Accessed 2026-09-13.
3. Wilkinson, M. D., et al. “[The FAIR Guiding Principles for Scientific Data Management and Stewardship](https://doi.org/10.1038/sdata.2016.18).” *Scientific Data* 3, 2016, 160018.
4. Batista, D., Gonzalez-Beltran, A., Sansone, S.-A., and Rocca-Serra, P. “[Machine Actionable Metadata Models](https://doi.org/10.1038/s41597-022-01707-6).” *Scientific Data* 9, 2022, 592.
5. Pirolli, P. “[Rational Analyses of Information Foraging on the Web](https://doi.org/10.1207/s15516709cog0000_20).” *Cognitive Science* 29(3), 2005, pp. 343–373.
6. Zhang, J., and Norman, D. A. “[Representations in Distributed Cognitive Tasks](https://doi.org/10.1207/s15516709cog1801_3).” *Cognitive Science* 18(1), 1994, pp. 87–122.
7. Python Software Foundation. “[`json` — JSON Encoder and Decoder](https://docs.python.org/3/library/json.html).” Accessed 2026-09-13.
8. Ecma International. “[ECMAScript Language Specification: `JSON.parse`](https://tc39.es/ecma262/multipage/structured-data.html#sec-json.parse).” Accessed 2026-09-13.
9. TOML Project. “[TOML v1.0.0](https://toml.io/en/v1.0.0).” Accessed 2026-09-13.
10. YAML Language Development Team. “[YAML 1.2.2 Specification](https://yaml.org/spec/1.2.2/).” 2021.
