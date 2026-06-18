# Output Format — local-competitor-auditor

The markdown brief template. The auditor writes this file
at `briefs/local-audit-[city-slug]-[niche-slug].md`.

## File path

`03 Projects/X-Content-Engine/briefs/local-audit-[city-slug]-[niche-slug].md`

Use lowercase kebab-case for the city and niche slugs:
- "Plumbers in Dallas, TX" → `local-audit-dallas-tx-plumbers.md`
- "HVAC Repair in Phoenix, AZ" → `local-audit-phoenix-az-hvac-repair.md`
- "Roofing Contractors in Denver, CO" →
  `local-audit-denver-co-roofing-contractors.md`

## Full template

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

[1-2 sentence recommendation: e.g., "Voice AI dispatcher
(Vapi or Synthflow) wired to Jobber + a 24/7 web chat
widget. 4-week install. ~$0.40/call."]

### Notes for the operator

[Any specifics — e.g., "this site is well-designed except
for the booking flow; the install would be incremental, not
a rebuild"]

---

(... Competitor 2, 3 same format)

---

## Cross-competitor summary

### Top 3 most-egregious friction patterns

1. [pattern, e.g., "All 3 sites are phone-only after-hours
   — 100% of after-hours revenue is leaking"]
2. [pattern, e.g., "None of the 3 have instant booking —
   every job requires a phone call to schedule"]
3. [pattern, e.g., "None of the 3 surface Google reviews on
   the homepage — trust friction at first contact"]

### The install that closes all three

[1-2 sentence recommendation — usually "voice AI dispatcher
+ web chat + instant-booking calendar. 4-week install.
~$X/month."]

### "Destroy or Defend" angle for the Scribe

[1 sentence — e.g., "I audited 12 plumbers in Dallas. None
of them can book a job online. Here's the 4-week install
I'd pitch to all of them."]

---

## Raw material for the operator (prospect list)

| Business | Phone | Address | Pitch (1 line) |
|----------|-------|---------|----------------|
| [name 1] | [phone] | [address] | "Voice AI + Jobber install — 4 weeks, ~$0.40/call" |
| [name 2] | [phone] | [address] | "Same pitch — they'd see a 30-50% lift in after-hours captured jobs" |
| [name 3] | [phone] | [address] | "Same pitch — strongest candidate, severity 5/5" |
```

## Per-section content discipline

- **Header:** search query verbatim, full Google URL with
  encoded query, top N (3 by default), filter applied (full
  Tier 1 + 2, Tier 3 noted).
- **Per-competitor:** all 9 friction signals checked
  (PRESENT/ABSENT). Severity 1-5 with the rubric. Install
  recommendation specific (named tools, time, cost).
- **Cross-competitor summary:** top 3 friction patterns
  named with evidence. The "Destroy or Defend" angle
  concrete (specific city + niche + install).
- **Prospect list:** every audited business with phone,
  address, 1-line pitch.

## What this output is NOT

- **Not a content draft.** The auditor produces
  intelligence; the Scribe produces the post. Don't
  conflate.
- **Not a public document.** Internal use only. The
  information is public (Google + competitor homepages),
  but the operator should not publish the audit results
  publicly (would be defamatory).
- **Not a sales pitch.** The prospect list is the operator's
  filter. The actual sales outreach is the operator's job.

## Cross-reference

- `references/friction-filter.md` — the 3-tier taxonomy
- `references/severity-scoring.md` — per-competitor scoring
- `references/procedure.md` — the 9-step procedure
- `client-pov-tracker` — downstream; uses the per-competitor
  signals + severity as input
- The Content Scribe — can convert the brief into a
  "Destroy or Defend" post (separate skill)
