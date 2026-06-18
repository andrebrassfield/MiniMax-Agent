---
type: moc
created: 2026-06-04
status: synthesis
sources: 7
tags: [moc, night-flight, cascade-recovery, scribe-3, researcher-4, fleet, mavis]
related:
  - "[[mavis-as-companion]]"
  - "[[mphrediction-missing-use-case]]"
  - "[[ai-landscape]]"
  - "[[harness-engineering]]"
  - "[[first-principles]]"
  - "[[philosophy-of-mind]]"
  - "[[2026-06-04 - AI-as-companion landing]]"
  - "[[Fleet-Status Surface]]"
  - "[[Mavis Daily Check-in]]"
  - "[[01 Daily/2026-06-04]]"
domains: [ea, mavis-design, fleet-architecture, well-being, productivity-economics]
---

# 2026-06-04 — Night Flight cascade landing (MOC)

> Hub note for the 7 artifacts that survived the 2026-06-04 Night Flight cascade. The cascade killed 5 worker sessions at 01:58 CT (5-hour token quota cap on the MiniMax Hs_plus plan). The Scribe and Researcher landed their work; Designer / Builder / Coder / Verifier all died. This MOC makes the survivors discoverable for future sessions.

## The 7 surviving artifacts (Scribe 3 + Researcher 4)

### Scribe (3)

- [[mavis-as-companion]] — *the strategic reframe*. Operator mode + companion mode as the two layers of the EA role. 7 contradictions worth attention. ~2,430 words, 7 contradictions, mavis-handoff consumed.
- [[mphrediction-missing-use-case]] — *the article digest*. The mphrediction thesis: AI-as-companion is the dominant consumer use case, not AI-as-productivity. ~1,842 words, 6-source triangulation, mavis-handoff consumed.
- [[Mavis Daily Check-in]] — *the first companion-mode artifact*. Coder's prototype (shipped 08:33 CT after the cascade): single HTML, one rotating question, localStorage, warm paper aesthetic, breath-in fade. The Coder's recommendation: live with it a week before any feature work. The pool is the easiest tweak surface.

### Researcher (4)

- [[ai-landscape]] — 20,941 bytes, 30+ primary sources. The AI landscape in mid-2026.
- [[harness-engineering]] — 28,993 bytes, 30+ primary sources. Maps to the agent-harness pattern. The 12-component checklist.
- [[first-principles]] — 26,114 bytes, 30+ primary sources.
- [[philosophy-of-mind]] — 32,564 bytes, 30+ primary sources. Completed 01:58 — 6 seconds before the quota cascade.

## The synthesis (Connections)

The 7 artifacts are not parallel outputs. They are one thesis expressed at four layers:

| Layer | Artifact | Function |
|---|---|---|
| **Trigger** | [[mphrediction-missing-use-case]] | Primary source. Six independent sources triangulating: AI-as-companion is the dominant consumer use case. |
| **Reframe** | [[mavis-as-companion]] | Strategic synthesis. Chief-of-staff role splits into operator mode (scaffolding) + companion mode (organ). The 7 contradictions. |
| **Manifest** | [[Mavis Daily Check-in]] | First companion-mode artifact. Coder's prototype. Operationalizes the Scribe's "a response to 'how are you' should not be turned into an action item" — no streaks, no mood tags, no chart. |
| **Foundation** | The 4 Research dossiers | Canonical reference material. 30+ primary sources per dossier. The textbook seed for any future compiled Mavis-procedural. |

Full synthesis: [[2026-06-04 - AI-as-companion landing]] (Connections note, 2026-06-04).

## The cascade: root cause and the operational fix

**Root cause:** the 5-hour token quota cap on the MiniMax Hs_plus plan. All 5 worker sessions hit the cap simultaneously at 01:58-01:59 CT. The Verifier's web_search calls failed first with HTTP 402, then the cascade took the rest.

**Operational fix (adopted 2026-06-04):** max 2-3 frontier workers at a time, plus N compiled engines on rented GPUs. The 5-worker Night Flight was the last gasp of the old architecture.

## What the cascade taught the orchestrator

1. **The Scribe + Researcher are the load-bearing layer.** Designer / Builder / Coder / Verifier are derivative; the strategic reframe is upstream of them. When the cascade killed 5 sessions, the Scribe + Researcher artifacts survived. They are the *primary* layer; the others are *primary re-expressions* in their respective domains.
2. **Fleet concurrency cap is structural, not tactical.** Last night's 5-worker cap was a quota pressure issue, not an architecture issue. The fleet phase discovers the procedures, the compiled phase enforces them. The orchestrator's scope shrinks as procedures stabilize.
3. **Mavis-judgment is permanent, Mavis-procedural is compilable.** The daily-brief workflow is ~14 boxes, 3B territory. The strategic synthesis in design-review mode is open-ended, stays on frontier. See [[99 _system/procedures/daily-brief/procedure.json]] for the v0.1.0-draft.

## What this MOC enables for future sessions

- **Cold start on the operator/companion split:** read this MOC → 02 Notes/ideas/mavis-as-companion.md → 06 Connections/2026-06-04 - AI-as-companion landing.md. Three reads, ~15 min, full context.
- **Pull the textbook seed for Mavis-procedural:** the 4 Research dossiers are the canonical reference. When the daily-brief procedure.json moves to compile, generate.py walks these dossiers for the conversation examples.
- **Trace any future claim about the mphrediction thesis:** back to its 6 primary sources via the article digest.
- **Find the live companion-mode artifact:** Mavis Daily Check-in (Coder's prototype, 08:33 CT) is the only shipping companion-mode artifact. Use it as the spec for future companion-mode work.

## Connections to other vault notes

- [[agent-harness]] — operator-mode view; companion mode adds components 13 (Continuity) and 14 (Forgetting)
- [[Mavis-Apex-Architecture]] — where the operator/companion split becomes an architecture decision
- [[Mavis EA Design]] — where the autonomy/privacy line meets the companion-mode protocols
- [[MAVIS]] — weekly context; companion mode is now part of "what Andre is thinking about this week"
- [[SOUL]] — the static operating contract; companion mode is the application to well-being
- [[Capture Over Polish]] — this MOC is the capture; the protocols + forgetting-rules + procedure.json are the polish

---
*Hub MOC created 2026-06-04 10:30 CT, while the Verifier audits the Artemis status board. The 7 surviving artifacts are now discoverable for future sessions; the cascade root cause and the operational fix are recorded.*
