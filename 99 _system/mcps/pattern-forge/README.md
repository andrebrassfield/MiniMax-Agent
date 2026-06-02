# PatternForge

> **The workflow workshop.** Given a rough intent for a new agentic workflow, PatternForge produces a strict `GENERATIVE-CODE.md` — the 6-section structure adapted from Christopher Alexander's *The Nature of Order* (2004) Book 3. M3 (via `mmx text chat`) does the qualitative grading. Python handles the file I/O, prompt template, and JSON parsing. Esalen posture.

## The discipline

A generative code is **not a script.** It is the *patterns* + *sequence* + *values* + *stakeholders* + *boundaries* of a workflow. The script (`run.sh`) is the *output* of the generative code, not the workflow itself.

The 6 required sections (in order):
1. **The design problem** — what does this solve, what does it prevent, what does "done" look like?
2. **The patterns it composes** — linked CHIEF notes, or proposed patterns
3. **The sequence (with rationale)** — ordered steps with one-line rationales
4. **The values it embodies** — operational values, not vague platitudes
5. **The stakeholder interactions** — when human, when tool, when both
6. **The boundary conditions** — when NOT to run this, what's out of scope

Plus two auxiliary sections:
7. **Implementation script** — a one-line bash invocation
8. **Wholeness check** — self-score against Alexander's 15 properties (0-30)

## Quick start

```bash
# Use the Glass Server's venv (it has Python 3 + we share the env)
99 _system/mcps/glass-server/.venv/bin/python 99 _system/mcps/pattern-forge/pattern_forge.py forge \
  --intent "A workflow for triaging incoming emails into urgent / important / archive." \
  --vault /Users/brassfieldventuresllc/MiniMax-Agent \
  --out 03 Projects/Email-Triage/GENERATIVE-CODE.md
```

Or print the empty template (no LLM call):

```bash
99 _system/mcps/glass-server/.venv/bin/python 99 _system/mcps/pattern-forge/pattern_forge.py template
```

Or print a few-shot example (no LLM call):

```bash
99 _system/mcps/glass-server/.venv/bin/python 99 _system/mcps/pattern-forge/pattern_forge.py examples
```

## Subcommands

| Subcommand | Purpose | LLM? |
|---|---|---|
| `forge` | Generate a generative code by calling M3 (full workshop) | Yes |
| `shape` | Template manually-written content into GENERATIVE-CODE.md | No |
| `template` | Print the empty 6-section template | No |
| `examples` | Print the few-shot examples (in-context anchors for M3) | No |

## Architecture

```
pattern-forge/
  pattern_forge.py     # main entry (Python + subprocess to mmx)
  __init__.py
  README.md            # this file
```

The script:
1. **Reads** the user's intent (free text)
2. **Scans** the vault for related CHIEF notes (max 8, ranked by tag/title overlap)
3. **Composes** the user prompt: intent + vault context
4. **Calls M3** via `mmx text chat --model MiniMax-M3 --output json` (temperature 0.7 default)
5. **Parses** the JSON response and extracts the `text` content
6. **Templates** the response with metadata header (date, intent, model)
7. **Writes** to `--out` or stdout

The system prompt enforces the 6-section structure and the "no early stopping" rule. Few-shot examples anchor M3's style.

## What it is NOT

- **Not a workflow runner.** PatternForge only *generates* the code; running it is a separate step.
- **Not autonomous.** The user (or EA) reviews the generated code before any workflow runs.
- **Not a refactor of existing workflows.** Use `pattern-forge shape` for templating a manually-written code.
- **Not deterministic.** LLM output varies between runs. This is a *workshop*, not a printer.

## Configuration

The M3 model is fixed to `MiniMax-M3` (per the user's directive). Other flags:

| Flag | Default | Description |
|---|---|---|
| `--vault` | (none) | Path to vault root for related-note context |
| `--intent` | (required for `forge`) | Free-text description of the workflow |
| `--out` | stdout | Output file path |
| `--temperature` | 0.7 | Sampling temperature (workshop mode) |
| `--max-tokens` | 8192 | Max tokens to generate |

## Tying into the Horizon pitches

PatternForge is **Pitch 3 of Operation Horizon** — the generative-code workshop. It operationalizes the principle from `02 Notes/ideas/Workflows as Generative Codes.md`. Every workflow in the Omni-Operator should be a generative code, not a script. PatternForge is the workshop that produces them.

The CLI subcommand `mavis-vault` will eventually wrap PatternForge as `mavis-vault forge` (Phase 3.5 of the Glass project). For now, call the script directly.

## Future work

- [ ] Wire as `mavis-vault forge` subcommand
- [ ] Add `--persona` flag for different founder voices
- [ ] Add a `--validate` mode that runs the wholeness check separately
- [ ] Add a "pattern gallery" — search existing CHIEF notes to suggest which to link
- [ ] Support a `--multi-shot` mode for multi-turn refinement

## See also

- `02 Notes/ideas/Workflows as Generative Codes.md` — the underlying idea
- `02 Notes/patterns/Mycelial Routing.md` — examples of pattern-format CHIEF notes
- `00 Inbox/Horizon-Pitches-2026.md` — the pitch this implements
- `03 Projects/Investor-Updates-Workflow/GENERATIVE-CODE.md` — the first output

---

*Seeded 2026-06-02 from Operation Architect's Forge Phase 1. The workflow workshop. M3 is the master; Python is the file system.*
