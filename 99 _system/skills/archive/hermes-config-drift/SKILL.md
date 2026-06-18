---
name: hermes-config-drift
description: |
  Diagnose and repair the three-layer Hermes config when the desktop app
  errors with "API call failed: HTTP 500/401/402", when the wrong provider
  / model / endpoint is being routed to, when the agent silently flips
  between providers, or when a chat session lands on a model the user did
  not choose. Triggers on phrases like "hermes config broken", "hermes
  routing wrong", "agent flipped to nous", "wrong model", "token plan not
  working", "hermes using fallback", or any symptom where `hermes doctor`
  shows green but the active session is on a different provider than the
  user expects. Do NOT load this for general agent debugging, network
  timeouts unrelated to provider routing, or Hermes update / version
  questions. The repair script + healthcheck cron already exist on disk;
  this skill encodes when to trust them, when to override, and how to read
  the symptoms.
metadata:
  version: "1.0"
  category: fleet-orchestration
  scope: agent
  authored: 2026-06-13
  codifies: 2026-06-13 deep-clean + drift incident
---

# Hermes Config Drift — Diagnose & Repair

## Inputs to collect

Before touching anything, read these three files in this exact order. The procedure is only safe when all three are read first — the rehydrate script writes to all three and you need the prior state to know which layer is wrong.

```bash
HERMES_HOME="${HERMES_HOME:-/Users/brassfieldventuresllc/.hermes}"
echo "=== 1. config.yaml (model block) ==="
sed -n '/^model:/,/^[^ ]/p' "$HERMES_HOME/config.yaml" | head -10
echo "=== 2. .env (key shape only, redact) ==="
grep -E "^(MINIMAX|HERMES|OPENAI|ANTHROPIC|GITHUB|XAI|GEMINI|OPENROUTER|NVIDIA|HUGGING|MEM0|FIRECRAWL|MISTRAL|TAVILY|BRAVE|EXA|NOTION|OBSIDIAN|SUPABASE|LCM|WEBHOOK|SUDO|TELEGRAM|GBRAIN|OPENCODE)_[A-Z_]*=" "$HERMES_HOME/.env" 2>/dev/null | sed 's/=.*/=<redacted>/'
echo "=== 3. auth.json (active_provider + pool status) ==="
"$HERMES_HOME/hermes-agent/venv/bin/python" -c "
import json
d = json.load(open('$HERMES_HOME/auth.json'))
ap = d.get('active_provider')
pool = d.get('credential_pool', {}).get(ap, [])
print(f'  active_provider = {ap!r}')
for c in pool:
    print(f'  pool entry {c.get(\"id\")[:6]} auth_type={c.get(\"auth_type\")!r} '
          f'last_status={c.get(\"last_status\")!r} '
          f'last_error={c.get(\"last_error_code\")} {c.get(\"last_error_reason\")!r}')
"
```

If the user is on a non-default Hermes home, ask for `HERMES_HOME` before proceeding — never assume the standard path.

## Three-layer rule (the rule that must hold)

Hermes decides which provider to route to from three places. All three must agree. **If any one disagrees, the symptom looks like the wrong provider silently flipping back to a default.**

| Layer | File | Master field | What writes it |
|---|---|---|---|
| 1 | `~/.hermes/config.yaml` | `model:` block (`provider`, `default`, `base_url`) | `hermes config set model.X Y` (CLI) — atomic_yaml_write |
| 2 | `~/.hermes/.env` | `MINIMAX_API_KEY` / `MINIMAX_TOKEN_PLAN_KEY` value (and any other provider key) | Direct edit (must be atomic write) |
| 3 | `~/.hermes/auth.json` | `active_provider` (top-level) — **master switch** | Internal auth flow. The CLI's `config set` does NOT touch this. |

The `auth.json` `active_provider` is what the auth subsystem consults first; the `model:` block in `config.yaml` is only a fallback. This is the most common source of "config drift" symptoms: a fresh `config.yaml` model block says the right thing, but `auth.json` still points to the old provider, so the runtime ignores layer 1.

## Procedure

### Step 1 — Confirm the symptom matches the drift pattern

Drift symptoms:
- `hermes doctor` shows all green **but** a live session is hitting a different provider / model than the user expected.
- The CLI header shows `Provider: nous` / `Model: nvidia/nemotron-3-ultra:free` when the user configured `minimax-oauth` / `MiniMax-M3`.
- A request fails with `HTTP 500` from `inference-api.nousresearch.com` even though the user has the MiniMax Token Plan key configured.
- The user pasted a `hermes-resume` log showing `WARNING agent.auxiliary_client: resolve_provider_client: unhandled auth_type oauth_minimax for minimax-oauth` repeatedly.

**Why:** the user often reports "Hermes is broken" without naming the provider. The four symptoms above map 1:1 to the three-layer rule being broken or the upstream resolver bug (see `references/upstream-resolver-bug.md`).

If the symptom is something else — model quality, latency, MCP errors, browser tool errors — this skill is not the right one. Bail and use general agent debugging.

### Step 2 — Run the healthcheck (read-only, fast)

```bash
~/.hermes/hermes-agent/venv/bin/python ~/.hermes/scripts/hermes-config-healthcheck.py
```

Output ends with one of:
- `✅ All 3 config layers in correct state.` — drift is not the problem. The user is hitting a different bug. Stop here.
- `❌ DRIFT DETECTED (N issues):` with a list — continue to step 3.
- `❌ DRIFT DETECTED` with the `[resolver-bug]` finding specifically — the config layers are correct but the upstream bug is flipping `active_provider` on a timer. Skip step 3, go straight to step 4 (the healthcheck cron will repair it; if the user wants the root cause gone, file the bug against Hermes — do NOT patch from the Mavis side).

**Why:** the healthcheck is read-only and runs in <2s. It distinguishes "config actually wrong" from "config correct but resolver bug flipping it back". Without this step, you risk running rehydrate for a problem rehydrate can't fix.

### Step 3 — Rehydrate (write, takes ~6s)

```bash
~/.hermes/scripts/hermes-rehydrate.sh
```

This is the only sanctioned repair. It:
1. Backs up `config.yaml`, `auth.json`, `.env` to `<file>.rehydrate-bak.<TS>`.
2. Writes the correct `model:` block via `hermes config set` (uses atomic_yaml_write, the same path the auth flow uses).
3. Atomically fixes `.env` `MINIMAX_*` keys.
4. Atomically flips `auth.json` `active_provider`.
5. Restarts the gateway.
6. Re-runs the healthcheck to confirm.

Idempotent. Safe to run while the gateway is up (it restarts itself as part of the script).

**Why this script and not direct edits:**
- `hermes config set model.provider X` only writes layer 1. It does not touch `auth.json`. This is the bug shape the user is hitting.
- Direct edits via `write_file` are refused by Hermes's tool guard with "Refusing to write to Hermes config file" — so Mavis can only fix this via the script.
- The rehydrate script exists precisely because the three layers are independent and need to be repaired together.

### Step 4 — Verify the cron is alive

The healthcheck is only useful if it actually runs. Verify the launchd entry is loaded:

```bash
launchctl print gui/501/ai.hermes.config-healthcheck 2>&1 | head -3
# Expected: "active count = 1" or "runs = N, last exit code = 0"
# Bad: "Could not find service" or "state = not running"
```

If bad, bootstrap it once:

```bash
launchctl bootstrap gui/501 ~/Library/LaunchAgents/ai.hermes.config-healthcheck.plist
```

A plist in `~/Library/LaunchAgents/` is **inert until bootstrapped**. Placing the file does not auto-load. This is a one-time fix; launchd remembers the load.

**Why this is in the procedure:** prior sessions have deployed the healthcheck plist and assumed it was running. It wasn't, and the next day the drift was back. Verify disk state (`launchctl print`), not the prior session's claim.

### Step 5 — If the resolver-bug check fires repeatedly, escalate

The `auxiliary_client.py:3888` upstream bug silently flips `active_provider` to `nous` every ~60s. The rehydrate fixes the immediate state, but the cron will keep running. The 5-min cadence means the user sees a broken Hermes roughly 1 in 5 times they start a chat.

**Do NOT patch `auxiliary_client.py` from this side.** It's Hermes's code, Hermes's PR review. Instead:

1. File an audit card on kanban `t_96382d79` with the file:line, the 5-line fix shape, and the test convention (`tests/hermes_cli/test_auth_xai_oauth_provider.py`).
2. Tell the user the proper fix is upstream; the healthcheck + rehydrate is a band-aid.
3. If the user wants the band-aid tightened (e.g., shorten `StartInterval` from 300 to 60), confirm before editing the plist.

## Output contract

When this skill runs successfully, the user has:
- A confirmed diagnosis (3 layers in sync, or resolver bug).
- A working repair (`rehydrate.sh` re-ran, gateway back up, healthcheck green).
- The cron verified alive so the next drift is auto-caught.

When you report back, state:
- Which layers were drifted (config.yaml / .env / auth.json / resolver bug).
- The output of the final healthcheck (verbatim, the `✅` line).
- The PID of the relaunched gateway (`pgrep -f hermes-gateway` or `cat ~/.hermes/gateway.pid`).

Do not include redacted key values in the report. Do include `last_status` and `last_error_code` from the credential pool — those are diagnostic.

## Failure handling

| Symptom | Cause | Fix |
|---|---|---|
| `rehydrate.sh` fails with `set -euo pipefail` early exit | `hermes-agent/venv/bin/python` missing or broken | `cd ~/.hermes/hermes-agent && uv sync` (or `python -m venv venv && pip install -e .`) |
| Healthcheck keeps reporting `nvidia/nemotron` in forbidden-substrings check | The healthcheck was edited to look for the wrong target | Edit `EXPECTED["forbidden_substrings"]` in `~/.hermes/scripts/hermes-config-healthcheck.py` |
| Cron keeps dying | plist has bad syntax or wrong `ProgramArguments` | `plutil -lint ~/Library/LaunchAgents/ai.hermes.config-healthcheck.plist` first, then re-bootstrap |
| Rehydrate passes healthcheck but new chat still hits wrong provider | Stale gateway process didn't restart, OR a different gateway instance is bound | `pgrep -f hermes-gateway` — kill all but the one in `gateway.pid` |
| User wants a different provider than the `EXPECTED` dict hardcodes | The healthcheck was authored for one target; change the source of truth | Edit `EXPECTED` in `hermes-config-healthcheck.py` (top of file) and the rehydrate script (Layers 1+3 blocks) together — they MUST agree |

## Examples

### Example 1: User says "hermes is broken, I'm on the wrong model"

1. Run the inputs-to-collect block.
2. Run healthcheck. Output: `❌ DRIFT DETECTED (3 issues): [config.yaml] model.provider='nous' ... [auth.json] active_provider='nous' ...`.
3. Run `rehydrate.sh`. Wait ~6s.
4. Verify launchd (Step 4) — show user it's running every 5 min.
5. Report: "3 layers were drifted; rehydrate fixed it. Cron `ai.hermes.config-healthcheck` is loaded and running. If it drifts again in the next 5 min, expect the resolver-bug class — that's an upstream Hermes code issue, not a config problem. Filed under `t_96382d79`."

### Example 2: User says "fix Hermes"

This is too vague. Ask one clarifying question: "Is Hermes routing to the wrong model, or is a chat session failing with an error?" If they say "wrong model" or "I keep getting a free NVIDIA model", use this skill. If they say "it's slow" or "MCP doesn't load", do not — different problem.

### Example 3: User says "Mavis says the audit and the disk say different things"

This is the recap-vs-disk pattern (see `fleet-trust-patterns.md` §3). Run the healthcheck, get the disk truth, ignore whatever the prior session claimed. Then proceed with Step 3 if needed.
