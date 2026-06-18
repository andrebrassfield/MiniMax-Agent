---
type: team-config
team: x-content-engine
chief: Mavis (mavis, MiniMax-M3)
workers:
  - x-researcher (registered 2026-06-16 15:48 CT, system-prompt = agents/researcher.md)
  - x-scribe (registered 2026-06-16 15:48 CT, system-prompt = agents/scribe.md)
stage: live-spawn-mode
activated: 2026-06-16 15:40 CT (dry-run) → 15:48 CT (live spawn)
activation-mode: live. Mavis dispatches via `mavis communication send --command spawn --content '{"agent":"x-researcher|xc-scribe","prompt":"<task>"}'`. Workers carry the full system prompt at spawn time via the registered agent's persona + system-prompt.
---

# X-Content-Engine — Team Configuration

## Identity

This is the team-level contract for the X content production pipeline. It defines the handoff protocol, queue lanes, and operational rules for the chief (Mavis) when dispatching the two worker agents.

## Team roster

| Agent | Role | Model | Spawn command |
|-------|------|-------|---------------|
| Mavis (chief) | Orchestrator | M3 | (always-on) |
| x-content-researcher | Viral Format Analyst | M2.7 | `mavis communication send --command spawn --content '{"agent":"x-content-researcher","prompt":"<task>"}'` |
| x-content-scribe | X-Platform Ghostwriter | M2.7 | `mavis communication send --command spawn --content '{"agent":"x-content-scribe","prompt":"<task>"}'` |

Workers do not call each other. The chief routes between them.

## Handoff protocol

### Stage 1: Bookmarks → Researcher

1. Mavis runs the `x-bookmark-parser` skill (already loaded).
2. Skill writes to `00 Inbox/x-bookmarks-YYYY-MM-DD-HHMM.md`.
3. Mavis reads the file's "Recently Consumed" tail at `03 Projects/X-Content-Engine/queue/researcher-inbox.mdl` (the queue lane for researcher tasks).
4. If the file is new and not in the consumed tail, Mavis dispatches `x-content-researcher` with the file path.
5. Researcher writes the brief to `03 Projects/X-Content-Engine/briefs/YYYY-MM-DD-HHMM-brief.md` and appends to `briefs/_ledger.mdl`.
6. Mavis appends the consumed file to `queue/researcher-inbox.mdl` (last 5).

### Stage 2: Brief → Scribe

1. Mavis reads `briefs/_ledger.mdl` for new briefs (not yet in `queue/scribe-inbox.mdl`).
2. Mavis checks if `agents/persona.md` exists. If not, **HALT** the Scribe and surface to Andre.
3. Mavis dispatches `x-content-scribe` with the brief path + persona path.
   - **Indexing convention is explicit in the dispatch prompt** (locked 2026-06-17): when listing source ideas, the prompt MUST state "0-indexed positions in `ideas_backlog`" or "1-indexed positions in `ideas_backlog`" — never omit. Default: 0-indexed (Python-natural). The Scribe HALT s on ambiguous indexing rather than guessing.
4. Scribe writes drafts to `drafts/YYYY-MM-DD-HHMM-draft-NNN.md` and appends to `drafts/_ledger.mdl`.
5. Mavis appends the consumed brief to `queue/scribe-inbox.mdl` (last 5).
6. **Mavis runs `tools/validate-batch.py <batch_file> --strict` (locked 2026-06-17, the script-side char-limit gate).** The script programmatically computes `len(post)` for each draft and compares against the Scribe's self-reported "Character count" line. Exit-code mapping:
   - **0** — clean; proceed to Stage 3.
   - **1** — one or more drafts exceed 280 chars; BLOCK; re-dispatch Scribe with a trim request, or chief takes over per `orchestration-failure-modes.md`.
   - **2** — banned-phrase hit; WARN; surface to Andre; chief decides whether to file or re-draft.
   - **3** — parsing error; Scribe's output is malformed; re-dispatch with a fix request.
   - **4** — Scribe self-report drift; log in the ledger as a Scribe accuracy note; batch still passes the hard limit.
7. Mavis appends the validation result to `drafts/_ledger.mdl` (e.g., "validated by `tools/validate-batch.py` — exit 0, max count 254/280").

### Stage 3: Drafts → user review

1. Mavis files each draft in `00 Inbox/` for Andre to see (or surfaces via Telegram, depending on user preference — TBD).
2. Andre opens the draft, reads the "Why this draft" + "Notes for Andre" sections, and toggles the approval checkbox.
3. Approved drafts: Andre publishes manually on x.com. **No auto-publish.** (The agents never have x.com write access.)
4. Rejected drafts: moved to `drafts/rejected/` with a one-line reason.
5. Revision-needed drafts: Scribe re-runs with the user's notes (rare; usually just rejected + redrafted).

### Stage 4: Publish → analytics feedback cron (the close-the-loop handoff)

This stage is the **feedback loop trigger** — the Sairahul1 Layer 5 piece. It answers: once a draft is published, how does its actual engagement flow back into the brain so the next batch is informed by it?

1. Andre publishes the approved draft manually on x.com and copies the post URL.
2. Andre tells Mavis (via Telegram, direct prompt, or by appending to the ledger himself): "I published {draft_file} draft {N}, URL is {x.com_url}."
3. Mavis appends a one-line entry to `queue/drafts-published.mdl` (per the schema in that file's frontmatter). The line includes: timestamp, draft file path, post URL, pillar, and the corresponding `ideas_backlog` index.
4. Mavis schedules a **one-shot `mavis cron`** for `publish_date + 3-5 days, 9am CT` with a prompt that fires `x-analytics-tracker` in 7-day window mode. The cron name is `xce-feedback-{publish_date}`. The cron deletes itself when complete (one-shot cleanup discipline).
5. Mavis appends to `drafts/_ledger.mdl`: "Mavis scheduled feedback cron for {publish_date} → {trigger_date}."
6. Mavis confirms to Andre: "Logged. Analytics will pull on {trigger_date} at 9am CT."

Full operational spec (the cron template, the prompt body, the verification backstop, the failure modes): `agents/feedback-loop.md`.

**Why this stage exists:** the Scribe's Hard Rule #10 says "Never publish to x.com" — drafts only. The analytics skill needs the post URL to know what to measure. The published ledger + the one-shot cron are the bridge between the Scribe (drafts, never publishes) and the analytics skill (measures, never drafts). Neither agent touches the other; the chief routes.

**Why 3-5 days, not 24h:** X's per-post analytics aggregates over ~24h lag. 3 days gives metrics time to settle; 5 days is the ceiling before the post ages out of "this week's performance" relevance.

## Queue lanes (YAML conventions)

The queue lanes are markdown lists (`.mdl` = markdown ledger) maintained by the chief. Each entry has the form:

```markdown
- YYYY-MM-DD HH:MM CT — <file or task id> — <one-line summary>
```

Each queue file ends with a "Recently Consumed (last 5)" tail. Older entries roll off.

- `queue/researcher-inbox.mdl` — bookmarks the Researcher has consumed
- `queue/scribe-inbox.mdl` — briefs the Scribe has consumed
- `queue/drafts-pending.mdl` — drafts the user hasn't approved yet
- `queue/drafts-published.mdl` — drafts the user approved and published (the **feedback-loop trigger ledger**; consumed by the chief when scheduling the analytics cron per Stage 4)

## Spawn discipline

Per `fleet-trust-patterns.md` §7 (delegation), the chief spawns workers via:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"<worker-name>","model":"MiniMax-M2.7","prompt":"<task with file paths, scope, hard constraints>"}'
```

The chief's prompt to the worker should include:
- The input file path
- The expected output file path
- Hard constraints (no auto-publish, no AI fluff, halt conditions)
- Reference to the agent's full system prompt (in `agents/researcher.md` or `agents/scribe.md`)

## Quality gates (per worker's contract)

Each worker self-verifies before returning to the chief (see "Verification" section in their system prompts). The chief spot-checks:
- File exists, non-zero
- Schema fields present
- No AI fluff (Scribe only) — re-grep before filing
- Ledger updated
- **Scribe char-limit programmatic check (locked 2026-06-17).** Chief runs `tools/validate-batch.py <batch_file> --strict` after every Scribe dispatch. The script's exit code is the authoritative char-limit verdict — see Stage 2 step 6 for the exit-code map. LLMs are unreliable at manual char counting; this is the script-side backstop.

## Failure escalation

| Failure | Detection | Response |
|---------|-----------|----------|
| Worker stalls at same step 2x | per `fleet-trust-patterns.md` §10 | Chief takes over (Mavis does the analysis itself) |
| Worker produces off-voice drafts | Scribe's self-check fails OR chief spot-check | Reject the batch; surface to Andre; do not file in `00 Inbox/` |
| Persona file is missing | Scribe halts on first invocation | Chief surfaces to Andre; team does not start until persona is filled |
| Bookmarks file is empty | Researcher halts | Chief does not dispatch; reports "no bookmarks to analyze" to Andre |
| Brief recommends a format that's all off-voice | Scribe halts on "all formats off-voice" failure | Chief surfaces to Andre; suggests re-seeding bookmarks |

## Operating cadence

TBD by Andre. Plausible defaults:
- **Light:** Mavis runs the parser weekly (Sunday 6pm CT), dispatches Researcher, then Scribe. User reviews drafts the next morning.
- **Medium:** Parser runs Mon/Wed/Fri; Researcher + Scribe each run after the parser. User reviews same-day.
- **Heavy:** Parser daily; Researcher + Scribe daily; user reviews in real-time.

The cadence is set in `cron/jobs.json` (to be created at activation).

## What this team is NOT

- **Not a posting engine.** The Scribe drafts. Andre publishes. There is no auto-publish path. The Scribe agent has zero x.com write capability.
- **Not a research engine for the user's industry.** The Researcher only analyzes what the user has bookmarked. It does not crawl X for new content. New inputs come from new bookmark captures.
- **Not a persona-mimicry tool trained on the user's data.** The Scribe uses the persona file (manual fill) + the brief. There is no fine-tuning, no learned persona.
- **Not a vanity metrics dashboard.** Engagement tracking is the user's job, via x.com's built-in analytics.

## Activation checklist (Andre)

Status as of 2026-06-16 15:48 CT live-spawn activation:

- [x] Fill in `agents/persona.md` with content pillars, voice notes, banned phrases, topics, and 6 voice-example posts — *locked 2026-06-16. Andre pinned 6 examples (the $450 missed-call post, the 19-year-old-with-AI-agent post, the stop-selling-SaaS post, the 30-min-automation weekend post, the roofer-practical-AI thread, the pro-human framing post) plus cadence rules: staccato periods, lead with a punch, follow with unit economics. Scribe has full voice fidelity. Steady-state target is 5-10 examples; 6 is in the healthy range.*
- [ ] Confirm cadence (light / medium / heavy) — *deferred. Default for now: on-demand via Mavis (Andre pings, Mavis runs the team cycle).*
- [x] Wire the **feedback loop** (Stage 4 + `agents/feedback-loop.md`) — *locked 2026-06-17 11:05 CT. The publish ledger (`queue/drafts-published.mdl`), the one-shot analytics cron template, the performance_log ranking step in Researcher + Scribe specs, and the verification backstop are all on disk. Triggered by the first publish event; backstop self-reminder covers the case where Andre forgets to log a publish.*
- [x] Confirm the approval loop — *drafts land at `drafts/001-missed-calls.md` with an unchecked review box per Scribe spec. Andre approves manually, publishes manually.*
- [x] Confirm the chief's spawn call uses M2.7 — *set in the Researcher + Scribe YAML frontmatter; default model routing per ea-contract.md.*
- [x] Review the Researcher + Scribe system prompts — *done as part of activation; the dry-run confirmed the Scribe's voice discipline.*
- [x] Run a manual dry-run — *completed 2026-06-16 15:42 CT. Output: `briefs/brief-001.md` (4-post analysis mapped to Pillar 2) + `drafts/001-missed-calls.md` (3 variants). Andre confirmed Variant B as closest to the pinned voice.*
- [x] Register the agents via `mavis agent` — *done 2026-06-16 15:48 CT. `x-researcher` and `x-scribe` registered with the full system prompts as their `system-prompt` field. Names distinct from the existing general `researcher` / `scribe` workers to avoid collision.*
- [ ] Set up `cron/jobs.json` for the chosen cadence — *blocked on cadence choice. When Andre picks a cadence, Mavis will write `cron/jobs.json` with the appropriate `mavis communication send` payloads.*

**Live spawn mode (active 2026-06-16 15:48 CT):** Mavis dispatches workers via `mavis communication send --command spawn --content '{"agent":"x-researcher","prompt":"<task>"}'`. Workers carry their full system prompt from the registered agent's `system-prompt` field. The dry-run path (Mavis executing the procedures directly) is no longer needed for normal operation — it stays as a fallback for `fleet-trust-patterns.md` §2 (chief takes over when worker stalls).

**Remaining gap (not blocking):** the persona's "Voice examples" block has 3 pinned posts. Steady-state target is 5-10. The Scribe can draft with 3, but voice fidelity improves with each example Andre adds.
