# Raw Captures

> Unprocessed input layer. Stage 0. Every collector writes here first, before extraction into findings.

## Layout

```
raw/
  <source_lane>/
    YYYY-MM-DD/
      <timestamp>-<id>.json
```

## Example

```
raw/
  frontier_ai/
    2026-06-02/
      20260602-150000-src-001.json
      20260602-150000-src-002.json
  ai_agents/
    2026-06-02/
      20260602-150500-src-003.json
```

## Schema (per capture file)

```json
{
  "id": "src-YYYYMMDD-HHMM-NNN",
  "captured_at": "2026-06-02T15:00:00Z",
  "source_lane": "frontier_ai",
  "url": "https://...",
  "type": "primary | secondary | social",
  "fetch_method": "rss | webfetch | api | browser",
  "raw_excerpt": "...",
  "raw_full_path": "raw/frontier_ai/2026-06-02/.../source.html",
  "content_hash": "sha256:...",
  "extracted_finding_ids": ["fnd-..."]
}
```

## Discipline

- Keep raw separate from `knowledge/`. The difference between an agent that synthesizes and an agent that smudges is whether raw is preserved.
- Cap total raw size at 500MB (config: `memory.raw_max_size_mb`). Older than 30 days is rotated.
- `raw/` is excluded from BACKUP (reproducible from sources). Everything else is included.
