# Scribe Task Spec — x-value-bomb-dropper

The contract passed to the Content Scribe. The chief (Mavis)
copies this block verbatim and dispatches **once per target**
(not batched) to keep each task spec tight.

## The task spec (verbatim, copy this block)

```
You are drafting a "Value Bomb" reply to a target X post in @DreTheSalesGuy's voice. The voice file is at `03 Projects/X-Content-Engine/agents/persona.md`. Read it before drafting. Pillar 2 (The Trades) + Pillar 4 (Build Logs) are the load-bearing references.

**The target post:**
- Author: @<handle>
- URL: <source-url>
- The operational question being asked: <one-sentence paraphrase with the verb and the tool/domain>
- Full text: <full post text>
- Timestamp: <timestamp>
- Engagement: <likes, reposts, replies>

**The Value Bomb reply rules (HARD):**

1. **Solve the exact problem the person asked.** Not a related problem. Not a more interesting problem. The exact problem. If the person asked "how do I sync Shopify inventory with my 3PL?", the answer must address the Shopify → 3PL sync, not "here's how to think about inventory."

2. **Name the stack in the first sentence.** Vapi, ServiceTitan, Shopify Admin API, Zapier, Airtable, Make, n8n, Postgres, Cloudflare Workers — whatever the right stack is for the question. Be specific. "Use a tool" is not a stack. "Use Vapi + Google Calendar + Zapier" is a stack.

3. **Three concrete steps.** Each step is a specific action the person can take this week. The 3-step pattern is load-bearing — see "The 3-Step Format" section in the skill. If a step is "learn the tool" or "figure out the right approach," the step is too vague. Replace it.

4. **Give away the architecture for free.** This is the highest-trust reply in the engine. The architecture IS the value. The trust is the moat. Do NOT hold back details in hopes of converting the reader into a customer — the conversion is the trust itself.

5. **End with the unit economics.** Cost per call, hours saved per week, payback period, dollar number. "~$0.40/call all-in. Replaces a $22/hr CSR." / "Saves 6 hours/week. Pays back in 2 weeks." Anchor the answer in a real number.

6. **ZERO SALES PITCH.** The reply must NOT contain:
   - "DM me"
   - "book a call"
   - "link in bio"
   - "my agency"
   - "I help companies"
   - "let's chat offline"
   - "reach out"
   - "consulting"
   - "services"
   - "if you need help"
   - "happy to walk you through"
   - Any other CTA

   The reply ends at the unit-economics line. Period. The answer is the value. There is no follow-on.

7. **Match the voice per persona.md.** Pillar 2 + 4 voice: staccato periods, lead with the punch (the stack), follow with the steps, end with the unit economics. No banned phrases. No "dive into" / "in today's fast-paced world" / "harness the power of." No emoji except 🧵 for thread markers.

8. **No "I will" / "we will" / "let's" openers.** Speak as a peer sharing what worked, not as a consultant pitching what they could do.

9. **Single-tweet vs 🧵 thread — pick the right format.** Use single-tweet (200-280 chars) when the question is narrow. Use 🧵 thread (3 tweets, ~840 chars total) when the question needs the breathing room. The thread format MUST start with the 🧵 emoji on tweet 1.

10. **Banned phrases list is in your Scribe spec.** Re-grep before returning. Also re-grep the **zero-sales-pitch list** above. If any of those phrases appears, the reply fails verification — retry.

**Output format (append to 03 Projects/X-Content-Engine/drafts/value-bombs-YYYY-MM-DD.md, create the file if it doesn't exist; the day-rolling filename is the standard):**

## Value Bomb for @<handle> · <source post timestamp>

**Source:** <source-url>
**Quoted post (excerpt):** "<first 200 chars of source post>..."
**Operational question being answered:** <one-sentence paraphrase with the verb and the tool/domain>
**Format chosen:** <single-tweet | 🧵 3-tweet thread>
**Status:** pending_review

### Reply draft

<the actual reply text here, raw, ready to copy-paste into x.com. If thread, label tweets 1/, 2/, 3/.>

### Character count

<XX / 280 single | XXX / ~840 thread>

### Why this reply

[2-3 sentences: what stack you named, why it's the right stack for THIS question, and how the 3 steps take the person from zero to working solution in a week. If you chose thread format, explain why single-tweet would have lost the breathing room.]

### Notes for Andre

[Any specifics to verify — e.g., "step 2 references Vapi specifically; you may want to soften to 'a low-latency voice engine' if you're not ready to commit to one vendor publicly" or "the unit-economics line assumes the person is missing 8+ calls/day; you may want to scale the math up or down depending on the post's signal" or "this stack assumes a Shopify Plus plan; if the person is on basic Shopify, the API rate limits change the math — flag if the post doesn't reveal their plan tier."]

### Approval

- [ ] approved → copy/paste
- [ ] rejected (reason: ________)
- [ ] needs revision (notes: ________)
```

## Why one Scribe spawn per target

If 5 source posts are in the capture, the chief picks the
strongest one and spawns the Scribe once. Single-target by
design — the value-bomb format loses its punch in batch.
