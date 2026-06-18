# Output Format — agent-deployment-monitor

The two output templates. The per-client
`deployment-status.md` (4-field status board) and the
aggregated `_god-view.md`.

## Per-client: `deployment-status.md`

For each client subdirectory in `03 Projects/Clients/`,
the skill writes/updates:

```
03 Projects/Clients/[ClientName]/
├── deployment-status.md   ← THIS SKILL WRITES THIS
├── (client's own files)
├── logs/                  ← optional, if exists, the skill reads from here
│   ├── lead-volume-YYYY-MM-DD.log
│   └── errors-YYYY-MM-DD.log
└── (other deployment files)
```

### Template

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

> **AUTO-MAINTAINED** by `agent-deployment-monitor`. Each
> field is either inferred from the client's directory
> contents or read from a known logs file. If a field
> shows "unclear", the data source wasn't found.

## Status board

| Field | Value | Source | Last updated |
|-------|-------|--------|--------------|
| **Agent-Type** | <Voice / SMS / Scraper / Other / unclear> | inferred from directory contents | YYYY-MM-DD HH:MM:SS CT |
| **Last-Sync-Date** | <YYYY-MM-DD or unclear> | mtime of most recent file | YYYY-MM-DD HH:MM:SS CT |
| **Lead-Volume-Today** | <integer or unclear> | `logs/lead-volume-YYYY-MM-DD.log` | YYYY-MM-DD HH:MM:SS CT |
| **Error-Log-Alerts** | <count or "0" or unclear> | `logs/errors-YYYY-MM-DD.log` (last 24h) | YYYY-MM-DD HH:MM:SS CT |

## Inference notes (Agent-Type)

[If Agent-Type was inferred, the heuristic used is
documented here. Example: "Found `vapi_client.py` and
`voice_prompt.txt` → inferred Voice." If unclear: "No
voice/sms/scraper signals found in directory. Inferred
'unclear'. Operator should manually tag."]

## Data source (the deployment's actual home)

[If `logs/` exists: "Logs found at
`03 Projects/Clients/[ClientName]/logs/`. The skill reads
from there for Lead-Volume-Today and Error-Log-Alerts."]
[If `logs/` doesn't exist: "No logs directory found.
Lead-Volume-Today and Error-Log-Alerts will show 'unclear'
until the deployment system writes logs."]

## Quick links

- Client directory: `03 Projects/Clients/[ClientName]/`
- God View: `03 Projects/Clients/_god-view.md`

## Notes for the operator

[If any field is "unclear" or anomalous, the operator
action is documented here. Example: "Lead-Volume-Today is
unclear — the deployment system may not be writing logs
yet. Check the client's deployment script."]
```

## Aggregated: `_god-view.md`

The God View at `03 Projects/Clients/_god-view.md`
aggregates all clients:

```markdown
---
type: god-view
generator: agent-deployment-monitor
generator_version: 1.0
last_refresh: YYYY-MM-DD HH:MM:SS CT
---

# God View — Active Agent Deployments

> **AUTO-MAINTAINED** by `agent-deployment-monitor`.
> Aggregated from per-client `deployment-status.md` files.
> Sorted by Last-Sync-Date (most recent first).

| Client | Agent-Type | Last-Sync-Date | Lead-Volume-Today | Error-Log-Alerts | Status file |
|--------|------------|-----------------|-------------------|------------------|-------------|
| [ClientA] | Voice | 2026-06-15 | 47 | 0 | [deployment-status.md](ClientA/deployment-status.md) |
| [ClientB] | SMS | 2026-06-15 | 12 | 2 | [deployment-status.md](ClientB/deployment-status.md) |
| [ClientC] | Scraper | unclear | unclear | unclear | [deployment-status.md](ClientC/deployment-status.md) |
| ... | ... | ... | ... | ... | ... |

## Aggregate

- Total clients: N
- By type: <X> Voice, <Y> SMS, <Z> Scraper, <W> Other, <V>
  unclear
- Synced in last 24h: <count>
- With error alerts: <count>

## Notes for the operator

[If any client has unclear fields, the action is
documented here.]
```

## Sort order

The God View is sorted by Last-Sync-Date (most recent
first). Clients with `unclear` Last-Sync-Date sort to the
end (no mtime to compare).

## What these outputs are NOT

- **Not the deployment itself.** The skill is the
  filesystem scaffolding. The deployment system writes to
  log files; the skill reads from there.
- **Not a live monitoring dashboard.** The skill produces
  a snapshot at run time. For real-time monitoring, use
  a different system.
- **Not a billing system.** The skill tracks deployment
  status, not cost.
- **Not a notification system.** The skill does not page
  the operator on error alerts; the operator checks the
  God View daily.
