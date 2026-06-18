# Data Schema — x-bookmark-parser

For every bookmarked post, extract these fields. If a field is not visible in
the snapshot, mark it as `unclear` rather than skipping or guessing.

| Field | Type | Source in snapshot |
|---|---|---|
| `index` | int | ordinal position in feed (1-based) |
| `author_name` | string | text immediately before `@handle` |
| `handle` | string | `@<username>` |
| `timestamp` | string | relative time string ("21h", "Jun 15") — keep raw, do not normalize |
| `post_url` | string | first `/status/<id>` link under the post |
| `type` | enum | `Text` / `Article` / `Quote` / `Reply` / `Repost` (infer from "·" + content indicators) |
| `title` | string? | if Article: the bolded first line |
| `pull_quote` | string? | the first 1-2 sentences if there's a strong hook; do not invent |
| `full_text` | string | everything between author block and engagement metrics |
| `engagement.replies` | int | first number in the engagement row |
| `engagement.reposts` | int | second number |
| `engagement.likes` | int | third number |
| `engagement.views` | int | the "K"-suffixed number (e.g., "15K", "607K") |
| `quoted_post` | object? | if present: nested schema (handle, full_text, link) |
| `media_attached` | bool | true if `photo/N` links are present in the post block |

**Do NOT extract:** profile pics, follower counts, the right-column "Who to
follow" / trending widgets, the bottom-of-page Terms of Service / Privacy
Policy links. Those are platform chrome, not bookmark content.

## Post-boundary detection (snapshot `text` field)

The snapshot's `text` field concatenates all visible text in DOM order. Post
boundaries are:

- **Start:** author name + handle + timestamp
- **End:** next author/timestamp line OR the right-column "Who to follow" widget

## Quote-tweet nesting

If a post quotes another post, render the quoted post as a nested object in
the schema. Do not flatten — the Researcher's format analysis depends on
seeing the nesting.
