# Initialization research 09: re-key rewrite scope

- **Status:** Accepted
- **Last updated:** 2026-09-13
- **Audience:** Wayfinder maintainers only
- **Research question:** Which occurrences may an automated re-key operation rewrite when assigning a new ID to a losing candidate?
- **Prior decision:** Canonical integration order determines precedence. An integrated occupant keeps its ordinal; a colliding unintegrated candidate must be re-keyed before integration.
- **Decision:** Option A, semantic allowlist with ambiguous-occurrence stop.

## Executive conclusion

Automatically rewrite only occurrences whose role and target are **semantically proven** by Wayfinder's parsers. This always includes the losing document's own `ID` declaration. It may later include typed ID-reference fields and structured reference syntax once those contracts exist. Generated artifacts should be regenerated from their authorities rather than edited. Every untyped occurrence of the old token should be reported as ambiguous and should block automatic application until a person classifies or edits it.

This is Option A below. It treats re-keying as a constrained refactoring with explicit preconditions, not a global string substitution. That distinction matters most when the loser and incumbent minted the same complete token: the bytes alone cannot reveal which document a reference intended to name.

This decision establishes an automation boundary. It does **not** yet specify transaction staging, rollback, crash recovery, dry-run presentation, reference grammar, or whether the losing candidate keeps its mnemonic.

## Why a full token can still be ambiguous

Wayfinder rejects both duplicate ordinals and duplicate full IDs. Two collision shapes are possible:

```text
ordinal-only collision:
  incumbent  wf-0042-product-brief
  candidate  wf-0042-market-brief

exact-token collision:
  incumbent  wf-0042-product-brief
  candidate  wf-0042-product-brief
```

In the first case, an exact occurrence of `wf-0042-market-brief` is unlikely to denote the incumbent because its complete token differs. It might still be quoted as historical data, a test fixture, or an example rather than used as a live reference.

In the second case, an exact occurrence of `wf-0042-product-brief` could target either knowledge object. After the incumbent integrates, a byte-level replacement across the combined record would corrupt valid references to the incumbent along with references intended for the candidate.

The safe question is therefore not merely “does this text equal the old ID?” It is “does a defined Wayfinder construct bind this occurrence to the losing candidate?”

## Definitions

- **Declaration:** the single `ID` value in the losing document's authoritative metadata block.
- **Typed reference:** a value in a Wayfinder field or reference form whose grammar and resolution rules identify it as a document reference.
- **Generated occurrence:** a token in an index, catalog, or other artifact derived entirely from authoritative documents.
- **Untyped occurrence:** the token in prose, a code block, a filename, foreign data, an unsupported file type, or any context whose binding Wayfinder cannot prove.
- **Semantic proof:** deterministic parser evidence that the occurrence is either the losing declaration or a typed reference resolving to the losing document under the applicable candidate view.

“Semantic” here refers to Wayfinder's own explicit grammar. It does not require natural-language understanding or an AI judgment about what prose probably means.

## Evaluation criteria

| Criterion | Meaning for Wayfinder |
| --- | --- |
| Referential safety | No valid reference to the canonical incumbent is redirected. |
| Completeness evidence | Every occurrence of the old token is classified or blocks the operation. |
| Determinism | The same bytes and grammar produce the same rewrite plan. |
| Reviewability | A person can see why each occurrence is editable or ambiguous. |
| Portability | Classification uses the skill's dependency-light parsers, not an IDE or external service. |
| Extensibility | New reference forms can join an explicit allowlist without broadening old behavior silently. |
| Context economy | Runtime agents execute a script and inspect a concise report rather than loading implementation or maintainer research. |

## Evidence synthesis

### 1. Safe refactoring depends on preconditions

Opdyke's foundational work defines refactorings as behavior-preserving transformations when their stated preconditions hold.^1 Mens and Tourwé's survey likewise treats preservation conditions, tooling, and the representation of affected artifacts as central refactoring concerns.^2 Although Wayfinder is transforming knowledge references rather than executable programs, the relevant structure is the same: changing an identifier is safe only if the tool can identify the declaration and every binding it intends to preserve.

**Implication:** specify machine-checkable preconditions before applying a re-key. “The old text appears here” is evidence of an occurrence, not proof of a reference binding.

### 2. Rename research distinguishes binding-aware edits from textual replacement

Schäfer, Ekman, and de Moor show that sound identifier renaming requires adequate name-analysis preconditions; weak preconditions can cause names to bind to the wrong declarations after a rename, while overly strong ones reject valid renames.^3 Wayfinder's grammar will be far simpler than Java's name-resolution rules, but an exact-token collision creates the same essential risk: identical spelling can refer to different entities.

**Implication:** define a small set of reference constructs whose target can be proven. Rewrite those constructs and refuse to guess about everything else.

### 3. Derived artifacts should follow their authorities

Wayfinder has already accepted that generated indexes and catalogs are derivations, never independent authorities. Editing a generated occurrence would create a second transformation path and could preserve stale data that the generator should instead replace.

**Implication:** exclude generated files from direct rewrite. Rebuild them after authoritative metadata and references change, and verify that the old candidate token no longer appears in generated output except where intentionally retained by a future history mechanism.

### 4. Full-text replacement overreaches even with token boundaries

Restricting replacement to the exact byte token avoids substring errors but cannot determine whether an occurrence is a live link, a quoted diagnostic, a migration fixture, or a reference to the incumbent. Restricting the scan to Markdown also does not solve that problem: Markdown contains prose, code spans, fenced examples, HTML, and link destinations in the same file.

**Implication:** token-boundary matching is useful for exhaustive discovery, but discovery results must be classified by the parser before they become edits.

### 5. Manual editing alone gives weak completeness evidence

Manual search can resolve genuinely ambiguous prose, but it is difficult to prove that every occurrence was considered. Refactoring research motivates automation precisely because globally visible names are expensive to change consistently.^3 A report-only workflow also conflicts with Wayfinder's constraint to make repeatable actions deterministic when possible.

**Implication:** let the script own exhaustive enumeration, classification, and safe edits. Reserve human judgment for a bounded list of untyped occurrences.

### 6. Human oversight should receive evidence, not a guessed answer

Parasuraman and Riley distinguish appropriate automation use from misuse, including overreliance that can create monitoring failures and decision bias.^4 Later systematic review evidence associates automation bias with verification complexity, including single-task settings.^5 These studies cover domains much higher-stakes and more complex than documentation refactoring, so their error rates do not transfer to Wayfinder.

Their relevant design implication is modest: when the classifier lacks semantic evidence, label the occurrence ambiguous and show its location and context. Do not present a probabilistic guess as a completed repair. Conversely, do not make a person re-check edits whose bindings the parser can prove.

**Implication:** automation should be decisive inside its proven domain and conspicuously stop at the boundary.

## Options

### Option A: semantic allowlist with ambiguous-occurrence stop — recommended

The script exhaustively finds the old token, classifies every occurrence, automatically plans changes only for semantically proven locations, and refuses to apply while any untyped occurrence remains unresolved.

Initial allowlist:

1. The losing candidate's authoritative `ID` field.
2. Typed reference fields defined by an accepted Wayfinder schema.
3. Structured references whose accepted resolver identifies the losing document.
4. No generated occurrence; regenerate its containing artifact instead.

Everything else is reported with file, line, context class, and reason for ambiguity. The person may edit the occurrence, mark it through a future explicit retention mechanism, or cancel. The script then rescans from bytes rather than trusting a previous acknowledgment.

**Benefits:** protects incumbent references; deterministic within an explicit grammar; exhaustive discovery; easy to extend deliberately; supports safe scripts without pretending to understand prose.

**Costs:** depends on reference grammar not yet designed; may stop often when IDs appear in prose or examples; exact-token collisions can require human classification; the first implementation can automate only the declaration until more semantic surfaces exist.

**Best fit:** durable records where false rewrites are more damaging than a visible stop.

### Option B: replace every exact token in authored record files

Replace the old full ID everywhere inside non-generated UTF-8 project-record files, using token boundaries.

**Benefits:** simple, fast, dependency-free, and usually complete; straightforward to explain; leaves few stale candidate references in ordinary cases.

**Costs:** corrupts incumbent references in an exact-token collision; changes quoted history, examples, and fixtures; assumes all text occurrences have the same binding; “authored file” classification does not supply semantics.

**Best fit:** a closed corpus that prohibits identifier literals except as live references and guarantees the old spelling has one referent. Wayfinder has not established either condition.

### Option C: rewrite only the declaration and report references

Automatically change the losing document's `ID` field. Report every other occurrence for manual repair, even when it is a typed reference.

**Benefits:** very small trusted transformation; cannot accidentally redirect a reference; implementable before reference grammar is complete.

**Costs:** fails to automate references that the system can eventually prove; manual work scales with record size; completeness depends on careful follow-through; underuses deterministic tooling.

**Best fit:** an initial prototype before typed references exist, but unnecessarily restrictive as the record contract matures.

### Option D: report only; all edits are manual

The script identifies the collision and occurrence inventory but changes nothing.

**Benefits:** maximum human control; no automated write risk; simplest implementation.

**Costs:** inconsistent edits are more likely; repetitive and slow; no behavioral guarantee; conflicts with the design goal of deterministic action; every operator must reconstruct the procedure.

**Best fit:** forensic recovery of an already-corrupt or unsupported record, not normal candidate re-keying.

## Recommendation

Choose **Option A: semantic allowlist with an ambiguous-occurrence stop**, with these invariants:

1. Discovery scans the complete declared project-record scope for the exact old token.
2. Every occurrence receives one class: declaration, proven typed reference, generated, or ambiguous.
3. Only the losing declaration and proven references may enter the automatic edit plan.
4. Generated files are regenerated, never patched as authorities.
5. Any ambiguous occurrence prevents automatic application.
6. The report includes file, line, parser context, proposed action, and reason.
7. The script never uses natural-language inference, similarity, authorship, or probability to classify a binding.
8. An exact-token collision receives the same conservative treatment as an ordinal-only collision.
9. After a person resolves ambiguity, the script rescans the current bytes and creates a new plan.
10. Unsupported encodings, binary files, symlinks, unreadable paths, or tokens outside declared scope are reported according to future environment and scope policy rather than silently skipped.

This boundary makes deterministic automation trustworthy: it performs all and only the transformations for which Wayfinder has a machine-readable meaning. It also leaves room for the reference model to increase automation later without weakening the safety rule.

## What acceptance would change now

The runtime skill would gain only the invariant that automatic re-keying is semantic and allowlisted. No re-key script should be implemented yet because the reference grammar, generated-file markers, record-root contract, and transaction safety model remain undecided. Implementing a broad replacement tool now would prematurely define those missing contracts.

## Deferred details

Accepting Option A would not yet answer:

- The syntax and resolution rules for typed document references.
- How generated artifacts identify themselves.
- How a person marks an ambiguous occurrence as intentionally retained.
- Whether the candidate's mnemonic remains frozen during re-keying.
- How the new ordinal is selected against baseline and candidate state.
- How edits are staged, previewed, committed, or rolled back.
- Whether a clean working state or version-control checkpoint is required.
- How final validation proves that every intended binding now resolves correctly.

## Next decision

Define the complete re-key transaction policy: how the replacement token is constructed, which visible state controls ordinal allocation, what preconditions apply, how changes are staged and recovered, when the operation stops, and what postconditions prove success.

## Sources

1. Opdyke, W. F. “[Refactoring Object-Oriented Frameworks](https://hdl.handle.net/2142/72072).” PhD dissertation, University of Illinois at Urbana-Champaign, 1992.
2. Mens, T., and Tourwé, T. “[A Survey of Software Refactoring](https://doi.org/10.1109/TSE.2004.1265817).” *IEEE Transactions on Software Engineering* 30(2), 2004, pp. 126–139.
3. Schäfer, M., Ekman, T., and de Moor, O. “[Sound and Extensible Renaming for Java](https://doi.org/10.1145/1449764.1449787).” *Proceedings of OOPSLA 2008*, pp. 277–294.
4. Parasuraman, R., and Riley, V. “[Humans and Automation: Use, Misuse, Disuse, Abuse](https://doi.org/10.1518/001872097778543886).” *Human Factors* 39(2), 1997, pp. 230–253.
5. Lyell, D., and Coiera, E. “[Automation Bias and Verification Complexity: A Systematic Review](https://doi.org/10.1093/jamia/ocw105).” *Journal of the American Medical Informatics Association* 24(2), 2017, pp. 423–431.
