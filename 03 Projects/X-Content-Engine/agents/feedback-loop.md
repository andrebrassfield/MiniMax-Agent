---
type: feedback-loop-spec
created: 2026-06-17
owner: Mavis (chief)
supersedes: (none — adds Layer 5 trigger to the existing pipeline)
depends_on:
  - x-analytics-tracker (skill) — does the actual extraction + brain write
  - content_brain.json (memory) — receives the performance_log append
  - queue/drafts-published.mdl — the publish event ledger
  - agents/researcher.md + agents/scribe.md — consume the performance_log
---

# X-Content-Engine — Feedback Loop (Layer 5 Trigger)

## What this document is

The Sairahul1-style "feedback loop that closes the content machine" — the piece the X-Content-Engine was missing. It answers: **once Andre publishes a draft, how do the post's actual engagement numbers flow back into the brain and influence the next batch?**

The analytics skill (`x-analytics-tracker`) already does the read-side work: it opens Chrome, pulls metrics, writes to the human dashboard + `content_brain.performance_log`. What was missing is the **trigger**: no one was telling the skill *when* to run, or which post URL to track.

This spec adds the trigger, the publish-tracking data structure, and the rank-by-performance changes in the Researcher + Scribe specs.

## What the loop looks like (the closed system)

```
[x-scribe drafts N posts]
        ↓
[Andre approves in drafts/]
        ↓
[Andre publishes manually on x.com]
        ↓
[Andre (or Mavis) logs the publish event to queue/drafts-published.mdl]
        ↓
[Chief schedules a one-shot mavis cron for publish_date + 3-5 days]
        ↓
[At trigger time, Mavis session starts with the cron prompt]
        ↓
[Mavis fires `x-analytics-tracker` in 7-day window mode]
        ↓
[Skill writes to 99 _system/dashboards/x-metrics-dashboard.md (human)]
        ↓
[Skill writes to content_brain.performance_log (machine, atomic)]
        ↓
[Next x-researcher run ranks ideas_backlog by past views/likes]
        ↓
[Next x-scribe run picks the highest-rank pending idea for the pillar]
        ↓
[Better draft, because the data said so]
        ↓
[Loop]
```

## The 4 moving parts

### 1. `queue/drafts-published.mdl` — the publish event ledger

The single source of truth for "which drafts have been published, and what was the post URL." Append-only. One line per publish event. Schema per the file's frontmatter.

**How it gets written:**
- Andre publishes a draft on x.com, copies the post URL
- Andre tells Mavis (via Telegram / direct prompt / during a session): "I published draft 2 of the v2 batch, URL is https://x.com/DreTheSalesGuy/status/1234"
- Mavis appends the line to `queue/drafts-published.mdl`
- OR: Andre appends the line himself (the file is human-readable markdown, no permission needed)

**Why a separate file instead of a field in the draft:** drafts are append-only and version-pinned (a draft approved yesterday shouldn't be edited today). The publish event is a downstream fact about a draft, not part of the draft itself. Splitting them keeps the audit clean.

### 2. The one-shot cron — the trigger

**Pattern:** at publish time, the chief schedules a `mavis cron` for `publish_date + 3-5 days` with a prompt that says: "fire x-analytics-tracker in 7-day window mode, then delete this cron."

**Why one-shot (not recurring):** per `cron-prompt-as-skill` pattern (memory 2026-06-16). Recurring daily crons would fire on every Andre-active session, and the skill needs Chrome + X login. A one-shot tied to a specific publish event is the right shape.

**Why 3-5 days, not 24h:** X's per-post analytics aggregates over ~24h lag. 3 days gives the metrics time to settle; 5 days is the ceiling before the post starts aging out of "this week's performance" relevance.

**The cron creation step (the new Stage 4):**

```bash
PUBLISH_DATE="2026-06-17"          # from drafts-published.mdl
TRIGGER_DATE="2026-06-20"          # +3 days
TRIGGER_TIME="09:00"               # 9am CT — when Andre is at the Mac
TIMEZONE="America/Chicago"

PROMPT='You are the feedback-loop closer for X-Content-Engine.

YOUR TASK:
1. Read `03 Projects/X-Content-Engine/queue/drafts-published.mdl` and identify any post URLs published in the last 7 days that do not yet have a `performance_log` entry in `03 Projects/X-Content-Engine/memory/content_brain.json`.
2. Fire the `x-analytics-tracker` skill in 7-day window mode (the default).
3. The skill handles the dashboard write + the brain `performance_log` append atomically. Do NOT bypass the skill.
4. After the skill completes, verify: `cat content_brain.json | python3 -m json.tool` exits 0, and the `performance_log` array grew by the expected delta.
5. Append a one-line entry to `03 Projects/X-Content-Engine/drafts/_ledger.mdl` summarizing the run: "YYYY-MM-DD HH:MM CT — feedback loop run: N posts closed, performance_log now M entries."
6. If `queue/drafts-published.mdl` is empty (no drafts published since the last feedback run), report "no new publishes to close" and exit without firing the skill.

HARD CONSTRAINTS:
- Do not run if `mavis browser status` shows `not connected` — halt and ask Andre to load the Chrome extension.
- Do not invent post URLs. The published ledger is the only source of truth.
- Do not run the skill more than once per cron invocation.
- The `x-analytics-tracker` skill has its own hard rules about `unclear` cells — honor them. Do not hallucinate metrics.

WHEN DONE:
- Delete this cron: `mavis cron delete mavis xce-feedback-{publish_date}` (the cron is one-shot; cleanup is part of the contract).
- Report a one-paragraph summary to Andre: how many posts closed, top performer, any halts.

---
[self-reminder TTL] This reminder expires at {trigger_date + 7d} (America/Chicago, UTC-5).
If `Date.now() > {epoch_ms}`, your first action MUST be to delete this reminder and exit silently:
`mavis cron delete mavis xce-feedback-{publish_date}`

[gate-discipline] If the published ledger is empty, wrap a one-line status in `<mavis-progress>xce-feedback: nothing to close</mavis-progress>` and exit. Do not send IMs and do not write plain replies on no-op ticks.'

mavis cron create mavis "xce-feedback-${PUBLISH_DATE}" \
  --schedule "0 9 ${TRIGGER_DATE_DD} ${TRIGGER_DATE_MM} *" \
  --timezone "${TIMEZONE}" \
  --prompt "${PROMPT}" \
  --session-mode new \
  --no-report-root
```

**The cron name convention:** `xce-feedback-YYYY-MM-DD` (one per publish date). If Andre publishes 3 drafts in one day, that's 3 ledger entries + 1 cron. If Andre publishes 3 drafts across 3 days, that's 3 ledger entries + 3 crons. The chief dedupes on the date.

### 3. The performance_log ranking — the consumer change

The Researcher + Scribe specs already mention `performance_log` in passing ("the next run can rank by `views`"). This spec promotes that from a note to a **load-bearing step**.

**The ranking rule (new, applies to both Researcher and Scribe):**

When filtering `ideas_backlog` for `status: "pending"` and ranking by priority, add a fourth criterion (after pillar coverage, hook `times_used`, pain `frequency`):

4. **Prior performance of the same hook family.** If any idea in `ideas_backlog` has a `hook` that shares ≥60% token overlap with a hook that appears in `performance_log` with high `views`, give that idea a +1 priority boost. Conversely, if the hook family is in `performance_log` with very low `views`, give it a -1 demotion.

The implementation is a simple `set(tokenize(hook)) & set(tokenize(perf_hook))` Jaccard-like overlap, then a threshold check.

**Why this matters:** the loop is the whole point. Without the ranking, the performance_log is decorative — it gets written but never read. With the ranking, the system compounds: every feedback run makes the next Researcher's 10 ideas slightly better than the last 10 ideas.

**What the Scribe does with it:** the Scribe's Step 2 ranking (already filters pending + ranks by pillar / hook / pain) gets the same +1/-1 boost. So a Pillar 2 idea whose hook family performed well in the last 7 days gets a small bias in the next Scribe run.

**What the Researcher does with it:** the Researcher's idea-generation step (Step 6, "generate 10 new ideas combining hook × format × pain × pillar") should be aware of which hook families are saturated. If a hook family is at high `views` (working) AND already has 3+ ideas in `ideas_backlog`, the Researcher can de-prioritize that family for the next run, in favor of new hook patterns. This is the "test the pillars, don't just lean on what worked" principle in the Scribe spec, applied at the hook level.

### 4. The verification cron (self-reminder) — the backstop

For the next 7 days (until the first publish event creates a real cron), the chief runs a **self-reminder cron** that prompts: "check if any drafts have been published in the last week. If yes, fire x-analytics-tracker. If no, just acknowledge and exit."

This is the backstop. It catches the case where Andre publishes a draft and forgets to log the URL — the next self-reminder tick will find the post in @DreTheSalesGuy's analytics dashboard (even if the published ledger is empty) and the chief can reconstruct the URL → draft mapping by reverse-lookup in `drafts/`.

**Once a real publish event creates a publish-tied cron, the backstop can be disabled or downgraded to weekly.** But for the first 7 days, the backstop is the verification mechanism for this spec.

## What the chief does on first publish event

1. Andre publishes a draft manually on x.com. He pastes the post URL to Mavis.
2. Mavis:
   - Appends to `queue/drafts-published.mdl` (one line, per the schema).
   - Creates the one-shot cron for `publish_date + 3-5 days, 9am CT` per the template above.
   - Appends to `drafts/_ledger.mdl`: "Mavis scheduled feedback cron for {publish_date} → {trigger_date}."
3. Mavis confirms to Andre: "Logged. Analytics will pull on {trigger_date} at 9am CT. You'll see the dashboard update and the brain will rank by what landed."

## What the chief does on cron trigger

1. Cron fires at trigger time. New Mavis session starts.
2. Mavis reads `queue/drafts-published.mdl` (or no posts — gate-discipline says wrap in `<mavis-progress>` and exit).
3. Mavis fires `x-analytics-tracker` per the skill's spec.
4. Skill writes dashboard + brain. Brain delta = N new `performance_log` entries.
5. Mavis appends to `drafts/_ledger.mdl` with the run summary.
6. Mavis deletes the cron (cleanup is part of the contract).
7. Mavis reports to Andre: "Feedback run complete. {N} posts closed. Top: {hook} at {views} views. Brain: {old_count} → {new_count} performance_log entries."

## What the Researcher does on next run (post-feedback)

1. Researcher reads brain. Sees the new `performance_log` entries.
2. In Step 2 ranking, the new criterion applies: hooks that share token overlap with high-`views` posts in `performance_log` get a +1 boost. Low-`views` hooks get a -1.
3. Researcher generates the 10 new ideas, biased by the new signal.
4. Brief file's "Notes for the chief" section surfaces: "Brain delta: performance_log now has {N} entries. Top-performing hook family: {hook_text_excerpt} at {views} views. Next 10 ideas biased toward this family."

## What the Scribe does on next run (post-feedback)

1. Scribe reads brain. Sees the new `performance_log` entries.
2. In Step 2 ranking, the same +1/-1 criterion applies.
3. Scribe's top 3 are biased toward hook families that have performed well for @DreTheSalesGuy.
4. Draft file's "Notes for Andre" section surfaces: "Picks informed by performance_log: hook family '{hook_text_excerpt}' has averaged {avg_views} views over the last 7 days, weighted into the top 3."

## What this loop is NOT

- **Not real-time.** X analytics lag ~24h; the cron fires 3-5 days post-publish. The loop is weekly cadence, not per-minute.
- **Not auto-publish.** The loop is feedback, not publishing. Andre still publishes manually (per Scribe's Hard Rule #10).
- **Not retroactive.** If Andre forgets to log a publish, the published ledger is empty, and the cron fires but has nothing to do. The backstop self-reminder is the catch-all.
- **Not a content recommender.** The loop ranks ideas by hook family performance; it does not tell Andre what to write. The Researcher + Scribe still produce the actual drafts, with Andre as the editor in chief.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Andre publishes but forgets to log URL | `queue/drafts-published.mdl` empty on cron trigger | Cron exits via gate-discipline. Backstop self-reminder catches the next week. |
| x-analytics-tracker halts on UI / login / rate limit | Skill's halt conditions trip | Cron prompt: halt and surface to Andre. The cron does not auto-retry. |
| Brain write fails (atomic rename) | `os.replace` raises | Skill halts. Dashboard may have been written; brain may not. Cron surfaces the mismatch. |
| Multiple drafts published in one day | Multiple `drafts-published.mdl` entries with same date | One cron for the day (chief dedupes on date). Skill pulls all posts in the 7-day window, which includes all of them. |
| Andre publishes the same draft to multiple platforms (e.g., x.com + LinkedIn) | Same draft_file_path in published ledger, different post URLs | Add separate lines per platform. The skill is x.com-only; LinkedIn metrics would need a separate skill. |

## Cross-references

- `x-analytics-tracker` skill — does the read-side work
- `agents/researcher.md` Step 2 — receives the new ranking criterion
- `agents/scribe.md` Step 2 — receives the new ranking criterion
- `agents/team-config.md` Stage 4 — the publish-tracking handoff
- `queue/drafts-published.mdl` — the publish event ledger
- `03 Projects/X-Content-Engine/memory/content_brain.json` — the brain, which receives the `performance_log` append
- `99 _system/dashboards/x-metrics-dashboard.md` — the human-readable output
- `cron/jobs.json` — the declarative spec for all X-Content-Engine crons (one-shot feedback, backstop self-reminder)
- Garry Tan's "evals and integration tests, repeat" — the feedback loop IS the eval. Each run is a system-wide test of "did the brain learn from what worked?"

## Changelog

- 2026-06-17 11:05 CT — initial spec. Sourced from the Sairahul1 thread that inspired the loop; adapted to the existing X-Content-Engine architecture (persona as source of truth, append-only ledgers, atomic brain writes, cron-as-trigger pattern).
- 2026-06-17 13:10 CT — added `publish-path` failure modes below. The cron-driven auto-publish attempt (`post-1-v2-2026-06-16`) halted on duplication: the mavis browser `type` tool duplicated every typed character into the X.com React-controlled inline compose, so the `$876K` / `9.5x` / `Build the damn thing` markers each appeared 2x in the textarea. Per the cron-prompt's mandatory duplication-detection rule, the post was NOT clicked. See `publish-path` section below for the discovered failure surface and recovery options.
- 2026-06-17 18:55 CT — **publish-path resolved.** Playwright MCP `browser_type` (which uses `page.fill()` internally) bypasses the keyboard-event-chain duplication. P4 R3-D3 post shipped cleanly via this path (`status 2067394237851636104`). Recovery Options A-D in the `publish-path` section tagged `[SUPERSEDED]` in favor of new canonical Option E. The cron-prompt template update is locked in (no longer "proposed"). The `x-publish` skill (`~/.mavis/agents/mavis/skills/x-publish/SKILL.md`) is the operational form. `tool-quirks.md` now carries the cross-cutting note: the mavis browser `type` doubling bug affects ANY React-controlled contenteditable, not just X.com. Publish pipeline is closed.

## `publish-path` — the auto-publish sub-loop (cron-driven, not Scribe-driven)

**Added 2026-06-17 13:10 CT after the v2 batch publish attempt halted on duplication.**

This section is separate from the analytics feedback loop above. It documents the **publish path** — the cron-driven Mavis session that posts Andre's approved draft to x.com. The Scribe agent's Hard Rule #10 ("Never publish to x.com") still binds the Scribe itself. The cron session is a Mavis-side workflow, not a Scribe override.

### What was tried (the v2 attempt + the P4 R3-D3 successful attempt)

**v2 attempt — 2026-06-17 13:10 CT — FAILED on duplication.** The cron `post-1-v2-2026-06-16` fired. The procedure:

1. Verified source file + dashboard for duplicates (PASS)
2. Set clipboard via osascript (PASS — verified with `osascript -e 'the clipboard'`)
3. Opened https://x.com/home (PASS — tabId 1230105288, signed in as @DreTheSalesGuy)
4. Clicked `[data-testid="tweetTextarea_0"]` to focus the inline compose (PASS — click returned success)
5. **First paste attempt:** `press_key {key: "v", modifiers: ["Meta"]}` with clipboard set → text query returned **empty** (FAIL — clipboard paste didn't take)
6. **Second paste attempt:** clicked again, then `press_key` with the selector targeting the textarea → text query returned **empty** (FAIL — same)
7. **Type fallback:** `type` with `text: "test"` → text query returned **"testtest"** (FAIL — type tool duplicates 2x in the React-controlled compose)
8. **Type with full post:** `type` with full post text → text query returned the post text **twice** with leftover "test"s sandwiched. `$876K` count: 2. `9.5x` count: 2. `Build the damn thing` count: 2. Length 330 chars (expected 174).

**HALT triggered** per the cron-prompt's mandatory duplication-detection rule. Post was NOT clicked. Tab was navigated to /DreTheSalesGuy to clear the compose. Cron was NOT deleted. Brain was NOT updated. Source file was NOT annotated.

**P4 R3-D3 attempt — 2026-06-17 18:48 CT — SUCCEEDED via Playwright MCP.** Andre requested the post in-session. Procedure (per the new `x-publish` skill):

1. Mavis opened https://x.com/compose/post in **Playwright MCP** (not the mavis browser bridge).
2. Snapshot returned the compose dialog with `textbox "Post text" [active] [ref=e88]`.
3. `mavis mcp call playwright browser_type '{"element":"Post text textbox","ref":"e88","text":"<verbatim 233-char P4 post>","submit":false}'` — text lands **exactly once**, no duplication.
4. Verified via `browser_evaluate` on `[data-testid=tweetTextarea_0]`: returned the 233-char post text, byte-identical to the Scribe's `**Post:**` line, count = 233.
5. Screenshot saved to `~/.mavis/tmp/mcp-images/` for audit.
6. Halted for Andre's "ship it" → Andre approved → `browser_click` on Post button (ref e174) → modal closed, page navigated to x.com/home.
7. Captured post URL via `browser_evaluate`: `https://x.com/DreTheSalesGuy/status/2067394237851636104`.
8. Appended to `queue/drafts-published.mdl`, scheduled one-shot cron `xce-feedback-2026-06-17` for 2026-06-20 09:00 CT.

**Why the Playwright MCP succeeds where the mavis browser bridge fails:** Playwright's `browser_type` is implemented via `page.fill()`, which sets the input/textarea `value` property directly through the DOM — no keyboard event chain, no `input` event dispatch, no React onChange race. The mavis browser bridge's `type` dispatches synthetic keyboard events that React's onChange picks up as two state updates per character. Same target, completely different transport. `page.fill()` is the bypass.

### Discovered failure surface

| Step | Tool | Verdict | Why |
|------|------|---------|-----|
| Click into `[data-testid="tweetTextarea_0"]` | `click` | Works | Returns success, but the textarea does not visibly receive focus in the snapshot |
| `press_key Cmd+V` to paste | `press_key` | **Broken** | Empty result. X's paste event handler requires user activation that the IPC bridge doesn't provide |
| `type "test"` | `type` | **Duplicates 2x** | Every character typed appears twice in the textarea value. The "text" attribute query reads back "testtest" for a "test" input |
| `type` with full post | `type` | **Duplicates 2x** | The full post text appears twice in the textarea |
| `press_key Backspace` / `press_key Delete` | `press_key` | **Broken (cannot delete)** | Backspace and Delete on the React-controlled contenteditable append the prior typed text instead of deleting. Even Ctrl+A → Delete leaves the text in place and adds one char. So the "delete the duplicate" workaround is also blocked. |
| `press_key` with selector target | `press_key` | **Broken** | Same as above — paste event still not received |
| `query text` on textarea | `query` | Reads the duplicated state correctly | Good — this is the duplication detector |
| `mavis mcp call playwright browser_type` (with `page.fill()` under the hood) | Playwright MCP | **Works** | Sets DOM value directly. No keyboard event chain, no duplication. Verified on the P4 R3-D3 post 2026-06-17 18:48 CT. |
| `mavis mcp call playwright browser_evaluate` to verify textarea contents | Playwright MCP | **Works** | Returns the actual rendered text for byte-identical comparison |

### Root-cause hypothesis (as of 2026-06-17 13:15 CT)

The X.com inline compose is a React-controlled contenteditable. Two failure modes:

1. **The `type` tool** dispatches `input` events that React's onChange handler picks up, but for some reason the dispatched events trigger TWO state updates per character. Could be: (a) the IPC bridge is firing the event twice, (b) React StrictMode is double-firing, or (c) the contenteditable mirrors its value in two places (input value + rendered text) and the query reads both.
2. **The `press_key` with Cmd+V** dispatches a `keydown` event for `v` with the `Meta` modifier, but X's paste handler gates on `clipboardData` being populated via a real user gesture, not an IPC-bridged keypress. The IPC layer's keypress doesn't carry a trusted-paste flag.

### Recovery options

| Option | What it requires | Risk | Status |
|--------|------------------|------|--------|
| **A. Clear the textarea, then `type` in N=10 char chunks with `wait` between chunks** | Possibly the duplication is timing-related (React debounce doesn't see one of the two updates if the next chunk arrives before debounce). Worth one attempt. | May still duplicate. | **[SUPERSEDED 2026-06-17 18:55 CT]** — Option E supersedes. Do not attempt. The duplication is not a timing issue; it's an event-chain issue. Chunking doesn't help. |
| **B. Use the AppleScript clipboard → direct Chrome paste via `mavis browser` IPC, NOT press_key** | Need a tool that can dispatch a `paste` event with `clipboardData` populated. Possibly `evaluate` (not in current tool list). | If no such tool exists, this option is blocked. | **[SUPERSEDED 2026-06-17 18:55 CT]** — Option E supersedes. No `evaluate` exists in the mavis browser tool set, and even if it did, it would still go through the same IPC-bridge transport. Use Playwright MCP. |
| **C. Use the cu (Computer Use) MCP** | A real mouse/keyboard action on the actual Chrome window. The cu server has `desktop_type`, `desktop_key`, `desktop_clipboard_write`. The clipboard write goes through OS-level, then `desktop_key "v" with "Meta"` is a real user gesture. | Requires the cu toggle to be enabled in renderer. Per `tooling-gotchas.md`, cu is per-session toggled off. | **[SUPERSEDED 2026-06-17 18:55 CT]** — Option E supersedes. cu MCP is a per-session toggle that may be off; Option E works without a renderer toggle. |
| **D. Andre posts manually.** The cron is just a headless publisher. If the headless path is broken, the fallback is the human. | Zero automation. | Loses the "scheduled autonomous" property of the cron-prompt-as-skill pattern. | **[SUPERSEDED 2026-06-17 18:55 CT]** — Option E keeps the headless property. The human-in-the-loop is now only the editorial approval (which is a Mavis-session conversation, not a manual browser interaction). |
| **E. Use the Playwright MCP `browser_type` (canonical path).** | The Playwright MCP must be reachable (`mavis mcp call playwright ...` works). | If the Playwright MCP is not available, fall back to Option D (manual). | **CANONICAL as of 2026-06-17 18:55 CT** — verified on the P4 R3-D3 post. Encoded in the `x-publish` skill (`~/.mavis/agents/mavis/skills/x-publish/SKILL.md`). Also logged to `tool-quirks.md` for any future React-controlled contenteditable automation (Notion, Linear, Substack, etc.). |

**Recommended next step:** **Option E (Playwright MCP `browser_type`).** This is the only path that satisfies the cron-prompt-as-skill discipline (autonomous publish, no renderer toggle dependency, no human browser interaction). The `x-publish` skill is the operational form.

### Update to the cron-prompt template (locked in)

The cron-prompt template now uses the Playwright MCP path, not the mavis browser bridge. The duplication-detection HALT branch is preserved as a belt-and-suspenders check (in case Playwright's behavior ever regresses), but the primary mechanism is `page.fill()`.

The new cron-prompt (the "publish" half of the loop) should:
1. Open https://x.com/compose/post in the Playwright MCP, not the mavis browser bridge.
2. Snapshot to find the `textbox "Post text"` ref.
3. `browser_type` with the verbatim post text, `submit:false` (always).
4. `browser_evaluate` on `[data-testid=tweetTextarea_0]` to verify byte-identical content + char count. If duplicated or wrong, HALT (the duplication-detector still earns its keep as a guard against upstream regression).
5. Screenshot for audit trail.
6. Halt for human approval — do NOT click Post autonomously.
7. On approval, `browser_click` the Post button, wait 2s, capture URL via `browser_evaluate` on the just-posted article in the home timeline.
8. Append to `queue/drafts-published.mdl`, schedule `xce-feedback-{publish_date}` cron, append summary to `drafts/_ledger.mdl`.

**The duplication-detection rule is no longer the primary failure mode** — it's a regression guard. The P4 R3-D3 attempt on 2026-06-17 18:48 CT did not duplicate, and the post went live cleanly. The rule stays in the prompt as documentation, not as the active HALT trigger.

This is the feedback-loop improvement in action: the cron-prompt template evolved from "HALT on duplication" (v2 attempt, broken) to "use Playwright MCP, verify via `browser_evaluate`, HALT only if `page.fill()` ever regresses" (current). The publish pipeline is now closed.

---

## Changelog (additive)

- 2026-06-17 18:55 CT — **Playwright MCP `browser_type` path discovered and verified as canonical.** P4 R3-D3 post (`status 2067394237851636104`) shipped cleanly via `mavis mcp call playwright browser_type` + `browser_evaluate` verification. Recovery Options A-D tagged `[SUPERSEDED]` in favor of new Option E. The "What was tried" section adds the P4 success as a sibling to the v2 failure, and the cron-prompt template rewrite is locked in (no longer "proposed"). `x-publish` skill created at `~/.mavis/agents/mavis/skills/x-publish/SKILL.md`. Cross-cutting note added to `tool-quirks.md` (the mavis browser `type` doubles in ANY React-controlled contenteditable — Notion, Linear, Substack, etc.). Publish pipeline is closed.
