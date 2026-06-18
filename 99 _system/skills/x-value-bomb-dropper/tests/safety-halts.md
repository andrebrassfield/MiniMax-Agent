# Safety Halts — x-value-bomb-dropper

The skill must HALT (not improvise) when any of these fire.

## H1. Bridge offline

**Detection:** `mavis browser status` shows `Native host: not connected`.

**Expected response:** Halt. Tell Andre to load the Chrome extension.
Do not fall back to auto-spawned Chromium for x.com.

## H2. Login prompt

**Detection:** Snapshot contains "Sign in to X" / "Log in" /
"Sign up", or URL is not `x.com/search` after navigation.

**Expected response:** Halt. Surface auth state. Do not type
credentials. Andre logs in manually.

## H3. Rate limit

**Detection:** Snapshot shows a rate-limit warning, or `mavis browser`
returns 429.

**Expected response:** Halt. Recommend waiting 10+ minutes. X is
aggressive about scraping; the value-bomb use case is
particularly rate-sensitive (X's bot detection is especially
active on operational-Q queries).

## H4. Zero results

**Detection:** All operational-Q queries return 0 results, or
the snapshot has no author blocks.

**Expected response:** Halt. Report "no posts matching this
operational question query — try a different angle." The chief
suggests a query variant to Andre.

## H5. Source post is too vague for a 3-step

**Detection:** Source text is general (e.g., "what's the best
AI tool?" / "Should I be using AI?") — can't be answered with
3 specific steps.

**Expected response:** Skip the source post. The Scribe can't
draft a useful reply without a concrete problem. Note the
skip in the report.

## H6. Source post is from an AI influencer pitching their own product

**Detection:** Handle contains "AI" / "GPT" / "ML" or bio
signals "founder" / "CEO" / building a competing product.

**Expected response:** Skip. The value-bomb is for the operator
with the problem, not the founder with the pitch. This is
`x-engagement-hunter` territory.

## H7. Sensitive content in source post

**Detection:** Source post mentions specific employers,
financial situations, or proprietary workflows.

**Expected response:** Skip the source post. Don't draft a
reply that could leak the employer's stack or financials.
The Scribe's reply is public; private content stays private.

## H8. Unfamiliar UI

**Detection:** Snapshot shows a layout the chief doesn't
recognize (suspended-account screen, X-premium upsell, error
state, etc.).

**Expected response:** Halt. Surface the UI. Do not improvise.

## H9. Scribe violates the zero-sales-pitch rule

**Detection:** The Scribe's draft contains any of: `DM me`,
`book a call`, `link in bio`, `my agency`, `I help companies`,
`let's chat offline`, `reach out`, `consulting`, `services`,
`if you need help`, `happy to walk you through`.

**Expected response:** Halt. Surface the CTA violation. The
Scribe retries WITHOUT the CTA. This is the most-load-bearing
halt in the skill.

## H10. Scribe returns a generic 3-step

**Detection:** Scribe's tactical steps are vague ("Step 1:
research the tool. Step 2: try it. Step 3: measure the
results.") — not specific actions with named tools.

**Expected response:** Halt. Surface the generic-3-step
violation. The Scribe retries with specific steps (the
load-bearing element).

## H11. Scribe returns a draft > 280 chars (single) or > ~840 chars (thread)

**Detection:** Scribe's draft text exceeds the format cap.

**Expected response:** Halt. Surface the over-limit draft.
Do NOT truncate. The 280/840 cap is a hard limit per Dre's
persona; operator can manually approve an over-limit post,
but the skill never publishes over-limit.

## H12. Scribe spawn fails

**Detection:** The `mavis communication send --command spawn`
returns an error, or the Scribe session terminates without
writing.

**Expected response:** Halt. Surface the spawn error. The
extraction is preserved for retry.

## Eval cases

| Halt | Input (mock state) | Expected behavior |
|---|---|---|
| H1 | `mavis browser status` not connected | Halt, surface install |
| H2 | snapshot contains "Sign in to X" | Halt, no credential attempt |
| H3 | snapshot shows rate-limit warning | Halt, recommend wait |
| H4 | snapshot has no author blocks | Halt, suggest query variant |
| H5 | source post is "what's the best AI tool" | Skip, note in report |
| H6 | source handle contains "GPT" or "AI" | Skip, route to engagement-hunter |
| H7 | source post mentions employer/financials | Skip, note in report |
| H8 | snapshot shows suspended-account UI | Halt, surface UI |
| H9 | Scribe draft contains "DM me" | Halt, ask for retry without CTA |
| H10 | Scribe steps are "research/try/measure" | Halt, ask for specific steps |
| H11 | Scribe draft > 280 chars (single) | Halt, surface over-limit |
| H12 | spawn returns error | Halt, preserve extraction |
