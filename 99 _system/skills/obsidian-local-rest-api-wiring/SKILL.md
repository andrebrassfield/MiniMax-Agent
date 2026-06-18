---
name: obsidian-local-rest-api-wiring
description: |
  Codifies the end-to-end wiring of an Obsidian vault via Adam Coddington's
  "Local REST API with MCP" community plugin into mavis as a queryable MCP
  server. Procedure: (1) accept the bearer token from chat OR extract it from
  the plugin's `data.json` (do not echo back); (2) store in macOS Keychain via
  `security add-generic-password` AND mirror to a mode-600 file at
  `~/.mavis/secrets/obsidian.env`; (3) extract the self-signed HTTPS cert from
  `data.json`, write to `~/.mavis/certs/obsidian-local-rest-api.crt`, and
  trust in macOS Keychain via `security add-trusted-cert -d -r trustRoot`;
  (4) export `NODE_EXTRA_CA_CERTS` to `~/.zshrc` (idempotent) so Node's
  `fetch` accepts the cert without per-request `rejectUnauthorized: false`;
  (5) wire mavis MCP server `obsidian` via `mavis mcp add` with the HTTPS
  URL + bearer header; (6) `mavis mcp sync obsidian` then run a round-trip
  (`vault_list` → `vault_read` on a known file → `tag_list`) to confirm
  tools surface and auth is live end-to-end. Use when Andre says "wire up
  Obsidian vault", "connect mavis to my vault", "Phase 2 setup", or shares
  the Local REST API screenshots/token/config. Auto-trigger when a chat
  references the plugin by name, the `/mcp/` endpoint, or bearer auth against
  `127.0.0.1:27123`/`27124`. Do NOT load for vault rendering/presentation
  (that's the separate `03 Projects/Obsidian-Glass/` project), for non-
  Obsidian MCP wiring (different cert/transport patterns — write a new
  skill), for peer-agent filesystem territory (Mavis has absolute separation
  from Hermes/OpenClaw/gbrain per the 2026-06-16 rule), or when the user
  hasn't actually enabled the Local REST API plugin in Obsidian yet.
---

# obsidian-local-rest-api-wiring

End-to-end wiring of the Obsidian "Local REST API with MCP" plugin into mavis
as a tool-shaped MCP server. The shape: vault → plugin's built-in `/mcp/`
(Streamable HTTP) → bearer-authenticated reverse-read → mavis MCP client →
16 vault tools (`vault_list`, `vault_read`, `vault_write`, `vault_append`,
`vault_patch`, `vault_delete`, `vault_move`, `vault_get_document_map`,
`active_file_get_path`, `periodic_note_get_path`, `search_query`,
`search_simple`, `tag_list`, `command_list`, `command_execute`, `open_file`).

The shape generalizes to "wire any HTTPS-with-self-signed-cert + bearer-auth
local MCP server into mavis" — the Obsidian instance is the prototype. Reuse
the procedure; swap the cert/URL/token fields for other local services.

## When to run

**Trigger phrases (Andre-side):**
- "wire up Obsidian / vault / Local REST API"
- "connect mavis to my vault" / "Phase 2 setup"
- Shares the Local REST API settings screenshot or bearer token in chat
- Pastes the canonical Claude Code MCP config block for Obsidian
- "set up the MCP server for [plugin name]"
- "why is auth failing on the obsidian MCP"

**Auto-trigger conditions:**
- Chat references `127.0.0.1:27123` or `:27124`
- Chat references the `/mcp/` endpoint and a bearer token
- Existing Mavis work surfaces need to read/write vault files but only have
  the Local REST API plugin (not the obsidiantools / Dataview JS layer)
- A failed `mavis mcp tools obsidian` returns 401 or cert rejection

**Do NOT load for:**
- Vault rendering / presentation layer (that's the `Obsidian-Glass` project
  in `03 Projects/`, separate scope — Glass Server is for human reading)
- Non-Obsidian MCP wiring (different cert formats, transport types, auth
  patterns — write a fresh skill, do not generalize blindly)
- Peer-agent filesystem territory (Hermes, OpenClaw, gbrain, hermes-evolution
  — Mavis has absolute separation from those per the 2026-06-16 rule;
  per `cross-team-discipline.md`, peer audit = state findings, don't fix)
- When the user hasn't actually enabled the Local REST API plugin in Obsidian
  yet (do that step first via UI, then come back to this skill)

## Preconditions

Verify on disk BEFORE doing anything:

```sh
test -d "/path/to/vault/.obsidian/plugins/obsidian-local-rest-api" || echo "FAIL: plugin not installed"
grep -q "obsidian-local-rest-api" "/path/to/vault/.obsidian/community-plugins.json" || echo "FAIL: plugin not enabled"
lsof -nP -iTCP:27123 -sTCP:LISTEN 2>/dev/null | grep -q LISTEN || echo "WARN: HTTP server not listening (may need plugin restart)"
```

If any FAIL, stop. Tell the user. The skill assumes the plugin is installed,
enabled, and currently serving. If the plugin needs a restart, see
`failure-modes.md` in references.

## Procedure (atomic steps)

**Step 1 — Capture the bearer token. NEVER echo it back in chat or files.**

Source paths, in order of preference:
1. From `~/.mavis/secrets/obsidian.env` (already stored) → source it
2. From macOS Keychain → `security find-generic-password -a 'mavis-mcp-obsidian' -s 'obsidian-local-rest-api' -w`
3. From chat input (Andre pastes it) → use immediately, never echo
4. From plugin's `data.json` → `python3 -c "import json; print(json.load(open('.../data.json'))['apiKey'])"`

If from chat, the user is in **interactive-prompts-OK mode** per MEMORY.md
"user-mode" → they prefer OS password prompts (Keychain Access / `security`
CLI) over typing shell commands. Run the secure-storage steps directly so
they only have to type a password when the macOS prompt pops, not shell.

**Step 2 — Store token in macOS Keychain.**

```sh
security add-generic-password -a 'mavis-mcp-obsidian' -s 'obsidian-local-rest-api' \
  -w "$TOKEN" -U 2>/dev/null \
  || security delete-generic-password -a 'mavis-mcp-obsidian' \
       -s 'obsidian-local-rest-api' 2>/dev/null \
   && security add-generic-password -a 'mavis-mcp-obsidian' \
        -s 'obsidian-local-rest-api' -w "$TOKEN"
```

The `-U` updates if exists; fallback deletes + re-adds. `2>/dev/null`
suppresses the "already exists" error so the second branch handles it.

**Step 3 — Mirror to mode-600 env file.**

```sh
mkdir -p ~/.mavis/secrets && chmod 700 ~/.mavis/secrets
umask 077
printf 'OBSIDIAN_TOKEN=%s\n' "$TOKEN" > ~/.mavis/secrets/obsidian.env
chmod 600 ~/.mavis/secrets/obsidian.env
```

Three on-disk locations now: Keychain (encrypted), env file (mode-600),
MCP config JSON (one literal occurrence). None cloud-synced. Token is also
in chat history — treat as compromised for any future operational concern;
rotate if threat model ever includes a chat-log leak.

**Step 4 — Extract self-signed cert and trust it.**

```sh
mkdir -p ~/.mavis/certs && chmod 700 ~/.mavis/certs
python3 -c "
import json
d = json.load(open('/path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json'))
print(d['crypto']['cert'], end='')
" > ~/.mavis/certs/obsidian-local-rest-api.crt
chmod 644 ~/.mavis/certs/obsidian-local-rest-api.crt

security add-trusted-cert -d -r trustRoot \
  -k ~/Library/Keychains/login.keychain-db \
  ~/.mavis/certs/obsidian-local-rest-api.crt
```

`-d` adds to admin certs; `-r trustRoot` sets the trust purpose. The
login keychain is the right scope for per-user dev tooling.

**Step 5 — Export `NODE_EXTRA_CA_CERTS` in `~/.zshrc` (idempotent).**

```sh
ZSHRC=~/.zshrc
touch "$ZSHRC"
if ! grep -q "NODE_EXTRA_CA_CERTS" "$ZSHRC"; then
  printf '\n# Mavis — trust self-signed Obsidian Local REST API cert\nexport NODE_EXTRA_CA_CERTS="$HOME/.mavis/certs/obsidian-local-rest-api.crt"\n' \
    >> "$ZSHRC"
fi
```

Tell the user to open a new Terminal tab or `source ~/.zshrc` so the
export takes effect. macOS Keychain trust alone is NOT enough — Node
uses its own CA store (`node:tls`), not Security.framework.

**Step 6 — Wire mavis MCP server.**

```sh
mavis mcp add obsidian "$(cat <<'JSON'
{
  "url": "https://127.0.0.1:27124/mcp/",
  "type": "streamable-http",
  "headers": { "Authorization": "Bearer <TOKEN>" },
  "enabled": true,
  "configured": true,
  "description": "Obsidian vault via Local REST API MCP endpoint (HTTPS, Mavis Phase 2 — cert trusted)"
}
JSON
)"
```

The `streamable-http` type matches the mavis convention (verify with
`mavis mcp get cu` for the builtin reference). HTTP `27123` is a fallback
when cert trust is not yet wired — but HTTPS is the right default once
NODE_EXTRA_CA_CERTS is set.

**Step 7 — Sync + verify round-trip.**

```sh
mavis mcp sync obsidian                  # expect: SYNC_DONE, 5/5 done
mavis mcp tools obsidian                 # expect: 16 tools listed
mavis mcp call obsidian vault_list '{"path": ""}'  # expect: vault root
mavis mcp call obsidian vault_read '{"path": "MAVIS.md"}'  # expect: frontmatter + content + links
mavis mcp call obsidian tag_list '{}'    # expect: tag index
```

The `vault_read` on `MAVIS.md` is the canonical verification — it has
known frontmatter (type, purpose, update-cadence, owner) and known content
length (~7.5KB), so any drift is obvious.

## Failure modes

See `references/failure-modes.md` for the full list. Top three:

**F1 — Auth returns 40101 even with valid bearer.**
In-memory `settings.apiKey` diverged from `data.json['apiKey']`. The
plugin loads settings into memory at `onload()` and does NOT re-read
on every disk write. Recovery: app reload (Cmd+P → "Reload app without
saving") OR regenerate the API key in the plugin UI (which forces a
`saveSettings()` + in-memory sync). After reload, the HTTP server can
take ~10 minutes to bind — don't retry inside the first few minutes.

**F2 — `fetch failed` or `ERR_TLS_CERT_ALTNAME_INVALID`.**
Self-signed cert not trusted by Node. Verify `NODE_EXTRA_CA_CERTS` is
set in the current shell (`echo $NODE_EXTRA_CA_CERTS`) and that the
file exists. New shells inherit it from `~/.zshrc`; old ones need
`source ~/.zshrc`.

**F3 — Plugin loads but HTTP server never starts.**
Look at Obsidian status bar — yellow/red "X plugins failed to load"
badge means the plugin threw during `onload()`. Settings → Community
Plugins → Installed plugins → Local REST API → look for the error.
Common: `data.json` was edited externally with a malformed shape, or
the cert/privateKey pair got out of sync. Recovery: close Obsidian,
delete `.obsidian/plugins/obsidian-local-rest-api/data.json`, reopen
Obsidian — the plugin will regenerate fresh cert + key. Update env
file + MCP config + Keychain with the new token.

## Output schema (after a successful run)

1. macOS Keychain: `security find-certificate -c "Obsidian Local REST API"` → 1 result
2. macOS Keychain: `security find-generic-password -a 'mavis-mcp-obsidian' -s 'obsidian-local-rest-api'` → 1 result
3. `~/.mavis/certs/obsidian-local-rest-api.crt` → 1216 bytes, valid 1 year from issue
4. `~/.mavis/secrets/obsidian.env` → mode 600, contains `OBSIDIAN_TOKEN=...`
5. `~/.zshrc` → contains `export NODE_EXTRA_CA_CERTS="$HOME/.mavis/certs/obsidian-local-rest-api.crt"`
6. `mavis mcp ls` → `obsidian` listed, enabled, configured, transport `http`
7. `mavis mcp tools obsidian` → 16 tools
8. Round-trip: `vault_read MAVIS.md` returns frontmatter + ~7.5KB content + links + backlinks

If any of 1–8 fail, do NOT declare success. Trace via `failure-modes.md`.

## Reference index

- `references/failure-modes.md` — full failure-mode catalog with diagnostic commands
- `references/commands.md` — copy-pasteable command blocks per step

## Test discipline

- `tests/round-trip.md` — verifies the full sync → tools → read → write cycle
- `tests/cert-revocation.md` — verifies removal flow (clean uninstall + cert/keychain cleanup)
