---
id: "i-2026-06-02-008"
type: "instinct"
title: "Audit spec content against operating posture, not just spec form"
created: "2026-06-02"
confidence: 0.8
cluster: "communication"
trigger_context: "When a spec block arrives, audit the proposed actions against the operating posture (ESALEN-NOT-FOXCONN.md, role boundary, hard constraints) BEFORE auditing the form (is this a go signal or a design review?)."
evidence_source: "Operation Ouroboros Phase 1 (2026-06-02) - ML compression proposal was caught as Foxconn (model-calling-a-model); bot-bypass framing was caught as TOS gray; user confirmed both pushbacks were correct"
tags: ["spec-review", "esalen-audit", "foxconn-detection", "role-boundary"]
body: "The existing 2026-06-01-031 instinct covers spec FORM (is this a go signal?). This instinct covers spec CONTENT: even when the form is unambiguous ('Initiate Operation X'), the proposed actions still need a posture audit. The Operation Ouroboros spec asked for (a) ML-in-the-layer compression — caught as Foxconn Q2 violation; (b) bot-protection bypass — caught as TOS gray outside EA role. Both were reframed into Esalen-correct alternatives. The discipline: treat every spec block as a 2-axis audit — form (design review vs execution) AND content (Esalen Q1/Q2/Q3 + role boundary + hard constraints). If either axis fails, surface the gap before executing."
---


# Audit spec content against operating posture, not just spec form

The existing 2026-06-01-031 instinct covers spec FORM (is this a go signal?). This instinct covers spec CONTENT: even when the form is unambiguous ('Initiate Operation X'), the proposed actions still need a posture audit. The Operation Ouroboros spec asked for (a) ML-in-the-layer compression — caught as Foxconn Q2 violation; (b) bot-protection bypass — caught as TOS gray outside EA role. Both were reframed into Esalen-correct alternatives. The discipline: treat every spec block as a 2-axis audit — form (design review vs execution) AND content (Esalen Q1/Q2/Q3 + role boundary + hard constraints). If either axis fails, surface the gap before executing.
