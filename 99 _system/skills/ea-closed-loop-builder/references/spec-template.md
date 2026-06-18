# Spec Template — ea-closed-loop-builder

The full markdown template. Copy this for every new closed-loop
spec. Replace the bracketed placeholders.

```markdown
# Closed-Loop Spec: [loop name]

**Owner:** Mavis (EA) | [or: worker name]
**Created:** [date]
**Cadence:** [cron / one-shot / on-demand]
**Cost ceiling:** [tokens, time, money per run]
**Verdict on first run:** [PASS / WARN / FAIL with one-line reason]

---

## 1. GOAL

[The outcome the loop produces — one sentence]

[The user-visible deliverable — where it lands, who reads it]

[The success criterion — what evidence = done]

---

## 2. CONTEXT

**VISION:** [link to VISION.md or quote the key sentence]

**ARCHITECTURE:** [link to ARCHITECTURE.md or summarize the structure]

**RULES:** [link to RULES.md or list the hard constraints]

---

## 3. ACTION

1. [step with input + output]
2. [step with input + output]
3. [step with input + output]
4. ...

[Minimum data the loop needs: file paths, env vars, API endpoints]

---

## 4. FEEDBACK

- **Verifier:** [who/what — different model, different agent, script, human, benchmark]
- **Evidence:** [what counts as verified — file on disk, exit code 0, test passing, human thumbs-up]
- **Frequency:** [every run / every N / sample]
- **On FAIL:** [retry / escalate / halt]

---

## 5. STOP CONDITION

- **Trigger:** [what tells the loop it's done]
- **Cleanup:** [state to leave behind when the loop ends]
- **Escalation:** [what happens if cost ceiling hit or stop condition can't be met]
```

## Spec path

`03 Projects/Mavis EA Design/loops/<loop-name>-spec.md` — Mavis
EA's loop library.

For project-specific loops:
`03 Projects/<project>/loops/<loop-name>-spec.md`.

## Spec filename conventions

- `kebab-case-spec.md` (the name is the loop's identity)
- Versioned on major changes: `<loop-name>-v2-spec.md`
- Archived specs: `<loop-name>-archived-<date>.md`

The library is the audit trail. Future Mavis sessions can read
existing specs before designing a new loop.
