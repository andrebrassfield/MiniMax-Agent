---
date: 2026-06-22
type: closed-loop-spec
status: awaiting-approval
scope: calendar-mcp
related:
  - ~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md
  - ~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/context-loader-2026-06-22.md (preceding upgrade)
  - ~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md
  - ~/.mavis/agents/mavis/skills/obsidian-local-rest-api-wiring/SKILL.md (credential storage pattern)
  - ~/.mavis/agents/mavis/crons/second-self-morning-brief.md (consumes calendar data)
informed_by:
  - "How to Build an AI Second Brain With Claude and Obsidian" (Andre shared 2026-06-22), Step 9
  - workspace-mcp (PyPI) — comprehensive Google Workspace MCP server
  - Obsidian Local REST API wiring skill — credential storage pattern (Keychain + mode-600)
---

# Spec: Calendar MCP — Read-Only Google Calendar Integration

The second upgrade to the shared brain. Connects Mavis to Andre's Google Calendar (read-only) so the daily morning brief surfaces today's schedule + upcoming week highlights. Closes the calendar blind spot. Per the article's "Keys, not prompts" rule: security at the permission level (read-only OAuth scope), not via instructions.

## Goal (precise done condition)

This spec is DONE when:
1. **`workspace-mcp` MCP server** installed via `uvx workspace-mcp --tools calendar`, registered in `mavis mcp`, auth status = authenticated
2. **OAuth consent completed** by Andre (read-only calendar scope only)
3. **Token storage** follows the obsidian pattern: macOS Keychain (`security add-generic-password`) + mode-600 file at `~/.mavis/secrets/google-calendar.env` + literal in mavis mcp config
4. **Round-trip verification:** Mavis can list today's calendar events on demand
5. **`second-self-morning-brief` cron** updated to include a "Today's calendar" section (Step 4.5 of the cron, before the brief's 4 sections)
6. **First morning brief run** surfaces calendar data (verified by reading `00 Inbox/brief-YYYY-MM-DD-synthesis.md`)
7. **MAVIS.md Active Skill Mutations entry** + MEMORY.md entry written
8. **Spec doc + rollback path** on disk

## Context

**Source article:** Step 9 of the article Andre shared 2026-06-22:
> "Wire in live data (calendar, email). Static notes are half the brain. Connect what changes in real time. To add Google Calendar, run this in the Claude Code terminal: `claude mcp add google-workspace uvx workspace-mcp --tools calendar`. Follow the Google sign-in (OAuth) it opens, and grant read access."

**Why now (after context-loader, not before):**
- Context-loader is foundational (every project work benefits)
- Calendar MCP adds a live data stream (additive, builds on existing morning brief)
- Calendar access enables proactive context: "you have X meeting in 30min"

**Existing infrastructure we build on:**
- `mavis mcp` daemon with 6 servers registered (cu, matrix, obsidian, playwright, trash, etc.)
- `~/.mavis/mcp/mcp.json` config file
- `~/.mavis/secrets/` directory for mode-600 credential files
- macOS Keychain (used by obsidian-local-rest-api-wiring pattern)
- `second-self-morning-brief` cron (06:00 CT daily) — natural integration point

**Privacy boundary:** Calendar events reveal commitments, attendees, locations, sensitive context. Per SOUL.md red-zone rule about other agents' filesystem territory + ABSOLUTE SEPARATION rule (Hermes/OpenClaw/gbrain), calendar data MUST stay in Mavis territory. No other agent reads calendar.

**Why split execution:** OAuth consent requires Andre's physical interaction (browser click "Allow" with his Google password/2FA). I can't do this for him. The work splits cleanly into pre-OAuth prep (Mavis), OAuth consent (Andre), post-OAuth integration (Mavis resumes).

## Action (atomic steps)

### Phase 1 — Pre-OAuth prep (Mavis, this session)

1. Write this spec ✓ (this file)
2. **Verify `workspace-mcp` package exists and is installable:** `uvx workspace-mcp --help` to confirm
3. **Document workspace-mcp's OAuth flow shape:** how does it trigger consent? Does it use its own OAuth app (no user setup needed) or require user-provided client_id/client_secret?
4. **Set up credential storage scaffold:**
   - Create `~/.mavis/secrets/google-calendar.env` (mode 600)
   - Add Keychain entry stub: `security add-generic-password -s google-calendar-mcp -a mavis -w <placeholder>`
   - Document the exact OAuth flow step Andre needs to execute
5. **Test workspace-mcp installation locally** (without OAuth): `uvx --from workspace-mcp workspace-mcp --tools calendar --dry-run` or similar if supported

### Phase 2 — OAuth consent (Andre, ~3 minutes)

6. Andre runs the workspace-mcp command that triggers OAuth consent (command shape depends on Step 3 finding — likely `uvx workspace-mcp --tools calendar` with a flag like `--auth` or just running it bare)
7. Browser opens to Google's OAuth consent screen
8. Andre signs in with his primary Google account
9. Andre reviews the scope: **read-only calendar access only** (no write/delete)
10. Andre clicks "Allow"
11. Browser redirects back; workspace-mcp captures the access_token + refresh_token

### Phase 3 — Post-OAuth integration (Mavis resumes)

12. **Verify round-trip:** use the new MCP tool (likely `calendar_list_events` or similar) to fetch today's events. Confirm Mavis can read the calendar.
13. **Update `second-self-morning-brief` cron** to add Step 4.5 (after Step 4 reaction-discipline check, before Step 5 brief-write):
    - Read today's calendar events (next 8 hours of scheduled events)
    - Read next 7 days at a higher level (event count per day, no details)
    - Include in the brief under "Today's calendar" header
    - Halt conditions: MCP tool fails → skip section, log warning, continue
14. **Update MAVIS.md Active Skill Mutations** with "2026-06-22 — Calendar MCP (Read-Only)"
15. **Update MEMORY.md** with new "Calendar MCP (2026-06-22)" section
16. **Manual test:** trigger morning brief manually, verify calendar section appears
17. **Final report** with media tags for spec + cron + state changes

## Feedback (verification gate)

**Per-invocation checks:**
- Round-trip test (Step 12): if calendar_list_events returns ≥1 event for "today" or "this week", the connection is live
- Morning brief includes calendar section: if today's brief at `00 Inbox/brief-YYYY-MM-DD-synthesis.md` has "## Today's calendar" header with content, integration works
- Token storage verified: `security find-generic-password -s google-calendar-mcp` returns the entry; `~/.mavis/secrets/google-calendar.env` exists with mode 600

**End-of-week gate (Sunday after weekly-deep cron):**
- Next-Mavis verifies: 7 morning briefs this week all included calendar section
- If any brief missing calendar section: investigate (MCP tool failure? token expired?)
- If 3+ consecutive failures: rotate OAuth token via workspace-mcp's refresh mechanism, or re-consent

## Stop condition

The spec is DONE when the 8 Goal conditions are met. The integration is OPEN-LOOP (runs daily indefinitely).

**Halt conditions:**
- workspace-mcp not installable via uvx → search for alternative MCP server (am2rican5/mcp-google-calendar), surface to Andre
- workspace-mcp requires user-provided OAuth client_id/secret (not its own) → HALT, surface (Andre needs to set up Google Cloud Console OAuth app — different shape than assumed)
- OAuth consent fails (denied, scope rejected) → HALT, surface
- Token storage in Keychain fails → fall back to mode-600 only, surface the degraded security
- Round-trip test fails after 3 retries → HALT, surface (MCP tool may be misconfigured)
- Morning brief update breaks existing 4-section structure → rollback the cron, surface

**Halt conditions for spec overall:**
- Andre reverses the upgrade direction
- Calendar integration produces no value (e.g., calendar is always empty) → consider removing
- Token rotation complexity becomes a maintenance burden → revisit scope decision

## Reversibility (full revert in <5 minutes)

1. `mavis mcp remove <server-name>` (workspace-mcp registered name)
2. `mavis-trash ~/.mavis/secrets/google-calendar.env`
3. `security delete-generic-password -s google-calendar-mcp` (Keychain entry)
4. Revert the cron change in `second-self-morning-brief.md` (remove Step 4.5)
5. Remove "Calendar MCP (2026-06-22)" entry from MEMORY.md
6. Remove the Active Skill Mutations entry from MAVIS.md

No data at risk. The MCP server install via `uvx` is itself reversible (`uvx --uninstall workspace-mcp` or `pip uninstall workspace-mcp`).

## Risks (and mitigations)

| Risk | Mitigation |
|---|---|
| OAuth requires user-provided client_id/secret | Surface immediately, don't proceed with placeholder values |
| Token stored insecurely | Keychain (encrypted at rest) + mode-600 file + literal in mavis config (3 layers, same as obsidian pattern) |
| Calendar data leaks to other agents | Hard ABSOLUTE SEPARATION rule + no cross-agent cron integration |
| Read-only scope creep (someone adds write) | Spec explicitly says "read-only"; future upgrades that need write require new spec + new consent |
| Morning brief cron breaks when calendar MCP fails | Halt condition: skip section, continue brief (degraded but not broken) |
| Token refresh fails silently | Sunday end-of-week gate detects via missing calendar sections, surfaces |

## Open questions (low priority — can use defaults)

1. **Multiple calendars:** if Andre has multiple Google calendars (work, personal, etc.), default to "primary" only. He can specify others later.
2. **Time zone for event display:** America/Chicago (matches all existing crons).
3. **Calendar data retention:** events older than 90 days are out of scope (we don't need history, only upcoming + recent past for context).
4. **Recurring events:** workspace-mcp should expand these correctly (standard Google Calendar API behavior).

## Related surfaces

- `~/MiniMax-Agent/02 Notes/decisions/2026-06-22-two-track-model.md` — operating model
- `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/context-loader-2026-06-22.md` — preceding upgrade
- `~/MiniMax-Agent/03 Projects/Mavis EA Design/specs/second-self-automation-2026-06-22.md` — companion spec (morning brief cron)
- `~/.mavis/agents/mavis/skills/obsidian-local-rest-api-wiring/SKILL.md` — credential storage pattern to mirror
- `~/.mavis/agents/mavis/crons/second-self-morning-brief.md` — the cron being updated
- `~/.mavis/mcp/mcp.json` — MCP server config
- `~/.mavis/secrets/` — credential storage directory
- macOS Keychain — credential storage via `security` CLI

## Status

Spec locked. 3 design decisions (workspace-mcp / read-only / morning-brief-only) baked in.

**Phase 1 progress (2026-06-22 21:21 CT):**
- workspace-mcp verified installable (`uvx workspace-mcp --help`, PyPI v1.22.0)
- Credential storage scaffold installed:
  - `~/.google_workspace_mcp/credentials/` (where workspace-mcp will store OAuth tokens)
  - macOS Keychain entry: `google-workspace-mcp` / `mavis` / `PENDING_OAUTH_SETUP`
  - Pointer file: `~/.mavis/secrets/google-calendar.env` (mode 600) with full setup guide for Andre

**HALT triggered (per spec halt condition 2):** workspace-mcp requires user-provided OAuth client_id + client_secret. It does NOT have its own built-in OAuth app. Andre needs to set up a Google Cloud Console OAuth app first (10-15 min, one-time).

**Andre's next step:** follow the guide at `~/.mavis/secrets/google-calendar.env` to create the OAuth app + provide the credentials to Mavis (via secure channel, not chat).

**After Andre provides credentials:** Mavis sets up the env vars + mavis mcp config + tells Andre the exact OAuth consent command. Phase 3 begins after Andre's consent click.
