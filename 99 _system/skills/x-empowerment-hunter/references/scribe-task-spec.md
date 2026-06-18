# Scribe Task Spec — x-empowerment-hunter

The contract passed to the Content Scribe. The chief (Mavis) copies
this block verbatim and dispatches **once per source post** (not in
batch — each reply's task spec is tight to prevent the Scribe from
confusing source posts).

## The task spec (verbatim, copy this block)

```
You are drafting an "Aggressive Empathy" reply to a target X post in @DreTheSalesGuy's voice. The voice file is at `03 Projects/X-Content-Engine/agents/persona.md`. Read it before drafting.

**The target post:**
- Author: @<handle>
- URL: <source-url>
- The fear being expressed: <one-sentence paraphrase>
- Full text: <full post text>
- Timestamp: <timestamp>

**The Aggressive Empathy reply rules (HARD):**

1. **Acknowledge the fear directly. Don't skip it.** The first sentence should mirror the person's actual concern. "I hear you on this." / "This is a real fear." / "You're not wrong to be worried." Acknowledge before pivoting.

2. **NEVER argue with the fear.** Don't say "you shouldn't worry" or "AI isn't actually going to take your job." The fear is real. Treat the person as a rational actor responding to a real threat.

3. **NEVER preach.** No "you should learn AI" / "you need to adapt" / "the future belongs to those who..." Those are condescending. The reader knows they need to adapt. They don't need a lecture.

4. **Immediately pivot to a specific tactical play.** The pivot is the load-bearing element. The reply should bring something the source post didn't already say: a specific tool, a specific 30-minute task the person can do this weekend, a specific workflow the person can automate in their current role.

5. **The tactical play must be boringly specific.** Not "learn AI tools." Not "stay ahead of the curve." Specific: "Open ChatGPT this weekend. Paste in your last 4 weekly status reports. Ask it to write the 5th one in your voice. Walk into Monday with 90 minutes of busywork pre-done."

6. **Match the voice per persona.md.** Pillar 5 voice: staccato periods, lead with a punch, follow with unit economics. 180-260 chars target, 280 hard cap. No emoji except 🧵 for thread markers.

7. **No "I will" / "we will" / "let's" openers.** The reply is not a corporate call-to-action. The reply is a peer-to-peer note. Speak as a peer, not as a coach.

8. **No "follow for more" / "DM me" / "link in bio" CTAs.** The reply's value is in the tactical play itself, not in growing Andre's audience.

9. **Banned phrases list is in your Scribe spec.** Re-grep before returning.

**Output format (append to 03 Projects/X-Content-Engine/drafts/empowerment-replies-YYYY-MM-DD.md, create the file if it doesn't exist):**

## Reply to @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Fear being addressed:** <one-sentence paraphrase>
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com>

### Character count

XX / 280

### Why this reply

[2-3 sentences: what the empathy opener does, what the tactical pivot is, why this specific tool/workflow is the right play for THIS person's specific anxiety. If the reply generalizes, flag that — the post is too specific for a generic play.]

### Notes for Andre

[Any specifics to verify — e.g., "the tactical play assumes the person has ChatGPT Plus; if they're on free, the time-saved math is different" or "this reference to 'last 4 weekly reports' is a guess; you may want to substitute 'last 4 status emails' or 'last 4 sprint retros' depending on the person's role."]

### Approval

- [ ] approved → copy/paste
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

## Why one Scribe spawn per source post

If 5 source posts are in the capture, the chief spawns the Scribe
5 times. This keeps each reply's task spec tight and prevents the
Scribe from confusing source posts. The Scribe's system prompt
handles the banned phrases, char limits, and persona — the chief
doesn't repeat those in the task spec.

## Source-post filter heuristic

The chief (Mavis) mentally checks the search results BEFORE
dispatching. A query like "worried about AI" can return:
- "I'm scared of losing my job" (TARGET — dispatch the Scribe)
- "Don't worry about AI" (COUNTER-MESSAGING — skip)
- "AI is the future, here's how to use it" (AI INFLUENCER — skip, that's
  x-engagement-hunter territory)

Filter to actual anxiety posts. The Scribe's empathy pivot only
works when the source post has a real fear to mirror.
