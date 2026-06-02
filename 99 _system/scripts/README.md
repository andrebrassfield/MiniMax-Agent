# update_state_of_mavis.py

End-of-session regenerator for `state-of-mavis.md`. v0.1.0.

## What it does

The script is the deterministic I/O layer for end-of-session state regen. The M3 synthesis layer (called via the `mavis` LLM client when wired) takes the harvest output and writes the new `state-of-mavis.md`. The split is the Esalen discipline: thin Python, M3 does the prose.

- **Harvesters** (git log, file counts, daily note, friction log extract) — deterministic, no LLM
- **can_i() audit** (rule-based mirror of SOUL.md § Autonomy Boundary Table) — deterministic
- **Prompt assembler** — builds the M3 synthesis input
- **--apply** — writes the synthesized content from stdin back to `state-of-mavis.md` after a re-audit

## Usage

```bash
# Harvest raw data
python3 update_state_of_mavis.py --harvest

# Audit session actions against the SOUL rule set
python3 update_state_of_mavis.py --audit

# Build the M3 synthesis prompt from harvest + audit
python3 update_state_of_mavis.py --assemble-prompt

# Dry run (harvest + audit + prompt, no write)
python3 update_state_of_mavis.py --dry-run

# Apply: read M3's synthesized output from stdin, re-audit, write
python3 update_state_of_mavis.py --apply < synthesized.md

# Override the harvest window
python3 update_state_of_mavis.py --harvest --since <commit-hash>

# Print version
python3 update_state_of_mavis.py --version
```

## The Friction 10 ruling (locked 2026-06-02)

**Mandated standard operating procedure: use `update_state_of_mavis.py --apply` for state regeneration.**

The `--apply` path is the only sanctioned routine for writing `state-of-mavis.md` after a synthesis. The full discipline is:

1. Run `--harvest` to get the deterministic data
2. Run `--audit` to confirm session actions were within boundary
3. Hand the M3 input (assembled via `--assemble-prompt`) to M3
4. Pipe M3's synthesized output through `update_state_of_mavis.py --apply`
5. The script re-audits the new content against the rule set, then writes

The `Write` tool **may not be used** to write `state-of-mavis.md` for routine regens. The only legitimate use of the Write tool on this file is the very first creation of the file in a fresh vault, when `--apply` has no prior commit to diff against.

### Why

- The `--apply` path enforces a re-audit before the write, so any rule violation in M3's synthesis is caught before it lands in the file
- The pipeline is auditable: every state-of-mavis commit is preceded by a logged harvest + audit + synthesis, all reproducible from the script
- The discipline matches the SOUL red-line for credential/structural changes: cross the boundary through the script, not around it

### When the Write tool is acceptable

- First creation of `state-of-mavis.md` in a fresh vault (no prior content to diff against)
- Recovery from a corrupted state-of-mavis (e.g., broken wikilinks that the script's parser chokes on) — log the recovery in the Friction Log first
- Anything else → use `--apply`

## Related

- `99 _system/ESALEN-NOT-FOXCONN.md` — the operating posture this script implements
- `state-of-mavis.md` § Friction Log — Friction 10 is the origin of the `--apply` mandate
- `SOUL.md` § Autonomy Boundary Table — the rule set `can_i_rule_based()` mirrors
- `learnings.md` — capture points when the script's behavior surprises you
