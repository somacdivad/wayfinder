# Wayfinder design record

- **Status:** Active
- **Last updated:** 2026-09-15
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
| Use a layered maintainer approval-response protocol for every explicit acceptance, authorization, or approval checkpoint. | Accepted 2026-09-14 | An always-loaded repository trigger and portable maintainer-skill trigger route approval turns to one progressively disclosed maintainer reference. An explicit affirmative records the accepted outcome when required, provides a detailed copy-ready prompt for the next bounded task in a new session, and does not begin it. A rejection remains unaccepted and starts a one-material-question-per-turn interview until the objection, required fix, evidence, and acceptance criteria are understood. Conditional and ambiguous responses cannot silently become acceptance. |
| Publish Wayfinder from one public `somacdivad/wayfinder` repository containing separate `wayfinder` and `wayfinder-maintainer` plugin packages. | Accepted 2026-09-14 | One portable skill source per package supports Codex, Claude, and GitHub Copilot without coupling end users to maintainer authority or duplicating digest-sensitive content. Apache-2.0 and package version `1.0.0-rc.8` apply to repository distribution only; they do not change the frozen contract, candidate identity, certification state, or activation state. |

## Workflow progress

| Workflow | Status | Current decision point |
| --- | --- | --- |
| Initialize | Candidate revision 10 evidence-publication readiness accepted as NOT READY; runtime disabled | Policy decisions 1–18, Slices 1–5, revision-8 history, and the bounded revision-9 Windows corrections and hosted findings are accepted. The revision-10 correction, exact passing hosted execution, promotion readiness, and 34-path local evidence-promotion implementation are accepted. The exact 27-file source/run/attempt evidence set is durable and hash-pinned. Source publication is present at `72da3542f3a7e65f4bcae09943612d8ba09daf3e`, but the accepted readiness review found a decisive workflow/verifier blocker. Evidence publication is not ready or dispatch-eligible; release-registry changes, certification expansion, runtime guidance, and activation remain pending. Initialize remains disabled. |
| Interview | Not started | Pending completion of initialization workflow design. |
| Update | Not started | Pending completion of initialization and interview workflow design; scope explicitly includes taxonomy evolution. |
| Validate | Not started | Pending definition of the project-record contract. |
| Use | Not started | Pending definition of authority, indexes, and retrieval metadata. |

## Stub state

The runtime `SKILL.md` is intentionally non-operational. It identifies planned modes and blocks agents from improvising unfinished workflows. Stage 0 through Slice 5, the exact frozen candidate revision 10 correction, its hosted execution record, the promotion-readiness decision, the local evidence-promotion implementation, and the not-ready evidence-publication readiness result are accepted. The runtime skill contains no maintainer-only directory or routing instructions; those live in the explicit companion skill. The package is not a certified runtime. The exact hosted set is accepted durable maintainer evidence. Protected-environment evidence publication is not ready or dispatch-eligible; release-registry changes, broader certification, runtime routing, and activation remain separate later tranches.

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

Await a separate decision on whether to reopen the frozen Python adapter and the Windows special-file certification mechanism. The bounded harness corrections are accepted, but an exact hosted rerun remains separately approval-gated and is expected to fail while those two blockers remain. Do not publish evidence, add release certification entries, rerun certification, begin forward tests, cross-adapter recovery, full-family certification, runtime guidance, activation, or live-project work from this acceptance.

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

## Candidate revision 8 bounded certification matrix — accepted

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
| Bounded certification-matrix orchestration and available evidence | Accepted 2026-09-14 | The skill owner selected Option A and accepted the bounded certification-matrix tranche as implemented, preserving one passing environment entry and seven explicitly unavailable entries without a completion claim. No follow-up exception was attached. Hosted matrix execution, evidence publication, forward tests, cross-adapter recovery, full-family certification, runtime guidance, activation, and live-project work remain separately authorized tranches; this approval begins none of them. |

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

## Candidate revision 8 hosted certification execution — accepted with failed aggregate

Executed on 2026-09-14 as the separately authorized bounded hosted tranche:

- GitHub Actions workflow run `34867347594`, attempt 1, used the exact source commit `12ca21e6642b2357c78cf09aff1842b03c764e36` and all eight fixed revision-8 entries. The run did not include the pre-existing uncommitted approval-record or repository-validator edits.
- CPython 3.14.7 passed 305/305 cases on macOS and Linux and failed 10 of 305 cases on Windows. Node.js 24.21.0 passed 305/305 on macOS and Linux and failed 4 of 305 cases on Windows. PowerShell 7.6.6 passed 305/305 on Linux and failed 4 of 305 cases on Windows. No runtime, operating-system, or adapter substitution was made.
- The three Windows entries shared failures in `inventory-special-file`, `inventory-exclusions`, `render-output-symlink-component`, and `initialize-minimal`. The CPython Windows entry additionally failed six interruption and rollback recovery cases. The accepted execution record preserves these observed failures without assigning a root cause.
- Every environment report binds to the frozen release, contract, fixture index, expected-output set, registered adapter, source commit, workflow run, and exact runtime identity. Passing reports cover both observed case-sensitive and case-insensitive filesystem behavior, and all eight reports record a successful Unicode filename round trip.
- The strict aggregate rejected the three non-passing Windows reports with `matrix.invalid-entry`, exited 2, and created no aggregate certification JSON or Markdown. Its review-only inventory has SHA-256 `f5b895acd6721657c46969354fcd529f1d0f71bebc846b49361d9ab1aa451086`; the hosted aggregate artifact has SHA-256 `9e5af7d8a7ab046e7632c96ba7acaf25f0c1015e31dea9dd889a5b06f102c327`.
- The eight entry artifacts and aggregate inventory remain GitHub Actions review evidence with 90-day retention through 2026-12-13. They were not copied into accepted durable evidence, published, added to the release certification registry, or used to claim matrix completion or full-family certification.
- This tranche changed no frozen contract, fixture, adapter, parity, or accepted historical-evidence bytes; added no runtime guidance; and did not activate Wayfinder, initialize a live project, run forward tests, or perform cross-adapter recovery.

### Hosted certification-execution approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact eight-entry hosted execution and strict aggregate result | Accepted 2026-09-14 | The skill owner selected Option A and accepted the authentic hosted execution record as five passing entries, three failing Windows entries, and an unsuccessful strict aggregate. The approval preserves the failures and artifact-review boundary and authorizes no investigation, correction, rerun, evidence publication, release certification entry, full-family claim, runtime guidance, activation, or subsequent tranche. |

## Candidate revision 8 Windows certification investigation and correction — accepted

Investigated and accepted on 2026-09-14 as a bounded correction tranche against source commit `12ca21e6642b2357c78cf09aff1842b03c764e36` and authentic GitHub Actions run `34867347594`, attempt 1:

- Retrieved and inspected all eight authentic entry artifacts, their execution records, the aggregate inventory, and the complete hosted logs as temporary review evidence. Nothing was copied into accepted durable evidence or added to the release certification registry.
- Established separate causes for every failure group. `inventory-special-file` and `inventory-exclusions` depend on a FIFO fixture created through Unix-only `os.mkfifo`; Windows therefore lacks the requested filesystem node. `render-output-symlink-component` was a harness snapshot-comparison defect caused by platform-specific symbolic-link target spelling. `initialize-minimal` was a harness normalization defect because canonical JSON escapes Windows backslashes. The six CPython recovery failures share a frozen Python-adapter defect: `_process_alive` uses `os.kill(pid, 0)`, which is not a non-mutating Windows process-existence probe and surfaced stale PIDs as `internal.unexpected` before recovery boundaries were reached.
- Corrected only the maintainer-owned harness where evidence supported it: special-file unavailability now fails explicitly rather than masquerading as a missing selection, rejected render output is compared with its actual pre-invocation snapshot, and canonical JSON workspace paths are normalized using their escaped spelling. The repository validator now recognizes the maintainer runner as a mutable post-migration path.
- Preserved all frozen contract, fixture, registered-adapter, parity, and accepted historical-evidence bytes. The exact suite remains 305 cases with all 96 normative rules cited. Initialization remains disabled.
- Focused local checks passed for the four shared cases on Python, Node.js, and PowerShell, and all six listed Python recovery cases passed on macOS. A synthetic Windows JSON-escaping assertion passed. These local checks do not substitute for Windows execution or the pinned Node.js 24.21.0 matrix target.
- Repository validation passed. The final maintainer doctor passed 29/29 checks under CPython 3.14.7 using the existing portable PowerShell 7.6.6 runtime. Optional PyYAML remained unavailable and the accepted dependency-free checks were used.
- Two blockers remain intentionally unresolved: Windows cannot construct the harness's FIFO fixture through the selected standard-library mechanism, and correcting Python recovery requires changing the frozen registered adapter. An exact rerun from the accepted worktree is therefore expected to correct the render and golden-normalization failures but still fail the two inventory cases on all Windows entries and the six recovery cases on CPython Windows.
- No hosted rerun, evidence publication, release-certification entry, forward test, cross-adapter recovery, full-family claim, runtime guidance, activation, live-project initialization, commit, or push was performed.

### Windows investigation/correction approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded Windows certification investigation and maintainer-harness correction | Accepted 2026-09-14 | The skill owner approved the investigation findings and smallest maintainer-only corrections with the disclosed local-test boundary and two remaining Windows blockers. This acceptance records the result only. It does not authorize reopening frozen adapter or contract bytes, committing or pushing the worktree, dispatching the exact hosted rerun, publishing evidence, adding certification entries, claiming full-family certification, adding runtime guidance, or activating Wayfinder. |

## Candidate revision 8 maintainer-efficiency tranche — accepted

Implemented and accepted by the skill owner on 2026-09-14 as a maintainer-only workflow and tooling tranche:

- Added a compact `references/current-state.md` containing the frozen candidate and activation state, accepted package, adapter, parity, matrix, and historical-evidence identities, the current approval boundary, the pending action, and exact routes into this chronological record. The doctor deterministically rejects drift between the compact reference, package facts, accepted evidence, and required chronology anchors.
- Revised the maintainer skill and workflow for progressive disclosure. Routine work reads the compact state; exact chronology sections are loaded only when prior rationale is relevant; the full record is required when reopening a decision, changing evidence governance, or recording an accepted outcome.
- Added canonical recipes to resolve and reuse runtime paths, inspect CLI help, batch repeated `--case` and `--category` selections, bound reads, avoid unjustified repeat checks, prefer summary or structured output, and stop at approval boundaries.
- Added doctor summary, verbose, stable JSON, and quiet-success internal-preflight modes. Focused tests retain repository, package, evidence, and every registered adapter byte and identity check while probing only the selected adapter runtime.
- Added `describe`/`context` output for canonical paths, candidate identity, conformance counts, adapter registry, runtime requirements, and approval boundaries. Added a dependency-free offline matrix-artifact reviewer that performs no network access or writes, preserves result-set versus aggregate-invocation digest distinctions, validates exact 305-case reports and coverage metadata, summarizes failures by environment, and labels Actions material review-only.
- Added dependency-free maintainer-tool regressions for doctor modes and failures, quiet preflight, multi-case batching, selected-adapter runtime isolation, runtime diagnostics, context output, artifact review, evidence overwrite refusal, output budgets, and accepted-evidence preservation.
- Explicitly excluded the bundled skill-creator `quick_validate.py` from canonical Wayfinder verification because it requires PyYAML, which is not a repository dependency. The canonical doctor and repository validator remain authoritative; an already-available PyYAML environment may run the external validator once only as a secondary check.
- The final routine startup reference set is 12,878 bytes versus 73,565 bytes before the tranche, an 82.49% reduction. Successful doctor output is 29 bytes versus 2,169 bytes, a 98.66% reduction. The representative three-case workflow reduced command output from 7,263 to 2,188 bytes, canonical CLI calls from five to three, and wall time from 4.40 to 1.20 seconds. The initial two failed exploratory setup calls were eliminated in the optimized replay.
- Eight maintainer-tool regression tests passed. The unchanged revision-8 suite passed 305/305 cases under CPython 3.14.7, the repository validator passed, the final full doctor passed 31/31, and `git diff --check` passed. Optional PyYAML remained unavailable and was not installed.
- Frozen contract, fixture, registered-adapter, parity, accepted historical-evidence, and accepted certification-evidence bytes remained unchanged. Initialization remains disabled. No hosted rerun, evidence publication, release-certification entry, forward test, cross-adapter recovery, runtime guidance, activation, live-project initialization, commit, or push was performed.

### Maintainer-efficiency approval checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Bounded maintainer-efficiency workflow and tooling | Accepted 2026-09-14 | The skill owner approved the tranche as implemented, including the compact validated state, efficient canonical recipes, output and preflight changes, offline review command, regression coverage, measurement caveats, and explicit non-PyYAML canonical-validation boundary. This acceptance records the result only. It does not reopen candidate revision 8, authorize correction of either Windows blocker, dispatch a hosted rerun, publish or promote evidence, add certification entries, claim full-family certification, add runtime guidance, activate Wayfinder, initialize a live project, commit, or push. |

## Candidate revision 9 Windows corrections — accepted

Implemented on 2026-09-14 under the owner's explicit Option A reopening authority as one bounded correction tranche:

- Reopened frozen candidate revision 8 and advanced every current identity to `v1-candidate-revision-9` while preserving `frozen`, `unactivated-frozen`, and disabled initialization status.
- Replaced the Python adapter's Windows `os.kill(pid, 0)` branch with a non-mutating `OpenProcess(SYNCHRONIZE)` plus `WaitForSingleObject(handle, 0)` query through standard-library `ctypes`. PID values outside `1..0xffffffff` are stale without conversion; `WAIT_TIMEOUT` is live; `WAIT_OBJECT_0` is stale; access denial, unexpected open failures, `WAIT_FAILED`, and unexpected wait results are conservatively live or indeterminate; every opened handle is closed exactly once. The POSIX branch is unchanged.
- Reordered both Python recovery call sites so malformed lock, requested action and operation, plan, and host predicates take precedence over process probing. PID reuse remains a conservative version-1 limitation: a reused live PID blocks reclamation.
- The maintainer harness continues to use `os.mkfifo` where supported. On Windows it binds a real pathname `AF_UNIX`, `SOCK_STREAM` socket beneath the temporary workspace, retains the socket through adapter execution and assertions, and closes and removes it deterministically. Provider or filesystem unavailability fails the case explicitly.
- Clarified `WF-INV-003` and `WF-INV-004` without weakening them: actual symbolic links and junctions remain `symlink`; Windows non-link reparse objects are `unsupported-file`, receive `unsupported-special-file`, and are never opened. Python uses non-following mode and reparse metadata, Node combines parent `Dirent`, `lstat`, and documented `readlink`, and PowerShell uses `.NET` `LinkTarget` rather than equating every reparse point with a link. Explicit selection and traversal share each adapter's classification path.
- The canonical builder rebuilt the digest graph. The exact contract is `3c79c6e1d2eae7c6016d789c9ade75125a2ec1dcc43f458541f9d7c63654bdd9`; release `1826fa1c1323561001565fe4bd635c0432306ced078320f1eecdad81ff268ffb`; fixture index unchanged at `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`; expected-output set `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`; Python adapter `f8fe1a0987a37e8a9a43003ede1bcb9eda590c88511daebaafcdd5d13932337a`; Node adapter `df0f3c2a000454b2f7aaa8fcf6762b670aab34b9cb721da571fe334ae29f10ac`; PowerShell adapter `b7f8687b5b4ede2bd124999c23aaa12681a07bddc0597255873fa9c4493fa8c9`.
- The exact suite remains 305 cases citing all 96 normative rules. Focused inventory cases passed on all adapters; the complete Python Apply/recovery category passed 51/51; deterministic maintainer tests passed 18/18; and each complete adapter suite passed 305/305 locally.
- Canonical exclusive evidence creation produced `candidate-revision-9-local.json` (`b7c9b046d2970c308530d2ba05893213fbf81445e96c4b355a9c3863c4fe734a`) and Markdown (`99a5ef242b1e96e966d1fe9cff3549565008520451921bc1e9d7abfc3237d264`), plus `parity-revision-9-local.json` (`3643fe1fb86a1c1fa99e7f47489e0f0c4965c56dbe86c6c01622d31887de9d4c`) and Markdown (`11f3f7436b96c2be98e5efeb8fb2fb29bb373ba8826ea38b0594aeba806c00f5`). All three result sets agree, and 900 normalized observations agree at `4463448355c7662a09bb2112052179df0e95216e5bd1092968ee4ddc95b6d233`.
- The exclusive freeze proposal is `proposed-freeze-revision-9.json` (`9baf19c1f17848b7f0b1b12ff0e821472358f2aadde3dafa4f423194cb5e916c`) and Markdown (`b75d8862b47a16b13c4862643e7551d44777c98348cd9608f5c5aebd1ff8855f`). The owner's explicit Option A response is recorded exclusively in `freeze-acceptance-revision-9.json` (`a934affb933fac7ad994257453afda952b6e81d7852e791f60389ebce4767088`) and Markdown (`2f0c4bb8859bb3f7f0356038922678673544ddf45907bcdb680670813a581691`).
- Local verification used CPython 3.14.7, Node.js 22.22.3, and PowerShell 7.6.6 on macOS. The Win32 branches are deterministically simulated but not executed on a real Windows host, and local Node is not the pinned Node.js 24.21.0 matrix target. AF_UNIX provider/filesystem availability and the exact non-link reparse behavior remain hosted Windows obligations.
- Every revision-8 evidence file remains byte-for-byte preserved and historical for revision 9, including local candidate and freeze records, accepted parity, accepted macOS matrix evidence, and GitHub Actions run `34867347594`, attempt 1 review material. No aggregate or release-certification entry exists for revision 9.
- No hosted execution, artifact download or promotion, evidence publication, release-certification entry, forward test, cross-adapter recovery, runtime guidance, activation, live-project work, commit, or push occurred.

### Revision 9 freeze-review checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact revision-9 frozen bytes and local evidence | Accepted 2026-09-14 | The skill owner selected Option A and accepted the exact revision-9 frozen bytes and local candidate and parity evidence. This acceptance records the reviewed outcome only. It does not dispatch hosted certification, publish evidence, add a release-certification entry, claim full-family certification, add runtime guidance, activate Wayfinder, initialize a live project, commit, push, or begin any later tranche. |

## Candidate revision 9 hosted certification execution — accepted with failed aggregate

Authorized by the skill owner on 2026-09-14 as one bounded hosted-execution tranche:

- Publish the complete accepted revision-9 worktree to the dedicated `candidate-revision-9-certification` branch without changing `main`.
- Dispatch the exact eight-entry revision-9 matrix from that branch using CPython 3.14.7, Node.js 24.21.0, and PowerShell 7.6.6 on the accepted operating-system targets.
- Preserve every resulting Actions artifact as review-only, run the strict aggregate, and report the authentic result without promotion or publication.
- Do not add a release-certification entry, claim full-family certification from incomplete or failing results, add runtime guidance, activate Wayfinder, initialize a live project, perform forward testing or cross-adapter recovery, or begin any later tranche.

Executed on 2026-09-14 within that authority:

- Published the complete accepted revision-9 worktree only to `candidate-revision-9-certification` at commit `b39203656049ad536ca690086e746ec860d7ba46`; `main` was not changed. GitHub Actions run `34890622679`, attempt 1, executed from that exact branch and commit.
- Five fixed entries passed 305/305: CPython 3.14.7 on macOS and Linux, Node.js 24.21.0 on macOS and Linux, and PowerShell 7.6.6 on Linux. All 213 required negative and mutation cases and the three interruption-boundary cases passed in each reported entry.
- All three Windows entries completed the 305-case suite and failed three cases each: CPython 3.14.7, Node.js 24.21.0, and PowerShell 7.6.6 each passed 302/305. Their result-set hashes are respectively `895a6ba36ae707dc2da20dec246c466bbfe47e686f2ebc0748587010a01fa5fb`, `ff624bf9193be656809dd7e740af091ed8c96cc8af44d991896fad39e619fd04`, and `cdf25748fa2f1db5b521fa6bb019cc7b8ecb90a3f69c2221885a43ca6465f320`. The workflow log exposes counts and report bindings but not the individual failed case identifiers; the reports were not downloaded under the tranche's explicit exclusion, so no case identity is inferred here.
- The strict aggregate rejected the three non-passing Windows reports with `matrix.invalid-entry`, exited 2, and created no aggregate certification JSON or Markdown. The review-only incomplete-inventory artifact is 697 bytes with SHA-256 `4e25093e7a7aad827cf81e5d85c07031183642caa86c263298259d66d642b9b1`.
- The eight review-only entry artifacts have SHA-256 digests: Node Linux `d1652b1a4dbdbc683eac6adc1e06c77f5c79f70e88ebb62139e5319f8a430e43`; Node macOS `5dca75bb8b1bcf92d8d50557bf8621fe6be4d0633e528a308147cf0261edd4ea`; Node Windows `ef07e9e2de54c76b1aff0efd0e7ccbad1065629240043cb6a8932db2f8188d2d`; PowerShell Linux `b93a28b86d09d0365a0f0e287b19090b2f1877cf1a4de59ac43940e32f1f30b0`; PowerShell Windows `cdb2c56d2c339c3a4b5a3e26242e15c805a351f664053393afcb36a0b2819c47`; Python Linux `1441b5e582c1fbe0e5f8039abf038ff3d0ceb6c2f45af26ea4174445b3108304`; Python macOS `64c9196a7f9ef6a11068b55c50b0928467ef8ca0da16aca24cebbe80ac0e70d5`; Python Windows `74a839b603a839b6a105cceb96884d2ac26aae26321745affb2b963464450c9b`. GitHub reports expiry on 2026-12-13.
- No hosted artifact was downloaded, promoted, copied into durable accepted evidence, published, or added to the release certification registry. No investigation, correction, rerun, full-family claim, runtime guidance, activation, live-project initialization, forward test, or cross-adapter recovery occurred. The owner explicitly accepted the authentic execution record on 2026-09-14; acceptance preserves the failures and review-only artifact boundary and authorizes no later tranche.

### Revision 9 hosted-execution checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact eight-entry revision-9 hosted execution | Accepted 2026-09-14 | The skill owner accepted run `34890622679`, attempt 1, exactly as five passing entries, three failing Windows entries, and no strict aggregate. Acceptance preserves the failures and review-only artifact boundary and authorizes no artifact download or promotion, investigation, correction, rerun, evidence publication, release-certification entry, full-family claim, runtime guidance, activation, or later tranche. |

## Candidate revision 9 maintainer reliability and efficiency — accepted

Authorized by the skill owner on 2026-09-14 as one bounded maintainer-only implementation tranche after a session-performance retrospective:

- Consolidate mutable candidate, evidence, activation, and tranche status in `references/current-state.md`; keep root repository instructions and the runtime stub stable and route maintainers through the compact state.
- Add an explicit action-authorization gate and failure classification protocol before authentication, downloads, hosted dispatch, publication, destructive work, and other consequential external actions.
- Add a canonical no-bytecode maintainer regression command, exact design-record section retrieval, mode-aware handoff scaffolding, bounded matrix failure details, GitHub annotations and job summaries, explicit workflow run identity, and uploaded-artifact digest reporting.
- Add regression coverage and a selectively loaded session-audit template. Measure representative workflows by calls, failures, elapsed time, reference and output bytes, authentication prompts, generated files, and validator reruns.
- Preserve the exact frozen revision-9 contract, fixture index, expected outputs, registered adapters, and every accepted evidence file. Do not download or promote hosted artifacts, dispatch or rerun hosted certification, create or publish evidence, add a release-certification entry, claim full-family certification, activate Wayfinder, initialize a live project, commit, push, or begin another tranche.

Implemented on 2026-09-14 within that authority:

- Updated the root repository instructions, runtime status stub, maintainer skill and workflow, current-state routing, maintainer command and regression tests, repository validator, hosted entry wrapper, and certification workflow. Added the selectively loaded session-audit template. The runtime status edit removes stale candidate chronology without adding operational guidance; it does not change the digest-bound contract or registered adapters.
- `maintain.py self-test` discovers all maintainer-owned regression modules, uses isolated no-bytecode controls, refuses pre-existing or newly generated repository bytecode, and supports summary, verbose, and JSON output. The canonical run passed 26/26 tests with zero bytecode artifacts.
- `record-section` retrieves one exact level-two chronology section. For the representative implementation workflow, the previous root, maintainer skill, current state, workflow, and full chronology totaled 106,653 bytes; the same set with the exact 2,124-byte routed section totaled 24,692 bytes, a 76.85% reduction. Doctor summary was 29 bytes and 1.29 seconds; self-test summary was 33 bytes and 2.37 seconds on the local host.
- Matrix-entry output now includes every failed case ID, up to 25 structured 512-character diagnostics, and an explicit truncation count. The hosted wrapper emits bounded GitHub error annotations and a job-summary table. The workflow has an explicit branch/SHA run name, non-canceling concurrency, and records the SHA-256 digest returned for every uploaded entry and aggregate artifact.
- Mode-aware handoffs distinguish investigation, implementation, hosted review, and acceptance recording. The workflow documents public metadata and failed-log inspection before an explicitly authorized exact artifact download, prohibits opportunistic OAuth, and requires failure classification after unsuccessful calls.
- Repository validation passed, the workflow parsed as YAML, `git diff --check` passed, and the canonical doctor passed 33/33 with CPython 3.14.7, local Node.js 22.22.3, and PowerShell 7.6.6. Local Node remains different from the pinned Node.js 24.21.0 matrix target.
- The frozen contract, fixture index, expected-output set, all registered adapters, and every accepted evidence file remain unchanged. No artifact was downloaded or promoted; no hosted workflow was dispatched or rerun; no evidence, release-certification entry, full-family claim, activation, live-project work, commit, or push occurred.

### Maintainer reliability checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Candidate revision 9 maintainer reliability and efficiency | Accepted 2026-09-14 | The skill owner accepted the exact maintainer-only changes and local verification. Acceptance records this outcome only and does not authorize artifact download or promotion, hosted investigation, correction or rerun, evidence creation or publication, a release-certification entry, a full-family claim, activation, live-project work, commit, push, or another tranche. |

## Candidate revision 9 Windows failure investigation — accepted

Investigated and accepted by the skill owner on 2026-09-14 against exact source commit `b39203656049ad536ca690086e746ec860d7ba46`, GitHub Actions run `34890622679`, attempt 1:

- The three Windows entries each failed `inventory-special-file`, `inventory-exclusions`, and `initialize-minimal`. The five macOS/Linux entries passed 305/305, while the Windows Python process correction succeeded across all 51 Apply cases, including both failure-boundary matrices and interrupted rollback.
- The two inventory failures occurred before adapter invocation because hosted CPython 3.14.7 did not expose `socket.AF_UNIX`. No pathname socket existed or remained live through assertions, so the shared harness capability assumption—not adapter behavior—was observed to fail.
- `initialize-minimal` completed adapter execution and matched the normalized preview, all six payload hashes, bundle inventory, and mutation snapshots. Only the normalized plan differed because root replacement left the Windows separator in the descendant absolute `recordRoot`. The accepted correction is structural normalization of environment-bound plan fields without modifying the frozen golden projection.
- The offline matrix reviewer found all eight authentic reports and all nine failed observations, and direct hashes matched the attempt-1 bindings. Its three Markdown-binding errors came from applying POSIX `Path.name` semantics to recorded Windows paths. The accepted correction resolves basenames from either separator while preserving missing, ambiguous, malformed, and hash-mismatch rejection.
- The owner authorized Option 1 as a maintainer-only correction: dependency-free native Winsock fixture creation, structural plan normalization, cross-host reviewer path resolution, focused regression tests, complete local adapter suites, local parity, repository validation, and integrity checks. Authentic Windows behavior remains unverified pending a separately authorized hosted execution.
- This authority excludes any frozen contract, release, fixture, expected-output, adapter, registry, manifest, workflow, package-version, governed-byte, or accepted-evidence change; any weakening or waiver; evidence creation or promotion; hosted dispatch or rerun; candidate advancement, certification, release, activation, forward testing, cross-adapter recovery, runtime guidance, live-project work, or Git staging, commit, or push.

### Revision 9 Windows investigation checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Candidate revision 9 Windows failure investigation | Accepted 2026-09-14; correction authorized | The owner accepted the exact investigation findings and authorized only the bounded maintainer correction described above. The correction itself remains pending review and is not accepted by this record. A hosted-execution tranche remains separately approval-gated. |

## Candidate revision 9 maintainer-only Windows correction — accepted

Implemented and accepted by the skill owner on 2026-09-14 as the exact bounded correction authorized by the preceding investigation:

- Replaced the Windows fixture's dependency on CPython `socket.AF_UNIX` with dependency-free `ctypes` interop against `Ws2_32.dll`. The harness declares every Winsock signature, uses a pointer-sized `SOCKET`, initializes Winsock 2.2, binds a null-terminated UTF-8 pathname through the SDK-compatible `SOCKADDR_UN`, verifies the pathname with non-following metadata, and retains explicit socket, Winsock, and pathname ownership through adapter invocation and assertions.
- Cleanup closes each acquired socket and successful Winsock registration exactly once, removes only an owned pathname, handles partial initialization and assertion failures, and reports stable fail-closed diagnostics. POSIX continues to use the existing FIFO fixture. No fallback object, skipped case, conditional pass, or adapter-classification change was introduced.
- `initialize-minimal` now parses and normalizes the plan structurally. Only the temporary physical `workspace.workspaceRoot`, its manifest-bound descendant `workspace.recordRoot`, and the pre-existing contract test marker are changed before canonical serialization. Non-path strings remain byte-semantically unchanged, and malformed, unsafe, outside, or inconsistent record roots fail closed. The frozen golden remains unchanged and retains normalized plan SHA-256 `4663f40f76f135f381feb6a216bf44482d521dfba4c826d937736585fbb3595f`.
- The offline matrix reviewer derives report basenames from either path separator, searches only inside the supplied artifact directory, requires one non-symbolic unambiguous match, binds the recorded JSON basename to the report under review, and still verifies actual JSON and Markdown SHA-256 digests. Empty, malformed, missing, ambiguous, and mismatched paths remain rejected.
- Focused maintainer logic verification passed 36/36 with no repository bytecode. The three focused conformance cases passed 3/3 for Python, Node.js, and PowerShell; all three complete local suites passed 305/305; and 900 normalized observations agreed at `4463448355c7662a09bb2112052179df0e95216e5bd1092968ee4ddc95b6d233`.
- Repository validation and `git diff --check` passed. The canonical doctor passed 33/33 before and after correction. The authentic review-only attempt-1 artifact directory validated all eight reports and execution statuses with zero binding issues while preserving the genuine three failed Windows cases per adapter and the failed strict aggregate.
- Contract `3c79c6e1d2eae7c6016d789c9ade75125a2ec1dcc43f458541f9d7c63654bdd9`, release `1826fa1c1323561001565fe4bd635c0432306ced078320f1eecdad81ff268ffb`, fixture index `a904318317a193dce9d3430770c3cbd8127cc8dc8cb0a7ced9ce6e6d087c70b6`, expected-output set `9d149d3b3603547b509803b3bfb119b79e40db41f97e848f76554f5dccbf1b94`, all three registered adapters, and every accepted evidence file remain unchanged.
- The macOS tests verify maintainer ownership and normalization logic but do not verify actual Windows AF_UNIX reparse metadata, adapter classification of the live socket, Node.js metadata-only `readlink` behavior, hosted pathname encoding and length behavior, or cleanup on the hosted Windows image. The old hosted execution remains historical and cannot certify corrected source.
- No hosted run, evidence creation or promotion, candidate revision, certification claim, release entry, activation, forward test, cross-adapter recovery, runtime guidance, live-project work, staging, commit, or push occurred during the correction or this acceptance record.
- In the same owner response that accepted the correction, the owner separately authorized a full eight-entry hosted rerun. Per the new-session boundary, that hosted execution was not begun here. It must use one exact published source commit; the publication scope must first be resolved against the broader pre-existing dirty worktree.
- At the start of the separately authorized hosted tranche, the owner resolved that publication boundary as all modified and untracked paths then present in the `candidate-revision-9-certification` worktree. This authorizes one exact commit and push containing that complete set for the eight-entry rerun; it does not authorize evidence promotion or any excluded later tranche.

### Revision 9 maintainer-only Windows correction checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Candidate revision 9 maintainer-only Windows correction | Accepted 2026-09-14; full eight-entry hosted rerun authorized | The owner accepted the exact correction packet and authorized a separate hosted-execution tranche for all eight entries. Acceptance makes no Windows or full-family certification claim and does not itself publish source, dispatch Actions, promote evidence, add a release-certification entry, activate Wayfinder, or begin a later tranche. |

## Candidate revision 9 corrected-source hosted execution and residual Windows investigation — accepted

Executed, investigated, and accepted by the skill owner on 2026-09-14 against exact source commit `e589f1b412847e886041047b2599bc70d6f11d1c`, GitHub Actions run `34907233259`, attempt 1:

- The separately authorized corrected-source rerun used all eight fixed matrix entries from the exact published branch and commit. CPython 3.14.7 on macOS and Linux, Node.js 24.21.0 on macOS and Linux, and PowerShell 7.6.6 on Linux each passed 305/305.
- CPython Windows and PowerShell Windows each passed 304/305 and failed only `initialize-minimal`. Node.js Windows passed 302/305 and failed `inventory-special-file`, `inventory-exclusions`, and `initialize-minimal`. The strict aggregate correctly exited 2 with `matrixComplete:false`; no aggregate certification report was created.
- Offline review of the already-downloaded review-only artifacts at `/private/tmp/wayfinder-r9-hosted-rerun.UzPZ4m` found all eight reports and execution statuses, verified every recorded JSON and Markdown hash binding, and returned `issues:[]` and `ok:true`. The failed aggregate and genuine Windows case failures remain unchanged. The artifacts were not promoted or copied into accepted evidence.
- The shared `initialize-minimal` failure is a maintainer-harness identity-normalization defect. The plan normalizer compares the adapter-emitted physical Windows `workspaceRoot` with the temporary-directory spelling as text; the authentic reports support a physically equivalent alternate spelling, most likely a short-name versus long-name alias, but do not retain enough raw data to prove the exact alias mechanism. The correction must use Windows physical path identity for the existing workspace root and retain strict structural and lexical validation that `recordRoot` is the expected safe descendant. It must not globally rewrite separators or mask unsafe, outside, or divergent paths.
- The native Winsock fixture itself succeeded on authentic Windows for Python and PowerShell. Windows represents the pathname AF_UNIX socket as a reparse point tagged `IO_REPARSE_TAG_AF_UNIX`. The Node.js adapter raised `internal.unexpected` before its existing Windows `Dirent`/metadata-only `readlink` classification branch could return `unsupported-file`; the high-confidence control-flow attribution is that `fs.lstatSync` throws on this unhandled reparse point. The sanitized adapter result does not preserve the underlying Node/libuv error code, so that exact code remains unknown.
- The revision-10 correction must narrowly reorder or otherwise guard Node.js Windows classification so the already-supplied parent `Dirent` can distinguish a true link through metadata-only `readlink` from an unsupported non-link reparse object before a failing `lstat` path. It must preserve fail-closed behavior for missing, ambiguous, inaccessible, or unexpected objects, must never content-read or traverse the socket, and must not weaken the existing inventory assertions.
- Existing revision-9 accepted evidence remains immutable historical evidence and cannot certify revised source. No evidence was created, overwritten, relabeled, accepted, or promoted; no release-certification entry, Windows or full-family certification claim, runtime guidance, activation, live-project initialization, forward test, or cross-adapter recovery occurred.
- The owner accepted these findings and authorized a separate candidate-revision-10 correction tranche. That authority includes the Node.js adapter change and the minimum candidate, release, registry, manifest, package-identity, harness, test, and integrity updates required by the established candidate-change workflow. It excludes contract-semantic, fixture-corpus, frozen-golden, historical-evidence, Python-behavior, or PowerShell-behavior changes unless an unexpected dependency is reported and separately authorized. It also excludes evidence creation or promotion, hosted dispatch, certification claims, runtime guidance, activation, forward testing, cross-adapter recovery, live-project work, staging, commit, and push.
- Per the accepted session boundary, implementation must begin in a new session and end with a detailed correction packet and one explicit approval question. A full eight-entry hosted rerun for the corrected revision remains a later, separately approval-gated tranche.

### Revision 9 corrected-source hosted execution and residual investigation checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact corrected-source rerun and residual Windows investigation | Accepted 2026-09-14; candidate-revision-10 correction authorized | The owner accepted run `34907233259`, attempt 1, exactly as five passing entries, three residual Windows failures, and no strict aggregate, accepted the bounded investigation findings, and authorized only the candidate-revision-10 correction described above. This record does not accept an unimplemented correction or authorize its hosted rerun, evidence promotion, certification, activation, staging, commit, push, or any later tranche. |

## Maintainer approval-response governance — accepted

Investigated and accepted by the skill owner on 2026-09-14 as a separate maintainer-only governance decision:

- The existing runtime facilitation protocol already requires a detailed new-session prompt after approval of a completed implementation slice, and the chronological record preserves the same constraint. The maintainer skill and repository instructions do not generalize that response requirement to every explicit acceptance, authorization, or approval checkpoint, so the strongest rule may not be loaded during maintainer work.
- Existing rejection guidance permits revision and follow-up questions but does not define a fail-closed rejection loop that continues until the objection, required correction, supporting evidence, and acceptance criteria are understood. Conditional or ambiguous responses likewise need an explicit classification boundary so they cannot silently become acceptance.
- The mutable `current-state.md` is not the canonical home for evergreen interaction behavior. The runtime facilitation reference is also not sufficient for the independently installable maintainer plugin. The accepted design therefore uses an always-loaded repository trigger, a portable maintainer-skill trigger, and one selectively loaded maintainer-owned approval-response reference, with workflow, handoff, and regression reinforcement.
- On an unambiguous affirmative response, the agent must restate the interpreted decision, record the accepted outcome when required, identify the next bounded task, provide a detailed copy-ready prompt for starting it in a new session, and stop without beginning that task. The prompt carries repository and skill locations, durable authority, required reading, objective, exclusions, working-tree boundaries, invariants, verification, expected packet, and the next approval question.
- On rejection or a material request for revision, the agent must not record acceptance or advance state. It must use the Wayfinder facilitation stance, ask one material question per turn, distinguish scope, behavior, evidence, risk, wording, verification, and authority concerns, periodically synthesize what is accepted, disputed, inferred, and unresolved, and continue until the reason, required fix, evidence, and acceptance criteria are sufficiently explicit to present a revised packet.
- A conditional response is accepted only when its conditions are explicit follow-up work that does not alter the approved boundary; otherwise it remains pending. Praise, silence, a vague acknowledgment, or a generic request to continue is not approval when explicit approval is required.
- The owner selected the layered Option A and authorized a new-session implementation tranche limited to `AGENTS.md`, the maintainer `SKILL.md`, a maintainer-owned progressively disclosed reference, `references/workflow.md`, focused maintainer handoff/tooling and tests, repository validation where needed, and pending/decision records. The implementation must preserve independent plugin installability and avoid duplicating mutable candidate facts in always-loaded instructions.
- This acceptance does not authorize changing `plugins/wayfinder/skills/wayfinder/references/facilitation.md`, runtime guidance, candidate identity, contract or release bytes, fixtures, expected outputs, registered adapters, registries, manifests, package version, accepted evidence, activation state, or live project data. It does not authorize hosted dispatch, publication, staging, commit, push, or implementation of the separately authorized candidate-revision-10 correction.
- The candidate-revision-10 correction remains authorized and queued. The approval-response governance tranche must finish with an approval packet and must not begin revision 10 automatically.
- The authorized governance implementation is now complete. `AGENTS.md` carries the concise always-loaded route; the independently installable maintainer skill routes both approval questions and owner responses to `references/approval-response.md`; the canonical reference defines affirmative, rejection/revision, conditional, ambiguous, conflicting, and terminal-workflow handling; and the workflow and generated handoff reinforce the new-session stop boundary.
- Focused handoff tests cover every handoff kind, preserve the investigation command exclusions, require the affirmative new-session prompt and stop, require all four rejection-understanding targets, and check bounded deterministic output. The dependency-free repository validator checks the repository route without mutable status, both maintainer-skill trigger directions, canonical response classifications, workflow route, and handoff reminder.
- The owner explicitly accepted the implementation on 2026-09-14 exactly as reviewed. Acceptance records the governance implementation only; it does not begin candidate revision 10 or authorize any excluded runtime, governed-byte, adapter, manifest, evidence, activation, hosted, live-project, or Git action.

### Maintainer approval-response governance checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Layered maintainer approval-response protocol | Accepted 2026-09-14 | The owner explicitly accepted the complete implementation exactly as reviewed. Candidate revision 10 is the next separately authorized bounded task and must begin from a detailed prompt in a new session; all hosted, evidence, activation, and Git actions remain outside that task unless separately authorized. |

## Candidate revision 10 Windows correction — accepted

Implemented on 2026-09-14 under the separately accepted candidate-revision-10 correction authority:

- The maintainer harness now validates the adapter-emitted existing Windows `workspaceRoot` against the supplied temporary workspace with physical file identity. This accepts physically equivalent spellings such as a short-name/long-name alias, rejects missing, inaccessible, malformed, inconsistent, or divergent roots, and still requires the emitted `recordRoot` to be the exact lexical descendant implied by the portable manifest `recordRoot`.
- The Node.js Windows classifier now consults the already-supplied parent `Dirent` before `lstat`. A reparse candidate is a `symlink` only when metadata-only `readlink` succeeds; `EINVAL` is accepted as `unsupported-file` only while refreshed parent metadata still identifies the object as a reparse candidate. Missing, inaccessible, ambiguous, changed, or unexpected metadata fails closed. No socket content is read and the path is not followed or traversed.
- The candidate advances to `v1-candidate-revision-10` while preserving contract status `frozen`, release status `unactivated-frozen`, disabled activation, all 305 cases, all 96 cited normative rules, the fixture index, and the complete frozen expected-output set. Python changes only its embedded candidate identity; PowerShell bytes and both adapters' observable behavior remain unchanged.
- Deterministic correction tests passed 6/6, the canonical maintainer self-test passed 41/41 with no bytecode, the three focused cases passed 3/3 on each local adapter, and the complete local suites passed 305/305 on each adapter. Dependency-free repository validation and diff hygiene passed. These are local verification results only, not new certification evidence.
- Accepted and historical revision-8 and revision-9 evidence remains byte-for-byte preserved and cannot certify revision 10. No revision-10 evidence, hosted execution, artifact download, evidence promotion, release-certification entry, certification claim, runtime guidance, activation, forward testing, cross-adapter recovery, live-project change, staging, commit, or push is part of this checkpoint.
- Local verification remains verification only. Authentic post-correction Windows execution is absent, and local Node.js 22.22.3 is not the pinned hosted Node.js 24.21.0 target.
- The owner explicitly accepted the exact correction on 2026-09-14 and separately authorized the full eight-entry hosted rerun as the next bounded new-session task. Acceptance makes no Windows, matrix, adapter-family, or full-family certification claim and did not begin publication, hosted execution, artifact download, evidence creation or promotion, a release-certification entry, runtime guidance, activation, forward testing, cross-adapter recovery, live-project work, staging, commit, or push.
- The authorized hosted rerun must use one exact published source commit. Because this acceptance does not itself authorize staging, commit, or push of the broader dirty worktree, the source-publication scope and target must be resolved explicitly at the start of that new-session task before any Git mutation.

### Candidate revision 10 correction checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Candidate revision 10 Windows correction | Accepted 2026-09-14; full eight-entry hosted rerun authorized | The owner accepted the exact correction packet and authorized a separate hosted-execution tranche for all eight entries. Acceptance makes no Windows, matrix, adapter-family, or full-family certification claim and does not itself publish source, dispatch Actions, download or promote artifacts, create evidence, add a release-certification entry, activate Wayfinder, or begin any later tranche. |

## Candidate revision 10 hosted certification execution — accepted

Published, executed, and accepted by the skill owner on 2026-09-14 as the separately authorized bounded hosted-rerun tranche:

- Published exactly the authorized 26-path candidate-revision-10 source set as commit `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54` on `candidate-revision-9-certification`, with parent `e589f1b412847e886041047b2599bc70d6f11d1c`. The set was `.claude-plugin/marketplace.json`, `AGENTS.md`, `CHANGELOG.md`, `README.md`, `docs/architecture.md`, `docs/certification.md`, the three maintainer plugin manifests, maintainer `SKILL.md`, `approval-response.md`, `current-state.md`, `design-record.md`, `workflow.md`, the conformance runner, `maintain.py`, `test_maintain.py`, `test_windows_corrections.py`, the three runtime plugin manifests, `contract.json`, `release.json`, the Node.js and Python adapters, and `scripts/validate_repository.py`.
- Pushed only `refs/heads/candidate-revision-9-certification:refs/heads/candidate-revision-9-certification` to `origin` without force. The remote branch resolved to the exact source commit. `main` remained `12ca21e6642b2357c78cf09aff1842b03c764e36`; no tag, other branch, remote, or ref was changed.
- GitHub Actions run `34921918384`, attempt 1, executed from that exact branch and commit. All eight fixed entries passed 305/305 with no failed case IDs: CPython 3.14.7 on macOS, Linux, and Windows; Node.js 24.21.0 on macOS, Linux, and Windows; and PowerShell 7.6.6 on Linux and Windows. No runtime, operating system, adapter, or matrix entry was substituted.
- On every Windows entry, `initialize-minimal`, `inventory-special-file`, and `inventory-exclusions` passed. The strict aggregate passed with exit status 0. Its matrix result is complete; the aggregate JSON SHA-256 is `be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50`, aggregate Markdown SHA-256 is `ffe1fe3dc6ae9ed1b21356943ea8f98451221a5e8248043d74cf21c5a0b3cf18`, and matrix SHA-256 is `2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0`.
- The exact review-only artifact names and GitHub-reported SHA-256 digests are: `wayfinder-python-macos-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`e0d27fcbc9fea7fae8ae55f2ed6deaa96b99110bc9775822ac3b363efc447506`); `wayfinder-python-linux-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`5b7832b00b10b25516e001fe62acea84512faba6897ba3018954a6ee591e8c25`); `wayfinder-python-windows-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`ca16a929eff072b14edcb37c2ba10d726a4038c937a3ce4944345e7e48a8c4d8`); `wayfinder-node-macos-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`093149b947aaffe855e57a9e7e1b1aff34cbbd45bd3193befc8ad0a14918cb4c`); `wayfinder-node-linux-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`8792e3d57ffb611cbb1af41beb5d5d1ca34146c3b55126073ec140c8f5822059`); `wayfinder-node-windows-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`b3c83a9308b5388f1febf97956a8c7c2ff238fb8c46d180326af71a2d9a9a56c`); `wayfinder-powershell-linux-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`f3a088078d62537fcce0a84e3378e22852f8a61e1fb1d7e11433b853dab8c65f`); `wayfinder-powershell-windows-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`95d5d0b979d35d5fd0f9a1f9c7240d57b80f97aad850882b62268c7f19f7a4bc`); and `wayfinder-matrix-aggregate-v1-candidate-revision-9-82a2bb994e7ef8d2ffda7317e0687b0c7230aa54-34921918384-1` (`a0a8d9dd378fe3fa69ae8dc74c5aca0b7ad15bd36570551cda860daa387274e4`). The retained revision-9 wording is an authentic workflow-level label and does not change the revision-10 report contents or source binding.
- Public run metadata, attempt, logs, job summaries, artifact names, and reported artifact digests were inspected. No artifact was downloaded. The workflow's aggregate job downloaded the entry artifacts on its hosted runner as designed; this maintainer session created no local artifact copy.
- The exact contract, release, fixture index, expected outputs, registered adapter bindings, accepted revision-8 and revision-9 evidence, activation state, and runtime guidance remained unchanged by execution. The initial local Git staging attempt was sandbox-blocked without side effect and then completed through the authorized elevated route. Two guessed nonexistent supplementary filenames produced only an incomplete-discovery read failure. One JavaScript log-filter expression produced an interface error before any request; documentation and current state were refreshed before the corrected read. The GitHub check-run API exposed no summary text, so rendered public job summaries were inspected through the browser fallback. Local PowerShell remained unavailable; pre- and post-action doctors therefore passed 30/31 with that sole known runtime failure.
- The owner explicitly accepted this exact execution record while preserving all artifacts as review-only and authorizing no evidence promotion, certification claim, activation, runtime-guidance change, artifact download, or later tranche. Passing execution and aggregate results are accepted historical facts, but they are not durable accepted certification evidence and do not themselves certify Windows, the matrix, any adapter family, or the full family.

### Candidate revision 10 hosted-execution checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact eight-entry candidate-revision-10 hosted execution | Accepted 2026-09-14 | The owner accepted run `34921918384`, attempt 1, exactly as eight passing 305/305 entries and a passing strict aggregate. Every artifact remains review-only. Acceptance authorizes no artifact download, evidence creation or promotion, release-certification entry, certification claim, runtime guidance, activation, Git mutation, or later tranche. |

## Candidate revision 10 local evidence promotion — accepted

The owner accepted the hosted-artifact verification and promotion-readiness packet and authorized only this bounded local implementation:

- Promoted exactly 27 previously verified, uniquely resolved, non-symbolic regular files from the temporary extraction for GitHub Actions run `34921918384`, attempt `1`, source commit `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54`, into `certification/v1/hosted/run-34921918384-attempt-1/` without replacing any prior evidence. The exact file set and every SHA-256 are pinned by doctor and `maintain.py describe`.
- Re-ran the offline matrix reviewer before promotion. It found all eight execution records and eight report pairs, zero failing environments, zero binding issues, and a passing strict aggregate. Aggregate JSON `be2d4b8542f9a50c1c446a57b05681bb43529cd4906064c2c354dc1d8b3f8d50`, aggregate Markdown `ffe1fe3dc6ae9ed1b21356943ea8f98451221a5e8248043d74cf21c5a0b3cf18`, and matrix `2cc501f45a238d3d6161a89890a33d28fe20aa750558d278d0a69d10bb34a2d0` retain their accepted bindings.
- Corrected `scripts/prepare_evidence_release.py` to accept only candidate revision 10 and the exact source commit, run ID, attempt, 27-file membership and digests, eight execution records, eight JSON/Markdown report pairs, aggregate entries, inventory, and recomputed matrix binding. Missing, extra, nested/ambiguous, symbolic, non-regular, changed-during-read, malformed, or digest-mismatched input fails before output creation.
- Corrected `.github/workflows/publish-evidence.yml` to require the exact accepted run, attempt, source, and matrix before checkout; pass those bindings to the preparation script; and use candidate-revision-10 tag, title, and bounded-evidence notes.
- The durable claim remains exact maintainer-run bounded matrix evidence for the eight named environments at this one source/run/attempt. It is not independent evaluation, generalized Windows certification, adapter-family certification, full-family certification, forward testing, cross-adapter recovery, runtime guidance, or activation.
- The release registry and its empty `certifications` array, all governed bytes, historical evidence, runtime instructions, adapter registry, activation state, Git state, external state, and live-project data remain unchanged. No workflow was dispatched and no release was created.
- On 2026-09-14, the owner explicitly accepted the exact 34-path implementation and authorized only a separate new-session source-publication tranche for those paths on `candidate-revision-9-certification`. This acceptance does not begin source publication or authorize workflow dispatch, protected-environment evidence publication, release creation, release-registry changes, runtime guidance, activation, live-project work, or a later tranche.

### Revision 10 local evidence-promotion checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact 27-file local evidence-promotion implementation | Accepted 2026-09-14; exact 34-path source publication authorized | The owner accepted the complete local implementation and authorized only a separate new-session source-publication tranche for the enumerated paths. Acceptance did not stage, commit, push, dispatch, publish evidence, create a release, alter the release registry, broaden certification, add runtime guidance, activate Wayfinder, or begin later work. |

## Candidate revision 10 evidence-publication readiness — accepted as not ready

Reviewed and accepted by the skill owner on 2026-09-14 as the separately authorized protected-environment evidence-publication readiness result:

- The owner accepted the readiness result as **NOT READY**. No evidence-publication dispatch is authorized.
- The decisive blocker is the workflow/verifier handoff. A dispatch of `.github/workflows/publish-evidence.yml` from `candidate-revision-9-certification` would load the corrected workflow at source-publication commit `72da3542f3a7e65f4bcae09943612d8ba09daf3e`, but `actions/checkout` then checks out the evidence source commit `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54`. The subsequent command would therefore invoke that older source commit's verifier, which targets revision 9 and lacks `--expected-run-id` and `--expected-attempt`. It would fail argument parsing before draft-release creation.
- The `evidence-publication` environment exists. Its sole required reviewer is `somacdivad`; `prevent_self_review` is `false`, so the initiating actor can self-approve; `can_admins_bypass` is `false`; and there is no wait timer or deployment-branch restriction.
- Immutable releases are enabled at repository level. The environment and immutable-release settings do not overcome the decisive workflow/verifier blocker and do not make publication ready or dispatch-eligible.
- The canonical local doctor passed 31/32 checks under CPython 3.14.7. Its sole failure was the known unavailable local PowerShell runtime; no runtime was installed or substituted.
- This acceptance records only the not-ready result and authoritative routing. It does not correct the workflow or verifier, modify GitHub settings, dispatch a workflow, download artifacts, create, modify, publish, or delete a release or tag, change `release.json`, add a release-certification entry, change runtime guidance, activate Wayfinder, perform forward testing or cross-adapter recovery, touch live-project data, or authorize any later tranche.
- A correction to the publication workflow/verifier handoff may be proposed only as a future separately authorized task. This acceptance does not authorize or begin that correction.
- The owner explicitly accepted the exact four-file acceptance-record implementation on 2026-09-14. This closes the record tranche without making a correction or later task eligible.

### Revision 10 evidence-publication readiness checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Protected-environment evidence-publication readiness | Accepted 2026-09-14 as NOT READY; exact four-file record accepted; dispatch unauthorized | The owner accepted the exact environment observations, decisive workflow/verifier blocker, and four-file acceptance-record implementation. Evidence publication is not ready or dispatch-eligible, and no correction or later task begins automatically. |

## Bounded-context and claim-integrity tranche — accepted

Recorded on 2026-09-15 under the owner's explicit acceptance of the exact 17-file implementation and authorization for two separate local commits, implementation first and acceptance record second. This acceptance supersedes the prior pending-acceptance routing; it does not reopen an accepted candidate or authorize another tranche.

- Accepted scope is Priority 0 and both Priority 1 groups from [the bounded-context report](research/2026-09-14-bounded-context-and-tool-output-management.md), plus Opportunity 1 only from [the broader opportunities addendum](research/2026-09-14-broader-wayfinder-opportunities-addendum.md). The research remains historical proposal material; this record captures the bounded implemented outcome, and `current-state.md` remains the sole mutable status authority.
- Implementation commit: `a7081fc0db72d519506ee1dedb5df3adcfc4f931` (`Add bounded-context and claim-integrity tooling`) on `codex/bounded-context-claim-integrity`, with parent `0c07928` (`Add Wayfinder reliability research`) and earlier preparation commit `0343ec0` (`Record revision 10 evidence publication readiness`). Exactly 17 files were committed unchanged from the reviewed worktree: `.claude-plugin/marketplace.json`, `README.md`, `docs/certification.md`, maintainer `SKILL.md`, `references/current-state.md`, `references/workflow.md`, `scripts/maintain.py`, `scripts/test_maintain.py`, `scripts/test_windows_corrections.py`, `scripts/maintainer_checkpoint.py`, `scripts/maintainer_output.py`, `scripts/maintainer_status.py`, `scripts/test_bounded_reliability.py`, the three runtime plugin manifests (`plugins/wayfinder/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/plugin.json`), and repository `scripts/validate_repository.py`. Maintainer-relative paths above are beneath `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/`; runtime compatibility manifests are beneath `plugins/wayfinder/`.
- Bounded command output now distinguishes discovery previews from complete evidence through a versioned envelope, named scope, completeness/truncation markers, counts, byte lengths, hashes, and continuation metadata where applicable. Formats and configurable byte budgets are standardized for the selected interactive commands. Complete output that cannot fit fails clearly rather than silently downgrading; previews remain non-authoritative.
- Exact design-record section reads expose stable UTF-8 chunk ranges, indices/counts, source hashes, and source-bound cursors. A cursor sequence requires complete ordered reconstruction and digest verification; changed sources or mismatched cursor bindings fail closed. Curated `describe/context` routing includes source sizes and next read commands, with allowlisted field projection and stable sorting; it does not replace decisive source reads.
- Checkpoint create/verify tooling produces ephemeral, derived, non-authoritative session state with explicit facts, source provenance, HEAD and worktree fingerprints. File output requires a new explicit path outside the repository. Stale state is rejected rather than refreshed automatically, and checkpoints never become accepted evidence or status authority.
- The canonical JSON status object embedded in `current-state.md` drives bounded public projections in README, certification documentation, runtime metadata, and marketplace descriptions. Status projection is read-only by default; writes require an explicit `--write` request and affect only declared targets. Doctor and repository validation validate facts and reject drift; neither repairs nor broadens claims automatically. The stale README hosted-evidence statement is corrected without changing evidence or certification authority.
- Local verification used CPython 3.14.7 at `/Users/davidamos/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14` and existing Node.js 22.22.3 at `/Users/davidamos/.nvm/versions/node/v22.22.3/bin/node`. Repository validation and `git diff --check` passed. Canonical self-test discovered 57 tests: 56 passed and one genuine unavailable-PowerShell executable-helper test was skipped, with zero repository bytecode. The pre-work canonical full doctor passed 32/33 checks; its sole failure was the missing `pwsh` runtime. Acceptance-record validation must preserve that disclosed baseline in the final full doctor. No runtime was installed or substituted. These checks are local verification, not new accepted certification evidence; local Node.js is not the pinned hosted 24.21.0 target, and no new Windows or full-family verification is claimed.
- Preserved identity: `v1-candidate-revision-10`, contract `frozen`, release `unactivated-frozen`, activation disabled; contract SHA-256 `0d8507c4a8b48fa976c1402b057755da28f896a3feeacf914c35b18a035dc341`; release SHA-256 `581e85c34eb5539d0af0e69128877fe57601600ed59366db13076a366524a083`; 305 frozen conformance cases. Frozen contract assets, registered adapters, historical evidence, and accepted parity evidence remain unchanged.
- Accepted hosted evidence remains run `34921918384`, attempt `1`, source `82a2bb994e7ef8d2ffda7317e0687b0c7230aa54`, with all 27 exact files and pinned hashes unchanged. Evidence publication remains NOT READY and not dispatch-authorized. No release-registry update, full-family certification, or cross-adapter-recovery claim is made. The second local commit is confined to `design-record.md` and `current-state.md` acceptance wording/routing; embedded candidate, evidence, and publication facts and generated public claims remain unchanged.
- Deferred work includes all Priority 2 and later bounded-context recommendations, every addendum opportunity other than Opportunity 1, publication/verifier correction, certification expansion, runtime guidance, and activation. Explicit exclusions remain: push, network mutation, authentication, artifact downloads, workflow dispatch, evidence publication, GitHub-settings changes, release/tag or release-registry changes, candidate advancement, frozen contract/adapter or evidence edits, dependencies, live-project data, and later work. None occurred in this task.

### Bounded-context and claim-integrity acceptance checkpoint

| Checkpoint | Status | Decision |
|---|---|---|
| Exact bounded-context and claim-integrity implementation | Owner-accepted; two local commits; final closure accepted 2026-09-15 | The owner accepted the exact 17-file implementation and authorized only two local commits. This record binds that acceptance to the implemented scope, disclosed verification limits, and preserved identity/evidence. The owner subsequently accepted this exact acceptance record and both local commits, closing the tranche without a push or later-work authority. The terminal closure was delivered; no closure decision remains pending and no next implementation task begins automatically. |

### Final closure and durable routing correction

- On 2026-09-15, in [Find remaining Initialize work](thread://01a0a38b-9418-7f00-9d77-9d783c13d7a0?hostId=local), the owner instructed, "I want it closed, so lets do it". That task verified implementation commit `a7081fc0db72d519506ee1dedb5df3adcfc4f931` and acceptance-record commit `de5e8fc10ee2169f2a5a6ca01061252cc1ae9e53` and delivered terminal closure of the exact record and both commits.
- The closure task reported a clean worktree, the acceptance commit confined to the two authorized record files, passing repository validation and whitespace checks, and doctor passing 32/33 with only the disclosed unavailable local PowerShell runtime. These are the closure task's recorded verification results, not new certification evidence.
- The terminal-handoff-only instruction and two-commit boundary left repository routing saying closure was pending even after that decision. On 2026-09-15, the owner explicitly instructed this task to persist the existing closure decision in `design-record.md` and `current-state.md`. The initial bounded record correction superseded that pending routing and permitted these two local file edits only, without a third commit or another acceptance of the same closure. The owner subsequently instructed, "commit and push the changes", authorizing a separate commit of only these two closure-record files and a non-force push to `origin` on `candidate-revision-9-certification`.
- The tranche is closed. Evidence publication remains NOT READY and dispatch-unauthorized; candidate revision 10, frozen bytes, accepted evidence, release-registry state, runtime guidance, and disabled activation remain unchanged. Only the two-file closure-record commit and non-force branch push are authorized by the subsequent instruction. No workflow dispatch, evidence publication, publication/verifier correction, certification expansion, activation, or later tranche is authorized or begun.
