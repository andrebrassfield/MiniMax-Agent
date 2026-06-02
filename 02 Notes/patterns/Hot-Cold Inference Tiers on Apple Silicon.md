---
type: capture
created: 2026-06-02T18:30:00+00:00
source: crucible-synthetic
category: technical
tags: [crucible, technical, synthetic, m3-eval-lab]
---

# Edge Inference Deployment on M3 Max

Trying to deploy a continuous AI loop on the MacBook without cooking the laptop. The M3 Max has:
- 16-core CPU (12P + 4E)
- 40-core GPU
- 16-core Neural Engine
- 128GB unified memory
- Software: mlx-lm, llama.cpp, Ollama

The naive deployment (always-on 70B model) draws 40W+ and the fans spin up. The smart deployment:
- Hot path: 8B model always warm (~3GB RAM, ~5W)
- Cold path: 70B model on-demand, unloaded after 60s idle
- Decision trigger: based on the routing hint (MycelialResolver)

The 8B model handles 80% of requests. The 70B handles the long-form (PatternForge generative codes, Wholeness-Engine rubric grading). The trigger is the MycelialResolver's flow_score — high flow_score on a skill means use 8B; low or no entry means use 70B for novelty.

Three open questions:
1. How do I measure the 70B cold-start penalty vs the latency savings from better answers? If 70B takes 8 seconds to warm and 8B answers 80% correctly in 200ms, the breakeven for switching is non-trivial.
2. Can I pre-warm the 70B during a "thinking period" (e.g., when the user is typing) so it's hot by the time they hit enter? M3 has 16GB/s memory bandwidth, so loading 40GB of weights takes ~2.5s. That fits a typical typing pause.
3. The Neural Engine is good for batch inference but not for autoregressive decode. Can I use ANE for the first 50 tokens (high parallelism) and GPU for the rest (low latency)?

I want a blog post on this, but first I need the math right. The "always-on 8B + on-demand 70B" pattern is the obvious answer; the interesting questions are the cold-start mitigation and the ANE/GPU split.
