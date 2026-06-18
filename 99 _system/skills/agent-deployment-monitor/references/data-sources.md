# Data Sources — agent-deployment-monitor

The 4 data sources the skill reads from to populate the
4-field status board. Each field has a primary source +
fallback rules. The discipline is: read from a known
location, fall back to "unclear" if not found.

---

## 1. Agent-Type (inferred from directory contents)

The skill infers the agent type from filenames OR file
contents. Heuristics in priority order (first match wins):

| Type | Filename / content signals |
|---|---|
| **Voice** | `vapi`, `synthflow`, `bland`, `retell`, `voice`, `tts`, `stt`, `telephony`, `fsm`, `voice_prompt`, `voice_agent` |
| **SMS** | `twilio`, `messagebird`, `sms`, `text_message`, `whatsapp` |
| **Scraper** | `scrapling`, `beautifulsoup`, `scrapy`, `playwright`, `selenium`, `crawler`, `scrape` |
| **Other** | client subdir exists but none of the above match |
| **unclear** | client subdir is empty |

### Inference procedure

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

### Inference notes (the discipline)

The inference is documented in the per-client
`deployment-status.md` "Inference notes" section so the
operator can verify and override. Example:

> "Found `vapi_client.py` and `voice_prompt.txt` → inferred
> Voice."

Or:

> "No voice/sms/scraper signals found in directory.
> Inferred 'unclear'. Operator should manually tag."

The operator can manually edit the `deployment-status.md`
to override the tag; the skill will preserve the manual
tag on re-runs (current spec overwrites the tag on each
run — operator can edit directly to override).

---

## 2. Last-Sync-Date (mtime of the most recent file)

The skill computes Last-Sync-Date as the mtime of the most
recently modified file in the client subdirectory,
**excluding `deployment-status.md` itself** (the skill's
own output is not the client's activity).

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

If no files found → "unclear".

---

## 3. Lead-Volume-Today (from a logs file)

The skill reads from
`03 Projects/Clients/[ClientName]/logs/lead-volume-YYYY-MM-DD.log`
(where YYYY-MM-DD is today's date in CT). The expected
format is a single integer per line (one entry per lead
handled).

```bash
today=$(TZ=America/Chicago date "+%Y-%m-%d")
if [ -f "03 Projects/Clients/[ClientName]/logs/lead-volume-${today}.log" ]; then
    count=$(wc -l < "03 Projects/Clients/[ClientName]/logs/lead-volume-${today}.log")
    echo "$count"
else
    echo "unclear"
fi
```

If the log file doesn't exist → "unclear". The operator
can set up the log file once the deployment system is
running.

---

## 4. Error-Log-Alerts (from an errors file)

The skill reads from
`03 Projects/Clients/[ClientName]/logs/errors-YYYY-MM-DD.log`
(today's date in CT). Counts lines in the last 24 hours.

```bash
today=$(TZ=America/Chicago date "+%Y-%m-%d")
if [ -f "03 Projects/Clients/[ClientName]/logs/errors-${today}.log" ]; then
    count=$(wc -l < "03 Projects/Clients/[ClientName]/logs/errors-${today}.log")
    echo "$count"
else
    echo "unclear"
fi
```

If the log file doesn't exist → "unclear". Same as
Lead-Volume-Today.

---

## What the skill does NOT read

- **External APIs (ServiceTitan, Jobber, Shopify, etc.).**
  The deployment system reads from those APIs and writes
  to the known log files. The skill reads from the log
  files.
- **Browser / web.** The skill is filesystem-only.
  `mavis browser` is not used.
- **Memory / gBrain.** The skill is deterministic against
  the filesystem.
- **Other agents' trees.** The skill is Mavis-internal
  (`03 Projects/Clients/` only).

## What the skill DOES write

- Per-client `deployment-status.md` (atomic write)
- Aggregated `_god-view.md` (atomic write, full rewrite on
  each run)
