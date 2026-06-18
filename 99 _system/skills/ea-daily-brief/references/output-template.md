# Output Template — ea-daily-brief

The markdown file structure + the bash atomic-write command.

## File location

`00 Inbox/brief-YYYY-MM-DD.md`

## Template

```markdown
---
date: YYYY-MM-DD
generator: ea-daily-brief
inbox_window: 24h
notes_window: 7d
connection_count: 3
---

# Daily Brief — YYYY-MM-DD

## 1. <Title A>
- **Surfaces:** <paths>
- **Pattern:** <2-3 sentences, EA voice — direct, not academic>
- **Evidence:** <file:line refs>

## 2. <Title B>
- **Surfaces:** <paths>
- **Pattern:** <2-3 sentences>
- **Evidence:** <file:line refs>

## 3. <Title C>
- **Surfaces:** <paths>
- **Pattern:** <2-3 sentences>
- **Evidence:** <file:line refs>

## Cross-domain pattern
<one sentence — or omit section entirely if no pattern>

## Question
<one question, one sentence>
```

## Atomic write (mandatory)

```bash
# Atomic write: temp → fsync → rename
TMP=~/MiniMax-Agent/00\ Inbox/.brief-$(date +%Y-%m-%d).md.tmp
cp /dev/null "$TMP"
cat >> "$TMP" <<'BRIEF_EOF'
---
date: YYYY-MM-DD
generator: ea-daily-brief
inbox_window: 24h
notes_window: 7d
connection_count: 3
---

# Daily Brief — YYYY-MM-DD

## 1. <Title A>
- **Surfaces:** <paths>
- **Pattern:** <2-3 sentences>
- **Evidence:** <file:line refs>

[... 2 more connections ...]

## Cross-domain pattern
<one sentence, or omit>

## Question
<one question, one sentence>
BRIEF_EOF
sync "$TMP"
mv "$TMP" ~/MiniMax-Agent/00\ Inbox/brief-YYYY-MM-DD.md
```

The atomic rename pattern: write to a temp file, `sync` to flush, then
`mv` (which is atomic on the same filesystem). If anything fails, the
brief file is unchanged.

## Update (not replace) rule

If a brief for today already exists and an update is needed, append
a `## Update — HH:MM CT` section at the bottom. Never replace the
existing file — the original is part of the audit trail.

## Surface the brief

After the write, **surface the brief to Andre at the next
interaction** (the brief itself, not a "I wrote a brief"
notification). The brief is the message.
