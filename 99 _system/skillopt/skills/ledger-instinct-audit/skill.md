# ledger-instinct-audit — Skill

> Trigger-on-change self-correction loop. Fires when the Mavis Daemon
> detects that `03 Projects/Researcher/knowledge/claims.jsonl` has
> changed since the last daemon run. Audits the instincts in
> `99 _system/instincts/` that may be affected by the new claims.

## Purpose

Keep the instinct ledger honest. Instincts are atomic confidence-scored
rules captured from real sessions (see `99 _system/instincts/README`).
When a new claim lands, the supporting evidence for some instincts may
have changed. This skill:

1. Identifies the new claims (diff against the persisted snapshot)
2. Finds the instincts that reference the changed claim IDs or their
   dossiers (text search over `99 _system/instincts/*.md`)
3. Asks M3 to score each affected instinct for contradiction or
   staleness (the M3 call is the only non-deterministic step)
4. Writes the audit results to a run log + the instinct files
5. Updates the snapshot so the next daemon run starts clean

## When this fires

- `mavis_daemon.py` detects a change in `claims.jsonl` (sha256 or
  record_count differs from the snapshot at
  `99 _system/logs/ledger-snapshot.json`).
- The daemon selects `ledger-instinct-audit` and calls this action.

This **replaces** the old 4h full-audit cadence (per ruling 2026-06-03).

## Input

- `VAULT_ROOT` env var (default `/Users/brassfieldventuresllc/MiniMax-Agent`)
- The snapshot file at `<VAULT_ROOT>/99 _system/logs/ledger-snapshot.json`
  written by the daemon's last run
- The claims ledger at
  `<VAULT_ROOT>/03 Projects/Researcher/knowledge/claims.jsonl`
- The instinct directory at `<VAULT_ROOT>/99 _system/instincts/`

## Output

- A run log at `<VAULT_ROOT>/99 _system/logs/ledger-instinct-audit-runs.jsonl`
  with one record per invocation (per-instinct score, contradiction flag,
  evidence strength delta)
- Updated instinct files where M3 detected a contradiction or staleness
  (the existing frontmatter gets a `last_audited` field and the body
  gets a "## Audit history" section appended)
- An updated `ledger-snapshot.json` so the next run starts from the new
  baseline

## Procedure (action.py implements this)

1. **Read the snapshot** — load `ledger-snapshot.json`. If missing, this is
   the first run; record the current state and exit (nothing to audit).
2. **Diff against current claims** — for each record in `claims.jsonl`
   that's new since the snapshot (record_count delta), collect the
   `{claim_id, dossier, weight, claim_text, verified}`.
3. **Find affected instincts** — for each new claim, grep the
   `99 _system/instincts/*.md` directory for:
   - the claim ID (e.g. `clm-2026-06-02-004`)
   - the dossier name (e.g. `ai_agents`, `frontier_ai`)
   - the claim text keywords (e.g. "LangGraph", "memory attacks")
4. **Score each affected instinct** — for each match, ask M3 to evaluate
   the instinct against the new claim using the standard prompt:
   "Given the instinct {instinct_text} and the new claim
   {claim_text}, does the claim support, contradict, or leave unchanged
   the instinct? Reply with one of: `support`, `contradict`,
   `neutral`. If `contradict`, append a 1-sentence explanation."
5. **Write the audit log** — append a JSON line per (instinct, claim)
   pair with the score and the explanation.
6. **Update instinct files** — for any `contradict` verdict, append a
   `## Audit history` section to the instinct file with the date, the
   contradicting claim ID, and the 1-sentence explanation.
7. **Update the snapshot** — write the new state to
   `ledger-snapshot.json` so the next run starts clean.

## Tier policy

This is a **GREEN** skill in `mavis_daemon.py`. Auto-execute when
selected. No human-in-the-loop required. All writes are reversible via
git (snapshots, audit log entries, instinct annotations).

## Constraints

- The M3 call is the only non-deterministic step. Everything else is
  deterministic I/O.
- If the M3 call fails, fall back to `neutral` for that instinct and
  log a `m3_error` flag. The instinct file is NOT updated in that case.
- Never delete an instinct. Never downgrade an instinct's
  `confidence` field — only the daemon-computed "audit contradiction"
  flag is allowed to mark one for review.
- If the snapshot is missing, exit cleanly. This is the first run
  state; the next daemon run will create the snapshot.

## Worked example

Daemon snapshot at start of run:
```json
{"sha256": "abc123", "record_count": 6, "last_id": "clm-2026-06-02-006"}
```

Current claims.jsonl state: 7 records, last_id "clm-2026-06-02-007".

The diff: 1 new claim (clm-2026-06-02-007). The action.py:
1. Greps `99 _system/instincts/*.md` for "clm-2026-06-02-007" and related
   keywords. Say 2 instincts match.
2. For each, asks M3 to score. M3 returns:
   - Instinct "html-render-and-curl" → `support` (new claim reinforces
     the instinct)
   - Instinct "reconfirm-before-irreversible" → `neutral` (claim is
     about something else)
3. Writes 2 lines to the run log. Updates no instinct files (no
   contradictions).
4. Updates snapshot to record_count=7, last_id=clm-2026-06-02-007.

## Related

- `action.py` — the deterministic I/O implementation
- `mavis_daemon.py` — the trigger-on-change detector
- `99 _system/mcps/vault-brain/` — the semantic retrieval layer (used as
  a secondary signal in step 3 when text grep is too narrow)
- `99 _system/instincts/2026-06-03-001-html-render-and-curl-verification-is-required.md`
  — a real instinct that this skill audited on its first run

---

*Skill authored 2026-06-03 as the operation implementation for the
trigger-on-change ruling. Replaces the previous 4h full-audit cadence.*
