---
description: "The x-ui-bouncer pre-flight + mid-flight modal dismissal procedure for X.com (and any React-controlled site with interstitials). Includes the JavaScript modal-scan, modal catalog, anti-patterns, and integration pattern. Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22 as part of Upgrade 1 aggressive refactor."
---

# x-ui-bouncer — Pre-flight + Mid-flight Modal Dismissal

## Pre-flight scan (run before every browser_navigate / browser_click / browser_type)

```js
() => {
  // 1. Generic close button (any modal)
  const closeButtons = document.querySelectorAll('[aria-label="Close"]');
  if (closeButtons.length > 0) {
    closeButtons[0].click();
    return { dismissed: 'generic-close', count: closeButtons.length };
  }
  // 2. X-specific modal indicators
  const indicators = ['Who to follow', 'Subscribe to Premium', 'Turn on notifications', 'Got it', 'Dismiss', 'Not now'];
  for (const indicator of indicators) {
    const buttons = document.querySelectorAll('button, [role="button"]');
    for (const b of buttons) {
      if (b.innerText && b.innerText.trim() === indicator && b.offsetParent !== null) {
        b.click();
        return { dismissed: indicator };
      }
    }
  }
  // 3. Modal overlay backdrop (skip if our compose dialog)
  const dialogs = document.querySelectorAll('[role="dialog"]');
  for (const d of dialogs) {
    if (d.querySelector('[data-testid="tweetTextarea_0"]')) continue;
    const close = d.querySelector('[aria-label="Close"]');
    if (close) {
      close.click();
      return { dismissed: 'dialog-close' };
    }
  }
  return { dismissed: 'none' };
}
```

Action: `dismissed: 'X' | 'none'` → wait 1s, then proceed with original action.

## Mid-flight retry (on timeout/failure)

1. Re-run pre-flight scan (modal may have appeared mid-action)
2. Wait 1s
3. Retry original action ONCE
4. If retry also fails → HALT, surface timeout + last 3 actions to Andre. Do not loop.

## Modal catalog (X.com, verified 2026-06-18)

| Modal | Trigger | Close | Bounceable |
|---|---|---|---|
| "Who to follow" | First interaction after login | `[aria-label="Close"]` | YES |
| "Subscribe to Premium" | After several posts | `[aria-label="Close"]` | YES (never click Premium itself) |
| "Turn on notifications" | After first like/follow | "Not now" / Close | YES |
| "Got it" (consent) | First post | "Got it" | YES |
| "X is now X" rebrand | First interaction after rebrand | "Got it" | YES |
| Compose / Reply (intended) | User action | (intended, not modal) | NO |
| "Save draft?" | Compose closed with text | Discard/Save | Bounceable if Discard; check Andre |
| "Login required" | Session expired | Log in | NO — HALT |
| "Rate limit exceeded" | High-volume activity | OK / toast | YES, but HALT sweep |
| "Post failed" | Network/policy | OK / retry | NO — HALT |

Pattern: bounceable = neutral "Close/Dismiss" that's safe to take. Non-bounceable = user decision required.

## Anti-patterns (do NOT)

- Click "Subscribe to Premium" — bounce the Close/Dismiss button only
- Dismiss Account/Profile menu drawers (user-initiated) — HALT
- Dismiss auth dialogs (login, 2FA) — HALT
- Loop bouncer more than once per action — modal storms HALT, not loop
- Dismiss "Confirm unsaved changes" during compose — HALT

## Integration pattern

```python
def safe_browser_action(action: Callable) -> Any:
    bouncer_scan()  # x-ui-bouncer pre-flight
    try:
        return action()
    except PlaywrightTimeoutError:
        bouncer_scan()  # mid-flight retry
        return action()  # one retry
```

Every new X skill: bouncer pre-flight is the first step.
