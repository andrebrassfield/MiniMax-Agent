# Procedure — ea-decision-logger

The 5-step procedure with bash commands. The SKILL.md
only carries the procedure overview. The actual commands
live here.

---

## Step 1: DETECT — catch the decision point mid-session

**Direct markers** (auto-capture):
- "let's go with X", "we're doing Y", "ship it",
  "approved", "decision is Z", "log this", "record that"

**Indirect markers** (auto-capture with intent):
- A back-and-forth where ≥2 alternatives were named and
  one was chosen ("I think option A is better than B...
  actually let's try A" → that's a decision)

**Reversal markers** (auto-capture as a new decision):
- "actually scratch that", "I changed my mind", "no wait,
  let's do it the other way" → log the reversal as a new
  file, do not edit the prior decision file

**Detection failure mode:** Mavis recognizes the decision
but doesn't pause to log it. The conversation moves on,
the session ends, the decision is lost. **The skill is to
be loaded mid-session, not post-hoc.** If you can see the
decision happening, load the skill, capture the 5 fields,
write the file, then continue the conversation.

## Step 2: EXTRACT — fill the 5 fields

Apply the schema discipline from `5-field-schema.md`. The
hard parts:

- **Decision** — one sentence, past tense, definitive
- **Rationale** — 2-4 sentences, cite the brief/research
- **Alternatives considered** — 2-5 options, each with
  1-line why-rejected
- **Expected impact** — 2-4 sentences, concrete effects
- **What would change my mind** — 2-3 sentences, specific
  triggers

If you can't fill in a field, HALT and escalate. A
partial decision file is worse than no file.

## Step 3: WRITE — atomic write to the decision file

**Path:** `02 Notes/decisions/YYYY-MM-DD-<slug>.md`

**Filename slug rules:**
- 2-4 words, lowercase, hyphenated
- Captures the decision's essence, not the date
  ("gepa-pivot", "weekly-connections-skill", "loop-
  engineering-frame", "5-mistakes-audit-addition-11")
- Date in YYYY-MM-DD prefix
- Example: `2026-06-16-gepa-pivot.md`

**Atomic write pattern:**

```bash
VAULT="/Users/brassfieldventuresllc/MiniMax-Agent"
DECISIONS_DIR="$VAULT/02 Notes/decisions"
mkdir -p "$DECISIONS_DIR"
SLUG="<the-slug>"
DATE=$(date "+%Y-%m-%d")
TARGET="$DECISIONS_DIR/${DATE}-${SLUG}.md"

# Atomic write
TMP="/tmp/decision-${SLUG}-$$.md"
cat > "$TMP" <<'EOF'
[content]
EOF
mv -f "$TMP" "$TARGET"
```

**File template** in `references/file-template.md`.

## Step 4: CROSS-LINK — link to related surfaces

The decision file is not useful in isolation. Cross-link
to the surfaces that:

- **Informed the decision** — the brief, research, or
  analysis that produced the evidence (e.g.,
  `03 Projects/Mavis EA Design/reports/loop-engineering-framework.md`
  that justified the GEPA pivot)
- **Depend on the decision** — the skill, cron, memory,
  or workflow that this decision enables or constrains
  (e.g., `99 _system/skills/ea-skill-evolution/SKILL.md`
  depends on the GEPA decision)
- **Preceded the decision** — any prior decision that
  this one reverses, supersedes, or builds on

Use the `related:` YAML field for paths. The Obsidian
wikilink convention `[[path]]` also works for the body
text. Full cross-link patterns in
`references/cross-link-patterns.md`.

## Step 5: SURFACE — include in the daily brief

The next daily brief (or the `ea-weekly-connections` if
the decision is large) gets a one-line entry: "<YYYY-MM-DD>
— Decision logged: <one-sentence decision> (<slug>)".
Andre can click through to the file.

**Discipline:** the daily brief is the audit hook. If
the brief doesn't surface the decision, Mavis will never
know if the capture is right or wrong. Andre's review is
the verification step.

## Reverse a decision (special case)

When a decision is reversed, create a NEW decision file
with a `reverses:` related field pointing at the prior
file. Do NOT edit the prior file.

**Example reversal file:**

```yaml
---
date: 2026-06-20
type: architectural-decision
status: reversed
decider: Andre
reversibility: full
reverses: 2026-06-16-gepa-pivot  # the prior decision
related:
  - 02 Notes/decisions/2026-06-16-gepa-pivot.md
---

# Decision: Revert to the pre-GEPA loop-engineering framework

[5 fields explaining the reversal]
```
