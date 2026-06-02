# Model Context Protocol — Architecture Summary (M3-summary, 2026-06-02)

> Faithful dense summary of `https://modelcontextprotocol.io/docs/learn/architecture`. The original is in CCR (`ccr_hash` in sidecar JSON). The reader can opt back into the original for full detail.

## What MCP is

MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems — data sources (local files, databases), tools (search engines, calculators), and workflows (specialized prompts). It's often described as "USB-C for AI applications": a standardized way to connect any AI app to any external system.

**MCP's scope is narrow**: it defines the *protocol for context exchange*. It does not dictate how AI applications use LLMs or manage the provided context. The four projects in the MCP ecosystem are: the Specification, the SDKs, the Development Tools (e.g., MCP Inspector), and Reference Server Implementations.

## Architecture: participants and layers

### Participants

MCP follows a **client-server** architecture with three roles:

- **MCP Host**: the AI application that coordinates and manages MCP clients. Examples: Claude Code, Claude Desktop, Visual Studio Code, Cursor.
- **MCP Client**: a component inside the host that maintains a connection to one MCP server. One client per server. The host instantiates a client when it needs to talk to a new server.
- **MCP Server**: a program that provides context (data, tools, prompts) to MCP clients. Runs locally (STDIO transport, single client) or remotely (Streamable HTTP transport, many clients).

Example: VS Code (host) → instantiates one MCP client per server (Sentry, filesystem, etc.). Each client holds a dedicated connection. Local filesystem server runs in-process via STDIO; remote Sentry server runs on Sentry's infra via Streamable HTTP.

### Layers

MCP has two layers, conceptually nested:

- **Data layer** (inner): the JSON-RPC 2.0 based protocol. Defines message structure and semantics. Includes lifecycle management, server features (tools/resources/prompts/notifications), client features (sampling/elicitation/logging), and utility features (notifications, progress tracking).
- **Transport layer** (outer): the communication channels. Two transports:
  - **Stdio**: process-to-process via stdin/stdout on the same machine. Optimal performance, no network.
  - **Streamable HTTP**: HTTP POST for client→server, optional Server-Sent Events for streaming. Supports bearer tokens, API keys, custom headers. **MCP recommends OAuth for auth tokens.**

The transport layer is abstracted from the protocol — same JSON-RPC message format across all transports.

## Data Layer Protocol

### Lifecycle management

MCP is **stateful**. Lifecycle management negotiates capabilities between client and server at connection time. Both sides declare what features they support. The `initialize` request carries `protocolVersion` (e.g., `2025-06-18`), `capabilities`, and `clientInfo`/`serverInfo`. After `initialize`, the client sends a `notifications/initialized` to confirm readiness. If protocol versions don't match, the connection is terminated.

### Primitives

**Primitives are the most important concept in MCP** — they define what clients and servers can offer each other.

**Server-exposed primitives** (the three core ones):

- **Tools**: executable functions the AI app can invoke (file ops, API calls, DB queries). Discovered via `tools/list`, executed via `tools/call`.
- **Resources**: data sources providing contextual info (file contents, DB records, API responses). Discovered via `resources/list`, read via `resources/read`.
- **Prompts**: reusable templates for LLM interactions (system prompts, few-shot examples).

**Client-exposed primitives** (for richer server→client interaction):

- **Sampling**: servers can request LLM completions from the host's AI app via `sampling/createMessage`. Server authors stay model-independent and don't bundle an LLM SDK.
- **Elicitation**: servers can request additional user input via `elicitation/create` (for confirmation, more info, etc.).
- **Logging**: servers send debug log messages to clients.

**Cross-cutting utility primitive** (experimental):

- **Tasks**: durable execution wrappers for deferred result retrieval and status tracking. Designed for expensive computations, workflow automation, batch processing, multi-step ops.

**Discovery pattern**: each primitive has `*/list` for discovery, `*/get` for retrieval, and (for tools) `tools/call` for execution. Listings are dynamic — servers can send `notifications/tools/list_changed` to push updates.

### Notifications

JSON-RPC notification messages (no response expected). Use case: a server's available tools change at runtime — the server sends a notification and connected clients refresh their view. Enables real-time, dynamic MCP servers.

## Example walkthrough: data layer in action

Three-step JSON-RPC exchange:

**1. Initialization** — client sends:

```json
{
  "jsonrpc": "2.0", "id": 1, "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {"elicitation": {}},
    "clientInfo": {"name": "example-client", "version": "1.0.0"}
  }
}
```

Server responds with its own capabilities. The negotiation does three things: **protocol version check** (kills the connection on mismatch), **capability discovery** (each side declares what primitives + notifications it handles), and **identity exchange** (for debugging + compat).

**2. Tool discovery** — `{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}` → response is a `tools` array, each entry with: `name` (unique, namespaced), `title` (human-readable), `description` (when to use it), `inputSchema` (JSON Schema for params). Listings are dynamic — clients can refresh.

**3. Tool execution** — `tools/call` with name + arguments:

```json
{
  "jsonrpc": "2.0", "id": 3, "method": "tools/call",
  "params": {
    "name": "weather_current",
    "arguments": {"location": "San Francisco", "units": "imperial"}
  }
}
```

## Why this matters for AI applications

The host's MCP client manager:
- Establishes connections to configured servers during init
- Stores each server's capabilities
- Routes tool calls to the right server based on capability matching
- Combines tools from all connected servers into a single unified registry the LLM can see
- Handles real-time updates from `list_changed` notifications

The architectural payoff: the AI app doesn't need to know about specific data sources, APIs, or tools at compile time. They appear in the LLM's tool registry dynamically as MCP servers are configured. The LLM can then use them transparently.

## Key concepts to internalize

1. **MCP is a protocol, not a framework** — it standardizes the wire format, not the implementation.
2. **Stateful with capability negotiation** — both sides declare what they support; mismatches kill the connection.
3. **Primitives are the unit of value exchange** — Tools (action), Resources (data), Prompts (templates) for server→client; Sampling, Elicitation, Logging for client→server.
4. **Transport is pluggable** — STDIO for local, Streamable HTTP for remote, both carry the same JSON-RPC.
5. **Notifications enable dynamic servers** — tool lists and capabilities can change at runtime.
6. **OAuth is the recommended auth pattern** for the Streamable HTTP transport.
