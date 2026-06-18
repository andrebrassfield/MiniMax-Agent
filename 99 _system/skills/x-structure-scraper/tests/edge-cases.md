# Edge Cases — x-structure-scraper

Test cases for the non-safety-halt edge cases the skill needs to handle
gracefully. Each is a scenario the model should recover from without
operator intervention.

## E1. Threads below the engagement floor

**Scenario:** The query returns 8 threads but only 3 are above the
50K-view floor. The other 5 are 10K-40K views.

**Expected response:** Analyze the 3 above-floor threads. Note in the
"Notes for the Scribe" how many threads were filtered by the floor.
Do not analyze the below-floor threads (they're not the proven-winners
signal the blueprint is meant to capture).

## E2. Threads all use the same bait pattern

**Scenario:** 3+ of 5 threads open with "I was wrong about X" or
similar. The analysis would be biased toward that one pattern.

**Expected response:** Flag explicitly in the cross-thread synthesis:
"3 of 5 threads use the 'I was wrong' bait pattern — this biases the
structural analysis. Consider scraping more threads or a different
account to round out the pattern coverage."

## E3. Thread is too long to capture in one snapshot

**Scenario:** The thread has 12+ tweets. The first `snapshot` call
captures tweets 1-8, the rest are cut off.

**Expected response:** Use `depth: 8` for the second snapshot, or
scroll in the X UI and re-snapshot. If still incomplete, flag the
thread as "partial scrape" in the blueprint's Notes column for that
thread.

## E4. Mixed-language thread

**Scenario:** The thread is primarily English but contains a 2-sentence
French anecdote.

**Expected response:** Capture verbatim including the French. Do not
translate. Note the language mix in the Human Markers section if the
anecdote is one of the human markers.

## E5. Quote-tweet at the top

**Scenario:** The thread's first tweet is a quote-tweet of someone
else's post, with the actual thread content in the reply chain.

**Expected response:** Treat the quote-tweet as the bait (it's the
first thing the reader sees). Note the structure in the Hook
Structure section: "Bait is a quote-tweet of @<other>; the thread
extends the quoted claim."

## E6. Account is in the pinned list but the Scribe is currently drafting

**Scenario:** Andre asks to scrape @GergelyOrosz while the Scribe is
mid-draft on a Pillar 5 post that already references the GergelyOrosz
blueprint.

**Expected response:** The blueprint scrape is independent of the
Scribe. The new blueprint overwrites the old one in the briefs
directory. The Scribe's in-flight draft will pick up the new
blueprint on its next Scribe run. No coordination needed.

## E7. Thread is a single-tweet essay >500 chars

**Scenario:** The "thread" is actually a single long-form tweet
(1,200 chars), not a multi-tweet chain.

**Expected response:** Treat as a "long-form" thread per the criteria
(≥500 chars single-tweet essays count). Apply the 4 dimensions to
the single tweet. The Pacing section will show "Tweets: 1, Avg
chars/tweet: 1200" — that IS the pacing for this thread.
