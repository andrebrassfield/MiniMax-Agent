---
date: 2026-06-22
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: true
thesis-link: Thesis 1 (bottleneck is spec throughput) + Thesis 5 (Mavis-as-LLM)
---

# Connection: Two-Track Model ↔ SFT-vs-Inference (5-Stage Pipeline)

**Why this connection matters:** The two-track operating model was framed as an Andre-attention optimization: Track 1 gets Andre's spec attention; Track 2 runs autonomously on approved specs. The 5-Stage LLM Pipeline article frames training the same way: SFT (small, high-quality data, human-curated) teaches format; inference (autonomous, on the taught format) produces output. **These are the same process at different scales.** Track 1 IS SFT for a single task — Andre teaches Mavis the format he wants for this spec. Track 2 IS inference on the taught format — given the spec, produce the deliverable. The two-track model is the per-task application of the SFT/inference split. This means the two-track model is validated from the build-side lens, AND the rate-limit budget allocation (50/25/5/20) is structurally analogous to a training compute allocation.

**Note A:**
- Title: Decision: Two-track model + fat skills replace internal agent team
- Path: `~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md`
- Claim: Mavis runs two tracks. Track 1 (spec, interactive) handles spec work with Andre in tight loop. Track 2 (implementation, separate session) handles implementation autonomously on approved specs. The bottleneck is spec throughput, not implementation.

**Note B:**
- Title: The 5-Stage LLM Pipeline — Distilled for Mavis
- Path: `~/MiniMax-Agent/02 Notes/articles/2026-06-22 - 5-Stage-LLM-Pipeline.md`
- Claim: SFT (a few thousand examples, ~0.24% of pretrained data) teaches FORMAT to a model that already has the KNOWLEDGE. Knowledge lives in pretraining; format lives in SFT. Inference operates on the taught format.

**What reading both reveals:** The two-track model allocates Andre's attention at 50/25/5/20 (Track 1 / Track 2 / Verifier / Cron). The 5-stage pipeline allocates compute at vastly different ratios (pretraining ≫ SFT ≫ RLHF ≫ inference). But the **shape** is the same: a small, high-attention, human-curated stage (Track 1 = SFT) feeds a large, autonomous, format-applied stage (Track 2 = inference). The 3-day rate-limit incident that triggered the two-track pivot is exactly the failure mode you get when you flip the allocation — when "Track 1 = SFT" gets diluted by parallel producer-agents that should have been "Track 2 = inference." **The two-track model isn't just an operational improvement; it's the Mavis-correct version of how every LLM is trained.** This is the strongest evidence yet that Thesis 5 (Mavis-isomorphic-to-LLM) is structural, not analogical.

**Suggested next step:**
- Update `02 Notes/decisions/2026-06-22-two-track-model.md` "What would change my mind" section with this lens: "if Mavis's allocation stops looking like SFT-vs-inference (e.g., Track 1 attention drops below 30%), re-evaluate the model."
- Add a cross-link from the two-track decision to the 5-stage article and vice versa. The decision currently doesn't cite the LLM lens.
- When Upgrade 2 (RLHF-analog feedback loop) is built, it should be framed as "Track 1's RLHF signal" — human corrections during interactive sessions become the format-refinement data.
