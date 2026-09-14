# Initialization research 17: existing-material adoption and completion boundary

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** When a repository already contains unmanifested plans, notes, requirements, research, or decision material, how should initialization use that material without silently changing it or creating competing sources of truth, and what exact conditions make initialization complete enough to hand off to Interview?
- **Prior decisions:** Initialization uses a confirmed taxonomy, a minimum viable semantic bootstrap, one digest-bound no-overwrite publication, a strict manifest published last, visible uncertainty, purpose-based document kinds, stable IDs, bounded trace links, a generated catalog, and certified dependency-free adapters executing one versioned contract.
- **Decision status:** Option A accepted by the user on 2026-09-13.

## Executive conclusion

Prefer **Option A: a fresh managed namespace with source-assisted intake and no in-place legacy conversion in version 1**.

Wayfinder should distinguish three acts that are often collapsed into “adoption”:

1. inspecting an existing document as potential evidence;
2. synthesizing selected knowledge into a new governed record; and
3. declaring which record is authoritative after publication.

Initialization can safely perform the first two under the already accepted no-overwrite transaction. It should perform the third only through an explicit, reviewed authority-cutover statement. It should not rewrite, move, delete, wrap, or automatically classify existing documents in version 1. Those operations require a future migration mode with before-and-after semantics stronger than the initializer currently promises.

For a repository with useful existing material, the user supplies a bounded set of source roots or files. A deterministic tool inventories those sources without following symbolic links; the agent progressively reads the inventory and relevant content; and the user reviews one disposition for every material candidate: `incorporate`, `reference`, `preserve-out-of-scope`, or `unresolved`. Incorporation creates new Wayfinder content while preserving source bytes and recording source paths, hashes, and target mappings in an intake ledger. Reference sources remain non-authoritative evidence. Material unresolved candidates block cutover; ordinary knowledge gaps can remain explicit open questions.

Initialization is complete only when both an operational gate and a semantic gate pass. Operationally, every confirmed byte, hash, target, journal event, generated artifact, validation result, manifest, intake ledger, and receipt must agree. Semantically, the minimum bootstrap must be honest and attributable, all material intake candidates must have reviewed dispositions, no unresolved source-of-truth conflict may remain, and the user must confirm the authority cutover. “Initialized” means trustworthy, discoverable, and resumable—not complete, correct in every respect, or ready for implementation.

The handoff should expose the entrypoint, structure, source dispositions, consequential open questions, validation result, and recommended first Interview focus. Those resumption cues belong in the record itself as well as in the operation receipt so a later agent can resume without the initialization transcript or maintainer research.

This recommendation is an engineering synthesis. Archival and records-management sources support preserving provenance, original context, and transformation history; schema-matching research warns that semantic mapping remains partly judgmental; requirements research supports managing rather than prematurely erasing inconsistency and keeping obsolete requirements out of the active view; sensemaking research supports external representations for a bounded corpus; and structured-handoff research supports explicit summaries, action lists, contingencies, and receiver synthesis. None of the reviewed studies evaluates this exact LLM-operated, repository-local planning skill. In particular, clinical handoff results justify the shape of a handoff, not an expected numerical improvement in software planning.

Sources were accessed on 2026-09-13.

## Decision boundary

This decision would settle:

- how initialization behaves when `.wayfinder/manifest.json` is absent but potentially relevant documents exist;
- the clean boundary required for files Wayfinder will manage;
- how the user bounds source discovery;
- which facts about source files are inventoried mechanically;
- how candidate sources are classified and reviewed;
- how source provenance and transformations are preserved;
- how duplicates, contradictions, and competing authority claims affect publication;
- the exact distinction between operational completion and semantic readiness;
- the durable initialization receipt; and
- the resumption contract between Initialize and Interview.

It would not settle:

- in-place migration, renaming, or reformatting of existing documents;
- continuous synchronization with a legacy plan;
- the detailed question-selection and interviewing method;
- the Update workflow for later taxonomy or authority changes;
- semantic validation of an entire mature record;
- retention or deletion policy for legacy sources after cutover; or
- import from remote knowledge systems.

## Evaluation criteria

| Criterion | Requirement |
| --- | --- |
| No silent data loss | Existing user content is never overwritten, moved, deleted, or semantically reclassified without a separately reviewed operation. |
| One authority | Publication does not leave two documents claiming to be the current source for the same governed concern. |
| Provenance | A reviewer can identify what source version informed each incorporation and what new artifact it produced. |
| Bounded review | The user can understand the intake set and dispositions without approving an opaque repository-wide scrape. |
| Honest uncertainty | Gaps may become open questions; material authority conflicts do not disappear into generic uncertainty. |
| Deterministic mechanics | Inventory, hashes, exact duplicate detection, containment, publication, and completion checks are scripted. |
| Human semantic control | The agent proposes mappings and syntheses, but the user confirms meaning, authority, and cutover. |
| Resumability | A new session can find the record, its remaining questions, and the recommended next planning focus without replaying initialization. |
| Progressive disclosure | Interview and Use consume the manifest, catalog, entrypoint, and focused documents—not intake history or maintainer research by default. |

## Evidence synthesis

### 1. Adoption should preserve provenance and context, not merely copy propositions

ISO 15489-1 treats records, their metadata, controls, and the processes for creating, capturing, and managing them as part of one records-management system.^1 NARA's account of provenance says records remain attributable to their creator and intelligible in the context and order in which they accumulated.^2 The Library of Congress METS model records the original source plus master/derivative relationships and migration or transformation information.^3 Digital-authenticity research likewise emphasizes that reformatting changes the object whose authenticity must be evaluated.^4

Wayfinder is not an archive, but the transferable concern is strong: copying a paragraph into a new hierarchy without recording its source version erases evidence needed to evaluate context and meaning.

**Implication:** preserve source bytes, identity by path plus SHA-256, source-use context, and explicit source-to-target mappings. Do not claim the synthesized target is a byte-preserving migration or let a target silently inherit the source's authority.

### 2. Schema matching can assist classification but cannot authorize semantic equivalence

Rahm and Bernstein's survey describes schema matching as historically manual and reviews techniques for partial automation across schema-, instance-, element-, structure-, language-, and constraint-level evidence.^5 The core distinction matters here: filename similarity or heading structure can suggest a home, but it cannot prove that `vision.md` is a current product brief, that two requirements are equivalent, or that a historical decision remains accepted.

**Implication:** tools may enumerate files, extract structural cues, compute hashes, and validate a user-confirmed mapping. The agent may propose a disposition and target. Neither may silently turn similarity into a semantic or authority decision.

### 3. A content inventory helps bound sensemaking, but inventory is not interpretation

Russell, Stefik, Pirolli, and Card model sensemaking as searching for a representation and encoding information into it to answer task-specific questions; different representations create different cognitive and external costs.^6 A bounded inventory gives the agent and user a stable external representation before they negotiate taxonomy and authority.

Content-audit scholarship describes audit as identifying, describing, quantifying, and assessing content, while also noting that the method's research literature remains limited.^7 This supports using an inventory as a decision aid, not treating it as a validated theory of knowledge completeness.

**Implication:** require user-selected source scope and a machine-generated inventory before semantic intake. Summarize counts and exceptional items, group exact duplicates, and review material candidates. Do not infer “complete inventory” from crawling the whole repository or convert inventory metadata into content claims.

### 4. Inconsistency is information; premature reconciliation can destroy it

Nuseibeh, Easterbrook, and Russo argue that multiple evolving software descriptions naturally become inconsistent and that development processes can exploit inconsistency rather than requiring immediate global consistency.^8 Wayfinder similarly needs to distinguish a productive unresolved question from a dangerous authority collision.

**Implication:** do not auto-merge contradictory sources or force every disputed claim into one answer. Preserve their provenance and either obtain a user resolution or record an honest open question. However, an unresolved conflict over which artifact is authoritative blocks cutover because the initialized record would otherwise violate its own source-of-truth promise.

### 5. Obsolete material should not remain in the default active path

Gren and Berntsson Svensson report a family of six experiments with students and practitioners (`N = 461`) in which obsolete requirements affected effort estimates even when participants were told to exclude them.^9 This is evidence about estimation tasks, not all planning cognition, but it demonstrates that labels alone do not reliably neutralize visible stale requirements.

**Implication:** legacy and superseded material may remain accessible for provenance, but the root map, catalog defaults, and Use workflow should not intermingle it with active guidance. A “legacy” label beside an otherwise current-looking requirement is not an adequate authority boundary.

### 6. Exact duplicates are mechanical; semantic duplication is not

Cryptographic hashes can establish that two inventoried byte streams are identical. They cannot establish that differently worded claims have the same meaning or lifecycle. Conversely, two byte-identical copies can occupy different provenance contexts.

**Implication:** group exact SHA-256 duplicates for review, but keep every source path in the ledger. Treat near-duplicate and semantic-conflict detection as agent assistance whose output requires confirmation. Never delete duplicates during initialization.

### 7. Completion should be an evidence-backed gate, not a hidden score

The accepted minimum viable bootstrap already rejects fixed question counts and completeness scores. This decision adds a second reason: operational integrity and semantic readiness have different evidence and failure modes. A perfectly hashed empty shell is not semantically ready; a thoughtful draft with a missing or mismatched manifest is not safely discoverable.

**Implication:** report a conjunction of named, inspectable predicates. A failed predicate has a stable diagnostic and recovery route. Do not average predicates into a score, let optional richness compensate for a broken invariant, or claim the whole plan is complete.

### 8. Handoffs work best when state, action, contingency, and confirmation are explicit

The I-PASS multicenter prospective intervention combined a standardized handoff structure with training, observation, and a sustainability campaign; across 10,740 pediatric admissions, implementation was associated with lower medical-error and preventable-adverse-event rates and better inclusion of prescribed handoff elements.^10 The clinical setting and bundled intervention prevent direct causal or numerical transfer to project planning.

The useful structural analogy is narrower: a receiver benefits from a concise current-state summary, explicit next actions, identified contingencies, and an opportunity to synthesize the handoff.

**Implication:** initialization ends with a stable, structured resumption view and invites the next agent to restate the chosen Interview focus. The receipt alone is not enough; the durable record must also contain human-readable next-step pointers.

## Proposed entry classification

The initializer evaluates states in this order:

1. If a candidate workspace contains an incomplete, valid Wayfinder operation journal, stop and route to `initialize-recover` before doing anything else.
2. If a valid `.wayfinder/manifest.json` exists at the selected workspace root, stop and route to Update. Initialize never “re-initializes” an existing record.
3. If a manifest exists but is invalid or unsupported, stop with diagnostics. Do not treat the record as absent.
4. Otherwise offer either `fresh` initialization or `source-assisted` initialization.

`fresh` means the user has declared no existing files as sources. It does **not** mean the repository itself is empty. `source-assisted` means the user has declared bounded local source roots or files for intake.

The mode is recorded in the proposal and receipt, not the manifest. Both modes publish the same record contract.

## Proposed managed-namespace rule

The proposed record may coexist with code, assets, and unrelated documents. The clean boundary is the namespace Wayfinder will create, not the entire repository.

Before proposal and again before application:

- `.wayfinder/manifest.json` must be absent;
- every proposed module root and the record entrypoint must be absent;
- every other proposed target path must be absent;
- `.wayfinder/operations/` may exist only for complete historical operations or the operation being recovered;
- every proposed target must resolve beneath the selected workspace and record roots without following symbolic links; and
- collisions are reported exactly; they are never treated as implicit adoption targets.

`recordRoot` may be `.` when the proposed entrypoint and module roots remain clean. Requiring a wholly empty `docs/` directory would make brownfield use needlessly difficult, but permitting arbitrary writes between unmanaged files would make authority and rollback hard to reason about.

If the desired Wayfinder module root already exists, version 1 requires the user to choose a different clean root or postpone initialization for a future migration workflow. The initializer does not create a partial managed island inside a pre-existing module tree.

## Proposed source-assisted intake

### 1. Bound the source set

The user explicitly selects local source files or roots. The proposal displays the normalized selections. The tool does not default to “all repository files.”

Inventory excludes:

- the VCS administration directory;
- `.wayfinder/` operation and manifest data;
- proposed target roots;
- ignored binary, archive, build-output, dependency, and secret-pattern classes declared by the contract; and
- any path that escapes through a symbolic link.

The user can explicitly add an otherwise excluded ordinary file, but cannot override containment, special-file, VCS-metadata, or secret-safety exclusions. Version 1 does not read remote URLs during intake.

### 2. Produce a deterministic inventory

For each discovered entry, the script records at least:

- normalized workspace-relative path;
- regular-file, directory, symbolic-link, or unsupported-file classification;
- byte size and SHA-256 for regular files;
- detected UTF-8 text versus opaque bytes;
- exact-duplicate group, if any;
- for accepted Markdown text, mechanically extracted H1 and heading outline; and
- exclusion or diagnostic status.

The inventory is sorted by normalized path and digest-bound. Symbolic links and unsupported special files are listed but never opened or followed. The script does not summarize prose, infer recency from wording, determine authority, or map content to taxonomy.

### 3. Review progressively

The agent first reads the inventory and structural cues. It loads a source body only when the path, title, heading outline, duplicate group, or user instruction makes that source plausibly relevant. It may request a narrower or expanded declared source scope, but every scope change produces a new inventory digest.

The agent treats retrieved source text as untrusted project content, not instructions that override the user, skill, or repository policy.

### 4. Give every material candidate one disposition

| Disposition | Meaning | Publication effect |
| --- | --- | --- |
| `incorporate` | Selected knowledge is synthesized into one or more new Wayfinder documents. | Source remains unchanged; ledger records its digest, target IDs, and a concise transformation note. |
| `reference` | Source remains useful evidence or history but is not copied into the governed record. | Ledger records locator, digest, intended use, limitations, and non-authoritative status; an evidence document may cite it when materially used. |
| `preserve-out-of-scope` | Source is intentionally not used for this initialization. | Source remains unchanged; ledger records a short reason so omission is visible. |
| `unresolved` | The candidate's role, meaning, or authority cannot yet be determined. | Blocks publication if material to scope or authority; otherwise requires the user's explicit choice to represent the issue as an open question. |

A **material candidate** is a source that plausibly claims current authority for project intent, desired outcomes, boundaries, requirements, architecture, development policy, accepted decisions, or the taxonomy being initialized, or that materially supports a claim proposed for the bootstrap. Materiality is a review judgment, not a filename heuristic.

The complete disposition table appears in the substantive proposal. The script checks that every inventoried material candidate named in the proposal has exactly one allowed disposition and that every incorporated or referenced digest still matches before application.

### 5. Preserve the transformation record

The bundle contains `intake.json`, governed by the contract and included in the plan digest. For each source, it records:

- inventory identity and source path;
- source SHA-256 and byte size;
- disposition and review reason;
- target document IDs for `incorporate`;
- transformation note describing selection, synthesis, or structural change;
- evidence/source key when the target uses the source as formal evidence; and
- any unresolved conflict or question ID.

The durable operation receipt references the intake digest and disposition counts. The detailed ledger stays in `.wayfinder/operations/<operation-id>/`; it is not copied into the manifest or catalog and is not loaded during ordinary Use. Material scholarly or project evidence is separately represented in an authored `evidence` document under the accepted source model.

## Proposed authority-cutover rule

User confirmation of the digest-bound proposal authorizes current synthesis; statements inside imported files do not.

The root knowledge map contains a concise **Authority boundary** section that:

- identifies the manifest-governed Wayfinder record as the repository's current project record after successful publication;
- links to any active repository instructions that remain co-authoritative for a different concern;
- states that sources listed in the intake receipt are legacy, evidentiary, or out of scope rather than active Wayfinder authority unless an explicit active link says otherwise; and
- links to the initialization receipt and consequential unresolved questions without making the receipt a semantic authority.

If an existing repository document or instruction explicitly claims to be the canonical source for the same concern, initialization blocks until the user resolves the boundary. Valid resolutions include changing the proposed scope, updating that external authority under a separately authorized change, or postponing initialization. The initializer may not silently choose one claimant, edit repository instructions, or publish two “canonical” entrypoints.

## Proposed inconsistency policy

Before publication, the agent reviews incorporated and referenced sources for material contradictions with the proposed bootstrap.

- Exact byte duplicates are grouped mechanically; no file is deleted.
- Semantically similar documents remain separate candidates until the user confirms their relationship.
- A conflict about intent, scope, authority, accepted decisions, or the meaning of a synthesized claim must be resolved or represented honestly in the governed record.
- A substantive unknown may become a stable open question with its competing evidence and next step.
- A source-of-truth conflict cannot be downgraded to an ordinary open question while two active claimants remain.
- A source that is stale, rejected, or superseded remains available through provenance but is omitted from active default navigation.
- The agent reports its material inferences and does not manufacture a “combined” position merely to eliminate disagreement.

Deterministic validation can check that all declared dispositions, target IDs, question IDs, links, and hashes exist. Semantic validation determines whether the synthesis and conflict treatment are warranted.

## Proposed completion contract

### Operational gate

All of the following must be true:

1. the applied plan digest equals the user-confirmed digest;
2. the adapter and contract digests match the bundle;
3. every declared target contains the planned SHA-256 bytes;
4. every precondition and no-overwrite check succeeded;
5. all required generated artifacts were regenerated and match their declared hashes;
6. deterministic validation succeeds with no error-level diagnostics;
7. the manifest was published last and parses as the exact supported schema;
8. the immutable journal has a valid hash chain ending in `complete`; and
9. the receipt validates and agrees with the manifest, plan, journal, generated artifacts, and intake ledger.

If the manifest exists but any final predicate fails, the operation is `recovery-required`, not complete. The agent routes to `initialize-recover` and does not start Interview.

### Semantic gate

All of the following must also be true:

1. the previously accepted minimum viable bootstrap readiness criteria pass;
2. every material candidate in the declared intake scope has a reviewed disposition;
3. incorporated claims are attributable to user input, identified sources, or explicitly labeled agent synthesis;
4. material contradictions are resolved or represented by appropriate, visible uncertainty;
5. no competing current authority remains within the declared project-record scope;
6. the authority boundary and next planning step are visible in the knowledge map; and
7. the user confirms the complete proposal and authority cutover.

No automatic score substitutes for these predicates. Warnings may remain when they are visible, non-authority-threatening, and paired with an open question, limitation, or next step accepted by the user.

### Meaning of `complete`

Completion means the record is:

- **discoverable:** a conforming agent can find and open it;
- **integral:** published bytes and derived views match the confirmed operation;
- **authoritative:** its scope and relationship to older material are explicit;
- **honest:** consequential gaps and disagreements are visible; and
- **resumable:** the next workflow has a durable starting point.

It does not mean that stakeholder discovery is finished, every question is answered, every source is correct, requirements are approved, architecture is decided, or implementation should begin.

## Proposed receipt

Write `.wayfinder/operations/<operation-id>/receipt.json` only after successful final validation, then append the terminal journal event. The receipt is an operational audit record, not product authority. It contains:

```json
{
  "format": "wayfinder-initialization-receipt",
  "schemaVersion": 1,
  "operationId": "<stable operation id>",
  "completedAt": "<effective publication timestamp>",
  "mode": "fresh | source-assisted",
  "planDigest": "<sha256>",
  "contractVersion": 1,
  "contractDigest": "<sha256>",
  "adapter": {
    "id": "<certified adapter id>",
    "digest": "<sha256>"
  },
  "canonicalBaseline": "<resolved baseline>",
  "manifestDigest": "<sha256>",
  "targetSetDigest": "<sha256>",
  "intake": {
    "ledgerDigest": "<sha256 or null>",
    "incorporate": 0,
    "reference": 0,
    "preserveOutOfScope": 0,
    "unresolved": 0
  },
  "validation": {
    "validatorVersion": 1,
    "errors": 0,
    "warnings": 0,
    "resultDigest": "<sha256>"
  },
  "entrypoint": "<record-relative path>",
  "openQuestionIds": ["<wfq id>"],
  "nextWorkflow": "interview",
  "recommendedFocusIds": ["<document or question id>"]
}
```

Exact timestamps and operation-ID generation belong to the executable contract. Disposition counts include only the accepted inventory. An unresolved count can be nonzero only for items explicitly converted into governed open questions and not involving competing authority.

## Proposed handoff into Interview

After completion, show the user one concise handoff containing:

- the human entrypoint;
- enabled modules and subjects;
- validation status and receipt path;
- source-intake disposition counts and any notable exclusions;
- consequential open-question IDs and summaries;
- the recommended first Interview focus with a short rationale; and
- the fact that Interview will not start automatically.

The durable knowledge map includes a **Next planning step** section linking to the same question or focused document. The question register supplies the importance and next-step details. The generated catalog makes those IDs and summaries retrievable. The receipt duplicates only the routing pointers needed to audit and resume the operation.

A later Interview session:

1. discovers the nearest valid manifest;
2. validates the entrypoint and catalog freshness;
3. reads the knowledge map and selected question/catalog entries;
4. loads only documents relevant to the confirmed interview focus; and
5. asks the user to confirm or redirect that focus before substantive elicitation.

It does not load `intake.json`, the full initialization bundle, or maintainer research unless the task specifically concerns provenance or Wayfinder maintenance.

## Options

### Option A — Fresh managed namespace with source-assisted intake

Initialize only into absent Wayfinder roots and targets. Existing material may be inventoried, synthesized, referenced, or left out of scope, but it is never changed. Require reviewed dispositions, provenance, a single authority cutover, named completion gates, a receipt, and a durable Interview handoff.

**Advantages**

- preserves the accepted no-overwrite and recoverability model;
- works in brownfield repositories without pretending legacy conversion is mechanical;
- separates evidence use from authority transfer;
- keeps normal Use lean while retaining an audit trail;
- makes failure and recovery states explicit; and
- creates a clear boundary for a later governed migration extension.

**Costs and risks**

- may temporarily duplicate selected knowledge in old and new files;
- requires a disposition review for material candidates;
- may require a different target root when existing desired roots are occupied; and
- does not solve cleanup or migration of a large legacy corpus.

### Option B — Two-lane initialization with governed in-place migration

Support Option A plus an initializer lane that can reformat, rename, move, supersede, or replace existing documents under one expanded transaction with exact before-and-after payloads and rollback data.

**Advantages**

- can produce the desired final layout without parallel legacy files;
- reduces a later cleanup step; and
- may suit carefully curated small document sets.

**Costs and risks**

- supersedes the accepted “targets absent, never overwrite” initialization invariant;
- expands rollback, link rewriting, history, authority, and user-review complexity sharply;
- makes a first release responsible for both bootstrap and migration semantics; and
- increases the risk that structurally valid conversion silently changes meaning.

Choose this only if in-place migration is a version-1 requirement worth reopening the prior publication decision.

### Option C — Lenient wrapper around existing documents

Generate a manifest and catalog over existing files, allow legacy metadata and structural exceptions, and gradually normalize them during Update.

**Advantages**

- fastest apparent adoption;
- minimal initial duplication; and
- preserves legacy paths.

**Costs and risks**

- gives “initialized” two meanings and forces every consumer to handle exceptions;
- weakens ID, kind, lifecycle, graph, and generation invariants;
- can confer authority merely because a file was present; and
- creates a prolonged shadow schema that may never be retired.

This is not recommended.

### Option D — Pristine-only scaffold

Require an empty record area and forbid source intake during initialization. Existing material can be considered only later through Interview or Update.

**Advantages**

- smallest initializer and easiest mechanical completion proof;
- no source-disposition schema; and
- cleanest generated layout.

**Costs and risks**

- discards valuable context at the moment the bootstrap is authored;
- encourages users or agents to copy facts without provenance;
- delays discovery of authority conflicts until after publication; and
- makes brownfield initialization unnecessarily artificial.

## Recommendation

Choose **Option A**.

It composes with every accepted initialization decision: the target namespace remains no-overwrite, the agent still performs semantic elicitation and synthesis, the user still confirms one exact proposal, and scripts still own deterministic inventory, hashing, publication, validation, and recovery. Most importantly, it refuses to equate a successful format conversion with a justified transfer of meaning or authority.

Version 1 should establish the clean extension seam for migration by making intake, source-target mappings, and authority cutover explicit. A later Update or dedicated migration workflow can reuse that evidence while adding exact before-images, link rewrites, supersession changes, and rollback policy. That is a safer evolution than embedding two materially different transaction models in the initializer.

## What acceptance of Option A would add to the skill

The runtime foundation would state that:

- initialization uses clean managed roots but may coexist with unrelated repository content;
- an existing manifest routes to Update and an incomplete operation routes to recovery;
- source-assisted intake begins from user-declared local scope and a deterministic inventory;
- all material candidates receive reviewed dispositions;
- incorporated sources remain unchanged and are traceable through a digest-bound intake ledger;
- semantic conflicts are never resolved automatically and competing authority blocks publication;
- completion is the conjunction of operational integrity and semantic readiness;
- a receipt and record-local next-step pointers support later resumption; and
- initialization hands off to, but does not automatically start, Interview.

## Deferred implementation questions

These are implementation details to resolve against the accepted contract, not reasons to widen this decision:

- the closed source-file extension and binary exclusion tables;
- maximum default inventory size and deterministic overflow diagnostics;
- the exact operation-ID and timestamp representation;
- which structural cues are extracted from non-Markdown text;
- receipt retention and pruning in the future Update workflow;
- a future migration proposal schema and rollback model; and
- whether authenticated published snapshots can later serve as intake sources.

## Next step if Option A is accepted

Mark initialization policy design complete, then implement it in reviewable tranches:

1. normative version-1 contract, registries, schemas, templates, and conformance fixtures;
2. Python reference adapter covering detection, inventory, planning, validation, generation, and publication;
3. equivalent Node.js and PowerShell adapters plus capability detectors;
4. cross-adapter, negative, golden-output, collision, interruption, and recovery verification; and
5. one forward test in a temporary fixture repository, followed by activation of the Initialize workflow.

Only after the Initialize implementation is certified should Wayfinder begin the detailed Interview workflow design.

## Sources

1. International Organization for Standardization. “ISO 15489-1:2016, Information and documentation—Records management—Part 1: Concepts and principles.” Current edition confirmed in 2021. <https://www.iso.org/standard/62542.html>
2. U.S. National Archives and Records Administration. “Record Group Concept” and Theodore R. Schellenberg, “Principles of Arrangement.” <https://www.archives.gov/research/guide-fed-records/index-numeric/concept.html> and <https://www.archives.gov/research/alic/reference/archives-resources/principles-of-arrangement.html>
3. Library of Congress. “METS: An Overview & Tutorial.” <https://www.loc.gov/standards/mets/METSOverview.v2.html>
4. Adam, Sharon. “Preserving authenticity in the digital age.” *Library Hi Tech* 28, no. 4 (2010): 595–604. <https://doi.org/10.1108/07378831011096259>
5. Rahm, Erhard, and Philip A. Bernstein. “A survey of approaches to automatic schema matching.” *The VLDB Journal* 10 (2001): 334–350. <https://doi.org/10.1007/s007780100057>
6. Russell, Daniel M., Mark J. Stefik, Peter Pirolli, and Stuart K. Card. “The cost structure of sensemaking.” *INTERCHI '93*, 269–276. <https://doi.org/10.1145/169059.169209>
7. Sperano, Isabelle. “Content audit: What does the method consist of?” *Proceedings of the 35th ACM International Conference on the Design of Communication* (2017). <https://doi.org/10.1145/3121113.3121227>
8. Nuseibeh, Bashar, Steve Easterbrook, and Alessandra Russo. “Leveraging inconsistency in software development.” *Computer* 33, no. 4 (2000): 24–29. <https://doi.org/10.1109/2.839317>
9. Gren, Lucas, and Richard Berntsson Svensson. “Is it possible to disregard obsolete requirements? A family of experiments in software effort estimation.” *Requirements Engineering* 26 (2021): 459–480. <https://doi.org/10.1007/s00766-021-00351-7>
10. Starmer, Amy J., et al. “Changes in Medical Errors after Implementation of a Handoff Program.” *New England Journal of Medicine* 371 (2014): 1803–1812. <https://doi.org/10.1056/NEJMsa1405556>

All implications above are Wayfinder design inferences unless a paragraph expressly describes a study result or standard requirement.
