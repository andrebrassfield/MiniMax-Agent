---
id: i-2026-06-02-009
type: instinct
title: "Pytest: namespace Skill Pack action modules per-slug"
created: 2026-06-02
confidence: 0.70
cluster: tools
trigger_context: "When a Skill Pack's action.py needs to be imported or pytest-collected alongside other Skill Packs in the same parent directory"
evidence_source: "Operation Chimera, 2026-06-02 (3 Skill Packs refactored)"
tags: [tools, pytest, python, skill-packs, module-shadowing, namespaces]
---

# Pytest: namespace Skill Pack action modules per-slug

When multiple Skill Packs live in `99 _system/skillopt/skills/<name>/` and each has an `action.py`, all the `action.py` files share the same leaf module name. Python's import system + pytest's collection will shadow or collide on this — the last `action.py` to be discovered wins, and `import action` is ambiguous. The fix is to namespace the module per-skill: `<skill_slug>_action.py` (e.g., `daily_brief_action.py`, `deep_research_action.py`, `weekly_connections_action.py`). The `process-inbox` pack is the legacy exception — it predates the Esalen Skill Pack anatomy and still uses `action.py`. New Skill Packs must use `<slug>_action.py`.

## Trigger

When authoring or refactoring a Skill Pack's Python action module that lives in `99 _system/skillopt/skills/<name>/`. Also fires when a Skill Pack needs to be import-tested in isolation (the namespaced module name makes the import path unambiguous).

## Evidence

Operation Chimera, 2026-06-02. The 3 refactored Skill Packs (daily-brief, deep-research, weekly-connections) were each given a per-skill namespaced action module (`daily_brief_action.py`, `deep_research_action.py`, `weekly_connections_action.py`) instead of the legacy `action.py`. The Resolver MCP's `discover_skills()` function explicitly looks for both patterns (`action.py` legacy OR `*_action.py` namespaced) and treats the namespaced version as the canonical one:

```python
# resolver.py L143-146
has_action=(
    (pack_dir / "action.py").exists()
    or any(p.name.endswith("_action.py") for p in pack_dir.glob("*_action.py"))
),
```

This dual-detection is the migration shim: legacy `action.py` still works (process-inbox trailblazer), but new packs get the namespaced name from day one. The Resolver also uses the action module's *name* (not just its presence) when wiring up the dispatch table, so namespacing is the source-of-truth going forward.

## Counter-evidence

A counter-instinct would arise if a session authored a new Skill Pack using the namespaced name and pytest collection still collided (e.g., two packs picked the same `<slug>`). Today's observation is one-sided: only the namespaced pattern was used, only the legacy pattern is the trailblazer. Bump confidence after 2+ Skill Packs have shipped with the namespaced pattern and one of them has had to import another's module without collision.
