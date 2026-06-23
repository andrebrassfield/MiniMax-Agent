---
date: 2026-06-22
type: closed-loop-spec
status: awaiting-approval-then-immediate
scope: vault-health
related:
  - ~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md
  - ~/.mavis/agents/mavis/crons/sepo-runner-weekly.md (similar pattern)
  - ~/MiniMax-Agent/INDEX.md
---

# Spec: Vault Health Cron

Monthly audit of the vault — finds orphan notes (no incoming links), stalled projects (no updates in 60+ days), inconsistent tags, missing frontmatter, broken wikilinks. Produces a maintenance checklist. Closes the "vault gets stale silently" failure mode.

## Goal (done condition)

1. New cron `vault-health` at `~/.mavis/agents/mavis/crons/vault-health.md` — first Sunday of month at 23:00 CT
2. Audit checks: orphan notes, stalled projects, stale tags, missing frontmatter, broken wikilinks, oversized files (>50KB), duplicate filenames
3. Output written to `00 Inbox/vault-health-YYYY-MM-DD.md` (mirrored to `99 _system/health/vault-health-YYYY-MM-DD.md`)
4. Telegram surface if any category has ≥5 issues
5. Vault mirror at `99 _system/crons/vault-health.md`
6. MAVIS.md + MEMORY.md updates
7. Manual test: run the audit procedure against the current vault, verify output

## Context

Vaults rot silently. Notes accumulate without incoming links. Projects stall. Tags drift. The article's "Vault Health Check" workflow: monthly Claude audit of orphan notes, outdated info, stalled projects, inconsistent tags, missing frontmatter. This cron delivers that automated.

## Action (atomic steps)

1. Write this spec (this file)
2. Build the cron prompt (self-contained procedure with shell commands)
3. Mirror cron to vault
4. Update MAVIS.md Active Skill Mutations
5. Update MEMORY.md (pointer)
6. Manual test against current vault

## Feedback

- Per-month audit log at `~/.mavis/state/vault-health-history.jsonl` (append-only, one record per month)
- Output file in `00 Inbox/vault-health-YYYY-MM-DD.md` is the human-readable report
- Telegram surface (silent skip if all categories < 5 issues)
- End-of-quarter gate: trend analysis (issues-per-category over last 3 months) → surface in weekly deep session if any category trending up

## Stop condition

Monthly open-loop. Halt conditions:
- Vault unreadable → HALT, surface
- Audit exceeds 5 minutes runtime → partial report, flag incomplete
- Output file > 1MB → truncate to top 100 issues per category, flag

## Reversibility

`<5 min: mavis cron delete mavis vault-health + mavis-trash state file + revert docs`
