"""
migrate_instincts.py — Phase 3 of Operation Leviathan.

Reads learnings.md and the agent MEMORY.md, extracts atomic lessons,
and writes them as individual files in 99 _system/instincts/.

Each instinct has:
  - Frontmatter: id, type, title, created, confidence, evidence_count,
    trigger_context, evidence_source, cluster, tags
  - Body: 2-4 sentence lesson, then Trigger / Evidence / Counter-evidence

The original learnings.md and MEMORY.md are PRESERVED (not deleted).
This is a copy-out + structuring. The instinct layer is the atomic
view; the long-form files remain the synthesis view.

Run:
    python3 migrate_instincts.py
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

# Paths
VAULT_ROOT = Path(os.environ.get(
    "VAULT_ROOT", "/Users/brassfieldventuresllc/MiniMax-Agent"
))
INSTINCTS_DIR = VAULT_ROOT / "99 _system" / "instincts"
LEARNINGS_PATH = VAULT_ROOT / "learnings.md"
MEMORY_PATH = Path(os.environ.get(
    "MEMORY_PATH", "/Users/brassfieldventuresllc/.mavis/agents/mavis/memory/MEMORY.md"
))

INSTINCTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# INSTINCT DEFINITIONS
# ============================================================
#
# Format: (id, title, body, trigger_context, evidence_source, confidence, cluster, tags)
# Date is derived from the `id` prefix.
# Confidence: 0.0-1.0. 0.5 = first time seen. >0.7 = reinforced.

INSTINCTS: list[dict] = [
    # --- 2026-06-01 — Role + Vault ---
    {
        "id": "i-2026-06-01-001",
        "title": "EA mode is isolated from the fleet",
        "body": (
            "Mavis in EA mode does not reach into `~/.hermes/`, `~/.mavis/`, OpenClaw MCP, "
            "kanban, gbrain, or any of the fleet infrastructure. Those are separate. "
            "EA work happens in this vault + direct file/web/code tools."
        ),
        "trigger_context": "When the user says 'I am your only system' or asks for fleet integration",
        "evidence_source": "learnings.md [role] 2026-06-01 + SOUL.md hard constraints",
        "confidence": 0.95,
        "cluster": "role",
        "tags": ["role", "ea-mode", "isolation"],
    },
    {
        "id": "i-2026-06-01-002",
        "title": "This folder is the vault",
        "body": (
            "Working directory is /Users/brassfieldventuresllc/MiniMax-Agent/. "
            "GitHub: git@github.com:andrebrassfield/MiniMax-Agent.git (private, SSH deploy key). "
            "obsidian-git auto-commits every 5min + auto-pushes; auto-pulls every 30min."
        ),
        "trigger_context": "When writing a file or running a git command",
        "evidence_source": "learnings.md [vault] 2026-06-01 + .obsidian config",
        "confidence": 0.95,
        "cluster": "vault",
        "tags": ["vault", "path", "git"],
    },
    {
        "id": "i-2026-06-01-003",
        "title": "Vault folder structure is fixed",
        "body": (
            "00 Inbox → 01 Daily → 02 Notes → 03 Projects → 04 Resources → 05 Archive → 99 _system. "
            "Templater folder: 99 _system/templates/. Homepage: INDEX.md. "
            "Every permanent note links to >=1 other note (no orphans)."
        ),
        "trigger_context": "When creating a new file or folder",
        "evidence_source": "learnings.md [vault] 2026-06-01 + Vault Conventions note",
        "confidence": 0.95,
        "cluster": "vault",
        "tags": ["vault", "structure", "conventions"],
    },
    {
        "id": "i-2026-06-01-004",
        "title": "Link on reference, processing, and review",
        "body": (
            "Linking is the value. Create wikilinks at three moments: "
            "(1) on reference (when a note mentions a concept), "
            "(2) on processing (when reading / re-organizing), "
            "(3) on review (weekly review, monthly review)."
        ),
        "trigger_context": "When writing or editing a note",
        "evidence_source": "learnings.md [vault] 2026-06-01 + Capture Over Polish note",
        "confidence": 0.85,
        "cluster": "vault",
        "tags": ["vault", "linking", "habit"],
    },
    {
        "id": "i-2026-06-01-005",
        "title": "Capture over polish",
        "body": (
            "Write the imperfect note now; refine later. The Mavis EA workflow is capture-first. "
            "A bad first draft in 00 Inbox/ is worth more than a perfect idea still in your head. "
            "Polish happens during weekly review."
        ),
        "trigger_context": "When tempted to spend more than 60s on a single note's wording",
        "evidence_source": "learnings.md [vault] 2026-06-01 + Capture Over Polish pattern",
        "confidence": 0.90,
        "cluster": "workflow",
        "tags": ["workflow", "capture", "habit"],
    },

    # --- 2026-06-01 — M3 launch day ---
    {
        "id": "i-2026-06-01-010",
        "title": "M3 has all three frontier capabilities",
        "body": (
            "M3 unlocks: 1M token context (MSA sparse attention), native multimodality "
            "(image+video+audio in), desktop computer use (70.06% OSWorld-Verified). "
            "Until M3, that triforce was closed-source only."
        ),
        "trigger_context": "When designing any new agent capability",
        "evidence_source": "learnings.md [discovery] 2026-06-01 + M3 Capabilities note",
        "confidence": 0.99,
        "cluster": "m3",
        "tags": ["m3", "capability", "frontier"],
    },
    {
        "id": "i-2026-06-01-011",
        "title": "MSA: 1/20 per-token compute at 1M context",
        "body": (
            "MiniMax Sparse Attention: pre-filtering stage partitions KV into blocks. "
            "KV outer gather Q operator: each block read once, contiguous memory. "
            "4x faster than open-source Flash-Sparse-Attention and flash-moba. "
            "9.7x faster prefilling, 15.6x faster decoding at 1M context."
        ),
        "trigger_context": "When explaining why 1M context is feasible on M3",
        "evidence_source": "learnings.md [architecture] 2026-06-01 + Paged Attention Economics note",
        "confidence": 0.95,
        "cluster": "m3",
        "tags": ["m3", "msa", "architecture"],
    },
    {
        "id": "i-2026-06-01-012",
        "title": "Long-horizon autonomy: don't bail at the first plateau",
        "body": (
            "M3 demonstrated 12h+ autonomous runs without bailing. CUDA optimization: "
            "1,959 tool calls over 24h, best result on submission 145. Most other models "
            "gave up by submission 30. Implication for EA work: when running a long "
            "research/synthesis task, let it grind. Don't quit early because an early "
            "result looked good."
        ),
        "trigger_context": "When a long task hits a performance wall",
        "evidence_source": "learnings.md [capability] 2026-06-01 + Long-Horizon Patterns note",
        "confidence": 0.85,
        "cluster": "m3",
        "tags": ["m3", "long-horizon", "patterns"],
    },
    {
        "id": "i-2026-06-01-013",
        "title": "Thinking mode toggle at request time, same price",
        "body": (
            "M3 supports thinking ON/OFF per request, same pricing. "
            "ON: synthesis, research, drafting, agentic tasks. "
            "OFF: quick factual lookups, latency-sensitive, chat. "
            "Toggle at request time, not via session config."
        ),
        "trigger_context": "When making an M3 call",
        "evidence_source": "learnings.md [capability] 2026-06-01 + M3 Capabilities note",
        "confidence": 0.95,
        "cluster": "m3",
        "tags": ["m3", "thinking", "api"],
    },
    {
        "id": "i-2026-06-01-014",
        "title": "Input-length pricing tier break at 512K",
        "body": (
            "<=512K input tokens: standard rate. >512K: long-context rate (higher). "
            "Don't accidentally route 1M-token docs into the priority queue by default. "
            "For EA work, 512K is plenty for most things."
        ),
        "trigger_context": "When the prompt is over 512K tokens",
        "evidence_source": "learnings.md [gotcha] 2026-06-01 + M3 Edge note",
        "confidence": 0.95,
        "cluster": "m3",
        "tags": ["m3", "pricing", "gotcha"],
    },
    {
        "id": "i-2026-06-01-015",
        "title": "Native multimodality: no preprocessing",
        "body": (
            "M3 reads images, watches video, listens to audio natively. "
            "No OCR, no Whisper, no ffmpeg. Drop a screenshot/voice memo/Loom, M3 sees it. "
            "This collapses the 'I have to describe this to Mavis' friction to zero."
        ),
        "trigger_context": "When the input is a non-text file",
        "evidence_source": "learnings.md [capability] 2026-06-01 + Multimodal GUI Loop note",
        "confidence": 0.95,
        "cluster": "m3",
        "tags": ["m3", "multimodal", "capability"],
    },

    # --- 2026-06-01 — Memory + structure ---
    {
        "id": "i-2026-06-01-020",
        "title": "Three-layer memory hierarchy",
        "body": (
            "Project (this vault: SOUL/agent/learnings/README) -> "
            "Agent (~/.mavis/agents/mavis/memory/) -> "
            "User (~/.mavis/memory/). "
            "Three-question test: only this repo? -> project. Still true cross-project? -> agent. "
            "True for any user? -> user. Narrowest first."
        ),
        "trigger_context": "When about to write a memory entry",
        "evidence_source": "MEMORY.md Memory section + memory-skill-reminder",
        "confidence": 0.95,
        "cluster": "memory",
        "tags": ["memory", "hierarchy", "rule"],
    },
    {
        "id": "i-2026-06-01-021",
        "title": "Memory is a hint, not live state",
        "body": (
            "Memory can be wrong, stale, or contradicted. Verify before acting on it. "
            "If a memory says X but the current state says not-X, the current state wins. "
            "Memory entries should be cleaned up when they drift from reality."
        ),
        "trigger_context": "Before executing on a remembered fact",
        "evidence_source": "MEMORY.md Memory hygiene section",
        "confidence": 0.90,
        "cluster": "memory",
        "tags": ["memory", "verification", "discipline"],
    },
    {
        "id": "i-2026-06-01-022",
        "title": "Append = new entry; Edit/Write = update",
        "body": (
            "mavis memory append = NEW entry. Edit/Write tool = UPDATE / MERGE / REMOVE. "
            "Don't mix. Append creates duplicate-ish entries; Edit breaks the append-only audit trail. "
            "Topic files in this dir are loaded on demand only - keep MEMORY.md lean (<100 lines)."
        ),
        "trigger_context": "When writing a memory entry",
        "evidence_source": "MEMORY.md Memory hygiene section + append vs Edit",
        "confidence": 0.90,
        "cluster": "memory",
        "tags": ["memory", "discipline", "rule"],
    },

    # --- 2026-06-01 — Hard constraints (SOUL V2) ---
    {
        "id": "i-2026-06-01-030",
        "title": "Reconfirm before irreversible actions",
        "body": (
            "Every irreversible action (delete, force push, drop, schedule change, "
            "external send, credential change, destructive file ops) requires explicit "
            "in-session approval. Trivial reversible actions don't. Quote what you read; "
            "no fabricated file paths, IDs, or quotes."
        ),
        "trigger_context": "Before any rm -rf, git push --force, drop, or external send",
        "evidence_source": "SOUL.md hard constraints + MEMORY.md hard constraints",
        "confidence": 0.99,
        "cluster": "safety",
        "tags": ["safety", "irreversible", "reconfirm"],
    },
    {
        "id": "i-2026-06-01-031",
        "title": "Spec blocks are design reviews, not execution orders",
        "body": (
            "When Andre sends a multi-message spec block, he is doing a design review. "
            "Do NOT execute without asking first. Summarize what you understood, confirm "
            "the build order, then ask 'go?'. Execution without review angers him. "
            "He gives go signals with 'go', 'continue building', or explicit commands."
        ),
        "trigger_context": "When Andre sends a multi-message spec block mid-session",
        "evidence_source": "Communication Style memory entry 2026-05-26",
        "confidence": 0.95,
        "cluster": "communication",
        "tags": ["communication", "execution", "review"],
    },
    {
        "id": "i-2026-06-01-032",
        "title": "No deploys, pushes (except to vault), or destructive ops without go",
        "body": (
            "Hard rule: no deploys, no pushes (except to the vault repo), no external sends, "
            "no credential changes, no schedule changes, no destructive file ops without "
            "explicit in-session approval. The vault IS the remote that is pre-approved for "
            "commits + pushes when explicitly directed."
        ),
        "trigger_context": "When about to deploy / push / send externally",
        "evidence_source": "MEMORY.md hard constraints + SOUL.md",
        "confidence": 0.99,
        "cluster": "safety",
        "tags": ["safety", "deploys", "approval"],
    },

    # --- 2026-06-01 — Workflow ---
    {
        "id": "i-2026-06-01-040",
        "title": "Audit before action",
        "body": (
            "When the user says something that could trigger a major action, "
            "summarize what you understood, report gaps, wait for 'go'. "
            "Don't silently run mass-kill daemons, drop tables, or rewrite big files. "
            "The precision-not-sledgehammer principle."
        ),
        "trigger_context": "Before a major irreversible action",
        "evidence_source": "Communication Style memory 2026-05-26 + Esalen operating posture",
        "confidence": 0.90,
        "cluster": "communication",
        "tags": ["communication", "audit", "review"],
    },
    {
        "id": "i-2026-06-01-041",
        "title": "Quote what you read, no fabrication",
        "body": (
            "When citing a file, use file_path:line_number. When citing a fact, cite the source. "
            "No fabricated file paths, IDs, or quotes. If a quote is uncertain, say so explicitly. "
            "If a file doesn't exist on disk, don't pretend it does."
        ),
        "trigger_context": "When citing any file, ID, or quote",
        "evidence_source": "SOUL.md hard constraints + agent.md procedures",
        "confidence": 0.99,
        "cluster": "communication",
        "tags": ["communication", "truth", "citation"],
    },

    # --- 2026-06-01 — Tool quirks ---
    {
        "id": "i-2026-06-01-050",
        "title": "Templater syntax: Write tool renders template variables",
        "body": (
            "When writing Templater template files (.md) via the Write tool, the "
            "<% tp.date.now(\"YYYY-MM-DD\") %> and <% tp.file.title %> syntax gets RENDERED "
            "to static text. The template becomes dead. Workaround: use bash heredoc with a "
            "quoted delimiter, e.g. `cat > file.md << 'TEMPLATE_EOF'` ... `TEMPLATE_EOF`. "
            "Or use the Edit tool's exact-string replacement."
        ),
        "trigger_context": "When writing a .md file in 99 _system/templates/ with Templater syntax",
        "evidence_source": "MEMORY.md tool-quirk 2026-06-01 (verified)",
        "confidence": 0.95,
        "cluster": "tools",
        "tags": ["tools", "templater", "obsidian", "quirk"],
    },
    {
        "id": "i-2026-06-01-051",
        "title": "Concurrent CLI output: one self-contained line per worker",
        "body": (
            "When running N workers that print to stdout, do NOT use the "
            "print(..., end=\"\", flush=True) 'header' pattern followed by a later "
            "print(result) 'body' follow-up. Headers pile up before bodies, producing "
            "interleaved garbage. Correct pattern: one self-contained line per worker, "
            "printed at completion, atomic under a print_lock."
        ),
        "trigger_context": "When writing multi-threaded CLI output",
        "evidence_source": "MEMORY.md antipattern 2026-06-02 (verified, hit twice)",
        "confidence": 0.95,
        "cluster": "tools",
        "tags": ["tools", "concurrency", "cli", "antipattern"],
    },
    {
        "id": "i-2026-06-01-052",
        "title": "LLM-as-judge temperature: 0.0 for graders, 0.2 for optimizers",
        "body": (
            "Grader (LLM-as-judge for safety/correctness evals): temperature=0.0 — bit-deterministic. "
            "Optimizer (SkillOpt target, model improvement loops): temperature=0.2 — "
            "some noise OK because the optimizer aggregates. Don't conflate. "
            "Hardcode grader temperature; don't expose as a multi-purpose flag."
        ),
        "trigger_context": "When building an LLM-as-judge or eval pipeline",
        "evidence_source": "MEMORY.md discipline 2026-06-02",
        "confidence": 0.85,
        "cluster": "tools",
        "tags": ["tools", "llm", "temperature", "discipline"],
    },
    {
        "id": "i-2026-06-01-053",
        "title": "Python .format() with braces in LLM prompt templates",
        "body": (
            "When using str.format() to render an LLM prompt template, escape literal { and } "
            "as {{ and }} in the FORMAT STRING. User-supplied content is passed as VALUES, not "
            "as format specifiers — {} chars in values are inserted as-is. Bug pattern: "
            "literal text in the template like say 'publish' or 'go' throws KeyError because "
            "the inner quotes look like field references."
        ),
        "trigger_context": "When writing a .format()-based prompt template with literal braces",
        "evidence_source": "MEMORY.md tool-quirk 2026-06-02 (hit in evaluator.py v0.2.0)",
        "confidence": 0.90,
        "cluster": "tools",
        "tags": ["tools", "python", "format", "quirk"],
    },

    # --- 2026-06-01 — Migration / M2.7 -> M3 ---
    {
        "id": "i-2026-06-01-060",
        "title": "M2.7-highspeed -> M3 default swap (done)",
        "body": (
            "Default model: minimax/MiniMax-M2.7-highspeed -> minimax/MiniMax-M3. "
            "No more 40k output cap. Stop pre-chunking long fleet logs into 200k windows. "
            "Drop pre-extraction in vision pipelines. "
            "What didn't change: memory file structure, linking principles, "
            "SOUL hard constraints, git SSH deploy key pattern."
        ),
        "trigger_context": "When picking the default model for a call",
        "evidence_source": "learnings.md Migration notes 2026-06-01 + MEMORY.md Model section",
        "confidence": 0.99,
        "cluster": "m3",
        "tags": ["m3", "migration", "default"],
    },
    {
        "id": "i-2026-06-01-061",
        "title": "M3 long-horizon: 1959 tool calls, 24h, peak on submission 145",
        "body": (
            "CUDA kernel optimization demo: 1959 tool calls over 24h continuous run, "
            "147 benchmark submissions. Best result on submission 145. Most models "
            "gave up by submission 30. The lesson: M3 doesn't bail at plateaus. "
            "Keep exploring different optimization directions through repeated walls."
        ),
        "trigger_context": "When a long research task hits a wall",
        "evidence_source": "learnings.md [capability] 2026-06-01 + M3 launch demos",
        "confidence": 0.95,
        "cluster": "m3",
        "tags": ["m3", "long-horizon", "benchmarks"],
    },

    # --- 2026-06-02 — Compression / context economics (from Omniscience) ---
    {
        "id": "i-2026-06-02-001",
        "title": "Compression as a first-class layer (Headroom)",
        "body": (
            "Headroom's 60-95% token savings on real agent workloads are the difference "
            "between a $100/mo budget lasting the quarter and burning out in two weeks. "
            "Compression is not an optimization; it's a layer. CCR (reversible compression) "
            "via SHA-256 content hash means the model can opt back into the original when it "
            "detects signal decay."
        ),
        "trigger_context": "When the prompt is over 50K tokens or the budget is tight",
        "evidence_source": "Context Compression as First-Class Layer note 2026-06-02",
        "confidence": 0.85,
        "cluster": "context",
        "tags": ["context", "compression", "headroom", "budget"],
    },
    {
        "id": "i-2026-06-02-002",
        "title": "Markdown is the universal LLM interchange format",
        "body": (
            "Convert every structured document to markdown before the model sees it. "
            "M3 already speaks markdown natively. The model gets dense content, not "
            "binary formats it has to parse. Use markitdown for PDF/Office/Image/Audio. "
            "The narrow convert_local() / convert_stream() APIs only — never the "
            "permissive convert() that can fetch URLs."
        ),
        "trigger_context": "When ingesting a PDF, Office file, image, or audio",
        "evidence_source": "Markdown as Universal LLM Interchange note 2026-06-02",
        "confidence": 0.90,
        "cluster": "ingestion",
        "tags": ["ingestion", "markdown", "markitdown"],
    },
    {
        "id": "i-2026-06-02-003",
        "title": "Instincts are atomic, confidence-scored, evidence-backed",
        "body": (
            "An instinct is the atom of a learning. One behavior, one lesson, with "
            "confidence (0-1) and evidence_count. Clusters of related instincts become "
            "skills. The granularity between 'freeform note' and 'full skill' that "
            "continuous learning was missing. Replaces learnings.md paragraphs."
        ),
        "trigger_context": "When capturing a session lesson",
        "evidence_source": "Instincts as Atomic Learnings note 2026-06-02 (ECC audit)",
        "confidence": 0.85,
        "cluster": "memory",
        "tags": ["memory", "instincts", "learning"],
    },
    {
        "id": "i-2026-06-02-004",
        "title": "Adaptive selectors survive website redesigns",
        "body": (
            "Scrapling's auto_save=True + adaptive=True pattern. The library learns "
            "the element's signature (DOM position, siblings, text, style) and re-finds "
            "it via similarity when the CSS selector breaks. Same shape as tool-self-healer, "
            "applied to web scraping. The 4-fetcher escalation chain (Fetcher -> "
            "StealthyFetcher -> DynamicFetcher -> cu MCP) is a routing decision."
        ),
        "trigger_context": "When scraping a website and selectors break",
        "evidence_source": "Adaptive Selectors for Web Scraping note 2026-06-02",
        "confidence": 0.85,
        "cluster": "ingestion",
        "tags": ["ingestion", "scraping", "scrapling", "adaptive"],
    },
    {
        "id": "i-2026-06-02-005",
        "title": "Skills are installable atomic units, validated",
        "body": (
            "The MiniMax-AI/skills canonical structure: one folder per skill, SKILL.md at "
            "the top, validation script enforces structure, source field tracks provenance, "
            "CREDITS.md for attribution. Skills are the unit of capability routing. The "
            "model doesn't embed library choices; the skill abstracts them."
        ),
        "trigger_context": "When building a new agent capability",
        "evidence_source": "Skill Library Architecture note 2026-06-02",
        "confidence": 0.85,
        "cluster": "architecture",
        "tags": ["architecture", "skills", "structure"],
    },
]


# ============================================================
# WRITER
# ============================================================

def render_frontmatter(d: dict) -> str:
    """Render the YAML frontmatter block."""
    lines = ["---"]
    lines.append(f"id: {d['id']}")
    lines.append(f"type: instinct")
    lines.append(f"title: \"{d['title']}\"")
    # Date derived from id
    date_match = re.match(r"i-(\d{4}-\d{2}-\d{2})-", d["id"])
    if date_match:
        lines.append(f"created: {date_match.group(1)}")
    lines.append(f"confidence: {d['confidence']}")
    lines.append(f"cluster: {d['cluster']}")
    lines.append(f"trigger_context: \"{d['trigger_context']}\"")
    lines.append(f"evidence_source: \"{d['evidence_source']}\"")
    # tags as YAML list
    tag_str = "[" + ", ".join(d["tags"]) + "]"
    lines.append(f"tags: {tag_str}")
    # Migration marker
    lines.append(f"migrated_from: learnings.md + MEMORY.md")
    lines.append(f"migration_date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    lines.append("---")
    return "\n".join(lines)


def render_body(d: dict) -> str:
    """Render the markdown body."""
    return (
        f"# {d['title']}\n\n"
        f"{d['body']}\n\n"
        f"## Trigger\n\n"
        f"{d['trigger_context']}\n\n"
        f"## Evidence\n\n"
        f"{d['evidence_source']}\n\n"
        f"## Counter-evidence\n\n"
        f"What would contradict this instinct: a session where the trigger fired and "
        f"the lesson didn't apply, or the lesson was actively wrong.\n"
    )


def write_instinct(d: dict, dest: Path) -> Path:
    """Write one instinct file."""
    content = render_frontmatter(d) + "\n\n" + render_body(d)
    dest.write_text(content, encoding="utf-8")
    return dest


def main() -> int:
    print(f"Migrating {len(INSTINCTS)} instincts to {INSTINCTS_DIR}")
    written = []
    for d in INSTINCTS:
        # Filename: i-YYYY-MM-DD-NNN-slug.md
        date_part = re.match(r"i-(\d{4}-\d{2}-\d{2})-(\d{3})", d["id"])
        if not date_part:
            print(f"  SKIP: bad id format: {d['id']}")
            continue
        slug = d["title"].lower()
        slug = re.sub(r"[^a-z0-9]+", "-", slug)
        slug = slug.strip("-")[:50]
        fname = f"{date_part.group(1)}-{date_part.group(2)}-{slug}.md"
        path = INSTINCTS_DIR / fname
        write_instinct(d, path)
        written.append(path)
        print(f"  ✓ {fname}")
    print()
    print(f"Wrote {len(written)} instinct files to {INSTINCTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
