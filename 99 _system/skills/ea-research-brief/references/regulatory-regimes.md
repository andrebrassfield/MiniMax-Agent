# Regulatory Regimes — ea-research-brief

The 4 named regulatory regimes that catch most "Build your own LLM"
use cases. Pre-flight check that runs BEFORE dispatching the worker.
Full table per `ea-5-mistakes-audit` Addition 11.

## The 4 regimes

| Regime | Trigger | What Mavis needs |
|---|---|---|
| **EU AI Act** | Biometric ID, employment screening, credit scoring, law enforcement, education access, critical infrastructure, migration, justice/democracy | Risk classification (high-risk = Annex III) + conformity assessment + post-market monitoring. HALT if the brief will be deployed in any of these contexts. |
| **FDA AI/ML + PCCP** | Medical device, clinical decision support, AI/ML that informs diagnosis/treatment | Locked-vs-adaptive classification, PCCP (Predetermined Change Control Plan) submission, real-world performance monitoring. HALT if the brief is the precursor to a regulated medical AI. |
| **HIPAA Security Rule (45 CFR Part 160/164)** | PHI (Protected Health Information) — patient data, claims, clinical notes, anything HIPAA-covered | BAA in place, audit logging, encryption at rest/in transit, 6-year retention. HALT if PHI is in scope and BAA is not confirmed. |
| **State-bar UPL (Unauthorized Practice of Law)** | Legal advice, legal document drafting, any output a non-lawyer would rely on as legal counsel | Lawyer-in-the-loop requirement, ABA Model Rule 5.5 compliance, jurisdiction-specific UPL statutes. HALT if the brief is the precursor to legal advice. |

## The halt rule

- Any regime hit + no human-in-the-loop gate → HALT, surface to Andre, do not dispatch
- Any regime hit + the brief is for an external client → HALT, surface to Andre
- No regime hit + the brief is internal → proceed to Stage 3

The regime check is Stage 2, not Stage 5. If the regulatory frame
applies, the entire deliverable shape may change (locked-vs-adaptive
design, audit logging, retention). Retrofitting regulatory reality
is 10x cost. Pre-flight is cheap.

## Why the 4 regimes (not more)

These 4 catch the highest-risk patterns in the work Mavis is likely
to dispatch. Other regimes (FAA, FinCEN, FTC, etc.) apply to
specific verticals but are less common. When in doubt about
applicability, run the regime check anyway and let Andre make the
call.
