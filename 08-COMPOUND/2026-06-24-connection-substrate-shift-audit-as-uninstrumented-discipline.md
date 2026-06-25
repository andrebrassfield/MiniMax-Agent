---
date: 2026-06-24
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: true
thesis-link: Thesis 1 (the bottleneck is spec throughput, not implementation) + Thesis 3 (skills beat agents when the harness is mature)
domains-crossed: [fb-engine-operations, xce-operations, ea-design-patterns]
---

# Connection: Three independent substrate shifts in 48 hours, zero shared dependency map

**Why this connection matters:** Three separate browser/CDP substrate events produced silent cron failures in the last 48 hours, and the only thing they share is the *discovery* mechanism — each was surfaced by a cron fire running into the failure and a chief session writing a postmortem. There is no registry, no map, no shared audit. Reading the three postmortems together reveals that the architecture-shift cron-audit discipline (named explicitly in the FB-Engine 06-24 postmortem) is **a documented rule that is not instrumented** — same shape as the "ships that aren't load-bearing" connection, but at the infrastructure layer instead of the skill layer. The substrate→cron dependency map the FB-Engine postmortem proposes for the *long term* is exactly the audit layer that would have caught all three of these incidents within hours instead of days.

**Note A:**
- Title: FB-Engine PM cron HALT — 2026-06-24 20:00 CT (CDP `Browser.setDownloadBehavior`)
- Path: `~/MiniMax-Agent/03 Projects/FB-Engine/postmortems/2026-06-24-2000-cdp-setdownloadbehavior.md`
- Claim: Chrome 149.0.7827.156 auto-updated and removed `Browser.setDownloadBehavior` support from regular (non-automation) CDP contexts. Playwright 1.60.0 calls it unconditionally during `connect_over_cdp()`. Result: every FB-Engine cron (AM + PM + reader) HALTs at the reader step. The postmortem explicitly proposes "a FB-Engine substrate→cron dependency map (which crons touch Chrome? which touch Playwright? which touch the FB session?) so future substrate shifts trigger a targeted cron audit, not a global one."

**Note B:**
- Title: reply-sweep-daily — DEPRECATED 2026-06-24 19:01 CT
- Path: `~/MiniMax-Agent/03 Projects/X-Content-Engine/postmortems/2026-06-24-reply-sweep-deprecation.md`
- Claim: XCE strategy was authored 2026-06-18 against a Playwright MCP pipeline; the actual runtime uses mavis browser bridge (wired 2026-06-17). The 06-18 postmortem flagged 11 items; the architecture-fix (Option A/B/C) was never picked. Every cron fire for 5+ days HALTed at step 0. Substrate shift (Playwright → mavis browser) happened 2026-06-17; no cron audit fired. The reply-sweep-daily was the only XCE cron that surfaced the issue; `x-analytics-tracker-daily` surfaced a parallel issue (H1 browser bridge offline) but they were diagnosed independently.

**Note C:**
- Title: XCE Feedback Loop Audit — T+7d (2026-06-24 09:00 CT) — Gap 2
- Path: `~/MiniMax-Agent/03 Projects/X-Content-Engine/memory/feedback-loop-audit-2026-06-24.md`
- Claim: `x-analytics-tracker-daily` had 3 consecutive daily halts (Jun 22 + Jun 23 = H1 mavis browser bridge offline; Jun 18 = H4 + H6 separate issue). The Chrome native messaging host (the unpacked `Mavis Browser Bridge` extension) is not connected. The substrate shift (extension disconnected) was not detected by any audit — it was discovered when the cron fired into the failure. The `nextRun: Jun 2027` timestamp on the stuck publish-tied `xce-feedback-2026-06-17/18` crons is also a substrate issue: one-shot crons that missed their window were rescheduled into 2027 without firing.

**What reading both reveals:** Three substrate events, three independent postmortems, zero shared infrastructure.

The unifying pattern: **Mavis has substrate-level dependencies (Chrome, Playwright, CDP, mavis browser bridge extension, X.com cookies, FB session cookies) but no instrumented map of which crons depend on which substrates.** When a substrate shifts, the discovery mechanism is *a cron fire running into the failure* — which means the failure is detected only when the cron's next fire time hits, which means there is an unbounded detection delay (in the `reply-sweep-daily` case, 5+ days).

The architecture-shift cron-audit rule (named in MEMORY.md: "When a pipeline substrate changes (Playwright → mavis browser, MCP rotation, cookie-jar source shift), audit every cron that touches the substrate") is a **documented rule that is not instrumented.** No cron fires when a substrate shifts. No skill checks the bridge connection proactively. No registry diffs "substrates I depend on" against "substrates that recently changed." The discipline exists; the mechanism does not. This is exactly the same shape as the "ships that aren't load-bearing" connection (skills without triggers are tombstones) and the cron-success-misleading connection (cron-runner reports success without checking revealed state). **Mavis has rules without mechanisms.**

The three incidents also reveal a clear pattern in *which substrates are involved*:
- **Browser engine + automation SDK** (Chrome 149 + Playwright 1.60.0) — affected FB-Engine reader path (06-24 PM)
- **Browser bridge extension** (mavis native host disconnected) — affected XCE reader path (06-22 + 06-23 daily halts; 06-24 09:00 audit)
- **Browser cookie jar** (Playwright Chrome has no X cookies; mavis Chrome has no FB session) — affected XCE reply-sweep (06-18 → 06-24) + FB-Engine (06-23 20:00 Mode B)
- **Cron-engine window handling** (one-shot crons missing their window rescheduled to Jun 2027) — affected XCE publish-tied crons (06-24 audit Gap 1)

That's four substrate categories, three incidents, two projects, one audit rule. A substrate→cron dependency map would have flagged the Chrome-149 update as "touches: FB-Engine reader (Playwright CDP), all mavis-browser-bridge crons" and the bridge extension disconnect as "touches: XCE analytics, all X.com browser automations" — triggering targeted audits within minutes of the shift instead of waiting for the next cron fire to discover it.

**Suggested next step:**
- Surface in tomorrow's morning brief as a `thesis-relevant: true` connection (Thesis 1 + Thesis 3).
- Promote the "substrate→cron dependency map" from the FB-Engine 06-24 postmortem's long-term follow-up to a near-term spec. The map is a single YAML file (`~/.mavis/state/substrate-cron-map.yaml`) listing each substrate (Chrome version, Playwright version, mavis bridge extension, FB session cookie, X session cookie, etc.) and the crons that depend on it. The map is updated by hand when a substrate shifts; a daily audit cron (`substrate-shift-audit-daily` at 04:00 CT) diffs the map against current system state and surfaces drifted substrates + dependent crons.
- Pair this with the "ships that aren't load-bearing" audit (skill catalog vs cron registry diff) — they are two halves of the same gap. The unified name for both is **`mavis self-verification registry`**: a single source of truth that names every artifact (skill, cron, substrate, loop) and its revealed state. This is the missing audit layer Mavis needs before it can credibly call itself "a second self."
- Add a fast-path for the `nextRun: Jun 2027` issue: any one-shot cron whose scheduled window has passed without firing should surface in the morning brief with a "window missed" flag, not silently reschedule into the next year. The XCE feedback-loop audit's Gap 1 has been sitting for 4 days; the surface mechanism missed it.
- For the long-term Mavis-as-loop-engineer plan (`mavis-loop-engineering-plan-2026-06-22.md` Item 1, bundle manifests), include substrate manifests in the bundle definitions. A bundle isn't just a skill list — it's a skill list + the substrates those skills touch. The `bundle: x-content-publish-ops` manifest should declare: "depends on: mavis browser bridge, X session cookie @DreTheSalesGuy, X Premium OR FxTwitter API key." Substrate shifts to any of those should trigger a bundle-level audit.