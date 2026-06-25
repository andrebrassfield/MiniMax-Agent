---
type: publish-ledger
asset: pcac-series-publish-ledger
status: 🟡 STAGED (ready for Buffer push after Thu Jun 25 13:14 CT rate-limit clearance)
window: 2026-06-27 09:00 ET → 2026-07-07 09:00 ET (11 days, 11 threads)
owner: Mavis (publish) + Dre (final human review on the locked thread files only — already closed)
priority: HIGH — protects Dre's Clinic Protocols + terrain blocks through pre-hearings window
---

# PCAC Series — Publish Ledger

> **Source of truth for the June 27 → July 7 publish schedule.** Each row is a thread in the locked 12-file set (11 threads + 1 index). Status flips through: STAGED → QUEUED (Buffer) → POSTED → VERIFIED.
>
> **Single CTA:** every thread ends at `https://doseofproof.substack.com/` — never a Buffer/Vercel/Shopify URL.
>
> **Closed-loop tracking:** `x-analytics-tracker-daily` cron (7pm CT) + `pcac-series-verification-backstop` cron (8pm CT, T+4 per thread) + manual Buffer re-push post-rate-limit-clearance.

---

## Infrastructure wired

- ✅ **Publish ledger:** this file
- ✅ **Buffer CSV:** `03 Projects/Dose of Proof/assets/scheduling/buffer-bulk-upload-pcac-series-june27-july7.csv` (12 rows: 1 header + 11 threads, ~30KB, generated from the locked markdown files via `scripts/build-pcac-buffer-csv.py`)
- ✅ **CSV generator script:** `03 Projects/Dose of Proof/scripts/build-pcac-buffer-csv.py` (idempotent — re-run after any thread edit to regenerate CSV)
- ✅ **Analytics cron:** `x-analytics-tracker-daily` updated to write to BOTH `03 Projects/X-Content-Engine/memory/content_brain.json` AND `03 Projects/Dose of Proof/memory/dose-of-proof-performance-log.json` with hook-family biasing (+1/-1/0)
- ✅ **Verification backstop cron:** `pcac-series-verification-backstop` at 8pm CT daily, runs T+4 verification per thread, writes to `03 Projects/Dose of Proof/stores/live-execution/hook-family-bias-log.md`
- ⏸ **Buffer push:** awaiting Thu Jun 25 13:14 CT rate-limit clearance (Buffer rate limit resets then per Decision 29 retry cron)

---

## Status legend

# PCAC Series — Publish Ledger

> **Source of truth for the June 27 → July 7 publish schedule.** Each row is a thread in the locked 12-file set (11 threads + 1 index). Status flips through: STAGED → QUEUED (Buffer) → POSTED → VERIFIED.
>
> **Single CTA:** every thread ends at `https://doseofproof.substack.com/` — never a Buffer/Vercel/Shopify URL.
>
> **Closed-loop tracking:** see `x-analytics-tracker-daily` cron (7pm CT) + `pcac-series-verification-backstop` cron (T+4 days per thread).

---

## Status legend

- 🟡 **STAGED** — thread file FINAL, ready to queue
- 🟠 **QUEUED** — pushed to Buffer, scheduled, awaiting publish time
- 🟢 **POSTED** — live on X, awaiting first performance snapshot
- ✅ **VERIFIED** — T+4d performance review complete, hook-family bias logged
- 🔴 **FAILED** — push error or rate-limit hit; manual fallback triggered

---

## Series 1 — The 4 Traps (June 27–30, 9:00am ET)

| # | Status | Date / Time ET | Asset | Hook (first sentence verbatim) | Compliance gates | Folder |
|---|---|---|---|---|---|---|
| 1 | 🟡 | Sat Jun 27, 09:00 | `4-traps/trap-1-kitting.md` | "The first trap that turns a 'research only' label into a federal target is hiding in plain sight at checkout." | ✅ All 9 | 4-traps |
| 2 | 🟡 | Sun Jun 28, 09:00 | `4-traps/trap-2-seo.md` | "You can keep your public copy technically perfect and still get hit — because the FDA reads your backend." | ✅ All 9 | 4-traps |
| 3 | 🟡 | Mon Jun 29, 09:00 | `4-traps/trap-3-testimonials.md` | "One comment can turn your entire page into misbranded drug labeling under Section 505(a)." | ✅ All 9 | 4-traps |
| 4 | 🟡 | Tue Jun 30, 09:00 | `4-traps/trap-4-community.md` | "The fourth trap is the one most modern creators walk into with their eyes open." | ✅ All 9 | 4-traps |

## Series 2 — PCAC Peptide-by-Peptide (July 1–7, 9:00am ET)

| # | Status | Date / Time ET | Asset | Compound | Hook (first sentence verbatim) | Compliance gates | Folder |
|---|---|---|---|---|---|---|---|
| 5 | 🟡 | Wed Jul 1, 09:00 | `pcac-peptides/2026-07-01-bpc-157.md` | BPC-157 | "On July 23 the FDA's Pharmacy Compounding Advisory Committee evaluates BPC-157 — free base and acetate forms — specifically for the ulcerative colitis indication." | ✅ All 9 | pcac-peptides |
| 6 | 🟡 | Thu Jul 2, 09:00 | `pcac-peptides/2026-07-02-kpv.md` | KPV | "July 23 also covers KPV — a tripeptide (Lysine-Proline-Valine) — for wound healing and inflammatory conditions." | ✅ All 9 | pcac-peptides |
| 7 | 🟡 | Fri Jul 3, 09:00 | `pcac-peptides/2026-07-03-tb-500.md` | TB-500 | "TB-500 (Thymosin Beta-4, free base and acetate forms) is also on the July 23 PCAC docket — wound healing indication." | ✅ All 9 | pcac-peptides |
| 8 | 🟡 | Sat Jul 4, 09:00 | `pcac-peptides/2026-07-04-mots-c.md` (11 tweets) | MOTs-C | "The FDA docket does not pause for federal holidays." | ✅ All 9 | pcac-peptides |
| 9 | 🟡 | Sun Jul 5, 09:00 | `pcac-peptides/2026-07-05-semax.md` | Semax | "The July 24 PCAC docket opens with Semax — for cerebral ischemia indication." | ✅ All 9 | pcac-peptides |
| 10 | 🟡 | Mon Jul 6, 09:00 | `pcac-peptides/2026-07-06-dsip-epitalon.md` | DSIP + Epitalon | "The July 24 PCAC docket closes with two more compounds: Emideltide (DSIP) and Epitalon." | ✅ All 9 | pcac-peptides |
| 11 | 🟡 | Tue Jul 7, 09:00 | `pcac-peptides/2026-07-07-recap-bridge-biomarkers.md` | (Recap + bridge) | "The July 23-24 PCAC is the biggest regulatory catalyst in this space in years." | ✅ All 9 | pcac-peptides |

---

## Cross-handle note

Per `content-calendar-june27-july7.md`: X handle is **@doseofproof if secured**, else cross from @DreTheSalesGuy with "new project — Dose of Proof" framing for the first 72 hours only.

For initial publish (June 27 – June 30), handle is whichever is live. Confirm handle security before first publish.

## Conflict resolution

- **Jul 7 (existing week-1-2 CSV):** Old "FDA PCAC meeting is in 16 days" standalone single — replaced by the new recap thread (regulatory content > countdown teaser). Buffer re-push script handles the dedupe.

---

## Pre-publish checklist (must pass before QUEUED status)

For each thread:
- [ ] File exists at the asset path
- [ ] First sentence (hook) matches the value in this ledger verbatim
- [ ] Final tweet links to `https://doseofproof.substack.com/` (no other URL)
- [ ] Compliance verification section ✅ All 9 gates
- [ ] `---` separator between every tweet (Buffer thread requirement)
- [ ] No `[BRACKETED PLACEHOLDERS]` left in copy
- [ ] No `TBD` / `TODO` / `XXX` markers
- [ ] ≤ 280 chars per tweet (verify with character counter)

---

## Post-publish verification (T+4 days per thread)

The `pcac-series-verification-backstop` cron (created this pass) fires 4 days after each thread publishes. It runs `x-analytics-tracker` for that thread specifically, captures 5-field metrics (post_id / hook_used / views / likes / date), and writes to the **Dose of Proof performance_log** (separate from X-Content-Engine's content_brain.json).

Hook-family biasing:
- Hook pattern → engagement ratio
- +1 if hook family outperforms median (apply to next thread in series)
- −1 if underperforms (revise hook structure for next thread)
- Updates Researcher/Scribe specs implicitly via this ledger

---

## Operational protections

- **Dre's calendar:** Threads publish 9:00am ET (8:00am CT). No Dre action required — Buffer auto-publishes.
- **Dre's terrain:** No high-cognitive-load work scheduled. Each thread is compliance-vetted + locked.
- **No manual posting:** All 11 threads pushed via Buffer after Thu Jun 25 13:14 CT rate-limit clearance. LinkedIn activation retry cron fires Thu Jun 25 13:20 CT (Decision 29); the LinkedIn-specific rows in Buffer CSV ship from there.
- **Hold-items NOT in this schedule:** Lead magnet PDF (Item 5, held), Marek/Lifeforce affiliate links (Item 6, held).

---

*Last updated: 2026-06-24 21:58 CT*
*Status: 🟡 STAGED — infrastructure wired, awaiting Buffer rate-limit clearance Thu Jun 25 13:14 CT*
*Next state change: 🟠 QUEUED (after Buffer push at Thu Jun 25 ~13:30 CT, immediately following LinkedIn retry cron fire at 13:20 CT)*
*First publish: Sat Jun 27, 9:00am ET (Trap 1 — Algorithmic Cross-Selling & Kitting)*

---

## Cron wiring verification

| Cron | Schedule | Mode | Status |
|---|---|---|---|
| `x-analytics-tracker-daily` | 0 19 * * * America/Chicago | sessionId (existing) | ✅ Updated — now writes Dose of Proof perf log + hook-family biasing |
| `pcac-series-verification-backstop` | 0 20 * * * America/Chicago | new (independent) | ✅ Created — T+4 verification + bias log |

## Hook-family classification (applied to each post in perf log)

- `regulatory_authority` — opens with FDA/docket/legal language
- `trap_warning` — opens with 'trap' / 'warning' framing
- `cultural_moment` — opens with cultural context (GLP-1, longevity, athletic recovery)
- `data_first` — opens with biomarker / HRV / scan data
- `lived_pivot` — opens with personal story → pivot to regulatory

## Bias propagation

After each T+4 verification, the +1/-1/0 bias is appended to `hook-family-bias-log.md`. Next thread in series reads the bias log implicitly when its Researcher/Scribe specs run — no manual Dre action required.