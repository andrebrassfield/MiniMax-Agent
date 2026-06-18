# Researcher Task Spec — ai-utility-scout

The contract passed to the Content Researcher. The chief
(Mavis) copies this block verbatim and dispatches the
Researcher. The Researcher produces the discovery brief
that the Scribe then uses to draft the Pillar 6 X post.

## The task spec (verbatim, copy this block)

```
You are drafting a **tool discovery brief** for a newly
released AI tool that was just spotted in a launch-directory
scan. Your job is NOT to analyze viral X posts (that's your
other job) — this is a tool scout, focused on "what does
this tool actually do and why should @DreTheSalesGuy
translate it for SMBs?"

The voice file is at
`03 Projects/X-Content-Engine/agents/persona.md`. Read it
before drafting.

**The tool:**
- Name: <tool name>
- Source directory: <directory name>
- Directory entry URL: <directory-url>
- One-line capability (verbatim from directory): "<directory's one-liner>"
- Launch date (if visible): <date or "unclear">
- Pricing tier: <free / freemium / paid / unclear>
- Engagement (saves/upvotes): <number>

**The discovery brief format (write to
03 Projects/X-Content-Engine/drafts/utility-scout-YYYY-MM-DD.md,
append to existing file or create new):**

## Tool: <tool name> — <source directory> — YYYY-MM-DD HH:MM CT

**Source:** <directory entry URL>
**Pricing:** <free / freemium / paid / unclear>
**Launched:** <date or "unclear">

### What it does (one sentence)

<the tool's actual capability, in plain English>

### Category

<video / voice / image / productivity / e-commerce / local
services / dev infra / other>

### Who uses it (3 candidate audiences)

1. <audience 1>
2. <audience 2>
3. <audience 3>

### The boring SMB use case (the Dre Builds angle)

<one paragraph: which of the 3 audiences is the "boring
practical money-making" audience, and what the 4-step
implementation would look like. Reference the persona's
content pillars (Pillar 1 E-Com, Pillar 2 Trades, Pillar 5
Job Defense, Pillar 6 Hype Translation) if relevant.>

### What makes it hype-able vs. practical

<2-3 sentences: what's the "cool" angle the X conversation
will hype, vs. the boring application Dre Builds would
post.>

### Open questions for the Scribe

- Should the post use a specific persona pillar (Pillar 1/2/5/6)?
- What's the specific tool pricing anchor (if visible)?
- Is there a 4-step implementation path that fits in 280 chars?
```

## Why this task spec shape

The Researcher is the **discovery** layer. The Scribe
(downstream) is the **draft** layer. The Researcher's
brief feeds the Scribe's task spec. The split keeps each
agent focused on its scope.

The 3 candidate audiences + the boring SMB use case are
the load-bearing elements. The Scribe picks ONE of the 3
audiences for the Pillar 6 post and maps the 4-step
implementation.

## The "no fabrication" rule (the load-bearing discipline)

The Researcher may not invent features the directory
didn't describe. If the tool's capability is unclear, mark
`unclear` in the brief. The Scribe then uses the brief as
the source of truth — no extrapolation, no embellishment.

The audit-trail discipline: the brief is the source of
truth. The Scribe's draft must align with the brief.

## Cross-reference

- `references/filter-rules.md` — the accept/reject
  categories the chief applied before dispatching the
  Researcher
- `references/scribe-task-spec.md` — the downstream Scribe
  task spec (the Researcher feeds the Scribe)
- `references/output-format.md` — the file format the
  Researcher appends to
- The Content Researcher
  (`03 Projects/X-Content-Engine/agents/researcher.md`) —
  the agent that produces the brief
- The Persona — the load-bearing voice source
