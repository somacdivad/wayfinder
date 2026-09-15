# Wayfinder maintenance workflow

Use this reference only while changing, testing, certifying, freezing, or preparing activation of Wayfinder itself.

The canonical source-repository entry point is `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py`; abbreviated `maintain.py` commands below refer to that file.

## Plan-to-PR Development

Use [Plan-to-PR Development](../resources/plan-to-pr-development/README.md) for changes to either plugin. Its planning subworkflow establishes shared intent through research-informed interviews, one material question per turn, and saves a decision-complete plan in repository `docs/plans`. Read the phase resources progressively. Discover with `plan list`; use `plan read --id ID --history` for exact scope and immutable approvals, and `plan create/update --input FILE [--dry-run]` for explicit bounded writes. See [plan management](../resources/plan-to-pr-development/plan-management.md) for the hierarchy, template, schema, and concurrency rules.

Approval of the complete plan permits continuous implementation and its named PR delivery actions. Keep behavior, tests, and necessary documentation in coherent PRs; stack only real dependencies using native GitHub stacks. Pause for a material scope/design/authority/criteria change, insufficient authority, or a named checkpoint; an optional experiment or review checkpoint is suggested when it could prevent substantial rework. The plan owns progress, accepted decisions/closure belong in design history, and current state remains the sole current authorization and candidate authority.

After requesting owner reviews on all ready PRs, stop without polling until the owner returns. On return, inspect feedback; explicit approval must identify the reviewed PRs/versions before eligible bottom-up integration under checks, protections, and any planned merge groups. Review completion alone does not permit merging. Native-stack unavailability requires a proposed fallback and decision, without installing or silently substituting tooling.

## Start cleanly

- Read `references/current-state.md` for current status, identities, approval boundaries, pending action, and record IDs. Read the [design-record guide](design-record/README.md), discover metadata with `record list`, and retrieve exact records with `record read --id ID --history`. Before reopening a decision, changing evidence governance, or recording acceptance, read the complete affected history and decisive linked authority/evidence. Expand on conflicts or missing dependencies; unrelated chronology is not a routine prerequisite.
- Resolve interpreter and adapter runtime paths once, export `WAYFINDER_NODE_RUNTIME` and `WAYFINDER_POWERSHELL_RUNTIME` when needed, and reuse them. Record the requested path, resolved path, observed version, and override variable. Do not retry a known-unsupported interpreter or install an unavailable runtime.
- Inspect `maintain.py --help` and selected subcommand help before assembling a command. `maintain.py describe --format json` provides stable machine-readable paths and identities. Reuse help, resolved runtimes, describe output, and unchanged pre-edit hashes within an uninterrupted session; refresh them after compaction, tool reset, checkout change, or a relevant file edit.
- Run `maintain.py doctor --format full` before feature work. A red baseline is maintenance work, not evidence for a new feature. Routine successful calls use summary output; internal preflight is quiet. A named owner-authorized maintainer-only tranche may compare against a recorded unavailable-runtime baseline; never report that runtime check as passed.
- Do not use `py_compile` for syntax-only checks; the canonical doctor compiles sources in memory and creates no bytecode cache.
- Use `maintain.py self-test` for the complete maintainer-owned regression suite. It sets no-bytecode controls, discovers every maintainer `test_*.py` module, and fails if repository bytecode exists before or after the run.
- Use `maintain.py record list --topic TOPIC` and `record read --id ID --history` for bounded history retrieval. Use `record add --input FILE --dry-run` to preview an addition, then the same command without dry-run when authorized. The writer creates new records only and does not update current state. `record-section --heading HEADING` remains a unique-title compatibility alias. Do not combine large ad hoc reads that can truncate and force repetition.
- Do not run the bundled skill-creator `quick_validate.py` as a canonical Wayfinder check. It requires PyYAML, which is not a repository dependency. Do not install PyYAML for this purpose; use `maintain.py doctor` and `scripts/validate_repository.py`. If PyYAML is already available, `quick_validate.py` may be used once as an optional secondary check, and its result does not replace either canonical validator.
- In a separately installed maintainer plugin, set `WAYFINDER_SKILL_ROOT` to an explicit local runtime-skill root. Do not fetch or infer a target checkout.

## Change a candidate

- Preserve accepted decisions and historical evidence.
- Change the normative contract before or with implementation behavior; fixtures cannot create semantics by themselves.
- When governed bytes change after acceptance, advance the candidate revision, rebuild package digests, and generate new evidence. Never relabel older evidence as current.
- If a rule can fail in multiple ways, define diagnostic precedence or test the documented acceptable outcomes instead of following accidental implementation order.
- Add adjacent-slice scenarios whenever one slice consumes another slice's output.

## Verify

Run in this order:

```text
maintain.py doctor --format full
maintain.py self-test
maintain.py test [--adapter ID] [--case ID --case ID]
maintain.py evidence --output DIR
maintain.py freeze-proposal --output DIR
maintain.py freeze-acceptance --output DIR --accept-option-a
```

`test` is read-only outside temporary fixtures and writes no certification evidence. `evidence` requires an explicit destination and refuses to replace an existing report.
`freeze-proposal` requires passing revision-scoped candidate and parity reports, validates their exact package bindings, and exclusively creates a pending proposal pair without recording owner acceptance.
`freeze-acceptance` is permitted only after an explicit owner Option A response. It validates and binds the exact proposal, exclusively creates a new acceptance pair, and does not authorize or begin any later tranche.

Repeat `--case` or `--category` in one `test` invocation rather than launching one process per selection. Summary output is the default; use `--format full` only for per-case detail or `--format json` for stable structured results. A focused adapter run still checks all registered adapter bytes and identities, but its quiet preflight probes only the selected adapter runtime, so an unavailable unrelated runtime does not block it. `--case-file` is intentionally omitted because repeated arguments are sufficient for the current 305-case suite and avoid another input format.

For already-downloaded hosted artifacts, use:

```text
maintain.py matrix-review --artifact-dir DIR [--format summary|full|json]
```

This command performs no network access and no writes. It verifies source/run bindings, exact registered adapters and report hashes, exact 305-case result sets, result-set digests, distinct aggregate invocation-digest metadata, and coverage summaries. It labels Actions artifacts review-only and never publishes, promotes, or replaces accepted evidence.

For a separately authorized adapter-parity tranche, select each registered
adapter through `maintain.py test --adapter ID`, then run
`maintain.py parity --output DIR`. The parity command runs the complete suite
for all three version-1 adapters and refuses to publish its local comparison
report unless per-adapter results and normalized black-box observations agree.
It does not create an environment-certification entry or a full-family claim.

Use `maintain.py expect --exit N --code CODE -- COMMAND...` for a negative demonstration. The wrapper succeeds only when the command returns the expected exit and result code.

Bound parallel file reads by line range and output budget. Once a check passes, repeat or broaden it only after changed inputs, increased scope, or a failure that creates a new risk. Run one full `maintain.py doctor --format full` after the final changed input.

## Bounded reads and public projections

Read in stages: current state and tranche, inventory/size metadata, headings or projected fields, one exact source section, then adjacent material only when needed. `describe/context` is a discovery preview and supplies a curated routing catalog rather than source bodies. Repeat `--field` for projection; use an allowlisted `--sort` for stable ordering.

Potentially large interactive commands use `--format summary|json|full` and `--max-bytes`. Partial-capable `describe/context`, `record list/read`, and `record-section` also expose `--response-class discovery-preview|complete-evidence`; checks, status, additions, and checkpoints always declare complete evidence for their named result scope. A preview explicitly reports incomplete and is safe only for routing. A complete response is complete for its named scope; an unmet completeness request returns nonzero and an actionable recovery command. Byte budgets apply to UTF-8 payload bytes, excluding the fixed envelope, and must be at least four bytes. Record reads bound source text chunks; listings bound their serialized item array. JSON payload schemas are nested under the common `wayfinder-maintainer-response` version-1 envelope. Artifact and adapter schemas are unchanged.

`record read` and its `record-section` alias default to complete evidence and full exact text. JSON chunks carry record ID, store/source hashes, byte range, chunk index/count, and digest-bound cursor. History reads include later predecessor-linked outcomes and outgoing authority/source record links. `complete` on a cursor sequence means the sequence is exhausted, not that the final chunk alone contains the source. Collect every chunk in order, verify contiguous ranges and chunk count, concatenate `data.text` as UTF-8, and compare SHA-256 with `sourceSha256`. History members are exact file bytes separated by one extra LF. The cursor binds command, selector, history flag, response class, store/source hashes, offset, and byte budget. Changed stores, invalid offsets, or changed budgets fail closed. See the guide for inventory pagination and digest reconstruction.

On truncation: classify the failure, mark conclusions depending on unseen output unproven, do not repeat the same broad request, and use a narrower projection/range or the supplied cursor. Stop before authorization, mutation, certification, publication, promotion, or activation unless every decisive source is complete. Initial budgets are 16 KiB for previews and 64 KiB for complete responses; calibrate against representative traces rather than treating them as universal limits.

`current-state.md` contains the sole canonical mutable status object. `status --format full` previews exact public-region/field changes; `status --write` is explicit, bounded, and mutating. Both doctor and repository validation cross-check the authority against frozen release and accepted evidence, then reject public drift. Neither validator repairs it automatically. Runtime metadata exposes activation state; installation is not activation.

## Ephemeral checkpoints

Use `checkpoint create --input FILE|- [--output PATH]` before compaction or a new-session handoff. Required input fields are `objective`, `tranche`, `exclusions`, `sources`, `validations`, `mutations`, `failures`, `unresolved`, `nextSafeAction`, and `cursor`. Repository sources name `path` and exact `scope`; external sources name `locator`, `scope`, and caller-supplied `sha256` and are never fetched. Validation entries should record exact command, exit code, result, and input provenance. Do not include secrets, bodies, diffs, or environment credentials.

The command adds current-state hash, source hashes, HEAD, and an aggregate worktree fingerprint over staged/unstaged diffs and sorted untracked path/content digests. It stores aggregate counts, not untracked names. File output is exclusive and outside the repository; stdout is the default. Checkpoints are derived, non-authoritative, never auto-committed or promoted to evidence, and never replace governed reads.

Before reuse, run `checkpoint verify --checkpoint PATH`. Changed HEAD, worktree, current-state hash, or repository source hash makes the checkpoint stale. Verification never refreshes it or reruns old validations; refresh sources and rerun affected checks explicitly.

## External-action authorization gate

Before authentication, artifact download, hosted dispatch, publication, destructive work, or another consequential external action, record internally:

1. The exact action and target.
2. Whether it is read-only or mutating.
3. The active tranche language that authorizes it.
4. Any explicit exclusion that applies.
5. Whether it introduces authentication or persistent permissions.
6. The least-powerful applicable tool.

If authorization is absent or an exclusion applies, stop that action. Do not route around the boundary merely to obtain diagnostic detail. After a failed call, classify it as interface, sandbox/network, authentication, authorization, external-state, truncation, incomplete-discovery, or side-effect contamination before selecting a materially different next action. After reset, compaction, or an interface error, refresh current tool documentation and state.

## Hosted failure review

Use this escalation ladder only in a separately authorized hosted-review tranche:

1. Read public run metadata and the exact run attempt.
2. Prefer `gh run view RUN_ID --attempt ATTEMPT --log-failed` for bounded failure logs.
3. Download artifacts only when the active tranche explicitly authorizes the download and existing authentication is already sufficient. Use the exact run ID, exact artifact name, and a new temporary destination.
4. Verify the Actions artifact digest and the internal Wayfinder report bindings before review.
5. Run `maintain.py matrix-review --artifact-dir DIR` offline.

Do not begin an OAuth flow merely because public or existing-auth inspection is insufficient. Stop and report the authentication boundary first. Browser automation is a read-only metadata fallback, not the primary artifact transport. Matrix-entry logs and `$GITHUB_STEP_SUMMARY` expose bounded failing case IDs and diagnostics; consult those before considering an artifact download.

## Handoff and approval

Generate factual handoff scaffolding with:

```text
maintain.py handoff --kind implementation --objective "Bounded objective" --exclude "Deferred action" [--plan-id ID]
```

Kinds are `investigation`, `implementation`, `hosted-review`, and `acceptance-record`. The generator derives the current release identity, digests, case counts, and mode-specific safeguards. Add only slice-specific design context that cannot be derived. Investigation scaffolding never recommends evidence, freeze, publication, activation, or governed-byte mutation without separate objective authority.

The [approval-response protocol](approval-response.md) is mandatory before asking for acceptance, authorization, or approval and when processing the response. Before approval, report the exact changed surface, observable behavior, verification, unavailable evidence, what acceptance would authorize, what remains excluded, and the next bounded activity. Approval never begins another project or an unapproved tranche automatically. `--plan-id` routes an existing approved current-state plan and its phase safeguards; it does not grant authority or bypass doctor. Omit it for the legacy bounded new-session mode.

After an explicit affirmative, record the outcome when required using `record add` and explicitly update current-state routing in the same authorized record task, including terminal closure. Plan approval also preserves its exact snapshot using `plan update`; within the approved plan, continue only its named activity. Outside it, provide the detailed copy-ready prompt for the next bounded task in a new session and stop. Persistence of an existing decision does not require another acceptance of that decision; a new closure PR still needs its own reviewed-version approval. After a rejection or material revision request, leave the checkpoint pending and use the facilitated rejection interview, one material question per turn, until the reason, correction, evidence, and acceptance criteria are understood. Conditional and ambiguous responses remain subject to the canonical fail-closed classifications.

Stop before any action outside the explicit tranche, before overwriting or promoting evidence, when a required selected runtime remains unavailable after one resolution attempt, or after delivering the requested approval packet. Hosted reruns, evidence publication, candidate reopening, activation, live-project work, commits, and pushes each require their own authorization when the current state says they are closed.
