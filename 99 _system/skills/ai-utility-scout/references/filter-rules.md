# Filter Rules — ai-utility-scout

The reject/accept filter. The chief applies the filter
after extracting the listings. Pick the top ONE from the
accepted categories.

## Reject (do NOT draft on these)

| Category | Why rejected |
|---|---|
| **Generic AI chatbots / "ChatGPT alternative" wrappers** | The persona translates specific-tool capability, not generic wrappers |
| **Pure infrastructure with no SMB-flavored application** | The audience is SMB owners, not developers |
| **Tools that have already been translated** | Check `drafts/_ledger.mdl` first; skip if the tool name is already on file |
| **Tools with vague capability** ("an AI that does X" with no specific use case) | The Scribe can't draft a concrete 4-step implementation |
| **Tools with no pricing info AND no free tier** | The Scribe can't anchor on cost without it |
| **Tools > 14 days old** | The scout is for fresh drops; settled tools go to `x-niche-scraper` |

## Accept (priority order)

| Priority | Category | Why preferred |
|---|---|---|
| 1 | AI video / voice / image generation tools | Pillar 6's bread and butter — "everyone is hyping it, here's what a roofer can do with it" |
| 2 | AI voice agents / voice cloning | Ties to Pillar 2's Missed Call thesis |
| 3 | AI inventory / e-commerce / Shopify tools | Pillar 1 |
| 4 | AI productivity / automation tools | Pillar 5 |
| 5 | AI local services / dispatching / CRM tools | Pillar 2 |
| 6 | Other (novelty) | Lower priority |

Pick the top ONE from the accepted categories. If the
top of the directory is a generic chatbot, skip to the
next non-generic tool.

## The "specific tool" rule (the load-bearing discipline)

The Scribe's draft must include the **specific tool name**.
If the draft writes "an AI tool" or "a new platform"
without naming the actual tool, the Scribe's contract is
violated and the draft is rejected.

This rule exists because the audience is operators who
want to know WHAT TOOL, not "an AI category." Specificity
is the trust signal.

## The "no fabrication" rule

The Scribe may not invent a feature the tool doesn't
have. If the tool's capability is unclear from the
directory, halt and ask the operator.

The Researcher's brief is the source of truth. The
Scribe's draft must align with the brief — no
extrapolation, no embellishment.

## The "1 tool per run" rule

The skill picks ONE tool per run. Mass translations are
a different skill (e.g., `ai-weekly-roundup` — not yet
built). If the operator wants a 5-tool roundup, surface
that the scout is single-tool by design.

## Filter application procedure

1. Extract top 5 tools (or "all visible in first snapshot")
2. Reject any in the reject list
3. Rank the remaining by accept priority
4. Pick the top ONE
5. If no tool meets the filter → HALT (H5: all generic
   chatbots) and try a different directory

## Edge cases

**A tool that's both chatbot AND something else:** if the
directory entry shows non-chatbot features (e.g., "AI
chatbot for HVAC service businesses"), accept. The
specificity is what counts.

**A tool with a vague one-liner but a useful specific
feature:** if the directory entry is vague but the tool's
own page (if clicked) has specific features, accept. The
chief clicks once to verify, then proceeds.

**A tool from a directory not in the approved list:**
accept if operator supplied the URL. The chief doesn't
gatekeep URLs.

## Eval cases

```bash
# Reject test
input="New ChatGPT wrapper with custom instructions"
echo "$input" | grep -qiE "chatgpt wrapper|gpt wrapper|chatbot" \
  && echo "REJECT"

# Accept test
input="AI voice agent for plumbers"
echo "$input" | grep -qiE "voice|agent|voice agent" \
  && echo "ACCEPT (priority 2)"

# Specific tool name test (Scribe output)
scribe_draft="Just dropped: Acme Voice — voice agent for plumbers. ..."
echo "$scribe_draft" | grep -qiE "(acme|tool|product)" \
  && echo "PASS: specific tool named"

# No fabrication test
brief="Acme Voice does X, Y, Z"
scribe_draft="Acme Voice does X, Y, Z, A, B, C"
echo "$scribe_draft" | grep -oE "X, Y, Z, A, B, C" | grep -qv "X, Y, Z" \
  && echo "FAIL: Scribe invented features A, B, C not in brief"
```
