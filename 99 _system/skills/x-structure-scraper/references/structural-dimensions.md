# Structural Dimensions — x-structure-scraper

The 4 dimensions applied to each thread. These are the analysis axes;
the model decides *what* the dimension reveals for each specific thread.

## 1. Hook Structure (bait vs. switch)

Every long-form thread has TWO moves in the first 1-3 tweets:
- **The bait** — what makes you click / keep reading (specific number, contrarian claim, personal failure, question)
- **The switch** — the bait's reframe. The thing the thread is actually about.

Capture per thread:
- The bait (verbatim, 1-2 sentences)
- The switch (verbatim or paraphrased, 1-2 sentences)
- The gap (what the bait promises vs. what the switch delivers)

**Common bait patterns:** specific dollar figures, "I was wrong about X," questions with non-obvious answer, "the real reason is Y," "everyone's talking about X, nobody's talking about Y."

**Common switch patterns:** "but here's the thing," "what I missed was," "the actual answer," "but that's not the real problem."

## 2. Argument Architecture (thesis → antithesis → synthesis)

Long-form threads almost always have a 3-move structure:
- **Thesis** — the initial claim
- **Antithesis** — the counter-argument, the complication, the "but wait"
- **Synthesis** — the resolution (rarely winner-take-all; usually "both X and Y are true, but Z is the load-bearing thing")

Capture per move:
- The position (1 sentence)
- The evidence (1 specific example or data point)
- The transition phrasing ("but," "however," "the real reason," "and this is where it gets interesting")

**If a thread lacks antithesis** → flag as "monologue" (useful contrast data)
**If a thread skips synthesis** → flag as "open loop" (also useful data)

## 3. Pacing

Count and categorize:
- Total tweet count
- Avg chars per tweet
- Avg sentences per tweet
- Stddev of sentence length (high = rhythmic, low = monotone)
- 1-2 example tweets showing the rhythm (verbatim)

**The staccato beat:** 1-clause sentences for emphasis. Frequency matters.
**The long exhale:** 4+ clause sentence to set up a complex idea.
**Tweet boundaries:** self-contained or mid-thought? Thread-on-purpose vs. chopped-for-length.

## 4. Human Markers

The single biggest tell of authentic human voice vs. AI-generated
content. Long-form human writers:
- **Admit they don't know** — "I genuinely don't know if this is right"
- **Use personal anecdotes** — "When I was at [company] we tried this and it failed because…"
- **Reference their own past wrongness** — "Last year I argued X. I was wrong."
- **Break the fourth wall** — "Okay this is going to sound weird but…"

Capture per thread:
- Number of "I don't know" admissions
- Number of personal anecdotes (1-line summary each)
- Number of past-wrongness references
- 1-2 verbatim examples of the strongest human marker

**If a thread has 0 human markers** → flag as "lecture mode." Authentic
long-form usually has 2-4 per thread. The Humanizer skill uses
"lecture mode" vs. "human mode" as a calibration signal for its
own rewrites.

## The 4 dimensions are the spec, not the script

The dimensions are the load-bearing analysis axes. The model applies
them to each thread and uses judgment to:
- Decide which bait/switch pattern a specific thread uses (not
  forced into a category)
- Decide whether a thread's "antithesis" is implicit or explicit
- Decide which pacing example to extract (the one that shows the
  rhythm most clearly, not just any random tweet)

The model reads the thread, sees what's there, and reports it
through the 4-dimension lens. The blueprint reflects what the thread
IS, not what the lens demands.
