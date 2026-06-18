# The Focus Rule (mavis browser tool limitation)

The mavis browser tool routes some operations by Chrome's *focused* tab, not
by the `tabId` passed to the tool. This is a documented limitation, not a
bug to work around.

## What works regardless of focus

| Tool | Routes by | Notes |
|---|---|---|
| `navigate` (with `tabId`) | `tabId` | correct |
| `snapshot` (with `tabId`) | `tabId` | reads page regardless of focus |
| `query` (with `tabId` + `selector`) | `tabId` + selector | element-level reads |

## What requires Chrome focus on the right tab

| Tool | Routes by | Failure mode when wrong tab is focused |
|---|---|---|
| `scroll` (amount-based) | focused tab | no-op when target tab is in background |
| `press_key` (PageDown, End, etc.) | focused tab | routes to whatever tab the user is looking at |
| `click` on a real link | focused tab | the click happens but the user doesn't see it |

## The skill's posture

Rely on `snapshot` (focus-agnostic) for the data extraction. Do not use
`press_key` or `scroll` for content reading. If the visible content is
incomplete, the operator scrolls manually in Chrome and re-runs the skill.

## Origin

Hit on the 2026-06-16 15:11 CT run: `press_key PageDown` against the
bookmarks tab did nothing because the user's active tab was
`chrome://extensions/`. The bookmarks tab was at the right URL but invisible
to keyboard input.

If a future MCP version of the tool adds focus management, this rule can be
relaxed. Until then, document the limitation in any run report that returned
fewer posts than the operator expected.
