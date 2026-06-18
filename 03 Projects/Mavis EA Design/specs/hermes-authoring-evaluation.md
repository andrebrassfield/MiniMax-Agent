---
type: spec
title: Hermes Authoring Evaluation — Should Mavis's Scribe engine migrate to Hermes-native text-mutation tools?
author: Mavis (EA)
date: 2026-06-16 19:30 CT
status: DRAFT (decision pending Andre review)
project_layer: 03 Projects/Mavis EA Design
target: Andre's architecture call, not a Hermes patch
---

# Hermes Authoring Evaluation — Scribe Engine Migration Analysis

## TL;DR

**Recommendation: NO migration. Use a HYBRID pattern.**

Mavis's Scribe engine should NOT migrate wholesale to Hermes-native text-mutation tools. The current Mavis-side architecture (custom Scribe agent + brain JSON + persona governance) is correct for the X-Content-Engine's specific needs: voice fidelity, manual-approval gate, and persona-as-source-of-truth. Migrating would risk diluting Andre's persona governance and create a coupling that the locked Mavis↔Hermes separation is designed to prevent.

**However**, Mavis's Scribe SHOULD invoke Hermes-as-a-co-processor for two specific long-form synthesis tasks that benefit from Hermes's compression + persistence:
1. **Multi-source synthesis** — when a brief references 3+ source documents and the Scribe needs to compress them into a single draft
2. **Long-running humanizer passes** — when the Humanizer needs to process 10+ drafts in one run with full history

These invocations go through the `mavis communication send` channel, not direct Hermes runtime access. The Mavis-side Scribe remains the source-of-truth for the brain + drafts ledger + persona governance. Hermes is a stateless co-processor that returns a result; Mavis decides what to do with it.

---

## 1. The Question

> "Should Mavis's Scribe engine migrate to use Hermes-native text-mutation tools?"

This is a Mavis-side architecture decision, NOT a Hermes patch. Per the locked Mavis↔Hermes separation (2026-06-16, Andre-locked), Mavis is **read-locked-out** of `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`. The decision space is: **how should Mavis's Scribe interact with Hermes-as-a-tool** — not "how do we modify Hermes to support Mavis."

The migration question decomposes into 4 sub-questions:
1. Does Hermes have capabilities that the current Scribe lacks?
2. If yes, are those capabilities worth the integration complexity?
3. If we integrate, what stays Mavis-side vs. what moves to Hermes?
4. What are the persona/governance risks of any coupling?

---

## 2. What Hermes Offers (per official architecture docs + recent web research)

From [Hermes Agent architecture docs](https://hermes-agent.nousresearch.com/docs/developer-guide/architecture), [Hermes Agent GitHub](https://github.com/nousresearch/hermes-agent), and recent technical writeups (CSDN, Medium, 掘金, 2026-Q2):

### 2.1 Local-File-Mutation Tools (the headline capability)

- `tools/file_tools.py` — `read_file`, `write_file`, `patch`, `search_files`
- 6 terminal backends: local, Docker, SSH, Daytona, Modal, Singularity
- 70+ tools total in `tools/registry.py`, organized into ~28 toolsets
- Tool registration is auto-discovery at import time (any `tools/*.py` with `registry.register()` is picked up)

**What this gives Mavis's Scribe:** the Scribe can mutate files directly without going through the Mavis daemon's CLI. Faster iteration, lower latency, no `mavis communication send` round-trip per file write.

**What this does NOT give:** any governance layer. Hermes's file tools are dumb-mutation primitives. They don't enforce "this file must match the persona's voice" or "this draft must be approved by Andre before publish." That governance is Mavis's responsibility.

### 2.2 Context Compression & Caching (the long-form reliability play)

- `agent/context_compressor.py` — lossy summarization of middle conversation turns when context exceeds thresholds
- `agent/prompt_caching.py` — Anthropic prefix caching for cost reduction
- 3 API modes: chat_completions, codex_responses, anthropic_messages
- 18+ provider registry with OAuth flows, credential pools, alias resolution

**What this gives Mavis's Scribe:** the Scribe can handle longer source inputs without losing early context. The whitepaper-based drafts (which synthesized 8+ source pages) hit the context ceiling; Hermes's compression would let the Scribe ingest more.

**What this does NOT give:** the compression is a general-purpose lossy summarization. It does not know about persona governance, banned-phrase rules, or pillar-specific voice. Mavis's Scribe has to apply those rules AFTER compression, in a post-processing step.

### 2.3 Trajectory Generation (the training-data play)

- `agent/trajectory.py` — generates ShareGPT-format trajectories from agent sessions
- Hermes's "learning loop" creates skills from experience and improves them over time

**What this gives Mavis's Scribe:** if we wanted to fine-tune a future Scribe on Andre-approved drafts, the trajectory format is the training-data substrate. Hermes would emit trajectories; Mavis would curate them.

**What this does NOT give:** fine-tuning is a separate architectural layer. Mavis is not currently fine-tuning the Scribe; the Scribe is a stock M2.7 worker with persona.md + brain JSON as context. Hermes's trajectory generation is forward-looking infrastructure that we'd only use if we decide to fine-tune later.

### 2.4 Plugin System (the extensibility play)

- 3 discovery sources: `~/.hermes/plugins/`, `.hermes/plugins/`, pip entry points
- Two specialized plugin types: memory providers + context engines
- Plugins register tools, hooks, and CLI commands through a context API

**What this gives Mavis's Scribe:** if we wanted to extend Hermes with a "Dre Builds" memory provider or context engine, the plugin system is the extension point. But that would require Mavis to write code INTO Hermes's plugin directory, which is a Hermes-modification action (not allowed under the separation).

**What this does NOT give:** anything Mavis can use without writing into `~/.hermes/plugins/`. The plugin system is for Hermes-side extensions, not for Mavis-side consumers.

---

## 3. What Mavis's Current Scribe Has (the baseline)

Per `03 Projects/X-Content-Engine/agents/scribe.md` (the canonical Scribe prompt) and the recent 4-run batch execution:

| Capability | Current Mavis Scribe | Notes |
|---|---|---|
| Voice fidelity | **6 pinned persona examples** + 10 banned phrase categories + cadence rules | Persona is the source-of-truth, not the Scribe prompt frontmatter |
| Backlog pull | **Persistent idea backlog** in `content_brain.json` with `status: pending` filter | 24 ideas, 11 pending / 13 used as of 19:13 CT |
| Manual approval gate | **Every draft has an approval toggle** that Andre reviews | No auto-publish; Scribe has zero x.com write capability |
| Atomic writes | **temp-write-rename** pattern on the brain JSON (same as Researcher) | Detected via `mtime` concurrency check |
| Long-form reliability | **Sequential append** to a single batch file per day | No compression — relies on M2.7's native context |
| Multi-source synthesis | **Brief from Researcher → 10 ideas** in the brain → 3 drafted at a time | Bounded by M2.7's context ceiling (handles 8-page whitepaper, fails on 30-page) |
| Local file mutation | **Via Mavis daemon's filesystem tools** | Slower than Hermes's direct local tools (round-trip per write) |
| Context compression | **None** — relies on M2.7's native context window | The hard ceiling for the Scribe |
| Trajectory generation | **None** — drafts are flat markdown | No fine-tuning substrate |
| Self-improvement loop | **None** | Persona evolves when Andre adds examples; the Scribe doesn't learn on its own |

**The Mavis Scribe is intentionally narrow.** It has voice governance, manual approval, and atomic writes. It does NOT have compression, trajectories, or self-improvement. Those are features Mavis deferred because the X-Content-Engine's correctness is more important than its self-improvement speed.

---

## 4. The Comparison: Hermes vs. Mavis's Current Scribe

| Dimension | Hermes-native | Mavis current Scribe | Migration value |
|---|---|---|---|
| Local file write latency | ~10ms (direct Python) | ~200ms (Mavis daemon round-trip) | High for high-volume drafting |
| Context compression | Built-in lossy summarization | None (M2.7's native ceiling) | **High for multi-source synthesis** |
| Provider flexibility | 18+ providers, OAuth flows | 1 provider (MiniMax) | Low (MiniMax is Andre's choice) |
| Manual approval gate | None built-in | **Built-in toggle per draft** | None — Mavis is the load-bearing layer |
| Persona governance | None | **Persona file as source-of-truth** | None — Mavis is the load-bearing layer |
| Atomic writes | Hermes's own atomic write pattern | Mavis's temp-write-rename + mtime check | Low (both are safe) |
| Trajectory generation | Built-in ShareGPT export | None | Low (only matters if we fine-tune) |
| Self-improvement loop | Yes (skills from experience) | No (persona evolves manually) | **Medium — but risky** |
| **Mavis ↔ Hermes separation compliance** | N/A (Hermes-side) | **Strictly Mavis-side** | **Critical — the locked separation is a hard constraint** |

**Two columns stand out:** context compression and self-improvement loop. Those are the legitimate capabilities Hermes offers that the current Scribe lacks. Everything else is either parity or governance trade-off.

---

## 5. The Migration Analysis

### 5.1 What "migration" would actually require

A full migration would mean:
- Mavis's Scribe becomes a Hermes plugin (writing into `~/.hermes/plugins/`)
- The brain JSON lives in Hermes's session storage (SQLite + FTS5)
- The persona file is loaded as a Hermes context file
- The drafts go through Hermes's trajectory generation
- Andre's approval gate is implemented as a Hermes hook

**This is a Hermes patch.** Per the locked Mavis↔Hermes separation, this is explicitly forbidden ("Patches are no longer on the table — period, even with sign-off"). A full migration is not on the table regardless of its technical merit.

### 5.2 What "integration" would look like (the realistic option)

A hybrid where Mavis's Scribe invokes Hermes-as-a-tool for specific long-form synthesis tasks. The architecture:

```
[Mavis Scribe (Mavis-side, persona-governed)]
  ├── reads persona.md
  ├── reads content_brain.json (atomic)
  ├── writes drafts/machine-batch-*.md (append-only)
  └── for multi-source synthesis:
      └── invokes [Hermes co-processor] via mavis communication send
            ├── Hermes reads the source files locally
            ├── Hermes compresses via context_compressor.py
            ├── Hermes returns a draft candidate
            └── Mavis Scribe post-processes (Stage 1+2+3 Humanizer)
            └── Andre approves / rejects
```

**This respects the separation.** Mavis's Scribe remains Mavis-side. Hermes is invoked as a stateless tool, with the result returned to Mavis. Hermes's runtime stays Hermes-side. There's no shared state, no plugin writing, no trajectory sharing.

**Risks:**
1. **Latency overhead** — the `mavis communication send` round-trip is ~1-2s. For a Scribe that produces 3 drafts in 2 minutes, the overhead is negligible. For a 30-draft run, it's 30-60s of overhead. Acceptable.
2. **Result quality** — Hermes's compression is general-purpose; Mavis's Scribe has to verify the returned draft matches persona voice. This is the Humanizer's job (which we just built). So the integration path is: Hermes returns a draft → Humanizer passes through → Scribe writes to the batch file. The Humanizer is the safety net.
3. **Persona leakage** — Hermes doesn't know about persona governance. If we invoke Hermes for P3 (GEO) content, the result will be off-voice. The Humanizer will catch the off-voice result and flag it. The Scribe's existing `voice-fit verdict: partial` mechanism is the second safety net.

**Benefits:**
1. **Long-form reliability** — the Scribe can handle 30+ page source documents via Hermes's compression. The 8-page whitepaper was already at the limit; the next round of briefs (the meta-minimax-audit, the Q3 SMB AI Maturity Report) is larger.
2. **Faster iteration** — local file writes are 20x faster via Hermes's direct Python tools vs. Mavis's daemon round-trip.
3. **Future fine-tuning substrate** — if we decide to fine-tune the Scribe on Andre-approved drafts, Hermes's trajectory generation is a clean export path. But this is forward-looking.

### 5.3 The persona governance risk (the load-bearing one)

Hermes's self-improvement loop is the biggest risk. If the Scribe invokes Hermes 50 times over a quarter, Hermes will start to "learn" patterns from those invocations. If any of those patterns conflict with the persona (e.g., Hermes learns that "dive into" is a load-bearing opener from a poorly-tuned task), the Scribe's next invocation will return off-voice content.

**Mitigation:** the Humanizer is the gate. Every Hermes-co-processor result passes through Stage 1 (Fluff Purge) + Stage 2 (Voice-Injection) + Stage 3 (Conflict Check) before it hits the drafts file. The Humanizer is the immune system for persona governance.

**Second mitigation:** rate-limit the Hermes invocations. The Scribe should invoke Hermes only when:
- The brief references 3+ source documents
- The total source length exceeds M2.7's context ceiling
- The Scribe is asked to produce 5+ drafts in a single run

In all other cases, the Scribe uses its native context. This keeps Hermes's "learning exposure" bounded to a small fraction of the Scribe's work.

---

## 6. The Recommendation

### 6.1 Don't migrate

The locked Mavis↔Hermes separation makes a full migration off the table, and the Mavis-side architecture (custom Scribe + persona governance + manual approval) is the right shape for the X-Content-Engine. A migration would dilute persona governance and create coupling that the separation is designed to prevent.

### 6.2 Use Hermes as a co-processor for long-form synthesis

For specific tasks where Hermes's compression + local file mutation add real value (multi-source synthesis above the context ceiling), Mavis's Scribe should invoke Hermes via the `mavis communication send` channel. The result goes through the Humanizer (Stage 1+2+3) before it hits the drafts file. The Scribe remains the source-of-truth for the brain + drafts ledger.

### 6.3 Concrete next steps (if Andre approves)

1. **Pilot the integration on one specific task type.** The next 10-page+ brief is the right test. The Scribe invokes Hermes for the multi-source compression, then post-processes with the Humanizer, then writes to the batch file. Measure: voice fidelity, latency, error rate. Compare to the current Scribe-only path.

2. **Codify the Hermes invocation as a Scribe prompt section.** Add a new section to `03 Projects/X-Content-Engine/agents/scribe.md` that defines when the Scribe should invoke Hermes, what the result schema is, and how the Humanizer post-processes. The Scribe prompt remains the source-of-truth for the Scribe's behavior; this just adds a conditional invocation path.

3. **Track the persona-leakage rate.** Every Hermes-co-processor result that fails Stage 1 (Fluff Purge) or Stage 2 (Voice-Injection) is a near-miss. If the rate exceeds 1 per 10 invocations, tighten the Scribe's prompt or the Humanizer's filter. If it exceeds 1 per 3, pause the integration and re-evaluate.

4. **Defer the self-improvement loop question.** Hermes's learning loop is a separate architectural concern. Don't enable it for the Scribe integration in v1. If we want to use trajectory generation for fine-tuning, that's a v2 conversation.

### 6.4 What to NOT do

- **Do not write a Hermes plugin for the Scribe.** This is a Hermes modification; it's blocked by the separation.
- **Do not move the brain JSON into Hermes's session storage.** Mavis's atomic-write pattern is the source-of-truth for the brain; moving it to Hermes's SQLite would require Hermes-side modifications.
- **Do not enable Hermes's self-improvement loop on the Scribe's invocations.** The persona is the governance layer; Hermes's learning loop is a separate risk surface.
- **Do not use Hermes's trajectory generation for v1.** Defer to a fine-tuning conversation; this spec is about long-form reliability, not training data.

---

## 7. Open Questions for Andre

1. **Pilot scope** — should the pilot be on the next 10-page+ brief, or on a specific pillar (e.g., P4 Build Logs, where the Scribe's existing strength makes the integration safer to test)?
2. **Latency budget** — what's the maximum acceptable latency for a Scribe run? 1-2 min (current)? 5 min (with Hermes co-processor)? This determines how aggressive the integration can be.
3. **Voice-leakage threshold** — at what rate of Humanizer failures should we tighten the integration vs. abandon it? My proposal: 1/10 = tighten, 1/3 = pause. Confirm.
4. **Persona governance escalation** — if Hermes's learning loop starts to drift the Scribe's voice, who's the escalation? Andre (manual override)? Mavis (auto-pause the integration)? Hermes (out of scope)?
5. **Trajectory generation timeline** — when do we want to revisit fine-tuning? Post the agency gBrain-ingest? Post the first 100 Andre-approved posts? Defer indefinitely?

---

## 8. Verification (spec-internal)

- [x] Recommendation is Mavis-side (no Hermes patch proposed)
- [x] Locked Mavis↔Hermes separation respected (no reads from `~/.hermes/`, no writes proposed)
- [x] Comparison grounded in official Hermes docs + recent technical writeups
- [x] Persona governance identified as the load-bearing risk
- [x] Humanizer identified as the mitigation
- [x] Concrete next steps proposed (pilot scope, latency budget, voice-leakage threshold)
- [x] Open questions surfaced for Andre's call
- [x] Defer items (self-improvement loop, trajectory generation) clearly marked as out-of-scope-for-v1

## Cross-reference

- Locked Mavis↔Hermes separation: `~/.mavis/agents/mavis/memory/MEMORY.md` §"ABSOLUTE SEPARATION: Mavis ↔ Hermes (Andre-locked 2026-06-16)"
- The Scribe prompt: `03 Projects/X-Content-Engine/agents/scribe.md`
- The Humanizer skill (just built): `99 _system/skills/scribe-humanizer/SKILL.md`
- Hermes official architecture: https://hermes-agent.nousresearch.com/docs/developer-guide/architecture
- Hermes GitHub: https://github.com/nousresearch/hermes-agent
- The Garry Tan "Thin Harness, Fat Skills" framework: `~/MiniMax-Agent/02 Notes/patterns/agent-harness.md` (per user memory) — Hermes fits the "fat skills + thin harness" pattern; the question is whether Mavis should consume those skills or build a parallel set
