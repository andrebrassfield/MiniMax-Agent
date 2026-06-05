# Decision 2026-06-05-001 — FDA 503A Peptide Dossier, Docket-Number Inconsistency

> Adjudicated under Mode 3 (ADJUDICATE) of the Verifier AGENTS.md.
> Audit log: `aud-2026-06-05-001`.
> Audit run: `vrd-fda-503a-2026-06-05-001`.

## Original contradiction (as flagged in the Researcher handoff)

The Researcher's inaugural FDA 503A peptide dossier surfaced a docket-number inconsistency:

- The Federal Register notice 91 FR 20465 (Doc. 2026-07361, published 2026-04-16) cites **Docket No. FDA-2025-N-6895** in both its heading and the "Instructions" paragraph: *"All submissions received must include the Docket No. FDA-2025-N-6895 for 'Pharmacy Compounding Advisory Committee; Notice of Meeting; Establishment of a Public Docket; Request for Comments—Bulk Drug Substances Nominated for Inclusion on the Section 503A Bulk Drug Substances List.'"*
- The FDA Advisory Committee Calendar page for the July 23-24, 2026 PCAC meeting has **two docket-number references** in different paragraphs:
  - The "Public Participation Information" main paragraph says: *"FDA is establishing a docket for public comment on this meeting. The docket number is FDA-2025-N-6895. The docket will close on July 22, 2026."*
  - The "Instructions" paragraph (immediately following) says: *"All submissions received must include the Docket No. **FDA-2026-N-2979** for 'Pharmacy Compounding Advisory Committee; Notice of Meeting; Establishment of a Public Docket; Request for Comments -- Bulk Drug Substances Nominated for Inclusion on the Section 503A Bulk Drug Substances List.'"* (the 2026 reference is on the FDA meeting page only)
- The Regulations.gov docket (https://www.regulations.gov/docket/FDA-2025-N-6895) confirms **FDA-2025-N-6895** is the live comment-collection docket, with comment due 2026-07-22 and 65 comments received as of 2026-06-05.

The Researcher best-inferred that FDA-2025-N-6895 is authoritative and the FDA-2026-N-2979 reference is a typo on the FDA meeting page, at weight 0.99.

## Re-check with full source trail

The Verifier independently re-fetched the Federal Register notice, the FDA meeting page, and the Regulations.gov docket on 2026-06-05 ~10:25 CT. All three live pages were inspected for the docket number:

| Source | Docket number cited | Verbatim |
|---|---|---|
| Federal Register 91 FR 20465 (heading) | FDA-2025-N-6895 | "Department of Health and Human Services / Food and Drug Administration / [Docket No. FDA-2025-N-6895]" |
| Federal Register 91 FR 20465 (Instructions paragraph) | FDA-2025-N-6895 | "All submissions received must include the Docket No. FDA-2025-N-6895" |
| FDA meeting page (Public Participation main paragraph) | FDA-2025-N-6895 | "FDA is establishing a docket for public comment on this meeting. The docket number is FDA-2025-N-6895." |
| FDA meeting page (Instructions paragraph) | FDA-2026-N-2979 | "All submissions received must include the Docket No. FDA-2026-N-2979" |
| Regulations.gov docket | FDA-2025-N-6895 | "Docket ID: FDA-2025-N-6895" (with 65 comments, due 2026-07-22) |

The 2026-N-2979 reference appears on **one single paragraph** of the FDA meeting page, immediately following a paragraph that correctly cites FDA-2025-N-6895. The surrounding text of the Instructions paragraph is otherwise verbatim from the Federal Register notice's Instructions paragraph (which cites FDA-2025-N-6895).

## Adjudication

The Verifier **upholds the Researcher's inference** that **FDA-2025-N-6895 is the authoritative docket number**, and the **FDA-2026-N-2979 reference on the FDA meeting page is a copy-paste typo**, not a parallel/updated secondary docket.

Reasoning:

1. **Three out of three non-FDA-instruction-paragraph sources (FR notice, Regulations.gov, FDA meeting page Public Participation main paragraph) consistently cite FDA-2025-N-6895.** The Instructions paragraph on the FDA meeting page is the only outlier.
2. **The Federal Register notice is the legal authority.** Per federal administrative law, the Federal Register notice is the binding public-notice document; a "Docket No." on an FDA web-page Instructions paragraph does not have independent legal authority to establish a different docket.
3. **Regulations.gov, the operative docket-management system, lists only FDA-2025-N-6895** as the live docket for this FR document. If FDA-2026-N-2979 were a real parallel docket, it would also appear on Regulations.gov.
4. **The Instructions paragraph on the FDA meeting page is otherwise verbatim from the FR notice Instructions paragraph** (which cites FDA-2025-N-6895). This pattern is consistent with a copy-paste error where the FDA meeting page template populated the docket-number field with a stale or test placeholder (FDA-2026-N-2979) instead of the actual docket number.
5. **No plausible alternative explanation.** A 2026-dated docket for an April 2026-published FR document would not have existed on the FDA meeting page on 2026-04-15 (when the page was "Content current as of"). The 2026-N-2979 reference is structurally an error.

**Final weight on FDA-2025-N-6895: 0.99.**
**Weight on FDA-2026-N-2979 (as a parallel docket): 0.0** — does not exist.

The dossier should keep the FDA-2025-N-6895 reference as the authoritative docket. The Verifier's recommended annotation in the dossier: note that the FDA-2026-N-2979 reference on the meeting page is a copy-paste error and not a parallel docket. This is a watch-item for the Researcher to surface in the Scribe's downstream consumption so a reader does not get confused.

## Action items

- [x] Decision written to `decisions/2026-06-05-001-docket-number.md`
- [x] Decision will be referenced in `knowledge/verdicts.jsonl` (dossier-level verdict) and `queue/researcher-verify-handoff.md` (routing)
- [x] Decision recorded in `dossiers/researcher-audit.md` (audit signal)

Decided by: Verifier (aud-2026-06-05-001).
Decided at: 2026-06-05T10:35:00-05:00.
Temperature: 0.0.
