---
date: 2026-06-26
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: true
thesis-link: Thesis 1 (spec throughput is the bottleneck) + Thesis 5 (Mavis is structurally isomorphic to an LLM)
domains-crossed: [dose-of-proof-engine, cron-runner-measurement, loop-engineering-vocabulary]
---

# Connection: v0.4 §9 "12/12 PASS" was the cron-success-misleading disease in engine-test form; the hard interlock (§3d) is the spec-level fix that closed the loop

**Why this connection matters:** The 2026-06-24 nightly-connection identified a disease ("cron `lastResult: success` ≠ skill-success" — Mavis's cron-runner tracks bash exit code, not work completion). The 2026-06-25 v0.4 §9 evidence turned out to be the **same disease at the engine-test layer**, and the Co-CEO's hard-interlock rule (§3d, imposed 21:21 CT the same day) is the **first spec-level fix** Mavis has implemented for it. Reading the three notes in sequence — the Jun 24 connection, the Jun 25 §9 finding, the Jun 25 §3d rule — reveals a loop that closed in 24 hours: name the disease (Discover) → instantiate it in a new layer (Execute) → impose a spec-level fix that the verifier can enforce (Plan) → re-verify (Verify). The fix is partial (it covers the engine layer, not the cron-runner layer yet), but the **shape** of the fix is now visible and reusable.

**Note A:**
- Title: Connection: `reply-sweep-daily` deprecation ↔ `x-analytics-tracker-daily` halt pattern (2026-06-24)
- Path: `~/MiniMax-Agent/08-COMPOUND/2026-06-24-connection-cron-success-misleading-measurement-system.md`
- Claim: Two XCE cron failures shared the same root cause at the *measurement-system* layer — the cron-runner reports `lastResult: success` whenever the bash script exits 0, even if the skill inside the script HALTed at step 0 and surfaced a Telegram notification. The connection proposes that the fix is not a script patch but a spec change: a `mavis cron health` audit layer that distinguishes `bash_exit_code` from `skill_outcome` (success / halt / fabricated) and reports both.

**Note B:**
- Title: v0.4 Gate Fix — Review Package §9.1-§9.4 (LLM-live §2 results, 2026-06-25)
- Path: `~/MiniMax-Agent/03 Projects/Dose of Proof/specs/v0.4-review-package.md`
- Claim: When the LLM layer was finally wired live (real MiniMax API key per Co-CEO directive 21:38 CT), the §2 regression produced **8/12 PASS, 4/12 FAIL** — every FAIL was the LLM over-blocking a CLEAR educational post as SENSITIVE. Crucially, before the LLM was live, the regex-only test reported "12/12 PASS" with the bash exit code at 0. The 12/12 figure was a function-count metric — regex layer flagging exactly the §2 expected flags, LLM layer fail-closed to SENSITIVE because `apiKey: sk-xxx` was a placeholder. **The "12/12 PASS" headline number was technically correct and operationally misleading in exactly the shape the Jun 24 connection named.**

**Note C:**
- Title: v0.4 §3d (Hard Interlock rule, Co-CEO imposition 2026-06-25 21:21 CT) + §9.4.1 sign-off (2026-06-26 11:54 CT, Decision B)
- Path: `~/MiniMax-Agent/03 Projects/Dose of Proof/specs/v0.4-review-package.md` + `03 Projects/Dose of Proof/specs/v0.5-staged-plan.md`
- Claim: Per [[triage-gate-spec]] §3d: "A halt that depends on a session reading a prompt correctly is not a halt." The implementation is a state file at `~/.mavis/state/dop-engine-halt.state` with `{halted: true, halted_at, halted_by, reason, resume_condition}` — checked as the FIRST action in main() of any script that can mutate production state. On `halted=true`, the script prints a clear stderr message and exits with EX_CONFIG (78). Cron jobs that can execute the halted service are `mavis cron disable`d at the daemon level — not just frontmatter-prompted to stand down. **The hard interlock is the first Mavis implementation of "verifier checks revealed state, not stated state."**

**What reading all three reveals:**

The Jun 24 connection named the disease: Mavis's measurement-system reports bash-exit, not skill-outcome. The disease is a general one — it applies to any layer where Mavis can produce a clean output without the work being complete.

The Jun 25 §9 finding is the **same disease at the engine-test layer**. The v0.4 review package was generated with bash exit 0, and the headline metric was "12/12 PASS." That headline was *literally true* at the bash-exit layer (the script ran without crashing). It was *operationally false* at the work-completion layer (the LLM layer was fail-closed to SENSITIVE for every call because `apiKey: sk-xxx` was a placeholder). If the Co-CEO had not asked for §9 evidence ("I want the ACTUAL model classifications, not fail-closed defaults"), the v0.4 sign-off package would have shipped with the "12/12 PASS" headline as the load-bearing evidence. **The v0.4 §9 finding is the canonical example of why stated state ≠ revealed state, applied to engine tests.**

The Jun 25 §3d rule is the **spec-level fix** at the engine layer. The hard interlock is structurally different from a prompt-level halt because:
- A prompt-level halt is a *request* to a future session to honor the halt. The session can ignore the request.
- The hard interlock is a **state file read as the first action** of any script that can mutate production state. The script cannot mutate state without first reading the state file. If the state file says `halted: true`, the script exits 78 before any mutation occurs.

This is the same pattern as the Jun 24 connection proposed (`mavis cron health` audit layer that distinguishes `bash_exit_code` from `skill_outcome`), but at the engine layer instead of the cron-runner layer. The fix is partial (engine only, not cron-runner), but the *shape* of the fix is now visible and reusable: **state file → first-action check → exit code on halt → daemon-level disable of triggering crons**.

The chronology is a 24-hour loop closing:
- **Discover** (Jun 24 23:00 CT nightly-connection): name the disease at the cron-runner layer
- **Execute** (Jun 25 ~21:00 CT): instantiate the disease at the engine-test layer (v0.4 §9 finding)
- **Plan + Verify** (Jun 25 21:21 CT): Co-CEO imposes §3d hard-interlock rule as a spec change, not a patch
- **Iterate** (Jun 26 11:54 CT): sign-off LOCKED on option B (ship citation_gate independently, hold LLM for v0.5 calibration) — the modular-system thinking is itself a response to the measurement-system disease. The working part ships; the part being tuned waits.

The deeper observation: **the citation_gate shipping to v0.5 staging independently is the same discipline as the hard interlock**, applied at the product level instead of the spec level. Citation gate has 4/4 regression PASS and is independently useful (catches the specific fb-004 rev1 failure that motivated it). LLM layer has 8/12 PASS and is being tuned. The decision to ship the working part while holding the part being tuned is the *product-level* equivalent of "track revealed state, not stated state" — the v0.5 release contains only the pieces that have been revealed to work, not the pieces that have been stated to work.

This is also Thesis 5 (Mavis-isomorphic-to-LLM) in operational form. The 5-Stage Pipeline's Stage 5 (Evaluation) is "human benchmarks after alignment, no single score captures a good model." The hard interlock is Mavis's first concrete implementation of an *evaluation* that doesn't trust a single score: it requires a state-file check before action, plus a verifier (Co-CEO) who can overrule the engine's stated state. Stage 5 in Mavis form is **multi-signal revealed-state verification**, not single-signal reported-state reporting.

**Suggested next step:**
- Add a new discipline note to `~/.mavis/agents/mavis/memory/cron-discipline.md`: "**Hard-interlock pattern (engine layer):** state file at `~/.mavis/state/<agent>-<service>-halt.state` with `{halted: true, halted_at, halted_by, reason, resume_condition}` — checked as FIRST action in main() of any script that can mutate production state. Cron jobs that can execute the halted service are `mavis cron disable`d at the daemon level, not just frontmatter-prompted. EX_CONFIG (78) on halt. This is the canonical implementation of 'verifier checks revealed state, not stated state.'"
- Extend the discipline to the cron-runner layer: propose `mavis cron health` (the Jun 24 connection's ask) as the cron-runner-side implementation of the same pattern. The state-file check pattern transfers directly: a cron-runner-level state file that any cron can read at first action; cron reports `lastResult: success` only if `bash_exit_code == 0 AND skill_outcome in {success, halt_filed}`. Anything else reports `lastResult: misreported`.
- The v0.5 sprint acceptance criteria (G6: "Hard interlock respected — Engine HALTED state honored by any cron firing during calibration") should be generalized to a permanent spec: every future engine / producer that Mavis ships has a corresponding hard interlock spec, not just the dose-of-proof engine.
- Surface in tomorrow's morning brief as a `thesis-relevant: true` connection (Thesis 1 + Thesis 5).
