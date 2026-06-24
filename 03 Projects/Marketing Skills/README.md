---
type: project
status: active
version: 2.5.0
shipped: 2026-06-23
owner: Mavis
---

# Marketing Skills (v2.5.0)

The marketing skill set for the thin harness. Each skill is a fat markdown procedure — value lives in the procedure, not the model.

## Skills in this set

| Skill | Status | Purpose |
|-------|--------|---------|
| **[/offers](offers/SKILL.md)** | ✅ Shipped v2.5.0 | Offer design — Value Equation + Six-Component Anatomy. Diagnoses weak offers. |
| **[/pricing](pricing/SKILL.md)** | ✅ Shipped v2.5.0 | Pricing strategy — anchor analysis, elasticity, payment math, charm vs premium, decoy, tiered, testing. Consumes /offers. |
| **[/copywriting](copywriting/SKILL.md)** | ✅ Shipped v2.5.0 | Copywriting — long-form sales pages, headlines, CTAs, email sequences, subject lines, voice & tone. Consumes /offers + /pricing. |
| **[/launch](launch/SKILL.md)** | ✅ Shipped v2.5.0 | Launch sequence mechanics — PLF/audience/signature/evergreen. Pre-launch, open cart, mid-launch, close cart. Consumes /offers + /pricing + /copywriting. |
| **[/sales-enablement](sales-enablement/SKILL.md)** | ✅ Shipped v2.5.0 | Sales-call assets for high-ticket — discovery framework, call structure, objection handling, proposals, case studies, follow-up. Consumes /offers + /pricing. |

## Pipeline shape

```
                    ┌─────────────┐
                    │   /offers   │  (no upstream — start here)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌─────────────────┐
        │ /pricing │ │ /copy-   │ │ /sales-         │
        │          │ │ writing  │ │  enablement     │
        └────┬─────┘ └────┬─────┘ └────────┬────────┘
             │            │                │
             │            ▼                │
             │      ┌──────────┐          │
             │      │ /launch  │          │
             │      └──────────┘          │
             │                            │
             └────────────────────────────┘
```

- `/offers` is upstream of everything. Run it first.
- `/pricing`, `/copywriting`, `/sales-enablement` consume `/offers`. Run in any order after.
- `/launch` consumes `/offers` + `/pricing` + `/copywriting`. Run last.

## Why this is a fat-skill set

Per the thin-harness-fat-skills principle (Active Thesis #3):
- The harness is the thin execution layer (mavis runtime).
- The skill files are the fat intelligence layer (markdown procedures).
- Each skill encodes a complete procedure with parameters, anti-patterns, and reference material.

Adding more agents multiplies the wrong variable. Adding more skills multiplies the right one.

## Installation

- **Runtime:** `/Users/brassfieldventuresllc/.mavis/skills/<skill>/SKILL.md`
- **Vault mirror:** `03 Projects/Marketing Skills/<skill>/` (this folder)

The runtime copy is what the harness invokes. The vault mirror is the durable reference.

## v2.5.0 release notes

**Released:** 2026-06-23

**What's new:** All 5 skills shipped in v2.5.0. /offers as the lead (most-developed), the other 4 designed by Mavis based on standard marketing domain practice.

**Caveats (Mavis-designed skills):** The 4 follow-on skills (pricing, copywriting, launch, sales-enablement) were designed without detailed operator specs. They encode standard marketing frameworks — value lies in the structure and the anti-pattern gates. **Iteration expected:** these are v1.0-shaped; expect refinement based on operator use.

**Caveats (cross-skill consistency):** Each skill cross-references its upstream skill in YAML + SKILL.md. The pipeline shape (offers → pricing/copywriting/sales-enablement → launch) is enforced in the cross-reference architecture but not in the runtime harness.

## Versioning

- **v2.5.0** (2026-06-23) — All 5 skills shipped. /offers as the lead; /pricing, /copywriting, /launch, /sales-enablement designed by Mavis.
- Future versions will iterate based on operator feedback. Expected: tightening of /pricing (anchor selection criteria), /copywriting (more industry-specific templates), /launch (more operator-specific calendar examples).
