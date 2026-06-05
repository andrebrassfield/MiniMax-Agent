# session-boot-sync — Skill Pack

> **Fresh-session context loader.** Mavis (M3) invokes this skill when
> Andre starts a new chat and types a boot phrase. The skill gathers
> the cross-session state (memory, git, ledger, queues) and synthesizes
> a 3-bullet "Where we left off" briefing so Mavis and Andre are
> immediately aligned on current system state.

## Purpose

Eliminate the cold-start tax. When a new session opens, Mavis has the
agent's `MEMORY.md` injected automatically — but that is the *durable*
memory, not the *current* state. The boot sync reads what has changed
*since* the durable memory was last touched: the latest commits, the
most recent in-flight handoffs, the ledger's last-recorded claim, the
hard corrections logged in the last 48 hours. Output is a 3-bullet
briefing — short, specific, actionable.

## Trigger phrases

Invoke this skill when Andre types any of:

- `Boot sequence`
- `boot sync`
- `session boot`
- `where we left off`
- `load context`
- `fresh sync`

The trigger is a hard signal — when seen, do not ask "do you want me
to load context?" Just invoke. The first turn after a fresh chat is
the right moment.

## Input

- **Vault root** (default: `/Users/brassfieldventuresllc/MiniMax-Agent`)
- **Memory file** (default: `~/.mavis/agents/mavis/memory/MEMORY.md`)
- **Action layer** (`action.py`) — gathers all raw state, returns JSON

## Output (M3 produces this JSON)

M3 receives the `bundle` dict from `action.py` and produces:

```json
{
  "where_we_left_off": "Most recent commit <hash> (<date>): <one-line summary of what landed>.",
  "hard_constraints_loaded": [
    "Memory entry <name> (<date>): <one-line rule>",
    "Memory entry <name> (<date>): <one-line rule>"
  ],
  "open_loops": [
    "<pending handoff or audit, with file path and date>",
    "<ledger state or in-flight work>"
  ]
}
```

Field reference:
- `where_we_left_off` — required, 1-2 sentences, must name a commit
  hash and date. The single most recent commit's headline + 1 line of
  context.
- `hard_constraints_loaded` — required, list. The 2-3 most recent
  dated memory entries (last 48-72h) that bind Mavis's behavior on
  this session. If no new entries since last boot, return
  `["No new constraints since <last boot date>"]`.
- `open_loops` — required, list. Pending handoffs in
  `03 Projects/*/queue/` (sorted by mtime, top 3) + the ledger
  snapshot's `last_id` + `saved_at`. If no open loops, return
  `["No open loops — all queues cleared"]`.

## Procedure

1. **Call `action.py`** to gather the bundle:
   ```python
   import action
   bundle = action.gather_boot_state()
   ```
2. **Read the bundle** — it contains the last 80 lines of MEMORY.md,
   the last 10 git commits, the ledger snapshot, the top 5 queue
   handoffs by mtime, and the most recent daily note.
3. **Identify the most recent commit** — first entry of
   `bundle["recent_commits"]`. The headline is its first 80 chars.
   The date is `bundle["recent_commits"][0]["date"]`.
4. **Identify the 2-3 most recent dated memory entries** — scan
   `bundle["memory_tail"]` for `### <topic> (<date>)` headers in the
   last 48-72h. Pick the ones that bind Mavis's behavior (hard
   corrections, hard constraints, orchestration-failure-modes). Skip
   "Untitled" entries that lack semantic content.
5. **Identify open loops** — for each entry in
   `bundle["pending_handoffs"]` (top 3 by mtime), name the file path
   and the `status` from its frontmatter. Add the ledger snapshot
   line: `Ledger: <last_id>, saved <saved_at>`.
6. **Write the JSON** in the format above.
7. **Render the briefing** to Andre as 3 markdown bullets, prefixed
   with a one-line header: `**Where we left off**` /
   `**Hard constraints loaded**` / `**Open loops**`. No tables, no
   prose padding.

## Rules

- **DO name specific files, commit hashes, and dates** — no
  "recently we..." or "in the last session...". If the briefing
  would not survive a hard re-prompt with no memory, it is not
  specific enough.
- **DO pull from action.py's bundle, not from your own context** —
  the bundle is the fresh state; your context is the durable
  state. The point of the boot is to bridge the two.
- **DO lead with the most recent commit** — the work that *just*
  landed is what Andre is most likely returning to.
- **DO include the ledger snapshot** in open loops — it tells
  Andre what claim ID the system is on and when the ledger was
  last touched.
- **DO NOT re-summarize the full memory file** — the briefing is
  3 bullets, not a recap.
- **DO NOT include watch-items, future work, or speculative
  todos** — only what's in flight right now.
- **If everything is clean, say so explicitly** — "No new
  constraints since 2026-06-05" and "No open loops" are valid
  outputs. False urgency is worse than honest quiet.

## Worked example

Bundle (truncated) from a 2026-06-05 12:13 CT boot:

```json
{
  "memory_tail_lines": 80,
  "recent_commits": [
    {"hash": "3b0ff3e", "date": "2026-06-05", "subject": "Operation Last Mile..."},
    {"hash": "fc0d308", "date": "2026-06-05", "subject": "System: Migrate..."}
  ],
  "ledger_snapshot": {"last_id": "clm-2026-06-04-010", "saved_at": "2026-06-05T12:42:07+00:00"},
  "pending_handoffs": [
    {"path": "03 Projects/Builder/queue/mavis-handoff.md", "mtime": "2026-06-05T09:58", "status": "ready"},
    {"path": "03 Projects/Verifier/queue/mavis-audit-handoff.md", "mtime": "2026-06-04T20:00", "status": "pending"}
  ],
  "recent_daily": "01 Daily/2026-06-04.md"
}
```

M3's JSON output:

```json
{
  "where_we_left_off": "Most recent commit 3b0ff3e (2026-06-05): Operation Last Mile finalized Phase 1 Builder widget, Phase 2 FDA dossier, and Scribe Substack — all three landed.",
  "hard_constraints_loaded": [
    "Vault destruction prevention (2026-06-05): quote paths with double-quotes, push to remote after every commit, atomic commits need clean staging area.",
    "Hung worker on rate-limited model (2026-06-04/05): abort-to-solo heuristic when worker hangs and parent had a rate-limit incident in the last 60 min."
  ],
  "open_loops": [
    "Builder → Mavis handoff pending Verifier audit (03 Projects/Builder/queue/mavis-handoff.md, Run #2, path-recovery completed 06-05).",
    "Verifier → Mavis audit handoff pending (03 Projects/Verifier/queue/mavis-audit-handoff.md, mtime 2026-06-04).",
    "Ledger: clm-2026-06-04-010, saved 2026-06-05T12:42:07+00:00."
  ]
}
```

Rendered to Andre:

> **Boot sync — 2026-06-05 12:13 CT**
>
> - **Where we left off.** Most recent commit `3b0ff3e` (2026-06-05): Operation Last Mile finalized Phase 1 Builder widget, Phase 2 FDA dossier, and Scribe Substack — all three landed.
> - **Hard constraints loaded.** (1) Vault destruction prevention (2026-06-05): quote paths with double-quotes, push to remote after every commit, atomic commits need clean staging area. (2) Hung worker on rate-limited model (2026-06-04/05): abort-to-solo heuristic when worker hangs and parent had a rate-limit incident in the last 60 min.
> - **Open loops.** Builder → Mavis handoff pending Verifier audit (`03 Projects/Builder/queue/mavis-handoff.md`, Run #2, path-recovery completed 06-05). Verifier → Mavis audit handoff pending (`03 Projects/Verifier/queue/mavis-audit-handoff.md`, mtime 2026-06-04). Ledger: `clm-2026-06-04-010`, saved `2026-06-05T12:42:07+00:00`.

## Integration: action.py

`action.py` is the deterministic I/O layer. It does not call M3. It
returns a JSON dict that M3 reads and synthesizes. Tests for
`action.py` cover the data-gathering logic — fixture-based, no LLM
calls.

## Edge cases

- **Vault not initialized** — if `MiniMax-Agent/.git` is missing,
  `action.py` returns a `vault_status: "missing"` flag in the bundle
  and an empty commits list. M3 surfaces this to Andre as "vault not
  initialized — fresh start?".
- **Memory file not found** — `action.py` returns
  `memory_status: "missing"`. M3 surfaces as "no durable memory yet".
- **Ledger snapshot not found** — `action.py` returns
  `ledger_status: "missing"`. M3 omits the ledger line from open
  loops and notes "ledger not yet seeded".
- **No recent commits** — M3 surfaces as "no vault commits yet — is
  this the first boot?".
- **Stale memory (>7 days since last entry)** — M3 surfaces as
  "memory last touched <date> — consider a memory hygiene pass" as a
  4th bullet (only when stale; otherwise stays at 3).
- **Multiple projects have queue handoffs** — surface top 3 by mtime,
  not all. The point is "what's blocking me right now", not "list
  every queue".

## Related

- `action.py` — deterministic data-gathering layer
- `test_action.py` — pytest unit tests for `action.py`
- `~/.mavis/agents/mavis/memory/MEMORY.md` — durable memory (the
  boot sync reads the *tail* of this, not the whole file)
- `99 _system/logs/ledger-snapshot.json` — claim ledger state
- `99 _system/skillopt/PIPELINE.md` — SkillOpt pipeline this skill
  will be added to in Phase B
- The trailblazer pack: `daily-brief/`, `process-inbox/` (same shape)

---

*Skill Pack authored 2026-06-05 12:13 CT. Trigger: "Boot sequence".
Codifies the cold-start context-load as a deterministic layer +
judgment-required synthesis. v0.1.0 — first articulation.*
