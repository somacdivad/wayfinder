# Initialization research 10: collision re-key transaction

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** What complete transaction should safely re-key a losing candidate after an identifier collision?
- **Prior decisions:** Canonical integration order determines precedence. Automated edits are limited to semantically proven declarations and references; generated artifacts are rebuilt; ambiguous occurrences block application.
- **Decision:** Option A, portable staged transaction.

## Executive conclusion

Use a **portable staged transaction with explicit preconditions and recovery**. The operation preserves the candidate's mnemonic, chooses one greater than the maximum ordinal visible in the union of the latest local canonical baseline and candidate view, builds and validates transformed copies before touching live files, verifies that its inputs have not changed, applies from a recovery journal, validates the live result, and rolls back on failure. It never integrates, commits, fetches, or retries automatically.

This is Option A below. It is broader than the preceding decisions because token construction, allocation visibility, staging, recovery, and verification jointly determine whether the re-key can make an honest all-or-nothing safety claim. Splitting them would repeatedly revisit the same failure boundaries.

The accepted semantic rewrite allowlist remains fixed. This decision chooses how to carry out those already-authorized edits, not which text the script may reinterpret.

## Target outcome

Given:

```text
canonical incumbent: wf-0042-product-brief
losing candidate:    wf-0042-market-brief
maximum visible ID:  wf-0067-architecture-map
```

the recommended transaction proposes:

```text
wf-0042-market-brief -> wf-0068-market-brief
```

It changes the losing declaration and every semantically proven reference, regenerates derived views, and proves that:

- the canonical incumbent is unchanged;
- ordinal `0068` is unique in the validated combined view;
- the candidate's mnemonic is unchanged;
- every old-token occurrence is classified;
- every intended reference resolves after transformation;
- no live file retains a partial transformation if validation fails.

## Policy components

### Replacement token

Preserve the existing mnemonic byte-for-byte and replace only the ordinal. A collision proves that the ordinal is unavailable; it says nothing about the document's topic. If the mnemonic is malformed under the current grammar, stop and route to future corruption or migration handling rather than combining semantic repair with collision recovery.

### Allocation visibility

Let the visible set be the union of:

1. every durable document in the declared canonical baseline available locally; and
2. every durable document in the candidate view being transformed.

Choose `max(visible ordinals) + 1`. This prevents the replacement from colliding with another new document in the same candidate contribution. Pending contributions that are not locally visible cannot be considered without adding a coordinator; canonical-order validation handles them later.

### Transaction boundary

The transaction starts only after preflight records immutable input digests and ends when live post-validation succeeds or all touched live files have been restored. A preview is not a transaction and creates no reservation.

### Retry boundary

If the canonical baseline, candidate inputs, or visible maximum changes after planning, abort. Do not silently choose another number and do not loop. The operator reruns the command against fresh state. This keeps each plan reviewable and prevents cascading edits from an unstable baseline.

## Evidence synthesis

### 1. Transaction safety means more than “the script usually finishes”

Gray describes a transaction as a state transformation with atomicity, durability, and consistency: all-or-nothing effects, survival of completed effects, and preservation of valid state.^1 Wayfinder is not a database and cannot cheaply reproduce database isolation or crash guarantees across arbitrary filesystems. The model nevertheless supplies the right questions: what is the pre-state, what invariants define a correct post-state, and how is an interrupted update recovered?

**Implication:** document an explicit transaction boundary, validate before and after mutation, and retain enough recovery information to restore the exact pre-state.

### 2. Recovery information must exist before destructive writes

ARIES formalizes write-ahead logging and uses logged information to support recovery and rollback after failures.^2 A documentation script does not need ARIES's database machinery, but copying live bytes only after an error would be too late.

**Implication:** create and durably record a recovery journal containing original bytes or verified backup paths before replacing the first live file. If a prior journal indicates an interrupted operation, the next invocation must enter recovery mode instead of starting a new re-key.

### 3. Single-file replacement is not a multi-file transaction

POSIX requires `rename()` to be atomic for one filesystem rename.^3 That permits safe replacement of an individual file through a same-directory temporary file on conforming systems. It does not make a sequence of ten replacements atomic as a group, and equivalent behavior varies across platforms and filesystems.

**Implication:** use the best available atomic single-file replacement primitive detected for the environment, but never claim that it supplies group atomicity. The journal plus rollback protocol supplies the cross-file recovery story. The later environment decision must define platform-specific adapters.

### 4. Preconditions and postconditions make the refactoring checkable

Refactoring research treats behavior preservation as dependent on checked preconditions, postconditions, and invariants.^4,5 Re-keying likewise needs more than a syntactically correct new token. It must preserve bindings, leave the incumbent untouched, and restore generated views from their authorities.

**Implication:** the script must refuse unsafe starting states, build a complete plan, validate a staged representation, verify unchanged inputs before apply, and run the same full validator on the live result.

### 5. Preserve the mnemonic during mechanical collision repair

Feitelson and colleagues found substantial variation in names chosen by 334 participants across programming scenarios, even when selected names were generally understandable.^6 The population and task differ from document IDs, but the finding illustrates that naming is a semantic choice rather than a neutral by-product. Regenerating from an H1 would introduce an unrelated naming decision and may fail for non-ASCII titles.

**Implication:** copy the existing mnemonic without normalization, translation, or regeneration. A separate pre-integration correction workflow may later govern actual mnemonic defects.

### 6. Preview should reduce verification work, not transfer it wholesale

Human-automation research warns that overreliance can produce monitoring failures, while high verification complexity increases automation-bias risk.^7,8 A raw whole-repository diff can be technically complete while remaining difficult to verify.

**Implication:** produce both a machine manifest and a concise human preview grouped by action: declaration change, proven reference rewrites, regenerated files, and blockers. Show exact paths and old/new tokens. Do not ask the operator to rediscover which edits are safe.

## Recommended preconditions

The staged transaction may plan only when all of the following hold:

1. The project-record root and canonical baseline are explicitly known.
2. The baseline revision resolves locally; the script performs no implicit network fetch.
3. The losing document exists exactly once in the candidate view and is proven unintegrated.
4. The canonical incumbent and collision type are identified.
5. Both baseline and candidate views pass every validator unrelated to the known collision.
6. The old ID parses under the accepted grammar and its mnemonic is valid.
7. All old-token occurrences are classified under the accepted semantic allowlist.
8. No unsupported binary, encoding, symlink, unreadable path, or out-of-scope occurrence could hide a required rewrite.
9. The project-record working state is checkpointed: clean under supported version control, or protected by an explicit verified snapshot in a future non-VCS adapter.
10. No unresolved recovery journal exists.

These are conservative on purpose. A future implementation can relax a precondition only when it supplies equivalent evidence.

## Recommended transaction phases

### Phase 1: inspect

- Resolve the declared project root, candidate view, and local canonical baseline.
- Confirm canonical precedence and candidate status.
- Run structural validation, tolerating only the diagnosed candidate collision.
- Scan the union view and compute `new ordinal = maximum + 1`.
- Construct the new token by preserving the mnemonic.
- Classify every old-token occurrence.

Any ambiguity stops here without writing.

### Phase 2: plan and stage

- Create a manifest containing the baseline revision, old and new IDs, source-file digests, planned semantic edits, derived artifacts to regenerate, and expected postconditions.
- Materialize transformed copies in an environment-appropriate temporary location outside the live project record.
- Regenerate derived artifacts against the staged authorities.
- Run full validation on the staged representation.
- Present a concise dry-run summary and make the complete manifest available for inspection.

Planning does not reserve the new ordinal.

### Phase 3: compare and apply

- Re-resolve the canonical baseline and compare it with the planned revision.
- Recompute source digests and visible maximum.
- Abort if any input or allocation fact changed.
- Write the recovery journal before the first live replacement.
- Replace changed files using the strongest supported single-file primitive.
- Track each completed replacement in the journal.

The script does not commit, merge, push, fetch, or modify files outside the declared record.

### Phase 4: verify or recover

- Run full live validation and compare required postconditions with the manifest.
- On success, remove temporary transformed copies and close the journal while retaining a concise operation report according to future audit policy.
- On any failure, restore every touched file from the journal, verify restoration digests, and return a nonzero result.
- If the process is interrupted, the next invocation detects the journal and offers only deterministic recovery or evidence-backed completion, not a new operation.

### Phase 5: integration check

- Revalidate against the current canonical baseline immediately before integration.
- If another contribution has since claimed the new ordinal, stop and plan a new transaction.
- Never auto-retry because every retry changes the reviewed token and rewrite plan.

## Options

### Option A: portable staged transaction — recommended

Use the five phases above. Preserve the mnemonic, allocate from the union of baseline and candidate state, stage and validate copies, journal original bytes, apply with per-file safe replacement, validate live state, and recover on failure.

**Benefits:** strongest platform-neutral safety story; detects stale plans; does not depend on Git for the transformation model; supports deterministic recovery; keeps network and integration side effects out of the script.

**Costs:** most implementation work; temporary space proportional to changed artifacts; true simultaneous multi-file atomicity is impossible on ordinary filesystems; adapters must define replacement and durable-journal behavior; conservative preconditions may block unusual repositories.

**Best fit:** a reusable skill intended to operate across repositories and eventually support more than one environment.

### Option B: Git-native checkpoint workflow

Require a clean Git worktree, apply semantic edits directly, validate, and rely on a dedicated Git commit or restoration from the known pre-operation commit for recovery.

**Benefits:** substantially less custom recovery code; Git already records history and diffs; easy review in software repositories; no separate snapshot adapter for the common case.

**Costs:** excludes non-Git records; a commit is an external workflow decision the script should not silently make; direct writes can remain partial before a commit; recovery commands can overwrite unrelated changes unless cleanliness is enforced perfectly; Git history does not replace staged pre-validation.

**Best fit:** an explicitly Git-only skill whose users accept a required checkpoint commit around every re-key.

### Option C: direct best-effort editing

Compute the token, show a preview, edit live files in sequence, regenerate indexes, validate afterward, and rely on the operator's version-control tools if something fails.

**Benefits:** smallest script; fastest normal path; few temporary artifacts; easy to prototype.

**Costs:** interruption can leave partial state; rollback is environment- and operator-dependent; stale inputs can invalidate the plan; recovery is not deterministic; encourages scripts to assume authorization for version-control restoration.

**Best fit:** disposable or trivially reconstructable records, not a canonical knowledge base.

## Recommendation

Choose **Option A: portable staged transaction**, with these binding policies:

1. Preserve the mnemonic; reallocate only the ordinal.
2. Allocate `max + 1` across the union of the local canonical baseline and candidate view.
3. Ignore invisible pending candidates; handle later races through canonical precedence.
4. Require a clean checkpoint or verified snapshot before planning.
5. Perform no implicit fetch, commit, merge, push, or integration.
6. Stage and fully validate transformed copies before live mutation.
7. Recheck the baseline revision, source digests, and visible maximum immediately before apply.
8. Journal recovery data before the first replacement.
9. Validate the live result; restore exact pre-state bytes if it fails.
10. Never auto-retry after stale state or a new collision; produce a fresh plan.
11. Treat an interrupted journal as a recovery task that blocks new mutations.
12. Emit a concise report distinguishing verified edits, regenerated artifacts, blockers, and postconditions.

This package is deliberately conservative because re-keying touches identity and potentially many references. The normal path remains script-driven; the human reviews one compact plan rather than executing a bespoke repair.

## What acceptance would change now

The skill would record the complete transaction contract. Implementation should still wait for the record-root contract, typed reference grammar, generated-artifact markers, validation interface, and environment-adapter decision. Those are inputs the transaction must call rather than invent.

## Deferred decisions

Accepting Option A would not yet answer:

- The concrete project-root manifest and canonical-baseline declaration.
- Typed reference syntax and resolution.
- Generated-artifact markers and generator interface.
- The validator's machine-readable result format.
- The portable runtime/adapters selected during environment detection.
- The audit report's durable location and retention.
- Whether an unintegrated mnemonic can be corrected outside collision repair.

These are meaningful contracts shared with initialization, validation, update, and use workflows; they should be decided at that broader level rather than as private details of re-keying.

## Next decision

Return to the initialization structure and define the project-record root manifest as one coherent contract: root discovery, canonical-baseline declaration, enabled capability modules, generated-artifact policy, and schema version.

## Sources

1. Gray, J. “[The Transaction Concept: Virtues and Limitations](https://www.cs.utexas.edu/~dahlin/Classes/GradOS/papers/Gray81.pdf).” *Proceedings of the 7th International Conference on Very Large Data Bases*, 1981, pp. 144–154.
2. Mohan, C., Haderle, D., Lindsay, B. G., Pirahesh, H., and Schwarz, P. M. “[ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging](https://doi.org/10.1145/128765.128770).” *ACM Transactions on Database Systems* 17(1), 1992, pp. 94–162.
3. The Open Group. “[POSIX.1-2024 `rename()` and `renameat()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html).” Accessed 2026-09-13.
4. Opdyke, W. F. “[Refactoring Object-Oriented Frameworks](https://hdl.handle.net/2142/72072).” PhD dissertation, University of Illinois at Urbana-Champaign, 1992.
5. Mens, T., and Tourwé, T. “[A Survey of Software Refactoring](https://doi.org/10.1109/TSE.2004.1265817).” *IEEE Transactions on Software Engineering* 30(2), 2004, pp. 126–139.
6. Feitelson, D. G., Mizrahi, A., Noy, N., Ben Shabat, A., Eliyahu, O., and Sheffer, R. “[How Developers Choose Names](https://doi.org/10.1109/TSE.2020.2976920).” *IEEE Transactions on Software Engineering* 48(5), 2022, pp. 1683–1697.
7. Parasuraman, R., and Riley, V. “[Humans and Automation: Use, Misuse, Disuse, Abuse](https://doi.org/10.1518/001872097778543886).” *Human Factors* 39(2), 1997, pp. 230–253.
8. Lyell, D., and Coiera, E. “[Automation Bias and Verification Complexity: A Systematic Review](https://doi.org/10.1093/jamia/ocw105).” *Journal of the American Medical Informatics Association* 24(2), 2017, pp. 423–431.
