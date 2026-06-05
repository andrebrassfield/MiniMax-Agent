---
description: Workarounds for tool-specific bugs and gotchas — Obsidian Templater syntax, Python str.format() with braces, concurrent CLI worker output. Load when writing Templater templates, formatting LLM prompts with .format(), or running concurrent workers that print to stdout.
---

# Tool Quirks

## Templater template authoring — Write tool renders syntax (2026-06-01)
When writing Obsidian Templater template files (.md) via the Write tool, the `<% tp.date.now("YYYY-MM-DD") %>` and `<% tp.file.title %>` syntax gets RENDERED to static text. The file ends up with `created: 2026-06-01` (current date) and `# idea` (static title) instead of dynamic template variables. Result: the template becomes dead — it does not auto-fill on new-note creation.

**Workaround**: use bash heredoc with a quoted delimiter:
```bash
cat > file.md << 'TEMPLATE_EOF'
...content with <% tp.* %>...
TEMPLATE_EOF
```
The single-quoted delimiter disables variable expansion, preserving text literally. The Edit tool's exact-string replacement also works (does not render template syntax).

**Verified 2026-06-01**: wrote 4 new templates (idea.md, pattern.md, question.md, number.md) via Write tool — all had static dates and titles. Rewrote via heredoc — all 9 expected `<% tp.* %>` occurrences intact. Title line confirmed at correct position in each file.

**Affected**: any future template file in `99 _system/templates/` or anywhere with Templater syntax. Always use heredoc or Edit, never Write, for these files.

## Python .format() with braces in LLM prompt templates (2026-06-02)
When using `str.format()` to render an LLM prompt template, escape literal `{` and `}` as `{{` and `}}` in the FORMAT STRING. User-supplied content (the Mavis output, the example JSON) is passed as VALUES, not as format specifiers — `{}` chars in values are inserted as-is and don't break formatting.

**Example bug** (hit in evaluator.py v0.2.0): the prompt template had:
```python
"expected_score_format": "say \"publish\" or \"go\" and I will run..."
```
where `"publish"` and `"go"` were literal text. The .format() call interpreted them as field references and threw `KeyError: '"publish"'` or similar.

**Fix**: either escape the inner quotes OR rephrase to avoid the inner braces (`say publish or go and I will run...` is cleaner and avoids the issue entirely).

**Rule of thumb**: in the format string, every `{` that's NOT a field reference should be `{{`. In the values, no escaping needed — strings are inserted verbatim. When in doubt, write a test that passes user content with literal `{}` chars to confirm no breakage.

## Concurrent CLI output: one self-contained line per worker (2026-06-02)
When running N workers in a thread pool that all print to stdout, do NOT use the `print(..., end="", flush=True)` "header" pattern followed by a later `print(result)` "body" follow-up. With concurrent execution, the headers pile up on stdout before any body can print, producing interleaved garbage like:
```
  [1/25] foo...  [3/25] bar...  [2/25] baz...  DRY-RUN
 DRY-RUN
```

**Correct pattern**: one self-contained line per worker, printed at completion. Hold the `print_lock` for the entire `print(...)` call so the line is atomic:
```python
with print_lock:
    print(f"  [{n}/{total}] {item_id} ({category}) — "
          f"{pass_str} (score={score_str}, {duration_ms}ms)")
```

**Atomicity is what matters.** The print_lock prevents byte-level interleaving; the single self-contained line prevents the "header without body" race where one thread's header lands before another thread's body.

Hit this twice in the SOUL compliance evaluator v0.3.0 refactor: first attempt with `end=""` headers, garbled output. Fix to single-line pattern, clean output.

## Team plan decision JSON requires arrays + plan_complete (2026-06-04)
`mavis team plan decision <plan_id> --file <path>` rejects decisions where `last_cycle` and `next_cycle` are objects. The error is `last_cycle: Expected array, received object` / `next_cycle: Expected array, received object` / `plan_complete: Required`. Both fields must be ARRAYS of task-decision objects, and `plan_complete` is a required boolean at the top level (not inside either array).

**Working skeleton**:
```json
{
  "last_cycle": [
    { "task_id": "step-N", "verdict": "accept", "reason": "..." }
  ],
  "next_cycle": [],
  "plan_complete": false,
  "message_to_user": "Step N accepted. ..."
}
```

The mavis-team skill shows the schema in prose, but the YAML examples use bare object form for these fields and the CLI parser is strict. Easy first-time mistake. Verified 2026-06-04: cycle 1 decision failed on object form, succeeded on array form.

`verdict` values: `accept` (done) | `reject` (retry, keep same task_id) | `override_accept` (accept despite verifier) | `manual_retry` (retry with explicit correction in reason). For accept-only decisions, `next_cycle: []` and `plan_complete: false` until the last cycle.
