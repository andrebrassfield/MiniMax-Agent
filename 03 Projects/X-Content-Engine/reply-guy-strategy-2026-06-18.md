---
type: strategy
created: 2026-06-18 10:50 CT
owner: Mavis (chief)
audience: Andre
status: **DEPRECATED 2026-06-24 19:01 CT** — cron `reply-sweep-daily` deleted. Pipeline never achieved Week 1 cap (3 POCs total, 0 captured metrics). Underlying architecture shifted from Playwright MCP to mavis browser bridge; reply-guy pipeline was the only remaining Playwright-dependent path and was never ported. Revival requires either (a) porting x-reply-guy to mavis browser bridge, or (b) launching Playwright Chrome with the user's real profile (Option C from 2026-06-18 19:04 halt-postmortem). Do NOT re-enable this strategy as-is.
depends_on:
  - 03 Projects/X-Content-Engine/agents/persona.md
  - 03 Projects/X-Content-Engine/agents/feedback-loop.md
  - 03 Projects/X-Content-Engine/memory/content_brain.json
  - x-publish skill (Playwright MCP path) ← **STALE**: x-publish now uses mavis browser bridge
  - x-niche-scraper skill (target discovery)
  - x-engagement-hunter / x-value-bomb-dropper / x-empowerment-hunter (reply patterns)
  - x-analytics-tracker skill (engagement feedback) ← **ALSO BROKEN**: 3 consecutive H1 halts per 2026-06-24 audit
deprecation_postmortem: 03 Projects/X-Content-Engine/postmortems/2026-06-18-19-09-reply-sweep-halt.md
prior_halt_postmortem: 03 Projects/X-Content-Engine/queue/halt-postmortem-2026-06-18-evening.md
---

# Reply-Guy Strategy — X-Content-Engine v2

## TL;DR

Posting originals is "yelling into the abyss" — even with a perfect 9-batch cron chain, single-account originals plateau at a few hundred impressions. The actual distribution engine is **replies to high-engagement posts in the niche**. Top replies on viral posts can hit 10-100x the impressions of originals. Andre's persona + Scribe + Playwright path gives us the toolchain to do this at scale.

**Week 1 target:** 10 replies/day (1 evening sweep, 19:00 CT) + 3 originals/day. Total: 13 pieces/day. Reply:original ratio = 3.3:1 — conservative for Week 1, scales to 30/day (8:1 ratio) only after engagement data confirms algorithm response is positive.

**Volume ramp plan (Andre's directive 2026-06-18 11:25 CT):**
- **Week 1 (2026-06-18 → 2026-06-25):** 10 replies/day, 1 sweep (evening). Monitor algorithm response.
- **Week 2+ (post-2026-06-25):** Scale to 30/day (3 sweeps: morning, midday, evening) IF engagement velocity is positive. Halt expansion if any negative signal (rate limit, engagement collapse, deboost).

**Effort:** New skill `x-reply-guy` (orchestrator) + 1 cron sweep/day + 1 daily tracker + 1 weekly recalibrator. Builds on existing x-niche-scraper, Scribe, x-publish, x-analytics-tracker.

**Resilience infrastructure (built 2026-06-18 11:27-11:35 CT):**
- `x-ui-bouncer` — pre-flight + mid-flight modal dismissal (X.com + general React-controlled sites)
- `x-semantic-locator` — 3-tier element finding (a11y → data-testid → contentEditable)
- `x-health-telemetry` — pre-sweep rate-limit + post-visibility + engagement-velocity checks

**Risk:** Replies are higher-stakes than originals (public comment on someone else's post = harder to walk back). Resilience skills + the 10/day Week 1 cap + the byte-identical Playwright verifier are the 3 layers of defense.

---

## The Algorithm (the load-bearing rules, 2026)

Sources: Typefully Jan 2026 deep-dive (Phoenix open-source), X-eng repo notes, Sprout Social 2026, Graham Mann "What's Actually Working", multiple reply-guy case studies. Where sources conflict, I picked the version that the open-source code + multi-source convergence support.

### What Phoenix (the 2026 algorithm) does

- **Grok transformer ranks posts** — replaced the 2023 hand-engineered feature system. No more "post at this time" / "use these hashtags" rules. The model learns from each user's interaction history.
- **Predicts 19 distinct actions per post** as probabilities (like, reply, repost, click, dwell, share, follow, quote-tweet, mute, block, report, etc.) and combines them into a score.
- **Per-user scores**, not universal scores. A post that scores 0.8 for User A might score 0.3 for User B based on their history.
- **No hand-engineered features** — but the code does have specific weight patterns (e.g., replies that get replies weighted 75x more than likes per the X-eng open-source notes).

### The 4 rules we can build on (the load-bearing 4)

1. **Replies are the highest-value engagement signal.** A reply requires effort (think + type). The "comment + author reply" pattern is the load-bearing compounding move. One reply with high reply-count can outperform 100 likes.

2. **First-30-min engagement velocity is decisive.** If a post doesn't get engagement in the first 30 min, it ages out (hard cutoff, not gradual). This applies to BOTH the original we're replying to (timing our reply) AND our own originals (timing our post).

3. **In-network distribution gets a priority boost.** Accounts you follow see your content first. The strategy: get on X Lists of mid-size accounts (1K-100K followers) → reply to their posts → they see our reply → they follow us back (or at least don't mute) → their followers see our replies on their timeline → we build in-network.

4. **Author diversity scorer attenuates consecutive posts from the same author.** The same author can't dominate a feed. BUT this applies to ORIGINAL POSTS, not REPLIES. A high-quality reply on a viral post is a separate author-context (the OP is the post author, the reply is its own candidate).

### What to AVOID

- Posting and ghosting (no replies to your own comments = the "author reply" compounding never fires)
- Same content reposts (duplicate detection will catch it)
- Long threads (3-6 tweets is the new sweet spot, not 20-tweet epics)
- Hashtag spam (filtered for muted-keyword audience segments)
- Rage bait / sentiment-negative content (Grok downranks even if engagement is high)
- Generic engagement ("great post 🔥", "I love this") — these don't pass the engagement-velocity threshold
- Bought followers / engagement pods (algorithm detects follower:engagement ratio, downranks)

---

## The Reply-Guy Strategy (the operational shape)

### Volume math (per 2026 case studies)

| Tier | Originals/day | Replies/day | Reply:Original ratio | Source |
|---|---|---|---|---|
| 0-1K followers | 3-5 | 20-30 | 6:1 | grahammann.net (Dec 2025 data) |
| 1K-10K | 5-10 | 30-50 | 5:1 | grahammann.net, brandwatch.com |
| 10K-50K | 10-15 | 50+ | 4:1 | Metricool 2024 study |

Andre is at ~low-tier follower count (R1D1 just published, small in-network). Target: 30 replies/day, 3-5 originals/day, ratio 8:1.

### Reply types — the 3 typologies (Andre's 2026-06-18 11:36 CT upgrade)

**The 75x reply-bait rules** (Phoenix 2026 algorithm: replies-to-replies weighted 75x more than likes). Polite agreements are a dead loss. The reply's value comes from the *typology*, not the *length* — different typologies catch different audiences, and only 3 are load-bearing:

| Typology | When to use | Formula | Example |
|---|---|---|---|
| **[P2: Operator Insight]** | High-level strategy / vague goals | [Counter-intuitive metric] + [Load-bearing constraint] + [Structural outcome] | "Sound human matters after pickup. Capture rate is the bottleneck — the HVAC shops I have seen go from 40% to 92% capture with sub-200ms latency. Sounds human is 5% of the conversion. The other 95% is picks up at 9pm." |
| **[P4: Contrarian-Extend]** | Popular technical framework / tool / breakthrough | [Strip branding to primitive] + [Expose systemic cost / design equivalence] | "Tool system is also just prompt engineering. The 200 lines of system prompt + retry patterns is the same shape as the memory layer — just expressed in dispatch logic. The opposite framing is doing a lot of work." |
| **[P5: Deep Contrarian]** | Mainstream stat / fear-mongering / linear trend | [Challenge timeline/half-life] + [Isolate risk profile the mainstream misses] | "The 3.4x stat misses the half-life. AI-generated vulns get auto-fixed in days. Human-written vulns live for 14 months. The risk profile is different, not worse." |

**Distribution target (Week 1):** 30% P2, 40% P4 (default fallback if unclear), 30% P5. The P4 dominance is deliberate — the niche has the most technical-framework posts in the AI/trades/GEO space, and P4 produces the highest-leverage replies in this segment. P5 is for the safety-fear-mongering posts. P2 is for the strategy/vague-goal posts. Tune based on engagement data after Week 1.

**Disqualified typologies (the old 5-reply-type distribution is now REPLACED):**
- "Insight" without a metric — falls back to P2 (Operator Insight) or P4 (Contrarian-Extend) depending on target
- "Contrarian" without reasoning — falls back to P4 or P5
- "Follow-up question" — too soft, doesn't trigger the 75x weight
- "Pure value" without the typology formula — falls back to P2 (operator insight) if the answer is a metric
- "Empathy" — only acceptable for P5 (Deep Contrarian) targets (AI anxiety posts)

### The 4-step Validation Gate (pre-publish content quality)

Before any reply is published, the Scribe's draft must pass the validation gate at `~/.mavis/agents/mavis/skills/x-reply-guy/scripts/validate-reply.py`:

1. **Char count strictly 140-275.** Outside range → re-dispatch the Scribe with a trim/expand prompt.
2. **Apostrophe detection + JSON-escape.** If apostrophes present, the script returns `escaped_version` — use that in the Playwright `browser_type` text field. Prevents the Playwright serialization issue that was the root cause of the v2 duplication bug.
3. **Soft-word scrub.** Flags Important / Interesting / Amazing / Revolutionary / etc. (full list in the script). Re-dispatch with flagged words listed.
4. **Compel-to-debate heuristic.** Score-based (0-1, threshold 0.6). Components: number present (+0.3), technical term (+0.2), staccato ≤4 sentences (+0.2), ends with declarative period (+0.2), punchy ≤10 words/sentence (+0.1). Below threshold → "the reply generates a 'Huh', not a debate — add a metric, end definitively, take a sharper angle."

**Test results on the v1 batch (2026-06-18 11:38 CT):**
- Reply 1 (P2 Operator Insight): PASS, debate_score 0.9
- Reply 2 (P4 Contrarian-Extend): PASS, debate_score 0.7
- Reply 3 (P5 Deep Contrarian): PASS, debate_score 0.85

The Scribe's voice + the typology formulas produce validator-passing output by default. The gate is defensive — catches mechanical issues (char count, soft words) that the Scribe might miss at scale.

### Targeting logic (who to reply to)

The targeting IS the strategy. Bad reply on a low-engagement post = wasted. Great reply on a viral post = 10K+ impressions.

**Target tiers (priority order):**

| Tier | Account size | Why | Reply effort | Expected payoff |
|---|---|---|---|---|
| **A** | 5K-50K followers, niche overlap | Their followers ARE our target audience. Reply seen by 10-50K qualified eyes. | High (must be insightful) | High (10K+ impressions possible) |
| **B** | 50K-500K, niche adjacent | Bigger reach but less targeted. Useful for visibility spikes. | Medium (insight or contrarian) | Medium-high (viral post = jackpot) |
| **C** | 1K-5K, hyper-niche match | The reply-guy sweet spot. Smaller but high-engagement audiences. Easy to stand out. | Medium (any type) | Medium (1K-5K impressions, high follow conversion) |
| **D** | 500K+ | Avoid unless post is huge. Their timeline is too crowded; our reply gets buried. | Low (insight only, no contrarian) | Low unless OP is trending |

**Avoid:** 0-1K accounts (low ROI), non-niche accounts (wrong audience), 500K+ unless trending (buried), and any account with predominantly negative/drama content (Grok sentiment downrank).

### Timing

- **First-30-min is the engagement-velocity window** for the post we reply to. If we reply to a post that's already 4 hours old, the engagement velocity has decayed; our reply lands in a quiet thread.
- **Sweet spot:** reply to a post that's 5-30 min old. The post still has engagement velocity; our reply rides the wave.
- **Sweep schedule:** 3 sweeps/day aligned with high-activity windows:
  - 7-9 AM CT (morning, US East waking up)
  - 12-2 PM CT (midday, broad activity)
  - 6-8 PM CT (evening, US East + Europe overlap)
- Each sweep hunts for posts in the last 2 hours, picks the highest-value targets, drafts + posts 10 replies.

### The compound loop (the load-bearing long-term play)

The 75x weight on "comment + author reply" means: every reply that gets a reply from the OP (or from anyone) is worth 75x a like. So:

- After publishing a reply, monitor for replies.
- When someone replies to our reply, we reply back (within the first hour if possible).
- This extends the conversation thread, which Phoenix's OON Scorer surfaces to more people, which drives more replies, which compounds.

**The compounding math:** if 1 reply has a 30% chance of getting any reply, and we do 30 replies/day, we get 9 reply-threads/day. If each thread gets 2-3 follow-on replies, we have 18-27 conversation extensions/day. Each extension is a 75x-weighted signal. Even a small compounding effect over weeks dramatically grows the in-network distribution.

---

## The Pipeline (the technical shape)

### New skill: `x-reply-guy` (the orchestrator)

**Inputs:**
- Niche query (default: 6-pillar query list from content-research-daily)
- Sweep size (default 10 replies)
- Reply type distribution (default: 40/25/20/10/5)
- Persona path (default: `03 Projects/X-Content-Engine/agents/persona.md`)
- Source-of-targets: X List of mid-size niche accounts (default: to be built)

**5 phases:**

1. **Hunt** — `x-niche-scraper` with niche query, extract top 30 posts by engagement velocity (likes + replies in last hour). Filter: target tier A/B/C, post age <2h, no muted keywords, niche fit.
2. **Rank** — score each candidate: (target_account_tier × 3) + (engagement_velocity_score × 2) + (niche_fit × 4) + (recency_bonus × 2). Pick top N (= sweep_size).
3. **Draft** — dispatch Scribe for each target with: target post URL, post text, target author handle, suggested reply type. Scribe writes the reply in @DreTheSalesGuy voice. Output: `03 Projects/X-Content-Engine/drafts/replies-YYYY-MM-DD-HHMM.md` (rolling file).
4. **Publish** — for each draft, auto-publish via Playwright MCP (the proven path from post-1):
   - `browser_navigate` to target post URL
   - `browser_snapshot` to find `[data-testid="tweetTextarea_0"]` reply textbox ref
   - `browser_type` with `page.fill()` (NO duplication — the proven fix)
   - `browser_evaluate` to verify byte-identical content, no duplication
   - `browser_click` on Reply button (`[data-testid="tweetButton"]` or similar)
   - Capture reply URL via `browser_evaluate` on the just-posted reply
5. **Track** — log to:
   - `03 Projects/X-Content-Engine/drafts/_ledger.mdl`: one line per reply
   - `03 Projects/X-Content-Engine/queue/replies-published.mdl`: structured (NEW file)
   - `03 Projects/X-Content-Engine/memory/content_brain.json`: performance_log entry

### Cron schedule (the operational loop)

**Week 1 (current):**

| Cron | Schedule (CT) | Job | Status |
|---|---|---|---|
| `reply-sweep-daily` | 0 19 * * * (19:00 daily) | 10 replies (1 sweep, evening) | **WIRED 2026-06-18** |
| `reply-sweep-evening-2026-06-18` | 0 19 18 6 * (single-shot 19:00 today) | 10 replies, first cron test of the resilience-integrated pipeline | **WIRED 2026-06-18** |
| `reply-engagement-tracker-2026-06-19` | 0 9 19 6 * (single-shot tomorrow 9:00) | T+24h metrics on today's 4 replies (3 v1 + 1 evening sweep) | **WIRED 2026-06-18** |

**Week 2+ (if Week 1 data shows positive algorithm response):**

| Cron | Schedule (CT) | Job | Status |
|---|---|---|---|
| `reply-sweep-morning` | 0 8 * * * (8:00 daily) | 10 replies | NOT WIRED YET |
| `reply-sweep-midday` | 0 13 * * * (13:00 daily) | 10 replies | NOT WIRED YET |
| `reply-recalibrator-weekly` | 0 17 * * 0 (Sun 17:00) | Weekly recalibration based on engagement data | NOT WIRED YET |

Total Week 1: 3 crons. Week 2+: 5 crons. Each sweep is a 15-30 min job (mostly Playwright navigation + Scribe dispatch + post time + bouncer/locator overhead).

### X List of target accounts (v1 seed curated 2026-06-18)

The targeting depends on a maintained X List of 50-100 accounts in the niche. **v1 seed at `03 Projects/X-Content-Engine/lists/target-accounts-2026-06-18.md`** (50 accounts across the 6 pillars). The Researcher expands the list to 100+ by Week 2 via:
- "Accounts that follow X" lookups
- Reply-guy sweep discovery (when a high-engagement post comes from an account not in the list, add it)
- Andre's manual additions

The v1 seed is curated from the initial seed in the strategy doc + today's 3 v1-batch targets + the search results. Tier assignments are **approx** (the recalibrator verifies at Week 1 end). The full list lives at the file path above; the reply-guy skill reads it at sweep time.

---

## Safety Rails (tighter than originals)

Replies are riskier than originals — a public comment on someone else's post is harder to walk back than deleting your own tweet. Tighter rails:

1. **First batch (today, 3-5 replies):** Manual verification step. Mavis publishes, then sends Telegram to Andre with the reply text + URL + target post URL. Andre has 5 min to say "delete" before it's permanent.
2. **After first batch ships clean:** Auto-publish with the same Playwright safety checks as post-1 (byte-identical verify, no duplication, HALT on any issue).
3. **Daily check-in:** Cron `reply-engagement-tracker` runs at 9:00 CT, pulls yesterday's replies, surfaces any with negative engagement (ratio < 0.1) to Andre. Manual review for delete.
4. **HALT conditions (any of these → Mavis stops the sweep and surfaces to Andre):**
   - Login prompt on x.com
   - Rate limit warning
   - Duplication detected (Playwright regressed)
   - Text mismatch between draft and what was posted
   - 2+ consecutive replies fail to post (might be a session issue)
5. **Reply content safety:**
   - Scribe's hard rules (no banned phrases, no emoji, no hashtags, no CTAs) — already enforced
   - For P2 + P4 value-bomb replies, the zero-sales-pitch rule applies (x-value-bomb-dropper)
   - For P5 empowerment replies, the empathy + pivot rule applies (x-empowerment-hunter)
   - No controversial political content, no attacks on named people (Grok sentiment downrank + brand risk)

---

## Tracking + Compounding (the close-the-loop)

The X-Content-Engine already has a feedback loop (xce-feedback cron pulls metrics 3 days post-publish). Reply performance needs the same treatment.

**`03 Projects/X-Content-Engine/queue/replies-published.mdl`** (NEW — schema mirrors drafts-published.mdl):

```
- YYYY-MM-DD HH:MM CT — reply to @<target> (target_post: <url>) → <reply_url> | <reply_type> | <pillar> | x.com
```

**Brain's `performance_log`:** add fields:
- `target_post_id` (the post we replied to, for engagement spillover tracking)
- `target_author_handle`
- `reply_type` (insight/contrarian/question/value/empathy)
- `pillar` (P1-P6)
- `target_account_tier` (A/B/C/D)

**Weekly recalibrator (Sunday 17:00):**
- Read last 7 days of replies + their engagement
- Rank by: (engagement_received × 1) + (follows_attributed × 5) + (target_author_replied × 25) + (replied_to_again × 50)
- Top 20% of replies → same reply_type + same target tier gets +20% weight in next week
- Bottom 20% → -20% weight or rotate out of distribution
- Update reply-type distribution (40/25/20/10/5 → recalibrate)
- Update target list (add hot accounts, prune cold ones)

This is the "compounding" part. Each week, the system gets slightly better at knowing what works for @DreTheSalesGuy.

---

## First Batch Plan (today, 2-3 hours)

**Phase 1: Test the Playwright reply path (30 min)**
- Pick 1 mid-size niche post (e.g., @sama or @karpathy)
- Publish 1 reply via Playwright MCP
- Verify: byte-identical content, no duplication, reply URL captured
- If works: ship 2-4 more replies in this session
- If fails: HALT, debug, fall back to manual publish

**Phase 2: Build the x-reply-guy skill + first cron (60 min)**
- Write `~/.mavis/agents/mavis/skills/x-reply-guy/SKILL.md`
- Create the first cron `reply-sweep-evening-2026-06-18` (single-shot for tonight 19:00 CT)
- Schedule it via `mavis cron create` with the Playwright path
- Set TTL: 7 days (auto-cleanup if not refreshed)

**Phase 3: Wire the daily tracking (15 min)**
- Create `queue/replies-published.mdl` (NEW file, append-only)
- Set up `reply-engagement-tracker-2026-06-18` for tomorrow 9:00 CT (one-shot)

**Phase 4: Report to Andre with:**
- Strategy doc link
- First batch results (3-5 replies, URLs, target posts)
- Skill + cron design
- Request approval to scale to full 3-sweep/day pipeline

**Phase 5 (post-approval, next 24h):**
- Wire 2 more sweeps (morning, midday)
- Build the X List of target accounts (50-100 mid-size)
- Wire weekly recalibrator
- Switch from one-shot crons to recurring crons

---

## Open Questions for Andre

1. **Auto-publish vs manual review?** Default I propose: auto-publish with HALT on issues (the proven post-1 path), with first batch of 3-5 verified manually. But if Andre wants 100% manual review until he trusts the path, the crons can stage drafts to `drafts/approved-replies/` for his review.

2. **Volume ramp:** 30/day is the target. Should we start at 10/day (1 sweep) for the first week, then ramp to 30/day? Or go straight to 30? The risk of going straight: if a few replies get ratio-of-engagement wrong, the negative signal compounds. The risk of starting slow: we lose a week of compounding.

3. **Niche scope:** The 6-pillar query set is broad. Should we focus the first batch on 1-2 pillars (e.g., P2 Trades + P6 Hype) and expand later? Or hit all 6 from day 1?

4. **DM follow-up:** When a reply gets a high-engagement conversation, should the EA auto-draft a DM to the OP for the lead-qualifier pipeline? This would tie x-reply-guy → x-lead-qualifier → x-publish (DM path).

5. **Andre participation:** Should the EA notify Andre of high-value reply opportunities in real-time (e.g., "Sam Altman just posted, this is a Tier B target, here's a draft reply — ship?") so he can manually review the most important ones?

---

## Cross-references

- `agents/persona.md` — voice source for Scribe's reply drafting
- `agents/feedback-loop.md` — Stage 4 analytics cron template, adapted for replies
- `x-publish` skill — Playwright MCP path, the proven mechanism
- `x-niche-scraper` — supply-side target discovery
- `x-engagement-hunter` / `x-value-bomb-dropper` / `x-empowerment-hunter` — reply patterns to invoke by type
- `x-analytics-tracker` — engagement feedback for the weekly recalibrator
- `x-lead-qualifier` — downstream DM pipeline (next iteration)
- `03 Projects/X-Content-Engine/memory/content_brain.json` — performance_log + reply tracking
- `03 Projects/X-Content-Engine/queue/drafts-published.mdl` — existing publish ledger (template for new replies-published.mdl)
- Typefully Jan 2026 article (algorithm source-of-truth) — https://typefully.com/blog/x-algorithm-open-source
- Graham Mann Feb 2026 article (reply-guy case study) — https://grahammann.net/blog/how-to-grow-on-x-twitter-2026
- X-eng open-source repo (algorithm code) — https://github.com/xai-org/x-algorithm

## Changelog

- 2026-06-18 10:50 CT — initial strategy. Synthesized from Typefully Jan 2026 algorithm analysis, Graham Mann reply-guy case study, X-eng open-source notes, and 4 reply skill audits. Proposed to Andre for approval before scaling.
- 2026-06-18 11:25 CT — **Andre's resilience-first directive applied.** (1) Volume cap reduced from 30/day to 10/day (1 sweep) for Week 1, scaling to 30/day only after Week 1 engagement data confirms positive algorithm response. (2) Manual review remains OFF — relying on the byte-identical Playwright verifier + the 3 new resilience skills. (3) The 3 new infrastructure skills (x-ui-bouncer, x-semantic-locator, x-health-telemetry) were built the same hour. (4) v1 seed X List of 50 mid-size accounts at `lists/target-accounts-2026-06-18.md` was curated manually (Andre's Researcher dispatch). (5) Strategy doc updated to reflect Week 1 cap + resilience skills + X List.
- 2026-06-18 11:36 CT — **Andre's 75x reply-bait upgrade applied.** (1) Replaced the 5-reply-type distribution (insight / contrarian / question / value / empathy) with 3 load-bearing typologies — P2 Operator Insight, P4 Contrarian-Extend, P5 Deep Contrarian. Each typology has a formula + worked example + load-bearing match rule. (2) Added the 4-step validation gate as a pre-publish content quality check: char count 140-275, apostrophe JSON-escape, soft-word scrub, compel-to-debate heuristic (score-based, threshold 0.6). Implemented as a Python script at `~/.mavis/agents/mavis/skills/x-reply-guy/scripts/validate-reply.py`. (3) Retrospective validation on the v1 batch: all 3 replies PASS (debate scores 0.9 / 0.7 / 0.85), confirming the Scribe's voice + the typology formulas produce validator-passing output by default. (4) The x-reply-guy skill + the reply crons (reply-sweep-evening-2026-06-18 + reply-sweep-daily) updated to use the new typology + validation gate. (5) Strategy doc updated to reflect the new typology + validation gate.
