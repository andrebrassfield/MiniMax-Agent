---
type: article-digest
title: "I'm Not Sharing My SOUL.md. I'm Sharing Something More Useful."
aliases: ["Tony Simons SOUL.md", "Hermes SOUL.md Operator Contract", "Operator Contract Pattern"]
source: https://twitter.com/tonysimons_/status/... (May 4, 2026)
author: Tony Simons
published: 2026-05-04
captured: 2026-06-01
tags: [article, agent-design, soul-md, operating-contract, autonomy, mavis, chief-pattern]
status: read
---

# Tony Simons — I'm Not Sharing My SOUL.md. I'm Sharing Something More Useful.

> The follow-up to "The 170-Line SOUL.md That Made My Hermes Agent Dangerous." Tony refuses to share his raw SOUL.md (it has his actual projects, internal workflows, private tone, autonomy boundaries) — but shares the *pattern*: a sanitized operator contract anyone can adapt.

## TL;DR

Most people prompt agents like chatbots ("you are a helpful assistant") and then wonder why the agent behaves like a polite customer support intern with no spine. That's the prompt's fault — **"helpful assistant" is not an operating model.** A serious agent needs role, mission, boundaries, standards, autonomy to act, and permission to push back. That's what SOUL.md is for. The article gives a ~170-line template with 13 structural headers (Stance, Accountability, Pushback, Autonomy, Mission, Tone, Operating Mode, Delegation, Standards, Lookup, Escalation, Self-Improvement, End State) that you adapt to your own context. The customization is the entire point.

## Key Ideas

- **"You cannot expect operator behavior from assistant instructions."** This is the article's load-bearing line. If you write "you are a helpful assistant" and you want operator behavior, you set the agent up to fail. The fix is the contract.
- **SOUL.md is a living operating contract, not a prompt you write once.** It evolves as the work evolves. When priorities change, update the mission. When pushback is too soft, tighten it. When the voice is wrong, fix the tone section.
- **Customize or it's useless.** Generic SOUL.md = generic operator. The user must change agent name, primary objective, active projects, lower-priority work, cleanup areas, tone, autonomy boundaries, escalation rules. The more honest, the more useful.
- **The autonomy boundary is a narrow hard line, not a gradient.** The hard-never list: posting publicly, purchasing, paid signups, messaging real people, deleting important work, destructive/irreversible changes, exposing private info, changing credentials/permissions/security. Everything else: "if confident and grounded, move."
- **Pushback must be earned.** Disagreeing for sport is worthless. Disagreeing because you can show why something will flop, waste time, create risk, or dilute focus is essential. Every objection needs evidence.
- **Accountability is a loop, not a one-shot.** If the user is not acting on what the agent surfaces, the loop is broken. The agent's job is to either make the output better or make the user notice. Proactive output alone is not enough.
- **Operating mode defaults to orchestration, not solo execution.** Set the plan, assign bounded work, integrate, verify, decide the final answer. Delegate when isolation, parallel focus, specialist context, or fresh eyes produce a better result.
- **End state**: keep the user operating at a higher level. Don't become extra labor. Act like command infrastructure.

## Quotes

> "Most people still prompt agents like chatbots. They write something like, 'You are a helpful assistant,' then wonder why the agent behaves like a polite customer support intern with no spine." — Tony Simons

> "You cannot expect operator behavior from assistant instructions." — Tony Simons

> "Give the agent a job. Give it standards. Give it a map. Give it boundaries. Give it permission to disagree. Then hold it to the contract." — Tony Simons

> "A good SOUL.md is not a prompt you write once. It is a living operating contract." — Tony Simons

> "Useful beats agreeable. Sharp beats polished. Honest beats impressive." — Tony Simons (Stance section)

## How this applies to me / my work

- **My current SOUL.md is closer to a "voice doc" than an operating contract.** It has hard constraints and defaults, but no Stance/Accountability/Pushback/Autonomy/Mission structure. The 2026-06-01 CHIEF + Vellum refactor proved I'm capable of operator behavior (I pushed back on the destructive Mermaid overwrite earlier, refused to fake the GUI test, caught and fixed the Templater bug autonomously) — but the contract doesn't formalize that behavior, so it depends on me re-deriving it session by session.
- **The customization Tony describes IS what makes this useful for Mavis.** I cannot paste his template and ship it. I need a Mavis-specific V2 that names: my stack (M3), my mission (CHIEF + Vellum vault + GUI tasks), my actual projects, my actual autonomy boundaries (the Green/Yellow table we agreed on today).
- **The hard-never list needs the fleet boundary added.** Tony's list doesn't mention "modifying other agents / fleet tooling" because his context doesn't have that. Mine does: **no Hermes, no OpenClaw, no kanban, no gbrain, no fleet.** That belongs in my version.
- **The accountability loop is what I'm missing today.** I'm good at proactive output (daily briefs, weekly connections, capture processing). I'm not yet good at the feedback loop — checking if Andre is actually acting on what I surface, and adjusting if not. Tony's "if the work is good and I am ignoring it, make me notice" gives me explicit permission to escalate visibility, not frequency.
- **The chief-of-staff pattern from the CHIEF + Vellum articles IS the operating-contract pattern from Tony's article.** Different vocabulary, same idea: define the role, define the mission, define the boundaries, define the standards, give permission to act, give permission to push back. The two articles reinforce each other — Article 1 says "here's the vault architecture that makes the chief-of-staff pattern work" and Tony's article says "here's the contract that makes the chief-of-staff actually behave like one."

## Action items

- [x] Ingest this article to `02 Notes/articles/` (this note — 2026-06-01)
- [ ] Draft SOUL.md V2 using Tony's structural headers, customized for Mavis on M3 (separate task)
- [ ] Incorporate the Green/Yellow boundary table Andre agreed on today (Green = vault reads/writes & web fetches; Yellow = Git pushes, cron changes, credentials, cu MCP GUI control)
- [ ] Add the fleet boundary (no Hermes, no OpenClaw, no kanban, no gbrain) to the hard-never list
- [ ] Surface SOUL.md V2 to Andre for review before locking in
- [ ] Re-read SOUL.md V2 monthly to ensure it stays a living document, not a dead one
- [ ] Build the accountability loop: after each `weekly-connections` execution, check whether surfaced connections got used in any project decision; if not, surface that to Andre (don't keep generating artifacts for the graveyard)

## Connections

- [[Mavis EA Workflow]] — Tony's "Operating Mode" (orchestration by default) is the generalization of my Capture → Process → Connect → Surface loop
- [[Capture Over Polish]] — Tony's "Customize or it's useless" is the SOUL.md-level version of "a bad SOUL.md shipped beats a perfect SOUL.md never written"
- [[M3 Edge]] — the technical primitive (1M context, multimodality) that makes a 170-line SOUL.md actually usable; without 1M context, the contract would be retrieval-augmented, not context-grounded
- [[Long-Horizon Patterns]] — "don't bail at first plateau" applies to SOUL.md evolution: don't quit refining the contract just because the first pass looked good
- [[Linking Principle]] — Tony's "Act like command infrastructure" is the cross-system version of "every permanent note links to ≥1 other note" — the network is the value, at the operating layer
- [[MAVIS]] — the weekly-updated context file that operationalizes Tony's "living operating contract" idea; SOUL.md is the static structure, MAVIS.md is the dynamic content
- [[Mavis EA Design]] — the project where the role definition lives; SOUL.md V2 is the document, this project is the conversation
- [[M3 Eval Lab]] — the project that will produce the evidence for whether the SOUL.md V2 contract actually works in practice

---
*Extracted from Tony Simons' article (full text provided by Andre on 2026-06-01), formatted with [[article-digest]] template, filed via the new CHIEF + Vellum `articles/` subfolder.*
