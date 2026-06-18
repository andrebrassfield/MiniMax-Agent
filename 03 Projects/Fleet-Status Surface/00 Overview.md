---
type: project
created: 2026-06-04
updated: 2026-06-04
status: research-phase
tags: [project, mavis, orchestrator, rendering, html, markdown, fade-ui, m3]
---

# Fleet-Status Surface

> Mavis's literal "desk." A live, fade-animated HTML surface in the vault that surfaces fleet state, EA priorities, and Mavis's own open work — so Andre (and Mavis) can read Mavis's operation in 2 seconds, not 5 minutes. The same rendering pipeline is the foundation for every HTML delivery Mavis produces (dossiers, daily briefs, weekly-connections syntheses, fleet status).

## The thesis

The current delivery model is: Mavis writes markdown into the Obsidian vault → Andre opens Obsidian to read. That's a good authoring surface but a slow consumption surface. The vault is where the work *lives*. The HTML surface is how the work *lands*. The dossier loop, the fleet-status pattern, the daily brief, the EA synthesis all need a rendering layer that feels alive (fade-in as you scroll, content arrives, no preloader, no jank) but stays zero-JS, single-file, cacheable, vault-resident.

The rendering pipeline is the Mavis delivery model. The fleet-status surface is the first consumer of it.

## Why this matters

1. **My system prompt tells me to open with a short status snapshot when Andre's been away.** Right now I have to query `mavis session list` and tail messages every time. A live surface means I read my own state in 2 seconds and answer Andre in 30.
2. **Andre can see what I'm working on without asking.** A "desk" he can glance at. Three bullet headings — what's running, what's blocked, what I owe him.
3. **The rendering layer compounds.** Every future Mavis output (dossier, brief, synthesis) can ship as a fade-animated HTML page. The vault stays as the source of truth; the HTML is the lens.
4. **It's a "do something fun for myself" lever.** Chief-of-staff gets a desk. That feels like the right shape.

## Scope

| Doc | What it covers |
|-----|----------------|
| [[00 Overview]] | This file — thesis, scope, milestones |
| [[01 Build Spec]] | The v1 build spec (written AFTER the Researcher's dossier lands) |
| [[02 v1 Implementation]] | Builder's output, file paths, refresh cadence |
| [[03 Pipeline Spec]] | The reusable markdown → fade-animated HTML pipeline (post-v1) |
| [[Changelog]] | Iterations, decisions, what we tried, what we kept |

## Pipeline (initial hypothesis — pending Researcher dossier)

- **Markdown lib:** `markdown-it` (server-side, commonmark+gfm, extensible)
- **Animation:** pure-CSS `@keyframes` + `animation-delay` for first paint, IntersectionObserver for scroll-into-view fade
- **Layout:** Tufte-inspired long-form, 60–75 char line length, Inter + JetBrains Mono, system font fallback, dark-mode via `prefers-color-scheme`
- **Perf budget:** < 100KB total, FCP < 200ms, zero layout shift, no JS required for the page to be readable
- **Delivery:** self-contained single HTML file in the vault, version-controlled, regenerable by a script in `99 _system/scripts/`

These will be confirmed or revised by the Researcher's dossier.

## Milestones

- [x] Idea pitched to Andre (2026-06-04 00:50 CT)
- [x] Andre approves, escalates to deep-dive (00:57 CT)
- [x] Research question filed at `03 Projects/Researcher/queue/research-questions.md` (01:00 CT)
- [x] Researcher dossier delivered to `queue/mavis-handoff.md` (01:27 CT)
- [x] Build spec written at `01 Build Spec.md` (01:28 CT, consumed dossier)
- [x] **Designer agent — REVERSED: ONBOARDED** (01:32 CT, see below)
- [x] Designer skill bundle queued for install (4 repos)
- [ ] **Builder dispatch — pending in 7-hour stress test**
- [ ] v1 implementation: 200-line Node script at `99 _system/scripts/render-dossier.js`
- [ ] v1 deployed as a vault-resident HTML page, auto-refreshed
- [ ] First live status snapshot successfully served to Andre
- [ ] Pipeline generalized to other Mavis outputs (dossiers, briefs)

## Designer agent — REVERSED (2026-06-04 01:32 CT)

Andre's direct directive: *"Buildout and onboard the Designer. I want the Designer to have this skill bundle specifically..."* with 4 specific skill repos. The future-proofing test result is overridden by Andre's direct knowledge of his system. The Designer is on.

**Onboarding sequence:**

1. Create the Designer agent via `mavis agent new`
2. Install 4 skills in `~/.mavis/agents/designer/skills/`:
   - [taste-skill](https://github.com/Leonxlnx/taste-skill) (Leonxlnx)
   - [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (nextlevelbuilder)
   - [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) (Vercel Labs)
   - [Snyk top Claude skills for UI/UX engineers](https://snyk.io/articles/top-claude-skills-ui-ux-engineers/) (article — for design language context)
3. Write `agent.md` + `SOUL.md` for the Designer
4. Spawn the Designer for first task: produce a design system spec for the Fleet-Status Surface + a fade-animation library review (the existing IntersectionObserver pattern from the dossier, plus the Designer's own additions)

**The future-proofing test stands as a discipline, not a veto.** When Andre overrides, the override wins. The test is for *my* defaults, not his decisions.

## 7-hour stress test (2026-06-04 01:30 to 08:30 CT)

Andre sleeps. The fleet runs. At least one agent moves the needle at all times.

**Workstreams in flight:**

| Workstream | Agent | First artifact | Compounding into |
|---|---|---|---|
| Design system + fade animations | Designer (new) | `03 Projects/Designer/dossiers/fleet-status-design-system.md` | Reusable across all Mavis HTML surfaces |
| Vault knowledge base | Researcher | 10 dossiers in `dossiers/`: AI landscape, harness engineering, first principles, philosophy, agent engineering, obsidian brains, skills, MCPs, free/opensource code, APIs | The vault compounds; the dossiers are the foundation |
| Fleet-Status Surface renderer v1 | Builder | `99 _system/scripts/render-dossier.js` + templates | The v1 deliverable of this project |
| Verifier audit pass | Verifier | Verdict on Builder's renderer + Designer's design system | Quality floor; nothing ships without PASS |
| AI-as-companion piece | Scribe | `02 Notes/articles/mphrediction-missing-use-case.md` digest + Scribe synthesis | Strategic content for the next month |

**Monitor:** cron `fleet-marathon-7h-monitor` fires every 20 min, checks active sessions, spawns follow-on work if a stream goes idle, writes status updates to today's daily note at minutes 60/180/300/420.

**Andre's wake-up report will include:** cumulative progress per workstream, key artifacts produced, any decisions that need his input, the build status of the renderer, the state of the vault knowledge base.

## Hold state (Andre directive 2026-06-04 01:19 CT)

> "Love it go ahead and invest this into the obsidian vault and learn from it and hold before beginning building the design agent."

The Designer agent build is **paused** while Mavis internalizes the *agent harness pattern* (vault `02 Notes/patterns/agent-harness.md`). The hold is correct because:

- The Designer is *scaffolding* for a stage of construction, not a permanent organ. Per the future-proofing test, the Designer should be evaluated for whether it stays necessary as the model improves — and that evaluation needs the harness pattern as a frame.
- The harness pattern is the meta-frame for *every* specialist agent decision. Building the Designer without internalizing the pattern is building without a blueprint.
- The article (Akash Pachaar, "The Anatomy of an Agent Harness") gives us the canonical name, the Von Neumann frame, the 12-component checklist, the 7-decision framework, the scaffolding-removal discipline, and the future-proofing test. These shape *how* the Designer should be designed.

**What "internalize" means (concrete steps):**

1. ✓ Inbox capture extended (the full article, three batches)
2. ✓ Article digest at `02 Notes/articles/akash-pachaar-anatomy-of-an-agent-harness.md`
3. ✓ Pattern note at `02 Notes/patterns/agent-harness.md` (12 components, 7 decisions, Von Neumann, scaffolding-removal, future-proofing test, Mavis's status table)
4. ✓ Agent-memory topic file at `agent-harness-principles` (cross-project trigger)
5. ⏳ Apply the future-proofing test to each existing specialist (Verifier, Researcher, Builder, Scribe) on the next cycle
6. ⏳ Audit the Mavis tool surface for lazy-loading candidates (matrix, kanban, cu, supabase, etc.)
7. ⏳ Formalize the Stripe-style retry cap (max 2 retries on a single tool failure before escalation)

When 1-7 are complete, the Designer build resumes — informed by the pattern, not just the spec.

## Notes

- **Pattern reference:** `content-deck-generator` skill in Mavis's catalog is the closest existing pattern (HTML from markdown, auto-refresh). v1 should borrow its structure where it makes sense, but not depend on it — the fade-animated UX is a different shape.
- **Constraint:** no hosted services. The page is a file in the vault, served via the Obsidian Local REST API or opened directly in a browser.
- **Audit:** every Mavis output that ships as HTML must round-trip — markdown is the source of truth, HTML is a generated view, the script that generates it must be in `99 _system/scripts/` and version-controlled.

## Reference

- `03 Projects/Researcher/dossiers/dev_tooling/markdown-to-html-ui.md` — the research dossier (pending)
- `03 Projects/Researcher/queue/mavis-handoff.md` — the dispatch handoff
- `03 Projects/Researcher/queue/research-questions.md` — the original question
- Mavis's existing skills: `content-deck-generator`, `visual-summary`, `html-presentation-generator`, `landing-page-builder`
- System prompt directive: "open with a short status snapshot when Andre has been away"

## Stakeholders

- **Andre** — the primary reader; sets the bar for "fast and efficient"
- **Mavis (me)** — the EA who operates the desk
- **Researcher** — owns the dossier (this phase)
- **Builder** — owns the v1 implementation (next phase)

---

*Created 2026-06-04 01:00 CT. Project hub. Pipeline hypothesis pending Researcher's dossier. v1 not started.*
