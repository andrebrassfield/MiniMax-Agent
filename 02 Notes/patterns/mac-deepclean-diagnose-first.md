---
description: "Why you don't just start deleting — the 4 metrics that matter (CPU, memory, disk I/O, energy), process count diagnostic table, post-OS-upgrade window, Computer Use visual verification. Moved from skill-local references 2026-06-22."
source: ~/.mavis/agents/mavis/skills/mac-deepclean/references/diagnose-first.md
---

# Diagnose First — Why You Don't Just Start Deleting

The single biggest mistake in Mac cleanup is reacting to a number
(process count, System Data bytes, Document folder size) without
checking what the number actually means. The chief-of-staff rule:

> **Look at all four resource metrics before proposing any deletion.**

## The four metrics that matter (in order)

### 1. CPU usage

- **Healthy**: < 30% sustained, 70-90% idle
- **Worth investigating**: 30-70% sustained (something is doing
  real work — could be legit, could be a runaway)
- **Problem**: > 80% sustained with no user action (runaway loop,
  infinite render, fork bomb)

Open Activity Monitor → CPU tab. The bottom panel shows
System/User/Idle split. A 729-process machine showing 82% idle is
**not** a problem, regardless of what the process count feels like.

### 2. Memory pressure

- **Healthy**: green, 0 swap, < 80% physical used
- **Worth investigating**: yellow pressure, swap > 0
- **Problem**: red pressure, swap growing, app crashes

Open Activity Monitor → Memory tab. **Green pressure with 0 swap
is the only verdict that matters** — total RSS, wired memory, and
app memory can all be high without being a problem if swap is 0.

### 3. Disk I/O

- **Healthy**: 0 bytes/s when idle, occasional spikes
- **Worth investigating**: sustained > 1 MB/s when idle
- **Problem**: sustained > 10 MB/s when idle (indexer stuck,
  Time Machine loop, log write storm)

Open Activity Monitor → Disk tab. If reads/writes are at 0
bytes/s right now, the disk is healthy.

### 4. Energy impact (laptops only)

- **Healthy**: "Very Low" on top consumers
- **Worth investigating**: "High" or "Very High" on apps that
  should be idle
- **Problem**: any app showing "Very High" with no user action

Open Activity Monitor → Energy tab. Sort by "Energy" column.

## What the process count actually tells you

Almost nothing. On a modern Mac:

| Configuration | Typical process count |
|---|---|
| Fresh Mac, zero apps | ~300 |
| One Safari window | ~400-450 |
| One Electron app (VS Code, Slack, Discord) | ~500-600 |
| Mavis Code + Hermes + OpenClaw + 2 MCP servers | ~700-800 |
| Full Adobe Creative Suite + 2 browsers | ~1000-1200 |

If the user reports "700 processes and only one app open" without
checking CPU/memory/swap, they are reacting to a number that has
no diagnostic value. **Show them the four metrics instead** and
the panic usually dissolves.

## The post-OS-upgrade window

macOS does a lot of background work for 24-72 hours after a major
upgrade:

- **Spotlight reindexing**: `mdworker_shared`, `corespotlightd`,
  `mds_stores` — adds 30-100 processes, several hundred threads,
  heavy disk I/O for a while
- **Photos library reanalysis**: `photolibraryd`, `mediaanalysisd`
  — can run for hours if library is large
- **iCloud sync re-sync**: `bird`, `cloudd` — network-heavy
- **Time Machine re-snapshot**: `backupd` — disk-heavy
- **Storage panel recalculation**: the panel itself uses
  several percent CPU while it rescans

The Storage panel's "System Data" number is also **stale for 24-48
hours** after a major upgrade. It keeps showing the pre-upgrade
total. `diskutil info /System/Volumes/Data` shows the real
volume-used number, which is more trustworthy in that window.

## Using Computer Use to verify visually

When the user is looking at a screenshot and says "this looks
insane", take your own screenshot via the cu MCP to confirm what
they're seeing is real and not a rendering glitch.

```bash
# Take screenshot
mavis mcp call cu desktop_screenshot '{"task_description": "Verify state"}'

# Open Activity Monitor (if not already open) — use Spotlight
mavis mcp call cu desktop_type '{"text": "Activity Monitor\n"}'

# Click through CPU / Memory / Energy / Disk tabs
mavis mcp call cu desktop_left_click '{"coordinate": [708, 110], "task_description": "Memory tab"}'
```

You can also click the colored bar at the top of Activity Monitor's
CPU/Memory tabs to see historical pressure graphs — useful when
the user wants to know "has it been like this all day?".

## The one situation where process count is real

If the user is also seeing:

- High CPU on a process they don't recognize
- Repeated app crashes
- Fans spinning up
- System feels sluggish
- New processes appearing that they didn't install

Then process count may be a symptom of malware or a runaway
process. In that case, use `lsof -p <pid>` to see what the
suspicious process is touching, and consider whether the user
needs a malware scan (separate skill scope — recommend, don't
auto-run).
