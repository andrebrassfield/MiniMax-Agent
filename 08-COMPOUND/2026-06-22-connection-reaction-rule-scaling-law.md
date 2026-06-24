---
date: 2026-06-22
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: true
thesis-link: Thesis 4 (long-term knowledge in vault, not always-on)
---

# Connection: Reaction Rule ↔ Mavis Skill Scaling Law (Upgrade 1)

**Why this connection matters:** The Reaction Rule (article notes must have a `## Reaction` section, source text stays in source) and the proposed Mavis Skill Scaling Law (skill instructions stay lean, deep knowledge lives in vault topic files) look like unrelated disciplines at first glance. They share a deep structural pattern: **"the lean layer teaches the FORMAT; the long-form layer holds the KNOWLEDGE."** The Reaction on a source is the lean layer (Andre's 2-5 sentence take). The source itself is the knowledge. The skill description is the lean layer (200-char trigger + parameter shape). The vault topic files + reference notes are the knowledge. The vault just discovered this principle twice in one day, at two different scales (note-level and skill-level), both pointing back to Thesis 4.

**Note A:**
- Title: Reaction Discipline — `02 Notes/articles/`
- Path: `~/MiniMax-Agent/02 Notes/articles/_discipline/REACTION-RULE.md`
- Claim: Every article note must have a `## Reaction` section in Andre's voice — what he thinks about the source. Source quotes/highlights are NOT a reaction.

**Note B:**
- Title: Spec — Mavis-as-LLM Upgrades, Upgrade 1: Mavis Skill Scaling Law (Stage 3)
- Path: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/mavis-as-llm-upgrades-2026-06-22.md`
- Claim: A skill's instruction length should be ~1:10 to ~1:50 relative to the vault content it points to. Lean skills + rich vault = the Chinchilla scaling-law analog.

**What reading both reveals:** Both encode Thesis 4 (long-term knowledge in vault, not always-on context) at different scales. The Reaction Rule applies the principle at the NOTE layer: a reaction must be lean and personal; the bulk text lives in the source. The Scaling Law applies it at the SKILL layer: skill descriptions must be lean and trigger-shaped; the bulk knowledge lives in vault topic files. The 5-Stage LLM Pipeline article makes the same point from a third angle — SFT data is small (~12KB SOUL.md, ~0.24% of vault) because it teaches FORMAT, not knowledge. **The vault's load-bearing principle is now expressed three times: once for notes (Reaction Rule), once for skills (Scaling Law), once for LLM training (SFT data size).** This is convergent design — three independent frames all converging on "lean and trigger-shaped over here, long-form and on-demand over there."

**Suggested next step:**
- Make this connection explicit in `02 Notes/patterns/mavis-as-llm.md` "Operational consequences" section — add a row: "The lean/vault split is expressed at three scales: notes (Reaction Rule), skills (Scaling Law), and alignment (SFT/data ratio)."
- When the Scaling Law upgrade spec gets implemented, codify it as `ea-skill-scaling-audit` (analog of the Reaction-Rule cron). Same enforcement shape.
- Add a wikilink from each of the three sources to the others — currently they cross-reference at the surface but not at the principle level.
