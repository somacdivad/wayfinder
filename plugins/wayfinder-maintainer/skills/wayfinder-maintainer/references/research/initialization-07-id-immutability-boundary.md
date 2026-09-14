# Initialization research 07: ID immutability boundary

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** At what event does a freshly allocated Wayfinder ID become immutable?
- **Prior decision:** IDs use `wf-<global-ordinal>-<frozen-mnemonic>`; ordinary allocation scans the complete valid record and chooses the next project-wide ordinal.
- **Decision:** Option B, immutable at first integration into the declared canonical project history.

## Executive conclusion

Make an ID immutable at its **first integration into the project record's declared canonical history**. Before that event, a newly minted ID is a candidate: it is valid and usable inside its isolated work, but validation at integration may require it to be re-keyed if another contribution has already integrated the same ordinal.

This is Option B below. It preserves the strong promise that an ID already shared through the canonical record never changes, while allowing independent branches to use a deterministic sequential allocator without a central reservation service. It maps naturally to optimistic concurrency control: work proceeds against a known state, then validates against the current integration target before the write is accepted.

This decision does **not** select a collision winner, specify re-key mechanics, or define replacement lineage for an incorrectly identified integrated document. Those are narrower follow-on decisions.

## The boundary being decided

Three states must not be conflated:

1. **Proposed:** the allocator has displayed a candidate but has not written it.
2. **Candidate:** the identifier exists in isolated work but has not entered the declared canonical project history.
3. **Integrated:** the identifier has appeared in that canonical history and is therefore permanent.

The decision is the transition from candidate to integrated. It is not a new document metadata field. Under the recommendation, candidate status is derived from version-control ancestry or an explicit publication baseline, rather than copied into every document where it could become stale.

## Scope assumptions

This review assumes:

- A project record has one declared integration baseline. In Git this will normally be the repository's default branch, but the exact declaration mechanism remains an initialization decision.
- Work may be created on independent branches or in disconnected copies.
- The normal allocator cannot reserve a number in a networked registry.
- Validation can inspect both the candidate contribution and the current integration baseline.
- Once integrated, links and external discussion may rely on an ID even if the document later moves, changes title, or changes metadata.

For a non-Git record, the same concept requires an explicit published snapshot or owner-acceptance marker. If no baseline is available, a validator can prove present syntax and uniqueness but cannot prove historical immutability.

## Evidence synthesis

### 1. Persistent-identifier systems distinguish reservation from registration

DataCite distinguishes draft records from registered and findable DOIs. A draft can reserve an identifier and can still be deleted; moving it to a registered state is final, and it cannot return to draft.^1 This is a useful governance pattern: local preparation and globally relied-upon identity need not have the same mutability guarantee.

Wayfinder is not a DOI registration service. A Git integration baseline is much smaller in scope and does not confer public resolvability. The transferable principle is the explicit one-way transition: before the reliance event, correction is allowed; after it, identity is durable.

**Implication:** distinguish candidate IDs from integrated IDs even though they share the same syntax. Make the transition objective and detectable rather than dependent on an author's memory.

### 2. Stable identifiers can coexist with changing metadata

Crossref states that a DOI string cannot change once registered, while associated metadata can be updated.^2 This separates identity from description. Wayfinder's earlier choices already place current title, kind, status, summary, and location outside the ID.

**Implication:** after integration, freeze the entire ID token, including its mnemonic. Continue to permit governed edits to document content and metadata. A dated mnemonic is not grounds for changing identity.

### 3. Independent sequential allocation is an optimistic transaction

Kung and Robinson's foundational optimistic-concurrency model separates a transaction into read, validation, and write phases. Work proceeds without locking, but validation decides whether it may safely commit against concurrent work.^3 A branch that scans the record and chooses `max + 1` performs an analogous read; integration validation checks whether the ordinal remains available; merging is the write.

This is an analogy, not a claim that a Markdown repository is a database transaction system. In particular, Git integration can span multiple commits and human review. The model nevertheless exposes the necessary safety point: the allocator's earlier scan is insufficient evidence at integration time.

**Implication:** revalidate against the current declared baseline immediately before integration. A collision blocks integration; it must never be silently accepted or repaired after the conflicting ID has entered canonical history.

### 4. No uncoordinated sequential allocator can guarantee uniqueness

Dillinger and colleagues analyze unique-ID generation without coordination and show why guarantees require either communication or a sufficiently large probabilistic space.^4 Wayfinder deliberately chose a small monotonic ordinal rather than a UUID-like random space. Two branches based on the same maximum can therefore produce the same next number, even when both allocators behave correctly.

**Implication:** either introduce centralized reservation at mint time or allow one unintegrated candidate to change at integration. Declaring every local mint immutable while also promising offline deterministic sequential allocation would be an inconsistent contract.

### 5. Collision handling should be explicit and narrow

Dias, Borba, and Barreto reproduced 73,504 merge scenarios and found that conflict likelihood increased when contributions overlapped a common application slice and as contribution size and duration grew. They describe conflict resolution as costly and error-prone.^5 The study concerns source-code merges in Ruby and Python MVC projects, not metadata IDs, so its numerical results should not be transferred to Wayfinder. It does support treating integration conflicts as a visible review event rather than embedding broad, silent repair behavior in a merge.

**Implication:** the validation failure should name the colliding IDs and documents and stop. A later decision should define one deterministic, minimal re-key operation for the unintegrated candidate only.

### 6. Human-factors evidence does not pick the repository event

The immutability boundary is principally a distributed-coordination and governance choice. The reviewed psychology and learning-science literature does not establish whether local minting or branch integration is the correct event for a project identifier. Claims about memory, cognitive load, or learning would not legitimately resolve this tradeoff.

The human-facing design implication is narrower: distinguish states with plain terms, make the one-way transition visible in diagnostics, and avoid requiring maintainers to remember hidden reservation state. This is a design inference from the operational evidence, not a directly tested learning-science result.

## Options

### Option A: immutable immediately upon local minting

The identifier becomes permanent as soon as the allocator writes it into any working copy.

**Operational contract:**

- Every mint must reserve its ordinal through one authoritative coordinator, or disconnected creators must accept that two permanent IDs can collide.
- A branch must contact the coordinator before creation and record the reservation.
- An abandoned reservation can never be reused if the permanence promise is literal.
- Integration validates the reservation but may not re-key either contributor.

**Benefits:** the strongest local promise; authors can share an ID immediately without qualifying it as provisional; no identity change within a branch.

**Costs:** incompatible with guaranteed uniqueness for offline `max + 1` allocation; adds a service, lock, protected reservation file, or serialized maintainer process; abandoned work permanently consumes sequence values; makes the skill less portable and more operationally demanding.

**Best fit:** a centrally administered record where all writers can reliably reserve IDs before editing.

### Option B: immutable at first canonical integration — recommended

The identifier is a candidate while it exists only in isolated work. It becomes immutable the first time it appears in the declared canonical history.

**Operational contract:**

- Local allocation remains deterministic and offline-capable.
- The skill describes a newly allocated branch ID as a candidate, without adding a mutable metadata field.
- Immediately before integration, validation compares all added IDs with the current integration baseline and with other additions in the contribution.
- A collision blocks integration and triggers the later, narrowly specified re-key workflow.
- Only a candidate may be re-keyed. Once an ID has appeared in canonical history, neither its ordinal nor mnemonic may change.
- An ordinary edit to an integrated document may change content, title, path, kind, status, summary, and updated date under their own rules, but not its ID.

**Benefits:** reconciles offline deterministic allocation with durable shared identity; no central service; establishes an objective one-way boundary; limits re-keying to work that has not yet become authoritative; fits version-controlled review.

**Costs:** branch-local references can change before merge; tools must know the integration baseline; contributors must not publish candidate IDs as permanent; squash, rebases, shallow clones, and non-Git use need an explicit baseline contract; the initial project scaffold becomes permanent only when first integrated.

**Best fit:** repository-owned records developed through branches or other reviewable contributions.

### Option C: IDs remain mutable with aliases and tombstones

Any identifier may later be replaced, provided a permanent alias or tombstone maps the old token to the new one.

**Operational contract:**

- Every rename adds an authoritative alias entry.
- Validators resolve alias chains, reject cycles, and prevent reuse.
- Indexes and links may retain old IDs indefinitely.
- Consumers must load alias data before resolving any reference.

**Benefits:** maximum correction flexibility; collisions and terminology changes can be repaired after integration; old references can continue to resolve.

**Costs:** weakens the simple stable-ID promise; creates permanent resolution state and chain-management rules; increases selective-retrieval context; makes identity history harder to inspect; turns a rare pre-integration collision into universal runtime complexity.

**Best fit:** a registry that must support identifier renaming as a normal operation and can maintain a permanent resolution service.

## Recommendation

Choose **Option B: immutable at first canonical integration**, with these invariants:

1. The same syntax is used for candidate and integrated IDs; lifecycle is external to document metadata.
2. Local allocation does not itself promise global uniqueness or permanence.
3. The declared canonical baseline is the authority for whether an ID is integrated.
4. Integration validation uses the latest available baseline, not only the branch point used during allocation.
5. A duplicate complete token or duplicate ordinal is a hard error.
6. No integrated ID may be rewritten, even to improve a mnemonic or close a numbering gap.
7. Re-keying is permitted only for a candidate and only through the collision/correction workflow still to be designed.
8. If historical ancestry is unavailable, validation reports that immutability was not verified rather than claiming success.
9. The initial scaffold's IDs become immutable when that scaffold first enters the declared canonical history.
10. Replacement of a misidentified integrated knowledge object uses future lineage/supersession rules, not an ID edit.

This boundary is the smallest contract that makes the accepted sequential grammar honest under concurrent branches. It also preserves the user's portability constraint: ordinary work needs version-control inspection and deterministic scripts, not a networked allocation service.

## Deferred details

Accepting Option B would not yet answer:

- How the canonical baseline is declared and detected.
- Which candidate wins when two contributions allocated the same ordinal.
- Whether the losing candidate keeps or regenerates its mnemonic.
- How references inside the losing contribution are rewritten safely.
- How a non-collision correction is authorized before integration.
- How imported pre-existing records establish an initial history boundary.
- How shallow or unavailable history affects validation severity.

These should be handled as narrow follow-on decisions rather than bundled into the immutability rule.

## Next decision

Define collision precedence: which unintegrated candidate retains the ordinal. After precedence is accepted, separately define how the losing candidate receives a new ordinal, what reference surfaces are rewritten, and what verification proves the operation complete.

## Sources

1. DataCite. “[DOI States](https://support.datacite.org/docs/doi-states).” Accessed 2026-09-13.
2. Crossref. “[Updating Your Metadata](https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/updating-your-metadata).” Accessed 2026-09-13.
3. Kung, H. T., and Robinson, J. T. “[On Optimistic Methods for Concurrency Control](https://doi.org/10.1145/319566.319567).” *ACM Transactions on Database Systems* 6(2), 1981, pp. 213–226.
4. Dillinger, P. C., Farach-Colton, M., Tagliavini, G., and Walzer, S. “[Optimal Uncoordinated Unique IDs](https://arxiv.org/abs/2304.07109).” 2023 preprint.
5. Dias, K., Borba, P., and Barreto, M. “[Understanding Predictive Factors for Merge Conflicts](https://doi.org/10.1016/j.infsof.2020.106256).” *Information and Software Technology* 121, 2020, 106256.
