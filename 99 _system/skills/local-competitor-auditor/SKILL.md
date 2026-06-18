---
name: local-competitor-auditor
description: Google-search a local business niche in a target city (e.g., "Plumbers in Dallas, TX"), click into the top 3 organic results, scan each homepage for friction signals (no web chat, no instant booking, "Call us for a quote" form only, no service area map, no reviews linked, etc.), and write a raw intelligence brief. Output to briefs/local-audit-[city]-[niche].md. Uses mavis browser tool against the user's real Chrome. Triggers when the user says "audit local competitors", "find plumbers in X", "competitor scan", "destroy or defend brief", or specifies a city + niche. Read-only. Provides raw material for "Destroy or Defend" case studies and a prospect list for custom-agent sales outreach. No X drafts — this is intelligence, not content.
---

# Local Competitor Auditor

## What this skill does

Runs a parameterized Google search for a local business niche in a target city. Clicks into the top 3 organic results, scans each homepage for **friction signals** (the operational gaps that a voice-AI / web-chat / instant-booking install would close), and writes a **raw intelligence brief** that the operator can use for two purposes:

1. **"Destroy or Defend" X case studies** (Pillar 1 / 2) — the friction signals become the leverage anchor for a post like "I audited 12 plumbers in Dallas. None of them can book online. Here's the install I'm pitching."
2. **Sales prospect list** — the operator can pitch a custom AI voice agent / web chat / instant-booking install to the audited businesses.

This is a **prospecting engine**, not a content engine. The output is intelligence for the operator, not a draft for X. Pair it with the Scribe's "Destroy or Defend" brief format when the operator wants to convert the intelligence into a post.

## When to run

**Trigger phrases:**
- "audit local competitors" / "competitor scan" / "local audit"
- "find [niche] in [city]" / "[city] [niche] audit"
- "destroy or defend brief" / "D&D brief"
- "where's the friction in [city] [niche]"
- "prospect list for [niche] in [city]"

**Do NOT run for:**
- Auditing the user's own website (use a different skill — not yet built)
- National / franchise chains (the local-audit format doesn't apply)
- Pure e-commerce (no "local" component)
- Niches outside the persona's pillar coverage (HVAC, plumbing, e-com, local services)

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| City | (none — must be specified) | **yes** |
| Niche / category | (none — must be specified) | **yes** |
| State | (none — for "City, ST" formatting) | no — operator can omit |
| Top N results | 3 organic results | no — 5 if the operator wants a fuller picture |
| Friction filter (which signals to look for) | full list (see below) | no — operator can scope down |
| Destination dir | `03 Projects/X-Content-Engine/briefs/` | no |
| File naming | `local-audit-[city-slug]-[niche-slug].md` | no |

**City + niche formatting:** the skill URL-encodes the search query as `plumbers+dallas+tx` for Google. Operator can supply a custom query (e.g., "emergency plumber 24/7" or "best plumber near me" — different queries surface different competitors).

## Outputs

A markdown file at `03 Projects/X-Content-Engine/briefs/local-audit-[city-slug]-[niche-slug].md` with:

- A header with the search query, the city, the niche, the capture timestamp
- A per-competitor section: business name, URL, Google rank position, friction signals detected, severity score (1-5), what install would close the gap, the address/phone (for prospect-list use)
- A summary section: the top 3 most-egregious friction patterns across the 3-5 sites, the install that would close all three, the "Destroy or Defend" angle the Scribe could draft on
- A "raw material for the operator" section: prospects to pitch, with their contact info and a 1-line pitch

The skill returns a one-paragraph summary to the operator with: file path, top friction pattern, the strongest "Destroy or Defend" angle.

## The Friction Filter (what to look for on each homepage)

The auditor scans each homepage for the following friction signals. Each signal that is PRESENT = the business is leaking revenue to friction.

### Tier 1 — High-leverage friction (Pillar 2 / Missed Call thesis)

- **Phone-only after-hours:** no live answer outside 9-5 (Mon-Fri). Indicates missed calls on weekends, evenings, holidays. (Pillar 2 anchor.)
- **No 24/7 web chat:** no chat widget in the bottom-right. Indicates after-hours visitors see a contact form and leave. (Pillar 2 anchor — voice AI install target.)
- **"Call us for a quote" only:** the primary CTA is a phone number, no online form, no instant quote. Indicates the lead is gated by a phone call the business may or may not answer. (Pillar 2 anchor.)
- **No instant-booking calendar:** no Calendly / ServiceTitan / Jobber / Housecall Pro embed. Indicates the customer has to call, leave a message, wait for a callback. (Pillar 2 anchor.)

### Tier 2 — Medium-leverage friction

- **No service-area map:** no geographic boundary visible. Indicates the customer has to call to confirm coverage. (Pillar 2 anchor.)
- **No online pricing:** no rate sheet, no "starting at $X" anywhere. Indicates the customer has to call to get any cost information. (Pillar 2 anchor.)
- **No reviews linked / social proof:** no Google reviews badge, no Yelp link, no Nextdoor, no testimonials on the homepage. Indicates the business doesn't actively surface proof. (Trust friction — medium.)
- **No FAQ or process page:** no "How it works" / "What to expect" / "Our process" page. Indicates the customer has to call to learn anything substantive. (Lead-friction — medium.)
- **Site is dated (last update > 2 years):** the copyright footer says 2023 or 2024. Indicates the business isn't actively investing in their web presence. (Stale signal — medium.)

### Tier 3 — Low-leverage friction (still note them, but lower priority)

- **No blog / content / SEO play:** no recent posts, no local SEO landing pages. Indicates the business is missing free organic traffic.
- **No team page / "About us":** the business is faceless. Lower priority — some local businesses intentionally don't have team pages.
- **No video / photo of completed work:** the homepage is text-only. Lower priority — some trades are camera-shy.
- **No SSL/HTTPS (just kidding — this is 2026).** Skip.

### Severity scoring (per competitor)

- **1-2 Tier 1 signals:** severity 3/5. The business is leaking after-hours revenue.
- **3-4 Tier 1 signals:** severity 4/5. The business is bleeding revenue. A voice-AI + instant-booking install would close most gaps.
- **Any Tier 1 + 2+ Tier 2:** severity 5/5. The business is the perfect prospect — a single 4-week install would 2-3x their lead capture.
- **No Tier 1 + few Tier 2:** severity 2/5. The business is operating OK; not a hot prospect.
- **Everything present (chat, booking, pricing, etc.):** severity 1/5. The business is already operating at a high level; not a prospect.

## Procedure

### Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected`, **HALT** and tell the operator to load the Chrome extension. Do not proceed with auto-spawned Chromium fallbacks for Google (login wall on Google is aggressive).

### Step 2: Build the search query

URL-encode the city + niche as a Google search. Examples:
- "plumbers dallas tx" → `https://www.google.com/search?q=plumbers+dallas+tx`
- "hvac repair phoenix az" → `https://www.google.com/search?q=hvac+repair+phoenix+az`
- "roofing contractors denver co" → `https://www.google.com/search?q=roofing+contractors+denver+co`

Note: Google may show local pack results (map with 3 businesses) at the top, then organic results below. The auditor clicks the top 3 organic results BELOW the local pack.

### Step 3: Open the Google search

```bash
mavis browser tool open_tab '{"url":"<google-search-url>"}'
```

Note the returned `tabId`.

### Step 4: Authentication + load wait + result check

Wait 3-5 seconds. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions:**
- Snapshot shows "Sign in" / "I'm not a robot" / reCAPTCHA — operator decides whether to solve
- URL is not `google.com/search` after navigation
- Zero results for the city + niche — HALT, try a different city or a broader niche

**Proceed conditions:**
- Local pack visible with map + 3 businesses (these are also valuable — capture them too if they have websites)
- Organic results visible below the local pack

### Step 5: Click the top 3 organic results

For each of the top 3 organic results, click the link to navigate to the business's homepage:

```bash
mavis browser tool click '{"tabId":<id>,"ref":"<result-link-ref>"}'
```

Note: in `agent-browser` and the mavis browser tool, `click` takes a ref. Get the ref from the snapshot.

**Wait for page load** (2-3 seconds) and take a snapshot of each homepage:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

### Step 6: Apply the friction filter

For each homepage, scan the snapshot's text for the friction signals in the filter list. Mark each signal as PRESENT (leak) or ABSENT (no leak). Tally per-competitor.

**Do NOT scroll.** The friction signals live on the homepage. If the business has friction on a sub-page (e.g., the booking flow is broken on /book but the homepage hides it), note that in "Open questions for the operator" but don't deep-crawl.

### Step 7: Write the brief

Compose the markdown file at `03 Projects/X-Content-Engine/briefs/local-audit-[city-slug]-[niche-slug].md`. Use UTC offset `America/Chicago` for the timestamp. Filename uses lowercase kebab-case for the city and niche.

Format:

```markdown
# Local Audit — [City], [ST] — [Niche] — YYYY-MM-DD HH:MM CT

**Search query:** "[query]"
**Search URL:** https://www.google.com/search?q=[encoded-query]
**Top N audited:** 3 organic results
**Friction filter applied:** full Tier 1 + Tier 2 (Tier 3 noted)

---

## Competitor 1 — [Business Name]

- **URL:** [homepage]
- **Google rank position:** #1 organic (below local pack)
- **Phone:** [from homepage or local pack]
- **Address:** [from homepage or local pack]
- **Severity score:** X/5

### Friction signals detected

- [ ] Phone-only after-hours: PRESENT / ABSENT
- [ ] No 24/7 web chat: PRESENT / ABSENT
- [ ] "Call us for a quote" only: PRESENT / ABSENT
- [ ] No instant-booking calendar: PRESENT / ABSENT
- [ ] No service-area map: PRESENT / ABSENT
- [ ] No online pricing: PRESENT / ABSENT
- [ ] No reviews linked: PRESENT / ABSENT
- [ ] No FAQ / process page: PRESENT / ABSENT
- [ ] Site is dated: PRESENT / ABSENT
- [ ] Other: [notes]

### What install would close the gap

[1-2 sentence recommendation: e.g., "Voice AI dispatcher (Vapi or Synthflow) wired to Jobber + a 24/7 web chat widget. 4-week install. ~$0.40/call."]

### Notes for the operator

[Any specifics — e.g., "this site is well-designed except for the booking flow; the install would be incremental, not a rebuild"]

---

(... Competitor 2, 3 same format)

---

## Cross-competitor summary

### Top 3 most-egregious friction patterns

1. [pattern, e.g., "All 3 sites are phone-only after-hours — 100% of after-hours revenue is leaking"]
2. [pattern, e.g., "None of the 3 have instant booking — every job requires a phone call to schedule"]
3. [pattern, e.g., "None of the 3 surface Google reviews on the homepage — trust friction at first contact"]

### The install that closes all three

[1-2 sentence recommendation — usually "voice AI dispatcher + web chat + instant-booking calendar. 4-week install. ~$X/month."]

### "Destroy or Defend" angle for the Scribe

[1 sentence — e.g., "I audited 12 plumbers in Dallas. None of them can book a job online. Here's the 4-week install I'd pitch to all of them."]

---

## Raw material for the operator (prospect list)

| Business | Phone | Address | Pitch (1 line) |
|----------|-------|---------|----------------|
| [name 1] | [phone] | [address] | "Voice AI + Jobber install — 4 weeks, ~$0.40/call" |
| [name 2] | [phone] | [address] | "Same pitch — they'd see a 30-50% lift in after-hours captured jobs" |
| [name 3] | [phone] | [address] | "Same pitch — strongest candidate, severity 5/5" |
```

### Step 8: Update the briefs ledger

Append a one-line entry to `03 Projects/X-Content-Engine/briefs/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — local-audit [city] [niche] (3 competitors, top friction: [one-line])
```

### Step 9: Return summary

Send a one-paragraph summary to the operator with: file path, top friction pattern, the strongest "Destroy or Defend" angle, and a count of how many of the 3 sites are severity 4 or 5 (hot prospects).

## The Safety Halts (inherited, plus the auditor specifics)

1. **No interaction.** Read-only against Google + the business homepages. Do not fill out any forms. Do not call the business. The operator handles the actual sales outreach.
2. **No credential entry.** Google reCAPTCHA is aggressive; if the operator isn't already logged into Google in Chrome, the snapshot will show "I'm not a robot" challenges. Halt and ask the operator to log in first.
3. **No data hoarding.** The brief is for the operator's use. It contains competitor info that's public on Google + their own homepages. The operator should not publish the audit results publicly (would be defamatory). Internal use only.
4. **No deep crawling.** One homepage per competitor. If the friction signals are on a sub-page, note it and stop. Deep-crawling a competitor's site without permission is iffy ethically.
5. **Rate limit.** Google is aggressive about scraping. If `mavis browser` returns 429, HALT. If the operator is running this skill across many cities, expect to hit limits within 10-20 minutes.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Bridge offline | `mavis browser status` shows `not connected` | Halt; tell operator to load Chrome extension |
| reCAPTCHA / login | snapshot shows challenge | Halt; ask operator to log in to Google in Chrome first |
| Zero results | snapshot has no organic results | Halt; try a different city or broader niche |
| Top 3 are all aggregator sites (Yelp, Angi, etc.) | homepage is not a real business | Skip to results #4-6; if all are aggregators, halt and note "no organic local businesses for this query" |
| Business homepage is a parked domain | copyright 2024, no content | Severity 1/5; note as low-priority prospect |
| Business homepage requires JS to render | snapshot is empty | Mark friction signals as `unclear`; note the JS issue |
| Business has 0 friction signals (severity 1/5) | all Tier 1 absent | Note as "operating at high level — not a prospect" |
| Friction signals present but the business is clearly already investing in AI (chat widget, modern site) | mixed signals | Severity 3/5; note that the install is incremental, not greenfield |

## Verification

After writing the file:
1. `ls -la` confirms the file exists with non-zero size
2. The file has 3 competitor sections, each with severity score + friction signals list
3. The cross-competitor summary identifies a top-3 friction pattern set
4. The "Destroy or Defend" angle is concrete (specific city + niche + install)
5. The prospect list has at least the 3 audited businesses with phone + pitch
6. The briefs ledger is appended

## Cross-reference

- `ai-utility-scout` — sibling for Pillar 6 supply. The scout finds AI tools; the auditor finds local businesses with friction. Same data intelligence, different angle.
- `x-engagement-hunter` — for replying to specific large accounts. The local-competitor-auditor doesn't produce X drafts, but the intelligence can be fed to the Scribe for a "Destroy or Defend" post.
- `x-hype-translator` — for Hype Translation posts on specific tools
- `x-empowerment-hunter` — for AI-anxiety reply pipeline
- `x-bookmark-parser` — for the user's own curated saves
- `x-niche-scraper` — for search-side AI tool scan
- `mavis browser` CLI — the underlying tool surface
- The Content Researcher (`03 Projects/X-Content-Engine/agents/researcher.md`) — not directly involved (this skill doesn't dispatch the Researcher; the operator uses the intelligence directly or feeds it to the Scribe for a "Destroy or Defend" draft)
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — can convert the brief into a "Destroy or Defend" Pillar 1/2 X post if the operator wants
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`) — the load-bearing voice source
- `team-config.md` — the dispatch protocol (for the optional Scribe "Destroy or Defend" draft)
