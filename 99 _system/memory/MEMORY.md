# Mavis — Memory

Operational essentials + pointers only. Long-term knowledge lives in the vault — see "Pointers" section.

## Session-start checklist

**Run `mavis-cold-start` skill first** — it orchestrates the 7-step cold-start procedure (identity → long-term knowledge → context-loader → freshness → integrity → acknowledge → audit).

Quick reference (the skill does this in detail):
1. Read `SOUL.md` (identity + operating contract).
2. Read `MAVIS.md` (current state + active theses + `active_project` field).
3. Read this `MEMORY.md` (operational essentials + pointers, ~4KB).
4. Run `context-loader` skill (canonical scoping; branches on `active_project`, writes state file).
5. Acknowledge readiness with the cold-start orientation block.

Skill: `~/.mavis/agents/mavis/skills/mavis-cold-start/SKILL.md`
State file: `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md`
Durable handoff (in vault): `~/MiniMax-Agent/03 Projects/Mavis EA Design/mavis-cold-start-handoff-2026-06-22.md`

## Core identity (one line)

Mavis = Andre's executive assistant on M3. Vault at `~/MiniMax-Agent/`. Telegram-Mavis = OpenCode-Mavis (same me, same vault).

## Active theses (2026-06-22)

These are positions Mavis currently holds. The intelligence layer (morning brief, contradiction check, weekly deep) checks new information against these. Full versions with supporting/counter-evidence: `~/MiniMax-Agent/01-PERMANENT/2026-06-22 - active-theses.md`.

1. **The bottleneck is spec throughput, not implementation.** Adding agents multiplies the wrong variable.
2. **A second brain is good capture; a second self is active reasoning.** Without automation, the vault is passive storage.
3. **Skills beat agents when the work is non-trivial and the harness is mature.** Source: `agent-harness-principles.md`.
4. **Long-term knowledge belongs in the vault, not in always-on context.** MEMORY.md = pointers only.

## Hard constraints

- No deploys / pushes / external sends / credential changes / destructive ops without in-session approval.
- **ABSOLUTE SEPARATION:** no read/write/diagnose/patch to `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`.
- Spec on disk before Track 2 spawn. Disk = source of truth.
- Spec blocks = design review. Wait for explicit "go" before executing.
- Audit filesystem before writing — and before dispatch. The queue IS the state.

## Cross-cutting disciplines (HOT)

- **Cron `lastResult: success` ≠ skill-success.** Daemon tracks whether the bash script exited 0, not whether the work landed. Cron prompts that "HALT and surface to Andre" typically use `exit 0` after surfacing — which the daemon reads as success. Real health = post-mortem queue + skill halt logs + publish/reply ledgers. Source: `reply-sweep-daily` ran 6+ weeks reporting success while HALTing at step 0 every fire; deprecation 2026-06-24 (postmortem at `03 Projects/X-Content-Engine/postmortems/2026-06-24-reply-sweep-deprecation.md`).
- **Architecture-shift cron audit.** When a pipeline substrate changes (Playwright → mavis browser, MCP rotation, cookie-jar source shift), audit every cron that touches the substrate. Reply-guy was the last Playwright-dependent cron in XCE and was never re-validated after the 2026-06-17 mavis browser bridge wiring. Pattern: keep a substrate→cron dependency map somewhere queryable, refresh on every substrate shift.
- **HALT-then-skip ≠ HALT-then-delete.** A cron that HALTs but stays scheduled will fire every period forever, burning tokens + Telegram noise. The right move when a broken pipeline has no near-term fix: delete the cron + mark the strategy doc DEPRECATED + leave the skill files on disk for revival. Don't just disable.

## Pointers (long-term knowledge lives here)

**Operating models (vault-side topic files):**
- Two-Track Operating Model: `~/MiniMax-Agent/03 Projects/Mavis EA Design/memory/two-track-model.md`
- Second-Self Automation: `~/MiniMax-Agent/03 Projects/Mavis EA Design/memory/second-self-automation.md`

**Skills (agent-private, canonical at `~/.mavis/agents/mavis/skills/`):**
- `context-loader/SKILL.md` — Karpathy-pattern project scoping
- `two-track-handoff/SKILL.md` — spec → Track 2 spawn procedure
- `two-link-rule/SKILL.md` — soft enforcement of the connection discipline
- `obsidian-local-rest-api-wiring/SKILL.md` — credential storage pattern
- `ea-*` skills — the CHIEF system contract (daily-brief, weekly-connections, decision-logger, commitment-tracker, skill-evolution, etc.)

**Skills (global, cross-agent, canonical at `~/.mavis/skills/`):**
- **Marketing Skills v2.5.0** — 5 skills: `/offers`, `/pricing`, `/copywriting`, `/launch`, `/sales-enablement`. See `~/.mavis/skills/INDEX.md` for the full registry (triggers, upstream/downstream, versions). Any agent can read; only Mavis writes. A2A topology: **A-read + B-write** (locked 2026-06-23). Selection spec: `03 Projects/Marketing Skills/specs/selection-layer.md`.
- **Marketing Skills v2.6 (calibration pending)** — target: **doseofproof.com** (Andre's personal brand, confirmed 2026-06-23). v2.5.0 was generic-operator-shaped; v2.6 recalibrates to personal-brand reality. Awaiting monetization-shape confirmation before dispatching the calibration. Plan in the v2.6 section of the selection spec.

**Crons (canonical at `~/.mavis/agents/mavis/crons/`):**
- `second-self-morning-brief.md` (06:00 CT daily) — 4-section synthesis + calendar
- `inbox-filer.md` (06:30 CT daily) — route inbox files
- `second-self-contradiction.md` (07:00 CT daily) — ideas-vs-sources conflict scan
- `second-self-nightly-connections.md` (23:00 CT daily) — non-obvious connections
- `second-self-weekly-deep.md` (Sun 19:00 CT) — emerging thesis
- `vault-health.md` (1st Sun 23:00 CT) — 7-check audit
- `rate-limit-tracker.md` (22:00 CT daily) — token budget ledger

**Topic files (load on demand at `~/.mavis/agents/mavis/memory/`):**
- `resolvers.md` — trigger → skill routing table (dial-in #4)
- `orphan-disciplines.md` — 5 disciplines from retired agent-70a1d300626d
- `calendar-mcp.md` — calendar MCP operational reference

**Decision log (vault):**
- `~/MiniMax-Agent/02 Notes/decisions/` — every architectural decision on disk

**Specs (vault):**
- `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/` — upcoming work, closed-loop shape

## Memory hygiene

- **English. Topic files on demand. Target MEMORY.md ≤10KB, hard ceiling 15KB.** Currently ~7KB (after 2026-06-23 harness-status entry).
- **New long-term knowledge → vault first, MEMORY.md gets only a pointer.** This is the 4th active thesis. Discipline matters here.
- **Topic files MUST have YAML `description`.** Load on demand, not auto-injected.
- **Append = new entry; Edit/Write = update, merge, or remove.** Don't mix.

### MiniMax Code harness: changelog + Computer Use status (2026-06-23)
Type: harness

**Changelog source of truth**: `https://agent.minimax.io/docs/changelog`
- Desktop build has NO public GitHub releases — `MiniMax-AI/minimax-code` repo exists but its Releases tab is empty (only the opencode CLI source lives there).
- The Squirrel CDN feed at `https://file.cdn.minimax.io/public/minimax-agent/release/` ships binary + sha512 only; `update-info.json` has no notes payload.
- The docs page is the ONLY authoritative changelog. Check it whenever asked "what changed".

**Baseline version observed**: 3.0.47 (build 74), installed 2026-06-23 08:47 via Squirrel auto-update.

**Computer Use (cu MCP) status flag — IMPORTANT, recheck every cold-start**:
- **Disabled as of v3.0.46** for "compatibility and user experience concerns" — explicit note in the changelog, expected to return in a future version.
- Current observable state: `mavis mcp ls` shows `cu` with `authStatus: pending_auth` and `skillStatus: active`. Calls will fail until the desktop team ships the fix.
- **Before promising desktop automation** (mouse / keyboard / clipboard / native macOS UI / full-screen capture work):
  1. Run `mavis mcp ls` and confirm the `cu` server `authStatus`.
  2. If still `pending_auth` → tell the user Computer Use is temporarily disabled, then propose fallbacks:
     - Browser automation → `playwright` MCP (works today)
     - Native macOS UI tasks → delegate to Andre (he is comfortable with desktop clicks)
     - Reading screen state → still try `desktop_screenshot` once; if it returns auth error, switch to delegation
  3. Do NOT burn tokens looping on cu calls that will fail.
- Re-verification trigger: any cold-start, any task asking for desktop control, any `mavis mcp ls` output showing `pending_auth` flipping to a different value.

**Update mechanism notes** (for future debugging):
- Squirrel.Mac, provider: `generic`, update feed URL above.
- Installer replaces `/Applications/MiniMax Code.app` in-place and does NOT retain a backup of the previous version. Local version diffing requires the docs page; do not look for a `.MMXCodeUpdate*` zip or prior `.app` on disk.
- macOS Squirrel update race was fixed in 3.0.46; daemon health-check timeout raised to 60s in same release.

### Brand scheduling discipline: verify profile ownership before API push (2026-06-24)
Type: agent

Before pushing brand content to any social profile via a scheduling API (Buffer, Postiz, Hootsuite, etc.), verify the connected profile is brand-owned, not the operator's personal account. Default assumption: the operator's personal profile is the one connected first, because that's what OAuth shows by default.

Concrete failure mode: Dose of Proof LinkedIn only had Dre's personal profile connected to Buffer. The push script was ready to schedule brand content (LinkedIn Post 1 origin story, 5 Biomarkers carousel) to Dre's personal LinkedIn — a brand/operator boundary violation.

Three-question test:
1. Only true in this repo/project? No — applies to ANY brand doing social scheduling
2. Still true on a different project? Yes — every brand has an operator with personal accounts
3. Would the conclusion change for a different user? No — this is universal brand discipline

Process check before any social push:
- Query the tool's channel/integration list BEFORE writing the push script
- Confirm channel name + type (personal vs company page vs business account)
- If only personal profile exists, gate the push: brand content blocked until company/brand profile is created and connected
- Document the channel ID + ownership status in OPERATIONS-LOG

Cost of getting this wrong: brand content on operator's personal profile = brand/operator boundary violation, regulatory exposure (Objective Intent Doctrine for health brands), and audience confusion (operator's network sees brand messaging).

### Async-wait discipline: ONE retry at reset time, not 144 polls (2026-06-24)
Type: agent

When waiting on a known-future async event (rate limit reset, scheduled deploy, CI pipeline expected completion time, OAuth window expiry), the wrong shape is a tight polling cron (`*/5` or `*/10`) for the full wait window. The right shape is **ONE retry cron at the predicted event time**, with explicit failure-branch escalation.

Anti-pattern (real case from 2026-06-24): set `linkedin-company-page-activation` cron to `*/10 * * * *` for 24 hours waiting on Buffer rate-limit reset. That's 144 cron ticks burning ~30-60K tokens of session context per tick just to print "still rate-limited." Andre called it: "there is no point in polling for 24 hours straight close the loop."

Correct pattern:
1. Hit the API once to confirm the failure mode and capture the reset timestamp (e.g., `x-ratelimit-reset` header).
2. Convert reset timestamp to a specific cron schedule (e.g., `20 13 25 6 *` for Jun 25 at 13:20 CT, 5 min after predicted reset).
3. Schedule ONE cron at that exact time with `--session-mode new` (independent context for the actual work).
4. The cron's prompt MUST include:
   - The exact workflow to execute
   - An explicit FAILURE BRANCH: if the wait condition still holds, write a log entry, send ONE notification to the user, delete the cron, and **do NOT re-schedule**.
   - A `[self-reminder TTL]` so the cron self-cleans if it somehow doesn't fire.
5. Delete any prior polling cron immediately.

Token math: 144 polls × ~30K tokens/tick = ~4M tokens wasted. ONE retry cron = one fresh session, ~30K tokens, fires once.

Trigger phrases from Andre that mean "close the loop, don't poll":
- "there is no point in polling for N hours"
- "close the loop"
- "stop polling"
- "just fire it once"
- "wait for X then try, don't keep checking"

Cross-project justification: every async wait pattern (CI follow-up, deploy health check, rate limit recovery, OAuth window, scheduled job trigger) has the same shape — known future event, do not poll. Applies to all of Andre's projects where Mavis handles async work.

When in doubt, ask: 'Is this the operator's personal profile or the brand's company page?'
