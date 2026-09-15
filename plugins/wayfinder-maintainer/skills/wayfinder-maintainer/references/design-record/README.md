# Maintainer design records

This store owns maintainer decision history, not runtime project records. [Current state](../current-state.md) alone owns current candidate, evidence, activation, and authorization. Historical outcome metadata does not grant current permission. The [legacy entrypoint](../design-record.md) retains old heading anchors without duplicating the chronology.

## Discover and read

Run the canonical `scripts/maintain.py` with Python 3.11 or newer; examples below abbreviate that path.

```text
maintain.py record list
maintain.py record list --topic initialize --format json
maintain.py record read --id wr-0031 --history --format json
maintain.py record read --id wr-0028 --format full
maintain.py record-section --heading 'Candidate revision 10 hosted certification execution — accepted'
```

Folders are [foundation](foundation/README.md), [Initialize](initialize/README.md), [governance](governance/README.md), and [distribution](distribution/README.md). Initialize uses `policy/` or `candidate-revision-N/`. Stable global `wr-NNNN` IDs do not encode topic, title, date, or outcome. The ordinal is the chronological ordering key; migrated undated history retains a null date. Listings are generated directly from record metadata, not an independently edited catalog.

`record list` is a metadata-only discovery preview by default. `record read` returns exact record bytes and defaults to complete evidence. All read modes support `--format summary|json|full`, `--response-class discovery-preview|complete-evidence`, `--max-bytes`, and `--cursor`. Read formats always retain exact source text, including visible metadata; summary does not replace authority with a paraphrase. List budgets bound the serialized item array; read budgets bound UTF-8 source chunks, excluding fixed envelope and per-chunk routing metadata. Defaults are 16 KiB for discovery and 64 KiB for complete evidence. An item that cannot fit requires a larger budget; it is never silently omitted.

Complete responses spanning pages/chunks return exit 2 until the sequence is exhausted. Follow the exact `next-command`, retaining the selector, class, and byte budget. In JSON, `sequenceExhausted` describes continuation; `complete` on the last chunk does not mean that chunk alone is the whole source. Concatenate all `data.text` bytes in order, verify contiguous byte ranges and chunk count, and compare SHA-256 against `sourceSha256`. History members are exact record files separated by one additional LF; `data.records` identifies only members intersecting this chunk. Inventory pages expose item ranges and a digest of the complete serialized inventory. Concatenate their items in order and hash the canonical JSON array to verify the inventory. Any store change invalidates cursors. Pre-migration `record-section` cursors are stale; restart by record ID.

`--history` follows predecessor links both backward and forward, so later corrections, rejection, and closure are visible. It also follows outgoing `record:ID` sources and authority locators. It does not follow inbound citations as if every citing record were the same decision. Missing, self, and forward references fail validation. If dependencies are unrecorded or conflicting, discover and read additional relevant records before concluding.

Before reopening a decision, changing evidence governance, or recording an accepted outcome, read current state, this guide, the complete affected history, and every decisive linked authority/evidence source. Expand on conflicts or missing dependencies. Discovery listings and summaries never replace these reads. The migration itself required one complete bounded read of the original chronology; routine additions no longer require unrelated history.

## Add a record

```text
maintain.py record add --input /private/tmp/record.json --dry-run --format json
maintain.py record add --input /private/tmp/record.json --format json
```

Supply exactly these JSON fields; unknown or duplicate members fail. `candidateRevision` is null outside Initialize, and null selects Initialize policy. Dates are explicit `YYYY-MM-DD`. Titles and summaries are single-line, at most 200 and 500 characters. Body is substantive Markdown without the generated title or metadata block.

```json
{
  "topic": "governance",
  "candidateRevision": null,
  "title": "Example maintainer proposal",
  "kind": "proposal",
  "outcome": "pending",
  "date": "2026-09-15",
  "summary": "A proposal awaiting an explicit owner decision.",
  "body": "Describe the problem, proposed behavior, boundaries, rationale, and acceptance criteria here.",
  "predecessors": ["wr-0031"],
  "authorities": [],
  "sources": ["record:wr-0026"]
}
```

| Kind | New-record outcomes |
| --- | --- |
| `context` | `recorded` |
| `proposal` | `pending` |
| `decision` | `pending`, `accepted`, `rejected`, `changes-requested` |
| `verification` | `passed`, `failed`, `recorded` |
| `closure` | `accepted` |

An accepted/rejected decision or accepted closure requires at least one authority object with exactly `locator` and `quotation`, supplied from the explicit owner decision. A locator can identify a task, source file, or `record:wr-NNNN`. Sources are nonempty locator strings; only `record:` locators are traversed automatically, and external sources are never fetched. The caller must read and substantiate other locators. CLI validation does not authenticate quotation provenance or owner approval and cannot infer permissions from an outcome.

Corrections and lifecycle changes create new records referencing their predecessor. Existing records are never overwritten by the CLI. Dry-run shows exact prospective content, ID, path, and digest without managed writes; the ID is prospective and may change after another addition. Add serializes cooperating writers with an exclusive `.record-add.lock`, stages a complete `.pending-*` file, and publishes by an exclusive same-filesystem hard link. It has no overwrite or partial-copy fallback. The command leaves current state unchanged and performs no Git or network action.

An interrupted writer may leave a lock or pending staging file. Subsequent additions and doctor fail closed; inspect the lock's host/PID, writer status, staging contents, and any completed record before explicitly authorized manual cleanup. Never steal a lock or delete a completed record to retry. Readers may inspect complete published records while a writer lock exists. A failed invocation cleans up only staging/lock artifacts it owns; a published record is retained.

## Durable decisions and closure

Follow [approval-response.md](../approval-response.md) for approval interpretation and stopping rules. When an accepted outcome or closure requires persistence, use `record add` and explicitly update current-state routing in the same authorized record task. A conversation-only terminal handoff must not leave routing claiming that the same closure is pending. Do not create another acceptance loop for the persistence of an already accepted decision. Git publication remains separately authorized.

The 31 migrated sections are bound by `migration.json` and its pinned digest in the record-store module. Validation reconstructs the original file from migrated bodies, reverses only enumerated relative-link adjustments, and verifies original section and whole-file hashes. Historical summaries and superseded guidance remain historical context. Reopening accepted history requires explicit owner authority; ordinary additions cannot redefine migration provenance.

## Research basis

[Bounded-context research](../research/2026-09-14-bounded-context-and-tool-output-management.md) supports selective retrieval, progressive disclosure, exact source chunks, and explicit completeness. [Traceability research recommendations](../research/2026-09-14-broader-wayfinder-opportunities-addendum.md#opportunity-9--deepen-traceability-and-change-impact-analysis) support a small generated index and useful dependency links rather than a manually maintained all-to-all map. The exact folder and CLI choices are Wayfinder design decisions, not thresholds established by those studies.
