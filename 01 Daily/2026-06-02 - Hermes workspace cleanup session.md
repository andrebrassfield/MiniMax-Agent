---
date: 2026-06-02
type: daily-session
tags: [hermes, m3, cleanup, capture]
---

# 2026-06-02 — Hermes workspace cleanup session

> Evening capture. Hermes-side session, summarized by Mavis (EA mode) at Andre's request before he jumped in the shower. ~20 min budget, capture + link only — no `~/.hermes/` reach-ins, no irreversible actions.

## What happened

A single working session inside the Hermes workspace that touched four distinct concerns, in order:

1. **Worktree prune** — old/stale worktrees (the detritus of past Hermes experiments) got removed. Reclaim disk, simplify `git worktree list`.
2. **M3 migration** — the Hermes side of the rollout to MiniMax-M3 as the default model. This is the same `minimax/MiniMax-M3` swap already done in this vault (see [[learnings]] §"Migration notes: M2.7-highspeed → M3").
3. **8192 cap discovery** — symptom: truncated JSON output on M3. Root cause: an `8192` token ceiling that was silently clipping completions. Discovery was the moment this stopped being a "M3 is flaky" mystery and became a concrete config-layer fix.
4. **Two-repos insight** — the real "aha" of the session. The 8192 cap and the fix don't live in one place. They live in **two different Hermes repos**, at two different layers, both needing changes for M3 to behave.

## Outcome

- **287M reclaimed** on disk from the worktree prune.
- **Local commit `0cb3a5a`** on the working repo (the M3-migration commit with the cap fix bundled in).
- **Vault snapshot** taken — a safe point to roll back to if the dual-repo rollout goes sideways.
- **Deferrals logged** — items intentionally punted to a later session (specific deferral list is in the Hermes session, not in scope for this capture).

## Key decisions and the reasoning

- **Treat the 8192 cap as a config problem, not a model problem.** Once the cap was identified, the next decision was *where* to fix it. The insight was that the answer is "both" — see [[Hermes dual-repo architecture (M3 fixes)]].
- **Bundle the cap fix with the M3 migration in one commit (`0cb3a5a`).** Reasoning: they're the same change from a rollback perspective. If M3 is bad, you want to revert one commit, not two.
- **Snapshot before deploying the dual-repo fixes.** The 8192 fix has application-layer + framework-layer surfaces; if one layer works and the other doesn't, you want a known-good point to fall back to.
- **Defer, don't force.** Items that didn't fit the budget (or that need a second pass once the dual-repo fixes are validated) were logged as deferrals, not silently dropped. Per [[2026-06-01-040-audit-before-action]] and the [[Reconfirm before irreversible actions]] instinct.

## What M3 actually requires (in this session's view)

The cap wasn't M3's fault. M3's actual specs (per [[M3 Capabilities]] / agent memory):
- 1M context via MSA sparse attention
- 128k+ output tokens (40k cap from M2.7 is gone)
- Native image+video+audio input

So an 8192 cap on M3 is a config inheritance from M2.7-era defaults, not a model limit. The fix is to *raise the cap to match what M3 actually supports*, not to clamp M3 down to old ceilings.

## What I deliberately did not do (EA-mode boundary)

- Did **not** reach into `~/.hermes/` to quote line numbers from the Hermes code. The actual cap location, the exact `max_tokens=` line, and the `transformModel` override site are in the Hermes workspace — out of scope per SOUL.md hard constraint ("Modifying Hermes, OpenClaw, kanban, gbrain, launchd, or any fleet tooling | This vault is the boundary — fleet is off-limits").
- Did **not** push, deploy, or change anything in the Hermes repo. This is capture only.
- Did **not** run any verification (re-test, re-eval) — that's a Hermes-side action.

## Connections

- [[Hermes dual-repo architecture (M3 fixes)]] — the permanent project note for the insight behind this session
- [[learnings]] § "Migration notes: M2.7-highspeed → M3" — the M3 swap that made this whole session necessary
- [[M3 Capabilities]] — the model spec the cap was wrong about
- [[2026-06-01-040-audit-before-action]] — the instinct that drove the "snapshot before deploying" decision
- [[2026-06-01-030-reconfirm-before-irreversible-actions]] — the constraint that kept this capture read-only
- [[2026-06-02]] — earlier today (scheduling items)
- [[2026-06-01]] — yesterday; set up the M3 migration context
- User memory: [[Hermes two-repo layout]] entry (appended in this same capture)

## What I couldn't find / not in scope

- Specific line numbers in Hermes Python/TypeScript code where the 8192 cap lived (in `~/.hermes/`, not readable from EA mode)
- The full text of the Hermes skill "File mtime before chasing a missing artifact" — referenced by name only, since the skill file lives in `~/.hermes/skills/`
- Exact deferral list (lives in the Hermes session, not in this conversation)
- The exact `git log` output of `0cb3a5a` (I can quote the SHA Andre gave me, but not the diff/author/timestamp)
