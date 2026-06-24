---
type: spec
status: draft (v2.6 calibration pending)
version: 0.2
created: 2026-06-23
updated: 2026-06-23
author: Mavis
owner: Andre
project: Marketing Skills v2.5.0 → v2.6
target: doseofproof.com (Andre's personal brand)
related: [INDEX.md, MEMORY.md, resolvers.md, 00 Inbox/2026-06-23-doseofproof-context-needed.md]
decisions:
  a2a_topology: A-read + B-write (locked 2026-06-23 18:37 CT)
  pipeline_enforcement: pending
  index_auto_gen: pending
  skill_load_log: pending
---

# Selection Layer + A2A Skill Handoff — Design Spec

## Why this exists

The Marketing Skills v2.5.0 set is shipped (5 skills, 36 files, ~250KB). But the skills only matter if they get loaded at the right moment. Right now there are 3 selection problems, each with a different shape:

1. **User input → skill** (you say X, which skill loads?)
2. **Agent input → skill** (mid-task, the agent realizes it needs a skill — which one?)
3. **A2A input → skill** (another agent's session needs a marketing skill — how does it get one?)

The mavis runtime has *some* auto-matching via SKILL.md `description` fields. But description-matching is fuzzy. And there's no orchestrator for cases 2 and 3.

This spec proposes a shape for all three. Foundation already shipped:
- `~/.mavis/skills/INDEX.md` — single registry, cross-agent readable
- `resolvers.md` — extended with marketing-skill routing table
- MEMORY.md — pointer to the INDEX + this spec
- `/offers` trigger overlap on "pricing strategy" — fixed

---

## Layer 1 — User input → skill

**Current state:** Mavis reads user message, matches against `description` field of all loaded skills, loads the strongest match. Soft fuzzy.

**Proposed:** Mavis (or any agent) follows a 3-step decision tree:

```
User says X
    ↓
1. Is there a marketing-domain keyword in X?
   (scan INDEX.md triggers + descriptions)
    ↓ yes
2. Does the matching skill's upstream exist in this context?
   (check _meta.json upstream + scan for prior offer/pricing artifacts)
    ↓ maybe no upstream
3. Soft-check: "Do you have an offer locked?"
   (don't load /copywriting on an unlocked offer)
```

**Trigger-disjointness rule:** Each trigger should belong to exactly one skill. The `/offers` ↔ `/pricing` overlap on "pricing strategy" was a v2.5.0 bug — fixed. New skills must pass this check before merge.

**Pipeline enforcement:** Soft, not hard. The agent asks; it doesn't block. If you say "just write the sales page" before locking an offer, the agent should warn but proceed with `/copywriting` if you confirm.

---

## Layer 2 — Agent input → skill (mid-task routing)

**Current state:** When Mavis is mid-task and realizes it needs a different skill, it loads the SKILL.md inline. No registry check, no upstream validation, no logging.

**Proposed:** Add a 4-step self-check before mid-task skill loading:

```
1. Why am I about to load this skill?
   (be explicit: "I need pricing strategy to set the anchor")
    ↓
2. Is the upstream present?
   (don't load /copywriting without an offer artifact)
    ↓
3. Is there a more specialized skill for this?
   (check INDEX.md — am I about to load a generic skill when a specific one exists?)
    ↓
4. Will loading this skill cost more tokens than it saves?
   (if the answer is in the existing context, don't load)
```

**Logging:** Each mid-task skill load should append a line to a per-session skill-load log. Format:
```
[2026-06-23 16:58:30] LOADED=pricing TRIGGERED_BY=offers-stage-4 REASON=anchor-not-yet-set UPSTREAM_CHECK=pass
```

This log feeds the morning brief ("yesterday you invoked /pricing 3x, all from /offers stage 4 — your pricing step is the slowest part of offer design").

---

## Layer 3 — A2A input → skill (cross-agent handoff)

**Current state:** No protocol. Another agent (Hermes, OpenClaw, Socratic) has no documented way to invoke a marketing skill. Theoretically it can read `~/.mavis/skills/<name>/SKILL.md` and run the procedure itself, but no contract exists.

**Proposed topology — pick one:**

### Option A: Direct passthrough (RECOMMENDED)
- Any agent reads `~/.mavis/skills/INDEX.md` to discover available skills
- Any agent reads the skill's `SKILL.md` directly and runs the procedure
- Mavis is the **owner** (writes, versions) but not the **router** for read
- Pros: zero latency, no Mavis bottleneck, scales to N agents
- Cons: no central audit, drift risk if an agent runs an old version

### Option B: Mediated
- All skill invocations go through Mavis via `mavis communication send --command invoke_skill`
- Mavis loads the skill, runs the procedure, returns the result
- Pros: single audit log, Mavis can refuse unsafe invocations, version-check guaranteed
- Cons: Mavis becomes a bottleneck, adds latency, creates a SPOF

### Option C: Federated
- Each agent maintains its own copy of the skills it needs
- `~/.mavis/agents/<name>/skills/` is the per-agent copy
- Sync via cron from `~/.mavis/skills/` (the canonical source)
- Pros: agents are isolated, no cross-dependency on `~/.mavis/skills/` being mounted
- Cons: drift between copies, sync overhead, doesn't actually work well with the mavis runtime which expects a single canonical location

**My recommendation: Option A for read, B for write.** Read = direct passthrough (the INDEX is the contract). Write = mediated through Mavis (no agent other than Mavis modifies a skill file). This gives speed on the read path and governance on the write path.

**Message schema (for Option B if you want it later):**

```yaml
# Sender: any agent X
# Receiver: Mavis session or daemon
command: invoke_skill
content:
  skill: "offers"           # skill name (must match INDEX.md)
  version: "2.5.0"          # optional version pin
  parameters:                # skill-specific inputs
    business_type: "coaching"
    current_offer: "1:1 executive coaching, $5k/month"
    problem: "low conversion on sales calls"
  caller_context: "I'm working on a launch plan for client X..."
  return_format: "text"     # text | file_path | json
```

Mavis responds with the output. Logs the invocation.

---

## Open decisions (need your call)

1. **A2A topology.** ✅ **LOCKED: A-read + B-write** (2026-06-23 18:37 CT, Andre's call). Direct passthrough for skill reads, mediated through Mavis for skill writes.
2. **Pipeline enforcement.** Soft-check (agent asks "do you have an offer locked?") or hard-gate (skill refuses to load without upstream)? My pick: soft-check — the agent warns but doesn't block. Hard-gate would create UX friction on small tasks.
3. **INDEX.md auto-generation.** Hand-maintained v1, auto-generated v2 (weekly cron, walks `_meta.json`). My pick: ship hand-maintained for now, build the auto-gen cron in v2.6 when the set is stable.
4. **Mid-task skill-load logging.** Append to a per-session file? Or to a global skill-usage ledger? My pick: per-session, then roll up to global weekly. Avoids hot-path write contention.

---

## v2.6 — Personal-brand calibration (target: doseofproof.com)

**Context (2026-06-23):** Andre confirmed the marketing skills target his personal brand at **doseofproof.com**, not a generic agency/client operator. v2.5.0 was designed against standard marketing practice (services, agencies, B2B). v2.6 should recalibrate the assumption-set, examples, and anti-patterns to personal-brand reality.

### What changes when the target is a personal brand

| Dimension | Generic operator (v2.5.0) | Personal brand (v2.6 target) |
|---|---|---|
| **Offer structure** | services, retainers, B2B contracts, courses | info products, courses, community, sponsorship, speaking, low-ticket + high-ticket mix |
| **Pricing driver** | ROI math, scope creep, FTE-equivalent value | emotional driver, identity fit, transformation, social proof |
| **Sales motion** | discovery calls, proposals, B2B procurement | self-serve checkout, low-friction DMs, occasional 1:1 high-ticket call |
| **Launch type** | PLF-heavy, B2B sales cycles | audience-launch + signature-launch + evergreen; PLF less common |
| **Copy voice** | professional, outcome-focused, often corporate | first-person, behind-the-scenes, contrarian, builder-not-marketer |
| **Brand asset** | logo, deck, case studies | the operator's face, voice, and track record |
| **Testimonial** | named logo, ROI metric | screenshot of DM, video, transformation story |
| **Anti-pattern specific** | fake corporate urgency, manufactured scarcity | fake "limited to 10" when unlimited, manufactured "live launch" energy, fake "I almost didn't share this" |

### v2.6 calibration plan

1. **/offers** — add a "personal-brand offer archetype" section: 6 archetypes (course, cohort, community, coaching, info product, sponsor-read). Value Equation reframed for transformation (not service). Decision tree: "is the offer you / is the offer the thing you made?"
2. **/pricing** — add "personal-brand pricing tiers" (low-ticket $27-$297, mid-ticket $497-$2k, high-ticket $2k+). Payment-plan-by-default for anything over $500. Charm pricing dominant; premium pricing reserved for high-ticket coaching.
3. **/copywriting** — rewrite `voice-and-tone-rules.md` to encode Dre-style first-person builder voice. Add personal-brand headline formulas ("How I [did thing]", "[N] lessons from [specific thing]"). Anti-patterns: no "as a [credentialed expert]", no manufactured vulnerability.
4. **/launch** — shift launch-type distribution toward audience-launch + signature-launch. Evergreen framework is the default for personal brands. PLF treated as exception, not default.
5. **/sales-enablement** — reduce discovery-call emphasis, add DM-script section for low-ticket intent handling, add 1:1 call framework for high-ticket coaching. Proposal template → consultation-replay script (personal brand sells on call, not in PDF).

### What I need from Andre to ship v2.6

**Required (1 question, blocking):**

What's the **primary monetization shape** for doseofproof.com?
- (a) **Course / cohort-based** — self-paced or live cohort, $XK one-time or payment plan
- (b) **Coaching** — 1:1 or small group, high-ticket ($5k+), sales-call driven
- (c) **Community / membership** — recurring, mid-ticket ($27-$97/mo), content + calls
- (d) **Mix** — specify the dominant + secondary (e.g., "course is the main, coaching is the high-ticket backend")
- (e) **Other / TBD** — still shaping, calibrate to all archetypes

**Helpful but not blocking:**

- Audience size + where they live (X followers, FB group, email list, YouTube)
- Current offer (if any) + current conversion rate
- The 1-2 offers you're most likely to build next

### Vault context I'm building from (until I hear back)

- @DreTheSalesGuy on X (existing brand surface, builder-not-marketer voice, AI/sales focus)
- FB-Engine targeting the "Dose of Proof" Facebook group (community engagement pattern)
- `andrebrassfield/doseofproof` repo (the website, GitHub)
- The name itself: "Dose of Proof" = small, frequent, evidence-based value (suggests case-study-driven positioning, short-form content cadence)

### Calibration log

- **2026-06-23 18:37 CT** — Brand identity confirmed (doseofproof.com, personal). v2.5.0 set is generic-operator-shaped; v2.6 will recalibrate to personal-brand. Awaiting monetization-shape answer from Andre.

---

## What ships with this spec (already done)

- [x] `~/.mavis/skills/INDEX.md` — global registry, cross-agent readable
- [x] `resolvers.md` — marketing section added, 5 skills mapped
- [x] MEMORY.md — pointer to INDEX + this spec
- [x] `/offers` trigger-overlap fix — "pricing strategy" removed

## What waits on your call

- [ ] A2A topology decision (A / B / C, or A-read + B-write)
- [ ] Pipeline enforcement level (soft / hard)
- [ ] INDEX.md auto-gen timeline (now / v2.6 / later)
- [ ] Skill-load log format (per-session / global / both)

## Next iteration (v2.6 candidates)

Once the above are decided:
- Auto-generated INDEX (cron-driven, weekly)
- Skill-load ledger with weekly digest
- Trigger-disjointness test in pre-merge gate
- A2A handoff E2E test (Hermes invokes /offers via direct passthrough, verifies output)

---

## Appendix: Trigger-disjointness check (current state)

| Trigger | /offers | /pricing | /copywriting | /launch | /sales-enablement |
|---|---|---|---|---|---|
| offer design | ✓ | | | | |
| value equation | ✓ | | | | |
| bonus stack | ✓ | | | | |
| guarantee design | ✓ | | | | |
| pricing strategy | | ✓ | | | |
| anchor analysis | | ✓ | | | |
| price testing | | ✓ | | | |
| sales page | | | ✓ | | |
| headline | | | ✓ | | |
| subject line | | | ✓ | | |
| email sequence | | | ✓ | | |
| launch / PLF / open cart | | | | ✓ | |
| discovery call | | | | | ✓ |
| objection handling | | | | | ✓ |
| proposal | | | | | ✓ |

All triggers are disjoint as of 2026-06-23. New skills must add new triggers (no overlaps).
