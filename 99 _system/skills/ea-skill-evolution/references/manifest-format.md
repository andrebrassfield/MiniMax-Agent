# Manifest Format — ea-skill-evolution

The JSONL audit trail. Append-only. One line per proposed change.

## Schema

```jsonl
{"ts": "2026-06-16T21:30:00-05:00", "type": "new", "target": "ea-regulatory-gate", "intent": "Gate that halts skill evolution when a proposal touches a regulated domain", "evidence": ["01 Daily/2026-06-16.md L8", "research-brief-articles-1-and-2.md L217"], "axes": {"what": "skill", "when": "on-evolution", "how": "scaffold-from-template", "where": "skills/ea-regulatory-gate"}, "staging": "ea-skill-evolution/staging/ea-regulatory-gate/SKILL.md", "audit": {"mistakes": "PASS", "loop": "PASS", "duplicate": "PASS", "regulatory": "PASS-NA"}, "status": "pending-review"}
```

## Status values

| Status | Meaning | When set |
|---|---|---|
| `pending-review` | Staged, awaiting Mavis's decision | After stage + audit |
| `shipped` | Moved to canonical + mirror-verified via `cmp` exit 0 | After Mavis approves + mirror sync |
| `mirror-pending` | Canonical write succeeded but mirror write or `cmp` failed — held, surface to Mavis | When mirror step fails |
| `discarded` | Failed audit OR Mavis rejected | When audit fails or Mavis says no |
| `memory-deferred` | Memory candidate awaiting `mavis memory append` | When the proposal is a memory candidate |

The `mirror-pending` state is the gate-keeper — a proposal cannot
reach `shipped` without first passing the home == mirror byte-
identity check.

## Required fields

For `status: shipped`, the manifest entry MUST include:
- `mirror_status: ok`
- `mirror_verified: <ISO-timestamp>` (the time the `cmp` exit-0 was confirmed)
- `shipped_at: <ISO-timestamp>`

For `status: mirror-pending`:
- `mirror_status: pending`
- `mirror_error: <one-line reason>`
- Do NOT set `shipped_at`

## The full audit-gate report

The `audit` field in the manifest records the result of each gate:

```json
"audit": {
  "mistakes": "PASS" | "FAIL: <which-mistake>",
  "loop": "PASS" | "FAIL: <which-stage-broken>",
  "duplicate": "PASS" | "FAIL: <duplicates-with>",
  "regulatory": "PASS-NA" | "PASS" | "FAIL: <regulated-domain>",
  "brief_evidence": "PASS" | "FAIL: <missing-file-line-ref>"
}
```

`regulatory: PASS-NA` means the proposal doesn't touch a regulated
domain (the gate doesn't apply). `regulatory: PASS` means the
proposal touches a regulated domain but the gate passed (human-in-
the-loop confirmed, BAA in place, etc.). `regulatory: FAIL` means
the proposal hits a regulated domain without proper gating — the
skill halts, not just flags.

## The 4 fields of the audit trail

For every proposed change, the manifest should answer:
1. **What** is the change? (the surface + the type)
2. **Why** is the change proposed? (the brief evidence + the gap it closes)
3. **How** was the proposal generated? (the algorithm — GEPA-style, scaffold, merge)
4. **Where** is the canonical home? (the file path)

These map to the 4-axis classification. The manifest is the
audit trail; the brief evidence is the file:line reference.
