# Safety Halts — x-hype-translator

The skill must HALT (not improvise) when any of these fire. The
"halt" means: stop, surface the condition, do not retry.

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
aggressive about scraping. If Andre is running multiple hype-
translations in a row, expect to hit a rate limit.

## H4. Zero results across all queries

**Detection:** All 2-3 auto-generated queries return 0 results.

**Expected response:** Halt. Report "tool too fresh, try again in 24h."
The X chatter may not have rolled up yet. The skill does NOT invent
a post from a vague source.

## H5. Scribe dispatch fails

**Detection:** The `mavis communication send --command spawn` call
returns an error, or the Scribe session terminates without writing
the output file.

**Expected response:** Halt. Surface the spawn error. The skill
does NOT write the file itself (the Scribe is the writer). The
capability extraction is preserved for retry.

## H6. Scribe returns a draft >280 chars

**Detection:** The Scribe's draft text exceeds 280 characters.

**Expected response:** Halt. Surface the over-limit draft. Do NOT
post. The 280 cap is a hard limit (the Scribe's persona spec);
Andre can manually approve an over-limit post if the content
warrants, but the skill never publishes over-limit.

## H7. Scribe returns a generic audience

**Detection:** The Scribe's draft targets "any business" or
"developers" or "AI researchers" — NOT a specific boring audience
from the persona-anchored list (roofer, plumber, sales rep,
marketing manager at a 12-person co, small e-com store).

**Expected response:** Halt. Surface the generic-audience finding.
Ask the Scribe to retry with a specific audience. The "any business"
framing is the persona's hard ban.

## H8. Scribe invents a feature the source post didn't announce

**Detection:** The Scribe's draft references a capability not in
the source post (e.g., "this AI tool can also do X" when the source
post only mentioned Y).

**Expected response:** Halt. Surface the fabricated feature. The
Scribe's job is a reframe, not an addition. The skill is the gate
for source accuracy.

## Eval cases

| Halt | Input (mock state) | Expected behavior |
|---|---|---|
| H1 | `mavis browser status` not connected | Halt, surface install |
| H2 | snapshot contains "Sign in to X" | Halt, no credential attempt |
| H3 | snapshot shows rate-limit warning | Halt, recommend wait |
| H4 | all 3 auto-queries return 0 results | Halt, "try again in 24h" |
| H5 | spawn returns error | Halt, preserve extraction |
| H6 | Scribe draft > 280 chars | Halt, surface over-limit draft |
| H7 | Scribe draft says "any business" | Halt, ask for specific audience |
| H8 | Scribe references feature not in source | Halt, surface fabrication |
