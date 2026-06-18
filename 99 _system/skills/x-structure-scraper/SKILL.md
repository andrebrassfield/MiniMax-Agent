---
name: x-structure-scraper
description: Scrape a target "source-of-truth" X account (e.g., @GergelyOrosz, @DanShipper, @WaitButWhy) for their most viral long-form threads, then extract the STRUCTURAL skeleton — Hook Structure (bait vs. switch), Argument Architecture (thesis → antithesis → synthesis), Pacing (short vs. long sentences), and Human Markers (admissions of uncertainty, personal anecdotes). Ignore the content. Codify the rhythm. Output a "Structural Blueprint" to 03 Projects/X-Content-Engine/briefs/blueprints-YYYY-MM-DD.md. Triggers when the user says "scrape the structure of [account]", "analyze the rhythm of [account]", "study [account]'s threads", "structural blueprint of [handle]", or "how does [account] write". The deliverable is a style-anatomy doc, NOT a content-copy file. Read-only.
---

# X Structure Scraper — Anatomic Reverse-Engineering of Long-Form Threads

## What this skill does

You don't read what they say. You read **how** they say it.

This skill targets a list of "source-of-truth" accounts known for high-quality, long-form X content — accounts whose threads feel like conversations, not lectures. The skill scrapes their most viral threads and produces a **Structural Blueprint**: a file that captures the *skeleton* of how those threads are built, not the *substance* of what they argue. The blueprint is then a reference the Scribe (or Andre) can use to study rhythm, pacing, hook mechanics, and human-marker placement.

This is a **style-anatomy** skill, not a content-summarization skill. The output should make a writer go "ah, that's why this thread feels different" — not "ah, I learned something new about AI infrastructure."

## When to run

**Trigger phrases:**
- "scrape the structure of [@account]" / "study [@account]'s threads"
- "analyze the rhythm of [@account]" / "how does [@account] write"
- "structural blueprint of [handle]" / "build a blueprint for [handle]"
- "reverse-engineer [@account]'s voice" / "anatomy of [handle]'s threads"
- "who else is good at long-form X" / "give me a model to study"

**Do NOT run for:**
- The user's own posts or drafts (that's the Scribe's territory — `03 Projects/X-Content-Engine/agents/scribe.md`)
- Bookmark dumps or personal saves (use `x-bookmark-parser`)
- Single-tweet links (use `x-link-reader`)
- A specific topic/niche (use `x-niche-scraper` for topic scouting)
- Live engagement / reply-writing (use `x-engagement-hunter`)
- Generic content (Low-engagement threads <1K views, accounts without a clear long-form style)

## The Source-of-Truth Account List (Andre-pinned 2026-06-16)

Start with these — Andre has confirmed them as the reference set:

| Handle | Style signature | Why they're on the list |
|---|---|---|
| @GergelyOrosz | Pragmatic tech/industry analysis | Long-form threads on engineering culture, pricing, layoffs. Specific numbers, contrarian-when-true framing, "here's what the data says" cadence |
| @DanShipper | First-person AI + business | "I tried X. Here's what happened." Personal-experiment-driven threads. Essay-style with embedded code/screenshots |
| @WaitButWhy | (legacy Tim Urban) | Essay-style long threads. Multiple "but here's the thing" pivots. The classic explainer that builds a world before the punchline |

**Add to the list as Andre approves new sources.** The skill takes a single handle per run, so building a multi-account blueprint requires multiple invocations or an explicit "scrape all 3" directive.

## Inputs

| Input | Default | Required |
|---|---|---|
| Target handle | (none — must be specified or in the pinned list) | **yes** |
| Thread count | top 5 most-viral threads from the account | no — override to 3, 10, or "all in the first snapshot" |
| Engagement floor | 50,000 views per thread (long-form means real engagement) | no — set higher for proven-winners-only |
| Output dir | `03 Projects/X-Content-Engine/briefs/` | no |
| File naming | `blueprints-YYYY-MM-DD.md` (multi-account) or `blueprint-[handle]-YYYY-MM-DD.md` (single-account) | no |
| Reference axis | 4 structural dimensions (see below) | fixed — do not add/remove without Andre's approval |

## The 4 Structural Dimensions (load-bearing — do not skip)

### 1. Hook Structure (the bait vs. the switch)

Every long-form thread has TWO moves in the first 1-3 tweets:
- **The bait** — what makes you click / keep reading. Usually a specific number, a contrarian claim, a personal failure, or a question that creates a knowledge gap.
- **The switch** — the bait's reframe. The thing the thread is actually about (which is rarely the bait).

The blueprint should capture, for each thread analyzed:
- The bait (verbatim, 1-2 sentences)
- The switch (verbatim or paraphrased, 1-2 sentences)
- The gap between them (what does the bait promise that the switch delivers? what does it set up that the switch subverts?)

**Common bait patterns to flag:** specific dollar figures, "I was wrong about X," questions with a non-obvious answer, "the real reason is Y," "everyone's talking about X. nobody's talking about Y."

**Common switch patterns to flag:** "but here's the thing," "what I missed was," "the actual answer," "but that's not the real problem."

### 2. Argument Architecture (thesis → antithesis → synthesis)

Long-form threads almost always have a 3-move structure:
- **Thesis** — the initial claim or position
- **Antithesis** — the counter-argument, the complication, the "but wait" moment
- **Synthesis** — the resolution (which is rarely a winner-take-all — usually "both X and Y are true, but Z is the load-bearing thing")

The blueprint should map each thread's 3 moves. For each, capture:
- The position itself (one sentence)
- The evidence used (one specific example or data point)
- The transition phrasing ("but," "however," "the real reason," "and this is where it gets interesting")

**If a thread lacks antithesis** (pure lecture mode), flag it as "monologue" — useful contrast data. **If a thread skips synthesis** (ends on a question or cliffhanger), flag it as "open loop" — also useful data.

### 3. Pacing (short vs. long sentences, sentence-count per beat)

Count and categorize:
- Sentence length distribution (chars per sentence, averaged across the thread)
- The "staccato beat" — does the thread use 1-clause sentences for emphasis? At what frequency? (e.g., "short. Short. SHORT." as a 3-beat emphasis)
- The "long exhale" — does the thread ever use a 4+ clause sentence to set up a complex idea?
- Tweet boundaries — are tweets self-contained, or do they break mid-thought? Thread-on-purpose vs. chopped-for-length.

**Capture, for each thread:**
- Total tweet count
- Avg chars per tweet
- Avg sentences per tweet
- Stddev of sentence length (high stddev = rhythmic; low stddev = monotone)
- 1-2 example tweets showing the rhythm in action (verbatim)

### 4. The "Human Marker" (admissions of uncertainty + personal anecdotes)

The single biggest tell of an authentic human voice vs. AI-generated content. Long-form human writers:
- **Admit they don't know** — "I genuinely don't know if this is right," "I'm not sure about X but here's my best guess"
- **Use personal anecdotes** — "When I was at [company] we tried this and it failed because…"
- **Reference their own past wrongness** — "Last year I argued X. I was wrong."
- **Break the fourth wall** — "Okay this is going to sound weird but…," "I'm going to stop pretending I have this figured out"

The blueprint should count, per thread:
- Number of "I don't know" admissions
- Number of personal anecdotes (with 1-line summary)
- Number of past-wrongness references
- 1-2 verbatim examples of the strongest human marker

**If a thread has 0 human markers**, flag as "lecture mode" — useful contrast data. Authentic long-form usually has 2-4 per thread.

## Outputs

A single markdown file at `03 Projects/X-Content-Engine/briefs/blueprints-YYYY-MM-DD.md` (or `blueprint-[handle]-YYYY-MM-DD.md` for a single-account run) with:

1. **Header** — target handle(s), thread count analyzed, engagement floor, timestamp, source URLs (per thread)
2. **Per-thread analysis** — the 4 structural dimensions applied to each thread
3. **Cross-thread pattern synthesis** — what unifies the threads? (the load-bearing answer)
4. **Notes for the Scribe** — what specific moves should the Scribe try to copy?

The blueprint is **NOT** a content-summary. It does not say "this thread argues X about Y." It says "this thread opens with a $450 bait, switches to a math-problem reframe, has 7 tweets of avg 180 chars, and includes 2 'I don't know' admissions in tweets 4 and 6."

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, HALT and tell Andre to load the Chrome extension per `mavis browser install` output. Do not proceed with auto-spawned Chromium fallbacks for x.com — the security memory locks the OAuth-hijack surface.

### Step 2: Identify the target handle(s) and find their viral threads

For a single handle, navigate to the account's "media" or "threads" tab (or search the handle for the highest-engagement long-form posts). For a single handle run, the URL pattern is:

```bash
mavis browser tool navigate '{"tabId":<id>,"url":"https://x.com/<handle>/with_replies"}'
# or for top posts only
mavis browser tool navigate '{"tabId":<id>,"url":"https://x.com/<handle>"}'
```

Wait 3-5 seconds for render. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":3}'
```

**Halt conditions (operator-alert only, never type credentials):**
- Snapshot shows "Sign in to X" / "Log in" — Andre needs to log in manually
- URL is not x.com/[handle] after navigation
- Snapshot shows a rate-limit warning
- The account is suspended / private / deleted

**Proceed conditions:**
- The handle's timeline is visible
- Posts are dated within the past 24 months (older threads = different platform dynamics)

### Step 3: Identify the top 5 (or N) long-form threads

Filter the visible posts:
- **Long-form** = multi-tweet threads (>=3 tweets in the chain) OR single-tweet essays >500 chars
- **Engagement** = above the floor (default 50K views; lower for accounts with smaller reach)
- **Recency** = within the past 24 months (X's algorithm and culture shift fast)

**Pick threads with diverse formats** — at least 2 different "moves" (e.g., one pure-essay thread, one Q&A-style thread, one numbered-list thread) so the blueprint covers the account's range.

**Anti-pattern:** do not pick 5 threads that all open with "I was wrong about X" — that biases the structural analysis. The blueprint should reflect the account's signature style, not a single format.

### Step 4: Scrape each thread's full text

For each selected thread, navigate to the source URL (the first tweet in the chain, not the profile timeline) and snapshot the full thread:

```bash
mavis browser tool navigate '{"tabId":<id>,"url":"https://x.com/<handle>/status/<thread_id>"}'
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":5}'
```

**Read the FULL thread, not just the first tweet.** The structural moves (switch, antithesis, human marker) often live in tweets 3-7, not the opener. If the thread is long (>10 tweets), the snapshot may not capture all of it — use `depth: 8` or scroll within the X UI and re-snapshot.

### Step 5: Apply the 4-dimension analysis

For each scraped thread, fill in:
- **Hook Structure:** bait verbatim → switch verbatim → gap (1-2 sentences)
- **Argument Architecture:** thesis → antithesis → synthesis (each 1 sentence + transition phrasing)
- **Pacing:** total tweets, avg chars/tweet, avg sentences/tweet, 1 verbatim example
- **Human Markers:** count of "I don't know" admissions + personal anecdotes + 1 verbatim example

**If a thread is missing a dimension** (e.g., no antithesis, no human marker), flag it explicitly. Missing dimensions are signal, not noise.

### Step 6: Cross-thread synthesis

After all threads are analyzed, write a 1-2 paragraph synthesis covering:
- **What unifies them** (the signature move — what's THIS account's structural fingerprint?)
- **What varies** (the dimensions where the threads diverge — the range of the account's range)
- **The single most-copyable move** (1-2 sentences — "if the Scribe wanted to sound like [handle], THIS is the move to steal")

**The single most-copyable move is load-bearing.** It's what Andre will use to train the Scribe. Don't bury it in the middle of the synthesis — put it at the top of the section.

### Step 7: Write the blueprint file

Use this schema (the Scribe's blueprint-reading procedure will rely on these sections being in this order):

```markdown
# Structural Blueprint — @[handle] — YYYY-MM-DD CT

**Threads analyzed:** N
**Engagement floor:** 50K views
**Source URLs:** (one per thread, with view count)
**Analyzed by:** x-structure-scraper (Mavis, 2026-06-16)
**Output target:** Scribe training reference for voice/rhythm mimicry

---

## The Single Most-Copyable Move

[1-2 sentences on the one structural move that, if stolen, would most improve a Scribe draft in this account's style.]

---

## Thread 1 — "[headline or first-tweet quote]" — N views

**Source:** https://x.com/[handle]/status/[id]

### Hook Structure
- **Bait:** "[verbatim first 1-2 sentences]"
- **Switch:** "[verbatim or paraphrased 1-2 sentences]"
- **Gap:** [1-2 sentences on what the bait promises vs. what the switch delivers]

### Argument Architecture
- **Thesis:** [1 sentence]
- **Antithesis:** [1 sentence]
- **Synthesis:** [1 sentence]
- **Transition phrasing:** "[verbatim 'but' / 'however' / 'the real reason' phrasing]"

### Pacing
- **Tweets:** N
- **Avg chars/tweet:** NNN
- **Avg sentences/tweet:** N.N
- **Rhythm example:** "[verbatim tweet showing the staccato beat or the long exhale]"

### Human Markers
- **"I don't know" admissions:** N (1 verbatim)
- **Personal anecdotes:** N (1-line summary each)
- **Past-wrongness references:** N (1-line summary each)

[... repeat for threads 2-N ...]

---

## Cross-Thread Synthesis

### What unifies them
[1-2 paragraphs on the signature structural move]

### What varies
[1 paragraph on the range]

---

## Notes for the Scribe

- [Move 1 to try: e.g., "open with a specific $ figure, switch to a math-problem reframe in tweet 2"]
- [Move 2 to try: e.g., "use 1-clause sentences for emphasis at 20% frequency"]
- [Move 3 to try: e.g., "include at least 1 'I don't know' admission in every thread >5 tweets"]
- [Move to AVOID: e.g., "do not use 'the real reason is' — this account used it 4x across 5 threads, which means it's a tic, not a move"]

---

## Cross-Account Patterns (only if multi-account run)

[If the skill was run on 2+ handles, add a section comparing them. Otherwise omit.]
```

### Step 8: Update the briefs ledger

Append a one-line entry to `03 Projects/X-Content-Engine/briefs/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — blueprint from @[handle] (N threads, floor 50K, output: blueprints-YYYY-MM-DD.md)
```

### Step 9: Return summary

Send a one-paragraph summary to Andre:
- Handle(s) analyzed
- Thread count + engagement floor
- Blueprint file path
- The single most-copyable move (1 sentence — preview it, don't make him open the file)
- Suggested follow-up scrapes (e.g., "scrape @[other_handle] for contrast" or "lower the floor to 10K to get more material from mid-tier accounts")

## The "Skeleton, Not Substance" Discipline (load-bearing)

This skill is NOT a content-summarization skill. The most common failure mode is the analyst drifting into "this thread argues that X is the future of Y" — that's a content summary, not a structural blueprint. The output should make a writer go "ah, I see how they built the rhythm" — not "ah, I learned something new about the topic."

**Discipline checks before returning the file:**
- Does the file contain a single line of paraphrased CONTENT from the threads? If yes, delete it. The blueprint is structure-only.
- Does the file contain at least 2 verbatim HOOK examples? If no, add them. Verbatim beats paraphrase for rhythm analysis.
- Does the file contain a single "most-copyable move"? If no, add it. This is the most actionable section.
- Does the file name correctly reflect single vs. multi-account? `blueprint-[handle]-...` for one handle, `blueprints-...` for multi.

## The Hard Rules

1. **Read-only.** No likes, no reposts, no follows, no replies. The skill is structural analysis, not engagement.
2. **No credential entry.** If the page shows a login prompt, halt and alert Andre.
3. **No fabrication.** If a thread is missing a structural dimension (e.g., no human marker), say "0 human markers" — do not invent one.
4. **Structure-only output.** Do not summarize the thread's argument. The blueprint is how the thread is BUILT, not what it ARGUES.
5. **Verbatim over paraphrase.** Hooks, switches, transition phrasing, human markers — capture verbatim whenever possible. The rhythm is in the exact wording.
6. **No auto-publish.** The blueprint is a reference file. The Scribe reads it. The Scribe does NOT copy the account's content — only the structural moves.
7. **Discipline check before returning.** The 4 questions in "Skeleton, Not Substance" must all be YES.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell Andre to load Chrome extension |
| Login prompt | snapshot shows Sign in / Log in | Halt; tell Andre to log in manually |
| Rate limit | snapshot shows rate limit OR `mavis browser` returns 429 | Halt; surface to Andre; recommend waiting 10+ minutes |
| Account suspended / private | URL returns 404 or "this account is private" | Halt; surface; suggest a different handle |
| Threads below engagement floor | views < floor | Skip silently; log in "Notes for the Scribe" how many were filtered |
| Threads all use the same bait pattern | 3+ of N threads open identically | Flag in the cross-thread synthesis — biases the analysis, suggest picking more diverse threads |
| Thread is too long to capture in one snapshot | snapshot cuts off mid-thread | Use `depth: 8` or scroll in X UI + re-snapshot; if still incomplete, flag as "partial scrape" |
| All threads lack human markers | 0 human markers in all N threads | Flag explicitly: account is lecture-mode; consider whether to keep on the reference list |
| Bridge navigation lands on wrong page | URL after navigate is not the expected page | Halt; surface; suggest a different scrape strategy |
| Account has < 3 long-form threads in 24 months | count of qualifying threads < 3 | Halt; surface; suggest a different account |

## Verification

Before returning the blueprint:
1. The file exists at the expected path with non-zero size
2. `grep -c "^## Thread" <file>` matches the thread count analyzed
3. `grep -c "^### Hook Structure" <file>` matches the thread count (every thread has all 4 sections)
4. `grep -c "Single Most-Copyable Move" <file>` returns 1
5. The briefs ledger is appended
6. The file contains at least 2 verbatim hook examples (grep for `"` quote marks in Hook Structure sections)
7. The file does NOT contain a single paraphrased CONTENT summary (Andre will spot-check; if you wrote "the thread argues that X," you failed the discipline check)
8. The 4 "Skeleton, Not Substance" discipline questions are all YES

## Cross-reference

- `x-niche-scraper` — for topic-based search ("what are people saying about HVAC missed calls")
- `x-bookmark-parser` — for Andre's personal saves
- `x-link-reader` — for a single X URL (use this for the per-thread scrape in Step 4)
- `x-engagement-hunter` — for reply-writing to a specific account
- The Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — consumes the blueprint as a style reference
- The Humanizer (`99 _system/skills/scribe-humanizer/SKILL.md`) — uses the blueprint's pacing + human-marker analysis as its "what does authentic look like" reference
- The persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the source of truth for voice; the blueprint is style-anatomy data, the persona is voice-rules data, and they live in different layers
