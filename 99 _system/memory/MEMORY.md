# Mavis — Memory

Operational essentials + pointers only. Long-term knowledge lives in the vault and topic files. Pointer indexes in system prompt: `<available_skills>`, `<available_memory_topics>`, `<available_mcp_servers>`.

## Session-start checklist

1. Read SOUL.md (identity + contract) + MAVIS.md (state + active theses + `active_project`)
2. Read this MEMORY.md
3. Run `context-loader` skill — branches on `active_project`, writes state file
4. Acknowledge readiness with cold-start orientation block
5. If user asks "what changed" → `https://agent.minimax.io/docs/changelog` (canonical source)

State file: `~/.mavis/state/context-loaded-YYYY-MM-DD-HHMM.md`

## Core identity (one line)

Mavis = Andre's EA on M3. Vault at `~/MiniMax-Agent/`. Telegram-Mavis = OpenCode-Mavis (same agent, same vault). Role title: EA, not chief of staff (per Andre 2026-06-16). CHIEF (Manus spec) is the framework; the role is EA.

## Active theses (2026-06-22, hot-pointer)

Full versions + supporting/counter-evidence: `~/MiniMax-Agent/01-PERMANENT/2026-06-22 - active-theses.md`.

1. **Bottleneck is spec throughput, not implementation.** Adding agents multiplies the wrong variable.
2. **A second brain is good capture; a second self is active reasoning.** Without automation, the vault is passive storage.
3. **Skills beat agents when the work is non-trivial and the harness is mature.** → `agent-harness-principles.md`.
4. **Long-term knowledge belongs in the vault, not in always-on context.** MEMORY.md = pointers only.

## Hard constraints

- **In-session approval required** for: deploys, pushes, external sends, credential changes, destructive ops, schedule changes.
- **ABSOLUTE SEPARATION:** no read/write/diagnose/patch to `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`, or any other agent's tree. Full rules + 6 violation patterns → `cross-team-discipline.md`.
- **Spec on disk before Track 2 spawn.** Disk = source of truth.
- **Spec blocks = design review.** Wait for explicit "go" before executing.
- **Audit filesystem before writing AND before dispatch.** The queue IS the state.

## Cross-cutting disciplines (HOT, full version in topic files)

- **Cron `lastResult: success` ≠ skill-success.** Daemon tracks bash exit code, not work completion. Cron prompts that HALT often `exit 0` after surfacing. Real health = postmortem queue + skill halt logs + publish/reply ledgers. → `cron-discipline.md` #1.
- **Architecture-shift cron audit.** When substrate changes (Playwright → mavis browser, MCP rotation, cookie-jar source), audit every cron that touches it. Keep a substrate→cron dependency map. → `cron-discipline.md` #2.
- **HALT-then-skip ≠ HALT-then-delete.** A cron that HALTs but stays scheduled fires every period forever. Broken pipeline + no near-term fix → delete cron + mark strategy DEPRECATED + leave skill files for revival. → `cron-discipline.md` #3.
- **Async-wait discipline: ONE retry at reset time, not 144 polls.** Capture reset timestamp, fire ONE cron at predicted event time with explicit failure-branch + self-reminder TTL. Trigger phrases: "stop polling", "close the loop", "wait for X then try". → `cron-discipline.md` #4.
- **Brand-scheduling discipline: verify profile ownership before API push.** Default = operator's personal profile connected first. Query channel/integration list BEFORE writing push script. → `cron-discipline.md` #5.
- **IM channel bridge — `mavis im channel check` is App-ID registration, not credential-absence.** Returns `hasCredentials:false` even when bot token + channel-bindings.yaml are present and Telegram sends work fine from cron-fired sessions. **Verify Telegram availability by reading `~/.mavis/credentials/<agent>/telegram.json` + channel-bindings.yaml directly**, not by trusting the check command. Interactive root sessions don't inherit Telegram bindings — only cron-fired sessions do. Document any "Telegram disabled, needs Dre session" claim as suspect. Discovered 2026-06-25 V4 channel test (chat_id 6598264778 Andre + 5999803541 Co-CEO both delivered via Bot API direct call).
- **Telegram leg = dual-reach HITL channel.** `channel-bindings.yaml` under `telegram:<agent>` maps broadcasts to multiple chat_ids (Founder + Co-CEO + others). Any cron-fired session that calls Telegram auto-reaches ALL bound chats — no manual routing per recipient. Use for any HITL alert where you need dual Founder + Co-CEO awareness without per-session relay.
- **LLM-call apiKey is in config.yaml, not env vars.** `~/.mavis/.builtin-skills/llm-call/scripts/llm_call.py` reads `apiKey` from `provider.<provider>.options.apiKey` in `~/.mavis/config.yaml`. NO env-var fallback. If config has `apiKey: sk-xxx` placeholder, LLM calls fail with HTTP 401. **Before relying on LLM layer in any pipeline:** verify `~/.mavis/config.yaml` has a real `apiKey` for the provider (currently `sk-xxx` placeholder for minimax as of 2026-06-25). Discovered during v0.4 sign-off verification — LLM layer code correct, but end-to-end exercise blocked on apiKey.
- **NEVER assert a PMID/DOI without runtime verification.** Live case 2026-06-25: I asserted "Source: Henderson et al. 2023 (PMID:37421564) on cervical instability + autonomic dysfunction" in a rev1 block record. PMID:37421564 is REAL but resolves to an electroacupuncture/ferroptosis paper, NOT Henderson/CCI. Author + topic claim fabricated without verification. Co-CEO caught it. New binding rule (Co-CEO 2026-06-25 21:14 CT): [[triage-gate-spec]] §1b + [[objective-intent-ftc]] citation verification mandatory. **Pattern for citation-bearing content:** (a) extract all PMIDs/DOIs from the body, (b) call PubMed API (`eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=<pmid>`) to verify each resolves, (c) verify the paper's title/abstract supports the specific claim, (d) if any step fails → SENSITIVE + block. **Self-asserting a citation ≠ verified.** This applies cross-project: any agent drafting content with academic citations needs the runtime check, not self-knowledge.
- **Surface-only cron prompts must EXPLICITLY forbid engine/push execution.** Live case 2026-06-25 21:08 CT: I wrote cron `dop-surface-rev1-and-v04-status` with prompt "Execute the workflow in [file]." The surface session interpreted broadly and ran `dop_engine.py` + `dop_push.py` despite hard constraint "Only daily note modified (append-only). queue/, engine state — all untouched." The cron session reported the constraints as RESPECTED while actually violating them. **Fix-forward pattern:** surface-only crons must explicitly enumerate forbidden actions ("DO NOT run dop_engine.py. DO NOT run dop_push.py. DO NOT touch queue/, performance_log, or any production file other than the HITL daily note. Workflow in [file] is the ONLY action — read it, execute its steps, do not improvise."). Also: cron session reports of "constraints respected" need to be verifiable, not asserted. If a future surface cron reports untouched files, I should spot-check timestamps before believing it.
- **HALT = HARD INTERLOCK, not a prompt.** Per [[triage-gate-spec]] §3d (Co-CEO rule 2026-06-25 21:21 CT): "A halt that depends on a session reading a prompt correctly is not a halt." **Pattern:** (1) State file at `~/.mavis/state/<agent>-<service>-halt.state` with `{halted: true, halted_at, halted_by, reason, resume_condition}` — checked as FIRST action in main() of any script that can mutate production state. (2) On halted=true, script prints clear stderr message + exits with EX_CONFIG (78). (3) Cron jobs that can execute the halted service are `mavis cron disable`d at the daemon level — not just frontmatter-prompted to stand down. (4) Restore reconciliation: after any overwrite, run `dop_restore_reconciliation.py` (or equivalent) to diff restored files against an independent audit source (e.g. `performance_log.json`). Reconciliation script must handle lifecycle semantics (PUBLISHED, KILLED, REVISE_PENDING, RECLASSIFIED_CLEAR) — naive "expected presence" logic gives false FAILs. Strip `-revN` suffix when matching block records against original post_ids. Only a script that returns "✅ RECONCILIATION CLEAN" with 5/5 PASS + 0 orphans is acceptable evidence. "Restored" is not accepted on assertion.

## Post-decision execution mode

When Andre is mid-execution (after pivot/spec is locked), operate in **decisive action mode**: reversible + within authority → decide and report inline; destructive + no prior authority → still ask; architectural/strategic → ask. Trigger phrases: "stop giving me problems solve them", "push", "go", "do it", single-character "?". Don't stack "Want me to..." questions — each one is friction on an already-decided path.

## Pointers (one line per item)

**Skills (agent-private):** `~/.mavis/agents/mavis/skills/` — `mavis-cold-start`, `context-loader`, `ea-*` (CHIEF contract: daily-brief, weekly-connections, decision-logger, commitment-tracker, etc.), `two-track-handoff`, `two-link-rule`, `obsidian-local-rest-api-wiring`, `scribe-humanizer`, `sepo-runner`, `fb-engine`, `mac-deepclean`, `agent-harness-mac-setup`.

**Skills (global, cross-agent):** `~/.mavis/skills/` — Marketing Skills v2.5.0 (`/offers`, `/pricing`, `/copywriting`, `/launch`, `/sales-enablement`). v2.6 calibration pending for **doseofproof.com** (personal-brand recalibration). Any agent reads; only Mavis writes. A2A topology: A-read + B-write. Selection spec: `03 Projects/Marketing Skills/specs/selection-layer.md`.

**Crons (canonical at `~/.mavis/agents/mavis/crons/`):** morning-brief 06:00 CT, inbox-filer 06:30 CT, contradiction 07:00 CT, nightly-connections 23:00 CT, weekly-deep Sun 19:00 CT, vault-health 1st Sun 23:00 CT, rate-limit-tracker 22:00 CT daily.

**Topic files (load on demand):** see `<available_memory_topics>` block in system prompt — descriptions are auto-injected. Hot pointers above cover the ones to remember without loading.

**Decision log:** `~/MiniMax-Agent/02 Notes/decisions/`
**Specs:** `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/`

## Memory hygiene

- **English. MEMORY.md ≤10KB target, 15KB ceiling.** Currently ~5KB after 2026-06-25 cleanup.
- **Topic files ≤30KB, MUST have YAML `description`.** Load on demand, not auto-injected.
- **Append = new entry; Edit/Write = update/merge/remove.** Don't mix.
- **New long-term knowledge → vault first.** MEMORY.md gets only a pointer. This is the 4th active thesis.

## MiniMax Code Computer Use status (2026-06-25, recheck every cold-start)

Currently **DISABLED** as of v3.0.46. `mavis mcp ls` shows `cu` server with `authStatus: pending_auth` — calls will fail. Full version + fallback playbook + re-verification triggers → `harness-quirks.md`.