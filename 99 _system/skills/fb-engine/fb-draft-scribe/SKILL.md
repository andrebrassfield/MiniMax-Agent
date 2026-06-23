---
name: fb-draft-scribe
description: |
  Generate FB-Engine drafts from fb-group-reader output. Ingests the JSON
  from the read path, samples 1-2 relevant entries from `ammunition.mdl`
  per post, applies the typology formula (T1 Value Bomb for operator-
  provided hooks, T2 Authority Comment for replies), and writes draft
  markdown files to `03 Projects/FB-Engine/drafts/`. Hard Rule: the Scribe
  never publishes, only writes to `drafts/`. v1.0.0 uses deterministic
  template-based generation; v1.1.0 will add an LLM-backed mode.
---

# fb-draft-scribe

The Mavis-side draft generator for the FB-Engine. Mirrors the role of
`x-scribe` in the X-Content-Engine — writes drafts, never publishes.

## When to invoke

**Auto-invoke when:**
- `fb-group-reader` produces a fresh JSON output and there are no unread
  drafts in `drafts/`
- The operator says "draft replies for [JSON]" or "value bomb on [topic]"
- A scheduled research cron (Phase 3) fires after the reader

**Triggers (manual):**
- "draft replies for /tmp/fb-posts.json"
- "value bomb on CAC math in HVAC"
- "scribe 5 drafts for [group]"
- "fb-draft-scribe on [JSON]"

**Do NOT use for:**
- Publishing to Facebook (the Scribe only writes to `drafts/`; the
  Poster consumes `approved/`)
- Drafts that already have operator approval (the bridge surfaces those
  via Telegram; the Scribe doesn't re-draft)
- Reading posts (that's `fb-group-reader`; the Scribe consumes its
  output, not the live Group)
- Other agents' content pipelines (this is Mavis territory)

## The mechanism (the discipline)

For each post the Scribe processes, the pipeline is:

```
post.text → tokenize → keyword overlap → sample 1-2 ammo entries
                                          ↓
                              apply typology formula
                                          ↓
                              write draft markdown to drafts/
```

### Step 1: Read `ammunition.mdl`

The Scribe parses the append-only ledger section
(`## Append-only ledger`) of `ammunition.mdl` and pulls all entries
into memory. Each entry has: `date`, `topic`, `typology`, `claim`,
`source`. v1.0.0 reads the whole ledger on each run; for Phase 3
auto-curation we'll add an LRU cache.

### Step 2: Sample 1-2 entries per post

For Typology 2 (default), the Scribe:
1. Tokenizes the post text against `PILLAR_KEYWORDS` (in `scribe.py`).
2. Scores each ammo entry by pillar match + recency.
3. Picks the top-1 or top-2 (deterministic hash of the post text
   controls the final pick so the same post + ledger always produces
   the same draft).
4. Falls back to a random sample of 2 entries if no overlap.

For Typology 1, the operator passes `--pillar N` to bias the sampling
toward Pillar 1/2/3, and the Scribe samples 2 entries from that
pillar's topic tags.

### Step 3: Apply the typology formula

**Typology 1 (Value Bomb):** the Scribe takes the operator's hook
(from `--hook`) and fills in:

```
{hook}

The math on this is pretty brutal:
  - {ammo[0].claim} (Source: ...)
  - {ammo[1].claim} (Source: ...)

Here's the 3-step breakdown:
  1. {derived step}
  2. {derived step}
  3. {derived step}

Anyone else running into this? What's your {pain-var} cost looking like?
```

The 3 breakdown steps are templated against the pillar name + first
metric. Operator can edit any of them.

**Typology 2 (Authority Comment):** the Scribe paraphrases the post's
first sentence as the premise, then injects the constraint:

```
Yeah, {premise} — that's a real problem in a lot of operator circles.

The thing I'd add: {ammo[0].claim} (Source: ...)

In our experience, the actual bottleneck is {bottleneck_name} — not the
thing most folks focus on. {explanation}.
```

The `bottleneck_name` is derived from the claim via a regex that
matches common FB-pillar patterns (lock-in, missed call, lead response,
stack, churn, integration, booking, support). Falls back to a generic
phrase if no match.

### Step 4: Write the draft

The Scribe writes one markdown file per draft to
`03 Projects/FB-Engine/drafts/`. Filename pattern:

```
YYYY-MM-DD-HHMM-t{typology}-{slug}.md
```

The file has YAML frontmatter + body + notes section. The bridge
(`ea-fb-draft-approval`) parses the frontmatter to extract the
`draft_id` and `original_post_id` for the Telegram proposal.

## Output contract (draft file structure)

```markdown
---
draft_id: fb-2-post-1234567890-a1b2c3d4e5
scribe: fb-draft-scribe
typology: T2
status: open
created_at: 2026-06-18T13:30:00+00:00
original_post_id: "1234567890"
original_author: "Jane Smith"
original_url: https://www.facebook.com/groups/.../posts/...
ammunition_used: |
  - pillar=#local-service | T1-Value-Bomb | Average missed HVAC call costs $400-600... | source=HVAC.com + ServiceTitan
  - pillar=#cac-ltv | T2-Authority | Lead response within 5 min = 21x more likely... | source=Lead Response Management Study
---

## Generated draft

Yeah, [premise]...

## Notes for Andre

- Typology: T2 (Authority Comment)
- Ammunition entries used: 2
- Status: open — awaiting your approval via Telegram

## Original post (for context)

- Author: Jane Smith
- Post ID: 1234567890
- URL: https://...
- Timestamp: 1718712000

```
[post text truncated to 1000 chars]
```
```

The bridge reads this file, posts the "## Generated draft" body to
Telegram, and waits for approve/deny/edit.

## CLI

```bash
# Default: T2 (Authority Comment) for each post in the JSON
python3 ~/.mavis/agents/mavis/skills/fb-engine/fb-draft-scribe/scripts/scribe.py \
  --from-reader /tmp/fb-posts.json

# T1: Value Bomb with operator-provided hook
python3 .../scribe.py \
  --typology 1 \
  --hook "Most HVAC owners I talk to are losing \$400/day to missed calls" \
  --pillar 1

# Combined: T1 first, then T2 for each post in JSON
python3 .../scribe.py \
  --from-reader /tmp/fb-posts.json \
  --hook "..." --pillar 1

# Override output dir
python3 .../scribe.py --from-reader /tmp/fb-posts.json \
  --output-dir /tmp/test-drafts/

# Override ledger path
python3 .../scribe.py --from-reader /tmp/fb-posts.json \
  --ledger /path/to/custom-ledger.mdl
```

## Hard constraints

- **The Scribe NEVER publishes.** It only writes to `drafts/`. The
  Poster (`fb-poster`) consumes `approved/`. The Scribe is a writer,
  not a publisher.
- **One draft per post (T2) or one draft per invocation (T1).** No
  batching across multiple posts into a single file (each Telegram
  proposal needs a stable draft_id).
- **Stable draft_id** — `<typology>-<source_key>-<sha256[:10]>`. The
  bridge matches Andre's reply to this ID. If the Scribe rewrites the
  draft between the proposal and the reply, the draft_id is different;
  treat as a new draft.
- **Append-only on `ammunition.mdl`.** The Scribe reads the ledger but
  never writes to it. The ledger is curated by the operator (manual
  seed entries) or by the Phase 3 nightly cron.
- **Mavis territory only.** The Scribe writes only to
  `03 Projects/FB-Engine/drafts/`. No cross-agent territory.

## HALT conditions

- `--typology 1` is passed without `--hook` → HALT with error
- `--from-reader` path doesn't exist → HALT with error
- The post's text is empty after parsing → skip that post, continue to
  the next (don't fail the whole run on a single empty post)
- `--max-drafts` reached → stop processing, report the cap
- `ammunition.mdl` is empty → continue with no-ammo drafts (the
  template flags the gap so the operator can add ammo before approving)

## Integration with other skills

The cron chain for the FB-Engine (Phase 2 / 3):

```
fb-group-reader (read path, Phase 1)
        ↓ JSON
fb-draft-scribe (THIS skill, Phase 2)
        ↓ draft markdown
ea-fb-draft-approval (Telegram bridge, Phase 2)
        ↓ operator replies approve/deny/edit
approved/  ← approved drafts land here
        ↓
fb-poster (Phase 2)
        ↓ published
archive/published/  ← audit trail
```

The Scribe's job is the deterministic data prep + template generation.
The LLM-quality draft text is a Phase 3 upgrade via `--use-llm`
(currently a stub; the operator can wire it to the mavis runtime's
LLM access when ready).

## Cross-references

- `fb-session-guardian` — pre-flight (read path depends on this)
- `fb-group-reader` — produces the JSON the Scribe consumes
- `ammunition.mdl` — the ledger the Scribe samples from
- `ea-fb-draft-approval` — the next skill (surfaces drafts to Andre)
- `fb-poster` — the poster (consumes `approved/`)
- `x-scribe` — the X-CE parallel (different topic tags, different
  typology codes — do NOT cross-consume)

## Source

- `~/.mavis/agents/mavis/skills/fb-engine/fb-draft-scribe/scripts/scribe.py`
- Mirror: `~/MiniMax-Agent/99 _system/skills/fb-engine/fb-draft-scribe/scripts/scribe.py`

## Changelog

- 1.0.0 (2026-06-18) — initial skill. Reads `ammunition.mdl` append-only
  section. Two typologies (T1 Value Bomb with operator hook, T2 Authority
  Comment from JSON posts). Deterministic template-based generation with
  pillar-keyword sampling. Stable draft_id via sha256. One-draft-per-file
  output. YAML frontmatter with original post metadata for bridge
  matching. CLI flags: --from-reader, --typology, --hook, --pillar,
  --output-dir, --ledger, --max-drafts. v1.1.0 will add `--use-llm` for
  LLM-backed generation via the mavis runtime.
