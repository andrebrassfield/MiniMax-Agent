# Sources

> Per-source registries, weights, freshness flags. Stage 0.5 — between raw and findings.

## Layout

```
sources/
  <source_lane>/
    <source_name>.md   # one markdown per source
    <source_name>.json # structured metadata
```

## Per-source markdown

```markdown
---
source_id: src-...
name: "<source name>"
lane: <lane>
type: primary | secondary | social
url: https://...
weight: 0.0-1.0
last_collected: YYYY-MM-DD HH:MM
freshness_ttl_hours: 24
status: active | degraded | retired
---

# <source name>

<one paragraph: what it is, why it is in the plan>

## Cadence
<6h | 12h | 24h | weekly>

## Failure modes
- <what happens if it goes down>

## Notes
- <history, tuning decisions, related sources>
```

## Status lifecycle

- `active` — collecting normally
- `degraded` — failed 3+ consecutive runs; flagged in operator brief
- `retired` — removed from active plan; archived here for replay
