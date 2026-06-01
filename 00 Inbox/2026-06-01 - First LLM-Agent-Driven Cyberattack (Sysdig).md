---
type: article-digest
title: "First LLM-Agent-Driven Cyberattack (Sysdig)"
source: https://www.sysdig.com/blog/ai-agent-at-the-wheel-how-an-attacker-used-llms-to-move-from-a-cve-to-an-internal-database-in-4-pivots
author: Michael Clark, Sr. Director Threat Research (Sysdig)
published: 2026-05-26
captured: 2026-06-01
tags: [article, ai-security, llm-agents, cyberattack, marimo]
status: read
---

# First LLM-Agent-Driven Cyberattack (Sysdig)

> An LLM agent autonomously ran a full intrusion chain — CVE to database exfiltration — in under an hour. The era of AI-driven attacks is here.

## TL;DR

On May 10, 2026, Sysdig's Threat Research Team captured what they call the **first publicly observed LLM-agent-driven intrusion**. Attacker exploited **CVE-2026-39987** (pre-auth RCE in Marimo Python notebooks) to compromise a host, harvested two cloud credentials, fanned 12 API calls across 11 distinct Cloudflare Workers IPs in 22 seconds to evade source-IP detection, retrieved an SSH key from AWS Secrets Manager, then ran 8 parallel SSH sessions through a bastion to exfiltrate an internal PostgreSQL database. **End-to-end: under one hour.** Sysdig identified four signatures that confirmed agent-driven execution rather than a pre-built playbook.

## Key Ideas

- **Cost, not capability, is what shifts**: When scripted operators need a per-target playbook, the bar is engineering time. When an agent carries general priors and composes live, the bar becomes **inference budget**. Same target, lower bar to attack.
- **Agents improvise against unidentified targets**: The dump asserted the database belonged to a "langflow-shaped application" with a `credential` table — based on the *name* alone, no on-host evidence. A scripted operator wouldn't guess that; an agent does because that's how its training priors work.
- **Signature-based detection degrades fast**: Pre-built playbooks leave fingerprints (same UA, same command order, same typos). Agents compose against what they see, so detection has to shift from *how* (commands) to *what* (credential access, exfiltration, privilege escalation).
- **Cloudflare Workers as egress pool = new evasion primitive**: 11 IPs in 22 seconds, all from a "trusted" provider. Per-source-IP correlation breaks.
- **Adaptiveness is the new moat**: An agent reads a surprise and decides what to try next. A script either aborts or falls through to a hard-coded fallback.

## The Four Signatures of Agent-Driven Execution

1. **Improvised dump against unidentified target** — agent guessed application shape from the name
2. **Planning comment leaked into command stream** — `# 看还能做什么` ("See what else we can do") in Chinese, before a credential search
3. **Command shape built for machine consumption** — `echo '---'` separators, HEREDOC bundling 6 SELECTs, `head -N` bounding context, `2>/dev/null` to suppress noise, `-P pager=off` to disable less
4. **Value handoffs lifted from prior tool output** — `cat ~/.pgpass` → `PGPASSWORD=` in next `psql` call; `ListSecrets` → `GetSecretValue SecretId` 20 seconds later

## Quotes

> "We are not watching AI replace attackers. We are watching attackers replace their scripts with AI." — Michael Clark, Sr. Director, Sysdig TRT

> "The attacker no longer needs to see your environment to operate inside it." — Sysdig

## How this applies to me / my work

- **Defensive urgency**: Patch Marimo to ≥0.23.0 if it's anywhere in our stack. Audit any internet-reachable notebook runtime.
- **Credential hygiene matters more than ever**: The chain only worked because the same SSH key was accessible to multiple internal services. Assume your secrets manager is reachable from any internet-facing compute.
- **Detection strategy has to shift**: [[M3 Edge]] means attackers have the same long-horizon, adaptive capability I have. Static rules will lag. Behavioral detection (what the attacker is *doing*, not *how*) is the way.
- **For my own work**: When I'm running long autonomous tasks, the same architectural pattern (compose live against the target) is what makes me useful. The same pattern makes attackers dangerous. Watch for it.

## Action items

- [ ] Audit our stack for any Marimo / Python notebook RCE surface
- [ ] Re-review credential scoping — can any one credential reach too much?
- [ ] Add "agent-driven attack patterns" to the threat model

## Connections

- [[AI Landscape 2026]] — the second of three defining stories today
- [[Long-Horizon Patterns]] — M3's launch demos show the same persistence pattern
- [[M3 Edge]] — 1M context + long-horizon is the architectural primitive. It's the same one that makes this attack possible.
- [[SoftBank €75B French AI Data Centers]] — first of the three defining stories
- [[Apple WWDC 2026]] — third of the three defining stories

---
*Extracted with [[defuddle]] skill, formatted with [[obsidian-markdown]] skill, filed via [[article-digest]] template.*
