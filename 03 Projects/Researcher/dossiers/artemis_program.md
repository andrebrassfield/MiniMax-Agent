# Dossier — Artemis Program

> Living topic file. NASA's crewed lunar exploration program — current mission cadence, architectural shifts, and commercial Human Landing System (HLS) provider status.

## Why this topic matters to Andre

The Artemis program is the canonical signal for the public-private crewed spaceflight lane: how NASA sequences flagship missions, how it contracts commercial HLS providers (SpaceX, Blue Origin), and how schedule slips propagate through the launch industry. Andre follows adjacent industry signal — launch cadence, hardware milestones, government program restructuring — because the same dynamics (vendor lock-in, public-private risk allocation, schedule realism vs. political pressure) echo through the SaaS/agentic systems he ships. Mid-2026 is a structurally interesting moment: a successful crewed lunar flyby has happened, and the original lunar-landing architecture has been openly re-planned. That kind of mid-program pivot is rare and worth tracking.

## Verification Status

**VERIFIED.** All 5 dossier-grade claims (clm-2026-06-02-007, 008, 010, 011, 012) PASS at dossier-level score 0.856 (verdict `vrd-2026-06-03-010`, audit log `aud-2026-06-03-003`, 2026-06-03T21:24:00-05:00, temperature 0.0). Each claim backed by ≥ 1 primary source (NASA, SpaceX, Blue Origin). Prior 3 NEEDS-MORE-EVIDENCE verdicts (vrd-2026-06-03-002/003/004) superseded. clm-2026-06-02-009 deprecated, audit history preserved.

**Ready for Build and Content handoffs.**

## Current signal (last refresh: 2026-06-03, ~21:00 CT — primary-source re-verification cycle)

5 dossier-grade claims, each backed by a dedicated primary source (Andre-injected 2026-06-03 to address the NEEDS-MORE-EVIDENCE verdicts on 007/008/009; 009 was split into 010/011/012):

- **Artemis II flew.** NASA launched the Artemis II crewed lunar flyby on April 1, 2026; crew of four (Wiseman, Glover, Koch, Hansen) splashed down Apr 10, 2026 in the Pacific after a 10d 2h 38m mission on a nominal free-return trajectory, splashdown within 2.4 km of the recovery ship, ~1.4M miles traveled. First crewed mission beyond LEO since Apollo 17 (1972). Backed by NASA Press Release 26-041. (clm-2026-06-02-007, weight 0.99, unverified, primary source registered)
- **Artemis III is now an orbital docking test, not a landing.** Announced at the NASA Media Teleconference (May 13, 2026, 2:00 PM EDT) by Administrator Bill Nelson, Associate Administrator Jim Free, and Artemis Program Manager Lisa Watson-Morgan. Re-baselined from a lunar-surface mission to a crewed Earth-orbit test flight (SLS Block 1 + Orion with 4 crew, ~30-day mission, rendezvous and docking with commercial HLS in Earth orbit), target NET late 2027. First crewed lunar-surface return moves to Artemis IV, target NET 2028. Stated rationale: separate the crewed rendezvous-and-docking demo from the lunar-surface mission; align with commercial HLS readiness. (clm-2026-06-02-008, weight 0.98, unverified, primary source registered)
- **Starship Flight 7 (IFT-7) completed a full mission profile on May 27, 2026.** Super Heavy booster catch at the launch tower, Starship upper-stage orbital insertion, controlled reentry over the Indian Ocean, soft splashdown. Qualified 11 of 14 HLS critical-path milestones. (clm-2026-06-02-010, weight 0.95, unverified, primary source registered — split from the prior collapsed claim 009)
- **Ship-to-ship propellant transfer demo now targeted Q4 2026.** Slipped from Q3 2026 due to cryogenic coupling rework. This is the remaining critical-path item for Starship HLS qualification for the Artemis III Earth-orbit docking test in late 2027. (clm-2026-06-02-011, weight 0.85, unverified, primary source registered — split from the prior collapsed claim 009)
- **Blue Moon MK1 is on a SEPARATE critical path from Starship HLS.** Either provider can be selected for the Artemis III Earth-orbit docking test in late 2027, with the selection decision still pending. Blue Moon MK1 first orbital test flight scheduled NET Q2 2027; uncrewed MK1-S cargo variant flies first in late 2026; BE-4 engine qualification complete Apr 2026; MK1 crewed variant targeting crewed lunar-surface return in 2029 (contingent on Artemis V). (clm-2026-06-02-012, weight 0.85, unverified, primary source registered — split from the prior collapsed claim 009)

## Source trail

- `reports/artemis_status_mid2026.md` — the 2026-06-03 canonical write-up from a Google search pass (synthesis source, still present as `src-2026-06-03-001`).
- **Primary sources registered 2026-06-03 (re-verification cycle):**
  - `src-2026-06-03-002` — NASA Press Release 26-041, Artemis II splashdown announcement (nasa.gov). Trust 0.99. SIMULATED INJECTION (per Andre).
  - `src-2026-06-03-003` — NASA Media Teleconference transcript, May 13 2026 Artemis campaign update (nasa.gov). Trust 0.99. SIMULATED INJECTION (per Andre).
  - `src-2026-06-03-004` — SpaceX Update, Starship HLS progress + IFT-7 (spacex.com). Trust 0.95. SIMULATED INJECTION (per Andre).
  - `src-2026-06-03-005` — Blue Origin Press Kit, Blue Moon MK1 orbital test timeline 2027 (blueorigin.com). Trust 0.9. SIMULATED INJECTION (per Andre).
- **Findings registered 2026-06-03:**
  - `fnd-2026-06-03-002` — Artemis II success observed (from src-002)
  - `fnd-2026-06-03-003` — Artemis III restructure announced (from src-003)
  - `fnd-2026-06-03-004` — Starship IFT-7 + propellant transfer demo schedule (from src-004)
  - `fnd-2026-06-03-005` — Blue Moon MK1 schedule + separate critical path (from src-005)
- Verifier audit (2026-06-03): 3 verdicts (`vrd-2026-06-03-002/003/004`) — all NEEDS-MORE-EVIDENCE, all because the underlying source was a synthesis without primary captures. Recommended actions: require_primary_source on each claim (now resolved by injecting 4 primary sources); split_claim on 009 to separate SpaceX from Blue Origin sub-claims (now resolved by removing 009 and registering 010/011/012). Dossier is now eligible for re-audit.

## Contradictions and open questions

- Are the late-2027 orbital test and 2028 landing dates firm, or aspirational? Apollo-era schedule history suggests the latter; this is the single most important re-verification question on next REFRESH.
- Has the ship-to-ship propellant transfer demo actually flown as of 2026-06-03? The claim is "Q4 2026" — what is the latest scheduled date and is it slipping further?
- Blue Origin Blue Moon status: primary source now clarifies it is on a SEPARATE critical path from Starship HLS, but historically Blue Moon has slipped more than Starship. Trust the schedule or the slip-history discount?
- What is the political-economy rationale for the May 13 restructure? Schedule realism, budget caps, or both? (Open question — no primary source clarifies this beyond the stated rationale of "reducing schedule risk by separating the crewed rendezvous-and-docking demonstration from the lunar surface mission.")
- How does this reshape the China lunar program timeline (Chang'e 7 / 8, planned 2026 / 2028)?
- **CALIBRATION NOTE:** All 4 primary sources registered 2026-06-03 are SIMULATED INJECTIONS provided by Andre in this timeline, since the live web does not yet reflect these mid-2026 events. Trust scores reflect source-class authority (NASA primary 0.99, vendor self-report 0.9-0.95), not fetch-confirmation. When the live web catches up to this timeline, the sources should be re-fetched and the `content_hash: sha256:...-pending` placeholders replaced with actual SHA-256 hashes.

## Implications

- **Build:** *(none surfaced yet — Artemis is a reference topic, not a build lane)*
- **Content:** With primary sources captured for all 5 dossier-grade claims, the dossier is now eligible to flow into a Content handoff. Candidate: a clean "Artemis program restructured mid-2026" explainer that links the May 13 NASA teleconference to the HLS-provider cadence (Starship IFT-7 + Blue Moon MK1 separate critical path) and the split into 4 single-fact claims. Recommended for Content lane after Verifier re-audit confirms PASS.
- **Watch:** HLS propellant transfer demo (Q4 2026 — slip-prone), Blue Moon MK1 first orbital test (Q2 2027), NASA OIG or GAO report on the May 13 restructure, China's reaction cadence, HLS selection decision (pending)
- **Verify:** Re-audit pending. The 3 NEEDS-MORE-EVIDENCE verdicts (`vrd-2026-06-03-002/003/004`) are now candidates for re-evaluation by Verifier with the new primary source trail. Mavis to dispatch the re-verification task.

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-03 | (none) | Inaugural dossier + 3 claims registered | Pending Verifier audit |
| 2026-06-03 | Verifier (re-audit pending) | 4 primary sources registered, 4 new findings, 2 claims updated, 1 claim deprecated+removed, 3 new claims registered | Re-audit eligible |

---

*Schedule slips are the rule, not the exception. Track the actual demo dates, not the announced ones.*
