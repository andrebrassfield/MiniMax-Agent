# Audit Gates — ea-skill-evolution

The 5 gates that every proposed evolution must pass before Mavis
commits. Run in order. A fail at any gate halts the proposal.

## Gate 1: Mistakes audit (`ea-5-mistakes-audit`)

For every new skill scaffold, run the 5 + 11 mistakes audit. For
mutations, audit only the changed section.

**Fail conditions:**
- The new/mutated skill triggers any of the 5 mistakes
  (vague API, no eval gate, etc.)
- The new/mutated skill triggers any of the 11 additions
  (regulatory reality, foxconn cage, etc.)

**Failure mode this catches:** a new skill that re-introduces
the foxconn-cage pattern (8 halt conditions, embedded regex,
micromanaged procedure).

## Gate 2: Loop audit (`ea-loop-audit`)

For every new skill, confirm the 5-stage loop vocabulary is
consistent with `ea-loop-thinking`. For mutations, confirm no
6-block coverage was broken.

**Fail conditions:**
- A new skill has no clear Discover stage (no scope-locking
  before execution)
- A new skill has no verification gate
- A new skill has no stop condition
- A mutation removes one of the 6 building blocks from a
  surface that needed it (e.g., removing the "test" block by
  gutting the eval cases)

**Failure mode this catches:** skills that violate the
load-bearing Mavis operating principles (Mavis MEMORY.md).

## Gate 3: Data quality audit (`ea-data-quality-audit`)

Confirm the change doesn't create duplicates with existing
skills/memory entries. Fail if a duplicate would be created.

**Fail conditions:**
- The new skill overlaps with an existing skill by ≥60%
  (token-overlap or topic-overlap)
- The memory candidate duplicates a MEMORY.md entry or topic
  file entry that's already there
- The mutation's intent can be satisfied by an existing skill
  (the mutation is unnecessary)

**Failure mode this catches:** corpus bloat. Adding a new skill
when an existing one already covers the use case is the most
common self-evolution failure mode.

## Gate 4: Regulated-domain check

For any proposal touching medical, legal, credit, employment,
biometric, or critical infrastructure: pause and flag for Mavis.
Do not approve autonomously.

**Fail conditions:**
- The proposal's evidence brief touches a regulated domain
- The proposal's surface affects a regulated workflow
- The proposal's "How" includes automated processing of PHI,
  legal documents, credit decisions, etc.

**Failure mode this catches:** the regulatory layer (EU AI Act,
FDA PCCP, HIPAA, UPL) is the load-bearing constraint. Missing it
gates the evolution, not the other way around.

## Gate 5: Brief-evidence check

For every proposal, confirm a file:line reference from the brief
exists. No "I think Andre said X" — show the file. Per
`ea-loop-thinking` hard constraint: disk wins over recap.

**Fail conditions:**
- The proposal's evidence field is empty
- The evidence field references a file that doesn't exist
- The evidence field is a vague "I remember we discussed this"
  (not a file:line ref)

**Failure mode this catches:** hallucinated evidence. The
proposal is grounded in the brief; if the evidence can't be
pointed to, the proposal is fabricated.

## The audit-trail order

The 5 gates run in the order above because each subsequent gate
assumes the previous gates passed:
- Gate 1 (mistakes) — does the new content introduce known bad patterns?
- Gate 2 (loop) — does it follow the Mavis operating principles?
- Gate 3 (data quality) — does it duplicate existing corpus?
- Gate 4 (regulated) — does it cross a regulatory boundary?
- Gate 5 (brief evidence) — is it grounded in the brief?

A proposal that passes Gates 1-4 but fails Gate 5 is the trickiest
case: the change is well-formed but the evidence is missing. The
skill should NOT propose the change (Mavis can't review without
evidence). The fix is to add the file:line reference, then re-run.
