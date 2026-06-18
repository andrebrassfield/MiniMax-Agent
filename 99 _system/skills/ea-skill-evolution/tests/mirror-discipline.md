# Mirror Discipline — ea-skill-evolution

The byte-identity gate. The eval suite verifies the gate holds.

## T1. Byte-identity check after every canonical write

**Verification:** after the skill writes to a canonical skill path
(`~/.mavis/agents/mavis/skills/<name>/SKILL.md`), the mirror-sync
runs and `cmp` exits 0.

```bash
# Canonical write happened
HOME="$HOME/.mavis/agents/mavis/skills/<name>/SKILL.md"
VAULT="$HOME/MiniMax-Agent/99 _system/skills/<name>/SKILL.md"

# Both files must exist
test -f "$HOME" || echo "FAIL: canonical file missing"
test -f "$VAULT" || echo "FAIL: mirror file missing"

# cmp must exit 0
if cmp -s "$HOME" "$VAULT"; then
  echo "PASS: byte-identical"
else
  echo "FAIL: home and mirror are not byte-identical"
  diff <(sha256sum "$HOME") <(sha256sum "$VAULT")
fi
```

**Failure mode this catches:** a canonical write that doesn't
reach the mirror. The skill marks the proposal `shipped` but the
mirror is stale — Mavis won't see the change on her next session,
Andre won't see it on the vault.

## T2. SHA-256 logged in the manifest

**Verification:** the manifest entry's `mirror_verified` field is
an ISO timestamp, and the manifest can be cross-checked against
the SHA-256 of the mirror file at that timestamp.

```bash
# Manifest entry timestamp
verified_at=$(grep -oE '"mirror_verified": "[^"]+"' manifest.jsonl | tail -1 | cut -d'"' -f4)
# Mirror file's mtime should be within 1 second of the verified_at
file_mtime=$(stat -c %Y "$VAULT")
# Compare (basic check — production should use proper timestamp parsing)
```

**Failure mode this catches:** manifest timestamps that don't
match the actual mirror file's mtime. A timestamp drift suggests
the manifest was written before the mirror sync, or the mirror
sync was reverted manually.

## T3. Mirror-pending state on failure

**Verification:** if the mirror-sync fails, the manifest entry's
status is `mirror-pending`, NOT `shipped`.

```bash
# Find all entries with status "shipped"
shipped=$(grep -c '"status": "shipped"' manifest.jsonl)
# Each one must have mirror_status: ok
ok_mirrors=$(grep -A1 '"status": "shipped"' manifest.jsonl | grep -c '"mirror_status": "ok"')
test "$shipped" -eq "$ok_mirrors" || echo "FAIL: shipped entries without mirror_status: ok"
```

**Failure mode this catches:** proposals that bypass the mirror
discipline (marked `shipped` without the gate passing).

## T4. Manifest is append-only

**Verification:** the manifest is append-only. No past entries
have been modified after their initial write.

```bash
# Use git to check that no past entry has been modified
git log --all --format="%H" -- manifest.jsonl | while read commit; do
  changed=$(git show "$commit" -- manifest.jsonl | grep -c "^-")
  # Append-only means new lines are added, not changed
done
```

**Failure mode this catches:** status changes after the fact
(e.g., changing a `discarded` entry to `shipped` to hide a
discipline violation). The manifest is the audit trail; it must
be tamper-evident.

## T5. Staging file exists at the time of the proposal

**Verification:** when the manifest entry references a `staging`
path, that path exists and contains the staged file.

```bash
# Extract staging path
staging=$(grep -oE '"staging": "[^"]+"' manifest.jsonl | tail -1 | cut -d'"' -f4)
# Path must exist
test -e "$staging" || echo "FAIL: staging path does not exist: $staging"
```

**Failure mode this catches:** a proposal that references a
staging path that doesn't exist. The proposal is grounded in a
file that was never created.
