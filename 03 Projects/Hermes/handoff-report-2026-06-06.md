# Hermes Agent — bug handoff: `hermes update` silent no-op on feature branches

**From:** Andre Brassfield (andrebrassfield)
**Date:** 2026-06-06
**PR:** [#40673](https://github.com/NousResearch/hermes-agent/pull/40673) — open, mergeable
**Severity:** High (silently breaks `hermes update` for any user on a long-lived feature branch — looks like a working update but isn't)
**Tested against:** `NousResearch/hermes-agent` v0.16.0 (2026.6.5), commit `d1771114e`

---

## TL;DR

Two bugs compound to make `hermes update` look like a successful no-op when you're on a long-lived feature branch. `main` advances, your branch doesn't, and the TUI banner keeps reporting the same "X commits behind" — so re-running update looks like a reversion.

Repro: be on `feat/X` forked from an old base, run `hermes update`, observe `main` advances but `feat/X` doesn't. The next TUI check still says "X commits behind." Repeat until frustrated.

The bug bit me personally on `feat/cron-until-done` (11 carried commits, 333 behind `main`); I went through the clean-slate + re-clone path before diagnosing. Fix is in PR #40673 — one commit, 168 lines, two files (`hermes_cli/banner.py`, `hermes_cli/main.py`).

---

## Bug 1 — TUI banner measures distance to the wrong ref

**File:** `hermes_cli/banner.py`, line 147, function `_check_via_local_git`

```python
result = subprocess.run(
    ["git", "rev-list", "--count", "HEAD..origin/main"],
    ...
)
```

The banner always measures `HEAD..origin/main`, regardless of which branch is checked out. A user on `feat/X` that's in sync with its own `origin/feat-X` but N commits behind `origin/main` will see "N commits behind" every time — even when their feature branch is current.

The companion function `get_git_banner_state` (line 321) has the same pattern in two places: it reads `origin/main` for the "upstream" hash and computes `origin/main..HEAD` for the "carried commits" annotation. Both are wrong for any non-main branch.

**Fix:** add `_resolve_tracking_ref()` that returns the current branch's `@{u}` (e.g. `origin/feat-x`) for any non-main branch with an upstream tracking ref, and `None` for `main` / detached HEAD. Use the result in both `_check_via_local_git` and `get_git_banner_state`.

Net effect: the "X commits behind" number now means "behind your branch's upstream," which is what users actually want to know.

---

## Bug 2 — `hermes update` doesn't switch back to the user's feature branch

**File:** `hermes_cli/main.py`, line 10218, function `_cmd_update_impl` (early-return path at line 10460 also has a partial version of this logic)

The update flow when the user is on a feature branch:

1. **Line 10384:** `if current_branch != branch:` — user is on `feat/X`, `branch` defaults to `main`.
2. **Line 10393:** `git checkout main`.
3. **Line 10499:** `git pull --ff-only origin main` — main advances.
4. **Line 10596+:** post-pull work (deps install, cache invalidation, etc.).
5. **No step to switch back.** Function returns while still on `main`.

The early-return path at line 10460 ("already up to date") does correctly switch back, but the success path doesn't. So on a successful update the user is left on `main` with their feature branch stale. Next TUI check shows the same "X commits behind" (because Bug 1 measures against `origin/main`).

**Fix:** after the post-pull work, if the user started on a non-main branch, switch back to it and run `git rebase origin/<branch>`. On rebase conflict, abort the rebase, switch back to `main`, and print a clear manual-resolution message. The current `auto_stash_ref` logic handles the stash-restore case correctly — the new rebase step runs after that.

Net effect: `hermes update` on a feature branch now actually updates that branch. The "X commits behind" count drops to 0 on the next TUI check (and the count is now measured against the right ref anyway, per Bug 1 fix).

---

## Reproduction (one-liner)

```bash
cd /tmp && rm -rf hermes-bug && mkdir hermes-bug && cd hermes-bug
git init -b main -q && git remote add origin /tmp/hermes-bug.git
git init --bare /tmp/hermes-bug.git -q 2>/dev/null
echo v1 > README.md && git add . && git -c user.email=t@t -c user.name=t commit -qm init && git push -u origin main -q
git checkout -b feat/x -q
echo feat1 >> README.md && git -c user.email=t@t -c user.name=t commit -qam "feat 1"
git push -u origin feat/x -q
git checkout main -q
for i in 1 2 3 4 5; do echo "main $i" >> README.md; git -c user.email=t@t -c user.name=t commit -qam "main $i"; done
git push -q
git checkout feat/x -q
# Now: HEAD..origin/main = 5 (5 main commits not in feat/x)
# Bug 1: banner would say "5 commits behind origin/main" — incorrect.
# Bug 2: `hermes update` would pull main, leave you on main, feat/x untouched.
```

After running `hermes update` on this setup:
- **Buggy behavior:** function returns "✓ Update complete!", you're on `main`, `feat/x` is unchanged, TUI says "5 commits behind" forever.
- **Fixed behavior:** function rebases `feat/x` onto new `main`, you stay on `feat/x`, TUI says 0 behind your `origin/feat-x`.

---

## Testing done in PR #40673

Three banner scenarios + two update scenarios in a synthetic repo, all pass:

1. **Banner on `main`, 0 behind `origin/main`:** 0 (unchanged from buggy code).
2. **Banner on `feat/test`, 0 behind `origin/feat-test`, 5 behind `origin/main`:** **0** (was 5 — the bug).
3. **Banner on `feat/test`, 2 ahead of `origin/feat-test`:** 0 behind + `ahead=2` annotation (was: just the wrong N-behind count, never surfaced unpushed local commits).
4. **`hermes update` on a `feat/happy` with a clean rebase path:** rebases onto new main, no errors, banner state correct after.
5. **`hermes update` on a `feat/test` with a rebase conflict (README.md touched in both):** rebase aborts, switches back to `main`, prints `⚠ Rebase of 'feat/test' onto main hit conflicts.` + manual-resolution commands, leaves repo in a clean state. No silent failures.

I also did an integration test on my running install: created `test/feat-branch`, added a commit, verified the patched banner correctly resolves `origin/test/feat-branch` and reports 0 behind (which the old code would have shown as "5 behind origin/main" or similar — the bug).

---

## Why this matters

Every Hermes user on a long-lived feature branch hits this. The most common scenario in the wild:

- User forks `main` at some point to do a focused feature.
- Days/weeks pass. `main` advances 50–500 commits.
- User runs `hermes update` and expects their branch to follow.
- `main` advances under them, but the function reports success and silently leaves the branch stale.
- TUI banner keeps showing the same behind-count.
- User assumes Hermes is broken (it kind of is) and either:
  - Re-installs from scratch (lossy, the disaster path I went down).
  - Gives up on updates.
  - Manually `git rebase origin/main` after every `hermes update`, working around the bug.

Fixing this is one commit. The PR is ready, tested, and mergeable. Please give it a look.

---

## Why this is low-risk to merge

- **No new dependencies** (just `subprocess.run` and `git rev-parse`).
- **No behavior change for the canonical case** (user on `main` — exactly identical to before).
- **Bounded new behavior** (user on a feature branch — switches back and rebases, with conflict-abort recovery to a known-good state).
- **Cherry-pickable** onto any commit on `main` (clean diff, no merge base assumptions).
- **No public API changes** — the `cmd_update` function signature is unchanged.
- **No config changes** — works with the existing `is_fork` / `_sync_with_upstream_if_needed` machinery.
- **Failure mode is graceful** — if the rebase fails (e.g. conflicts), the function aborts the rebase, switches back to `main`, and prints a clear message. The user is left on `main` with a clean working tree, exactly the same state as if they'd run the buggy version.

---

## Acknowledgments

I went through the worst-case path on this one — nuked my local install, re-cloned from my fork, lost carried work, and bounced through several false-start diagnoses before I could see the actual code. The clean-slate route in the diagnosis is real-user pain, not a contrived repro. The fix removes that footgun for everyone.

The work outside the PR (clean-slate, branch archiving, fork consolidation) is on me and lives in my own fork / vault. The two-line root cause is in upstream. PR #40673 carries the minimal, tested fix.

Thanks for building Hermes — v0.16.0 / 2026.6.5 is a genuinely strong release. The Desktop app + remote-gateway flow in particular is a much better experience than the old CLI-only model.

— Andre
