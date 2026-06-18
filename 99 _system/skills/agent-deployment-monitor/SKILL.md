---
name: agent-deployment-monitor
description: Monitor `03 Projects/Clients/` for new client subdirectories, auto-create a per-client tracking file at `03 Projects/Clients/[ClientName]/deployment-status.md` with a 4-field status board (Agent-Type, Last-Sync-Date, Lead-Volume-Today, Error-Log-Alerts), and aggregate all clients into a single "God View" at `03 Projects/Clients/_god-view.md`. Triggers: cron (suggested: every 4-6 hours during business hours), "scan for new clients", "refresh god view", "deployment status check", "any new client deployments?". Idempotent — re-running on the same client subdirectory updates the file (doesn't duplicate). Atomic write (temp-write-fsync-rename). Halt conditions: directory missing, deployment logs unreadable, schema anomaly.
---

# Agent Deployment Monitor

## What this skill does

Provides a "God View" of every active agent deployment the operator is running for clients. The skill:

1. **Monitors** `03 Projects/Clients/` for new subdirectories. Each immediate subdirectory is treated as a client.
2. **Auto-creates** a tracking file at `03 Projects/Clients/[ClientName]/deployment-status.md` for each new client. The tracking file has 4 fields:
   - **Agent-Type** (Voice / SMS / Scraper / Other) — inferred from the client's directory contents
   - **Last-Sync-Date** — the mtime of the most recently modified file in the client subdirectory
   - **Lead-Volume-Today** — read from a known logs file (see "Data Sources" below); "unclear" if no logs found
   - **Error-Log-Alerts** — read from a known logs file; "unclear" if no logs found
3. **Aggregates** all clients into a single "God View" at `03 Projects/Clients/_god-view.md`. The God View shows all clients in a single table, sortable by Agent-Type or Last-Sync-Date.
4. **Refreshes** on re-run — idempotent. Re-running on the same client subdirectory updates the file (doesn't duplicate).

The skill is the **filesystem scaffolding** for client deployments. The deployment system itself (the code that runs the agents) writes to a known location; the skill reads from there. Without a deployment system, the tracking fields are scaffolded with "unclear" placeholders.

## When to run

**Primary trigger:** cron (suggested: every 4-6 hours during business hours, 09:00 / 14:00 / 18:00 CT).

**Manual triggers:**
- "scan for new clients"
- "refresh god view"
- "deployment status check"
- "any new client deployments?"
- "show me the god view"

**Do NOT run for:**
- Subdirectories that are clearly NOT clients (e.g., `_god-view.md` is a tracked file, not a client; `.DS_Store` is OS noise; `README.md` at the top level is the directory's own doc, not a client)
- Subdirectories that are template/scaffold subdirs (e.g., `_template/`, `_archive/`) — these are operator-curated, skip them
- Any other agent's territory (per the Mavis ↔ Hermes absolute separation: this skill only touches `03 Projects/Clients/`, Mavis-owned)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Client root | `03 Projects/Clients/` | no |
| Tracking schema | Agent-Type, Last-Sync-Date, Lead-Volume-Today, Error-Log-Alerts | no — fixed |
| God View path | `03 Projects/Clients/_god-view.md` | no |
| Skip patterns | `_god-view`, `.DS_Store`, `README.md`, `_template`, `_archive` | no |
| Agent-Type inference | See "Data Sources" below | no |
| Logs source | `03 Projects/Clients/[ClientName]/logs/` | no — falls back to "unclear" |

## Outputs

For each client subdirectory in `03 Projects/Clients/`, the skill writes/updates:

```
03 Projects/Clients/[ClientName]/
├── deployment-status.md   ← THIS SKILL WRITES THIS
├── (client's own files)
├── logs/                  ← optional, if exists, the skill reads from here
│   ├── lead-volume-YYYY-MM-DD.log
│   └── errors-YYYY-MM-DD.log
└── (other deployment files)
```

`deployment-status.md` schema:

```markdown
---
client: <ClientName>
agent_type: <Voice | SMS | Scraper | Other | unclear>
last_sync_date: <YYYY-MM-DD or unclear>
tracking_schema_version: 1.0
generator: agent-deployment-monitor
generator_version: 1.0
---

# Deployment Status — [ClientName]

> **AUTO-MAINTAINED** by `agent-deployment-monitor`. Each field is either inferred from the client's directory contents or read from a known logs file. If a field shows "unclear", the data source wasn't found.

## Status board

| Field | Value | Source | Last updated |
|-------|-------|--------|--------------|
| **Agent-Type** | <Voice / SMS / Scraper / Other / unclear> | inferred from directory contents | YYYY-MM-DD HH:MM:SS CT |
| **Last-Sync-Date** | <YYYY-MM-DD or unclear> | mtime of most recent file | YYYY-MM-DD HH:MM:SS CT |
| **Lead-Volume-Today** | <integer or unclear> | `logs/lead-volume-YYYY-MM-DD.log` | YYYY-MM-DD HH:MM:SS CT |
| **Error-Log-Alerts** | <count or "0" or unclear> | `logs/errors-YYYY-MM-DD.log` (last 24h) | YYYY-MM-DD HH:MM:SS CT |

## Inference notes (Agent-Type)

[If Agent-Type was inferred, the heuristic used is documented here. Example: "Found `vapi_client.py` and `voice_prompt.txt` → inferred Voice." If unclear: "No voice/sms/scraper signals found in directory. Inferred 'unclear'. Operator should manually tag."]

## Data source (the deployment's actual home)

[If `logs/` exists: "Logs found at `03 Projects/Clients/[ClientName]/logs/`. The skill reads from there for Lead-Volume-Today and Error-Log-Alerts."]
[If `logs/` doesn't exist: "No logs directory found. Lead-Volume-Today and Error-Log-Alerts will show 'unclear' until the deployment system writes logs."]

## Quick links

- Client directory: `03 Projects/Clients/[ClientName]/`
- God View: `03 Projects/Clients/_god-view.md`

## Notes for the operator

[If any field is "unclear" or anomalous, the operator action is documented here. Example: "Lead-Volume-Today is unclear — the deployment system may not be writing logs yet. Check the client's deployment script."]
```

The God View at `03 Projects/Clients/_god-view.md` aggregates all clients:

```markdown
---
type: god-view
generator: agent-deployment-monitor
generator_version: 1.0
last_refresh: YYYY-MM-DD HH:MM:SS CT
---

# God View — Active Agent Deployments

> **AUTO-MAINTAINED** by `agent-deployment-monitor`. Aggregated from per-client `deployment-status.md` files. Sorted by Last-Sync-Date (most recent first).

| Client | Agent-Type | Last-Sync-Date | Lead-Volume-Today | Error-Log-Alerts | Status file |
|--------|------------|-----------------|-------------------|------------------|-------------|
| [ClientA] | Voice | 2026-06-15 | 47 | 0 | [deployment-status.md](ClientA/deployment-status.md) |
| [ClientB] | SMS | 2026-06-15 | 12 | 2 | [deployment-status.md](ClientB/deployment-status.md) |
| [ClientC] | Scraper | unclear | unclear | unclear | [deployment-status.md](ClientC/deployment-status.md) |
| ... | ... | ... | ... | ... | ... |

## Aggregate

- Total clients: N
- By type: <X> Voice, <Y> SMS, <Z> Scraper, <W> Other, <V> unclear
- Synced in last 24h: <count>
- With error alerts: <count>

## Notes for the operator

[If any client has unclear fields, the action is documented here.]
```

## Data Sources (the load-bearing section)

The skill reads from these locations to populate the 4 fields:

### Agent-Type (inferred from directory contents)

Heuristics (in priority order, first match wins):
- **Voice**: any of `vapi`, `synthflow`, `bland`, `retell`, `voice`, `tts`, `stt`, `telephony`, `fsm`, `voice_prompt`, `voice_agent` in filenames OR file contents
- **SMS**: any of `twilio`, `messagebird`, `sms`, `text_message`, `whatsapp` in filenames OR file contents
- **Scraper**: any of `scrapling`, `beautifulsoup`, `scrapy`, `playwright`, `selenium`, `crawler`, `scrape` in filenames OR file contents
- **Other**: client subdir exists but none of the above match
- **unclear**: client subdir is empty

The inference is documented in the per-client `deployment-status.md` "Inference notes" section so the operator can verify and override.

### Last-Sync-Date (mtime of the most recent file)

```bash
find "03 Projects/Clients/[ClientName]" -type f -not -name ".DS_Store" 2>/dev/null \
  | xargs -I {} stat -f "%m %N" "{}" 2>/dev/null \
  | sort -rn | head -1 \
  | awk '{print $1}' \
  | python3 -c "import datetime, sys; ts=int(sys.stdin.read().strip()); print(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d'))"
```

If no files found → "unclear".

### Lead-Volume-Today (from a logs file)

The skill reads from `03 Projects/Clients/[ClientName]/logs/lead-volume-YYYY-MM-DD.log` (where YYYY-MM-DD is today's date in CT). The expected format is a single integer per line (one entry per lead handled).

```bash
today=$(TZ=America/Chicago date "+%Y-%m-%d")
if [ -f "03 Projects/Clients/[ClientName]/logs/lead-volume-${today}.log" ]; then
    count=$(wc -l < "03 Projects/Clients/[ClientName]/logs/lead-volume-${today}.log")
    echo "$count"
else
    echo "unclear"
fi
```

If the log file doesn't exist → "unclear". The operator can set up the log file once the deployment system is running.

### Error-Log-Alerts (from an errors file)

The skill reads from `03 Projects/Clients/[ClientName]/logs/errors-YYYY-MM-DD.log` (today's date in CT). Counts lines in the last 24 hours.

```bash
today=$(TZ=America/Chicago date "+%Y-%m-%d")
if [ -f "03 Projects/Clients/[ClientName]/logs/errors-${today}.log" ]; then
    count=$(wc -l < "03 Projects/Clients/[ClientName]/logs/errors-${today}.log")
    echo "$count"
else
    echo "unclear"
fi
```

If the log file doesn't exist → "unclear". Same as Lead-Volume-Today.

## The Procedure

### Step 1: Verify the client root exists

```bash
if [ ! -d "03 Projects/Clients" ]; then
    echo "HALT: 03 Projects/Clients/ does not exist. The skill expects this directory to be created by the operator when they're ready to onboard clients." >&2
    exit 1
fi
```

The skill does NOT auto-create `03 Projects/Clients/` — it's a forward-looking scaffolding. The operator creates it when ready to onboard clients.

### Step 2: List client subdirectories

```bash
find "03 Projects/Clients" -mindepth 1 -maxdepth 1 -type d 2>/dev/null \
  | grep -vE "/_template$|/_archive$|/_god-view$" \
  | while read client_dir; do
    client_name=$(basename "$client_dir")
    # ... process each client
  done
```

Skip patterns: `_template`, `_archive`, `_god-view` (the skill's own output).

### Step 3: For each client, infer Agent-Type

```bash
infer_agent_type() {
    local client_dir="$1"
    # Voice heuristics
    if find "$client_dir" -type f \( -iname "*vapi*" -o -iname "*synthflow*" -o -iname "*bland*" -o -iname "*retell*" -o -iname "*voice*" -o -iname "*tts*" -o -iname "*stt*" -o -iname "*telephony*" -o -iname "*fsm*" \) -print -quit 2>/dev/null | head -1 | grep -q .; then
        echo "Voice"
        return
    fi
    if grep -rIlE "vapi|synthflow|bland|retell|telephony|voice_agent" "$client_dir" 2>/dev/null | head -1 | grep -q .; then
        echo "Voice"
        return
    fi
    # SMS heuristics
    if find "$client_dir" -type f \( -iname "*twilio*" -o -iname "*sms*" -o -iname "*messagebird*" -o -iname "*whatsapp*" \) -print -quit 2>/dev/null | head -1 | grep -q .; then
        echo "SMS"
        return
    fi
    if grep -rIlE "twilio|sms|messagebird|whatsapp" "$client_dir" 2>/dev/null | head -1 | grep -q .; then
        echo "SMS"
        return
    fi
    # Scraper heuristics
    if find "$client_dir" -type f \( -iname "*scrapling*" -o -iname "*scrapy*" -o -iname "*playwright*" -o -iname "*selenium*" -o -iname "*crawler*" -o -iname "*scrape*" \) -print -quit 2>/dev/null | head -1 | grep -q .; then
        echo "Scraper"
        return
    fi
    if grep -rIlE "scrapling|scrapy|playwright|selenium|crawler" "$client_dir" 2>/dev/null | head -1 | grep -q .; then
        echo "Scraper"
        return
    fi
    # Empty?
    if [ -z "$(ls -A "$client_dir" 2>/dev/null)" ]; then
        echo "unclear"
        return
    fi
    echo "Other"
}
```

### Step 4: For each client, compute Last-Sync-Date

```bash
compute_last_sync() {
    local client_dir="$1"
    local latest_file
    latest_file=$(find "$client_dir" -type f -not -name ".DS_Store" -not -path "*/deployment-status.md" 2>/dev/null \
        | xargs -I {} stat -f "%m {}" "{}" 2>/dev/null \
        | sort -rn | head -1)
    if [ -z "$latest_file" ]; then
        echo "unclear"
    else
        local ts=$(echo "$latest_file" | awk '{print $1}')
        python3 -c "import datetime; print(datetime.datetime.fromtimestamp($ts).strftime('%Y-%m-%d'))"
    fi
}
```

The `deployment-status.md` file is excluded from the Last-Sync-Date calculation (it's the skill's own output, not the client's activity).

### Step 5: For each client, read Lead-Volume-Today and Error-Log-Alerts

Use the bash snippets from the "Data Sources" section above.

### Step 6: Write the per-client `deployment-status.md`

Atomic write (temp-write-fsync-rename).

### Step 7: Write the God View at `03 Projects/Clients/_god-view.md`

Aggregate all clients into a single table, sorted by Last-Sync-Date (most recent first).

### Step 8: Return summary to operator

Send a one-paragraph summary:
- Number of clients found
- Number of NEW clients (this run added them)
- Number of clients with errors / unclear fields
- God View path
- Halt conditions, if any

## Idempotency

Re-running the skill on the same client subdirectory updates the file (doesn't duplicate). The dedup logic:
- If `deployment-status.md` already exists for a client, **update** it (overwrite with new values, atomic write)
- If it doesn't exist, **create** it
- The God View is fully rewritten on each run (it's a snapshot, not a ledger)

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| `03 Projects/Clients/` missing | `ls` fails | Halt; surface (the operator hasn't created the dir yet — forward-looking) |
| Client subdir unreadable | `ls` fails | Halt; surface the disk error |
| Client subdir is a symlink | `find -type d` follows but `readlink` reveals it | Halt; surface (symlinks are not clients, they're references — operator should resolve) |
| Empty client subdir | `ls -A` returns empty | Mark Agent-Type as "unclear", Last-Sync-Date as "unclear", Lead-Volume as "unclear" |
| Logs dir exists but today's log is missing | `[ -f logs/lead-volume-today ]` fails | Mark Lead-Volume-Today and Error-Log-Alerts as "unclear" |
| Logs dir exists but log is malformed | `wc -l` fails | Mark as "unclear", note the parse error |
| Atomic write fails | `os.replace` raises | Halt; surface |
| God View write fails | `os.replace` raises | Halt; surface |
| `03 Projects/Clients/_god-view.md` already exists | `ls` succeeds | OK, the skill overwrites it (it's the skill's own output) |

## Verification

After each run:
1. The per-client `deployment-status.md` files exist for every client subdir (except skipped patterns)
2. The God View exists and includes all clients
3. The 4 fields are populated for each client (or marked "unclear" with a reason)
4. The Agent-Type inference is documented in the "Inference notes" section
5. The Last-Sync-Date is correct (spot-check against the directory's actual mtime)
6. The atomic write pattern was used (no partial writes)
7. The return summary correctly reports new vs. updated clients

## Cross-reference

- `03 Projects/X-Content-Engine/` — the lead-gen / content surface (different territory)
- `03 Projects/Hermes/` — ABSOLUTE SEPARATION: this skill does not touch Hermes's tree
- `mavis browser` CLI — NOT used by this skill (purely filesystem-based)
- The operator's deployment scripts — should write logs to `03 Projects/Clients/[ClientName]/logs/lead-volume-YYYY-MM-DD.log` and `logs/errors-YYYY-MM-DD.log` for the skill to read

## Notes for the operator

- The `03 Projects/Clients/` directory is forward-looking. Until the operator creates it and onboards the first client, the skill halts cleanly. This is by design — the skill is the scaffolding, not the deployment.
- The Agent-Type inference is heuristic, not authoritative. If the operator's deployment uses a less common stack (e.g., a custom voice engine not in the heuristic list), the inference will say "Other" or "unclear". The operator can manually tag in the `deployment-status.md` and the skill will preserve the manual tag on re-runs (this is a future enhancement; the current spec overwrites the tag on each run).
- The Lead-Volume-Today and Error-Log-Alerts fields require the deployment system to write to known log files. Until the deployment system is set up, these fields will be "unclear". This is the design: the skill reads from a known location, doesn't pull metrics from an unknown source.
- The God View is the operator's daily check surface. Open it once a day, scan the table, follow up on clients with `unclear` fields or `Error-Log-Alerts > 0`.
