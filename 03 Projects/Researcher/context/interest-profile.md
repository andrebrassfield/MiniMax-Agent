# Interest Profile — Researcher

This file is the researcher's priority surface. It is rebuilt from shared system state on each REFRESH.

## Andre's Active Lanes (as of 2026-06-02)

| Lane | Why it matters | Sub-topics |
|------|----------------|------------|
| **AI agents & agentic systems** | Andre runs 6 agents; agent architecture is the spine of his stack | orchestration, tool use, multi-agent patterns, agent memory, eval, safety |
| **Frontier AI** | Every model release shifts his stack's capabilities and constraints | M3 / M2.7, Claude, GPT, open-weight, context length, multimodality |
| **Memory orchestration** | Andre cares about persistent, queryable memory across agents and runs | vector DBs, FTS, gbrain, Honcho, OpenClaw, long-horizon context |
| **Research methodology** | He values research-quality output over summaries; the loop pattern itself is a lane | evidence ops, dossier design, verification queues, source balance |
| **Builder patterns & dev tooling** | Andre ships; tooling friction is a first-class concern | IDE, terminal, testing, deployment, observability |
| **Crypto rails & agent commerce** | Recurring lane in his stack — agent-to-agent payments, on-chain identity | Base, Coinbase adjacencies, x402, payment rails |
| **Robotics & embodied agents** | Lower-frequency lane; slow-burn watch | sim2real, foundation models for control, robot data |

## Topics Demoted

- Generic AI news ("X company raised $Y") — secondary at best.
- Pure opinion / hot takes without source trail — verification queue only.
- Crypto tokens not adjacent to Andre's rails — out of scope.

## Personalization Posture

The Researcher is not a neutral news service. It is designed to be useful to one operator and one agent system. If a topic does not map to one of Andre's lanes, it gets the minimum collection effort and lives in the verification queue or out of scope entirely.

## How This Gets Rebuilt

On each REFRESH, the Researcher re-reads:
- `~/MiniMax-Agent/02 Notes/connections/` (synthesized insights)
- `~/MiniMax-Agent/03 Projects/` (active shipping lanes)
- `~/MiniMax-Agent/MAVIS.md`, `SOUL.md`, `agent.md` (Andre's stated priorities)
- `~/MiniMax-Agent/01 Daily/` recent entries
- `queue/research-questions.md` (Mavis injections)

If Andre's center of gravity has shifted (e.g. a new project appears in `03 Projects/`), the lane list updates and the dossier set gets a corresponding dossier added. Lanes with no signal in 30 days get demoted to watch-only.

---

*This file is priority. The source plan is how. The loop is the method.*
