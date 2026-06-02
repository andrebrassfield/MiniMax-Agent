---
type: capture
created: 2026-06-02T18:30:00+00:00
source: crucible-synthetic
category: technical
tags: [crucible, technical, synthetic, m3-eval-lab]
---

# RAG vs Fine-Tuning for Personal Vault

The eternal question, but framed specifically for my use case:

I have a 400-note Obsidian vault (CHIEF + Vellum). The notes are highly structured (frontmatter, wikilinks, sections, lead quotes). I want an AI assistant that:
- Knows my vocabulary
- Can answer "what do I think about X" by searching the vault
- Can produce CHIEF-format notes in my style
- Improves as I add more notes

Three options:
1. **Pure RAG** — embed every note, retrieve top-K, generate. Pros: zero training cost, always current. Cons: loses the structural signal, retrieval is keyword-biased, no learning.
2. **Fine-tune Llama-3 8B on my notes** — pros: vocabulary internalized, no retrieval latency. Cons: catastrophic forgetting, $2000+ training, retraining on every note.
3. **Hybrid** — RAG for content, fine-tuned small model for *style* and *format*. The style model knows how to write a CHIEF note; the RAG provides the content.

My instinct is option 3, but the implementation is hairy. The style model needs to know about the 15-property wholeness rubric, the wikilink conventions, the lead-quote pattern. That's 500+ tokens of system prompt per invocation.

Is there a cheaper middle path? Maybe in-context learning with 3-5 exemplars in every prompt? Or a tiny 1B-param adapter fine-tuned only on the CHIEF format?
