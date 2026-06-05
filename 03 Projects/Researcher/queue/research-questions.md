# Research Question Backlog

> Mavis and Andre drop questions here. Researcher processes on the next REFRESH (or immediately if flagged urgent).

## Pending

### 2026-06-02 — Vellum (vellum.ai): pricing, value, fit — Mavis (for Andre)

Andre is considering Vellum — the LLM development platform (prompt workspace, eval tooling, dataset management, observability, workflow routing). Need a clean dossier: is it free, what does it cost, what does it actually do, and is it worth the spend for our fleet given what we already run.

**Required findings:**

1. **Pricing tiers — current as of June 2026.**
   - Free tier: exists? limits (seats, traces/month, prompts, evals)?
   - Paid tiers: per-seat pricing, usage-based, enterprise custom?
   - Any startup credits / free trial / OSS exception?
   - Source: vellum.ai/pricing, any current rate card or blog post.

2. **Feature inventory — what it actually does.**
   - Prompt management / versioning / workspace
   - Evaluation: human-in-the-loop, LLM-as-judge, batch runs, regression detection
   - Dataset management and test set curation
   - Observability / tracing / monitoring
   - Workflow / routing / deployment
   - Integrations (OpenAI, Anthropic, Bedrock, Vertex, custom)
   - Anything new in the last 6 months that changes the picture

3. **Worth the cost? — comparison vs alternatives we could use instead.**
   - LangSmith (LangChain)
   - Helicone (open-source-friendly)
   - Portkey
   - Arize Phoenix / Arize AX
   - Braintrust
   - Confident AI (DeepEval)
   - Maxim AI
   - **Roll-our-own** on top of what we already have (Hermes + gbrain + kanban + OpenTelemetry)

4. **Fit with our fleet — does Vellum duplicate or extend what Hermes/GBrain already do?**
   - gbrain is already a knowledge + FTS + embeddings layer with source provenance
   - Hermes kanban already has evaluation/scoring via the agent-disease-detector and skill-evolution skills
   - We have custom observability via the agent-disease-detector and verifier agents
   - Where does Vellum create new capability vs create a silo we have to sync?

5. **G2 / Reddit / HN / actual-team sentiment.**
   - Where does Vellum shine? Where does it fall over?
   - Common complaints (cost, lock-in, eval reliability, support)?
   - Any team that migrated off Vellum and why?

**Output format:** standard Researcher dossier. `dossiers/dev_tooling/vellum.md` (or similar — check existing dossier taxonomy first). Include:
- Pricing table with sources
- Feature matrix vs the 7 alternatives above
- Verdict on fit (recommend / don't recommend / recommend with caveats)
- If recommend with caveats: what would we have to change in our stack to use it well
- Raw sources in `sources/` and findings in `knowledge/findings.jsonl`

**Urgency:** Not urgent. Process on next REFRESH. Andre is in design-review mode, not blocking on a decision tonight.

**Mavis follow-ups if useful:** None queued. If you find evidence Vellum is the answer, also surface the integration cost with our MiniMax + OpenAI-compatible proxy layer. If it's not the answer, say so cleanly and propose what is.

### 2026-06-02 — Wire up last30days as a REFRESH collector lane — Mavis

Andre wants the `/last30days` skill (mvanhorn, MIT, v3.3.1, 26K+ stars) installed and paired with you, since you are the fleet's research operator and the skill is a multi-source recency aggregator. Mavis is chief of staff and should not be running research collectors.

**What's already done (Mavis side):**
- Engine installed at `~/.agents/skills/last30days/` (v3.3.1, ~250KB)
- Symlinked into `~/.claude/skills/`, `~/.codex/skills/`, `~/.hermes/skills/` etc. (universal installer)
- Config dir at `~/.config/last30days/.env` (600 perms, empty)
- Mavis wrapper at `~/.mavis/skills/last30days/` was removed (wrong placement)

**What's needed (Researcher side):**
1. **Source plan integration.** Add last30days to `context/source-plan.md` as a high-recall multi-source lane. Note: it covers 14+ sources in one call (Reddit, X, YouTube, TikTok, Instagram, HN, Polymarket, GitHub, Bluesky, TruthSocial, Digg, Web, Threads, Pinterest, xquik, Perplexity). Treat as a single lane with configurable subsets, not 14 separate lanes.
2. **AGENTS.md mention.** Add a step to the REFRESH section (around step 5 "Collect from each enabled source lane") saying "Optionally invoke last30days for broad recency probes on dossier topics. Pass `--store` to persist to `~/.config/last30days/last-run.json` and `store.py` SQLite."
3. **Wrapper script.** Add `scripts/last30days_collect.py` (or similar) that wraps the engine and returns structured output suitable for your stage discipline. It should: accept a topic, invoke `python3 ~/.agents/skills/last30days/scripts/last30days.py --emit compact --store "<TOPIC>"`, then parse the engine's `last-run.json` and write findings to `raw/last30days/<timestamp>.json` + append sources to `knowledge/sources.jsonl`.
4. **Quality floor note.** The skill's output is engagement-weighted social signal, not primary sources. Treat it as a discovery / recency probe, not a verification path. The verification step still belongs to you (or Verifier). Add a note that any claim sourced solely from last30days social lanes (X, TikTok, IG, Bluesky, Threads) needs Verifier cross-check before it gets dossier weight.
5. **API keys (optional, non-blocking).** If you can drop a `SCRAPECREATORS_API_KEY` into `~/.config/last30days/.env`, that unlocks X, TikTok, Instagram, Bluesky, Digg. Without it, the engine still works on Reddit + HN + GitHub + Polymarket + YouTube + OpenRouter reasoning. Andre has not provided keys; don't block on this.
6. **Dossier impact.** When you run last30days on a dossier topic, append the engine's evidence cluster to the dossier's source trail and surface any contradictions in `queue/verification-review.md`.

**Engine CLI you have access to:**
```bash
python3 ~/.agents/skills/last30days/scripts/last30days.py --emit compact --store "<TOPIC>"
python3 ~/.agents/skills/last30days/scripts/last30days.py --emit compact --search reddit,hackernews "<TOPIC>"   # subset
python3 ~/.agents/skills/last30days/scripts/last30days.py --diagnose   # provider status
python3 ~/.agents/skills/last30days/scripts/last30days.py --help
```

**Source for provenance:** https://github.com/mvanhorn/last30days-skill (mvanhorn, also author of Compound Engineering, Printing Press, Agent Cookie — same author Andre is already a fan of per the June 2026 article).

**Urgency:** Not urgent. Process on next REFRESH or whenever you next rebuild your source plan.

**Status: partial-wired 2026-06-02 22:19 CT, finalized 2026-06-02 22:25 CT.** Items 1 (source plan) and 2 (AGENTS.md mention) completed. Item 3 (wrapper script) deferred to REFRESH-2 per Andre's sequencing (script first, then cron, then memory_orchestration on REFRESH-3). Item 4 (quality floor note) is captured in the new source-plan lane description (per-source-type tagging in the wrapper is the implementation, the discipline itself is documented). Items 5 and 6 are operational and will execute when the wrapper runs. Acknowledged via `mavis communication send` to Mavis session `mvs_d4e34657b3ec41289d639e3d42d1bc79`; Mavis's reply confirmed the OpenRouter-vs-social split and added the two-sub-tag discipline (`last30days/reasoning-primary` vs `last30days/social-weighted`), which is now encoded in the source-plan lane. Spec closed from Mavis's side.

## Processed

### 2026-06-03 — Consume Verifier calibration handoff vrf-handoff-2026-06-03-001 — Mavis

Verifier ran its first calibration AUDIT on `dossiers/ai_agents.md` and issued PASS at 0.8025. Real finding: stage discipline gap. Three high-weight claims (clm-2026-06-02-004 weight 0.75, clm-2026-06-02-005 weight 0.7, clm-2026-06-02-006 weight 0.7) sat at `verified: false` in the claims ledger while the dossier prose presented them as established fact. Verifier pre-staged the primary sources and wrote a handoff to my queue.

**Consumed actions (2026-06-03 09:50 CT):**

1. **Read the verdict:** `03 Projects/Verifier/queue/researcher-verify-handoff.md#vrf-handoff-2026-06-03-001` — full trail and rubric breakdown reviewed.
2. **Promoted three claims** in `knowledge/claims.jsonl`:
   - `clm-2026-06-02-004` → `verified: true` (3 primary sources: src-2026-06-02-003, src-2026-06-02-006, src-2026-06-02-015)
   - `clm-2026-06-02-005` → `verified: true` (2 primary arXiv sources: src-2026-06-02-017, src-2026-06-02-018)
   - `clm-2026-06-02-006` → `verified: true` (1 primary source: src-2026-06-02-018; single-source at rubric boundary — re-verification watch added in dossier)
3. **Updated dossier prose** in `dossiers/ai_agents.md` — the dossier convention uses plain claim ID citations (no inline marker), so the prose was already accurate after promotion. The clm-2026-06-02-006 citation got an inline `single-source at rubric boundary` annotation, and a new "Re-verification watch" entry was added to the "Contradictions and open questions" section.
4. **Cross-dossier leak fixed** in `dossiers/ai_agents.md` Implications line 60 (was 59): bare `clm-2026-06-02-001 (GPT-5.5 frontier)` citation replaced with `[clm-2026-06-02-001 (GPT-5.5 frontier)](../dossiers/frontier_ai.md)` link to the frontier_ai dossier.
5. **Handoff moved** in `03 Projects/Verifier/queue/researcher-verify-handoff.md` from "## Pending (Researcher to consume)" to "## Recently Consumed (last 5)" with a status footer.
6. **This research question** moved to `## Processed` here (per spawn instruction, overriding the file's own "move to decisions/" convention — flagged to Mavis in report-back).

**Side-finding flagged to Mavis (fixed in this handoff, per Mavis adjudication at 2026-06-03 09:58 CT):** Implications line 61 in `dossiers/ai_agents.md` originally said "No claim has crossed the `weight ≥ 0.7` AND `verified: true` bar for content framing yet." That statement went stale the moment this handoff promoted the three claims. Mavis's decision: fold the implication rewrite into this handoff rather than queue it for the next REFRESH, because splitting the fix across two cycles creates a 6h+ audit gap where the ledger says "verified" but the dossier still says "no verified claim." The implication now names the 5 claims that cross the bar: clm-2026-06-02-002 (0.8) and clm-2026-06-02-003 (0.85) verified 2026-06-02, plus clm-2026-06-02-004 (0.75), clm-2026-06-02-005 (0.7), and clm-2026-06-02-006 (0.7, single-source caveat) promoted by this handoff. Strongest single-claim framing candidate named explicitly: clm-2026-06-02-003. Also: this research question has been mirrored to `decisions/research-questions-resolved.md` per the file convention (## Processed lookback retained for in-flight scanability).

**Status: consumed in vrf-handoff-2026-06-03-001 on 2026-06-03 | dossier prose updated Y | cross-dossier leak fixed Y | handoff moved Y | side-finding flagged: Implications line 61 stale (REFRESH trigger).**

---

**Convention:**
- Use `### YYYY-MM-DD — <one-line question> — <asker>` headers.
- Below the header, link to the dossier or source if relevant.
- Mark `URGENT:` prefix if the question needs a sub-1h response.
- Researcher adds a status footer: `Status: answered in <file> on <date> | escalated to <lane> | awaiting source`.

The Researcher does not just answer — it adds the question, the source trail, and the resolved location to the dossier or claim record. Backlog is not a chat log; it is a traceable log.

---

**Standing question to flag for Mavis** (do not process unless Mavis drops it):

> gbrain / Honcho / OpenClaw ↔ Letta / Mem0 / Zep / Cognee — where does Andre's stack actually sit, and is there a synthesis worth writing?

This is the highest-leverage follow-up suggested by the first REFRESH. Mavis has not asked. I will not self-answer.

### 2026-06-04 — Serving HTML for the human "fading UI" layer from flat markdown — Mavis (for Andre) — CONSUMED

URGENT-flavored, dispatch immediately. Andre asked for a deep-dive on the rendering pattern that turns Mavis's flat-markdown outputs (dossiers, daily briefs, chief-of-staff summaries, fleet-status state) into a beautiful, fade-animated HTML surface for human consumption — one that makes Andre (and me) faster and more efficient when reading my work.

[Original required-findings list elided for brevity; see queue/research-questions.md git history 2026-06-04 if needed.]

**Consumed actions (2026-06-04 01:50 CT):**

1. **Dossier written**: `dossiers/dev_tooling/markdown-to-html-ui.md` — 8 sections, 50+ unique primary sources across the 8 required findings areas, 10 promoted claims (8 verified researcher @ weight 0.85-0.95, 1 verified @ 0.8, 1 single-source @ 0.55 with explicit re-verification watch), 68 findings extracted.
2. **Sources ledger** updated: 31 new primary sources added to `knowledge/sources.jsonl` covering marked, markdown-it, pandoc, GFM spec, CommonMark, Quartz 5, Material for MkDocs, Eleventy, Astro Content Collections, MDN scroll-driven animations, MDN IntersectionObserver, MDN @starting-style, MDN View Transitions, MDN Web Animations API, Chrome DevRel (4 blogs), Gwern.net design, Tufte CSS, HTTP Archive Web Almanac 2025, web.dev Vitals, web-platform-dx, W3C Scroll Animations spec, Anthropic Artifacts blog, Perplexity Pages blog, Mavis skill catalog (content-deck-generator, html-presentation-generator, landing-page-builder, visual-summary reference), and CanIUse.
3. **Findings ledger** updated: 68 new findings extracted in `knowledge/findings.jsonl`.
4. **Claims ledger** updated: 10 new claims promoted in `knowledge/claims.jsonl` (clm-2026-06-04-001 through clm-2026-06-04-010).
5. **Handoff staged**: `queue/mavis-handoff.md` updated with priority_alert (mvs-handoff-2026-06-04-001) including dossier path, top-3 findings, recommended rendering pipeline, and contradictions worth Mavis's attention.
6. **Run receipt written**: `runs/RUN-20260604-0102-DIVE-MAVIS-UI.md` — full audit trail of sources collected, findings extracted, claims promoted, dossier written, handoff staged.
7. **This research question moved** from `## Pending` to `## Processed` here (consumed in this cycle, per the file convention).

**Top 3 findings (per spawn instruction's "What success looks like" + handoff convention):**

1. **Markdown lib = markdown-it** (Node) + 3 plugins: `markdown-it-anchor` (auto-generated heading IDs for jump-links), `markdown-it-container` (Pandoc-style fenced divs for render hints like `::: callout` / `::: fade-in-stagger` / `::: collapse` / `::: source-trail`), `markdown-it-footnote`. 100% CommonMark + GFM, mature since 2014, used by Vue/VitePress/Astro as default. Trust 0.95. Pandoc is the fallback for non-markdown inputs (docx, rst).

2. **Animation = hybrid layer-cake**: pure-CSS `@keyframes fade-in` + `animation-delay` for first paint (zero JS, every browser since 2014); vanilla JS IntersectionObserver for scroll-into-view fade (~30 lines, Baseline since March 2019, one observer per page, threshold 0.1, adds CSS class to target); CSS scroll-driven animations (`animation-timeline: view()`) as Chrome 115+ progressive enhancement via `@supports`. NOT in v1: View Transitions (defer to v2), @starting-style (defer until Safari/Firefox catch up). Animation MUST use opacity + transform: translateY() to avoid CLS.

3. **Layout = Tufte-inspired, system font stack, < 100KB total weight**: cap heading depth at H3 (per Tufte's Feynman-lectures principle), sidenotes sparingly, off-white #fffff8 + off-black #111111, text-wrap: pretty on body paragraphs, text-wrap: balance on headings. Zero webfonts in v1 (system font stack). Self-contained single HTML file (Pandoc --embed-resources pattern), no external requests, all content in initial raw HTML (HTTP Archive 2025 confirms this is also a content accessibility win for AI crawlers).

**Recommended rendering pipeline (summary for v1 build):**

`markdown file → markdown-it (server-side) → + markdown-it-anchor + markdown-it-container + manual CSS template → inlined <style> in <head> → vanilla JS IntersectionObserver block (~30 lines, inlined before </body>) → single self-contained HTML file written to vault`

Build at `99 _system/scripts/render-dossier.js` as a 200-line Node script. Run on file-watch or manual trigger. The Builder agent owns the script; Researcher owns the spec (this dossier).

**Status: consumed 2026-06-04 01:50 CT | dossier written Y | handoff staged Y | run receipt written Y | claims promoted 10 | sources captured 31 | findings extracted 68 | re-verification watch: clm-2026-06-04-009 (Thariq 'MD is dead' thread) is single-source at weight 0.55; will need a second primary source corroboration on next REFRESH.**

