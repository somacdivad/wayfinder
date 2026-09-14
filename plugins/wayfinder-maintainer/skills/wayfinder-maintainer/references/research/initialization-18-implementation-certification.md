# Initialization research 18: implementation, certification, and activation strategy

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** In what order should the accepted Initialize contract, fixtures, adapters, detectors, and runtime instructions be implemented; what evidence should certify equivalent behavior across environments; and when should the workflow stop being a non-operational stub?
- **Prior decisions:** Initialization policy decisions 1–17 are accepted. Version 1 uses one digest-bound executable contract, dependency-free Python, Node.js, and PowerShell adapters, capability detection, strict manifests and Markdown grammar, byte-stable templates, generated projections, source-assisted intake, digest-bound proposals, no-overwrite publication, immutable recovery journals, two completion gates, and a durable Interview handoff.
- **Decision status:** Option A accepted by the user on 2026-09-13.
- **Implementation progress:** See the [maintainer design record](../design-record.md) for the current candidate revision, accepted slices, pending reviews, and blocked work. This research record owns the accepted strategy, not mutable implementation status.

## Executive conclusion

Prefer **Option A: risk-ordered vertical contract slices, followed by a candidate freeze, independent parity implementations, a full-family certification gate, and isolated forward tests**.

Do not write the complete normative package in isolation and only then discover that it cannot be implemented cleanly. Do not make three adapters evolve in lockstep from the beginning, because that multiplies rework while the contract is still changing and encourages accidental copying. Do not activate a Python-only workflow and promise that the other environments will eventually behave the same.

Instead, build the version-1 candidate in five executable slices. Each slice adds its normative rules, schemas or grammar, fixtures, and one end-to-end Python reference implementation together. The slices progress from pure and low-risk behavior to stateful and destructive behavior: package/probe; discovery/inventory; document rendering and validation; generation and planning; then apply/recovery/receipt. Every slice must pass positive, negative, boundary, property, and golden-output checks before the next begins.

When the Python path can complete and recover a realistic initialization, freeze a release-candidate contract digest. Implement the Node.js and PowerShell adapters from the normative contract and fixtures—not by transliterating Python. Cross-adapter comparison is then useful as disagreement detection. It is not a majority-vote oracle: the normative contract and reviewed expected fixture results remain authoritative, because independently written programs can share failures induced by the same ambiguous specification.

Certification should produce objective, digest-bound evidence for every adapter and named environment. It covers exact bytes, rejection behavior, path containment, generated views, interruption at every journal boundary, recovery from every reachable state, idempotent inspection, and end-to-end greenfield and source-assisted scenarios. Mutation and property tests challenge the suite rather than merely count executed lines. The workflow remains blocked at runtime until the complete initial adapter family has passed the release matrix and isolated forward tests. Activation is one deliberate change that installs focused runtime references, enables the router, and replaces the stub warning; no partially implemented mode is advertised as usable.

This recommendation is an engineering synthesis. Stepwise refinement supports progressively elaborating design and program together; industrial formal-methods experience supports specifying stateful protocols before trusting tests alone; conformance guidance distinguishes specifications from their test suites; test-oracle research warns that determining correct output is itself difficult; property, mutation, differential, and independent-verification work support complementary evidence; confirmation-bias research supports deliberately disconfirming cases; and reproducible-build research supports byte-level comparison. None of these sources establishes five slices, three adapters, or this exact activation threshold as universally optimal. Those details follow from Wayfinder's accepted risk boundaries and portability requirement.

Sources were accessed on 2026-09-13.

## Decision boundary

This decision would settle:

- the implementation order for the entire Initialize workflow;
- how specification, fixtures, and executable feedback evolve together;
- when the version-1 contract becomes frozen for parity work;
- the relationship between the reference adapter and the normative contract;
- how the Node.js and PowerShell implementations avoid becoming blind translations;
- the hierarchy of test oracles;
- the minimum conformance, property, mutation, differential, environment, interruption, and forward-test evidence;
- how certification evidence is recorded and invalidated;
- whether adapters can be released progressively; and
- the exact activation boundary between the current stub and a usable Initialize workflow.

It would not settle:

- every individual schema field or diagnostic code;
- the internal module decomposition of each adapter;
- the Interview workflow;
- distribution outside this repository;
- continuous integration provider configuration;
- future adapters beyond Python, Node.js, and PowerShell; or
- version-2 compatibility and migration.

## Evaluation criteria

| Criterion | Requirement |
| --- | --- |
| Early executable feedback | Ambiguities and impossible rules surface before the whole contract is treated as finished. |
| Singular semantics | The specification remains authoritative; no implementation or test snapshot silently becomes the real contract. |
| Disconfirming evidence | Tests actively try to falsify behavior, including invalid inputs, boundaries, mutations, and interrupted states. |
| Portability evidence | Each advertised adapter is exercised in named runtime, operating-system, and filesystem environments. |
| Equivalent behavior | Certified adapters agree on accepted inputs, normalized plans, emitted bytes, errors, and recovery outcomes. |
| Reviewability | Each development tranche has a coherent purpose, observable outputs, and a bounded review surface. |
| Safe activation | Runtime agents cannot mistake a partially implemented workflow for a usable one. |
| Maintainability | A later contract change invalidates the right certifications and supplies focused regression evidence. |

## Evidence synthesis

### 1. Refine the specification and implementation together, but preserve their distinct authority

Wirth's stepwise-refinement account develops a program through successive decompositions in which design decisions and representations become more concrete.^1 The transferable principle is not a particular programming style; it is that feedback arrives at manageable levels of detail rather than after one monolithic implementation.

Newcombe and colleagues report that AWS engineers used lightweight formal specifications to find subtle distributed-system design errors that ordinary testing and code review did not expose.^2 Wayfinder's transaction is much smaller than an AWS distributed service, but its manifest-last publication, journal state machine, and recovery rules similarly benefit from an explicit state model before file writes are trusted.

**Implication:** implement coherent behavior slices, but require each slice to start with a normative state, invariant, and error contract. Executable feedback may reveal a contract defect; changing the contract then requires an explicit rationale and updated fixtures, not silent accommodation in code.

### 2. Conformance tests measure a specification; they do not replace it

NIST defines conformance testing as determining whether an implementation faithfully meets a standard or specification and notes that test suites and specifications change over time, requiring retesting.^3 This directly supports digest-binding certification to both an adapter and one contract package.

Barr and colleagues survey the test-oracle problem: deciding the correct result for arbitrary executions is itself a fundamental testing difficulty.^4 Golden outputs are valuable only when a maintainer has derived and reviewed them against the semantic contract.

**Implication:** use an explicit oracle hierarchy. A fixture cannot legalize behavior absent from the contract, and an implementation cannot establish expected output by emitting it. Every expected fixture must cite the governing rule or invariant in machine-readable case metadata.

### 3. Positive examples are vulnerable to confirmation bias

Calikli and colleagues' controlled experiment studied time pressure and confirmation bias in functional software testing; the broader testing literature they build on distinguishes confirmatory cases from cases designed to disconfirm a hypothesis.^5 The study population and task do not establish a Wayfinder effect size, but the cognitive risk is relevant when the same maintainer authors a rule, implementation, and tests.

**Implication:** every accepted rule needs at least one neighboring invalid case; every repair needs a minimized regression; and review explicitly asks “what plausible implementation mistake would still pass?” A release gate cannot consist only of successful sample initializations.

### 4. Properties exercise families of behavior beyond hand-authored examples

Claessen and Hughes introduced QuickCheck as a way to state program properties and test them automatically over generated inputs, while also describing pitfalls in generator design.^6 Wayfinder cannot depend on QuickCheck, but its maintainer suite can implement deterministic, seeded generators with each target language's standard library.

**Implication:** supplement examples with properties such as parse/render round trips, normalization idempotence, sorted stable output, containment under generated path variants, no target change after rejected apply, equivalent recovery from every injected boundary, and preservation of authored bytes outside declared generated regions. Persist every discovered counterexample as a fixed regression fixture.

### 5. Mutation tests ask whether the suite notices realistic faults

Jia and Harman's survey describes mutation testing as a large body of fault-based testing research used to assess test-suite strength.^7 Mutation score is not correctness and equivalent mutants complicate interpretation, but deliberately altering inputs, contract resources, plans, journals, and implementation decisions can expose weak tests.

**Implication:** use a bounded, deterministic maintainer mutation set rather than adding a dependency-heavy mutation framework. Mutations include unknown fields, duplicate JSON keys, non-NFC paths, delimiter damage, stale digests, swapped event order, missing pre-events, altered payload bytes, path escapes, invalid status transitions, broken reciprocal links, and wrong manifest publication order. Certification records which required mutants were detected, not a vanity percentage over arbitrary source edits.

### 6. Differential testing finds disagreements, not truth

McKeeman describes differential testing as presenting comparable systems with mechanically generated cases and investigating divergent outputs, crashes, or loops as bug candidates.^8 This fits the three adapters well.

Knight and Leveson's experiment with 27 independently developed program versions found coincident failures substantially more often than an independence assumption predicted.^9 Although their subject was N-version fault tolerance, the warning transfers: multiple implementations based on one ambiguous contract can all be wrong in the same way.

**Implication:** compare normalized result envelopes, payload bytes, diagnostics, journals, receipts, and final trees across adapters. On disagreement, inspect the contract and oracle; never vote. On agreement, retain separate negative and property evidence rather than treating consensus as proof.

### 7. Independence is a spectrum and should focus on risk

NASA describes independent verification and validation as rigorous analysis and testing that produces objective assurance evidence for nominal and off-nominal behavior, with effort tailored to risk.^10 Wayfinder does not warrant NASA-scale organizational independence, and the current development policy does not authorize automatic subagent delegation. Technical separation can still be improved.

**Implication:** parity adapters are written from the contract and fixtures after candidate freeze, without copying reference-adapter control flow. A later independent behavioral forward test should be requested explicitly when the skill is ready, using an isolated temporary repository and a realistic task without disclosing the intended answer. Until that authorization exists, maintainer-run black-box tests provide evidence but are not labeled independent validation.

### 8. Reproducibility makes cross-adapter comparison meaningful

Lamb and Zacchiroli define reproducible builds around bit-for-bit identical output and connect reproducibility with quality assurance and supply-chain integrity.^11 Wayfinder's output is a document record rather than a binary package, but the same observation holds: semantic “equivalence” is hard to audit when encoding, newlines, ordering, or timestamps vary.

**Implication:** separate deterministic content from explicitly injected effective dates and operation identifiers. Given the same contract, proposal, injected values, source snapshot, and initial filesystem fixture, every adapter must produce byte-identical planned payloads, generated artifacts, normalized journals, and receipts except for fields the contract explicitly classifies as environment evidence.

## Proposed implementation sequence

### Stage 0 — Build the maintainer harness and contract skeleton

Create only the infrastructure needed to make subsequent work falsifiable:

- the contract-resource manifest and digest builder;
- a language-neutral fixture case index;
- a runner that invokes adapters as black boxes and compares closed result envelopes;
- normalized fixture-directory snapshotting;
- deterministic injected clock, operation-ID, and failure-boundary controls available only in test mode; and
- a generated certification-report format.

The harness is maintainer-only and may use the available development runtime, but release adapters and runtime detectors remain standard-library only. The harness never becomes runtime authority.

### Slice 1 — Package integrity, `probe`, and discovery

Implement:

- contract resource enumeration and digest verification;
- UTF-8, Unicode, JSON, and duplicate-key primitives;
- closed result envelopes and diagnostic codes;
- adapter self-identification and known-answer `probe`;
- workspace and VCS-boundary discovery;
- strict manifest parsing; and
- symlink, containment, and unsupported-version rejection.

This slice is pure or read-only. It validates the foundation before content generation or writes exist.

### Slice 2 — Source inventory and adoption inputs

Implement:

- user-bounded source traversal;
- exclusions and special-file handling;
- hashes, sizes, UTF-8 classification, heading extraction, and exact duplicate groups;
- canonical inventory and intake-ledger schemas; and
- validation of confirmed dispositions and unchanged source digests.

The adapter does not infer materiality, disposition, or semantic mapping.

### Slice 3 — Record model, rendering, validation, and generation

Implement:

- ID and question-ID grammars and allocation;
- metadata, relationships, questions, sources, and generated-region parsing;
- module and subject containment;
- document-kind and lifecycle validation;
- literal one-pass templates;
- exact document rendering;
- graph validation; and
- deterministic catalog and index generation.

This slice establishes that a semantic proposal can become a fully validated in-memory and staged record without publishing it.

### Slice 4 — Proposal normalization and `initialize-plan`

Implement:

- closed proposal schema and semantic preflight;
- profile/taxonomy representation already confirmed by the agent and user;
- exact payload bundle;
- preview tree and substantive review view;
- preconditions and ordered operation plan;
- canonical JSON and plan digest; and
- cross-linking of source intake, targets, generated artifacts, completion predicates, and handoff pointers.

The command remains noninteractive and never decides interview answers.

### Slice 5 — `initialize-apply`, recovery, and receipt

Implement the explicit state machine for:

- bundle import into the workspace operation directory;
- precondition recheck;
- hash-chained pre/post events;
- exclusive target creation;
- manifest-last publication;
- post-publication generation and validation checks;
- operational and semantic completion evidence;
- receipt creation;
- failure injection at every consequential boundary; and
- conservative inspection, resume, or rollback behavior for every reachable state.

The reference adapter is not feature-complete until every injected state has a specified and tested recovery outcome.

## Contract candidate freeze

After the Python reference adapter passes all five slices and two local end-to-end scenarios, create one release-candidate contract digest.

Freeze means:

- governed resource bytes do not change during parity implementation without invalidating all accumulated results;
- every normative rule has stable identifiers used by fixture metadata and diagnostics;
- all expected outputs have been independently reviewed against those rules;
- open ambiguities are resolved or explicitly excluded from version 1; and
- the Python adapter is an implementation under test, not a source to copy or an oracle.

A defect found while porting may reopen the candidate. The correction increments a candidate revision, regenerates the contract digest, invalidates prior certification results, and reruns all adapters. It does not silently preserve a stale “passing” badge.

## Parity implementation

Implement Node.js and PowerShell after the candidate freeze.

- Each port starts from the normative contract, closed schemas, grammar, templates, and fixtures.
- Shared fixture data and literal templates are reused; executable source is not mechanically translated.
- Adapter-specific modules may differ, but command names, result envelopes, diagnostics, accepted inputs, planned bytes, and recovery semantics may not.
- A port may expose a contract ambiguity. Resolve it in the normative contract and add a minimized fixture before changing all adapters.
- Each adapter runs its own conformance suite before differential comparison.

This is **technical separation**, not full independent validation. The design record must not call it independent merely because the languages differ.

## Oracle hierarchy

When evidence conflicts, resolve it in this order:

1. accepted user decisions and the normative versioned semantic contract;
2. closed registry, schema, and grammar constraints within their declared authority;
3. reviewed fixture expectations linked to the governing rules;
4. semantic invariants and deterministic properties;
5. differential observations among adapters; and
6. current implementation behavior.

Templates are authoritative only for exact new-document shell bytes. Generated snapshots are evidence, not authority. A majority of adapters cannot overrule a contract rule; an obviously mistaken contract rule must be revised through the candidate process.

## Required test portfolio

### Per-rule examples

- at least one smallest accepted instance;
- at least one realistic accepted instance where useful;
- at least one nearest invalid instance;
- boundary values for length, ordering, containment, and cardinality rules; and
- stable diagnostic code and JSON pointer or source location for rejection.

### Golden-byte cases

- every template;
- all profile bootstraps;
- manifest, proposal, plan, intake, event, result, catalog, and receipt JSON;
- representative Markdown blocks and generated regions;
- complete greenfield and source-assisted output trees; and
- normalized recovery results.

### Deterministic properties

- parse/render and encode/decode round trips where the contract promises them;
- normalization and generation idempotence;
- stable ordering independent of traversal order;
- no accepted path escapes its declared root;
- rejected operations do not change managed targets;
- successful apply produces exactly the planned target-set digest;
- recovery reaches only a documented state and preserves unrelated files; and
- different adapters produce identical governed bytes from identical injected inputs.

### Required mutations

- JSON duplicate, unknown, missing, wrongly typed, and unsupported-version fields;
- malformed UTF-8, BOM, newline, normalization, and delimiter cases;
- path traversal, absolute paths, case collisions, symlinks, and special files;
- duplicate IDs, ID gaps where prohibited, stale digests, and ambiguous references;
- invalid lifecycle, supersession, relationship, question, and source states;
- changed source or target after planning;
- altered, missing, reordered, truncated, and forked journal events;
- interrupted writes at every event boundary; and
- premature, altered, or missing manifest and receipt.

### Regression rule

Every defect found by review, a port, environment testing, or forward use adds the smallest fixture that would have exposed it. The fixture cites both the defect and governing contract rule.

## Environment certification matrix

An adapter is certified only for a named matrix entry containing:

- adapter ID and source digest;
- contract version and digest;
- fixture-index and expected-output digests;
- exact runtime implementation and version;
- operating-system family and version;
- filesystem identity and relevant case-sensitivity behavior;
- locale and timezone controls;
- test categories and counts;
- required mutation detections;
- interruption boundaries exercised;
- pass/fail result and result digest; and
- certification time and expiry condition.

At minimum before initial activation:

| Adapter | Required environments |
| --- | --- |
| Python | Current supported Python on macOS, Linux, and Windows |
| Node.js | Current supported Node.js on macOS, Linux, and Windows |
| PowerShell | Current supported PowerShell on Windows plus one Unix-like environment |

“Current supported” is resolved to exact versions in the release candidate and never evaluated dynamically at runtime. The matrix should include both case-sensitive and case-insensitive filesystems. If the available workspace cannot supply an environment, certification remains incomplete until that evidence is run elsewhere; the implementation is not waived or marked passing by inspection.

Runtime `probe` verifies that its adapter and contract digests match a certified pairing embedded in the release contract and that required capabilities pass known-answer tests. It does not rerun the maintainer suite or load certification research.

### Freeze-time runtime targets resolved on 2026-09-13

These targets define future evidence requirements; they do not establish that an environment is available or certified.

- **Python 3.14.7.** Original sources: [Python version status](https://devguide.python.org/versions/) and [Python documentation by version](https://www.python.org/doc/versions/). Accessed 2026-09-13. The first directly establishes that Python 3.14 is a supported bugfix branch; the second directly identifies 3.14.7 as its latest released patch. Wayfinder therefore pins CPython 3.14.7 for the initial macOS, Linux, and Windows matrix. Remaining uncertainty: operating-system packaging and filesystem behavior must be recorded by each actual evidence run.
- **Node.js 24.21.0.** Original sources: [Node.js release status](https://nodejs.org/en/about/previous-releases) and [the latest version-24 distribution index](https://nodejs.org/download/release/latest-v24.x/). Accessed 2026-09-13. The first directly establishes version 24 as LTS and recommends production use of LTS lines; the second directly identifies 24.21.0 as the latest version-24 release. Wayfinder therefore pins Node.js 24.21.0 for the initial macOS, Linux, and Windows matrix. Remaining uncertainty: release availability does not establish successful execution on any Wayfinder target host.
- **PowerShell 7.6.6.** Original sources: [Microsoft's PowerShell lifecycle](https://learn.microsoft.com/en-us/lifecycle/products/powershell) and [the official PowerShell release list](https://github.com/PowerShell/PowerShell/releases). Accessed 2026-09-13. Microsoft directly identifies 7.6 as the current supported LTS line through 2028; the official project release list directly identifies 7.6.6 as its latest patch. Wayfinder therefore pins PowerShell 7.6.6 for Windows and Linux, satisfying the required Windows-plus-one-Unix-like minimum. Remaining uncertainty: supported upstream status does not prove that either environment is present or that Wayfinder behavior is conformant there.

## Forward tests before activation

Run black-box scenarios in newly created temporary repositories:

1. greenfield `software-product` initialization;
2. source-assisted initialization from a synthetic legacy corpus containing exact duplicates, a stale requirement, a semantic contradiction, and an authority collision;
3. user cancellation before apply, proving no managed writes;
4. changed source and target preconditions between plan and apply;
5. interruption at every apply boundary followed by recovery with the same adapter;
6. interruption followed by recovery with a different certified adapter;
7. discovery from nested directories and refusal at VCS boundaries;
8. refusal to reinitialize a valid record; and
9. post-completion handoff discovery using only manifest, catalog, entrypoint, and focused open-question context.

The synthetic source corpus prevents private MyPond facts from becoming test-oracle data and makes expected results distributable. After these pass, run one read-only plan generation against a bounded selection of MyPond documents and inspect the proposed intake and tree without applying it. That dogfood exercise tests realism without modifying the canonical MyPond plan.

The skill-creation guidance recommends an independent forward test for sufficiently complex skills when delegation is available and authorized. Before final activation, ask the user for explicit authorization to have an independent agent evaluate Wayfinder in an isolated temporary workspace. Give that evaluator the skill and realistic request, not the intended output or known suspected faults. This step is valuable but must not be claimed until it actually occurs.

## Activation gate

Keep the current runtime block until all of these are true:

1. all governed contract resources exist and their manifest verifies;
2. all three adapters pass every applicable required test in the environment matrix;
3. all cross-adapter comparisons are equal or have contract-declared environment differences;
4. required mutations are detected;
5. every reachable injected transaction state has a verified recovery result;
6. all black-box forward tests pass;
7. the read-only MyPond dogfood proposal has been reviewed;
8. any authorized independent evaluation findings are resolved or recorded as explicit activation exceptions approved by the user;
9. focused `references/runtime.md` and `references/initialize.md` are accurate against the certified commands; and
10. the user reviews the activation evidence and approves changing Initialize from stub to active.

Activation is one reviewable change:

- replace the global “not ready” warning with mode-specific routing;
- route Initialize to the runtime and initialization references;
- retain blocks for Interview, Update, Validate, and Use;
- expose only certified adapter/runtime pairs to detection;
- preserve maintainer-only research boundaries; and
- record the contract version, certification matrix, and remaining unsupported environments.

No generated adapter or passing local smoke test activates the skill automatically.

## Options

### Option A — Risk-ordered vertical slices, then full-family certification

Build each normative slice with fixtures and the Python reference path; freeze a complete candidate; independently implement Node.js and PowerShell from the contract; run the complete matrix and forward tests; activate once as a family.

**Advantages**

- executable feedback arrives before the contract is fully frozen;
- early work is reviewed in coherent, risk-ordered units;
- parity implementations encounter a stable target;
- all advertised environments share one activation standard; and
- users never encounter a partially portable Initialize workflow.

**Costs and risks**

- activation waits for the slowest adapter and environment;
- late parity findings can reopen the candidate and invalidate results;
- Python may still influence expectations unless oracle review is disciplined; and
- the environment matrix may require infrastructure not present locally.

### Option B — Complete the whole contract package before writing any adapter

Finish all normative prose, schemas, grammar, templates, and expected fixtures first. Implement Python, Node.js, and PowerShell only after a specification freeze.

**Advantages**

- strongest apparent separation between specification and implementation;
- easiest work partitioning after freeze; and
- less risk that Python structure leaks into the normative text.

**Costs and risks**

- delays executable feedback on ambiguous or impractical rules;
- likely causes a large contract rewrite when implementation begins;
- makes fixtures harder to validate without any working path; and
- produces a large, difficult review before observable behavior exists.

### Option C — Implement all three adapters in lockstep for every slice

For each small capability, update the contract, fixtures, Python, Node.js, and PowerShell before moving to the next capability.

**Advantages**

- portability feedback arrives immediately;
- semantic drift is caught within each slice; and
- no adapter accumulates a large parity backlog.

**Costs and risks**

- every early contract correction causes three-way rework;
- implementers are likely to copy one another while behavior is unstable;
- review context expands from one coherent behavior to four artifacts at once; and
- progress can be dominated by environment-specific mechanics before the model is sound.

### Option D — Activate progressively by adapter

Build and activate the Python implementation first, then add Node.js and PowerShell as each becomes certified.

**Advantages**

- earliest usable workflow;
- real usage informs later ports; and
- certification can be genuinely per adapter.

**Costs and risks**

- weakens the accepted initial portability promise;
- encourages Python behavior to become the de facto specification;
- gives users different availability depending on environment; and
- makes later parity defects compatibility problems in an already active contract.

## Recommendation

Choose **Option A**.

It balances early learning with a strong release boundary. Risk-ordered slices prevent a large speculative specification exercise, while a candidate freeze keeps parity work from chasing daily changes. Delaying activation until the full initial family is certified preserves the user's portability constraint and gives the detector an honest set of choices rather than an aspirational list.

The most important control is the oracle hierarchy: contract, reviewed expectations, properties, and then differential evidence. Without that hierarchy, any option can collapse into self-confirming tests generated from the same implementation they are meant to assess.

## What acceptance of Option A would add to the skill-development record

- Initialization policy would remain complete and implementation would begin in five risk-ordered slices.
- Each slice would deliver normative rules, machine resources, fixtures, and executable Python behavior together.
- A complete reference path would trigger a release-candidate contract freeze, not runtime activation.
- Node.js and PowerShell would be implemented from the frozen contract and fixtures.
- Certification would be digest-bound, environment-specific, falsification-oriented, and invalidated by governed changes.
- Initialize would activate only after the full adapter family, failure paths, forward tests, runtime references, and user activation review pass.
- Other Wayfinder workflows would remain blocked while Initialize alone becomes operational.

## Next step if Option A is accepted

Begin Stage 0 and Slice 1 as one bounded implementation tranche. Before writing code, present the exact files, normative rule IDs, commands, fixture classes, result envelopes, and observable acceptance criteria for that tranche. Then implement and demonstrate it without creating any project record or enabling runtime Initialize.

## Sources

1. Wirth, Niklaus. “Program Development by Stepwise Refinement.” *Communications of the ACM* 14, no. 4 (1971): 221–227. <https://doi.org/10.1145/362575.362577>
2. Newcombe, Chris, Tim Rath, Fan Zhang, Bogdan Munteanu, Marc Brooker, and Michael Deardeuff. “How Amazon Web Services Uses Formal Methods.” *Communications of the ACM* 58, no. 4 (2015): 66–73. <https://doi.org/10.1145/2699417>
3. National Institute of Standards and Technology. “Conformance Testing.” <https://www.nist.gov/itl/ai/applied-ai-research-group/conformance-testing>
4. Barr, Earl T., Mark Harman, Phil McMinn, Muzammil Shahbaz, and Shin Yoo. “The Oracle Problem in Software Testing: A Survey.” *IEEE Transactions on Software Engineering* 41, no. 5 (2015): 507–525. <https://doi.org/10.1109/TSE.2014.2372785>
5. Calikli, Gul, Andrea Bener, and Berna Arslan. “A controlled experiment on time pressure and confirmation bias in functional software testing.” *Empirical Software Engineering* 24 (2019): 1727–1761. <https://doi.org/10.1007/s10664-018-9668-8>
6. Claessen, Koen, and John Hughes. “QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs.” *Proceedings of ICFP 2000*, 268–279. <https://doi.org/10.1145/351240.351266>
7. Jia, Yue, and Mark Harman. “An Analysis and Survey of the Development of Mutation Testing.” *IEEE Transactions on Software Engineering* 37, no. 5 (2011): 649–678. <https://doi.org/10.1109/TSE.2010.62>
8. McKeeman, William M. “Differential Testing for Software.” *Digital Technical Journal* 10, no. 1 (1998): 100–107. <https://vmssoftware.com/docs/dtj-v10-01-1998.pdf>
9. Knight, John C., and Nancy G. Leveson. “An Experimental Evaluation of the Assumption of Independence in Multiversion Programming.” *IEEE Transactions on Software Engineering* SE-12, no. 1 (1986): 96–109. <https://doi.org/10.1109/TSE.1986.6312924>
10. NASA. “IV&V Overview” and “Software Engineering Procedural Requirements, Standards, and Related Resources.” <https://www.nasa.gov/ivv-overview/> and <https://www.nasa.gov/intelligent-systems-division/software-management-office/nasa-software-engineering-procedural-requirements-standards-and-related-resources/>
11. Lamb, Chris, and Stefano Zacchiroli. “Reproducible Builds: Increasing the Integrity of Software Supply Chains.” *IEEE Software* 39, no. 2 (2022): 62–70. <https://doi.org/10.1109/MS.2021.3073045>

All implications and implementation thresholds above are Wayfinder design inferences unless a paragraph expressly describes a study result or standard requirement.
