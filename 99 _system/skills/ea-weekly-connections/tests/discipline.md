# Discipline — ea-weekly-connections

The 4-floor quality check the brief itself must pass.
The brief is a synthesis artifact; it must not become
the thing it's auditing (a recap of single-surface items
or a forced connection list).

## D1. 3-5 range floor (the load-bearing discipline)

**Verification:** the brief has 3-5 connections, not
2 (insufficient) and not 7+ (signal-diluted).

```bash
brief="02 Notes/connections/2026-W25-synthesis.md"
connection_count=$(grep -cE "^## Connection [0-9]+:" "$brief")

[ "$connection_count" -lt 3 ] && echo "FAIL: $connection_count connections (need ≥3)"
[ "$connection_count" -gt 5 ] && echo "FAIL: $connection_count connections (need ≤5, >5 is signal-diluted)"
```

**Failure mode this catches:** the brief is under-
populated (insufficient cross-domain signal) or over-
populated (signal-diluted).

## D2. Cross-domain floor (each connection spans ≥2 surfaces)

**Verification:** each connection's "Surfaces" field
names ≥2 surfaces.

```bash
for conn in $(grep -E "^## Connection [0-9]+:" "$brief" | sed 's/^## //'); do
  # Extract the Surfaces field
  surfaces=$(awk "/^## $conn/,/^## /" "$brief" | grep "Surfaces" | head -1)
  surface_count=$(echo "$surfaces" | grep -oE "(daily|kanban|workers|memory|skills)" | sort -u | wc -l | tr -d ' ')
  [ "$surface_count" -lt 2 ] && echo "FAIL: $conn has $surface_count surfaces (need ≥2)"
done
```

**Failure mode this catches:** a "connection" is
actually a single-surface item. The cross-domain
discipline is violated.

## D3. EA-voice floor ("What this means for Andre")

**Verification:** the "What this means for Andre" field
is in EA voice (synthesis + why), not operator voice
("the data shows X").

```bash
for conn in $(grep -E "^## Connection [0-9]+:" "$brief" | sed 's/^## //'); do
  what_field=$(awk "/^## $conn/,/^## /" "$brief" | grep "What this means" | head -1)
  # Anti-pattern: data-shows voice
  echo "$what_field" | grep -qiE "(the data shows|metrics show|stats indicate|looking at the data)" \
    && echo "FAIL: $conn is in operator voice, not EA voice"
done
```

**Failure mode this catches:** the field is a recap of
data, not a synthesis. The EA role discipline is
violated.

## D4. "What to do" concreteness floor

**Verification:** the "What to do" field is concrete
(action + specific), not vague ("consider," "monitor,"
"think about").

```bash
for conn in $(grep -E "^## Connection [0-9]+:" "$brief" | sed 's/^## //'); do
  do_field=$(awk "/^## $conn/,/^## /" "$brief" | grep "What to do" | head -1)
  # Anti-pattern: vague verbs
  if echo "$do_field" | grep -qiE "(consider|monitor|think about|keep an eye|watch)"; then
    # OK if "no action — informational" is the value
    if ! echo "$do_field" | grep -qiE "(no action.*informational)"; then
      echo "WARN: $conn's 'What to do' is vague (consider / monitor / think about)"
    fi
  fi
done
```

**Failure mode this catches:** the action is too vague
to act on. The connection surfaces the pattern but
doesn't give Andre something to do.

## Cross-reference

- `references/4-step-procedure.md` — Step 3 in detail
- `references/brief-template.md` — the brief structure
- `references/4-connection-types.md` — the 4 connection
  types + 3 anti-patterns
- `tests/safety-halts.md` — 5 halt conditions
