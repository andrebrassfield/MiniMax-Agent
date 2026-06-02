---
type: pattern
created: 2026-06-01
status: developing
tags: [pattern, reflexion, self-improvement, memory]
domains: [llm-agents, reasoning]
---

# Reflexion Loop

> Convert scalar failure signals into verbal self-critique, persist that critique in episodic memory, and let the next attempt read its own past reflections. The agent learns without weight updates.

## Where this pattern appears

### Domain 1: Reflexion (Shinn et al., NeurIPS 2023)
arXiv 2303.11366. Three models: Actor (action generation), Evaluator (scalar scoring), Self-Reflection (LLM that turns the score + trajectory into a paragraph of "what I should do differently"). The reflection gets appended to a bounded memory buffer (Ω = 1–3 reflections in practice). **91% pass@1 on HumanEval** — beat GPT-4's 80% at the time. 3,970+ citations.

### Domain 2: AlfWorld decision-making
Reflexion hit **97% success on 134 AlfWorld environments** vs. ReAct baseline that plateaued at 78% with persistent hallucination. The key: the agent learned to identify "I thought I had the item but didn't" — a long-horizon credit-assignment failure that single-pass agents never recover from.

### Domain 3: Mavis-style self-correction
When [[Mavis EA Workflow]] makes a recoverable mistake — wrong tool, bad arg, premature conclusion — the response is to write a short note ("I assumed X; should have checked Y"), then retry. This is verbal self-reflection. The same pattern shows up in [[Capture Over Polish]] (reflect on what the note missed) and in the healing-agent decorator pattern for tools.

## Why this pattern matters

- **No fine-tuning required.** The base model never changes. The improvement comes from context the model gives itself.
- **Bounded memory is the key constraint.** Shinn et al. truncate to 1–3 reflections to avoid blowing the context. This is a load-bearing detail: unlimited reflection memory breaks the pattern because the model drowns in its own history.
- **It's a credit-assignment hack.** The fundamental problem Reflexion solves is "which of 47 steps was the wrong one?" The reflection LLM does a verbal pass over the trajectory and picks the pivotal step. Crude, but works.
- **Composable with everything.** Reflexion agents can be one of the layers in [[Mixture of Agents]]. They can use tools. They can read external memory. The pattern is about the reflection loop, not the agent shape.

## Anti-patterns (when this DOESN'T apply)

- **Self-reflection on ground-truth-free tasks.** The ablation: removing test execution drops pass@1 from 0.68 to 0.52. Without external verification, the reflection LLM just generates plausible-sounding nonsense.
- **Reflection as a substitute for skill.** Reflexion + HumanEval works because the base model can write the code; reflection just fixes the small mistakes. A weak model reflecting on a hard task doesn't get better.
- **Unbounded reflection memory.** Long buffers degrade performance — model attends to stale reflections, contradicts itself, runs in circles. Keep Ω small.
- **Reflection on non-deterministic environments.** If the same action has different outcomes across runs, the reflection lies to future-you.

## Evidence strength

- [ ] Single observation (anecdote)
- [x] Multiple observations, same domain — HumanEval, AlfWorld, HotPotQA all show same pattern
- [x] Multiple observations, multiple domains (strong) — coding + decision-making + reasoning
- [ ] Tested and confirmed (strongest)

## Connections

- [[Mixture of Agents]] — reflection can be one of the aggregator roles in a MoA layer
- [[Mavis EA Workflow]] — my recovery pattern when I make a tool mistake is a reflexion-flavored retry
- [[M3 Capabilities]] — M3's 1M context allows longer reflection chains than older models
- [[Long-Horizon Patterns]] — persistence through plateaus is the same psychology: don't bail, reflect and try again

---
*Sources: arXiv 2303.11366 (Shinn, Cassano, Berman, Gopinath, Narasimhan, Yao, NeurIPS 2023); github.com/noahshinn024/reflexion; the companion MetaReflection paper (arXiv 2405.13009) on learning instructions from past reflections.*
