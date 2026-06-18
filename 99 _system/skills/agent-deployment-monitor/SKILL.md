---
name: agent-deployment-monitor
description: |
  Monitor `03 Projects/Clients/` for new client subdirectories, auto-create
  a per-client tracking file at `03 Projects/Clients/[ClientName]/deployment-status.md`
  with a 4-field status board (Agent-Type, Last-Sync-Date, Lead-Volume-Today,
  Error-Log-Alerts), and aggregate all clients into a single "God View" at
  `03 Projects/Clients/_god-view.md`. Triggers: cron (suggested: every 4-6
  hours during business hours), "scan for new clients", "refresh god view",
  "deployment status check", "any new client deployments?". Idempotent —
  re-running on the same client subdirectory updates the file (doesn't
  duplicate). Atomic write (temp-write-fsync-rename). Halt conditions:
  directory missing, deployment logs unreadable, schema anomaly.
---

# agent-deployment-monitor

The "God View" of every active agent deployment the
operator is running for clients. Monitors
`03 Projects/Clients/`, auto-creates per-client tracking
files, aggregates into a single God View. The skill is the
**filesystem scaffolding** for client deployments; the
deployment system itself writes to a known location, the
skill reads from there.

## When to run

**Primary trigger:** cron (suggested: every 4-6 hours during
business hours, 09:00 / 14:00 / 18:00 CT).

**Manual triggers:**
- "scan for new clients"
- "refresh god view"
- "deployment status check"
- "any new client deployments?"
- "show me the god view"

**Do NOT run for:**
- Subdirectories that are clearly NOT clients (e.g.,
  `_god-view.md` is a tracked file, not a client;
  `.DS_Store` is OS noise; `README.md` at the top level
  is the directory's own doc, not a client)
- Subdirectories that are template/scaffold subdirs
  (e.g., `_template/`, `_archive/`) — operator-curated,
  skip them
- Any other agent's territory (per the Mavis ↔ Hermes
  absolute separation: this skill only touches
  `03 Projects/Clients/`, Mavis-owned)

## Inputs

| Input | Default | Required |
|---|---|---|
| Client root | `03 Projects/Clients/` | no |
| Tracking schema | Agent-Type, Last-Sync-Date, Lead-Volume-Today, Error-Log-Alerts | no — fixed |
| God View path | `03 Projects/Clients/_god-view.md` | no |
| Skip patterns | `_god-view`, `.DS_Store`, `README.md`, `_template`, `_archive` | no |
| Agent-Type inference | see "Data Sources" below | no |
| Logs source | `03 Projects/Clients/[ClientName]/logs/` | no — falls back to "unclear" |

## The 4-field status board (the load-bearing structure)

The skill creates/updates a per-client tracking file with
4 fields. Full inference rules + data source patterns in
`references/data-sources.md`. Output templates in
`references/output-format.md`.

| Field | Source | Fallback |
|---|---|---|
| **Agent-Type** | inferred from directory contents (Voice / SMS / Scraper / Other) | "unclear" if no signals |
| **Last-Sync-Date** | mtime of most recent file (excluding `deployment-status.md` itself) | "unclear" if no files |
| **Lead-Volume-Today** | `logs/lead-volume-YYYY-MM-DD.log` line count (today in CT) | "unclear" if log missing |
| **Error-Log-Alerts** | `logs/errors-YYYY-MM-DD.log` line count (today in CT) | "unclear" if log missing |

The 4 fields are scaffolded with "unclear" placeholders
when the data source isn't found. The operator can set up
the log files once the deployment system is running.

## Agent-Type inference (the load-bearing heuristic)

Per `references/data-sources.md` §1, the skill infers the
agent type from filenames or file contents. Heuristics in
priority order (first match wins):

| Type | Filename / content signals |
|---|---|
| **Voice** | `vapi`, `synthflow`, `bland`, `retell`, `voice`, `tts`, `stt`, `telephony`, `fsm`, `voice_prompt`, `voice_agent` |
| **SMS** | `twilio`, `messagebird`, `sms`, `text_message`, `whatsapp` |
| **Scraper** | `scrapling`, `beautifulsoup`, `scrapy`, `playwright`, `selenium`, `crawler`, `scrape` |
| **Other** | client subdir exists but none of the above match |
| **unclear** | client subdir is empty |

The inference is heuristic, not authoritative. The
operator can manually tag in the `deployment-status.md`
"Notes for the operator" section; the skill preserves
manual tags on re-runs (this is a future enhancement; the
current spec overwrites the tag on each run — operator
can edit the file directly to override).

## The 8-step procedure (overview)

The full 8-step procedure with bash commands lives in
`references/procedure.md`. The high-level flow:

1. Verify the client root exists (HALT if not — forward-
   looking scaffolding)
2. List client subdirectories (skip `_template`, `_archive`,
   `_god-view`)
3. For each client, infer Agent-Type
4. For each client, compute Last-Sync-Date (mtime of most
   recent file, excluding `deployment-status.md` itself)
5. For each client, read Lead-Volume-Today and
   Error-Log-Alerts from logs
6. Write the per-client `deployment-status.md` (atomic)
7. Write the God View at `_god-view.md` (aggregate, sorted
   by Last-Sync-Date)
8. Return summary to operator

## Idempotency (the load-bearing discipline)

Re-running the skill on the same client subdirectory
**updates** the file (doesn't duplicate). The dedup logic:
- If `deployment-status.md` already exists for a client,
  **update** it (overwrite with new values, atomic write)
- If it doesn't exist, **create** it
- The God View is fully rewritten on each run (it's a
  snapshot, not a ledger)

Atomic write pattern (temp-write-fsync-rename) is the
discipline. Never write directly to the target file.

## Hard constraints

1. **Idempotent.** Re-running on the same client subdir
   updates the file (doesn't duplicate). The atomic write
   is the discipline.
2. **Mavis territory only.** This skill only touches
   `03 Projects/Clients/`. Does not cross into
   `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`,
   `~/.hermes-evolution/`, or any other agent's tree.
3. **Filesystem-only.** Does NOT use `mavis browser`,
   ServiceTitan APIs, Shopify APIs, or any external
   system. The deployment system writes to known log
   files; the skill reads from there.
4. **Skip template/archive subdirs.** `_template/`,
   `_archive/`, `_god-view` are operator-curated, not
   clients. Skip them.
5. **Last-Sync-Date excludes `deployment-status.md`.** The
   skill's own output is not the client's activity. The
   calculation must exclude the file it's writing.
6. **Logs fall back to "unclear".** If the deployment
   system isn't writing logs yet, the field shows
   "unclear" (not 0, not "N/A"). The operator sets up
   logs once the deployment is running.
7. **The skill does NOT auto-create `03 Projects/Clients/`.**
   The operator creates the dir when ready to onboard
   clients. Forward-looking scaffolding.
8. **Mavis territory only.** This skill is the
   filesystem scaffolding for Mavis-owned client work.
   No cross-team handoff.

## When the skill HALTs

Halt and escalate to Andre when:
- `03 Projects/Clients/` missing (H1) — operator hasn't
  created the dir yet (forward-looking)
- Client subdir unreadable (H2) — disk error
- Client subdir is a symlink (H3) — not a real client;
  resolve the symlink first
- Atomic write fails (H4) — surface
- God View write fails (H5) — surface

The skill is a diagnostic, not an authorization. The
operator decides the action.

## Verification (post-write)

After each run:

1. The per-client `deployment-status.md` files exist for
   every client subdir (except skipped patterns)
2. The God View exists and includes all clients
3. The 4 fields are populated for each client (or marked
   "unclear" with a reason)
4. The Agent-Type inference is documented in the
   "Inference notes" section
5. The Last-Sync-Date is correct (spot-check against the
   directory's actual mtime)
6. The atomic write pattern was used (no partial writes)
7. The return summary correctly reports new vs. updated
   clients

## Cross-reference

- `references/data-sources.md` — Agent-Type inference +
  Last-Sync-Date + Lead-Volume + Error-Log patterns
- `references/output-format.md` — `deployment-status.md`
  template + `_god-view.md` template
- `references/procedure.md` — the 8-step procedure with
  bash scripts
- `references/idempotency.md` — dedup logic + atomic write
  pattern
- `tests/4-field-presence.md` — field population checks
- `tests/god-view-aggregation.md` — God View completeness
  + sort order
- `tests/idempotency-check.md` — re-run does not duplicate
- `03 Projects/X-Content-Engine/` — the lead-gen / content
  surface (different territory)
- `03 Projects/Hermes/` — ABSOLUTE SEPARATION: this skill
  does not touch Hermes's tree
- The operator's deployment scripts — should write logs to
  `03 Projects/Clients/[ClientName]/logs/lead-volume-YYYY-MM-DD.log`
  and `logs/errors-YYYY-MM-DD.log` for the skill to read
