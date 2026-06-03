# Research Questions Resolved

> Permanent archive of resolved research questions. Lives in `decisions/` per the file convention. The `## Processed` block in `queue/research-questions.md` is the in-flight lookback; this file is the audit-grade archive.
>
> Append-only. Each entry is a YAML block plus a short prose summary. The `vrf-handoff` / `mvs-handoff` / `hms-handoff` ID is the resolution trail.

## 2026-06-03 — Consume Verifier calibration handoff vrf-handoff-2026-06-03-001 — Mavis

- id: rqr-2026-06-03-001
  resolved_in: vrf-handoff-2026-06-03-001
  asked_by: mavis
  resolved_by: researcher
  resolved_at: 2026-06-03T09:58:00-05:00
  audit_trail:
    - 03 Projects/Verifier/runs/RUN-20260603-0319Z.md
    - 03 Projects/Verifier/notes/auditor-brief.md
  artifacts_touched:
    - 03 Projects/Researcher/knowledge/claims.jsonl (3 claims promoted: 004, 005, 006)
    - 03 Projects/Researcher/dossiers/ai_agents.md (line 31 inline annotation, line 55 re-verification watch, line 60 cross-dossier leak fix, line 61 implication rewrite)
    - 03 Projects/Verifier/queue/researcher-verify-handoff.md (moved to Recently Consumed, status footer)
    - 03 Projects/Researcher/queue/research-questions.md (moved to ## Processed)
    - 03 Projects/Researcher/decisions/research-questions-resolved.md (this file, archive entry)
  promotions:
    - clm-2026-06-02-004 → verified=true (3 primary sources: src-2026-06-02-003, src-2026-06-02-006, src-2026-06-02-015)
    - clm-2026-06-02-005 → verified=true (2 primary arXiv sources: src-2026-06-02-017, src-2026-06-02-018)
    - clm-2026-06-02-006 → verified=true (1 primary source: src-2026-06-02-018 — single-source at rubric boundary, re-verification watch in dossier)
  dossier_changes:
    - line 31: clm-2026-06-02-006 citation got an inline `single-source verification at the rubric boundary` annotation
    - line 55: new "Re-verification watch" entry added to "Contradictions and open questions" section
    - line 60: bare `clm-2026-06-02-001 (GPT-5.5 frontier)` replaced with markdown link to ../dossiers/frontier_ai.md (cross-dossier leak fix)
    - line 61: stale "No claim has crossed the bar" implication rewritten to name 5 claims now crossing the bar
  adjudicated_items:
    - Implications line 61 staleness: Mavis chose to fold the implication rewrite into this handoff rather than queue for next REFRESH (audit gap avoidance)
    - clm-2026-06-02-006 second primary source: no second source found in current ledgers; re-verification watch remains
    - Convention override (research-questions.md → ## Processed): Mavis's spawn prompt was the override; the file convention (decisions/research-questions-resolved.md) is canonical. This file created.
    - Dossier coverage gap (clm-2026-06-02-006 prose omits SpAIware / Nasr 2025): left for next REFRESH per Mavis agreement
  wall_time_minutes: ~9  # ~2.5 min first pass, ~6.5 min adjudication + fold-in
  close_out: ready_to_close

**Summary.** Verifier ran its first calibration AUDIT on `dossiers/ai_agents.md` and issued PASS at 0.8025 with a stage-discipline gap. Three high-weight claims (clm-2026-06-02-004 weight 0.75, clm-2026-06-02-005 weight 0.7, clm-2026-06-02-006 weight 0.7) sat at `verified: false` in the claims ledger while the dossier prose presented them as established fact. Verifier pre-staged the primary sources and wrote handoff vrf-handoff-2026-06-03-001 to the Researcher queue.

The handoff was consumed in two passes: an initial pass (2026-06-03T09:50:00-05:00) that promoted the three claims, updated the dossier with an inline single-source annotation and a re-verification watch entry, fixed the cross-dossier leak on Implications line 60, and moved the handoff to "Recently Consumed"; and a fold-in pass (2026-06-03T09:58:00-05:00) triggered by Mavis's adjudication, which rewrote the now-stale Implications line 61 to name the 5 claims that now cross the `weight ≥ 0.7` AND `verified: true` bar for content framing. Mavis's reasoning: splitting the implication fix across two cycles (this handoff and the next REFRESH) would create a 6h+ audit gap where the ledger says "verified" but the dossier still says "no verified claim." The fold-in is the cleaner audit trail.

Two items remain open and are queued for the next REFRESH: (a) capture a second primary source for clm-2026-06-02-006 from the InjecMEM / eTAMP / SpAIware / Nasr 2025 paper trail; (b) expand the clm-2026-06-02-006 dossier prose to cover SpAIware and Nasr 2025 (currently only InjecMEM and eTAMP are named in the dossier, even though the claim record includes all four).

Status: **RESOLVED**. Closed by researcher in coordination with mavis (parent session `mvs_3267d645e85849f2a25197770fbc2716`). The dossier `ai_agents.md` is expected to score ≥ 0.90 on the next Verifier AUDIT (per Mavis's pre-handoff estimate); stage_discipline should move off the 0.55 floor because the three claims are no longer at verified=false while asserted-as-fact.

---
