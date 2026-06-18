---
name: local-competitor-auditor
description: |
  Google-search a local business niche in a target city (e.g., "Plumbers in
  Dallas, TX"), click into the top 3 organic results, scan each homepage for
  friction signals (no web chat, no instant booking, "Call us for a quote"
  form only, no service area map, no reviews linked, etc.), and write a raw
  intelligence brief. Output to `briefs/local-audit-[city]-[niche].md`. Uses
  mavis browser tool against the user's real Chrome. Triggers: "audit local
  competitors", "find plumbers in X", "competitor scan", "destroy or defend
  brief", or specifies a city + niche. Read-only. Provides raw material for
  "Destroy or Defend" case studies and a prospect list for custom-agent sales
  outreach. No X drafts — this is intelligence, not content.
---

# local-competitor-auditor

The prospecting engine. Runs a Google search for a local
business niche in a target city, clicks the top 3 organic
results, scans each homepage for **friction signals**, and
writes a **raw intelligence brief** for two purposes:

1. **"Destroy or Defend" X case studies** (Pillar 1/2) — the
   friction signals become the leverage anchor for posts
2. **Sales prospect list** — pitchable businesses for
   custom AI voice / web chat / instant-booking installs

This is intelligence, not content. No X drafts. Pair it
with the Scribe's "Destroy or Defend" brief format when
the operator wants to convert intelligence to a post.

## When to run

**Triggers:**
- "audit local competitors" / "competitor scan" / "local audit"
- "find [niche] in [city]" / "[city] [niche] audit"
- "destroy or defend brief" / "D&D brief"
- "where's the friction in [city] [niche]"
- "prospect list for [niche] in [city]"

**Do NOT run for:**
- Auditing the user's own website (different skill — not
  yet built)
- National / franchise chains (the local-audit format
  doesn't apply)
- Pure e-commerce (no "local" component)
- Niches outside the persona's pillar coverage (HVAC,
  plumbing, e-com, local services)

## Inputs

| Input | Default | Required |
|---|---|---|
| City | — | **yes** |
| Niche / category | — | **yes** |
| State | for "City, ST" formatting | no |
| Top N results | 3 organic results | no — 5 if fuller picture wanted |
| Friction filter | full list (see below) | no — operator can scope down |
| Destination dir | `03 Projects/X-Content-Engine/briefs/` | no |
| File naming | `local-audit-[city-slug]-[niche-slug].md` | no |

**City + niche formatting:** the skill URL-encodes the
search query as `plumbers+dallas+tx` for Google. Operator
can supply a custom query (e.g., "emergency plumber 24/7"
or "best plumber near me" — different queries surface
different competitors).

## The 3-tier Friction Filter (the load-bearing taxonomy)

The auditor scans each homepage for friction signals. Each
signal that is PRESENT = the business is leaking revenue to
friction. Full taxonomy + signal-to-install mapping in
`references/friction-filter.md`. Per-competitor severity
scoring in `references/severity-scoring.md`.

| Tier | Friction | What it leaks |
|---|---|---|
| **1** | Phone-only after-hours | Missed calls weekends/evenings/holidays (Pillar 2) |
| **1** | No 24/7 web chat | After-hours visitors see contact form and leave (Pillar 2) |
| **1** | "Call us for a quote" only | Lead gated by phone call business may not answer (Pillar 2) |
| **1** | No instant-booking calendar | Customer calls, leaves message, waits for callback (Pillar 2) |
| **2** | No service-area map | Customer has to call to confirm coverage (Pillar 2) |
| **2** | No online pricing | Customer has to call to get any cost info (Pillar 2) |
| **2** | No reviews linked / social proof | Business doesn't actively surface proof (Trust friction) |
| **2** | No FAQ / process page | Customer has to call to learn anything (Lead friction) |
| **2** | Site is dated (last update > 2 years) | Business isn't actively investing in web presence (Stale signal) |
| **3** | No blog / content / SEO play | Missing free organic traffic (noted, not prioritized) |
| **3** | No team page / About us | Business is faceless (lower priority) |
| **3** | No video / photo of completed work | Homepage is text-only (lower priority) |

The same taxonomy feeds `client-pov-tracker` (the
per-client POV). The auditor produces the raw signals; the
client-pov-tracker categorizes them per the per-client
context.

## Severity scoring (per competitor)

Per-competitor severity score (1-5) per
`references/severity-scoring.md`:

| Tier 1 count | Tier 2 count | Severity |
|---|---|---|
| 1-2 | 0-1 | 3/5 (leaking after-hours revenue) |
| 3-4 | 0-1 | 4/5 (bleeding revenue) |
| Any | 2+ | 5/5 (perfect prospect — single install 2-3x lead capture) |
| 0 | 0-1 | 2/5 (operating OK; not hot) |
| 0 | 0 | 1/5 (already operating at high level; not a prospect) |

The severity is the per-competitor score; the cross-
competitor summary identifies the top 3 friction patterns
across the cohort.

## The 9-step procedure (overview)

The full 9-step procedure with bash commands lives in
`references/procedure.md`. The high-level flow:

1. Verify bridge is live (`mavis browser status`)
2. Build the search query (URL-encode city + niche)
3. Open the Google search URL
4. Auth + load wait + result check
5. Click the top 3 organic results (one at a time)
6. Apply the friction filter to each homepage
7. Write the brief (markdown file at
   `briefs/local-audit-[city-slug]-[niche-slug].md`)
8. Update the briefs ledger
9. Return summary

## Hard constraints

1. **No interaction.** Read-only against Google + business
   homepages. Do not fill out any forms. Do not call the
   business. The operator handles the actual sales
   outreach.
2. **No credential entry.** Google reCAPTCHA is aggressive;
   if the operator isn't logged into Google in Chrome, the
   snapshot will show "I'm not a robot" challenges. Halt
   and ask the operator to log in first.
3. **No data hoarding.** The brief is for the operator's
   use. The information is public (Google + their own
   homepages), but the operator should not publish the
   audit results publicly (would be defamatory). Internal
   use only.
4. **No deep crawling.** One homepage per competitor. If
   friction signals are on a sub-page, note in "Open
   questions" and stop. Deep-crawling without permission
   is iffy ethically.
5. **Rate limit.** Google is aggressive about scraping. If
   `mavis browser` returns 429, HALT. The operator running
   this across many cities can hit limits within 10-20
   minutes.
6. **One homepage per competitor.** Do NOT click into
   sub-pages. The friction signals live on the homepage.
7. **No "Destroy or Defend" draft.** The auditor produces
   intelligence; the Scribe produces the post. Don't
   conflate the two.
8. **Read-mostly.** The brief is written to a file. The
   operator copy/pastes. No form fills, no calls, no DMs.

## When the skill HALTs

Halt and escalate to Andre when:
- Bridge offline (H1) — load Chrome extension
- reCAPTCHA / login (H2) — operator logs in
- Zero results (H3) — try a different city or niche
- Top 3 are all aggregators (H4) — try results #4-6
- Rate limit (H5) — wait 10+ minutes
- Source output write fails (H6) — surface

The skill is a diagnostic, not an authorization. The
operator decides the action.

## Verification (post-write)

After writing the brief, verify:

1. `ls -la` confirms the file exists with non-zero size
2. The file has 3 competitor sections, each with severity
   score + friction signals list
3. The cross-competitor summary identifies a top-3 friction
   pattern set
4. The "Destroy or Defend" angle is concrete (specific
   city + niche + install)
5. The prospect list has at least the 3 audited businesses
   with phone + pitch
6. The briefs ledger is appended

## Cross-reference

- `references/friction-filter.md` — the 3-tier taxonomy
  (load-bearing)
- `references/severity-scoring.md` — per-competitor
  severity scoring rules
- `references/procedure.md` — the 9-step procedure with
  bash + Google search URL building
- `references/output-format.md` — the markdown brief
  template
- `tests/safety-halts.md` — 6 halt conditions + eval cases
- `tests/discipline.md` — 5 quality floors (no-interaction,
  one-homepage-only, no-deep-crawl, no-CTAs, read-mostly)
- `client-pov-tracker` — downstream skill. The auditor
  produces raw signals; the tracker categorizes them per
  per-client context.
- `ai-utility-scout` — sibling for Pillar 6 supply. Scout
  finds AI tools; auditor finds local businesses with
  friction.
- `x-engagement-hunter` — for replying to specific large
  accounts (separate use case)
- The Content Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`)
  — can convert the brief into a "Destroy or Defend"
  Pillar 1/2 X post if the operator wants
- The Persona (`03 Projects/X-Content-Engine/agents/persona.md`)
  — the load-bearing voice source
