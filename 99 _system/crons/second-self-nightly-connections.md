---
name: second-self-nightly-connections
schedule: 0 23 * * *
timezone: America/Chicago
session:
  mode: new
  keepSessions: 5
---

# Second-Self Nightly Connection Finder (23:00 CT)

Fills the gap between morning brief (06:00) and weekly deep (Sun). Reads notes created/modified in last 48h, searches vault for non-obvious connections, writes connection notes to `08-COMPOUND/`. The Obsidian Masterclass's "Nightly Connection Finder" (Workflow 3), automated.

## Procedure

### Step 1 — Identify recent notes

```bash
# Find notes created or modified in last 48 hours
find ~/MiniMax-Agent -name "*.md" -type f -mtime -2 \
  -not -path "*/node_modules/*" \
  -not -path "*/.obsidian/*" \
  -not -path "*/.git/*" \
  -not -path "*/99 _system/*" \
  -not -path "*/07 Vellum/Archive/*" 2>/dev/null | sort
```

If count < 2: silent skip (insufficient material for cross-connection).

### Step 2 — Extract core claims from each recent note

For each recent note, extract:
- Title (first `# ` heading or filename)
- Core claim (1-2 sentences)
- Tags (from frontmatter)

### Step 3 — Search vault for non-obvious connections

For each recent note, search the rest of the vault for connections. Skip same-topic. Skip obvious. Look for:
- Notes that, when read together with the recent note, reveal something neither says alone
- Notes that challenge or complicate the recent note's position
- Notes that the recent note would naturally link to but doesn't yet

Use grep for fast first-pass:
```bash
# For each recent note, find candidates
TITLE="<note title>"
grep -rilF "$TITLE" ~/MiniMax-Agent --include="*.md" 2>/dev/null \
  | grep -v "99 _system" \
  | head -10
```

Then read each candidate to assess connection strength.

### Step 4 — Write connection notes

For each strong connection, write a note to `~/MiniMax-Agent/08-COMPOUND/YYYY-MM-DD-connection-<slug>.md`:

```markdown
---
date: YYYY-MM-DD
type: connection
trigger: nightly-finder
---

# Connection: <Note A title> ↔ <Note B title>

**Why this connection matters:** <2-4 sentences. The bar is: "I would not have made this link myself reading the notes one at a time.">

**Note A:**
- Title: <title>
- Path: <absolute path>
- Claim: <1-sentence summary>

**Note B:**
- Title: <title>
- Path: <absolute path>
- Claim: <1-sentence summary>

**What reading both reveals:** <the load-bearing insight that emerges from the connection>

**Suggested next step:** <add a wikilink from each note to the other? Update a thesis? Surface in a brief?>
```

### Step 5 — Append to today's log

Output to `~/.mavis/state/second-self-nightly-connections-YYYY-MM-DD.md`:

```markdown
---
date: YYYY-MM-DD
trigger: nightly-finder
---

# Nightly Connection Log — YYYY-MM-DD

## Notes scanned
- <count> recent notes

## Connections found
- [[08-COMPOUND/connection-A]] — strength: strong/medium/weak
- ...

## No-connection notes
- <count> recent notes had no non-obvious connections

## Process notes
- Cross-domain check: <how many notes crossed domains>
- Active-theses check: <any connections to the 4 active theses>
```

Mirror to `99 _system/logs/nightly-connections-YYYY-MM-DD.md`.

### Step 6 — Surface (silent unless meaningful)

If `connections_found >= 2`: Telegram nudge with the count + the strongest connection summary.
Otherwise: silent. The log is on disk for next-session pickup.

## Hard Constraints

1. **Skip same-topic connections.** "Both notes are about AI" is not a connection — it's a category match.
2. **Skip obvious connections.** If the wikilink already exists, don't write a new connection note.
3. **No fabrication.** If the vault has no strong non-obvious connection, write the log + "no meaningful connections" + exit.
4. **Active theses check.** If a recent note connects to one of the 4 Active Theses in MAVIS.md, mark the connection note as `thesis-relevant: true` so the morning brief can surface it.
5. **Mavis territory only.** All paths are `~/MiniMax-Agent/` and `~/.mavis/`.
6. **Rate-limit aware.** This cron counts toward the 20% cron allocation per the rate-limit-tracker.

## Halt Conditions

- Vault unreadable → HALT, surface
- Fewer than 2 recent notes → silent skip (no material)
- Connections scan exceeds 5 minutes → partial log, flag incomplete
- Output file > 500KB → truncate per-connection summaries

## Failure Modes

| Failure | Detection | Recovery |
|---|---|---|
| Grep returns too many candidates | Head -10 limit | Accept narrow search, log "may have missed" |
| Active thesis detection fails | Cross-check MAVIS.md load | Skip thesis flag, log |
| File moved between scan and write | Existence check before write | Skip if missing, log |

## Cross-references

- Spec: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md` (companion)
- Active theses: `~/MiniMax-Agent/MAVIS.md` "Current Active Theses" section
- Companion crons: `second-self-morning-brief` (06:00), `second-self-contradiction` (07:00), `second-self-weekly-deep` (Sun 19:00)
- Output destination: `~/MiniMax-Agent/08-COMPOUND/`
- Source article: Obsidian Masterclass (2026-06-22), Workflow 3
