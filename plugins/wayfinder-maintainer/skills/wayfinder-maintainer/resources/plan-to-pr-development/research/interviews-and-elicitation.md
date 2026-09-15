# Interviews and requirements elicitation

Research question: How can an owner-agent planning conversation discover needs without leading the owner or becoming an endless questionnaire?

Researched 2026-09-15. Inspected the original systematic review's abstract, method/context discussion and comparisons, plus the complete official interview guidance. This is focused decision research, not a new systematic review.

## Findings and strength

**Systematic review:** Pacheco, García, and Reyes (2018) examined 140 studies from 1993–2015. Their synthesis describes elicitation effectiveness as dependent on product, stakeholders, and information sought; it does not establish a single technique for every setting. Interviews have support across several comparisons, but effectiveness, completeness, and efficiency differ and studies use heterogeneous measures. [Original IET Software article](https://ietresearch.onlinelibrary.wiley.com/doi/10.1049/iet-sen.2017.0144)

**Practitioner guidance:** GOV.UK (published 2017) recommends a discussion guide, open neutral starter questions, follow-up probes, real examples, and flexibility to pursue relevant topics. This is a mature public-service research practice, rather than a controlled test of agent planning. [Original Service Manual guidance](https://www.gov.uk/service-manual/user-research/using-in-depth-interviews)

These sources support structured coverage with conversational flexibility. They do not show that a fixed number of questions or a long chain of yes/no confirmations produces better plans. User-research interviews also differ from a decision-making conversation with a repository owner: the owner can prescribe future behavior and grant authority, whereas observations of current experience alone cannot.

## Recommended adaptation

Use a semi-structured interview: begin with a concrete recent change, clarify the intended outcome and preservation constraints, then resolve consequential options. Keep an uncertainty list and select the next question by how much its answer could change scope, acceptance, or implementation. This priority method is our synthesis; one material question per turn is the owner's agreed preference.

Open questions discover meaning: “What happened when you last tried this?” Probes clarify causality or boundaries: “What made that step difficult?” Recommendations follow discovery and research. A closed confirmation can then lock a specific choice with its tradeoff. Do not use the entire session to obtain assent to agent-proposed defaults; periodically restate understanding and allow correction.

When the owner cannot describe a behavior in the abstract, propose a sample scenario or output and ask how it should differ. Samples can expose ambiguity, but must not be represented as experimentally guaranteed elicitation improvements. Any implementation experiment needs authority appropriate to its actions.

## Alternatives and revisit triggers

A compact clarification is appropriate for a familiar localized fix. Workshops, stakeholder interviews, observation, or prototype evaluation may be needed when the owner cannot speak for affected users, roles disagree, or desired usability is uncertain. Do not claim the owner's interview establishes broad user needs in such cases. Revisit the guide if plans repeatedly omit important requirements, leading questions dominate, the owner experiences confirmation fatigue, or implementation discovers consequential ambiguity after approval.
