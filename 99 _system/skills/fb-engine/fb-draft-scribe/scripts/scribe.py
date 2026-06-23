#!/usr/bin/env python3
"""fb-draft-scribe: generate FB-Engine drafts from fb-group-reader output.

The mechanism: ingest the JSON output of `fb-group-reader` (the read path),
sample 1-2 relevant entries from `ammunition.mdl` per post, apply the
typology formula, and write draft markdown files to
`03 Projects/FB-Engine/drafts/`.

Two typologies:
- Typology 1 (Group Value Bomb, original post): requires operator-provided
  hook via `--hook`. The Scribe fills in the metric + breakdown + question.
- Typology 2 (Authority Comment, reply): default. The Scribe reads each
  post from `--from-reader` and generates a reply that acknowledges the
  premise + injects a constraint + names the actual bottleneck.

The Scribe NEVER publishes. It only writes to `drafts/`. The operator
reviews each draft via the Telegram bridge, then approves → `approved/`,
which the Poster consumes.

v1.0.0 generation strategy: deterministic template-based. The Scribe
samples ammunition, then fills a typology template with the post text
+ sampled metric. Output is mechanical but functional; the operator
edits drafts before approving. Phase 3 will add an LLM-backed
generation mode via the `--use-llm` flag (callable through the mavis
runtime's LLM access).

Usage:
    # Typology 2 (default): reply to each post in the JSON
    python3 scribe.py --from-reader /tmp/fb-posts.json

    # Typology 1: Value Bomb with operator-provided hook
    python3 scribe.py --typology 1 \\
        --hook "Most HVAC owners I talk to are losing $400/day to missed calls" \\
        --pillar 1

    # Combined: T1 first, then T2 for each post in JSON
    python3 scribe.py --from-reader /tmp/fb-posts.json \\
        --hook "Most HVAC owners I talk to are losing $400/day to missed calls" \\
        --pillar 1

Output: one markdown file per draft in the output dir, e.g.
  drafts/2026-06-18-1330-t2-post-1234567890.md
  drafts/2026-06-18-1330-t1-value-bomb-hvac-missed-calls.md
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------- Ammunition ledger parsing ----------

LEDGER_PATH = Path("03 Projects/FB-Engine/ammunition.mdl")
PILLAR_KEYWORDS: dict[str, list[str]] = {
    "1": ["missed call", "phone", "call", "cac", "ltv", "cost", "acquisition",
          "lifetime", "lead", "churn", "patient", "client", "marketing", "spend"],
    "2": ["automation", "ai", "bot", "dispatch", "response time", "after-hours",
          "after hours", "weekend", "booking", "inventory", "support", "ticket",
          "tech debt", "operations", "workflow", "bottleneck"],
    "3": ["saas", "tool", "stack", "platform", "switch", "migrate", "software",
          "vendor", "per-seat", "per seat", "lock-in", "lock in", "integration",
          "export", "api", "rate limit", "stack", "subscription"],
}

PILLAR_NAMES: dict[str, str] = {
    "1": "CAC & LTV Math",
    "2": "Operational Bottlenecks",
    "3": "Software Stack Friction",
}


def parse_ledger(ledger_path: Path) -> list[dict[str, str]]:
    """Parse the append-only section of ammunition.mdl into entry dicts."""
    if not ledger_path.exists():
        return []
    text = ledger_path.read_text(encoding="utf-8")
    # Find the append-only ledger section. The marker is intentionally
    # specific (matches the X-CE pattern) so the frontmatter description
    # (which contains a bare "## Append-only ledger" reference) doesn't
    # match.
    marker = "## Append-only ledger (do not edit above this line"
    if marker not in text:
        return []
    section = text.split(marker, 1)[1]
    entries: list[dict[str, str]] = []
    for line in section.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        # Format: [Date] | [Topic] | [Typology] | [Claim] | [Source]
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5:
            continue
        date, topic, typology, claim, source = parts[0], parts[1], parts[2], parts[3], "|".join(parts[4:]).strip()
        # Skip sub-headers like "## Pillar 1: CAC & LTV Math" (but NOT
        # topic tags like "#local-service" which legitimately start with #).
        if topic.startswith("##") or "Pillar" in topic:
            continue
        entries.append({
            "date": date,
            "topic": topic,
            "typology": typology,
            "claim": claim,
            "source": source,
        })
    return entries


def sample_ammunition(
    post_text: str,
    entries: list[dict[str, str]],
    n: int = 2,
    pillar_hint: str | None = None,
) -> list[dict[str, str]]:
    """Sample n relevant ammunition entries for a post.

    Heuristic:
    - If pillar_hint is set, prefer entries from that pillar's topic tags.
    - Otherwise, compute keyword overlap between post text and each entry's
      claim (using PILLAR_KEYWORDS).
    - Tiebreak: prefer more recent entries, then random.
    - Fallback: random sample of n entries from the ledger.
    """
    if not entries:
        return []
    post_lower = post_text.lower()

    def score(entry: dict[str, str]) -> tuple[int, int]:
        # Pillar match score
        pillar_score = 0
        if pillar_hint:
            for kw in PILLAR_KEYWORDS.get(pillar_hint, []):
                if kw in post_lower:
                    pillar_score += 2
                if kw in entry["claim"].lower():
                    pillar_score += 1
        else:
            # Detect pillar from entry's topic tag
            for p, kws in PILLAR_KEYWORDS.items():
                for kw in kws:
                    if kw in post_lower:
                        pillar_score += 1
                        break
        # Recency score (later dates rank higher)
        try:
            date_score = int(entry["date"].replace("-", ""))
        except (ValueError, AttributeError):
            date_score = 0
        return (pillar_score, date_score)

    scored = sorted(entries, key=score, reverse=True)
    top = scored[: max(n, 4)]  # top-4 candidates, then pick n
    # Stable random pick from top-N — using entry hash for determinism
    import hashlib as _h
    seed = _h.md5(post_lower.encode("utf-8")).hexdigest()
    rng_state = int(seed[:8], 16)
    picked: list[dict[str, str]] = []
    for entry in top:
        if len(picked) >= n:
            break
        # Deterministic: include if (hash % 3 != 0) or first one
        if not picked or (rng_state % 3) != len(picked) % 3:
            picked.append(entry)
    # If we still don't have n, fill from the rest
    if len(picked) < n:
        for entry in scored:
            if entry in picked:
                continue
            picked.append(entry)
            if len(picked) >= n:
                break
    return picked[:n]


# ---------- Draft generation ----------

def _slugify(s: str, max_len: int = 50) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:max_len].rstrip("-")


def _post_id_slug(post_id: str | int | None) -> str:
    if post_id is None:
        return "unknown"
    s = str(post_id)
    return s[:20] if len(s) > 20 else s


def generate_t1_draft(
    hook: str,
    pillar: str,
    ammo: list[dict[str, str]],
) -> str:
    """Generate a Typology 1 (Value Bomb) draft from a hook + sampled ammo."""
    pillar_name = PILLAR_NAMES.get(pillar, "the work")
    metric_lines: list[str] = []
    for i, a in enumerate(ammo[:2], start=1):
        metric_lines.append(f"  - {a['claim']} *(Source: {a['source']})*")
    metrics_block = "\n".join(metric_lines) if metric_lines else "  - (no specific metric injected — operator to add)"

    # Step derivations: 3 mechanical steps from the pillar name + first metric
    first_metric = ammo[0]["claim"] if ammo else "the bottleneck in question"
    steps = [
        f"Audit your last 30 days of {pillar_name.lower()} data — count the actual occurrences of {first_metric[:60]}...",
        f"Apply a 10x cost multiple: every missed instance costs the LTV multiple, not just the immediate job.",
        f"Pick the single highest-volume leak. Fix that one. Defer the rest. The 80/20 here is brutal but real.",
    ]
    steps_block = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    pain_var = {
        "1": "missed-call",
        "2": "after-hours-response",
        "3": "per-seat",
    }.get(pillar, "friction-cost")

    return (
        f"{hook}\n"
        f"\n"
        f"The math on this is pretty brutal:\n"
        f"{metrics_block}\n"
        f"\n"
        f"Here's the 3-step breakdown:\n"
        f"{steps_block}\n"
        f"\n"
        f"Anyone else running into this in their business? What's your {pain_var} cost looking like?"
    )


def generate_t2_draft(
    post_text: str,
    ammo: list[dict[str, str]],
) -> str:
    """Generate a Typology 2 (Authority Comment) draft from a post + ammo."""
    # Premise paraphrase: first sentence of the post, lightly trimmed
    premise = post_text.strip().split(".")[0]
    if len(premise) > 200:
        premise = premise[:200].rstrip() + "..."
    premise = premise.replace("\n", " ")

    if not ammo:
        return (
            f"Yeah, {premise.lower()} — that's a real problem in a lot of operator circles.\n"
            f"\n"
            f"(Scribe did not find a matching ammunition entry — operator to add a specific metric before approving.)"
        )

    constraint = ammo[0]["claim"]
    # The ledger's source field starts with "Source: " — strip the prefix
    # so the template wrapper (which adds "*(Source: ...)*") renders cleanly.
    source = ammo[0]["source"]
    source = re.sub(r"^Source:\s*", "", source, flags=re.IGNORECASE)
    # Pick a bottleneck name from the constraint (first noun phrase, or default)
    bottleneck = "the actual root cause"
    claim_lower = constraint.lower()
    if "lock-in" in claim_lower or "lock in" in claim_lower:
        bottleneck = "the lock-in margin transfer"
    elif "missed" in claim_lower:
        bottleneck = "the missed-call math, not the labor cost"
    elif "lead response" in claim_lower or "5 min" in claim_lower:
        bottleneck = "the 5-minute response window, not the lead volume"
    elif "stack" in claim_lower or "saas" in claim_lower:
        bottleneck = "the SaaS sprawl, not the per-tool cost"
    elif "churn" in claim_lower:
        bottleneck = "the churn rate, not the new-client acquisition"
    elif "integration" in claim_lower or "switch" in claim_lower:
        bottleneck = "the integration / switching cost, not the tool price"
    elif "booking" in claim_lower or "friction" in claim_lower:
        bottleneck = "the booking friction, not the lead quality"
    elif "support" in claim_lower or "response" in claim_lower:
        bottleneck = "the response time, not the support volume"
    else:
        # Try to extract a noun phrase
        m = re.search(r"\b(?:is|are)\s+(?:about\s+)?(?:the\s+)?([\w\s-]+?)(?:,|\.|\s+not\b)", claim_lower)
        if m:
            bottleneck = m.group(1).strip()[:60]

    explanation = (
        f"the per-event cost in {bottleneck} is what compounds — the hourly/dollar "
        f"savings people chase is the wrong unit"
        if "cost" in claim_lower or "$" in constraint
        else f"once you fix {bottleneck}, the rest of the optimization is mechanical"
    )

    return (
        f"Yeah, {premise.lower()} — that's a real problem in a lot of operator circles.\n"
        f"\n"
        f"The thing I'd add: {constraint} *(Source: {source})*\n"
        f"\n"
        f"In our experience, the actual bottleneck is {bottleneck} — not the thing most folks focus on. {explanation.capitalize()}."
    )


# ---------- Draft writing ----------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _draft_id(typology: str, source_key: str) -> str:
    """Stable draft_id for the Telegram bridge to match replies to."""
    h = hashlib.sha256(f"{typology}|{source_key}|{_now_iso()}".encode("utf-8")).hexdigest()[:10]
    return f"fb-{typology}-{source_key}-{h}"


def write_draft(
    output_dir: Path,
    typology: str,
    source_key: str,
    post_meta: dict[str, Any] | None,
    ammo: list[dict[str, str]],
    body: str,
) -> Path:
    """Write a draft markdown file with frontmatter + body."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    slug = _slugify(source_key)[:40]
    fname = f"{timestamp}-t{typology[-1]}-{slug}.md"
    out_path = output_dir / fname

    draft_id = _draft_id(typology, source_key)
    ammo_lines = "\n".join(
        f"  - pillar={a['topic']} | {a['typology']} | {a['claim']} | source={a['source']}"
        for a in ammo
    )
    frontmatter_lines = [
        "---",
        f"draft_id: {draft_id}",
        "scribe: fb-draft-scribe",
        f"typology: T{typology[-1]}",
        "status: open",
        f"created_at: {_now_iso()}",
    ]
    if post_meta:
        if post_meta.get("post_id"):
            frontmatter_lines.append(f"original_post_id: {post_meta['post_id']}")
        if post_meta.get("author"):
            frontmatter_lines.append(f"original_author: \"{post_meta['author']}\"")
        if post_meta.get("url"):
            frontmatter_lines.append(f"original_url: {post_meta['url']}")
    frontmatter_lines.extend([
        "ammunition_used: |",
        ammo_lines or "  - (none sampled)",
        "---",
        "",
        "## Generated draft",
        "",
        body,
        "",
        "---",
        "",
        "## Notes for Andre",
        "",
        f"- Typology: T{typology[-1]} ({'Group Value Bomb' if typology.endswith('1') else 'Authority Comment'})",
        f"- Ammunition entries used: {len(ammo)}",
        f"- Status: open — awaiting your approval via Telegram",
        f"- To approve: reply to the Telegram message with `approve`",
        f"- To deny: reply with `deny`",
        f"- To edit: reply with the edited text",
        "",
    ])
    if post_meta:
        frontmatter_lines.extend([
            "## Original post (for context)",
            "",
            f"- Author: {post_meta.get('author', 'unknown')}",
            f"- Post ID: {post_meta.get('post_id', 'unknown')}",
            f"- URL: {post_meta.get('url', 'unknown')}",
            f"- Timestamp: {post_meta.get('timestamp', 'unknown')}",
            "",
            "```",
            (post_meta.get("text", "")[:1000] + ("..." if len(post_meta.get("text", "")) > 1000 else "")),
            "```",
            "",
        ])

    out_path.write_text("\n".join(frontmatter_lines), encoding="utf-8")
    return out_path


# ---------- Entry point ----------

def main() -> int:
    parser = argparse.ArgumentParser(description="FB-Engine Scribe (draft generator)")
    parser.add_argument("--from-reader", type=Path, default=None,
                        help="Path to fb-group-reader JSON output (Typology 2 mode)")
    parser.add_argument("--typology", choices=["1", "2", "auto"], default="auto",
                        help="Typology: 1 (Value Bomb, requires --hook), 2 (Authority Comment), auto (default: T2 per post)")
    parser.add_argument("--hook", type=str, default=None,
                        help="Operator-provided hook for Typology 1 (Value Bomb)")
    parser.add_argument("--pillar", choices=["1", "2", "3"], default=None,
                        help="Bias sampling toward this pillar (1=CAC/LTV, 2=Ops, 3=Stack)")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("03 Projects/FB-Engine/drafts"),
                        help="Output directory for draft markdown files")
    parser.add_argument("--ledger", type=Path, default=LEDGER_PATH,
                        help=f"Path to ammunition.mdl (default: {LEDGER_PATH})")
    parser.add_argument("--max-drafts", type=int, default=10,
                        help="Max drafts to generate per run (default: 10)")
    args = parser.parse_args()

    entries = parse_ledger(args.ledger)
    if not entries:
        print(f"WARNING: no entries parsed from {args.ledger}", file=sys.stderr)
        print(f"  Continuing with empty ammunition (drafts will flag the gap)", file=sys.stderr)

    drafts_written: list[Path] = []

    # Typology 1: Value Bomb with operator-provided hook
    if args.typology == "1" or (args.typology == "auto" and args.hook):
        if not args.hook:
            print("ERROR: Typology 1 requires --hook", file=sys.stderr)
            return 1
        if not args.pillar:
            print("WARNING: --pillar not set for Typology 1; sampling across all pillars", file=sys.stderr)
        ammo = sample_ammunition(args.hook, entries, n=2, pillar_hint=args.pillar)
        body = generate_t1_draft(args.hook, args.pillar or "1", ammo)
        out = write_draft(
            output_dir=args.output_dir,
            typology="1",
            source_key=f"value-bomb-{_slugify(args.hook)[:30]}",
            post_meta=None,
            ammo=ammo,
            body=body,
        )
        drafts_written.append(out)
        print(f"[fb-draft-scribe] T1 Value Bomb → {out}", file=sys.stderr)

    # Typology 2: reply to each post in the JSON
    if (args.typology == "2" or args.typology == "auto") and args.from_reader:
        if not args.from_reader.exists():
            print(f"ERROR: --from-reader path does not exist: {args.from_reader}", file=sys.stderr)
            return 1
        data = json.loads(args.from_reader.read_text(encoding="utf-8"))
        results = data.get("results", [])
        if not results:
            print(f"WARNING: no posts in {args.from_reader}", file=sys.stderr)
        for post in results[: args.max_drafts]:
            post_text = post.get("text", "")
            post_id = post.get("post_id", "unknown")
            post_url = post.get("url") or (
                f"https://www.facebook.com/groups/<group>/posts/{post_id}"
            )
            post_meta = {
                "post_id": post_id,
                "author": post.get("author", "unknown"),
                "text": post_text,
                "url": post_url,
                "timestamp": post.get("timestamp"),
            }
            ammo = sample_ammunition(post_text, entries, n=2, pillar_hint=args.pillar)
            body = generate_t2_draft(post_text, ammo)
            out = write_draft(
                output_dir=args.output_dir,
                typology="2",
                source_key=f"post-{_post_id_slug(post_id)}",
                post_meta=post_meta,
                ammo=ammo,
                body=body,
            )
            drafts_written.append(out)
            print(f"[fb-draft-scribe] T2 Authority Comment → {out}", file=sys.stderr)

    if not drafts_written:
        print(
            "[fb-draft-scribe] no drafts written — provide --from-reader (T2) or "
            "--typology 1 --hook (T1), or both",
            file=sys.stderr,
        )
        return 1

    print(f"[fb-draft-scribe] wrote {len(drafts_written)} drafts to {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
