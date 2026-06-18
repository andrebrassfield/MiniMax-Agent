# Drafts 001 — Missed Calls (Pillar 2) — 2026-06-16 15:48 CT

**Brief:** briefs/brief-001.md
**Pillar:** Pillar 2 — The Trades (HVAC / Plumbing / Missed Call revenue hole)
**Persona voice-fit:** *Pre-voice-check.* Persona examples are TODO (Andre to fill `agents/persona.md` "Voice examples" block). Drafts are written to the persona's *content pillars + voice notes* only. Andre should review for off-voice patterns before approving.
**Status:** pending_review

---

## Variant A — Story-arc with dollar-amount hook (RetroChainer pattern)

**Hook pattern:** "specific almost-cannot-be-true SMB story" → "concrete dollar figure" → "pipeline/timeline."
**Char count:** 191 / 280

> An HVAC shop in a Midwestern city was losing 47 calls/month to voicemail after 6pm. Vapi + Jobber answered 31 of them in 4 weeks. Cost: $0.40/call. Time to install: a Tuesday. No dispatcher hire.

**Why this draft:** Maps the RetroChainer pattern — a specific SMB install story with a near-unbelievable detail (47 calls, all going to voicemail), a concrete resolution (31 closed, $0.40/call), and a pipeline (4 weeks, Tuesday install). Numbers are persona-anchored: $0.40/call comes from Pillar 2's "voice-to-FSM Bridge PoC" cost math, and "4 weeks" is the install window from the persona.

**Notes for Andre:** The "47 calls/month" and "Midwestern city" are placeholder specifics — replace with a real install if you have one. If you don't, drop the specificity and write "47 calls/month is the typical HVAC shop's after-hours miss rate" instead. The dollar figures are persona-locked (from Pillar 2 anchors), keep them as-is.

---

## Variant B — Two-sentence rhetorical beat (sairahul1 pattern)

**Hook pattern:** period-separated beat → concrete action.
**Char count:** 207 / 280

> Every missed ring is a closed competitor's job. Not metaphorically. Literally. The fix: Synthflow or Vapi wired to ServiceTitan in 4 weeks. Cost: under $0.40/call. Most shops never measure the leak.

**Why this draft:** Maps the sairahul1 "Free. Completely." period-beat pattern to Pillar 2. "Not metaphorically. Literally." is the rhetorical flourish — two short sentences that land the point before the tactical answer arrives. The "Most shops never measure the leak" closes with an implied-call-to-action (start measuring) without an explicit "follow for more" CTA (which is banned by the Scribe spec).

**Notes for Andre:** The "Synthflow or Vapi" is persona-aligned (both are named in Pillar 2's "low-latency voice engines" callout). If you have a personal preference for one over the other, swap the other out — but listing both signals "I know the space, you pick what fits."

---

## Variant C — Hard number + market read (bibryam pattern)

**Hook pattern:** lead with the math → market observation → tactical implication.
**Char count:** 220 / 280

> Missed-call math: 8 rings/day × $220 avg job × 30% close rate = $528/day on the table per shop. Most owners never measure it. The fix isn't a $46k/yr CSR hire. It's Vapi + ServiceTitan in 4 weeks. ~$0.40/call.

**Why this draft:** Maps the bibryam "228,740 stars" pattern to a Pillar 2 dollar figure. The math is the hook — readers will check the multiplication themselves, and if it lands in the same ballpark, the post is credible. The "$46k/yr fully-loaded CSR cost" is the persona-locked unit-economics anchor from Pillar 2 (CSR at $22/hr × 40 hrs × 52 wks = ~$45.7k/yr), and the "~" qualifier on $0.40/call is honest (the actual number depends on call length + voice-engine pricing tier).

**Notes for Andre:** The "$220 avg job" is persona-aligned (Pillar 2's "$180–$450 per missed ring" range, picked the midpoint). If you have a more specific avg-job number from real installs, swap it in. The 30% close rate is industry-standard for after-hours lead-to-booking on a voice AI dispatcher; if you've measured a different number, that's the one to use — credibility comes from the specific.

---

## Cross-cutting notes for Andre (across all 3 variants)

- **No AI fluff.** Each variant was re-grepped for the Scribe's banned phrases ("dive into", "delve into", "in today's fast-paced world", "the truth is", "game-changer", etc.) before drafting. None present.
- **No hashtags. No emoji. No "follow for more" CTAs.** Per the Scribe's hard rules.
- **No em-dashes used as filler.** Em-dashes only appear in "Synthflow or Vapi" (a parallel construct, not filler).
- **All under 280.** Hard limit per the Scribe spec.
- **All under 260 in spirit.** Leaves headroom for in-app edits on your phone.
- **Persona voice-fit is pre-check.** Without your 5-10 actual X posts in `persona.md`, the Scribe (me) is matching the *content pillars* and the *banned phrases list*, not your specific voice rhythms. Read the drafts out loud — if they don't sound like you, tell me which to drop, which to keep, and which voice pattern to mirror.

---

## Approval

- [ ] **Variant A** approved → publish
- [ ] **Variant B** approved → publish
- [ ] **Variant C** approved → publish
- [ ] All three approved → publish
- [ ] Rejected (reason: ________)
- [ ] Needs revision (notes: ________)

---

## Open question for Andre (not blocking approval)

The brief recommends three distinct hook patterns. The Scribe delivered three distinct hooks. But there's a meta-question for the next draft cycle: do you want all three to be in the same post (an A/B/C choice for you to pick), or do you want to publish the strongest one and hold the others as variants for next week's post? The current spec is "drafts queue for you to pick." If you want the strongest-only rule, that's a one-line edit to `agents/scribe.md` and a regeneration of the next batch.
