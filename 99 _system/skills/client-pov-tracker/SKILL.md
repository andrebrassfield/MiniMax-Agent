---
name: client-pov-tracker
description: Codifies the Dre Builds POV (point-of-view) for an onboarded client. When a new `03 Projects/Clients/[ClientName]/` directory is created, this skill ingests the Friction Signals from `03 Projects/X-Content-Engine/briefs/local-audit-*.md` reports, cross-references them against the Agentic Standard defined in the SMB AI Maturity Report (03 Projects/Mavis EA Design/reports/2026-Q3-SMB-AI-Maturity-Report.md §2), categorizes the friction by urgency (Tier 1 = high-urgency revenue leak, Tier 2 = medium-leverage, Tier 3 = low-leverage), and writes `03 Projects/Clients/[ClientName]/pov-roadmap.md` with: friction being solved, target ROI, the Dre Builds technical solution (mapped to the 4-week Blueprint phases), outcome-pricing commitment, and the 5 measurement numbers baseline. Triggers on phrases like "onboard a client", "POV for [ClientName]", "build the client roadmap", "Dre Builds POV", or when a new `03 Projects/Clients/[ClientName]/` directory is created. Read-mostly: it reads briefs and writes one roadmap per client. Does not modify FSMs, inventory, or external systems.
---

# Client POV Tracker

## What this skill does

Codifies the **Dre Builds point-of-view (POV) for a single onboarded client.** The output is a single roadmap file at `03 Projects/Clients/[ClientName]/pov-roadmap.md` that:

1. **Categorizes the Friction Signals** found in local-competitor-auditor reports (`briefs/local-audit-*.md`) by urgency (Tier 1 / 2 / 3, per the local-competitor-auditor skill's Friction Filter).
2. **Cross-references** the friction against the **Agentic Standard** (idempotency, real-time sync, FSM-native, outcome-priced) defined in §2 of the SMB AI Maturity Report.
3. **States the target ROI** for the install, with the math anchored to the whitepaper's Section 4 (Build Gap Quantified) — adjusted for the client's city, niche, and any client-specific data the operator has provided.
4. **Maps each friction → Dre Builds technical solution** (the 4-week Blueprint phases from §5 of the whitepaper: Baseline Audit → Voice Path → Inventory/Ops Path → Outcome Loop).
5. **Commits to outcome-pricing** at the customer layer (per §2.4 of the whitepaper).
6. **Baselines the 5 measurement numbers** (time per task, output quality, revenue per AI-supported activity, error rate, tool cost vs value) per the Forbes/QuickBooks dissection cited in §5.1 of the whitepaper.

The roadmap is the **single document the agency uses to align with the client** at the kickoff meeting, and the **single document the operator references** when making weekly progress calls.

## When to run

**Trigger phrases:**
- "onboard a client" / "onboard [ClientName]"
- "POV for [ClientName]" / "build the POV"
- "Dre Builds POV" / "client POV"
- "build the client roadmap" / "client roadmap for [ClientName]"
- "create [ClientName]/pov-roadmap.md"
- The skill also auto-triggers when a new `03 Projects/Clients/[ClientName]/` directory appears (operator workflow: create the dir, then dispatch the skill).

**Do NOT run for:**
- A client that has not yet been onboarded (no `03 Projects/Clients/[ClientName]/` directory exists and the operator has not yet named the client).
- A prospect that is still in the "audit" stage (the local-competitor-auditor skill produces intelligence, not a POV — the POV is for post-conversion clients only).
- A Dre Builds internal project (this skill is for client engagements, not for tracking the agency's own work).

## Inputs

| Input | Default | Required |
|-------|---------|----------|
| Client name | (none — must be specified) | **yes** |
| City | (inferred from local-audit briefs; if multiple cities, ask) | yes if no audit briefs exist |
| Niche | (inferred from local-audit briefs; if multiple niches, ask) | yes if no audit briefs exist |
| Local-audit briefs to ingest | all `briefs/local-audit-*.md` | no — operator can scope to specific city/niche |
| Whitepaper path | `03 Projects/Mavis EA Design/reports/2026-Q3-SMB-AI-Maturity-Report.md` | no — defaults to the canonical whitepaper |
| Persona / voice | `03 Projects/X-Content-Engine/agents/persona.md` | no — used for the narrative voice of the roadmap |
| Target ROI override | (none — uses whitepaper §4 math, scaled) | no — operator can specify a different number |
| Outcome-pricing % | 10–20% of captured revenue (per whitepaper §4 footnote) | no |
| Install start date | (operator-provided) | no |
| Existing client dir | `03 Projects/Clients/[ClientName]/` | yes — must exist or be creatable |

**Empty local-audit halt.** If no `briefs/local-audit-*.md` files exist, the skill cannot categorize Friction Signals. **HALT** and surface to the operator with: "No local-audit briefs found. Run `local-competitor-auditor` on the client's city + niche first, then re-dispatch `client-pov-tracker`." This is a hard halt — the POV without local-audit data is not the POV; it's a generic pitch deck.

**Multiple-audit disambiguation.** If multiple local-audit briefs exist for different city/niche combos, the operator must specify which audit(s) the client falls into. If unclear, HALT and ask.

**Stale-audit warning.** If the most recent local-audit brief for the client's city/niche is older than 90 days, surface a staleness warning in the roadmap's "Caveats" section. Do not halt — the operator can override.

## Outputs

A single markdown file at `03 Projects/Clients/[ClientName]/pov-roadmap.md`. The file is **created once** (per the skill's intent — the POV is the kickoff artifact, not a living document; ongoing tracking is the `agent-deployment-monitor` skill's job).

The file is structured:

```markdown
---
client: [ClientName]
city: [City, ST]
niche: [Niche]
generated: [YYYY-MM-DD HH:MM CT]
generator: client-pov-tracker (Mavis, EA)
whitepaper: 03 Projects/Mavis EA Design/reports/2026-Q3-SMB-AI-Maturity-Report.md
local_audits_ingested: [list of briefs file paths]
agentic_standard: §2 of the whitepaper (idempotency / real-time sync / FSM-native / outcome-priced)
blueprint_phases: §5 of the whitepaper (4-week install)
outcome_pricing: [% of captured revenue, default 10-20%]
install_start: [YYYY-MM-DD if known]
---

# POV Roadmap — [ClientName] — [City, ST] — [Niche] — [YYYY-MM-DD]

> **What this is.** Dre Builds' point-of-view on what we are building, why, and how we measure success. Single document. Kickoff artifact. Cited throughout to the SMB AI Maturity Report and the underlying local-audit intelligence.

---

## 1. The Friction (what we are solving)

[Per-competitor Friction Signals categorized by tier. Pulled from the local-audit briefs. Each tier is a section.]

### Tier 1 — High-urgency revenue leaks
[List each Tier 1 signal with: business name (if from audit), the signal itself, the revenue impact estimate (e.g., "8 missed calls/day × $300/job = $876K/year per the whitepaper §4").]

### Tier 2 — Medium-leverage friction
[Same format.]

### Tier 3 — Low-leverage friction (noted, not prioritized)
[Same format.]

---

## 2. The Agentic Standard (how the fix must satisfy technical criteria)

[For each of the 4 Agentic Standard criteria, state what it means for THIS client's stack. The criteria are the whitepaper's §2 — quoted, then applied.]

- **Idempotency:** [specific test for this client's FSM — e.g., "duplicate-call within 100ms must not create duplicate jobs in ServiceTitan."]
- **Real-time sync:** [specific SLA — e.g., "voice agent booking must appear on the ServiceTitan dispatch board within 60 seconds."]
- **FSM-native:** [which FSM the client uses — Jobber, ServiceTitan, Housecall Pro, FieldEdge — and what canonical fields the agent must populate.]
- **Outcome-priced:** [the agency's billing model for this client — the agency bills on booked jobs that complete within 30 days; the voice-agent usage fee is the agency's cost, not the client's.]

---

## 3. Target ROI (the math)

[The dollar impact, anchored to whitepaper §4. If the client has provided their own call volume, job ticket, or after-hours %, override the whitepaper defaults with the client-specific numbers.]

| Line item | Wrapper-tier (current state) | Dre Builds True Agent | Source |
|---|---|---|---|
| Missed-call revenue leak | $[X]/year | $0 (covered) | whitepaper §4 |
| After-hours revenue leak | $[X]/year | $0 (covered) | whitepaper §4 |
| ... (any client-specific line items) | | | |
| **Net annual impact** | **–$[X]** | **–$[X] net cost** | |
| **Dre Builds ROI (vs wrapper)** | — | **+$[X]/year** | |

**Realistic capture assumption:** 30–60% of the lost revenue (per whitepaper §4 footnote). Conservative case: 30%. Base case: 40%. Aggressive case: 60%.

**Payback period:** 30–90 days for any client doing $300K+ in annual revenue (per whitepaper §4).

---

## 4. The Blueprint (what we are building)

[Per Blueprint phase from whitepaper §5: the deliverable, the week, what the client sees.]

### Phase 1 — Baseline Audit (Week 1)
- Deliverable: 1-page baseline doc with the 5 measurement numbers.
- Client sees: the baseline doc + a calibration call to confirm the numbers.

### Phase 2 — Voice Path (Week 2)
- Deliverable: working inbound voice path with idempotency + real-time sync + FSM-native write-back.
- Client sees: 5+ test calls, the agent's call outcomes in the FSM, the 5 numbers re-measured at Day 14.

### Phase 3 — Inventory/Ops Path (Week 3, e-com clients only)
- Deliverable: inventory reconciliation middleware (Shopify / TikTok Shop / Amazon).
- Client sees: daily inventory confidence report.

### Phase 4 — Outcome Loop (Week 4)
- Deliverable: 30-day retrospective + outcome invoice (agency billed on booked jobs that complete within 30 days) + 90-day forward plan.
- Client sees: ROI statement, the 5 numbers trended over 30 days, the 90-day plan.

---

## 5. The 5 Measurement Numbers (baseline)

[From the Forbes/QuickBooks dissection cited in whitepaper §5.1. The baseline is the agency's pre-install reference. The 30-day re-measure is the agency's success/failure indicator.]

1. **Time per task** (in seconds, stopwatch, baseline vs AI-assisted).
2. **Output quality** (edit rate on AI-generated content; 80% needs minor or no edits = pass).
3. **Revenue per AI-supported activity** (revenue from AI-drafted campaigns vs human-drafted).
4. **Error rate** (data-entry errors before vs after AI).
5. **Tool cost vs value delivered** (the dollar ratio of AI subscriptions to documented value).

---

## 6. The Outcome-Pricing Commitment

[From whitepaper §2.4. The agency bills the client on outcomes, not inputs. The exact % is the outcome_pricing field in the frontmatter. The agency's commitment: if the 30-day ROI is negative, the agency eats the cost of the build.]

---

## 7. Caveats and open questions

[Anything that the local-audit data didn't resolve, anything the client needs to confirm, any staleness warnings on the source data.]

---

## Appendix — sources

[List of local-audit briefs ingested, the whitepaper, the persona, the client-specific data the operator provided.]
```

## Procedure

### Step 1: Verify the inputs

```bash
ls "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Clients/"
```

If the `[ClientName]` directory does not exist, create it:

```bash
mkdir -p "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Clients/[ClientName]/"
```

If `briefs/local-audit-*.md` does not exist (use glob), **HALT** with the empty-audit halt message.

Verify the whitepaper exists at the default path. If it doesn't, HALT and ask for the path.

Verify the persona file exists. If it doesn't, HALT and ask.

### Step 2: Read the local-audit briefs

Open every `briefs/local-audit-*.md` that matches the client's city + niche. For each:

- Extract the per-competitor friction signal checkboxes (PRESENT / ABSENT).
- Extract the severity score (1-5) per competitor.
- Extract the "What install would close the gap" line.
- Note the cross-competitor top-3 friction patterns.

If multiple briefs match (multiple cities or niches), merge the friction signals into a single list. De-duplicate identical signals.

### Step 3: Categorize by tier (per the Friction Filter taxonomy)

The Friction Filter in the local-competitor-auditor skill defines 3 tiers:

- **Tier 1 — High-leverage friction (Pillar 2 anchor):** Phone-only after-hours, no 24/7 web chat, "Call us for a quote" only, no instant-booking calendar.
- **Tier 2 — Medium-leverage friction:** No service-area map, no online pricing, no reviews linked, no FAQ/process page, site is dated.
- **Tier 3 — Low-leverage friction:** No blog/content/SEO, no team page, no video/photo of completed work.

For each unique friction signal across the audits, assign the tier per the taxonomy. If a friction signal is novel (not in the taxonomy), flag it in the "Caveats" section and ask the operator to confirm the tier.

### Step 4: Read the whitepaper §2 (Agentic Standard) and §4 (Build Gap Quantified)

Open the whitepaper at the default path. Read §2 (the 4 criteria) and §4 (the cost-comparison table). Note the math defaults:

- 2-truck HVAC shop: 8 missed calls/day × $300/job × 365 days = $876K/year.
- 10K orders/month TikTok Shop merchant at 5% LDR: $500/month late-order penalties + 31-day settlement hold + 10% order cap.
- 40% realistic capture assumption (from whitepaper §4 footnote).
- 30–90 day payback period.

If the client has provided their own numbers (call volume, job ticket, order volume), override the whitepaper defaults. The override is logged in the "Target ROI" table's "Source" column.

### Step 5: Generate the Target ROI table

Apply the whitepaper's §4 math to the client's specific situation. If the client is a 2-truck HVAC shop in Phoenix with $300/job ticket, use the whitepaper's $876K/year directly. If the client is a single-truck plumbing shop in Dallas with $250/job ticket, scale accordingly.

If the client is e-commerce, use the TikTok Shop penalty math (or Shopify oversell math). If the client is both e-com and trades (rare but possible), use both tables.

### Step 6: Map friction → Blueprint phase

For each Tier 1 friction, identify the Blueprint phase that addresses it:

- **Phone-only after-hours / no 24/7 web chat / "Call us for quote" only / no instant-booking calendar:** Phase 2 (Voice Path). The voice agent handles all four.
- **Inventory sync failures (e-com clients only):** Phase 3 (Inventory/Ops Path).
- **Stale site / no reviews / no FAQ (Tier 2):** Phase 4 (Outcome Loop) — these are the 30-day retrospective's content.

If a Tier 1 friction has no Blueprint phase, flag it in the "Caveats" section. The operator decides whether to extend the Blueprint or deprioritize the friction.

### Step 7: Write the pov-roadmap.md

Use the template above. Atomic write (temp-write-rename) is not required for a single client file (the file is created once, not appended), but use a similar pattern to avoid corruption:

```bash
TMP=/tmp/pov-roadmap-$$.md
cat > "$TMP" <<'EOF'
[content]
EOF
mv "$TMP" "/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Clients/[ClientName]/pov-roadmap.md"
```

Or use Python:

```python
from pathlib import Path
content = "..."
target = Path(f"/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Clients/{client_name}/pov-roadmap.md")
target.write_text(content)
```

### Step 8: Update the clients ledger (if it exists)

If `03 Projects/Clients/_ledger.mdl` exists, append:

```markdown
- YYYY-MM-DD HH:MM CT — [ClientName] / [City, ST] / [Niche] — POV roadmap created (N Tier 1, M Tier 2, K Tier 3 signals ingested; whitepaper §2 Agentic Standard applied; target ROI: $X/year)
```

If the ledger does not exist, create it.

### Step 9: Return to the operator

Send a one-paragraph summary:

- Client name + city + niche
- File path of the pov-roadmap.md
- Counts: N Tier 1, M Tier 2, K Tier 3 signals ingested
- Target ROI (annualized)
- Install start date (if known)
- Any halt conditions / blockers / staleness warnings

## Constraints

- **No fabrication.** Every friction signal must come from a real local-audit brief. Every ROI number must be traceable to the whitepaper §4 math (or to client-provided data explicitly cited).
- **No public publishing.** The pov-roadmap.md is for client engagement, not for X drafts. The sales-audit-hook template (`03 Projects/Mavis EA Design/templates/sales-audit-hook.md`) is the X-facing analog.
- **No live-system modification.** This skill writes markdown only. It does not call ServiceTitan / Jobber / Shopify APIs. It does not send emails. It does not run voice agents. The Blueprint's Phase 2-4 are future deployments, not part of this skill.
- **Single document per client.** The POV is a kickoff artifact. Re-running the skill on the same client should HALT and surface ("POV already exists for [ClientName] — use `agent-deployment-monitor` for ongoing tracking").

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| No local-audit briefs exist | `ls briefs/local-audit-*.md` returns 0 | HALT; tell operator to run `local-competitor-auditor` first |
| Multiple city/niche audits match | city/niche input is ambiguous | HALT; ask operator to specify |
| Client dir does not exist | `ls 03 Projects/Clients/[ClientName]/` fails | Auto-create the dir (the operator's intent is to onboard) |
| Whitepaper missing | default path doesn't exist | HALT; ask for the path |
| Persona missing | default path doesn't exist | HALT; ask for the path |
| Brain / state corrupted | N/A — this skill is read-mostly | N/A |
| Stale audit (>90 days) | mtime > 90d on the most recent matching audit | Surface a warning in the Caveats section; do not halt |
| POV already exists for this client | `pov-roadmap.md` already in client dir | HALT; surface that the POV is a one-shot artifact; redirect to `agent-deployment-monitor` |
| Client-specific data conflicts with whitepaper math | operator-provided numbers disagree with §4 defaults | Use the operator-provided numbers; cite both in the Source column |

## Verification

Before returning:
1. `ls` confirms `03 Projects/Clients/[ClientName]/pov-roadmap.md` exists with non-zero size
2. The file has all 7 sections (Friction / Agentic Standard / Target ROI / Blueprint / 5 Numbers / Outcome-Pricing / Caveats)
3. The Target ROI table has at least 3 line items
4. The 5 measurement numbers are in the file (Section 5)
5. The Agentic Standard is applied specifically to this client's stack (Section 2 — not generic)
6. The Outcome-Pricing commitment is stated (Section 6)
7. The Caveats section is non-empty if any audit was >90 days stale
8. The clients ledger was appended (or created)

## Cross-reference

- **`local-competitor-auditor`** — the upstream skill that produces the Friction Signals this skill ingests. Run the auditor first.
- **`agent-deployment-monitor`** — the downstream skill for ongoing client tracking after the POV kickoff. The POV is the kickoff artifact; the monitor is the weekly/monthly tracking.
- **`x-content-engine`** — sibling project. The Scribe may eventually draft a "POV for [Client]" X post from this roadmap (in Pillar 4 / Build Log format), but only with operator approval and only with all identifying details redacted.
- **The 2026 SMB AI Maturity Report** — the load-bearing reference for §2 (Agentic Standard) and §4 (Build Gap Quantified). The whitepaper is canonical; the POV is the per-client application.
- **The Dre Builds persona** (`03 Projects/X-Content-Engine/agents/persona.md`) — the narrative voice for the roadmap. Match the persona's staccato, dollar-first, no-fluff voice.
