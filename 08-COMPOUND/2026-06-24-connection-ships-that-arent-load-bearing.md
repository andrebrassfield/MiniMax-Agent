---
date: 2026-06-24
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: true
thesis-link: Thesis 1 (the bottleneck is spec throughput, not implementation) + Thesis 2 (a second self is active reasoning, not good capture)
domains-crossed: [mavis-self-model, ea-design-spec, xce-operations]
---

# Connection: Three "ships" that aren't load-bearing — `ea-skill-evolution` dormant + `ea-correction-capture` Phase A possibly unfired + `reply-sweep-daily` HALTs as `success`

**Why this connection matters:** Three artifacts Mavis treats as load-bearing (a skill, a feedback-loop phase, a cron) all turn out, on close inspection, to be *shells that don't run*. The Mavis skill catalog lists `ea-skill-evolution` as live; the morning synthesis notes it has no triggering cron. The Mavis loop-engineering plan locked `ea-correction-capture` as Item 2 on 2026-06-22 with a two-phase architecture (Phase A cron + Phase B chief-session); the Phase A cron (`correction-classifier-nightly` at 21:00 CT) may exist on disk but the morning synthesis flags the whole feedback loop as "dormant, not load-bearing." The `reply-sweep-daily` cron was deprecated today after 5+ days of HALT-at-step-0 fires reported as `success`. Reading the three together, the unifying finding is that **Mavis's self-model treats "shipped" as equivalent to "operational," and they are not.** This is the same shape as the 2026-06-23 connection (signal vs revealed state) applied to Mavis itself — and it's Thesis 2 (`a second self is active reasoning, not good capture`) in its most uncomfortable form: a captured list of skills is *not* a reasoning system, it's a tombstone.

**Note A:**
- Title: Morning Synthesis — 2026-06-24 (contradiction section)
- Path: `~/MiniMax-Agent/02 Notes/_MOCs/2026-06-24-morning-synthesis.md`
- Claim: The synthesis names the contradiction directly: the 2026-06-22 daily late-session wrap says "post-skill-evolution" (claims it shipped); `mavis-as-llm.md` codified the same day says "Stopping at SFT (no RLHF). Skills exist but no structured feedback loop captures Andre's mid-session corrections and routes them into skill evolution." Resolution proposed: schedule `ea-correction-capture` as a daily cron (or kill the claim).

**Note B:**
- Title: Plan: Mavis as Loop Engineer — Synthesis + 3 Carry-Over Items (Item 2)
- Path: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/mavis-loop-engineering-plan-2026-06-22.md`
- Claim: `ea-correction-capture` implemented 2026-06-22 with a two-phase architecture pivot (daemon does not expose LLM endpoint; `mavis llm call` does not exist). Phase A: `correction-classifier-nightly` cron at 21:00 CT — pure filesystem ops, writes context buffer to `~/.mavis/state/correction-buffer/`. Phase B: chief session on cold-start reads the buffer, runs LLM classifier, surfaces to Andre. Status on the Phase A cron: not visible in the 06-22 plan doc as "verified firing."

**Note C:**
- Title: reply-sweep-daily — DEPRECATED 2026-06-24 19:01 CT
- Path: `~/MiniMax-Agent/03 Projects/X-Content-Engine/postmortems/2026-06-24-reply-sweep-deprecation.md`
- Claim: `reply-sweep-daily` shipped 2026-06-18, fired for 5+ days, every fire HALTed at step 0 (architecture drift — strategy authored against Playwright, runtime uses mavis browser bridge). Cron-runner reported `success` the whole time. The skill was *listed in the cron registry* (stated: shipped) but never produced a reply (revealed: dormant).

**What reading both reveals:** Three "ships," three different failure modes, one unifying finding.

`ea-skill-evolution` is dormant because **a skill without a trigger is not a workflow — it's documentation.** The skill exists on disk; no cron references it; no chief session loads it by default; nothing moves corrections through it. Same shape as a playbook no one opens.

`ea-correction-capture` is *potentially* in the same shape: the plan describes Phase A as a cron that "scans files, writes daily summary, appends context buffer." But the 06-24 morning synthesis lists the whole feedback loop as "dormant, not load-bearing" — which means the Phase A cron's revealed state is unverified. If Phase A is not firing, Phase B has nothing to read, and the whole RLHF-analog loop is a pointer to a phase that doesn't run. This is the textbook instance of a two-phase architecture whose spec was approved but whose Phase A was never instrumented.

`reply-sweep-daily` is the canonical example: a cron *was* firing, but every fire was a HALT disguised as success. The XCE feedback-loop audit captures the same shape across two more crons (`x-analytics-tracker-daily` 3+ consecutive halts; `xce-feedback-2026-06-17/18` never fired, `nextRun: Jun 2027`).

The unifying discipline gap: **Mavis currently has no registry of which artifacts (skills, crons, loops) are stated-live vs revealed-live.** A skill that exists on disk and a skill that runs in production look identical in the catalog. The loop-engineering plan's 6 blocks include Memory (block #6) but not *verification of which block is currently firing* — that's the missing 7th block, or the missing audit layer for the existing 6.

The thesis connection is sharpest here. **Thesis 2 says "a second self is active reasoning, not good capture."** A Mavis that has 46 skills catalogued but a third of them are dormant is not a reasoning system — it's a vault with a fancy index. The "active reasoning" claim requires *revealed state*, not *catalogued state*. The same applies to the skill catalog as to the vault: a permanent note without wikilinks is a tombstone, a skill without a trigger is a tombstone, a cron that HALTs as success is a tombstone.

This is also Thesis 1 in pure form: every one of these three "ships" has working implementation. The bottleneck is the spec that says "verify revealed state." None of the three specs did.

**Suggested next step:**
- Surface in tomorrow's morning brief as a `thesis-relevant: true` connection (Thesis 1 + Thesis 2).
- Cross-reference from `agent-disease-detector` skill: name this as **Anosognosia at the self-model layer** — the system reports itself as operational without checking. Pair it with the measurement-system disease from the cron-success-misleading connection (they're the same disease at different layers).
- Add a verification step to the `ea-correction-capture` plan: Phase A cron firing must be verified (via `lastRun` timestamps in `mavis cron list` + a buffer-file mtime check) before declaring the RLHF-analog loop live. The same verification should be applied retroactively to `ea-skill-evolution` and any other "shipped but uncroned" skill.
- For the catalog hygiene: produce a one-shot audit cron that diffs the skill catalog (`ls ~/.mavis/agents/mavis/skills/`) against the crons that reference those skills (`mavis cron list --json | jq` against `~/.mavis/agents/mavis/crons/*.md`) and surfaces unreferenced skills as candidates for either deletion or trigger-creation. This is the equivalent of the substrate→cron dependency map (proposed in the FB-Engine 06-24 postmortem), but for the skill layer.