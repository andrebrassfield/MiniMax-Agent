---
type: project
created: 2026-06-01
status: seed
tags: [project, mavis, architecture, mcp, design]
---

# 03 The Custom MCP Arsenal

> Five new MCP servers designed for M3's specific capabilities — 1M context, native vision, persistent memory. These are design specs, not implementations; they describe the right tool surface for a solo EA-mode operator on the M3 frontier.

## Why custom MCPs

Generic MCP servers (`filesystem`, `git`, `fetch`, etc.) cover maybe 60% of an EA's needs. The other 40% is capability-specific:

- Vault-scale semantic search that takes advantage of 1M context (not chunk-and-embed)
- Visual screen-state with cross-session memory (not stateless screenshot)
- Context pre-packing that knows about MSA's block selection
- Tool failure classification that learns from past recoveries
- The agent's own introspection — what it has access to, what it has done, what state it's in

These five are the design. Each is small, sharp, and earns its place by filling a gap the generic stack leaves open.

## MCP #1: `vault-brain`

**Purpose:** Semantic search + cross-link suggestions for the entire Obsidian vault, designed to fit M3's 1M context window.

### Tool surface

```typescript
// Returns the top-K most relevant notes for a query, with full content
vault_brain.search({
  query: string,             // semantic search query
  top_k?: number,            // default 20
  max_total_tokens?: number, // default 200_000; respects M3's 1M budget
  include_backlinks?: boolean, // default true
  include_frontlinks?: boolean // default false
}) → {
  results: Array<{
    path: string,
    title: string,
    score: number,           // 0-1
    content: string,         // full note body
    backlinks: string[],     // titles of notes that link here
    tags: string[]
  }>,
  total_tokens: number
}

// Suggests new links between two notes
vault_brain.suggest_links({
  note_a: string,           // path or title
  note_b: string
}) → {
  relationship: string,     // one-line description
  confidence: number,       // 0-1
  suggested_link_type: "wikilink" | "embedded" | "MOC-reference"
}

// Returns a Map-of-Content (MOC) auto-generated for a topic
vault_brain.build_moc({
  topic: string,
  max_notes?: number
}) → {
  title: string,
  sections: Array<{
    heading: string,
    note_paths: string[],
    summary: string
  }>
}
```

### Why custom

The Obsidian plugin `vault-brain` already exists (used in the existing `obsidian` MCP). What M3 unlocks is **whole-vault in-context**: instead of retrieving top-5 chunks, retrieve top-20 full notes within a 200K token budget, then ask M3 to reason over all of them. The whole-vault mode is the new primitive.

### The implementation hint

- Index = note embeddings (existing approach) + a small knowledge graph from `[[wikilinks]]`
- Search = hybrid (semantic + graph-walk) for better precision
- Token budget = explicit, not implicit; the caller controls the output size
- Backlinks = pulled at index time, not computed per-query

### Cost

Embedding a 2K-note vault: ~$0.50 one-time with a small embedding model. Per-query: ~$0.001 for embedding the query, ~0 for the index lookup. No LLM cost on the server side; M3 does all the reasoning.

## MCP #2: `macos-vision-anchor`

**Purpose:** Persistent multimodal screen understanding with cross-session state. Unlike the stateless `cu` MCP, this one remembers what was on screen, where the model clicked, and what happened next.

### Tool surface

```typescript
// Capture current screen state with semantic anchor
vision_anchor.capture({
  scope?: "full" | "window" | "region",  // default "window" (focused window)
  include_a11y?: boolean,                 // default true
  annotate_elements?: boolean             // default true (Set-of-Marks style)
}) → {
  anchor_id: string,        // unique ID for this state
  screenshot_b64: string,
  a11y_tree: object,        // accessibility tree
  elements: Array<{
    ref: string,            // e.g., "elem-3"
    role: string,           // "button", "textfield", etc.
    label: string,          // visible text
    bounds: [x, y, w, h],
    interactive: boolean
  }>,
  captured_at: string       // ISO timestamp
}

// Recall a previous state by anchor_id
vision_anchor.recall({
  anchor_id: string
}) → { /* same shape as capture */ }

// List recent anchors
vision_anchor.history({
  session_id?: string,      // default current session
  limit?: number            // default 50
}) => Array<{ anchor_id, captured_at, summary }>

// Compare two anchors (what changed)
vision_anchor.diff({
  anchor_a: string,
  anchor_b: string
}) => {
  changes: Array<{
    type: "appeared" | "disappeared" | "moved" | "resized" | "text-changed",
    element_ref: string,
    description: string
  }>
}
```

### Why custom

`cu` is stateless: every screenshot is a new event, no memory of what was tried before. `macos-vision-anchor` adds the cross-anchor memory that long visual workflows need:
- After 30 steps of "open Settings, navigate to Network, click Advanced," the model can recall the first screenshot and reason about progress
- After an action fails, the diff between the pre-action and post-action anchors tells the model *exactly* what changed (or didn't)
- Cross-session: the model can pick up a visual task from where it left off, even hours later

### The implementation hint

- Anchors stored locally in SQLite, indexed by timestamp + element signature
- Element signatures = perceptual hash + role + label (so the same button matches across sessions)
- a11y tree via the macOS `AXUIElement` API
- Set-of-Marks annotation = overlay numbered tags on interactive elements, captured in the screenshot

### Cost

Per-capture: ~50ms to take screenshot, ~100ms to query a11y, ~20ms to write anchor. Storage: ~500KB per anchor (PNG screenshot). 1 hour of work at 30 actions = ~15MB. Trivial.

## MCP #3: `long-context-curator`

**Purpose:** Takes a corpus + a query and returns the optimal pre-ordered, block-aligned context within M3's 1M window. The user-side counterpart to MSA's block-level attention.

### Tool surface

```typescript
// Curate context for a specific task
curator.pack({
  query: string,            // the task the model will work on
  candidates: Array<{       // candidate chunks to consider
    id: string,
    content: string,
    source: string,         // optional provenance
    token_count: number
  }>,
  budget_tokens: number,    // e.g., 800_000
  strategy?: "marginal-value" | "recency" | "diversity" | "anchor-ends"  // default "anchor-ends"
}) => {
  selected: Array<{ id, content, token_count, position: number, /* 0=start, 1=middle, 2=end */ }>,
  total_tokens: number,
  dropped: Array<{ id, reason: string }>,
  rationale: string         // why this ordering
}

// Compact a long context at intervals
curator.compact({
  context: string,          // current context
  target_tokens: number,    // e.g., 400_000 (halve it)
  preserve?: string[]       // note paths or content fingerprints to keep verbatim
}) => {
  compacted: string,
  summary_added: string,
  dropped_sections: string[]
}
```

### Why custom

With 1M context, the failure mode shifts from "doesn't fit" to "fits but lost in the middle." The curator solves the second problem: given a budget and a query, what should be at the start, end, and middle of the prompt?

The `anchor-ends` strategy places the highest-signal content at positions 0 and (budget-1), where attention is strongest. The `marginal-value` strategy ranks by expected information gain per token. The `diversity` strategy ensures multiple perspectives, not 5 near-duplicates.

### The implementation hint

- Marginal-value scoring = a small re-ranker (cross-encoder) on top of the embedding similarity
- Anchor-ends = sort by score, place top-2 at the ends, fill the middle with the rest
- Compaction = sliding-window summarization, with explicit preservation of pinned items
- "Why this ordering" rationale = short LLM call (Haiku-class) to generate the explanation

### Cost

Per-pack: ~$0.005 for the re-ranker + rationale call. Cheap. The savings on attention-quality + reduced follow-up tool calls dwarf this.

## MCP #4: `tool-self-healer`

**Purpose:** Wraps every MCP tool call with intelligent error classification, targeted recovery, and pattern learning. The model never sees a 401 or 429 raw — it sees a recovery plan.

### Tool surface

```typescript
// Wrap a tool call with self-healing
healer.invoke({
  tool: string,             // e.g., "gmail.send"
  args: object,
  options?: {
    max_retries?: number,           // default 3
    cost_ceiling_usd?: number,      // default 0.10
    allow_escalation?: boolean,     // default true; can re-prompt model for help
    timeout_ms?: number             // default 30_000
  }
}) => {
  success: boolean,
  result: any,              // raw tool result if success
  recovery_applied: Array<{ step: string, succeeded: boolean }>,
  total_attempts: number,
  total_cost_usd: number
}

// Inspect learned patterns
healer.patterns({
  tool?: string,            // filter by tool name
  error_class?: string      // filter by error class
}) => Array<{
  pattern_id: string,
  tool: string,
  error_class: string,      // "rate-limit", "auth-expired", "schema-drift", etc.
  recovery: string,         // the steps that worked
  success_rate: number,     // 0-1 over N uses
  last_used: string
}

// Reset a learned pattern (when the world changes)
healer.forget({ pattern_id: string }) => { deleted: boolean }
```

### Why custom

The self-healing patterns from [[Reflexion Loop]] and the production error-recovery literature (tenacity, circuit breakers, Try-Rewrite-Retry) are general. What M3 specifically unlocks: the model can *generate* the recovery strategy on the fly, in-context, based on the actual error. The healer captures those successful recoveries and turns them into instant patterns for the next occurrence.

A first-time "401 from Google API" gets a full retry-with-OAuth-refresh dance. A second occurrence of the same 401 gets the cached pattern applied in <1ms with zero LLM cost. This is the production engineering that makes long-running agents reliable.

### The implementation hint

- Error classifier = rule-based for common classes (429, 401, 5xx, schema mismatch, timeout) + small LLM fallback for unknown
- Pattern store = local SQLite, keyed by (tool, error_class, error_signature_hash)
- Recovery strategies = templates (auth refresh, exponential backoff, schema repair) + model-generated for novel cases
- Cost ceiling = hard cap per call; aborts the recovery loop and escalates to the user

### Cost

First occurrence: $0.01-0.05 (model-generated recovery). Cached: $0. The break-even is 1-2 uses per pattern. For an EA running the same tool APIs daily, the cache fills fast.

## MCP #5: `self-model-card`

**Purpose:** The agent's own introspection. Reports current capability state, accessible tools, session history, hard-constraint reminders, and operating envelope. The "model card" is for the *model itself*, not for users.

### Tool surface

```typescript
// Current state of the agent
self.what_am_i({
  include?: ("identity" | "tools" | "memory" | "constraints" | "history" | "all")[]
}) => {
  identity: {
    name: string,
    model: string,
    session_id: string,
    session_started_at: string,
    operating_mode: "ea" | "code" | "research" | "uncategorized"
  },
  tools: {
    loaded: string[],         // currently available MCP tools
    recently_used: Array<{ tool: string, last_used: string, call_count: number }>
  },
  memory: {
    vault_chunks_in_context: number,
    session_turns: number,
    approximate_tokens_used: number,
    compaction_due: boolean
  },
  constraints: {
    hard_constraints: string[],    // the SOUL V2 red lines
    session_constraints: string[], // anything added this session
    irreversible_pending: string[] // actions queued but not yet executed
  },
  history: {
    recent_actions: Array<{ tool: string, args_summary: string, timestamp: string, outcome: string }>
  }
}

// What CAN I do right now?
self.can_i({
  action: string             // e.g., "delete file X", "push to git", "send email"
}) => {
  allowed: boolean,
  constraints_hit: string[], // which constraints, if any, block this
  approval_required: boolean,
  approval_path?: string     // how to get approval if needed
}

// Hard reset for introspection
self.audit() => {
  anomalies: string[],       // things that look off
  recent_constraint_proximity: Array<{ constraint: string, distance: number }>
}
```

### Why custom

Without introspection, the model operates blind. It doesn't know what tools it has, what it's done so far, what constraints apply, whether it's approaching a context limit. The `self-model-card` makes the operating envelope explicit and queryable. The `self.can_i` is the pre-flight check for irreversible actions — directly serving the "Reconfirm before any irreversible action" hard constraint.

This is the MCP that enforces the SOUL V2 boundaries at runtime, not just at session start. Every irreversible action gets a `can_i` check first.

### The implementation hint

- Identity + tools = derived from the runtime context
- Memory = computed from the actual prompt token count
- Constraints = loaded from the SOUL/AGENTS files at startup, with session deltas appended
- `can_i` = rule-based classifier (string match on action description + tool name) + LLM fallback for ambiguous cases
- `audit` = the recent-actions log scanned for constraint-proximity patterns (e.g., "3 deletes in 5 minutes, one away from the red line")

### Cost

Negligible. Rule-based for the common cases, <$0.001 for the LLM fallback when needed. The value is in the safety and self-awareness, not the compute.

## Why these five

| MCP | Fills the gap of | M3-specific leverage |
|---|---|---|
| `vault-brain` | Whole-vault semantic search at 1M context | Loads full notes, not chunks |
| `macos-vision-anchor` | Cross-session visual state | Persistent anchors + diff over time |
| `long-context-curator` | Attention-quality at 1M | MSA-aware ordering, marginal-value scoring |
| `tool-self-healer` | Production reliability | Model generates novel recovery strategies, caches them |
| `self-model-card` | Agent self-awareness | Runtime enforcement of hard constraints |

Together they cover: **memory** (vault-brain, macos-vision-anchor), **attention** (long-context-curator), **reliability** (tool-self-healer), **safety** (self-model-card). The four EAs need: memory of what was, attention to what matters, recovery from what fails, and discipline about what's allowed.

## What this is NOT

- Not a replacement for the generic MCP stack (`filesystem`, `git`, `fetch`, etc.). These five are the layer above.
- Not a framework. Each is a small, focused tool. The harness that calls them is the agent, not a library.
- Not implemented. These are design specs. Implementation requires a separate build decision.
- Not the only five. There are more good designs (a `time-anchor` for cross-session continuity, a `privacy-redactor` for sensitive content filtering, a `cost-attribution` for token spend tracking). Those are for v2.

## Connections

- [[00 Overview]] — the project hub
- [[01 Capability Boundaries]] — the M3 capabilities these MCPs exploit
- [[02 Native Execution Layers]] — `macos-vision-anchor` is the implementation
- [[M3 Edge]] — what M3 makes possible
- [[02 Notes/patterns/Paged Memory Pattern|Paged Memory Pattern]] — vault-brain and macos-vision-anchor implement this at the EA level
- [[02 Notes/patterns/Reflexion Loop|Reflexion Loop]] — tool-self-healer is the production-grade version
- [[02 Notes/ideas/Context Engineering 1M|Context Engineering 1M]] — long-context-curator is the design discipline embodied
- [[02 Notes/questions/M3 Bypass Hypothesis|M3 Bypass Hypothesis]] — these MCPs are the user-side bet on the answer being "yes, the capability shift is real"
- [[Mavis EA Workflow]] — current workflow that would consume these MCPs

---
*Design document 2026-06-01. Each MCP is a small focused tool. Total tool surface across all five is ~30 tools, <800 tokens in the prompt. That's the target.*
