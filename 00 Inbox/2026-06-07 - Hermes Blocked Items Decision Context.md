---
type: mavis-prep
created: 2026-06-07 11:05 CT
purpose: Decision context for the Hermes Blocked Items doc. Not a draft reply — Andre's answers only. Vault-grounded context so he can sign off in ~5 min.
expires: when the 8 items are unblocked
---

# Hermes Blocked Items — Decision Context (2026-06-07)

> For Andre. Read alongside [[2026-06-07 - Hermes Blocked Items Decision Doc]].
> I'm not filling in your answers — that's your call. Below is the vault context each question deserves, the tradeoffs I see, and any patterns from your prior decisions that bear on it.

## Q1 — P5 Pillars (Cost / Latency / Safety)

**What you committed to today (per the doc):** these become *eval criteria* for the next P5 round, not just a one-time unblock. So whatever you write here sets the bar for every downstream P5 task.

**Vault grounding:**
- **Safety** — already mostly locked. `[[MAVIS]]` hard constraints and `[[SOUL]]` give you the rule set: no deploys / pushes / external sends / credential / schedule / destructive ops without explicit in-session approval; no fleet from Mavis; no orphan spawns. For the *operator path* specifically, this maps cleanly to: "no destructive ops without explicit confirmation, no outbound sends without auth, no schedule changes without confirmation." The mphrediction companion-mode lens (`[[mavis-as-companion]]`) adds an under-specified dimension: emotional/personal-domain actions. Not in scope for P5 eval criteria unless you want it to be.
- **Cost** — your prior post-mortem (`[[2026-06-04]]` Night Flight) found the *budget* was the bottleneck, not the architecture. Cascade hit at 18,462,000 / 18,462,000 tokens on Token Plan Hs_plus (5-hour cap). Suggested next-time levers: lower concurrency (3-4 workers, not 5-6); lighter tasks; staged dispatches. The cost eval criterion should be expressible in the same units (tokens/task, or % under current ceiling).
- **Latency** — no prior stated targets in the vault. Apple Silicon is the inference substrate per `[[Hot-Cold Inference Tiers on Apple Silicon]]`; hot-tier latency is a few seconds for short prompts. P50 <2s, P95 <8s is the kind of target that constrains design without being impossible. You may want to flag whether the latency target is the *operator path only* (chief-of-staff loop) or the full request→response (including worker dispatch + tool calls).

**Tradeoff to flag:** the cost ceiling and the latency target can fight each other. Cheaper (slower model, fewer tokens) → higher latency on harder tasks. Tighter latency → more likely to use the bigger/faster model. The eval rubric should pick which side loses when they collide.

---

## Q2 — Phase C Fleet Redesign (A / B / C)

**This is the architectural call.** Affects every downstream task for the foreseeable future.

**The three options, restated for clarity:**
- **A. Stay current (11 profiles)** — evolutionary, lowest disruption
- **B. Consolidate (5 profiles)** — reductive, mirrors the V3→V4 Gibson cleanup pattern (20 V3 daemons killed, 42 launchd agents unloaded, 9 profile YAMLs cleaned per your memory)
- **C. Split by function** — cleanest abstraction, highest upfront design cost

**Vault grounding:**
- The V3→V4 cleanup is the closest analog in your history. You chose to consolidate when the system was over-instrumented and under-load. But that was a *daemon / launchd* cleanup, not a *profile-role* cleanup. Different unit of consolidation.
- The mphrediction thesis argues *fewer* profiles with deeper intimacy contracts per profile, not more (companion-mode favors depth over breadth). This pulls toward **B** for the philosophical direction.
- The agent-harness pattern (`[[agent-harness]]`) argues against premature role-splitting — the future-proofing test should validate the role exists before the role is built. This pulls toward **A** (wait) or **B** (consolidate, don't split).

**What I'd ask before you answer:** is the 11-profile count *current* (after V3 cleanup) or *pre-cleanup*? If post-cleanup, then 11 is already reduced. If pre-cleanup, then 11 is inflated and the question is "how much more to cut." The decision doc doesn't disambiguate. Worth confirming with Hermes.

**My read (chief-of-staff, not decision-maker):** the impulse to *split by function* is usually a refactorer's instinct — clean abstractions look right on paper but compound the coordination cost. The Night Flight taught you the budget, not the architecture, was the bottleneck. Consolidation (B) is the change that compounds; the C split is the change that has to be defended repeatedly.

But you have more context than I do. If there's a *specific* reason C is right (e.g., a verifier profile that's blocking other work, a routing profile that needs to be standalone), I can't see it from the vault. Worth a 1-line "why" on whichever option you pick.

---

## Q3 — Docs Corrections PR (A / B / C)

Trivial. Confirm/deny. The vault doesn't have the PR body in scope to evaluate — Hermes holds that. If you want me to pull the PR body and flag any doc-consistency issues before you answer, I can do that in 2 min — say the word.

---

## Q4 — Spec §7 — Desktop Bridge + Fleet Switcher

**Desktop bridge — auth model.** Three real options:
1. **Local-only (loopback / unix socket)** — safest, no network surface; locks you to same-machine
2. **OAuth relay (your existing OpenClaw gateway at 18789/18792?)** — fleet-adjacent, leverages existing auth; adds a network hop and an OAuth dependency
3. **Always-on tunnel (Cloudflare / Tailscale-style)** — works from anywhere; biggest attack surface, hardest to revoke

The mphrediction / companion-mode framing argues for *more* friction on cross-machine access (the chief-of-staff should be present, not always-on-remote). Pulls toward #1 unless there's a specific cross-machine use case I'm missing.

**Fleet switcher — UX + persistence.** UX options: CLI flag (power-user), dashboard toggle (visible), both (redundant). Persistence options: per-session (lost on restart), per-machine (config file), per-machine synced via vault (cross-device). The vault-as-source-of-truth pattern (`[[INDEX]]` / `[[MAVIS]]`) would argue for vault-synced; the "no hosted service" constraint from your 06-04 daily would argue against it. Pick one UX, pick one persistence. If you don't have a strong preference, "CLI flag + per-machine" is the boring-correct default.

---

## Q5 — Anything else in the `needs-andre` bucket?

**My read: probably "none", close the loop.** Math: the decision doc lists 5 items in the bucket (P5 Pillars = 3, Phase C = 1, that's 4 *groups*, not 5 items). Either Hermes over-counted, or there's a 5th single item. I grepped the vault for `needs-andre` / `awaiting-andre-decision` — only the decision doc and one internal note match. No orphan 5th item in the vault.

If you want to be sure, ask Hermes: "the report says 5 items in `needs-andre`, the decision doc names 4 groups. Is the 5th a typo or a hidden item?"

---

## Ready-to-paste reply template (for when you decide)

```
Q1: Cost=[ceiling], Latency=[P50/P95], Safety=[rule]
Q2: A / B / C — [one-line why]
Q3: A / B / C
Q4: Desktop=[auth model]; Switcher=[UX+persistence]
Q5: [item + answer, or "none"]
```

Fill, paste back, I'll synthesize → route to Hermes → update kanban.

---

## What I'd also flag (not in the doc, but adjacent)

- **MAVIS.md is stale (last touched 2026-06-01).** Weekly-context update is overdue (should be Monday). 5-min refresh. Worth slotting in while you're in a "weekly review" headspace.
- **Git working tree has ~40 modified/deleted files in `99 _system/mcps/`.** Looks like cleanup that wasn't committed. Not urgent; not in your decision scope; flagging because I'd rather you know than discover it.
- **No daily note for 06-05, 06-06, 06-07.** Gap. I'll backfill the 06-07 one (this morning) — defer the others to your call, they may not exist for a reason.
