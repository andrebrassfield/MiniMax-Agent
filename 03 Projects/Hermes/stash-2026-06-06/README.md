# Hermes — pre-clean-slate archive (2026-06-06)

Created 2026-06-06 11:38 CT during the "clean slate" reset of `~/.hermes/hermes-agent/`.

## Why this directory exists

The local `hermes-agent` checkout at `~/.hermes/hermes-agent/` was on
`feat/cron-until-done` (8 commits ahead of the user's fork, 11 commits
ahead of `origin/main`, 333 commits behind upstream main, and even more
behind after v0.16.0 dropped the same day). Updates were no-ops because
of a bug in `hermes update` (it pulls main then switches back to the
user's feature branch without rebasing) compounded by a TUI bug (banner
measures `HEAD..origin/main` regardless of which branch is checked out).

Andre asked for a clean slate on `git@github.com:andrebrassfield/hermes-agent.git`
to stop having to fix Hermes daily. Everything from the old local state
that might be useful later is archived here.

## Contents

### `stash-tracked.patch` (27 KB)
The **tracked-file modifications** from the autostash
`hermes-update-autostash-2026-06-06-162438` (index portion). Modifications
to existing files like `agent/agent_init.py`, `agent/auxiliary_client.py`,
`agent/conversation_loop.py`, `agent/cost_routing.py`, `agent/prompt_builder.py`,
`agent/system_prompt.py`, `check_langgraph.py`, `cron/scheduler.py`,
`hermes_cli/config.py`, `hermes_cli/kanban_db.py`, `hermes_cli/main.py`,
`run_agent.py`, `tests/hermes_cli/test_kanban_db.py`, plus 3 JSON files
in `outbox/`, plus markdown notes `phase1_comparison.md`, `phase1_run_log.md`.

### `stash-untracked.patch` (85 KB)
The **untracked-file additions** from the autostash (untracked portion).
New files that were stashed and never re-applied: `apps/research_analyst/`
(full new module: `__init__.py`, `research_graph.py`, `run.py`, `state.py`,
`sub_agents.py`), `mini_harness/` (full new module), `phase1_claude_sdk/`
(CLAUDE.md + briefing agent + hook + skill), and tests for research_analyst.

### `carried-commits/` (11 patches)
The 11 commits that were on `feat/cron-until-done` ahead of
`1927ff217e6b886bedf6428c3798795968916031` (the merge-base with
`origin/main`):

| #  | Commit (short) | Subject |
|----|----------------|---------|
| 01 | 8dc0b42a1 | fix(profiles): allow dots in profile ids |
| 02 | bb2458b21 | feat(cron): add until_done work-based loop primitive |
| 03 | 5dc6a3a68 | test(cron): add hermetic pytest coverage for until_done primitive |
| 04 | 49f39b129 | deps: add langgraph, langchain-core, langgraph-checkpoint-postgres, langsmith, asyncpg, psycopg-binary |
| 05 | b55eac407 | feat(agent/langgraph): package skeleton with graph_builder, checkpointer, hitl, time_travel, middleware, budget |
| 06 | 4e533667f | test(agent/langgraph): tests for HermesPostgresSaver config resolution and factory |
| 07 | 5b9900bb1 | feat(observability): add langsmith_relay plugin for graph run tracing |
| 08 | a6f6bb6de | feat(langgraph): DollarBudget class + tests |
| 09 | f656d0bbc | feat(langgraph): HITLInterrupt class + tests |
| 10 | 2070eae36 | feat(langgraph): TimeTravelController class + tests |
| 11 | 859ddb5c6 | feat(langgraph): MiddlewareRegistry class + tests |

To re-apply later (in order): `git am carried-commits/*.patch`

## What was NOT preserved

- `hermes.db` and `memory.db` (SQLite runtime state, regenerable)
- `__pycache__/`, `.ruff_cache/`, `.pytest_cache/` (build artifacts)
- `.pyc`, `.wasm`, `.map` files (build artifacts)
- The venv at `~/.hermes/hermes-agent/venv/` (regenerated on re-install)

These were either regenerable runtime state or build artifacts.

## Recovery

If anything in here needs to come back:

```bash
# Re-apply stashed modifications
cd ~/.hermes/hermes-agent   # the new clean checkout
git apply /Users/brassfieldventuresllc/MiniMax-Agent/03\ Projects/Hermes/stash-2026-06-06/stash-tracked.patch
git apply /Users/brassfieldventuresllc/MiniMax-Agent/03\ Projects/Hermes/stash-2026-06-06/stash-untracked.patch

# Re-apply carried commits
git checkout -b feat/cron-until-done-recovered
git am /Users/brassfieldventuresllc/MiniMax-Agent/03\ Projects/Hermes/stash-2026-06-06/carried-commits/*.patch
```

## What was the actual fix?

The local state was fine. The bug was in Hermes Agent itself:

1. `hermes_cli/banner.py::_check_via_local_git` measures
   `HEAD..origin/main` regardless of which branch is checked out.
2. `hermes_cli/main.py::_cmd_update_impl` pulls main then switches
   back to the user's feature branch without rebasing.

Both bugs still exist in upstream v0.16.0. A clean local slate removes
the symptom (the carried branch is gone, TUI measures 0) but does NOT
fix the root cause for anyone else on a feature branch. The upstream
PR prep is tracked as a separate follow-up.
