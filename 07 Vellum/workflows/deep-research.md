---
type: workflow
name: deep-research
trigger:
  - "deep research on [topic]"
  - "what do I know about [topic]"
cadence: on-demand
created: 2026-06-01
---

# Deep Research

## Purpose

Read everything in the vault on a specific topic and surface what I believe, what contradicts that, what's missing, and the single most important unasked question. This is the workflow you run before any major decision or when picking up a topic that's been dormant.

## When to use

- Before a major decision on a topic (the workflow forces you to find the contradictions)
- When picking up a project that's been dormant for weeks
- Before writing a brief, post, or talk on a topic — surfaces the gaps in your thinking
- When you suspect you're missing something obvious

## Prompt

> Read everything in my vault related to **[TOPIC]**. Search:
> - `02 Notes/` (all subfolders, including `_MOCs/`)
> - `03 Projects/` (all subfolders, including the Overview notes)
> - `06 Connections/` (synthesized insights)
> - `04 Resources/` (reference material, if any)
> - `01 Daily/` (for the last 90 days — surface any daily-note mentions)
>
> Tell me four things:
>
> **1. What I already believe** about this based on my actual notes — not generically. Quote my own words (with `[[wikilinks]]` back to source). If I have 3+ notes on the topic, I have a position. Name it.
>
> **2. What I have saved that contradicts that belief** — show me both sides from my own notes. A good belief is load-bearing; if there's no tension, I haven't been honest with myself. Name the contradiction explicitly. Don't soften it.
>
> **3. What perspective is clearly missing** from my research based on what I am and am not reading. Look at the gaps in my note coverage. If I have 5 notes on X and 0 on Y, and Y is a major counter-position to X, that's the gap.
>
> **4. What is the single most important question I have not asked yet** about this topic. Not a question I have asked before (use `[[02 Notes/questions/]]` to check). The kind of question that, if I sat with it for a week, would change my position.
>
> Be direct. Challenge me. Do not summarize what I already know. Do not give generic advice that could apply to anyone. **Every claim must be grounded in a specific note from my vault.** If you can't ground it, flag the gap.

## What "the most important unasked question" looks like

A bad output: "What are the risks?"
A good output: "You have 6 notes on Apple's Gemini pivot and 0 on Google's counter-move — what does Google do in the next 12 months if Apple wins the UX layer and they lose the model layer? You haven't asked this because you implicitly assumed Google stays at the model layer. What if they don't?"

The second is specific, grounded in the gap, and changes the question.

## Related

- `weekly-connections.md` — runs the lighter-weight synthesis weekly
- `daily-brief.md` — runs daily, surfaces a single question worth sitting with
