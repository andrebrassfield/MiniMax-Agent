---
description: "Fleet-orchestration failure incidents and recovery disciplines — vault destruction, hung workers, long-inference auto-abort, orphan spawns, cron-watch heuristics, abort-to-solo. Load when debugging worker stalls, recovering from a fleet incident, or designing abort/recovery patterns."
---

# Orchestration Failure Modes

The EA patterns learned the hard way — incidents + recovery. Process/feedback patterns (verdict-before-synthesis, cascading-effect patches, delegation, Verifier rigor, audit-nit propagation, no-handshake-loops, queue-read) live in `fleet-trust-patterns.md`.

All entries are cross-project durable: any agent fleet that uses filesystem-as-source-of-truth and async worker dispatches.

---

## 1. Vault destruction incident — 2026-06-05 11:28→11:42 CT (hard correction)

**The signature.** A vault-wide destruction where the entire `/Users/brassfieldventuresllc/MiniMax-Agent/` directory tree was gutted to 4 entries (only `.smart-env/`, `99 _system/` with partial contents, plus `.`/`..`). All git history lost (no `.git/`). All projects, all daily briefs, all notes, all resources, all project handoffs, all worker queues, all memory files — gone. Recovery was via macOS Finder Trash → "Put Back" (Finder preserved the original-path reference that shell `mv` could not).

**Timeline (best reconstruction).**
- 11:23 — migration commit `fc0d308` landed clean
- 11:27 — first atomic commit sequence (`5c4abb6` "Operation Last Mile", then `git reset --soft HEAD~1` + `git reset` to undo)
- 11:28 — `mavis-trash /Users/brassfieldventuresllc/MiniMax-Agent/99\ _system/scripts` (intended to trash only the framework-drift Node.js mess)
- 11:28-11:42 — multiple failed osascript recovery attempts and shell `mv` operations
- ~11:42 — vault shown as gutted to 4 entries; the entire `/Users/brassfieldventuresllc/MiniMax-Agent/` had been moved to Finder Trash
- 11:54 — Andre manually did Finder Trash → Put Back to restore the vault; recovery verified clean

**Likely cause.** The `mavis-trash 99\ _system/scripts` command on macOS uses osascript `tell application "Finder" to delete POSIX file "$file"`. The backslash-escaped path was passed to bash, then to mavis-trash, then to osascript. The most likely failure mode: the escaping was misinterpreted at some layer, and the POSIX file path resolved to the parent dir `MiniMax-Agent` (the vault) rather than the intended subdir. The other 3 attempts (osascript queries, shell `mv`) were recovery attempts and FAILED without moving anything.

**Why I didn't catch it sooner.** I assumed the mavis-trash only removed the targeted subdir. I didn't verify the rest of the vault was intact until 11:42, when a `git log` check returned "fatal: not a git repository". The "Operation not permitted" error from `mv ~/.Trash/MiniMax-Agent ~/` is a macOS SIP protection on the user trash — shell tools cannot read or move out of `~/.Trash/`. Only Finder can "Put Back" trashed items.

**Four prevention rules (locked 2026-06-05).** Cross-cutting hard corrections — see MEMORY.md "Hard corrections" for the 1-line version. Full rationale here:
1. **Always quote paths with double-quotes** in shell commands. Backslash-escaping spaces is fragile. POSIX path resolution at the osascript layer may not handle backslash-escaped spaces correctly. Hard rule: `"$path"` with double-quotes everywhere, no exceptions. Example fix: `mavis-trash "/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/scripts"`.
2. **Push the vault to remote after every meaningful commit.** Without remote backup, vault destruction = total data loss. The 2026-06-05 incident is fully recoverable BECAUSE Andre had Finder Trash with Put Back. Without that, the data was gone. Default: push to `git@github.com:andrebrassfield/MiniMax-Agent` after every commit, or set up a post-commit hook. Verify SSH key in the agent's keychain.
3. **Atomic commits require clean staging area.** When the user gives specific `git add` commands, verify the staging area is clean first (`git diff --cached --stat`). Otherwise `git commit` captures all staged changes, not just the user's scope. The first atomic commit was bundled (18 files instead of 2) because I trusted the user's `git add` without checking the prior staging state. Better: `git reset` first, then the user's `git add`, then commit.
4. **Use explicit per-file `git add`, never recursive `git add <dir>` or `git add .`,** when the staging area has unrelated pre-existing modifications. The vault's working tree is rarely in a fully clean state. Recursive adds sweep them all in. Tactical pattern that worked: `git add path1 path2 path3`. Always run `git diff --cached --stat` before `git commit` to verify the staged scope matches intent.

**The vault-watchdog cron (post-correction).** Set a 5-min watch via `mavis cron self vault-watchdog --every 5m` that verifies:
- `/Users/brassfieldventuresllc/MiniMax-Agent/.git` exists (failure → page Andre immediately)
- `00 Inbox/`, `01 Daily/`, `02 Notes/`, `03 Projects/`, `99 _system/memory/MEMORY.md` all exist
- `git -C /Users/brassfieldventuresllc/MiniMax-Agent log --oneline -1` returns a valid commit hash
- Stale detection: if the cron fires and the last successful integrity check was > 30 min ago, surface to Andre

The cron does NOT verify content; it just verifies the vault's structural integrity. Content integrity is the Verifier's job.

Pairs with "Vault rule (locked 2026-06-05)" in MEMORY.md — the durable knowledge must live in the vault, but the vault itself must be protected. The two rules together: vault = source of truth (write side) + vault integrity must be guarded (protection side).

---

## 2. Hung worker on rate-limited model → silent 12h orchestrator timeout (2026-06-04/05)

**The signature.** A worker session running on the same model the user just hit a rate limit on (in our case, `minimax/MiniMax-M3` doing a deep-research task) hangs silently. Observable shape:
- Engine re-sends the task prompt 2–3 times within ~12 minutes (3 message events with no outbound text from the worker between them)
- Session `status.type` stays `started` the entire time — the worker is alive but producing zero text, zero tool calls, zero deliverable file writes
- Engine fires a 15-min "hang alert" (warning only; doesn't kill)
- Worker's `effectiveModel` matches the model that was rate-limited in the parent context
- Plan status shows `attempt: 0` because the worker hasn't even completed one turn to be scored

**What I did wrong.** Cancelled the plan, tried to take over solo in the same orchestrator session — read both input files, started writing `analysis.md` — and then the orchestrator session went idle. 12 hours 23 minutes later, the runtime auto-aborted the orchestrator turn. The work-in-progress (`analysis.md`) was preserved on disk because it had been written before the idle, but the user was left without a final report and no closure signal. Irony: the failure mode we were researching for them is the same one that broke our own delivery loop.

**The orchestration correction — abort-to-solo heuristic.** When the team plan has a hung worker AND the cause is plausibly the same rate-limit pressure the user just experienced, **the EA takes over and finishes solo in the same session** instead of cancelling-then-recovering. Concretely:

| Detection signal | Action |
|---|---|
| 2+ consecutive task re-prompts to the same worker with no deliverable file appearing | Steering probe: send a one-line "are you stuck? check API rate limits" nudge, wait 2 min. |
| 15-min hang alert fires AND parent context had a rate-limit incident in the last 60 min | **Abort to solo.** Cancel the plan, do remaining work directly in the orchestrator session. Do NOT launch a fresh plan. |
| 25 min elapsed on a 30-min cap with no deliverable file written | **Abort to solo.** Same path. |
| Multiple workers (>=2) showing the same hang signature in parallel | Fleet-wide rate pressure. Abort the entire plan, go solo, do not re-launch. |
| Worker produces 1 partial file then hangs | Salvage mode: copy the partial to the canonical path, abort, finish the rest solo around it. |

**The EA solo-finish protocol** (when triggering abort-to-solo):
1. `mavis team plan cancel <id>` — preserves files, halts workers.
2. Survey what artifacts exist on disk; read each, note gaps.
3. If `analysis.md` or equivalent is partial but salvageable, finish writing it FIRST.
4. Read the partial carefully. Don't blindly continue — verify the section structure matches the skill spec.
5. Do NOT re-launch the plan, do NOT spawn a new worker. Solo means solo.
6. After final.md is written, report back to the user with the file path + one-line summary + duration.
7. Update memory with the incident signature so the heuristic is stronger next time.

**The 12-hour-orchestrator-timeout is the second-order failure.** The first-order failure was the hung worker. The second-order failure was the orchestrator session going idle mid-recovery. The mitigation: after cancelling a plan, **finish or explicitly park the recovery in the same turn.** Don't read both inputs and stop. If context budget is too tight for the full synthesis, write a stub `analysis.md` with a clear "owner session was throttled, continue from here" header and park. Better to land a checkpoint than to leave the user wondering for 12 hours.

Pairs with "Cron watches for workers must verify deliverable existence, not just session status" — same underlying principle (filesystem is source of truth, not session lifecycle), different application.

---

## 3. Long-inference auto-abort pattern with heavy web research (2026-06-05)

**The signature.** A session that runs 8-12+ parallel web searches + multiple file reads in a single turn, then attempts a large Write output, can be auto-aborted by the runtime ("推理长时间无响应"). The retry starts fresh, losing in-flight work.

**Why it happens.** The context window fills with search-result payloads (each search ~1-3K tokens) before the Write. When the LLM starts a long generation turn, the inference latency exceeds the runtime's safety threshold. The system aborts rather than risk a stuck turn.

**Mitigation (chunk-first, write-second):**
- **Summarize intermediate findings** into the dossier structure BEFORE running more searches. Use a small Write to checkpoint: "Phase 1.1 done: X, Y, Z. Phase 1.2 pending: A, B, C."
- **Cap parallel research calls** to 4-6 per turn. Run subsequent research batches in later turns, after checkpointing what you have.
- **Write the dossier in sections**, not as one big file. First Write: frontmatter + section 1. Second Write: section 2. Third Write: section 3. Each Write is short, completion is checkpointed.
- **Use TodoWrite to track dossier sections.** The completion signal survives retries.

Pairs with "Abort-to-solo heuristic" (2026-06-04, rate-limit cascade lesson) and "The 12-hour-orchestrator-timeout" — three auto-abort failure modes, three different triggers, same fix: checkpoint early, finish in the same session, signal closure.

---

## 6. Orphan-spawn pattern: placeholder 'X ready for Y' prompts with no task spec (2026-06-06)

**The signature.** A worker session is spawned from the parent with `mavis communication send --command spawn --content '{"agent":"<name>","prompt":"X ready for Y"}'`, but the prompt is a status signal, not a task spec. The session boots, sends a 'ready' ack, and waits indefinitely. No scratchpad content, no workspace content, no originating user message. The parent (me) is attributed as spawner but didn't actually issue the spawn.

**Concrete instance (2026-06-06 09:55-09:56 CT).** Two sessions spawned from my root session in 38 seconds with empty scratchpad/workspace and no user message in between: one Researcher ("ready for sources ledger append") and one Builder ("ready for Sprint 1"). The Researcher politely asked what I wanted. I asked for the originating spec — they had none. Confirmed it was a daemon-level misfire (likely a hook/cron/auto-spawn), aborted both.

**The fix (when this happens again):**
1. **Don't accept the task.** The prompt is a status signal, not a spec. Asking for clarification is the right move.
2. **Check for siblings.** If one orphan spawned, more may have. Run `mavis communication messages --from <mysession>` to see all spawns.
3. **Abort and clean up.** `mavis session abort <id>` works for most.
4. **Note the pattern in memory and tell Andre.** A single orphan could be a one-off, but 2+ orphans in <1 minute = something is auto-spawning. Worth surfacing.

**Discriminator vs. normal spawn-with-prompt.** A normal spawn sends a status signal as the initial prompt, then follows up with the real task as a separate `--command prompt` message. An ORPHAN spawn sends ONLY the status signal and never follows up. The presence/absence of the follow-up task prompt is the discriminator. Always check `mavis session messages <workerId>` before accepting work.

Pairs with "Spawn-lifecycle gotcha" in `tool-quirks.md` — same spawn mechanism, different failure mode. That entry teaches that placeholder-prompt + task-prompt is normal. THIS entry teaches that placeholder-prompt with NO task-prompt is an orphan, not a normal spawn.

---

## 11. Cron watches for workers must verify deliverable existence, not just session status (2026-06-04)

On 2026-06-04 morning, I set up a cron to watch the Builder on the Artemis status board (60-90 min budget). The cron checked `mavis session info` for `started` vs `error` vs `finished` status. The Builder received the prompt at 09:33, produced 5 empty assistant messages, went into `finished` state at 09:38, and stayed idle for 25+ minutes. The cron kept reporting "Builder in flight, started" because the session was technically alive. The actual artifact (`artemis_status_board.html`) was never written.

**Three things I should have done:**
1. **Check the file system as the source of truth, not the session lifecycle.** The `finished` session status is ambiguous — it can mean "the worker shipped a handoff" (good) OR "the worker went idle without producing output" (stalled). The cron was reporting "in flight" when the Builder was actually stalled. The file system tells the truth: if `artemis_status_board.html` doesn't exist or its mtime is > 30 min stale, the Builder is stalled.
2. **Define explicit file-watch logic in the cron prompt.** The cron instructions should specify: check the artifact file's mtime, check the handoff file's existence, AND check the session status. The three together give a complete picture. Session status alone is insufficient.
3. **Build a nudge mechanism into the cron.** If the cron detects a stall, the recovery action is: send a `mavis communication send` to the Builder asking for status, with a follow-up: "If the artifact is not yet written, continue with the build. If the artifact is written but no handoff, write the handoff now." The nudge converts a stall into a continuation.

**The right cron pattern (post-correction):**
- Primary: check file existence and mtime
- Secondary: check session status for the error case
- Tertiary: send a nudge if the file is missing or stale
- Quaternary: surface to Andre if nudge doesn't recover within one tick

Pairs with the abort-to-solo heuristic — same underlying principle (filesystem is source of truth, not session lifecycle), different application (cron monitoring vs. abort-to-solo decision).

---

## 12. Don't patch other agents' daemons from this side — file an incident and move on (2026-06-12)

**The signature.** A long-running daemon in another agent's filesystem territory gets stuck in a spin loop. The bug is real, the loop is burning CPU, and the dispatcher isn't processing work. From Mavis's shell, it looks like the fix is one sed/python one-liner away.

**Mavis's rules around this (from the 2026-06-12 incident, hardened 2026-06-16):**

1. **Do NOT patch other agents' daemons from a Mavis session.** It lives in their territory. Even if I have filesystem access, touching another agent's daemon from this side is overstep. The right move is to file an incident card documenting the symptom + diagnostic snippet, then leave it for the responsible agent.
2. **Cancelling my own cards does NOT fix the loop** — verified. The bad byte is in something pre-existing. My cancelled cards don't appear in the dispatcher's exception trace.
3. **If the dispatcher's loop is blocking work I need done**, options are: (a) `pkill -f <daemon>` to free CPU (the responsible agent will likely respawn it), (b) send the responsible agent a direct message via the kanban card, (c) wait for them to fix it. Default to (c) unless explicitly told otherwise.
4. **The bug can be a useful data point for the cutover:** when building replacement infrastructure, use the failure mode as a reason to do strict input validation at the tool boundary, not in a long-running poll loop. The validation pattern is the durable lesson, not the symptom.

**Diagnostic snippet for any agent (no daemon modification needed):** brute-force scan of `tasks`/`task_events`/`task_comments`/`task_attachments` for non-UTF-8 bytes. Can be run from a different agent's session without modifying the broken daemon.

**Cross-project relevance:** the rule "don't patch other agents' daemons from this side, file an incident and move on" applies to any fleet with multiple agents in separate filesystem territories. The dispatcher loop is the responsible agent's domain; Mavis's responsibility is to surface it cleanly.

**Hardened 2026-06-16:** per the new ABSOLUTE SEPARATION rule, Mavis doesn't even diagnose another agent's runtime. Surface the symptom, attach the diagnostic snippet, route to the responsible agent. The new rule supersedes this entry's "run a diagnostic scan" step — the scan was useful for Mavis's own awareness, but the new boundary is: not even that. Hand off the symptom, no ownership transfer.

---

## 7. Cron-driven autonomous workflows — the X-Content-Engine auto-publish pivot (2026-06-16)

**The signature.** Andre's "Full Autonomy mode" directive asked Mavis to post approved drafts to @DreTheSalesGuy via the live browser. The architecture has a "no auto-publish" guideline in `scribe.md` Hard Rule #10 and the `team-config.md` ("Not a posting engine. The Scribe drafts. Andre publishes."). The Scribe's no-publish rule is for the Scribe agent; the team-config is a guideline, not a hard-locked separation. The right pivot: cron-driven Mavis sessions that perform the publish step on a schedule.

**Why cron > live-browser from this session:**

| Live browser (failed path) | Cron-driven (adopted path) |
|---|---|
| Active tab drifted to a Hermes Agent Dashboard mid-task; compose modal didn't open in test snapshot | Cron tick spawns a fresh session, claims a fresh tab, executes the procedure in isolation |
| cu (Computer Use) is per-session toggled off; can't take screenshots or use desktop_left_click/desktop_type | mavis browser tool is per-session and works in the cron session |
| Single point of failure: if anything goes wrong, the post is half-done in the same session | Failure halts the cron session cleanly; the post didn't happen; cron self-deletes only on success |
| No audit trail between "navigate" and "Post clicked" | Atomic write to brain's `performance_log` with post_url, hook_used, date — full audit trail |
| No pacing — risk of triggering X.com rate limit if multiple posts in quick succession | Schedule per post (4h pacing); X.com rate limit is well within bounds |

**The cron-prompt-as-skill pattern.** Each cron's `--prompt` is a self-contained skill:
- **Self-contained data:** the post text inline (no file-read at trigger time) — the cron is the source of truth, not a thin pointer
- **Procedure:** Final Audit (verify approved/ file + x-analytics for duplicate hooks) → browser open_tab/navigate/snapshot/click/type/snapshot/click/extract-url
- **Output schema:** atomic write to `content_brain.json` performance_log with `post_id`, `hook_used`, `views: 0`, `likes: 0`, `date`, `_note` describing the cron name + fire time
- **Halt conditions:** login prompt, rate limit warning, text mismatch on checksum (load-bearing specifics: dollar figures, key numbers, em-dashes), UI change — HALT with the exact UI state, do NOT auto-retry
- **Cleanup:** `mavis cron delete mavis <cron-name>` as a post-success step. One-shot crons self-destruct after firing
- **Failure handling:** do NOT delete the cron on failure (preserves the audit trail for human inspection)

**The cron schedule (the v2 batch as canonical example):**

| Cron | Schedule | Next fire (CT) | Why this time |
|---|---|---|---|
| `post-1-v2-2026-06-16` | `30 20 16 6 *` (CT) | 2026-06-16 20:30 | 19 min from cron creation; buffer for the parent session to settle |
| `post-2-v2-2026-06-16` | `30 0 17 6 *` (CT) | 2026-06-17 00:30 | +4h from post-1; 4-hour pacing per X.com rate-limit hygiene |
| `post-3-v2-2026-06-16` | `30 4 17 6 *` (CT) | 2026-06-17 04:30 | +4h from post-2 |
| `analytics-v2-batch-2026-06-16` | `30 20 17 6 *` (CT) | 2026-06-17 20:30 | +24h from post-1; first analytics check after the batch |

**Self-reminder for async handoff verification.** Per the Mavis cron self-reminder rule (MEMORY.md §"Cron silent-tick default"), every async handoff gets a `mavis cron self <name> --every 30m --ttl 2h --prompt "..."` reminder. For the v2 batch: `check-post-1-result-2026-06-16` (every 30m, 2h TTL, auto-expires at 22:13 CT). The reminder checks `mavis cron info mavis post-1-v2-2026-06-16` — if the cron self-deleted, the post went through; if still active or in error state, surface to Andre immediately.

**Cross-project lesson:** any "auto-do-X" workflow should be cron-driven, not live-session-driven. The cron prompt IS the skill. The cron tick IS the model loop. The session-mode `new` creates a fresh Mavis session per tick (independent recurring task), `--session-mode sessionId` routes to a specific session (self-reminder / CI follow-up). For one-shot production tasks, target a specific date+time in the schedule, not a recurring interval — the cron is naturally one-shot by virtue of its schedule, and self-cleanup keeps the cron list from accumulating dead tasks.

**Pair with `agent-harness-principles.md` §"Cron as thin harness" and `tooling-gotchas.md` §"mavis cron syntax + browser bridge."**
