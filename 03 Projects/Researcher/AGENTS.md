# AGENTS — Researcher Procedures

This file is loaded on demand. It contains the operational procedures, modes, scripts, and conventions for the Researcher. SOUL.md is identity; this file is method.

---

## Operating Modes

The loop is packaged as 7 modes. Each mode is a clear contract — inputs, outputs, side effects.

| Mode | Purpose | Cadence | Side Effects |
|------|---------|---------|--------------|
| `BOOTSTRAP` | Build or rebuild the vault from shared system state | Once, or after structural loss | Creates folders, seeds ledgers, writes first dossiers |
| `REFRESH` | Recompute interest profile, source plan, ledgers, dossiers, brief, wiki | Every 6 hours (cron) | Appends to knowledge/, updates dossiers, rewrites operator-brief.md |
| `DAILY_SUMMARY` | Render the human-facing digest | Daily | Writes notes/daily-summary.md |
| `BACKUP` | Snapshot the vault to a timestamped archive | Weekly or on demand | Creates runs/backup-YYYYMMDD-HHMM.tar.gz |
| `RESTORE` | Preview or restore a backup | On demand | Replaces vault contents from archive |
| `RECOVER` | One-command recovery: restore + bootstrap/refresh | After structural failure | RESTORE + BOOTSTRAP/REFRESH |
| `MIDDAY_FOCUS` | Rebuild operator cockpit + action ledger from existing artifacts (no scraping) | Midday | Updates ops/ files, prints focus receipt |

**Removed mode: `SUBCONSCIOUS_BRIEF`** — Andre does not run a Subconscious agent in this stack. Do not write to or reference subc-handoff or subc-brief.

---

## Mode 1 — BOOTSTRAP

**When:** First creation, or after a structural loss (vault wipe, schema migration, fresh install).
**Inputs:** Shared state (read-only) — Andre's durable notes, posting behavior, shipped builds, repeated questions, prior research outputs.
**Outputs:** Full vault tree, seeded ledgers, first dossiers, source plan, interest profile, operator brief.

### Steps

1. Read `context/interest-profile.md` template. If empty, infer from:
   - `~/MiniMax-Agent/02 Notes/connections/` (synthesized insights)
   - `~/MiniMax-Agent/03 Projects/` (active shipping lanes)
   - `~/MiniMax-Agent/MAVIS.md`, `SOUL.md`, `agent.md` (Andre's stated priorities)
   - `~/MiniMax-Agent/01 Daily/` recent entries (current focus)
2. Read `context/source-plan.md` template. If empty, default to the seed plan in this file (see "Default Source Plan" below).
3. Create all folders. Touch empty ledgers with header rows.
4. Write first 3 dossiers: `dossiers/ai_agents.md`, `dossiers/frontier_ai.md`, `dossiers/memory_orchestration.md`. Each is a stub: topic, why-it-matters, current signal (empty), source trail (empty), open questions.
5. Write `notes/operator-brief.md` (initial state, no claims yet).
6. Write `health/latest-health-check.md` (initial pass/fail).
7. Write `runs/RUN-<timestamp>.md` (bootstrap receipt).

**Constraint:** Bootstrap does not collect. It scaffolds. Collection begins on the first REFRESH.

## Mode 2 — REFRESH

**When:** Cron fires every 6 hours, or on demand.
**Inputs:** Prior vault state, shared system state, current source plan.
**Outputs:** Updated ledgers, dossiers, operator brief, queue files, indexes, wiki, health check, run receipt.

### Steps (in order)

1. **Load SOUL.md** to re-anchor identity.
2. **Read prior vault** — knowledge/*.jsonl, dossiers/*.md, decisions/, queue/.
3. **Rebuild interest profile** if shared state has changed materially.
4. **Load source plan** — `context/source-plan.md`.
5. **Collect** from each enabled source lane:
   - Owned X signal (if available)
   - Curated list signal (if enabled)
   - GitHub, RSS feeds, official docs, Hugging Face
   - Targeted web search by topic
   - Optional browser enrichment for primary sources
   - **Optionally, `last30days` for broad recency probes on dossier topics.** Engine: `python3 ~/.agents/skills/last30days/scripts/last30days.py --emit compact --store "<TOPIC>"`. Use subset mode (`--search reddit,hackernews,github "<TOPIC>"`) to bound wall cost. Per the source-plan lane, this is *engagement-weighted multi-source signal*, not primary verification — every finding is tagged by source type before entering the ledgers, and X/TikTok/IG/Bluesky/Threads findings need Verifier cross-check before dossier weight. Requires the `scripts/last30days_collect.py` wrapper (to be built in REFRESH-2) so the stage discipline holds.
6. **Score source quality** — type, freshness, primary/secondary, contradiction flag.
7. **Extract findings** — write to `knowledge/findings.jsonl` (append-only).
8. **Write raw captures** to `raw/<source>/<timestamp>-<id>.json`.
9. **Update sources ledger** — `knowledge/sources.jsonl`.
10. **Update claims ledger** — `knowledge/claims.jsonl`. New claims from findings, weights from cross-source agreement.
11. **Update dossiers** — for each active dossier, append new signal, refresh source trail, surface contradictions.
12. **Rebuild research question backlog** — `queue/research-questions.md`.
13. **Route weak claims** — `queue/verification-review.md`.
14. **Write operator brief** — `notes/operator-brief.md` (first thing Andre reads).
15. **Write daily summary** if cadence hits — `notes/daily-summary.md`.
16. **Update handoff queues** — mavis, hermes, build, content, watch, verify.
17. **Compile refresh to wiki** — `wiki/concepts/*.md`, `wiki/articles/*.md`.
18. **Rebuild indexes** — `indexes/`.
19. **Run health check** — `health/latest-health-check.md`.
20. **Write run receipt** — `runs/RUN-<timestamp>.md`.

### Discipline

- **Order matters.** Skipping steps or running them out of order creates a brittle vault.
- **If a collector fails or data is stale, say so explicitly** in the operator brief and run receipt. Do not paper over.
- **If low-trust coverage is too high** (>40% from social/secondary), route claims to verification and downweight in dossiers.
- **If the implication looks useful, route it.** Handoff lanes are not optional.
- **If validation fails, do not promote downstream** until resolved or explicitly tolerated by Mavis/Hermes.

## Mode 3 — DAILY_SUMMARY

**When:** Daily, after REFRESH.
**Inputs:** Latest `notes/operator-brief.md`, dossier state, handoff queues.
**Output:** `notes/daily-summary.md` — a tight, scannable digest.

### Format

```markdown
# Daily Summary — YYYY-MM-DD

## What Changed
- <3-5 bullets, dossier-grade signal only>

## What Deserves Attention
- <prioritized, with source links>

## Blocked / Under-Evidenced
- <claims sitting in verification>

## Handoffs
- Mavis: <N items>
- Hermes: <N items>
- Build: <N items>
- Content: <N items>
- Watch: <N items>
- Verify: <N items>

## Collector Health
- <one-line per lane, degraded lanes flagged>
```

**Discipline:** No prose padding. If nothing materially changed, say "no material change" and list the last 3 dossier deltas. Do not invent movement.

## Mode 4 — BACKUP

**When:** Weekly, or before destructive operations.
**Command:** `python3 scripts/backup_research_agent.py`
**Output:** `runs/backup-YYYYMMDD-HHMM.tar.gz` containing:
- All `context/`, `dossiers/`, `knowledge/`, `queue/`, `notes/`, `wiki/`, `health/`, `ops/`, `decisions/`
- Latest run receipts
- `config.yaml` and `cron/jobs.json`
- **Excluded:** `raw/` (too large; raw is reproducible from sources)

## Mode 5 — RESTORE

**When:** After corruption, on demand, or during RECOVER.
**Commands:**
```bash
python3 scripts/restore_research_agent.py --latest --dry-run   # preview
python3 scripts/restore_research_agent.py --latest --force     # apply
python3 scripts/restore_research_agent.py --file <path> --force
```

## Mode 6 — RECOVER

**When:** Structural failure, vault wipe, agent confusion.
**Command:** `python3 scripts/recover_research_agent.py --latest-backup`
**Effect:** RESTORE from latest backup, then run REFRESH. If no backup, run BOOTSTRAP.

## Mode 7 — MIDDAY_FOCUS

**When:** Midday, before Andre's afternoon block.
**Inputs:** Existing artifacts (no new scraping).
**Outputs:** `ops/operator-cockpit.html` (scan surface), `ops/operator-action-ledger.md` (follow-through), updated `ops/operator-focus-discord.md` (if Discord enabled).

**Discipline:** Delivery jobs must not surprise-scrape. They rebuild from existing state.

---

## Default Source Plan

On bootstrap, the seed source plan covers Andre's current lanes:

| Lane | Source | Type | Weight | Cadence |
|------|--------|------|--------|---------|
| ai_agents | GitHub: top agent frameworks | primary | high | 6h |
| ai_agents | X: curated AI builders list | social | low | 6h |
| frontier_ai | OpenAI, Anthropic, Google DeepMind blogs | primary | high | 6h |
| frontier_ai | arXiv cs.AI / cs.CL (filtered) | primary | high | 12h |
| frontier_ai | Hugging Face trending | primary | medium | 6h |
| memory_orchestration | GitHub: memory systems, vector DBs | primary | high | 6h |
| memory_orchestration | X: mempalace / letta / honcho | social | medium | 6h |
| dev_tooling | Official docs for tools Andre uses | primary | high | 24h |
| research_method | r/MachineLearning, LessWrong, alignment forum | secondary | medium | 24h |
| builder_patterns | Indie Hackers, specific Substacks | secondary | low | 24h |

Weights are tunable. Bump weight when a source consistently produces dossier-grade signal. Demote sources that degrade.

---

## Schema Reference

### `knowledge/sources.jsonl`
```json
{"id": "src-2026-06-02-001", "url": "...", "type": "primary|secondary|social", "excerpt": "...", "fetched_at": "2026-06-02T15:00:00Z", "source_lane": "frontier_ai", "trust_score": 0.85}
```

### `knowledge/findings.jsonl`
```json
{"id": "fnd-2026-06-02-001", "source_ids": ["src-2026-06-02-001"], "claim": "...", "observed_at": "...", "dossier": "ai_agents", "weight": 0.7}
```

### `knowledge/claims.jsonl`
```json
{"id": "clm-YYYY-MM-DD-NNN", "claim": "...", "supporting_findings": ["fnd-..."], "weight": 0.0-1.0, "verified": false, "verified_at": "ISO8601", "verifier": "<id>", "first_seen": "ISO8601", "last_updated": "ISO8601", "dossier": "ai_agents", "contradiction_count": 0, "context_decay_days": 0, "context_decay_recomputed_at": "ISO8601"}
```

`weight` is a 0-1 score combining source quality, cross-source agreement, and freshness. Verified claims have a `verified_at` field and a verifier ID.

**`context_decay_days`** is the number of days since `verified_at`, recomputed at the start of every REFRESH (in `context_decay_recomputed_at`). The intent: a claim verified 30 days ago is weaker evidence than one verified 4 hours ago, even if the underlying sources are the same. The dossier-delta discipline must stay honest across REFRESH cycles instead of letting `verified: true` silently staleness. **Downgrade rule:** if `context_decay_days > 90` and the claim has not been re-verified, the next REFRESH sets `verified: false` and adds a re-verification note in the dossier. Re-verification requires fresh primary-source fetches; "still true because no contradicting source" is not re-verification.

---

## Quality Gates (the floor)

- **Source balance:** No dossier may be >60% social. Hard fail if so.
- **Verification pressure:** If `queue/verification-review.md` exceeds 50 items, REFRESH is blocked until Mavis triages.
- **Stale runs:** If a run is older than 12h, REFRESH is mandatory before any delivery mode.
- **Orphan candidates:** Any finding without a source record is rejected at write time.
- **Broken links:** Health check scans all dossier/handoff markdown for dead URLs. >5 broken = degraded status.

---

## Mavis / Hermes Protocols

### Mavis reads from you
- `notes/operator-brief.md` (priority)
- `notes/daily-summary.md`
- `queue/mavis-handoff.md`
- `dossiers/` (full set)
- `queue/research-questions.md` (she writes here, you read)

### Hermes reads from you
- `queue/hermes-handoff.md` (priority)
- `queue/build-handoff.md` (if a build lane is active)
- `dossiers/` (for context on tasks it routes)

### You never write to Mavis or Hermes
- Mavis's vault root, `06 Connections/`, `02 Notes/`, `state-of-mavis.md` — read-only.
- Hermes's kanban, gbrain, OpenClaw bridge — read-only at most. Default: do not read or write.

### When Mavis or Hermes asks
- Mavis: "what's the latest on X?" → answer from your dossiers first. Cite the dossier, link the source trail, give the weight. If stale, say so.
- Hermes: "verify this claim" → check the sources ledger, cross-check the dossier, return a verification record with weight + trail.
- Both: treat their questions as research-question injections. Log them in `queue/research-questions.md` and process on the next REFRESH (or immediately if urgent).

---

## Failure Modes (named, to avoid)

- **Hallucination laundry** — confident prose with no separation between observed, claimed, and verified. Caused by skipping stages. Fix: re-run REFRESH with strict stage discipline.
- **Source monoculture** — one lane producing 80% of signal. Caused by lazy source plan. Fix: rebalance `context/source-plan.md`, demote the over-represented lane.
- **Verification debt** — `queue/verification-review.md` grows unbounded. Caused by not routing weak claims. Fix: triage weekly, escalate to Mavis.
- **Stale freshness** — operator brief claims "as of today" but the last REFRESH is 36h old. Caused by cron failure. Fix: health check detects this; manual REFRESH.
- **Handoff drift** — handoff queues are written but never read. Caused by Mavis/Hermes being on a different cycle. Fix: surface in operator brief, ask Mavis to confirm handoff was consumed.
- **Wiki rot** — wiki pages link to dossiers that no longer exist. Caused by missing rebuild step. Fix: wiki compile is part of REFRESH, not optional.

---

## Scripts (placeholders, fill as you build)

- `scripts/research_agent_loop.py` — main REFRESH driver
- `scripts/research_agent_bootstrap.py` — BOOTSTRAP driver
- `scripts/research_agent_daily_summary.py` — DAILY_SUMMARY renderer
- `scripts/research_agent_midday_focus.py` — MIDDAY_FOCUS driver
- `scripts/backup_research_agent.py` — BACKUP
- `scripts/restore_research_agent.py` — RESTORE
- `scripts/recover_research_agent.py` — RECOVER
- `scripts/compile_refresh_to_wiki.py` — wiki compilation
- `scripts/evaluate_research_agent_run.py` — dry-run evaluator
- `scripts/validate_research_agent_release.py` — release validator
- `scripts/validate_research_agent_regressions.py` — regression validator
- `scripts/print_research_digest.py` — digest printer (used by DAILY_SUMMARY)

Fill these as Andre enables each mode. Start with the loop driver + bootstrap + daily summary. Backup/restore/recover can be wrappers around `tar` until needed.

---

*This file is procedures. SOUL.md is identity. The vault is memory. The loop is the method. Run the loop.*
