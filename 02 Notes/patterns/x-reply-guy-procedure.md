---
description: "The 5-phase x-reply-guy procedure — Hunt (graphql-interceptor), Rank (scoring formula), Draft (ammunition + Scribe + 3 typologies), Publish (4-step validation gate + Playwright path), Track (3-destination logging). Load when the skill is invoked. Moved from SKILL.md inline content 2026-06-22."
---

# x-reply-guy — The 5-phase Procedure

## Phase 1: Hunt (target discovery) — the GraphQL interceptor

**Architecture (2026-06-18 19:09 HALT fix):** The gate is in the shell script, not the LLM. The cron calls `scripts/mavis-sweep.sh` which runs:

1. **Stage 1: Session check** via Playwright MCP (`mavis-session-check.py`). MCP is the source of truth — no CDP port discovery needed (replaced `guard.py` which had a `find_cdp_port()` bug that filtered out Playwright MCP's dynamic port 0).
2. **Stage 2: Pre-sweep telemetry** — currently SKIP (x-health-telemetry has no script yet; LLM does this via Playwright MCP after the verdict is read).
3. **Stage 3: GraphQL interceptor** (`intercept.py`, single-page contract — ONE page reused across all targets).
4. **Stage 4: Write verdict** to `/tmp/x-sweep-verdict.json`. Exit 0 (proceed) or 1 (halt). Verdict is on-disk binary — no bypass path.

```bash
~/.mavis/agents/mavis/skills/x-reply-guy/scripts/mavis-sweep.sh
cat /tmp/x-sweep-verdict.json  # trust the verdict, do NOT bypass
```

**Why interceptor over scraper for the velocity window:**
- DOM scraping takes 3-5 sec per profile; interceptor <1 sec
- Interceptor uses page's existing authenticated session — no anti-bot triggers
- Interceptor gets exact Unix timestamp + exact view count (not DOM-rounded)

**Fallback:** if interceptor unavailable (CDP down), use x-niche-scraper or MCP-based search fallback.

Pool: top 30 by engagement velocity (likes + replies weighted 1:5 per the 75x reply-weight signal).

Filter (in addition to interceptor's age filter):
- Skip accounts in target tier D (500K+) unless trending
- Skip muted-keyword patterns (the 8 from persona's persona.md)
- Skip Dre's own posts
- Apply view_count floor (e.g., > 100) if needed for niche quality

## Phase 2: Rank

Score: `(target_account_tier × 3) + (engagement_velocity_score × 2) + (niche_fit × 4) + (recency_bonus × 2)`

- target_account_tier: A=5, B=3, C=2, D=1
- engagement_velocity_score: replies_in_first_30min × 5 + likes_in_first_30min
- niche_fit: 1-5 based on @DreTheSalesGuy persona pillars overlap
- recency_bonus: 5 if <30min, 3 if 30-60min, 1 if 60-120min

Pick top N (= sweep_size, default 10).

## Phase 3: Draft (Scribe dispatch)

### Phase 3.0: Ammunition lookup (chief runs before Scribe dispatch)

```bash
AMMO=$(python3 ~/.mavis/agents/mavis/skills/x-reply-guy/scripts/ammunition_lookup.py \
  --ledger "$VAULT/03 Projects/X-Content-Engine/ammunition.mdl" \
  --post-text "$TARGET_POST_TEXT" \
  --typology "$CHOSEN_TYPOLOGY_CODE" \
  --n 2 --show-path)
```

`--typology` accepts both ledger code (`P2-Operator`) and full name. Script outputs sampling path + 0-2 ledger lines. Fallback path (`most-recent-fallback`) means no topic match — use most-recent entries as "evidence ladder." If ledger empty: pass "(none — ledger empty)" to Scribe. Do NOT block Scribe dispatch on ammo absence.

### Phase 3.1: Scribe dispatch

```bash
mavis communication send --from <chief> --to <chief> --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

Task spec contains:
- Target post URL + author handle + full post text
- Reply typology hint (P2/P4/P5 — see typologies vault file)
- Ammunition (1-2 ledger entries formatted as `[date] | [topic] | [typology] | [metric] | [url]`)
- Persona path: `03 Projects/X-Content-Engine/agents/persona.md`
- Output path: `03 Projects/X-Content-Engine/drafts/replies-YYYY-MM-DD-HHMM.md`

## Phase 4: Publish (4-step validation gate + Playwright MCP)

### Pre-publish validation gate (4 checks, programmatic)

```bash
python3 ~/.mavis/agents/mavis/skills/x-reply-guy/scripts/validate-reply.py "<reply text>"
```

1. **Char count strictly 140-275.** Outside → re-dispatch Scribe with trim/expand prompt.
2. **Apostrophe detection.** If present, use `escaped_version` (JSON-escaped) in Playwright `browser_type` — prevents serialization failure that caused v2 duplication bug.
3. **Soft-word scrub.** Flag Important/Interesting/Amazing/Revolutionary with replace recommendations.
4. **Compel-to-debate heuristic.** Score-based (specific number + technical term + staccato + ends-with-declarative). Threshold 0.6. Below → re-dispatch.

If gate FAILS, re-dispatch Scribe once with fixes. If 2nd Scribe also fails → HALT.

### Publish steps

1. `browser_navigate '{"url":"<target_post_url>"}'`
2. Wait 3-5s
3. `browser_snapshot '{}'` → find `textbox "Post text"` ref
4. `browser_type '{"element":"Reply textbox","ref":"<ref>","text":"<validated>","submit":false}'` (use JSON-escaped version if gate produced one)
5. `browser_evaluate` verify byte-identical content, no duplication
6. **DUPLICATION GUARD:** if staged text contains load-bearing phrase twice → HALT
7. **LENGTH CHECK:** programmatic `len()`. Wildly different → HALT
8. `browser_snapshot` → find Reply button ref
9. `browser_click '{"element":"Reply button","ref":"<ref>"}'`
10. Wait 2s
11. `browser_evaluate` to find just-posted reply URL
12. If URL not found, wait 2s + retry once. Still missing → screenshot + HALT

Loop: phases 1-4 sequential. Each reply ~3-4 min. 10-reply sweep ~30-40 min total.

## Phase 5: Track (3-destination logging)

For each published reply:

1. **Append to `03 Projects/X-Content-Engine/queue/replies-published.mdl`:**
   ```
   - YYYY-MM-DD HH:MM CT — reply to @<target> (target_post: <url>) → <reply_url> | <reply_type> | <pillar> | <target_tier>
   ```

2. **Append to `03 Projects/X-Content-Engine/memory/content_brain.json` `performance_log`:**
   ```json
   {
     "post_id": "<reply_url>",
     "type": "reply",
     "hook_used": "<first 80 chars>",
     "views": 0, "likes": 0, "retweets": 0, "replies": 0,
     "date": "YYYY-MM-DD",
     "publish_time": "HH:MM CT",
     "pillar": "P?",
     "reply_type": "insight|contrarian|question|value|empathy",
     "target_post_id": "<url>",
     "target_author_handle": "@<handle>",
     "target_account_tier": "A|B|C|D",
     "target_engagement_at_publish": "<snapshot>",
     "target_text_excerpt": "<first 200 chars>",
     "_note": "<1-line context>"
   }
   ```
   Atomic write: temp + fsync + rename.

3. **Append to `03 Projects/X-Content-Engine/drafts/_ledger.mdl`:**
   ```
   - YYYY-MM-DD HH:MM CT — reply-guy sweep complete: N replies shipped, M halts, <N-M> in queue/replies-published.mdl
   ```

## Cron schedule

| Cron | Schedule (CT) | Job |
|---|---|---|
| `reply-sweep-morning` | 0 8 * * * | 10-reply morning sweep |
| `reply-sweep-midday` | 0 13 * * * | 10-reply midday sweep |
| `reply-sweep-evening` | 0 19 * * * | 10-reply evening sweep |
| `reply-engagement-tracker` | 0 9 * * * | Pull T+24h metrics on yesterday's replies |
| `reply-recalibrator-weekly` | 0 17 * * 0 (Sun 17:00) | Weekly recalibration from engagement data |

## First batch proof (2026-06-18 10:55 CT)

3 replies shipped clean via Playwright reply path:
- @michaelheredia (P2 HVAC AI, **P2 Operator Insight**) → 2067637331520111070
- @spandan_madan (P4 Claude Code, **P4 Contrarian-Extend**, 510K-view post) → 2067637840058470606
- @svpino (P5 AI vulns, **P5 Deep Contrarian**) → 2067638115041153121

**Validation gate results:** Reply 1 (debate 0.9), Reply 2 (debate 0.7), Reply 3 (debate 0.85) — all PASS.
