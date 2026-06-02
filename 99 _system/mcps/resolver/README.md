# Resolver MCP — Skill Router

> The brain stem. When Mavis gets a generic prompt ("Clear out my tabs",
> "What happened this week?", "Do I have anything on memory architectures?"),
> the Resolver routes it to the right Skill Pack.

## Esalen posture

This MCP is a **thin API router** per the Esalen operating posture
(`99 _system/ESALEN-NOT-FOXCONN.md` audit Q2). The Python does the I/O:

- walk `99 _system/skillopt/skills/` to discover Skill Packs
- read each `skill.md` to extract a description + tag set
- gather lightweight vault state (today's date, inbox count, recent commits)
- construct a "ranking request" JSON
- validate the M3-produced ranking

The **M3 context window does the classification and confidence scoring**.
A deterministic layer trying to classify prompts is the canonical Foxconn
"model judges itself" pattern. The Python gathers inputs; M3 makes the call.

## Tools

| Tool | Purpose |
|------|---------|
| `resolver.build_ranking_request` | Build a ranking request for a user query. Returns the request JSON + a prompt for M3 to fill in. |
| `resolver.apply_ranking` | Apply M3's ranking to a saved request. Validates the structure and returns the final routing decision. |

## Usage

### As an MCP server (stdio)

```bash
python3 resolver.py --serve
```

Then from an MCP client:
```
build_ranking_request(query="Clear out my tabs", top_k=2)
# → returns {request_id, request, prompt}
# → M3 reads the prompt, emits a JSON ranking
apply_ranking(request_id="rank-...", ranking_data={...})
# → returns the validated ranking
```

### As a CLI (one-shot)

```bash
# Build a request
python3 resolver.py --query "Clear out my tabs and process the inbox"
# → prints a one-line report + the request JSON
# → saves the request to 99 _system/mcps/resolver/_requests/<id>.json
# → saves the prompt to 99 _system/mcps/resolver/_requests/<id>-prompt.txt

# Apply an M3-produced ranking
python3 resolver.py --apply-ranking my-ranking.json --with-request-id rank-...
```

### List all discovered Skill Packs

```bash
python3 resolver.py --list-skills
```

## How it works

```
                ┌─────────────────────┐
                │  user query         │
                │ "Clear out my tabs" │
                └──────────┬──────────┘
                           │
                ┌──────────▼──────────┐
                │  build_ranking_     │   deterministic I/O
                │  request (Python)   │   ─ walk skills/
                │                     │   ─ gather vault state
                │                     │   ─ build prompt
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  M3 context window  │   classification + confidence
                │  (the model itself) │
                │                     │
                │  Emits: ranking +   │
                │  reasoning          │
                └──────────┬──────────┘
                           │
                ┌──────────▼──────────┐
                │  apply_ranking      │   deterministic validation
                │  (Python)           │   ─ top-K enforced
                │                     │   ─ confidence in [0,1]
                │                     │   ─ skill names exist
                │                     │   ─ one_line_match non-empty
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │  validated ranking  │   the routing decision
                │  {ranking, status}  │
                └─────────────────────┘
```

## What's NOT here

- **No LLM call inside this module.** The Python script does not import
  any LLM client. Audit Q2 passes.
- **No classification in the deterministic layer.** The Python does
  I/O and validation, not classification. M3 makes the call.
- **No automatic execution of Skill Packs.** The Resolver returns a
  ranking; the orchestrator (Mavis) decides whether to invoke the
  skill's action.py. The Resolver is a router, not a dispatcher.

## Related

- `99 _system/skillopt/skills/` — the Skill Packs the Resolver routes to
- `99 _system/mcps/vault-brain/` — the retrieval layer the orchestrator
  uses to gather vault state for M3's context
- `99 _system/ESALEN-NOT-FOXCONN.md` — the operating posture this MCP obeys

## Tests

```bash
cd 99 _system/mcps/direct-intake
.venv-direct-intake/bin/python -m pytest ../../mcps/resolver/test_resolver.py -v
```

17 tests cover skill discovery, request building, prompt rendering,
ranking validation, and apply_ranking end-to-end.

---

*Authored 2026-06-02 as part of Operation Chimera — the Resolver Layer.*
