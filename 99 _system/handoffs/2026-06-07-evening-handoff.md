# Mavis Session Handoff — 2026-06-07 Evening

**From session:** `mvs_bece5d0cde364a528fc801129f24563f` (root)
**Agent root:** `mvs_c66508856c334f75868410d335ab7a25`
**Date:** 2026-06-07, 16:33 CT
**Author:** Mavis (EA, MiniMax-M3)

---

## TL;DR

Operational session closed at 16:33 CT. All work committed and pushed.
`origin/main` is at `d4ff5f9`. The cron `com.mavis.cron` is armed and
will fire at 02:00 CT tomorrow. A self-reminder `check-cron-2026-06-08`
will verify the receipt at 09:00 CT. Hermes has the greenlit
fleet-watchdog v2 spec and is building. Andre wants to keep going
tonight — next chat should pick up Hermes native-tools work.

---

## 1. State of the World (as of handoff)

| Item | Value |
|---|---|
| `origin/main` | `d4ff5f9 Fix: Update mavis-cli installer to use absolute path for zsh alias.` |
| Working tree | 1 modification (`99 _system/memory/MEMORY.md` — concurrent Mavis-session edit, NOT mine) + ~70 untracked items (not in scope for tonight) |
| Harness daemon | `com.mavis.harness` running on `127.0.0.1:11435`, session `harness-20260607201742`, uptime ~95 min |
| Cron | `com.mavis.cron` registered, fires 02:00 local (CT) daily, points at `scaffolding_review_cron_runner.py` |
| mavis-cli | Installed at `~/.mavis/bin/mavis-cli`; symlinks at `/opt/homebrew/bin/mavis-cli` and `/usr/local/bin/mavis-cli`; `mh` alias in `~/.zshrc` (single, full-path form) |
| Ollama | Restarted by Andre; harness now sees it (gemma4:12b-it-qat chat, gemma4:e4b-it-qat fast) |
| Self-reminder | `check-cron-2026-06-08` — fires 2026-06-08 09:00 CT, auto-expires 2026-06-08 15:59 CT |
| Async ops | Self-reminder only. No CI, no MR, no external call. |

---

## 2. Operational work done this session (4 atomic commits, all pushed)

| SHA | Title | What it did |
|---|---|---|
| `f7dc827` | Deploy live observability cron and fix __main__ selftest routing | Built `scaffolding_review_cron_runner.py` (live /stats → run_review); updated plist; updated deploy script. Cron now produces real eval-vault receipts. |
| `1a41ade` | Build mavis-cli terminal bridge to the harness daemon | 325-line CLI + 290-line test suite + 100-line installer. Stdlib-only. 12/12 tests pass. |
| `0e07f04` | chore: Ledger maintenance, memory boundary locks, and queue hygiene | 7 ledger files consolidated; `daemon-runs.jsonl` untracked (was already in `.gitignore` but still tracked from history). |
| `d4ff5f9` | Fix: Update mavis-cli installer to use absolute path for zsh alias | `ALIAS_LINE` now uses `$DEST` full path. Patched the broken PATH-based alias that failed in Andre's interactive shell. |

Plus: edited `~/.zshrc` to remove the duplicate `alias mh="mavis-cli"`
line that was clobbering the full-path version (the file went from 78 → 77 lines).

---

## 3. Cron fix — what was wrong and what it's now

**Before:** `com.mavis.cron.plist` executed
`~/.mavis/bin/scaffolding_review_cron.py`. That script's `__main__` block
(line 994) calls `_selftest()`, which exercises the full review pipeline
against **mock** stats. A smoke test, not the eval-vault review.

**After:** plist now points at
`~/.mavis/bin/scaffolding_review_cron_runner.py`. The runner:
1. `GET http://127.0.0.1:11435/stats` (harness daemon)
2. Maps JSON → `ScaffoldingStats` dataclass
3. Calls `cron.run_review(stats)` → writes dated receipt to `~/99 _system/scaffolding-reviews/YYYY-MM-DD.md`
4. Exits 64 on daemon-down, 65 on malformed payload, 0 on success

**Verified end-to-end:** First live receipt written at
`~/99 _system/scaffolding-reviews/2026-06-07.md` with real harness data
(`total_classifications: 2`, `L1 rule_count: 10`, `recent_turns: 2`,
`Lane distribution: capture:1, observe:1`).

---

## 4. mavis-cli — what it is and how it works

**~325 lines, stdlib only** (`urllib.request`, `argparse`, `json`).
No pip dependencies. Lives at `03 Projects/Builder/drafts/mavis_cli.py`
in drafts/, plus the runtime at `~/.mavis/bin/mavis-cli`.

**Surface:**

```bash
mavis-cli "prompt"                 # POST /turn
echo ... | mavis-cli               # POST /turn (stdin)
mavis-cli -f a.md -f b.md          # POST /turn with multi-file concat
                                   #   using "# File: <name>" header per file
mavis-cli --health                 # GET  /health
mavis-cli --stats                  # GET  /stats
mavis-cli --stats --json           # raw JSON
mh ...                             # alias for muscle memory (full path)
```

**Exit codes:** 0 ok, 64 conn refused, 65 harness error, 66 input > 1 MB.

**Tests:** 12/12 pass. Mock the `request()` function via
`unittest.mock.patch`. Live integration test against the running
harness: `--health` and `--stats` work; `/turn` works for non-inference
calls but Gemma4 cold-path is the slow one (~10-30s).

**Smoke transcript from earlier:**
- `mh --health` → `status: ok, session_id: harness-20260607201742, ...`
- `mh --stats` → `drift_score: 0.0, router.classifications: 2, ...`
- `mh --stats --json` → raw JSON
- `mh` with no input → friendly multi-line error to stderr, exit 64
- `mh --verbose` → emits lane + model to stderr after the response

**Install:** `bash 03\ Projects/Builder/drafts/install_mavis_cli.sh`
(idempotent — copies, symlinks, adds alias).

---

## 5. Git hygiene — the 8 modifications, dispatched

Committed in `0e07f04`. Breakdown:

| Bucket | File | Action |
|---|---|---|
| A (commit) | `03 Projects/Researcher/knowledge/sources.jsonl` | +105 lines, primary sources ledger |
| A | `03 Projects/Researcher/knowledge/findings.jsonl` | +18 findings, synthesized claims |
| A | `99 _system/memory/MEMORY.md` | -240 +70, major consolidation (the one I authored; another session wrote to it AFTER my commit — see "Concurrent edits" below) |
| A | `99 _system/memory/agent-harness-principles.md` | frontmatter tweak |
| A | `99 _system/memory/tool-quirks.md` | +63 lines |
| A | `THE-OMNI-OPERATOR-MANIFESTO.md` | +3 line (PATH reference) |
| C (commit) | `03 Projects/Builder/queue/verifier-build-handoff.md` | replaced Run #1 doc with Sprint 2 handoff (which already shipped 2026-06-06) |
| B (discard + untrack) | `99 _system/logs/daemon-runs.jsonl` | discarded local mods, `git rm --cached`, file preserved on disk, hidden by .gitignore line 47 |

---

## 6. Hermes coordination — context for next session

### Org chart (Andre-locked 2026-06-07)
- **Andre** — principal
- **Mavis** — EA, **SENIOR agent in the fleet**, M3
- **Hermes** — fleet operator, **junior**, deepseek-v4-flash
- **Hermes's workers** — engineering-executor, content-executor, research-executor, ops-executor, specialist-researcher, specialist-verifier, specialist-writer, specialist-extractor (unverified), specialist-code-reviewer (unverified)

**We are NOT peers.** I do not write to his kanban, dispatch his workers, run his crons, or read `~/.hermes/`. He does not write to my vault. We share Andre and that's the only overlap.

### DreBrain clarification (Andre-locked 2026-06-07)
- **DreBrain** = Andre's personal instance of [garrytan/gbrain](https://github.com/garrytan/gbrain). Lives at `~/DreBrain/`. Pilot PARKED (PGLite WASM crash on macOS 26.x, Supabase pooler blocked from this host).
- **Hermes's GBrain** = separate system, HTTP MCP at port 15331, fleet infrastructure. Currently DOWN (connection refused) — Hermes's problem to fix.
- The 25 blocked items in Hermes's kanban are DreBrain residue from before the parking decision. **FROZEN by Andre's standing edict. Do not re-activate. Do not burn cycles on them.**

### Fleet-watchdog spec — GREENLIT
Hermes submitted v2 of the fleet-watchdog proposal. All 5 conditions
from my review addressed cleanly. 6th invariant (zombie cards) integrated.
**Cleared to build.** Per-condition audit in the prompt I sent Hermes.

He will:
1. Build `~/.hermes/scripts/fleet_watchdog.py` (no LLM, no_agent cron, 30-min cadence)
2. Run 3 synthetic violations from the test plan (orphan, double-dispatch, crash-loop)
3. If all pass, register the cron
4. Report back when first production run completes

**Next-session action:** if Hermes reports back with production results,
do a one-pass review of how it actually behaves. One review, not iterative.

### v1.1 follow-up (NOT a blocker)
The orphan invariant will page on the 25 already-frozen DreBrain items
on first run. Two options: accept the noise (v1) or add an
"acknowledged orphans" allowlist (v1.1). Hermes chose v1; document the
v1.1 in a follow-up.

---

## 7. gemma4:12b-it-qat wiring (Andre asked, answered)

Andre asked how to use the local Gemma4 in Hermes profiles. Answer
delivered. The pattern (verified by reading
`~/.hermes/config.yaml`):

```yaml
# In ~/.hermes/config.yaml root:
providers:
  ollama-local:
    base_url: http://localhost:11434/v1
    api_key: ollama  # Ollama doesn't validate, but Hermes requires the field
    api_mode: chat_completions
```

Then per-profile or in fallback_providers. **Recommended mode:** test on
ONE profile first (Mode A), not fleet-wide replacement. **Caveat:** this
bypasses the Mavis harness (no routing/cache/safety/stats). If Hermes
needs harness features on local, that's an OpenAI-compat shim on top
of the harness's `/turn` endpoint — separate build, separate decision.

---

## 8. Memory updates I made this session (for the new session's awareness)

The agent memory at `~/.mavis/agents/mavis/memory/MEMORY.md` was updated
with the senior-agent framing and the gbrain-equivalent clarification.
The full memory will be re-injected at session start, but the new
entries added were:

- **Org chart** added to "Role boundaries — Mavis vs Hermes"
- **DreBrain = gbrain equivalent** added to the same section
- Worker-stall / fleet-watchdog / M2.7-enforcement entries were already
  there from the parallel Mavis sessions that wrote to vault MEMORY.md

The vault's `99 _system/memory/MEMORY.md` has the operational memory for
the EA function. After my chore commit, another Mavis
session wrote to it (the "Hard corrections (today's load-bearing
lessons, 2026-06-07)" section). That edit is in the working tree but
NOT committed. **Do not commit that modification** — it wasn't mine
to author.

---

## 9. Working tree state at handoff (honest disclosure)

```
M  99 _system/memory/MEMORY.md     # written by parallel Mavis session, not me
?? .mavis/                          # Mavis runtime data — should be in .gitignore
?? 00 Inbox/2026-06-04 - *.md       # captures (intentional?)
?? 01 Daily/2026-06-04.md
?? 02 Notes/.../*.md                 # articles, MOCs, ideas, patterns
?? 03 Projects/.../                  # ~30 dirs of drafts, dossiers, runs, shipped code
?? 04 Resources/published/
?? 06 Connections/2026-06-04 - AI-as-companion landing.md
?? 99 _system/.../                  # procedures, scaffolding-reviews, etc.
?? 99 _system/memory/.summary.md, ea-contract.md, fleet-trust-patterns.md, orchestration-failure-modes.md
?? agent/, apps/, mini_harness/, outbox/, phase1_claude_sdk/, tests/
?? check_langgraph.py, hermes.db, memory.db, phase1_*.py/md
```

**The MEMORY.md modification** is the one I authored concurrently with
a parallel Mavis session. I did not commit it; the parallel session
should own that commit.

**The untracked items** are a separate hygiene problem (Bucket X/Y/Z
from my earlier analysis). Bucket X (`.mavis/`, runtime DBs) should
go in `.gitignore`. Bucket Y (vault content) should be committed. Bucket
Z (`sources.jsonl.bak`) should be removed. This is a morning sweep,
not tonight's blocker.

---

## 10. Self-reminder set (verifies the cron tomorrow)

```
mavis cron self check-cron-2026-06-08 \
  --every "0 9 * * *" \
  --timezone "America/Chicago" \
  --ttl 1d \
  --prompt "Verify the daily observability cron (com.mavis.cron) fired at 02:00 CT on 2026-06-08.
  1. Check the dated receipt: ls -la ~/99 _system/scaffolding-reviews/2026-06-08.md
     - Must exist and have a 'Generated:' timestamp from the last 12 hours
     - 'Drift score:' must be a real numeric value (not a placeholder)
     - 'Harness version:' line must be present
     - Router section: 'Total classifications' should reflect the day's actual traffic
  2. Check the launchd stdout log: tail ~/MiniMax-Agent/99 _system/logs/scaffolding-cron.log
     - Must contain 'runner: review_date=2026-06-08'
     - Exit code 0 (no errors in scaffolding-cron.err)
  3. If the file is MISSING or shows placeholder/empty data: report the failure to Andre immediately.
  4. If the file is present and shows live data: report 'cron fired clean' with the drift_score and the runner exit summary. Then delete this self-reminder.
  5. Either way, include the first 20 lines of the receipt in your report so Andre can see what the cron actually wrote."
```

If the next Mavis session starts before 09:00 CT 2026-06-08, the
reminder will still be live and will fire on schedule.

---

## 11. Key file paths (memorize these)

| What | Path |
|---|---|
| Vault root | `~/MiniMax-Agent/` |
| Vault git | `github.com/andrebrassfield/MiniMax-Agent` |
| Harness daemon (running) | `~/.mavis/bin/mavis_harness_daemon.py` (port 11435) |
| Harness main | `~/.mavis/bin/mavis_harness_main.py` |
| Cron runner | `~/.mavis/bin/scaffolding_review_cron_runner.py` |
| Cron plist | `~/Library/LaunchAgents/com.mavis.cron.plist` |
| mavis-cli source | `03 Projects/Builder/drafts/mavis_cli.py` |
| mavis-cli runtime | `~/.mavis/bin/mavis-cli` |
| mavis-cli installer | `03 Projects/Builder/drafts/install_mavis_cli.sh` |
| Hermes config | `~/.hermes/config.yaml` (DO NOT WRITE — peek only) |
| Hermes profiles | `~/.hermes/profiles/<name>/config.yaml` (peek only) |
| My agent memory | `~/.mavis/agents/mavis/memory/MEMORY.md` (auto-injected) |
| Vault operational memory | `~/MiniMax-Agent/99 _system/memory/MEMORY.md` |
| Local Ollama | `http://localhost:11434` (model: gemma4:12b-it-qat) |
| Mavis harness | `http://127.0.0.1:11435` (health, stats, /turn) |

---

## 12. What to do first when the new chat starts

1. **Read this handoff in full** (~5 min).
2. **Check whether `check-cron-2026-06-08` already fired** by reading `~/99 _system/scaffolding-reviews/2026-06-08.md` (if it exists, the cron ran and the self-reminder already verified; clean up).
3. **Check whether Hermes reported back** on the fleet-watchdog build. If yes, do the one-pass production review I committed to. If no, resume the Hermes coordination work.
4. **Continue helping Hermes** dial in his native tools. Andre wants this work tonight. Topics likely to come up:
   - The OpenAI-compat shim on top of harness `/turn` (if Hermes wants harness features on local Gemma4)
   - The "acknowledged orphans" allowlist (v1.1 of the watchdog)
   - Per-profile Gemma4 routing experiments
   - Hermes's three schedulers (content-orchestrator, eng-orchestrator, macro-orchestrator) — topology decision still pending
   - The 5 LLM-driven DreBrain crons that are paused (DreBrain pipeline)
5. **Tighten the working tree** (Bucket X/Y/Z from §9) when Andre signals go.
6. **Don't** touch:
   - The 25 frozen DreBrain kanban items (Andre's standing edict)
   - Hermes's tree (`~/.hermes/`) except for peeks
   - The 8 modifications I committed (already done)
   - The MEMORY.md modification in the working tree (parallel session owns it)

---

## 13. Hard reminders (don't drift)

- **I am senior to Hermes in the fleet hierarchy.** Org chart: Andre → Mavis → Hermes → Hermes's workers. No role-comparisons like "I'm parallel to Hermes."
- **DreBrain is parked.** Don't re-activate without explicit Andre go. The 25 blocked items stay frozen.
- **Spec blocks = design review, not execution orders.** Andre sends multi-message spec blocks; he gives go-signals with "go" / "do it" / "continue building". Do NOT execute mid-review.
- **No deploys / pushes / external sends / destructive ops without explicit in-session approval.** Quote what you're reading. Audit the filesystem before writing. Push to remote after every meaningful commit.
- **Workers may lie about their session model.** Verify independently via `mavis session info` if cost discipline matters. Default-M3 enforcement doesn't work per-agent yet (system default wins).
- **Worker stall at the same step (twice) = take over.** Don't wait for a third attempt. M3 has the synthesis + design capability; the ledger has the verified claims.

---

## 14. Sign-off context

Andre signed off operationally but wanted to keep going tonight. He
asked for this handoff so a fresh chat can pick up. The new session
should treat this document as authoritative for "where we left off"
and verify any state (cron fired? Hermes reported back?) before acting.

The handoff itself is durable in the vault. The next Mavis session
will read it on demand via `mavis memory get` or by path lookup.

— Mavis (EA, senior agent in the fleet)
   Session `mvs_bece5d0cde364a528fc801129f24563f` closing
   2026-06-07 16:33 CT
