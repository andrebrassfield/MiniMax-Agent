# Proposal Types — ea-skill-evolution

The 3 proposal shapes the skill generates. Each has a different
procedure, different staging area, and different review criteria.

## 1. New skill scaffold

For HIGH-durability candidates that look like a recurring workflow
with no current skill.

**Procedure:**
1. Pull the relevant brief evidence (file:line refs from the
   extract)
2. Pick a template structure from the existing skill library
   (e.g., `ea-loop-thinking` is the meta-skill template;
   `ea-data-quality-audit` is the diagnostic template;
   `ea-closed-loop-builder` is the operational template)
3. Draft the new `SKILL.md` with: YAML frontmatter (name,
   description with triggers), What this skill does, When to run
   (trigger phrases), Inputs, Procedure, Hard constraints,
   Anchoring sources
4. Stage the file at `~/.mavis/agents/mavis/skills/ea-skill-evolution/staging/<new-skill-name>/SKILL.md`. Do NOT write to the canonical path yet.
5. Add a manifest entry with `staging: ...` pointing to the staged file
6. Run the 5 audit gates
7. Surface the manifest entry to Mavis

**Manifest entry example:**
```jsonl
{"ts": "2026-06-16T22:00:00-05:00", "type": "new", "target": "ea-regulatory-gate", "intent": "Gate that halts skill evolution when a proposal touches a regulated domain", "evidence": ["01 Daily/2026-06-16.md L8"], "axes": {"what": "skill", "when": "on-evolution", "how": "scaffold-from-template", "where": "skills/ea-regulatory-gate"}, "staging": "ea-skill-evolution/staging/ea-regulatory-gate/SKILL.md", "audit": {"mistakes": "PASS", "loop": "PASS", "duplicate": "PASS", "regulatory": "PASS-NA", "brief_evidence": "PASS"}, "status": "pending-review"}
```

## 2. Skill mutation

For HIGH/MEDIUM-durability candidates that point at a gap in an
existing skill.

**Procedure:**
1. Read the current `SKILL.md` end-to-end
2. Identify the smallest change that closes the gap from the brief
   evidence. Per GEPA discipline: **one paragraph, one section,
   or one trigger phrase** at a time. Don't rewrite the whole skill.
3. Draft the diff as a unified-format patch against the current
   `SKILL.md`
4. Stage the diff at `~/.mavis/agents/mavis/skills/ea-skill-evolution/staging/<target-skill>/<date>-mutation.diff`
5. Add a manifest entry with the proposed change summary and the
   brief evidence it addresses
6. Run the 5 audit gates (only on the changed section)
7. Surface the manifest entry to Mavis

**Manifest entry example:**
```jsonl
{"ts": "2026-06-16T22:00:00-05:00", "type": "mutate", "target": "x-bookmark-parser", "intent": "Add H5 halt condition for sensitive content skip (DM screenshots, financial info)", "evidence": ["ea-skill-evolution/briefs/lesson-extract-2026-06-16.md L42"], "axes": {"what": "skill", "when": "on-incident", "how": "GEPA-style single-trigger edit", "where": "skills/x-bookmark-parser/SKILL.md"}, "staging": "ea-skill-evolution/staging/x-bookmark-parser/2026-06-16-mutation.diff", "audit": {"mistakes": "PASS", "loop": "PASS", "duplicate": "PASS", "regulatory": "PASS-NA", "brief_evidence": "PASS"}, "status": "pending-review"}
```

## 3. Memory candidate

For HIGH-durability "Type A recurring correction" patterns that
belong in `MEMORY.md` or a topic file.

**Procedure:**
1. Draft the proposed `mavis memory append` invocation: agent name,
   content, suggested slot (MEMORY.md or topic file)
2. Stage the proposed invocation as a markdown file at `~/.mavis/agents/mavis/skills/ea-skill-evolution/staging/memory/<date>-<slug>.md`. Do NOT execute the append.
3. Add a manifest entry with `status: memory-deferred`
4. Run the 5 audit gates
5. Surface the manifest entry to Mavis
6. Mavis reviews the proposed invocation
7. If Mavis approves, Mavis (not the skill) runs `mavis memory append`
8. Mavis updates the manifest entry with the decision + the actual
   memory entry path

**Manifest entry example:**
```jsonl
{"ts": "2026-06-16T22:00:00-05:00", "type": "memory", "target": "MEMORY.md", "intent": "Add hot-path rule: when Andre names a tool + 'hype translate,' auto-invoke x-hype-translator with the tool name as the required input", "evidence": ["01 Daily/2026-06-16.md L23"], "axes": {"what": "memory", "when": "on-3+-occurrences", "how": "append-to-MEMORY.md", "where": "MEMORY.md"}, "staging": "ea-skill-evolution/staging/memory/2026-06-16-hype-translate-autorun.md", "audit": {"mistakes": "PASS", "loop": "PASS", "duplicate": "PASS", "regulatory": "PASS-NA", "brief_evidence": "PASS"}, "status": "memory-deferred"}
```

## Why the skill doesn't execute the writes

Memory writes are Mavis's decision. Skill canonical writes are
Mavis's review. The skill is the proposer; the chief is the gate.
This is the load-bearing discipline that keeps self-evolution
from drifting. If the skill executed the writes autonomously:
- Memory entries could land in the wrong slot (MEMORY.md vs. topic
  file) without the right formatting
- Skills could land in the canonical path with bugs (no
  review-before-ship gate)
- The corpus would grow faster than Mavis can review

The skill stages, Mavis reviews, Mavis commits. The audit trail
is the manifest.
