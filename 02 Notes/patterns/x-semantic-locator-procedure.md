---
description: "The 4-tier element-finding fallback for x-semantic-locator — a11y snapshot, data-testid, text content + bounding box, HALT. Includes the X.com element catalog (textbox, buttons, links). Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22."
---

# x-semantic-locator — The 4-tier Fallback

## Tier 1: Accessibility tree (preferred)

```bash
mavis mcp call playwright browser_snapshot '{}'
```

Match by **role + accessible name**. Output looks like:
```yaml
- textbox "Post text" [active] [ref=e375]
- button "Reply" [ref=e461]
- button "Close" [ref=e315]
```

Use the `ref=eNNN` in subsequent MCP calls. This is the load-bearing path — works for 90% of X.com elements.

## Tier 2: data-testid query (when a11y tree doesn't expose)

```js
() => {
  const candidates = [
    '[data-testid="tweetTextarea_0"]',
    '[data-testid="tweetButton"]',
    '[data-testid="tweetButtonInline"]',
    '[data-testid="reply"]',
    '[data-testid="retweet"]',
    '[data-testid="like"]',
  ];
  for (const sel of candidates) {
    const el = document.querySelector(sel);
    if (el) return { found: sel };
  }
  return { found: null };
}
```

Use the selector directly in `browser_click` or `browser_type`.

## Tier 3: Text content + bounding box (when no testid)

```js
() => {
  const wantText = 'Reply';  // or 'Post text', 'Post', etc.
  const buttons = document.querySelectorAll('button, [role="button"]');
  for (const b of buttons) {
    if (b.offsetParent !== null && b.innerText && b.innerText.trim().includes(wantText)) {
      const rect = b.getBoundingClientRect();
      return { text: b.innerText.trim(), x: rect.x, y: rect.y, w: rect.width, h: rect.height };
    }
  }
  return null;
}
```

Use the bounding box in `browser_click` (MCP accepts bounding-box coordinates for some tools).

## Tier 4: HALT (when all 3 fail)

Surface:
- The target element name
- The 3 tiers attempted
- Current page URL
- Last 5 actions taken
- A `browser_snapshot` dump for Andre

Andre (or future Mavis) decides: update catalog, patch bouncer, skip, or surface to user.

## Element catalog (X.com, verified 2026-06-18)

| Element | Tier 1 (a11y) | Tier 2 (data-testid) | Tier 3 (text) |
|---|---|---|---|
| Reply textbox (post page / timeline / compose modal) | `textbox "Post text"` | `[data-testid="tweetTextarea_0"]` | N/A |
| Post button (compose) | `button "Post"` | `[data-testid="tweetButtonInline"]` | `button:has-text("Post")` |
| Post button (reply) | `button "Reply"` | `[data-testid="tweetButtonInline"]` | `button:has-text("Reply")` |
| Reply count link | `link "X Replies"` | `[data-testid="reply"]` | `button:has-text("Reply")` |
| Close button (modal) | `button "Close"` | `[aria-label="Close"]` | N/A |
| Search box | `searchbox "Search query"` | `[data-testid="SearchBox_Search_Input"]` | N/A |
| Profile menu | `button "Account menu"` | `[data-testid="AppTabBar_Profile_Link"]` | `a[href="/DreTheSalesGuy"]` |
| X post status link | (no role) | `a[href*="/status/"]` | N/A |

## Output contract

```json
{
  "tier": 1,
  "ref": "e375",
  "selector": "[data-testid=...]",
  "bounding_box": {"x": 100, "y": 200, "w": 50, "h": 30},
  "method": "a11y-snapshot | data-testid | text-content"
}
```

The chief uses the returned ref/selector/bounding box in the next browser action.

## Integration

1. Try Tier 1 (a11y snapshot) — default
2. If Tier 1 fails, try Tier 2 (data-testid)
3. If Tier 2 fails, try Tier 3 (text content + bounding box)
4. If all 3 fail → Tier 4 HALT

When a new X skill is added, the 3-tier fallback is the default. The crons encode this procedure.

## Halt conditions

- All 3 tiers fail (element genuinely missing — UI update, modal, etc.)
- Tier 3 returns bounding box but `browser_click` with coordinates fails
- Element found but disabled (e.g., Reply disabled because textbox empty)
- 2+ consecutive locates fail (likely session issue)

The `scripts/locate.py` helper wraps this fallback for cron-driven invocation. The X cron chain runs bouncer (pre-flight) → locator (find target) → publish.
