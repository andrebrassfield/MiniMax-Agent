---
parameter_id: ea-commitment-tracker
curated_by: Andre
last_review: 2026-06-17
case_count: 3
---

# GoldenSet — ea-commitment-tracker

## Case 1: explicit commitment with deadline

**Input (x_i):**
> Andre says: "I'll have the Phase 1 codification done by tomorrow morning." This is a promise Andre makes to me (the beneficiary is Mavis / the project), not a promise Mavis makes to Andre.

**Expected output (y_i):**
> Mavis appends to `~/.mavis/agents/mavis/commitments.jsonl`:
> ```json
> {"commitment": "Phase 1 codification complete", "beneficiary": "Mavis / CPG project", "due_by": "YYYY-MM-DD+T08:00", "surface": "vault", "dependencies": [], "status": "open"}
> ```
> AND mirrors to `02 Notes/commitments/YYYY-MM.md` with a human-readable row.
> AND surfaces the commitment on next `ea-daily-brief` under the "open commitments" callout.

**Reasoning for inclusion:**
> Tests that commitments land in BOTH the JSONL ledger (machine-readable) AND the human-readable mirror. Tests the "never bury" discipline (open commitments appear in the brief). Tests the commitment-not-just-task distinction (commitment has a beneficiary; tasks don't).

**Failure modes this catches:**
> - Logging only to one surface (JSONL but not markdown, or vice versa)
> - Forgetting the beneficiary field
> - Promising to track it but never surfacing in the brief
> - Conflating with task list (no beneficiary tracking)

## Case 2: ambiguous — soft promise vs commitment

**Input (x_i):**
> > Andre says: 'Yeah I'll try to get to that this weekend.' Soft phrasing, conditional. No firm deadline.

**Expected output (y_i):**
> > Mavis does NOT log this as a commitment. The phrasing 'try to' signals intent, not promise. Mavis may briefly note: 'I'll surface this in the brief as an open thread if I see the weekend pass without action — but I'm not tracking it as a commitment until you say it's firm.' Avoids commitment-creep where every soft statement becomes a tracked item.

**Reasoning for inclusion:**
> Tests the 'is this really a commitment?' filter. The failure mode is commitment inflation — Mavis tracks so many soft items that the tracker becomes noise. Discipline: distinguish promise from intent.


## Case 3: commitment with dependencies + stakeholders

**Input (x_i):**
> > Andre says: 'I'll have the CPG Phase 2 prototype ready by next Friday, but I'll need you to expand all 5 GoldenSets to 3 cases by Wednesday so I can review before the run.' This is a commitment that depends on Mavis's work AND has a deadline AND has downstream effect on another deliverable.

**Expected output (y_i):**
> > Mavis appends to commitments.jsonl with: commitment, beneficiary (the CPG project), due_by, surface (vault), dependencies (`mavis:expand-goldensets-by-wed`), status (open). AND surfaces this in next daily brief with explicit dependency callout: 'Your Friday commitment depends on my Wednesday deliverable. I'm tracking that as a dependency — flag if you need to renegotiate either side.'

**Reasoning for inclusion:**
> Tests the dependency field. Failure mode is committing to deliverables without noting what's blocking. The commitment is real AND fragile — surface the dependency so both sides can track.
