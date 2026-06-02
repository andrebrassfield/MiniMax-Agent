---
type: project
created: 2026-06-01
status: seed
tags: [project, mavis, architecture, execution, computer-use, m3]
---

# 02 Native Execution Layers

> How to design Mavis's OS-execution model on M3 — using the model's native vision and computer-use capabilities directly, instead of building a headless-script-only interface. The model sees the screen, drives the app, and reasons about visual feedback in the same loop.

## The principle: see, decide, act, verify — all in one model

Headless execution is a strong default (deterministic, fast, debuggable, API-stable), but it's not the *only* interface. M3's native multimodality plus computer use gives us a second tier — the *visual execution* layer. The architecture is:

```
M3 multimodal input ──> reasoning ──> action ──> visual feedback ──> reasoning ──> ...
```

Same model, same context, same memory. The loop doesn't split into "vision module" + "action module" + "verification module" — they're all one forward pass through M3. This is the architectural shift.

## The execution tier stack

Mavis should have a 3-tier execution model, used in order of preference:

### Tier 1: API-first (deterministic, preferred when available)

```bash
# Use the API for clean, deterministic operations
calendar.events.list(timeMin=now, timeMax=now+7d)
gmail.users.messages.send(to=..., subject=..., body=...)
sheet.values.update(spreadsheetId="...", range="...", values=[/* your 2D array of rows */])
```

**When to use:** the operation has a stable API, the data is structured, the user doesn't need to see anything visual, and there's no benefit to "the model looking at the screen."

**Why prefer it:** speed (sub-100ms), determinism (same call = same result), auditability (clear log of what was called with what args), recoverability (retry is trivial).

### Tier 2: Headless browser / scripted GUI (deterministic-ish)

```python
# Headless Playwright for web apps without good APIs
page.goto("https://app.example.com")
page.fill("#email", user.email)
page.click("button[type=submit]")
```

**When to use:** the web app has no API but a stable DOM/URL structure. The flow is well-defined and unlikely to change between runs. Speed matters but visual feedback is not needed.

**Tradeoff:** brittleness. CSS selector changes break flows. The script needs maintenance when the app ships an update.

### Tier 3: Visual computer use (M3 native, when nothing else works)

```
M3 sees screenshot ──> reasons about UI state ──> emits action ──> sees new screenshot ──> ...
```

**When to use:**
- No API exists (legacy enterprise software, government portals, niche SaaS)
- The visual state IS the source of truth (e.g., "what does the chart on screen look like right now")
- The workflow is one-off and not worth a headless script
- The user wants the EA to "just figure it out"

**Why it's different:** the same model that's doing the reasoning is doing the visual parsing. There's no separate OCR step, no separate element-detection model, no separate "is the click successful" verifier — the next screenshot is the verification.

## The visual execution harness

The right design for the M3 computer-use harness:

### Loop structure

```
1. Capture current screen state (screenshot + a11y tree)
2. Build prompt: current task + screen state + action history + tools
3. M3 reasons → emits action (click, type, scroll, keypress, wait)
4. Execute action via OS driver
5. Wait for stable state (heuristic: no new pixels for 300ms)
6. Capture new screen state
7. Return to step 2
```

The harness is small. The model is the brains. The OS driver is the body.

### Tool surface (what M3 should see)

Instead of "here's the entire pyautogui API," expose a small, documented set:

- `screenshot()` → returns the current screen
- `a11y_tree()` → returns the accessibility tree of the focused window (richer signal than pixels)
- `click(element_ref)` → where `element_ref` is from the a11y tree, not pixel coordinates
- `type(text)` → keyboard input
- `key(key_name)` → special keys (Enter, Tab, Cmd+C, etc.)
- `scroll(direction, amount)` → scroll a region
- `wait_for(stable_ms)` → wait for screen to stabilize
- `open_app(name)` → launch an app
- `set_clipboard(text)` / `get_clipboard()` → for cross-app data transfer
- `find_image(template)` → optional, for pixel-anchored clicks

That's ~10 tools. Each documented with one example call. Total tool surface < 200 tokens in the prompt. Compare to a generic pyautogui dump at 1500+ tokens.

### Why a11y tree > pixel coordinates

The OSWorld paper and the OSWorld-G grounding work both confirm: **mixed screenshot + a11y tree is materially better than pure screenshot.** Reasons:
- Element references (button labels, role, current value) are stable across theme changes
- A11y trees are smaller than screenshots, so they fit in context cheaply
- A11y semantics (e.g., "this is a dropdown with options X, Y, Z") are easier to reason about than pixel patterns

The M3 model's native vision is great for "what's on screen visually" but the a11y tree is the right substrate for "what can I click."

### Error recovery in the visual loop

GUI actions fail. The right design:

1. **Verify after every action.** A new screenshot is the verification. If the screen didn't change as expected, the action failed.
2. **Backtrack on failure.** OSWorld-Human shows top agents take 1.4-2.7× more steps than humans. Most of that extra is backtracking. Budget for it.
3. **Reflection on stuck state.** If the same screenshot has appeared 3 times in a row, the model is stuck. [[Reflexion Loop]]-style: "I tried X, the screen didn't change, the reason might be Y, let me try Z."
4. **Hard stop on error budget.** Max 30 actions per task. If not done, surface to user with a screenshot of where it's stuck.

## When to use which tier

| Signal | Tier |
|---|---|
| Operation has a clean API | 1 |
| Web app, stable DOM, multi-step flow | 2 |
| Legacy app, no API, no stable DOM | 3 |
| Visual state is the source of truth (e.g., "what does the chart look like") | 3 |
| One-off operation, not worth scripting | 3 |
| Real-time, sub-100ms response needed | 1 |
| User is watching and wants me to "just do it" | 3 |
| The action is destructive (delete, send, pay) | 1, always Tier 1 + explicit confirmation |

**The rule:** if Tier 1 works, use it. If Tier 2 is worth the maintenance, use it. Tier 3 is for "there's no other way" — and that's the place M3's computer use shines.

## What this replaces

- **Headless-only execution:** the old default assumed anything GUI-required was either scripted or out of scope. M3's computer use breaks that assumption. The new default is "can I see it and click it? Then I can do it."
- **Separate vision models:** the old vision pipeline (OCR → text → LLM) becomes a single forward pass. No "I OCRed the wrong region" failure mode.
- **DOM-only web automation:** the visual tier handles the apps where Playwright selectors don't exist or keep breaking. M3 sees the actual UI, not a model of it.

## What this does NOT replace

- **Tier 1 (APIs) for speed and determinism.** M3 computer use is 30× slower than `calendar.events.list`. Use the API when you have it.
- **Tier 2 (headless scripts) for high-volume flows.** A weekly billing reconciliation across 200 invoices is a Playwright job, not a computer-use job. Don't burn 200× the time on visual interaction when the script works.
- **The OS auth model.** M3's computer use doesn't bypass sudo, doesn't bypass TouchID for sudo escalation, doesn't bypass per-app permissions (Accessibility, Screen Recording on macOS). Those gates are real and right.
- **Human judgment on destructive actions.** Tier 3 should not be used for "delete this file" or "send this email" without explicit confirmation, because the error rate is non-trivial.

## The audit story

The 3-tier model has a clean audit trail:

- Tier 1: API call log (call, args, response, timestamp)
- Tier 2: Script execution log (script name, input, output, exit code)
- Tier 3: Screenshot sequence + action log (screenshot N, action N, screenshot N+1, ...)

For Tier 3, the screenshot sequence is the audit. Each step is reproducible: re-run the action sequence on the same starting state, get the same result (modulo model stochasticity). This is much better than a black-box "the agent did something."

## Connections

- [[00 Overview]] — the project hub
- [[01 Capability Boundaries]] — the M3 capabilities these MCPs exploit
- [[03 The Custom MCP Arsenal]] — the `macos-vision-anchor` MCP that makes this practical
- [[M3 Edge]] — the OSWorld-Verified 70.06% is the headline number here
- [[Multimodal GUI Loop]] — the deeper reasoning
- [[State Machine Failure Modes]] — when rigid scripting beats open-ended GUI
- [[Mavis EA Workflow]] — current execution patterns this is the design evolution of
- [[Vault Conventions]] — the "1M context as working memory" pattern is what makes the screenshot-history auditable

---
*Design document 2026-06-01. The visual tier is new for M3; the design will sharpen as production deployment reveals which abstractions actually earn their keep.*
