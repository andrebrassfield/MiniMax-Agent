# Making Your MiniMax Token Plan More Efficient — A Concrete Plan After a 1-Hour Rate-Limit Outage

> **Audience:** a developer or platform owner running an agent/automation fleet on MiniMax's Token Plan, who has just had a 1-hour rate-limit-induced outage and wants a research-backed plan to prevent recurrence and extract more useful work per quota.
>
> **Scope:** diagnosis (which rate-limit mechanism fired), protection (short-term, this sprint), optimization (medium-term, this quarter), monitoring (so the next incident is detected in minutes), and contingency design (when to add credits, when to upgrade tier, when to migrate workload to PayGo).
>
> **Out of scope:** switching vendors, building a custom rate-limit dashboard, deep M3 architecture explainer, M3 open-source licensing debate, M4 roadmap speculation.

---

## TL;DR

1. **Diagnose first.** Your "1 hour of inactivity" maps to one of at least five distinct throttles in the official error catalog (`1002`, `1041`, `2045`, `2056`, plus the unnamed peak-hour dynamic throttle). Each has a different fix. Before changing anything, identify which one fired — check the error code(s) returned, the time-of-day, the request pattern, and the usage-bar state at the incident. Section 1 has the checklist.
2. **Smoothing traffic is the single highest-leverage fix for repeat-outage risk.** The `2045` "rate-growth limit" is the silent killer — sudden bursts trigger it even when total volume is well under the cap. Queue, batch, and stagger fleet start times. Crons should not all fire on the hour.
3. **Passive prompt caching is the single highest-leverage efficiency win on a per-token basis.** MiniMax's worked example shows a 66.7% saving on input tokens when the prefix is stable. Every Hermes agent that has a stable system prompt + tool list is leaving money on the table until the prefix is stable. Audit your prompts for prefix discipline; this is a one-time fix, not ongoing work.
4. **Run a hybrid M3 / M2.7 routing model.** M3 has lower RPM (200 vs 500) and TPM (10M vs 20M) than M2.7 but wins on long-context (>512k) and quality. Use M3 only for those; default everything else to M2.7. This single change can roughly halve the rate-limit pressure on Plus-tier setups.
5. **Set up observability before the next incident.** The Token Plan's `remains` endpoint + Hermes's `/usage` and `/insights` give you the data you need to detect the next incident in minutes, not after an hour. Also expect the open issue MiniMax-AI/MiniMax-M2.7#47 to mean the usage bar may not accurately show cache savings — measure input tokens yourself.

The full plan, with the diagnosis checklist, the opportunity matrix, the three-horizon action list, the monitoring setup, and the known unknowns, follows.

---

## 1. Diagnosis: which of the rate-limit mechanisms actually fired?

The official MiniMax error catalog has four numeric codes that look like "rate limit" to a user, plus an unnamed peak-hour dynamic throttle. They look similar from the outside but have different causes and different remedies. Walk through this checklist against your logs.

### 1.1 The five mechanisms

| Code / throttle | What it actually limits | Most common cause in a fleet setup | Stated remedy |
|---|---|---|---|
| `1002` — API rate limit | RPM or TPM hard cap (per API key) | Bursty parallel requests; multiple agents running in parallel hitting the same key | retry later |
| `1041` — Connection limit | Too many concurrent connections | Long-running streaming connections (video, image pipelines); many sessions open at once | contact us |
| `2045` — Rate-growth limit | Sudden increase or decrease in request rate | Crons firing on the hour, scheduled tasks waking the fleet, batch jobs starting simultaneously | "avoid sudden spikes" |
| `2056` — Usage limit exceeded | 5h rolling or weekly credit exhaustion | Sustained heavy use; the weekly cap burning faster than the 5h | "wait for the next 5h window" |
| Peak-hour dynamic throttle (no code) | Soft tightening under load, weekdays 15:00–17:30 China time | Anything running during CN business hours, especially fleet-wide | docs flag it as may-tighten |

### 1.2 Diagnosis checklist

Run through these four checks against your incident logs. You should be able to land on a single root cause within 10 minutes.

1. **What error code(s) came back during the incident?** Map to the table above. If you see `2056`, you're in credit-exhaustion territory. If `1002`, it's a true API rate limit. If `2045`, your traffic shape is the problem, not your total volume. If you see no code but a slowdown during CN business hours, suspect the peak-hour throttle.
2. **What time-of-day was it, in China time (UTC+8)?** If it was between 15:00–17:30 on a weekday, the peak-hour dynamic throttle is in play. If it was 11:00 PM Beijing time, it's not that.
3. **What did your request pattern look like in the 10 minutes before the incident?** Was there a burst (cron, batch job, subagent fan-out)? If yes, `2045` is the leading suspect. Was it a slow, steady ramp? Then `1002` or `2056` is more likely.
4. **Where was the usage bar at the moment the incident started?** If the bar was at 90%+ of the 5h allowance, it's a 5h cap (5h × 60 min / window — note that the 5h window is rolling, not fixed). If it was 60–70%, the weekly cap is the leading suspect. If it was 20%, the throttle was a true API rate limit, not a quota limit.

If you can answer all four of these, you have a single root cause and a single primary lever to pull. The plan below is layered — Section 3 is the action list — but Section 2 is the reference for what each lever actually does.

### 1.3 What the public docs do *not* tell you

Be aware of these gaps before you trust the published error-code mapping:

- The docs do not publish a clear RPM-vs-TPM-vs-5h-vs-weekly mapping. The 4 codes are a starting taxonomy, not a complete one.
- The "≈3–4 agents" hint for the Plus tier is flagged as approximate in the docs themselves. It is an order-of-magnitude figure, not a hard cap.
- The exact weekly credit allowance per tier is not published. Press releases cite "10× the 5-hour amount" but the official FAQ doesn't confirm a number. You'll need to observe your own usage over a full week.
- The open issue MiniMax-AI/MiniMax-M2.7#47 suggests the `remains_time` value can drain passively and the cache discount may not show up in the usage bar. Don't trust the bar as the single source of truth — track input tokens in your own request log.

---

## 2. The Token Plan mechanics you need to know

A compact reference for the moving parts. Most of this is in the official docs; the framing is what's actionable.

### 2.1 Tiers and quota windows

| Tier | USD/mo | CNY/mo | 5h rolling | Weekly | Agent count hint (peak) |
|---|---|---|---|---|---|
| Plus | $20 | ¥49 | yes | yes | ~3–4 agents |
| Max | $50 | ¥119 | yes | yes | ~4–5 agents |
| Ultra | $120 | ¥469 | yes | yes | ~6–7 agents |

The non-obvious mechanics:

- **Two windows, not one.** Both the 5h rolling and the weekly are active. Burning the 5h allowance does NOT relieve the weekly cap. Sustained heavy users hit the weekly first.
- **Quota is shared across modalities.** Text, image, speech, music, video, and code all draw from the same pool. A busy video pipeline will deplete credits a code agent also needs.
- **Credits don't carry over.** Unused monthly credits are forfeit at the end of the cycle.
- **Mid-cycle upgrades are supported;** the new tier takes effect immediately and the price difference is pro-rated.
- **Subscriptions can be supplemented with separately-purchased credits** (1,000 credits = $1, 365-day validity). When both are available, the subscription is consumed first; credits cover eligible overflow automatically.

### 2.2 API rate limits (per key)

| Model | RPM | TPM |
|---|---|---|
| M3 | 200 | 10,000,000 |
| M2.7 / M2.7-highspeed | 500 | 20,000,000 |
| M2.5 / M2.5-highspeed | 500 | 20,000,000 |
| M2.1 / M2.1-highspeed | 500 | 20,000,000 |
| M2 | 500 | 20,000,000 |

These are at the API-key level. The Token Plan tier hint ("≈N agents") is enforced as an aggregate session counter at the platform layer, not as an RPM/TPM figure. Hitting one does not necessarily mean the other is the bottleneck.

### 2.3 PayGo pricing (relevant for hybrid / overflow)

| Model | Input ($/M) | Output ($/M) | Cache read ($/M) | Cache write ($/M) |
|---|---|---|---|---|
| M3 ≤ 512k input | $0.30 | $1.20 | $0.06 | — |
| M3 > 512k input (limited) | $1.20 | $4.80 | $0.24 | — |
| M3 Priority tier | 1.5× the standard | | | |
| M2.7 | $0.30 | $1.20 | $0.06 | $0.375 |
| M2.7-highspeed | $0.60 | $2.40 | — | — |
| M2.5 / M2.1 / M2 | same input/output as M2.7 | — | $0.03 | — |

The M3 > 512k tier exists but is "limited availability" — check with support if you need it.

### 2.4 Peak-hour dynamic throttle

- Active on **weekdays 15:00–17:30 China time** (UTC+8).
- The official FAQ calls this a "Platform Rate Limiting Rule" and explicitly says it "may tighten during peak traffic."
- This is the most likely cause of an incident with no specific error code. The fix is calendar, not code: schedule heavy work outside the peak window, or accept the throttle and budget for it.

### 2.5 The two prompt-caching mechanisms

- **Passive (automatic)** — supported on M3, M2.7, M2.5, M2.1. Minimum 512 input tokens. Prefix matching order: tool list → system prompts → user messages. 5-min refresh on hit. The official worked example: 50,000 input, 45,000 cache hits, 1,000 output → $0.0108 vs $0.0324 without caching = **66.7% saving** on input at M3 standard pricing.
- **Explicit (Anthropic-compatible)** via `cache_control` — supported on M2.7, M2.5, M2.1, M2 only. *Not* supported on M3. Cache lifetime: 5 minutes, refreshed on hit. First-time cache write is charged extra. Compatible with the Anthropic SDK via `ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic`.

**Critical caveat:** the > 512k long-context pricing threshold counts cache-hit tokens. So caching does not let you escape the long-context pricing tier once your input is over 512k — it just makes the input cheaper within that tier.

---

## 3. Quantified opportunity matrix

A single table that maps each lever to its expected impact, the effort it takes, and what to verify in the user's own data. The expected impacts are anchored to the strongest data in the background research; the medium and low numbers are reasoned estimates, not measured promises.

| Lever | What it does | Effort | Expected impact | What to verify |
|---|---|---|---|---|
| **Prefix discipline for passive caching** | Make the system prompt + tool list identical and at the start of every request. This unlocks the 66.7% input-token saving the docs cite. | Low (one-time audit + template change) | High — up to ~66% on input tokens for cache-hitting agents | The actual cache hit rate in your request log (use response headers or count input tokens before/after a stable prefix change) |
| **Subagent delegation (Hermes `delegate_task`)** | Replace serial multi-step flows with parallel subagent calls; only summaries return to main context. Keeps the main context small, which makes caching more effective. | Medium (refactor a few workflows) | High — typical 30–60% reduction in main-context tokens per request, *and* faster wall-clock | Compare per-task latency and total tokens before/after on the same workload |
| **Hybrid M2.7 / M3 routing** | Default to M2.7 for cache-friendly or high-throughput work; use M3 only for > 512k context or quality-critical tasks. M3 has 60% lower RPM and 50% lower TPM than M2.7. | Low (one-time routing change) | High on rate-limit pressure — for fleet setups, defaulting to M3 means ~2.5× more likely to hit RPM | Per-model request count and per-model 429 rate in your logs |
| **Rate-growth smoothing (`2045` defense)** | Stagger cron start times, batch subagent fan-outs, queue bursty jobs, add a small jitter to scheduled tasks. The `2045` limit punishes *shape*, not volume. | Low (config change) | High — eliminates a whole class of incident | Plot request count over time; the goal is a smooth curve, not spikes |
| **Peak-hour scheduling** | Move heavy work outside 15:00–17:30 China time on weekdays. The dynamic throttle is a calendar constraint, not a code constraint. | Medium (depends on workload) | High for fleets running during CN business hours | Compare per-hour request success rate between peak and off-peak |
| **Use `/compress` proactively (Hermes)** | Compress conversation history before the context fills. Don't wait for the limit. | Low (operational discipline) | Medium — 20–40% reduction in per-request input tokens for long conversations | Compare context length and per-request cost before/after the compress trigger |
| **Structured output / JSON mode** | Force schema-conformant responses. Reduces output tokens, eliminates re-asks for malformed output. | Low (one-time schema design) | Medium — typically 20–30% on output tokens; eliminates the re-ask cost entirely | Output token count + per-task retry rate |
| **Explicit `cache_control` on M2.7** | Use Anthropic-style `cache_control` blocks for callers that need guaranteed cache hit behavior (5-min lifetime). | Low–Medium (API integration) | Medium–High if the workload has 5-min-stable prefixes; ~50–75% saving on input | Cache hit rate, ideally measured against the same prompt before and after |
| **Batched subagent calls** | Combine multiple sub-100-token asks into a single request rather than fanning out. Reduces round-trips and request count. | Medium (refactor batching logic) | Medium — fewer round-trips, lower RPM pressure, lower wall-clock latency | RPM at the API-key level before/after |
| **LLMLingua-style prompt compression** | Run a pre-step compressor on long prompts to remove low-information tokens. | High (extra dependency) | High *in theory* (up to 20× compression) but real-world gains are smaller; trades latency for tokens | Don't use unless the workload is dominated by long, low-density prompts |
| **Upgrade tier (Plus → Max → Ultra)** | Higher envelope; more concurrent agents. | Low (one-click) | High *if* you're capped by tier, none if you're capped by per-key rate limits | Check the `remains` value at incident time — if it's not near zero, tier isn't the binding constraint |
| **Add credits (1,000 credits = $1)** | Overflow coverage with 365-day validity. | Low (purchase) | Medium — gives runway when the 5h or weekly cap is binding | Useful as a stopgap during the audit, less useful as a permanent fix |
| **Migrate a specific workload to PayGo** | For one-off or bursty workloads, PayGo is more cost-efficient than upgrading the whole plan. | Medium (requires per-workload accounting) | Variable — depends on workload's token consumption | Compare PayGo cost per task vs Token Plan cost per task for the specific workload |

The five highest-leverage moves, in order, are: **(1) prefix discipline for caching, (2) hybrid M2.7/M3 routing, (3) rate-growth smoothing, (4) subagent delegation, (5) peak-hour scheduling.** Everything else is secondary. Get these five right and the rest is incremental.

---

## 4. The plan: three horizons

A prioritized action list, sequenced so that the cheap, high-impact items ship first.

### 4.1 Immediate (this week)

The goal is to make the next incident less likely and to gather the data needed to do the deeper work next sprint.

1. **Run the diagnosis checklist from Section 1 against your last 7 days of logs.** Land on which of the five mechanisms actually fired. Don't skip this — the rest of the plan depends on it.
2. **Add a 5-minute jitter to every cron and scheduled task in the fleet.** Even 60 seconds of jitter per task will materially smooth the request curve. This is the single most effective defense against `2045` (rate-growth).
3. **Audit your system prompts and tool lists for prefix stability.** If two different agents have system prompts that are 80% the same, standardize them. The goal is one shared system-prompt prefix that every agent uses. This unlocks the 66.7% input-token saving.
4. **Set a baseline.** Run `/usage` and `/insights` once a day for a week. Note the cache hit rate (if your tooling reports it), the per-agent input/output token count, the 5h-rolling usage, and the weekly-rolling usage. This baseline is what you compare against.
5. **Default the fleet to M2.7** (or M2.7-highspeed for latency-critical paths) instead of M3. Keep M3 for the two cases where it actually wins: input > 512k, and quality-critical tasks where the SWE-Bench Pro gap matters. This single change can roughly halve the rate-limit pressure on Plus-tier setups because M3's RPM is 60% lower than M2.7's.
6. **Verify whether the incident was inside the 15:00–17:30 China-time peak window.** If yes, the leading suspect is the dynamic throttle and the next-step priority is peak-hour scheduling (Section 4.2), not deeper caching work.

### 4.2 Short-term (this sprint)

The goal is to get the structural wins in place: caching, delegation, peak-hour awareness.

1. **Refactor 2–3 of your highest-volume workflows to use Hermes `delegate_task` for parallel work.** Only summaries return to the main context. This shrinks the main-context tokens (improving cache hit rate) and improves wall-clock latency. Pilot on one workflow before rolling out.
2. **Add peak-hour awareness to the scheduler.** Either move heavy work outside 15:00–17:30 China time, or build a "peak-aware" mode that throttles request rate during the window. The docs say the throttle "may tighten under load" — assume it does.
3. **Implement structured output / JSON-mode for any task that's currently re-asking for malformed responses.** The token savings on output + the elimination of re-ask cost is a free win.
4. **Switch on Hermes's `/compress` proactively** — call it on a schedule (e.g., every 10 turns) rather than waiting for the context to fill. This is a config change, not a code change.
5. **Add a session memory size cap** (`MEMORY.md ≈ 2,200 chars`, `USER.md ≈ 1,375 chars` per Hermes's own docs). Memory bloat directly inflates every subsequent request's input cost.
6. **Tighten the cache prefix.** Now that you've measured the baseline, look at which agent sessions are NOT cache-hitting and figure out why. The fix is almost always a small change in prompt order or template structure.
7. **If on Plus and consistently hitting the cap, consider Max.** The upgrade is one click and the price difference is pro-rated. But verify first that you're actually capped by the tier envelope (`remains` near zero at incident time) — if not, the upgrade won't help.

### 4.3 Medium-term (this quarter)

The goal is to make the system self-monitoring and self-correcting, and to harden the contingency design.

1. **Build a monitoring layer around the `remains` endpoint.** Poll it at a reasonable cadence (e.g., every minute from a single watchdog) and alert when `remains` drops below a configured threshold. This is the single highest-leverage observability investment.
2. **Build alerting around each of the five rate-limit mechanisms.** Each gets its own alert path: `1002`, `1041`, `2045`, `2056`, and "request success rate drops during 15:00–17:30 China time" (peak-hour throttle). One alert per mechanism, not one alert for "rate limits."
3. **Create a runbook for each mechanism.** When the alert fires, the runbook tells the on-call exactly what to do: for `2045` it's "check the request curve, look for the burst, stagger it"; for `2056` it's "check the 5h rolling and weekly bars, decide whether to wait, add credits, or upgrade"; for `1002` it's "check per-key RPM/TPM, possibly add keys and load-balance."
4. **Design a contingency tier.** For each mission-critical workload, decide: (a) is the workload on Token Plan, PayGo, or both? (b) if the Token Plan 5h cap is hit, do we wait, add credits, upgrade the tier, or migrate the workload to PayGo? (c) if the weekly cap is hit, what's the fallback? Write this down so the on-call doesn't have to decide in the moment.
5. **Adopt the skill-creation discipline** (per Hermes: "if a task takes 5+ steps and you'll do it again, ask the agent to create a skill for it"). Skills keep repeated workflows out of the main context, which keeps the system prompt stable, which improves cache hit rate. This compounds the gains from Section 4.2.
6. **Audit cache hit rate systematically.** Use the response headers (or compare input-token counts before/after a stable prefix change) to measure cache effectiveness per workflow. Make the cache hit rate a tracked KPI. Aim for > 60% on cacheable workloads; the 66.7% worked example in the docs is the floor, not the ceiling.
7. **Once a quarter, re-evaluate the model routing decision.** M3 is the new model; as it matures and as MiniMax tunes the per-key rate limits, the right routing may shift. Don't bake in a routing decision and forget it.

---

## 5. Monitoring and alerting: detect the next incident in minutes

The default observability stack is *good enough to debug after the fact* and *not good enough to detect in real time*. The work in this section closes that gap.

### 5.1 What to instrument

1. **Poll the Token Plan `remains` endpoint at a reasonable cadence** (every 60s from a single watchdog is a good default). Record `remains_5h`, `remains_weekly`, and `remains_total`. Alert when any of them drops below a configured threshold (e.g., 20% of nominal).
2. **Track per-key request rate, RPM, and TPM.** The 4xx error response codes are a direct signal: `1002` (true rate limit), `1041` (connection limit), `2045` (rate-growth), `2056` (usage). Tag every error in your log with the code.
3. **Track the per-agent session count.** This is what the Plus tier's "≈3–4 agents" hint is actually enforcing. If you cross the hint, you'll feel it before you see it in the error rate.
4. **Track cache hit rate per workflow.** Use response headers (MiniMax returns cache-related headers) or compare input tokens before/after a stable-prefix change. Make this a KPI; aim for > 60% on cacheable workloads.
5. **Run Hermes's `/usage` and `/insights` once a day.** `/usage` is per-session; `/insights` is 30-day patterns. Both are useful.
6. **Set a "no successful request for N minutes" alert.** This is the canary for any of the five mechanisms. If the fleet is silent for 5 minutes during operating hours, something is wrong.

### 5.2 Alert design

One alert per mechanism, not one alert for "rate limits." The on-call needs to know *which* mechanism fired to act on it correctly.

| Alert | Trigger | Runbook step |
|---|---|---|
| `1002` spike | More than N `1002` errors in a 5-min window | Check per-key RPM/TPM, consider request-coalescing or multi-key load balancing |
| `1041` spike | More than N `1041` errors in a 5-min window | Check concurrent connection count, close idle streams, stagger session starts |
| `2045` spike | More than N `2045` errors in a 5-min window | Plot request count over time, find the burst, smooth it (Section 4.1 step 2) |
| `2056` spike | More than N `2056` errors in a 5-min window | Check 5h and weekly `remains`, decide: wait, add credits, upgrade tier, or migrate to PayGo |
| Peak-hour throttle | Request success rate drops > X% during 15:00–17:30 China time | Reduce request rate; defer non-critical work to off-peak |
| Cache hit rate drop | Per-workflow cache hit rate drops > Y% vs baseline | Check system-prompt template changes; check that the prefix hasn't drifted |
| Watchdog silence | No successful request in N minutes during operating hours | Page on-call; check the model availability page and MiniMax status |

### 5.3 The known issue with the usage bar

The open issue MiniMax-AI/MiniMax-M2.7#47 documents two problems:
- `remains_time` can drain passively without API calls.
- The cache-read discount may not be visible in the Token Plan Plus usage bar.

Both mean the usage bar is not a single source of truth. Cross-check by tracking input tokens in your own request log against the bar's reported consumption. The gap (if any) is the cache discount, which is real but invisible in the UI.

---

## 6. Known unknowns — what to verify in your own logs

The research is thorough, but the public docs leave some questions open. Don't trust the plan to know the answer; verify each in your own data.

1. **Exact weekly credit allowance per tier.** The official FAQ says "5h rolling and weekly" but does not publish the per-week credit cap. Press releases cite "10× the 5-hour amount" but the official FAQ doesn't confirm. Run the fleet at steady state for a full week and observe the cap in action.
2. **What error code fires for a true RPM (not TPM) cap hit.** The 4 codes don't map clearly to RPM vs TPM vs 5h vs weekly. Record the exact code, the time, the request pattern, and the usage-bar state at the next incident.
3. **Whether M3 (vs M2.7) automatically applies the passive cache, and at what hit rate.** The docs list M3 in the supported models for passive caching but the explicit `cache_control` is NOT supported on M3. The implications for M3 callers are not fully detailed.
4. **Specific M3 TPM/RPM under Token Plan Plus.** The public rate-limits table is at the API-key level, not the Token Plan tier level. Whether the Plus "≈3–4 agents" cap is enforced at the RPM/TPM level or as an aggregate session counter is to be verified.
5. **Root cause of the user's "1 hour of inactivity."** The Section 1 diagnosis checklist will land on this. None of the public sources can tell you which mechanism fired in your incident.
6. **M3 thinking / reasoning tokens interaction with prompt caching and TPM.** The caching example includes thinking content and there's a `reasoning_split=True` parameter for the OpenAI SDK. How thinking tokens interact with caching, output token pricing, and the TPM cap is to be verified.

For each of these, the answer is "measure in your own logs." The plan's recommendations are robust to the unknown answers — they're conservative, leverage high-confidence mechanisms (caching, smoothing, hybrid routing), and don't depend on any single unverified number.

---

## 7. Contingency: when to wait, when to add credits, when to upgrade, when to migrate

The four options, when to use each, and the trade-offs.

### 7.1 Wait for the 5h window to roll over

- **Use when:** the 5h rolling allowance is binding, the workload is deferrable by hours, and the cost of waiting is lower than the cost of credits/upgrade.
- **Trade-off:** zero cost, but the workload is paused. The official 2056 error code tells the user "wait for the next 5h window" — this is the path the system is suggesting.

### 7.2 Add credits

- **Use when:** a 1-time or low-frequency overflow has pushed past the 5h or weekly cap, and adding credits is cheaper than upgrading the tier or migrating to PayGo. 1,000 credits = $1, 365-day validity.
- **Trade-off:** low cost, no behavioral change. The credits cover eligible overflow automatically. But: this is a stopgap, not a structural fix. If you're burning credits every cycle, the structural problem (Section 4 plan) is what to fix.

### 7.3 Upgrade the tier

- **Use when:** you're consistently at the tier envelope (check the `remains` value at incident time — if it's near zero, the tier is the binding constraint). Plus → Max → Ultra gives more concurrent agents and a larger 5h and weekly envelope.
- **Trade-off:** predictable monthly cost increase. Pro-rated for mid-cycle upgrades. The new tier takes effect immediately. If the binding constraint is per-key RPM/TPM rather than the tier envelope, the upgrade won't help and you should look at hybrid routing or PayGo migration instead.

### 7.4 Migrate a workload to PayGo

- **Use when:** a specific workload is bursting past the Token Plan envelope and PayGo pricing is more cost-efficient for that workload than upgrading the whole plan. This is most often a single heavy/bursty workload, not the whole fleet.
- **Trade-off:** PayGo is per-token, no envelope. It's structurally different from a subscription. Do the math: PayGo cost per task vs Token Plan cost per task for the specific workload. If PayGo is cheaper (which it often is for bursty or low-volume-but-high-quality work), migrate just that workload.

The right answer for most fleets is a mix: Token Plan for the steady baseline, PayGo for the bursty tail, credits as a stopgap, and tier upgrades only when the envelope is the binding constraint.

---

## 8. Appendix: quick-reference tables

### 8.1 Error codes

| Code | Meaning | Stated remedy |
|---|---|---|
| 1000 | unknown error | retry later |
| 1001 | request timeout | retry later |
| 1002 | rate limit | retry later |
| 1004 | not authorized / API key mismatch | check key |
| 1008 | insufficient balance | top up account |
| 1024 | internal error | retry later |
| 1026/1027 | input/output sensitive | change content |
| 1039 | token limit | retry later |
| 1041 | connection limit | contact us |
| 2045 | rate growth limit | "avoid sudden spikes" |
| 2056 | usage limit exceeded | "wait for next 5h window" |

The standard 429 / `RateLimitError` is mapped to 1002/2045/2056 in MiniMax's error catalog.

### 8.2 Model rate limits and pricing

See Section 2.2 (rate limits) and Section 2.3 (PayGo pricing) above. The two tables together are the complete reference for which model to use when.

### 8.3 Tier envelope

See Section 2.1 above. The Plus tier's "≈3–4 agents" hint is the published cap; if you're consistently above it, the binding constraint is the tier, not the per-key rate limits.

### 8.4 Caching behavior per model

| Model | Passive (auto) cache | Explicit `cache_control` (Anthropic-style) |
|---|---|---|
| M3 | yes (512+ tokens, prefix match) | no |
| M2.7 / M2.7-highspeed | yes | yes (5-min lifetime) |
| M2.5 / M2.5-highspeed | yes | yes (5-min lifetime) |
| M2.1 / M2.1-highspeed | yes | yes (5-min lifetime) |
| M2 | no (passive not supported) | yes (5-min lifetime) |

If you need the explicit-cache guarantee, you must use M2.x. If you need long-context (> 512k), you must use M3 and accept that the explicit cache won't help you.

### 8.5 Industry precedent: the weekly limit is not MiniMax-specific

- **Anthropic added weekly limits to Claude Pro/Max on 2025-08-28** citing "24/7 in background" usage and account-pool sharing. < 5% of subscribers affected.
- The same 5h + weekly dual-window pattern is now industry standard across Claude, MiniMax, and effectively across the metered LLM subscription market.
- Expect this to be a permanent constraint, not a bug. Plan for it.

---

## 9. One core takeaway

> The next 1-hour outage is not primarily a Token-Plan-capacity problem. It's a *traffic-shape* and *prefix-stability* problem. Smooth your request curve, stabilize your system prompts, and route long-context work to M3 only when it actually pays for itself. The capacity is already there — your fleet is just spending it inefficiently.

---

*Sources for the data in this report are documented in the research material at `/tmp/mavis-deep-research/20260604-201835-minimax-token-efficiency/document.md`. The full background fact list, source URLs, and reliability grading are in `background.md`. The judgment and analysis that shaped the structure of this report are in `judgment.md` and `analysis.md`.*
