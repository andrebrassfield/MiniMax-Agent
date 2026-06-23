# Reaction Discipline — `02 Notes/articles/`

The rule that makes a source note different from a highlight. Per the 2026-06-22 Path A spec, the second-self automation layer enforces this discipline via the `second-self-morning-brief` cron (Step 1.5).

## The rule

**Every note in `02 Notes/articles/` must have a `## Reaction` section.** No exceptions.

## What a Reaction is

A Reaction is **what Andre thinks about what the source said.** Not a summary. Not a paraphrase. Andre's voice on the source — the assessment, the friction, the agreement-with-caveat, the disagreement, the "this changes nothing for me" honest take.

**Structure:**
```markdown
## Reaction

<2-5 sentences in Andre's voice. Cite the specific claim or quote from the source that triggered the reaction.>

<!-- Optional: -->
- **What I'm taking from this:** <the actionable takeaway>
- **What I'm rejecting:** <the part that doesn't apply or is wrong>
- **What I'm sitting with:** <the open question this raised>
```

## What a Reaction is NOT

- NOT a summary of the source. The summary is the rest of the note (or the highlights). The Reaction is your reaction.
- NOT "this is interesting." That's not a reaction — that's a bookmark.
- NOT empty. "Looks good" or "Save for later" or just a link to the source — none of these count.
- NOT a quote from the source. If the Reaction is just a pull-quote, the source has no Andre in it yet.

## Why this rule exists

The article ("Everyone Is Building a Second Brain...") is explicit:

> "Most Obsidian vaults are full of what other people said. Highlights from articles. Excerpts from papers. Saved quotes. Bookmarked ideas. A second self needs to be full of what you think about what other people said."

Without the Reaction, the source note is a highlight reel — anyone could have written it. With the Reaction, the note becomes Andre's voice on the source. That's the difference between second brain and second self.

## How the rule is enforced

The `second-self-morning-brief` cron (06:00 CT daily) runs Step 1.5:

```bash
for f in $(find ~/MiniMax-Agent/02\ Notes/articles -type f -name "*.md" -mtime -7); do
  if ! grep -qE "^## (Reaction|My Reaction|Reactions|My Take|My Reading)" "$f"; then
    mv "$f" ~/MiniMax-Agent/00\ Inbox/
    echo "$(date): moved $f to Inbox (missing reaction)" >> ~/.mavis/state/reaction-discipline.log
  fi
done
```

**What happens when a note is moved:**
- It's moved to `00 Inbox/` with its current content intact
- The morning brief surfaces it in the "Best Capture" section ("re-process these for the reaction discipline")
- Next-Mavis reads it, writes the Reaction, and moves it back to `02 Notes/articles/`

## Migration rule for existing notes

Existing notes in `02 Notes/articles/` (created before 2026-06-22) are grandfathered — they won't be auto-moved. But the next time one is touched (modified after 2026-06-22), it must have a Reaction or it gets moved on the next morning brief run.

To grandfather-clear existing notes all at once:
1. Read each note
2. Add a `## Reaction` section (even if it's just "Re-reading this in light of <current context>. <2-3 sentences>.")
3. The discipline is forward-looking — the new norm applies to new and modified notes

## What if a source genuinely doesn't deserve a Reaction?

Move it to `00 Inbox/`. If it sits there unprocessed for 30 days, archive it to `05 Archive/`. The vault doesn't need every source — it needs the sources Andre has actually engaged with.

## Audit

Every Sunday after `second-self-weekly-deep` runs, the weekly deep session includes a Reaction-discipline summary:

> **Reaction discipline:** <N> articles in `02 Notes/articles/`, <M> have Reactions, <K> missing (moved to Inbox this week).

If K > 0 for 3 consecutive weeks: the cron is moving notes faster than Andre is writing reactions. Either Andre needs to engage, or the discipline threshold needs adjustment (move from 7d window to 14d).

## Cross-references

- Cron that enforces: `~/.mavis/agents/mavis/crons/second-self-morning-brief.md` (Step 1.5)
- Spec that introduced this: `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md`
- Source article: Khairallah, "Everyone Is Building a Second Brain. The People Winning Are Building a Second Self." (2026-06-22)
- Log file: `~/.mavis/state/reaction-discipline.log`
