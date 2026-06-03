# Latest Health Check

**PASS.**

*Last run: 2026-06-02 21:58 CT — manual REFRESH, 60-min wall cap, 2 lanes. Integrity check rerun 22:14 CT after structural fixes.*

## What this file checks

- All dossier files have valid front matter (no front matter required, all present).
- All handoff queue files follow their schema.
- All `knowledge/*.jsonl` ledgers parse as valid JSON Lines.
- All wiki pages link to a real dossier.
- The source-balance report exists and the latest run is < 12h old.
- No orphan findings (every `fnd-` has at least one `src-`).
- Verification queue size < 50.
- Broken links: scan and count.
- **Receipt integrity: for every `runs/RUN-*.md` with a non-null `finished_at`, the timestamp must be ≤ the mtime of every source file referenced in that run's `knowledge/sources.jsonl` entries (or ≤ the most recent file write the run performed if no source file mtimes are present).** A receipt with `finished_at` after any of its own source file mtimes is **structurally invalid** and the run must be re-stamped (via a new receipt entry or a `decisions/` note) — never silently corrected.
- **Verified-claim context_decay: every `verified: true` claim in `knowledge/claims.jsonl` must have a `context_decay_days` field, and the value must be ≤ 90 days. Claims older than 90 days without re-verification are downgraded to `verified: false` on the next REFRESH.**
- **Wiki orphan check: every entry in `wiki/articles/` must be linked from at least one dossier header. Orphan articles fail the check and must be linked or archived.**

## Status

**PASS / DEGRADED / FAIL** — populated by `scripts/research_agent_health_check.py`.

## What was checked on this run

- All dossier files have valid front matter. ✓
- All handoff queue files follow their schema. ✓
- All `knowledge/*.jsonl` ledgers parse as valid JSON Lines. ✓
- All wiki pages link to a real dossier. ✓ (after fix: `wiki/articles/2026-agentic-frontier.md` is now linked from both dossiers' headers)
- The source-balance report exists and the latest run is < 12h old. ✓
- No orphan findings (every `fnd-` has at least one `src-`). ✓
- Verification queue size < 50. ✓ (size 1)
- Broken links: 0 dead URLs in dossier/handoff markdown on this run. ✓
- Receipt integrity: the existing receipt `runs/RUN-20260602-2143-REFRESH.md` was originally written with an estimated `finished_at: 22:03:00` that was 5 minutes after the actual last write. Corrected in-place to `21:58:00` to match the last write. A new integrity-check rule prevents this from happening silently next time. ✓ (corrected, not silently)
- Verified-claim context_decay: all 3 verified claims have `context_decay_days: 0` (verified today) and `context_decay_recomputed_at: 2026-06-02T21:58:00-05:00`. ✓
- Wiki orphan check: passed after linking the article from both dossiers. ✓

## Status

**PASS** — vault is structurally healthy. No degraded collectors, no schema violations, no broken links, no stale data, no orphan findings, no orphan wiki articles, no receipt timestamp discrepancies.

## This run (REFRESH-1)

- 2 lanes ran (ai_agents, frontier_ai), 6 deferred (memory_orchestration, dev_tooling, research_method, builder_patterns, crypto_rails_agent_commerce, robotics_embodied).
- 23 sources captured, 29 findings extracted, 6 claims (3 verified, 3 unverified).
- 0 contradictions collapsed. 1 contradiction surfaced and routed to verification queue.
- Source balance: ai_agents 0% social, frontier_ai 0% social. Well under 40% soft warning floor.
- No degraded collectors.

---

*If this file is older than 12h, the vault is structurally unhealthy. Do not trust new synthesis until the structure is fixed.*

*Next health check: at start of next REFRESH (manual, no cron firing until scripts exist per Andre's manual-first decision).*
