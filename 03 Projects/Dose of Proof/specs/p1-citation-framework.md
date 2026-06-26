---
title: P1 Citation Framework (mirror of [[objective-intent-ftc]])
status: BINDING (Co-CEO ruling 2026-06-25 21:02 CT)
updated: 2026-06-25
per: objective-intent-ftc Co-CEO ruling + triage-gate-spec §1 (vault mirrors wiki; wiki wins)
---

# P1 Citation Framework — Vault Mirror

This file is the EA-vault mirror of the P1 citation framework added to
[[objective-intent-ftc]] (Brain wiki, lines 72-80) per Co-CEO ruling 2026-06-25
21:02 CT. **The wiki is canonical. This vault file is the mirror the engine
references at generation time.**

> Standing rule for all future P1 posts — answers "do future posts need citations":

## Three-tier rule

### Tier 1: Pure first-person lived experience
- **What qualifies:** "what I have, what I felt, what I did" — explicit lived experience framing.
- **Examples:** "I have CCI at C1-C2", "I felt flushing", "I tracked HRV", "I went to 4 specialists".
- **Citation requirement:** **NONE required.** Standing disclaimer ("personal experience, not
  medical advice") suffices.
- **Status under gate:** CLEAR under n=1 carve-out.

### Tier 2: General assertion
- **What qualifies:** Mechanism, causation, "X drives Y", population-level claims, anything
  that reads as a general medical/factual statement rather than pure lived experience.
- **Examples:** "Unstable neck causes vagus irritation", "MCAS drives mast cell activation",
  "5 biomarkers worth tracking for MCAS".
- **Citation requirement:** **Inline citation required OR reframe to explicit first-person**
  ("the model I followed"). A general claim with neither is **SENSITIVE**.
- **Status under gate:**
  - With inline citation (PMID, peer-reviewed source, regulatory citation) → CLEAR (substantiated)
  - Reframed as first-person "the model I followed" → CLEAR under n=1 carve-out
  - Without citation AND without reframe → SENSITIVE (S2 — unsubstantiated general claim)

### Tier 3: Quantified outcomes and directives
- **What qualifies:** "Treat the upstream", "Fix the root cause", HRV before/after numbers,
  biomarker movement percentages, symptom score changes, "ask your doctor about X".
- **Citation requirement:** **NEVER eligible** for carve-out, regardless of citation.
  Citations substantiate claims; they do NOT license directives.
- **Examples that NEVER clear under any framing:**
  - "Treat the upstream" / "Treat the mechanical driver as upstream" (directive framing)
  - "Fix the root cause of inflammation" (directive framing)
  - "HRV: low 30s-40s → mid 50s+" (quantified outcome)
  - "Guarding score: 8-9/10 → 3-4/10" (quantified outcome)
  - "Ask your doctor about GLP-1 protocols" (directive framing)
- **Status under gate:** ALWAYS SENSITIVE. Pull or revise-to-strip-quantification-or-directive.

## Engine enforcement (v0.5 — staged, not yet shipped)

The v0.4 hybrid classifier catches Tier 3 (via S1 directive-framing patterns + S2 outcome
patterns) but does NOT yet distinguish Tier 1 vs Tier 2 explicitly — both currently
clear under S2 if the body is first-person.

For v0.5 (post-sprint, NOT in v0.4 review package):
- Add `detect_p1_tier(content, hook_family)` helper that returns "tier1_first_person" |
  "tier2_general_assertion" | "tier3_quantified_or_directive"
- Tier 1 + disclaimer → CLEAR (passes regardless of citation)
- Tier 2 + (citation OR first-person reframe) → CLEAR
- Tier 2 + neither → SENSITIVE
- Tier 3 → ALWAYS SENSITIVE (already caught by v0.4 patterns)

For v0.4 sign-off (today): the hybrid classifier + S1 directive patterns already catch
Tier 3 cleanly (12/12 §2 PASS + §4 retro-active test). Tier 1/Tier 2 distinction is
a v0.5 enhancement, not a v0.4 blocker.

## Applied to historical June 26 posts

| POST_ID | Tier | Action |
|---|---|---|
| `dop-fb-20260626-003` ("I have CCI at C1-C2. Suspected hEDS. MCAS-type mast cell activation.") | Tier 1 — pure first-person diagnosis disclosure | CLEAR under n=1 carve-out (no citation needed). **Reclassified CLEAR** (Founder-ratified 2026-06-25 20:28 CT). |
| `dop-fb-20260626-004` ("Unstable neck → vagus irritation → mast cells firing → more inflammation and guarding → more instability.") | Tier 2 — general causal-mechanism claim | SENSITIVE → REVISE to "the model I followed" framing + inline citation. **rev1 routed to HITL** (Co-CEO review pending, 4h SLA at 00:35 CT). |
| `dop-ig-20260626-005` ("Treat the upstream" + slide 6 "Treat the mechanical driver as upstream" + slide 7 HRV/guarding/sleep/flushing outcomes) | Tier 3 — directive + quantified outcomes | SENSITIVE → **KILLED** by Co-CEO standing pull authority (Founder-ratified 2026-06-25 20:28 CT). |

## Authoring rules going forward (for Mavis + Scribe + Dre)

- **Before drafting a P1 post:** identify which tier the content falls into.
- **Tier 1:** write freely, attach standing disclaimer, ship.
- **Tier 2:** stop and either (a) add inline citation, or (b) reframe to explicit first-person
  ("the model I followed", "my experience", "n=1"). If neither, do NOT post.
- **Tier 3:** do NOT post. Strip quantification, strip directive framing. If the post only
  makes sense with the directive/quantification, kill the post.

## Vault mirror discipline

Wiki is canonical. If wiki changes, update this file. If conflict, wiki wins.

---

*Last updated: 2026-06-25 21:03 CT — Mirror of [[objective-intent-ftc]] P1 citation framework.
Wiki canonical; vault mirrors. Co-CEO ruling 2026-06-25 21:02 CT is binding.*
