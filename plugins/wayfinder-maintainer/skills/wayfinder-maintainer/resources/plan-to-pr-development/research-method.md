# Research and recommendation method

Research questions should serve a decision. Begin with what is uncertain, what options are credible, and which finding could change the plan. Avoid an exhaustive literature dump that makes the owner do the synthesis.

## Source selection

Inspect repository truth first. For external questions, prefer original empirical papers, the authors' own systematic reviews, official technical documentation, and first-party engineering reports. Search broadly enough to discover contrary findings, then narrow to the relevant conditions. Verify current tooling, interfaces, and feature availability from official sources before consequential use.

Label the evidence:

| Class | What it supports | Caution |
| --- | --- | --- |
| Empirical study | Findings within the studied population, tasks, and measures | Association is not necessarily causation; benchmark results are not deployment guarantees |
| Systematic review | Synthesis across selected prior studies | Search period, inclusion criteria, study quality, and heterogeneity limit generality |
| Official documentation | Current product mechanics and constraints | Availability and preview behavior can change; capability is not authorization |
| Practitioner report | Plausible methods and operational lessons | Organizational context and vendor incentives may affect transferability |
| Workflow synthesis | A reasoned adaptation for this repository | State it as a chosen heuristic, not a proven universal rule |

No source type can establish owner approval. Preserve frozen governed bytes and accepted evidence regardless of a research recommendation.

## Save a focused brief

Save new briefs in this workflow's `research/` folder; preserve existing research elsewhere. Give each a stable descriptive filename and record:

1. Research question and local decision it informs.
2. Date researched, source URLs, publication/version dates where known, and inspected source scope.
3. Findings with links adjacent to supported claims and evidence class.
4. Limitations, contrary findings or alternatives, and uncertainty.
5. Resulting recommendation, adaptation rationale, and decision consequences.
6. What would cause the recommendation to be revisited.

Use short source-grounded paraphrases, not copied articles. Never cite a source for a claim it does not establish. Explain when a recommendation combines evidence with owner preferences. Link approved decisions to the brief and decisive sources in the plan; accepted decisions or closures belong in the design record, with current-state routing when required.

## Research stopping and disclosure

Stop when evidence distinguishes the consequential options well enough for an informed choice, diminishing searches no longer change the recommendation, and uncertainties are disclosed. Broaden when sources conflict, a decisive dependency is absent, or only promotional/secondary accounts support a claim. Do not equate agreement among copied secondary articles with independent evidence.

A truncated response, inaccessible full paper, or missing documentation section must be named as a limitation. Use narrower reads or supplied continuation before relying on unseen source content; do not repeat the same broad call. An abstract supports only abstract-level conclusions. For a required tool failure, classify the interface, sandbox/network, authentication, authorization, external-state, truncation, incomplete-discovery, or side-effect issue before a materially different attempt.

Delegated research must have a bounded question, source standard, output format, and exclusions. Independent sources or competing option investigations can run in parallel; the lead checks source fidelity, resolves conflicts, and owns the recommendation. See [coordination research](research/implementation-and-delegation.md).
