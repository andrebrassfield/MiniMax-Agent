# Procedure — local-competitor-auditor

The 9-step procedure with bash commands. The SKILL.md only
carries the procedure overview. The actual commands live
here (the deterministic layer).

---

## Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected` → HALT (H1). Do not fall
back to auto-spawned Chromium for Google (login wall on
Google is aggressive).

## Step 2: Build the search query

URL-encode the city + niche as a Google search. Examples:
- "plumbers dallas tx" → `https://www.google.com/search?q=plumbers+dallas+tx`
- "hvac repair phoenix az" → `https://www.google.com/search?q=hvac+repair+phoenix+az`
- "roofing contractors denver co" → `https://www.google.com/search?q=roofing+contractors+denver+co`

Note: Google may show local pack results (map with 3
businesses) at the top, then organic results below. The
auditor clicks the top 3 organic results BELOW the local
pack.

## Step 3: Open the Google search

```bash
mavis browser tool open_tab '{"url":"<google-search-url>"}'
```

Note the returned `tabId`.

## Step 4: Authentication + load wait + result check

Wait 3-5 seconds. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions:**
- Snapshot shows "Sign in" / "I'm not a robot" / reCAPTCHA
  → operator decides whether to solve (H2)
- URL is not `google.com/search` after navigation
- Zero results for the city + niche → HALT, try a
  different city or a broader niche (H3)

**Proceed conditions:**
- Local pack visible with map + 3 businesses (these are
  also valuable — capture them too if they have websites)
- Organic results visible below the local pack

## Step 5: Click the top 3 organic results

For each of the top 3 organic results, click the link to
navigate to the business's homepage:

```bash
mavis browser tool click '{"tabId":<id>,"ref":"<result-link-ref>"}'
```

Note: in `agent-browser` and the mavis browser tool,
`click` takes a ref. Get the ref from the snapshot.

**Wait for page load** (2-3 seconds) and take a snapshot
of each homepage:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Do NOT scroll.** The friction signals live on the
homepage. If the business has friction on a sub-page
(e.g., the booking flow is broken on /book but the
homepage hides it), note in "Open questions for the
operator" but don't deep-crawl.

## Step 6: Apply the friction filter

For each homepage, scan the snapshot's text for the
friction signals in the filter list. Mark each signal as
PRESENT (leak) or ABSENT (no leak). Tally per-competitor.

Apply the severity scoring rules in
`references/severity-scoring.md` to assign a 1-5 score
per competitor.

## Step 7: Write the brief

Compose the markdown file at
`03 Projects/X-Content-Engine/briefs/local-audit-[city-slug]-[niche-slug].md`.
Use UTC offset `America/Chicago` for the timestamp.
Filename uses lowercase kebab-case for the city and niche.

Full template in `references/output-format.md`. The brief
includes:
- Header (search query, URL, top N audited, filter applied)
- Per-competitor sections (business name, URL, rank,
  phone, address, severity, friction signals checkboxes,
  install recommendation, notes)
- Cross-competitor summary (top 3 patterns, install,
  D&D angle)
- Raw material for the operator (prospect list)

## Step 8: Update the briefs ledger

Append a one-line entry to
`03 Projects/X-Content-Engine/briefs/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — local-audit [city] [niche] (3 competitors, top friction: [one-line])
```

## Step 9: Return summary

Send a one-paragraph summary to the operator with: file
path, top friction pattern, the strongest "Destroy or
Defend" angle, and a count of how many of the 3 sites
are severity 4 or 5 (hot prospects).
