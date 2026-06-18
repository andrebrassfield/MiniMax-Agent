# God View Aggregation — agent-deployment-monitor

The eval suite verifies the God View at
`03 Projects/Clients/_god-view.md` is complete + correctly
sorted + has the aggregate summary.

## G1. All clients are in the God View

```bash
god_view="03 Projects/Clients/_god-view.md"
clients_root="03 Projects/Clients"

# Count actual clients (excluding _template, _archive, _god-view)
actual_clients=$(find "$clients_root" -mindepth 1 -maxdepth 1 -type d \
  | grep -vE "/_template$|/_archive$|/_god-view$" \
  | xargs -I{} basename {} | sort)

# Extract clients from God View
god_clients=$(awk '/^---$/,/^---$/' "$god_view" | grep -oE "\[[A-Z][a-zA-Z0-9_-]+\]" | tr -d '[]' | sort -u)

# Compare
for client in $actual_clients; do
  echo "$god_clients" | grep -qF "$client" \
    || echo "FAIL: client $client not in God View"
done
```

**Failure mode this catches:** a client subdirectory
exists but is not in the God View. The aggregation is
incomplete.

## G2. God View is sorted by Last-Sync-Date (most recent first)

```bash
# Extract Last-Sync-Date per client from the God View table
god_dates=$(awk '/^| Client |/,/^## Aggregate/' "$god_view" | tail -n +3 \
  | awk -F'|' '{print $4}' | grep -oE "[0-9]{4}-[0-9]{2}-[0-9]{2}|unclear")

# Check that dates are in descending order (most recent first)
prev=""
echo "$god_dates" | while read d; do
  if [ -n "$prev" ] && [ "$d" != "unclear" ] && [ "$prev" != "unclear" ]; then
    if [ "$d" \> "$prev" ]; then
      echo "FAIL: sort order broken ($d > $prev)"
    fi
  fi
  prev="$d"
done
```

**Failure mode this catches:** the God View is not
properly sorted. The operator's daily check is harder.

## G3. Aggregate section is present and correct

```bash
# Total clients count must match `find | wc -l`
aggregate_total=$(awk '/Total clients:/,/By type:/' "$god_view" | grep -oE "[0-9]+" | head -1)
actual_total=$(find "$clients_root" -mindepth 1 -maxdepth 1 -type d | grep -vE "/_template$|/_archive$|/_god-view$" | wc -l | tr -d ' ')
[ "$aggregate_total" != "$actual_total" ] \
  && echo "FAIL: total clients mismatch (God View=$aggregate_total, actual=$actual_total)"

# By type breakdown must sum to total
by_type_sum=$(awk '/By type:/,/Synced in last 24h:/' "$god_view" | grep -oE "[0-9]+" | paste -sd+ | bc)
[ "$by_type_sum" != "$actual_total" ] \
  && echo "WARN: by-type sum $by_type_sum != total $actual_total"
```

**Failure mode this catches:** the aggregate summary has
wrong counts. The operator's daily metrics are off.

## G4. Each client has a status file link

```bash
# Every client in the God View should have a link to their
# deployment-status.md
god_clients=$(awk '/^| Client |/,/^## Aggregate/' "$god_view" | tail -n +3 \
  | grep -oE "\[[A-Z][a-zA-Z0-9_-]+\]\([^)]+\)" | wc -l | tr -d ' ')
status_files=$(find "$clients_root" -name "deployment-status.md" | wc -l | tr -d ' ')

[ "$god_clients" != "$status_files" ] \
  && echo "WARN: $god_clients clients in God View, $status_files status files on disk"
```

**Failure mode this catches:** a client is in the God View
but the per-client file is missing. Inconsistency.

## G5. Notes for the operator section is non-empty when fields are unclear

```bash
unclear_count=$(grep -cE "unclear" "$god_view" 2>/dev/null || echo 0)
notes_section=$(awk '/## Notes for the operator/,/^## /' "$god_view" | grep -v "^##" | wc -l | tr -d ' ')

if [ "$unclear_count" -gt 0 ] && [ "$notes_section" -lt 1 ]; then
  echo "FAIL: $unclear_count 'unclear' fields but Notes section is empty"
fi
```

**Failure mode this catches:** the operator sees "unclear"
without a follow-up action documented.

## G6. Last refresh timestamp is present

```bash
grep -qE "^last_refresh: [0-9]{4}-[0-9]{2}-[0-9]{2}" "$god_view" \
  || echo "FAIL: last_refresh timestamp missing in frontmatter"
```

**Failure mode this catches:** the operator doesn't know
when the God View was last updated.
