---
type: article
source: @sairahul1 / popularization of the LLM 5-stage pipeline (GPT/Claude/Llama common architecture)
captured: 2026-06-22
tags: [article, llm-fundamentals, 5-stage-pipeline, data-quality, alignment, evaluation, mavis-design, mavis-as-llm]
status: processed
cross-refs: [02 Notes/patterns/agent-harness.md, 02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md, 03 Projects/Mavis EA Design/specs/mavis-as-llm-upgrades-2026-06-22.md]
---

# The 5-Stage LLM Pipeline — Distilled for Mavis

> Article digest. The thesis: **architecture is the LEAST important part of an LLM**. The same transformer block sits inside GPT, Claude, Gemini, and Llama. What separates them is data, training, alignment, and evaluation. This is the BUILD-side lens that complements the akash-pachaar article's RUNTIME-side lens. Together they give the full picture: harness = runtime, pipeline = build.

## The headline reframing (load-bearing for us)

> "The lie everyone believes about LLMs: most people think building an LLM is about the architecture. It is not. The real secret: data, training, and alignment. Architecture is one paragraph. Everything else is where real models are won and lost."

**For Mavis:** Mavis = MiniMax-M3 (the architecture) + a vault + skills + crons + the EA protocol. The architecture is shared across every Mavis session. What differentiates one session from another is the **data** (what's in the vault, what's in memory) and the **alignment** (SOUL.md, hard constraints, the EA tone). This is identical to the LLM situation. The dial-in cycle (56.6KB → 26.0KB always-on context) is a Stage 1 + Stage 2 operation — data quality + tokenization efficiency.

## The 5 stages — distilled to one line each

| # | Stage | The one-line summary | The Mavis analog |
|---|---|---|---|
| 1 | **Data** | Filter 1M GB of raw web text into a clean training corpus. Data quality > quantity. | The vault, memory files, skill corpus. Vault-health cron = the data filter. |
| 2 | **Tokenization** | Break text into ~32K-100K tokens via BPE. 1 token ≈ 0.75 words. | How context gets chunked for the context window. Skill descriptions, memory pointers, cold-start handoff. |
| 3 | **Training** | Predict the next token. Trillions of examples. Emergent grammar, facts, reasoning, code. | The Two-Track session loop. Pretraining = vault load. SFT = skill applied. |
| 4 | **Alignment** | SFT (prompt → ideal response) + RLHF (human preference signal). | SOUL.md + hard constraints + the EA tone. The "text predictor → assistant" step. |
| 5 | **Evaluation** | Perplexity during pretraining → human benchmarks (MMLU, Chatbot Arena) after alignment. No single score captures a good model. | The crons (contradictions, agent-disease-detector, vault-health) + Andre's direct feedback as the human benchmark. |

## The 5 mistakes (mapped to Mavis failure modes)

| # | LLM mistake | Mavis failure mode |
|---|---|---|
| 1 | **Obsessing over architecture.** Transformers are public. The architecture is the least important part. | Obsessing over prompts when the real leverage is in memory/vault/skills. The dial-in cycle was a correction. |
| 2 | **Treating data as a commodity.** Dirty data caps your ceiling. Top labs spend more on cleaning than modeling. | Vault entries treated as commodity captures. The vault-health cron + two-link-rule exist but isn't load-bearing yet. |
| 3 | **Skipping the scaling math.** ~20 tokens of training data per parameter is the optimal ratio. | Skills overstuffed with content they don't need (4-10KB skills that should be 1-2KB pointers into the vault). |
| 4 | **Stopping at SFT.** A fine-tuned model imitates. Without RLHF it never learns what people prefer. | Skills exist but no structured feedback loop captures Andre's mid-session corrections and routes them into skill evolution. |
| 5 | **Trusting perplexity after alignment.** Perplexity stops being meaningful the moment you run SFT. Switch to human benchmarks. | Trusting SOPs / procedures blindly without context. After SOUL.md is loaded, raw-capability checks become less useful than human-eval-style benchmarks. |

## Stage 4 alignment — the surprise

The article calls this the most under-appreciated stage. Key claim:

> "The surprising part: you need very little data. A few thousand examples is enough because the knowledge is already inside the pretrained model. SFT just teaches it to express that knowledge in the right format."

**For Mavis:** SOUL.md is ~12KB. The vault is ~5MB. The SFT-data-to-knowledge ratio is ~0.24%. Same shape. SOUL.md doesn't carry the knowledge — it teaches the *format*. The knowledge is the vault. The dial-in cycle extracted SOUL from 19.8KB → 12.6KB because the "extra" was actually long-term knowledge that belongs in the vault, not in always-on alignment instructions. **This validates Thesis 4 (long-term knowledge in vault, not in always-on context) from the LLM training lens.**

## The 5 niches share a pipeline — leverage insight

> "Same pipeline. Different data. Same tokenizer setup. Same transformer architecture. Same training loop. Same evaluation method. Different data → different expert → different product. That is the leverage."

**For Mavis:** Same architecture (MiniMax-M3), same harness (OpenCode + Mavis EA protocol), different SKILLS = different specialist. The 50+ skills in `~/.mavis/agents/mavis/skills/` are Mavis's "niches." `ea-cold-start` is the Coding Assistant niche. `ea-draft-approval` is the Legal Summarizer niche (raw input → plain English + red flags + risk level). `ea-state-audit` is the Medical Explainer niche (symptom → most likely + alternatives + escalation signal). **The niche framing is the right shape for thinking about Mavis skill design.**

## What the article explicitly tells you to do

- **Start small.** 15M parameters, WikiText dataset, free Colab GPU. Perplexity dropping from 800 → 50 in a few hours is the moment everything clicks.
- **Same pipeline, different data.** Don't redesign the harness. Swap the corpus.
- **5 stages, not 1.** Skipping any one breaks the whole thing.
- **Engineering, not just training.** "A great LLM is not trained. It is engineered."

## Connections to existing Mavis operational model

- **[[02 Notes/patterns/agent-harness]]** (akash-pachaar) — the RUNTIME lens. 12 components of the harness.
- **[[02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness]]** — the canonical runtime article. The Von Neumann frame (LLM = CPU, context = RAM, vault = disk, harness = OS).
- **[[01-PERMANENT/2026-06-22 - active-theses]]** — Thesis 3 (Skills beat agents) and Thesis 4 (long-term knowledge in vault) are the operational reflections of "data quality > quantity" and "SFT teaches format."
- **[[03 Projects/Mavis EA Design/minimax-token-dialin-ledger-2026-06-22]]** — the dial-in cycle as a worked example of Stage 1 + Stage 2 applied to Mavis.
- **[[03 Projects/Mavis EA Design/specs/mavis-as-llm-upgrades-2026-06-22]]** — the upgrade proposals this article inspired.

## What I'd push back on or sharpen

The article is a popularization (sairahul1's framing), not a primary source. The actual mechanics are older — Karpathy's "Let's build GPT from scratch" video, the GPT-2/GPT-3 papers, the Chinchilla scaling laws paper (Hoffmann et al. 2022, which is the source of the "20 tokens per parameter" claim). Use the popularization as the *trigger* for the framework; cite Karpathy + Chinchilla for the canonical references.

The "SFT teaches format" claim is overstated. SFT also bakes in safety behaviors, refusal patterns, and stylistic defaults that aren't strictly "format" — those are closer to the line between SFT and RLHF in modern post-training stacks (Anthropic's Constitutional AI, OpenAI's RLHF + RLAIF, etc.). The article's framing is right enough for our purposes but don't over-apply.

## Bottom line for Mavis

The 5-stage pipeline is the BUILD-side audit framework I was missing. The akash-pachaar article gave me the runtime harness. Together they answer:
- **Are we aligned with how the underlying technology actually works?** Yes — Mavis's structure (vault + skills + alignment layer + eval crons) is isomorphic to the 5-stage pipeline.
- **Where are the leverage points?** Stage 1 (data quality) and Stage 4 (alignment quality). Both already under active work (dial-in cycle + SOUL.md hygiene).
- **What's the audit framework?** Run the 5 stages as a self-check on Mavis. Identify gaps. Propose upgrades. Codify. (See upgrade spec.)
