# Edge Cases — x-niche-scraper

Inherits all edge cases from `x-bookmark-parser` (empty results, partial
capture, truncated text, quote-tweet nesting, focus mismatch, mixed
language). See `../../x-bookmark-parser/tests/edge-cases.md` for those.

This file documents only the search-specific edge cases.

## E8. Zero results for the query

**Scenario:** The query returns no posts (very specific phrasing, niche
topic with low activity, or a query X doesn't recognize).

**Expected response:** Write a file with the header + "No results for
this query. Suggested refinements: ..." in the Notes section. The
operator refines and re-runs.

## E9. All posts below the engagement floor

**Scenario:** The query returns posts but every one is below the floor
(e.g., a 1K floor on a niche with mostly 200-view posts).

**Expected response:** Either:
- Write an empty file + "0 posts above the <N>K floor. Consider lowering
  to <lower> or broadening the query."
- If the operator specified the floor explicitly, write the file with all
  posts (no filtering) and note the floor-override in Notes.

Default: honor the explicit floor, write what passes. Surface the
filter-loss count.

## E10. Mixed-language result set

**Scenario:** The query returns posts in multiple languages (e.g., a
"Shopify" search returns English + Spanish + Portuguese results).

**Expected response:** Capture each post's text verbatim including
non-English. Note the language mix in the "Notes for the Content
Researcher" section. Do not translate.

## E11. Top vs Latest gives very different results

**Scenario:** The operator asked for a specific tab. The results skew
heavily toward one format on Top (mostly viral) vs Latest (mostly
real-time chatter).

**Expected response:** In the Notes section, compare briefly. If the
operator asked for Top, the result is what Top returns. Suggest Latest
as a follow-up if the Top result feels stale.
