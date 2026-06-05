# Dossier — Researcher Audit

> Per-agent audit dossier. Tracks the Researcher's process discipline, common failure modes, and audit history.

## Why this agent is audited

The Researcher is Andre's evidence operator. Its claim ledger, dossier deltas, and handoff lanes are upstream of Mavis, Hermes, and every decision Andre makes on a research-implication. A research agent that smudges is a hallucination laundry with extra steps.

## What the Researcher does well
- **Dossier density.** `dossiers/ai_agents.md` carries 10 signal bullets, 9 primary sources, 4 routed handoffs, and an explicit contradiction surface. The "living topic file" pattern actually lives.
- **Contradiction surfacing.** Low-trust signals (geo.fkw.com GPT-6 rumor, sources.news Mythos mention, YouTube transcript Versept) are explicitly flagged and routed to verification queue / watch lane rather than smuggled in as established. This is the right shape.
- **Routing hygiene.** All five handoff routes from the 2026-06-02 REFRESH are recorded in a routing-history table with date, lane, item ID, and outcome state. Queue files exist for every route.
- **Source-tier discipline.** High-weight claims lean on primary sources (langchain.com, letta.com, anthropic.com, blog.google, arxiv.org). Secondary sources (whatllm, fazm, linas substack) are correctly weighted at 0.55–0.70 and used as corroboration, not as the spine.

## Common failure modes to watch
- **Hallucination laundry** — confident prose without separation between observed, claimed, and verified.
- **Source monoculture** — one lane producing 80% of signal.
- **Verification debt** — `queue/verification-review.md` growing unbounded.
- **Stale freshness** — operator brief claims "as of today" but the last REFRESH is 36h old.
- **Handoff drift** — handoff queues written but never read.
- **Wiki rot** — wiki pages link to dossiers that no longer exist.

## Recent audit signal (last 5 verdicts)

| Date | Target | Verdict | Score | Issue |
|------|--------|---------|-------|-------|
| 2026-06-05 | dossiers/fda_503a_peptides.md (dossier-level) | PASS | 0.940 | 8 per-claim PASS verdicts (mean 0.93); 7/12/13 number family correctly preserved; 2 contradictions adjudicated (docket, meeting time). PDF-as-binary edge case for 12-name enumeration correctly downgraded to weight 0.92. Inaugural FDA 503A dossier is verified and ready for Scribe dispatch. |
| 2026-06-05 | clm-2026-06-05-008 (second PCAC meeting before end of Feb 2027) | PASS | 0.815 | Forward-looking schedule claim, secondary-corroborated across Frier Levitt + Orrick; 5 not-on-July + GHK-Cu non-injectable from Cat 1. No primary PCAC meeting notice yet (must be published by Feb 2027). Re-verify trigger preserved. |
| 2026-06-05 | clm-2026-06-05-007 (12-peptide Category 2 removal enumeration) | PASS | 0.830 | Full 12-name enumeration is secondary-corroborated across Frier Levitt + Orrick; primary PDF returns as raw binary. 7-of-12 names indirectly primary-verified via FR notice. Weight 0.92 is correct discipline. Re-verify on next REFRESH by parsing the PDF. |
| 2026-06-05 | clm-2026-06-05-006 (Removal from Cat 2 ≠ 503A bulks list ≠ Cat 1) | PASS | 0.965 | FDA 503A bulks hub page verbatim confirms interim policy applies ONLY to Cat 1. Frier Levitt and Orrick both distinguish. 3-way corroboration. |
| 2026-06-05 | clm-2026-06-05-005 (7 peptides on 503A Bulks List inclusion, not Cat 1) | PASS | 0.965 | FR verbatim: 'inclusion on the 503A Bulks List'. Correctly distinguished from Cat 1 placement. |
| 2026-06-05 | clm-2026-06-05-004 (July 24 agenda: 3 peptides) | PASS | 0.965 | FR verbatim corroborates Emideltide/DSIP, Semax, Epitalon with uses-evaluated table. |
| 2026-06-05 | clm-2026-06-05-003 (July 23 agenda: 4 peptides) | PASS | 0.965 | FR verbatim corroborates BPC-157, KPV, TB-500, MOTs-C with uses-evaluated table. |
| 2026-06-05 | clm-2026-06-05-002 (per-day meeting times + location) | PASS | 0.965 | FR DATES section verbatim: July 23 8am-4:30pm ET; July 24 8am-3:50pm ET. FDA meeting page top-line is a UI simplification (adjudicated in decisions/2026-06-05-002-meeting-time.md). |
| 2026-06-05 | clm-2026-06-05-001 (FR notice 91 FR 20465 headline) | PASS | 0.965 | Federal Register primary notice confirmed verbatim. 3 independent sources (FR, FDA meeting page, Regulations.gov) all cite FDA-2025-N-6895. The FDA-2026-N-2979 reference on the FDA meeting page is a copy-paste typo (adjudicated in decisions/2026-06-05-001-docket-number.md). |
| 2026-06-03 | dossiers/artemis_program.md (dossier-level) | PASS | 0.8560 | 5 per-claim PASS verdicts; 3 prior NEEDS-MORE-EVIDENCE on clm-007/008/009 superseded. HUD badge can light up green. |

## Process compliance checks (per REFRESH)
- [x] REFRESH steps ran in order (no skipped stages) — for the re-audit capture cycle (sources, findings, claims, dossier, brief): all 5 succeeded. For the surrounding REFRESH discipline (raw capture, run receipt, wiki compile, source plan lane update): 4 of 12 process items still skipped; flagged as cross_cutting findings, not blocking per-claim PASS.
- [x] Source quality scored per claim — 4 new sources classified primary, trust 0.9-0.99, simulation flag noted
- [x] Cross-source agreement surfaced — single primary per claim, dossier-level corroboration noted
- [x] Claims ledger appended (not edited in place) — 2 claims updated (007/008 supporting_findings repointed), 1 deprecated (009), 3 new (010/011/012)
- [x] Dossiers updated with new signal — artemis_program.md rewritten (46→59 lines), no factual errors remaining
- [x] Verification queue routed — GPT-6 rumor still routed, artemis dossier no longer in queue
- [x] Operator brief rewritten (not appended) — addendum at lines 25-58 documents the entire re-audit cycle
- [x] Handoff lanes updated — dossier Implications: Content lane now eligible
- [ ] Wiki compiled — artemis dossier still has no wiki article
- [x] Indexes rebuilt — dossier is current
- [ ] Health check run — no new health check for the 2026-06-03 artemis pass
- [ ] Run receipt written — no `runs/RUN-2026-06-03-*.md` for the artemis pass; process gap from prior audit still open

## Audit signal — 2026-06-05 — FDA 503A peptide dossier (inaugural, vrd-fda-503a-2026-06-05-001)

- **Verdict:** PASS at weighted score 0.94 (dossier-level). 8 per-claim PASS verdicts issued; mean 0.93; 6 high-confidence at 0.965, 2 secondary-corroborated at 0.815–0.830.
- **What the Researcher did well on this dossier:**
  - **Number-family discipline.** The 7/12/13 number family (7 on July PCAC agenda, 12 removed from Category 2, 13 total removals including GHK-Cu non-injectable from Cat 1) is the most likely downstream Scribe confusion, and the dossier explicitly distinguishes all three counts in the "Contradictions" section. Verifier confirmed: 7 = 4 on July 23 + 3 on July 24 (FR verbatim, primary-captured). 12 = 12 names verbatim enumerated by Frier Levitt (and 7 of those 12 names are primary-captured via the FR notice; 5 are secondary-corroborated only). 13 = 12 from Cat 2 + 1 GHK-Cu non-injectable from Cat 1 (both Frier Levitt and Orrick confirm the separate actions). The math: 7 + 5 = 12 ✓; 12 + 1 = 13 ✓; 5 + 1 = 6 on second meeting ✓.
  - **Contradiction surfacing.** Both surfaced contradictions (docket-number, meeting-time) are routed to Verifier for adjudication, not papered over. The Researcher correctly inferred the most likely resolution (FDA-2025-N-6895 authoritative; FR per-day times authoritative) and explicitly flagged the second-tier possibility (parallel docket for docket-number; UI simplification for meeting-time). Verifier confirmed both inferences.
  - **PDF-as-binary edge case handled correctly.** When `fda.gov/media/94155/download` returned as raw binary, the Researcher did not attempt to extract the 12-name enumeration from the binary. Instead, the Researcher accepted secondary-corroboration across Frier Levitt and Orrick, downgraded clm-2026-06-05-007 to weight 0.92, and flagged re-verify on next REFRESH by re-fetching the PDF via a PDF parser. This is the right shape for the edge case — the Researcher did not hallucinate the 12 names, did not silently collapse the 7/12/13 distinction, and did not promote clm-007 to 0.99 on the basis of secondary sources.
  - **Stage discipline end-to-end.** 6 raw captures in `raw/fda_regulation/2026-06-05/`, 11 findings, 8 claims, 1 dossier, 1 handoff, 1 run receipt. No collapsed stages, no in-place edits to prior ledgers, no other-agent-vault touch.
  - **Hard constraints honored.** Explicit check in run receipt: no commit, no push, no external sends, no other-agent-vault touch, no Scribe/Builder/Mavis/Hermes/OpenClaw/kanban/gbrain lane activity. The Verifier handoff at `03 Projects/Verifier/queue/researcher-verify-handoff.md` is the standard Researcher→Verifier lane (allowed by the parent brief).
- **What the Verifier verified independently:**
  - Re-fetched all 6 sources (FR notice, FDA meeting page, FDA 503A bulks hub, Regulations.gov docket, Frier Levitt, Orrick/JD Supra) on 2026-06-05 ~10:25 CT and confirmed verbatim match with Researcher's captures on all 8 claims.
  - Re-fetched the 503A bulks PDF (`fda.gov/media/94155/download`) and confirmed it returns as raw binary (PDF 1.6 with embedded TrueType fonts and FlateDecode compression, not parseable as text via webfetch). The Researcher's edge-case handling is correct.
  - Adjudicated the 2 surfaced contradictions in `decisions/2026-06-05-001-docket-number.md` (FDA-2025-N-6895 authoritative) and `decisions/2026-06-05-002-meeting-time.md` (FR per-day times authoritative). Both uphold Researcher's inference.
- **Watch-items preserved in dossier (re-verify triggers):**
  1. After July 23-24, 2026: re-fetch FDA's PCAC outcomes and update dossier.
  2. When FDA publishes the second-meeting notice (before end of February 2027): update clm-2026-06-05-008 to primary-source registration.
  3. On any FDA action that extends enforcement discretion to one or more of the 12 peptides: high-priority re-verification of clm-2026-06-05-006.
  4. On the next REFRESH: re-fetch `fda.gov/media/94155/download` via a PDF parser (pdftotext, pdf2text) to upgrade clm-2026-06-05-007 from secondary-corroborated to primary-sourced.
  5. Watch the docket for additional public comments (currently 65 received as of 2026-06-05 10:25 CT).
- **Mavis routing:** Dossier is verified at the dossier level and per-claim. On Mavis dispatch, the Scribe should be free to render from the dossier. The 7/12/13 number family must be carried forward explicitly to prevent downstream confusion. The 2 decisions (docket-number, meeting-time) should be referenced in the Scribe's source-trail so a reader does not get confused by the FDA-2026-N-2979 reference on the FDA meeting page.
- **Audit-pattern note (carry-forward for future Researcher dossiers):**
  - **PDF edge case is a known and recurrent failure mode for webfetch-based source capture.** Mitigation pattern: (a) accept secondary-corroboration with weight downgrade (Researcher's call here, weight 0.92), or (b) re-fetch via a PDF parser (pdftotext, pdf2text, or curl + binary-to-text). Researcher chose (a) for clm-007. (b) should be tried on the next REFRESH. This generalizes to any future dossier involving FDA media files or other PDF primaries.
  - **The "primary triangle" pattern (FR notice + FDA meeting page + Regulations.gov docket) is highly efficient for any FDA advisory committee meeting.** All three cross-reference the same docket number and the same date/time/location, making cross-source agreement check very efficient. This generalizes to any future PCAC meeting handoff.
  - **Forward-looking schedule claims (clm-2026-06-05-008) inherently score lower than historical event claims (clm-2026-06-05-001 through 006).** The rubric's cross-source agreement criterion (0.20 weight) penalizes forward-looking claims because there is no primary capture of a future event. The Researcher correctly weighted clm-008 at 0.85 (lower than the 0.97-0.99 of historical claims) and the dossier preserves the re-verify trigger. This is the right shape.

## Audit cadence

- **Frequency:** every AUDIT cycle, sample-check 1-2 REFRESH run receipts
- **Floor:** at least one audit per 7 days
- **SLA on FAIL verdicts:** routed to `queue/researcher-verify-handoff.md` within 24h
- **Current state:** 0 audit debt (no NEEDS-MORE-EVIDENCE items pending); 9 new verdicts in `vrd-fda-503a-2026-06-05-001` series (8 per-claim PASS + 1 dossier-level PASS at 0.94) awaiting Mavis dispatch to Scribe; 0 superseded verdicts; 0 stale appeals; 2 ADJUDICATE decisions written and recorded.

## Source trail

- `verdicts.jsonl#vrd-2026-06-05-001` — FDA 503A peptide dossier audit, 9 verdicts (8 per-claim + 1 dossier-level), all PASS. aud-2026-06-05-001.
- `verdicts.jsonl#vrd-2026-06-03-001` — calibration audit against `dossiers/ai_agents.md`. PASS at 0.8025 with three concentrated verification-debt findings.
- `verdicts.jsonl#vrd-2026-06-03-002/003/004` — first artemis audit. NEEDS-MORE-EVIDENCE on clm-007/008/009. Superseded by re-audit (vrd-005/006/007/008/009/010). Audit history preserved.
- `verdicts.jsonl#vrd-2026-06-03-005/006/007/008/009/010` — re-audit pass. All 5 per-claim PASS (0.8175-0.88) + 1 dossier-level PASS (0.856). aud-2026-06-03-003.
- `verdicts.jsonl#vrd-builder-2026-06-05-001` — Builder Run #2 re-audit, PASS at 0.951. aud-builder-2026-06-05-001.
- `findings.jsonl#fnd-2026-06-05-001..007` — FDA 503A audit supporting observations (cross-source recapture, 12-peptide enumeration corroboration, second-meeting pending, docket-number adjudication, meeting-time adjudication, stage discipline, Researcher process compliance).
- `findings.jsonl#fnd-2026-06-03-001..006` — supporting observations on stage discipline, cross-dossier reference, routing state.
- `audit-log.jsonl#aud-2026-06-05-001` — FDA 503A peptide dossier audit (9 verdicts, all PASS).
- `audit-log.jsonl#aud-2026-06-03-001` — calibration run receipt.
- `audit-log.jsonl#aud-2026-06-03-002` — first artemis audit (3 verdicts, NEEDS-MORE-EVIDENCE).
- `audit-log.jsonl#aud-2026-06-03-003` — re-audit pass (6 verdicts, all PASS).
- `audit-log.jsonl#aud-builder-2026-06-05-001` — Builder Run #2 re-audit.
- `decisions/2026-06-05-001-docket-number.md` — ADJUDICATE decision on the FDA-2025-N-6895 vs FDA-2026-N-2979 docket-number contradiction. Upholds Researcher's inference (FDA-2025-N-6895 authoritative).
- `decisions/2026-06-05-002-meeting-time.md` — ADJUDICATE decision on the FR per-day times vs FDA meeting page top-line time contradiction. Upholds Researcher's inference (FR per-day times authoritative).
- Researcher's own: `dossiers/fda_503a_peptides.md` (audit target), `dossiers/ai_agents.md` (calibration target), `dossiers/artemis_program.md` (re-audit target), `knowledge/claims.jsonl` (21 records including 8 FDA), `knowledge/findings.jsonl` (44 records including 11 FDA), `knowledge/sources.jsonl` (36 records including 6 FDA), `runs/RUN-2026-06-05-fda-503a.md` (FDA dossier build run receipt), `runs/RUN-20260602-2143-REFRESH.md` (REFRESH that produced the prior dossier state).

## Audit-pattern notes

- **Verification-debt pattern**: when the Researcher's REFRESH extracts a finding and creates a claim, it writes the claim with `verified=false` (correct — findings ≠ claims). But the dossier prose often promotes unverified claims into "current signal" bullets without flagging the distinction. The fix is at the dossier-writing stage: bullets should carry a verification state in their citation (`(clm-... verified: false, src-... primary, trust 0.85)`) so the reader knows the claim is high-weight-but-unverified rather than confirmed.
- **Cross-dossier reference pattern**: `dossiers/ai_agents.md` cites `clm-2026-06-02-001` (dossier=frontier_ai) in its Implications section. Not wrong, but breaks the dossier-as-authoritative-per-topic model. Cleaner pattern: link to the frontier_ai dossier, which itself cites the claim.
- **NEEDS-MORE-EVIDENCE → PASS closure pattern (new, observed 2026-06-03)**: when a claim is NEEDS-MORE-EVIDENCE due to a single secondary-source synthesis (no primary captures), the resolution is not just "add a primary" — the dossier and ledger IDs must be re-anchored atomically, and the operator-brief should carry an "Addendum" section documenting the closure. The Researcher executed this cleanly for the artemis dossier: 4 new sources → 4 new findings → 2 claim updates + 1 deprecation + 3 new claims → dossier prose rewrite (46→59 lines) → operator-brief addendum. The internal factual error from the first audit (line 20 "fnd-artemis-2026-06-03-001" + "not yet present in findings.jsonl") was fixed as a side effect. This is the right shape for a NEEDS-MORE-EVIDENCE → PASS closure.
- **1-to-many finding-to-claim structure (new, observed 2026-06-03)**: fnd-2026-06-03-004 (Starship IFT-7 + propellant transfer demo) supports both clm-010 (IFT-7 event) and clm-011 (propellant transfer demo schedule). The dossier-as-authoritative-per-topic convention prefers 1-to-1, but 1-to-many is acceptable when the underlying fact structure warrants it (a single SpaceX update covers both the IFT-7 event and the propellant transfer demo schedule). Verifier accepts the deviation; the stage_discipline score is downgraded by 0.15 to reflect the structural difference.
- **Process-gap persistence pattern (carry-forward from vrd-2026-06-03-002/003/004)**: 4 process items remain open across the re-audit cycle: (1) no raw capture in `raw/aerospace/`; (2) no run receipt for the 2026-06-03 artemis pass; (3) `aerospace` source lane not in `context/source-plan.md`; (4) no wiki article for artemis dossier. These are structural REFRESH-step gaps, not claim-level evidence gaps, so they do not block per-claim verdicts. The Researcher should treat them as a backlog to clear on the next REFRESH. Recommendation: add a "Process compliance — REFRESH steps" checklist to the operator-brief so the gaps are visible at every cycle, not just at audit time.
