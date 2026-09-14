# Wayfinder design record

- **Status:** Active
- **Last updated:** 2026-09-14
- **Audience:** Wayfinder maintainers only

This file preserves the governing brief, accepted design choices, unresolved decisions, and workflow progress so development can continue across sessions. It is not runtime guidance. Agents using Wayfinder for project work must not read this directory.

## Governing brief

Build a reusable skill that creates and maintains a durable project plan resembling the MyPond project record: a structured hierarchy of focused Markdown documents, stable entry points and indexes, research with provenance and uncertainty, explicit decisions with history, architecture guidance, development guidance, and links between those layers.

Wayfinder must eventually support five workflows:

1. Initialize a new plan structure.
2. Interview the user to develop the plan.
3. Update the plan.
4. Validate the plan, including links and semantic consistency.
5. Use the plan by retrieving only the context needed for another agent's task.

Develop the workflows one at a time. Break each workflow into focused, moderately scoped decision points. Bundle tightly coupled mechanics when they form one coherent policy, but keep independent product or governance choices separate. At every decision point:

1. Research relevant scholarly work, psychology, learning science, information science, requirements methods, and other applicable evidence.
2. Present research-backed implementation options with enough specificity for the user to evaluate them.
3. Stop for the user's decision.
4. Record the accepted choice and its rationale.
5. Make the smallest corresponding update to the skill and verify it.

Research knowledge must remain inside the skill, cite original sources, synthesize their implications, and explain the resulting workflow design. It is maintainer-only context and must never be loaded merely to initialize, interview for, update, validate, consume, or implement from a project record.

Prefer deterministic scripts for repeatable actions. Keep scripts portable and dependency-light. If one portable implementation cannot cover plausible environments, provide explicit alternatives. Runtime agents should detect their environment once when they first load Wayfinder, then reuse that result rather than repeatedly probing it.

## Accepted choices

| Decision | Status | Rationale |
| --- | --- | --- |
| Name the skill `wayfinder`. | Accepted | The name emphasizes orientation and navigation across both plan development and selective consumption. |
| Keep research and design rationale under `maintainers/`. | Superseded 2026-09-13 | This originally separated maintenance knowledge from runtime context, but the internal directory remained visible inside the runtime skill and made ownership confusing. The accepted companion-skill decision preserves the progressive-disclosure intent with a structural boundary. |
| Move all maintainer-only material into the explicit-only `wayfinder-maintainer` companion skill. | Accepted 2026-09-13 | The separate skill owns research, design history, tooling, demonstrations, and certification evidence. Wayfinder retains runtime instructions and its self-contained executable contract, including governed conformance fixtures under contract assets. This supersedes the earlier in-skill `maintainers/` location. |
| Develop one workflow at a time through focused, moderately scoped, user-approved decisions. | Accepted | Bundles tightly coupled mechanics into coherent choices while preserving user control and reviewability. |
| Prefer dependency-light deterministic scripts and one-time environment detection. | Accepted constraint | Direct instruction from the skill owner. Exact environment contract remains undecided. |
| Include taxonomy evolution in the general update workflow. | Accepted scope requirement | Subject and module additions, renames, splits, merges, moves, and retirements need the same authority, history, link, and stable-identity protections as other plan updates. The exact workflow remains undecided. |
| Use a stable semantic kernel plus capability-driven modules. | Accepted | Preserves predictable meaning, authority, navigation, and retrieval while allowing the physical record to reflect the project's actual concerns. A software-product profile may reproduce the useful MyPond shape without making it universal. |
| Store authoritative structural metadata with each durable document and generate indexes deterministically. | Accepted | Co-locates content and intrinsic metadata, avoids an independently edited catalog, lets documents retain identity when moved, and supports machine-assisted retrieval. Generated views are derivations, never authorities. |
| Encode metadata in a constrained, visible Wayfinder Markdown block. | Accepted | Keeps routing and authority cues visible and co-located while allowing a dependency-free, strict parser. Exact delimiters distinguish the application convention from ordinary Markdown; JSON remains a possible derived format rather than the authoring source. |
| Require the universal fields `ID`, `Kind`, `Status`, `Updated`, and `Summary`; derive title and path. | Accepted | Supplies the minimum cross-cutting cues for identity, validation, authority, recency, and selective retrieval. Avoiding duplicated title and path removes preventable inconsistency, while provenance and governance remain kind-specific extensions. |
| Use stable, human-readable, location-independent document IDs scoped to one project record. | Accepted | Preserves identity across moves and ordinary retitling while keeping diagnostics inspectable. IDs never encode mutable path, status, date, ownership, hierarchy, or implementation facts and are never reused for a different knowledge object. |
| Use `wf-<global-ordinal>-<frozen-mnemonic>` IDs and allocate the next ordinal by scanning the whole valid record. | Accepted | A global sequence gives deterministic, dependency-free allocation and obvious collision diagnostics; a bounded lowercase-ASCII mnemonic aids recognition without becoming authoritative. Both the full token and ordinal are project-wide unique, and content-derived hashes are reserved for snapshots rather than evolving document identity. Concurrent allocation remains a separate integration problem. |
| Make an ID immutable when it first enters the declared canonical project history. | Accepted | Before integration, an allocated ID is a candidate that may be re-keyed by a governed correction or collision workflow. This reconciles offline sequential allocation with permanent shared identity without a central reservation service. Lifecycle is derived from version-control ancestry or an explicit publication baseline, not duplicated in document metadata. |
| Resolve candidate collisions by canonical integration order. | Accepted | An existing canonical occupant always retains its ordinal; otherwise the first candidate successfully validated and integrated becomes the occupant. This makes the same history yield the same result without clocks, registries, contributor-based judgment, or content-derived ranking. An unordered batch with multiple claimants is rejected until an explicit integration order exists. |
| Limit automatic re-key edits to semantically proven occurrences. | Accepted | The script may rewrite the losing declaration and typed references whose binding the accepted Wayfinder grammar proves, while regenerating derived artifacts. It exhaustively reports all old-token occurrences and blocks on untyped or ambiguous contexts instead of applying a global replacement or guessing from prose. |
| Use a portable staged and journaled collision re-key transaction. | Accepted | Preserve the mnemonic; allocate `max + 1` across the local canonical baseline and candidate view; require a checkpoint; stage and validate copies; verify unchanged inputs; journal recovery data before live writes; validate afterward; restore prior bytes on failure. The script never fetches, commits, integrates, or auto-retries, keeping side effects bounded and each plan reviewable. |
| Anchor each record with a strict `.wayfinder/manifest.json` and a Markdown entrypoint. | Accepted | A closed, versioned JSON contract gives dependency-light tools one deterministic source for workspace discovery, record location, canonical baseline, enabled modules, and exact generated outputs, while Markdown retains the explanatory navigation role. Discovery selects the nearest manifest without crossing the VCS boundary; parsing rejects duplicate or unknown fields and unsafe paths; tools never infer a missing record or fetch implicitly. |
| Seed initialization with a named profile, then conduct a bounded taxonomy interview. | Accepted | The invariant kernel and standard profiles preserve cross-project meaning, while a four-pass inventory/place/extend/challenge interview adapts shallow subjects to the project's real concerns. Prefer subjects within standard modules; allow an explicitly approved `local-<slug>` module only for a non-duplicative, independently governed authority or lifecycle boundary with real content. Scripts validate only the confirmed proposal and never infer taxonomy from prose. |
| Use a minimum viable bootstrap and one reviewed, recoverable publication. | Accepted | Initialization establishes enough attributable content and visible uncertainty for a useful record without claiming discovery is complete. The user reviews one digest-bound proposal; deterministic tooling stages and validates exact bytes, never overwrites, publishes the manifest last, journals recovery state, and performs no implicit network or version-control operations. |
| Use a closed purpose-based document-kind registry with kind-specific lifecycles and derived navigation. | Accepted | Separate communicative role from module and subject through the seven authored kinds `map`, `brief`, `register`, `evidence`, `decision`, `guide`, and `index`. Living knowledge and decisions use distinct controlled status transitions; only lifecycle-actionable conditional metadata is added. Authored shells remain authoritative while generated regions and wholly generated artifacts are reproducible projections. |
| Use a bounded distributed trace graph, first-class question items, document-local sources, and a generated catalog. | Accepted | Keep the highest-value authority and evidence relationships with the content that asserts them, preserve unresolved work with stable project-wide question identity and lifecycle, and preserve each evidence document's source-use context. Strict typed links, reciprocal acyclic supersession, local citation anchors, and a derived catalog support deterministic integrity checks and selective routing without turning the record into a dense traceability database. |
| Package one versioned executable contract and certify capability-probed standard-library adapters against shared conformance evidence. | Accepted | Give semantics, grammars, schemas, templates, and fixtures distinct authority inside one digest-bound package; require byte-equivalent Python, Node.js, and PowerShell adapters before claiming support. One-time capability detection, a noninteractive file-oriented CLI, document/collection subject declarations, exact proposal bundles, and immutable recovery events make portability and publication behavior testable without installations or agent improvisation. |
| Initialize in a fresh managed namespace while allowing source-assisted intake of existing material. | Accepted | Preserve the no-overwrite publication model while making brownfield knowledge usable through user-bounded inventory and reviewed `incorporate`, `reference`, `preserve-out-of-scope`, or `unresolved` dispositions. Source bytes remain unchanged and digest-traceable; semantic conflicts are never auto-merged; competing current authority blocks cutover. Initialization completes only when both operational-integrity and semantic-readiness gates pass, then records a receipt and durable Interview resumption cues without claiming the plan itself is complete. |
| Implement Initialize as risk-ordered vertical contract slices, then certify the complete adapter family before activation. | Accepted | Develop normative rules, fixtures, and Python reference behavior together in five slices; freeze a release candidate only after the complete Python path works; implement Node.js and PowerShell from the frozen contract rather than by translation. Use a contract-first oracle hierarchy, disconfirming and mutation cases, byte-level differential checks, environment-specific evidence, interruption recovery, isolated forward tests, and explicit user activation review. The runtime remains blocked until the complete initial family is certified. |
| Use a decision-centered facilitation protocol as Wayfinder's default interview style. | Accepted constraint | Interactive Wayfinder work should use collaborative, evidence-first, moderately scoped checkpoints with explicit boundaries, a recommendation and real alternatives, one substantive decision per turn, and explicit approval. Research may prepare a pending choice, but behavior changes follow only accepted decisions; implementation checkpoints remain bounded and cannot silently activate or advance to the next tranche. Detailed guidance is a selectively loaded runtime reference so non-interactive Use and validation tasks do not pay for it. |
| Start every implementation slice in a new session and hand it off with a detailed prompt. | Accepted constraint | Approval of a completed slice authorizes recording its acceptance and preparing the next-session prompt, not beginning the next slice. A direct request to start a slice has the same result: provide a self-contained implementation prompt carrying accepted state, scope, boundaries, verification, and the post-implementation approval interview so each tranche begins with clean context and remains independently reviewable. |
| Publish Wayfinder from one public `somacdivad/wayfinder` repository containing separate `wayfinder` and `wayfinder-maintainer` plugin packages. | Accepted 2026-09-14 | One portable skill source per package supports Codex, Claude, and GitHub Copilot without coupling end users to maintainer authority or duplicating digest-sensitive content. Apache-2.0 and package version `1.0.0-rc.8` apply to repository distribution only; they do not change the frozen contract, candidate identity, certification state, or activation state. |

## Workflow progress

| Workflow | Status | Current decision point |
| --- | --- | --- |
| Initialize | Certification-matrix tranche pending approval; runtime disabled | Policy decisions 1–18, Slices 1–5, candidate revision 8, and the bounded Node.js and PowerShell adapter parity tranche are accepted. One of eight exact certification-matrix environments has passing immutable evidence; seven remain unavailable and matrix completion is not claimed. Initialize remains disabled. |
| Interview | Not started | Pending completion of initialization workflow design. |
| Update | Not started | Pending completion of initialization and interview workflow design; scope explicitly includes taxonomy evolution. |
| Validate | Not started | Pending definition of the project-record contract. |
| Use | Not started | Pending definition of authority, indexes, and retrieval metadata. |

## Stub state

The runtime `SKILL.md` is intentionally non-operational. It identifies planned modes and blocks agents from improvising unfinished workflows. Stage 0 through Slice 5, frozen candidate revision 8, and the bounded adapter parity tranche are accepted. The runtime skill contains no maintainer-only directory or routing instructions; those live in the explicit companion skill. The package is not a certified runtime. Certification, runtime routing, and activation remain separate later tranches.

## Stage 0 + Slice 1 implementation

Implemented and accepted by the skill owner on 2026-09-13:

- `assets/contract-v1/release.json` is the fixed-path distribution trust root. It hashes the contract manifest and Python adapter but never itself, avoiding circular self-hashing.
- `assets/contract-v1/contract.json` enumerates and hashes the normative reference, schemas, known answers, fixture index, fixture inputs, and expected results beneath closed governed scopes. Maintainer runner code and generated certification evidence are deliberately outside semantic contract authority.
- `references/contracts/v1.md` assigns stable Slice 1 rule identifiers and owns normative semantics. JSON Schemas document closed machine shapes; the standard-library Python runtime performs validation itself.
- Strict JSON rejects BOM, CRLF, malformed UTF-8 and Unicode, duplicate or unknown fields, unsupported versions, floats/exponents, and integers outside the cross-runtime exact range. Canonical JSON uses UTF-16 object-name ordering and the version-1 integer-only subset.
- `probe` verifies the release, adapter, contract, every governed resource, nine fixed known answers, Python 3.11+, and required runtime capabilities. It separates deterministic results from environment evidence.
- `discover` implements exact-root and physical upward discovery, nearest-candidate selection, repository-boundary stopping, invalid-nearest refusal, strict live-manifest validation, containment, and symlink refusal without writes.
- The maintainer harness invokes the adapter as a black box, snapshots fixture trees, provides gated deterministic clock/operation-ID/failure-boundary controls for later slices, exercises seeded properties and mutations, and emits digest-bound local evidence.

Accepted consequential implementation choices:

1. Managed version-1 paths use a conservative portable ASCII segment profile and ASCII case-insensitive identity checks. This excludes otherwise NFC-valid non-ASCII filenames and is intentionally recorded rather than treated as an already accepted capability reduction.
2. Discovery identifies a containing Git worktree through the nearest `.git` directory or regular-file marker and treats a symbolic-link marker as a conservative stop. It does not invoke Git. This is deterministic and network-free but does not authenticate that an arbitrary `.git` marker is a valid worktree.
3. A discovered live manifest requires its record root, all entrypoints, module and collection roots, declared snapshot, and generated artifacts to exist with the required regular-file/directory type. The later initializer's pre-publication missing-path exception remains outside Slice 1.
4. Local evidence covers CPython 3.12 on one macOS host and temporary local filesystems only. It is not independent validation or the accepted multi-platform, multi-adapter certification matrix.

Evidence: [Stage 0 + Slice 1 local report](../certification/v1/slice-1-local.md) and its [machine-readable form](../certification/v1/slice-1-local.json).

### Approval progress

| Checkpoint | Status | Outcome |
| --- | --- | --- |
| 1 — Package and trust model | Accepted 2026-09-13 | The skill owner accepted the current package boundary, authority split, distribution-rooted release descriptor, non-circular digest graph, and adapter-verification model as Option A. No external signature or additional distribution pin is required in this tranche. |
| 2 — Runtime behavior and safety | Accepted 2026-09-13 | The skill owner accepted Option A: the current `probe`, physical nearest-manifest discovery, marker-based Git boundary, strict JSON and manifest parsing, portable ASCII managed-path profile, containment and symlink refusal, stable diagnostics, and read-only guarantees. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Stage 0 plus Slice 1 on the strength of the digest-bound local evidence, with the disclosed cross-platform, independence, adapter-family, and bundled-validator limitations. No follow-up exception was attached to the approval. |

## Slice 2 implementation — accepted

Implemented as candidate revision 2 and accepted by the skill owner on 2026-09-13:

- Added one public read-only `inventory --workspace-root PATH --request FILE [--ledger FILE]` command. The skill owner selected this interface as Option A after the accepted closed command surface proved insufficient for black-box Slice 2 behavior without prematurely implementing `initialize-plan`.
- The strict request bounds local source selections, target-root exclusions, and deterministic entry, byte, and traversal-depth limits. It never defaults to scanning a repository.
- Traversal uses non-following classification, stable UTF-8 path ordering, normalized workspace-relative paths, overlap de-duplication, explicit exclusion reasons, safe regular-file reads, strict UTF-8 versus opaque-byte classification, ATX Markdown cues, and exact duplicate groups.
- The strict intake ledger validates all four confirmed dispositions, identifier shapes, mappings, transformation notes, evidence keys, question IDs, inventory binding, and current source bytes. It does not infer materiality or any semantic decision.
- Candidate resources and the Python adapter remain unactivated. Slice 1 evidence remains historical and digest-bound to candidate revision 1; Slice 2 receives separate cumulative local evidence and is not full-family certification.

Evidence: [cumulative Stage 0 through Slice 2 local report](../certification/v1/slice-2-local.md) and its [machine-readable form](../certification/v1/slice-2-local.json).

### Slice 2 approval progress

| Checkpoint | Status | Outcome |
| --- | --- | --- |
| 1 — Inventory and intake model | Accepted 2026-09-13 | The skill owner selected Option A and accepted the canonical inventory representation, explicit source selections and limits, normalized deterministic traversal, exclusion model, file classification and hashing, Markdown cues, exact duplicate groups, and closed intake-ledger structure as implemented. No follow-up exception was attached. |
| 2 — Runtime safety and semantic-authority boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted exact physical workspace resolution, lexical containment, intermediate-symlink rejection, non-following classification and file reads, hard and soft exclusion boundaries, explicit limits, stale-source failure, closed deterministic result behavior, read-only guarantees, and the rule that the adapter validates mechanics without making human semantic or authority judgments. No follow-up exception was attached. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Slice 2 on the cumulative 104-case local evidence, with the disclosed local-only, single-adapter, missing-platform, missing-independent-validation, and unavailable bundled-PyYAML-validator limitations. The dependency-free frontmatter check was accepted as the local substitute. No follow-up exception was attached. |

## Slice 3 implementation — accepted

Implemented as candidate revision 3 and accepted by the skill owner on 2026-09-13; intentionally left unactivated:

- Added read-only `validate --workspace-root PATH` and file-oriented `generate --workspace-root PATH --request FILE [--output-root PATH]`. The closed generation request has four bounded actions: read-only candidate `allocate`, no-overwrite `render`, manifest-declared `catalog`, and explicit-path `regions`.
- Added strict authored Markdown parsing for global document and question IDs, exact metadata and relationship blocks, kind-specific lifecycles and content profiles, first-class question histories, evidence source records, local citations, and explicit material-claim markers.
- Added record-wide validation for manifest-derived module/subject membership, typed link ID/path bindings, target kind/status, reciprocal acyclic supersession, generated-region ownership and freshness, and catalog freshness. Mechanical checks do not infer semantic meaning or authority.
- Added seven governed literal templates with four closed one-pass slots. Render validates every complete document in memory, preserves supplied prose, rejects existing outputs and symbolic path components, and writes only beneath an explicit existing output root.
- Added deterministic `document-catalog-v1` and `document-index-v1` projections. Generated regions have one exact delimiter carrying the input digest; region updates preserve every authored byte outside the delimited range and are byte-idempotent.
- Chose inline exact question histories and the explicit `Scope: Record-Wide` marker as the smallest portable question representation. Chose `- **Material claim:**` as the only machine-enforced claim boundary; identifying other material prose and assessing source support remain human semantic work.
- Generation uses same-directory temporary files and atomic replacement only for already declared catalogs and explicitly requested existing regions. Slice 3 adds no prompt, network, dependency installation, external-system, Git, publication, journal, receipt, or project-record authority.
- Candidate resources and the standard-library Python adapter remain unactivated. Earlier Slice 1 and Slice 2 evidence remains historical and digest-bound; Slice 3 receives separate cumulative local evidence and is not full-family certification.

Evidence: [cumulative Stage 0 through Slice 3 local report](../certification/v1/slice-3-local.md) and its [machine-readable form](../certification/v1/slice-3-local.json).

### Slice 3 approval progress

| Checkpoint | Status | Outcome |
| --- | --- | --- |
| 1 — Record model and semantic constraints | Accepted 2026-09-13 | The skill owner selected Option A and accepted the implemented document and question ID model, exact metadata and content profiles, kind-specific lifecycles, question state/history rules, evidence-source and explicit material-claim citation model, typed relationships, reciprocal acyclic supersession, manifest-derived membership, contained local-source paths, and the boundary between deterministic mechanical validation and human semantic judgment. No follow-up exception was attached. |
| 2 — Rendering, generation, and runtime-safety boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted read-only validation/allocation, closed one-pass rendering into an explicit existing output root, exclusive no-overwrite creation, manifest-declared catalog replacement, explicit generated-region replacement, authored-byte preservation outside regions, deterministic byte-idempotent projections, and the no-prompt/network/external-system/dependency/Git boundary. Per-file rather than batch atomicity remains an explicitly disclosed Slice 3 limitation deferred to the later journaled transaction work. No follow-up exception was attached. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Slice 3 on the cumulative 202-case local evidence, including all 104 accepted regressions, with the disclosed local-only, single-adapter, missing-platform, missing-independent-validation, per-file atomicity, later-slice, and unactivated-runtime limitations. No follow-up exception was attached. |

## Slice 4 implementation — accepted

Implemented as candidate revision 4 on 2026-09-13 and intentionally left unactivated:

- Added the public noninteractive `initialize-plan --workspace-root PATH --proposal FILE --bundle-root PATH` command. The explicit bundle must be absent, non-symbolic, and outside the workspace; the command never writes a target-record path.
- Added closed proposal and canonical-plan schemas. A proposal carries the confirmed profile and final manifest taxonomy, exact authored-document declarations, concern homes, epistemic states, omissions, authority boundary, material inferences, source bindings, material-source declarations, bootstrap readiness, and Interview resumption pointers.
- Normalization validates rather than chooses. Candidate document and question IDs begin at 1, remain consecutive in proposal order, and are checked for token and ordinal collisions. Complete authored content is rendered through the accepted literal templates and validated with the complete Slice 3 graph and containment model.
- Added deterministic virtual generation of authored payloads, generated regions, and the catalog. The plan addresses every authored, generated, and manifest payload by final target, ordinal bundle path, byte length, SHA-256, and producer digest; its declarative operation list creates directories, creates non-manifest files, and publishes the manifest last without executing any operation.
- Source-assisted planning rebuilds and compares the bound inventory, rechecks intake and source bytes, requires a reviewed disposition for each proposal-declared material source, proves target/question/evidence-key bindings, and copies canonical inventory and intake bytes into the external bundle.
- Added target, module-root, workspace, local Git-ref or snapshot baseline, source-digest, namespace, symlink, existing-output, prior-operation, competing-authority, readiness, placeholder, knowledge-map, and Interview-resumption preconditions.
- Resolved an unavoidable digest cycle by making raw canonical `plan.json` the confirmation object. It binds the full normalized plan and all target payload hashes. `preview.md` displays the plan digest and derived operation ID but is a reproducible review projection rather than a digest input or publication payload.
- Added a narrow Slice 3 regression correction: the accepted `foundation` and `evidence-led` profiles place `plan-brief.md` and `open-questions.md` directly under the record root, so root-level authored Markdown is now classified as kernel content with null module/subject. Nested documents still require exactly one module.
- Corrected the Slice 3 renderer's structured-link precheck to use the same owner-relative containment rule as the accepted Markdown parser. This permits normalized `../` links from collection documents to siblings while still rejecting destinations that escape the record.
- Local Git-ref resolution reads loose or packed refs without invoking Git or fetching. Effective date is explicit proposal data. The ordinary operation ID derives from the first 24 hex digits of the plan digest; maintainer injection requires test mode and a reserved visible namespace.
- Slice 4 still performs no application, publication, journaling, rollback, recovery, receipt, completion gate, Node.js or PowerShell work, runtime routing, candidate freeze, or activation.
- The cumulative local suite passes 251/251 cases: all 202 accepted Stage 0–Slice 3 regressions plus 49 Slice 4 cases. The final contract digest is `3b9e4b95db3263d7987e62316eda4329da2990813da8f6a4822b86ff138570df`; the final release descriptor digest is `59a57ebb370a43c059ce141378343b3792eab3892d319a4adfa007792b709915`.

Consequential implementation choices requiring this tranche review:

1. The bundle is external to the workspace, which makes its write boundary unambiguous and prevents a planning output from entering the future record namespace.
2. Materiality remains human authority: the proposal explicitly declares material source paths, and the adapter checks only that each declaration has one confirmed intake disposition.
3. The canonical plan digest excludes the preview to avoid a self-reference cycle; all review facts used to render the preview remain inside the digested plan.
4. Producer digests identify the literal template for authored files, the normative contract for generated projections, and the manifest schema for the manifest payload.
5. Multi-file bundle creation uses exclusive file creation after full semantic preflight. Slice 4 promises rejected-preflight zero writes and no overwrite; journaled interruption recovery belongs only to Slice 5.

Evidence: [cumulative Stage 0 through Slice 4 local report](../certification/v1/slice-4-local.md) and its [machine-readable form](../certification/v1/slice-4-local.json).

### Slice 4 approval checkpoints

| Checkpoint | Status | Decision |
|---|---|---|
| 1 — Proposal and normalized-plan model | Accepted 2026-09-13 | The skill owner selected Option A and accepted the closed proposal schema, semantic-authority boundary, identifier and candidate-ordering rules, virtual validation through the accepted Slice 3 model, and normalized-plan representation as implemented. No follow-up exception was attached. |
| 2 — Bundle, digest, preview, preconditions, and runtime-safety boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted the absent external non-symbolic bundle root, canonical `plan.json` confirmation object, SHA-256 binding of the normalized plan and every target payload, reproducible non-digested preview projection, declarative manifest-last operation order for future application, full preflight before exclusive no-overwrite bundle creation, rejected-preflight zero-write guarantee, and the no-target/source/Git/network/dependency/external-system-mutation boundary. No follow-up exception was attached. |
| 3 — Evidence and tranche approval | Accepted 2026-09-13 | The skill owner selected Option A and accepted Slice 4 on the cumulative 251-case local evidence, including all 202 accepted Stage 0–Slice 3 regressions and 49 Slice 4 cases, with the disclosed local-only, single-adapter, missing-platform, missing-independent-validation, later-slice, and unactivated-runtime limitations. No follow-up exception was attached. |

## Slice 5 implementation — accepted

Implemented as candidate revision 5 and accepted by the skill owner on 2026-09-13; intentionally left unactivated:

- Added public noninteractive `initialize-apply` and `initialize-recover` commands. Apply requires the external bundle, exact plan SHA-256, and the literal `wayfinder-confirm-sha256:<digest>` token; recovery requires an operation ID and an explicit `inspect`, `resume`, or `rollback` action.
- Apply verifies canonical plan bytes, the current contract, workspace binding, closed bundle membership, every payload length and digest, the locally resolved baseline, source inventory/intake/source bytes, target and module-root absence, and manifest absence. It imports exact bundle bytes and never regenerates or reinterprets semantic content.
- The workspace lock is one exclusive `.wayfinder/initialize.lock` with operation, plan, host, process, and owner-token identity. Apply never steals it. Recovery reclaims only same-operation, same-plan, same-host locks whose recorded process is no longer present; malformed, foreign, live, mismatched, and ownership-changed locks block mutation.
- Each operation uses a private `.wayfinder/operations/<operation-id>/` root and same-filesystem staging area. The first immutable hash-chained event records the complete intended target set and digests before staging or publication. Canonical event lines use one-based sequence, UTC whole seconds, predecessor digest, and a digest of the event basis.
- Staging materializes every planned payload byte, verifies its length and hash, and reproduces the Slice 4 validation projection. Publication creates only absent directories, exclusively creates and verifies non-manifest files, then exclusively publishes and verifies the manifest as the final discovery marker.
- Post-publication checks regenerate catalog and region expectations in memory through the accepted validator, compare the complete live target set with the plan, and record separate passed operational-integrity and semantic-readiness gates. A manifest without both gates and a valid receipt remains recovery-required.
- The canonical receipt binds the plan, contract, adapter, baseline, target set, manifest, intake counts, validation, both gates, entrypoint, open questions, and durable Interview handoff. The receipt is written before the terminal `complete` event and remains audit/routing data rather than semantic authority.
- Recovery inspection is read-only and returns `resumable`, `completed`, `rolled-back`, `blocked`, or `manual-recovery`. Resume trusts only a valid imported bundle, hash chain, exact event-owned paths, absent unowned targets, and current baseline/source predicates. Rollback removes an exact operation manifest first, then only exact unchanged event-owned files and empty event-owned directories; modified, missing-unexpected, unowned, nonempty, or symbolic paths are preserved and reported.
- Maintainer-only failure injection covers lock acquisition, bundle recording, every staged payload, staging completion, the second preflight, publication start, each directory, every file pre/post boundary, manifest pre/post, live validation pre/post, receipt, completion, rollback start, and rollback removals. The cumulative fixtures exercise inspection, resume, rollback, completed, blocked, and manual-recovery outcomes without changing MyPond's project record.
- Slice 4's historical evidence remains unchanged. Slice 5 writes separate cumulative local evidence labeled incomplete family certification; Node.js, PowerShell, cross-adapter recovery, the release environment matrix, independent evaluation, contract freeze, runtime guidance, and activation remain deferred.
- The final cumulative local suite passes 302/302 cases: all 251 accepted Stage 0–Slice 4 regressions plus 51 Slice 5 cases. The candidate-revision-5 contract digest is `39c22cfd2ddb39ca1ba043364bc9d916fd9f8236d1fc75c8e3b39e7eb1d7f666`; the release descriptor digest is `5c920381334368a799ad397f146391251cf95fb443824f70421014f6f7a36c7f`; the Python adapter digest is `47fa949e5b329337009d74d7890edf6cfdc636d772f90f6f798a5d4886209693`; and the result-set digest is `1a4a430a3880808da03197bb2a02ee3425d56ae3168f4cf28bdc7ce4ba06f066`.

Accepted consequential Slice 5 implementation choices:

1. The confirmation token is deliberately mechanical and plan-bound: `wayfinder-confirm-sha256:<plan digest>`. It proves explicit caller intent without parsing preview prose.
2. Operation IDs continue to derive from the first 24 plan-digest hex characters; the injected Slice 4 operation ID remains a planning-only test projection because ordinary Apply accepts no unbound operation-ID override.
3. `events.jsonl` is append-only by adapter behavior and tamper-evident through a strict hash chain; version 1 does not claim filesystem-enforced immutability.
4. Directory durability uses file flushes plus best-effort directory `fsync` where the platform permits it. The contract promises detection and conservative recovery, not universal crash-atomic persistence.
5. Staging is private and on the workspace filesystem, but publication uses exclusive creation of final files rather than renaming staged files; this preserves no-clobber behavior consistently across the version-1 portability target.
6. Completed operations retain imported bundle, journal, and receipt. Successful staging bytes are removed. Retention or pruning belongs to a later Update/governance decision.
7. A same-host dead-process check is the only automatic stale-lock proof. Foreign-host locks remain blocked because a local process check cannot establish their owner is gone.

Evidence: [cumulative Stage 0 through Slice 5 local report](../certification/v1/slice-5-local.md) and its [machine-readable form](../certification/v1/slice-5-local.json).

### Slice 5 approval checkpoints

| Checkpoint | Status | Decision |
|---|---|---|
| 1 — Apply, staging, and manifest-last publication model | Accepted 2026-09-13 | The skill owner selected Option A and accepted the confirmation binding, two-stage preflight, same-filesystem staging, exclusive no-clobber publication, and manifest-last visibility boundary as implemented. No follow-up exception was attached. |
| 2 — Journal, interruption recovery, rollback, receipt, and runtime-safety boundary | Accepted 2026-09-13 | The skill owner selected Option A and accepted the hash-chained journal, interruption classification, conservative resume and rollback behavior, externally modified-path preservation, completion receipt, Interview handoff, and runtime-safety boundary as implemented. No follow-up exception was attached. |
| 3 — Evidence and explicit Slice 5 tranche approval | Accepted 2026-09-13 | The skill owner selected Option A, accepted the cumulative 302/302 conformance portfolio and independent 251/251 regression run with the documented local macOS/Python evidence boundary, and explicitly approved Slice 5 as implemented. No follow-up exception was attached; parity, freeze, publication, runtime guidance, activation, and live-project initialization remain unauthorized. |

## Candidate revision 6 maintenance correction — changes requested

Implemented on 2026-09-13 as a bounded correction to the unactivated candidate:

- Replaced slice-shaped release identity with `v1-candidate-revision-<positive integer>` and made the contract's `candidateRevision` the single current-revision authority. The release descriptor, release schema, deterministic probe oracle, normative contract, and Python adapter now agree on candidate revision 6.
- Added `WF-PKG-004` and a digest-valid mutation case that proves the adapter rejects semantic disagreement between the release descriptor and release schema. Package hash agreement alone is no longer treated as sufficient.
- Added `maintainers/maintain.py` as the dependency-free entry point for environment checks, package verification, conformance runs, explicit evidence creation, expected-negative demonstrations, and factual handoff scaffolding.
- Changed the conformance runner so ordinary test runs create no certification evidence. Evidence requires `--write-evidence`, is created only after a zero-failure suite, uses revision-scoped filenames, and refuses replacement through exclusive creation.
- Pinned the accepted Slice 1 through Slice 5 evidence hashes in `certification/v1/historical-sha256.json`; maintainer checks fail if those historical reports are missing or altered.
- Added the explicit-only `$wayfinder-maintainer` companion skill to keep maintainer instructions outside the runtime skill and to record the supported-interpreter, no-bytecode, optional-validator, evidence-preservation, and approval boundaries.
- Made the design record the only mutable implementation-progress authority; the research record now links here instead of duplicating a stale current-slice statement.
- This correction does not add Node.js or PowerShell adapters, certify parity, freeze or publish a release, activate runtime guidance, initialize a live project, install dependencies, mutate Git state, or change MyPond's product record.

Evidence: [candidate revision 6 local report](../certification/v1/candidate-revision-6-local.md) and its [machine-readable form](../certification/v1/candidate-revision-6-local.json). All 303/303 cases pass on local macOS with CPython 3.12.14. The contract digest is `df286c2633834814ff67cff79ee95bd46be62a1d5b33b3c5b45a31b8d3bdfccc`; the release descriptor digest is `a15d52f1dffb3342858f056ba6affdc454d8a5db519ad135a59b4fe90926d27a`; the Python adapter digest is `deb68477217e8d831ce5861f5b18e59dcaf4daef8d080c43d93d4f440296e95f`; and the result-set digest is `0074f0babf120639a0affea6be2319d97ebeea0b32a9aa85a13f2bd6af9fd526`. Historical Slice 1 through Slice 5 reports remain unchanged and retain their original candidate bindings. This is maintainer-run local evidence, not independent validation or complete adapter-family certification.

Review outcome: changes requested by the skill owner on 2026-09-13. The maintainer-only material remained inside `$wayfinder`, making the companion-skill boundary confusing. Candidate revision 7 preserves the revision-6 fixes while correcting that topology.

### Candidate revision 6 approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Maintenance safety and cross-artifact consistency | Changes requested 2026-09-13 | The skill owner selected Option B because the separate maintainer skill and an internal Wayfinder `maintainers/` subtree created a confusing ownership boundary. The revision-6 evidence is preserved, but revision 6 was not accepted. |

## Candidate revision 7 structural boundary correction — accepted

Implemented on 2026-09-13 as the requested revision to candidate 6:

- `$wayfinder` now contains runtime instructions, its adapter, and the self-contained executable contract package. Governed conformance cases, inputs, and expected outputs moved to `assets/contract-v1/conformance/v1/` because they are part of that package rather than maintainer instructions.
- `$wayfinder-maintainer` now owns the maintainer design record, research, command, runner and package builder, demonstrations, and certification evidence.
- The runtime `SKILL.md` no longer describes or links a maintainer directory. The companion `SKILL.md` is the sole route into maintenance work and remains explicit-only.
- Package building and mutation tests accept an explicit Wayfinder skill root, so maintainer tools can verify both the installed sibling skill and isolated package copies without reintroducing a runtime-maintainer dependency.
- Candidate revision 7 preserves the revision-6 semantic identity check, evidence safeguards, historical pins, supported-runtime selection, no-bytecode checks, and approval boundaries.
- This structural correction adds no runtime capability and does not authorize parity, freeze, certification, publication, runtime activation, or live-project initialization.

Evidence: [candidate revision 7 local report](../certification/v1/candidate-revision-7-local.md) and its [machine-readable form](../certification/v1/candidate-revision-7-local.json). All 303/303 cases pass on local macOS with CPython 3.12.14. The contract digest is `79e5b4f0f89bff5b01c1a302745f8af5a27e17d26f29627b2e0a79f39cd9dc71`; the release descriptor digest is `3b08de7e5db25ea1b0818fa6606d365876ff9ca8e37d05a1e1ee8b293beef74e`; the Python adapter digest is `a4e62f8ce938e87157b964b8aabf061558368299f578695b70d1554241bf7de4`; and the result-set digest is `0281fb4b1d9eec4229f1ee8ca480c80b5308909a607e360955a67cd8c19958c6`. Candidate revision 6 evidence remains preserved and hash-pinned under this companion skill and is not relabeled as accepted evidence. This is maintainer-run local evidence, not independent validation or complete adapter-family certification.

### Candidate revision 7 approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Skill ownership and maintenance safety | Accepted 2026-09-13 | The skill owner selected Option A and accepted the complete removal of `skills/wayfinder/maintainers/`, relocation of governed package fixtures under runtime contract assets, ownership of all maintainer-only resources by `$wayfinder-maintainer`, the preserved revision-6 safeguards, and the 303/303 local revision-7 evidence. No follow-up exception was attached; parity, freeze, certification, publication, runtime guidance, activation, and live-project initialization remain unauthorized. |

## Next decision

Review the pending bounded certification-matrix tranche described below. Do not begin forward tests, cross-adapter recovery, full-family certification, runtime guidance, activation, or live-project work from either the implementation result or its approval.

## Candidate revision 8 freeze — accepted

Implemented on 2026-09-13 as the bounded freeze-readiness correction:

- Separates the semantic contract's `frozen` status from the release's `unactivated-frozen` status. Frozen identifies the parity target; it does not certify the Python adapter, any environment, adapter parity, the adapter family, or runtime activation.
- Generalizes the release descriptor from one fixed Python adapter to a closed ordered adapter registry plus closed certification entries. The frozen release still lists only `python-reference-v1`; Node.js and PowerShell implementations remain absent.
- Adds digest-valid mutations for status/schema disagreement and adapter-registry disagreement. Package verification now rejects both before reporting a successful probe.
- Makes all 96 normative rules directly cited by at least one of 305 conformance cases and records that coverage counts are traceability evidence, not semantic proof.
- Reviews each governed expected-output artifact against named normative rules and records one deterministic expected-output-set digest in the maintainer-owned freeze proposal.
- Pins future matrix targets to CPython 3.14.7, Node.js 24.21.0, and PowerShell 7.6.6 using current primary official sources. These are requirements for future evidence, not claims that the environments exist or have passed.
- Records precise invalidation triggers and actions. Governed-byte or semantic changes reopen the candidate, advance its revision, invalidate affected evidence, and require every adapter to rerun.
- Preserves the Python adapter as an implementation under test and keeps runtime activation disabled.

The proposed-freeze record, acceptance record, and revision-8 local evidence remain maintainer-owned under `certification/v1/`. Candidate revisions 6 and 7 and Slice 1–5 historical evidence remain preserved. The freeze acceptance does not authorize parity implementation.

Evidence: [candidate revision 8 local report](../certification/v1/candidate-revision-8-local.md), its [machine-readable form](../certification/v1/candidate-revision-8-local.json), the [freeze-readiness packet](../certification/v1/proposed-freeze-revision-8.md), and the [Option A acceptance record](../certification/v1/freeze-acceptance-revision-8.md). All 305/305 cases pass on local macOS with CPython 3.12.14. The contract digest is `75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b`; the release descriptor digest is `69d029df64b5ac553aedab0d6127d3b99371f77847a7e41defac459b7e3c773e`; the Python adapter digest is `d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4`; the fixture-index digest is `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`; the expected-output-set digest is `c0fad6a47eff844f27135620e07210d081f19fab88aaa962cf5f0a6fb563ed7e`; and the result-set digest is `6cb5f6f61a5000bd69cd175dd4835feca61366ea0f9c2c9fbb483b8f12cfa022`. This remains maintainer-run local Python evidence, not independent, cross-platform, parity, environment, or full-family certification.

### Revision 8 approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Version-1 freeze readiness | Accepted 2026-09-13 | The skill owner selected Option A and accepted revision 8 as the frozen version-1 parity target. This authorizes later, separately requested Node.js and PowerShell implementations to target the frozen semantics. It does not begin parity work, certify any adapter or environment, authorize cross-adapter comparison, or activate Wayfinder. |

## Candidate revision 8 adapter parity — accepted

Implemented on 2026-09-14 as the bounded, independently assigned Node.js and PowerShell adapter parity tranche:

- Adds dependency-free Node.js and PowerShell adapters against the accepted frozen revision-8 contract and registers both adapters in the closed release registry. The Python reference adapter and every contract-governed semantic resource retain their accepted digests.
- Extends the maintainer runner to launch each native adapter, filter focused cases, capture deterministic differential observations, and apply identical package mutations to the selected adapter.
- Adds an atomic parity command that runs the complete common suite for all three registered adapters, compares frozen observable envelopes and ordered stable diagnostic codes across 900 invocations, and refuses to write evidence on any suite failure or mismatch.
- Compares adapter-independent observations after normalizing temporary paths, runtime and adapter identity, adapter-bound operation and audit digests, and contract-open human prose. The common suite separately asserts every frozen command-data projection, golden output byte sequence, mutation outcome, and stateful filesystem invariant.
- Keeps runtime instructions non-operational and records no certification entry. No later certification-matrix, forward-test, cross-adapter-recovery, runtime-guidance, activation, live-project, MyPond dogfooding, or Git tranche was performed.

Evidence: [candidate revision 8 local adapter parity report](../certification/v1/parity-revision-8-local.md) and its [machine-readable form](../certification/v1/parity-revision-8-local.json). The Python reference, Node.js, and PowerShell adapters each pass 305/305 common cases, their case-result digests agree, and their 900 normalized invocation observations agree at digest `4463448355c7662a09bb2112052179df0e95216e5bd1092968ee4ddc95b6d233`. The contract digest remains `75a0fe4ac106ffb6ad496a38d65addf004f03f128c18fd512232c4631315955b`; the Python adapter digest remains `d0ce8b8e21606bd026ff82b93945cbef3225387b0c47702b688d285c966679d4`; the Node.js adapter digest is `fcd01cfd47c98488eb2e85055924630642ee4093c02272bb67ba961d4e084125`; the PowerShell adapter digest is `9b64624f0c837db6082ce241a3f17f3d05614490e4e721d757588c8fefbe0bce`; and the adapter-registry release descriptor digest is `677fa5af49c11532d49875bd8d1138a36903668449188e6358f2d0a5947f2284`.

This evidence is maintainer-run on one macOS arm64 host with CPython 3.14.7, Node.js 22.22.3, and portable PowerShell 7.6.6. Node.js 22 is not the pinned Node.js 24 matrix target, and portable PowerShell on macOS is not a pinned matrix operating-system entry. The evidence is therefore local adapter parity only: it is not independent validation, an environment certification, or full-family certification.

### Adapter parity approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded Node.js and PowerShell adapter parity | Accepted 2026-09-14 | The skill owner selected Option A and accepted the bounded adapter parity tranche as implemented, including the disclosed local-only, non-independent, non-environment, and non-full-family evidence limits. No follow-up exception was attached. The later certification matrix, forward tests, cross-adapter recovery, runtime guidance, activation, and live-project work remain separately authorized tranches; this approval begins none of them. |

## Candidate revision 8 bounded certification matrix — pending approval

Implemented on 2026-09-14 as maintainer-only orchestration and partial environment evidence for the exact frozen matrix:

- Added `maintain.py matrix-entry` to verify the selected required target, accepted candidate/package/adapter/parity bindings, exact native runtime identity and executable digest, OS family and version, architecture, effective locale and timezone, filesystem encoding, Unicode filename round trip, and actual filesystem case behavior before running the exact registered adapter. A matching environment runs all 305 cases and exclusively creates a timestamped JSON/Markdown evidence pair; runtime, version, or OS substitutions are rejected before the suite begins.
- Added `maintain.py matrix-aggregate` to accept explicit immutable environment-report paths, revalidate every result-set and package binding, require one passing 305/305 report for each of the eight exact entries, require both observed filesystem behaviors, and exclusively create the maintainer-owned aggregate only after all conditions hold. An incomplete selection returns `matrix.incomplete` and writes no aggregate.
- Extended the doctor to pin the accepted candidate, contract, release, fixture-index, expected-output, adapter, and local parity-evidence digests. The accepted parity JSON and Markdown remain byte-for-byte unchanged.
- CPython 3.14.7 on macOS 26.6.2 arm64 passed 305/305 cases, including 213/213 negative and mutation cases and all three summarized interruption-boundary cases. The suite ran with explicit `C.UTF-8` locale and `UTC` timezone controls. The temporary filesystem reported UTF-8 with `surrogateescape`, passed the Unicode filename round trip, and was observed as case-insensitive because exclusive creation of a case-variant name was refused as an existing file.
- Immutable evidence: [macOS CPython 3.14.7 JSON](../certification/v1/matrix-revision-8-python-reference-v1-macos-20260914T125208Z.json) (`6b43c2f0b41e83d76218e363651d6353ab62561426e4c7abf997cb561aa3fd78`) and [Markdown](../certification/v1/matrix-revision-8-python-reference-v1-macos-20260914T125208Z.md) (`8a81084ab64a18bac8d59694bc81233035cc0f02434a36d8106dfc0f2cc1c11c`). The result-set digest is `3b70db99a1cc2caa40a3e472dbf742b2b10cf2b467a191c124ff9e35685d8757`.
- CPython 3.14.7 on Linux and Windows, Node.js 24.21.0 on macOS/Linux/Windows, and PowerShell 7.6.6 on Windows/Linux remain unavailable. The present host is macOS, and its available Node.js is 22.22.3 rather than the pinned 24.21.0. Environment-only maintainer checks rejected all seven exact targets before conformance execution and wrote no evidence for them.
- The aggregate command was exercised with the one passing report and correctly refused publication because seven entries and case-sensitive filesystem coverage are missing. No aggregate matrix report or release certification entry exists.

This tranche is partial passing environment evidence, not a completed matrix, independent validation, cross-adapter recovery, forward testing, or full-family certification. It does not authorize runtime guidance or activation.

### Certification-matrix approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded certification-matrix orchestration and available evidence | Pending explicit approval | **Option A:** accept the bounded certification-matrix tranche as implemented, preserving one passing environment entry and seven explicitly unavailable entries without a completion claim. **Option B:** request bounded changes. Either choice begins no subsequent tranche. |

## Public repository migration — implementation checkpoint

Authorized on 2026-09-14 as a delivery and packaging tranche separate from certification and activation:

- The repository root is a source and marketplace container with independently installable `plugins/wayfinder` and `plugins/wayfinder-maintainer` packages.
- Each package has one canonical skill tree, a portable Agent Plugins 1.0 manifest, and thin Codex and Claude compatibility manifests. The end-user catalogs list only `wayfinder`; the maintainer package remains opt-in.
- The frozen contract, release registry, registered adapter bytes, accepted historical evidence, accepted parity evidence, and existing macOS matrix evidence remain unchanged. A migration manifest binds every imported source file to its source and destination SHA-256 digest and labels only maintainer-owned topology changes.
- Repository validation, ordinary conformance, exact eight-entry certification, aggregation, and evidence-publication preparation are separate workflows. Certification and evidence publication are manual-only; the latter is gated by a protected GitHub environment and produces a draft release for final review.
- GitHub Actions use fixed OS labels, exact runtime patch versions, checksum-verified PowerShell archives, full action commit SHAs, least-privilege permissions, and no `pull_request_target` execution.
- The migration does not approve the pending bounded matrix tranche, execute hosted certification, add release certification entries, perform full-family certification, publish a runtime release, add runtime guidance, or activate Wayfinder.

### Migration checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Public two-plugin repository structure and CI route | Published and validated | The owner authorized implementation on 2026-09-14. The public `somacdivad/wayfinder` repository was created and initial commit `6f8a311be0d8c98d557db64ed3263acd4b92ffe3` was published to `main`. The first hosted validation exposed a maintainer-harness path-normalization defect on Linux; a bounded maintainer-only correction preserved all frozen governed and adapter bytes, and ordinary repository validation subsequently passed. The manual certification and evidence-publication workflows were not run. No subsequent certification or activation tranche begins automatically. |
