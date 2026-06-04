---
type: instinct
id: 2026-06-03-001
status: active
confidence: 0.90
created: 2026-06-03
captured_session: "Operation Heartbeat — codifying the smoke-test discipline"
trigger: "Any change to glass_server.py OR any template under 99 _system/mcps/glass-server/templates/"
---

# HTML render-and-curl verification is required for any Glass server change

## The rule

After editing `glass_server.py` or any file in `99 _system/mcps/glass-server/templates/`, before the `git commit`:

1. Start the server in the background (use `start.sh --port <free>` or `nohup ... &`).
2. `curl -sI http://localhost:<port>/<route>` for every route touched by the change. Expect `HTTP/1.x 200`.
3. `curl -s http://localhost:<port>/<route> | grep -c <expected-content-fragment>` to confirm the rendered HTML contains the expected sections, not just the right status code.
4. Kill the server (`pkill -f glass_server.py`).
5. Only then run `git commit`.

## Why

A passing `python3 -m py_compile` or a clean `ast.parse` only proves the file **parses**. It does not prove the file **works at runtime**. The four bugs caught during the Operation Glass Fleet rollout (2026-06-03) all parsed cleanly:

- Missing `markdown` dep → the system Python had no `markdown` module, so the server couldn't even start.
- Module-name shadowing: a local variable `html` shadowed `import html`, so every `html.escape(...)` call inside an f-string failed at runtime with `UnboundLocalError`.
- Tuple-unpacking drift: a return signature changed from `(html, dict, int)` to `(html, int, int)` but the caller still did `_d.get("total", 0)` on the int.
- Dossier counting: a check `d.is_dir()` only counted subdirectories, but the Researcher and Verifier keep dossiers as top-level `.md` files (not subdirectories).

All four would have been caught by one `curl /` round-trip. The lesson: **parse ≠ work**.

## When to relax

- If the change is documentation-only (comment edits, docstring fixes) → no smoke test needed.
- If the change is purely a CSS tweak in `theme/glass.css` → the page won't 500, but a 1-second `curl /` is still cheap insurance.
- If the server is already running for another reason → `curl` is essentially free.

## Automation

`99 _system/mcps/glass-server/smoke_test.py` automates the full cycle (start, curl, check, kill, report). Run it before any Glass server commit.

## Hard-stop interpretation

If `smoke_test.py` returns non-zero exit code, the commit is **blocked**. Do not pass `--no-verify` or otherwise override. The smoke test IS the verification.

## Reference

Captured from the 2026-06-03 19:14 CT Andre message ("the main page is still there and looks like shit i thought you replaced that") and the subsequent diagnostic that found the four bugs above. The user explicitly asked for this rule to be "codified" rather than left to conversational memory.
