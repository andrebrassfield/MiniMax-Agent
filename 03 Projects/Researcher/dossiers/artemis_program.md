# Dossier — Artemis Program

> Living topic file. NASA's crewed lunar exploration program — current mission cadence, architectural shifts, and commercial Human Landing System (HLS) provider status.

## Why this topic matters to Andre

The Artemis program is the canonical signal for the public-private crewed spaceflight lane: how NASA sequences flagship missions, how it contracts commercial HLS providers (SpaceX, Blue Origin), and how schedule slips propagate through the launch industry. Andre follows adjacent industry signal — launch cadence, hardware milestones, government program restructuring — because the same dynamics (vendor lock-in, public-private risk allocation, schedule realism vs. political pressure) echo through the SaaS/agentic systems he ships. Mid-2026 is a structurally interesting moment: a successful crewed lunar flyby has happened, and the original lunar-landing architecture has been openly re-planned. That kind of mid-program pivot is rare and worth tracking.

## Current signal (last refresh: 2026-06-03)

3 dossier-grade claims registered today from the Google search pass:

- **Artemis II flew.** NASA launched the Artemis II crewed lunar flyby on April 1, 2026. 10-day mission, four astronauts, lunar free-return trajectory, splashdown recovery. First crewed mission beyond LEO since Apollo. (clm-2026-06-02-007, weight 0.99, unverified)
- **Artemis III is now an orbital docking test, not a landing.** Announced May 13, 2026. Orion + SLS, rendezvous and docking with commercial HLS (SpaceX Starship HLS, Blue Origin Blue Moon) in Earth orbit, targeted for late 2027. The lunar-surface return has been pushed to Artemis IV (~2028). (clm-2026-06-02-008, weight 0.98, unverified)
- **HLS providers are racing the new 2027 orbital deadline.** SpaceX completed a Starship flight test in late May 2026 and is targeting ship-to-ship propellant transfer tests later in 2026 to qualify Starship HLS. Blue Origin (Blue Moon) is on a parallel track. (clm-2026-06-02-009, weight 0.85, unverified)

## Source trail

- `reports/artemis_status_mid2026.md` — the 2026-06-03 canonical write-up from a Google search pass (no primary-source verification performed by Researcher yet).
- Findings: `fnd-2026-06-03-001` (referenced by all 3 claims; present in `knowledge/findings.jsonl` as a secondary-type synthesis with `src-2026-06-03-001` as the backing source — both written by Mavis to complete the chain after the Researcher's spec-only registration).
- Verifier audit (2026-06-03): 3 verdicts (`vrd-2026-06-03-002/003/004`) — all NEEDS-MORE-EVIDENCE, all because the underlying source is a synthesis without primary captures. Recommended actions: require_primary_source on each claim; split_claim on 009 to separate SpaceX from Blue Origin sub-claims.

## Contradictions and open questions

- Are the late-2027 orbital test and 2028 landing dates firm, or aspirational? Apollo-era schedule history suggests the latter; this is the single most important re-verification question on next REFRESH.
- Has the ship-to-ship propellant transfer demo actually flown as of 2026-06-03? The claim is "later in 2026" — what is the latest scheduled date and is it slipping?
- Blue Origin Blue Moon status is described at the same level as Starship HLS, but the public cadence is much quieter. Is Blue Moon on a parallel critical path or a backup?
- What is the political-economy rationale for the May 13 restructure? Schedule realism, budget caps, or both?
- How does this reshape the China lunar program timeline (Chang'e 7 / 8, planned 2026 / 2028)?

## Implications

- **Build:** *(none surfaced yet — Artemis is a reference topic, not a build lane)*
- **Content:** *(possible — clean "Artemis program restructured mid-2026" explainer; wait for primary-source verification before publishing)*
- **Watch:** HLS propellant transfer demo, Blue Moon schedule slips, any official NASA OIG or GAO report on the May 13 restructure, China's reaction cadence
- **Verify:** All 3 claims need primary-source confirmation — NASA press release for Artemis II success, NASA announcement for May 13 restructure, SpaceX/Blue Origin official statements for HLS status

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-03 | (none) | Inaugural dossier + 3 claims registered | Pending Verifier audit |

---

*Schedule slips are the rule, not the exception. Track the actual demo dates, not the announced ones.*
