"""
PatternForge — the workflow workshop.

Given a rough intent for a new agentic workflow, PatternForge produces a
strict GENERATIVE-CODE.md containing the 6 sections of Alexander's
generative code (adapted to digital workflows):

  1. The design problem
  2. The patterns it composes (linked CHIEF notes)
  3. The sequence (with rationale)
  4. The values it embodies
  5. The stakeholder interactions
  6. The boundary conditions

The script calls M3 (via `mmx text chat`) to do the qualitative work.
Python handles files, the prompt template, and the JSON parsing.

Esalen posture: M3 is the workshop master (qualitative grading).
                  Python is the file system (mechanical work).

Usage:
    python pattern_forge.py forge --intent "..."
    python pattern_forge.py template    # print the template
    python pattern_forge.py examples    # print the few-shot examples
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(_HERE))

# ============================================================================
# The 6-section generative code template (the workshop's structure)
# ============================================================================

GENERATIVE_CODE_TEMPLATE = """# GENERATIVE CODE: <workflow name>

> A generative code is not a script. It is the *patterns* + *sequence* + *values* + *stakeholders* + *boundaries* of a workflow. The script (`run.sh`) is the *output* of the generative code, not the workflow itself. (See Christopher Alexander, *The Nature of Order* Book 3, 2004.)

## 1. The design problem

<What problem does this workflow solve? What failure mode does it prevent? What does "done" look like?>

## 2. The patterns it composes

<Linked CHIEF notes — the building blocks. Each pattern contributes one structural decision to the workflow.>

## 3. The sequence (with rationale)

<Step 1 → 2 → 3 → ... with one-line rationale per step. The rationale is more important than the step.>

## 4. The values it embodies

<The "why" — what value does each step express? What would be lost if we removed the step? If the values are vague, the workflow will be vague.>

## 5. The stakeholder interactions

<When does this need a human? When a tool? When both? When neither? What does the human review? What does the tool execute?>

## 6. The boundary conditions

<When should this workflow NOT be run? What inputs are out of scope? What are the failure modes the workflow does NOT handle?>

## 7. Implementation script (the *output* of the generative code)

```bash
#!/usr/bin/env bash
# <one-line description>
set -e

# <step 1>
# <step 2>
# ...
```

## 8. Wholeness check (self-evaluation against Alexander's 15 properties)

<For each of the 15 properties (Levels of Scale, Strong Centers, Thick Boundaries, Alternating Repetition, Positive Space, Good Shape, Local Symmetries, Deep Interlock and Ambiguity, Contrast, Gradients, Roughness, Echoes, The Void, Simplicity and Inner Calm, Not Separateness), score 0-2 and one-line rationale.>
"""


# ============================================================================
# Few-shot examples (to anchor M3's output style)
# ============================================================================

EXAMPLE_INPUT_1 = "A workflow for triaging incoming emails into three categories: urgent, important, archive."

EXAMPLE_OUTPUT_1 = """# GENERATIVE CODE: Email Triage

## 1. The design problem

Inbox zero is impossible. But *knowing what to ignore* is achievable. This workflow triages incoming email into three buckets so the user can spend attention only on `urgent` and `important` items. The failure mode it prevents is "I missed the email I needed to see." The done state: every email is classified within 4 hours of arrival, and the user sees a daily digest of the `urgent` bucket.

## 2. The patterns it composes

- [[Capture Over Polish]] — capture the email's metadata first, classify later
- [[Paged Attention Economics]] — short, focused batches over long unfocused lists
- [[Self-Healing via Reflection Layer]] — the workflow reflects on its own misclassifications

## 3. The sequence (with rationale)

1. **Poll inbox every 15 minutes** — frequent enough to catch urgent within 15min, infrequent enough to batch
2. **Score each email on (sender importance, content urgency, actionability)** — three orthogonal axes reduce bias
3. **Apply thresholds: urgent = (sender OR content) high; important = (sender OR content) medium + actionable; archive = low on both** — explicit thresholds make the classification auditable
4. **Tag and move (don't delete)** — non-destructive; user can always undo
5. **Daily digest of `urgent` to user at 8am** — visibility without interrupt
6. **Weekly review: how many misclassifications?** — meta-cognition

## 4. The values it embodies

- **Attention is the scarce resource** — every email is a vote for or against the user's most valuable hour
- **Reversibility over speed** — never delete; the cost of an undo (5 sec) is less than the cost of a lost message
- **Explicit thresholds, not vibes** — "important" is a function of three scores and a rule, not a feeling
- **The workflow reflects on itself** — misclassifications are data, not failures

## 5. The stakeholder interactions

- **Tool**: poll, score, tag, move
- **Human**: review the daily 8am digest; correct misclassifications (which the workflow learns from)
- **Neither**: archive (no review needed)

## 6. The boundary conditions

- **Not for**: spam filtering (use a separate spam system), group emails with >20 recipients (low signal), automated system notifications (route them to a separate channel)
- **Out of scope**: composing replies (a separate workflow), calendar integration (separate workflow), attachment triage (separate workflow)
- **Failure modes not handled**: phishing detection (out of scope), thread vs new-message disambiguation (use thread ID), email-account changes (rebuild from scratch)

## 7. Implementation script

```bash
#!/usr/bin/env bash
set -e
# Poll inbox, score, tag, move, report
python3 .vault-brain/scripts/triage.py
```

## 8. Wholeness check

- Levels of Scale: 2 — sub-workflows (polling, scoring, digest) are clearly nested
- Strong Centers: 2 — the "attention is scarce" claim is the central value
- Thick Boundaries: 1 — interfaces between polling/scoring/digest could be cleaner
- Alternating Repetition: 2 — examples and rules alternate
- Positive Space: 2 — the structure does real work
- Good Shape: 2 — recognizable section headers
- Local Symmetries: 2 — "What this is NOT" + "Boundary conditions" mirror
- Deep Interlock: 2 — each section links to other workflows and notes
- Contrast: 2 — sections differ in voice
- Gradients: 1 — could ramp up the stakes more
- Roughness: 1 — too clean, could admit more honest caveats
- Echoes: 2 — "attention" appears 4+ times
- The Void: 2 — closing opens with "Failure modes not handled"
- Simplicity: 2 — no unnecessary sections
- Not Separateness: 2 — connects to other workflows explicitly

**Total: 27/30** — alive and well-formed.
"""


# ============================================================================
# The M3 system prompt (the workshop master's discipline)
# ============================================================================

SYSTEM_PROMPT = """You are the PatternForge workshop master.

Your job: given a user's intent for a new agentic workflow, produce a strict GENERATIVE-CODE.md — the 6-section structure adapted from Christopher Alexander's *The Nature of Order* (2004) Book 3.

The 6 sections (all required, in order):
  1. The design problem — what problem does this workflow solve, what failure does it prevent, what does "done" look like?
  2. The patterns it composes — linked CHIEF notes (the building blocks). If a pattern doesn't exist in the vault, propose its name and describe what it would say.
  3. The sequence (with rationale) — the order of operations, with one-line rationale per step. The rationale is more important than the step.
  4. The values it embodies — the "why" of each step. Vague values → vague workflow.
  5. The stakeholder interactions — when human, when tool, when both, when neither.
  6. The boundary conditions — when NOT to run this workflow, what's out of scope.

Plus two auxiliary sections (all required):
  7. Implementation script — a one-line bash invocation (the script is the OUTPUT, not the workflow)
  8. Wholeness check — self-score the code on Alexander's 15 properties (0-2 each, total 0-30)

CRITICAL RULES:
- DO NOT stop early. ALL 8 sections must be present, in order, complete. If you stop after section 3 or 5, the output is broken.
- Each section must be substantive (multiple paragraphs, real content, no placeholders).
- Be specific. "Be careful" is not a value. "Reversibility over speed" is.
- Quote the CHIEF note names with [[wikilink]] syntax. If a pattern doesn't exist, say "[[Pattern Name]] (proposed)".
- The sequence is ordered, not a list. Order matters.
- The values are *operational* — "be curious" is bad; "ask 'what is this also?' before responding" is good.
- The boundary conditions are *exclusionary* — list the things this workflow does NOT do, not the things it does.
- The wholeness check is honest. Don't inflate. A 22/30 is honest; a 30/30 is suspicious.

Output ONLY the markdown. No preamble, no explanation, no "here's the generative code." Start with the H1 title.
"""


USER_PROMPT_TEMPLATE = """# Workshop request

A new agentic workflow is needed. The intent:

> {intent}

{vault_context}

# Output

Produce the GENERATIVE-CODE.md following the 6-section + 2-auxiliary structure. Use [[wikilink]] syntax for pattern references. Be specific. Be honest about boundary conditions and wholeness.
"""


# ============================================================================
# The M3 caller — wraps `mmx text chat`
# ============================================================================

def call_m3(system: str, user: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
    """Call M3 via the `mmx` CLI and return the assistant's text content.

    Esalen posture: M3 is the workshop master; Python is the file system.
    """
    cmd = [
        "mmx", "text", "chat",
        "--model", "MiniMax-M3",
        "--system", system,
        "--message", user,
        "--temperature", str(temperature),
        "--max-tokens", str(max_tokens),
        "--output", "json",  # we want JSON to parse reliably
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except FileNotFoundError:
        sys.stderr.write("PatternForge: `mmx` CLI not found in PATH\n")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        sys.stderr.write("PatternForge: mmx call timed out after 180s\n")
        sys.exit(1)

    if result.returncode != 0:
        sys.stderr.write(f"PatternForge: mmx exited with code {result.returncode}\n")
        sys.stderr.write(f"stderr: {result.stderr}\n")
        sys.exit(1)

    # mmx returns JSON when output is JSON; we asked for default text. Try to parse as JSON.
    raw = result.stdout.strip()
    # The output may be JSON like {"content": [{"type": "text", "text": "..."}], ...}
    if raw.startswith("{"):
        try:
            data = json.loads(raw)
            content = data.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        return item.get("text", "")
            if "text" in data:
                return data["text"]
            if "message" in data:
                return data["message"]
        except json.JSONDecodeError:
            pass
    # Fallback: assume plain text
    return raw


# ============================================================================
# Vault context — find related CHIEF notes for the intent
# ============================================================================

def find_vault_context(vault_root: Path, intent: str, max_results: int = 8) -> str:
    """Find CHIEF notes whose tags or titles match the intent. Return as context for M3."""
    if not vault_root or not vault_root.is_dir():
        return ""

    intent_words = re.findall(r"\w{3,}", intent.lower())
    if not intent_words:
        return ""

    candidates = []
    for md_file in vault_root.rglob("*.md"):
        if any(p.startswith(".") for p in md_file.parts):
            continue
        if "/99 _system/" in str(md_file):
            continue
        if "00 Inbox" in str(md_file) and "Horizon-Pitches" not in str(md_file):
            continue
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # Score by tag/title match
        score = 0
        text_lower = text.lower()
        for word in intent_words:
            if word in text_lower:
                score += 1
        # Boost for tag match
        if "tags:" in text_lower:
            for word in intent_words:
                if f"- {word}" in text_lower or f"{word}," in text_lower:
                    score += 2
        if score > 0:
            rel = md_file.relative_to(vault_root)
            # Extract title from frontmatter or first H1
            title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else rel.stem
            candidates.append((score, str(rel), title))

    candidates.sort(key=lambda x: -x[0])
    candidates = candidates[:max_results]

    if not candidates:
        return ""

    lines = ["# Related CHIEF notes (use [[wikilink]] syntax to reference these):"]
    for score, rel, title in candidates:
        lines.append(f"- {title} (`{rel}`) — relevance {score}")
    return "\n".join(lines)


# ============================================================================
# The forge command — full LLM call
# ============================================================================

def cmd_forge(args):
    """Generate a generative code by calling M3."""
    if not args.intent:
        sys.stderr.write("PatternForge forge: --intent is required\n")
        sys.exit(1)

    vault_root = Path(args.vault).resolve() if getattr(args, "vault", None) else None
    vault_context = find_vault_context(vault_root, args.intent) if vault_root else ""

    user_prompt = USER_PROMPT_TEMPLATE.format(
        intent=args.intent,
        vault_context=vault_context if vault_context else "(no vault context available)",
    )

    sys.stderr.write(f"PatternForge: forging generative code for: {args.intent[:80]}...\n")
    sys.stderr.write(f"PatternForge: temperature={args.temperature}, model=MiniMax-M3\n")

    code = call_m3(
        system=SYSTEM_PROMPT,
        user=user_prompt,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    # Strip any leading/trailing whitespace and ensure starts with `# GENERATIVE CODE`
    code = code.strip()
    if not code.startswith("#"):
        code = "# GENERATIVE CODE\n\n" + code

    # Add metadata header
    header = (
        f"<!-- Generated by PatternForge on {datetime.now().isoformat(timespec='seconds')} -->\n"
        f"<!-- Source intent: {args.intent} -->\n"
        f"<!-- Model: MiniMax-M3 | Temperature: {args.temperature} -->\n\n"
    )
    code = header + code

    # Output
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(code, encoding="utf-8")
        sys.stderr.write(f"PatternForge: wrote {out_path} ({len(code)} chars)\n")
    else:
        sys.stdout.write(code)
        if not code.endswith("\n"):
            sys.stdout.write("\n")


# ============================================================================
# The shape command — manual templating (no LLM)
# ============================================================================

def cmd_shape(args):
    """Write the template or a manually-filled version."""
    if args.content:
        # User provided the content; template it
        # Try to extract the 6 sections
        out = GENERATIVE_CODE_TEMPLATE.replace(
            "<workflow name>", args.name or "Untitled Workflow"
        )
        # If the content is already a GENERATIVE-CODE.md, write as-is
        if "# GENERATIVE CODE" in args.content or "## 1. The design problem" in args.content:
            out = args.content
    else:
        out = GENERATIVE_CODE_TEMPLATE.replace(
            "<workflow name>", args.name or "Untitled Workflow"
        )

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out, encoding="utf-8")
        sys.stderr.write(f"PatternForge: wrote {out_path} ({len(out)} chars)\n")
    else:
        sys.stdout.write(out)
        if not out.endswith("\n"):
            sys.stdout.write("\n")


# ============================================================================
# The template / examples commands
# ============================================================================

def cmd_template(args):
    """Print the empty 6-section template."""
    print(GENERATIVE_CODE_TEMPLATE.replace("<workflow name>", args.name or "Untitled Workflow"))


def cmd_examples(args):
    """Print the few-shot examples."""
    print("=" * 60)
    print("EXAMPLE INPUT:")
    print("=" * 60)
    print(EXAMPLE_INPUT_1)
    print()
    print("=" * 60)
    print("EXAMPLE OUTPUT:")
    print("=" * 60)
    print(EXAMPLE_OUTPUT_1)


# ============================================================================
# Main
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pattern-forge",
        description="PatternForge — workflow workshop (M3-powered generative codes)",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # forge
    sp = sub.add_parser(
        "forge",
        help="Generate a generative code by calling M3 (full LLM workshop)",
    )
    sp.add_argument(
        "--vault", type=Path, default=None,
        help="Path to vault root (for related-note context)",
    )
    sp.add_argument(
        "--intent", required=True,
        help="The intent for the new workflow (free text)",
    )
    sp.add_argument(
        "--out", type=Path, default=None,
        help="Write the result to a file instead of stdout",
    )
    sp.add_argument(
        "--temperature", type=float, default=0.7,
        help="Sampling temperature (default 0.7 — workshop mode)",
    )
    sp.add_argument(
        "--max-tokens", type=int, default=8192,
        help="Maximum tokens to generate (default 8192 — long generative codes need room)",
    )
    sp.set_defaults(func=cmd_forge)

    # shape
    sp = sub.add_parser(
        "shape",
        help="Template manually-written content into GENERATIVE-CODE.md (no LLM)",
    )
    sp.add_argument("--name", help="Workflow name (replaces placeholder)")
    sp.add_argument(
        "--content", help="Pre-written content (file path or '-' for stdin)",
    )
    sp.add_argument("--out", type=Path, default=None)
    sp.set_defaults(func=cmd_shape)

    # template
    sp = sub.add_parser("template", help="Print the empty 6-section template")
    sp.add_argument("--name", default=None)
    sp.set_defaults(func=cmd_template)

    # examples
    sp = sub.add_parser("examples", help="Print the few-shot examples")
    sp.set_defaults(func=cmd_examples)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
