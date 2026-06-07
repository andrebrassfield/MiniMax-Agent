---
description: Workarounds for tool-specific bugs and gotchas — Obsidian Templater syntax, Python str.format() with braces, concurrent CLI worker output. Load when writing Templater templates, formatting LLM prompts with .format(), or running concurrent workers that print to stdout.
---

# Tool Quirks

## Templater template authoring — Write tool renders syntax (2026-06-01)
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

## Hermes CLI not on PATH by default (macOS, git install) (2026-06-06)
The Hermes CLI installs its venv at `~/.hermes/hermes-agent/venv/bin/hermes` but does NOT add that directory to `~/.zshrc` / `~/.zprofile` on git-based installs. The venv activates for the running gateway process, but a fresh interactive `hermes` shell command fails with `zsh: command not found: hermes`. `hermes --help`, `hermes doctor`, etc. all fail the same way.

**Verified 2026-06-06**: `which hermes` returned "not found" on a fresh shell. Full-path call `~/.hermes/hermes-agent/venv/bin/hermes --version` returned `Hermes Agent v0.16.0`. `hermes doctor` reported all green. The issue was purely PATH.

**Fix (reversible)**: `ln -sf ~/.hermes/hermes-agent/venv/bin/hermes ~/bin/hermes && rehash`. `~/bin/` is on PATH by default on macOS. Works immediately, survives shell restarts and Hermes reinstalls (target path is stable).

**Fix (canonical, persistent)**: add `export PATH="$HOME/.hermes/hermes-agent/venv/bin:$PATH"` to `~/.zshrc`. Makes `hermes-acp` and `hermes-agent` reachable too, not just `hermes`. Held off on this — it's a dotfile edit, ask user first.

**Affected**: any new Hermes git install on macOS where the installer doesn't add the venv to the shell rc. The bashrc-style hint in the install script doesn't run for zsh users. Test with `which hermes` on a fresh terminal.

## Hermes `fleet_reconcile.py --verify` flags real SOUL.md as drift (2026-06-06)
After replacing the default Hermes SOUL.md ("You are Hermes Agent, an intelligent AI assistant created by Nous Research…") with a real, profile-specific SOUL.md, `fleet_reconcile.py --verify` reports a SOUL/config.yaml drift for that profile. Reason: the reconcile script compares the on-disk SOUL.md against the registry's expected template; any non-default content shows as drift.

This is a FALSE POSITIVE when the drift is intentional. Distinguishing real drift from intentional replacement requires reading the diff — `fleet_reconcile.py --diff` shows the actual content. The audit's "14 SOUL/config drift" was 12 pre-existing + 2 newly-introduced by Hermes's reestablishment SOUL.md replacements. The +2 was expected, not a bug.

**Affected**: any profile that has a custom SOUL.md. The reconcile script needs an `--allow-soul-drift` flag or a similar mechanism to suppress intentional drift — pending fix in fleet_reconcile.py. Until then, expect drift count to grow whenever profiles get a real SOUL.md.

## gbrain PGLite WASM crash on macOS 26.x (2026-06-06)
Installing gbrain with the default PGLite backend on macOS 26.5.1 is unstable. Symptom: fresh init works, but any session that terminates via a killed process (SIGKILL, OOM, system sleep/wake) corrupts the WASM state permanently. The embed pipeline and MCP stdio server become unstable under repeated load. Tracked as gbrain issue #223 (open as of 2026-06-06).

**Affected**: anyone running `gbrain init --pglite` on macOS 26.x for non-toy use (single-shot imports work, ongoing cron/MCP usage does not).

**Workaround**: use the Supabase (or self-hosted Postgres) backend. The gbrain schema migrates cleanly. The 588-page DreBrain import re-runs idempotently against the new backend via `gbrain import ~/DreBrain/DreBrain/` — `content_hash` short-circuits already-imported files. The README documents Supabase as the production path for "shared / large / multi-machine deployments."

**Verification 2026-06-06**: gbrain v0.42.26.0, PGLite DB at ~/.gbrain/brain.pglite/ (86MB) on macOS 26.5.1. Import worked (588/588 pages, 0 errors), search worked (5 results for "fleet redesign" with scores 2.24-2.50), but the runtime crash pattern was reproducible and confirmed via issue #223. Pilot rolled forward to Supabase backend rather than waiting for the upstream fix.

## Supabase Postgres pooler access from this network (2026-06-06)
The Supabase project `xfqlxujtaticrsbcasai` is reachable from this host for the REST API (`https://xfqlxujtaticrsbcasai.supabase.co`, postgrest service role) and for TCP probes to `aws-0-*.pooler.supabase.com:5432` and `:6543` — all 14 regions confirmed OPEN. But actual Postgres auth is blocked on three different layers:

1. **Transaction pooler** (`db.{ref}.supabase.co:6543`): works with `psql` / `libpq` clients, but Bun's native postgres driver (used by gbrain) sends `statement_timeout` in the startup packet, which Supabase's PgBouncer in transaction mode rejects. Error: "unsupported startup parameter: statement_timeout". This is a real Bun + PgBouncer interaction, not a config issue.
2. **Session pooler** (`aws-0-*.pooler.supabase.com:5432`): TCP reachable across all 14 regions, but `psql` and Bun both return "tenant not found" for the `postgres.xfqlxujtaticrsbcasai` user format. The session pooler appears to expect a different user format or to be disabled for this project.
3. **Direct IPv6** (`db.{ref}.supabase.co:5432`): intermittent, "Connection refused consistently after initial intermittent success" per Phase I.7. Probably routing / firewall / ISP issue from this host.

**Workaround 2026-06-06**: gbrain was rolled back to local PGLite (the original Phase I setup). The 1,025 pages on Supabase are still queryable via the postgrest REST API. Full migration to Supabase Postgres is parked until one of: (a) Bun's postgres driver adds a config to suppress `statement_timeout` in startup, (b) Supabase's session pooler is reconfigured to accept the `postgres.{ref}` user format, (c) the IPv6 route to `db.{ref}.supabase.co:5432` stabilizes. Password and connection string are documented in `DreBrain/01 - ACTIVE/projects/fleet-redesign-v5/gbrain_supabase_live.md` for when one of those lands.

**Affected**: any future gbrain install on this host, any direct Postgres connection from Bun-based tools (Hermes plugins that use Bun's pg driver), any future work that needs to talk to this specific Supabase project's Postgres directly rather than via the REST API.
