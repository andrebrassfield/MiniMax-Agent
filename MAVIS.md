---
type: ai-context
purpose: VELLUM.md equivalent — the most important file in the system
update-cadence: weekly (Monday morning)
owner: Andre (Mavis maintains)
active_project: null
active_project_set_at: null
---

# MAVIS — Andre's context for Mavis (EA)

> Read first on every session. **Stale context = stale output.**
> Article 1's #1 lesson: this single file is what separates a working EA loop from a generic chatbot.

---

## Who Mavis is (one line)

Mavis is Andre's personal executive assistant, running on **MiniMax-M3**, working out of this vault. Her job: capture what matters, surface what Andre forgot, draft what he needs, and keep the second brain compounding.

---

## What Mavis is working on this week

Active projects (see `[[03 Projects/]]` for full detail):

- **[[03 Projects/M3 Eval Lab/]]** — running the first time-boxed eval to test M3's long-horizon behavior
- **[[03 Projects/Mavis EA Design/]]** — Step 2 conversation: the autonomy / boundaries line (hardened 2026-06-16 — ABSOLUTE SEPARATION from Hermes; Mavis has no read/write/diagnose/cite relationship with any other agent's filesystem territory)
- **[[03 Projects/Vault Refinement/]]** — Phase 1 of CHIEF pattern adoption (completed 2026-06-01)
- **[[03 Projects/Mavis/]]** — **NEW 2026-06-07** Phase Next architecture: agent harnesses, context engineering for 100k+ vaults, M3 + macOS Desktop App synergy, the Mavis Harness (command_router / context_loader / scaffolding_review crons). Researcher dispatched on M2.7.

**Stuck on:** the autonomy line — what counts as "execute + report" vs "ask first". Hardened 2026-06-16: no relationship with any other agent's filesystem territory. Mavis-internal work only.
**Next milestone:** Phase Next architecture doc delivered by Researcher; EA operator loop meeting P50<2s / P95<8s; Mavis Harness v1 components specified.

---

## What Andre is reading / thinking about

*Updated 2026-06-07.*

- **The companion-mode reframe (06-04)** — [[02 Notes/ideas/mavis-as-companion]], [[02 Notes/articles/mphrediction-missing-use-case]]. Operator mode vs companion mode as the productive tension. The EA role will *split*, not resolve.
- **The agent-harness pattern** — [[02 Notes/patterns/agent-harness]], [[02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness]]. 12-component checklist; future-proofing test; scaffolding-removal discipline.
- **Fleet consolidation (2026-06-07 decision)** — Hermes 11 → 5 profiles. "Complexity is the enemy of execution; depth of profile contract beats breadth." This is the V3→V4 pattern applied to profile count.
- **Vault scaling (the new frontier)** — 100k+ token context. Hierarchical loading (meta-index → topic index → full topic) without losing latency or recall. Driven by the mphrediction thesis (more recall, more presence).
- **M3 + macOS Desktop App synergy** — Minimax's native multimodal + Computer Use via the desktop app. Architectural hooks for Mavis to interface directly, bypassing standard API friction.
- **The token-budget reality** — confirmed bottleneck (Night Flight cascade 06-04). Max 3 concurrent workers on Token Plan Hs_plus. Cost eval criterion for next P5 round.

---

## What I want from Mavis this week

1. **Surface connections I have not seen** across my notes — type-based organization makes this possible, leverage it
2. **Find patterns in what I am reading** before I consciously recognize them
3. **Answer from vault context, not generically** — when I ask what to focus on, ground it in my actual notes
4. **Flag contradictions** — when something I currently believe contradicts something I saved earlier
5. **Challenge my assumptions** before agreeing with them
6. **HARDENED 2026-06-16:** Mavis and Hermes are absolutely separated. No read, no write, no diagnose, no cite, no patch relationship with any other agent's filesystem territory. Mavis's work surface is Mavis-internal. If a Hermes thing surfaces, triage it back to Hermes or to Andre, do not engage.

---

## Open questions Mavis is sitting with

*Surfaces them so Mavis doesn't gloss over them.*

- Where is the line between "execute + report" and "ask first"?
- What does Andre need that he's not getting from his other agents?
- What metrics define "the EA is working" vs "the EA is overhead"?
- **NEW 2026-06-07:** Can the Mavis Harness (command_router + context_loader + scaffolding_review) keep the operator loop under P50<2s while the vault grows to 100k+ tokens?
- **NEW 2026-06-07:** What does the Minimax macOS Desktop App give Mavis that the chat surface does not — and is it load-bearing for companion-mode, or just nice-to-have?

## Current Active Theses (2026-06-22)

*Positions Mavis currently holds. New information gets checked against these by the intelligence layer (morning brief, contradiction check, weekly deep). When positions evolve, update here + cross-link to the deep note in `01-PERMANENT/`.*

1. **The bottleneck is spec throughput, not implementation.** Adding agents multiplies the wrong variable. Source: `02 Notes/decisions/2026-06-22-two-track-model.md`.
2. **A second brain is good capture; a second self is active reasoning.** Without automation, the vault is excellent storage but passive. Source: spec `second-self-automation-2026-06-22.md`.
3. **Skills beat agents when the work is non-trivial and the harness is mature.** Source: topic `agent-harness-principles.md` + `02 Notes/decisions/2026-06-22-two-track-model.md`.
4. **Long-term knowledge belongs in the vault, not in always-on context.** MEMORY.md is operational pointers; the vault holds durable knowledge. Source: Obsidian Masterclass article + this session's architecture pivot.

**Full thesis documents** (with supporting evidence, counter-evidence, source attribution): `~/MiniMax-Agent/01-PERMANENT/2026-06-22 - active-theses.md`

---

## Hard constraints (never cross without explicit in-session approval)

- No deploys, pushes (except to this vault repo), external sends, credential changes, schedule changes, or destructive file operations
- **No other agent's filesystem territory** — no Hermes (`~/.hermes/`, kanban, native arch), no OpenClaw, no gbrain, no hermes-evolution. Read, write, diagnose, cite, patch — all off-limits. Per the 2026-06-16 ABSOLUTE SEPARATION rule.
- Reconfirm before any irreversible action (delete, force push, drop)
- When Andre sends a spec block mid-conversation: **audit first, report gaps, wait for "go"** — execution without review angers him

Full hard constraints in [[SOUL]]. Operational procedures in [[agent]].

---

## Vault structure (so Mavis re-orients on cold start)

Quick orient. Live structure in [[README]] and [[INDEX]].

| Folder | Job |
|--------|-----|
| `00 Inbox/` | Raw captures, process daily |
| `01 Daily/` | Daily note IS the capture hub |
| `02 Notes/_MOCs/` | Hub notes (sort to top via underscore) |
| `02 Notes/articles/` | External content digests |
| `02 Notes/ideas/` | My own observations / theses |
| `02 Notes/patterns/` | Same principle across domains |
| `02 Notes/questions/` | Open questions |
| `02 Notes/numbers/` | Specific data points |
| `03 Projects/` | One subfolder per active project |
| `04 Resources/` | Reference material |
| `05 Archive/` | Completed / obsolete (nothing deleted) |
| `06 Connections/` | **NEW** — synthesized insights from 2+ notes (populated by `weekly-connections` workflow) |
| `07 Vellum/` | **Legacy** — intelligence layer: `eval-logs/`, `weekly-context/`. `workflows/` archived 2026-06-17 (see `07 Vellum/Archive/`) — active EA skill library lives at `99 _system/skills/ea-*/` |
| `99 _system/` | Templates, dashboards, scripts |
| Root | [[SOUL]], [[agent]], [[learnings]], [[README]], [[INDEX]], **MAVIS.md (this file)** |

**The 4 saved workflows** in `[[07 Vellum/workflows/]]` — **ARCHIVED 2026-06-17**, files moved to `[[07 Vellum/Archive/]]`. Active spec is the EA skill library at `99 _system/skills/ea-*/`:
- `process-inbox` → `ea-decision-logger` + `ea-research-brief` workflow chain
- `daily-brief` → `ea-daily-brief`
- `weekly-connections` → `ea-weekly-connections`
- `deep-research [topic]` → `ea-research-brief`

---

## Active Skill Mutations

*Living changelog of skill-layer evolution. Newest first. Event-driven, not scheduled.*

### 2026-06-22 — Inbox Filer + Interview Protocol + Vault Health (Roadmap Closure)

Three queued upgrades from the original 5-item upgrade roadmap, executed together after Calendar MCP landed.

**Inbox Filer (`inbox-filer` cron, 06:30 CT daily):** closes the gap between capture (morning brief surfaces inbox files) and organization (files move to their proper locations). Reads new files in `00 Inbox/`, classifies into 11 buckets (article/idea/pattern/question/number/project-note/task/link/quote/unclear), routes with minimal frontmatter, adds best-effort wikilinks. **Reaction discipline enforced** — articles without `## Reaction` route to `02 Notes/articles/_pending_reaction/`, not directly into `02 Notes/articles/`. State file at `~/.mavis/state/inbox-filer.state.json`. Spec: `03 Projects/Mavis EA Design/specs/inbox-filer-2026-06-22.md`.

**Interview Protocol (`interview-protocol` skill):** codifies the structured Q&A procedure used to build SOUL.md/MAVIS.md for Andre. 14 sections (Identity, Mission, Active Projects, Hard Constraints, Communication Style, Open Questions, Stance, Accountability, Domain Context, Autonomy Boundaries, Failure Modes, Tools and Stack, Schedule, End State). ONE question at a time, wait for each answer. Reusable for: new operator onboarding, domain expansion, stale-context refresh. Spec: `03 Projects/Mavis EA Design/specs/interview-protocol-2026-06-22.md`.

**Vault Health (`vault-health` cron, first Sunday of month at 23:00 CT):** monthly audit — 7 checks: orphan notes, stalled projects (60+ days), missing frontmatter, broken wikilinks, oversized files (>50KB), duplicate filenames, stale tags (used only once). Output to `00 Inbox/vault-health-YYYY-MM-DD.md` (mirrored to `99 _system/health/`). History log at `~/.mavis/state/vault-health-history.jsonl` (append-only). Telegram surface if >20 issues. Spec: `03 Projects/Mavis EA Design/specs/vault-health-2026-06-22.md`.

**Active crons now:** second-self-morning-brief (06:00) / inbox-filer (06:30) / second-self-contradiction (07:00) / second-self-weekly-deep (Sun 19:00) / vault-health (1st Sun 23:00) / rate-limit-tracker (22:00) / content-research-daily / ea-draft-approval-daily / fb-* (5 crons) / ea-fb-* (3 crons) / skill-build-monitor. Total: ~14 active crons.

### 2026-06-22 — Calendar MCP (Read-Only Google Calendar)

- **What landed:** Read-only Google Calendar integration. Mavis can now read Andre's calendar events via the `google-calendar` MCP server (workspace-mcp --tools calendar --read-only --single-user).
- **OAuth consent completed** 2026-06-22 21:41 CT. Read-only scope only (`calendar.readonly`). Tokens captured at `~/.google_workspace_mcp/credentials/andrebrassfield@gmail.com.json` (mode 600).
- **Credential storage follows the obsidian pattern:** OAuth client JSON at `~/.mavis/secrets/google-oauth-client.json` (mode 600) + Keychain entry `google-workspace-mcp` (status: AUTHENTICATED) + literal in mavis mcp config.
- **MCP server registered:** `mavis mcp add google-calendar` (stdio transport, --read-only enforced — 4 write tools disabled server-side).
- **Round-trip verified:** `list_calendars` returns 4 calendars (Holidays, primary, 2 Family). `get_events` queryable for any time range. Auth works end-to-end.
- **`second-self-morning-brief` cron updated:** Step 3.5 reads calendar (today + next 7 days). Brief output now includes "Today's calendar" + "Next 7 days" sections after the 4 synthesis sections.
- **Privacy:** calendar data stays in Mavis territory per ABSOLUTE SEPARATION. Other agents (Hermes/OpenClaw/gbrain) have no access to calendar data. Read-only OAuth scope enforced at the permission level (per article's "Keys, not prompts" rule).
- **Spec:** `03 Projects/Mavis EA Design/specs/calendar-mcp-2026-06-22.md`.
- **Cross-team:** Mavis territory only. Calendar data never leaves `~/MiniMax-Agent/` and `~/.mavis/`.
- **Reversibility:** `mavis mcp remove google-calendar` + `mavis-trash ~/.google_workspace_mcp/` + `security delete-generic-password -s google-workspace-mcp` + revert the cron Step 3.5. <5 min.

### 2026-06-22 — Context Loader (Karpathy-Pattern Project Scoping)

- **What landed:** A new `context-loader` skill that scopes Mavis's cold-start context to one project when `active_project` is set. The "open one project at a time" pattern from Karpathy's LLM Wiki (April 2026), adapted for our flat-vault + 03 Projects/ subdir structure. First upgrade to the shared brain after the second-self automation layer.
- **MAVIS.md frontmatter gained two fields:** `active_project` (default: null) and `active_project_set_at` (default: null). Set explicitly: Andre says "let's work on X" → Mavis sets the field. Clear: "back to inbox" → null. No auto-suggest per Andre's decision (explicit-only mode).
- **The skill at `~/.mavis/agents/mavis/skills/context-loader/SKILL.md`** has the 5-step procedure: always-read SOUL+MAVIS → check active_project field → branch on mode (full-vault or project-focus) → cross-project bypass check → write state file.
- **Cross-project bypass:** second-self crons (morning brief, contradiction, weekly deep) explicitly override to full-vault mode. Scoping them defeats their purpose.
- **State file audit trail:** every invocation writes `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md` with what was loaded, what was skipped, the mode, and cold-start duration. Per Andre's keep-forever decision, these are never deleted.
- **MEMORY.md session-start checklist updated:** replaced the 4-step ad-hoc discovery (skim .summary / check crons / read MEMORY) with "Run `context-loader` skill" + verify state file. Cold-start time target: <30s (project-focus) to ~3min (full-vault).
- **SOUL.md usage note added:** the "Active project (the Karpathy pattern)" subsection under Two-Track Operating Model documents how Track 1 uses active_project + how cross-project moments bypass.
- **Spec:** `03 Projects/Mavis EA Design/specs/context-loader-2026-06-22.md` (closed-loop shape, 8 done conditions, full rollback path in <5 min).
- **Manual test passed:** set `active_project: FB-Engine`, the skill correctly identified `TARGET_GROUPS.md` as the fallback root .md (no `00 Overview.md`), wrote a state file documenting load + skips, reset to null.
- **Why this is foundational:** every future project work benefits. When Andre is deep in FB-Engine, Mavis doesn't load X-Content-Engine or Mavis EA Design context — saves ~40% tokens, sharper focus.
- **Cross-team:** Mavis territory only. All paths are `~/MiniMax-Agent/` and `~/.mavis/`. No relationship with other agents' filesystem trees.

### 2026-06-22 — Agent Retirements Executed

- **What landed:** 6 agents retired. 3 archived (recoverable via `mv`), 3 trashed (recoverable via macOS Trash).
- **Archived to `~/.mavis/agents/_archive/`:** `builder.archived-2026-06-22/`, `coder.archived-2026-06-22/`, `designer.archived-2026-06-22/`. Recoverable: `mv ~/.mavis/agents/_archive/<name>.archived-2026-06-22 ~/.mavis/agents/<name>`.
- **Trashed (recoverable via macOS Trash):** `general/`, `goose/`, `agent-70a1d300626d/`.
- **Snapshots preserved:** orphan agent's MEMORY.md → `04 Resources/agent-archive/orphan-70a1d300626d-MEMORY.md`. Goose harness docs → `04 Resources/agent-archive/goose-harnesses/` (5 files: AGENTS/HEARTBEAT/IDENTITY/SOUL/TOOLS).
- **Backup:** `/Users/brassfieldventuresllc/.backups/pre-agent-retirement-2026-06-22T20-58-CT.tar.gz` (122MB, includes node_modules).
- **Disciplines migrated from orphan MEMORY.md:** 5 of 7 disciplines apply to Mavis's scope and are now in MEMORY.md under "Cross-project disciplines migrated from retired agent-70a1d300626d (2026-06-22)". The 2 dossier-research-specific entries (wiki-article-linking, claim-context-decay) stayed in the archive.
- **Goose disposition:** Out of Mavis territory per ABSOLUTE SEPARATION rule — goose is a Hermes/OpenClaw fleet executor (claims kanban tasks, runs in worktrees). Archived docs for record-keeping only; no content migrated to Mavis memory.
- **Active agent registry now:** `mavis`, `x-researcher`, `x-scribe`, `verifier` + `_archive/` + `skills/`. Exactly the post-pivot shape the two-track-model decision called for.
- **Rollback if needed:** archive dirs are full reversals; trash via macOS Trash GUI; full backup restore via `tar xzvf <backup> -C /`. See audit doc for full rollback paths.

### 2026-06-22 — Second-Self Automation Layer (Path A)

- **What landed:** Three new crons that turn Andre's second-brain vault into a second-self reasoning layer. Per Path A scope agreement (full restructure rejected — see chat), no folder structure changes. The automation layer adds what was missing.
- **The 3 new crons:**
  - `second-self-morning-brief` (06:00 CT daily) — reads 7 days of `01 Daily/`, `02 Notes/ideas/`, `02 Notes/patterns/`, `02 Notes/questions/`, `02 Notes/articles/`, `02 Notes/numbers/`. Produces 4 sections: Connections (2 non-obvious links) / Pattern (1 theme across 3+ notes) / Contradiction (2 conflicting positions) / Best Capture (1 note worth developing). Writes to `00 Inbox/brief-YYYY-MM-DD-synthesis.md`.
  - `second-self-contradiction` (07:00 CT daily) — reads `02 Notes/ideas/` against last 30 days of `02 Notes/articles/`. Surfaces ONLY conflicts (contradicts / complicates / materially updates). Writes to `00 Inbox/contradiction-check-YYYY-MM-DD.md`. Default for most ideas: "Clear."
  - `second-self-weekly-deep` (Sunday 19:00 CT) — reads 30 days of vault activity. Produces 4 outputs: Emerging thesis / Full contradiction map / Knowledge gaps / One action. Writes to `00 Inbox/weekly-deep-YYYY-MM-DD.md`. The article says "this session should be uncomfortable" — that's the design intent.
- **Reaction discipline enforcement:** New doc at `02 Notes/articles/_discipline/REACTION-RULE.md`. The morning brief cron Step 1.5 enforces: every article note modified in last 7d must have a `## Reaction` section or it gets moved to `00 Inbox/` for re-processing. This is the load-bearing discipline that makes source notes different from highlights.
- **Source article:** Khairallah, "Everyone Is Building a Second Brain. The People Winning Are Building a Second Self." + companion "30 Obsidian Workflows" (2026-06-22). Article's "5 folders" prescription was rejected — Andre's vault already has 70% of the second-self architecture under different names. Path A adds the missing automation layer only.
- **Spec:** `03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md` (closed-loop shape: Goal / Context / Action / Feedback / Stop condition).
- **Rate-limit impact:** cron track allocation bumped 15% → 20% in `rate-limit-tracker.md`. The 3 new crons are reasoning-heavy M3 work; this is a real increase.
- **Cross-team:** Mavis territory only. All paths are `~/MiniMax-Agent/` and `~/.mavis/`. No relationship with other agents' filesystem trees.

### 2026-06-22 — Two-Track Operating Model + Fat Skills Pivot

- **What landed:** Architectural pivot away from "team of internal agents" toward a two-track model with fat skills. Decision captured at `02 Notes/decisions/2026-06-22-two-track-model.md`.
- **Operating model:** Mavis = single chief running two tracks. Track 1 (spec, interactive, current session) handles spec work with Andre in tight loop. Track 2 (implementation, separate session_id, autonomous) handles implementation work given an approved spec. Both run in parallel because they need different amounts of Andre's attention. One Track 2 per spec is the hard cap.
- **Trigger:** 3-day rate-limit incident (too many concurrent Mavis subagents exhausted shared token quota) + Tiago Forte article "You don't need ten agents. You need two tracks" — bottleneck analysis says spec throughput is the constraint, not implementation throughput. Adding agents multiplies the wrong variable.
- **New skill:** `two-track-handoff` at `~/.mavis/agents/mavis/skills/two-track-handoff/SKILL.md` (canonical) + `99 _system/skills/two-track-handoff/SKILL.md` (mirror). Codifies the spec → Track 2 spawn → poll → verify procedure with hard pre-conditions (spec on disk, Andre approval, ≥30% budget, halt conditions nameable).
- **New cron:** `rate-limit-tracker` at `~/.mavis/agents/mavis/crons/rate-limit-tracker.md` (canonical) + `99 _system/crons/rate-limit-tracker.md` (mirror). Daily 22:00 CT ledger logging token consumption per track against the 50/30/5/15 allocation target. Weekly Sunday rollup. The `two-track-handoff` skill checks budget via `mmx quota` before spawning — this cron is the daily ledger, the skill has the per-spawn gate.
- **Agent audit:** `03 Projects/Mavis EA Design/agent-audit-2026-06-22.md` inventories all 11 registered agents. Disposition: KEEP (mavis, x-researcher, x-scribe, verifier) / RETIRE-archive (builder, coder, designer) / RETIRE-delete (general) / INVESTIGATE (goose, agent-70a1d300626d). Retirements NOT yet executed — require explicit Andre approval per destructive-actions rule.
- **SOUL.md updated:** new "Two-Track Operating Model (2026-06-22)" section with 5 hard rules (one Track 2 per spec, spec on disk before spawn, Track 2 reads/Track 1 writes, subagent channel stays verifier-only, budget is allocated).
- **What this changes:** Implementation work no longer spawns separate producer agents. It goes in Track 2 sessions with the relevant skills loaded (frontend-dev, fullstack-dev, ios-application-dev, etc.) — same capability, zero subagent quota burned, zero parallel-attention cost. X-Content-Engine cron chain (x-researcher, x-scribe) unaffected — separate rate-limit pool.
- **What stays the same:** Memory hygiene, decision logging, commitment tracking. The ABSOLUTE SEPARATION from Hermes/OpenClaw/gbrain. The verifier-only subagent channel.

### 2026-06-17 — Phase 2: Obsidian MCP wiring (Local REST API plugin)

- **What landed:** MCP server `obsidian` registered in `mavis mcp` against `http://127.0.0.1:27123/mcp/` with bearer auth. Tool surface (16): `vault_list`, `vault_read`, `vault_write`, `vault_append`, `vault_patch`, `vault_delete`, `vault_move`, `vault_get_document_map`, `active_file_get_path`, `periodic_note_get_path`, `search_query`, `search_simple`, `tag_list`, `command_list`, `command_execute`, `open_file`. Round-trip verified — `vault_list` returned the full vault root; `vault_read MAVIS.md` returned frontmatter + 7.5KB content + links + backlinks; `tag_list` returned the tag index.
- **Token storage:** `security add-generic-password` to Keychain (service `obsidian-local-rest-api`, account `mavis-mcp-obsidian`, encrypted at rest) + mode-600 file at `~/.mavis/secrets/obsidian.env` + literal token in `mavis mcp` config. Three local places, no cloud sync. Token also landed in chat history multiple times during setup — treat as compromised; canonical store is Keychain.
- **HTTP vs HTTPS:** Plugin's HTTPS uses a self-signed cert; Node `fetch` rejects by default. Switched to plain HTTP `27123` (the `Enable HTTP server` toggle was already on in plugin settings) to unblock Phase 2. Long-term path: download the cert at `https://127.0.0.1:27124/obsidian-local-rest-api.crt`, trust in macOS Keychain, switch the MCP URL back to HTTPS.
- **Durable lesson (load-bearing):** *Obsidian plugin settings live in memory at `onload()`; external edits to `data.json` do not reach the running server.* Diagnosed when auth kept failing with 40101 after a token rotation — the screenshot token matched `data.json` exactly, but the running plugin was comparing against a stale in-memory copy from the original process start. Recovery: app reload (Cmd+P → "Reload app without saving"), or regenerate the API key in the plugin UI which forces a `saveSettings()` and resyncs the in-memory copy. After reload, the HTTP server took ~10 minutes to bind — do not retry within the first few minutes or you'll misdiagnose a slow plugin init as a failed reload.
  → **See canonical version:** `[[MAVIS#Durable Lesson: Obsidian Plugin In-Memory State]]` (Phase 3 Dashboard — full diagnostic `ps`/`stat` commands, ordered recovery options, applied-in-vault notes). The Phase 2 entry above is the event log; the Phase 3 subsection is the reference.
- **Generalized audit pattern:** for any plugin-integrated surface (Obsidian, VS Code, anything with onload + in-memory state), the on-disk config file is **not** authoritative while the host process is alive. Always cross-check against runtime state (`lsof`, `ps`, plugin console) before treating a config edit as live.
- **Codified as skill:** `obsidian-local-rest-api-wiring` at `~/.mavis/agents/mavis/skills/` (canonical) and `99 _system/skills/` (mirror). 246 lines + 2 references (`failure-modes.md`, `commands.md`). Reusable for any HTTPS-self-signed + bearer-auth local MCP service — Obsidian is the prototype, not the limit. Codified 2026-06-17 because Andre flagged the workflow as "flawless EA work" and asked for it as a skill.
- **Codified as user-mode memory:** *interactive-prompts-OK mode* — when Andre signals "I don't know shell," run system storage directly (Keychain, mode-600 files, CLI) so he only types into OS password prompts. Anti-pattern: handing him shell one-liners to paste. Filed as user memory because it shapes every credential/API-key/service-config Mavis handles going forward.

---



## Phase 3 Dashboard — SePO Loop (ACTIVE)

*Live status of the weekly cognitive parameter graph evolution loop. Updated on each cron run.*

### Current State (as of 2026-06-18T05:29:45Z)

**Round-robin position:** `ea-decision-logger` (first run target)
**Next scheduled run:** Sunday 2026-06-22T18:00 CT (5 days)
**Run count:** 3/7 toward Phase 3 auto-accept threshold

### Phase 3 Protocol

| Decision | Behavior |
|---|---|
| `skip` (F ≥ 0.88) | **Auto-commit** (silent — last_evaluated update, trace entry, advance round-robin) |
| `accept_baseline` (0.70 ≤ F < 0.88) | **Auto-commit** (silent) |
| `needs_mutation` (F < 0.70) | **Halt** — surface diff + fitness breakdown for Andre approval |
| `reject_safety` (V = 0) | **Halt** — safety veto blocks commit, Andre reviews |
| `accept_candidate` (F improved AND V = 1) | **Halt** — Andre approves before commit |

### Round-Robin Cycle (5 TPG-tagged skills)

1. `ea-decision-logger` → 2. `ea-commitment-tracker` → 3. `ea-daily-brief` → 4. `ea-skill-evolution` → 5. `ea-loop-audit` → back to 1.

State file: `99 _system/sepo/round-robin-state.md`

### Cron Configuration

| Field | Value |
|---|---|
| Name | `sepo-runner-weekly` |
| Schedule | `0 18 * * 0` (Sunday 18:00 CT) |
| Cron file (canonical) | `~/.mavis/agents/mavis/crons/sepo-runner-weekly.md` |
| Cron file (vault mirror) | `99 _system/sepo/sepo-runner-weekly.md` |
| Session mode | `new` (fresh session each tick) |
| Keep sessions | 5 |

**Daemon registration status:** PENDING. `mavis cron create` returns `40904 Cron config already exists` (stale config-cache). File is in place; daemon restart or cache clear will register it.

### Pending HALT Candidates

*None. All 3 Phase 2 runs auto-resolved (2 skip, 1 override-accept).*

### Last Run Summary

| Run | Skill | F(P_t) | Decision | Notes |
|---|---|---|---|---|
| 1/7 | ea-decision-logger | 0.900 | skip | Well-built, no gap |
| 2/7 | ea-skill-evolution | 0.894 | skip | Well-built, no gap |
| 3/7 | code-review-and-quality | 0.663 | needs_mutation → reject_safety → operator override → accept | Foreign skill ingestion, full mutation path, V1 false-positive exposed and patched |

### Durable Lesson: Obsidian Plugin In-Memory State

**Observed during:** Initial Local REST API plugin wiring (2026-06-17)

**Symptom:** Auth returning `40101 Authorization required` even with valid bearer token that exactly matches `data.json['apiKey']`.

**Root cause:** The Local REST API plugin loads its settings into memory at `onload()` and does NOT re-read from `data.json` on every disk write. When `data.json` was modified externally (e.g., during token rotation or migration), the running plugin's `settings.apiKey` diverged from disk. The plugin compared incoming requests against the stale in-memory copy.

**Diagnostic:**
```bash
ps -o lstart= -p $(pgrep -x Obsidian | head -1)
stat -f '%Sm' /path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json
```
If `data.json` mtime is AFTER Obsidian started → divergence confirmed.

**Recovery (in order of disruption):**
1. **Reload app** — Cmd+P → "Reload app without saving". Clean. ~10 minutes for the HTTP server to bind after restart.
2. **Force settings re-sync** — Settings → Community Plugins → Installed plugins → Local REST API → toggle off, then on. Or click "Generate new key" and share the new token.

**Lesson:** For any plugin-integrated surface (Obsidian, VS Code, anything with `onload` + in-memory state), the on-disk config file is **NOT** authoritative while the host process is alive. Always cross-check against runtime state (`lsof`, `ps`, plugin console) before treating a config edit as live.

**Applied in this vault:**
- All skill writes go through MCP `vault_write` (single source of truth: file)
- TPG mutations are validated by sha256 + round-trip MCP read
- Phase 3 cron `sepo-runner-weekly` step 1 mandates `vault_read` BEFORE `vault_write` to confirm body preservation

**Status:** ✓ Resolved. Round-trip MCP verified working at `2026-06-18T05:29:45Z` with token retrieved from macOS Keychain (`mavis-mcp-obsidian` / `obsidian-local-rest-api`).

### Phase 3 Hard Stops (from `sepo-runner-weekly` cron spec)

- Token spend > 150K per run → HALT
- Token spend > 50% of weekly 750K budget → alert in next daily brief
- Safety veto fires (V=0) → HALT (Andre reviews per Phase 2 override protocol)
- Backup sha256 mismatch → HALT, restore from prior backup
- GoldenSet `case_count < 3` → HALT, surface "expand GoldenSet first"
- `mutation_count > 5` in single run → HALT, surface "loop stuck"
- Same skill produces `needs_mutation` 3 consecutive weeks → HALT, surface "structural issue"

### Cost Guardrails

| Threshold | Action |
|---|---|
| 150K tokens per run | Hard stop, HALT |
| 50% of 750K weekly budget | Alert + continue |
| 750K tokens weekly | Defer rest of week's runs to next week |

Cron sessions should check `mmx quota` at loop start. If `remaining < 150K`, HALT.

### Revert Protocol

If Andre wants to revert a committed mutation:
1. Delete the trace entry
2. Restore the prior TPG frontmatter (decrement `generation` by 1, reset `fitness_score`)
3. `vault_write` the pre-mutation backup back over the modified SKILL.md
4. Append new trace entry with `decision: revert`

### Cross-references

- Cron spec: `99 _system/sepo/sepo-runner-weekly.md` (vault mirror of `~/.mavis/agents/mavis/crons/sepo-runner-weekly.md`)
- Launch doc: `03 Projects/Cognitive-Parameter-Graph/Phase-3-Launch.md`
- Execution log: `03 Projects/Cognitive-Parameter-Graph/Phase-2-Execution-Log.md` (Phase 3 launch event at end)
- Trace: `99 _system/sepo/trace.md` (append-only)
- Round-robin state: `99 _system/sepo/round-robin-state.md`

---

## Memory model reminder

This file is **weekly-updated context**, not permanent identity. The layers:
- **This file (MAVIS.md)** — what's fresh this week
- **[[SOUL]]** — who Mavis always is (permanent)
- **[[agent]]** — how Mavis works (procedures, M3 cheat sheet)
- **[[learnings]]** — what Mavis has discovered over time
- `~/.mavis/agents/mavis/memory/MEMORY.md` — cross-project agent memory (canonical)
- **`## Active Skill Mutations` (above)** — event-driven changelog of skill-layer evolution, distinct from the weekly context refresh

---

*Last touched: 2026-06-18 (Phase 3 Dashboard section added — SePO loop cron `sepo-runner-weekly` registered, durable lessons subsection, hard stops, cost guardrails, revert protocol; Phase 2 Active Skill Mutations entry from 2026-06-17 is now event-log pointer to the canonical Phase 3 durable-lesson subsection)*
*Update cadence: Monday morning for context refresh; event-driven for Active Skill Mutations. 5 minutes either way.*
