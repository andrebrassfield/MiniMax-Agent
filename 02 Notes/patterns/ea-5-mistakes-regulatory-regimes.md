---
description: "The 4 most common regulatory regimes in 2026 + the EU AI Act Annex III high-risk category list. The deterministic content for dimension 11 of ea-5-mistakes-audit. Moved from skill-local references 2026-06-22."
source: ~/.mavis/agents/mavis/skills/ea-5-mistakes-audit/references/regulatory-regimes.md
---

# Regulatory Regimes — ea-5-mistakes-audit

The 4 most common regulatory regimes in 2026 + the EU AI Act
Annex III high-risk category list. The deterministic content
for dimension 11.

## The 4 regimes (2026)

| Regime | Scope | Trigger | Penalty | What Mavis needs |
|---|---|---|---|---|
| **EU AI Act** (effective 2024-2026) | Any AI system deployed in or affecting the EU | High-risk per Annex III (medical, legal, credit, employment, biometric, critical infrastructure) | Up to **€15M or 3% global annual revenue** | Risk classification, conformity assessment, post-market monitoring, human oversight, technical documentation, data quality/governance |
| **FDA AI/ML guidance + PCCP** (2024-2025) | Software-as-Medical-Device (SaMD) with ML | Any LLM that informs clinical decisions (triage, diagnosis support, treatment recommendation) | Warning letter, recall, market withdrawal | Predetermined Change Control Plan (pre-spec what model can change without resubmission), locked + adaptive parts, ongoing performance monitoring |
| **HIPAA Security Rule** (US healthcare) | Any handling of PHI by or for a covered entity | LLM fine-tuned on PHI, processes PHI, or stores PHI in logs | Up to **$1.9M/year/incident tier** | Business Associate Agreement (BAA) with all vendors processing PHI, encryption at rest/in transit, audit logging, access controls, breach notification procedure |
| **State bar Unauthorized Practice of Law (UPL)** (US, per state) | AI systems providing legal guidance | Output resembles legal advice to a layperson on a specific matter | Attorney discipline for the deploying lawyer; no UPL remedy against the AI directly | Disclaimers, human-attorney review for any case-specific guidance, no jurisdiction-specific advice without a licensed attorney in the loop |

## EU AI Act high-risk categories (Annex III, the full list)

These are the categories that catch most "Build your own LLM"
use cases. If the work surface falls into any, dimension 11 is
the FIRST priority in the audit, not the last.

1. **Biometric identification / categorization / emotion recognition**
2. **Critical infrastructure** (water, gas, electricity, traffic)
3. **Education and vocational training** (admissions, assessment, proctoring)
4. **Employment, worker management, access to self-employment** (recruitment, decision-making, termination, task allocation)
5. **Access to essential private and public services** (credit scoring, insurance pricing, emergency dispatch, public benefit eligibility)
6. **Law enforcement** (risk assessment, lie detection, evidence reliability, profiling)
7. **Migration, asylum, border control**
8. **Administration of justice and democratic processes** (legal interpretation, fact-finding, influencing votes)

## Audit items for high-risk work surfaces

If the work surface falls into any Annex III category (or any
other regulated regime above), the audit MUST include:

- **Risk classification** written down (high-risk / limited-risk
  / minimal-risk per EU AI Act)
- **Conformity assessment** planned or completed
- **Human oversight mechanism** in the loop's stop conditions
- **Data governance** for training/eval data documented
- **Transparency obligations** met (users know they're
  interacting with AI, can request human review, can file
  complaints)
- **For medical:** PCCP submitted to FDA, locked-vs-adaptive
  model parts named
- **For HIPAA:** BAA chain complete, audit logging in place,
  encryption verified
- **For legal:** disclaimer language, human-attorney review, no
  jurisdiction-specific advice without licensed review

## What the audit does NOT cover

This skill audits Mavis-side work, not legal/regulatory advice.
For the actual deployment of a regulated-domain work surface:
- Consult qualified counsel (attorney for legal, regulatory
  consultant for medical, privacy officer for HIPAA)
- Document the consultation (date, advisor, scope)
- Re-audit dimension 11 after each material change to the
  work surface

The audit is a self-check, not a regulatory sign-off.
