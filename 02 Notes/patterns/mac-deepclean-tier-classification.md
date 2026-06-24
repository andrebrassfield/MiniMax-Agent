---
description: "Tier classification (1=auto-clean, 2=user-data-needs-go, 3=architecture-reorg) for Mac cleanup. Risk+reversibility based, not size. Includes post-reboot reclaim section. Moved from skill-local references 2026-06-22."
source: ~/.mavis/agents/mavis/skills/mac-deepclean/references/tier-classification.md
---

# Tier Classification — Mac Deep Clean

Tiers reflect **risk + reversibility**, not size. The same item can move
between tiers depending on context (e.g., `~/.ollama` is Tier 2 if the
user actively uses Ollama, but Tier 1 if they don't and it was orphaned).

## Tier 1 — Auto-cleanable (low risk, reversible)

Run without per-item approval **only if the user said something like
"deepest clean possible" or "do all three tiers"**. Each item is a
cache or temp dir that the OS or app rebuilds automatically. If a
later session asks "what did you clean?", these are always defensible.

- `/private/tmp/*` — build artifacts, temp install dirs, node_modules
  from one-off test runs
- `/private/var/folders/63/*` — XDG user cache (the `X` cache can be
  10+ GB if left alone for months)
- `/private/var/db/diagnostics` — Apple diagnostic logs (2+ GB typical,
  rebuilds within days)
- `/private/var/db/uuidtext` — macOS text index (500-900 MB,
  rebuilds on next file open)
- `~/Library/Caches/<app>` for apps that are not currently running
  (SiriTTS, callintelligenced, textunderstandingd, electron,
  antigravity-updater, node-gyp, ollama, playwright, pip, python)
- `~/Library/Logs/<app>/*` for old logs
- `~/.hermes/profiles.*-archive-<date>` — stale profile reconcile
  archives (anything older than 7 days)
- Broken symlinks (e.g., from `brew cleanup` warnings)

## Tier 2 — User data, needs go

Each item is data the user might want. Get blanket or per-item approval.
**Default to "ask" rather than assume.** When in doubt, leave it.

- Dev toolchains: `~/.rustup`, `~/.cargo`, `~/.bun`, `~/Library/pnpm`,
  `~/.ollama`, `~/.pyenv` (check if anything currently uses them first)
- Old project dirs: `~/ComfyUI`, `~/Doseofproof-Website-Local`,
  `~/projects/<old>` (verify they're not active)
- Large `~/Library/Application Support/<app>`: Notion, Google, Adobe,
  Codex, Telegram (offline caches, rebuilds on next sync)
- `~/Library/Containers/com.apple.mediaanalysisd`,
  `~/Library/Containers/com.apple.wallpaper.agent` — **SIP-locked,
  only sudo in Recovery Mode**, usually skipped
- `~/Library/Caches/Safari`, `~/Library/Caches/CloudKit` —
  **active, never delete**
- `~/models/<unused>` — ML models not referenced anywhere

## Tier 3 — Architecture reorganization

This is not deletion — it's moving content to where it belongs. Always
preserve; never overwrite. Get explicit approval.

- **Vault consolidation**: 2+ Obsidian-style vaults → 1 design target.
  Old content goes into `<target>/02 - ARCHIVE/vault-merge-<date>/`,
  never overwriting the new vault's structure.
- **MCP server relocation**: code that lives in the vault body
  (e.g., `~/MiniMax-Agent/99 _system/mcps/`, 600+ MB) moves to
  `~/.minimax/mcp-servers/`. This stops Obsidian from indexing config
  files but preserves the code.
- **Symbolic-link weirdness**: e.g., a literal `~/~` directory created
  by a path-quoting bug in a previous session. Preserve the content,
  trash the broken path.
- **Harness settings** (separate workflow, not "clean"):
  - `pmset -a displaysleep 0 sleep 0 powernap 0 womp 1`
  - `ulimit -n 65536`
  - Homebrew package set (chief-of-staff lane only — never install
    operator fleet tools)

## What NEVER goes in any tier

These are off-limits regardless of authorization:

- `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`
  (operator territory)
- `~/.mavis/` (Mavis's own working data — only the chief may modify
  her own files, and usually not via this skill)
- Anything in `~/Library/Application Support/com.apple.*` that is
  actively managing the system (Spotlight, Siri, Photos library)
- Sealed system volumes: `/System/Volumes/Preboot`,
  `/System/Volumes/VM`, `/System/Volumes/Update` (read-only,
  or read-mostly; size via `du -sh` is fine, contents are not
  user-modifiable)
- Active `.env` files, agent skill directories, workspace project
  files (the user already has these; "clean" doesn't mean "delete
  active config")

## Post-reboot reclaim (not a tier — automatic)

The OS reclaims some space on the next reboot without any user action.
Mention these in the report so the user knows what to expect.

- `/private/var/vm/sleepimage` — 2 GB, cleared when machine powers on
  cleanly (i.e., not after sleep — requires shutdown or restart)
- `/System/Volumes/VM` swap files — 3-5 GB, freed when machine reboots
  and dynamic pager releases them
- Sealed system volume overlays — variable, OS-managed
- Phantom Trash on sealed volume — variable; if user reports
  "8.69 GB Trash" but `~/.Trash` is empty, that's a sealed
  volume and not a real reclaim target from user space
