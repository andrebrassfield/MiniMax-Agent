---
description: Tool-specific bugs and gotchas — Obsidian Templater syntax, Python str.format() / state-mutation pitfalls, mavis CLI quirks, gbrain/Supabase gotchas, gh auth + git credential helper, spawn lifecycle. Load when a specific tool is misbehaving and you need a verified workaround. For cross-project lessons (launchd, hygiene, PAT scope strategy), see `tooling-gotchas.md`.
---

# Tool Quirks

> **Status legend:** entries tagged `[LIVE]` are actively in use. `[PARKED]` = the underlying issue is unresolved but we have a working workaround elsewhere; keep for reference until upstream fixes. `[SUPERSEDED]` = the path described is no longer the production path; archive or delete.
>
> **Current state of gbrain (2026-06-10):** bridgebrain on port 18446 is the live path. PGLite WASM crash entry below is `[PARKED]` (kept for context, but PGLite isn't the active engine). Supabase pooler entry is `[PARKED]`.

## Templater template authoring — Write tool renders syntax (2026-06-01) [LIVE]
When writing Obsidian Templater template files (.md) via the Write tool, the `<% tp.date.now("YYYY-MM-DD") %>` and `<% tp.file.title %>` syntax gets RENDERED to static text. The file ends up with `created: 2026-06-01` (current date) and `# idea` (static title) instead of dynamic template variables. Result: the template becomes dead — it does not auto-fill on new-note creation.

**Workaround**: use bash heredoc with a quoted delimiter:
```bash
cat > file.md << 'TEMPLATE_EOF'
...content with <% tp.* %>...
TEMPLATE_EOF
```
The single-quoted delimiter disables variable expansion, preserving text literally. The Edit tool's exact-string replacement also works (does not render template syntax).

**Verified 2026-06-01**: wrote 4 new templates (idea.md, pattern.md, question.md, number.md) via Write tool — all had static dates and titles. Rewrote via heredoc — all 9 expected `<% tp.* %>` occurrences intact. Title line confirmed at correct position in each file.

**Affected**: any future template file in `99 _system/templates/` or anywhere with Templater syntax. Always use heredoc or Edit, never Write, for these files.

## Python .format() with braces in LLM prompt templates (2026-06-02)
When using `str.format()` to render an LLM prompt template, escape literal `{` and `}` as `{{` and `}}` in the FORMAT STRING. User-supplied content (the Mavis output, the example JSON) is passed as VALUES, not as format specifiers — `{}` chars in values are inserted as-is and don't break formatting.

**Example bug** (hit in evaluator.py v0.2.0): the prompt template had:
```python
"expected_score_format": "say \"publish\" or \"go\" and I will run..."
```
where `"publish"` and `"go"` were literal text. The .format() call interpreted them as field references and threw `KeyError: '"publish"'` or similar.

**Fix**: either escape the inner quotes OR rephrase to avoid the inner braces (`say publish or go and I will run...` is cleaner and avoids the issue entirely).

**Rule of thumb**: in the format string, every `{` that's NOT a field reference should be `{{`. In the values, no escaping needed — strings are inserted verbatim. When in doubt, write a test that passes user content with literal `{}` chars to confirm no breakage.

## Concurrent CLI output: one self-contained line per worker (2026-06-02)
When running N workers in a thread pool that all print to stdout, do NOT use the `print(..., end="", flush=True)` "header" pattern followed by a later `print(result)` "body" follow-up. With concurrent execution, the headers pile up on stdout before any body can print, producing interleaved garbage like:
```
  [1/25] foo...  [3/25] bar...  [2/25] baz...  DRY-RUN
 DRY-RUN
```

**Correct pattern**: one self-contained line per worker, printed at completion. Hold the `print_lock` for the entire `print(...)` call so the line is atomic:
```python
with print_lock:
    print(f"  [{n}/{total}] {item_id} ({category}) — "
          f"{pass_str} (score={score_str}, {duration_ms}ms)")
```

**Atomicity is what matters.** The print_lock prevents byte-level interleaving; the single self-contained line prevents the "header without body" race where one thread's header lands before another thread's body.

Hit this twice in the SOUL compliance evaluator v0.3.0 refactor: first attempt with `end=""` headers, garbled output. Fix to single-line pattern, clean output.

## Team plan decision JSON requires arrays + plan_complete (2026-06-04)
`mavis team plan decision <plan_id> --file <path>` rejects decisions where `last_cycle` and `next_cycle` are objects. The error is `last_cycle: Expected array, received object` / `next_cycle: Expected array, received object` / `plan_complete: Required`. Both fields must be ARRAYS of task-decision objects, and `plan_complete` is a required boolean at the top level (not inside either array).

**Working skeleton**:
```json
{
  "last_cycle": [
    { "task_id": "step-N", "verdict": "accept", "reason": "..." }
  ],
  "next_cycle": [],
  "plan_complete": false,
  "message_to_user": "Step N accepted. ..."
}
```

The mavis-team skill shows the schema in prose, but the YAML examples use bare object form for these fields and the CLI parser is strict. Easy first-time mistake. Verified 2026-06-04: cycle 1 decision failed on object form, succeeded on array form.

`verdict` values: `accept` (done) | `reject` (retry, keep same task_id) | `override_accept` (accept despite verifier) | `manual_retry` (retry with explicit correction in reason). For accept-only decisions, `next_cycle: []` and `plan_complete: false` until the last cycle.

## Mavis agent description has a 100-character hard cap (2026-06-03)
`mavis agent new --description` validation error code 40002 ("String must contain at most 100 character(s)") fires on the description field. `mavis agent info` will show the truncated description. Workaround: keep descriptions to ≤100 chars. The display-name and agent.md body are not capped.

## zsh chokes on parens/glob chars in inline mavis communication send --content args (2026-06-03)
Symptom: `zsh:1: no matches found`. Workaround for long prompts with mixed punctuation: write the prompt to a file (e.g., `/tmp/<task>-prompt.md`), then JSON-encode via `printf '%s' "$PROMPT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'`, then pass via heredoc. Or escape the parens. File-load is more reliable for long prompts.

## mavis communication send --command spawn returns "delivered" immediately; worker boots async (2026-06-03)
Don't poll the return for a verdict — the spawned agent reports back via an `<agent-message from-session="...">` block when it has something to say. Track spawned sessions via the `peers_update` block in subsequent turns, or set a cron self-reminder to poll. Test spawns (with prompt="test") are cheap but accumulate; abort duplicate test sessions before sending the real task.

## Spawn-lifecycle gotcha: spawn-with-prompt vs. spawn-then-send-task (2026-06-05)
Spawning a worker with `mavis communication send --command spawn --content '{"agent":"<name>","model":"...","prompt":"<some text>"}'` creates a session that BOOTS, sends a one-line "<ready>" ack, and goes `finished` state. The actual task spec is NOT delivered — the worker is waiting for a SEPARATE prompt. Subsequent `mavis communication send --to <session> --command prompt --content "<actual task>"` will wake the session and deliver the task. The session is still alive even in `finished` state.

**Concrete instances (2026-06-05).** 3 spawns to `verifier` and 2 spawns to a Researcher all followed this pattern: spawn with prompt="ready", session boots, sends ack, goes finished. Then the actual task was sent as a separate `prompt` command. One Researcher session reported the wrong patch summary — it had re-ported the previous Researcher's summary because it didn't receive the new task spec, only the spawn prompt. The session list lags 10-25 seconds after spawn — newly spawned sessions don't appear in `mavis session list` immediately, but they ARE alive and will receive subsequent prompts.

**The discipline (correct spawn flow):**
1. Spawn: `mavis communication send --command spawn --content '{"agent":"<name>","model":"...","prompt":"<name> ready"}'` — this creates the session.
2. Wait for the "ready" ack (an `<agent-message from-session="...">` block) to confirm the session is alive.
3. Send the actual task: `mavis communication send --to <session-id> --command prompt --content "<full task spec>"`.

**OR (alternative correct flow):** spawn with the full task in the `prompt` field. The session boots, gets the task as its initial context, and starts working immediately. The "ready" ack may be skipped or arrive after the work begins.

**The wrong flow (what I did multiple times this session):** spawn with a placeholder prompt ("ready"), expect the session to wait indefinitely. It doesn't — it sends a "ready" ack and goes finished. Send the task to a session that hasn't been spawned. Forget to send the actual task at all and assume the spawn prompt was the task.

**Discriminator vs. orphan-spawn.** A normal spawn sends a status signal as the initial prompt, then follows up with the real task as a separate `--command prompt` message. An ORPHAN spawn sends ONLY the status signal and never follows up (see `orchestration-failure-modes.md` §6). The presence/absence of the follow-up task prompt is the discriminator. Always check `mavis session messages <workerId>` before accepting work.

## gbrain PGLite WASM crash on macOS 26.x (2026-06-06)
Installing gbrain with the default PGLite backend on macOS 26.5.1 is unstable. Symptom: fresh init works, but any session that terminates via a killed process (SIGKILL, OOM, system sleep/wake) corrupts the WASM state permanently. The embed pipeline and MCP stdio server become unstable under repeated load. Tracked as gbrain issue #223 (open as of 2026-06-06).

**Affected**: anyone running `gbrain init --pglite` on macOS 26.x for non-toy use (single-shot imports work, ongoing cron/MCP usage does not).

**Workaround**: use the Supabase (or self-hosted Postgres) backend. The gbrain schema migrates cleanly. The 588-page DreBrain import re-runs idempotently against the new backend via `gbrain import ~/DreBrain/DreBrain/` — `content_hash` short-circuits already-imported files. The README documents Supabase as the production path for "shared / large / multi-machine deployments."

**Verification 2026-06-06**: gbrain v0.42.26.0, PGLite DB at ~/.gbrain/brain.pglite/ (86MB) on macOS 26.5.1. Import worked (588/588 pages, 0 errors), search worked (5 results for "fleet redesign" with scores 2.24-2.50), but the runtime crash pattern was reproducible and confirmed via issue #223. Pilot rolled forward to Supabase backend rather than waiting for the upstream fix.

## Fine-grained GitHub PAT: Issues and Pull requests are SEPARATE permissions (2026-06-08)

Fine-grained GitHub PATs (`github_pat_*` prefix) split the conceptual "Issues + PRs" surface into **two distinct permission toggles** on the token's settings page: "Issues" and "Pull requests." They look like one feature in the GitHub UI ("Issues and PRs") but the API treats them as separate resources, and granting one does NOT grant the other.

**Symptom (hit 2026-06-08 21:54 CT)**: Created a fine-grained PAT with `Contents: Read+Write` and `Issues: Read+Write` for the Mavis-Socratic PR workflow. `gh api repos/.../issues` worked (returned 200 with empty list). `gh pr create` failed with `GraphQL: Resource not accessible by personal access token (repository.pullRequests)`. Direct REST call to `/pulls` returned 403 "Resource not accessible by personal access token." Adding "Pull requests: Read and Write" resolved both.

**The non-obvious detail**: the GitHub web UI token editor groups Issues and PRs visually on the same line, and the permission toggle is labeled something like "Issues: Read and Write" without making clear that PRs are a separate toggle. An agent (or human) reading "I have Issues access" will reasonably assume they can create PRs, because PRs are a sub-resource of Issues in the data model. They're not, on the API permission model.

**Workaround / correct setup for any agent doing PR-workflow collaboration:**
- `Contents: Read and Write` — for clone, push, read files
- `Metadata: Read-only` — forced, leave it
- `Issues: Read and Write` — for issue creation, comments, labels
- `Pull requests: Read and Write` — **separate from Issues**; required for `gh pr create`, `gh pr list`, `gh pr merge`, and the `/pulls` REST endpoints
- `Actions: Read and Write` (optional) — only if the agent needs to trigger or inspect workflow runs

**Verification 2026-06-08**: token at `~/.config/gh/mavis-token` (`github_pat_11BUQYGPY0zHct95eVVxsu_...`, mode 600). After adding "Pull requests: Read and Write" on top of existing scopes, `gh api repos/.../pulls` returned 200, `gh pr create` succeeded (PR #1 opened against `andrebrassfield/socratic-hermes-brain` from branch `mavis/task-complete-thr82a101`).

**Affected**: any future fine-grained PAT minted for an agent that needs to do PR-workflow collaboration. Always include "Pull requests" as a separate permission, do not assume "Issues" covers it.

## git credential helper on this Mac reads from a path the shell can't see (2026-06-08)

The system-wide git credential helper is configured at `~/.gitconfig` to use `!/Users/brassfieldventuresllc/.local/bin/gh auth git-credential` for `https://github.com` operations. **That binary path does not exist on this machine** — the real `gh` is at `/opt/homebrew/bin/gh` (Homebrew install). The system config appears to be stale (perhaps from an earlier install location, perhaps from a different machine's config that got copied over).

**Symptom (hit 2026-06-08 21:49 CT)**: `git clone https://github.com/.../socratic-hermes-brain.git` fails with `fatal: could not read Username for 'https://github.com': Device not configured`, even after `gh auth login` succeeded and `gh repo clone` works fine. The credential helper shell-out fails silently, git falls back to interactive auth, the non-interactive shell hangs.

**Workaround** (use this pattern for any future `git push` / `git pull` against GitHub in this shell):
```bash
# Force git to use an inline credential helper that reads GH_TOKEN from env
export GH_TOKEN="$(cat ~/.config/gh/mavis-token)"
git -c credential.helper= -c credential.helper='!f() { echo username=git; echo password="$GH_TOKEN"; }; f' push ...
```

The first `-c credential.helper=` clears the inherited helper, the second sets the inline one. The shell function reads `GH_TOKEN` from the current shell's env, prints the username (`git`, the literal — not the user's GitHub login) and the password (the PAT). Git consumes them, the push proceeds.

**Long-term fix** (worth a separate ticket): either symlink `/Users/brassfieldventuresllc/.local/bin/gh` to `/opt/homebrew/bin/gh`, or fix the `~/.gitconfig` credential helper to point at the Homebrew path. Until then, every `git` operation that hits github.com needs the inline-credential dance.

**Affected**: every `git push` / `git pull` against GitHub in this shell. `gh repo clone` and `gh api` work because they use the token via `GH_TOKEN` directly, not via the credential helper. `git` operations don't.

## Supabase Postgres pooler access from this network (2026-06-06)
The Supabase project `xfqlxujtaticrsbcasai` is reachable from this host for the REST API (`https://xfqlxujtaticrsbcasai.supabase.co`, postgrest service role) and for TCP probes to `aws-0-*.pooler.supabase.com:5432` and `:6543` — all 14 regions confirmed OPEN. But actual Postgres auth is blocked on three different layers:

1. **Transaction pooler** (`db.{ref}.supabase.co:6543`): works with `psql` / `libpq` clients, but Bun's native postgres driver (used by gbrain) sends `statement_timeout` in the startup packet, which Supabase's PgBouncer in transaction mode rejects. Error: "unsupported startup parameter: statement_timeout". This is a real Bun + PgBouncer interaction, not a config issue.
2. **Session pooler** (`aws-0-*.pooler.supabase.com:5432`): TCP reachable across all 14 regions, but `psql` and Bun both return "tenant not found" for the `postgres.xfqlxujtaticrsbcasai` user format. The session pooler appears to expect a different user format or to be disabled for this project.
3. **Direct IPv6** (`db.{ref}.supabase.co:5432`): intermittent, "Connection refused consistently after initial intermittent success" per Phase I.7. Probably routing / firewall / ISP issue from this host.

**Workaround 2026-06-06**: gbrain was rolled back to local PGLite (the original Phase I setup). The 1,025 pages on Supabase are still queryable via the postgrest REST API. Full migration to Supabase Postgres is parked until one of: (a) Bun's postgres driver adds a config to suppress `statement_timeout` in startup, (b) Supabase's session pooler is reconfigured to accept the `postgres.{ref}` user format, (c) the IPv6 route to `db.{ref}.supabase.co:5432` stabilizes. Password and connection string are documented in `DreBrain/01 - ACTIVE/projects/fleet-redesign-v5/gbrain_supabase_live.md` for when one of those lands.

**Affected**: any future gbrain install on this host, any direct Postgres connection from Bun-based tools (Hermes plugins that use Bun's pg driver), any future work that needs to talk to this specific Supabase project's Postgres directly rather than via the REST API.

## Python: `state = state or {}` rebinds and silently breaks in-place mutations (2026-06-07)

When a function takes a mutable dict parameter and the caller may pass `{}` (empty dict is FALSY in Python), `state = state or {}` rebinds the local name to a new dict instead of keeping the reference. Subsequent `state[key] = value` mutations happen on the new local dict, not the caller's. The caller never sees the updates.

**Discovered in:** a fleet-watchdog daemon. The `state = state or {}` line meant the weekly pacer was silently a no-op — the sidecar state file was never written, and the same 3 cards would have re-paged every 30 minutes forever instead of being silenced for the week.

**The fix:** distinguish "not provided" from "provided empty":
```python
if state is None:
    state = {}
```
NOT `state = state or {}` — that conflates `None` and `{}` and breaks reference semantics for empty inputs.

**General rule for mutable defaults in Python:**
- `def f(x=None): x = x or []` → BUG when caller passes `[]` and mutates
- `def f(x=None): if x is None: x = []` → safe
- Same applies to dicts, sets, lists — any falsy empty value gets clobbered

**Diagnostic pattern:** if mutations to a dict parameter are not visible to the caller, search the function for `param = param or default_value` and replace with `if param is None: param = default_value`. Also check `param = param or default_value` inside loops, helper functions, and conditionals.

**Related:** `fleet-trust-patterns.md` §4 verdict-before-synthesis — silent state divergence is a fleet-trust failure mode (verification would have caught this if the state file content was checked after each run).

## Ollama num_ctx default = 4096 silently truncates large prompts (2026-06-13) [LIVE]
Ollama loads GGUF models with `context_length: 4096` as the default, regardless of what the model's real context window is. When you POST a prompt larger than ~3K tokens (with `num_predict` room on top), Ollama returns 200 OK with `response: ""` and `done_reason: "length"` — no error, no warning, just empty content. The model loaded, processed tokens, hit the context limit *during prompt processing*, and never got to generate visible text.

**Symptom:** `requests.post(... timeout=300)` returns 200, `data["response"]` is empty string, `data["done_reason"] == "length"`. From the script's perspective: "Ollama chat returned 0 chars" with no exception.

**Hit on:** `gemma4:12b-it-qat` (Q4_0, 11.9B) on 2026-06-13. The model's real `context_length` is 262144 (per `/api/tags`), but `ollama ps` shows it loaded with `context_length: 4096`. Setting `num_ctx: 32768` (or whatever fits the prompt + response) makes it work.

**Fix:** always set `num_ctx` explicitly in the Ollama call:
```python
payload = {
    "model": "gemma4:12b-it-qat",
    "prompt": prompt,
    "options": {
        "num_predict": 4000,
        "num_ctx": 32768,  # explicit, not the 4096 default
    },
}
```

**Verification pattern:** after a successful Ollama call, check `data["done_reason"]` — `"length"` means it hit the limit; `"stop"` means natural completion. If you see `"length"` with empty `response`, the prompt was too big for the configured context.

## Local LLM throughput on M-series Mac via Ollama (2026-06-13) [LIVE]
gemma4:12b-it-qat (Q4_0, 11.9B params) on Andre's Mac via Ollama direct: **~12 tokens/sec** for both prompt_eval and eval. This is the binding constraint on any "synthesize the vault" workflow.

**Implication for timeouts:** 30K-token prompt + 4K-token response = 34K tokens = ~47 minutes at 12 tok/s. A 5-minute HTTP timeout will silently truncate. A 30-minute timeout barely fits. A 60-minute timeout is the right floor for a weekly-scale synthesis job.

**Implication for prompt size:** a 130K-character prompt (~32K tokens) takes ~45 min for prompt_eval alone. If you need a sub-10-min turn-around, cap the prompt at ~7K tokens (≈ 30K characters). For daily-brief-style work, top-20 captures × 1.5K chars each = ~7.5K tokens is the sweet spot.

**Implication for cron scheduling:** a daily-synthesis cron that takes 15-20 min in steady state needs a schedule with 30+ min headroom before the next dependent job. A weekly cron that takes 60+ min shouldn't share the same day as a daily run.

**Workaround for speed (not yet tried):** switch to `gemma4:e4b-it-qat` (7.5B Q4_0) which should be ~1.5-2x faster. Or use the bridge → harness → MiniMax-M3 path for synthesis (faster, costs M3 budget). Both are follow-ups, not blockers.

**The general lesson:** any "synthesize N documents" job on a local M-series Mac has a ~12 tok/s ceiling for 12B-class models. Budget for it. Don't write `timeout=300` for a 30K-token prompt — that's wishful thinking.

## MiniMax key types — `sk-cp-` (token-plan) vs `sk-api-` (platform) (2026-06-13) [INCIDENT]
Type: agent

An `.env` file had `MINIMAX_API_KEY` set to an `sk-api-...` (platform) key. `https://api.minimax.io/v1` returned **HTTP 402 `insufficient_balance_error` http_code 1008** on live calls. The misread was "billing problem" — but it was a key-type mismatch. The actual key is `sk-cp-...` (token-plan type), and that's the same key Mavis itself uses.

**Rule (formalized):**

| Key prefix | Type | Endpoint it works on | What 402 actually means |
|---|---|---|---|
| `sk-cp-...` | Token Plan | `https://api.minimax.io/v1` | **Key is wrong type for this endpoint**, OR plan quota genuinely exhausted (rare — Token Plan has 5h rolling + weekly limits, see screenshot) |
| `sk-api-...` | Platform (pay-as-you-go) | Different endpoint (NOT `api.minimax.io/v1`) | n/a for `api.minimax.io` calls |

**Don't conflate:**
- HTTP 401 → bad/missing key
- HTTP 402 + `insufficient_balance_error` (1008) → **wrong key type** for the endpoint you're hitting, OR genuine billing issue (verify with the Token Plan dashboard screenshot)
- HTTP 200 with empty `content` + `finish_reason: "length"` → model ran out of max_tokens mid-generation (M3 burns tokens on `<think>` tags by default — give it 200+ tokens for short replies, 2K+ for real answers)

**How to verify a key fast:**
```bash
curl -sS -X POST "https://api.minimax.io/v1/chat/completions" \
  -H "Authorization: Bearer $KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MiniMax-M3","max_tokens":15,"messages":[{"role":"user","content":"say ok"}]}' \
  --max-time 15
```
- 200 → key works, you're good
- 401 → wrong/missing key
- 402 / 1008 → wrong key type (`sk-api-` won't work on this endpoint — you need `sk-cp-`)

**Cross-project:** the key-type confusion will hit any future session that auto-detects `MINIMAX_API_KEY` from env. Always check the prefix before debugging balance.

**Why this is agent memory, not project memory:** the `sk-cp-` vs `sk-api-` distinction is a fact about the MiniMax platform, durable across any project.

## mavis browser `type` duplicates text 2x in React-controlled contenteditable (2026-06-17) [LIVE]

The `mavis browser tool type` command fires text twice into any React-controlled contenteditable. Verified on X.com compose (both the inline `[data-testid="tweetTextarea_0"]` and the modal textbox). A single character typed via the tool reads back as "XX"; a 233-char post reads back as 466 chars with the duplicate appended immediately. This is the v2 attempt at 13:10 CT (documented in `03 Projects/X-Content-Engine/agents/feedback-loop.md`) plus a second reproduction at 18:48 CT.

**Root cause (as of 2026-06-17):** the IPC bridge's `type` dispatches input events that React's onChange picks up as two state updates per character. Could be (a) the bridge firing the event twice, (b) React StrictMode double-firing, or (c) the contenteditable mirroring value in two places. Whichever — the user-visible result is identical: text lands 2x, every time.

**`press_key Backspace` and `press_key Delete` are ALSO broken in this environment** — they append the prior typed text instead of deleting. Confirmed 18:48 CT. Select-all + delete (Ctrl+A → Delete) leaves the text in place and adds one char. So even the "delete the duplicate" workaround is blocked.

**`press_key Cmd+V` is broken too** — X's paste handler gates on a real user-gesture trusted-paste flag, which the IPC-bridged keypress doesn't carry. Clipboard paste is silently dropped.

**The working path (the fix):** use the **Playwright MCP** with `browser_type`. Internally Playwright calls `page.fill()` which sets the textarea value directly via the DOM `value` property — no keyboard event chain, no React onChange race, no duplication. Verified 18:48 CT: typed 233 chars once, `browser_evaluate` on `[data-testid=tweetTextarea_0]` returned exactly the 233 chars, post went live at `x.com/DreTheSalesGuy/status/2067394237851636104`.

**The pattern (reusable for any "fill a React-controlled contenteditable" task):**
```bash
mavis mcp call playwright browser_navigate '{"url":"<page>"}'
mavis mcp call playwright browser_snapshot '{}'  # get the textbox ref
mavis mcp call playwright browser_type '{"element":"<textbox>","ref":"<e88>","text":"<verbatim>","submit":false}'
# verify
mavis mcp call playwright browser_evaluate '{"function":"() => document.querySelector(\"<selector>\").innerText"}'
```

**Affected surfaces (confirmed as of 2026-06-17):**
- x.com compose (inline + modal)
- Likely any React/ProseMirror/TipTap-controlled editor (Notion, Substack, Ghost, Linear, etc.) — the bug is at the IPC layer, not the X-specific surface

**Affected skills:** the `x-publish` skill (`~/.mavis/agents/mavis/skills/x-publish/SKILL.md`) is built around this fact. The older `twitter-playwright-poster` (Hermes-side, Python+Playwright direct) was the original workaround path — the Playwright MCP `page.fill()` is now the canonical Mavis-side mechanism.

**Why this is agent memory, not project memory:** the IPC bridge bug is at the tool layer, durable across every project that uses mavis browser `type` on a React-controlled editor.
