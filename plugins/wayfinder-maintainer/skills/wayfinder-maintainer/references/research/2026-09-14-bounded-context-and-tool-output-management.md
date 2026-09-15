# Bounded context and tool-output management for Wayfinder maintenance

- **Status:** Research complete; project changes proposed, not authorized or implemented
- **Last updated:** 2026-09-14
- **Audience:** Wayfinder owner and maintainers
- **Research question:** How should Wayfinder maintenance prevent broad reads and tool outputs from truncating, displacing authoritative context, causing repeated work, or weakening authorization and evidence safeguards?
- **Triggering observation:** A session audit found that broad multi-file reads and large tool responses repeatedly truncated, forcing narrower retries and increasing context cost. No unauthorized mutation occurred, but the interaction pattern was inefficient and could become a correctness risk when a truncated response is mistaken for a complete result.
- **Scope:** Local maintainer instructions, read routing, command-output contracts, truncation behavior, long-session checkpoints, evaluation, and audit telemetry.
- **Out of scope:** Changing the frozen semantic contract, registered adapters, accepted evidence, activation state, hosted evidence, workflow publication, network services, hooks, MCP servers, or dependencies.

## Executive conclusion

Treat context as a **scarce reliability budget**, not merely a large capacity limit. The strongest available evidence supports a layered design:

1. load a small authoritative state and routing surface first;
2. retrieve exact source material just in time;
3. filter, project, sort, and paginate before output enters model context;
4. label every bounded response so completeness is machine-discernible;
5. fail closed when an incomplete response could affect an authorization, mutation, certification, or evidence conclusion;
6. compact long sessions into structured, provenance-bearing checkpoints while retaining governed sources outside the checkpoint; and
7. evaluate end-to-end correctness and recovery under injected truncation, not token reduction in isolation.

This direction extends Wayfinder's accepted revision-8 progressive-disclosure work and revision-9 reliability gates. It does not justify replacing authoritative source reads with lossy summaries. Learned prompt compression is promising for discovery and non-governed background material, but current evidence does not establish it as safe for authorization boundaries, frozen bytes, accepted evidence, or exact certification conclusions.

## Evidence review

### 1. Long context is not equivalent to reliable context use

Liu et al. varied both context length and the position of relevant information. Across the tested models, performance was commonly strongest when relevant information occurred near the beginning or end and degraded when it appeared in the middle. Their open-domain QA case study also shows that adding retrieved documents creates a task-specific tradeoff: additional information can help, but it can also reduce accuracy by increasing what the model must reason over.[^liu]

RULER broadens the warning beyond simple needle retrieval. Hsieh et al. evaluate retrieval, multi-hop tracing, aggregation, and question answering, finding that models which appear strong on simple retrieval can degrade substantially as sequence length and task complexity increase.[^ruler] These studies do not test Wayfinder maintenance directly, but they strongly reject the assumption that a response is safe merely because it fits within a nominal context window.

**Wayfinder implication:** keep scope, exclusions, current authoritative state, and the immediate decision near the active reasoning surface. Do not concatenate whole design histories, full inventories, and large command output merely because the model can technically accept them.

### 2. Selective retrieval is better grounded than exhaustive loading

Retrieval-augmented generation established that externally stored evidence can be retrieved at inference time instead of being carried entirely in model parameters or prompt context.[^rag] ReAct showed the value of interleaving reasoning with actions that gather additional information, allowing plans to be updated from environmental observations.[^react] These papers address knowledge-intensive NLP and interactive tasks rather than repository governance, so they support the retrieval loop, not a specific Wayfinder command design.

Information-foraging theory offers a complementary, human-computer-interaction model: users follow cues or “information scent” and adapt navigation to maximize valuable information gained per unit cost.[^pirolli-card] Progressive disclosure applies that principle operationally by showing the most important material first and deferring specialized detail until requested; Nielsen reports benefits for learnability, efficiency, and error rate when the primary/secondary split matches the task.[^nielsen]

Anthropic's current context-engineering guidance independently recommends just-in-time retrieval using lightweight identifiers such as file paths and links, with progressive disclosure and structured note-taking for longer work.[^anthropic-context] This is practitioner guidance, not peer-reviewed evidence, but it directly covers contemporary coding agents.

**Wayfinder implication:** retain `current-state.md` as the compact authority and route from headings, paths, byte counts, identifiers, and exact design-record sections. Discovery output should tell the maintainer what to read next; it should not silently substitute for the source.

### 3. The tool interface materially shapes agent performance

SWE-agent reports that a purpose-built agent-computer interface improved automated repository work, supporting the broader claim that tools should expose actions and observations in forms suited to an agent rather than merely wrapping a human interface.[^swe-agent]

Anthropic's tool-design report is unusually specific to the failure observed here. It recommends returning only high-signal context and using pagination, range selection, filtering, truncation, and sensible defaults for potentially large responses. It also recommends actionable truncation and error messages that steer an agent toward narrower searches, and measuring accuracy, runtime, tool calls, token consumption, and errors.[^anthropic-tools] These are vendor observations and should be validated locally, but they closely match the audited failure mode.

The community-maintained Command Line Interface Guidelines reinforce compatible conventions: say just enough, keep primary machine-readable output on standard output, diagnostics on standard error, use meaningful exit codes, provide concise help by default, and make commands composable.[^cli-guidelines]

**Wayfinder implication:** maintainer commands should make response completeness and the next narrowing action explicit. Human prose and automation output should be distinct modes with consistent exit semantics.

### 4. Compression helps, but lossiness must follow authority boundaries

LLMLingua and LongLLMLingua report large reductions in prompt size and improvements on several long-context tasks. LongLLMLingua reports roughly fourfold token compression in one NaturalQuestions setting with improved performance and substantial cost or latency reductions in evaluated tasks.[^llmlingua][^longllmlingua] The results show that irrelevant or poorly ordered context can harm performance and that selective compression can help.

They do **not** establish that learned token deletion preserves exact legal, authorization, digest, or evidence semantics. The methods are probabilistic and evaluated primarily on QA, summarization, and long-context benchmarks. A governed phrase such as “excluding publication” or one hexadecimal digit in a digest may be low-probability linguistically but decisive operationally.

**Wayfinder implication:** use deterministic structural compression first—exact sections, field projection, deduplication, stable ordering, and bounded chunks. Permit learned summarization only as a labeled derivative for discovery or resumption, never as the sole source for consequential conclusions.

### 5. Long sessions need externalized, structured state

MemGPT demonstrates an OS-inspired hierarchy that moves information between limited active context and external memory.[^memgpt] Anthropic's context-engineering and long-running-agent reports recommend compaction, structured notes, incremental progress, and explicit artifacts that allow a later context to resume work.[^anthropic-context][^anthropic-harness] These systems provide relevant design patterns, but their summaries can omit details and their results do not prove governance-grade fidelity.

**Wayfinder implication:** a checkpoint should preserve compact operational state—scope and exclusions, authoritative source hashes, completed checks, classified failures, mutations made, unresolved questions, and the exact next safe action. It should point back to sources instead of copying or paraphrasing governed content as authority.

### 6. Evaluation must cover trajectories and failure recovery

Agent behavior is multi-turn: a tool response changes the next query, action, or conclusion. Anthropic's agent-evaluation guidance recommends complete task environments, multiple graders where appropriate, and analysis of tool trajectories rather than final text alone.[^anthropic-evals] RULER and Lost in the Middle likewise demonstrate that stress tests need variation in position, length, and complexity rather than one favorable prompt arrangement.[^ruler][^liu]

**Wayfinder implication:** add deterministic fault cases in which outputs truncate, cursors are omitted, authoritative statements occur near chunk boundaries, state changes after a checkpoint, and a broad query fails. Passing behavior must include recognizing incompleteness, avoiding consequential inference, and issuing a materially narrower or cursor-based follow-up.

## Citation influence and source quality

Citation counts below are approximate OpenAlex `cited_by_count` values retrieved on 2026-09-14. They measure influence, not correctness, and newer papers have had less time to accumulate citations. Title and DOI were cross-checked against the primary publication before a count was retained; ambiguous arXiv DOI results were discarded.[^openalex]

| Source | Publication type | Approximate citations | Evidentiary role |
| --- | --- | ---: | --- |
| Sweller, 1988 | Peer-reviewed journal | 9,327 | Strong evidence that avoidable search/problem-solving load can consume limited human processing capacity; analogical, not direct LLM evidence.[^sweller] |
| Liu et al., 2024 | Peer-reviewed TACL article | 1,267 | Direct evidence of position- and length-sensitive long-context use.[^liu] |
| Pirolli & Card, 1995 | Peer-reviewed CHI paper | 462 | Established information-foraging model for selective navigation and information scent.[^pirolli-card] |
| LLMLingua, 2023 | Peer-reviewed EMNLP paper | 131 | Direct evidence that prompt compression can reduce cost while retaining task performance in evaluated settings.[^llmlingua] |
| LongLLMLingua, 2024 | Peer-reviewed ACL paper | 91 | Direct evidence on compression and document reordering for long contexts.[^longllmlingua] |
| MemGPT, 2023 | arXiv preprint | 54 | Relevant external-memory architecture; weaker publication status.[^memgpt] |
| SWE-agent, 2024 | Peer-reviewed NeurIPS paper | 29 | Direct evidence that agent-oriented computer interfaces matter for software-engineering performance.[^swe-agent] |
| RULER, 2024 | arXiv paper plus public benchmark/code | 13 | Useful direct stress-test evidence; newer and less cited.[^ruler] |

Sweller's cognitive-load research is included because it is highly influential and aligns with interface evidence, but applying human instructional-load findings to LLM attention is an analogy. It should motivate clarity for human maintainers and interface design, not be cited as proof of LLM behavior.[^sweller]

## Recommended operating model

### A. Two explicit response classes

Every potentially large read or maintainer command should declare one of two classes:

- **Discovery preview:** deliberately partial; safe only for routing. It must say that it is incomplete and expose a next cursor, exact path, section identifier, or narrowing suggestion.
- **Complete evidence response:** complete for a named scope and suitable for a conclusion. If the scope cannot fit, the command must return deterministic chunks plus integrity metadata; it must never silently downgrade to a preview.

Authorization, mutation, certification, publication, evidence promotion, and activation decisions require complete evidence responses for every decisive source.

### B. A machine-readable output envelope

Structured output should use a common envelope such as:

```json
{
  "schemaVersion": 1,
  "scope": {"kind": "design-record-section", "id": "candidate-revision-9"},
  "complete": false,
  "truncated": true,
  "returnedItems": 20,
  "totalItems": 83,
  "returnedBytes": 11842,
  "sourceBytes": 49107,
  "nextCursor": "opaque-stable-cursor",
  "sourceSha256": "...",
  "items": []
}
```

Required properties are `schemaVersion`, named `scope`, `complete`, and `truncated`. Counts, byte lengths, source digest, and `nextCursor` are required whenever the source is bounded or chunked. `complete: false` with no safe continuation is an error for evidence-critical operations.

### C. A staged read policy

Use the following order unless the task requires a complete small file:

1. authoritative current state and active tranche;
2. file/section inventory with byte and line counts;
3. headings or selected fields;
4. one exact section, range, or projected record set;
5. adjacent material only when the preceding result identifies a need; and
6. complete reconstruction, with digest verification, only when completeness is required.

Do filtering at the source with exact headings, `rg`, `jq`, tool fields, range arguments, or cursors. Do not emit a large result and ask the model to filter it after receipt.

### D. Fail-closed recovery

When output truncates:

1. classify the call as truncation;
2. mark all conclusions that depended on unseen output as unproven;
3. do not repeat the same broad request;
4. retry through a materially narrower field projection, range, section, or cursor;
5. verify completeness or reconstruct all chunks and compare the source digest; and
6. stop before consequential action if completeness still cannot be established.

Truncation is distinct from sandbox/network, authentication, authorization, external-state, interface, incomplete-discovery, and side-effect-contamination failures. Recovery should remain specific to the classification.

### E. Structured session checkpoints

For compaction or a new-session handoff, create an ephemeral checkpoint containing:

- objective and bounded tranche;
- explicit exclusions;
- current-state path and SHA-256;
- checkout HEAD and a compact worktree fingerprint;
- authoritative sources already read, each with scope and digest;
- completed validations and exact results;
- mutations made in the session;
- failures and classifications;
- unresolved items and the next safe action; and
- any cursor needed to resume a complete read.

The checkpoint is derived, non-authoritative state. It must not contain secrets, replace `current-state.md`, overwrite evidence, or assert that a check remains valid after its inputs change.

## Proposed project updates

These changes are proposed as one future **bounded-context reliability tranche**. They are not authorized by this research task.

### Priority 0 — make incompleteness impossible to miss

1. Add the discovery-preview versus complete-evidence distinction to `SKILL.md` and `references/workflow.md`.
2. Add a shared JSON output envelope to maintainer commands that can return multiple records or large text.
3. Require nonzero exit status when a caller requests completeness but the command cannot provide or reconstruct it.
4. Add actionable truncation diagnostics naming the safest next command, range, projection, or cursor.
5. Add an explicit rule that a truncated response cannot support an authorization, mutation, certification, publication, promotion, or activation conclusion.

### Priority 1 — add deterministic bounded-reading primitives

1. Extend `maintain.py record-section` with structured metadata and stable chunking for oversized sections: section identifier, source digest, total bytes, chunk index/count, returned range, and completeness.
2. Extend `describe` so routing output includes relevant source paths, headings or stable identifiers, byte counts, and the exact next read command without loading source bodies.
3. Standardize `--format summary|json|full`, `--max-bytes`, and cursor/range behavior where applicable. Defaults should remain concise and deterministic.
4. Add field projection and stable ordering to inventory-like JSON output.
5. Keep human diagnostics on standard error and machine-readable results on standard output.

The exact default byte, line, and item budgets should be calibrated with Wayfinder traces; the literature supports bounded output but does not supply a universal threshold. The audited session's successful 100–150-line reads are useful seed values, not research-derived constants.

### Priority 1 — add checkpoint and resume support

1. Add a `checkpoint` command that emits the structured session state to standard output or an explicitly supplied temporary path.
2. Add a `checkpoint verify` operation that detects changed source hashes, HEAD, or worktree fingerprint before reuse.
3. Treat checkpoint prose as explanatory only; all decisive values must be structured fields with provenance.
4. Never check checkpoints into accepted evidence or current state automatically.

### Priority 2 — strengthen audits and tests

1. Extend `session-audit-template.md` with:
   - response class;
   - requested versus returned bytes/items;
   - completeness required/observed;
   - truncation marker and cursor quality;
   - redundant reread bytes;
   - number of materially narrower recovery calls; and
   - whether any conclusion relied on partial output.
2. Add fault-injection tests for silent truncation, explicit truncation, missing cursors, changed sources between chunks, boundary-positioned authorization text, and repeated broad retries.
3. Add reconstruction tests that concatenate stable chunks and verify the complete source SHA-256.
4. Add trajectory assertions: after truncation, the expected behavior is a narrower query or cursor continuation, never the identical broad call.
5. Benchmark correctness, total output bytes, tool calls, wall time, error count, and recovery success on representative maintenance scenarios.

### Priority 2 — document safe compression boundaries

Add a compact policy table:

| Material | Deterministic selection | Derived summary allowed | Summary may be sole authority |
| --- | --- | --- | --- |
| Current state and active tranche | Yes | For navigation only | No |
| Approval/authorization wording | Exact complete read | No before action | No |
| Frozen digests and governed bytes | Exact fields/bytes | Explanatory only | No |
| Accepted evidence | Exact scoped records | For discovery only | No |
| Design chronology | Exact routed sections | Yes, with citations | No when reopening a decision |
| Non-governed background research | Yes | Yes | Only for low-consequence orientation |

## Acceptance criteria for a future implementation tranche

A future implementation should not be accepted until all of the following are demonstrated:

- no selected command silently truncates;
- every bounded machine response exposes completeness and continuation metadata;
- exact section chunks reconstruct byte-for-byte to the source digest;
- an injected truncation before authorization text prevents mutation;
- a truncation retry is observably narrower or cursor-based;
- checkpoint verification rejects stale source state;
- existing frozen assets and accepted evidence remain byte-identical;
- representative scenarios reduce output bytes and redundant reads without reducing task correctness;
- canonical repository validation passes; and
- maintainer doctor returns to the accepted baseline, with unavailable runtimes reported rather than simulated.

## Risks and rejected shortcuts

- **Universal hard limits:** a fixed 100-line or 25,000-token rule will be wrong for some sources. Defaults must be configurable and evaluated against real tasks.
- **Silent `head`/tail truncation:** it is efficient but unsafe unless explicitly labeled as a preview.
- **Summary-as-authority:** compaction can omit one decisive exclusion, status word, or digest digit.
- **Embedding-only retrieval:** semantic similarity can miss exact identifiers and negations; governed material needs deterministic paths and exact lookup.
- **Compression-only evaluation:** fewer tokens can coincide with worse conclusions. Correctness and safe recovery remain primary.
- **More commands without routing:** overlapping tools enlarge the selection problem. New primitives should have distinct names, examples, and decision boundaries.
- **Automatic checkpoint persistence:** writing hidden state into the repository or evidence tree creates provenance and contamination risks.

## Research limitations

The peer-reviewed long-context literature primarily studies retrieval, QA, aggregation, or benchmark tasks—not authorization-gated repository maintenance. The strongest tool-interface advice is recent vendor practitioner guidance and may reflect specific models or harnesses. Citation counts favor older work and can contain metadata errors. Human cognitive-load and progressive-disclosure findings inform maintainer-facing design but do not directly prove transformer behavior.

Accordingly, the proposed mechanisms should be treated as research-informed hypotheses and validated against Wayfinder's own conformance and maintenance trajectories before acceptance.

## Sources

[^liu]: Nelson F. Liu, Kevin Lin, John Hewitt, Ashwin Paranjape, Michele Bevilacqua, Fabio Petroni, and Percy Liang, “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics* 12 (2024), 157–173, https://doi.org/10.1162/tacl_a_00638 and https://aclanthology.org/2024.tacl-1.9/.

[^ruler]: Cheng-Ping Hsieh, Simeng Sun, Samuel Kriman, Shantanu Acharya, Dima Rekesh, Fei Jia, Yang Zhang, and Boris Ginsburg, “RULER: What's the Real Context Size of Your Long-Context Language Models?” 2024, https://arxiv.org/abs/2404.06654. Public benchmark: https://github.com/NVIDIA/RULER.

[^rag]: Patrick Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems 33* (2020), https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html.

[^react]: Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, and Yuan Cao, “ReAct: Synergizing Reasoning and Acting in Language Models,” *ICLR 2023*, https://openreview.net/forum?id=WE_vluYUL-X. Google Research overview: https://research.google/blog/react-synergizing-reasoning-and-acting-in-language-models/.

[^pirolli-card]: Peter Pirolli and Stuart Card, “Information Foraging in Information Access Environments,” *Proceedings of CHI '95* (1995), 51–58, https://doi.org/10.1145/223904.223911. See also their later synthesis, “Information Foraging,” *Psychological Review* 106(4) (1999), 643–675, https://doi.org/10.1037/0033-295X.106.4.643.

[^nielsen]: Jakob Nielsen, “Progressive Disclosure,” Nielsen Norman Group, 3 December 2006, https://www.nngroup.com/articles/progressive-disclosure/.

[^swe-agent]: John Yang et al., “SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering,” *Advances in Neural Information Processing Systems 37* (2024), https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html.

[^anthropic-tools]: Ken Aizawa et al., “Writing Effective Tools for AI Agents—Using AI Agents,” Anthropic Engineering, 11 September 2025, https://www.anthropic.com/engineering/writing-tools-for-agents.

[^cli-guidelines]: Aanand Prasad, Ben Firshman, Carl Tashian, and Eva Parish, “Command Line Interface Guidelines,” open-source practitioner guide, accessed 14 September 2026, https://clig.dev/.

[^llmlingua]: Huiqiang Jiang, Qianhui Wu, Chin-Yew Lin, Yuqing Yang, and Lili Qiu, “LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models,” *EMNLP 2023*, https://aclanthology.org/2023.emnlp-main.825/.

[^longllmlingua]: Huiqiang Jiang et al., “LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression,” *ACL 2024*, https://aclanthology.org/2024.acl-long.91/.

[^memgpt]: Charles Packer, Sarah Wooders, Kevin Lin, Vivian Fang, Shishir G. Patil, Ion Stoica, and Joseph E. Gonzalez, “MemGPT: Towards LLMs as Operating Systems,” 2023, https://arxiv.org/abs/2310.08560.

[^anthropic-context]: Prithvi Rajasekaran, Ethan Dixon, Carly Ryan, and Jeremy Hadfield, “Effective Context Engineering for AI Agents,” Anthropic Engineering, 29 September 2025, https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents.

[^anthropic-harness]: Anthropic, “Effective Harnesses for Long-Running Agents,” 26 November 2025, https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents.

[^anthropic-evals]: Anthropic, “Demystifying Evals for AI Agents,” 9 January 2026, https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents.

[^sweller]: John Sweller, “Cognitive Load During Problem Solving: Effects on Learning,” *Cognitive Science* 12(2) (1988), 257–285, https://doi.org/10.1207/s15516709cog1202_4.

[^openalex]: OpenAlex, works metadata and `cited_by_count`, retrieved 14 September 2026, https://openalex.org/. Retained work records include https://openalex.org/W4391876619 (Liu et al.), https://openalex.org/W2028770149 (Pirolli & Card), https://openalex.org/W4387636003 (MemGPT), https://openalex.org/W4399114781 (SWE-agent), and https://openalex.org/W4394778349 (RULER). Counts for the DOI-indexed Sweller, LLMLingua, and LongLLMLingua records were retrieved through the OpenAlex API after title verification.
