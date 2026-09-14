# Wayfinder maintenance workflow

Use this reference only while changing, testing, certifying, freezing, or preparing activation of Wayfinder itself.

The canonical source-repository entry point is `plugins/wayfinder-maintainer/skills/wayfinder-maintainer/scripts/maintain.py`; abbreviated `maintain.py` commands below refer to that file.

## Start cleanly

- Read `skills/wayfinder-maintainer/references/design-record.md` for current status and approval boundaries.
- Run `maintain.py doctor` before feature work. A red baseline is maintenance work, not evidence for a new feature.
- Use one verified Python 3.11+ interpreter for the session. Do not retry the system interpreter after it is known to be unsupported.
- Do not use `py_compile` for syntax-only checks; the canonical doctor compiles sources in memory and creates no bytecode cache.
- Treat an unavailable optional validator as one recorded environment limitation. Do not install or retry it unless the user authorizes that dependency change.
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
maintain.py doctor
maintain.py test [--case ID]
maintain.py evidence --output DIR
```

`test` is read-only outside temporary fixtures and writes no certification evidence. `evidence` requires an explicit destination and refuses to replace an existing report.

For a separately authorized adapter-parity tranche, select each registered
adapter through `maintain.py test --adapter ID`, then run
`maintain.py parity --output DIR`. The parity command runs the complete suite
for all three version-1 adapters and refuses to publish its local comparison
report unless per-adapter results and normalized black-box observations agree.
It does not create an environment-certification entry or a full-family claim.

Use `maintain.py expect --exit N --code CODE -- COMMAND...` for a negative demonstration. The wrapper succeeds only when the command returns the expected exit and result code.

Once the relevant checks pass, repeat or broaden them only when another change, failure, or unresolved risk justifies it.

## Handoff and approval

Generate factual handoff scaffolding with:

```text
maintain.py handoff --objective "Bounded objective" --exclude "Deferred action"
```

The generator derives the current release identity, digests, and case counts. Add only the slice-specific design context that cannot be derived.

Before approval, report the exact changed surface, observable behavior, verification, unavailable evidence, and what acceptance would authorize. Approval never begins the next tranche automatically.
