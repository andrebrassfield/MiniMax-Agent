---
type: verifier-verdict
target: mavis + builder
project: directive-5
artifact: render-dossier.js (Fleet-Status Surface)
verdict: FAIL
reason: wrong-artifact — Mavis routing error
created: 2026-06-04
author: verifier
status: formal-record-of-routing-error
related:
  - "[[03 Projects/Builder/queue/verifier-build-handoff.md]]"
  - "[[03 Projects/Builder/queue/verifier-handoff.md]]"
  - "[[03 Projects/Fleet-Status Surface/07 Builder Deliverable.md]]"
tags: [verifier, fail, directive-5, routing-error, framework-drift, artemis]
---

# Verifier Verdict — Directive 5 — FAIL (wrong artifact)

> **One-liner:** The Builder built `99 _system/scripts/render-dossier.js` (a 167-line Node script for the Fleet-Status Surface renderer). The Directive 5 spec at `03 Projects/Builder/queue/verifier-build-handoff.md` calls for `artemis_status_board.html` (a single-file vanilla HTML/JS/CSS widget visualizing 5 Artemis claims). Mavis routed to the wrong project. The Verifier's verdict for Directive 5 is FAIL on **Fidelity** and **Hygiene / Spec Compliance** per Andre's adversarial input. The Fleet-Status Surface work itself is valid code and will be re-audited under a separate directive.

## Formal record of the routing error

| Layer | What Directive 5 spec asked for | What Builder delivered | Verdict |
|---|---|---|---|
| Artifact | `artemis_status_board.html` | `render-dossier.js` (Node) | **FAIL — Fidelity** |
| Stack | Single-file vanilla HTML/JS/CSS (per spec's hard constraints) | Node.js with `markdown-it` + 4 plugins | **FAIL — Spec Compliance** |
| Domain | 5 Artemis claims | Markdown → fade-animated HTML pipeline | **FAIL — Fidelity** |
| Deliverable shape | One `.html` file readable in a browser | `render-dossier.js` + 3 templates | **FAIL — Spec Compliance** |

The Builder did the work the *other* Builder was supposed to do (Fleet-Status Surface). Both pieces of work have legitimate value, but they are not interchangeable, and the spec compliance is not a matter of degree — it is a matter of whether the produced artifact matches the artifact the spec asked for.

## What the Verifier did during the contaminated audit window

I started the audit in good faith on the Builder's claimed handoff (the Fleet-Status Surface renderer). I read all 7 context files, re-ran the Builder's 28-check audit script, did adversarial probes (XSS, re-render fidelity, line-count claims, palette-vs-spec, contrast calc), and confirmed the demo HTML is real but **not reproducible from the current source files**.

I am preserving those findings as a separate file (`02 fleet-status-surface-deferred-findings.md`) so the Fleet-Status Surface audit can resume later with the evidence intact. They are **not part of this verdict** — the verdict is the framework-drift finding.

## Action items (for the re-dispatch)

1. **Mavis** (parent session): the Fleet-Status Surface renderer is a valid separate deliverable. Re-schedule its audit under a future directive with a Builder that was *actually* dispatched for that spec. The audit scope (~50-60 checks) and my deferred findings carry over.
2. **New Builder** (post-re-dispatch): consume `03 Projects/Builder/queue/verifier-build-handoff.md` as the spec, not `verifier-handoff.md`. The latter is the Fleet-Status Surface handoff. Build `artemis_status_board.html`.
3. **New Verifier audit** (when this session is re-tasked): apply the same 50-60-check scope (the 28 from the new Builder's handoff + the new Designer's 11 + 26 a11y + 5 Build Spec + 3 open questions) to the new artifact.

## What I am NOT doing

- I am not auditing the Fleet-Status Surface artifact as a Directive 5 deliverable.
- I am not modifying the Builder's code, the Designer's docs, or the demo.
- I am not issuing a second verdict on the Fleet-Status Surface renderer. That audit happens later, under its own directive, with the deferred findings file as a starting point.
- I am not retrying this with a different framing. The routing was wrong. The verdict is FAIL on framework drift. The end.

## File accounting

This verdict is written to two paths (per the redirect):
- `03 Projects/Verifier/audit/01 fleet-status-surface-audit.md` (formal audit record)
- `03 Projects/Verifier/queue/mavis-handoff.md` (Mavis handoff mirror)

The deferred Fleet-Status findings (separate audit, separate directive) are at:
- `03 Projects/Verifier/audit/02 fleet-status-surface-deferred-findings.md`

VERDICT: FAIL
