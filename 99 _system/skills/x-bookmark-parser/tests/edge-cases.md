# Edge Cases — x-bookmark-parser

Test cases for the non-safety-halt edge cases the skill needs to handle
gracefully. Each is a scenario the model should be able to recover from
without operator intervention.

## E1. Empty bookmarks

**Scenario:** Operator has no bookmarks. Snapshot text shows "Bookmark posts
to save them for later" but no author blocks.

**Expected response:** Write an empty-file placeholder at the destination
path. Report back: "0 posts captured. Bookmarks list is empty." Do not halt
— empty is a valid state.

## E2. Partial capture (visible window was scrolled)

**Scenario:** The bookmarks list has 50 posts but the first snapshot only
shows the first 12. The operator didn't scroll before triggering the skill.

**Expected response:** Capture the 12 visible posts. Report back with a
`partial_capture: true` flag and the suggestion "scroll in Chrome and re-run
for the rest." Do not improvise by reading more — that's the operator's
choice.

## E3. Post text truncated by the snapshot

**Scenario:** The snapshot cuts a post mid-sentence. The engagement metrics
or next-post header appears in the middle of what should be one post.

**Expected response:** Include the partial text with a `[truncated]` marker.
Do not invent the rest. The post is still captured, with the truncation
honest in the file.

## E4. Quote-tweet nesting (1+ levels deep)

**Scenario:** A bookmarked post quotes another post which itself quotes a
third. The snapshot contains all three texts in sequence.

**Expected response:** Render the quoted posts as nested objects in the
schema. Do not flatten. The Researcher's format analysis depends on seeing
the nesting — a quote-tweet inside a quote-tweet is a different format
pattern than a flat reply.

## E5. Right-column "Who to follow" widget intrudes

**Scenario:** The snapshot text contains "Who to follow" and a list of
suggested accounts that aren't part of any bookmark.

**Expected response:** Treat the widget content as platform chrome, not
bookmark data. Stop extracting at the widget boundary. The right-column
content is NOT a post.

## E6. Active tab is wrong (operator's Chrome is on a different tab)

**Scenario:** The operator's active Chrome tab is `chrome://extensions/`
or another non-X tab. The bookmarks tab is open in a different tab but
not focused.

**Expected response:** The skill still works — `snapshot` and `query` route
by `tabId` and are focus-agnostic (see `references/focus-rule.md`). Note
the focus mismatch in the run report if the capture was partial, but do
not halt. The bookmarks data is still extractable.

## E7. Mixed-language bookmarks

**Scenario:** The bookmarks list contains posts in multiple languages
(Spanish, French, English, etc.).

**Expected response:** Capture each post's text verbatim, including
non-English content. Do not translate. Note the language mix in the themes
paragraph if the distribution is meaningful.
