# Auditor Brief — 2026-06-05 11:00 CT

> First thing Andre reads. Scannable. No padding.

## Calibration status

**System is live and operating on a fourth-cycle leg.** Live audit runs: `aud-2026-06-03-003` (Researcher dossier re-audit, artemis), `aud-builder-2026-06-05-001` (Builder Run #2 re-audit, post path-recovery), `aud-2026-06-05-001` (Researcher FDA 503A peptide dossier, inaugural), `aud-scribe-fda-substack-2026-06-05-001` (Scribe longform Substack post Fidelity Audit, FDA 503A peptide topic, 2,061 words).

## What was audited (2026-06-05 10:47–11:00 CT)

- `Scribe/drafts/fda-peptide-substack.md` (2,061-word longform Substack post, 7 H2s, FDA 503A peptide topic, target 1,800-2,200)
- Handoff: `Verifier/queue/scribe-verify-handoff.md` (19,015-byte claim manifest, structural-choice notes, discipline carry-forwards)
- Source dossier: `Researcher/dossiers/fda_503a_peptides.md` (dossier-PASS at 0.94, ground truth)
- Scribe contract: `~/.mavis/agents/scribe/agent.md` (5 stop-conditions; Run #1 + Run #2 discipline notes)

## What was found (2026-06-05 10:47–11:00 CT — Scribe longform Substack Fidelity Audit)

- **VERDICT: PASS** at weighted score **0.974** (highest of the run, above Builder's 0.951 and Scribe Run #1's 0.975). One verdict issued (artifact-level).
- The 12-name Category 2 removal enumeration is verbatim order-independent match against dossier clm-007. All 12 names present including the multi-clause 'GHK-Cu (for injectable routes of administration)' and 'Thymosin Beta-4, Fragment (LKKTETQ) (TB-500)'.
- The 7/12/13 disambiguation is in H2 #1 ('The 7, the 12, and the 13 — let's get the numbers straight'), not buried at the end. The 13 = 12 + GHK-Cu non-injectable from Cat 1 is explicit. The 'seven of the 12 ... on the July agenda' relationship is explicit in the same H2.
- Both adjudicated contradictions from the dossier audit (decision 2026-06-05-001 and 002) are cited correctly: (1) FDA-2025-N-6895 as authoritative, FDA-2026-N-2979 as 'stale snippet or typo'; (2) per-day FR meeting times as authoritative.
- All 7 July agenda peptides (4 on July 23, 3 on July 24) preserved verbatim with uses-evaluated (BPC-157 ulcerative colitis, KPV wound healing, TB-500 wound healing, MOTs-C obesity and osteoporosis on July 23; Emideltide opioid withdrawal / insomnia / narcolepsy, Semax cerebral ischemia / migraine / trigeminal neuralgia, Epitalon insomnia on July 24).
- All 5 second-meeting peptides (Cathelicidin LL-37, Dihexa Acetate, GHK-Cu injectable, PEG-MGF, Melanotan II) verbatim. PCAC quorum watch-item fully present (4 members, vacancies, no quorum, Kennedy authority to fill).
- All 6 elements of 503A conditions (fnd-010) present: USP/NF monograph, FDA-approved drug component, 503A bulks list, Section 510 registration, certificate of analysis, individually identified patient.
- FR notice metadata in dossier order: 91 FR 20465, document 2026-07361, published April 16, 2026, signed by Grace R. Graham, Deputy Commissioner for Policy, Legislation, and International Affairs.
- 'Use evaluated' disclaimer correctly framed as 'uses FDA reviewed for safety and effectiveness at the bulks-list evaluation stage, not approved indications and not on-label uses.'
- Verbatim quotes preserved: FDA 503A bulks page (Cat 1 enforcement discretion); Frier Levitt (2 quotes — enforcement discretion, API bottleneck); Orrick (2 quotes — API sourcing, 2024 PCAC precedent).
- Style discipline: 0 hype words across 25 patterns, 0 exclamation points, 0 emojis, 0 CTA phrases. 'Inflection point' allowed (dossier's own framing, in lede). 'Worst-case procedural outcome' allowed (description of quorum failure mode, in closing).
- Closing: H2 'The question that should be answered on July 24' is the chief-contract sharp question (behavior 3, not a CTA). Body articulates two implicit questions; final line is a closing, not a CTA.
- 7 adversarial probes (substring false-positive trap, vendor-owner smuggling, external knowledge smuggling, hidden numerical hallucinations, hidden date hallucinations, Biden-era framing, clinical characterization smuggling) all clean.
- Word count 2,061 (in 1,800-2,200 target). H2 count 7 (in 5-7 target). File in `published/` (MD5 4574f5aa49235324b8fb083d66a0c738 byte-identical to draft).
- 8 new findings appended to `knowledge/findings.jsonl`. 1 new verdict appended to `knowledge/verdicts.jsonl` (artifact-level). 1 new audit log entry appended.

## What was found (2026-06-05 10:25–10:42 CT — Researcher FDA 503A dossier, inaugural)

- **VERDICT: PASS** at weighted score **0.94** (dossier-level), 8 per-claim verdicts at 0.815–0.965.
- All 6 sources re-fetched independently by the Verifier; verbatim match with Researcher's captures on all 8 claims.
- The 7/12/13 number family (7 on July PCAC agenda, 12 removed from Category 2, 13 total removals including GHK-Cu non-injectable Cat 1) is load-bearing and correctly preserved. The 7/12 math is internally consistent: 7 + 5 (not on July) = 12 ✓; 12 + 1 (GHK-Cu non-injectable from Cat 1) = 13 ✓.
- The 2 surfaced contradictions adjudicated:
  1. **Docket-number inconsistency (FDA-2025-N-6895 vs FDA-2026-N-2979):** ADJUDICATE upholds Researcher's inference — FDA-2025-N-6895 is authoritative; FDA-2026-N-2979 is a copy-paste typo on the FDA meeting page Instructions paragraph. See `decisions/2026-06-05-001-docket-number.md`.
  2. **Meeting-time inconsistency (per-day FR times vs FDA meeting page top-line):** ADJUDICATE upholds Researcher's inference — FR per-day times are authoritative (July 23: 8am-4:30pm ET; July 24: 8am-3:50pm ET); FDA meeting page top-line 8am-3:50pm ET is a UI simplification. See `decisions/2026-06-05-002-meeting-time.md`.
- The PDF-as-binary edge case (fda.gov/media/94155/download) is correctly handled: the Researcher accepted secondary-corroboration across Frier Levitt + Orrick and downgraded clm-2026-06-05-007 to weight 0.92, with re-verify trigger preserved for next REFRESH. The Verifier independently re-fetched the PDF and confirmed the binary edge case.
- Stage discipline end-to-end: 6 raw captures, 11 findings, 8 claims, 1 dossier, 1 handoff, 1 run receipt. No collapsed stages, no in-place edits to prior ledgers.
- 2 ADJUDICATE decisions written to `decisions/`. 7 new findings appended to `knowledge/findings.jsonl`. 9 new verdicts appended to `knowledge/verdicts.jsonl` (8 per-claim + 1 dossier-level).

## What I recommend

- **For Mavis:** consume the FDA 503A peptide dossier handoff. The dossier is verified at the dossier level (PASS 0.94) and per-claim (8 PASS). The Scribe draft is verified at PASS 0.974 and has been moved to `published/` by the Verifier. The 7/12/13 number family was carried forward explicitly in the Scribe's H2 #1, as required by the parent brief. The 2 ADJUDICATE decisions are referenced in the Scribe's source-trail so a reader does not get confused by the FDA-2026-N-2979 reference on the FDA meeting page. The Scribe is now available for the next dispatch.
- **For Andre:** the FDA 503A peptide dossier is the Researcher's first non-aerospace dossier, and the inaugural FDA-regulation dossier. The PDF-as-binary edge case is a known and recurrent failure mode for webfetch-based source capture; the Researcher's mitigation (accept secondary-corroboration with weight reduction, flag re-verify on next REFRESH via a PDF parser) is the right shape. The 7/12/13 number-family discipline is the kind of careful distinction that prevents downstream Scribe confusion. The Scribe's longform Substack post is the Scribe's third PASS in a row (Run #1 0.975, Run #2 0.995, Run #3 0.974) and demonstrates the producer→trust loop working as designed: dossier → Verifier audit → Scribe manifest handoff → Verifier Fidelity Audit → published. The 2 contradictions surfaced (docket-number, meeting-time) are textbook examples of primary-source-disagreement that the rubric catches — both Researcher's inferences are correct, and the Scribe rendered them correctly.
- **For the Researcher agent contract:** carry forward the PDF-as-binary mitigation pattern. When `webfetch` returns raw binary for a PDF, the Researcher's three options are: (a) accept secondary-corroboration with weight downgrade (the current call for clm-007), (b) re-fetch via a PDF parser (pdftotext, pdf2text, or curl + binary-to-text), or (c) extract via a different source. Future REFRESH cycles should default to (b) for the 503A bulks PDF, which would upgrade clm-007 from weight 0.92 to ~0.99.
- **For the Scribe agent contract (Run #3 watch-item):** the H2 #4 'BPC-157, KPV, Semax — the most-asked-about peptides' framing is editorial labeling of an audience-aware inference from the parent brief (Audience: regulatory-aware practitioner). Defensible as a Scribe structural choice (selecting 3 of 7 to highlight), but recommended for future longform handoffs: explicitly flag this kind of editorial framing as a structural-choice so the Verifier can verify it is a label, not a fact-claim. Process observation, not discipline violation.

## What this audit is NOT

- Not a re-render of the Researcher's claimed demo. I re-fetched all 6 sources independently from the live URLs and confirmed verbatim match with Researcher's captures. The dossier's claims are not based on a snapshot of a demo; they are based on the live primary and secondary sources.
- Not a verdict on the substantive regulatory interpretation of the FDA's actions. The Verifier audits process and source — the regulatory interpretation is the Scribe's lane (or a policy analyst's lane if one exists).
- Not a judgment on the Researcher's or Scribe's character. The Researcher surfaced 2 contradictions and 1 PDF edge case explicitly; the Scribe surfaced its own structural-choice notes and ledger drops. Both shapes are correct — the alternative is to paper over and smuggle in.

## Score breakdown (FDA 503A peptide dossier, dossier-level)

| Criterion | Weight | Score | Note |
|-----------|--------|-------|------|
| source_quality | 0.25 | 0.96 | 4 primary sources (FR notice 91 FR 20465, FDA meeting page, FDA 503A bulks hub, Regulations.gov docket) backing 6 of 8 claims at 0.97–0.99; 2 claims (clm-007, clm-008) at 0.92 and 0.85 with secondary-corroboration; 12-name enumeration corroborated across 2 independent law-firm secondaries (Frier Levitt + Orrick) |
| cross_source_agreement | 0.20 | 0.93 | 4 distinct primaries + 2 independent law-firm secondaries; 1-to-many finding-to-claim structure for the 7-on-July claims (clm-003 + clm-004 share fnd-001/002 which is acceptable for legitimate granularity); 1 contradiction surfaced and adjudicated (docket-number), 1 surfaced and adjudicated (meeting-time) |
| stage_discipline | 0.20 | 0.92 | raw→finding→claim→dossier→handoff→run receipt chain preserved end-to-end; 6 raw captures, 11 findings, 8 claims, 1 dossier, 1 handoff, 1 run receipt; no collapsed stages; 1-to-many finding-to-claim structure acknowledged |
| freshness | 0.10 | 1.00 | dossier refresh 2026-06-05 10:15 CT, audit 2026-06-05 10:25–10:42 CT (within 30 min window); primary sources 2026-04-15 to 2026-05-14 (within 60 days) |
| process_compliance | 0.15 | 0.93 | Researcher's REFRESH-adjacent single-topic dossier build follows documented procedure; hard-constraint check explicit in run receipt; 2 contradictions routed to Verifier for adjudication, not papered over; PDF-as-binary edge case correctly handled |
| handoff_hygiene | 0.10 | 0.95 | handoff at correct location with full claim ledger, source trail, raw capture paths, rubric criteria, recommended action, needs-adjudication items; Researcher recommendation explicit and well-scoped |

Weighted: **0.94** (dossier-level); per-claim: 0.815–0.965.

## Files

- Verdicts: `knowledge/verdicts.jsonl#vrd-fda-503a-2026-06-05-001` through `vrd-fda-503a-2026-06-05-009` (8 per-claim + 1 dossier-level)
- Audit log: `knowledge/audit-log.jsonl#aud-2026-06-05-001`
- Findings: `knowledge/findings.jsonl#fnd-2026-06-05-001` through `fnd-2026-06-05-007` (7 supporting observations)
- ADJUDICATE decisions: `decisions/2026-06-05-001-docket-number.md`, `decisions/2026-06-05-002-meeting-time.md`
- Verifier raw captures: `raw/fda_regulation/2026-06-05/20260605-103000-vrf-*.json` (6 independent re-captures)
- Researcher handoff (incoming): `queue/researcher-verify-handoff.md`
- Researcher dossier (target): `dossiers/fda_503a_peptides.md`
- Researcher run receipt (referenced): `Researcher/runs/RUN-2026-06-05-fda-503a.md`
- Researcher audit dossier (updated): `dossiers/researcher-audit.md` (2026-06-05 signal appended)
- This audit's run receipt: `runs/RUN-20260605-1042Z.md`

## Audit-debt status

- Open NEEDS-MORE-EVIDENCE items: **0**
- Audit-debt cap: 25 — well within.
- Pending appeals: 0
- Stale-routing SLA windows: 0
- Re-verify triggers preserved in dossier: 5 (post-July-23-24 PCAC outcomes, second-meeting notice, enforcement discretion action, 503A bulks PDF re-fetch via PDF parser, docket comment count)

## What changed in trust posture (FDA 503A dossier)

- Inaugural FDA 503A peptide dossier is verified at the dossier level (PASS 0.94) and per-claim (8 PASS). The dossier is eligible to flow into the Scribe lane on Mavis dispatch.
- The 2 surfaced contradictions are adjudicated in `decisions/`. Both Researcher's inferences are upheld at weight 0.99.
- The 7/12/13 number family is correctly preserved. The most likely downstream Scribe confusion is mitigated.
- The PDF-as-binary edge case is correctly handled. Re-verify trigger preserved for next REFRESH.
- The "primary triangle" pattern (FR notice + FDA meeting page + Regulations.gov docket) is validated for any future FDA advisory committee meeting dossier.
- The Verifier's adversarial probes (alternate explanations for the docket-number, alternate explanations for the meeting-time) did not surface any new evidence that overrides Researcher's inferences. Both inferences are correct.

## Next audit

- Target: any new Researcher dossier that comes through the queue, OR a re-audit of an existing dossier if the Researcher triggers a re-verify (e.g., the 503A bulks PDF upgrade attempt).
- Watch-item: the next REFRESH cycle's handling of the 503A bulks PDF — if the Researcher successfully re-fetches via a PDF parser and the 12-name enumeration comes back primary-sourced, the weight upgrade from 0.92 to ~0.99 should be audited and a new verdict issued.
- Audit-debt is at 0; all 4 open per-claim re-verify triggers (post-July PCAC, second-meeting notice, enforcement discretion, PDF re-fetch) are future-state and will be re-audited on the appropriate trigger.
