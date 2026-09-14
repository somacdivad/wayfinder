# Initialization research 16: executable schema package and portability contract

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** How should Wayfinder package its exact schemas, grammars, templates, fixtures, taxonomy declarations, environment detection, runtime adapters, command interface, and initialization transaction data so independently implemented tools produce the same safe result without requiring installation?
- **Prior decisions:** The record uses a strict versioned manifest, constrained visible Markdown, stable document and question IDs, a purpose-based kind registry, a bounded relationship graph, a generated catalog, and a digest-bound recoverable initialization transaction. Runtime users must not load maintainer rationale.
- **Decision status:** Option A accepted by the user on 2026-09-13.

## Executive conclusion

Prefer **Option A: one versioned executable contract with capability-probed, conformance-certified standard-library adapters**.

Wayfinder should not make prose in `SKILL.md`, templates, JSON Schema, and three scripts four competing definitions of validity. Version 1 should instead be one named contract package whose resources have distinct, non-overlapping authority: a human-readable normative specification for semantics and algorithms; closed machine schemas and a small ABNF-like grammar for structure; literal templates for byte-stable rendering; and shared positive, negative, and golden-output fixtures. A contract manifest records the version and digest of every governed resource. Every adapter declares the same contract version and must pass the same suite before release.

At runtime, an agent runs one small detector once on first entry to Wayfinder. The detector probes candidate adapters by executing their self-test, rather than trusting an operating-system label or version string alone, and returns a JSON selection record containing the exact executable and adapter digest. The agent reuses that invocation for the session. No detector result is written into the project record, no dependency is installed, and no agent is allowed to emulate a missing deterministic command manually.

The initial certified family should target Python, Node.js, and PowerShell using only their standard libraries. Multiple implementations increase reach but also create correlated specification mistakes and semantic drift; therefore an adapter is not “supported” merely because it starts. It must reject the same invalid fixtures, emit the same normalized plans and generated artifacts, and survive the same recovery scenarios. If no certified adapter passes its probe, the workflow stops with a diagnostic and the user can choose another environment.

The initializer should be a noninteractive file-oriented CLI. It accepts a strictly validated semantic proposal, builds an inspectable bundle containing exact payload bytes and a canonical operation plan, and applies only a user-confirmed SHA-256 digest. Application copies that bundle into a workspace-local operation directory, writes immutable hash-chained journal events before and after consequential steps, creates each target exclusively, and publishes the manifest last. An alternate certified adapter can inspect or recover the operation because adapter identity is evidence in the journal, not a condition for resumption.

This recommendation is an engineering synthesis. Serialization standards support strict UTF-8 JSON and explicit duplicate handling; conformance and differential-testing work supports common fixtures across implementations; research on multi-version programs warns that independently written implementations can share failures; reproducible-build work supports byte-identical derived outputs; portability practice supports capability tests; and transaction-recovery and file-system studies support write-ahead recovery evidence without promising universal multi-file atomicity. No reviewed study tests this exact LLM-operated Markdown skill or establishes that three adapters are the optimal number.

Sources were accessed on 2026-09-13.

## Decision boundary

This decision would settle:

- where normative runtime contracts, generated-document templates, adapter code, and maintainer-only tests live;
- how those resources are versioned and checked for drift;
- the exact v1 module/subject declaration shape;
- the canonical byte and serialization rules needed for equivalent adapters;
- how an agent selects and reuses one runtime;
- the common noninteractive command and result interface;
- the initialization proposal, bundle, plan, digest, journal, and recovery interchange formats; and
- what “portable” and “certified” mean for Wayfinder.

It would not settle:

- whether and how initialization adopts an existing unmanifested document collection;
- the full semantic Interview, Update, Validate, or Use workflows;
- external-link network checking or caching;
- project-local templates or executable extensions;
- package distribution and installation outside this repository; or
- long-term migration policy between schema major versions.

## Evaluation criteria

| Criterion | Requirement |
| --- | --- |
| Semantic singularity | One versioned contract governs all adapters; generated examples and tests do not silently redefine it. |
| Zero-install operation | A supported environment uses a bundled script and built-in libraries only. |
| Behavioral equivalence | Different certified adapters accept, reject, render, hash, and recover the same fixtures consistently. |
| Human inspectability | A maintainer can read the rules; a runtime agent can inspect the proposal and diagnostics without reading maintainer research. |
| Deterministic publication | Confirmed inputs bind to exact bytes, paths, order, and preconditions. |
| Conservative recovery | A different certified adapter can understand interrupted state and never guesses whether unrelated work may be removed. |
| Progressive disclosure | Normal use loads only the workflow reference and executes assets/scripts; tests and research remain maintainer-only. |
| Bounded evolution | Schema versions fail closed and changes require fixtures and migration decisions. |

## Evidence synthesis

### 1. A schema needs both a precise contract and conformance evidence

JSON Schema Draft 2020-12 provides a published vocabulary for structural constraints, bundling, and validation, but a schema cannot express all Wayfinder algorithms or Markdown semantics.^1 NIST describes conformance testing as measuring whether an implementation faithfully implements a specification and emphasizes that tests are bounded by what the specification defines.^2 Sarikaya and Wiles' work on TTCN similarly distinguishes a machine-processable test notation from the operational semantics it tests.^3

**Implication:** publish an explicit normative contract before treating fixtures as authority. Use JSON Schema for closed JSON shapes, a small textual grammar for Wayfinder Markdown, prose/pseudocode for algorithms, and test vectors for observable behavior. A passing suite increases confidence; it does not make an unspecified behavior valid.

### 2. Multiple implementations expose disagreements but do not guarantee correctness

McKeeman's differential-testing method feeds comparable systems the same mechanically generated cases and treats divergent outputs, crashes, or loops as bug candidates.^4 This is directly useful when Python, Node, and PowerShell adapters should implement one contract.

Knight and Leveson's experiment with 27 independently produced programs found coincident failures substantially more often than the independence assumption predicted.^5 Their study concerned fault-tolerant N-version programming, not portable tooling, but it warns against treating implementation diversity as proof: ambiguous specifications can induce correlated errors.

**Implication:** compare adapters against each other and against explicit expected results. Every discovered disagreement becomes a minimized permanent fixture and, when necessary, a clarified contract rule. Do not vote among adapters or accept the majority output automatically.

### 3. Example fixtures should be supplemented by properties and invalid cases

Claessen and Hughes' QuickCheck work demonstrated that executable properties plus generated inputs can expose errors beyond hand-selected examples.^6 Model-based conformance literature likewise evaluates whether test suites cover specified behaviors and known fault classes.^7

**Implication:** the maintainer suite should contain:

- positive examples for every registered construct;
- one negative example for each rejection rule and common near miss;
- golden byte outputs for manifests, documents, previews, catalogs, plans, and journals;
- cross-adapter differential runs;
- generated property tests for IDs, paths, ordering, escaping, graph cycles, and interrupted phases; and
- regression fixtures minimized from every defect.

Property generators belong to maintenance, not runtime. Adapter `probe` runs only a small fixed known-answer set so first-use detection remains fast and deterministic.

### 4. Reproducibility requires byte-level controls, not merely equivalent parsed values

Lamb and Zacchiroli define reproducibility around bit-for-bit identical outputs and connect it with quality assurance and supply-chain integrity.^8 Wayfinder is generating text rather than binaries, but the core benefit transfers: a reviewer-confirmed digest is meaningful only if encoding, newlines, ordering, escaping, and templates are controlled.

RFC 8259 requires UTF-8 for interoperable JSON exchange, recommends unique object names, and documents divergent behavior when names repeat.^9 RFC 8785 defines a canonical JSON representation specifically so hashing and signing can be reliably repeated.^10 CommonMark 0.31.2 supplies a fixed reference for the Markdown constructs Wayfinder embeds, including HTML comments.^11

**Implication:** use UTF-8 without a byte-order mark and LF newlines for governed text. Reject malformed Unicode and duplicate JSON object names. Use RFC 8785 JCS for digest-bound control objects, restricted to I-JSON values; hash raw payload bytes and list those hashes in the canonical plan. Pin the supported CommonMark reference even though the Wayfinder block grammar is stricter than CommonMark.

### 5. Portability should be tested as capability, then cached at the workflow level

GNU Autoconf's mature portability practice runs feature tests and caches their results instead of assuming platform labels imply capabilities.^12 POSIX.1-2024 defines a portable shell language and command lookup for Unix-like systems, but POSIX shell itself has no standard JSON parser.^13 Python, Node.js, and PowerShell all currently have supported release lines and built-in JSON, hashing, and file APIs, but their release schedules differ and installed availability cannot be inferred from the OS.^14,15,16

**Implication:** use shell only to locate and invoke a real adapter. A detector validates an exact adapter by running `probe`; it does not parse or generate Wayfinder data. Return the resolved executable path and adapter digest, and reuse them for the active agent session. Re-probe only if the executable disappears, its script digest changes, or a command reports a capability mismatch.

### 6. A stable machine interface reduces agent interpretation

POSIX utility conventions distinguish command arguments, standard output, standard error, and exit status.^13 The practitioner-authored Command Line Interface Guidelines recommend primary output on stdout, diagnostics on stderr, nonzero failure status, structured JSON when machine consumption matters, and file/stdin/stdout support where appropriate.^17 These are practical conventions rather than controlled empirical results.

**Implication:** every adapter implements the same command names and file arguments, emits one closed JSON result envelope to stdout, sends explanatory diagnostics to stderr, and never prompts interactively. Large proposed content travels through files, not shell quoting or model-parsed console prose.

### 7. Recovery information must precede the writes it explains

ARIES formalized write-ahead logging and recovery using structured log records.^18 SQLite's documented rollback protocol similarly writes recovery information before changing primary data and detects unfinished journals on a later open.^19 Wayfinder does not need database isolation, page logging, or SQLite as a dependency; the transferable principle is to persist enough intent and prior state before a consequential write.

Pillai and colleagues found materially different crash-consistency behavior across six Linux file systems and numerous vulnerabilities in real applications.^20

**Implication:** write immutable event files with hashes before and after each publication step, keep exact target hashes in the plan, and inspect the longest valid event prefix during recovery. Promise no-overwrite behavior and conservative recovery, not power-loss durability or universal atomicity.

### 8. Templates should hide syntax variability without becoming a second program

Parnas argues for decomposing systems around design decisions likely to change rather than procedural steps.^21 The Wayfinder Markdown grammar, field order, and generated markers are such decisions; project prose is not. Shipman and Marshall's work on incremental formalization cautions against forcing users to manipulate more formal structure than their work requires.^22

**Implication:** scripts, not agents, own punctuation, delimiters, ordering, escaping, and generated regions. Templates are literal versioned byte resources with named one-pass slots, not a general conditional template language. The agent supplies reviewed content in a structured proposal. Missing, unknown, repeated, or unexpanded reserved slots are errors. Templates never re-render an authored document after publication.

## Proposed contract package

### Runtime and maintenance layout

```text
skills/wayfinder/
├── SKILL.md
├── references/
│   ├── runtime.md
│   ├── initialize.md
│   └── contracts/
│       └── v1.md
├── assets/
│   └── contract-v1/
│       ├── contract.json
│       ├── grammar.abnf
│       ├── schemas/
│       │   ├── manifest.schema.json
│       │   ├── proposal.schema.json
│       │   ├── plan.schema.json
│       │   ├── event.schema.json
│       │   ├── result.schema.json
│       │   └── catalog.schema.json
│       └── templates/
│           ├── map.md
│           ├── brief.md
│           ├── register.md
│           ├── evidence.md
│           ├── decision.md
│           ├── guide.md
│           └── index.md
├── scripts/
│   ├── detect-runtime.sh
│   ├── detect-runtime.ps1
│   └── adapters/
│       ├── wayfinder.py
│       ├── wayfinder.mjs
│       └── Wayfinder.ps1
└── assets/contract-v1/conformance/v1/
    ├── cases.json
    ├── inputs/
    └── expected/
```

Normal runtime routing is:

1. `SKILL.md` identifies the requested runtime workflow.
2. The agent reads `references/runtime.md` and runs one detector if no valid adapter selection exists in the current session.
3. The agent reads only the requested workflow reference, such as `references/initialize.md`.
4. The adapter reads contract assets and templates directly. The agent does not load all schemas or templates into model context.

Maintainer research, design history, tooling, demonstrations, and certification evidence live in the separate explicit-only `$wayfinder-maintainer` skill. The governed conformance fixtures remain inside the Wayfinder contract package because adapters must be able to verify their bytes without loading maintainer instructions.

### Authority inside the package

The package is one versioned contract, but each resource owns a different question:

| Resource | Authority |
| --- | --- |
| `references/contracts/v1.md` | Normative semantic meanings, invariants, algorithms, and error conditions. |
| `contract.json` | Closed registries, field order, exact delimiters, path rules, generator IDs, adapter requirements, and governed-resource digests. |
| `grammar.abnf` | Exact accepted line syntax for metadata, relationship, question, source, history, and generated markers. |
| JSON Schemas | Closed structural shape and scalar constraints for JSON interchange objects. |
| Templates | Exact authored shells and generated-region placement for new bytes. They do not define semantic validity. |
| Conformance fixtures | Expected observable examples and rejection cases. They do not legalize behavior absent from the normative contract. |

`contract.json` identifies every resource by record-relative package path and SHA-256. An adapter refuses a package with a missing, extra governed, or digest-mismatched resource. A contract change requires a version decision; an editorial clarification may retain the version only if it changes no accepted/rejected instance or output byte.

### Byte profile

All governed Markdown, ABNF, templates, and JSON use:

- well-formed Unicode encoded as UTF-8 without BOM;
- LF (`0A`) line endings;
- exactly one terminal LF for Markdown/templates and ordinary pretty JSON;
- no trailing spaces in generated lines;
- lowercase 64-character hexadecimal SHA-256 values;
- Unicode normalization form NFC for accepted user text and paths, with a diagnostic rather than silent normalization;
- ordinal Unicode-code-point ordering only where a rule explicitly sorts free text;
- numeric ordinal ordering for `wf-` and `wfq-` IDs; and
- RFC 8785 JCS bytes for digest-bound control objects.

User prose remains byte-preserved after proposal acceptance except for the preflight rejection of invalid encoding, forbidden delimiter collisions, and non-NFC input. Adapters never apply smart punctuation, paragraph reflow, heading rewriting, or platform newline conversion.

## Proposed v1 taxonomy declaration

Decision 11 fixed the manifest's top-level fields but left the nested module shape open. Each module entry should now be:

```json
{
  "id": "product",
  "root": "product",
  "entrypoint": "product/product-brief.md",
  "subjects": [
    {
      "id": "audiences-and-market",
      "kind": "document",
      "entrypoint": "product/audiences-and-market.md"
    },
    {
      "id": "collaboration-and-sharing",
      "kind": "collection",
      "root": "product/collaboration-and-sharing",
      "entrypoint": "product/collaboration-and-sharing/README.md"
    }
  ]
}
```

Rules:

- Module IDs are the registered standard IDs or an approved `local-<slug>`; subject IDs are lowercase ASCII slugs unique within their module.
- All `root` and `entrypoint` values are record-relative. Module roots are pairwise disjoint, and every module entrypoint is contained in its module root.
- `subjects` is required, may be empty, and preserves the user's confirmed navigation order rather than priority.
- A `document` subject owns exactly its entrypoint and has no `root`.
- A `collection` subject owns its entrypoint and authored documents contained beneath its root. Its root is contained in the module root.
- Subject collection roots do not overlap or nest in v1. Document-subject entrypoints cannot fall inside a collection subject.
- A module entrypoint and other documents outside a declared subject remain valid module-level knowledge with `subject: null`; a project need not classify every file.
- Catalog subject keys are the unambiguous composite `<module-id>/<subject-id>`.
- Module and subject membership derive only from the manifest and physically contained paths. Documents do not duplicate `Module` or `Subject` metadata.
- Moving a document across a module or subject boundary changes classification but not document identity and therefore belongs to the Update workflow.

This union represents both MyPond patterns: a focused product subject can be one file, while a decision subject can be a folder with its own index. It does not require empty directories or a manifest edit for every evidence brief when no finer research taxonomy is useful.

## Proposed template contract

Templates are immutable skill-owned assets for creating new documents. They use reserved one-pass slots such as `{{WF_TITLE}}`, `{{WF_METADATA}}`, and `{{WF_BODY}}`.

The renderer must:

1. select a template only from the registered `Kind` and contract version;
2. validate the structured slot values before substitution;
3. replace each registered slot exactly once in template order without recursively interpreting inserted text;
4. reject missing, unknown, duplicate, or unexpanded `{{WF_...}}` slots;
5. render syntax-owned blocks from typed proposal data rather than accepting preformatted metadata or relationship strings;
6. validate the resulting complete document; and
7. include its exact bytes and hash in the proposal bundle.

Profiles select document sets and semantic prompts, not alternative punctuation. Project-local templates are forbidden in v1. Templates are not copied into the initialized record as editable authorities. The operation plan records the contract and template digest that produced each file, but published authored metadata does not retain template provenance because the file becomes independently maintained after creation.

## Proposed adapter and detection contract

### Certified adapters

The first release should include functionally complete standard-library-only adapters for:

- supported Python 3, with 3.11 as the minimum language baseline;
- supported Node.js LTS, with major 22 as the minimum baseline; and
- PowerShell 7.4 or newer, plus Windows PowerShell 5.1 only where its separate probe and full fixture lane pass.

The version floors constrain syntax; `probe` determines actual usability. The support matrix is maintained with current upstream lifecycle information. Wayfinder never downloads a runtime or package manager dependency.

### Detection

On first runtime use in an agent session:

- a POSIX-like shell invokes `sh scripts/detect-runtime.sh --json`;
- PowerShell invokes `scripts/detect-runtime.ps1 -Json`;
- the detector checks candidates in a documented stable order;
- each candidate is invoked with `probe` and must return the expected contract version, adapter ID, adapter file digest, runtime details, and fixed known-answer results;
- the detector returns one selection record with the resolved executable path and exact argument prefix; and
- the agent retains that record in session context and invokes the selected adapter directly afterward.

The detector itself does not parse manifests, render files, inspect Git history, or mutate the workspace. A mere version match is insufficient. A selection is invalidated if the executable is unavailable, adapter digest changes, contract digest changes, or the adapter reports a capability error. The agent may then run detection once again and report the transition.

If no candidate passes, the result lists every candidate checked and its rejection. The workflow stops; the agent must not reproduce the command manually, install software, or silently weaken validation.

### Cross-adapter certification

An adapter release is certified only if it:

- passes every positive and negative fixture independently;
- emits byte-identical golden plans, payloads, catalogs, generated regions, and journal events wherever the contract declares deterministic output;
- returns equivalent normalized diagnostics and error codes, allowing only registered runtime-detail differences;
- passes pairwise differential runs against all already certified adapters;
- passes interruption tests at every journal boundary; and
- introduces regression fixtures for every corrected adapter disagreement.

The contract version, not an adapter, is authority. An alternate certified adapter may resume an operation if it validates the contract package, raw plan digest, payload hashes, and journal chain.

## Proposed common command surface

All adapters implement these noninteractive commands with the same options and semantics:

| Command | Side effects | Purpose |
| --- | --- | --- |
| `probe` | None | Verify adapter, contract assets, and fixed known-answer capabilities. |
| `discover` | None | Resolve an explicit or nearest existing Wayfinder workspace and validate its manifest boundary. |
| `initialize-plan` | Writes only to an explicit non-record bundle directory | Validate a semantic proposal, render exact payloads and preview, and produce a canonical plan and digest. |
| `initialize-apply` | Confirmed workspace transaction | Recheck preconditions and publish exactly the confirmed bundle with journaling and no overwrite. |
| `initialize-recover` | Inspect by default; resume or rollback only when explicitly selected | Validate and conservatively resolve one interrupted operation. |
| `validate` | None unless a future explicit repair flag is designed | Run the registered deterministic checks against a bundle, stage, or live record. |
| `generate` | Writes only declared generated paths/regions under an explicit mode | Recompute registered derivations from authoritative inputs. |

Every command accepts paths through arguments or an input JSON file; it never asks interactive questions. It writes exactly one UTF-8 JSON result envelope to stdout:

```json
{
  "format": "wayfinder-command-result",
  "schemaVersion": 1,
  "ok": true,
  "command": "initialize-plan",
  "code": "ok",
  "data": {}
}
```

Failures set `ok: false`, use a registered stable `code`, include path/field/expected/actual/remediation fields when applicable, and return nonzero. Human diagnostics go to stderr. Expected exit classes are `0` success, `2` command or input contract error, `3` failed precondition/conflict, `4` record validation failure, `5` recovery required, and `70` unexpected internal failure. The JSON code, not the process number alone, carries precise meaning.

Commands never fetch, install, commit, merge, push, open a browser, call external services, or infer semantic interview answers. Filesystem and Git reads remain bounded by the accepted workspace, baseline, containment, and symlink policies.

## Proposed initialization interchange

### Semantic proposal

The agent translates the user-confirmed bootstrap and taxonomy interview into a closed `wayfinder-initialize-proposal` JSON document. It contains structured manifest declarations, document identities and kinds, typed question/source/relationship data, section bodies, epistemic markers, omitted modules and reasons, baseline, and target paths. It does not contain already-formatted Wayfinder metadata or generated indexes.

`initialize-plan` rejects unknown fields, duplicate names, delimiter collisions, invalid paths, unregistered values, missing required content, and contradictions detectable from the structured data. The proposal is an input to deterministic rendering, not durable project authority.

### Plan bundle

The agent supplies an explicit temporary bundle directory outside the final record paths. The command exclusively creates:

```text
bundle/
├── plan.json
├── preview.md
└── payload/
    ├── 0001
    ├── 0002
    └── ...
```

`plan.json` is an RFC 8785 canonical JSON object containing:

- literal format and schema version;
- contract version and complete contract-package digest;
- normalized workspace and record-root identity;
- declared and locally resolved canonical baseline;
- exact preconditions, including absent manifest and target paths;
- confirmed modules and subjects;
- ordered target records with final path, payload file, byte length, SHA-256, document or generated role, ID where applicable, and template/generator digest;
- deterministic validation results over the virtual record; and
- the preview hash.

The plan contains no wall-clock timestamp, random UUID, adapter-specific path, or embedded full prose. The operation ID is `wfinit-` plus a collision-safe prefix of the SHA-256 of the exact `plan.json` bytes; the complete digest remains authoritative. Payload names are ordinal and path-independent. `preview.md` is deterministically rendered from the plan and exact payloads and includes the complete tree, full authored content, concern-to-home map, unresolved states, material inferences, omissions, preconditions, and plan digest.

The user confirms the complete `sha256:<64-hex>` plan digest. Any proposal, payload, path, baseline, template, contract, or preview change yields a new plan and requires confirmation again.

### Workspace operation directory

`initialize-apply` first validates the external bundle and confirmation, then exclusively creates:

```text
.wayfinder/operations/<operation-id>/
├── plan.json
├── payload/
├── events/
│   ├── 0001-started.json
│   ├── 0002-staged.json
│   ├── 0003-validated.json
│   ├── 0004-create-intent.json
│   └── ...
└── receipt.json
```

This operation directory is tooling state, not a discoverable record: discovery still requires `.wayfinder/manifest.json`. The bundle is copied and rehashed before live publication so recovery does not depend on an operating-system temporary directory.

### Journal events

Events are separate immutable, exclusive-created canonical JSON files rather than appended lines or a mutable status document. Every event contains:

- format and schema version;
- one-based consecutive sequence;
- plan SHA-256 and operation ID;
- registered phase;
- SHA-256 of the preceding event, or `null` for the first;
- the exact paths, expected hashes, and observations relevant to that phase; and
- the adapter ID/runtime as non-authoritative execution evidence.

The event filename sequence, embedded sequence, and hash chain must agree. Recovery uses only the longest complete valid prefix and reports any missing, truncated, duplicate, or divergent suffix. A `create-intent` event naming a target and expected bytes is written before each live create; a `created` event is written after verifying the placed bytes. The manifest has its own final intent/created pair and is always last among project-record targets. A final `complete` event precedes a compact immutable receipt.

### Recovery behavior

`initialize-recover` defaults to read-only inspection. With explicit `resume`, it verifies the contract package, raw plan digest, payloads, current baseline, lock state, valid event prefix, and every possibly created target before continuing the next unambiguous step. With explicit `rollback`, it follows the accepted conservative rule: remove the manifest first only when exact planned bytes remain, then remove only operation-target files whose exact bytes remain and whose journal state proves the operation had entered their create step; remove only operation-created empty directories. Any mismatch is preserved and blocks automatic cleanup with an exact report.

Recovery never needs the original adapter, but it does require one certified adapter for the recorded contract version. No adapter silently upgrades an operation plan.

## Options

### Option A: versioned contract plus capability-probed certified adapter family — recommended

Adopt the package, taxonomy declaration, template rules, one-time detection, common CLI, bundle, and immutable journal above. Initially certify Python, Node.js, and PowerShell adapters against one suite.

**Benefits:** broad zero-install reach across common development and Windows environments; one workflow and recovery format; adapter choice disappears after first-use detection; exact preview/digest binding; testable cross-language behavior; runtime agents load only relevant guidance; no parser dependency; an alternate adapter can recover an interrupted operation.

**Costs and risks:** three complete implementations and differential CI are real maintenance work; shared specification mistakes remain possible; capability probes add startup work; PowerShell 5.1 compatibility needs its own lane; exact byte rules and journal fixtures are substantial; initialization remains blocked until at least one adapter is certified.

**Best fit:** Wayfinder is intended to be a reusable skill across heterogeneous agent environments and correctness matters more than minimizing initial implementation effort.

### Option B: one required Python standard-library implementation

Make supported Python 3 the sole runtime and use one implementation, schema package, and suite. Detection only locates and probes Python.

**Benefits:** smallest codebase; lowest drift risk; fastest route to a working initializer; Python's standard library covers JSON, hashing, paths, subprocesses, and exclusive creation; one implementation makes diagnostics easier to stabilize.

**Costs and risks:** environments without a supported Python are blocked or require installation; Windows agents cannot rely on Python being present; “portable” means portable only where Python is already available; a Python runtime upgrade can become a system-wide gate.

**Best fit:** Wayfinder is initially deployed only in controlled developer environments that already guarantee supported Python.

### Option C: native shell pair with POSIX shell and PowerShell

Implement the complete core directly in POSIX `sh` for Unix-like systems and PowerShell for Windows, avoiding Python and Node.

**Benefits:** uses conventional command environments on the two major platform families; only two implementations; launch and core are the same artifact; no language runtime selection on most systems.

**Costs and risks:** POSIX shell has no standard JSON parser, Unicode-normalization library, or ergonomic graph/data structures; a hand-built JSON/Markdown parser greatly enlarges the security and conformance surface; Unix utility variants differ; complex rollback logic becomes hard to review; equivalent behavior across the pair is less plausible than with structured standard libraries.

**Best fit:** the contract is drastically simplified or the target environments guarantee additional command-line utilities, contrary to the current dependency constraint.

### Option D: normative templates and agent-executed recipes without adapters

Publish schemas, examples, and step-by-step instructions, but let each runtime agent inspect the environment and perform file operations with its available tools.

**Benefits:** almost no bundled implementation; agents can adapt to unusual environments; easy to revise prose during early exploration; no cross-language code maintenance.

**Costs and risks:** environment detection repeats; rendering and validation vary by agent; digest binding can fail through whitespace or quoting; recovery is improvised at the moment of failure; user trust depends on a model following a long protocol perfectly; violates the request to make repeatable actions deterministic whenever possible.

**Best fit:** disposable prototypes where a partially created record can be discarded and reproducibility is not important.

## Recommendation

Choose **Option A** as one implementation bundle:

1. Treat `contract-v1` as a single versioned package with separate semantic, grammar, schema, template, and fixture responsibilities.
2. Pin UTF-8/LF, strict JSON, CommonMark reference behavior, SHA-256, and RFC 8785 canonical control objects.
3. Extend each manifest module with ordered `document` or `collection` subjects while permitting module-level unclassified documents.
4. Keep literal one-pass templates in skill assets; scripts own syntax and never re-render published authored prose.
5. Provide complete standard-library Python, Node.js, and PowerShell adapters; make support contingent on the shared conformance suite rather than file presence.
6. Run one capability-based detector on first Wayfinder use per agent session and reuse its exact selection.
7. Keep the CLI noninteractive, file-oriented, JSON-result based, and incapable of implicit network, install, or VCS mutation.
8. Separate semantic proposal, exact bundle, canonical plan, human preview, and confirmed digest.
9. Derive the operation ID from the plan digest and copy the confirmed bundle into workspace-local recovery state before publishing.
10. Use immutable hash-chained event files, exclusive target creation, manifest-last publication, and conservative explicit resume/rollback.
11. Permit a different certified adapter to recover the transaction without treating adapter output diversity as a vote.
12. Block rather than improvise when no certified adapter or valid contract package is available.

This is more work than a Python-only prototype, but it turns the user's portability requirement into a falsifiable release property instead of an aspiration. The common contract and fixtures are the primary product; the adapters are replaceable implementations.

## What acceptance would change now

The runtime `SKILL.md` would record the one-time detector rule, certified-adapter boundary, package authority, taxonomy declaration, deterministic CLI, and bundle/journal contract. The previously empty runtime directories could then receive the v1 contract references, assets, templates, detectors, adapter skeletons, and conformance harness incrementally.

Acceptance would not mean all adapters are immediately complete. Wayfinder's Initialize workflow must remain marked non-operational until the accepted contract is encoded, at least one complete adapter passes the suite, the remaining supported-adapter claims are truthful, and the final initialization boundary is settled.

## Deferred decisions

- Fresh empty-root initialization versus adoption/migration of existing unmanifested documents.
- Exact semantic proposal field-by-field schema and each kind's final starter heading template; these can be encoded from Decisions 12–15 once the existing-record boundary is known.
- Which completed-operation receipt fields and retention duration belong in the durable record.
- Long-term adapter deprecation and contract migration policy.
- Whether binary or non-Markdown evidence attachments become governed targets.
- Project-local template extension or executable plugins.
- Network-based validators and external-link cache formats.
- CI platform matrix and release packaging outside the skill directory.

## Next decision if Option A is accepted

Define the **initialization adoption and completion boundary**: whether v1 supports only a new record, can wrap or import an existing unmanifested plan, how foreign files are classified and preserved, what constitutes a successful initialized state, and the exact handoff into the full Interview workflow. This is the remaining policy needed before implementing the initializer against fixtures.

## Sources

1. JSON Schema Project. “[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12).” Published 2022; accessed 2026-09-13.
2. National Institute of Standards and Technology. “[Conformance Testing 101](https://www.nist.gov/itl/voting/conformance-testing-101).” Accessed 2026-09-13.
3. Sarikaya, B., and Wiles, A. “[Standard Conformance Test Specification Language TTCN](https://doi.org/10.1016/0920-5489(92)90054-H).” *Computer Standards & Interfaces* 14(2), 1992, pp. 117–144.
4. McKeeman, W. M. “[Differential Testing for Software](https://vmssoftware.com/docs/dtj-v10-01-1998.pdf).” *Digital Technical Journal* 10(1), 1998, pp. 100–107.
5. Knight, J. C., and Leveson, N. G. “[An Experimental Evaluation of the Assumption of Independence in Multiversion Programming](https://doi.org/10.1109/TSE.1986.6312924).” *IEEE Transactions on Software Engineering* SE-12(1), 1986, pp. 96–109.
6. Claessen, K., and Hughes, J. “[QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://doi.org/10.1145/351240.351266).” *Proceedings of ICFP 2000*, pp. 268–279.
7. Dorofeeva, R., El-Fakih, K., Maag, S., Cavalli, A. R., and Yevtushenko, N. “[FSM-Based Conformance Testing Methods: A Survey Annotated with Experimental Evaluation](https://doi.org/10.1016/j.infsof.2010.07.001).” *Information and Software Technology* 52(12), 2010, pp. 1286–1297.
8. Lamb, C., and Zacchiroli, S. “[Reproducible Builds: Increasing the Integrity of Software Supply Chains](https://doi.org/10.1109/MS.2021.3073045).” *IEEE Software* 39(2), 2022, pp. 62–70.
9. Bray, T., ed. “[RFC 8259: The JavaScript Object Notation Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259).” IETF Internet Standard STD 90, 2017.
10. Rundgren, A., Jordan, B., and Erdtman, S. “[RFC 8785: JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785).” 2020.
11. MacFarlane, J., et al. “[CommonMark Specification 0.31.2](https://spec.commonmark.org/0.31.2/).” 2024.
12. Free Software Foundation. “[GNU Autoconf Manual: Existing Tests and Cached Results](https://www.gnu.org/software/autoconf/manual/autoconf-2.70/autoconf.html).” Version 2.70, 2020; accessed 2026-09-13.
13. The Open Group. “[POSIX.1-2024 Shell Command Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html).” IEEE Std 1003.1-2024; accessed 2026-09-13.
14. Python Software Foundation. “[Status of Python Versions](https://devguide.python.org/versions/).” Accessed 2026-09-13.
15. OpenJS Foundation. “[Node.js Releases](https://nodejs.org/en/about/previous-releases).” Accessed 2026-09-13.
16. Microsoft. “[PowerShell Support Lifecycle](https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle).” Accessed 2026-09-13.
17. Widdowson, C., et al. “[Command Line Interface Guidelines](https://clig.dev/).” Accessed 2026-09-13.
18. Mohan, C., Haderle, D., Lindsay, B. G., Pirahesh, H., and Schwarz, P. M. “[ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging](https://doi.org/10.1145/128765.128770).” *ACM Transactions on Database Systems* 17(1), 1992, pp. 94–162.
19. SQLite Project. “[Atomic Commit in SQLite](https://sqlite.org/atomiccommit.html).” Accessed 2026-09-13.
20. Pillai, T. S., Chidambaram, V., Alagappan, R., Al-Kiswany, S., Arpaci-Dusseau, A. C., and Arpaci-Dusseau, R. H. “[All File Systems Are Not Created Equal: On the Complexity of Crafting Crash-Consistent Applications](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai).” *11th USENIX Symposium on Operating Systems Design and Implementation*, 2014, pp. 433–448.
21. Parnas, D. L. “[On the Criteria to Be Used in Decomposing Systems into Modules](https://doi.org/10.1145/361598.361623).” *Communications of the ACM* 15(12), 1972, pp. 1053–1058.
22. Shipman, F. M., and Marshall, C. C. “[Formality Considered Harmful: Experiences, Emerging Themes, and Directions on the Use of Formal Representations in Interactive Systems](https://doi.org/10.1023/A:1008716330212).” *Computer Supported Cooperative Work* 8, 1999, pp. 333–352.
