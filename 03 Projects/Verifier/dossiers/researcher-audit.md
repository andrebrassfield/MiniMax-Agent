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
| 2026-06-03 | dossiers/artemis_program.md (dossier-level) | PASS | 0.8560 | 5 per-claim PASS verdicts; 3 prior NEEDS-MORE-EVIDENCE on clm-007/008/009 superseded. HUD badge can light up green. |
| 2026-06-03 | clm-2026-06-02-012 (Blue Moon MK1 separate critical path) | PASS | 0.8550 | New claim from 009 split. Primary Blue Origin source in trail. Narrowest of 5 by 0.005 above 011. |
| 2026-06-03 | clm-2026-06-02-011 (propellant transfer demo Q4 2026) | PASS | 0.8175 | New claim from 009 split. Narrowest of 5 PASS at 0.0175 above 0.80. Forward-looking schedule claim. |
| 2026-06-03 | clm-2026-06-02-010 (Starship IFT-7 May 27 2026) | PASS | 0.8475 | New claim from 009 split. Primary SpaceX source in trail. |
| 2026-06-03 | clm-2026-06-02-008 (Artemis III restructured May 13 2026) | PASS | 0.8800 | Re-audit of prior NEEDS-MORE-EVIDENCE. NASA primary in trail. Supersedes vrd-2026-06-03-003. |
| 2026-06-03 | clm-2026-06-02-007 (Artemis II flew Apr 1 2026) | PASS | 0.8800 | Re-audit of prior NEEDS-MORE-EVIDENCE. NASA primary in trail. Supersedes vrd-2026-06-03-002. |
| 2026-06-03 | dossiers/ai_agents.md | PASS | 0.8025 | 3 high-weight claims (clm-2026-06-02-004, 005, 006) carry verified=false but are asserted as fact. Verification debt is concentrated; primary sources exist to resolve it. |

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

## Audit cadence

- **Frequency:** every AUDIT cycle, sample-check 1-2 REFRESH run receipts
- **Floor:** at least one audit per 7 days
- **SLA on FAIL verdicts:** routed to `queue/researcher-verify-handoff.md` within 24h
- **Current state:** 0 audit debt (no NEEDS-MORE-EVIDENCE items pending); 6 new verdicts in handoff lane awaiting Researcher consumption; 3 superseded verdicts retained for audit history

## Source trail

- `verdicts.jsonl#vrd-2026-06-03-001` — calibration audit against `dossiers/ai_agents.md`. PASS at 0.8025 with three concentrated verification-debt findings.
- `verdicts.jsonl#vrd-2026-06-03-002/003/004` — first artemis audit. NEEDS-MORE-EVIDENCE on clm-007/008/009. Superseded by re-audit (vrd-005/006/007/008/009/010). Audit history preserved.
- `verdicts.jsonl#vrd-2026-06-03-005/006/007/008/009/010` — re-audit pass. All 5 per-claim PASS (0.8175-0.88) + 1 dossier-level PASS (0.856). aud-2026-06-03-003.
- `findings.jsonl#fnd-2026-06-03-001..006` — supporting observations on stage discipline, cross-dossier reference, routing state.
- `audit-log.jsonl#aud-2026-06-03-001` — calibration run receipt.
- `audit-log.jsonl#aud-2026-06-03-002` — first artemis audit (3 verdicts, NEEDS-MORE-EVIDENCE).
- `audit-log.jsonl#aud-2026-06-03-003` — re-audit pass (6 verdicts, all PASS).
- Researcher's own: `dossiers/ai_agents.md` (calibration target), `dossiers/artemis_program.md` (re-audit target), `knowledge/claims.jsonl` (13 records), `knowledge/findings.jsonl` (37 records), `knowledge/sources.jsonl` (30 records), `runs/RUN-20260602-2143-REFRESH.md` (REFRESH that produced the prior dossier state).

## Audit-pattern notes

- **Verification-debt pattern**: when the Researcher's REFRESH extracts a finding and creates a claim, it writes the claim with `verified=false` (correct — findings ≠ claims). But the dossier prose often promotes unverified claims into "current signal" bullets without flagging the distinction. The fix is at the dossier-writing stage: bullets should carry a verification state in their citation (`(clm-... verified: false, src-... primary, trust 0.85)`) so the reader knows the claim is high-weight-but-unverified rather than confirmed.
- **Cross-dossier reference pattern**: `dossiers/ai_agents.md` cites `clm-2026-06-02-001` (dossier=frontier_ai) in its Implications section. Not wrong, but breaks the dossier-as-authoritative-per-topic model. Cleaner pattern: link to the frontier_ai dossier, which itself cites the claim.
- **NEEDS-MORE-EVIDENCE → PASS closure pattern (new, observed 2026-06-03)**: when a claim is NEEDS-MORE-EVIDENCE due to a single secondary-source synthesis (no primary captures), the resolution is not just "add a primary" — the dossier and ledger IDs must be re-anchored atomically, and the operator-brief should carry an "Addendum" section documenting the closure. The Researcher executed this cleanly for the artemis dossier: 4 new sources → 4 new findings → 2 claim updates + 1 deprecation + 3 new claims → dossier prose rewrite (46→59 lines) → operator-brief addendum. The internal factual error from the first audit (line 20 "fnd-artemis-2026-06-03-001" + "not yet present in findings.jsonl") was fixed as a side effect. This is the right shape for a NEEDS-MORE-EVIDENCE → PASS closure.
- **1-to-many finding-to-claim structure (new, observed 2026-06-03)**: fnd-2026-06-03-004 (Starship IFT-7 + propellant transfer demo) supports both clm-010 (IFT-7 event) and clm-011 (propellant transfer demo schedule). The dossier-as-authoritative-per-topic convention prefers 1-to-1, but 1-to-many is acceptable when the underlying fact structure warrants it (a single SpaceX update covers both the IFT-7 event and the propellant transfer demo schedule). Verifier accepts the deviation; the stage_discipline score is downgraded by 0.15 to reflect the structural difference.
- **Process-gap persistence pattern (carry-forward from vrd-2026-06-03-002/003/004)**: 4 process items remain open across the re-audit cycle: (1) no raw capture in `raw/aerospace/`; (2) no run receipt for the 2026-06-03 artemis pass; (3) `aerospace` source lane not in `context/source-plan.md`; (4) no wiki article for artemis dossier. These are structural REFRESH-step gaps, not claim-level evidence gaps, so they do not block per-claim verdicts. The Researcher should treat them as a backlog to clear on the next REFRESH. Recommendation: add a "Process compliance — REFRESH steps" checklist to the operator-brief so the gaps are visible at every cycle, not just at audit time.
