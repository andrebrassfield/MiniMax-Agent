---
type: cli-spec
created: 2026-06-02
status: spec
tags: [cli, obsidian-glass, vault-tooling, mavis-apex, mavis-infrastructure]
related: [[README]], [[Architecture]]
domains: [cli-design, vault-tooling, executive-assistant]
---

# Obsidian Glass — CLI Toolkit Spec

> The `mavis-vault` command-line interface. A single binary (`99 _system/cli/mavis-vault`) that wraps the Glass Server's renderer module for one-shot operations on the vault. Esalen posture: one engine, many surfaces. The server is a *daemon* that uses the renderer; the CLI is a *one-shot* that uses the renderer. Same code, different interface.

## The design principle

**The CLI is not a new tool — it's a new surface for the existing tool.** The Python module that renders HTML in the Glass Server is the same Python module that the CLI uses to render, audit, search, and score. This means:
- The CLI and the server are always in sync.
- New features land in the renderer and become available in both.
- The test surface is shared (one test harness for both).
- The bundle is small (one Python codebase, one venv, one set of dependencies).

## The command surface

```
mavis-vault serve           # Start the Glass Server (default: localhost:8765)
mavis-vault render <path>   # Render a single file to HTML (stdout or --out)
mavis-vault audit           # Vault health check (broken wikilinks, missing frontmatter, etc.)
mavis-vault wholeness <path> # Score a single note on Alexander's 15 properties
mavis-vault search <query>  # Full-text search across the vault
mavis-vault index           # Regenerate the vault's INDEX.md
mavis-vault tree            # Print the vault tree
mavis-vault wholeness-report # Run the 15-property rubric on every atomic note
mavis-vault stats           # Quick vault statistics (count by type, etc.)
```

## Subcommand specs

### `mavis-vault serve`

Start the Glass Server. Default port 8765, default host 127.0.0.1.

```
mavis-vault serve [--port 8765] [--host 127.0.0.1] [--vault PATH]
```

**Flags:**
- `--port`: Port to listen on (default 8765)
- `--host`: Host to bind to (default 127.0.0.1 — local only)
- `--vault`: Path to vault root (default: parent of CLI's location)

**Behavior:** Identical to `glass_server.py`. The CLI is a thin wrapper that imports the same modules.

**Exit:** Runs forever until Ctrl+C.

### `mavis-vault render <path>`

Render a single vault file to HTML. Output to stdout by default, or to a file with `--out`.

```
mavis-vault render "02 Notes/patterns/Mycelial Routing.md" [--out file.html]
```

**Flags:**
- `--out PATH`: Write to file instead of stdout
- `--no-template`: Output just the body HTML (no page template)
- `--pretty`: Pretty-print (default: yes)

**Output:** Full HTML page (or body-only with `--no-template`).

**Use case:** Generate a one-off HTML view of a single note, or extract body HTML for embedding elsewhere.

### `mavis-vault audit`

Run a vault health check. Reports broken wikilinks, missing frontmatter, orphan notes (no inbound links), and other integrity issues.

```
mavis-vault audit [--strict] [--json] [--vault PATH]
```

**Flags:**
- `--strict`: Exit non-zero on warnings (default: only errors)
- `--json`: Output as JSON (default: human-readable table)
- `--no-color`: Disable ANSI colors

**Output (human-readable):**
```
=== VAULT AUDIT — 2026-06-02 17:15 ===
Indexed 381 files

[OK]    0 broken wikilinks across all atomic notes
[WARN]  16 broken wikilinks in INDEX.md (mostly folder references)
[WARN]  4 atomic notes below 18/30 wholeness (run `mavis-vault wholeness-report`)
[INFO]  381 files indexed
[INFO]  0 orphan atomic notes (no inbound links)
[INFO]  0 files with missing frontmatter (atomic notes only)
[INFO]  Mean file size: 8.4 KB
[INFO]  Largest file: 02 Notes/patterns/Skill Library Architecture.md (12.5 KB)

Suggested next steps:
  - Run `mavis-vault wholeness-report` to see the bottom-10 atomic notes
  - Run `mavis-vault search "TODO"` to find action items
```

**Use case:** Pre-flight check before publishing, regular vault maintenance, or in the Wholeness-Engine workflow.

### `mavis-vault wholeness <path>`

Score a single note on Alexander's 15 structural properties. Returns a score (0-30) and per-property analysis.

```
mavis-vault wholeness "02 Notes/patterns/Mycelial Routing.md" [--json]
```

**Flags:**
- `--json`: Output as JSON (default: human-readable)

**Output (human-readable):**
```
=== WHOLENESS — 02 Notes/patterns/Mycelial Routing.md ===
Score: 24/30  (alive, well-structured)

Properties:
  1. Levels of Scale        [2/2]  Strong
  2. Strong Centers         [2/2]  One clear central claim
  3. Thick Boundaries       [1/2]  Sections connect, transitions are thin
  4. Alternating Repetition [2/2]  Examples and principles alternate
  5. Positive Space         [2/2]  Structure does real work
  6. Good Shape             [2/2]  Recognizable section headers
  7. Local Symmetries       [2/2]  Parallel sections mirror
  8. Deep Interlock         [1/2]  Some sections are isolated
  9. Contrast               [2/2]  Sections differ in voice
 10. Gradients              [2/2]  Smooth energy transitions
 11. Roughness              [1/2]  Slightly too polished
 12. Echoes                 [2/2]  "flow" appears 3+ times
 13. The Void               [1/2]  Closing is dense
 14. Simplicity             [2/2]  No unnecessary content
 15. Not Separateness       [2/2]  Connects to MOCs

Suggested repairs:
  - Add a transitional sentence between sections 3 and 4 (Thick Boundaries)
  - Add one more cross-link to Mother-Tree MOC Topology (Deep Interlock)
  - Add a closing paragraph that opens (The Void)
```

**This is the `wholeness` subcommand of the Wholeness-Engine pitch (Pitch 2).** Initial implementation uses heuristics (regex + section count + link count); the LLM-as-judge is added when the Wholeness-Engine build begins.

### `mavis-vault wholeness-report`

Run the 15-property rubric on every atomic note (in `02 Notes/patterns/`, `02 Notes/ideas/`, `02 Notes/articles/`, `06 Connections/`, `00 Inbox/`).

```
mavis-vault wholeness-report [--top 10] [--bottom 10] [--json] [--out report.md]
```

**Output:** Distribution chart, top-10 (highest scores), bottom-10 (lowest scores).

### `mavis-vault search <query>`

Full-text search across the vault. Returns a list of matching files with context.

```
mavis-vault search "mycelial" [--type md] [--limit 20] [--json]
```

**Output (human-readable):**
```
=== SEARCH — "mycelial" — 7 matches in 4 files ===
[24/30] 02 Notes/patterns/Mycelial Routing.md  (12 matches)
  ... a flow-reinforced network that thickens the mycelial ...
  ... 3 lines later ...
  ... the mycelial shuttle-streaming is the same as the Resolver's hot-path ...
[21/30] 02 Notes/ideas/Mycelial Shuttle-Streaming as Resolver Principle.md  (8 matches)
  ... MycelialResolver — the mycelial network's transport ...
[20/30] 06 Connections/2026-W23 - Operation-Horizon-Synthesis.md  (4 matches)
  ... mycelial routing, topological quantum ...
```

**Use case:** Find related notes before writing a new one, debug wikilink targets, audit for "TODO" markers.

### `mavis-vault index`

Regenerate the vault's `INDEX.md` by scanning all notes, MOCs, and frontmatter. Output to stdout, or to `--out`.

```
mavis-vault index [--out INDEX.md] [--include-private]
```

**Use case:** When a new atomic note is added and the INDEX needs to reflect it (but the user is editing by hand for now).

### `mavis-vault tree`

Print the vault's folder structure with file counts and types.

```
mavis-vault tree [--depth 3] [--type]
```

**Output:**
```
MiniMax-Agent/  (381 files)
├── 00 Inbox/  (1 file, 0 atomic)
├── 01 Daily/  (3 files, 0 atomic)
├── 02 Notes/
│   ├── _MOCs/  (3 files, 3 atomic)
│   ├── articles/  (5 files, 5 atomic)
│   ├── ideas/  (14 files, 14 atomic)
│   ├── numbers/  (6 files, 0 atomic)
│   ├── patterns/  (15 files, 15 atomic)
│   └── questions/  (2 files, 0 atomic)
├── 03 Projects/  (6 projects)
├── 04 Resources/  (2 files)
├── 05 Archive/  (1 file)
├── 06 Connections/  (1 file, 1 atomic)
├── 07 Vellum/  (5 files)
├── 99 _system/  (system)
└── (root files)
    ├── INDEX.md
    ├── README.md
    ├── SOUL.md
    ├── MAVIS.md
    ├── agent.md
    ├── learnings.md
    └── state-of-mavis.md
```

### `mavis-vault stats`

Quick vault statistics. Counts by type, by folder, by frontmatter values.

```
mavis-vault stats [--by-type] [--by-tag] [--by-folder]
```

**Output:**
```
=== VAULT STATS — 2026-06-02 ===
Total files: 381
  .md files: 374
  .canvas files: 2
  other: 5

Atomic notes (CHIEF):
  patterns:  15
  ideas:     18  (was 14 before Horizon)
  articles:   5
  questions:  0
  connections: 1
  inbox:      1  (Horizon pitches)

Total frontmatter fields: 1847
Most common tags:
  - pattern: 19
  - idea: 18
  - chief-pattern: 17
  - mavis-apex: 15
  - isomorphism-from-horizon: 8
  - horizon: 6

Mean atomic note wholeness: 21.4/30  (n=58)
Below threshold (18/30):  6 (10.3%)
```

## Implementation

The CLI is a single Python file at `99 _system/cli/mavis_vault.py`, with a thin shell wrapper at `99 _system/cli/mavis-vault`. The Python file uses `argparse` with subcommands.

```python
# 99 _system/cli/mavis_vault.py
import argparse
import sys
from pathlib import Path

# Reuse the Glass Server's renderer
sys.path.insert(0, str(Path(__file__).parent.parent / "mcps" / "glass-server"))
from renderer import MarkdownRenderer

def cmd_serve(args): ...
def cmd_render(args): ...
def cmd_audit(args): ...
def cmd_wholeness(args): ...
# ... etc

def main():
    parser = argparse.ArgumentParser(...)
    subparsers = parser.add_subparsers(dest="command", required=True)
    # ... register each subcommand
    args = parser.parse_args()
    dispatch[args.command](args)
```

The shell wrapper (`mavis-vault`):
```bash
#!/usr/bin/env bash
exec "$(dirname "$0")/../mcps/glass-server/.venv/bin/python" "$(dirname "$0")/mavis_vault.py" "$@"
```

## What this CLI is NOT

- **Not a replacement for Obsidian.** Obsidian is still the editor.
- **Not a sync engine.** No write-back, no auto-commit.
- **Not a deployment tool.** The Glass Server is for *viewing*, not publishing.
- **Not a complete vault-management solution.** It's a *toolkit* for one-shot operations.

## What this CLI ties into

The `mavis-vault` CLI is the *operative* surface for the Horizon pitches:

| Horizon Pitch | CLI Subcommand |
|---|---|
| MycelialResolver (1) | `audit` shows routing data; `wholeness-report` shows note quality |
| Wholeness-Engine (2) | `wholeness` and `wholeness-report` are the core |
| PatternForge (3) | `wholeness-report` is the QA loop; `audit` checks the discipline |

The CLI is how the EA *interacts* with the system. The Glass Server is how the EA *sees* the system. The vault is the *source of truth*. Three surfaces, one engine.

## See also

- `Architecture.md` — the design rationale
- `99 _system/mcps/glass-server/README.md` — the prototype
- `2026-W23 - Operation-Horizon-Synthesis.md` — the pitches this CLI operationalizes
- `Mavis-Apex-Architecture` — the existing stack

---

*CLI Toolkit spec for Operation Obsidian Glass. Esalen posture: one engine, many surfaces. The CLI is a one-shot surface; the server is a daemon surface; the renderer is the engine.*
