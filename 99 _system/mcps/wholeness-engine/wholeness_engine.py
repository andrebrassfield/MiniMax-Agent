"""
Wholeness-Engine — LLM-as-judge for Alexander's 15 properties.

The engine:
1. Reads a CHIEF atomic note
2. Constructs a strict LLM prompt with the 15-property rubric
3. Calls M3 (via mmx text chat) at temperature 0.0 for deterministic grading
4. Parses the JSON response
5. Validates the result and computes structure surgery if score < 18

Esalen posture: M3 does the qualitative grading. Python handles files,
JSON parsing, and surgery validation. One engine, two surfaces
(CLI + Glass Server).

Usage:
    python wholeness_engine.py score --path "02 Notes/patterns/My Note.md"
    python wholeness_engine.py score --stdin < note.md
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

from rubric import PROPERTIES, RUBRIC, SYSTEM_PROMPT, total_to_verdict  # noqa: E402
from surgery import validate_surgery, format_surgery, surgery_template, generate_repair  # noqa: E402


# ============================================================================
# The M3 caller
# ============================================================================

def call_m3_judge(system: str, user: str, temperature: float = 0.0, max_tokens: int = 6144) -> str:
    """Call M3 for the LLM-as-judge. Temperature 0.0 for determinism."""
    cmd = [
        "mmx", "text", "chat",
        "--model", "MiniMax-M3",
        "--system", system,
        "--message", user,
        "--temperature", str(temperature),
        "--max-tokens", str(max_tokens),
        "--output", "json",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        sys.stderr.write("Wholeness-Engine: `mmx` CLI not found in PATH\n")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        sys.stderr.write("Wholeness-Engine: mmx call timed out after 120s\n")
        sys.exit(1)

    if result.returncode != 0:
        sys.stderr.write(f"Wholeness-Engine: mmx exited with code {result.returncode}\n")
        sys.stderr.write(f"stderr: {result.stderr}\n")
        sys.exit(1)

    raw = result.stdout.strip()
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
        except json.JSONDecodeError:
            pass
    return raw


def parse_json_response(raw: str) -> dict:
    """Extract the JSON object from M3's response. Robust to code fences and preamble."""
    # Try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Try extracting from ```json ... ``` fence
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    # Try finding the first { and last }
    first = raw.find("{")
    last = raw.rfind("}")
    if first != -1 and last != -1 and last > first:
        try:
            return json.loads(raw[first:last+1])
        except json.JSONDecodeError:
            pass
    # Last resort
    raise ValueError(f"Could not parse JSON from M3 response: {raw[:200]}...")


# ============================================================================
# The score function
# ============================================================================

def score_note(file_path: Path, vault_root: Path = None, use_cache: bool = True) -> dict:
    """Score a single note. Returns the parsed JSON result with metadata.

    Caches results in 99 _system/mcps/wholeness-engine/cache.jsonl
    keyed by file path + mtime, so we don't re-grade unchanged notes.
    """
    # Read the note
    text = file_path.read_text(encoding="utf-8", errors="replace")
    rel_path = str(file_path.relative_to(vault_root)) if vault_root else str(file_path)
    mtime = file_path.stat().st_mtime

    # Check cache
    cache = _load_cache(vault_root)
    cache_key = f"{rel_path}@{mtime}"
    if use_cache and cache_key in cache:
        return cache[cache_key]

    # Strip frontmatter for grading (the body is what we evaluate)
    body_match = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.DOTALL)
    if body_match:
        body = text[body_match.end():]
    else:
        body = text

    # Truncate very long notes to keep the prompt manageable
    if len(body) > 12000:
        body = body[:12000] + "\n\n[... truncated for grading ...]"

    # Construct the user prompt
    user_prompt = f"""# Note to grade

**Path:** {rel_path}

# Body

{body}

# Output

Return STRICT JSON only. No preamble, no explanation. The JSON must include all 15 properties with score and rationale, plus total, verdict, and (if total < 18) structure_surgery.
"""

    raw = call_m3_judge(SYSTEM_PROMPT, user_prompt, temperature=0.0, max_tokens=6144)
    result = parse_json_response(raw)

    # Validate and enrich
    result = _validate_result(result, rel_path)

    # Cache
    cache[cache_key] = result
    _save_cache(vault_root, cache)

    return result


def _validate_result(result: dict, rel_path: str) -> dict:
    """Validate the LLM's result, fill in defaults, compute surgery if missing."""
    # Ensure all 15 properties are present
    for prop in PROPERTIES:
        if prop not in result.get("properties", {}):
            result.setdefault("properties", {})[prop] = {"score": 0, "rationale": "missing"}
        else:
            entry = result["properties"][prop]
            if "score" not in entry:
                entry["score"] = 0
            if "rationale" not in entry:
                entry["rationale"] = ""
            # Coerce score to 0-2
            try:
                entry["score"] = max(0, min(2, int(entry["score"])))
            except (ValueError, TypeError):
                entry["score"] = 0

    # Compute total if missing
    scores = [p["score"] for p in result["properties"].values()]
    result["total"] = sum(scores)
    result["verdict"] = total_to_verdict(result["total"])

    # Surgery: validate if present, generate from template if missing
    surgery = result.get("structure_surgery", [])
    surgery = validate_surgery(surgery)
    if result["total"] < 18 and not surgery:
        surgery = surgery_template(result["properties"])
    result["structure_surgery"] = surgery

    # Add metadata
    result["rel_path"] = rel_path
    result["scored_at"] = datetime.now().isoformat(timespec="seconds")
    result["model"] = "MiniMax-M3"
    result["temperature"] = 0.0

    return result


def _load_cache(vault_root: Path) -> dict:
    """Load the cache from the wholeness-engine directory."""
    cache_path = _HERE / "cache.jsonl"
    cache = {}
    if not cache_path.is_file():
        return cache
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    key = entry.get("_key")
                    if key:
                        cache[key] = entry
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return cache


def _save_cache(vault_root: Path, cache: dict):
    """Save the cache. Each entry is a JSON line."""
    cache_path = _HERE / "cache.jsonl"
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            for key, value in cache.items():
                value["_key"] = key
                f.write(json.dumps(value) + "\n")
    except OSError as e:
        sys.stderr.write(f"Wholeness-Engine: failed to write cache: {e}\n")


# ============================================================================
# The score command
# ============================================================================

def cmd_score(args):
    """Score a single note."""
    file_path = Path(args.path).resolve()
    if not file_path.is_file():
        sys.stderr.write(f"Not found: {file_path}\n")
        sys.exit(1)

    vault_root = Path(args.vault).resolve() if args.vault else file_path.parent
    result = score_note(file_path, vault_root, use_cache=not args.no_cache)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result, file_path)


def _print_human(result: dict, file_path: Path):
    """Print the result in a human-readable format."""
    total = result["total"]
    verdict = result["verdict"]

    # Color the verdict
    if verdict == "exemplary":
        color_start, color_end = "\033[1;32m", "\033[0m"  # bold green
    elif verdict == "alive":
        color_start, color_end = "\033[32m", "\033[0m"  # green
    elif verdict == "working":
        color_start, color_end = "\033[33m", "\033[0m"  # yellow
    elif verdict == "rough":
        color_start, color_end = "\033[31m", "\033[0m"  # red
    else:
        color_start, color_end = "\033[1;31m", "\033[0m"  # bold red

    use_color = sys.stdout.isatty()
    if use_color:
        score_str = f"{color_start}{total}/30{COLOR_END}" if (color_start := color_start) else f"{total}/30"
    else:
        score_str = f"{total}/30"

    print(f"=== WHOLENESS — {result['rel_path']} ===")
    print(f"Score: {color_start}{total}/30{COLOR_END if use_color else ''}  ({verdict})")
    print(f"Model: {result['model']} (temperature {result['temperature']})")
    print(f"Scored: {result['scored_at']}")
    print()
    for prop in PROPERTIES:
        info = result["properties"][prop]
        score = info["score"]
        bar = "●" * score + "○" * (2 - score)
        if use_color:
            if score == 2:
                bar_str = f"\033[32m{bar}\033[0m"
            elif score == 1:
                bar_str = f"\033[33m{bar}\033[0m"
            else:
                bar_str = f"\033[31m{bar}\033[0m"
        else:
            bar_str = bar
        rationale = info.get("rationale", "")[:100]
        print(f"  {bar_str}  {prop:35s}  {rationale}")
    print()

    # Surgery if needed
    surgery_text = format_surgery(result["structure_surgery"], total)
    if surgery_text:
        print(surgery_text)


# ANSI color helpers (avoid f-string brace issues)
COLOR_END = "\033[0m"


# ============================================================================
# The report command — run across all atomic notes
# ============================================================================

def cmd_report(args):
    """Run the engine on every atomic note and produce a report."""
    vault_root = Path(args.vault).resolve() if args.vault else Path.cwd()
    atomic_dirs = [
        vault_root / "02 Notes" / "patterns",
        vault_root / "02 Notes" / "ideas",
        vault_root / "02 Notes" / "articles",
        vault_root / "02 Notes" / "questions",
        vault_root / "06 Connections",
        vault_root / "00 Inbox",
    ]
    atomic_files = []
    for d in atomic_dirs:
        if d.is_dir():
            atomic_files.extend(d.rglob("*.md"))

    if not atomic_files:
        sys.stderr.write("No atomic notes found\n")
        return

    print(f"Scoring {len(atomic_files)} atomic notes...")
    results = []
    for f in atomic_files:
        try:
            r = score_note(f, vault_root, use_cache=not args.no_cache)
            results.append((f, r))
        except Exception as e:
            sys.stderr.write(f"Failed to score {f}: {e}\n")

    # Sort by total ascending (worst first)
    results.sort(key=lambda x: x[1]["total"])

    if args.json:
        print(json.dumps(
            [{"rel_path": str(f.relative_to(vault_root)), **r} for f, r in results],
            indent=2,
        ))
    else:
        print()
        print(f"=== WHOLENESS REPORT — {datetime.now().isoformat(timespec='seconds')} ===")
        print(f"Vault: {vault_root}")
        print(f"Scored {len(results)} atomic notes")
        print()
        # Distribution
        verdict_counts = {}
        for _, r in results:
            verdict_counts[r["verdict"]] = verdict_counts.get(r["verdict"], 0) + 1
        print("Distribution:")
        for v in ["exemplary", "alive", "working", "rough", "weak"]:
            n = verdict_counts.get(v, 0)
            if n > 0:
                print(f"  {v:12s}  {n}")
        print()
        # Bottom 10
        print("Bottom 10 (need structure surgery):")
        for f, r in results[:10]:
            print(f"  [{r['total']:2d}/30]  {r['rel_path']}")
        print()
        # Top 10
        print("Top 10 (alive or better):")
        for f, r in results[-10:]:
            print(f"  [{r['total']:2d}/30]  {r['rel_path']}")
        print()
        # Mean
        if results:
            mean = sum(r["total"] for _, r in results) / len(results)
            print(f"Mean score: {mean:.1f}/30")
        # Below threshold
        below = sum(1 for _, r in results if r["total"] < 18)
        print(f"Below 18 threshold (need surgery): {below} ({100*below/len(results):.1f}%)")


# ============================================================================
# The cache command — show cache stats
# ============================================================================

def cmd_cache(args):
    """Show cache statistics."""
    cache_path = _HERE / "cache.jsonl"
    if not cache_path.is_file():
        print("No cache yet.")
        return
    count = 0
    size = cache_path.stat().st_size
    with open(cache_path, "r") as f:
        for line in f:
            if line.strip():
                count += 1
    print(f"Cache: {count} entries, {size:,} bytes")
    if args.clear:
        cache_path.unlink()
        print("Cache cleared.")


# ============================================================================
# Main
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wholeness-engine",
        description="Wholeness-Engine — LLM-as-judge for Alexander's 15 properties",
    )
    sub = p.add_subparsers(dest="command", required=True)

    # score
    sp = sub.add_parser("score", help="Score a single note")
    sp.add_argument("--path", required=True, help="Path to note")
    sp.add_argument("--vault", type=Path, default=None, help="Vault root")
    sp.add_argument("--json", action="store_true", help="Output as JSON")
    sp.add_argument("--no-cache", action="store_true", help="Bypass cache")
    sp.set_defaults(func=cmd_score)

    # report
    sp = sub.add_parser("report", help="Run across all atomic notes")
    sp.add_argument("--vault", type=Path, default=None, help="Vault root")
    sp.add_argument("--json", action="store_true", help="Output as JSON")
    sp.add_argument("--no-cache", action="store_true", help="Bypass cache")
    sp.set_defaults(func=cmd_report)

    # cache
    sp = sub.add_parser("cache", help="Show or clear the cache")
    sp.add_argument("--clear", action="store_true", help="Clear cache")
    sp.set_defaults(func=cmd_cache)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
