# Procedure — client-pov-tracker

The 9-step procedure with bash commands. The SKILL.md only
carries the procedure overview. The actual commands live
here (the deterministic layer).

---

## Step 1: Verify the inputs

```bash
VAULT="/Users/brassfieldventuresllc/MiniMax-Agent"
CLIENTS="$VAULT/03 Projects/Clients"
WHITEPAPER="$VAULT/03 Projects/Mavis EA Design/reports/2026-Q3-SMB-AI-Maturity-Report.md"
PERSONA="$VAULT/03 Projects/X-Content-Engine/agents/persona.md"

# Verify vault + clients dir
[ -d "$CLIENTS" ] || { echo "HALT: 03 Projects/Clients/ does not exist" >&2; exit 1; }

# Verify client dir exists or create
CLIENT_DIR="$CLIENTS/[ClientName]"
if [ ! -d "$CLIENT_DIR" ]; then
  mkdir -p "$CLIENT_DIR"
fi

# Verify whitepaper
[ -f "$WHITEPAPER" ] || { echo "HALT: whitepaper missing at $WHITEPAPER" >&2; exit 1; }

# Verify persona
[ -f "$PERSONA" ] || { echo "HALT: persona missing at $PERSONA" >&2; exit 1; }

# Verify local-audit briefs exist (H1 — empty local-audit halt)
AUDITS=$(find "$VAULT/03 Projects/X-Content-Engine/briefs" -name "local-audit-*.md" 2>/dev/null)
[ -z "$AUDITS" ] && { echo "HALT: no local-audit briefs found. Run local-competitor-auditor first." >&2; exit 1; }
```

## Step 2: Read the local-audit briefs

For each `briefs/local-audit-*.md` that matches the
client's city + niche, extract:

- The per-competitor friction signal checkboxes
  (PRESENT / ABSENT)
- The severity score (1-5) per competitor
- The "What install would close the gap" line
- The cross-competitor top-3 friction patterns

If multiple briefs match (multiple cities or niches), merge
the friction signals into a single list. De-duplicate
identical signals.

## Step 3: Categorize by tier (per the Friction Filter taxonomy)

The 3-tier Friction Filter in `references/friction-filter.md`
defines the categorization. For each unique friction signal
across the audits, assign the tier per the taxonomy. If a
friction signal is novel (not in the taxonomy), flag it in
the roadmap's Section 7 and ask the operator to confirm the
tier.

## Step 4: Read the whitepaper §2 + §4

Open the whitepaper at the default path. Read §2 (the 4
Agentic Standard criteria) and §4 (the cost-comparison
table). Note the math defaults per `references/roi-math.md`.

If the client has provided their own numbers (call volume,
job ticket, order volume), override the whitepaper defaults.
The override is logged in the "Target ROI" table's Source
column.

## Step 5: Generate the Target ROI table

Apply the whitepaper's §4 math to the client's specific
situation. If the client is a 2-truck HVAC shop in Phoenix
with $300/job ticket, use the whitepaper's $876K/year
directly. If the client is a single-truck plumbing shop in
Dallas with $250/job ticket, scale accordingly.

If the client is e-commerce, use the TikTok Shop penalty
math (or Shopify oversell math). If the client is both e-com
and trades, use both tables.

## Step 6: Map friction → Blueprint phase

For each Tier 1 friction, identify the Blueprint phase that
addresses it. Per `references/blueprint-phases.md`:

- **Phone-only after-hours / no 24/7 web chat / "Call us for
  quote" only / no instant-booking calendar:** Phase 2
  (Voice Path)
- **Inventory sync failures (e-com clients only):** Phase 3
  (Inventory/Ops Path)
- **Stale site / no reviews / no FAQ (Tier 2):** Phase 4
  (Outcome Loop)

If a Tier 1 friction has no Blueprint phase, flag in
Section 7. The operator decides whether to extend the
Blueprint or deprioritize the friction.

## Step 7: Write the pov-roadmap.md

Use the template in `references/roadmap-template.md`. Atomic
write pattern (avoid corruption):

```bash
TMP=/tmp/pov-roadmap-$$.md
cat > "$TMP" <<'EOF'
[content]
EOF
mv "$TMP" "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Clients/[ClientName]/pov-roadmap.md"
```

Or use Python (atomic via `os.replace`):

```python
from pathlib import Path
content = "..."
target = Path(f"/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Clients/{client_name}/pov-roadmap.md")
target.write_text(content)
```

## Step 8: Update the clients ledger

If `03 Projects/Clients/_ledger.mdl` exists, append:

```markdown
- YYYY-MM-DD HH:MM CT — [ClientName] / [City, ST] / [Niche] — POV roadmap created (N Tier 1, M Tier 2, K Tier 3 signals ingested; whitepaper §2 Agentic Standard applied; target ROI: $X/year)
```

If the ledger does not exist, create it.

## Step 9: Return to the operator

Send a one-paragraph summary:
- Client name + city + niche
- File path of the pov-roadmap.md
- Counts: N Tier 1, M Tier 2, K Tier 3 signals ingested
- Target ROI (annualized)
- Install start date (if known)
- Any halt conditions / blockers / staleness warnings
