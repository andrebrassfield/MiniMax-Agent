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
| 2026-06-03 | dossiers/ai_agents.md | PASS | 0.8025 | 3 high-weight claims (clm-2026-06-02-004, 005, 006) carry verified=false but are asserted as fact. Verification debt is concentrated; primary sources exist to resolve it. |

## Process compliance checks (per REFRESH)
- [ ] REFRESH steps ran in order (no skipped stages)
- [ ] Source quality scored per claim
- [ ] Cross-source agreement surfaced
- [ ] Claims ledger appended (not edited in place)
- [ ] Dossiers updated with new signal
- [ ] Verification queue routed
- [ ] Operator brief rewritten (not appended)
- [ ] Handoff lanes updated
- [ ] Wiki compiled
- [ ] Indexes rebuilt
- [ ] Health check run
- [ ] Run receipt written

## Audit cadence

- **Frequency:** every AUDIT cycle, sample-check 1-2 REFRESH run receipts
- **Floor:** at least one audit per 7 days
- **SLA on FAIL verdicts:** routed to `queue/researcher-verify-handoff.md` within 24h

## Source trail

- `verdicts.jsonl#vrd-2026-06-03-001` — calibration audit against `dossiers/ai_agents.md`. PASS at 0.8025 with three concentrated verification-debt findings.
- `findings.jsonl#fnd-2026-06-03-001..006` — supporting observations on stage discipline, cross-dossier reference, and routing state.
- `audit-log.jsonl#aud-2026-06-03-001` — calibration run receipt.
- Researcher's own: `dossiers/ai_agents.md` (target), `knowledge/claims.jsonl`, `knowledge/findings.jsonl`, `knowledge/sources.jsonl`, `runs/RUN-20260602-2143-REFRESH.md` (REFRESH that produced the dossier state).

## Audit-pattern notes

- **Verification-debt pattern**: when the Researcher's REFRESH extracts a finding and creates a claim, it writes the claim with `verified=false` (correct — findings ≠ claims). But the dossier prose often promotes unverified claims into "current signal" bullets without flagging the distinction. The fix is at the dossier-writing stage: bullets should carry a verification state in their citation (`(clm-... verified: false, src-... primary, trust 0.85)`) so the reader knows the claim is high-weight-but-unverified rather than confirmed.
- **Cross-dossier reference pattern**: `dossiers/ai_agents.md` cites `clm-2026-06-02-001` (dossier=frontier_ai) in its Implications section. Not wrong, but breaks the dossier-as-authoritative-per-topic model. Cleaner pattern: link to the frontier_ai dossier, which itself cites the claim.
