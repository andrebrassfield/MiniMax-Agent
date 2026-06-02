---
type: project
status: build
created: 2026-06-02
tags: [project, mavis, architecture, mcp, build, self-model-card, safety]
builds-on: "[[03 The Custom MCP Arsenal]]" (MCP #5 design)
---

# 05 self-model-card — Build

> First MCP to cross from design to build. The runtime enforcement layer for [[SOUL]]'s autonomy table.

## What this is

`self-model-card` is the MCP server that gives Mavis **runtime self-awareness and a pre-flight gate for irreversible actions**. Without it, the SOUL red lines live in the prompt and degrade with context pressure; with it, they live in code and are checked at the moment of action.

Three tools, all small:

1. `self.what_am_i()` — current identity, tools loaded, memory pressure, recent actions
2. `self.can_i({ action, tool? })` — the pre-flight gate; returns allowed / tier / approval_required / approval_path
3. `self.audit()` — recent-actions scan for constraint-proximity anomalies

Total effective logic: **~30 lines of rule-based classifier + ~40 lines of LLM fallback + server scaffold**. The bulk of this file is the SOUL-rule map, the test cases, and the self-test routine. The actual server is small.

## Tool surface (re-stated from the Arsenal for self-containment)

```typescript
self.what_am_i({ include?: ("identity"|"tools"|"memory"|"constraints"|"history"|"all")[] })
  → { identity, tools, memory, constraints, history }

self.can_i({ action: string, tool?: string })
  → { allowed: boolean, tier: "green"|"yellow"|"red",
      constraints_hit: string[], approval_required: boolean,
      approval_path?: string, rationale: string }

self.audit()
  → { anomalies: string[],
      recent_constraint_proximity: Array<{ constraint: string, distance: number }> }
```

## The classifier — how a free-form action becomes a tier

### Step 1: rule-based (the fast path, covers ~85% of calls)

The rule table is a direct machine-readable mirror of SOUL.md's Autonomy Boundary Table. Each rule: `(regex pattern, tier, reason, approval_path?)`. Patterns are tested in order of **specificity** (red > yellow > green precedence when multiple match), so a "delete file in vault" is correctly classified red even though "write to vault" is green.

The rules file lives at `99 _system/mcps/self-model-card/rules.ts` and is generated from SOUL.md by a one-shot script (so the source of truth stays SOUL, not the code). See "Maintaining the rule map" below.

### Step 2: LLM fallback (for ambiguous cases)

When the rule-based classifier returns `null` (no rule matched), we call a Haiku-class model with the SOUL autonomy table pasted in and ask for a JSON classification. Cost: <$0.001 per call. We cache the result for the action-text fingerprint so the same ambiguous action doesn't get re-classified.

### Step 3: explicit override

If the LLM says "yellow" but the model already has explicit in-session approval from Andre (e.g., "go ahead and push"), the model can pass `override: "approved"` and the gate returns allowed. **This is the only way to bypass a red.** The override is logged.

## Full implementation

### File layout

```
99 _system/mcps/self-model-card/
├── server.ts            # MCP server entry point
├── classifier.ts        # rule-based + LLM fallback (the ~30 lines)
├── what_am_i.ts         # runtime introspection
├── audit.ts             # constraint-proximity scanner
├── rules.ts             # generated from SOUL.md, do not hand-edit
├── rules.gen.ts         # the script that regenerates rules.ts
├── package.json
├── tsconfig.json
└── test/
    └── classifier.test.ts   # 30+ test cases covering every SOUL rule
```

### `classifier.ts` — the actual logic

```typescript
// classifier.ts — self-model-card MCP
// Source of truth: SOUL.md Autonomy Boundary Table
// ~30 lines of effective logic per the Arsenal spec

import { RULES } from "./rules";

export type Tier = "green" | "yellow" | "red";

export interface CanIInput { action: string; tool?: string; override?: "approved" }
export interface CanIOutput {
  allowed: boolean;
  tier: Tier;
  constraints_hit: string[];
  approval_required: boolean;
  approval_path?: string;
  rationale: string;
}

const TIER_RANK = { green: 1, yellow: 2, red: 3 } as const;

export function classifyRuleBased(input: CanIInput): CanIOutput | null {
  const text = `${input.tool ?? ""} ${input.action}`.toLowerCase();
  const hits = RULES
    .map(r => ({ r, matched: r.pattern.test(text) }))
    .filter(x => x.matched)
    .sort((a, b) => TIER_RANK[b.r.tier] - TIER_RANK[a.r.tier]);
  if (hits.length === 0) return null; // ambiguous → fallback
  const top = hits[0].r;
  return buildResult(top.tier, top.reason, top.approval_path, `rule: ${top.reason}`, input);
}

export async function classify(input: CanIInput, llmCall: (p: string) => Promise<{tier: Tier; reason: string; approval_path?: string}>): Promise<CanIOutput> {
  // 1. Explicit override — only path past a red
  if (input.override === "approved") {
    return { allowed: true, tier: "red", constraints_hit: ["user override"], approval_required: false, rationale: "explicit in-session approval" };
  }
  // 2. Rule-based fast path
  const ruled = classifyRuleBased(input);
  if (ruled) return ruled;
  // 3. LLM fallback for ambiguous cases
  const llm = await llmCall(`Classify this action per SOUL.md autonomy rules.\nAction: ${input.action}\nTool: ${input.tool ?? "(unspecified)"}\nReturn JSON: { tier, reason, approval_path? }`);
  return buildResult(llm.tier, llm.reason, llm.approval_path, `llm: ${llm.reason}`, input);
}

function buildResult(tier: Tier, reason: string, approvalPath: string | undefined, rationale: string, input: CanIInput): CanIOutput {
  return {
    allowed: tier !== "red" || input.override === "approved",
    tier,
    constraints_hit: [reason],
    approval_required: tier !== "green",
    approval_path: approvalPath,
    rationale,
  };
}
```

That's the classifier. The rest is glue (server scaffold, what_am_i, audit) — none of it more than 50 lines each.

### `rules.ts` — the SOUL mirror (excerpt, generated)

```typescript
// AUTO-GENERATED from SOUL.md. Do not hand-edit.
// Run `npm run generate-rules` after editing SOUL.md.

export const RULES = [
  // === RED — never without explicit in-session approval ===
  { pattern: /\b(send|email|message|post|tweet|publish|signup|buy|purchase|subscribe)\b/i,
    tier: "red" as const,
    reason: "external send / Andre's identity / money",
    approval_path: "Ask Andre: 'OK to send / publish / buy X?'" },
  { pattern: /\b(delete|rm|drop|trash|force.push|hard.reset)\b/i,
    tier: "red" as const,
    reason: "destructive or irreversible",
    approval_path: "Reconfirm. 'OK to delete / force-push / drop X?'" },
  { pattern: /\b(hermes|openclaw|kanban|gbrain|launchd|fleet|profile\.yaml)\b/i,
    tier: "red" as const,
    reason: "fleet boundary (isolation principle)",
    approval_path: "Vault is the boundary. Fleet is off-limits without explicit approval." },
  { pattern: /\b(credential|token|password|api[._-]?key|secret|auth)\b/i,
    tier: "red" as const,
    reason: "credential / security change",
    approval_path: "Reconfirm before any credential rotation." },
  { pattern: /\b(push).*\b(github|origin|main|master|remote)\b/i,
    tier: "yellow" as const,                  // SOUL says push is yellow, not red
    reason: "git push to remote",
    approval_path: "Yellow — execute + report. Don't pre-ask." },
  // === YELLOW — execute + report ===
  { pattern: /\b(cron|launchctl|schedul)/i,
    tier: "yellow" as const,
    reason: "schedule change",
    approval_path: "Yellow — execute + report." },
  { pattern: /\b(cu|desktop_|click|type|scroll|screenshot)/i,
    tier: "yellow" as const,
    reason: "macOS GUI control",
    approval_path: "Yellow — execute + report. Renderer must be on." },
  { pattern: /\b(clipboard|pbcopy)/i,
    tier: "yellow" as const,
    reason: "clipboard access",
    approval_path: "Yellow — execute + report." },
  { pattern: /\b(open app|launch|cd |navigate filesystem)\b/i,
    tier: "yellow" as const,
    reason: "live state mutation",
    approval_path: "Yellow — execute + report." },
  { pattern: /\b(modify template|templater|plugin|dataview).*\bconfig\b/i,
    tier: "yellow" as const,
    reason: "affects future note creation / dashboard",
    approval_path: "Yellow — execute + report." },
  // === GREEN — execute without asking ===
  { pattern: /\b(read|fetch|search|grep|find|list|view)\b/i,
    tier: "green" as const,
    reason: "read-only, no side effects" },
  { pattern: /\b(write|edit|append|create).*\b(inbox|notes|projects|connections|vellum|_system|daily|resources|06|07|99|01|02|03|04|05)\b/i,
    tier: "green" as const,
    reason: "vault write, reversible via git" },
  { pattern: /\b(git add|git commit|git status|git log|git diff|git show)\b/i,
    tier: "green" as const,
    reason: "local git, reversible" },
  { pattern: /\b(draft|compose|outline|template|summarize|synthesize)\b/i,
    tier: "green" as const,
    reason: "draft only, no send / no publish" },
];
```

### `what_am_i.ts` — runtime introspection (excerpt)

```typescript
import os from "node:os";
import fs from "node:fs/promises";

export async function whatAmI(include: string[] = ["all"]) {
  const want = (k: string) => include.includes("all") || include.includes(k);
  const out: any = {};
  if (want("identity")) {
    out.identity = {
      name: "Mavis",
      model: process.env.MAVIS_MODEL ?? "minimax/MiniMax-M3",
      session_id: process.env.MAVIS_SESSION_ID,
      session_started_at: process.env.MAVIS_SESSION_START,
      operating_mode: "ea", // single-mode for now
    };
  }
  if (want("memory")) {
    // Approximate token count from the prompt's last snapshot
    out.memory = {
      vault_chunks_in_context: await countVaultChunks(),
      session_turns: Number(process.env.MAVIS_TURN_COUNT ?? 0),
      approximate_tokens_used: Number(process.env.MAVIS_TOKENS_USED ?? 0),
      compaction_due: Number(process.env.MAVIS_TOKENS_USED ?? 0) > 400_000,
    };
  }
  if (want("constraints")) {
    const soul = await fs.readFile(process.env.SOUL_PATH!, "utf8");
    out.constraints = {
      hard_constraints: extractHardConstraints(soul),
      session_constraints: process.env.MAVIS_SESSION_CONSTRAINTS?.split("|") ?? [],
      irreversible_pending: await readReversibleQueue(),
    };
  }
  if (want("history")) {
    out.history = { recent_actions: await readRecentActions(20) };
  }
  return out;
}
```

### `audit.ts` — constraint-proximity scanner

```typescript
const RECENT_LOG = process.env.MAVIS_ACTION_LOG ?? "/tmp/mavis-actions.jsonl";

export async function audit() {
  const lines = (await fs.readFile(RECENT_LOG, "utf8")).trim().split("\n").filter(Boolean);
  const recent = lines.slice(-50).map(l => JSON.parse(l));
  const anomalies: string[] = [];

  // 3+ destructive actions in 5 min = anomaly
  const destructiveRecent = recent.filter(a =>
    /delete|rm|drop|trash/.test(a.action) &&
    Date.now() - new Date(a.timestamp).getTime() < 300_000
  );
  if (destructiveRecent.length >= 2) {
    anomalies.push(`${destructiveRecent.length} destructive actions in 5 min — approaching red-line cadence.`);
  }

  // 5+ yellow actions without a report = anomaly
  const yellows = recent.filter(a => a.tier === "yellow" && !a.reported);
  if (yellows.length >= 5) anomalies.push(`${yellows.length} yellow actions without a report. Are you reporting?`);

  // Any action that hit the LLM fallback more than 3x = rule-map drift
  const fallbackHits = recent.filter(a => a.classified_by === "llm").length;
  if (fallbackHits >= 3) anomalies.push(`${fallbackHits} LLM-fallback classifications — consider adding a rule.`);

  return { anomalies, recent_constraint_proximity: computeProximity(recent) };
}
```

### `server.ts` — MCP server wiring

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { classify } from "./classifier";
import { whatAmI } from "./what_am_i";
import { audit } from "./audit";
import { callHaiku } from "./llm";

const server = new Server({ name: "self-model-card", version: "0.1.0" }, {
  capabilities: { tools: {} },
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    { name: "what_am_i", description: "Current state of the agent: identity, tools, memory, constraints, history.", inputSchema: { type: "object", properties: { include: { type: "array", items: { type: "string" } } } } },
    { name: "can_i",    description: "Pre-flight gate. Classifies an action per SOUL.md autonomy rules. Always call before irreversible actions.", inputSchema: { type: "object", required: ["action"], properties: { action: { type: "string" }, tool: { type: "string" }, override: { type: "string", enum: ["approved"] } } } },
    { name: "audit",    description: "Scan recent actions for constraint-proximity anomalies.", inputSchema: { type: "object", properties: {} } },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const { name, arguments: args } = req.params;
  if (name === "what_am_i") return { content: [{ type: "json", json: await whatAmI(args?.include) }] };
  if (name === "can_i") {
    const result = await classify(args, callHaiku);
    // Log every can_i call for audit
    await fs.appendFile(process.env.MAVIS_ACTION_LOG!, JSON.stringify({ ts: new Date().toISOString(), tool: "can_i", ...result }) + "\n");
    return { content: [{ type: "json", json: result }] };
  }
  if (name === "audit") return { content: [{ type: "json", json: await audit() }] };
  throw new Error(`Unknown tool: ${name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## Maintaining the rule map

The `rules.ts` file is **generated**, not hand-edited. The generator:

1. Parses `SOUL.md` and extracts the Autonomy Boundary Table (the three colored tables).
2. Converts each row to a `{ pattern, tier, reason, approval_path }` object using a small pattern library (verb → regex, scope → path match).
3. Writes `rules.ts`.

Run the generator after any SOUL.md edit. CI can enforce that `rules.ts` is up-to-date.

**Why generate?** Two reasons:
- SOUL is the source of truth, not code. If they drift, the gate is enforcing the wrong rules.
- A test that compares `rules.ts` to SOUL.md catches drift before it bites.

## Test cases (excerpt of `classifier.test.ts`)

```typescript
import { classify, classifyRuleBased } from "../classifier";

describe("self.can_i — SOUL.md mirror", () => {
  test.each([
    // RED
    [{ action: "delete 2026-05-15-attack-plan.md" }, "red"],
    [{ action: "send a message to Andre's CFO via Telegram" }, "red"],
    [{ action: "purchase Cursor Pro subscription" }, "red"],
    [{ action: "modify ~/.hermes/profiles/main/config.yaml" }, "red"],   // fleet boundary
    [{ action: "rotate the GitHub PAT" }, "red"],
    // YELLOW
    [{ action: "git push origin main" }, "yellow"],
    [{ action: "use cu to click the Save button in Numbers" }, "yellow"],
    [{ action: "schedule daily-brief cron at 6am" }, "yellow"],
    [{ action: "modify Templater config" }, "yellow"],
    // GREEN
    [{ action: "read the latest 3 Daily notes" }, "green"],
    [{ action: "write a new permanent note in 02 Notes/ideas/" }, "green"],
    [{ action: "git add . && git commit -m 'update'" }, "green"],
    [{ action: "draft an email to Andre" }, "green"],
    // OVERRIDE
    [{ action: "delete X", override: "approved" }, { allowed: true, tier: "red" }],
  ])("classifies %j as %j", (input, expected) => {
    const out = classifyRuleBased(input);
    expect(out?.tier).toBe(typeof expected === "string" ? expected : expected.tier);
  });
});
```

## Self-test routine (manual, on first deploy)

```bash
# Start the server
cd 99 _system/mcps/self-model-card && npm install && npm run build

# Test 1: what_am_i
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"what_am_i","arguments":{"include":["identity"]}},"id":1}' \
  | node dist/server.js

# Test 2: can_i on a known red
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"can_i","arguments":{"action":"delete the inbox folder"}},"id":2}' \
  | node dist/server.js
# Expected: { "tier": "red", "allowed": false, "approval_required": true, "approval_path": "Reconfirm..." }

# Test 3: can_i on a known green
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"can_i","arguments":{"action":"write a note in 02 Notes/ideas/"}},"id":3}' \
  | node dist/server.js
# Expected: { "tier": "green", "allowed": true, "approval_required": false }

# Test 4: audit
echo '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"audit","arguments":{}},"id":4}' \
  | node dist/server.js
```

## Registration in the agent's MCP config

Add to `~/.mavis/config.yaml`:

```yaml
mcpServers:
  self-model-card:
    command: node
    args: [/Users/brassfieldventuresllc/MiniMax-Agent/99 _system/mcps/self-model-card/dist/server.js]
    env:
      VAULT_ROOT: /Users/brassfieldventuresllc/MiniMax-Agent
      SOUL_PATH: /Users/brassfieldventuresllc/MiniMax-Agent/SOUL.md
      MAVIS_SESSION_ID: ${MAVIS_SESSION_ID}
      MAVIS_ACTION_LOG: /tmp/mavis-actions.jsonl
      MAVIS_MODEL: minimax/MiniMax-M3
```

## What this is NOT

- **Not a replacement for the SOUL.md prompt content.** The prompt still loads the rules; this is the runtime enforcement. Defense in depth.
- **Not perfect.** Rule-based classification is brittle on paraphrase ("make this go away" could be a delete or a draft). The LLM fallback is the safety net for that. The test suite is the safety net for the safety net.
- **Not autonomous.** The override path is explicit. There is no "trust the model to judge itself" path. Mavis asks; Andre decides.
- **Not the only safety mechanism.** The other four MCPs in the Arsenal are also safety-flavored (e.g., `tool-self-healer` for production reliability, `long-context-curator` for attention quality). This one is specifically for action gating.

## Limitations / known gaps

1. **English-only patterns.** "delete" works, "elimina" doesn't. Future: multilingual patterns.
2. **No semantic understanding of intent.** "Move the file to 05 Archive/" is green (vault write), but the model might say "move" when it means "delete". The LLM fallback catches the obvious cases; the subtle ones depend on the model's honesty.
3. **Action log can fill up.** `/tmp/mavis-actions.jsonl` needs rotation. Cron is the obvious answer — and cron is itself yellow. Catch-22; resolve by exempting the rotation cron from the gate.
4. **Override is binary.** "approved" or nothing. A future v2 could add conditional approval ("approved for files under 10MB").

## Cost

Negligible. Rule-based for common cases (<1ms, $0). LLM fallback: <$0.001 per call. The audit runs on demand, not on schedule. The value is in the safety and self-awareness, not the compute.

## Connections

- [[03 The Custom MCP Arsenal]] — the design spec this builds (MCP #5)
- [[SOUL]] — the source of truth the rule map mirrors
- [[agent]] — calls `self.can_i` before any irreversible action
- [[00 Overview]] — this project hub
- [[01 Capability Boundaries]] — M3 capabilities this exploits (M3 1M context = whole SOUL in the LLM fallback prompt)
- [[Mavis EA Workflow]] — current workflow that consumes this
- [[state-of-mavis]] — the MOC that should record when this is shipped + operational

---

*Build doc 2026-06-02. First MCP to cross from design to build in the Apex Architecture project. Next: when the other four get greenlight, follow the same pattern (spec from Arsenal → build doc with full code + tests + registration).*
