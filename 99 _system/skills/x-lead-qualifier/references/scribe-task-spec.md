# Scribe Task Spec — x-lead-qualifier

The contract passed to the Content Scribe. The chief
(Mavis) dispatches the Scribe with this spec for each
intent-qualified candidate. The Scribe produces a
Qualification DM (not a post) per the 3-section structure.

## The task spec (verbatim, copy this block)

```
You are drafting a **Qualification DM** for @DreTheSalesGuy. This is NOT a post. This is a direct message response.

**Source (the inbound engagement that triggered this):**
- Author: @<handle>
- Source URL: <post-URL or DM-source>
- Source text (verbatim): "<the verbatim quote, ≤500 chars>"
- Detected intent: <"ai_automation_question" | "pain_point_statement" | "integration_inquiry" | "job_defense_question" | "operational_distress">

**The voice (loaded from `03 Projects/X-Content-Engine/agents/persona.md`):**
- @DreTheSalesGuy's voice: staccato periods, lead with a punch, follow with unit economics, no AI fluff
- For DMs: more conversational than posts, longer (300-500 words is fine), no 280-char limit, no banned-phrase list from the post context (the banned phrases are for posts; DMs are direct conversation)
- Banned in DMs: "dive into", "delve into", "unlock", "game-changer", "harness the power of", "in today's fast-paced world", "at the end of the day", "let's unpack this"

**The hard constraint (READ THIS):**
- **NO SELLING. ONLY QUALIFICATION.** The DM is the first step of a sales funnel, not a sales pitch. The lead is asking a question; you answer it with genuine value. The CTA at the end is a low-friction offer ("DM me 'AUDIT' for a free stack review"), not a hard sell.
- The technical tip in the body must be GENUINELY useful — not a teaser, not bait-and-switch. The lead gets value even if they never reply.
- The CTA must be:
  - Free (no cost barrier)
  - Self-qualifying (lead types the keyword → they're warm)
  - Single-step (one action, not a "schedule a call" funnel)

**The DM structure (3 sections):**

1. **Acknowledge the specific question/pain** (1-2 sentences)
   > "Saw your post about [specific topic]. The [specific thing they asked about] is exactly where most teams [common failure]."

2. **Tiny high-value technical tip** (2-3 sentences with a real number or insight)
   > "Quick tip: [specific technical insight]. The [specific metric/result] is the test. If your [current state] is below [threshold], you have a [specific problem]."

3. **Low-friction CTA** (1 sentence)
   > "If you want me to look at your current stack for free, DM me 'AUDIT' and I'll spend 15 minutes on it."

**The output format:**

Write to: `03 Projects/X-Content-Engine/queue/qualification-dms-YYYY-MM-DD.mdl` (append, do not overwrite). Use the queue entry format from the Outputs section.

**The verification checklist (the Scribe self-checks before returning):**
1. The DM has the 3 sections (Acknowledge / Tip / CTA) in order
2. The technical tip is genuinely useful (a real number, a real insight, not "you should consider X")
3. The CTA is free + self-qualifying + single-step
4. No hard-sell language (no "buy", no "sign up", no "this week only", no "scarcity")
5. The voice matches the persona (staccato, no AI fluff, no "dive into" / "delve into")
6. The DM is conversational (talks TO the lead, not AT them)

**Halt conditions (the Scribe halts on any of these):**
- The source text is < 10 chars (too thin to qualify against)
- The detected intent is below confidence threshold (default 0.6)
- The persona file is missing
- The technical tip would require making up facts (halt and surface the gap)

**The return summary (the Scribe returns to the chief):**
- File path written
- Source handle + intent type + confidence
- 1-line preview of the drafted DM
- Any halt conditions / blockers
```

## Why this task spec shape

The Scribe's system prompt is post-focused (Hard Rule
#10: never publish to x.com). The lead-qualifier
overrides the post format for DMs:

- **No 280-char limit** — DMs can be 300-500 words
- **No post-banned-phrase list** — DMs are direct
  conversation, not broadcast
- **DM-specific banned phrases** (above) — the DM
  voice is more conversational

The 3-section structure is the load-bearing element:
Acknowledge → Tip → CTA. The Scribe fills in the
template with source-specific details.

## The "no fabrication" rule (the load-bearing discipline)

The technical tip must be GENUINELY useful — not a
teaser, not bait-and-switch. The lead gets value even
if they never reply.

If the technical tip would require making up facts,
HALT and surface the gap. The Scribe may not invent.

## The "no hard-sell" check (the load-bearing element)

The Scribe self-checks the draft against the
verification checklist before returning. If any
check fails (especially check #4: no hard-sell
language), the Scribe halts.

The chief (Mavis) may override the Scribe's self-check
and submit the draft anyway, but the Scribe's default
is to halt on a failed check.

## The CTA discipline

The CTA must be:
- **Free** — no cost barrier ("DM me 'AUDIT' for a free
  stack review" is OK; "Book a $5k engagement" is not)
- **Self-qualifying** — the lead types the keyword to
  signal interest ("AUDIT" → they're warm; "schedule a
  call" → they're not yet warm)
- **Single-step** — one action, not a "schedule a call"
  funnel with 3 follow-ups

The default CTA keyword is `AUDIT`. The operator can
override per run (e.g., "DEMO" for a product demo,
"STACK" for a tech-stack review).

## Cross-reference

- `references/filter-rules.md` — the 5 intent types +
  classification
- `references/procedure.md` — the 7-step procedure
- `references/voice-discipline.md` — DM-specific voice
  rules
- `references/output-format.md` — the queue file format
- The Content Scribe — produces the DM drafts
- The Persona — voice source
