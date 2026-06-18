# Procedure — agent-deployment-monitor

The 8-step procedure with bash commands. The SKILL.md only
carries the procedure overview. The actual commands live
here (the deterministic layer).

---

## Step 1: Verify the client root exists

```bash
CLIENTS="/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Clients"
if [ ! -d "$CLIENTS" ]; then
    echo "HALT: $CLIENTS does not exist. The skill expects this directory to be created by the operator when they're ready to onboard clients." >&2
    exit 1
fi
```

The skill does NOT auto-create `03 Projects/Clients/` —
it's a forward-looking scaffolding. The operator creates
it when ready to onboard clients.

## Step 2: List client subdirectories

```bash
find "$CLIENTS" -mindepth 1 -maxdepth 1 -type d 2>/dev/null \
  | grep -vE "/_template$|/_archive$|/_god-view$" \
  | while read client_dir; do
    client_name=$(basename "$client_dir")
    # ... process each client
  done
```

Skip patterns: `_template`, `_archive`, `_god-view` (the
skill's own output).

## Step 3: For each client, infer Agent-Type

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

Full inference rules in `references/data-sources.md` §1.

## Step 4: For each client, compute Last-Sync-Date

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

The `deployment-status.md` file is excluded from the
Last-Sync-Date calculation (it's the skill's own output,
not the client's activity).

## Step 5: For each client, read Lead-Volume-Today and Error-Log-Alerts

```bash
today=$(TZ=America/Chicago date "+%Y-%m-%d")

# Lead-Volume-Today
if [ -f "$client_dir/logs/lead-volume-${today}.log" ]; then
    lead_volume=$(wc -l < "$client_dir/logs/lead-volume-${today}.log")
else
    lead_volume="unclear"
fi

# Error-Log-Alerts
if [ -f "$client_dir/logs/errors-${today}.log" ]; then
    error_alerts=$(wc -l < "$client_dir/logs/errors-${today}.log")
else
    error_alerts="unclear"
fi
```

Full patterns in `references/data-sources.md` §3-4.

## Step 6: Write the per-client `deployment-status.md`

Atomic write (temp-write-fsync-rename). Use the
`Write` tool (which is atomic by default), or manual
pattern:

```bash
TMP="/tmp/deployment-status-${client_name}-$$.md"
cat > "$TMP" <<EOF
[content]
EOF
mv -f "$TMP" "$client_dir/deployment-status.md"
```

If the file exists, **overwrite** (idempotent). If it
doesn't exist, **create**.

Template in `references/output-format.md` §1.

## Step 7: Write the God View at `_god-view.md`

Aggregate all clients into a single table, sorted by
Last-Sync-Date (most recent first). Full rewrite on each
run (it's a snapshot, not a ledger).

Template in `references/output-format.md` §2.

## Step 8: Return summary to operator

Send a one-paragraph summary:
- Number of clients found
- Number of NEW clients (this run added them)
- Number of clients with errors / unclear fields
- God View path
- Halt conditions, if any
