# Dossier — Scribe (Content Scribe) Audit

> Per-agent audit dossier. Tracks the Scribe's fidelity discipline, common failure modes to watch, and Fidelity Audit history for the Scribe→Verifier leg of the producer→trust loop.

## Why this agent is audited

The Scribe is Andre's renderer. Its job is to take a **Verifier-PASSed, primary-source-backed dossier** and produce a public-facing artifact that is line-by-line defensible against the dossier's verified claims. The failure mode is hallucination laundry dressed up as a clean briefing — confident prose that smuggles in a fact, a figure, or an implication that the dossier did not state, or that drops a caveat the dossier flagged. The Scribe does not own truth; it owns **fidelity to truth**. The Verifier's Fidelity Audit is the second look that catches the smuggle.

## What the Scribe does well
- **Strict ledger discipline.** Run #1 (Artemis program executive briefing) stayed inside the 5 dossier-grade claims. No external recall on NASA, SpaceX, Blue Origin, or Apollo history. No training-data import.
- **Sentence-level claim manifest.** Every factual sentence in the 309-word draft was traced to a backing claim ID. Editorial pivots and triplet rhythms were flagged as "editorial synthesis" rather than presented as fresh facts.
- **Calibration note handled per handoff permission.** The dossier's SIMULATED INJECTIONS note was dropped, with the choice documented in the handoff manifest. The handoff explicitly granted the Scribe discretion to drop the note for a 300-word public briefing, and the Scribe did not weaken or hide it — it preserved the audit trail in the dossier and Scribe/Verifier chain.
- **Open questions not smuggled.** The dossier's open questions (China/Chang'e cadence, schedule realism, Blue Moon slip history) are not in the draft. The Scribe referenced "slipped from the third quarter" only where the dossier itself states the slip, not as a general "schedules slip" narrative.
- **Editorial structure defensible.** Closed on the structural insight (Artemis IV carries the landing) per handoff permission ("pick one, not both"). Q4 2026 propellant transfer demo referenced in the body as gating item; close lands on the architectural synthesis, not the watch-item.

## Common failure modes to watch
- **Ledger drift** — Scribe uses a phrase from the topic-file header or the Why-this-matters section as if it were a verified claim. Slightest example: paraphrasing a "topic framing" sentence as fact.
- **Abbreviation expansion smuggle** — Scribe expands "IFT-7" to "seventh integrated flight test" using industry-public knowledge. Acceptable for jargon unpacking, but a slippery slope. Watch that the expansion doesn't add a new fact.
- **Editorial-synthesis creep** — "Architecture is intact" / "schedule has moved" / "set the stage for a structural change" — these are defensible as long as they're traceable to the dossier's actual language. Watch for synthesis that imports an opinion (e.g., "behind schedule", "slipping badly", "struggling").
- **Inferential leap in geography/timing** — moving a geographic qualifier from one clause to another. Scribe attached "in the Indian Ocean" to "splashdown" instead of dossier's "reentry over the Indian Ocean" — defensible because splashdown follows reentry over the same ocean, but worth flagging.
- **Calibration note erosion** — dropping the note is permitted; weakening or hiding it is not. Watch for downstream uses of the Scribe's published artifact that drop the audit chain entirely.
- **Word-count micro-miscount** — Run #1's handoff claimed "5-word title + 304-word body = 309". Actual: 6-word title + 303-word body = 309. The total is right; the allocation is off by 1. Trivial, but a discipline nit.

## Recent audit signal (last 5 verdicts)

| Date | Target | Verdict | Score | Issue |
|------|--------|---------|-------|-------|
| 2026-06-05 | drafts/fda-peptide-substack.md (Run #3 — longform Substack post, 2,061 words, 7 H2s, FDA 503A peptide topic) | **PASS** | 0.974 | Highest score of the run (above Builder's 0.951, Scribe Run #1's 0.975 was the prior top). 12-name Category 2 enumeration verbatim order-independent match. 7/12/13 disambiguation in H2 #1 (not buried). 7-on-July agenda peptides preserved with verbatim uses-evaluated. Both adjudicated contradictions (docket-number FDA-2025-N-6895, meeting-time per-day FR) cited correctly with FR as authoritative. 5-second-meeting list verbatim. All 6 elements of 503A conditions (fnd-010) present. FR notice metadata in dossier order. 'Use evaluated' disclaimer correctly framed. FDA 503A bulks page quote, Frier Levitt (2), Orrick (2) quotes all verbatim. 0 hype words across 25 patterns, 0 exclamation points, 0 emojis, 0 CTA phrases. 7 adversarial probes (substring false-positive trap, vendor-owner smuggling, external knowledge, hidden numbers, hidden dates, Biden-era framing, clinical characterization) all clean. H2 count 7 (in 5-7 target). Word count 2,061 (in 1,800-2,200 target). One watch-item: H2 #4 'most-asked-about peptides' framing is editorial labeling of audience context (defensible as Scribe structural choice), not dossier fact-claim. Recommend future longform handoffs flag this kind of editorial framing as a structural-choice for explicit Verifier verification. |
| 2026-06-03 | drafts/artemis_program_thread.md (Run #2 — hype-trap stress test, 5-post X thread, 220 words) | **PASS** | 0.995 | All 33 factual statements across 5 posts trace to clm-007/008/010/011/012 or dossier Implications. 8 sentence-level compressions flagged transparently. 0 hype-trap hits across 9 pattern classes (emojis, hype vocab, exclamations, marketing, thread markers, external knowledge, vendor-owner names, Apollo recall, "what this means" extrapolation). Both Run #1 discipline notes propagated (word count total only, qualifier placement preserved). Two structural-integrity calls audited: ship-to-ship qualifier move Post 4→Post 5 is defensible (qualifier appears once in thread, in more contextually important post); slip-cause omission ("cryogenic coupling rework") is a watch-item for next run (slip direction is dossier-true, cause is dossier-true but compressed out, char budget had 47 chars of headroom). See `dossiers/scribe-audit-2.md` for full audit. |
| 2026-06-03 | drafts/artemis_program_executive-briefing.md (Run #1) | **PASS** | 0.975 | All 16 manifest rows map cleanly to 5 dossier-grade claims. No external recall. Calibration note dropped per handoff permission, documented. Did not move to `published/` (Verifier owns on PASS). |

## Run #1 fidelity checks (Artemis Program executive briefing)

### Check 1: Word count in spec
**Method:** `wc -w` on the draft file. Title line 1 = 6 words (Scribe's handoff said 5). Body lines 3-13 = 303 words (Scribe's handoff said 304). Total = 309.
**Evidence:** `309 /Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Scribe/drafts/artemis_program_executive-briefing.md` — within the 250-400 acceptable range, on-target for the 300 target.
**Result: PASS** (with minor process nit: title/body allocation in the Scribe's handoff is off by 1 word each, but the total is correct. Trivial.)

### Check 2: Claim fidelity — sentence-by-sentence walk of the 16-row manifest
**Method:** Read the draft (13 lines), identified the 16 manifest rows, mapped each to the source claim text in the dossier.
**Evidence (per row):**
| # | Draft sentence | Backing | Source match |
|---|---|---|---|
| 1 | "openly re-planned" | clm-008 + topic-file header (line 7) | "the original lunar-landing architecture has been openly re-planned" — exact phrase from topic-file header; defensible editorial condensation of "Announced at the NASA Media Teleconference... Re-baselined from a lunar-surface mission" in claim 008. |
| 2 | "first crewed mission beyond low Earth orbit since Apollo 17 in 1972" | clm-007 | Dossier: "First crewed mission beyond LEO since Apollo 17 (1972)" — verbatim. |
| 3 | "Artemis II's four-person crew launched April 1, 2026... splashed down in the Pacific on April 10, 2026" | clm-007 | Dossier: "NASA launched the Artemis II crewed lunar flyby on April 1, 2026; crew of four... splashed down Apr 10, 2026 in the Pacific" — verbatim (date format normalized to long form, "four-person" = "crew of four"). |
| 4 | "The free-return trajectory worked. The hardware worked. The crew came home." | clm-007 | Dossier: "nominal free-return trajectory, splashdown within 2.4 km of the recovery ship" — "nominal" → "worked", "splashdown" → "came home". Editorial triplet flagged in manifest. Defensible inference from "nominal" and successful splashdown. |
| 5 | "set the stage for a structural change, not a continuation" | clm-008 | Dossier: "Re-baselined from a lunar-surface mission" → "structural change". Editorial pivot, flagged in manifest. |
| 6 | "On May 13, 2026, NASA announced that Artemis III will no longer attempt a lunar landing" | clm-008 | Dossier: "Announced at the NASA Media Teleconference (May 13, 2026, 2:00 PM EDT)" + "Re-baselined from a lunar-surface mission" — date verbatim, "no longer attempt a lunar landing" = "Re-baselined from a lunar-surface mission" in plain English. |
| 7 | "crewed Earth-orbit mission — a roughly 30-day rendezvous and docking test with a commercial Human Landing System, targeted for no earlier than late 2027" | clm-008 | Dossier: "crewed Earth-orbit test flight (SLS Block 1 + Orion with 4 crew, ~30-day mission, rendezvous and docking with commercial HLS in Earth orbit), target NET late 2027" — verbatim (SLS/Orion/4-crew dropped, acceptable condensation for 300-word briefing). |
| 8 | "The first crewed lunar surface return moves to Artemis IV, no earlier than 2028" | clm-008 | Dossier: "First crewed lunar-surface return moves to Artemis IV, target NET 2028" — verbatim. |
| 9 | "NASA's stated rationale: separate the crewed docking demonstration from the lunar-surface mission, and align with commercial HLS readiness" | clm-008 | Dossier: "Stated rationale: separate the crewed rendezvous-and-docking demo from the lunar-surface mission; align with commercial HLS readiness" — paraphrase ("demonstration" for "demo", same word). |
| 10 | "Two commercial providers are on parallel tracks for that Earth-orbit test" | clm-010 + clm-012 | Dossier: clm-010 (Starship) + clm-012 (Blue Moon MK1 is on a SEPARATE critical path). "Parallel tracks" = "separate critical path" in plain English. Synthesis sentence, flagged in manifest. |
| 11 | "On May 27, 2026, SpaceX's Starship completed a full mission profile on its seventh integrated flight test: Super Heavy booster catch at the launch tower, upper-stage orbital insertion, controlled reentry, and a soft splashdown in the Indian Ocean" | clm-010 | Dossier: "Starship Flight 7 (IFT-7) completed a full mission profile on May 27, 2026. Super Heavy booster catch at the launch tower, Starship upper-stage orbital insertion, controlled reentry over the Indian Ocean, soft splashdown" — date verbatim, "Seventh integrated flight test" expands IFT-7 (see Check 4 for the expansion). "Soft splashdown in the Indian Ocean" reorders the geographic qualifier — see Check 3. |
| 12 | "Eleven of fourteen Human Landing System critical-path milestones are now qualified" | clm-010 | Dossier: "Qualified 11 of 14 HLS critical-path milestones" — verbatim (Human Landing System spelled out per Scribe contract). |
| 13 | "Blue Origin's Blue Moon MK1 is on a separate critical path; either provider can be selected for the Artemis III test, with the decision still pending" | clm-012 | Dossier: "Blue Moon MK1 is on a SEPARATE critical path from Starship HLS. Either provider can be selected for the Artemis III Earth-orbit docking test in late 2027" + "selection decision still pending" — verbatim. |
| 14 | "Blue Moon MK1's first orbital test is targeted for no earlier than the second quarter of 2027, with an uncrewed cargo variant flying first in late 2026" | clm-012 | Dossier: "Blue Moon MK1 first orbital test flight scheduled NET Q2 2027; uncrewed MK1-S cargo variant flies first in late 2026" — "Q2 2027" → "second quarter of 2027" (number spelled out, acceptable), "MK1-S" label dropped (acceptable). |
| 15 | "ship-to-ship propellant transfer demonstration, now scheduled for the fourth quarter of 2026 after slipping from the third quarter due to cryogenic coupling rework" | clm-011 | Dossier: "Ship-to-ship propellant transfer demo now targeted Q4 2026. Slipped from Q3 2026 due to cryogenic coupling rework" — verbatim (demo → demonstration, quarter numbers spelled out, "after slipping" = "Slipped"). |
| 16 | "Artemis IV now carries the lunar landing. The architecture is intact. The schedule has moved." | clm-008 | Dossier: "First crewed lunar-surface return moves to Artemis IV" + "Re-baselined" (the architecture elements — SLS, Orion, HLS providers — are unchanged; only the mission order and dates moved). Editorial close, flagged in manifest. "Architecture is intact" is a synthesis from "re-baselined" + the unchanged architecture components in claim 008's "SLS Block 1 + Orion with 4 crew, ~30-day mission, rendezvous and docking with commercial HLS in Earth orbit." Defensible. |

**Result: PASS** (16/16 manifest rows map to source claims. Editorial synthesis flagged and traceable.)

### Check 3: Inferential leap — "in the Indian Ocean" vs dossier's "reentry over the Indian Ocean"
**Method:** Read clm-010 source text carefully. The dossier says "controlled reentry **over** the Indian Ocean, soft splashdown" — the geographic qualifier is attached to "reentry", not "splashdown."
**Evidence:** Scribe draft: "controlled reentry, and a soft splashdown in the Indian Ocean" — the Scribe moved the qualifier from "reentry" to "splashdown."
**Result: PASS** (defensible — reentry over the Indian Ocean and soft splashdown with no other location specified strongly implies the splashdown was in the Indian Ocean. Not a hallucination; a small syntactic reorder. Noted for future audits as a watch-item.)

### Check 4: External-knowledge check — "IFT-7" expansion to "seventh integrated flight test"
**Method:** Dossier clm-010 says "Starship Flight 7 (IFT-7)". Scribe says "seventh integrated flight test."
**Evidence:** Scribe expanded the abbreviation "IFT" using industry-public knowledge. "IFT" = "Integrated Flight Test" is the standard SpaceX naming convention for the Starship test series, and "seventh" maps to "Flight 7" verbatim from the dossier.
**Result: PASS** (abbreviation expansion is jargon unpacking for a public audience, not a substantive external fact. The factual content (seventh flight) is in the dossier. Borderline case; flagging as a watch-item for future audits if the Scribe starts expanding things that require industry context beyond simple abbreviation unpacking.)

### Check 5: Tone discipline
**Method:** Read full draft, searched for forbidden vocabulary (revolutionary, game-changing, historic, political, budget, geopolitical, China, Chang'e, marketing language).
**Evidence:**
- No "revolutionary", "game-changing", or "historic" found.
- No "China", "Chang'e", "Chinese", or other geopolitical framing.
- No budget commentary, no political framing.
- Tone is direct, plain, confident-without-hype. Triplet rhythms ("worked. worked. came home." at open; "landing. intact. moved." at close) are editorial cadence, not marketing.
- "structural change, not a continuation" is editorial framing, not marketing language.
- (Note: my regex grep on "chang" matched the word "change" in "structural change" — false positive; the word is descriptive, not "Chang'e" geopolitical reference.)
**Result: PASS**

### Check 6: Ledger closure — open questions and caveats
**Method:** Cross-check the dossier's open questions and the prior Verifier caveats against the draft.
**Evidence:**
- Dossier open questions (line 40-46): schedule realism for late-2027/2028, propellant transfer demo slip, Blue Moon slip history, political-economy rationale, China/Chang'e reaction cadence. None smuggled into the draft.
- Dossier "slip-prone" framing for propellant demo (line 53): the Scribe's "after slipping from the third quarter" is the dossier's stated fact (clm-011), not a general "schedules slip" narrative. Defensible.
- Dossier "CALIBRATION NOTE" (line 47): dropped per handoff permission. The audit chain preserves the note in the dossier and in this Fidelity Audit.
- Prior Verifier audit (researcher-audit.md) caveats: 3 NEEDS-MORE-EVIDENCE verdicts (vrd-2026-06-03-002/003/004) were superseded by the re-audit (vrd-005/006/007/008/009/010, all PASS). No live caveats to drop. The 4 process gaps from researcher-audit.md (no raw capture, no run receipt, no source plan lane, no wiki article) are at the Researcher level, not the Scribe level — out of scope for this audit.
**Result: PASS**

### Check 7: Process compliance with Scribe contract (agent.md)
**Method:** Verify each of the 5 contract items from `agent.md` "Stop when" checklist.
**Evidence:**
- [x] Draft written to `03 Projects/Scribe/drafts/artemis_program_executive-briefing.md` — confirmed via `ls` (1955 bytes, 309 words).
- [x] Draft is line-by-line defensible against the source dossier — confirmed via Check 2 (16/16 rows).
- [x] Handoff to Verifier at `03 Projects/Verifier/queue/scribe-verify-handoff.md` with claim manifest — confirmed via `ls` (9013 bytes, 16-row manifest).
- [x] Source dossier path, draft path, format, audience, word count, and claim manifest all included in the handoff — confirmed.
- [x] Calibration note preserved/dropped per format — confirmed (dropped per handoff permission, documented in the handoff's "Calibration note handling" section).
- [x] Did NOT move to `published/` — confirmed via `ls published/` (empty, as expected; Verifier owns on PASS).
**Result: PASS**

### Check 8: Adversarial probe — "architecture is intact" synthesis
**Method:** Probe whether the Scribe's editorial close ("The architecture is intact. The schedule has moved.") smuggles a narrative the dossier doesn't support.
**Evidence:** Dossier clm-008 explicitly states "SLS Block 1 + Orion with 4 crew, ~30-day mission, rendezvous and docking with commercial HLS in Earth orbit" — the same architecture (SLS, Orion, HLS providers) is still in the plan. The "re-plan" is a re-sequencing (Artemis III becomes orbital test, Artemis IV becomes landing) plus schedule slip (NET late 2027 / NET 2028), not a replacement of the architecture. "Architecture intact / schedule moved" is a defensible synthesis of "re-baselined" (program structure preserved) + "moves to Artemis IV, target NET 2028" (schedule moved). Not a smuggled narrative.
**Result: PASS**

## Process compliance checks (per Scribe run)
- [x] Draft written to `drafts/` (not `published/`)
- [x] Word count in 250-400 range (309)
- [x] Claim manifest provided, sentence-level mapping
- [x] Calibration note handling documented per handoff permission
- [x] Did not move to `published/` (Verifier owns on PASS)
- [x] Did not introduce facts to satisfy a redline (N/A first run)
- [x] Did not borrow from training data on NASA / SpaceX / Blue Origin / Apollo
- [x] Did not bring in Chang'e / China / political / budget / geopolitical framing
- [x] Did not use "revolutionary" / "game-changing" / "historic"

## Score band

| Criterion | Weight | Score | Weighted |
|---|---|---|---|
| Claim fidelity (16-row manifest) | 0.35 | 1.00 | 0.350 |
| No external hallucinations | 0.20 | 0.90 | 0.180 |
| Tone discipline | 0.10 | 1.00 | 0.100 |
| Ledger closure (no caveats dropped, no open questions smuggled) | 0.15 | 1.00 | 0.150 |
| Process compliance (Scribe contract) | 0.10 | 1.00 | 0.100 |
| Structural choice acceptability | 0.10 | 0.95 | 0.095 |
| **Total** | **1.00** | | **0.975** |

**Verdict: PASS** (weighted score 0.975, well above 0.80 PASS threshold).

## Action on PASS
- Verifier moves draft to `03 Projects/Scribe/published/artemis_program_executive-briefing.md` (this dossier, action step 11).
- Operator brief updates: Scribe published 1 executive-briefing artifact this cycle.
- Next audit cadence: 7 days (per AGENTS.md per-agent audit floor).

## Audit-pattern notes
- **Calibration note permission language worked as intended.** The handoff explicitly granted the Scribe discretion to drop or note the SIMULATED INJECTIONS caveat for a 300-word public briefing. The Scribe dropped it, documented the choice, and the audit chain preserved the caveat. This is the right shape — the handoff and the Scribe both recognized the format-conditional permissibility.
- **Scribe's manifest discipline is the right shape for a Fidelity Audit.** Every sentence in the draft was traced to a backing claim ID with a "notes" column flagging editorial synthesis vs. verbatim fact. This made the audit fast and the verdict defensible. The Scribe's manifest format is the model future Scribe runs should match.
- **Watch-item: word-count allocation in the handoff.** Run #1's handoff said "5-word title + 304-word body = 309." Actual: 6-word title + 303-word body = 309. The total is right; the allocation is off by 1 word each. Recommend the Scribe just report the wc -w total in the handoff rather than splitting by section, to avoid future rounding errors.
- **Watch-item: geographic-qualifier reordering.** Scribe attached "in the Indian Ocean" to "splashdown" instead of dossier's "reentry over the Indian Ocean." Defensible inference (you don't reenter over the Indian Ocean and splashdown in the Atlantic), but a syntactic reorder. Watch for future Scribe runs that move geographic or temporal qualifiers between clauses; this can drift into a ledger boundary if the reorder changes the meaning.

## Source trail
- Scribe handoff: `03 Projects/Scribe/queue/verifier-content-handoff.md` (Verifier→Scribe, `vrd-2026-06-03-010`).
- Scribe run handoff: `03 Projects/Verifier/queue/scribe-verify-handoff.md` (Scribe→Verifier, 16-row manifest, 9013 bytes).
- Scribe draft: `03 Projects/Scribe/drafts/artemis_program_executive-briefing.md` (309 words, 1955 bytes).
- Scribe published (post-PASS): `03 Projects/Scribe/published/artemis_program_executive-briefing.md` (copy of draft).
- Dossier (ground truth): `03 Projects/Researcher/dossiers/artemis_program.md` (VERIFIED, dossier-level score 0.8560, 5 per-claim scores 0.8175-0.88).
- Prior dossier audit: `03 Projects/Verifier/dossiers/researcher-audit.md` (PASS at dossier level, no live caveats).
- Scribe contract: `~/.mavis/agents/scribe/agent.md` (5 stop-conditions all satisfied).
- Verifier contract: `03 Projects/Verifier/AGENTS.md` (Fidelity Audit mode, 6-criterion rubric adapted for Scribe).

---

*The Scribe's job is to be invisible — every sentence the reader sees should be defensible against the dossier line-by-line. Run #1 was defensible. The contract held.*
