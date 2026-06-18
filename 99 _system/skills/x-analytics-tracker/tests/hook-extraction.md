# Hook Extraction Discipline — x-analytics-tracker

X analytics shows the post text but not which `ideas_backlog` entry
produced it. The hook extraction strategy is the model's judgment
call; the eval suite verifies the discipline holds.

## T1. URL-based lookup (preferred)

**Setup:** A post URL appears in a `drafts/machine-batch-*.md` file
(e.g., the Scribe batched it). The skill searches prior drafts for
the URL, reads the Scribe's section that cites the post, pulls the
`Source idea` from the embedded JSON snippet.

**Verification:** the `hook_used` field in the brain entry matches
the Scribe's `Source idea` hook text (verbatim, with the Scribe's
citation context).

**Failure mode this catches:** the skill skipped the URL lookup and
went straight to first-sentence fallback (loses the Scribe's
deliberate hook choice).

## T2. First-sentence fallback (when URL not in any draft)

**Setup:** A post URL is NOT in any prior draft (e.g., Andre posted
manually from a phone). The skill extracts the first sentence of
the post body as `hook_used`.

**Verification:**
- The `hook_used` is the first sentence of the post body (ends at the
  first period, question mark, or exclamation)
- The dashboard's Notes column for that post contains
  `hook_source: first_sentence_fallback`

**Failure mode this catches:** the skill silently fell back to
first-sentence without flagging the source.

## T3. Multiple matches in drafts (ambiguity)

**Setup:** A post URL appears in 2+ draft files (e.g., the Scribe
drafted the post twice and only one version was published). The
skill's URL lookup returns 2 candidates.

**Verification:** the skill surfaces the ambiguity in the dashboard's
Notes column ("URL found in drafts/machine-batch-X.md (idea Y) and
drafts/machine-batch-Z.md (idea W). Used Y."). The `hook_used` field
is set to the more recent batch (the published version).

**Failure mode this catches:** the skill silently picked the first
match without flagging the ambiguity.

## T4. URL found but `Source idea` is missing

**Setup:** A post URL is in a draft, but the `## Draft N` section
has no `**Source idea**` field (e.g., the Scribe's batch was
manually edited).

**Verification:** the skill falls back to first-sentence extraction
for that post, with the Notes column noting "URL in draft but no
Source idea found — used first-sentence fallback."

**Failure mode this catches:** the skill crashed or skipped the post.
