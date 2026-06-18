# Commands — obsidian-local-rest-api-wiring

Copy-pasteable command blocks per step. Source of truth is `../SKILL.md` —
this file is the reference for running the procedure by hand.

## Step 2 — Store token in Keychain

```sh
TOKEN='<paste-token-from-chat-or-extract-from-data.json>'
security add-generic-password -a 'mavis-mcp-obsidian' -s 'obsidian-local-rest-api' \
  -w "$TOKEN" -U 2>/dev/null \
  || security delete-generic-password -a 'mavis-mcp-obsidian' \
       -s 'obsidian-local-rest-api' 2>/dev/null \
   && security add-generic-password -a 'mavis-mcp-obsidian' \
        -s 'obsidian-local-rest-api' -w "$TOKEN"
```

Verify:
```sh
security find-generic-password -a 'mavis-mcp-obsidian' -s 'obsidian-local-rest-api' -w
```

## Step 3 — Mirror to env file

```sh
mkdir -p ~/.mavis/secrets && chmod 700 ~/.mavis/secrets
umask 077
printf 'OBSIDIAN_TOKEN=%s\n' "$TOKEN" > ~/.mavis/secrets/obsidian.env
chmod 600 ~/.mavis/secrets/obsidian.env
ls -la ~/.mavis/secrets/obsidian.env  # expect: -rw------- 1 user staff ...
```

## Step 4 — Extract + trust cert

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

Verify:
```sh
openssl x509 -in ~/.mavis/certs/obsidian-local-rest-api.crt -noout -subject -dates
security find-certificate -c "Obsidian Local REST API"
```

## Step 5 — Export NODE_EXTRA_CA_CERTS

```sh
ZSHRC=~/.zshrc
touch "$ZSHRC"
if ! grep -q "NODE_EXTRA_CA_CERTS" "$ZSHRC"; then
  printf '\n# Mavis — trust self-signed Obsidian Local REST API cert\nexport NODE_EXTRA_CA_CERTS="$HOME/.mavis/certs/obsidian-local-rest-api.crt"\n' \
    >> "$ZSHRC"
fi
grep "NODE_EXTRA_CA_CERTS" "$ZSHRC"
```

Activate in current shell:
```sh
source ~/.zshrc
echo "$NODE_EXTRA_CA_CERTS"  # expect: /Users/<user>/.mavis/certs/obsidian-local-rest-api.crt
```

## Step 6 — Wire mavis MCP

```sh
mavis mcp add obsidian "$(cat <<JSON
{
  "url": "https://127.0.0.1:27124/mcp/",
  "type": "streamable-http",
  "headers": { "Authorization": "Bearer $TOKEN" },
  "enabled": true,
  "configured": true,
  "description": "Obsidian vault via Local REST API MCP endpoint (HTTPS, Mavis Phase 2 — cert trusted)"
}
JSON
)"
```

Verify:
```sh
mavis mcp get obsidian
```

## Step 7 — Sync + round-trip

```sh
mavis mcp sync obsidian
# expect: "MCP sync completed (SYNC_DONE) — 5/5 done, 0 failed."

mavis mcp tools obsidian
# expect: 16 tools including vault_list, vault_read, vault_write

mavis mcp call obsidian vault_list '{"path": ""}'
# expect: vault root directory listing (folders + files)

mavis mcp call obsidian vault_read '{"path": "MAVIS.md"}'
# expect: frontmatter with type=ai-context, content ~7500 chars, links array

mavis mcp call obsidian tag_list '{}'
# expect: tag index with counts
```

## Diagnostic one-liners

```sh
# Is the plugin's HTTP server listening?
lsof -nP -iTCP:27123 -iTCP:27124 -sTCP:LISTEN

# What's in the plugin's data.json?
python3 -m json.tool /path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json | head -20

# When did Obsidian start vs when was data.json last written?
ps -o lstart= -p $(pgrep -x Obsidian | head -1)
stat -f '%Sm' /path/to/vault/.obsidian/plugins/obsidian-local-rest-api/data.json

# Is the cert still valid?
openssl x509 -in ~/.mavis/certs/obsidian-local-rest-api.crt -noout -dates

# Direct curl probe (auth-exempt / endpoint returns manifest)
curl -sk https://127.0.0.1:27124/

# Auth check (use the token from Keychain)
TOK=$(security find-generic-password -a 'mavis-mcp-obsidian' -s 'obsidian-local-rest-api' -w)
curl -sk -H "Authorization: Bearer $TOK" https://127.0.0.1:27124/ | python3 -c "import json,sys; print('authenticated:', json.load(sys.stdin)['authenticated'])"
```
