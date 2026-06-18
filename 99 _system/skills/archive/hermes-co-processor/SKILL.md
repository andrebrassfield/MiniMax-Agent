---
name: hermes-co-processor
description: Mavis-side utility for invoking Hermes as a stateless long-form synthesis co-processor. Wraps context (file paths, not raw text) and ships via mavis communication send to a Hermes worker session when input exceeds 8,000 words OR requires complex trajectory analysis. Hermes returns STRUCTURAL output only (analysis, compression, formatting) — never raw text mutations. The Mavis-side caller post-processes the result through the scribe-humanizer before Andre ever sees it. This is NOT a Hermes patch and NOT a plugin install — Mavis stays strictly Mavis-side. The Mavis↔Hermes separation is preserved: Mavis only uses the standard inter-agent communication channel, never writes to ~/.hermes/, never reads Hermes internals. Triggers when a brief or draft crosses 8,000 words, when multi-source synthesis requires context compression, or when trajectory-format analysis is requested. Read-only on the source file.
---

# Hermes Co-Processor — Mavis-Side Long-Form Synthesis Utility

## What this skill does

You are the **co-processor dispatcher**. You sit between Mavis's Scribe/Researcher and Hermes.

The X-Content-Engine's Scribe and Researcher are Mavis-side agents. They have persona governance, manual-approval gates, and atomic-write discipline. They are correct for the X-Content-Engine's specific needs.

But the Scribe and Researcher are bounded by **M2.7's native context window** for any single run. A 30-page whitepaper, a 3-source synthesis brief, or a trajectory analysis across multiple sessions can exceed that ceiling. The Scribe can compress text, but it cannot compress multi-document context across files.

Hermes, by contrast, has **built-in context compression** (`agent/context_compressor.py`) and **local file mutation tools** (`tools/file_tools.py`). For specific long-form synthesis tasks, Hermes can do work Mavis's Scribe cannot.

**This skill wraps Mavis's long-form task in a Hermes invocation, ships it via the standard inter-agent communication channel, and returns the result to the Mavis-side caller.** Mavis stays strictly Mavis-side. The Scribe and the Humanizer are still the governance layer.

This is the **hybrid pattern** documented in `03 Projects/Mavis EA Design/specs/hermes-authoring-evaluation.md`. This skill is the implementation of the "Hermes-as-co-processor" branch.

## When to run

**Trigger phrases:**
- "send this to Hermes" / "invoke Hermes co-processor" / "use the co-processor on this"
- "compress this brief" / "synthesize these 3 sources"
- "long-form synthesis on [file]" / "trajectory analysis on [scope]"

**Auto-trigger thresholds (load-bearing — do not change without Andre's sign-off):**
- **Word count:** any input file exceeding 8,000 words
- **Source count:** any brief that references 3+ source documents
- **Trajectory analysis:** any request to analyze multiple sessions for pattern extraction
- **Multi-format synthesis:** any request that requires combining 2+ different output formats (e.g., narrative + table + code blocks)

**Do NOT run for:**
- Anything that fits M2.7's native context (under 8,000 words, single source, single format)
- Anything that needs persona governance applied DURING the synthesis (the co-processor doesn't know about Andre's persona — the Humanizer is the only safety net)
- Anything that needs Hermes's self-improvement loop enabled (deferred to v2; this skill is read-only-by-default for trajectory analysis)
- Any task that would require writing into `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/` (the Mavis↔Hermes separation is absolute)

## Inputs

| Input | Default | Required |
|---|---|---|
| Source file(s) | (none — must be specified) | **yes** — paths only, never raw text |
| Operation type | (none) | **yes** — one of: `compress`, `synthesize`, `trajectory-analyze`, `format-rewrite` |
| Output schema | (operation-dependent) | **yes** — see Outputs section |
| Word count budget | (caller's responsibility) | no — but the co-processor should return a summary if output exceeds caller's budget |
| Persona overlay | (none) | **DISABLED by default** — Hermes does not have the persona; the Humanizer is the only governance layer |

**Critical: the source input is FILE PATHS, not raw text.** Mavis wraps the context by reading the file metadata + a brief 1-paragraph description of what each file contains. Hermes reads the files locally. Raw text through `mavis communication send` would burn tokens on the channel AND lose the file-path resolution that makes Hermes's local-file-mutation tools valuable.

## The 4 Operation Types

### Operation 1: Compress

**Use case:** a single source file exceeds 8,000 words; Mavis needs a compressed version that fits in M2.7's context.

**Input schema:**
```json
{
  "operation": "compress",
  "source_files": ["path/to/source.md"],
  "target_word_count": 4000,
  "preservation_priorities": ["specific_numbers", "key_quotes", "structural_skeleton"]
}
```

**Output schema:**
```json
{
  "compressed_text": "[verbatim compressed text]",
  "compression_ratio": 0.42,
  "preserved_facts": ["$876K/year", "27 calls × $140", "9.5x payback"],
  "lost_facts": ["(list of facts removed during compression)"],
  "structural_notes": "[1-paragraph summary of the original's structure]"
}
```

**Why "lost_facts" is mandatory:** the co-processor's compression is lossy. Mavis's caller needs to know what was dropped so the Humanizer can verify nothing load-bearing was lost. If `lost_facts` contains any banned-phrase pattern, persona rule, or specific number from the source, the Humanizer flags it.

### Operation 2: Synthesize

**Use case:** 3+ source files need to be combined into a single brief or pattern-extraction document.

**Input schema:**
```json
{
  "operation": "synthesize",
  "source_files": ["path/to/source1.md", "path/to/source2.md", "path/to/source3.md"],
  "synthesis_focus": "Top 5 hooks + 5 formats + 5 pain points + 10 ideas across all sources",
  "brain_schema_target": "03 Projects/X-Content-Engine/memory/content_brain.json"
}
```

**Output schema:**
```json
{
  "synthesized_brief": "[markdown brief, Researcher-style]",
  "hooks_extracted": [...],
  "formats_extracted": [...],
  "pain_points_extracted": [...],
  "ideas_generated": [...],
  "source_attribution": {
    "hook[N]": "source1.md §3.2",
    "format[N]": "source2.md §1",
    "...": "..."
  }
}
```

**Why "source_attribution" is mandatory:** every extracted pattern must trace to a source post. The Researcher's "no fabrication" rule applies — the co-processor is just a faster Researcher, not a content inventor.

### Operation 3: Trajectory-Analyze

**Use case:** analyze multiple Scribe sessions for pattern extraction (e.g., "which pillars produce the highest-engagement drafts?" or "what hooks land best across the 30-day window?").

**Input schema:**
```json
{
  "operation": "trajectory-analyze",
  "session_files": ["drafts/machine-batch-2026-06-16.md", "drafts/machine-batch-2026-06-15.md", "..."],
  "analysis_focus": "pillar_performance + hook_performance + format_performance",
  "metrics": ["engagement_rate", "voice_fit_verdict", "approval_count"]
}
```

**Output schema:**
```json
{
  "trajectory_summary": "[1-paragraph synthesis of the cross-session patterns]",
  "pillar_performance": {"Pillar 1": {"avg_engagement": 0.15, "approval_rate": 0.7}, "...": "..."},
  "hook_performance": [...],
  "format_performance": [...],
  "recommendations": ["[actionable insight 1]", "[actionable insight 2]"]
}
```

**Why this operation exists:** the Scribe's 12-draft queue and the brain's `performance_log` contain the raw data. Cross-session analysis is what tells us which pillars/hhooks/formats are actually working. Mavis's Scribe cannot do this analysis in a single run (M2.7 context ceiling); Hermes can.

### Operation 4: Format-Rewrite

**Use case:** a piece of content needs to be re-cast into a different format (e.g., a long-form article → 5 X posts, or 3 X posts → 1 LinkedIn long-form).

**Input schema:**
```json
{
  "operation": "format-rewrite",
  "source_files": ["path/to/source.md"],
  "source_format": "long-form article (3000 words)",
  "target_format": "X thread (5-7 posts, 280 char ceiling)",
  "anchor_voice": "(none — Humanizer applies voice on return)"
}
```

**Output schema:**
```json
{
  "rewritten_content": "[verbatim rewritten text]",
  "post_count": 5,
  "character_counts": [267, 245, 271, 263, 280],
  "structural_notes": "[1-paragraph note on what was preserved vs. cut]"
}
```

**Why "anchor_voice" is empty by default:** Hermes does not have the persona. The co-processor returns structural output; the Humanizer applies persona voice on return. If `anchor_voice` is set, the caller is asking Hermes to mimic — that's higher risk and the Humanizer's Stage 1 (Fluff Purge) becomes the primary safety check.

## Outputs (the return path)

The co-processor returns the operation's output schema to the Mavis-side caller. The caller is **always the Humanizer** (the load-bearing safety gate). The Humanizer then:
1. Applies Stage 1 (Fluff Purge) to the result
2. Applies Stage 2 (Voice-Injection) if needed
3. Applies Stage 3 (Conflict Check) if the result is a post
4. Writes the humanized result to `drafts/humanized-[original].md` (or to the brain JSON if the result is ideas)

**The co-processor NEVER bypasses the Humanizer.** This is non-negotiable. Even if the operation type is "compress" and the output is a summary, the Humanizer runs on the summary before Mavis's Scribe consumes it.

## Procedure

### Step 1: Verify inputs

1. All source file paths exist (`ls -la <path>`)
2. The operation type is one of the 4 supported
3. The output schema is operation-appropriate
4. The total input size exceeds the auto-trigger threshold (or the caller has explicitly requested co-processor usage)

If any fail, HALT and surface to Andre.

### Step 2: Wrap the context

Build the `mavis communication send` payload. The payload structure:

```bash
mavis communication send \
  --from <caller-session-id> \
  --to <caller-session-id> \
  --command spawn \
  --content '{
    "agent": "<hermes-agent-name>",
    "model": "MiniMax-M2.7",
    "prompt": "<operation-type>-and-input-schema-as-text>",
    "input_files": ["<source-file-1>", "<source-file-2>", ...],
    "operation": "<one-of-4>",
    "output_schema": "<verbatim-output-schema>"
  }'
```

**Note on the agent name:** the Hermes agent's registered name must be discovered at runtime. The Mavis-side co-processor skill does not hardcode the Hermes agent's name (that would be a coupling). Use:

```bash
mavis agent list | grep -i hermes
```

to discover the registered name, then substitute. If no Hermes agent is registered, HALT and surface to Andre.

**Note on the prompt:** the prompt is a textual description of the operation + the input/output schema in natural language. Hermes's worker reads the prompt, follows the schema, reads the source files locally, applies compression/synthesis/etc., and returns the result via the same communication channel.

### Step 3: Ship and wait

The `mavis communication send --command spawn` returns a `sessionId` for the Hermes worker. Mavis's caller polls the Hermes session until completion (per `fleet-trust-patterns.md` §10: worker stall at same step 2x = take over).

**Polling cadence:** 30 seconds between checks, 5-minute total budget. If the Hermes worker hasn't returned in 5 minutes, abort and surface to Andre.

### Step 4: Receive the result

The Hermes worker returns the operation's output schema. Mavis's caller receives it via the communication channel.

**Critical: do NOT trust the result blindly.** The co-processor is a tool, not a governed agent. It can return off-voice, off-format, or off-persona content. The Humanizer is the only safety net.

### Step 5: Pipe to the Humanizer

The result is automatically piped to the Humanizer (via `99 _system/skills/scribe-humanizer/SKILL.md`). The Humanizer runs Stage 1, Stage 2, and Stage 3 on the result. The Humanizer's output is the final-form content that Mavis presents to Andre.

**If the Humanizer fails any stage on the co-processor result, the result is REJECTED. Mavis's Scribe is not allowed to use it.** The caller logs the rejection and surfaces to Andre.

### Step 6: Write the audit trail

Append a one-line entry to `~/.mavis/logs/hermes-co-processor.log`:

```markdown
- YYYY-MM-DD HH:MM CT — operation=<type> source=<count> files result=<passed|rejected> humanizer_stages=<3P/2P1F/etc>
```

This is a Mavis-side log, not a Hermes-side log. It stays in `~/.mavis/logs/` (Mavis's home) to respect the Mavis↔Hermes separation.

### Step 7: Return to the caller

The caller (Scribe, Researcher, or Andre-direct dispatch) receives the humanized result. The co-processor's job is done.

## The Mavis↔Hermes Separation (load-bearing — do not violate)

This skill is **Mavis-side only**. The strict rules:

1. **No writes to `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, `~/.hermes-evolution/`.** Mavis dispatches Hermes via the standard communication channel; Hermes writes to its own files. Mavis does not write.
2. **No reads of Hermes internals.** Mavis does not `cat ~/.hermes/` files, does not inspect Hermes's config, does not look at Hermes's session storage.
3. **No diagnosing of Hermes's runtime.** If the Hermes worker errors, surface the error to Andre. Do not investigate.
4. **No "while I was in there" fixes.** If Mavis notices something off about Hermes, the response is "I noticed X. Want me to dispatch a Hermes worker to fix it?" — NOT "I patched X."
5. **The co-processor is read-only-by-default for Hermes.** The Hermes worker is invoked, returns a result, and that's the end of Mavis's interaction. Mavis does not iterate on Hermes-side state.

**If Andre ever asks Mavis to do something that violates these rules, Mavis refuses and proposes a Mavis-side alternative.** The locked separation is a hard constraint, not a preference.

## The Safety Gate (the only thing keeping this skill safe)

The Humanizer is the only safety net between the co-processor and Andre. The co-processor returns structural output; the Humanizer applies persona governance, banned-phrase rules, and conflict-check criteria. If the Humanizer fails, the co-processor result is rejected.

**Track the rejection rate over time.** Every co-processor invocation that fails any Humanizer stage is a near-miss. If the rate exceeds 1 per 10 invocations, tighten the co-processor's input schema (more specific `preservation_priorities` for compress; more specific `synthesis_focus` for synthesize). If it exceeds 1 per 3, pause the co-processor and re-evaluate the integration.

**The Humanizer is the load-bearing immune system.** Without it, this skill is unsafe to use.

## Hard Rules

1. **Read-only on source files.** The co-processor never modifies the Scribe's drafts or the Researcher's briefs. Input is file paths, output is structural.
2. **No raw text in the channel payload.** All inputs are file paths + schema descriptions. Raw text through `mavis communication send` burns tokens AND loses file-path resolution.
3. **No bypass of the Humanizer.** Every co-processor result must pass through Stage 1, Stage 2, and Stage 3 before reaching Andre.
4. **Polling has a 5-minute budget.** If Hermes doesn't return in 5 minutes, abort and surface to Andre. Do not poll forever.
5. **Worker stall at same step 2x = take over.** If the Hermes worker stalls at the same step twice, Mavis does the synthesis itself (it may take longer but it respects the Mavis↔Hermes separation).
6. **No retries without Andre's sign-off.** If a co-processor invocation fails, surface to Andre. Do not auto-retry with adjusted params.
7. **No writes to Hermes's runtime, ever.** This is the locked Mavis↔Hermes separation. Even with Andre's explicit instruction. The co-processor invokes Hermes; it does not modify Hermes.
8. **Log every invocation to `~/.mavis/logs/hermes-co-processor.log`.** This is the audit trail. It stays in Mavis's home.

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Source file missing | `ls` returns 404 | HALT; surface to Andre |
| Source file exceeds 50,000 words | `wc -w` returns > 50K | HALT; the co-processor is for 8K-50K range; for >50K, Andre should split the input |
| Operation type not in {compress, synthesize, trajectory-analyze, format-rewrite} | schema validation | HALT; surface; the caller picked the wrong operation type |
| Output schema is empty | payload validation | HALT; surface; the operation type requires a specific output schema |
| Hermes agent not registered | `mavis agent list` returns 0 matches | HALT; surface; ask Andre to register the Hermes agent name |
| Hermes worker stalls at same step 2x | per `fleet-trust-patterns.md` §10 | Mavis does the synthesis itself; logs the takeover in the audit trail |
| Hermes worker returns empty result | payload validation | HALT; surface; this is a Hermes-side error, not Mavis's |
| Humanizer fails Stage 1 on the result | Stage 1 grep returns 1+ match | REJECT the result; surface to Andre; log the rejection |
| Humanizer fails Stage 2 on the result | Stage 2 pattern check returns 1+ match | REJECT the result; surface to Andre; log the rejection |
| Humanizer fails Stage 3 on the result | Stage 3 conflict check returns 0 of 5 criteria | REJECT the result; surface to Andre; log the rejection |
| Polling exceeds 5-minute budget | elapsed time > 5 min | ABORT; surface to Andre; the Hermes worker may be stuck |
| `mavis communication send` itself errors | CLI returns non-zero | HALT; surface; the communication channel itself is broken (operator-tier issue) |
| Co-processor invocation would write to `~/.hermes/`, `~/.openclaw/`, `~/.gbrain/`, or `~/.hermes-evolution/` | payload would contain a write target inside Hermes's tree | REFUSE; the separation is hard-locked; surface to Andre with the Mavis-side alternative |

## Verification

Before returning to the caller:
1. The co-processor invocation completed (or was aborted with a clean exit)
2. The result was piped to the Humanizer
3. The Humanizer's verdict is recorded (3P = all 3 pass, 2P1F = 2 pass + 1 fail, etc.)
4. The audit log entry was written
5. The caller has the humanized result
6. No writes to Hermes's runtime occurred
7. The polling budget was respected (no infinite loops)

## Cross-reference

- `03 Projects/Mavis EA Design/specs/hermes-authoring-evaluation.md` — the architectural recommendation that this skill implements
- `99 _system/skills/scribe-humanizer/SKILL.md` — the safety gate (always runs on co-processor output)
- The Scribe (`03 Projects/X-Content-Engine/agents/scribe.md`) — the primary caller for compress + format-rewrite operations
- The Researcher (`03 Projects/X-Content-Engine/agents/researcher.md`) — the primary caller for synthesize + trajectory-analyze operations
- The Mavis↔Hermes separation: `~/.mavis/agents/mavis/memory/MEMORY.md` §"ABSOLUTE SEPARATION" — the hard constraint
- `~/.mavis/logs/hermes-co-processor.log` — the audit trail (Mavis-side, not Hermes-side)
