---
description: "The 7-step procedure x-niche-scraper runs — encode query, navigate, apply engagement floor, capture top N, write markdown, append ledger, report. Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22 as part of Upgrade 1 aggressive refactor."
---

# x-niche-scraper — The 7-step Procedure

1. **Encode query** per `[[02 Notes/patterns/x-niche-scraper-url-encoding]]`. Special chars percent-encoded, spaces to `+`, phrases wrapped in `%22`.
2. **Navigate** to `https://x.com/search?q=<encoded>&f=<tab>` via the real Chrome session (`mavis browser tool`).
3. **Apply engagement floor.** Skip posts below the configured floor (default 1,000 views). Posts below are skipped silently — do not narrate skips.
4. **Capture top N posts** (default 10) using the per-post schema inherited from `x-bookmark-parser`.
5. **Write the markdown capture** to `00 Inbox/x-niche-<query-slug>-YYYY-MM-DD-HHMM.md` per `[[02 Notes/patterns/x-niche-scraper-output-format]]`. Use CT timezone.
6. **Append one line** to `00 Inbox/_x-niche-ledger.mdl` (the Researcher's append-only index): `- YYYY-MM-DD HH:MM CT — <query-slug> (N posts, <tab> tab, floor <N>K)`.
7. **Report** to caller: file path, post count, dominant format/theme, search tab used, engagement floor applied.

If X returns "This request looks like it might be automated" or a similar bot-detection warning at any step, halt per `tests/niche-halts.md#H7` (skill-local) — the operator needs to slow down or log in more explicitly.
