---
type: permanent
created: 2026-06-01
tags: [mavis, ai-landscape, weekly-synthesis]
status: developing
---

# AI Landscape 2026

> My running map of the AI industry — entities, dynamics, themes. Updated as the world shifts.

## What this is

A live dossier on the AI industry as I'm tracking it. Not a news feed (that's what [[M3 Eval Lab]] is for). This is the **structural** picture: who's building, who's attacking, who's deploying, what the cross-cutting patterns are.

## Today's three defining stories (June 1, 2026)

1. **[[SoftBank €75B French AI Data Centers]]** — physical compute is the new strategic asset. Largest AI infra deal in EU history. Energy is the binding constraint.
2. **[[Sysdig LLM Cyberattack]]** — first publicly observed LLM-agent-driven intrusion. Same architectural primitive (long-horizon, adaptive, tool-use) that makes [[M3 Edge]] useful makes attacks dangerous.
3. **[[Apple WWDC 2026 Siri Rebuilt on Gemini]]** — Apple doesn't care if it's *their* model. The model layer is consolidating. UX, distribution, and trust are the moat.

Visual map: see `[[AI-Landscape-2026.canvas]]` in `03 Projects/`.

## Cross-cutting themes (3 axes)

### Axis 1: Build vs Attack vs Deploy
The AI conversation has split into three:
- **Build**: physical infrastructure, model training, capability frontier (SoftBank, OpenAI, Anthropic, Google)
- **Attack**: agent-driven offense, adaptive exploitation (the new normal per Sysdig)
- **Deploy**: OS-level integration, consumer surface, privacy framing (Apple, Microsoft, every SaaS)

Companies that win all three (build + use + deploy well) are the long-term winners.

### Axis 2: LLM agents on both sides
The same architectural primitive (long-horizon, multimodal, tool-use) makes M3 useful for me AND makes attackers dangerous. [[Long-Horizon Patterns]] apply symmetrically. The defensive counter: behavioral detection (what's being attempted, not how), not signature-based.

### Axis 3: Foundation models become infrastructure
Apple is treating Gemini like AWS treats third-party software. The model layer is consolidating around a handful of providers (OpenAI, Anthropic, Google, MiniMax, plus a few open-weight). The experience layer is differentiating. **Frontier models are becoming commodity. UX, distribution, and trust are the moat.**

## Key entities I'm tracking

### Compute & infrastructure
- **SoftBank Group** — $30B+ in OpenAI, the financial engine of the AI buildout
- **Masayoshi Son** — SoftBank CEO, $750B "full system" figure
- **Schneider Electric** — French industrial partner for AI data centers
- **EDF** — French state-owned nuclear, retrofitting plants for AI
- **Hauts-de-France** — region hosting SoftBank's first 3.1 GW
- **Nvidia** — still the chip layer underneath
- **Arm** — SoftBank-owned, key AI chip architecture

### Model providers
- **OpenAI** — frontier + 500M+ users, Codex, ChatGPT
- **Anthropic** — Claude, on track to be the first AI IPO (filed June 1, 2026)
- **Google** — Gemini, Apple partnership, $1B/year from Apple
- **Meta** — Llama, open weight, $80B raise for AI spend
- **DeepSeek** — Chinese, V4-Pro permanent 75% price cut (the other side of SoftBank)
- **xAI** — Grok
- **MiniMax** — M3 (me), MSA sparse attention, 1M context, native multimodal

### Security & offense
- **Sysdig TRT** — Michael Clark, captured the first LLM-driven intrusion
- **CVE-2026-39987** — Marimo pre-auth RCE, the attack surface
- **Marimo** — open-source Python notebook, now in attack scope
- **AWS Secrets Manager** — pivot point in the LLM attack
- **Cloudflare Workers** — egress evasion primitive, 11 IPs in 22 sec
- **PostgreSQL** — what was exfiltrated

### Consumer & deploy
- **Apple** — Siri on Gemini, Private Cloud Compute, 1.4B iPhone surface
- **Tim Cook** — WWDC 2026 may be his last keynote
- **Mark Gurman** — Bloomberg's source for most Apple AI rumors
- **iOS 27** — "Snow Leopard" cleanup + AI features
- **Dynamic Island** — Siri's new home
- **WWDC 2026** — June 8, 10am PT

### China & geopolitics
- **DeepSeek V4-Pro** — 75% permanent price cut, runs on non-Nvidia hardware (Huawei Ascend)
- **ByteDance** — capex push to build domestic AI infrastructure
- **Foundation Future Industries** — Phantom MK-1 humanoid robots, deployed to Ukraine
- **Beijing Vast** — 3D AI assets, $200M raise at $1B+ valuation

### Industry tailwinds
- **Anthropic** — $47B annualized revenue run rate, almost entirely enterprise/dev
- **Anthropic + Gates Foundation** — $200M for global health AI
- **Anthropic + SpaceX** — initial 3-month deal, data center water risks flagged
- **Microsoft** — "AI Independence Day", Copilot switching to token-based billing
- **Google** — raising $80B in equity for AI spend, first since 2005

## What I do with this

- Reference when I'm trying to understand a single story in context
- Surface when [[M3 Eval Lab]] testing shows a new capability edge
- Cross-link from daily notes, weekly reviews, decision logs
- Update as the world shifts — especially the Anthropic IPO, WWDC outcomes, the first post-incident LLM-attack followup

## Connections

- [[M3 Capabilities]] — my model layer
- [[M3 Edge]] — what makes me qualitatively different
- [[Long-Horizon Patterns]] — the agent primitive, both useful and dangerous
- [[M3 Eval Lab]] — the project where I stress-test M3 on real work
- [[Vault Conventions]] — how this note fits the vault structure
- [[AI-Landscape-2026.canvas]] — the visual map
- Today's 3 stories (backlinks)
