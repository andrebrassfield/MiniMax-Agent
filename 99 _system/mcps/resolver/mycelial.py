"""
MycelialResolver v2.0 — flow-reinforced skill routing.

Inspired by Physarum polycephalum's flow-reinforcement network. The
biological metaphor:

  - HOT paths: skills frequently and successfully used → "thicken" their
    baseline confidence in the ranking request. Like a Physarum tube
    carrying more flow.
  - COLD paths: skills unused for weeks → decay in baseline confidence,
    unless a query explicitly targets them (the Resurrection Rule).
  - FRESH paths: newly created skills (from PatternForge or manually)
    get an artificial 14-day boost so the system actively tries to use
    its new capabilities.

Esalen posture: the math is fully deterministic in Python. The final
routing decision is M3's, in the context window — but M3 sees the
mycelial context (hot/cold/fresh + modifiers) as a structured hint.
Python never picks the skill; it just shapes the context.

The same data structure is consumed by:
  - mavis-vault mycelial       (CLI table)
  - Glass Server /mycelial     (HTML page)
  - resolver.build_ranking_request  (per-skill context for M3)
"""

from __future__ import annotations

import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# ============================================================
# CONFIG
# ============================================================

VAULT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")
RESOLVER_DIR = VAULT_ROOT / "99 _system" / "mcps" / "resolver"
SKILLS_DIR = VAULT_ROOT / "99 _system" / "skillopt" / "skills"
DAEMON_LOG = VAULT_ROOT / "99 _system" / "logs" / "daemon-runs.jsonl"
AUDIT_LOG = RESOLVER_DIR / "resolver-audit.jsonl"
PROJECTS_DIR = VAULT_ROOT / "03 Projects"
DAYS_WINDOW = 30           # rolling window for "hot path" calc
FRESH_BOOST_DAYS = 14       # fresh-skill boost duration
HOT_PATH_CAP = 0.30         # max +0.3 from hot-path modifier
FRESH_BOOST_CAP = 0.20      # max +0.2 from fresh-skill modifier
DECAY_PENALTY = -0.40       # -0.4 for skills used <5 in 30d
SUCCESS_WEIGHT = 0.20       # max +0.2 from success rate
DECAY_THRESHOLD = 5         # skills with <5 uses in 30d are "decaying"
BASE_CONFIDENCE = 0.5       # neutral default

# PatternForge output patterns (for fresh-skill detection)
PATTERN_FORGE_PATTERN = re.compile(r"^#\s+GENERATIVE-CODE", re.MULTILINE)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class SkillUsage:
    """Aggregated usage of a single skill, ingested from logs."""
    name: str
    use_count_30d: int = 0
    success_count_30d: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None

    def record_use(self, ts: datetime, success: bool = True):
        self.use_count_30d += 1
        if success:
            self.success_count_30d += 1
            if not self.last_success or ts > self.last_success:
                self.last_success = ts
        if not self.last_used or ts > self.last_used:
            self.last_used = ts

    @property
    def success_rate(self) -> float:
        """Bayesian-smoothed success rate (Laplace prior: 1 success, 1 failure)."""
        return (self.success_count_30d + 1) / (self.use_count_30d + 2)

    @property
    def days_since_used(self) -> float:
        if not self.last_used:
            return float("inf")
        # Normalize both datetimes to UTC-aware so the subtraction is correct
        # regardless of the system's local timezone.
        last = self.last_used
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = (now - last).total_seconds() / 86400.0
        return max(0.0, delta)  # never negative (clock skew)


@dataclass
class SkillVine:
    """A skill with its mycelial state — the unit of routing."""
    name: str
    description: str = ""
    tags: list[str] = field(default_factory=list)
    path: str = ""
    created_at: Optional[datetime] = None
    source: str = ""  # "skill-dir" or "patternforge" or "other"
    usage: SkillUsage = field(default_factory=lambda: SkillUsage(name=""))

    @property
    def age_days(self) -> float:
        if not self.created_at:
            return 0.0
        # Normalize to UTC-aware
        created = self.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = (now - created).total_seconds() / 86400.0
        return max(0.0, delta)  # never negative

    @property
    def flow_score(self) -> float:
        """Hot path: linear bonus up to +0.30. Saturates at 60 uses/30d."""
        return min(HOT_PATH_CAP, 0.005 * self.usage.use_count_30d)

    @property
    def fresh_score(self) -> float:
        """Fresh skill: linear decay over 14 days, max +0.20."""
        if self.age_days >= FRESH_BOOST_DAYS:
            return 0.0
        return FRESH_BOOST_CAP * (FRESH_BOOST_DAYS - self.age_days) / FRESH_BOOST_DAYS

    @property
    def decay_penalty(self) -> float:
        """Cold path: -0.40 if used <5 in 30d. Otherwise 0."""
        if self.usage.use_count_30d < DECAY_THRESHOLD:
            return DECAY_PENALTY
        return 0.0

    @property
    def final_confidence(self) -> float:
        """Composite: base + flow + fresh + success + decay. Clamped [0, 1]."""
        score = (
            BASE_CONFIDENCE
            + self.flow_score
            + self.fresh_score
            + SUCCESS_WEIGHT * self.usage.success_rate
            + self.decay_penalty
        )
        return max(0.0, min(1.0, score))

    @property
    def verdict(self) -> str:
        """One-word classification for routing context."""
        if self.fresh_score > 0.05:
            return "fresh"
        if self.decay_penalty < 0:
            return "cold"
        if self.flow_score >= 0.10:
            return "hot"
        return "neutral"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "path": self.path,
            "source": self.source,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "age_days": round(self.age_days, 1),
            "use_count_30d": self.usage.use_count_30d,
            "success_rate": round(self.usage.success_rate, 2),
            "last_used": self.usage.last_used.isoformat() if self.usage.last_used else None,
            "days_since_used": (
                round(self.usage.days_since_used, 1)
                if self.usage.days_since_used != float("inf")
                else None
            ),
            "flow_score": round(self.flow_score, 3),
            "fresh_score": round(self.fresh_score, 3),
            "decay_penalty": round(self.decay_penalty, 3),
            "final_confidence": round(self.final_confidence, 3),
            "verdict": self.verdict,
        }


# ============================================================
# LOG INGESTION
# ============================================================

def _parse_iso(ts: str) -> Optional[datetime]:
    """Parse ISO 8601 timestamp; return None on failure."""
    if not ts:
        return None
    try:
        # Handle +00:00 suffix and Z suffix
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _ingest_daemon_log(usages: dict[str, SkillUsage]) -> int:
    """Ingest daemon-runs.jsonl. Returns count of records parsed."""
    if not DAEMON_LOG.is_file():
        return 0
    count = 0
    cutoff = datetime.now().timestamp() - (DAYS_WINDOW * 86400)
    try:
        for line in DAEMON_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            skill = entry.get("selection_skill")
            if not skill:
                continue
            ts = _parse_iso(entry.get("ts", ""))
            if not ts or ts.timestamp() < cutoff:
                continue
            # Daemon "decision" field tells us if it was actually executed
            decision = entry.get("decision", "")
            success = decision not in ("idle", "error", "skipped", None, "")
            usage = usages.setdefault(skill, SkillUsage(name=skill))
            usage.record_use(ts, success=success)
            count += 1
    except OSError:
        pass
    return count


def _ingest_audit_log(usages: dict[str, SkillUsage]) -> int:
    """Ingest resolver-audit.jsonl. Returns count of records parsed."""
    if not AUDIT_LOG.is_file():
        return 0
    count = 0
    cutoff = datetime.now().timestamp() - (DAYS_WINDOW * 86400)
    try:
        for line in AUDIT_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            # The audit log records which skill M3 picked (top_skill)
            skill = entry.get("top_skill")
            if not skill:
                continue
            ts = _parse_iso(entry.get("ts", ""))
            if not ts or ts.timestamp() < cutoff:
                continue
            # Audit log doesn't have explicit success/fail; treat as success
            usage = usages.setdefault(skill, SkillUsage(name=skill))
            usage.record_use(ts, success=True)
            count += 1
    except OSError:
        pass
    return count


# ============================================================
# SKILL DISCOVERY (with fresh-skill detection)
# ============================================================

def _read_first_paragraph(text: str) -> str:
    """Pull the first paragraph (or quoted tagline) from the skill.md body."""
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5:]
    m = re.search(r"^>\s*(.+?)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(">"):
            continue
        return line[:200]
    return "(no description)"


def _read_tags_from_skill_md(text: str) -> list[str]:
    if not text.startswith("---\n"):
        return []
    end = text.find("\n---\n", 4)
    if end == -1:
        return []
    fm = text[4:end]
    m = re.search(r"^tags:\s*\[(.+?)\]", fm, re.MULTILINE | re.DOTALL)
    if m:
        return [t.strip().strip('"\'') for t in m.group(1).split(",") if t.strip()]
    return []


def _discover_skill_dirs(vault_root: Path) -> list[SkillVine]:
    """Walk SKILLS_DIR and return a SkillVine for each Skill Pack."""
    vines = []
    if not SKILLS_DIR.exists():
        return vines
    for pack_dir in sorted(SKILLS_DIR.iterdir()):
        if not pack_dir.is_dir():
            continue
        if pack_dir.name.startswith("_") or pack_dir.name == "__pycache__":
            continue
        skill_md = pack_dir / "skill.md"
        if not skill_md.exists():
            continue
        try:
            text = skill_md.read_text(encoding="utf-8", errors="ignore")
            stat = skill_md.stat()
        except OSError:
            continue
        vines.append(SkillVine(
            name=pack_dir.name,
            description=_read_first_paragraph(text),
            tags=_read_tags_from_skill_md(text),
            path=str(pack_dir),
            created_at=datetime.fromtimestamp(stat.st_mtime),
            source="skill-dir",
        ))
    return vines


def _discover_patternforge_outputs(vault_root: Path) -> list[SkillVine]:
    """Find PatternForge outputs (GENERATIVE-CODE.md) in 03 Projects/.

    These are treated as fresh-skill candidates: each is a newly-minted
    workflow that the user might invoke. They get the 14-day fresh boost.
    """
    vines = []
    if not PROJECTS_DIR.exists():
        return vines
    cutoff = datetime.now().timestamp() - (FRESH_BOOST_DAYS * 86400)
    for md in PROJECTS_DIR.rglob("*.md"):
        if not md.name.endswith(".md"):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
            stat = md.stat()
        except OSError:
            continue
        # Only count PatternForge outputs (have GENERATIVE CODE header)
        if not PATTERN_FORGE_PATTERN.search(text):
            continue
        if stat.st_mtime < cutoff:
            continue  # only fresh ones (within 14 days)
        rel = md.relative_to(vault_root)
        vines.append(SkillVine(
            name=f"pattern-forge:{rel.stem}",
            description=f"PatternForge output: {rel}",
            tags=["pattern-forge", "fresh"],
            path=str(md),
            created_at=datetime.fromtimestamp(stat.st_mtime),
            source="patternforge",
        ))
    return vines


# ============================================================
# THE MYCELIAL RESOLVER
# ============================================================

class MycelialResolver:
    """Builds and queries the mycelial state — the living routing network.

    Esalen posture: this class only computes and *presents* the mycelial
    state. The final routing decision is M3's, given this state as a
    structured hint.
    """

    def __init__(self, vault_root: Path = VAULT_ROOT):
        self.vault_root = vault_root.resolve()
        self.usage: dict[str, SkillUsage] = {}
        self.vines: list[SkillVine] = []

    def build_state(self) -> dict:
        """Build the full mycelial state. Idempotent and deterministic."""
        # 1. Ingest usage from logs
        self.usage = {}
        daemon_count = _ingest_daemon_log(self.usage)
        audit_count = _ingest_audit_log(self.usage)
        total_records = daemon_count + audit_count

        # 2. Discover skills + fresh outputs
        skill_vines = _discover_skill_dirs(self.vault_root)
        forge_vines = _discover_patternforge_outputs(self.vault_root)

        # 3. Merge into a single list of vines, attaching usage
        vines_by_name = {v.name: v for v in skill_vines}
        for fv in forge_vines:
            vines_by_name[fv.name] = fv
        self.vines = list(vines_by_name.values())

        # Attach usage
        for vine in self.vines:
            if vine.name in self.usage:
                vine.usage = self.usage[vine.name]
            # Also try matching by skill dir basename
            else:
                # Some audit entries might use full path — fallback
                pass

        # 4. Compute summary
        hot = [v for v in self.vines if v.verdict == "hot"]
        cold = [v for v in self.vines if v.verdict == "cold"]
        fresh = [v for v in self.vines if v.verdict == "fresh"]
        neutral = [v for v in self.vines if v.verdict == "neutral"]

        return {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "vault_root": str(self.vault_root),
            "totals": {
                "skills": len(self.vines),
                "skill_dirs": len(skill_vines),
                "patternforge_outputs": len(forge_vines),
                "log_records_30d": total_records,
                "daemon_records": daemon_count,
                "audit_records": audit_count,
                "hot": len(hot),
                "cold": len(cold),
                "fresh": len(fresh),
                "neutral": len(neutral),
            },
            "hottest": [v.to_dict() for v in sorted(hot, key=lambda x: -x.final_confidence)[:5]],
            "decaying": [v.to_dict() for v in sorted(cold, key=lambda x: x.final_confidence)[:5]],
            "boosted": [v.to_dict() for v in sorted(fresh, key=lambda x: -x.fresh_score)[:5]],
            "all_vines": [v.to_dict() for v in sorted(self.vines, key=lambda x: -x.final_confidence)],
        }

    def build_ranking_context(self) -> dict:
        """Build the per-skill mycelial context to inject into ranking requests.

        Consumed by resolver.build_ranking_request() so M3 sees the
        modifiers in the context window. M3 still makes the final call.
        """
        if not self.vines:
            self.build_state()

        # Sort by final_confidence descending
        sorted_vines = sorted(self.vines, key=lambda v: -v.final_confidence)
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "totals": {
                "skills": len(self.vines),
                "hot": sum(1 for v in self.vines if v.verdict == "hot"),
                "cold": sum(1 for v in self.vines if v.verdict == "cold"),
                "fresh": sum(1 for v in self.vines if v.verdict == "fresh"),
            },
            "skills": [v.to_dict() for v in sorted_vines],
            "routing_hints": {
                "hot_paths": [v.name for v in sorted_vines if v.verdict == "hot"][:3],
                "cold_paths": [v.name for v in sorted_vines if v.verdict == "cold"][:3],
                "fresh_boosts": [v.name for v in sorted_vines if v.verdict == "fresh"][:3],
                "resurrection_rule": (
                    "Cold skills remain in the candidate set. If the user's query "
                    "explicitly matches a cold skill's tags or description, you may "
                    "still select it. The decay is a *default*, not a hard filter."
                ),
            },
        }

    def render_cli_table(self, state: dict = None) -> str:
        """Render the mycelial state as a CLI table for mavis-vault."""
        if state is None:
            state = self.build_state()
        totals = state["totals"]
        c = C()

        lines = []
        lines.append("")
        lines.append(f"{c.BOLD}════════════════════════════════════════════════════════════════════════{c.RESET}")
        lines.append(f"{c.BOLD}  MYCELIAL NETWORK — Skill Routing State{c.RESET}")
        lines.append(f"  Generated: {state['generated_at']}")
        lines.append(f"  Skills indexed: {totals['skills']} "
                     f"({totals['hot']} hot, {totals['cold']} decaying, "
                     f"{totals['fresh']} fresh, {totals['neutral']} neutral)")
        lines.append(f"  Log records (30d): {totals['log_records_30d']} "
                     f"({totals['daemon_records']} daemon + {totals['audit_records']} audit)")
        lines.append(f"{c.BOLD}════════════════════════════════════════════════════════════════════════{c.RESET}")
        lines.append("")

        # Hottest pathways
        lines.append(f"{c.RED}🔥 HOTTEST PATHWAYS{c.RESET} (top 5)")
        if state["hottest"]:
            for v in state["hottest"]:
                bar = self._bar(v["final_confidence"])
                lines.append(
                    f"  {bar}  {c.BOLD}{v['name']:<28s}{c.RESET} "
                    f"{v['use_count_30d']:>3d} uses  "
                    f"{int(v['success_rate']*100):>3d}% succ  "
                    f"{c.DIM}last used {int(v['days_since_used'])}d ago{c.RESET}"
                )
        else:
            lines.append(f"  {c.DIM}(no hot paths yet — system needs more invocations){c.RESET}")
        lines.append("")

        # Decaying paths
        lines.append(f"{c.BLUE}🧊 DECAYING PATHS{c.RESET} (bottom 5)")
        if state["decaying"]:
            for v in state["decaying"]:
                bar = self._bar(v["final_confidence"])
                lines.append(
                    f"  {bar}  {v['name']:<28s} "
                    f"{v['use_count_30d']:>3d} uses  "
                    f"{c.DIM}last used {int(v['days_since_used'])}d ago{c.RESET}"
                )
        else:
            lines.append(f"  {c.DIM}(no decaying paths — all skills are active){c.RESET}")
        lines.append("")

        # Fresh-skill boosts
        lines.append(f"{c.GREEN}✨ FRESH-SKILL BOOSTS{c.RESET} (< 14d old)")
        if state["boosted"]:
            for v in state["boosted"]:
                days_left = max(0, FRESH_BOOST_DAYS - int(v["age_days"]))
                bar = self._bar(v["final_confidence"])
                lines.append(
                    f"  {bar}  {v['name']:<28s} "
                    f"{int(v['age_days'])}d old  "
                    f"{c.GREEN}{days_left}d boost left{c.RESET}"
                )
        else:
            lines.append(f"  {c.DIM}(no fresh boosts active){c.RESET}")
        lines.append("")

        # Routing decision history (last 7d, top 5)
        lines.append(f"{c.BOLD}📊 ROUTING DECISIONS (last 7d, top 5){c.RESET}")
        top_decisions = sorted(
            [v for v in state["all_vines"] if v["use_count_30d"] > 0],
            key=lambda x: -x["use_count_30d"],
        )[:5]
        if top_decisions:
            for v in top_decisions:
                lines.append(f"  {v['name']:<28s}  → {v['use_count_30d']:>3d} selections")
        else:
            lines.append(f"  {c.DIM}(no routing decisions in the last 7 days){c.RESET}")
        lines.append(f"{c.BOLD}════════════════════════════════════════════════════════════════════════{c.RESET}")
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _bar(confidence: float) -> str:
        """Render a confidence bar (10 chars wide)."""
        filled = int(round(confidence * 10))
        bar = "█" * filled + "░" * (10 - filled)
        if confidence >= 0.7:
            color = "\033[32m"  # green
        elif confidence >= 0.4:
            color = "\033[33m"  # yellow
        else:
            color = "\033[31m"  # red
        return f"{color}{bar}\033[0m {confidence:.2f}"


# ANSI helpers
class C:
    USE = sys.stdout.isatty()
    RED = "\033[31m" if USE else ""
    GREEN = "\033[32m" if USE else ""
    YELLOW = "\033[33m" if USE else ""
    BLUE = "\033[34m" if USE else ""
    BOLD = "\033[1m" if USE else ""
    DIM = "\033[2m" if USE else ""
    RESET = "\033[0m" if USE else ""


# ============================================================
# CLI
# ============================================================

def main():
    import argparse
    p = argparse.ArgumentParser(
        prog="mycelial",
        description="MycelialResolver v2.0 — flow-reinforced skill routing",
    )
    p.add_argument("--vault", type=Path, default=VAULT_ROOT)
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.add_argument("--ranking-context", action="store_true",
                   help="Output the per-skill context for resolver ranking requests")
    args = p.parse_args()

    resolver = MycelialResolver(args.vault)
    if args.ranking_context:
        print(json.dumps(resolver.build_ranking_context(), indent=2))
    elif args.json:
        print(json.dumps(resolver.build_state(), indent=2))
    else:
        print(resolver.render_cli_table())


if __name__ == "__main__":
    main()
