---
description: "The 8-step procedure agent-harness-mac-setup runs — baseline snapshot, pmset power, kernel limits, homebrew hygiene, TM exclusions, App Nap disable, cache purge, verify. Load when the skill is invoked. Includes all bash commands. Moved from SKILL.md inline content 2026-06-22 as part of Upgrade 1 aggressive refactor."
---

# agent-harness-mac-setup — The 8-step Procedure

## 1. Baseline snapshot (read-only)

```bash
df -h /System/Volumes/Data
ps -ax | wc -l
sysctl vm.swapusage
sysctl kern.maxfiles kern.maxfilesperproc kern.maxproc
launchctl limit maxfiles maxproc
pmset -g
brew list --formula | wc -l
brew outdated | wc -l
```

If disk >75% or swap >2GB, run `mac-deepclean` first.

## 2. Power management — `pmset`

```bash
sudo pmset -a displaysleep 0 disksleep 0 sleep 0 lowpowermode 0 powernap 0 proximitywake 0 womp 0 standby 0 hibernatemode 0
```

Verify with `pmset -g | grep -E "lowpowermode|womp|standby|sleep"`.

## 3. Kernel limits

```bash
sudo sysctl -w kern.maxfiles=524288
sudo sysctl -w kern.maxfilesperproc=524288
sudo launchctl limit maxfiles 524288 unlimited
```

`kern.maxproc` is read-only on M-series — accept 4000 default.

## 4. Homebrew hygiene

```bash
brew update
brew upgrade
brew cleanup -s
brew doctor
brew link <formula>
brew untap <tap>
brew uninstall <formula>
```

Common M4 removals: `docker`, `colima`, `docker-completion`, `docker-compose`, `lima` (if not used), `tldr` (deprecated).

## 5. Time Machine exclusions

```bash
for dir in .hermes .omp .gbrain .openclaw .openhuman .minimax; do
  tmutil addexclusion "$HOME/$dir"
done
```

Verify: `tmutil isexcluded <path>` returns `[Excluded]`.

## 6. App Nap disable

```bash
defaults write -g NSAppSleepDisabled -bool YES
defaults read -g NSAppSleepDisabled
```

## 7. Daemon cache purge + DNS flush

```bash
dscacheutil -flushcache
sudo killall -HUP mDNSResponder
atsutil databases -removeUser
qlmanage -r cache
sudo purge
```

## 8. Verify and report

```bash
echo "=== POST-TUNE ==="
pmset -g | grep -E "lowpowermode|womp|sleep"
sysctl kern.maxfiles kern.maxfilesperproc
launchctl limit maxfiles
df -h /System/Volumes/Data
sysctl vm.swapusage
brew outdated | wc -l
tmutil isexcluded ~/.hermes
```

Expected post-tune: lowpowermode 0, womp 0, maxfiles 524288, swap minimal, 0 outdated.

## Failure handling

- `pmset` setting accepted but `pmset -g` still shows old value → kernel locked it (M-series). Don't loop; document.
- `kern.maxproc: 4000` won't budge → it's read-only on M-series. `kern.maxfiles` is the lever.
- `brew upgrade` warns about untrusted tap (e.g. tinyhumensai/core) → `brew untap <tap>`.
- `tmutil addexclusion` returns immediately but `isexcluded` says no → check Spotlight indexing (`mdutil -s /`).
- Sudo password not in chat → use `osascript -e 'do shell script "..." with administrator privileges'` for any sudo batch.
