# Safety Halts — ea-draft-approval

The skill must HALT (not improvise) when any of these fire.

## H1. Telegram post fails (auth, network)

**Detection:** The Telegram post returns an error
(auth failure, network timeout, rate limit).

**Expected response:** Halt. Do NOT assume the proposal
was sent. Surface the Telegram error. The proposal is
not recorded in the state file (since it wasn't sent).

## H2. State file write fails

**Detection:** The state file write fails (disk full,
permission error, etc.).

**Expected response:** Halt. Surface the disk error. The
proposal is in a partial state (Telegram may have sent
but state didn't update) — surface the inconsistency.

## H3. Scribe's file is missing or unreadable

**Detection:** The Scribe's batch file is missing or
unreadable when Mavis tries to parse it.

**Expected response:** Halt. Surface the missing file.
The bridge can't propose drafts it can't read.

## H4. Ambiguous reply (not approve/deny/edit)

**Detection:** Andre's reply doesn't match any of the
approve/deny/edit patterns in
`references/reply-patterns.md`.

**Expected response:** Halt (one short message). Ask
Andre to clarify: "approve / deny / edit?" Don't
elaborate. The proposal stays open.

## H5. Stale draft_id (sha256 mismatch)

**Detection:** The reply matches a draft_id, but the
Scribe's file has been rewritten since the proposal
(sha256 of current post_text ≠ sha256 of proposed
post_text).

**Expected response:** Halt. Re-propose the new draft.
Do NOT act on the stale reply.

## H6. Post-N chain is down

**Detection:** The post-N cron chain is failing (auth,
rate limit, x.com UI change). The bridge can route to
`approved/`, but the publisher is broken.

**Expected response:** Halt. Surface the post-N failure.
The bridge's job (propose + route) is fine; the
publisher's job (publish) is broken. The operator
investigates the post-N chain.

## Eval cases

| Halt | Input (mock state) | Expected behavior |
|---|---|---|
| H1 | Telegram returns 401 | Halt, surface auth error |
| H2 | state file write returns EACCES | Halt, surface disk error |
| H3 | Scribe's file is missing | Halt, surface missing file |
| H4 | Reply is "looks good" | Halt, ask "approve / deny / edit?" |
| H5 | Scribe rewrote the file after proposal | Halt, re-propose |
| H6 | post-N cron returns 429 | Halt, surface post-N failure |
