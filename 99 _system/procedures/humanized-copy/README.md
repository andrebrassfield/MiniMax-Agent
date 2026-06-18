# humanized-copy procedure.json

> Mavis-procedural (compiled, planned) for the skill_polish step; frontier for the human_last_pass review. Adapted from the Machina tweet (Gary Provost principles) on 2026-06-04.

## Status

**v0.1.0-draft** — first articulation. The skill_polish step is 3B territory when compiled (Qwen 2.5-3B per the article's spec). The human_last_pass stays on Andre (or whoever owns the voice).

## What's in the file

- **system_prompt** — who Mavis-humanized-copy is, and the load-bearing distinction: the polish is FORM, not VOICE
- **3-node flow**:
  - `brain_dump` — receive the human's bullets/fragments
  - `skill_polish` — apply Provost's principles (sentence length variation, rhythm, pacing, structure) to produce a draft
  - `human_last_pass` — the human reviews, makes the voice their own, ships
- **3 routing-out paths**: `routed_to_judgment` (not a copy request, route to Mavis-judgment), `blocked_on_human_input` (brain dump too sparse), `voice_leak_detected` (AI voice leaked in)
- **5 scenario variables** — platform (LinkedIn, X, blog, email, script), length target, register, voice anchor loaded, audience
- **5 warnings** (severity: high) — voice-leak failure mode, no-facts-not-in-brain-dump, sentence-length-variation required, paragraph-break-at-emotional-pivots, human-last-pass-is-non-negotiable
- **eval_set_planned** — 50 conversations, 80/20 train/eval, 6 held-out criteria

## Provost's principles encoded

The 5 high-severity warnings ARE Provost's principles translated to flowchart rules:

1. **Sentence length variation** — short, short, long, or long, short, medium. NOT all-same-length. This is Provost's core.
2. **Paragraph break at emotional pivots** — not at word counts.
3. **Pacing via fragments and detail** — speed up with fragments, slow down with detail.
4. **Rhythm via cadence** — short sentences followed by longer ones, the breath pattern.
5. **Voice in rhythm, not vocabulary** — the writer's voice is in how the sentences move, not in word choice. This is the discipline that lets the polish produce form without leaking AI voice.

## The voice-leak gate

The `voice_leak_check` node is the load-bearing gate. It reads the polished draft and checks for AI-voice tells:
- Overly symmetric sentence structures
- Marketing language ('revolutionary', 'game-changing', 'historic')
- Paragraphs that all start the same way
- Perfect grammar in informal contexts
- 'Enabling' verb stacks ('leveraging synergies to deliver outcomes')

If the check finds AI voice, the polish routes to `voice_leak_detected` with specific tells. If clean, the polish routes to `polished` and the human's last pass is the gate that makes the piece land as the human, not Mavis.

## Why this is compilable (and the daily-brief's compilation target)

The skill_polish step IS flowchart-able. The compile target:
- 200-600 conversations (per the article's spec, scaled down for v0.1)
- Generate.py walks the flowchart with a frontier model (Claude Sonnet 4.5)
- Fine-tune a Qwen 2.5-3B model on the resulting textbook
- Self-host on a rented GPU (~$2.50/hour for an A100)
- Recompile cycle: 30-50 min on contract change

The human_last_pass is NOT compilable — it requires the human's voice, which is the load-bearing thing the polish cannot produce.

## First use case

The LinkedIn cross-post of the `mavis-companion-piece.md`. Workflow:
1. Andre brain-dumps the LinkedIn-specific framing points (more hook-driven, less philosophical, "here's what I've been thinking")
2. Skill polish applies Provost's discipline, returns a draft
3. Andre's last pass makes the LinkedIn version sound like Andre, not Mavis
4. Ship

## Related

- `daily-brief/procedure.json` — operator-mode counterpart
- `mavis-orchestrator/procedure.json` — judgment-mode counterpart (handles the design-review-class judgment workflows)
- `02 Notes/articles/mphrediction-missing-use-case.md` — the article that the mavis-companion-piece operationalizes; the LinkedIn cross-post will draw on the same source material
- `04 Resources/published/mavis-companion-piece.md` — the canonical longform piece; the LinkedIn cross-post is a derivative

---
*Staged 2026-06-04 13:00 CT, during an Andre-out autonomous session. First v0.1 of the humanized-copy procedure. Not compiled. The skill_polish step is the compilable target; the human_last_pass stays on Andre.*
