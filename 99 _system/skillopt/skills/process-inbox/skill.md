# process-inbox — Skill

> **Trailblazer for the Esalen Skill Pack structure.** The three primitives
> in this directory (`skill.md`, `action.py`, `test_action.py`) are the
> template for the other three workflow skills (daily_brief, weekly_connections,
> deep_research) when they get the same treatment.

## Purpose

Take a raw capture from `00 Inbox/`, sharpen it into a permanent note, and
route it to the correct `02 Notes/` subfolder with tags and at least one
wikilink to an existing note.

## Input

- **Inbox path**: a path like `00 Inbox/Some-Capture-2026-06-02.md`
- **Mavis output** (you, the model): a single JSON object that `action.py`
  consumes and turns into file operations

## Output (M3 produces this JSON)

```json
{
  "destination_folder": "02 Notes/ideas",
  "destination_filename": "Some-Concept.md",
  "sharpened_note": "# Some-Concept\n\nThe single-sentence sharpening of the capture, in one or two sentences at most.\n\n## Why this matters\n\n...optional elaboration...",
  "tags": ["idea", "tag-from-existing-taxonomy"],
  "primary_wikilink": "[[Existing-Note-Name]]",
  "additional_links": ["[[Another-Note]]", "[[Yet-Another]]"],
  "rationale": "One-sentence reason for this routing decision."
}
```

Field reference:
- `destination_folder` — required, must be one of the existing taxonomy
  folders (see `action.py` for the canonical list)
- `destination_filename` — required, kebab-case, no date in the name
  (the date is in the frontmatter, not the filename)
- `sharpened_note` — required, the full text of the new note including
  the title line. One specific thought, not a dump.
- `tags` — required, list of strings. Pick from the existing tag set;
  do not invent new tags without strong reason.
- `primary_wikilink` — required, the single most relevant existing note
  in `[[Note Name]]` form
- `additional_links` — optional, 0-3 additional wikilinks for context
- `rationale` — required, one-sentence reason for this routing decision
  (for the audit log)

## Procedure

1. **Read** the inbox capture at the given path
2. **Query vault-brain** for semantically related notes — this is the
   primary context mechanism, always query before guessing related notes
3. **Decide the destination folder** from the existing taxonomy
4. **Decide the destination filename** (kebab-case, descriptive)
5. **Sharpen the capture** to one specific sentence (or two for context)
6. **Choose 1-3 tags** from the existing tag set
7. **Identify the primary wikilink** from vault-brain's top result
8. **Identify 0-3 additional wikilinks** for related context
9. **Write the JSON** in the format above. Do NOT touch any files yourself
   — `action.py` will perform the move + backlinks + audit log.

## Rules

- **DO sharpen** — one specific thought, not a verbatim quote or a dump
- **DO use vault-brain first**, before guessing related notes
- **DO pick a destination from the existing taxonomy** — don't create new
  folders without strong reason
- **DO add at least one wikilink** to an existing note (the primary_wikilink)
- **DO write the JSON in the exact format above** — `action.py` parses it
  strictly, missing fields = ValueError, invalid folder = ValueError
- **DO NOT move the file yourself** — let `action.py` do the I/O
- **DO NOT add tags that aren't already in the taxonomy**
- **DO NOT add prose padding** to the sharpened note
- **DO NOT extrapolate beyond the source** — sharpen what is there, do
  not invent content
- **"Sharp enough"** = a note that still makes sense in 18 months with
  no extra context

## Worked example

Inbox: `00 Inbox/AI-Coding-Agents-2026-06-02.md`
Content: "thinking about how AI coding agents differ from autocomplete —
they're stateful, they have memory, they make decisions. might be relevant
to the broader question of agent design."

M3's JSON output:
```json
{
  "destination_folder": "02 Notes/ideas",
  "destination_filename": "Stateful-Coding-Agents.md",
  "sharpened_note": "# Stateful Coding Agents\n\nAI coding agents differ from autocomplete by maintaining state across the session, forming short-term memory, and making explicit decisions about which tool to invoke next.",
  "tags": ["idea", "agent-design"],
  "primary_wikilink": "[[Mavis-Apex-Architecture]]",
  "additional_links": ["[[Reflexion Loop]]", "[[Paged Memory Pattern]]"],
  "rationale": "Idea about the architectural distinction; Mavis-Apex-Architecture is the closest existing note on agent state."
}
```

## Integration: vault-brain

This skill relies on `vault-brain` (the MCP at `99 _system/mcps/vault-brain/`)
for semantic retrieval. **Always query vault-brain BEFORE making the routing
decision** — the top result is usually the right primary_wikilink. The
seeded test query is `"What are all the operating postures and constraints
we locked in today?"` — that surfaces the canonical notes for this vault.

## Edge cases

- **Unclear captures** — even unclear captures get a destination, usually
  `02 Notes/questions/` with a `[unclear — needs review]` tag
- **Already-categorized notes** — if a capture is in `00 Inbox/` but
  already has a clear type in its frontmatter, do not re-categorize
- **No existing related notes** — pick the closest by title match;
  primary_wikilink is still required, fall back to `[[INDEX]]` if nothing
  else fits
- **Destination filename collision** — `action.py` will raise
  FileExistsError. M3 should pick a different filename (e.g., add a
  number suffix) and re-emit the JSON

## Related

- `action.py` — the deterministic I/O layer that consumes this JSON
- `test_action.py` — pytest tests for `action.py`
- `99 _system/mcps/vault-brain/` — the semantic retrieval MCP
- `99 _system/skillopt/PIPELINE.md` — how SkillOpt optimizes this skill

---

*Skill authored 2026-06-02 as the trailblazer for the Esalen Skill Pack
structure. The other three workflow skills (daily_brief, weekly_connections,
deep_research) get the same treatment in the next session.*
