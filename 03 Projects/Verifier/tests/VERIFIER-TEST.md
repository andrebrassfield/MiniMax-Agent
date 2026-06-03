# Verifier — God Prompt Test

> Test plan for the Verifier's first session. Validates that the agent can load its vault, run BOOTSTRAP, and complete a sample AUDIT against a known-good and a known-bad target.

## Pre-flight

1. Load `SOUL.md` — confirm identity is anchored.
2. Load `AGENTS.md` — confirm procedures are accessible.
3. Load `config.yaml` — confirm `temperature.audit: 0.0` is hardcoded.
4. Confirm vault structure matches `vault.folders` in config.

## Test 1 — BOOTSTRAP (idempotency check)

Run BOOTSTRAP against the existing vault. Expected:
- No new folders created.
- No new ledgers created.
- Existing dossiers untouched.
- `runs/RUN-<timestamp>.md` written with mode=BOOTSTRAP.

## Test 2 — CROSS_CHECK against a known-good target

Pull the Researcher's `dossiers/ai_agents.md` (currently empty signal). Expected:
- Source trail captured to `raw/researcher/<timestamp>-dossiers-ai_agents.json`.
- Audit log appended to `knowledge/audit-log.jsonl`.
- Verdict written: `PASS` (vacuously — no claims to fail) with rubric criteria all at 1.0 except `freshness: 0.5` (last REFRESH is pending).
- Routed to `queue/researcher-verify-handoff.md` (researcher will mark consumed).

## Test 3 — CROSS_CHECK against a known-bad target

Construct a fake claim: "M3 is 10x cheaper than every competitor, weight 0.95, no source." Place it in `raw/test-fixtures/`. Expected:
- Verdict: `FAIL` with weighted_score < 0.40.
- Issue: "weight 0.95 with no source trail violates source_quality criterion."
- Recommended action: `require_primary_source` or `drop`.
- Routed to a test lane; not consumed.

## Test 4 — DAILY_BRIEF

Run DAILY_BRIEF. Expected:
- `notes/audit-summary.md` rewritten.
- Verdict counts reflect tests 2 and 3.
- Audit debt = 0 (no real NEEDS-MORE-EVIDENCE items).
- Pass/fail overall.

## Pass criteria

- All 4 tests pass.
- No verdicts issued without a trail.
- `temperature.audit: 0.0` verified at each AUDIT start.
- `notes/auditor-brief.md` rewritten, not appended.
- `health/audit-health.md` reports overall pass.

## What this test does NOT cover

- Live audits against running Researcher / Mavis / Hermes sessions.
- Real appeals, real disputes.
- Cross-agent load (10+ claims, 50+ findings).
- 6h cron loop.

Those are run in production after the first BOOTSTRAP-AUDIT cycle completes.
