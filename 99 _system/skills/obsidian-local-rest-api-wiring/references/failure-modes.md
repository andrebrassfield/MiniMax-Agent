# Failure modes — obsidian-local-rest-api-wiring

Diagnostic catalog for when the wiring doesn't go green. Each entry: symptom,
root cause, recovery, prevention. Cross-referenced from `SKILL.md`.

## F1 — `mavis mcp tools obsidian` returns 40101 with valid bearer

**Symptom:**
```json
{"errorCode": 40101, "message": "Authorization required.  Find your API Key..."}
```
even when the bearer in `Authorization: Bearer <token>` exactly matches the
apiKey stored in `data.json`.

**Root cause:** In-memory `settings.apiKey` diverged from `data.json['apiKey']`.
The plugin loads settings into memory at `onload()` and does NOT re-read on
every disk write. If `data.json` was modified externally (token rotation by
filesystem edit, vault-sync overwriting it, etc.), the running plugin still
compares incoming requests against the in-memory copy.

**Diagnostic:**
```sh
# Verify data.json has the token you expect
python3 -c "import json; print(json.load(open('/path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json'))['apiKey'])"

# Verify Obsidian process start time vs data.json mtime
ps -o lstart= -p $(pgrep -x Obsidian | head -1)
stat -f '%Sm' /path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json
```
If `data.json` mtime is AFTER Obsidian started → divergence confirmed.

**Recovery (in order of disruption):**
1. **Reload app** — Cmd+P → "Reload app without saving". Clean. ~10min for
   the HTTP server to bind after restart. Don't retry inside the first
   few minutes.
2. **Force settings re-sync** — Settings → Community Plugins → Installed
   plugins → Local REST API → toggle off, then on. Or click "Generate new
   key" and share the new token.

**Prevention:** rotate tokens via the plugin UI, not via filesystem edits.
If a tool must touch `data.json`, schedule an Obsidian reload in the same
operation.

## F2 — `fetch failed` / `ERR_TLS_CERT_ALTNAME_INVALID` / self-signed cert rejection

**Symptom:** `mavis mcp sync obsidian` returns `SYNC_ERROR`, `mavis mcp tools
obsidian` returns `Error: Failed to connect to MCP server "obsidian": fetch
failed` or `Streamable HTTP error: Error POSTing to endpoint`.

**Root cause:** Node's `fetch` (`node:undici`) uses Node's CA store, NOT
macOS Keychain. `security add-trusted-cert` only updates the system store;
it doesn't propagate to Node.

**Diagnostic:**
```sh
# Is NODE_EXTRA_CA_CERTS set in the current shell?
echo "$NODE_EXTRA_CA_CERTS"

# Does the file exist and is it readable?
ls -la "$NODE_EXTRA_CA_CERTS"

# Does Node accept the cert?
NODE_EXTRA_CA_CERTS="$HOME/.mavis/certs/obsidian-local-rest-api.crt" \
  node -e "fetch('https://127.0.0.1:27124/').then(r => r.json()).then(console.log).catch(e => console.error(e.message))"
```
If the cert file is missing or unset, Node rejects. If the cert is expired,
Node rejects with `CERT_HAS_EXPIRED`.

**Recovery:**
```sh
# Re-extract cert (plugin regenerates when expired)
python3 -c "import json; print(json.load(open('/path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json'))['crypto']['cert'], end='')" \
  > ~/.mavis/certs/obsidian-local-rest-api.crt

# Re-trust
security add-trusted-cert -d -r trustRoot \
  -k ~/Library/Keychains/login.keychain-db \
  ~/.mavis/certs/obsidian-local-rest-api.crt

# Source the env var
source ~/.zshrc
```

**Fallback:** if cert trust cannot be wired, switch the MCP URL to
`http://127.0.0.1:27123/mcp/`. The plugin's HTTP endpoint is gated behind a
plugin settings toggle (`Enable HTTP server`); if disabled, enable it.
HTTP is acceptable for localhost-only access but loses on-the-wire encryption
on the loopback interface — typically fine since traffic never leaves the
machine, but HTTPS is the right long-term default.

**Prevention:** run `security find-certificate -c "Obsidian Local REST API"`
periodically; cert is valid 1 year from issue. Calendar reminder at month 11.

## F3 — Plugin loads but HTTP server never starts

**Symptom:** `lsof -nP -iTCP:27123 -iTCP:27124 -sTCP:LISTEN` returns empty
even minutes after Obsidian is up. Obsidian is running; the plugin is in the
enabled list.

**Root cause:** The plugin's `onload()` threw. Obsidian marks the plugin
failed and skips its initialization, but keeps it in the enabled list. The
status bar shows a yellow/red "X plugins failed to load" badge.

**Diagnostic:**
- Look at Obsidian status bar (bottom of window) → yellow/red badge
- Settings → Community Plugins → Installed plugins → Local REST API →
  red error banner with the actual exception

**Common onload errors:**
- `Cannot read property 'X' of undefined` → `data.json` was edited externally
  with a malformed shape. Fix: delete `data.json`, reopen Obsidian (plugin
  regenerates fresh).
- `Port 27124 already in use` → leftover socket. Fix: `lsof -nP -iTCP:27124`
  to find the holder; usually a previous Obsidian instance. `kill -9` it.
- `EACCES: permission denied, open '...data.json'` → `data.json` permissions
  wrong (typically mode 600 required, sometimes 644). Fix: `chmod 644`.

**Recovery (nuclear option):**
```sh
# Close Obsidian first
killall Obsidian
rm /path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json
open -a Obsidian
# Wait ~30s for plugin to regenerate cert + key
# Settings → Community Plugins → Local REST API → copy new API key
# Update env file + MCP config + Keychain with the new token
```

**Prevention:** never edit plugin `data.json` files manually. If you must
(for debugging), take a backup first and plan a reload.

## F4 — `vault_read` returns 404 for a known-existing file

**Symptom:** A file is in the vault (visible in Obsidian file explorer, has
entries from `vault_list`), but `vault_read '{"path": "X.md"}'` returns 404.

**Root cause:** URL encoding. The path uses URL-encoded slashes (%2F) but
some clients send raw slashes. Spaces must be `%20`.

**Diagnostic:**
```sh
# What does vault_list return for the path?
mavis mcp call obsidian vault_list '{"path": "01 Daily"}'
# Should return files including spaces in their names

# What does vault_read do with the right encoding?
mavis mcp call obsidian vault_read '{"path": "01 Daily/2026-06-17.md"}'
# vs
mavis mcp call obsidian vault_read '{"path": "01%20Daily/2026-06-17.md"}'
```

**Recovery:** use URL-encoded paths (`%20` for space, `%2F` is optional).
The MCP layer handles most encoding automatically when you pass JSON args.

**Prevention:** when in doubt, `vault_list` the parent directory first to
confirm the exact filename as the plugin sees it.

## F5 — Round-trip works once, then hangs on subsequent calls

**Symptom:** First `mavis mcp call` returns 200; second call hangs forever
or returns a connection error.

**Root cause:** mavis MCP's Streamable HTTP transport may not be closing
sessions properly, or the plugin's session-id handling expects an explicit
`Mcp-Session-Id` header. Less common with v4.1.1+ of the plugin.

**Diagnostic:**
```sh
# Check mavis daemon logs
ls -lt ~/.mavis/logs/ | head -5
tail -50 ~/.mavis/logs/mcp-obsidian.log 2>/dev/null

# Test with explicit fresh connection each time
mavis mcp call obsidian vault_list '{"path": ""}'  # should always work
```

**Recovery:** `mavis mcp sync obsidian` to refresh the connection state.
If persistent, disable + re-enable the MCP server:
```sh
mavis mcp disable obsidian
mavis mcp add obsidian '<config>'   # same config
mavis mcp sync obsidian
```

**Prevention:** none known. Upgrade to plugin v4.1.3+ (latest as of 2026-06)
if you hit this often.
