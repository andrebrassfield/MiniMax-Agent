# Instincts

> Atomic, confidence-scored, evidence-backed learnings. The granularity between "freeform note" and "full skill" that continuous learning was missing. Per the [[Instincts as Atomic Learnings]] pattern (audited from ECC, 2026-06-02).

## What is an instinct?

An instinct is one behavior + one lesson + one trigger. Three pieces:

- **Body** — 2-4 sentence description of the lesson
- **Trigger** — when this fires
- **Evidence** — where it came from (a session, a paper, a reference, a reasoning chain)

Plus frontmatter: `id`, `type: instinct`, `title`, `created`, `confidence: 0-1`, `cluster`, `trigger_context`, `evidence_source`, `tags`.

## When to write a new instinct

Every session produces instincts. Three triggers:
1. A behavior worked → write an instinct with confidence 0.5-0.7 (first time)
2. A behavior was reinforced (worked again) → bump confidence, increment evidence_count
3. A behavior was contradicted → write a counter-instinct or downgrade

## How instincts cluster into skills

When 3+ related instincts reach confidence >= 0.7 in the same cluster, they cluster into a skill. The `evolve` step (TBD) automates this. Today it's manual — review the cluster, write the skill, reference the instinct IDs.

## The current set (30 instincts, 2026-06-02)

| ID | Cluster | Title | Confidence |
|---|---|---|---|
| [[2026-06-01-001-ea-mode-is-isolated-from-the-fleet]] | role | EA mode is isolated from the fleet | 0.95 |
| [[2026-06-01-002-this-folder-is-the-vault]] | vault | This folder is the vault | 0.95 |
| [[2026-06-01-003-vault-folder-structure-is-fixed]] | vault | Vault folder structure is fixed | 0.95 |
| [[2026-06-01-004-link-on-reference-processing-and-review]] | vault | Link on reference, processing, and review | 0.85 |
| [[2026-06-01-005-capture-over-polish]] | workflow | Capture over polish | 0.90 |
| [[2026-06-01-010-m3-has-all-three-frontier-capabilities]] | m3 | M3 has all three frontier capabilities | 0.99 |
| [[2026-06-01-011-msa-1-20-per-token-compute-at-1m-context]] | m3 | MSA: 1/20 per-token compute at 1M context | 0.95 |
| [[2026-06-01-012-long-horizon-autonomy-don-t-bail-at-the-first-plat]] | m3 | Long-horizon autonomy: don't bail at first plateau | 0.85 |
| [[2026-06-01-013-thinking-mode-toggle-at-request-time-same-price]] | m3 | Thinking mode toggle at request time, same price | 0.95 |
| [[2026-06-01-014-input-length-pricing-tier-break-at-512k]] | m3 | Input-length pricing tier break at 512K | 0.95 |
| [[2026-06-01-015-native-multimodality-no-preprocessing]] | m3 | Native multimodality: no preprocessing | 0.95 |
| [[2026-06-01-020-three-layer-memory-hierarchy]] | memory | Three-layer memory hierarchy | 0.95 |
| [[2026-06-01-021-memory-is-a-hint-not-live-state]] | memory | Memory is a hint, not live state | 0.90 |
| [[2026-06-01-022-append-new-entry-edit-write-update]] | memory | Append = new entry; Edit/Write = update | 0.90 |
| [[2026-06-01-030-reconfirm-before-irreversible-actions]] | safety | Reconfirm before irreversible actions | 0.99 |
| [[2026-06-01-031-spec-blocks-are-design-reviews-not-execution-order]] | communication | Spec blocks are design reviews, not execution orders | 0.95 |
| [[2026-06-01-032-no-deploys-pushes-except-to-vault-or-destructive-o]] | safety | No deploys/pushes (except to vault) without go | 0.99 |
| [[2026-06-01-040-audit-before-action]] | communication | Audit before action | 0.90 |
| [[2026-06-01-041-quote-what-you-read-no-fabrication]] | communication | Quote what you read, no fabrication | 0.99 |
| [[2026-06-01-050-templater-syntax-write-tool-renders-template-varia]] | tools | Templater syntax: Write tool renders template variables | 0.95 |
| [[2026-06-01-051-concurrent-cli-output-one-self-contained-line-per-]] | tools | Concurrent CLI output: one self-contained line per worker | 0.95 |
| [[2026-06-01-052-llm-as-judge-temperature-0-0-for-graders-0-2-for-o]] | tools | LLM-as-judge temperature: 0.0 for graders, 0.2 for optimizers | 0.85 |
| [[2026-06-01-053-python-format-with-braces-in-llm-prompt-templates]] | tools | Python .format() with braces in LLM prompt templates | 0.90 |
| [[2026-06-01-060-m2-7-highspeed-m3-default-swap-done]] | m3 | M2.7-highspeed -> M3 default swap (done) | 0.99 |
| [[2026-06-01-061-m3-long-horizon-1959-tool-calls-24h-peak-on-submis]] | m3 | M3 long-horizon: 1959 tool calls, 24h, peak on submission 145 | 0.95 |
| [[2026-06-02-001-compression-as-a-first-class-layer-headroom]] | context | Compression as a first-class layer (Headroom) | 0.85 |
| [[2026-06-02-002-markdown-is-the-universal-llm-interchange-format]] | ingestion | Markdown is the universal LLM interchange format | 0.90 |
| [[2026-06-02-003-instincts-are-atomic-confidence-scored-evidence-ba]] | memory | Instincts are atomic, confidence-scored, evidence-backed | 0.85 |
| [[2026-06-02-004-adaptive-selectors-survive-website-redesigns]] | ingestion | Adaptive selectors survive website redesigns | 0.85 |
| [[2026-06-02-005-skills-are-installable-atomic-units-validated]] | architecture | Skills are installable atomic units, validated | 0.85 |

## Cluster distribution

| Cluster | Count | Avg confidence |
|---|---:|---:|
| m3 | 8 | 0.95 |
| memory | 4 | 0.90 |
| tools | 4 | 0.91 |
| communication | 3 | 0.95 |
| safety | 2 | 0.99 |
| vault | 3 | 0.92 |
| workflow | 1 | 0.90 |
| role | 1 | 0.95 |
| context | 1 | 0.85 |
| ingestion | 2 | 0.88 |
| architecture | 1 | 0.85 |

## How the migration was done

The migration script is in `_migration.py`. It reads the structured list in that file and writes the 30 atomic files. Run it again if you add new instincts to the list.

The original source files are PRESERVED (not deleted):
- `learnings.md` — long-form synthesis layer
- `~/.mavis/agents/mavis/memory/MEMORY.md` — agent-level cross-project memory

The instinct layer is a third view: atomic, confidence-scored, evidence-backed. It complements the long-form files; it doesn't replace them.

## Future

- **Confidence decay** — instincts not reinforced in 90 days decay by 0.05. Below 0.3 → archived.
- **Cluster evolution** — every quarter, run `evolve` to cluster related instincts into skills.
- **Counter-evidence discipline** — when an instinct is contradicted, write a counter-instinct (or note the contradiction in the existing file's `## Counter-evidence` section).
- **Validation script** — like the MiniMax skills validator, a small `validate_instincts.py` that checks each file for required frontmatter fields, valid confidence range, and non-empty body.
