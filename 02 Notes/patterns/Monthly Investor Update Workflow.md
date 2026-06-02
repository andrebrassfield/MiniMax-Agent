---
type: capture
created: 2026-06-02T18:30:00+00:00
source: crucible-synthetic
category: workflow
tags: [crucible, workflow, synthetic, m3-eval-lab]
---

# Monthly Investor Update Workflow

Want a workflow that produces the monthly investor update automatically. Inputs:
- The previous 30 days of git commits (grouped by repo)
- Stripe revenue (from the Stripe dashboard, or a CSV export)
- Customer support tickets (from HelpScout, or a CSV)
- Any product launches or press mentions
- A draft from the previous month's update (for tone matching)

Process:
1. Pull the data (cron job, daily)
2. On the 1st of each month, generate a draft
3. The draft should have: opening summary (3-4 sentences), financials (MRR, growth %, burn), product highlights (3-5 bullets), team update (1-2 sentences), asks (1-2)
4. Match the voice of the previous 3 monthly updates
5. Send to me for review
6. After my approval, format and send to the investor list

Constraints:
- Never auto-send. Always pause for human approval.
- Match voice but don't fabricate numbers. If a number is missing, write "[VERIFY: Stripe data]".
- Highlight wins, but include challenges. Investors hate spin.
- Length: 500-800 words.

Should this be a PatternForge generative code? Or a Skill Pack? Or both? My intuition: PatternForge (for the generative code) + a Skill Pack (for the actual email send, which is YELLOW-tier).
