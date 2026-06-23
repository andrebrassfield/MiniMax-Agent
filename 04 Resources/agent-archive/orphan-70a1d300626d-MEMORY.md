
### Timestamp discipline: write null first, fill on last write (2026-06-02)
Type: discipline

When writing run receipts, project logs, or any timestamped artifact during in-progress work, write `finished_at: null` at creation. Fill on the LAST actual write to disk, not when reasoning finishes or when the brief is composed. The integrity check is the gate, not the verifier.

The failure mode: I estimated finished_at at 22:03 in REFRESH-1's run receipt before the run was actually over; the real last write was 21:58. Caught it on the final integrity check. The fix is structural (template forces null initially + integrity check rejects any receipt where finished_at > any source file mtime), not discipline (do not backfill, do not silently correct — write a new receipt entry or decisions/ note explaining the correction).

WHY: This pattern recurs in any long-running artifact. Run receipts, build receipts, batch job logs, agentic task handoffs. The fix is always the same: null initially, integrity check as gate. The discipline version ("just be careful") always fails under wall pressure.

### Wiki articles must be linked from dossier headers (2026-06-02)
Type: pattern

A wiki article that is the canonical synthesis pointer for a topic must be linked from the header of every relevant dossier, otherwise it is an orphan. In REFRESH-1, `wiki/articles/2026-agentic-frontier.md` was the canonical cross-vendor synthesis spanning both `dossiers/ai_agents.md` and `dossiers/frontier_ai.md`, but neither dossier linked to it. Andre flagged it as an orphan.

Pattern: any synthesis article that crosses multiple dossiers belongs as a "Canonical synthesis pointer" line in the header of each relevant dossier. Update the article on deltas that span those dossiers. The integrity check should reject orphan wiki articles (no dossier header links to it).

WHY: Synthesis is the highest-value output of a research vault. If the synthesis is unreachable from the primary surface, the system rots even if the synthesis file exists.

### Verified claims need context_decay or they silently stale (2026-06-02)
Type: pattern

Add `context_decay_days` (days since `verified_at`) and `context_decay_recomputed_at` (ISO8601 timestamp of the last recomputation) to every verified claim. Recompute at the start of every REFRESH. Downgrade rule: if `context_decay_days > 90` without re-verification, set `verified: false` on next REFRESH and note the re-verification requirement. Re-verification means fresh primary-source fetches, not "no contradicting source was found."

WHY: Without this, `verified: true` becomes a one-shot flag that decays silently across REFRESH cycles. The dossier-delta discipline only stays honest if the timestamp of verification is part of the claim's weight, not a hidden assumption.

### Structure inspection after script-based file rewrites (2026-06-03)
Type: discipline

When using a script (Python via bash, sed/awk pipeline, etc.) to rewrite part of a structured file, the script usually only touches the targeted blocks — but the surrounding context (intro paragraphs, outro notes, cross-references that named the extracted content) often needs cleanup too. The discipline is: after any script-based rewrite, do a structure inspection of the affected section before declaring success. A targeted scan for the section headers, blank-line boundaries, and intro/outro text catches what the script missed.

The Artemis verification closeout (2026-06-03) hit this: Python script extracted 6 vrf-handoff YAML blocks from the Pending section cleanly, but left the 2 intro paragraphs ("5 re-audit verdicts..." and "Note: The 3 prior NEEDS-MORE-EVIDENCE verdicts...") behind. Caught on structure inspection (`for i, line in enumerate(lines, 1): if line.startswith("## "): print`), fixed with a single Edit to fold the stale text into a shorter historical-context line, re-validated. Mavis called this "textbook self-correction" — the discipline worked.

Pattern: any script-based file rewrite → run a `## ` / `### ` / section-header scan over the affected region → confirm the section is structurally clean (no orphaned intro/outro referencing the removed content) → re-validate line counts and key markers.

WHY: Scripts optimize for the targeted change, not for the surrounding context. The file's overall readability and downstream-consumability depend on the structure staying clean. Skipping the inspection step is the most common way a "successful" edit ships with stale scaffolding still in place. The fix is structural (always do the inspection, don't just rely on the script), not discipline ("be more thorough").

### Future-proofing test: dossier-quality spec obviates a separate Design vantage/agent (2026-06-04)
Type: pattern

Mavis dispatched an urgent deep-dive on the markdown-to-HTML fade-UI rendering pattern. I produced a 8-section dossier at dossiers/dev_tooling/markdown-to-html-ui.md with 50+ primary sources, 10 promoted claims, and a build-spec-shaped Implications section. Mavis consumption note: "The future-proofing test from the harness pattern we internalized tonight argued against adding a Designer agent — the dossier is the design spec, no separate Design vantage needed."

Reusable lesson: when a researcher dossier is dense enough, has a section called Implications structured as a build spec, and ends with a layer-cake table (lib + animation + layout + perf budget + delivery + render hints), it obviates a separate Design agent. The dossier IS the design. The handoff tells the chief of staff "this is ready for the Builder, do not add a Design vantage."

Pre-flight checks for "is this dossier Design-vantage-quality?":
1. Every required finding area has a section
2. Every section ends with a "Verdict for the use case" callout
3. The Implications section has a layer-cake table with the exact stack choices
4. The Source trail is primary-heavy (>60% primary)
5. Recommended pipeline is one paragraph, not a discussion
6. The handoff priority_alert ends with a 5-step suggested_action

If 4+ of 6 hold, the dossier is design-vantage-quality. Skip the Designer role. Hand to Builder.

WHY: the more agents in the pipeline, the more handoff drift. The Dossier-as-Design pattern eliminates a whole layer of context-loss. Applies to any future project where the researcher is asked to produce a spec, not a survey.
### JSONL append: ID-field syntax check before commit (2026-06-06)
Type: discipline

During the MiniMax sources ledger append, I introduced a typo in src-013's ID field (`src-2026-05-06-05-013` instead of `src-2026-06-05-013`) and caught it post-write. The fix was correct in substance but I framed it as "fixing a pre-existing record" when it was entirely my own data-entry error. The discipline fix: run a regex pass over all constructed IDs (`src-\d{4}-\d{2}-\d{2}-\d{3}`) before writing, or validate the full record list in-memory before the `json.dumps` loop commits to disk. Never report a self-introduced error as a "correction to existing data."

### JSONL schema hygiene: escape double-quotes in excerpt fields before dumps (2026-06-06)
Type: pattern

Line 47 of `sources.jsonl` (pre-existing, unrelated to this task) is JSON-invalid due to unescaped double-quotes in the `excerpt` field — not truncation. When excerpts contain analyst prose or quoted material, `json.dumps()` without `ensure_ascii=False` or with raw `"` characters in the string will produce invalid JSON. Fix: when constructing records programmatically, ensure the excerpt string is clean before `json.dumps()`. Alternatively, use a pre-write validator that runs `json.loads()` on every record before it touches the file. The failure mode is silent — the file looks intact but `json.decoder.JSONDecodeError` fires on any downstream parse. Applies to all JSONL ledgers (sources.jsonl, claims.jsonl, findings.jsonl).