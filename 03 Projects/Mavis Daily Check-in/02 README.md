# Mavis Daily Check-in — Prototype

> A small, daily, low-friction moment of presence. Companion mode, not operator mode.

This is the first companion-mode artifact of Mavis — the AI-as-companion prototype that demonstrates the mphrediction thesis: *the biggest use case of AI is emotional survival, not productivity.*

It is intentionally minimal. No build step. No frameworks. No backend. Open the file, write, save, return tomorrow.

---

## How to open it

The file is fully self-contained. Three options, pick whichever you prefer:

1. **Double-click** `01 prototype.html` — it opens in your default browser.
2. **Drag** the file into any open browser window.
3. **From the terminal** (if you keep this in the vault):
   ```bash
   open "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Mavis Daily Check-in/01 prototype.html"
   ```

No server. No install. Nothing to set up.

---

## How it works

### The ritual

- Each day, the page opens with **one question**. The question rotates deterministically by day-of-year across a pool of 15 companion-mode prompts — presence, energy, weight, warmth. The same date always gives the same question.
- You write a few words. A sentence is fine. There is no minimum and no character count.
- Click **Save** (or press `Cmd+Enter` / `Ctrl+Enter`). The answer is stored on your device.
- Tomorrow, the question is different. The previous seven days are quietly visible below today, in a warm timeline.
- If you've already written today, the page shows what you wrote, with an **Edit** button if you want to revise it.

### The design primitives (companion, not operator)

- **Warm paper background, warm dark ink, serif typography.** The feel is a notebook, not a CRM.
- **No streaks, no counts, no charts, no badges.** There is no progress metric to optimize. The check-in is a moment, not a stat.
- **No "next steps" generated from your answer.** A response to "how are you" is not turned into an action item. That collapse — turning feeling into task — is the failure mode this prototype refuses.
- **Slow fade-in on first load.** Not a motion vocabulary — breath. Respects `prefers-reduced-motion`.
- **One question at a time.** Not a form. Not a survey. A single opening.
- **Quiet empty days** in the timeline — `— a quiet day —`. No "you missed yesterday." No judgment.
- **Dark mode** follows system preference. Same warmth, deeper paper.

### The data model

Everything is stored locally in `localStorage` under the key `mavis.checkins.v1`:

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

The privacy line in the footer — *"Stays on this device. Nothing leaves."* — is a fact, not a promise. There is no network call anywhere in the file. The check-in cannot phone home because it has no phone.

### Keyboard shortcuts

- `Cmd+Enter` (macOS) / `Ctrl+Enter` (other) — save the current draft.
- `Tab` — move from the textarea to the Save button.

---

## What's next (companion-mode roadmap)

This is a prototype. The next moves should grow in the same direction — *presence*, not *productivity*. Possible next steps, in rough order:

1. **Try it for a week.** See which questions land, which feel performative, which you skip. Use that signal to refine the question pool.
2. **Add a gentle "welcome back" if you skip a day.** Not a streak message — a single soft line, the way a friend might say "hey, haven't seen you in a bit."
3. **Add a "what was the question on [date]" retroactive view.** For when you want to find a moment you remember having but can't place. Search by date, see the question and your answer.
4. **Add export to a `.md` file.** So the year's check-ins can be folded into the Obsidian vault as a single long-form note. `01 Daily/2026-checkins.md` or similar.
5. **Add a monthly "echo" view.** Pick one of your answers from 30 days ago and quietly show it back to you, once, on a day you don't expect it. Memory as gift, not surveillance. This requires *forgetting rules* — the under-specified discipline from the Scribe's `mavis-as-companion.md` synthesis.
6. **A second profile: the philosopher profile** could read from this file (with permission) as one input to its long-form conversational layer — the system-of-record for the emotional arc.

What this prototype should **never** become:
- A productivity dashboard with charts and weekly trends
- A social feed (even private) with engagement metrics
- A prompt-injection surface — no external content ever renders in this page
- A "smart" predictor that nudges you with patterns you've already articulated

The mphrediction thesis is the boundary: *AI as presence, not output.*

---

## Files in this project

- `01 prototype.html` — the working file. Open this in a browser.
- `02 README.md` — this file.
- `03 handoff.md` — the handoff note for the Coder queue and Mavis's next pass.

---

*Captured during the Night Flight, 2026-06-04, in the spirit of the Scribe's `mavis-as-companion.md` synthesis: the EA mission has two layers now. This prototype is the *organ* of the second layer.*
