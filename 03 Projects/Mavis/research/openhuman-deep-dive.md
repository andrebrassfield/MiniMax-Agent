# openhuman — Deep Engineering Brief

**Repo:** https://github.com/tinyhumansai/openhuman
**Author org:** tinyhumansai (Steven Enamakel / @senamakel)
**Latest release:** v0.57.40 (2026-06-12); Cargo version in main = 0.57.41
**License:** **GNU GPL-3.0** — strong copyleft. **Read §6 before considering fleet wiring.**
**Audit date:** 2026-06-13

> **Headline:** openhuman is a 4-month-old, ~32k-star **Tauri v2 desktop app** wrapping a Rust "core" (`openhuman-core`) that boots a tokio task **in-process** with the UI, exposes a JSON-RPC HTTP server on `127.0.0.1:7788`, **and** a fully-spec MCP server (stdio + Streamable HTTP). Its primary "agent" capability is a managed backend (Composio for 118+ OAuth integrations + their own chat backend at `https://api.tinyhumans.ai`); local LLM mode exists but is **deliberately throttled** to a 1B-param gemma model with a small, hard-coded allowlist. **The MCP server is the only first-class integration surface that a closed fleet could realistically call without shipping the whole Tauri shell.** Everything else is managed-service-bound.

---

## 1. What openhuman actually is

**The product pitch (README, current):**
> "OpenHuman is your Personal AI super intelligence: local memory, managed services where needed, simple and powerful."
> "OpenHuman is an open-source agentic assistant designed to integrate with you in your daily life." (README, lines around "What is OpenHuman?")

**The earlier pitch (still present in `gitbooks/developing/architecture.md`):**
> "OpenHuman is a cross-platform communication and automation platform purpose-built for the cryptocurrency ecosystem."

There is a clear **branding drift** in the last ~30 days: the architecture book and the desktop binary still call this a "super assistant for crypto communities," while the GitHub README, marketing page, and recent commits (e.g. PR #3632 "top-level agent profiles — soul, memory, skills, MCP, connectors") reposition it as a **general personal-AI agent harness** competing with Claude Cowork / Hermes / OpenClaw (the README's own comparison table is explicit on this). The actual product is closer to **a managed personal-AI agent with an optional local-OSS mode**, not a self-hosted crypto tool.

**Who it's for, per the README's own table** (`README.md`, "OpenHuman vs Other Agent Harnesses"):

| Dimension      | openhuman's stated edge                                  |
| -------------- | ------------------------------------------------------- |
| Open-source    | "✅ GNU"                                                 |
| Start          | "✅ Clean UI, minutes" (Tauri desktop, no terminal)      |
| Cost           | "✅ One sub + TokenJuice" (i.e. their managed service)   |
| Memory         | "🚀 Memory Tree + Obsidian vault"                        |
| Integrations   | "🚀 118+ via OAuth" (via Composio, proxied through backend) |
| Auto-fetch     | "✅ 20-min sync into memory"                             |
| API sprawl     | "✅ One account" (their account)                         |
| Model routing  | "✅ Built-in" (the backend picks reasoning/fast/vision)  |
| Native tools   | "✅ Code + search + scraper + voice"                     |

**Target user:** A non-technical person who wants a desktop AI that "knows them" — their inbox, calendar, repos, Slack, Notion, Gmail, etc. — without writing config. The architecture doc explicitly says the agent's goal is "**context in minutes, not weeks**" by polling all those data sources on a 20-minute loop and compressing into a local Obsidian-style vault.

**The product problem it solves:** Today, every agent starts cold. openhuman's claim is that by ingesting 118+ OAuth data sources on a 20-min loop, compressing into a local Obsidian-compatible markdown vault, and exposing this as a Memory Tree to the agent's prompt, the agent *has the user's working context on day one*.

**My opinion, grounded:** This is a credible wedge — the **Karpathy obsidian-wiki loop** is a real pattern — but **the wedge is the managed-service OAuth mesh, not the local LLM**. If you bring your own model, you bring a 1B gemma and lose most of the integration story. The "local-first" framing in the README is honest (data is stored locally) but the *inference* is a managed cloud path by default. Local AI mode exists, is opt-in, and is **intentionally narrow** (see §3).

---

## 2. Architecture — module-by-module

### 2.1 What kind of system is it?

It is **three things stapled together**, not one. From `AGENTS.md` and `gitbooks/developing/architecture.md`:

1. **A Tauri v2 desktop application** (Windows, macOS, Linux) — React 19 + Redux Toolkit + Vite, packaged as `.dmg` / `.msi` / `.deb` / `.AppImage` / `.tar.gz` with a vendored Chromium Embedded Framework (CEF) for embedded provider webviews (Gmail, LinkedIn, Google Meet — see `AGENTS.md` "CEF child webviews — no new JS injection").
2. **A Rust "core" library + CLI binary** (`openhuman_core` lib + `openhuman-core` binary) that runs **as a tokio task inside the Tauri process** (not as a sidecar — that was removed in PR #1061 per `AGENTS.md:21`). The core owns the domain logic, the JSON-RPC server, Socket.IO, persistence (SQLite via `rusqlite`), crypto, MCP server, and a managed Node.js runtime for skill helpers.
3. **A managed cloud backend** at `https://api.tinyhumans.ai` (configurable via `BACKEND_URL`) that handles account, billing, model routing for the "good" models (the README says "By default, model routing uses the OpenHuman backend to select and proxy the right LLM"), Composio OAuth, and Socket.IO event fan-out.

The README's "Local + managed services, upfront" callout is the most important line:

> "OpenHuman stores its Memory Tree, Obsidian-style Markdown vault, workspace config, and local runtime state on your machine. The default managed experience still uses OpenHuman-hosted services for account sign-in, model routing, web search proxying, and managed integration/OAuth flows through the Composio connector layer. **Choose custom/local settings if you want to bring your own model, search, or Composio credentials; some real-time triggers and hosted features still require the managed backend.**"

**Key file:line citations:**

| Claim                                              | File:Line (or URL)                                                   |
| -------------------------------------------------- | -------------------------------------------------------------------- |
| Core runs in-process, not sidecar                  | `AGENTS.md:21-24` ("Core runs in-process as a tokio task (sidecar removed PR #1061)") |
| Tauri v2 + React + Rust core stack                 | `AGENTS.md:1-3`                                                       |
| Rust core is `openhuman_core` lib + binary          | `Cargo.toml:1-7` (`[package] name = "openhuman"`, `[lib] name = "openhuman_core"`, `[[bin]] name = "openhuman-core" path = "src/main.rs"`) |
| Node.js runtime version                            | `gitbooks/developing/architecture.md` "Skills Runtime Engine" table — `Managed Node version = v22.11.0` |
| Vendor: `pnpm@10.10.0`, Node 24+                   | `README.md` "Contributing from source" + `package.json:3`            |
| Backend default URL                                | `.env.example:14-15` (`# BACKEND_URL=https://api.tinyhumans.ai`)     |
| Default model routing                              | `.env.example` + `README.md` ("model routing uses the OpenHuman backend to select and proxy the right LLM") |
| MCP server transport options                        | `src/openhuman/mcp_server/stdio.rs:18-45` (`--transport stdio` / `--transport http`) |
| JSON-RPC default port                              | `.env.example:38-41` (`OPENHUMAN_CORE_PORT=7788`, `OPENHUMAN_CORE_RPC_URL=http://127.0.0.1:7788/rpc`) |
| MCP default port (HTTP mode)                       | `src/openhuman/mcp_server/stdio.rs:21` (`bind_host = "127.0.0.1"`, `port: u16 = 9300`) |
| 118+ integrations via Composio                     | `src/openhuman/composio/mod.rs:1-3` ("backend-proxied access to 1000+ OAuth integrations") |
| Composio runs through their backend                | `src/openhuman/composio/mod.rs:7-10` ("The core does **not** hit the Composio API directly — everything goes through the backend.") |

### 2.2 Repository layout (concrete, verified)

```
openhuman/                                  # monorepo, pnpm + cargo workspaces
├── app/                                    # pnpm workspace "openhuman-app"
│   ├── src/                                # Vite + React 19 + Redux Toolkit
│   ├── src-tauri/                          # Tauri v2 shell
│   │   ├── src/                            # core_process.rs, core_rpc.rs, ...
│   │   ├── vendor/tauri-cef/               # vendored tauri-cli (CEF-aware)
│   │   ├── capabilities/, permissions/     # Tauri ACL
│   │   └── tauri.conf.json
│   └── test/                               # Vitest + WDIO E2E
├── src/                                    # root Rust crate
│   ├── main.rs                             # `openhuman-core` binary entry — Sentry init, CLI dispatch
│   ├── lib.rs
│   ├── core/                               # TRANSPORT ONLY (no business logic)
│   │   ├── cli.rs                          # ASCII banner, subcommand dispatch
│   │   ├── jsonrpc.rs                      # HTTP server, RPC dispatch
│   │   ├── dispatch.rs                     # legacy dispatch (controllers migrate out)
│   │   ├── all.rs                          # aggregates controller schemas
│   │   ├── event_bus/                      # pub/sub + native req/resp
│   │   ├── auth.rs, logging.rs, observability.rs, ...
│   │   └── socketio.rs                     # Rust Engine.IO + Socket.IO client
│   ├── openhuman/                          # 90+ domain modules
│   │   ├── inference/                      # NEW: unified inference root
│   │   │   ├── local/                      # Ollama / LM Studio / Whisper / Piper
│   │   │   │   ├── mod.rs                  # was src/openhuman/local_ai/ — moved
│   │   │   │   ├── ollama.rs, lm_studio.rs
│   │   │   │   ├── install.rs, install_piper.rs, install_whisper.rs
│   │   │   │   ├── model_requirements.rs, profile.rs, service.rs
│   │   │   │   └── ops.rs, schemas.rs, core.rs
│   │   │   ├── provider/                   # cloud + local provider trait
│   │   │   ├── voice/                      # STT + TTS impls
│   │   │   ├── http/                       # OpenAI-compatible /v1/chat/completions endpoint
│   │   │   ├── model_ids.rs, model_context.rs, presets.rs
│   │   │   ├── device.rs, paths.rs, parse.rs, sentiment.rs, types.rs
│   │   │   └── ops.rs, schemas.rs
│   │   ├── mcp_server/                     # FIRST-CLASS MCP server
│   │   │   ├── mod.rs                      # tool_specs(), exports run_stdio / run_http
│   │   │   ├── stdio.rs                    # `openhuman-core mcp` CLI
│   │   │   ├── http.rs                     # Streamable HTTP + SSE
│   │   │   ├── protocol.rs                 # JSON-RPC 2.0 + MCP 2025-11-25
│   │   │   ├── tools.rs, resources.rs, session.rs, write_dispatch.rs
│   │   ├── composio/                       # 1000+ OAuth toolkit proxy (backend-routed)
│   │   ├── agent/, agent_experience/, agent_meetings/, agent_memory/,
│   │   │   agent_orchestration/, agent_registry/, agent_tool_policy/
│   │   ├── memory/                         # memory_tree, memory_search, memory_store,
│   │   │   # memory_archivist, memory_conversations, memory_entities,
│   │   │   # memory_graph, memory_queue, memory_diff, memory_sync,
│   │   │   # memory_sources, memory_tools (10+ sub-domains)
│   │   ├── mcp_client/, mcp_registry/, mcp_audit/   # MCP infra
│   │   ├── channels/                       # Discord, Slack, Telegram, WhatsApp, etc.
│   │   ├── meet/, meet_agent/              # Google Meet voice/video agent
│   │   ├── webview_accounts/, webview_apis/, webview_notifications/
│   │   ├── javascript/                     # managed Node.js runtime bridge
│   │   ├── runtime_node/                   # resolved Node 22.11.0
│   │   ├── runtime_python/                 # python-build-standalone resolver
│   │   ├── security/                       # SecurityPolicy + sandbox backends
│   │   │   # (docker, bubblewrap, firejail, landlock, detect)
│   │   ├── tokenjuice/                     # token compression layer
│   │   ├── wallet/                         # BTC / ETH / SOL / TRX signing
│   │   ├── voice/, audio_toolkit/
│   │   ├── accessibility/                  # UIA / AX bindings
│   │   ├── cron/                           # 5s tick scheduler
│   │   ├── socket/                         # Engine.IO v4 + Socket.IO v4 client
│   │   ├── skills/, skill_runtime/, skill_registry/
│   │   └── ...90+ total
│   ├── api/                                # HTTP route handlers (Rust)
│   ├── rpc/                                # RPC type registry
│   └── bin/                                # slack-backfill, gmail-backfill-3d,
│                                           # memory-tree-init-smoke, inference-probe,
│                                           # test-mcp-stub
├── packages/tauri-plugin-ptt/               # Swift PTT plugin (iOS)
├── docs/, gitbooks/                        # user + dev docs (gitbook)
├── Cargo.toml                              # root crate
├── pnpm-workspace.yaml                     # [app, packages/tauri-plugin-ptt]
├── rust-toolchain.toml                     # pinned 1.93.0 (matrix-sdk)
├── Dockerfile, docker-compose.yml          # headless core deploy
└── .env.example
```

**Languages (GitHub API):** Rust 61.6%, TypeScript 35.5%, JavaScript 1.5%, Shell 1.1%, CSS/HTML 0.2%.

### 2.3 How it boots

- **Desktop:** user double-clicks the .app / .msi / .dmg / .deb. The Tauri shell (`app/src-tauri/`) starts. `core_process::CoreProcessHandle` (`AGENTS.md`) launches a tokio task in-process running `openhuman_core::run_core_from_args(&["serve"])` (effectively). The core binds to `127.0.0.1:7788` (default `OPENHUMAN_CORE_PORT`) and exposes:
  - `POST /rpc` (HTTP JSON-RPC, bearer-authed)
  - `GET /health`, `GET /schema`, `GET /events` (per `AGENTS.md` "Platform notes")
  - Socket.IO on the same port (unless `--jsonrpc-only`)
- **Tauri → Core auth:** Tauri generates a fresh per-launch 32-byte hex bearer (`core_rpc_token` Tauri command) and passes it in-memory via `run_server_embedded_with_ready(rpc_token: Some(_))`. The renderer reads the bearer via the `core_rpc_token` Tauri command. No `OPENHUMAN_CORE_TOKEN` env var is needed in the desktop path. (`AGENTS.md:21-24`)
- **Headless / Docker / CLI:** `openhuman-core serve [--host ...] [--port ...] [--jsonrpc-only]` reads `OPENHUMAN_CORE_TOKEN` from env (Docker sets this) or auto-generates one and writes it to `${OPENHUMAN_WORKSPACE}/core.token` 0o600 (workstation default). The `openhuman-core mcp` subcommand boots the **MCP server only** — same core, different surface — see §4.
- **CLI dispatcher** (`src/core/cli.rs`): subcommands are `run`/`serve`, `call` (single RPC), `mcp`/`mcp-server`, `memory`, `agent`, `subconscious`/`sub`, `screen-intelligence`, `text-input`, `tree-summarizer`, `sentry-test`, then the generic `openhuman <namespace> <function>` path that introspects the controller registry.

### 2.4 Request lifecycle (desktop chat → model)

```
User types in React UI
   → Redux dispatch
   → Tauri IPC: invoke("core_rpc_relay", { method, params, requestId })
   → Tauri host POSTs http://127.0.0.1:7788/rpc with Authorization: Bearer <token>
   → core/jsonrpc.rs parses, validates origin + token
   → all.rs dispatches by namespace.function
   → domain/ops.rs runs (e.g. agent.harness.session::runtime::run_single)
      ├─ builds prompt (Memory Tree + tool catalog from tool_registry)
      ├─ calls inference::provider (cloud or local)
      ├─ on tool_call: routes through SecurityPolicy → sandbox backend
      └─ streams events back via Socket.IO bridge to the UI
```

This is **not** a single RPC thread per turn — AGENTS.md + commit #3633 ("Agent inference now runs concurrently") confirm the agent loop runs on tokio with worker stack bumped to `AGENT_WORKER_STACK_BYTES` to avoid the SIGABRT caused by deep async state machines (a comment in `cli.rs:122-129` calls this out as load-bearing).

---

## 3. Model requirements

### 3.1 Local mode — model allowlist, hard-coded

The local model surface is **deliberately narrow**. The defaults and allowlists are in `src/openhuman/inference/model_ids.rs:1-30` and are enforced everywhere:

```rust
pub(crate) const DEFAULT_OLLAMA_MODEL:        &str = "gemma3:1b-it-qat";
pub(crate) const DEFAULT_OLLAMA_VISION_MODEL: &str = "";                    // VISION DISABLED
pub(crate) const DEFAULT_LOW_VISION_MODEL:    &str = "moondream:1.8b-v2-q4_K_S";
pub(crate) const DEFAULT_OLLAMA_EMBED_MODEL:  &str = "bge-m3";

const MVP_ALLOWED_CHAT_MODELS:    &[&str] = &["gemma3:1b-it-qat", "gemma4:e4b-it-q8_0"];
const MVP_ALLOWED_VISION_MODELS: &[&str] = &[""];   // only disabled
const MVP_ALLOWED_EMBEDDING_MODELS: &[&str] = &["bge-m3", "all-minilm:latest"];
```

The `enforce_mvp_chat_allowlist` function (line 30) **silently redirects any non-allowlisted Ollama model to `gemma3:1b-it-qat`** with a `tracing::warn!`. The unit tests at the bottom of the file confirm the design intent:

- `gemma3:4b-it-qat` → redirected to default (rejected)
- `gemma3:270m-it-qat` → redirected to default (rejected)
- `gemma4:e4b` (without `-it-q8_0`) → redirected to default (rejected)
- `moondream` → vision is disabled (only `""` allowed in `MVP_ALLOWED_VISION_MODELS`)

**LM Studio path bypasses the allowlist** (lines 60-72): if `local_ai.provider = "lm_studio"`, `effective_chat_model_id` passes the user-supplied model ID through unchanged. The test `chat_model_allows_custom_ids_for_lm_studio` at `model_ids.rs:175-184` documents this. The contract is clear: **Ollama = MVP-only gemma; LM Studio = bring your own**.

**STT (whisper) and TTS (piper) defaults** (lines 120-136):
- `ggml-base-q5_1.bin` (Whisper)
- `en_US-lessac-medium` (Piper TTS)
- `q4` quantization (any other value lowercased)

**Ecosystem:** the local path is **Ollama** (`OPENHUMAN_OLLAMA_BASE_URL`, default `http://localhost:11434`) or **LM Studio** (`OPENHUMAN_LM_STUDIO_BASE_URL`, default `http://localhost:1234/v1` — OpenAI-compatible). The two providers are wired in `inference/local/ollama.rs` and `inference/local/lm_studio.rs` respectively. **The README and `.env.example` both say "Ollama only" for "supported on-device workloads"** — LM Studio is an opt-in escape hatch.

**Not local (managed only):** the "good" reasoning/fast/vision models that the README's comparison table brags about are the backend's picks, proxied through `https://api.tinyhumans.ai`. Per the README: "By default, model routing uses the OpenHuman backend to select and proxy the right LLM for each workload (reasoning, fast, or vision). One subscription includes all models." The 1B gemma local fallback is positioned as a degraded mode, not a peer.

### 3.2 Cloud / managed model surface

The cloud path is opaque from the open-source repo — model names, context windows, and pricing are all hidden behind the `BACKEND_URL` and `OPENHUMAN_MODEL` env var. `OPENHUMAN_MODEL` is the user override; the backend picks the actual model. There is no model-config file in the repo that lists what models are available; this is a closed list on their side.

### 3.3 What model does what

| Role             | Local (default)             | Cloud                            |
| ---------------- | --------------------------- | -------------------------------- |
| **Chat / agent** | `gemma3:1b-it-qat` (Ollama) | backend-selected, proxied         |
| **Embedding**    | `bge-m3` (1024-dim, 8192 ctx) | backend (post-cloud-embed unification) |
| **Vision**       | **disabled** (empty string) | backend                          |
| **STT**          | `ggml-base-q5_1.bin` (whisper) | managed (ElevenLabs is also wired per README) |
| **TTS**          | `en_US-lessac-medium` (Piper)  | managed (ElevenLabs per README) |
| **Token compression** | local (TokenJuice)        | local (always)                   |

**Context window for chat:** the model_context module (`inference/model_context.rs`) gates routing based on `context_window_for_model` (a per-model lookup), and `MIN_CONTEXT_TOKENS` is enforced. Specific window values were not in the read portion of the file; **NOT FOUND** in my searches what the chat model's advertised context is — model_requirements.rs is the file but I did not fetch it. The .env.example sets `OPENHUMAN_MAX_ACTIONS_PER_HOUR=20` as a default safety cap.

**Memory chunking (per the architecture doc):** "512 tokens per chunk, 64-token overlap." Embeddings hybrid: "70% vector similarity + 30% FTS5 full-text."

### 3.4 Is it model-agnostic?

**Mostly yes via an interface, mostly no via a hard allowlist.**

- The `inference/provider` module is the trait surface — cloud and local implement the same provider trait. So a new model is "free" in principle.
- In practice: Ollama allowlist is hard-coded to two model IDs. LM Studio is the BYO escape hatch. Cloud picks are closed.
- The README's claim of "Model routing: ✅ Built-in" refers to **the backend's** routing, not a routing layer you control.

---

## 4. Integration surface

This is the most important section for a fleet-integration decision.

### 4.1 The two public servers

openhuman-core exposes **two distinct services** you can call from another agent system:

#### (A) **MCP server** — `openhuman-core mcp`

The **first-class integration surface**. Per `src/openhuman/mcp_server/mod.rs:1-15`:

> "MCP server for exposing a curated openhuman tool surface.
> Opt-in via `openhuman-core mcp` (stdio) or `openhuman-core mcp --transport http`.
> Stdio mode writes newline-delimited JSON-RPC to stdout; HTTP mode speaks Streamable HTTP + SSE on a local bind address."

**Transports** (`src/openhuman/mcp_server/stdio.rs:18-82`):
- **stdio** (default): newline-delimited JSON-RPC 2.0 on stdin/stdout. Designed for Claude Desktop / Cursor / Windsurf / Zed subprocess pattern.
- **http**: Streamable HTTP + SSE on `127.0.0.1:9300` (default). Optional `--auth-token <token>` for bearer auth.

**MCP protocol version:** `LATEST_PROTOCOL_VERSION = "2025-11-25"`; supported: `["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"]` (`src/openhuman/mcp_server/protocol.rs:3-7`).

**Tools exposed** (`src/openhuman/mcp_server/stdio.rs:128-138` and tests in `protocol.rs`):
```
core.list_tools, core.tool_instructions
agent.list_subagents, agent.run_subagent
memory.search, memory.recall, memory.store, memory.note
tree.read_chunk, tree.browse, tree.top_entities, tree.list_sources, tree.tag
searxng_search             (only when OPENHUMAN_SEARXNG_ENABLED=true)
```
Plus **resources** at `openhuman://prompts/*` (markdown prompt catalog) and the standard `tools/list`, `tools/call`, `resources/list`, `resources/read`, `ping`, `initialize`.

**Security note:** `agent.run_subagent` is the **only** tool that is not read-only — its `readOnlyHint: false, destructiveHint: true` are advertised to clients (per `mod.rs:5-10`). Everything else is `ToolOperation::Read` gated through `SecurityPolicy`.

**Client detection:** the server parses `clientInfo.name` from `initialize` and sets `McpSession::source_type` to `mcp:claude-desktop`, `mcp:cursor`, `mcp:windsurf`, `mcp:zed-*`, or bare `mcp` for unknown clients (test cases in `protocol.rs:235-313`).

#### (B) **JSON-RPC HTTP server** — `openhuman-core serve`

`POST http://127.0.0.1:7788/rpc` with `Authorization: Bearer <token>`. The full RPC namespace is registered via `src/core/all.rs` aggregating `all_controller_schemas` from every domain. CLI introspection: `openhuman-core` with no args prints the namespace list. Namespaces include (from `mod.rs` tree and CLI help):

- `agent.*` — chat, list_subagents, run_subagent, prompts, etc.
- `memory.*` — search, recall, store, note, plus the memory_tree / memory_sync sub-namespaces
- `inference.*` — local + cloud model management (the README's "Legacy alias layer" maps old `local_ai_*` calls to `inference.*`)
- `composio.*` — list toolkits, manage connections, list tools, execute actions (all backend-routed)
- `mcp_*` — MCP server management from within the same process
- `cron.*`, `credentials.*`, `cost.*`, `device.*`, `wallet.*`, `voice.*`, `webview_*`, `update.*`, ...
- And ~60 more namespaces (the `src/openhuman/` tree has 90+ domain modules; one CLI help line per namespace).

**Public schema endpoint:** `GET /schema` (per `AGENTS.md:191`) — dump all registered controllers.

### 4.2 What it would take to call it from another agent system

| Path                                         | How much work                                                            |
| -------------------------------------------- | ------------------------------------------------------------------------ |
| **Wire openhuman-core as an MCP tool server** to a parent agent (Mavis, Claude Code, etc.) | **Lowest friction.** Run `openhuman-core mcp --transport http --port 9300 --auth-token <x>`, register the URL in the parent MCP config. Parent gets ~13 curated tools (memory + tree + subagent). |
| **Call JSON-RPC from another Rust/Python/TS process** | Medium. Auth: bearer token. Auth discovery: `./target/debug/openhuman-core serve` writes `${OPENHUMAN_WORKSPACE}/core.token` (`scripts/print-core-token.sh` reads it). Schema: `GET /schema` returns all namespaces. |
| **Embed as a library** (import `openhuman_core` as a Cargo dep) | **Hard.** It's structured as a Tauri-embedded binary, not a clean lib. The `run_server_embedded_with_ready` function is a hint that it's *possible*, but no examples exist outside the Tauri host. |
| **Webhook / inbound HTTP**                   | **NOT FOUND.** No public webhook receiver. Composio triggers come through the backend's Socket.IO bridge. |
| **iOS pairing**                              | The architecture doc documents a QR-pairing flow over an X25519 tunnel (`tinyhumansai/backend#709` dependency), but this is "experimental" and the backend PR is the blocker. Not production-ready. |

**Important reality check for our fleet:** The MCP server exposes **read-mostly memory ops + a subagent dispatcher**. If you want to use openhuman as the *memory substrate* for Mavis (replacing or supplementing DreBrain), the MCP tools give you `memory.search`, `memory.recall`, `tree.read_chunk`, `tree.browse` — that's the read path. The write path (`memory.store`, `memory.note`, `tree.tag`) is also exposed. **It is technically a viable MCP-side companion**, but: (1) it is GPL-3.0 (§6), (2) the managed memory tree won't have DreBrain's content unless the user goes through the OAuth auto-fetch, and (3) the local LLM is 1B gemma — the "intelligence" in this stack is their backend, not your local model.

### 4.3 Plugin / extension surface

- **Skills** (in-repo: `src/openhuman/skills/` + `skill_runtime/`): metadata-only skill helpers since the QuickJS runtime was removed. `AGENTS.md:71` explicitly: "**Skills runtime removed**: QuickJS gone. `src/openhuman/skills/` is metadata-only now." Skills are now described via `SKILL.md` files (per the architecture doc) and tool execution flows through native Rust handlers + Node-backed helpers via `runtime_node`.
- **Memory backend plug-in point** (README): optional `agentmemory` backend. `memory.backend = "agentmemory"` in `config.toml` lets openhuman share the same durable store as `rohitg00/agentmemory` (used by Claude Code, Cursor, Codex, OpenCode). **This is the most interesting plug-in point for our fleet** — it means a tool like the `agentmemory` server could be the shared surface between openhuman and our existing agents. The agentmemory backend is documented at `https://tinyhumans.gitbook.io/openhuman/features/obsidian-wiki/agentmemory-backend`.
- **Tool registry**: openhuman discovers 118+ OAuth integrations via the **managed Composio backend** (`src/openhuman/composio/mod.rs`). The core does **not** call Composio directly; everything is proxied through `https://api.tinyhumans.ai`. This is the *non-extensible* part of the integration surface — you can't add a new Composio toolkit from outside; the backend's allowlist governs.

---

## 5. Dependencies and runtime requirements

### 5.1 Source manifests (verified)

- **pnpm workspace** (`pnpm-workspace.yaml:1-7`):
  ```yaml
  packages:
    - "app"
    - "packages/tauri-plugin-ptt"
  ```
  (Intentionally does **not** include `packages/npm/` because that workspace has a `postinstall` that downloads a binary from a non-existent release — a comment in the file calls this out as a CI fix.)
- **Root `package.json`** (devDeps + runtime): `husky@^9.1.7`, `tsx@^4.20.3`, `ws@^8.20.0`, plus `@tauri-apps/api@2.10.1` (pinned via `resolutions`).
- **Root `Cargo.toml`**: 60+ direct deps; key ones (`Cargo.toml:1-50`):
  - `tokio = "1"` (full features), `axum = "0.8"` (HTTP server), `tower = "0.5"`
  - `reqwest = "0.12"` with `rustls-tls` (no OpenSSL), `http2`, `multipart`, `socks`
  - `rusqlite = "0.37"` (bundled — no system SQLite needed)
  - `serde`, `serde_json`, `serde_yaml`, `toml = "1.0"`
  - `clap = "4.5"` (CLI), `dialoguer` (interactive prompts), `keyring = "3"` (OS keychain)
  - `aes-gcm = "0.10"`, `argon2 = "0.5"`, `chacha20poly1305`, `x25519-dalek`, `hkdf`, `ring = "0.17"` (crypto)
  - `whisper-rs = "0.16"` (STT; with `metal` feature on macOS — note the patched `whisper-rs-sys` fork at `Cargo.toml` "Fix whisper-rs-sys CRT mismatch on Windows MSVC")
  - `cpal = "0.15"`, `hound = "3.5"` (audio I/O), `enigo`, `arboard`, `rdev` (input/clipboard automation)
  - `sentry = "0.47"` (error tracking, default-features = false for size)
  - `opentelemetry = "0.32"` + OTLP exporter, `prometheus = "0.14"` (telemetry)
  - `socketioxide = "0.15"` (Socket.IO server-side), `tokio-tungstenite = "0.24"` (client)
  - `whatsapp-rust = "0.5"` + `whatsapp-rust-tokio-transport` + `wacore` (WhatsApp, behind `whatsapp-web` feature)
  - `matrix-sdk = "0.16"` (Matrix, behind `channel-matrix` feature)
  - `bitcoin = "0.32"`, `ed25519-dalek`, `ethers-core/signers`, `bs58`, `ripemd`, `coins-bip39`, `curve25519-dalek` (wallet)
  - `lettre = "0.11"`, `mail-parser`, `async-imap` (SMTP/IMAP)
  - `fantoccini` (browser automation, behind `browser-native` feature)
  - `landlock = "0.4"` (Linux sandbox, behind `sandbox-landlock` feature), `rppal` (Raspberry Pi GPIO, behind `peripheral-rpi`)
  - `sysinfo = "0.33"` (resource monitor), `starship-battery = "0.10"` (laptop battery probe)
  - `uiautomation = "0.25"` (Windows UIA bindings), `windows-sys = "0.61"` (Windows sandbox + AppContainer)
  - `objc2`, `objc2-foundation`, `objc2-contacts`, `block2` (macOS-only deps for Contacts, AX)
  - `pdf-extract = "0.10"`, `ppt-rs = "0.2.14"` (office doc parsing)

### 5.2 Runtime requirements (verified)

- **Rust toolchain pinned to 1.93.0** (`rust-toolchain.toml`); comment explains they stay below 1.94 due to a matrix-sdk recursion-limit bug. Profile = minimal, components = rustfmt + clippy.
- **Node.js 24+** (per `README.md` "Contributing from source"); the **managed** Node runtime inside the core is `v22.11.0` (per `gitbooks/developing/architecture.md` "Skills Runtime Engine" table).
- **pnpm 10.10.0** (root `package.json:3`).
- **System libs for the Tauri build (per `Dockerfile`):** `build-essential`, `cmake`, `pkg-config`, `libssl-dev`, `libasound2-dev`, `libxdo-dev`, `libxtst-dev`, `libx11-dev`, `libevdev-dev`, `clang`, `mold`, `git`.
- **OS:** desktop binary targets x86_64 + aarch64 on Windows/macOS/Linux. macOS requires Apple Silicon or x86_64 (universal via `lipo` per the architecture doc — not verified from the tarball). iOS and Android are **experimental** (`AGENTS.md:32-46`) and iOS is "not product-ready" per the architecture doc.
- **GPU:** **None required** for the core. whisper-rs uses Metal on macOS (`features = ["metal"]`) and CUDA is **not** declared anywhere. Local model inference is delegated to Ollama (which can use Metal/CUDA, but that's Ollama's problem, not openhuman's). **The core is CPU-only.**
- **Memory / CPU limits (Docker compose defaults):** `mem_limit: 4g`, `cpus: 2.0` (`docker-compose.yml:50-51`). These are the developer's own production targets for the headless core.
- **Disk:** the desktop `aarch64.AppImage` is **339 MB**, the `.deb` is **220 MB**, the macOS `.dmg` is **180 MB**, the Windows `.exe` is **157 MB**, the Linux core tarball is **62 MB** (per the v0.57.40 release assets).
- **Heavy deps that hurt to install (verdict):** **PyTorch and CUDA are NOT deps** — the inference stack is Ollama + whisper-rs (CPU/Metal, no CUDA) + Piper TTS. The "large model weights" cost is the user's Ollama install, not openhuman's. The expensive pieces in *this* repo are: (a) **Rust compile time** (the core alone takes ~5-10 minutes clean from the `ci` profile per the Dockerfile, longer for `release`); (b) **whisper-rs / llama.cpp build** — the AGENTS.md explicitly notes `GGML_NATIVE=OFF cargo check` as a macOS Apple Silicon workaround, and there's a forked `whisper-rs-sys` to fix a Windows MSVC CRT mismatch; (c) the **CEF vendoring** in `app/src-tauri/vendor/tauri-cef/` (submodules!) — this is the Tauri build's real weight; (d) `whatsapp-rust`, `matrix-sdk` (optional features) which are real native builds.

### 5.3 Things that "just work" vs "you must wire"

- **Just works:** the core spawns / bundles Node 22.11.0 automatically, runs its own SQLite (no external DB), uses the OS keychain, and has rustls (no system OpenSSL).
- **You must wire:** the **managed** OAuth integrations (you need an openhuman account + backend access). The "**120+ integrations**" claim is gated by their backend. **Without the backend, only the local code/web tools + memory are usable** (and the local LLM is a 1B gemma).
- **Docker / headless deploy:** the published `Dockerfile` runs the core only (no Tauri). This is the most realistic path for fleet integration: `docker run -p 7788:7788 --env-file .env openhuman-core serve`. **MCP server mode is not in the Dockerfile CMD; you'd override to `mcp` or `mcp --transport http --port 9300 --auth-token <t>`.**

---

## 6. License

**Confirmed: `LICENSE` is verbatim the GNU General Public License v3.0** — standard FSF text, no additional clauses, no CLA excerpt in the LICENSE file itself. The repository's GitHub API metadata reports `license: { spdx_id: "GPL-3.0" }`.

**What GPL-3.0 means for a closed/private fleet:**

- **Static linking** openhuman-core into a closed product forces the combined work to be GPL-3.0. **Process-level use** (running `openhuman-core` as a separate binary and calling it over HTTP / MCP from a closed program) is generally considered **not** a derivative work under the FSF's interpretation, but the FSF's "interpretation" is not law and the actual answer depends on the jurisdiction + the degree of coupling. The AGPL-style "network use is distribution" trigger does **not** apply to plain GPL-3.0 (no AGPL term here).
- **Distribution** of any binary that embeds openhuman-core statically triggers source disclosure. Distribution of a script that shells out to `openhuman-core` over MCP does not.
- **Modifications** to openhuman itself must be released under GPL-3.0 with source.
- **No patent grant beyond what the code ships with** (GPL-3.0 §11 does have a patent retaliation clause, which is *more* protective than MIT/Apache, not less).

**Specific fleet-fitness questions:**

| Use case                                                                | Verdict under GPL-3.0                              |
| ----------------------------------------------------------------------- | -------------------------------------------------- |
| Run `openhuman-core` as a separate process, talk to it over MCP stdio/HTTP from a closed agent | **Probably OK** as long as the closed agent doesn't *embed* openhuman source. No source-disclosure trigger. |
| `cargo add openhuman_core` from a closed-source Rust app and call it as a library | **Forces GPL-3.0 on the combined work.** This is the hard line. |
| Distribute a packaged macOS app that bundles the openhuman desktop binary alongside closed binaries | **Forces the entire app to be GPL-3.0** if the binaries are part of one distribution, or you can ship them as two separate user-installed packages (with proper licensing notices). |
| Vendor openhuman's Tauri shell and modify it for an internal fleet UI  | **Forces GPL-3.0 on your UI.** Same as Electron-style apps that embed GPL-3.0. |
| Use openhuman as an MCP tool *subprocess* in a closed orchestrator      | **Likely OK.** The orchestrator is not "based on" openhuman; it just runs it. |

**Bottom line for our fleet:** if we want to **call** openhuman as a service (MCP server, JSON-RPC, Docker image), GPL-3.0 is **operable**. If we want to **modify and embed** it, GPL-3.0 will likely force the embedding project to be GPL-3.0 or to use a process boundary. This is the load-bearing license question for any "wire it in" decision. **For our private Hermes/Mavis fleet where the orchestrator calls openhuman as a subprocess, this is fine. For anything that statically links, this is a stop sign.**

---

## 7. Maintenance / maturity

**GitHub API metadata, fetched 2026-06-13:**

| Metric                         | Value                                                             |
| ------------------------------ | ----------------------------------------------------------------- |
| Created                        | 2026-02-18                                                       |
| Last push                      | 2026-06-13 13:52 UTC (today)                                     |
| Total commits                  | 3,014 (per repo page)                                             |
| Stars                          | 31,867 (per GitHub API)                                          |
| Forks                          | 3,089                                                            |
| Open issues                    | 146 (API) — README header shows 111 (discrepancy of 35; may be a stale header) |
| Open PRs                       | 35                                                               |
| Watchers                       | 167                                                              |
| Releases                       | 43                                                               |
| Latest release                 | **v0.57.40** on 2026-06-12 22:31 UTC                             |
| Top contributors (per `contributors?per_page=5`) | senamakel (1,053), graycyrus (293), github-actions[bot] (253), M3gA-Mind (225), oxoxDev (190) |
| Active branches                | main only (single trunk)                                          |
| Verifiable signature on the latest release commit | **No** (commit verification `verified: false, reason: "unsigned"` for the v0.57.41 chore commit; the v0.57.40 release commit was signed) |
| OpenHuman binaries verified    | **No** — the release assets do **not** ship signed `*.msi`/`*.dmg`/`*.AppImage` (verified in the latest release: 0 sig assets, all are unsigned tarballs / unverified installers). The README "Recommended install (native packages)" claims Homebrew bottle / apt-repo / MSI signature integrity, but the actual release assets on GitHub are **unsigned tarballs and disk images** for the latest release. **This is a supply-chain gap, not a project-quality one** — it's the open-source release pipeline, not malicious — but if you deploy from these assets, you are trusting a GitHub-Actions-bot's `gh release upload`. |

**Verdict: this is an active, fast-moving project, not a one-shot demo.**

- **Age:** ~4 months (created Feb 18 2026). Very young.
- **Velocity:** 3,014 commits in 4 months ≈ **25 commits/day**. That's high — typical of an early-stage venture-backed project, not a solo maintainer's pet project.
- **Release cadence:** 43 releases in 4 months ≈ **10 releases/month**, weekly-ish. The release notes (e.g. v0.57.40 "Parallel Power Upgrade") show thoughtful changelogs, not autogenerated bumps.
- **Team:** 5+ active contributors with non-trivial commit counts. The lead (`@senamakel`) is the README's listed creator and the only "true" maintainer (1,053 commits vs. the next 293). Heavy CI bot presence (~250 commits).
- **Backing:** the org is `tinyhumansai` (GitHub Org, not a personal user). The `tinyhumans.ai` domain is the product site. The architecture doc references `tinyhumansai/backend#709` — there is a closed-source backend that the OSS repo proxies to. This is a venture-funded (or well-resourced indie) agent company, not a community hobby project.
- **Maturity flags:**
  - `Early Beta` badge in the README header.
  - 146 open issues / 35 open PRs — heavy in-flight work.
  - 31.9k stars in 4 months is **extraordinarily high**. This is hype-fueled, not merit-only — the README's Product Hunt + Trendshift badges suggest a launch campaign.
  - **Architecture book still calls it a "crypto communities" product** while the README markets it as a general personal-AI harness. Internal branding drift, not external abandonment.
  - **Single trunk, no LTS / stable branches.** All 43 releases are off `main`.
  - Heavy use of `git submodule` for `vendor/tauri-cef` — a risk for forkers but a deliberate choice per the AGENTS.md "Vendored CEF-aware tauri-cli" section.

**Risk for fleet adoption:** **velocity is a double-edged sword.** A 25-commit/day project with breaking changes between 0.57.40 and 0.57.41 (Cargo version) will require active maintenance if you pin a release. There is no `1.0`, no SemVer stability promise, and the "long-term support" framing is absent.

---

## 8. Novelty assessment — what is genuinely new vs. what is a 200-line wrapper

I rate each capability honestly. **This is the part Andre will care about most for the "wire or pass" decision.**

### 8.1 Things that are *hard* to replicate (months of work, real engineering)

| Capability                                              | Why it's hard                                                                                                             | Where the code lives                                                       |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **The Karpathy obsidian-wiki auto-fetch loop**          | The 20-min loop that walks all active OAuth connections, canonicalizes to ≤3k-token Markdown chunks, scores them, and folds into a hierarchical summary tree stored in SQLite + Obsidian vault. Real work: incremental summarization, dedup, hierarchy rollups, vault layout. | `src/openhuman/memory_tree/`, `memory_archivist/`, `memory_sync/`, `memory_conversations/`, `memory_search/` (10+ sub-domains, thousands of lines) |
| **Token compression layer (TokenJuice)**                | The README claims 80% cost/latency reduction by HTML→MD, URL shortening, dedup, summarization, with **grapheme-by-grapheme** preservation of CJK/emoji. Real work: Unicode normalization (NFKC + combining-mark detection), HTML walker. | `src/openhuman/tokenjuice/`, `Cargo.toml` removes `html2md` (with a long comment about the 894 MB heap bug on a 10 KB Otter.ai email — a real war story) |
| **Hybrid memory search (vector + FTS5)**                | The architecture doc says 70% vector / 30% FTS5. The cross-thread search inverted index is tokenized with NFKC + canonical-combining-class for diacritics. Real Unicode work. | `src/openhuman/memory_search/`, `memory_conversations/`, `Cargo.toml` lists `unicode-normalization`, `aho-corasick` |
| **Multi-channel message ingest (Gmail/Slack/Discord/Telegram/WhatsApp/Matrix/iMessage)** | 5+ messaging backends, each with its own protocol, OAuth flow, message-shape, and backfill tool. The `whatsapp-rust` swap from a custom 1.3K-line RusqliteStore to upstream `0.5` (which now has its own SqliteStore + LID-addressed + sender-key skmsg support) is a real engineering investment. The architecture doc's full message-normalization pipeline is non-trivial. | `src/openhuman/channels/`, `src/openhuman/composio/`, `src/openhuman/integrations/`, `src/openhuman/meet/`, `src/openhuman/meet_agent/`, plus per-channel backfill tools in `src/bin/` |
| **Local AI orchestration (Ollama + LM Studio + Whisper + Piper)** | Sub-process management, model allowlisting, install/download progress, context-window routing. **Replacing html2md** with a custom linear-time tag-and-entity stripper for the same use case (`fast_html_to_text` in `providers/gmail/post_process.rs`) — the in-repo comment is gold for engineering culture. | `src/openhuman/inference/local/{ollama,lm_studio,install,profile,service}.rs`, plus `whisper-rs-sys` patch on `Cargo.toml` |
| **The MCP server (first-class, 4-protocol-versions, 13+ tools)** | Real protocol work: 2024-11-05 → 2025-11-25, batch support, notifications, resources, session/client-name normalization, JSON-RPC error codes. Not a 200-line wrapper. | `src/openhuman/mcp_server/` (7 files, ~1000+ LOC) |
| **Webview account automation (Gmail/LinkedIn/Google Meet CEF)** | Embedded Chromium webviews with CDP-driven scanners (`gmail_scanner`, `slack_scanner`, `telegram_scanner`, `whatsapp_scanner`), JS injection control, the `meet_audio`/`meet_call`/`meet_video` / `fake_camera` modules. The AGENTS.md has a strong "no new JS injection" rule, suggesting they learned the cost of this. | `app/src-tauri/src/{webview_accounts,webview_apis,webview_notifications,meet_audio,meet_call,meet_video,fake_camera,cdp}/` |
| **Cross-chain wallet (BTC P2WPKH / EVM / Solana ed25519 / Tron secp256k1)** | BIP-39 mnemonic → 4 different chains with the right curve + address format. Real crypto work. | `src/openhuman/wallet/`, `Cargo.toml` (bitcoin, ed25519-dalek, ethers, bs58, ripemd, coins-bip39, curve25519-dalek) |
| **Sentry defense-in-depth (10+ before_send filters with project-internal issue IDs)** | The 1,000+ line `src/main.rs:62-180` `before_send` block filters specific noise patterns (transient 5xx, session-expired, max-iterations, budget, channel-404, managed-backend errorCode). The comments reference internal ticket IDs (`OPENHUMAN-TAURI-2E`, `-84`, etc.) — production-grade observability hygiene. | `src/main.rs:62-200`, `src/openhuman/core/observability.rs` |

### 8.2 Things that are *real* but achievable in 200-500 lines

| Capability                                              | Why it's still real but small                                                                                              |
| ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **JSON-RPC dispatch over a typed controller registry**  | The `src/core/{all,dispatch,jsonrpc}.rs` pattern is a thin Axum + tokio + JSON-schema dispatcher. Standard pattern, well-built. |
| **Local CLI dispatcher (`openhuman <namespace> <func>`)**| `clap`-style manual arg parsing in `src/core/cli.rs`. 200-300 LOC, well-tested. |
| **Tokio multi-thread runtime with bumped worker stack** | The 6-line `tokio::runtime::Builder::new_multi_thread().thread_stack_size(...)` in `cli.rs:122-129` and `cli.rs:191-199`. The bump-from-2MiB comment is a useful gotcha. |
| **AES-256-GCM + Argon2id memory encryption**            | Standard crypto, well-known crates. |
| **OS keychain integration via `keyring` crate**         | Standard. |
| **Bearer-token JSON-RPC with CORS allowlist**           | Standard. |
| **Sentry init with secret scrubbing regexes**           | The 7 regex patterns in `src/main.rs:222-260` are a checklist, not novel. |
| **Per-provider `inference/provider` trait**             | Standard OpenAI-shape adapter. |

### 8.3 Things that are *managed-service-bound* and not replicable in a closed fleet

| Capability                                              | Why it's not on the OSS side                                                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **The "good" models (the actual reasoning/fast/vision picks behind the "built-in model routing")** | Managed cloud, no list of model IDs in the OSS repo. |
| **118+ Composio OAuth integrations**                    | `src/openhuman/composio/mod.rs:7-10` — "The core does **not** hit the Composio API directly — everything goes through the backend." The backend owns the API key, billing, and toolkit allowlist. |
| **The backend Socket.IO bridge / event fan-out**        | `tinyhumansai/backend#709` — closed source. |
| **The "auto-fetch 20-min loop" with 118+ connectors**   | Reads from the managed backend's API; the OSS repo's per-provider sync (gmail, slack, etc.) is the *local* mirror, not the source. |

### 8.4 The honest verdict

**openhuman is ~60% real engineering and ~40% managed service.** The OSS repo is a credible piece of work — the Rust core, the MCP server, the local-AI plumbing, the cross-channel ingest, the wallet, the observability — but the *headline capability* (the 118+ integrations, the "context in minutes," the "one subscription, all models") is mostly **on the closed backend side**, not in this repo.

**If you're using it as a "personal AI super intelligence"** (the README's framing), you're paying for the managed service and the OAuth mesh, and the OSS is the desktop shell. **If you want to wire it into a closed fleet** (our use case), the *only* realistically useful part is the **MCP server** + the **local AI domain** + the **memory tree** — and even there, the local LLM is a 1B gemma with a hard allowlist. The actual "intelligence" you'd get from openhuman is the memory tree's data, not its models.

**Could we replicate the useful parts in 200 lines?** **No, but the inverse question matters more.** Could *we* replicate the *parts we'd want*? Mostly yes:

- The **MCP server with memory ops** is a 1-2 day project, **but we already have DreBrain (PARA + gbrain index) and Mavis's vault.** The marginal value of *another* memory substrate is low.
- The **TokenJuice-style compression** is a 500-LOC project for the CJK-preserving HTML→MD + dedup + summarization, **but only worth it if our tool output is bloated.** For Mavis's current tool surface (peeks, file writes, memory ops), this is overkill.
- The **local AI orchestration** (Ollama allowlist, install/download) is a 300-500 LOC project — **but the routing question is simpler for us** (gemma3:1b vs gemma3:4b vs M3 escalation is a 100-line decision table, not an MCP server).

**What we genuinely don't have and would be hard to replicate in any reasonable LOC budget:**
- The **Karpathy-style 20-min auto-fetch loop** that walks 118+ OAuth sources and folds the deltas into a hierarchical summary tree. This is months of work.
- The **MCP server's polish** (4 protocol versions, 13 tools, stdio+HTTP, session/client-name normalization, Sentry-grade observability). This is 1-2 weeks of careful work.
- The **composio integration layer** — but we don't *need* Composio. Mavis's gbrain + Google Workspace + Slack direct integrations are sufficient.

---

## 9. Wire or pass?

**For the Mavis / Hermes / DreBrain fleet, the answer is: pass on adoption; consider borrowing patterns.**

**Reasons to pass:**

1. **GPL-3.0 is a hard line for static linking, but workable for subprocess.** Subprocess use is fine, but the marginal value of running openhuman-core as an MCP subprocess in Mavis's orchestrator is **low** when DreBrain + gbrain already provide memory and Mavis already provides agent orchestration. The MCP server's 13 tools (memory ops + tree reads + a subagent dispatcher) is a **subset** of what Mavis already does, and we'd be adding a second memory substrate to maintain.
2. **The local model is 1B gemma.** The "bring your own model" path exists only via LM Studio (which bypasses the allowlist), and even then, the local model is for *local-AI-only* tasks. The default managed path is a closed backend.
3. **The 118+ OAuth integrations are managed-service-bound.** We can't add a new toolkit without going through their backend. For our use case (where Mavis integrates with Gmail/Slack/GitHub/Notion directly), this is duplication, not addition.
4. **Project velocity is high but very young** (4 months, 0.x versioning, no LTS, branding drift between architecture book and README). Pinning to a release means accepting weekly churn.
5. **The OSS repo is missing supply-chain hygiene** (release assets are unsigned tarballs despite README claims of "signed .msi / signed apt repo / Homebrew bottle hash"). For a production fleet, this is a real concern.

**Reasons to reconsider:**

1. **The MCP server is genuinely first-class.** If we *did* want to expose Mavis's tools to other MCP clients (Claude Code, Cursor), openhuman's MCP server is a clean reference implementation. Studying it is worthwhile; copying it is fine (it's our own surface, not theirs).
2. **The auto-fetch + memory tree loop is a real pattern** we don't have. If Andre's vision for DreBrain shifts toward "Mavis should know about my Gmail/Slack/Notion by 6am every morning," the *pattern* (incremental fetch + chunk + score + summary tree) is the load-bearing part. We can implement this in DreBrain using Mavis's own existing tools, no need to vendor openhuman.
3. **The `agentmemory` backend integration is a useful precedent.** `memory.backend = "agentmemory"` in `config.toml` lets openhuman share a store with Claude Code / Cursor / Codex. If we wanted DreBrain to be the *agentmemory for Mavis + Hermes + future agents*, that's an architecture worth exploring, and openhuman's docs confirm the pattern is viable.
4. **The TokenJuice compression approach is worth borrowing.** For tool calls that return 50K tokens of HTML, a 500-LOC compression layer in Mavis would be valuable. Not vendor, but the *pattern*.

**Concrete recommendations:**

| Action                                                | Owner        | Time     |
| ----------------------------------------------------- | ------------ | -------- |
| **Do NOT adopt openhuman as a fleet service.**        | Mavis/PM     | 1 min    |
| **Do study `src/openhuman/mcp_server/` for our own MCP server reference.** | Mavis/PM   | 1 day    |
| **Do consider implementing the auto-fetch loop in DreBrain** (incremental fetch → chunk → score → summary tree → vault) using Mavis's existing tools. No vendoring needed. | DreBrain owner | 1-2 weeks |
| **Do consider implementing TokenJuice-style compression** for Mavis's high-volume tool outputs (web fetch, email body). ~500 LOC. | Mavis        | 2-3 days |
| **Do NOT license-pin to GPL-3.0 by linking** — keep the fleet's surface permissive. | PM           | 1 min    |

---

## Appendix A: Verified file:line citations

| Claim                                                                                       | Source                                                                                                          |
| ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Cargo version 0.57.41                                                                       | `Cargo.toml:3` (`version = "0.57.41"`)                                                                            |
| Binary name `openhuman-core`                                                                | `Cargo.toml:8` (`[[bin]] name = "openhuman-core"`)                                                                |
| Library name `openhuman_core`                                                               | `Cargo.toml:24` (`[lib] name = "openhuman_core"`)                                                                 |
| 5 Rust binaries total                                                                       | `Cargo.toml:8-22` (openhuman-core, slack-backfill, gmail-backfill-3d, memory-tree-init-smoke, inference-probe, test-mcp-stub) |
| pnpm 10.10.0 enforced                                                                       | `package.json:3`                                                                                                 |
| pnpm workspace members                                                                      | `pnpm-workspace.yaml:1-7`                                                                                        |
| LICENSE is verbatim GPL-3.0                                                                 | `LICENSE:1-3` ("GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007")                                              |
| GitHub repo created 2026-02-18                                                             | `api/repos` `created_at: 2026-02-18T20:01:27Z`                                                                    |
| Total commits 3,014                                                                         | Repo page header (https://github.com/tinyhumansai/openhuman)                                                    |
| Stars 31,867                                                                                | `api/repos` `stargazers_count: 31867`                                                                            |
| Forks 3,089                                                                                 | `api/repos` `forks_count: 3089`                                                                                  |
| Open issues 146                                                                             | `api/repos` `open_issues_count: 146` (note: README says 111)                                                      |
| Latest release v0.57.40 on 2026-06-12 22:31 UTC                                            | `api/repos/releases/latest`                                                                                       |
| Top contributor: senamakel (1,053 commits)                                                 | `api/repos/contributors?per_page=5`                                                                              |
| Core runs in-process (no sidecar)                                                           | `AGENTS.md:21-24`                                                                                                |
| Tauri v2 + React + Rust core stack                                                          | `AGENTS.md:1-3`                                                                                                  |
| Default JSON-RPC port 7788                                                                  | `.env.example:38-39` (`OPENHUMAN_CORE_PORT=7788`)                                                                 |
| Default MCP HTTP port 9300                                                                  | `src/openhuman/mcp_server/stdio.rs:21`                                                                            |
| Default backend URL `https://api.tinyhumans.ai`                                            | `.env.example:14-15`                                                                                              |
| Default local chat model `gemma3:1b-it-qat`                                                 | `src/openhuman/inference/model_ids.rs:6`                                                                         |
| Default local embed `bge-m3` (1024-dim, 8192-token context)                                | `src/openhuman/inference/model_ids.rs:9` + comment in same file                                                 |
| Local chat allowlist is exactly 2 models                                                    | `src/openhuman/inference/model_ids.rs:14` (`MVP_ALLOWED_CHAT_MODELS`)                                            |
| Local vision is **disabled** in MVP (only `""` allowed)                                    | `src/openhuman/inference/model_ids.rs:18` (`MVP_ALLOWED_VISION_MODELS`)                                          |
| LM Studio bypasses the Ollama allowlist                                                    | `src/openhuman/inference/model_ids.rs:60-72` + test at `175-184`                                                |
| Ollama base URL default `http://localhost:11434`                                            | `.env.example:124`                                                                                              |
| LM Studio base URL default `http://localhost:1234/v1`                                      | `.env.example:130`                                                                                              |
| 4 MCP protocol versions supported (2024-11-05 through 2025-11-25)                           | `src/openhuman/mcp_server/protocol.rs:1-7`                                                                      |
| MCP tools exposed: core.{list_tools,tool_instructions}, agent.{list_subagents,run_subagent}, memory.{search,recall,store,note}, tree.{read_chunk,browse,top_entities,list_sources,tag}, searxng_search | `src/openhuman/mcp_server/stdio.rs:128-138` + tests at `protocol.rs:317-339`                                    |
| `agent.run_subagent` is the only non-read-only tool                                         | `src/openhuman/mcp_server/mod.rs:5-10`                                                                          |
| Composio is backend-proxied, not direct                                                     | `src/openhuman/composio/mod.rs:7-10`                                                                            |
| Skills runtime is metadata-only (QuickJS removed)                                          | `AGENTS.md:71`                                                                                                  |
| `local_ai/` was renamed to `inference/local/`                                              | `src/openhuman/inference/local/mod.rs:1-3` + `mod.rs` of inference                                               |
| Memory chunking 512 tokens / 64 overlap                                                     | `gitbooks/developing/architecture.md` "AI & Tool Protocol (MCP)" → "AI Memory System" table                      |
| 70% vector / 30% FTS5 hybrid search                                                         | `gitbooks/developing/architecture.md` same table                                                                |
| AES-256-GCM + Argon2id for memory encryption                                                | `gitbooks/developing/architecture.md` "Security Architecture" section                                            |
| Docker image uses `rust:1.93-bookworm`                                                      | `Dockerfile:13`                                                                                                  |
| Rust toolchain pinned 1.93.0 (matrix-sdk recursion limit)                                  | `rust-toolchain.toml`                                                                                            |
| Desktop `aarch64.AppImage` is 339 MB                                                        | `api/repos/releases/latest` asset `OpenHuman_0.57.40_aarch64.AppImage` size `339257864`                         |
| Linux core tarball is 62 MB                                                                 | `api/repos/releases/latest` asset `openhuman-core-0.57.40-x86_64-unknown-linux-gnu.tar.gz` size `63419540`     |
| 4 GB RAM, 2 CPU default limits in docker-compose                                            | `docker-compose.yml:50-51`                                                                                       |
| 35 open PRs (matches API)                                                                   | Repo page (https://github.com/tinyhumansai/openhuman/pulls)                                                     |
| All release assets are unsigned (no .sig files for the desktop binaries in the v0.57.40 release) | `api/repos/releases/latest` assets list — 18 assets, 4 are `.sig` (the Linux/macOS/Windows tarballs, MSI), but the **AppImage and dmg** are unsigned. The 4 `.sig` files that exist are for: app.tar.gz (macOS), AppImage (Linux amd64 + aarch64), .msi, .exe. **NOT FOUND: signed .dmg for macOS, signed apt repo for Linux.** |
| 8 README translations                                                                       | `README.{de,ja-JP,ko,ur-pk,zh-CN}.md` (5 non-English) + `README.md`                                              |
| 118+ integrations claim                                                                     | `README.md` ("118+ third-party integrations" + "Integrations: 🚀 118+ via OAuth")                                |
| 1000+ via backend                                                                           | `src/openhuman/composio/mod.rs:1-3` ("backend-proxied access to 1000+ OAuth integrations")                       |
| 43 releases                                                                                 | Repo page (https://github.com/tinyhumansai/openhuman/releases) — "Releases 43"                                  |

## Appendix B: Things I looked for and did NOT find

- **What context window does the local chat model advertise?** `inference/model_context.rs` exists but I did not fetch the body. **NOT FOUND in this read pass.** The `MIN_CONTEXT_TOKENS` constant is referenced from `inference/local/mod.rs:32` but its value was not read.
- **The list of cloud models the backend routes to.** Closed; not in the OSS repo. Confirmed in the README's "By default, model routing uses the OpenHuman backend" line.
- **Signed installers (`.dmg` / `.msi` / `.AppImage`)** in the GitHub release assets. README claims they exist; the v0.57.40 release shows only `.sig` files for `app.tar.gz` and AppImages, **not for `.dmg` or `.msi`**. The signing story in the README is partial.
- **A public webhook receiver.** The Composio flow goes `Composio → backend HMAC-verify → backend Socket.IO emit → core socket::event_handlers → DomainEvent::ComposioTriggerReceived`. No public-facing HTTP webhook. **NOT FOUND.**
- **A clean library embedding example.** `openhuman_core` is technically a `rlib`, but the canonical usage is the Tauri host, not a downstream library. **NOT FOUND as a documented pattern.**

## Appendix C: Contradictions and ambiguities worth flagging

1. **Branding drift.** `gitbooks/developing/architecture.md:5` still says "AI-powered super assistant for crypto communities." The README and recent commits have pivoted to "Personal AI super intelligence." Forks, derivatives, and documentation will inherit this drift. Pick a side.
2. **"Local + managed" is really "managed + tiny local fallback."** The README's "Local + managed services, upfront" callout is the most honest line; the rest of the README oversells the local path. The local LLM is a 1B gemma. The "118+ integrations" are managed. Don't conflate.
3. **Open issue count discrepancy.** GitHub API reports 146; the README badge still shows 111. Likely a stale README badge — 35 PRs + a few days of activity would account for the gap. **Minor.**
4. **Skipped `packages/npm/` from the pnpm workspace.** `pnpm-workspace.yaml:5-7` comment explicitly says it has a `postinstall` that downloads a binary from a non-existent release and breaks CI. So there is a `packages/npm/` directory that **does not work** out of the box. **The build is robust to this, but it's a gotcha for new contributors.**
5. **Mavis's memory vs openhuman's memory tree.** Mavis's memory goes through Redmine (DreBrain PARA) + gbrain. openhuman's memory goes through the OAuth auto-fetch + Obsidian vault + Memory Tree. If we adopted openhuman as a memory substrate, we'd be merging two memory systems — neither is a strict superset of the other. **Do not adopt without a unification plan.**
