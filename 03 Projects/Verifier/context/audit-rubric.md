# Audit Rubric

> The scoring framework. Every verdict applies the same rubric to a specific artifact.

## Criteria (weighted)

| Criterion | Weight | What is checked | Pass condition |
|-----------|--------|-----------------|----------------|
| **Source quality** | 0.25 | Are the sources for this artifact primary, secondary, or social? Are they fresh? Are they independent? | At least one primary source OR two independent secondary sources for any claim weight ≥ 0.6 |
| **Cross-source agreement** | 0.20 | Do independent sources converge on the same claim? If they diverge, is the contradiction explicitly surfaced? | Independent sources converge, OR contradictions are surfaced with both sides cited |
| **Stage discipline** | 0.20 | Is the raw → finding → claim → verified → task → approved chain preserved? Are stages collapsed into confident prose? | Chain is preserved; no collapsed stages |
| **Freshness** | 0.10 | Are the sources within the cadenced window for the lane? Is stale data flagged, not smuggled? | Sources are within the cadenced window; staleness is flagged if present |
| **Process compliance** | 0.15 | Does the agent's recent output follow the agent's own documented procedures (Researcher REFRESH steps, Mavis chain rules, Hermes routing rules)? | Recent outputs follow the agent's own AGENTS.md |
| **Handoff hygiene** | 0.10 | Does every claim promoted to a handoff lane have a source trail? Are queue files written, not abandoned? | Source trail on every promoted claim; queues consumed |

## Verdict bands

```
PASS                : weighted_score >= 0.80
NEEDS-WORK          : 0.60 <= weighted_score < 0.80
NEEDS-MORE-EVIDENCE : 0.40 <= weighted_score < 0.60
FAIL                : weighted_score < 0.40
```

## How to score

For each criterion, score 0.0–1.0:
- 1.0 = criterion fully met
- 0.5 = criterion partially met (specific gap)
- 0.0 = criterion not met (specific failure)

Weighted score = sum(criterion_score × criterion_weight).

## How to write a verdict

```yaml
- id: vrd-YYYY-MM-DD-NNN
  audit_target: "<artifact>"
  verdict: PASS|FAIL|NEEDS-WORK|NEEDS-MORE-EVIDENCE
  weighted_score: 0.0-1.0
  rubric_criteria:
    source_quality: 0.0-1.0
    cross_source_agreement: 0.0-1.0
    stage_discipline: 0.0-1.0
    freshness: 0.0-1.0
    process_compliance: 0.0-1.0
    handoff_hygiene: 0.0-1.0
  trail:
    - src-...
    - raw/.../snapshot.json
  issue: "<one sentence — name the artifact, name the gap>"
  recommended_action: <one of demote_weight | require_primary_source | split_claim | surface_contradiction | promote | freeze | drop | cite_dossier | add_source_link | back_link | split_connection | demote_confidence | drop | freeze_publish | re_route | require_verified_claim | add_source_trail_to_task | close_task | freeze_routing>
  snapshot_as_of: YYYY-MM-DDTHH:MM:SSZ
  issued_at: YYYY-MM-DD
  temperature: 0.0
```

## Failure modes of the rubric itself

- **Rubber-stamp** — every artifact scores ≥ 0.80. Caused by lazy scoring. Fix: random-sample a re-audit of recent verdicts and check for false PASS.
- **Gotcha** — every artifact scores < 0.40. Caused by mis-calibrated thresholds. Fix: re-anchor against a known-good baseline (e.g. Mavis's most-cited connection note).
- **Drift** — the rubric criteria no longer match the agents' actual procedures. Caused by the agents evolving faster than the rubric. Fix: pull `AGENTS.md` from each agent on every BOOTSTRAP and surface deltas.

## Versioning

The rubric is versioned in `config.yaml` (`audit_rubric.version`). When the rubric changes, write a migration note to `wiki/concepts/rubric-changelog.md` and re-run a calibration pass.
