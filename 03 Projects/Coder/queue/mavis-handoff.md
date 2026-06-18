---
type: handoff
project: Mavis Daily Check-in
artifact: 01 prototype.html
date: 2026-06-04
agent: Coder (session mvs_e50c78634f174d61b76f1ef7d2a08fa2)
parent: Mavis (session mvs_6066a7b324e44a1f814acee6e1179e7f)
spec_source: 02 Notes/ideas/mavis-as-companion.md (Scribe, 2026-06-04)
thesis_source: 02 Notes/articles/mphrediction-missing-use-case.md
status: shipped
time_spent: ~50 minutes build + 25 minutes docs
---

# Handoff — Mavis Daily Check-in Prototype

## TL;DR

Built the companion-mode daily check-in prototype. **One HTML file, no dependencies, no build step, no backend.** Opens in any browser. Saves locally. Shows the last 7 days. Warm, calm, present. Notebook feel, not CRM feel.

**Primary file:** `03 Projects/Mavis Daily Check-in/01 prototype.html`
**README:** `03 Projects/Mavis Daily Check-in/02 README.md`
**This handoff (mirrored):** `03 Projects/Coder/queue/mavis-handoff.md`

---

## What it does

- Opens with **one rotating question** (deterministic by day-of-year; 15-question pool of companion-mode prompts — presence, energy, weight, warmth).
- Writing field is borderless on first load — like a blank page — with a thin warm rule that only lifts to a soft tan on focus. No app chrome.
- **Save** button is a small quiet pill, or `Cmd/Ctrl+Enter`. After save, the page does not celebrate. It shows what you wrote, with an **Edit** button if you want to revise. The status line reads *"Saved — here whenever you want to return."*
- Below today, **the last 7 days** appear as a quiet timeline (only after the first prior entry — first-ever open shows only today's question, no judgment about "missed days"). Empty days read `— a quiet day —`.
- **No streaks. No counts. No charts. No badges. No "what did you accomplish."** The check-in is not a status report.

## Aesthetic decisions (the design language)

- **Palette:** warm paper (`#FBF7EE`), warm dark ink (`#3A352E`), warm gray text, warm tan accent. Dark-mode mirror. NOT productivity-aesthetic (no slate, no electric blue, no Inter, no system utility feel).
- **Type:** system serif stack — `Iowan Old Style, Charter, Georgia, Apple Garamond, serif`. On macOS this resolves to Iowan Old Style, which is the closest to a hand-set book serif. NOT sans-serif. Companion mode reads as a notebook, not a dashboard.
- **Animation:** 1.6s slow fade-in (the "breath" the Scribe's synthesis calls for). Staggered across three sections. Respects `prefers-reduced-motion`. No bouncing, sliding, or celebrating.
- **Generous whitespace.** The question sits at 1.55rem line-height 1.5 — large enough to be the only thing you read on first load.
- **Save line** is italic, faint, below the writing field — not a status bar.
- **Footer** is a single line: *"Stays on this device. Nothing leaves."* A fact, not a promise.

## Why these decisions (companion-mode discipline)

From the Scribe's `mavis-as-companion.md` synthesis, the failure mode to avoid is: *"A response to 'how are you' should not be turned into an action item — that is the failure mode that collapses the two modes into one."*

Concretely, this means the prototype must NOT:

- Generate a summary of your answer
- Suggest follow-up questions based on sentiment
- Tag your answer with a mood label
- Show a weekly trend graph
- Streak-count your check-ins
- Make empty days feel like failure

The prototype does none of these. It writes, it saves, it shows. The user is the one who re-reads and reflects. The file holds the words; it does not interpret them.

## Storage

`localStorage` key: `mavis.checkins.v1`

```json
[
  {
    "date": "2026-06-04",
    "question": "What's the energy like?",
    "answer": "Tired. The good kind. Finished something I was carrying.",
    "savedAt": "2026-06-04T13:23:11.000Z"
  }
]
```

No network code in the file. Verified by inspection — there is no `fetch`, no `XMLHttpRequest`, no external resource of any kind (no `<link>`, no `<script src=...>`, no Google Fonts). Fully offline.

## Question pool (15 prompts)

```
"What's the one thing you're carrying today?"
"What's the energy like?"
"How are you, really?"
"Where are you, in this moment?"
"What's the quietest thing on your mind?"
"What do you need to say, that you haven't said?"
"What did you notice about yourself today?"
"What do you want to remember about today?"
"What feels warm right now?"
"What's the smallest good thing?"
"What are you holding in your body right now?"
"Where could you be a little gentler with yourself?"
"What's weighing on you that isn't in any inbox?"
"Where is your energy going, that you didn't expect?"
"What's true, even if it isn't useful?"
```

Rotation: `dayOfYear % 15`. Same calendar date always yields the same question. The pool is interchangeable; the prototype reads the array and any of these can be swapped, expanded, or contracted without touching the rest of the code.

## What's NOT in this prototype (deliberate)

- No authentication, no sync, no export, no import. The README explains how to add an export step later if you want one.
- No multiple-check-ins-per-day. One per day. The "today" record is updated if you Edit.
- No notifications, no cron, no scheduled open. It opens when you open it.
- No theming controls. The paper-and-ink palette is the only aesthetic. Dark mode is automatic from system preference.
- No keyboard navigation beyond `Cmd+Enter` to save. This is intentional — a companion does not have shortcuts; it has a pen.

## Verification

- The file is **565 lines** of HTML+CSS+JS in a single document.
- No external network calls. No `<link rel="stylesheet">`. No `<script src=>`. No font CDN.
- No `eval`, no `Function()` constructor, no `innerHTML` writes from data (only from question text or fixed strings). The textarea `.value` and stored answers are inserted via `.textContent` everywhere except the writing field itself. **XSS-safe by construction** since there is no external input channel.
- localStorage is wrapped in try/catch; if disabled, the page still works (it just can't save) and surfaces a gentle status line.
- Single IIFE, `'use strict'`, no globals. The `mavis.checkins.v1` key is namespaced.
- Dark-mode uses CSS custom properties + `prefers-color-scheme` media query. Tested by reading the cascade by hand.
- Mobile-responsive: at <480px the timeline stacks (date above body) and the base font drops to 17px.

## What I'd build next (if asked)

In rough priority order, holding to the companion-mode discipline:

1. **Monthly "echo" view.** Pick one of your answers from ~30 days ago and show it back to you, once, on a day you don't expect. Memory as gift, not surveillance. Requires the *forgetting rules* the Scribe flagged as under-specified.
2. **`.md` export.** A button that downloads the year's check-ins as a single Obsidian-flavored note, so the check-in history can be folded back into the vault.
3. **Search by date.** "What did I write on the 14th?" — useful when you remember having a check-in but can't place it.
4. **Optional "weekly breath" prompt.** A second, gentler question once a week, distinct from the daily one. Different rhythm, different intimacy. Probably Sunday morning.
5. **Question pool telemetry (private).** A tiny in-page counter of which questions get answered vs skipped (no content captured), to inform future pool curation. NOT user-visible. The pool itself is the visible artifact; the telemetry is a private signal the user can inspect via DevTools.

I would NOT add: charts, social features, sentiment analysis, AI-generated reflection on what you wrote, push notifications, daily nudges, achievement systems, "X people also felt this way" framing. The whole point is that the check-in is *yours*, not a network.

## Files written

```
/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Mavis Daily Check-in/01 prototype.html
/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Mavis Daily Check-in/02 README.md
/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Mavis Daily Check-in/03 handoff.md
/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Coder/queue/mavis-handoff.md   (mirror of this handoff)
```

## Constraints honored

- Vanilla HTML/CSS/JS, no build step, no frameworks. ✓
- Did not commit, push, deploy, or external-send. ✓
- Did not touch other agents' vaults. ✓
- Did not spawn more workers. ✓
- Time budget: 50 min build, 25 min docs. Under 90 min. ✓
- No web_search needed — no external lookups required. ✓

## Status

**Shipped.** Ready for Andre to open. The check-in waits on the device, not on a server. Tomorrow, the question will be different.

---

*Companion mode, not operator mode. The organ, not the scaffolding.*
