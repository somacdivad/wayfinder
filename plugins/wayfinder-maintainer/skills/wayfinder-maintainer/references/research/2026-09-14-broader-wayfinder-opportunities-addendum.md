# Broader reliability, security, evolution, and adoption opportunities for Wayfinder

- **Status:** Research complete; opportunities proposed, not authorized or implemented
- **Last updated:** 2026-09-14
- **Audience:** Wayfinder owner and maintainers
- **Parent research:** [Bounded context and tool-output management for Wayfinder maintenance](2026-09-14-bounded-context-and-tool-output-management.md)
- **Research question:** Beyond context truncation and tool-output management, which evidence-backed changes would most improve Wayfinder or Wayfinder Maintainer?
- **Scope:** Opportunity discovery across governance, documentation integrity, agent security, conformance strength, recovery, supply-chain provenance, schema evolution, compatibility, usability, scale, privacy, and operational sustainability.
- **Out of scope:** Implementing any recommendation; changing frozen contract or adapter bytes; changing accepted evidence; publishing source or evidence; dispatching workflows; creating releases; changing runtime guidance; activation; live-project work; dependencies; authentication; commits; or pushes.

## Relationship to the parent report

The [parent report](2026-09-14-bounded-context-and-tool-output-management.md) addresses one specific reliability problem: excessive or incomplete context and tool output. This addendum deliberately avoids restating its pagination, completeness-envelope, bounded-read, or session-checkpoint recommendations. The opportunities below are independently useful even if truncation never occurs.

Several recommendations interact with the parent design. For example, security evaluations should include malicious content near read boundaries, and status projections should use compact generated views. Those intersections do not change the primary purpose of this addendum.

## Executive conclusion

Wayfinder already has unusually strong foundations for a pre-release project: a frozen executable contract, closed schemas, three standard-library adapters, deterministic outputs, 305 shared conformance cases, failure-boundary testing, explicit approval boundaries, accepted hosted evidence, pinned workflow actions, and separation between runtime and maintainer authority.[^local-contract][^local-state][^local-governance]

The largest remaining risks are therefore not ordinary missing unit tests. They are **correlated assurance, drift between authoritative and public state, untested agent-level attacks, incomplete lifecycle planning, and absence of real-use evidence**.

The recommended order is:

1. eliminate status and claim drift;
2. threat-model the agent/data boundary and add adversarial agent evaluations;
3. measure conformance-suite strength with mutation, metamorphic, and independently derived oracles;
4. certify cross-adapter crash recovery and filesystem persistence behavior;
5. add signed, verifiable package/evidence provenance at publication time;
6. define schema migration, compatibility, and revocation before activation;
7. validate actual client installation and invocation behavior;
8. run task-based usability and scale pilots on representative repositories;
9. deepen traceability and change-impact reporting; and
10. add risk-based static analysis, privacy controls, and maintenance-health metrics.

These should be separate bounded tranches. Combining them would make approval ambiguous and would invalidate more evidence than necessary.

## Repository-grounded opportunity map

The following observations are about the current checkout, not generalized assumptions:

| Current strength or limitation | Evidence in the repository | Opportunity |
| --- | --- | --- |
| `current-state.md` is the sole mutable status authority. | Maintainer instructions and repository rules route status through it.[^local-state] | Generate or validate all public status projections from that authority. |
| Public status has already drifted. | `README.md` says revision 10 has no hosted evidence, while `current-state.md` and `docs/certification.md` record accepted revision-10 hosted evidence.[^local-readme][^local-certification] | Add a status projection/invariant check immediately. |
| The matrix is strong but explicitly not independent evaluation, forward testing, cross-adapter recovery, or full-family certification. | Certification documentation states these exclusions.[^local-certification] | Build assurance layers that target those exact gaps. |
| All adapters share one contract and one conformance harness. | Three implementations run the same 305 cases; six are categorized as property tests.[^local-contract][^local-cases] | Test for correlated faults and weak oracles rather than assuming agreement means correctness. |
| Initialization has extensive journal, interruption, race, and rollback cases. | The suite includes failure-boundary, target-race, rollback, and manual-recovery scenarios.[^local-cases] | Extend recovery testing across adapters, processes, filesystems, and real termination modes. |
| Local source content is explicitly “untrusted project data.” | Runtime guidance says source-assisted content is untrusted.[^local-runtime] | Turn this prose boundary into an explicit threat model and adversarial agent test corpus. |
| Secret-looking filenames are excluded from inventory. | The contract blocks `.env`, key, credential, VCS, and other sensitive paths.[^local-contract] | Add content-level privacy guidance and false-negative/false-positive evaluation without silently scanning or uploading files. |
| Actions are SHA-pinned and default to read-only permissions. | Governance and workflow files implement those controls.[^local-governance] | Add CodeQL/workflow analysis and release attestations without weakening least privilege. |
| Compatibility packaging is implemented, but hosted client smoke validation remains pending. | Compatibility documentation states that limitation.[^local-compatibility] | Test install, discovery, invocation policy, and uninstall on each claimed client. |
| Version 1 rejects unsupported schema versions but has no published migration path. | The contract fixes `schemaVersion` to 1 and fails unsupported versions.[^local-contract] | Specify migration and coexistence before records exist in the wild. |
| No production runtime is activated. | Runtime and support documentation intentionally block use.[^local-runtime][^local-support] | Obtain task-based usability, scale, and recovery evidence before activation. |

## Opportunity 1 — make public status a verified projection

### Finding

The strongest immediate finding is an actual repository inconsistency. `README.md` still says candidate revision 10 has no hosted evidence and that revision-9 parity is current, while the authoritative state and certification page record accepted revision-10 hosted evidence.[^local-readme][^local-state][^local-certification] The canonical validator passes despite this discrepancy.

Software-documentation studies find that engineers often update documentation incompletely or late; outdated documentation can remain useful, which makes silent staleness especially dangerous because readers may not recognize which parts are wrong.[^lethbridge] Traceability research finds its clearest maintenance benefit in change management, while also warning that trace links themselves impose maintenance cost.[^traceability]

### Recommendation

Create a small, explicit public-status projection owned by `current-state.md`:

- mark generated regions in `README.md`, `docs/certification.md`, package metadata, and marketplace descriptions;
- derive candidate, activation, certification claim, evidence run, source commit, and supported-runtime statements from one machine-readable maintainer status object;
- have repository validation fail when a public projection differs;
- keep narrative explanation authored, but prohibit duplicated mutable identity/status facts outside validated regions;
- expose a `maintain.py status --format json|markdown` command for both humans and CI; and
- distinguish “evidence exists,” “evidence accepted,” “evidence published,” “release registry updated,” and “runtime activated.”

This should not make `README.md` authoritative or generate the design record. It should make public claims mechanically consistent with authority.

### Acceptance evidence

- A test that deliberately changes the README candidate/evidence statement fails repository validation.
- All projections are byte-stable across repeated generation.
- A state transition changes only the intended generated regions.
- Historical documents and accepted evidence are never rewritten.
- A reader can determine the current candidate and exact claim without consulting maintainer-only chronology.

### Priority

**P0: high impact, low-to-medium effort.** This is the only opportunity supported by a presently observed contradiction.

## Opportunity 2 — threat-model the agent boundary and test indirect prompt injection

### Finding

Wayfinder correctly labels local source material as untrusted, but the current executable suite primarily verifies deterministic adapter behavior. The more consequential boundary is agent-level: source files, imported research, issue content, or repository instructions can contain text that pretends to be authoritative instructions.

Greshake et al. demonstrated that content retrieved by LLM-integrated applications can inject instructions, alter tool use, and cause data disclosure or unintended actions.[^greshake] NIST's Generative AI Profile treats direct and indirect prompt injection as a cross-sector risk, and OWASP ranks prompt injection, sensitive-information disclosure, supply-chain risk, and improper output handling among its principal LLM-application risks.[^nist-ai][^owasp-llm] NIST's SSDF recommends tracking security requirements, risks, and design decisions, using threat modeling, reviewing for hardcoded secrets, and collecting provenance.[^nist-ssdf]

### Recommendation

Create a Wayfinder-specific threat model before activation. At minimum, map:

- assets: repository bytes, approval authority, credentials, private project records, accepted decisions, generated plans, operation journals, and publication evidence;
- trust boundaries: user prompt, repository instructions, source inventory, browsed sources, project-record content, deterministic adapters, shell/runtime, VCS, and hosted workflows;
- attacker capabilities: malicious source author, compromised dependency/action, pull-request contributor, stale or misleading project record, and prompt-injected web content;
- consequential actions: record mutation, shell execution, network access, secret disclosure, VCS mutation, evidence creation, publication, and activation; and
- controls: instruction precedence, data labeling, least privilege, explicit authorization, deterministic plans, source confinement, output validation, and postcondition checks.

Add an agent-level adversarial corpus containing documents that attempt to:

- override the user or skill;
- ask for secrets or private files;
- widen source roots;
- follow symlinks or hidden VCS paths;
- reinterpret a hypothesis as an accepted decision;
- change an approval choice;
- trigger a shell/network/Git action;
- counterfeit a Wayfinder metadata block or evidence record; and
- exploit Markdown links, comments, Unicode confusables, encoded text, or nested quoted instructions.

Passing behavior should preserve the content as data, report the attempted instruction when material, and continue only within the user's authority. Adapter tests alone cannot prove this because the vulnerability is in the agent/harness interaction.

### Acceptance evidence

- A reviewed threat model with explicit assumptions and residual risks.
- Red-team scenarios across at least two capable host clients.
- No adversarial source causes unauthorized tool use or authority escalation.
- Tests cover both obvious and indirect/multi-document attacks.
- Security failures are reproducible without storing real secrets or private records.
- A documented policy explains that prompt injection cannot be eliminated solely by prompting; system permissions and action gates remain mandatory.

### Priority

**P0 before activation: high impact, medium effort.** The risk follows directly from Wayfinder's core feature of interpreting untrusted project material.

## Opportunity 3 — measure conformance-suite strength, not only pass count

### Finding

The current suite has excellent breadth and deterministic cross-adapter comparison, but a common specification, common fixtures, and common harness can produce correlated blind spots. Knight and Leveson's classic multiversion experiment found that independently developed implementations failed together more often than an independence assumption predicted; design diversity must not be treated as statistical independence.[^knight-leveson]

QuickCheck established executable properties with generated inputs as a practical complement to examples.[^quickcheck] Metamorphic testing is particularly useful where a complete test oracle is difficult: controlled input transformations define relations that outputs must preserve.[^metamorphic] Mutation testing evaluates whether a suite detects seeded faults rather than merely executing code.[^mutation] Differential testing finds disagreements among comparable implementations, but disagreement identifies a candidate bug; it does not by itself identify which implementation is right.[^differential]

### Recommendation

Add four complementary assurance layers:

1. **Property-based generation:** expand beyond the six current property-category cases. Generate bounded valid and invalid manifests, metadata blocks, relationship graphs, question transitions, inventories, operation plans, and path edge cases from the contract grammar.
2. **Metamorphic relations:** verify, for example, that input enumeration order does not change canonical output; moving an authored file while preserving ID updates only path-derived projections; adding irrelevant out-of-scope files changes neither plan nor catalog; canonical-equivalent Unicode is handled according to the declared NFC rule; and repeated recovery inspection remains read-only and byte-identical.
3. **Mutation analysis:** seed temporary changes such as reversed diagnostic precedence, missing symlink checks, skipped digest comparisons, incorrect sort keys, omitted journal links, or premature manifest publication. Report which mutants survive. Never mutate governed source in place or preserve mutants as evidence.
4. **Independent oracles:** derive a subset of expected results from small declarative models or independently reviewed scripts that do not import adapter or harness implementation helpers. Focus on canonical JSON, path containment, graph invariants, digest chains, and state transitions.

Add counterexample shrinking or minimization so a failing generated case becomes a small permanent regression fixture. Preserve seeds and generator versions in reports.

### Acceptance evidence

- A documented mutation score for security- and integrity-critical operators.
- Zero surviving “must-kill” mutations.
- Repeatable generated suites with recorded seeds.
- At least one independent oracle for each high-consequence domain: paths, canonicalization, graph rules, and journals.
- Demonstrated detection of one intentionally correlated three-adapter defect introduced only in an isolated test checkout.
- Runtime and output budgets that prevent generated tests from destabilizing ordinary CI.

### Priority

**P0/P1: very high assurance value, medium-to-high effort.** Start with a small must-kill mutation set and metamorphic relations before adopting a dependency-heavy framework.

## Opportunity 4 — certify cross-adapter recovery and crash consistency

### Finding

Wayfinder already tests many interruption boundaries, races, rollback states, and manual-recovery cases. However, accepted certification explicitly excludes cross-adapter recovery. A Python-started operation recovered by Node or PowerShell exercises interoperability that same-adapter tests cannot.

Pillai et al. found 60 crash vulnerabilities across 11 mature systems and showed that application-level update protocols can depend on subtle persistence properties that differ among filesystems.[^pillai] SQLite's long-running testing program combines branch coverage with simulated I/O errors, out-of-memory faults, crash tests, and multiple independently developed harnesses.[^sqlite-testing] These sources support systematic fault injection, but not a claim that Wayfinder needs database-grade durability.

### Recommendation

Build a bounded recovery matrix that varies:

- creating adapter versus recovering adapter;
- interruption boundary;
- recovery action (`inspect`, `resume`, `rollback`);
- process termination mode where safely reproducible;
- OS and filesystem case behavior;
- pre-existing directories and externally modified operation-owned paths;
- disk-full/write-error simulation where the host permits safe isolation; and
- source changes between planning, application, and recovery.

Test all directed adapter pairs: Python→Node, Python→PowerShell, Node→Python, Node→PowerShell, PowerShell→Python, and PowerShell→Node. Preserve current fail-closed behavior when ownership or durability cannot be proven.

Do not infer true power-loss durability from exception injection. If Wayfinder intends to promise persistence across abrupt host crashes, it must define required flush/rename/directory-sync semantics and test them on supported filesystems. Otherwise, keep the narrower promise of conservative application-level recovery explicit.

### Acceptance evidence

- All six directed cross-adapter pairs pass every supported recovery state.
- Injected faults never overwrite unrelated or externally modified bytes.
- Operation journals remain hash-valid and state-machine valid after recovery.
- The test report distinguishes simulated exceptions, killed processes, and actual persistence observations.
- Filesystem-specific guarantees and unsupported environments are documented rather than generalized.

### Priority

**P1 before activation: high impact, high effort.** It closes an explicit certification exclusion and validates a headline portability claim.

## Opportunity 5 — attach verifiable provenance to distributed artifacts

### Finding

Wayfinder binds local and hosted evidence with hashes and workflow metadata, and actions are pinned. Those controls establish strong internal integrity. They do not yet give a consumer a standard cryptographic statement connecting a distributed plugin/evidence bundle to the exact source workflow.

The in-toto framework was evaluated against 30 real software supply-chain compromises and uses cryptographically verifiable metadata across supply-chain steps.[^in-toto] SLSA 1.2 separates source and build tracks and defines progressively stronger provenance guarantees.[^slsa] GitHub artifact attestations use signed claims containing repository, workflow, commit, environment, and trigger information, and can be verified with GitHub CLI.[^github-attestations] GitHub also cautions that an attestation proves provenance, not that an artifact is secure.

### Recommendation

For a future authorized publication workflow:

- create one canonical distributable archive per plugin with deterministic file order, normalized timestamps/modes where the package format permits, and a complete SHA-256 manifest;
- attest the archive and the evidence-release manifest, not every source document;
- use GitHub's OIDC-backed artifact attestation only in the tightly scoped publication job;
- grant `id-token: write` and `attestations: write` only to that job and only after environment approval;
- publish verification instructions and expected repository/workflow identity;
- verify the attestation in a clean consumer job before treating publication as complete; and
- state the achieved controls rather than claiming a SLSA level without a formal assessment.

Because Wayfinder has no application dependencies, an SBOM adds less immediate value than a signed subject manifest. Still, include interpreter/action/toolchain inputs in provenance and reconsider an SPDX or CycloneDX SBOM if dependencies or generated binaries are introduced.

### Acceptance evidence

- A consumer can download a release bundle and verify its digest, attestation, source commit, and workflow identity.
- Rebuilding twice from the same source produces the same logical manifest and, if claimed, byte-identical archive.
- A tampered archive, wrong repository, wrong workflow, or wrong subject digest fails verification.
- Publication permissions remain absent from validation and certification jobs.

### Priority

**P1 at publication: high trust value, medium effort.** It should accompany distribution, not ordinary CI runs.

## Opportunity 6 — define schema migration and compatibility before activation

### Finding

Version 1 correctly rejects unknown schema versions. That is safe for a frozen candidate, but activation will create persistent records that later software must read, validate, migrate, or deliberately refuse. A version integer is not a migration policy.

JSON Schema requires schemas to declare the dialect they use through `$schema`; otherwise validators can make incompatible assumptions.[^json-schema-dialect] The JSON Schema project has explicitly identified backward compatibility as a major upgrade concern after changes between dialects altered validation behavior.[^json-schema-stability] Semantic Versioning is useful only after the public compatibility surface is defined.[^semver]

### Recommendation

Before activation, specify:

- the JSON Schema dialect for every schema and whether schemas are bundled or resolved only locally;
- the difference among contract version, record schema version, plugin package version, candidate revision, and evidence format version;
- reader/writer compatibility rules;
- whether multiple record versions may coexist in one workspace;
- migration preconditions, preview, confirmation digest, journal, rollback, and post-migration validation;
- preservation of stable document/question IDs and decision history;
- downgrade behavior and whether downgrade is unsupported;
- how an older adapter reports a newer record without mutating it;
- deprecation timelines and support windows; and
- golden migration fixtures for every supported version pair.

Migration should be a new explicit command/workflow, never an implicit side effect of `discover`, `validate`, or ordinary Update work.

### Acceptance evidence

- A written compatibility matrix and terminology table.
- Exact old→new golden records plus negative and rollback cases.
- Older tools fail read-only and diagnostically against newer unsupported records.
- Migration never changes historical meaning silently.
- Every schema declares its dialect and validates consistently across selected validators.

### Priority

**P1 before stable activation: high future value, medium effort.** Designing this before real records proliferate is substantially cheaper than retrofitting it.

## Opportunity 7 — perform real client installation and invocation smoke tests

### Finding

The repository validates manifest agreement, but compatibility documentation still says hosted smoke validation is pending. Packaging conformance cannot prove client discovery, explicit-only maintainer invocation, asset containment, help rendering, or uninstall behavior.

### Recommendation

Create a version-pinned compatibility matrix for Codex, Claude, and GitHub Copilot that tests only publicly documented behavior:

- repository/catalog discovery;
- runtime-only installation from the catalog;
- direct maintainer installation without catalog promotion;
- skill name and description presentation;
- explicit-only maintainer invocation policy where the client supports it;
- access to packaged references/assets/scripts;
- absence of duplicate skill copies;
- clean uninstall/reinstall and cache refresh; and
- non-activation behavior of the current runtime stub.

Separate packaging compatibility from semantic certification. A client smoke test may pass even though Wayfinder remains unactivated, and it must not mutate a live project record.

### Acceptance evidence

- Reproducible screen/log evidence for each supported client version.
- Expected differences documented as compatibility limits, not hidden.
- A failing optional client does not rewrite portable metadata solely to satisfy undocumented behavior.
- The maintainer package never appears as an ordinary end-user recommendation unless explicitly approved.

### Priority

**P1 before public runtime promotion: high product value, medium effort.** It closes another explicit documentation limitation.

## Opportunity 8 — validate usability with representative tasks and repositories

### Finding

Conformance proves deterministic behavior, not whether people can understand authority boundaries, create a useful initial record, recover from errors, or maintain the record without excessive ceremony. ISO 9241-11 treats usability as an outcome of use and centers effectiveness, efficiency, and satisfaction in a specified context.[^iso-usability] The System Usability Scale offers a lightweight standardized satisfaction measure, but it should supplement task outcomes rather than replace them.[^sus]

Architecture-decision research finds that structured decision support can improve effectiveness and efficiency, while field studies also report practical concerns about documenting too much or too little and keeping records current.[^decision-models][^adr-practice] This supports Wayfinder's facilitation design but also argues for testing it with real maintainers.

### Recommendation

Run a small formative pilot before activation, followed by a broader validation pilot. Include:

- a greenfield software project;
- a brownfield repository with conflicting documentation;
- a non-software or research-heavy project;
- a monorepo or repository with multiple plausible roots;
- a source-assisted initialization containing duplicates, secrets-by-name, binary files, and stale decisions; and
- an interrupted initialization requiring recovery.

Measure:

- task completion and correctness;
- time and number of clarification turns;
- incorrect authority assumptions;
- ability to locate a decision, evidence basis, and open question;
- recovery success without expert assistance;
- proposal revisions before approval;
- satisfaction/SUS score;
- perceived documentation burden; and
- record usefulness after a delayed return session.

Capture qualitative confusion points, but do not store private project records in the public repository.

### Acceptance evidence

- Predetermined success criteria and participant/task protocol.
- At least one usability finding that changes guidance or interface before activation, or evidence that no material issue was observed within stated limits.
- Separate reporting for novices and experienced maintainers.
- No claim of general usability from a single owner-led walkthrough.

### Priority

**P1 before activation: high product value, medium-to-high effort.** This is the missing bridge between executable correctness and useful operation.

## Opportunity 9 — deepen traceability and change-impact analysis

### Finding

Doctor verifies that every declared normative rule is cited by at least one conformance case. That is valuable rule-to-test traceability. It does not show whether each rule is implemented in every relevant adapter, which schemas/templates/docs it constrains, or whether a passing case would detect its violation.

A mapping study of 63 traceability studies found support for 11 maintenance/evolution activities, with change management the most frequently supported; it also identifies link maintenance as the principal cost.[^traceability] This argues for a small generated trace model, not a manually maintained all-to-all matrix.

### Recommendation

Introduce a maintainer-owned change-impact index linking:

- normative rule → schema/grammar/template fields;
- normative rule → positive, negative, property, recovery, and mutation tests;
- normative rule → adapter implementation region or named semantic function;
- command → result codes and schemas;
- accepted decision → governed artifacts changed; and
- public claim → authoritative status field and evidence.

Generate inverse views and fail on orphaned rules, cases with no asserted behavior, undocumented result codes, or changed governed artifacts without an impact declaration. Avoid embedding trace annotations throughout every line of code; stable function/section identifiers are less costly.

### Acceptance evidence

- A change to one rule produces a bounded, reviewable impact report.
- The index detects an intentionally orphaned rule and an uncited diagnostic code.
- Generated trace views never become authority for semantic meaning.
- Maintenance effort is measured; links that do not support a concrete review question are removed.

### Priority

**P2: medium-to-high value, medium effort.** Implement after mutation analysis identifies which links materially improve assurance.

## Opportunity 10 — add scale and resource-envelope certification

### Finding

The contract defines explicit inventory limits, but the current evidence emphasizes semantic cases rather than operational envelopes. A tool can be semantically correct on small fixtures yet become unusable or unsafe with deep trees, many files, large Markdown documents, long paths, huge generated regions, or constrained disk space.

### Recommendation

Define supported envelopes rather than promising arbitrary scale:

- maximum entries, total bytes, file bytes, path length, nesting, metadata blocks, documents, questions, relations, and operation targets;
- expected time and peak memory for representative small/medium/large records;
- cancellation/termination behavior;
- deterministic limit-exceeded diagnostics;
- no partial output or writes when a preflight limit fails; and
- platform-specific limitations for Windows paths and filesystem semantics.

Add performance regression thresholds only after collecting repeatable baselines on controlled runners. Avoid fragile wall-clock gates for ordinary CI; use generous ceilings and trend reports.

### Acceptance evidence

- Benchmark fixtures and generator code are deterministic.
- Limits are documented and enforced identically across adapters.
- Exceeding a limit fails before consequential writes.
- Results report environment, runtime, input shape, time, and memory methodology.

### Priority

**P2 before broad adoption: medium value, medium effort.** It prevents accidental claims of unbounded scalability.

## Opportunity 11 — add risk-based static and workflow analysis

### Finding

Wayfinder uses substantial Python, JavaScript, PowerShell, and GitHub Actions code. Current validation is purpose-built and strong on package invariants, but no general static-analysis workflow is present. GitHub CodeQL supports Python, JavaScript/TypeScript, and GitHub Actions; it does not cover PowerShell.[^github-codeql]

### Recommendation

- Enable CodeQL for Python, JavaScript, and Actions with read-only checkout and minimal `security-events` permission.
- Add a PowerShell-specific static analyzer only after evaluating dependency, pinning, and false-positive cost.
- Add secret scanning and push protection if repository settings allow it.
- Periodically assess against the OpenSSF OSPS Baseline, documenting not-applicable controls.[^openssf-baseline]
- Keep findings advisory initially; promote only high-confidence rules to required gates.
- Preserve pinned action SHAs and review Dependabot action updates.

Static analysis should complement, not replace, path/race/recovery tests and human review.

### Acceptance evidence

- Baseline findings triaged with no blanket suppressions.
- Workflow analysis covers permission escalation, untrusted inputs, script injection, and credential persistence.
- A documented path exists for unsupported PowerShell analysis.
- No new network dependency is added to runtime adapters.

### Priority

**P2: medium value, low-to-medium effort.** Useful defense in depth after the P0 assurance work.

## Opportunity 12 — formalize privacy, retention, and disclosure boundaries

### Finding

The contract excludes common secret filenames, and issue/security templates warn against submitting secrets or private project records. Filename rules cannot identify all sensitive content, while aggressive content scanning can itself expose data or create false confidence.

### Recommendation

Before activation:

- document what project content Wayfinder reads, hashes, stores, copies, and displays;
- state that local hashes may still be sensitive correlators;
- distinguish local deterministic processing from optional model/provider data handling;
- add a pre-publication privacy checklist for fixtures, bug reports, evidence, and research;
- define retention and deletion expectations for `.wayfinder/operations` after successful initialization;
- provide a safe redaction recipe that never edits accepted evidence in place;
- test obvious high-risk filenames and content markers, while labeling detection as best effort; and
- ensure diagnostics do not echo secret values or large source excerpts.

This policy should avoid promising comprehensive secret detection. The safer default remains local confinement, least disclosure, and explicit user review.

### Acceptance evidence

- A data-flow and retention table for every command.
- Tests prove diagnostics redact representative tokens and credentials.
- Documentation explains model/provider exposure separately from adapter behavior.
- Public bug/evidence tooling rejects or warns on likely private payloads without uploading them automatically.

### Priority

**P2 before activation: medium-to-high impact, medium effort.** It protects the project-record use case, which naturally involves sensitive organizational knowledge.

## Opportunity 13 — define release revocation and incident response

### Finding

`SECURITY.md` provides a private reporting channel but intentionally offers no response-time commitment while the candidate is unactivated. That is reasonable now. Activation changes the obligation: a compromised adapter, bad evidence release, leaked signing identity, or unsafe contract interpretation needs a predefined response.

### Recommendation

Before activation, define:

- supported versions and security contact expectations;
- vulnerability intake, embargo, triage, and disclosure states;
- how to mark a plugin or evidence release revoked without deleting historical evidence;
- how release registry status communicates withdrawal or supersession;
- emergency authority and which actions still require owner approval;
- attestation/signing compromise recovery;
- downstream notification channels; and
- a tabletop exercise for a malicious release, prompt-injection bypass, and recovery defect.

NIST SSDF explicitly includes responding to residual vulnerabilities and improving processes after incidents.[^nist-ssdf]

### Acceptance evidence

- A tabletop report with decisions, gaps, and follow-up owners.
- Revocation preserves forensic evidence and never relabels a compromised artifact as valid.
- Consumers can distinguish unsupported, superseded, withdrawn, and active releases.

### Priority

**P2 before activation: high consequence, low frequency, medium effort.** Prepare the mechanism before it is needed.

## Opportunity 14 — monitor maintainability and correlated complexity

### Finding

The three adapters, maintainer command, and conformance runner together exceed 12,000 lines and 900 KB in the current checkout. Large single-file adapters may be justified by dependency-free portability, but they increase review burden and the chance that equivalent logic is copied with the same misconception.[^local-size]

### Recommendation

Do not refactor solely to reduce line count. Instead:

- measure function size, cyclomatic/cognitive complexity, duplication, and change coupling as trend signals;
- identify semantic kernels that should remain independently implemented versus mechanical tables that can be generated and verified;
- require a “correlated-fault review” when the same semantic change is copied to all adapters;
- rotate the order in which adapter implementations are reviewed;
- use mutation results to target risky regions; and
- keep the dependency-free, separately installable package boundary unless evidence supports changing it.

Generated code can reduce drift but also creates one generator as a common-mode failure. If introduced, generated bytes, generator version, and independent output checks must be governed explicitly.

### Acceptance evidence

- Complexity trends are informational until correlated with defects or review cost.
- Refactors preserve frozen behavior through differential and mutation tests.
- No common helper silently becomes the sole semantic oracle for all adapters.

### Priority

**P3: useful sustainability work, evidence-dependent.** Measure first; refactor only where data identifies a problem.

## Recommended tranche sequence

| Tranche | Contents | Why grouped | Explicit exclusions |
| --- | --- | --- | --- |
| A — Claim integrity | Opportunity 1 | One low-risk maintainer/documentation concern with an observed defect | Contract, adapters, evidence, publication, activation |
| B — Agent threat model | Opportunity 2 plus privacy threat boundaries from 12 | One coherent agent-security design and evaluation surface | Runtime activation, external scanning services, secrets, live projects |
| C — Assurance strength | Opportunity 3 and traceability subset of 9 | Mutation/metamorphic/oracle work should inform trace links | Governed semantics, accepted evidence, dependency additions unless separately approved |
| D — Recovery portability | Opportunity 4 | Cross-adapter and filesystem behavior require a dedicated matrix | Broad full-family claim, live-project recovery |
| E — Publication trust | Opportunity 5 plus revocation design from 13 | Attestation and revocation belong to release governance | Actual publication, registry change, activation |
| F — Evolution contract | Opportunity 6 | Schema migration changes future semantic surface | Implementing v2 or migrating any live record |
| G — Product readiness | Opportunities 7, 8, and 10 | Compatibility, usability, and scale jointly support activation decisions | Activation itself and live destructive mutation |
| H — Defense in depth | Opportunities 11, remaining 12, and 14 | Static analysis and maintenance metrics are valuable after core risks | Runtime dependencies and unbounded tooling expansion |

Tranche A is the best next implementation candidate because it fixes an observed public contradiction without reopening the frozen runtime candidate. Tranches B and C offer the greatest risk reduction before activation. Tranche G should produce the evidence used for an activation decision; passing conformance alone should remain insufficient.

## What not to do

- Do not reopen the frozen contract merely to adopt fashionable tooling.
- Do not equate three agreeing adapters with three independent proofs.
- Do not claim crash durability from injected exceptions alone.
- Do not sign individual documentation files; attest distributable subjects and verify them.
- Do not claim a SLSA level without assessing every requirement for that level.
- Do not add an SBOM ceremony when there are no runtime dependencies and no defined consumer need.
- Do not make automated secret detection an authorization to read excluded files.
- Do not treat CodeQL as coverage for PowerShell or as proof of security.
- Do not infer usability from the owner's successful maintenance sessions.
- Do not add trace links that have no concrete change-impact or review use.
- Do not persist private pilot repositories or adversarial payloads containing real secrets.
- Do not combine research acceptance with implementation, publication, or activation authority.

## Evidence strength and limitations

Approximate citation counts below are OpenAlex `cited_by_count` values retrieved on 2026-09-14 after title/DOI verification. They indicate influence, not correctness. New standards and operational guidance are better judged by authority, applicability, and version currency than citation totals.[^openalex]

| Source | Approximate citations | Use in this addendum |
| --- | ---: | --- |
| Knight & Leveson, 1986 | 773 | Strong warning against assuming independent failure among multiple implementations. |
| Greshake et al., 2023 | 513 | Direct evidence of indirect prompt injection in LLM-integrated applications. |
| Lethbridge et al., 2003 | 341 | Empirical evidence about software-documentation use and staleness. |
| QuickCheck, 2000 | 220 | Foundational property-based testing method. |
| Pillai et al., 2014 | 99 | Direct empirical evidence about application crash-consistency assumptions. |
| Tian et al., 2021 | 34 | Systematic mapping of traceability benefits, costs, and research gaps. |
| in-toto, 2019 | 25 | Peer-reviewed supply-chain integrity framework evaluated against real compromises. |

Material limitations remain:

- No external study evaluates Wayfinder itself.
- Agent prompt-injection defenses remain an active research area; adversarial tests demonstrate bounded resistance, not universal safety.
- Citation counts lag and bibliographic services contain metadata errors.
- Filesystem papers often study Linux and durable storage semantics that may not map directly to macOS, Windows, network filesystems, or hosted runners.
- Usability standards define evaluation dimensions but do not prescribe Wayfinder-specific success thresholds.
- Vendor documentation describes available platform controls, not independent proof that enabling them improves this repository.
- Repository observations are point-in-time and should be refreshed before an implementation tranche.

## Sources

[^local-state]: Wayfinder Maintainer, “[Current maintainer state](../current-state.md),” current repository authority, accessed 14 September 2026.

[^local-readme]: Wayfinder, “[README](../../../../../../README.md),” repository public status, accessed 14 September 2026.

[^local-certification]: Wayfinder, “[Certification](../../../../../../docs/certification.md),” repository documentation, accessed 14 September 2026.

[^local-governance]: Wayfinder, “[Governance](../../../../../../docs/governance.md),” repository documentation, accessed 14 September 2026.

[^local-compatibility]: Wayfinder, “[Client compatibility](../../../../../../docs/compatibility.md),” repository documentation, accessed 14 September 2026.

[^local-support]: Wayfinder, “[Support](../../../../../../SUPPORT.md),” repository policy, accessed 14 September 2026.

[^local-runtime]: Wayfinder, “[Runtime skill](../../../../../wayfinder/skills/wayfinder/SKILL.md),” frozen unactivated runtime guidance, accessed 14 September 2026.

[^local-contract]: Wayfinder, “[Executable contract version 1](../../../../../wayfinder/skills/wayfinder/references/contracts/v1.md),” frozen candidate reference, accessed 14 September 2026.

[^local-cases]: Wayfinder, “[Conformance cases](../../../../../wayfinder/skills/wayfinder/assets/contract-v1/conformance/v1/cases.json),” 305-case registry, accessed 14 September 2026.

[^local-size]: Line and byte counts from the three registered adapter files, `maintain.py`, the conformance runner, and maintainer regression modules in this checkout, measured 14 September 2026: 12,463 lines and 920,945 bytes.

[^lethbridge]: Timothy C. Lethbridge, Janice Singer, and Andrew Forward, “[How Software Engineers Use Documentation: The State of the Practice](https://doi.org/10.1109/MS.2003.1241364),” *IEEE Software* 20(6), 2003, 35–39.

[^traceability]: Yuan Tian, Peng Liang, and Antony Tang, “[The Impact of Traceability on Software Maintenance and Evolution: A Mapping Study](https://doi.org/10.1002/smr.2374),” *Journal of Software: Evolution and Process* 33(10), 2021. The study synthesizes 63 studies published from 2000 through May 2020.

[^greshake]: Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz, “[Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://doi.org/10.1145/3605764.3623985),” *AISec 2023*. Preprint and artifacts: https://arxiv.org/abs/2302.12173 and https://github.com/greshake/llm-security.

[^nist-ai]: Chloe Autio et al., “[Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile](https://doi.org/10.6028/NIST.AI.600-1),” NIST AI 600-1, 26 July 2024, updated 8 April 2026.

[^owasp-llm]: OWASP GenAI Security Project, “[OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/),” including LLM01 Prompt Injection, LLM02 Sensitive Information Disclosure, LLM03 Supply Chain, and LLM05 Improper Output Handling.

[^nist-ssdf]: Murugiah Souppaya, Karen Scarfone, and Donna Dodson, “[Secure Software Development Framework (SSDF) Version 1.1](https://doi.org/10.6028/NIST.SP.800-218),” NIST SP 800-218, February 2022. See also NIST, “[Recommended Minimum Standard for Vendor or Developer Verification of Code](https://www.nist.gov/itl/executive-order-14028-improving-nations-cybersecurity/software-supply-chain-security-guidance-3),” 2021.

[^knight-leveson]: John C. Knight and Nancy G. Leveson, “[An Experimental Evaluation of the Assumption of Independence in Multiversion Programming](https://doi.org/10.1109/TSE.1986.6312924),” *IEEE Transactions on Software Engineering* SE-12(1), 1986, 96–109.

[^quickcheck]: Koen Claessen and John Hughes, “[QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs](https://doi.org/10.1145/351240.351266),” *ICFP 2000*, 268–279.

[^metamorphic]: Tsong Yueh Chen et al., “[Metamorphic Testing: A Review of Challenges and Opportunities](https://doi.org/10.1145/3143561),” *ACM Computing Surveys* 51(1), 2018. NIST application overview: https://csrc.nist.gov/pubs/journal/2016/06/metamorphic-testing-for-cybersecurity/final.

[^mutation]: Yue Jia and Mark Harman, “[An Analysis and Survey of the Development of Mutation Testing](https://doi.org/10.1109/TSE.2010.62),” *IEEE Transactions on Software Engineering* 37(5), 2011, 649–678.

[^differential]: William M. McKeeman, “[Differential Testing for Software](https://vmssoftware.com/docs/dtj-v10-01-1998.pdf),” *Digital Technical Journal* 10(1), 1998, 100–107.

[^pillai]: Thanumalayan Sankaranarayana Pillai, Vijay Chidambaram, Ramnatthan Alagappan, Samer Al-Kiswany, Andrea C. Arpaci-Dusseau, and Remzi H. Arpaci-Dusseau, “[All File Systems Are Not Created Equal: On the Complexity of Crafting Crash-Consistent Applications](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/pillai),” *OSDI 2014*, 433–448.

[^sqlite-testing]: SQLite Project, “[How SQLite Is Tested](https://sqlite.org/testing.html),” practitioner documentation, accessed 14 September 2026.

[^in-toto]: Santiago Torres-Arias, Hammad Afzali, Trishank Karthik Kuppusamy, Reza Curtmola, and Justin Cappos, “[in-toto: Providing Farm-to-Table Guarantees for Bits and Bytes](https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias),” *USENIX Security 2019*, 1393–1410.

[^slsa]: OpenSSF SLSA Working Group, “[SLSA Specification 1.2](https://slsa.dev/spec/v1.2/),” current approved specification, accessed 14 September 2026.

[^github-attestations]: GitHub, “[Artifact Attestations](https://docs.github.com/en/actions/concepts/security/artifact-attestations)” and “[Using Artifact Attestations to Establish Provenance for Builds](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations),” accessed 14 September 2026.

[^json-schema-dialect]: JSON Schema, “[Dialect and Vocabulary Declaration](https://json-schema.org/understanding-json-schema/reference/schema),” accessed 14 September 2026.

[^json-schema-stability]: JSON Schema, “[Moving Toward a Stable Spec](https://json-schema.org/blog/posts/stable-json-schema),” 19 December 2024.

[^semver]: Tom Preston-Werner et al., “[Semantic Versioning 2.0.0](https://semver.org/),” accessed 14 September 2026.

[^iso-usability]: International Organization for Standardization, “[ISO 9241-11:2018 — Usability: Definitions and Concepts](https://www.iso.org/standard/63500.html),” March 2018, confirmed current in 2023.

[^sus]: John Brooke, “[SUS: A Quick and Dirty Usability Scale](https://hci-studies.org/methods-and-measures/downloads/SUS_Brooke1996.pdf),” in *Usability Evaluation in Industry*, 1996, 189–194.

[^decision-models]: Olaf Zimmermann et al., “[Two Controlled Experiments on Model-Based Architectural Decision Making](https://doi.org/10.1016/j.infsof.2015.03.006),” *Information and Software Technology* 63, 2015, 58–75.

[^adr-practice]: Bardha Ahmeti, Maja Linder, and Rebekka Wohlrab, “[Exploring the Adoption and Effectiveness of Architecture Decision Records in Agile Software Development](https://research.chalmers.se/en/publication/538920),” womENcourage 2023.

[^github-codeql]: GitHub, “[Code Scanning with CodeQL](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning),” accessed 14 September 2026.

[^openssf-baseline]: OpenSSF, “[Open Source Project Security Baseline](https://baseline.openssf.org/versions/2026-02-19.html),” version 2026-02-19.

[^openalex]: OpenAlex, publication metadata and `cited_by_count`, retrieved 14 September 2026, https://openalex.org/. Verified records include https://openalex.org/W1971991620 (Knight and Leveson), https://openalex.org/W4388886073 (Greshake et al.), https://openalex.org/W1989526951 (Lethbridge et al.), https://openalex.org/W4242126179 (QuickCheck), https://openalex.org/W1412006679 (Pillai et al.), https://openalex.org/W3197095895 (Tian et al.), and https://openalex.org/W2967772953 (in-toto).
