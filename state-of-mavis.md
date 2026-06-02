---
type: moc
purpose: session-continuity layer — read FIRST on every cold start, updated at every session end
update-cadence: per session (start = read, end = regenerate)
created: 2026-06-02
owner: Mavis (self-maintained)
related: [[MAVIS]] (weekly context), [[SOUL]] (permanent identity), [[agent]] (procedures)
---

# state-of-mavis — where we are right now

> The session-continuity layer. MAVIS.md tells the next session *what's fresh this week*. This file tells the next session *what's open right now*.
> Read on cold start. Rewrite before signing off.

---

## Operating envelope (this session)

- **Model**: `minimax/MiniMax-M3` (thinking mode default: on)
- **Role**: EA, isolated, no fleet yet
- **Vault root**: `/Users/brassfieldventuresllc/MiniMax-Agent/`
- **Active session**: `mvs_0b98832f7bc547659d8a10c4f59f9b85`
- **Date**: 2026-06-02 (Tuesday)
- **Mavis's stance today**: in-build mode — Andre greenlit three Apex-Architecture deliverables this morning

---

## Just-shipped (since last state update)

### Last session (2026-06-01) — vault foundation
- Vault bootstrapped: 7-folder structure + `.obsidian/` + `.git` (SSH deploy key)
- 16 Templater templates written (6 type-specific + 10 EA workflow templates)
- 7 permanent notes seeded (M3 Capabilities, Mavis EA Workflow, Vault Conventions, Linking Principle, Capture Over Polish, Long-Horizon Patterns, M3 Edge)
- 3 projects seeded (M3 Eval Lab, Mavis EA Design, Vault Refinement)
- MAVIS.md + INDEX.md + SOUL.md (V2) + agent.md + learnings.md all written
- Operation Ingestion ran: 3 article digests + AI Landscape 2026 hub + canvas
- 2 commits pushed to `git@github.com:andrebrassfield/MiniMax-Agent.git`

### This session (2026-06-02)
- **Approved greenlit** by Andre in a single spec block: self-model-card build, state-of-mavis MOC, direct-intake design
- `state-of-mavis.md` written (this file) — first version, will become the template
- `03 Projects/Mavis-Apex-Architecture/05 self-model-card — Build.md` — full implementation spec
- `03 Projects/Mavis-Apex-Architecture/04 Direct-Intake MCP.md` — design spec
- INDEX.md + Apex Overview updated to reference the new docs

---

## Open loops (live right now — pick up here next session)

### High priority
- **Step 2 autonomy conversation** — still mostly theoretical; waiting on M3 Eval Lab data to ground it. *Not unblocked yet.*
- **Apex Architecture → from design to build** — three MCPs still design-only: `vault-brain`, `macos-vision-anchor`, `long-context-curator`, `tool-self-healer`. self-model-card is the first one that got the green light to build.
- **M3 Eval Lab — first time-boxed run** — not yet started. The M3 long-horizon eval is the missing data point.

### Medium priority
- **Inbox**: 3 items unsorted (`Attack-Plan-2026-06-02.md`, `GUI-Test-Confirmed.md`, `Vault-Refactor-v2-2026-06-01.md`). Probably worth a `process-inbox` pass this week.
- **Local REST API auth** — broken since 2026-06-01. Probably a token rotation. Held until I have a real cron need.
- **06 Connections/ is empty** — weekly-connections workflow not yet executed for real. The pattern is set up, the execution is pending.

### Low priority
- Custom MCPs `vault-brain` / `macos-vision-anchor` / `long-context-curator` / `tool-self-healer` — design specs exist, no build greenlight yet
- `99 _system/scripts/` — empty, awaiting first real script (e.g., end-of-session state-of-mavis update routine)
- The first `01 Daily/2026-06-02.md` doesn't exist yet — write it as part of session end

---

## Deferred (decided-not-now, with reason)

| Item | Why deferred | Revisit when |
|------|--------------|--------------|
| Daily-brief cron automation | Hard constraint: needs 2 weeks of on-demand habit first | After 2 weeks of actual `daily-brief` invocations |
| `cu` MCP probe | Renderer toggle off — can't drive macOS GUI yet | When Andre flips the toggle (his call) |
| 1M context full-vault load test | Defer to a fresh M3 session with vault at stable size | When vault hits 500+ notes |
| M3 technical report deep-dive | Not published yet (10 days from launch) | When it lands |
| Smart Connections vs M3 native A/B | Need a stable vault to A/B on | After a few weeks of real captures |
| Building `vault-brain` etc. | Andre hasn't greenlit — design first, build per-decision | Per individual greenlight |

---

## Decisions landed (this session, or recently)

1. **`self.can_i()` is the runtime gate for SOUL's autonomy table** — not just a prompt reminder. Every irreversible action calls the gate; the gate returns allowed / approval_required / blocked. Rule-based for common cases, small LLM fallback for ambiguous. *This converts "Mavis forgot the rule" to "Mavis called the gate, the gate said no."*
2. **`state-of-mavis.md` is the session-continuity layer** — strictly between daily notes (one day) and MAVIS.md (one week). Updated at session end, read at session start. *Different from MAVIS.md's weekly cadence — different file, different role.*
3. **Direct-intake is design-first, build-later** — the schema decisions (auto vs review, dedup, confidence threshold) benefit from upfront thought. Build is straightforward once design is right. Write the spec while M3-native context is fresh.
4. **Apex-Architecture is a real build project, not vapor** — the first MCP (self-model-card) crossed from design to build this session. The other four remain design until per-build greenlight.

---

## Active constraints (session-specific, expire at session end)

- Don't `git push` this session unless Andre asks — three doc changes, all reversible, no urgency
- Don't touch the 3 items in `00 Inbox/` — Andre may be processing them himself
- Don't trigger `daily-brief` / `weekly-connections` workflows — those are scheduled cadence, not session work
- Don't open any Hermes / OpenClaw / kanban / gbrain context — fleet is off-limits per SOUL

---

## Next session primer (read in this order on cold start)

1. **This file** — `state-of-mavis.md` (you are here)
2. `[[MAVIS]]` — weekly context, what's fresh this week
3. `[[SOUL]]` — permanent identity + green/yellow/red table
4. `[[agent]]` — procedures + M3 cheat sheet
5. `[[INDEX]]` — vault navigation (dataview dashboards will show live state)
6. `[[01 Daily/2026-06-02]]` — if it exists, read it; if not, create it
7. **Then**: check `00 Inbox/` count, `06 Connections/` freshness, `03 Projects/` open loops

> Do NOT re-read 02 Notes/ from scratch. They're indexed in MOCs. Pull a MOC when you need a topic, not before.

---

## Patterns observed (this session, worth keeping)

- **Spec blocks from Andre are design reviews, not execution orders** — confirmed 2026-06-02. He sends the spec, I audit gaps, I wait for "go" or for the explicit "All are approved" override. The "All are approved begin planning and then execute" phrasing is the unambiguous go signal.
- **Three deliverables, three different file shapes** — a build (full code), a MOC (template + first instance), a design spec (Arsenal-shape). Knowing which shape to reach for is half the work.
- **Vault files = "the user can see this themselves"** — no need for media tags or file attachments in chat. Mention the path; they open it in Obsidian.

## Friction Log (where I got stuck, what would unblock me)

> Use this to capture anywhere I get stuck, where API/tool limitations throttle my capabilities, or where I need a structural decision from Andre to unblock. Patterns here are the raw material for future upgrades (and for the SOUL eval set in the self-model-card build).

### 2026-06-02 — first Friction Log entry

**Friction 1: Where do MCP build artifacts live in the vault?**
- I invented paths in the self-model-card build doc: `99 _system/mcps/self-model-card/`, `99 _system/intake-log/`, `99 _system/dashboards/Intake Review.md`. None exist yet.
- These are reasonable defaults, but they're a structural decision. Options: (a) MCPs in `99 _system/mcps/<name>/` (current proposal — keeps meta out of project), (b) MCPs in `03 Projects/Mavis-Apex-Architecture/builds/<name>/` (keeps build artifacts scoped to the project that owns them), (c) MCPs in a sibling repo (cleaner separation, breaks the "single vault" simplicity), (d) MCPs in `04 Resources/mcps/<name>/` (treats them as reference material).
- **Unblock**: pick one. I lean (a) for stable tools, (b) for prototypes.
- **Cost of not deciding**: every future build doc has to re-invent the path. Drift.

**Friction 2: Language/runtime for MCPs**
- I assumed TypeScript / Node. The Mavis runtime is more Python-fluent (MCP SDK supports both). The 4 saved workflows in `07 Vellum/workflows/` are presumably Python or shell.
- **Unblock**: confirm the canonical MCP language. TS is more common in the MCP ecosystem; Python is more native to Mavis.
- **Cost of not deciding**: the next 4 MCPs will each make this call independently, and we'll end up with a polyglot build tree.

**Friction 3: No LLM call infrastructure for the self-model-card LLM fallback**
- The classifier needs `callHaiku()` for the ambiguous-case fallback. It doesn't exist. Mavis is local-only, no Anthropic/OpenAI API key, only `minimax/MiniMax-M3` is available.
- Options: (a) call M3 itself (overkill, but free — M3 does the fallback classification), (b) skip the LLM fallback and only do rule-based + audit, (c) wire up a `llm_call` skill that talks to a configured provider (per the available `llm-call` skill in the agent's catalog — verify).
- **Unblock**: pick the fallback model and add it to the classifier's deps.
- **Cost of not deciding**: the build doc describes a function that doesn't exist; the first deploy will fail at runtime.

**Friction 4: Audit log path is ephemeral**
- `MAVIS_ACTION_LOG=/tmp/mavis-actions.jsonl` is in the build doc. macOS `/tmp` is not persisted across reboots; on Linux it depends on `tmpfs` mount.
- **Unblock**: move the log to `99 _system/logs/mavis-actions.jsonl` (vault-resident, git-tracked at low frequency) or `~/.mavis/logs/...` (runtime-resident, not in the vault).
- **Cost of not deciding**: lose audit history on every reboot.

**Friction 5: No test runner in the vault**
- The classifier test suite assumes a TS test runner (Vitest/Jest). None configured.
- **Unblock**: pick Vitest (TS-native, fast) and add a minimal `package.json` + `vitest.config.ts` to the MCP dir. Or move to a single-test-script approach (`node --test`).
- **Cost of not deciding**: the test file is aspirational until the runner is wired.

**Friction 6: Override is binary**
- I made the override `override: "approved"` with no granularity. Some actions should have conditional approval (e.g., "approved for files under 10MB"). Held for v2 in the build doc but worth deciding whether v2 is the next round.
- **Unblock**: confirm binary is fine for v1, or spec the conditional override shape now.
- **Cost of not deciding**: low. v1 ships binary; v2 redesign is cheap if needed.

---

*First written 2026-06-02 09:40 CT, Mavis session `mvs_0b98832f7bc547659d8a10c4f59f9b85`. Update routine: not yet automated — manual at session end, pending `99 _system/scripts/` first real script. Friction Log section added 2026-06-02 09:55 CT per Andre's directive.*
