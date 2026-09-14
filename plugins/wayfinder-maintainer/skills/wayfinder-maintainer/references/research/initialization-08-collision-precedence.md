# Initialization research 08: collision precedence

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** When independently allocated candidate IDs use the same ordinal, which candidate retains it?
- **Prior decision:** An allocated ID is a candidate until first integration into the declared canonical project history; at that boundary it becomes immutable.
- **Decision:** Option A, canonical integration order.

## Executive conclusion

Use **canonical integration order**: an identifier already present in the latest canonical baseline always retains its ordinal. A colliding candidate that has not yet integrated must be re-keyed. If multiple colliding candidates are presented together and none is yet canonical, they must be integrated in an explicit order; the first one successfully validated and integrated becomes the incumbent.

This is Option A below. The rule makes canonical history the only arbiter and gives every state one reproducible answer. It does not claim that the first-integrated document is older, more important, or more deserving. Retaining an ordinal is merely a consequence of the accepted immutability boundary; the losing document's knowledge remains eligible for integration after re-keying.

This decision does **not** define how re-keying edits metadata and references, whether a mnemonic is regenerated, or how the operation is made atomic. Those mechanics are the next decision.

## Collision cases

The precedence rule must cover two cases without conflating them:

### Case 1: canonical incumbent versus candidate

The latest declared canonical baseline already contains `wf-0042-a`. A contribution proposes `wf-0042-b`.

The accepted immutability rule already constrains the result: `wf-0042-a` cannot change. The candidate must lose the ordinal or remain unintegrated. Allowing it to displace the incumbent would make an integrated ID mutable.

### Case 2: candidate versus candidate

Two contributions based on the same earlier baseline independently allocate ordinal `0042`; neither has yet entered canonical history.

There is no causal fact in the project record that intrinsically makes one candidate the rightful owner. The policy must either serialize their integration, infer precedence from secondary data, or ask a person to choose.

## Evaluation criteria

| Criterion | Meaning for Wayfinder |
| --- | --- |
| Consistency with immutability | An integrated ID is never displaced. |
| Reproducibility | The same canonical baseline and candidate set yield the same diagnosis. |
| Portability | No network clock, forge-specific queue, or central registry is required. |
| Auditability | A reviewer can explain the winner using visible project history. |
| Bias resistance | Precedence does not depend on author identity, document importance, or mutable prose. |
| Correctability | The losing contribution remains recoverable through a narrow re-key operation. |
| Minimal semantics | Keeping an ordinal does not imply priority, authority, or chronology beyond integration order. |

## Evidence synthesis

### 1. The canonical history can provide the serial order

Herlihy and Wing define linearizability as making concurrent operations appear to take effect at a single point in a sequential history while respecting real-time ordering.^1 Wayfinder is not implementing a concurrent data object, but the model clarifies what the accepted integration boundary needs: one observable event at which a candidate becomes the permanent occupant of an ordinal.

Git's default push safety similarly protects an existing branch history: branch updates are ordinarily accepted only when they fast-forward, and stale parallel work must first incorporate the already-published history.^2 Git does not validate Wayfinder IDs, so this is supporting operational precedent rather than sufficient enforcement.

**Implication:** treat successful validation and integration into the declared baseline as the linearization point. Once the baseline contains an ordinal, its occupant is the reproducible incumbent.

### 2. Creation timestamps cannot establish a trustworthy global order

Lamport shows that events in distributed systems naturally form a partial causal order; constructing a total order requires an explicit logical rule rather than assuming physical clocks reveal causality.^3 Independently created branches may have no happens-before relation.

Git also permits author and committer dates to be supplied through command options and environment variables.^4 Rebasing removes commits from one line of development and reapplies their changes as new commits on another.^5 Therefore “earliest timestamp,” “lowest commit date,” and “oldest commit hash” do not reliably represent first conceptual creation.

**Implication:** do not compare wall-clock dates, author dates, committer dates, or commit topology to award an ordinal before either candidate integrates.

### 3. Content-derived tie-breakers create false semantics

A lexicographic comparison of path, H1, mnemonic, complete file bytes, or commit hash would produce a machine answer, but it would couple precedence to facts Wayfinder has already declared non-authoritative or mutable. Rewording a title, moving a file, formatting Markdown, or rebasing could change the winner. A hash would make the rule less inspectable without making the result more meaningful.

The earlier identifier research rejected content hashes for evolving logical records for the same reason: they identify a representation or version, not the durable knowledge object.

**Implication:** determinism should arise from canonical state transition, not an arbitrary ordering over candidate content.

### 4. A known, consistently applied rule supports procedural fairness

Procedural-justice research distinguishes satisfaction with an outcome from judgments about the process that produced it. Colquitt's construct-validation work found procedural justice to be distinct from distributive, interpersonal, and informational justice and related it to outcomes including rule compliance and commitment.^6 The underlying criteria include consistency, lack of bias, accuracy, correctability, representation, and ethicality.

This literature studies people and organizations, not identifier collisions. It cannot prove that “first integrated wins” is morally fair or psychologically optimal. Its relevant design lesson is narrower: publish the precedence rule in advance, apply it without regard to contributor identity or content importance, explain the evidence used, and preserve a correction path for the losing contribution.

**Implication:** diagnostics should say “the canonical baseline already contains this ordinal,” not “your document lost” or “the other document is older.” Before either candidate integrates, contributors retain voice by choosing integration order or withdrawing a candidate; after integration, the invariant controls.

### 5. Silent conflict resolution carries avoidable risk

Dias, Borba, and Barreto describe source merge conflict resolution as costly and error-prone and found higher conflict likelihood with overlapping and larger contributions across 73,504 reproduced merge scenarios.^7 Their population was Ruby and Python MVC repositories, so the measured effects do not transfer directly to Markdown metadata.

**Implication:** collision detection must stop integration visibly. Precedence tells the operator which candidate may keep the ordinal; it must not silently rewrite or discard either document.

## Options

### Option A: canonical integration order — recommended

The first candidate successfully integrated into the declared canonical history retains the ordinal. Thereafter it is the incumbent. Every later colliding candidate must re-key before integration.

**Exact precedence key:**

1. If the latest canonical baseline contains the ordinal, that document wins.
2. If the baseline does not contain it and only one candidate contribution uses it, that candidate may integrate.
3. If an integration batch contains multiple new uses, validation rejects the unordered batch. The integrator must establish an order, integrate one valid contribution, refresh the baseline, and re-key the others.
4. A candidate's local creation time, commit time, path, H1, mnemonic, author, branch name, and content do not affect precedence.

**Benefits:** directly follows the accepted immutability boundary; no additional metadata or registry; same canonical state gives the same answer; easy to explain and validate; neutral about content and contributor identity.

**Costs:** scheduling and review latency can decide who retains a number; a candidate may use an ID for a long time and still lose it; unordered batch integration requires serialization; “first” must never be presented as conceptual seniority or merit.

**Best fit:** a repository workflow with one authoritative integration history and re-keying before merge.

### Option B: earliest verifiable local claim

The candidate with the earliest creation evidence retains the ordinal, even if another candidate reached canonical review first.

Possible evidence includes the first Git commit containing the ID, an author date, a signed timestamp, or a reservation record.

**Benefits:** may feel closer to “I claimed it first”; rewards early creation rather than review throughput; can honor a long-lived branch.

**Costs:** ordinary Git time is user-controlled and history can be rewritten; concurrent events lack a natural global order; defining trustworthy evidence effectively adds a signed registry or logical-clock protocol; forces canonical history to defer to non-canonical state; creates disputes over provenance.

**Best fit:** a centrally timestamped submission system where claim time is already authoritative.

### Option C: content-derived deterministic tie-breaker

Compare a stable-looking candidate attribute, such as mnemonic, path, document digest, or commit hash, and let the lexicographically smaller value retain the ordinal.

**Benefits:** automatic selection for an unordered batch; no human decision; superficially reproducible when all bytes and history are fixed.

**Costs:** mutable prose or version artifacts decide identity; contributors can influence the outcome; rebasing and formatting can change hashes; the result is difficult to justify; it embeds accidental semantics into a governance decision.

**Best fit:** replicated systems whose entire state and conflict function are formally canonicalized, not an evolving human-authored record.

### Option D: integrator discretion

When neither candidate is canonical, a person selects which one keeps the ordinal based on context.

**Benefits:** can consider stakeholder expectations, already-shared links, and effort required to repair references; gives contributors direct voice.

**Costs:** non-reproducible; potentially biased; requires case-specific negotiation; diagnostics cannot predict the outcome; encourages treating ordinals as valuable rather than arbitrary identity tokens.

**Best fit:** rare migrations or exceptional recovery where evidence outside the project record genuinely matters.

## Recommendation

Choose **Option A: canonical integration order**, with these invariants:

1. An ordinal's canonical incumbent always retains it.
2. A candidate never displaces or renames an integrated document.
3. If no incumbent exists, the first candidate successfully validated and integrated becomes the incumbent.
4. An unordered batch with multiple claimants is rejected rather than auto-ranked.
5. Integration order is the only precedence fact; it conveys no semantic priority, age, quality, or ownership.
6. Author identity, timestamps, branch names, paths, titles, mnemonics, file content, and hashes never decide precedence.
7. The losing candidate is preserved and blocked pending a deterministic re-key operation.
8. Validation reports the baseline revision and both claimant locations so the result is auditable.
9. Validation refreshes the baseline immediately before the integration attempt; a stale result cannot confer precedence.
10. Exceptional manual recovery cannot rewrite an integrated ID; it must use future supersession or repair policy.

This option converts a distributed allocation race into a serialized, visible integration decision. It keeps the runtime contract small and makes the collision winner derivable from the same history that establishes immutability.

## Deferred details

Accepting Option A would not yet answer:

- How the losing candidate obtains the next available ordinal.
- Whether its frozen mnemonic remains unchanged during re-keying.
- Which metadata, links, indexes, generated artifacts, and prose references are rewritten.
- How the script distinguishes ID references from coincidental text.
- Whether uncommitted changes are permitted during repair.
- How the operation rolls back if validation fails.
- How the collision report represents the baseline revision portably.

Those details belong to the re-key transaction decision.

## Next decision

Define what the re-key transaction may rewrite automatically: semantically proven metadata and references, every exact token occurrence, only the losing declaration, or nothing. After that boundary is accepted, separately define staging, rollback, and final verification.

## Sources

1. Herlihy, M. P., and Wing, J. M. “[Linearizability: A Correctness Condition for Concurrent Objects](https://doi.org/10.1145/78969.78972).” *ACM Transactions on Programming Languages and Systems* 12(3), 1990, pp. 463–492.
2. Git Project. “[git-push: Push Rules and Note About Fast-Forwards](https://git-scm.com/docs/git-push#_push_rules).” Accessed 2026-09-13.
3. Lamport, L. “[Time, Clocks, and the Ordering of Events in a Distributed System](https://doi.org/10.1145/359545.359563).” *Communications of the ACM* 21(7), 1978, pp. 558–565.
4. Git Project. “[git-commit: Commit Information and Date Formats](https://git-scm.com/docs/git-commit#_commit_information).” Accessed 2026-09-13.
5. Git Project. “[Git User Manual: Rebasing](https://git-scm.com/docs/user-manual#_rebasing).” Accessed 2026-09-13.
6. Colquitt, J. A. “[On the Dimensionality of Organizational Justice: A Construct Validation of a Measure](https://doi.org/10.1037/0021-9010.86.3.386).” *Journal of Applied Psychology* 86(3), 2001, pp. 386–400.
7. Dias, K., Borba, P., and Barreto, M. “[Understanding Predictive Factors for Merge Conflicts](https://doi.org/10.1016/j.infsof.2020.106256).” *Information and Software Technology* 121, 2020, 106256.
