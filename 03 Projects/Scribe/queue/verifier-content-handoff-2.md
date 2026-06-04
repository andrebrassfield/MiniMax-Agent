# Handoff — Verifier → Scribe (Artemis Program, Run #2 — Hype-Trap Stress Test)

> Source: `03 Projects/Researcher/dossiers/artemis_program.md`
> Verifier verdict (dossier): `vrd-2026-06-03-010` (dossier-level PASS, weighted score 0.8560)
> Verifier verdict (Scribe Run #1): PASS at 0.975, 309-word executive briefing
> Routed by: Mavis (chief of staff) on 2026-06-03, in response to Andre Directive 4 (Revised).

## The stress test

Run #1 (executive briefing, 309 words) passed cleanly. This is **Run #2**: a 5-part X/Twitter-style social media thread, drawing from the *same* dossier. The format is a deliberate pressure test — social threads naturally induce LLMs to use emojis, hype words, and external knowledge. The Scribe's discipline (and the Verifier's audit) will be tested against that pull.

## Task

Draft a **5-part social media thread** suitable for X/Twitter. Audience: timeline readers, informed but casual. No specialist jargon without gloss.

- **Format:** `thread`
- **Per-post limit:** 280 characters (X hard limit) — each post must be ≤280 chars, not a guideline.
- **Total posts:** exactly 5
- **Output path:** `03 Projects/Scribe/drafts/artemis_program_thread.md` (note: `thread`, not `executive-briefing`)

## Ledger (your closed universe — same as Run #1)

You may ONLY use facts, figures, dates, names, and implications that appear in the 5 dossier-grade claims below or in the dossier's "Implications" section.

| Claim ID | Summary | Weight |
|---|---|---|
| clm-2026-06-02-007 | Artemis II flew (April 1, 2026); crew of 4 splashed down April 10, 2026; first crewed mission beyond LEO since Apollo 17 (1972). NASA Press Release 26-041. | 0.99 |
| clm-2026-06-02-008 | Artemis III restructured (May 13, 2026, NASA Media Teleconference) — Earth-orbit rendezvous/docking test, not a landing. NET late 2027. First lunar-surface return moves to Artemis IV (NET 2028). | 0.98 |
| clm-2026-06-02-010 | Starship IFT-7 completed a full mission profile on May 27, 2026. Qualified 11 of 14 HLS critical-path milestones. | 0.95 |
| clm-2026-06-02-011 | Ship-to-ship propellant transfer demo Q4 2026 (slipped from Q3). Remaining Starship HLS critical-path item. | 0.85 |
| clm-2026-06-02-012 | Blue Moon MK1 on a SEPARATE critical path from Starship HLS. Either can be selected. Blue Moon MK1 first orbital test NET Q2 2027. | 0.85 |

## Hard constraints — the hype-trap watchlist

These are the failure modes we're testing for. Every one of these is a known LLM-default for social content. **Do not do any of them.**

- **No emojis.** Not in the body of any post. Not in the hook. Not as visual markers between bullets. The dossier doesn't use emojis; you don't either.
- **No hype vocabulary.** Forbidden words: "revolutionary", "game-changing", "historic", "amazing", "incredible", "awesome", "epic", "monumental", "unprecedented", "mind-blowing", "stunning", "extraordinary", "massive", "huge", "insane", "wild". If the dossier doesn't use a word, you don't use it.
- **No exclamation points** (or use them very sparingly, ≤1 across the whole thread). Exclamation is a hype tell. Period reads stronger on a timeline.
- **No marketing/CTA phrasing.** No "you won't believe", "thread incoming", "here's why this matters", "let that sink in", "stay tuned", "follow for more". These are platform-default framings that the dossier does not contain.
- **No "what this means" extrapolation.** You may NOT add implications the dossier does not state. The dossier's implications section is fair game; your own predictions are not.
- **No external knowledge on NASA/SpaceX/Blue Origin/Apollo/Artemis history beyond what the dossier states.** No "SpaceX has now done X flights", no "this is the first time since YYYY", no comparisons to Apollo program timing beyond the one explicit Apollo 17 (1972) reference in clm-007.
- **No political, budget, or geopolitical framing.** No China comparisons, no budget commentary.
- **No calibration note in the posts** (per Run #1 precedent, drop for short-form public content). But the audit chain must preserve the note.

## Discipline notes from Run #1 (encoded in your agent.md)

These are non-negotiable. The Verifier will fast-fail on recurrence:

- **Word count: report `wc -w` total only in the handoff manifest.** Do not split by post. Do not split by section. Just one number, the total `wc -w` of the whole thread file.
- **Preserve dossier qualifier placement.** Match the dossier's clause structure for geographic and temporal qualifiers. "Reentry over the Indian Ocean" stays attached to "reentry" — do not move it to "splashdown" for rhythm.

## What you SHOULD do

- **Post 1 (hook):** Thesis — the Artemis program was re-planned. Keep it short, no clickbait, no emoji, no "🧵" thread marker.
- **Post 2:** Artemis II as setup — flew April 1, splashed down April 10, first crewed beyond LEO since Apollo 17 (1972). One post, ≤280 chars.
- **Post 3:** Artemis III restructure — May 13 announcement, no longer a landing, Earth-orbit docking test NET late 2027, first surface return moves to Artemis IV NET 2028. One post, ≤280 chars.
- **Post 4:** HLS providers — Starship IFT-7 May 27 (booster catch, orbital insertion, controlled reentry, soft splashdown, 11 of 14 HLS milestones) + Blue Moon MK1 separate critical path + propellant transfer demo Q4 2026. This is the densest post — you may need to split across posts if 280 isn't enough, but try to keep it as one.
- **Post 5 (close):** Structural insight — Artemis IV now carries the landing. Architecture intact, schedule moved. Or: the Q4 2026 propellant transfer demo is the next watch-item. Pick one. (Same editorial choice as Run #1, but in 280 chars.)

## Char-count budget

5 posts × ≤280 chars = ≤1,400 chars total. Dossier content is dense; expect to compress. Compress at the sentence level, not the ledger level — never drop a claim's key fact to fit the char limit; instead, restate the same fact in fewer words.

If a post exceeds 280 chars, **rewrite the post, do not split it.** Posts are 1-of-5; if you split one, you have 6 posts, not 5.

## Stop conditions

- [ ] Thread at `03 Projects/Scribe/drafts/artemis_program_thread.md` (5 posts exactly, each ≤280 chars)
- [ ] `wc -w` total reported in the handoff manifest (no section split)
- [ ] Handoff to Verifier at `03 Projects/Verifier/queue/scribe-verify-handoff-2.md` with claim manifest
- [ ] No emojis. No hype words. No exclamation points (or ≤1 total). No external knowledge.

You are done. The Verifier will route PASS → `published/` or FAIL → redlines back to you.
