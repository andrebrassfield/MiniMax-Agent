---
description: "The 7-step Mac Deep Clean procedure — diagnose, parallel audit, classify tiers, propose + ask, execute in waves, verify, hand back green light. Includes failure handling + the 3 locked walls (TCC, SIP, sealed). Moved from SKILL.md inline content 2026-06-22."
---

# mac-deepclean — The 7-step Procedure

## 1. Diagnose first

Open Activity Monitor via Computer Use (`desktop_screenshot`, `desktop_left_click`). Check all 4 tabs: CPU, Memory, Energy, Disk. A Mac at 82% idle CPU with green memory pressure is not sick even with 727 processes. See `[[02 Notes/patterns/mac-deepclean-diagnose-first]]`.

## 2. Parallel audit (no deletes)

Run in parallel:
- `df -h` on every APFS volume
- `du -sh ~/*` and `du -sh ~/.[a-z]*`
- `du -sh ~/Library /Library/Caches /private/var/db /private/var/folders`
- `du -sh /System/Volumes/Preboot /System/Volumes/VM` (sizes only — sealed)
- `tmutil listlocalsnapshots /` (if returns snapshots, propose `tmutil deletelocalsnapshots`)
- `ps -ax | wc -l`
- `mo analyze --json <path>` from Mole (tw93/Mole) for structured disk map
- **Do not descend into `~/.hermes` or `~/.openclaw`** — operator territory, top-level size only
- `xattr -l` any suspicious bundle that du reports 0 bytes (TCC-blocked: `com.apple.fileprovider.ignore#P = -1` + `com.apple.quarantine = -1`)

## 3. Classify into tiers

Use `[[02 Notes/patterns/mac-deepclean-tier-classification]]` to classify each finding:
- Tier 1: auto-clean (low risk, reversible)
- Tier 2: user data, needs explicit go
- Tier 3: architecture reorganization (preserve, never overwrite)

Default rule: Tier 1 may run if user said "deepest clean"; Tier 2/3 always need explicit in-session approval.

## 4. Propose with evidence, ask "go?"

Show user before/after projections per tier, what stays, recovery path (`mavis-trash`), reboot-required reclaim. Ask explicitly: "go?" or "go on Tier 1 only" or "skip Tier 3". Never execute Tier 2/3 without in-session approval.

## 5. Execute in waves

- **Wave 1 — Tier 1**: `/private/tmp/*`, `/private/var/folders/63`, `/private/var/db/diagnostics`, `/private/var/db/uuidtext`, `~/Library/Caches/<biggest>`, `~/Library/Logs/<app>/*`, stale `~/.hermes/profiles.*-archive-*`. Use `mavis-trash <path>` not `rm -rf`.
- **Wave 2 — Tier 2**: dev toolchains (`~/.rustup`, `~/.cargo`, `~/.ollama`, `~/.bun`, `~/Library/Python`), model weights, large `~/Library/Application Support` caches. One target per `mavis-trash` call.
- **Wave 3 — Tier 3**: vault consolidation, MCP-server moves, broken symlink cleanup. Create new files (cp -R then mavis-trash old), not deletions.
- **Sudo**: never pipe passwords. Use `osascript -e 'do shell script "bash /tmp/<script>.sh" with administrator privileges with prompt "<one-line>"'`. Batch all sudo into one osascript call.
- **Apple containers** (`~/Library/Containers/com.apple.*`): mavis-trash may fail (700+ siblings). Skip — regenerable Apple caches.

## 6. Verify and report

- `df -h` on every volume, `du -sh` on same dirs from step 2, `brew doctor` if Homebrew touched
- Report: total bytes freed, items skipped + why, what still requires reboot, Storage panel expected drop (immediate or 24-48h), reboot recommendation

## 7. Hand back green light

End with: "go ahead and reboot" or "no reboot needed, you're clean." If user wanted harness optimization instead, transition to harness setup (pmset, brew installs, ulimit) — separate skill scope.

## The 3 locked walls (invisible-to-shell disk usage)

1. **TCC-blocked bundles** — `~/Pictures/Photos Library.photoslibrary`, iCloud private folders. Only the owning app reads via TCC scope. CLI sees 0 bytes. Check `com.apple.fileprovider.ignore#P`.
2. **SIP-blocked Preboot** — `/System/Volumes/Preboot/Cryptexes/Incoming`. Even root via osascript returns "Operation not permitted." Only Recovery Mode + `csrutil disable` (never do) or letting update complete.
3. **Sealed system volumes** — `/dev/disk3s1s1` (~12GB), `/dev/disk3s6` (~4GB), `/dev/disk3s4`. Firmware + recovery + VM swap. Cannot reclaim without reformatting.

## Failure handling

- `mavis-trash` times out at 120s on multi-GB dir → split into smaller sub-dir targets
- Permission denied → skip, document, ask if sudo password available
- Storage panel doesn't change → macOS recalculates over hours; don't loop
- "Phantom Trash X GB" → sealed APFS volume, not real Trash
- Process count looks insane but metrics green → count-vs-meaning confusion
- Vault-merge collision → never overwrite, copy old to `<new>/02 - ARCHIVE/vault-merge-<date>/`
- MCP server code in vault body → move to `~/.minimax/mcp-servers/`, don't delete
- Storage panel shows N GB but `du ~/X` tiny → TCC-blocked bundle
