---
name: post-n-v2-batch
type: closed-loop
generator: ea-closed-loop-builder
date: 2026-06-17
status: paused — chain halted at post-3 (Drafts 1+2 absent from brain)
---

# Closed-Loop Spec — X-Content-Engine v2 Batch (3 posts, 4-hour pacing)

## 1. GOAL

Post 3 drafts from the v2 batch to @DreTheSalesGuy on X.com with strict 4-hour pacing between each post. Each post must:
- Land on X.com with text byte-equal to the source
- Be recorded in `03 Projects/X-Content-Engine/memory/content_brain.json` `performance_log` with the post URL
- Be annotated in the source file with a "PUBLISHED <timestamp> CT — <url>" line

**Success criterion:** 3 entries in `content_brain.json` `performance_log` for dates 2026-06-16, 2026-06-17, 2026-06-17, all with valid `x.com/DreTheSalesGuy/status/<id>` URLs, and the source file in `03 Projects/X-Content-Engine/archive/` (only moved after the LAST post succeeds).

**Stop condition for the loop:** all 3 posts landed (loop complete) OR any post HALTs at audit / text-mismatch / chain-validation (loop paused for human recovery).

## 2. CONTEXT

- **VISION.md reference** — `03 Projects/X-Content-Engine/persona.md` (the 6 pillars + 6 voice examples; the "Scribe never publishes to x.com" Hard Rule #10)
- **ARCHITECTURE.md reference** — `03 Projects/X-Content-Engine/agents/scribe.md` (Scribe system prompt, draft format, approved/ vs drafts/ vs archive/ directory semantics)
- **RULES.md reference** — `~/.mavis/agents/mavis/skills/ea-skill-evolution/SKILL.md` (mirror discipline: home == vault, byte-for-byte); `~/.mavis/agents/mavis/memory/MEMORY.md` §"Disk wins over recap"; the X-Content-Engine v2 batch's 4-hour pacing directive (set by Andre)
- **Closed-loop spec format** — `~/.mavis/agents/mavis/skills/ea-closed-loop-builder/SKILL.md` (5-section: Goal / Context / Action / Feedback / Stop condition)
- **Three-hard-stops discipline** — `~/.mavis/agents/mavis/memory/loop-engineering-framework.md` (max iter / no-progress / $ ceiling; the cron fleet's discipline)

## 3. ACTION

The loop runs as 3 sequential cron-triggered sessions, each ~4 hours apart. Each post-N session executes the same 10-step procedure (customized per N for the specific draft text):

**For post-N (N in {1, 2, 3}):**

1. **FINAL AUDIT** (mandatory, blocks the procedure):
   - Verify source file exists at `approved/humanized-machine-batch-2026-06-16-v2.md` and contains Draft N
   - For N > 1: verify Drafts 1..N-1 are present in `content_brain.json` `performance_log` (chain-validation)
   - Read `99 _system/dashboards/x-metrics-dashboard.md` and confirm Draft N's hook is NOT in the 30d window (no duplicate)
   - Confirm `approved/` is the source (NOT `drafts/` — drafts is working dir, approved is publish queue)
   - Any audit failure → HALT, exit non-zero (silent-failure patch on the crons enforces this)

2. **PROCEDURE** (10 steps, run only if audit passed):
   1. `mavis browser tool open_tab '{"url":"https://x.com/compose/post"}'`
   2. Note the returned tabId
   3. `mavis browser tool navigate` to the same URL (forces a clean compose modal)
   4. `mavis browser tool snapshot` to find the compose text area
   5. Click the compose text area
   6. `mavis browser tool type` the post text exactly (no extra chars, no leading/trailing whitespace, load-bearing specifics preserved — em-dash for Draft 2, period for Drafts 1+3)
   7. `mavis browser tool snapshot` to verify the typed text matches the source (load-bearing specifics: Draft 1: '$876K', '9.5x', '90 days', 'Build the damn thing'; Draft 2: '10K-orders/month', '5% LDR', '$2,500/month', 'real-time inventory sync', 'Not a wrapper'; Draft 3: '200 lines of Python', '30-second polling fallback', "vendor's own product can't write call notes")
   8. Find and click the Post button
   9. `mavis browser tool snapshot` to confirm the post was published
   10. Extract the post URL (format: `https://x.com/DreTheSalesGuy/status/<id>`)

3. **ON SUCCESS — log to brain** (atomic write, temp + fsync + rename):
   - Append entry to `performance_log`: `{post_id: '<extracted_url>', hook_used: '<first sentence>', views: 0, likes: 0, date: '<YYYY-MM-DD>', _note: 'auto-published via mavis cron <timestamp> CT (Draft N of v2 batch)'}`
   - If `grep -q post_id content_brain.json` returns non-zero AFTER the append, exit 1 (silent-failure mode)

4. **ON SUCCESS — update source file**:
   - For Drafts 1+2 (not the last): add a "Draft N: PUBLISHED <timestamp> CT — <url>" note at the top of Draft N's section. Do NOT move the file.
   - For Draft 3 (the last): `mkdir -p 03 Projects/X-Content-Engine/archive && mv approved/humanized-machine-batch-2026-06-16-v2.md archive/humanized-machine-batch-2026-06-16-v2.md`

5. **ON FAILURE — HALT and report** (exit 1, do NOT clean up the cron):
   - Login prompt: HALT, report UI state
   - Rate limit: HALT, report the message
   - Text mismatch (load-bearing specifics absent or altered): HALT, report the diff
   - UI changes (button location, layout, X.com compose flow changed): HALT, report the snapshot
   - Chain-validation failure (upstream post absent from brain): HALT, report which upstream is missing
   - Any other error: HALT with the exact error message

6. **CLEANUP — gated on post-success verification**:
   - Run `grep -q post_id 03\ Projects/X-Content-Engine/memory/content_brain.json` (must exit 0)
   - If exit 0: `mavis cron delete mavis post-N-v2-2026-06-16`
   - If exit 1: leave the cron in place; surface to Andre that the cron is in recovery mode

7. **REPORT BACK to Andre via this session** (terse, per the playbook):
   - Success: `'Draft N posted. URL: <url>. Brain updated. Cron post-N-v2-2026-06-16 deleted.'`
   - Halt: `'Draft N HALTED. Reason: <reason>. Cron post-N-v2-2026-06-16 NOT deleted.'`

## 4. FEEDBACK (the verification gate)

The loop's feedback is the post-success verification chain. Three layers, all must pass for the loop to consider a tick "successful":

1. **Layer 1: chain-validation** (per cron, blocks the procedure) — Drafts 1..N-1 must be in `content_brain.json` `performance_log` for any post N > 1. Disk check, not recap.
2. **Layer 2: text verification** (per cron, after type, before click Post) — the typed text must contain the load-bearing specifics named in step 7 of the procedure. Snapshot, not recap.
3. **Layer 3: brain verification** (per cron, after the append) — `grep -q post_id content_brain.json` must exit 0. Disk check, not recap.

**Why three layers:** the @cv_usk failure mode (cron says green, on-disk state unchanged) is a class of bug that survives single-layer verification. The chain-validation catches upstream failures; the text verification catches UI/typing failures; the brain verification catches silent-failure. All three together close the class.

**The verification gate IS the eval.** Per the article's question "Who decides if the output is good enough?" — the cron itself does, via the three layers. The human (Andre) reviews the report-back, not the work.

## 5. STOP CONDITION

The loop stops (pauses for human recovery) when ANY of the following hold:

- **Chain-validation failure** — any post N > 1 with Drafts 1..N-1 absent from `content_brain.json` `performance_log`. The cron HALTs, exit 1, leaves the cron in place for the next-tick recovery. The 4-hour pacing is broken until the chain is reconciled.
- **Text-mismatch failure** — load-bearing specifics absent or altered in the typed text. HALT, exit 1, leave the cron in place.
- **Login prompt or UI change** — the browser tool reports a state that doesn't match the procedure's assumptions. HALT, exit 1, leave the cron in place.
- **Brain update verification failure** — the append didn't land (silent-failure). HALT, exit 1, leave the cron in place.

The loop completes (not just stops) only when:

- All 3 posts have valid `content_brain.json` `performance_log` entries with `x.com/DreTheSalesGuy/status/<id>` URLs
- The source file is in `archive/`
- All 3 crons (`post-1-v2-2026-06-16`, `post-2-v2-2026-06-16`, `post-3-v2-2026-06-16`) are deleted

**Recovery path** (not part of the loop — human-only):
1. Audit the halted session's transcript at `.mavis/sessions/<sessionId>/` to find the root cause
2. Decide: re-run the chain, backfill the brain, or skip the batch
3. Apply the fix; the next tick picks up the work

## Current state (2026-06-17 04:32 CT)

- post-1 (20:30 CT 2026-06-16): HALTED silently. X.com compose text duplicated 4×. Session did not click Post. Cron reports `lastResult=success` (session ran without throwing). Brain not updated. Source file not annotated.
- post-2 (00:30 CT 2026-06-17): HALTED via audit 2. Detected Draft 1 absent from brain. Cron reports `lastResult=success` (runner error). Brain not updated. Source file not annotated.
- post-3 (04:30 CT 2026-06-17): HALTED via chain-validation. Detected Drafts 1+2 absent from brain. Cron `lastResult` is unknown at time of writing (was 04:32 CT, the cron-executor report was just received). Source file in approved/ (not yet archived).

**The loop IS getting sharper** (per the article's "does the next run get better"): post-1 HALTed silently → post-2 HALTed via audit → post-3 HALTed via chain-validation. Each run came back a little sharper than the last. But the upstream chain (Drafts 1+2) is still unresolved.

**Andre's call needed** (recovery, not loop):
- (a) Re-run the chain from post-1 with the original 4-hour pacing (re-derive the text from source, post fresh)
- (b) Backfill `content_brain.json` with the actual post URLs (if Drafts 1+2 are actually live on X.com but the brain is stale)
- (c) Skip the v2 batch, archive the source file with a "DRAFTS NOT POSTED" note, move on
