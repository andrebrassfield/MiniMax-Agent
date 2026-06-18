# Safety Halts — x-structure-scraper

The skill must HALT (not improvise) when any of these fire. The "halt"
means: stop the run, surface the condition, do not retry.

## H1. Bridge offline

**Detection:** `mavis browser status` shows `Native host: not connected`.

**Expected response:** Halt and tell Andre to load the Chrome extension
per `mavis browser install` output. Do not fall back to auto-spawned
Chromium for x.com.

## H2. Login prompt

**Detection:** Snapshot contains "Sign in to X" / "Log in" / "Sign up",
or URL is not `x.com/<handle>` after navigation.

**Expected response:** Halt. Surface the auth state. Andre logs in
manually. Do not type credentials.

## H3. Rate limit

**Detection:** Snapshot contains a rate-limit warning or `mavis browser`
returns 429.

**Expected response:** Halt. Recommend waiting 10+ minutes. X is
aggressive about scraping. If Andre is running this skill repeatedly
across multiple accounts, expect to hit a rate limit within 10-20 minutes.

## H4. Account suspended / private / deleted

**Detection:** URL returns 404, "this account is suspended," "this
account is private," or the timeline shows no posts at all.

**Expected response:** Halt. Surface the account state. Suggest a
different handle from the pinned list (or a new one Andre approves).

## H5. Account has <3 long-form threads in 24 months

**Detection:** The handle's timeline shows fewer than 3 threads
matching the long-form criteria (≥3 tweets OR >500 chars single-tweet
essays) in the past 24 months.

**Expected response:** Halt. Surface the count. The account is not a
useful reference if there's not enough material. Suggest a different
account or a different engagement-floor.

## H6. All threads lack human markers (lecture mode)

**Detection:** All analyzed threads have 0 "I don't know" admissions,
0 personal anecdotes, 0 past-wrongness references. All are pure
lecture mode.

**Expected response:** Halt. Surface the observation. The account is
not a good voice reference for the Scribe (the whole point of the
blueprint is the human-marker calibration). Suggest a different
account.

## H7. URL navigation lands on wrong page

**Detection:** After `navigate` to a thread URL, the snapshot shows a
different page (e.g., a search result, a "this post is unavailable"
page, the timeline again).

**Expected response:** Halt. Surface the URL vs. the actual page
content. The thread may be deleted, the URL may be wrong, or X's
anti-scrape UI may have redirected.

## Eval cases

| Halt | Input (mock state) | Expected behavior |
|---|---|---|
| H1 | `mavis browser status` not connected | Halt, surface install instructions |
| H2 | snapshot contains "Sign in to X" | Halt, no credential attempt |
| H3 | snapshot shows rate-limit warning | Halt, recommend wait |
| H4 | URL returns 404 | Halt, surface account state |
| H5 | only 2 long-form threads in 24 months | Halt, surface count |
| H6 | all 5 threads have 0 human markers | Halt, surface lecture-mode finding |
| H7 | navigate to thread URL lands on search page | Halt, surface URL mismatch |
