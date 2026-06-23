# AGENTS.md — Goose Work Queue Protocol

## Gibson Overlay

Canonical vault: `/Users/brassfieldventuresllc/vault`

Default cognition path: gbrain MCP. Fallback: gbrain CLI. Do not crawl the vault directly for normal memory retrieval.

Read before work:

- `/Users/brassfieldventuresllc/vault/Shared/MemoryRules/Gibson-Memory-Contract.md`
- `/Users/brassfieldventuresllc/vault/Shared/Runtime/Gibson-Runtime-Contract.md`
- `/Users/brassfieldventuresllc/vault/Agents/Protocols/AGENT-BOOT-SEQUENCE.md`

Hard stops:

- No deploys, pushes, database migrations, external sends/posts, credential changes, schedule changes, destructive file operations, or memory purges without explicit in-session approval.

Every completed run should produce a receipt shaped like:

- `/Users/brassfieldventuresllc/vault/Shared/Schemas/gibson-run-receipt.yaml`

## Your One Job
Poll the Hermes kanban queue, claim coding tasks, execute in worktrees, report completions.

This is a work queue — not a chat interface. Execute, iterate, report.

## Worker Loop
```
REPEAT FOREVER:
    1. poll_mavis_tasks(limit=5)
       Filter: status TODO/READY, assignee NOT 'goose'
       Sort: priority DESC

    2. No tasks? → wait 60s → re-poll

    3. Claim highest-priority:
       claim_task(task_id="<id>")
       If success=false → skip, re-poll

    4. Execute in worktree:
       - Read task.body for instructions
       - Use openclaw worktree factory to create isolated worktree
       - Apply coding rules from oh-my-pi AGENTS.md
       - Write code, run tests, validate
       - Never modify main branch

    5. emit_completion(task_id, result, success)
       result = what was done, key findings, or failure reason

    6. Loop
```

## Worktree Lifecycle
1. Call openclaw `get_worktree_inventory()` to check available worktrees
2. Request worktree from OpenClaw worktree factory (via kanban dispatcher)
3. Work in isolated branch, never touch main
4. On completion: emit_completion → worktree auto-archived or cleaned

## Coding Standards
- Follow oh-my-pi AGENTS.md rules (TypeScript, Rust, Python patterns)
- No `any` types, no inline prompts (prompts in .md files)
- Barrel exports preferred
- Test before reporting success
- If tests fail: retry once, then BLOCK with specific failure reason

## Claiming Rules
- Atomic claim: sets assignee=goose, status=READY
- If API returns success=false → another worker won → skip
- Never execute work without successful claim

## Completion
- success=true → status becomes DONE
- success=false → status becomes BLOCKED (clear reason required)
- Result field is permanent — write it well
