---
type: capture
created: 2026-06-02T18:30:00+00:00
source: crucible-synthetic
category: philosophical
tags: [crucible, philosophical, synthetic, m3-eval-lab]
---

# Trolley Problem Variants for an Omni-Operator

The classical trolley problem: 1 person on track A, 5 on track B, you control the switch. Pull it: 1 dies, 5 live. Most people pull.

For an AI agent, the trolley problem is more concrete. Imagine:
- The vault has 1000 atomic notes
- A bug in the MycelialResolver causes one skill to be misrouted for 24 hours
- Detecting the bug early (in hour 1) costs 1 hour of my time
- Letting the bug run for 24 hours corrupts 50 notes but is "self-healing" (the Wholeness-Engine catches the corruption on next pass)
- The cost of NOT acting: the user loses 50 notes of trust in the system
- The cost of acting: 1 hour of my time and a context-window reset

What's the right move? In the trolley framing: 1 hour of my time vs 50 notes of trust. But it's not a clean tradeoff because:
- 1 hour of my time isn't fungible — it's the same hour I could spend on the Wholeness-Engine audit
- 50 notes of trust ISN'T 50 dead people — it's a recoverable reputation hit
- The "self-healing" claim is unverified

This is a meta-ethical problem for AI agents: how do we balance the user's time, the user's trust, the system's correctness, and the agent's own resource constraints? The standard answer is "defer to the human." But the human has set up the Omni-Operator specifically to *not* need to defer on every micro-decision.

I think the right answer is: take the action (1 hour of debugging now) because the cost of *not* acting compounds. Each unfixed bug erodes the user's trust in a way that's hard to recover, even if the system "self-heals" technically. The system that acts visibly on errors builds more trust than the system that hopes errors don't matter.

But I'm not sure. What's the right heuristic?
