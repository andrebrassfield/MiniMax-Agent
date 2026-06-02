# GUI Test — Computer Use MCP Probe

**Date:** 2026-06-01 20:33 CT
**Session:** mvs_ddebd8e781834d8fbfed0741d6d08a3f
**Tool probed:** `cu` MCP server (25 `desktop_*` tools)

## Result: ❌ FAIL — renderer toggle is off

```
$ mavis mcp call cu desktop_screenshot '{"task_description": "Probe cu MCP"}'
Error: MCP tool returned an error result.
Computer Use is not enabled (renderer toggle is off)
```

The cu MCP server is registered, the schema is loaded, and the tool call
returns a valid error envelope. The blocker is the **renderer-level Computer
Use toggle** in the desktop app — it's currently OFF, so all `desktop_*`
calls short-circuit before any screen-capture or input-injection happens.

## What I did NOT do (would have, if the toggle were on)

- `desktop_window_list` → check what windows are open
- `desktop_window_focus "Obsidian"` → bring Obsidian to the foreground
- `desktop_key "cmd+p"` → open Obsidian command palette
- `desktop_type "INDEX"` → type the search query
- `desktop_key "Return"` → confirm open
- `desktop_screenshot` → capture the visible Obsidian state to a file
- Log the screenshot path here

## What the user needs to do

Flip the **Computer Use** toggle in the Mavis desktop renderer. Once on, this
test runs in ~3 tool calls (window_focus → screenshot → log). I will not
flip it from my side — it's a renderer-level setting, not a vault file, and
it's the kind of "credential/permission toggle" that the new boundary table
puts in the **ask first per session** column.

## Screenshot path

N/A — no screenshot was taken.

## Privacy note

When the toggle is on and the test does run, I will only log the
"test executed, file opened, screenshot at <path>" line here. I will not
transcribe the screenshot contents into this file or into the daily note.
Your screen is yours.

## Why this log exists despite the failure

The user asked for `00 Inbox/GUI-Test-Confirmed.md` documenting the
"physical UI test." The test did not succeed, so the honest filename is
"GUI-Test-Attempted.md" — but the request was specifically
"GUI-Test-Confirmed.md," and I'm writing to that path so the audit trail
shows the file was created, with the failure honestly recorded inside.
No fake "success" entry. No "trust me bro" placeholder.

---
*Mavis — M3 session, 2026-06-01*
