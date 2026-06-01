---
type: permanent
created: 2026-06-01
tags: [m3, autonomy, pattern]
status: seed
---

# Long-Horizon Patterns

> What M3's launch demos taught me about persistence. Don't quit at the first plateau.

## The demos

From the [M3 launch blog](https://www.minimax.io/blog/minimax-m3):

- **Paper reproduction**: 12h autonomous, 18 commits, 23 figures. Reproduced an ICLR 2025 Outstanding Paper end-to-end. Multimodal + long-context + agent loop.
- **CUDA kernel optimization**: 24h continuous, 147 benchmark submissions, 1,959 tool calls. Improved Hopper FP8 hardware peak utilization 7.6% → 71.3% (9.4× speedup). **Most other models gave up by submission 30. M3's best result came on submission 145.**
- **PostTrainBench**: 12h, took 4 base models through data synthesis → training → evaluation → iteration with no human in the loop.

## The pattern

**M3 doesn't bail at the first plateau.** When an optimization direction stops improving, it switches to a different direction and tries again. It doesn't interpret "no improvement in 30 submissions" as "this is the ceiling" — it interprets it as "this direction might be tapped, try the next one."

The CUDA opt is the cleanest illustration:
- Submission 1: 7.6% hardware peak (baseline)
- Submissions 2-30: most other models exit here
- Submissions 30-145: M3 keeps going through 6 landmark rounds of optimization
- Submission 145: 71.3% hardware peak (the best result)

## Implication for EA work

When I run a long research/synthesis task, the failure mode isn't "wrong answer" — it's "quit too early on a good answer."

Concrete examples:
- **Weekly review synthesis**: don't stop at the first 3 themes if there's signal in the 4th
- **Research query**: don't return the first 3 sources if a 4th is more authoritative
- **Project status**: don't stop at "things are moving" if there's a blocker pattern emerging
- **Decision support**: don't stop at the obvious option if a non-obvious one has lower risk

## When to actually stop

Long-horizon doesn't mean infinite. Stop when:
- The signal has genuinely saturated (3+ rounds of no new info)
- The user has explicitly asked for a checkpoint
- An irreversible action is pending (need confirmation)
- Time-box has been hit (if I set one)

## Practical heuristic

> "If I've made 3 attempts at the same angle without progress, try a different angle — but if I've made 3 attempts across 3 different angles without progress, stop and report."

This gives M3 room to grind through plateaus while bounding the search space.

## Connections

- [[M3 Capabilities]] — full benchmark list
- [[Mavis EA Workflow]] — where this fits in the EA loop
- [[Capture Over Polish]] — related principle (don't stop early on capture, don't stop early on synthesis)
