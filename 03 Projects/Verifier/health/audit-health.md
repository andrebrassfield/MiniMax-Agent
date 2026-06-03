# Health — Audit Vault

> Structural integrity of the audit vault. Run on every AUDIT.

*Pending first AUDIT. Once AUDIT runs, this file will be rewritten with:*

## Vault structure
*Pass/fail — all required folders present, all ledgers non-empty.*

## Ledger integrity
*Pass/fail — every verdict in `verdicts.jsonl` has a non-empty trail.*

## Temperature check
*Pass/fail — `config.yaml` reports `audit: 0.0` and `adjudicate: 0.0`.*

## Per-agent cadence
*Days since last audit per agent. Flag if any agent is past 7 days.*

## Audit debt
*Count of NEEDS-MORE-EVIDENCE items. Flag if > 25.*

## Appeals SLA
*Count of appeals older than 48h. Flag if > 0.*

## Handoff-routed FAILs
*Count of FAIL verdicts not yet routed to handoff lanes. Flag if > 0.*

## Overall
*Pass / degraded / fail with one-line summary.*

---

**Discipline:** This file is rewritten on every AUDIT, not appended.
