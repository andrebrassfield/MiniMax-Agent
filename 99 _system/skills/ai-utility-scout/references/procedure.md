# Procedure — ai-utility-scout

The 10-step procedure with bash commands. The SKILL.md
only carries the procedure overview. The actual commands
live here (the deterministic layer).

---

## Step 1: Verify the bridge is live

```bash
mavis browser status
```

If `Native host: not connected` → HALT (H1). Do not fall
back to auto-spawned Chromium.

## Step 2: Pick the launch directory

Default rotation: alternate across the 4 approved
directories across days to get a diverse feed. Per
`references/launch-directories.md`.

If the operator specified a directory, use that.

## Step 3: Open the directory

```bash
mavis browser tool open_tab '{"url":"<directory-url>"}'
```

Note the returned `tabId`.

## Step 4: Authentication + load wait + result check

Wait 3-5 seconds. Take a snapshot:

```bash
mavis browser tool snapshot '{"tabId":<id>,"interactive":false,"depth":2}'
```

**Halt conditions (H2/H3/H4):**
- Snapshot shows "Sign in" / "Sign up" / "Subscribe"
  paywall → operator decides whether to log in
- Snapshot shows a rate-limit warning → HALT
- URL is not the expected directory after navigation
- Zero results → HALT, try a different directory

**Proceed conditions:**
- Listings visible with tool names + 1-line descriptions
- At least one tool within the engagement floor (100
  saves / 50 upvotes)

## Step 5: Filter the listings

Apply the reject/accept filter per
`references/filter-rules.md`:

**Reject:**
- Generic AI chatbots / "ChatGPT alternative" wrappers
- Pure infrastructure with no SMB-flavored application
- Tools already in `_ledger.mdl`
- Vague capability (no specific use case)
- No pricing AND no free tier
- Tools > 14 days old

**Prefer (priority order):**
1. AI video / voice / image generation
2. AI voice agents / voice cloning
3. AI inventory / e-commerce / Shopify
4. AI productivity / automation
5. AI local services / dispatching / CRM
6. Other (novelty)

Pick the top ONE from the accepted categories. If the
top is a generic chatbot, skip to the next.

## Step 6: Extract the tool info

For the picked tool, extract:
- Tool name
- Source URL (the tool's own page if available, or the
  directory entry URL)
- One-line capability description (verbatim from the
  directory)
- Launch date (if visible)
- Pricing tier (free / freemium / paid — from the tool's
  page if linked, or "unclear" if not)
- Engagement metrics (saves, upvotes, comments)

**Do NOT click into the tool's full marketing page**
unless necessary — the directory's one-liner is enough
for the discovery brief.

**Do NOT scroll via `press_key`** — Focus Rule (same as
sibling X skills).

## Step 7: Dispatch the Researcher

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-researcher","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

The task spec is the verbatim block in
`references/researcher-task-spec.md` with placeholders
filled in.

## Step 8: Dispatch the Scribe

After the Researcher's brief is written:

```bash
mavis communication send \
  --from <chief-session-id> \
  --to <chief-session-id> \
  --command spawn \
  --content '{"agent":"x-scribe","model":"MiniMax-M2.7","prompt":"<task spec>"}'
```

The task spec is the verbatim block in
`references/scribe-task-spec.md` with placeholders filled
in (pulling from the Researcher's brief).

## Step 9: Update the drafts ledger

Append one line to
`03 Projects/X-Content-Engine/drafts/_ledger.mdl`:

```markdown
- YYYY-MM-DD HH:MM CT — utility-scout from <directory> (tool: <tool name>, Scribe draft, pending)
```

## Step 10: Return summary

Send a one-paragraph summary to the operator: file path,
tool name, source, draft headline, the strongest SMB use
case identified, any halt conditions.
