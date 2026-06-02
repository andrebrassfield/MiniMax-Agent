---
id: "i-2026-06-02-007"
type: "instinct"
title: "Headroom ratios are a chain, not a number"
created: "2026-06-02"
confidence: 0.85
cluster: "tools"
trigger_context: "When reporting compression or token-savings results from a multi-stage pipeline, report each stage's contribution separately, never the final ratio alone."
evidence_source: "Operation Ouroboros Phase 2 (2026-06-02) - MCP architecture page: regex 0.6%, M3-summary 71.2%, end-to-end 71.2%"
tags: ["compression", "headroom", "m3-summary", "reporting", "honest-metrics"]
body: "On the MCP architecture page, the regex layer gave 0.6% (content is mostly code blocks, not prose); the M3-summary layer gave 71.2%. Reporting '71.2% compression' alone would have been misleading — it implies the regex layer did the work, when in fact it was the M3 call. The right report is the chain: original_tokens → regex_tokens (ratio X) → m3_summary_tokens (ratio Y) → end-to-end (ratio Z). This is the honest version of the existing 2026-06-02-001 'Compression as a first-class layer' instinct. The discipline applies to any multi-stage pipeline where one stage's contribution could be hidden by another's headline number."
---


# Headroom ratios are a chain, not a number

On the MCP architecture page, the regex layer gave 0.6% (content is mostly code blocks, not prose); the M3-summary layer gave 71.2%. Reporting '71.2% compression' alone would have been misleading — it implies the regex layer did the work, when in fact it was the M3 call. The right report is the chain: original_tokens → regex_tokens (ratio X) → m3_summary_tokens (ratio Y) → end-to-end (ratio Z). This is the honest version of the existing 2026-06-02-001 'Compression as a first-class layer' instinct. The discipline applies to any multi-stage pipeline where one stage's contribution could be hidden by another's headline number.
