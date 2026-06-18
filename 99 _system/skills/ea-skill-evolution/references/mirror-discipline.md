# Mirror Discipline — ea-skill-evolution

The sync gate: every canonical write to
`~/.mavis/agents/mavis/skills/<name>/SKILL.md` MUST be mirrored to
`~/MiniMax-Agent/99 _system/skills/<name>/SKILL.md` AND verified
byte-identical via `cmp` before the proposal can reach
`status: shipped`.

## Why the gate exists

The agent home (`~/.mavis/agents/mavis/`) is what Mavis reads at
session start. The vault mirror (`99 _system/skills/`) is what
Andre sees on the vault surface. A skill that's canonical but
unmirrored is a **partial mutation**: Mavis doesn't see it (she
reads the mirror), Andre doesn't see it (he sees the mirror), and
the corpus is in a silent-drift state where future-Mavis re-
litigates the change as if it never happened.

## The atomic-mirror command

```bash
# 1. Write to canonical (atomic)
TMP_HOME="$(mktemp -t mirror-sync-home-XXXXXX)"
cat > "$TMP_HOME"
mv -f "$TMP_HOME" "$HOME_PATH"  # $HOME_PATH = ~/.mavis/agents/mavis/skills/<name>/SKILL.md

# 2. Write to mirror (atomic)
TMP_VAULT="$(mktemp -t mirror-sync-vault-XXXXXX)"
cp "$HOME_PATH" "$TMP_VAULT"
mv -f "$TMP_VAULT" "$VAULT_PATH"  # $VAULT_PATH = ~/MiniMax-Agent/99 _system/skills/<name>/SKILL.md

# 3. Verify byte-identity (the gate)
if cmp -s "$HOME_PATH" "$VAULT_PATH"; then
  echo "MIRROR OK: $(shasum -a 256 "$HOME_PATH" | awk '{print $1}')"
  exit 0
else
  echo "MIRROR FAIL: home and mirror are not byte-identical"
  exit 1
fi
```

## State transitions

| State | Trigger | Next state |
|---|---|---|
| `pending-review` | Mavis hasn't decided yet | `shipped` (approve) / `discarded` (reject) |
| `shipped` | Mavis approved + mirror verified | (terminal — no further transitions) |
| `mirror-pending` | Canonical write succeeded but mirror write or `cmp` failed | Mavis runs the mirror command manually; on success → `shipped`; on continued failure → keep held |
| `discarded` | Mavis rejected OR audit failed | (terminal — kept in manifest as audit trail) |
| `memory-deferred` | Memory candidate awaiting `mavis memory append` | (Mavis runs the append; on success → `shipped` with the memory entry) |

## The mirror script

`~/.mavis/agents/mavis/skills/ea-skill-evolution/scripts/mirror-sync.sh`
is the wrapper that wraps the 3 commands above. The script enforces
the byte-identity gate. Do NOT hand-roll the write; use the
wrapper. The gate is the wrapper, not the commands.

## What happens if the mirror fails

The skill does NOT mark the proposal `shipped`. It marks it
`mirror-pending` and surfaces to Mavis with:
- The exact `cmp` error
- The home's SHA-256
- The mirror's SHA-256 (if the mirror file exists at all)

Mavis can then:
- Re-run the mirror-sync.sh command manually
- Check filesystem permissions on the vault mirror
- If persistent, escalate to Andre (the mirror infrastructure is
  broken, that's a system-level issue)

## What this is NOT

- Not a permission to skip the mirror. The mirror is mandatory.
- Not a manual step. The script handles it.
- Not optional for "small changes." A 1-line edit still needs the
  mirror sync.
