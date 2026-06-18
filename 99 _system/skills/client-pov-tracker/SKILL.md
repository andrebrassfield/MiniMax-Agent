---
name: client-pov-tracker
description: |
  Codifies the Dre Builds POV (point-of-view) for an onboarded client. When
  a new `03 Projects/Clients/[ClientName]/` directory is created, this skill
  ingests the Friction Signals from `03 Projects/X-Content-Engine/briefs/local-audit-*.md`
  reports, cross-references them against the Agentic Standard defined in the
  SMB AI Maturity Report (§2), categorizes friction by urgency (Tier 1 =
  high-urgency revenue leak, Tier 2 = medium-leverage, Tier 3 = low-leverage),
  and writes `03 Projects/Clients/[ClientName]/pov-roadmap.md` with: friction
  being solved, target ROI, the Dre Builds technical solution (mapped to the
  4-week Blueprint phases), outcome-pricing commitment, and the 5 measurement
  numbers baseline. Triggers: "onboard a client", "POV for [ClientName]",
  "build the client roadmap", "Dre Builds POV", or when a new
  `03 Projects/Clients/[ClientName]/` directory is created. Read-mostly:
  reads briefs and writes one roadmap per client. Does not modify FSMs,
  inventory, or external systems.
---

# client-pov-tracker

The Dre Builds point-of-view (POV) for a single onboarded
client. The output is a single roadmap file at
`03 Projects/Clients/[ClientName]/pov-roadmap.md` — the
kickoff artifact the agency uses to align with the client.
The ongoing tracking is `agent-deployment-monitor`'s job.

## When to run

**Triggers:**
- "onboard a client" / "onboard [ClientName]"
- "POV for [ClientName]" / "build the POV"
- "Dre Builds POV" / "client POV"
- "build the client roadmap" / "client roadmap for [ClientName]"
- "create [ClientName]/pov-roadmap.md"
- Auto-triggers when a new `03 Projects/Clients/[ClientName]/`
  directory appears (operator workflow: create the dir, then
  dispatch the skill)

**Do NOT run for:**
- A client that has not yet been onboarded (no
  `03 Projects/Clients/[ClientName]/` directory exists and the
  operator has not yet named the client)
- A prospect that is still in the "audit" stage
  (`local-competitor-auditor` produces intelligence, not a POV
  — the POV is for post-conversion clients only)
- A Dre Builds internal project (this skill is for client
  engagements, not for tracking the agency's own work)
- A client that already has a POV (re-running HALTs — the POV
  is a one-shot artifact; use `agent-deployment-monitor` for
  ongoing tracking)

## Inputs

| Input | Default | Required |
|---|---|---|
| Client name | — | **yes** |
| City | inferred from local-audit briefs | yes if no audit briefs exist |
| Niche | inferred from local-audit briefs | yes if no audit briefs exist |
| Local-audit briefs | all `briefs/local-audit-*.md` | no — operator can scope to specific city/niche |
| Whitepaper path | `03 Projects/Mavis EA Design/reports/2026-Q3-SMB-AI-Maturity-Report.md` | no |
| Persona / voice | `03 Projects/X-Content-Engine/agents/persona.md` | no |
| Target ROI override | uses whitepaper §4 math, scaled | no |
| Outcome-pricing % | 10-20% of captured revenue | no |
| Install start date | operator-provided | no |
| Existing client dir | `03 Projects/Clients/[ClientName]/` | yes — must exist or be creatable |

**Empty local-audit halt (load-bearing):** if no
`briefs/local-audit-*.md` files exist, the skill cannot
categorize Friction Signals. HALT with: "No local-audit
briefs found. Run `local-competitor-auditor` on the client's
city + niche first, then re-dispatch `client-pov-tracker`."
The POV without local-audit data is not the POV; it's a
generic pitch deck.

**Multiple-audit disambiguation:** if multiple local-audit
briefs exist for different city/niche combos, the operator
must specify which audit(s) the client falls into.

**Stale-audit warning:** if the most recent local-audit
brief for the client's city/niche is >90 days old, surface a
staleness warning in the roadmap's "Caveats" section. Do
not halt.

## The 7-section roadmap (the load-bearing structure)

The output is one markdown file with these 7 sections, in
this order. Full template (per section's purpose, what to
include, the source-citation pattern) in
`references/roadmap-template.md`.

| # | Section | Source |
|---|---|---|
| 1 | The Friction (Tier 1 / 2 / 3) | `local-audit-*.md` briefs + Friction Filter |
| 2 | The Agentic Standard | whitepaper §2 (4 criteria, applied to this client's stack) |
| 3 | Target ROI (the math) | whitepaper §4 (line items, capture assumption, payback) |
| 4 | The Blueprint (4 phases) | whitepaper §5 (Baseline → Voice → Inventory → Outcome) |
| 5 | The 5 Measurement Numbers | Forbes/QuickBooks dissection, whitepaper §5.1 |
| 6 | The Outcome-Pricing Commitment | whitepaper §2.4 (the agency's billing model) |
| 7 | Caveats and open questions | staleness warnings, ambiguities, novel frictions |

The 3-tier Friction Filter (load-bearing taxonomy) in
`references/friction-filter.md`. The 4 Agentic Standard
criteria in `references/agentic-standard.md`. The 4-week
Blueprint phases in `references/blueprint-phases.md`. The
§4 ROI math defaults + scaling per client in
`references/roi-math.md`.

## The 9-step procedure (overview)

The full 9-step procedure with bash commands lives in
`references/procedure.md`. The high-level flow:

1. Verify inputs (client dir exists, briefs exist, whitepaper
   exists)
2. Read the local-audit briefs (extract friction signals,
   severity, install recommendation)
3. Categorize by tier (per the Friction Filter taxonomy)
4. Read whitepaper §2 (Agentic Standard) + §4 (Build Gap
   Quantified)
5. Generate the Target ROI table
6. Map friction → Blueprint phase
7. Write the `pov-roadmap.md` (atomic write)
8. Update the clients ledger (`03 Projects/Clients/_ledger.mdl`)
9. Return summary to operator

## Hard constraints

1. **No fabrication.** Every friction signal must come from a
   real local-audit brief. Every ROI number must be traceable
   to whitepaper §4 math (or to client-provided data explicitly
   cited).
2. **No public publishing.** The `pov-roadmap.md` is for
   client engagement, not for X drafts. The sales-audit-hook
   template is the X-facing analog.
3. **No live-system modification.** This skill writes markdown
   only. It does not call ServiceTitan / Jobber / Shopify APIs.
   It does not send emails. It does not run voice agents. The
   Blueprint's Phase 2-4 are future deployments.
4. **Single document per client.** The POV is a kickoff
   artifact. Re-running HALTs and surfaces — use
   `agent-deployment-monitor` for ongoing tracking.
5. **Empty local-audit halt (HARD).** No briefs = no POV.
   Halt and surface.
6. **Stale-audit warning, not halt.** Audit >90 days old →
   Caveats section, do not halt.
7. **Atomic write.** Use temp-write-rename (or `Write` tool
   which is atomic by default) to avoid corruption.
8. **Append to clients ledger.** Always append a one-line
   entry to `_ledger.mdl` after a successful write.

## When the skill HALTs

Halt and escalate to Andre when:
- No local-audit briefs exist (H1 — empty local-audit halt)
- Multiple city/niche audits match (H2 — disambiguation)
- Whitepaper path missing (H3 — ask for the path)
- Persona file missing (H4 — ask for the path)
- POV already exists for this client (H5 — redirect to
  `agent-deployment-monitor`)
- Atomic write fails (H6 — surface)
- Clients ledger write fails (H7 — surface)

The skill is a diagnostic, not an authorization. The
operator decides the action.

## Verification (post-write)

After writing the roadmap, verify:

1. `ls -la` confirms `pov-roadmap.md` exists with non-zero size
2. The file has all 7 sections
3. The Target ROI table has ≥3 line items
4. The 5 measurement numbers are in Section 5
5. The Agentic Standard is applied specifically to this
   client's stack (Section 2 — not generic)
6. The Outcome-Pricing commitment is stated (Section 6)
7. The Caveats section is non-empty if any audit was >90 days
   stale
8. The clients ledger was appended (or created)

## Cross-reference

- `references/roadmap-template.md` — the full 7-section template
- `references/friction-filter.md` — the 3-tier taxonomy
  (load-bearing)
- `references/agentic-standard.md` — the 4 Agentic Standard
  criteria
- `references/blueprint-phases.md` — the 4-week install phases
- `references/roi-math.md` — whitepaper §4 math defaults +
  scaling
- `references/procedure.md` — the 9-step procedure with bash
- `tests/roadmap-completeness.md` — 7-section sanity check
- `tests/audit-discipline.md` — no-fabrication, whitepaper-
  cited, ledger-appended checks
- `local-competitor-auditor` — the upstream skill that
  produces the Friction Signals. Run the auditor first.
- `agent-deployment-monitor` — the downstream skill for
  ongoing client tracking after the POV kickoff
- The 2026 SMB AI Maturity Report — the load-bearing
  reference for §2 (Agentic Standard) and §4 (Build Gap
  Quantified)
- The Dre Builds persona — the narrative voice for the roadmap
