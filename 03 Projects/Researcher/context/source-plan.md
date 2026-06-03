# Source Plan — Researcher

The Researcher's taste is encoded here. This is where it learns what to watch, what to skip, and how to weight what it sees.

## Operating Principle

> Prefer sources that change decisions. A wider collection is not a better collection.

If the plan collects everything, the vault drowns. If it only collects what is easy, the vault overfits to convenient APIs. This file is the balance.

## Source Lanes (current)

### ai_agents (high weight)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| GitHub: langchain-ai/langchain, crewAIInc/crewAI, letta-ai/letta, openai/swarm, anthropics/anthropic-sdk | primary | 6h | Watch releases, RFCs, breaking changes |
| GitHub: sigoden/aichat, mitchellh/ghostty, simonw/llm | primary | 6h | Tooling patterns |
| RSS: LangChain blog, Letta blog, Anthropic engineering | primary | 6h | Primary voice |
| X: curated "AI builders" list | social | 6h | Early signal only — verify before dossier |

### frontier_ai (high weight)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| OpenAI blog + release notes | primary | 6h | |
| Anthropic news + research | primary | 6h | |
| Google DeepMind blog | primary | 6h | |
| arXiv cs.AI + cs.CL (filtered by Andre's keywords) | primary | 12h | Use arxiv-sanity or HF papers API |
| Hugging Face: trending models, trending spaces | primary | 6h | |
| MiniMax releases (when public) | primary | 6h | Direct source of truth for Andre's stack |

### memory_orchestration (high weight)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| GitHub: letta-ai/letta, plastic-labs/honcho, mem0ai/mem0, chroma-core/chroma | primary | 6h | |
| Docs: pgvector, sqlite-vec, LanceDB, Qdrant | primary | 24h | |
| X: @mem_palace, @Letta_AI, @plastic_labs | social | 6h | Verification queue only |

### dev_tooling (high weight)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| Official docs for tools Andre uses (Claude Code, Codex, OpenCode, Hermes, OpenClaw) | primary | 24h | |
| GitHub releases for the same | primary | 6h | |

### research_method (medium weight)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| r/MachineLearning | secondary | 24h | Filter by score > 100 |
| LessWrong, AI Alignment Forum | secondary | 24h | |
| Selected Substacks (Latent Space, Interconnects, etc.) | secondary | 24h | |

### builder_patterns (low weight)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| Indie Hackers | secondary | 24h | Filter for AI-agent builders |
| Hacker News (filtered: AI + agents + tools) | secondary | 24h | |
| Specific Substacks on solo-founder patterns | secondary | weekly | |

### crypto_rails_agent_commerce (medium weight)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| Base blog + docs | primary | 24h | |
| Coinbase developer blog | primary | 24h | |
| x402 protocol updates | primary | 24h | |
| Agent commerce discussions (X, Farcaster) | social | 12h | Verify before dossier |

### robotics_embodied (low weight — watch only)

| Source | Type | Cadence | Notes |
|--------|------|---------|-------|
| Selected lab blogs (Figure, 1X, Skild AI) | primary | weekly | |
| arXiv cs.RO (filtered) | primary | weekly | |

### last30days (high-recall multi-source probe)

**Treat as a single lane with configurable subsets — it fans out internally to 14+ surfaces.** Engine: `~/.agents/skills/last30days/scripts/last30days.py --emit compact --store "<TOPIC>"`. Wrapper: `scripts/last30days_collect.py` (to be built in REFRESH-2 per Andre's sequencing, encoding what REFRESH-1's manual sequence actually worked).

**Sub-tag discipline (enforced at write time, not at read time):** every finding from this lane is tagged with one of two sub-tags before it enters `knowledge/sources.jsonl`. This is the implementation of Mavis's "two sub-tags rather than a collapsed one" rule.

| Sub-tag | Subsets in scope | Type effective | Notes |
|--------|------------------|----------------|-------|
| `last30days/reasoning-primary` | GitHub, OpenRouter, Reddit, Hacker News, Polymarket, YouTube | primary-or-secondary depending on subset | Reddit/HN are secondary by type but treated as primary for *reasoning* purposes — they reflect multi-perspective community signal useful for triangulation, not verification. OpenRouter is primary cross-model synthesis. GitHub is primary for code-level claims. **Cross-source agreement with primary lanes can promote these to claims.** |
| `last30days/social-weighted` | X (Twitter), TikTok, Instagram, Bluesky, Threads, TruthSocial, Digg | social | Engagement-weighted. **Single-source findings default to `queue/verification-review.md` (`issue: social_only`, `issue: single_source`) before dossier weight.** **Requires `SCRAPECREATORS_API_KEY` in `~/.config/last30days/.env`. Without it, this sub-tag is silent — do not block on the key.** |

**Per-subset type details:**

| Subset | Sub-tag | Native type | Cadence / weight |
|--------|---------|-------------|------------------|
| GitHub | reasoning-primary | primary | high — code-level signal, replaces per-repo ad-hoc watching |
| OpenRouter | reasoning-primary | primary (multi-model synthesis) | medium — useful for triangulation, not as a source of facts |
| Reddit | reasoning-primary | secondary | medium — community signal, trust varies by subreddit |
| Hacker News | reasoning-primary | secondary | medium — higher signal density than Reddit for AI topics |
| Polymarket | reasoning-primary | secondary | low — prediction-market signal for "is X actually shipping" probes |
| YouTube | reasoning-primary | secondary | low — tag by channel, not by topic |
| Web (general) | reasoning-primary | secondary | low — fallback, often redundant with arXiv RSS |
| X (Twitter) | social-weighted | social | low — key-gated |
| TikTok | social-weighted | social | low — key-gated |
| Instagram | social-weighted | social | low — key-gated |
| Bluesky | social-weighted | social | low — key-gated |
| Threads | social-weighted | social | low — key-gated |
| TruthSocial | social-weighted | social | low — key-gated |
| Digg | social-weighted | social | low — key-gated |

**Cadence:** invoked on demand for dossier recency probes during REFRESH step 5, not on a fixed schedule. Use subset mode (`--search reddit,hackernews,github "<TOPIC>"`) to keep wall cost bounded.

**Routing:** the wrapper script writes findings to `raw/last30days/<timestamp>.json` and appends to `knowledge/sources.jsonl` + `knowledge/findings.jsonl`. Cross-source agreement with primary lanes can promote `last30days/reasoning-primary` findings to claims. `last30days/social-weighted` findings go to verification queue first.

## Weights and Tuning

- **Bump weight** when a source consistently produces dossier-grade signal (cross-source agreement, primary, fresh).
- **Demote** sources that go silent or start producing low-trust signal.
- **Add** sources when a new lane appears in `context/interest-profile.md`.
- **Remove** sources that have produced zero signal in 60 days.

Tuning decisions are recorded in `decisions/source-plan-changes.md`.

## Anti-Patterns

- **Daily-summary-of-X scrapers.** If a source's output is "here are today's headlines," it does not get dossier weight.
- **Aggregator-only sources.** If a source is repackaging other sources, demote it to the source it repackages.
- **Engagement-bait social accounts.** No matter how on-topic, if the account is "growth content," verification queue only.
- **Promotional material** (vendor blogs disguised as research). Read, but never use as primary.

## Collector Health

Per-source health is tracked in `ops/collector-health.md`. A lane that fails 3 consecutive runs is marked `degraded`, removed from the active plan, and surfaced in the operator brief.

---

*The source plan is taste. Update it like you update a chef's pantry — keep what's working, demote what isn't, never let it grow without pruning.*
