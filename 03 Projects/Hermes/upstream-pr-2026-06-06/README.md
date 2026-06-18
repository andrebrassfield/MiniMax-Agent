# Upstream Hermes PR — `fix/update-rebase-and-banner-tracking`

This directory holds the PR-ready artifacts for the bug that caused
`hermes update` to silently look like a no-op when you were on a
long-lived feature branch. The local clean-slate work around the
diagnosis (`~/MiniMax-Agent/03 Projects/Hermes/stash-2026-06-06/`)
doesn't fix the bug for anyone else — this PR does.

## Status: **PR OPEN**

- **PR #**: [#40673](https://github.com/NousResearch/hermes-agent/pull/40673)
- **State**: open, mergeable
- **Source**: `andrebrassfield:fix/update-rebase-and-banner-tracking` (in the canonical fork `andrebrassfield/hermes-agent`)
- **Target**: `NousResearch:main`
- **Commit**: `60d6f6518` (168 lines, 2 files: `hermes_cli/banner.py`, `hermes_cli/main.py`)

## Consolidation (2026-06-06, post-PR)

Two repos with the same content existed:
- `andrebrassfield/hermes-agent` (personal copy, not a real fork)
- `andrebrassfield/hermes-agent-fork` (the real fork of NousResearch)

Consolidated to a single canonical repo:
- `andrebrassfield/hermes-agent` — now the REAL fork of NousResearch
  (was renamed from `hermes-agent-fork`)
- `andrebrassfield/hermes-agent-archive` — the old personal copy,
  renamed out of the way, preserved for reference. Has the fix
  commit + 10 new upstream commits at the time of consolidation
  (commit `bb8694d66`).
- The old `-fork` repo no longer exists (it was renamed, not deleted
  — the token didn't have `delete_repo` scope).

PR #40673's head label automatically updated to point at the renamed
repo. The PR is still open, mergeable, and correctly sourced.

## What's here

- `0001-fix-update-rebase-and-banner-tracking.patch` — the patch
  against `upstream/main` (commit `d1771114e`, v0.16.0 / 2026.6.5).
  Apply with `git am 0001-*.patch` or `git apply 0001-*.patch`.
  168 lines, 2 files changed (`hermes_cli/banner.py`,
  `hermes_cli/main.py`).

## What it fixes

**Bug 1 — `hermes_cli/banner.py::_check_via_local_git` (line 147)**
The TUI banner always measured `HEAD..origin/main` regardless of
which branch was checked out. So a feature branch that was in sync
with its own `origin/feat-x` would still report "333 commits behind"
because main had moved 333 since the feature branch was forked.

**Bug 2 — `hermes_cli/main.py::_cmd_update_impl` (line 10218)**
`hermes update` pulls `main` (or `--branch=<x>`) but never switches
back to the user's original feature branch. After a successful pull
the function just returns — leaving the user on `main` with their
feature branch stale. The next TUI check then reports the same
"X commits behind" because Bug 1 measures against `origin/main`.

## The fix

1. New helper `_resolve_tracking_ref(repo_dir)` returns
   `origin/<current-branch>` for any non-main branch with an upstream
   tracking ref, `None` for `main` / detached HEAD.

2. `_check_via_local_git` uses the tracking ref when present,
   falling back to `origin/main` for the canonical "on main" case.

3. `get_git_banner_state` uses the same resolution for the
   `· upstream <sha> ·` line and the `+N carried commits` annotation,
   so both numbers refer to the same thing the user is actually
   diverged from.

4. `_cmd_update_impl` adds a post-pull step: if the user started on
   a non-main branch, switch back to it and rebase onto
   `origin/<branch>`. On rebase conflict, abort the rebase, switch
   back to main, and print a clear manual-resolution message. The
   rebase happens before dep install / cache invalidation so the
   user's working tree is in a known good state for the rest of the
   update.

## Testing

Tested with a synthetic git repo (`/tmp/hermes-pr-test`, since
trashed):

- **Banner on main**: 0 behind. Unchanged behavior.
- **Banner on feat/test, up to date with origin/feat/test, 5 behind
  origin/main**: 0 behind. The bug: previously showed 5.
- **Banner on feat/test, 2 ahead of origin/feat/test**: 0 behind,
  banner state shows `ahead=2`. The fix surfaces unpushed local
  commits (the old code only measured against `origin/main`, so
  this case was invisible).
- **Update on feat/happy (clean rebase)**: rebases onto new main,
  no errors, banner state correct after.
- **Update on feat/test (rebase conflict)**: rebase aborts, switches
  back to main, prints manual-resolution message, leaves repo in
  a clean state.

## How to push + open the PR

The work is committed on `fix/update-rebase-and-banner-tracking` in
the local worktree at `~/.hermes/worktrees/hermes-pr-fix/`. That
branch tracks `upstream/main` (NousResearch).

```bash
# From the worktree
cd ~/.hermes/worktrees/hermes-pr-fix
git push upstream fix/update-rebase-and-banner-tracking
# Then open the PR on github.com/NousResearch/hermes-agent
```

If you'd rather drive it from a PR-ready fork branch on
`andrebrassfield/hermes-agent`:

```bash
cd ~/.hermes/worktrees/hermes-pr-fix
git remote add andrebrassfield git@github.com:andrebrassfield/hermes-agent.git  # if not already
git push andrebrassfield fix/update-rebase-and-banner-tracking
# Then open a PR from andrebrassfield:fix/update-rebase-and-banner-tracking
# → NousResearch:main
```

## PR description template

```
## Problem

`hermes update` looks like a silent no-op when you're on a long-lived
feature branch. The TUI banner keeps reporting the same "X commits
behind" even after a "successful" update. Two bugs in the same
project compound to produce this:

1. `banner.py::_check_via_local_git` always measures
   `HEAD..origin/main` regardless of which branch is checked out.
2. `main.py::_cmd_update_impl` pulls `main` but never switches back
   to the user's original feature branch.

A user on `feat/X` who forked from an old base sees this every time:

- Run `hermes update`.
- main advances 333 commits.
- feat/X does not advance.
- TUI still says "333 commits behind."

## Fix

- New `_resolve_tracking_ref()` helper in `banner.py` returns the
  current branch's upstream tracking ref (e.g. `origin/feat-x`) for
  any non-main branch, `None` for `main` / detached HEAD.
- `_check_via_local_git` and `get_git_banner_state` both use the
  tracking ref so the "X commits behind" number refers to the same
  thing the user is actually diverged from.
- `_cmd_update_impl` adds a post-pull step: if the user started on a
  non-main branch, switch back to it and rebase onto
  `origin/<branch>`. On rebase conflict, abort the rebase, switch
  back to main, and print a clear manual-resolution message.

## Tested

Synthetic repo, 3 banner scenarios + 2 update scenarios, all pass.
```

## Worktree state

The worktree is at `~/.hermes/worktrees/hermes-pr-fix/` on branch
`fix/update-rebase-and-banner-tracking` with one commit
(`60d6f6518`) on top of `upstream/main` (`d1771114e`). Push when
ready — I deliberately did not push without explicit go-ahead.
