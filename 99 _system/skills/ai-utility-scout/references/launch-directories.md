# Launch Directories — ai-utility-scout

The 4 approved AI launch directories. The default rotation
the chief alternates across days to get a diverse feed.
Operator can supply any custom URL.

## 1. There's An AI For That

**URL:** `https://theresanaiforthat.com`
**Tab:** "Today"

**Strengths:**
- Daily curated list
- Strong for SMB-flavored tools (inventory, voice, video)
- Pillar 1/2/6 friendly

**Weaknesses:**
- Weak for dev-only infrastructure
- Some entries are aggregator duplicates of Product Hunt

**Best for:** SMB-focused launches, voice/video tools,
infrastructure with consumer angle.

## 2. Product Hunt — AI category

**URL:** `https://www.producthunt.com/topics/artificial-intelligence`
**Tab:** Default (top by upvotes)

**Strengths:**
- Daily launches
- Upvote-based ranking
- Strong for new products with consumer/SMB angles

**Weaknesses:**
- Launch-pad noise (day-of-launch voting)
- Some entries are clearly hype-cycle
- May require login for full archive (H2 halt)

**Best for:** New product launches, consumer/SMB tools,
tools with strong community backing.

## 3. Rundown AI

**URL:** `https://www.rundown.ai`
**Tab:** Default (today's post)

**Strengths:**
- Daily AI news post + weekly tool roundup
- More curated than Product Hunt
- Strong for "what dropped this week" framing

**Weaknesses:**
- Smaller tool list (focuses on a few highlights)
- Daily post may not have a "tools" section every day

**Best for:** Weekly tool roundups, narrative-driven
introductions, "the news + the tool" angle.

## 4. Hacker News — Show HN

**URL:** `https://news.ycombinator.com/show`
**Tab:** Default

**Strengths:**
- Dev-flavored
- Open-source repos, dev infra
- High signal for technical AI tools

**Weaknesses:**
- Weak for SMB-flavored tools (mostly developer audience)
- High noise-to-signal ratio
- Vote score matters more than "new today"

**Best for:** Technical AI tools (open-source repos, dev
infra). Use as a fallback for technical categories.

## Rotation strategy

Default rotation: alternate across the 4 directories across
days to get a diverse feed:

| Day | Directory |
|---|---|
| Monday | There's An AI For That |
| Tuesday | Product Hunt — AI |
| Wednesday | Rundown AI |
| Thursday | Hacker News — Show HN |
| Friday | There's An AI For That (re-visit) |
| Saturday | Operator's choice |
| Sunday | Skip (low signal on weekends) |

Operator can override per run.

## Custom URLs

Operator can supply any custom URL. The chief opens the
URL, applies the filter, picks the strongest tool per
`references/filter-rules.md`.

Custom URL examples:
- `https://betalist.com/?cat=ai` (BetaList AI category)
- `https://www.futurepedia.io/` (Futurepedia)
- `https://www.aibase.com/` (AIBase)
- `https://www.toolify.ai/` (Toolify)

If a custom URL is paywalled or requires login, HALT (H2)
and surface.
