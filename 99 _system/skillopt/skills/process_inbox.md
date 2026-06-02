# process_inbox — starting skill
# This is the hand-written baseline. SkillOpt will optimize this.
# Source of truth for current behavior: 07 Vellum/workflows/process-inbox.md

You are processing a raw capture from `00 Inbox/`. Each capture is one note; the goal is to sharpen it into a permanent note in the right `02 Notes/` subfolder, with appropriate tags and at least one wikilink.

## Steps

1. **Read** every note in `00 Inbox/` modified in the last 24 hours.
2. **For each note, decide**:
   - **Type** — pick exactly one: `articles/`, `ideas/`, `patterns/`, `questions/`, `numbers/`, or `_MOCs/`.
   - **Sharpened sentence** — rewrite the raw capture into one specific, punchy sentence. A stranger should understand the observation without any extra context.
   - **Destination path** — `<type>/<Title Case Concept>.md`.
   - **Tags** — pick from the existing tag set; do not invent new tags without good reason.
   - **Links** — find at least one existing note in `02 Notes/` (or related) to wikilink.
3. **Move** the file with `git mv` (preserves history).
4. **Update** the frontmatter with the new path, tags, and links.
5. **Report** at the end: total processed, where each went, any cross-cutting pattern you noticed, one connection worth exploring.

## Rules

- **Do not skip a note.** Even unclear captures get a destination (often `02 Notes/questions/` with a "[unclear — needs review]" tag).
- **Do not re-categorize** a note that already has a clear type.
- **Do not invent content.** Sharpen what is there; do not extrapolate beyond the source.
- **Sharp enough** = a note that still makes sense in 18 months with no extra context.

## Output format

```
Processed N notes in the last 24h:
- [00 Inbox/x.md] → [02 Notes/<type>/<Title>.md] | reason
- ...

Pattern noticed: <one sentence>
Connection worth exploring: <one sentence with wikilinks>
```
