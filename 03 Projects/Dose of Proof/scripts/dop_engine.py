#!/usr/bin/env python3
"""
Dose of Proof — Daily Content Engine v0.3 (gate-implementing)

Reads source corpus, generates 8-11 posts per day for the Postiz channels,
runs compliance audit (8-item + triage-gate-spec §1 self-classification block),
writes to queue/drafts-YYYY-MM-DD.mdl + queue/blocked-records-YYYY-MM-DD.mdl
(if any SENSITIVE posts generated).

v0.3 CHANGES (per triage-gate-spec V1+V2+V3+V8 implementation, 2026-06-25 18:30 CT):
- **V1 self-classification block (§1)** — every post outputs a header with
    POST_ID | PLATFORM | HOOK_FAMILY | CLASSIFICATION | SENSITIVE_REASONS |
    SENSITIVE_FLAGS_DETAIL before the body. CLASSIFICATION = CLEAR | SENSITIVE.
    Errs toward SENSITIVE on ambiguity (spec §1).
- **V2 sensitivity taxonomy (§2)** — S1-S4 trigger patterns encoded with concrete
    examples (cure/heal/banned phrases + new S1-S4 regex set).
- **V3 block record queue** — SENSITIVE posts also written to
    queue/blocked-records-YYYY-MM-DD.mdl with §3a 15-field schema, BLOCKED status.
- **V8 hook-family taxonomy (§5)** — output tag on every post is one of 8 §5
    hook families (regulatory-reality, biomarker-education, terrain-mechanics,
    citizen-science, literature-map, reconstitution-math, telehealth-routing,
    community-proof). Pillar rotation (P1/P2/P3/PCAC) persists internally as
    content-calendar logic only — output tag is hook family.

v0.2 BEHAVIOR (volume bump — "take over the market"):
- Pillar rotation: P1 Mon/Thu/Sun | P2 Tue/Fri | P3 Wed/Sat | PCAC-Deep-Dive weekly
- Channel split: 6 Facebook text + 1 multi-image FB + 1 Instagram carousel + 3 Pinterest pins per day
- Source: prelaunch calendar (which asset for which date) + existing X thread / LinkedIn / Substack corpus
- FB text: programmatic from hooks in source asset
- FB multi-image: reuses the IG carousel slides (FB supports up to 10 images per post)
- IG carousel: reuses existing rendered slides
- Pinterest pins: cover + secondary data slide + CTA — 3 separate pins per source, Dre batch-pushes
- Compliance: programmatic 8-item audit (dop_compliance.py) + triage-gate-spec §1 self-classification

Volume: 11 posts/day across 4 active channels (FB × 7, IG × 1, Pinterest × 3 Dre-pushed).

DEFERRED CHANNELS (per Andre 2026-06-25):
- TikTok + YouTube Shorts — DEFERRED until after Jul 7 PCAC recap window.
  Phase 2.5 video pipeline (matrix MCP text-to-video / image-to-video + ffmpeg
  concat + Postiz video attachments) NOT built. Reassess after we have real
  hook-family bias + performance data from the 11/day cadence. Do NOT add
  video attachments to this engine without explicit Andre go.
- LinkedIn — DEFERRED until Company Page is confirmed. Repurposing only.

Usage:
    python3 dop_engine.py                          # generate tomorrow's posts
    python3 dop_engine.py --date 2026-06-26        # specific date
    python3 dop_engine.py --dry-run                # parse + audit only, no queue write
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add this script's dir to path so we can import dop_compliance
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
import dop_compliance as compliance

# =============================================================================
# §3d HALT HARD INTERLOCK — Co-CEO rule 2026-06-25
# Per [[triage-gate-spec]] §3d, the engine refuses to run if HALTED.
# This is a code-level precondition, not a prompt instruction.
# =============================================================================
HALT_STATE_FILE = Path.home() / ".mavis" / "state" / "dop-engine-halt.state"

def check_halt_precondition() -> int:
    """
    Returns 0 if engine may run, non-zero if HALTED.
    Called as the FIRST action in main() before any work.
    """
    if not HALT_STATE_FILE.exists():
        return 0  # No halt state file → engine may run
    try:
        state = json.loads(HALT_STATE_FILE.read_text())
        if state.get("halted"):
            print(f"⛔ ENGINE HALTED — refusing to run.", file=sys.stderr)
            print(f"   Halted at: {state.get('halted_at')}", file=sys.stderr)
            print(f"   Halted by: {state.get('halted_by')}", file=sys.stderr)
            print(f"   Reason: {state.get('reason')}", file=sys.stderr)
            print(f"   Resume condition: {state.get('resume_condition')}", file=sys.stderr)
            print(f"   To resume: edit {HALT_STATE_FILE} and set halted:false, OR delete the file.", file=sys.stderr)
            print(f"   See [[triage-gate-spec]] §3d.", file=sys.stderr)
            return 78  # EX_CONFIG — configuration error
        else:
            return 0  # Halt state file present but halted:false → engine may run
    except (json.JSONDecodeError, KeyError) as e:
        print(f"⛔ ENGINE HALTED — halt state file malformed: {e}", file=sys.stderr)
        print(f"   Treating as halted (fail-closed). See [[triage-gate-spec]] §3d.", file=sys.stderr)
        return 78  # Treat malformed as halted (fail-closed)

# Paths
PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
SOCIAL_DIR = PROJECT_ROOT / "assets" / "social"
QUEUE_DIR = PROJECT_ROOT / "queue"
VISUAL_DIR = PROJECT_ROOT / "assets" / "visual"

# Pillar rotation by weekday (0=Mon, 6=Sun) — content-calendar logic only, NOT output tag
PILLAR_ROTATION = {
    0: "P1",  # Mon: Lived Protocol
    1: "P2",  # Tue: Macro-Longevity Economy
    2: "P3",  # Wed: Reconstitution & Data Utility
    3: "P1",  # Thu: Lived Protocol
    4: "P2",  # Fri: Macro-Longevity Economy
    5: "P3",  # Sat: Reconstitution & Data Utility
    6: "PCAC",  # Sun: PCAC deep-dive
}

# V8: §5 Hook-Family Taxonomy (canonical — output tag on every post)
HOOK_FAMILIES = {
    "regulatory-reality":    {"risk": "Low",       "desc": "PCAC, FDA, scheduling, policy translation"},
    "biomarker-education":   {"risk": "Medium",    "desc": "Lab markers, panels, tracking frameworks"},
    "terrain-mechanics":     {"risk": "Medium",    "desc": "CCI, vagus, MCAS, guarding loop, upstream drivers"},
    "citizen-science":       {"risk": "High",      "desc": "Dre's own data, protocol documentation, n=1 framing"},
    "literature-map":        {"risk": "Low-Medium","desc": "PubMed/peer-reviewed research translation"},
    "reconstitution-math":   {"risk": "High",      "desc": "Dose Calc utility content, math, BAC water, syringe ticks"},
    "telehealth-routing":    {"risk": "Medium",    "desc": "Marek Health, Lifeforce, supervised protocol framing"},
    "community-proof":       {"risk": "High",      "desc": "Skool/testimonial-adjacent content"},
}

# V8: Pillar → hook family mapping (pillar persists as calendar logic, output tag = hook family)
PILLAR_TO_HOOK_FAMILY = {
    "P1":   "citizen-science",      # Lived Protocol → Dre's own data / n=1 framing
    "P2":   "regulatory-reality",   # Macro-Longevity Economy → regulatory framing
    "P3":   "reconstitution-math",  # Reconstitution & Data Utility → math/utility
    "PCAC": "regulatory-reality",   # PCAC deep-dive → regulatory
}

# V1/V2: S1-S4 self-classification trigger patterns (per triage-gate-spec §1 + §2)
S1_PRESCRIBING_PATTERNS = [
    r"\byou\s+should\s+take\b",
    r"\brecommended\s+dosage\b",
    r"\bstart\s+with\s+\d+\s*(mg|mcg|ml)\b",
    r"\bprescribe\b",
    r"\bprotocol\s*:\s*take\b",
    r"\bthis\s+worked\s+for\s+me\s+at\s+\d+\s*(mg|mcg|ml)\b",  # personal + specific dose
    r"\bask\s+your\s+doctor\s+about\b",  # borderline prescribing per §2
    r"\bhere'?s\s+what\s+to\s+ask\b",   # implicit prescribing per §2
    r"\bi\s+take\s+\d+\s*(mg|mcg|ml|iu)\b",  # personal dosing statement
    r"\bdosing\s+(is|at|of)\s+\d+\s*(mg|mcg|ml)\b",  # dosing protocol language
    r"\btake\s+\d+\s*(mg|mcg|ml)\s+(daily|morning|night|before|after)\b",  # schedule + dose
    r"\b\d+\s*(mg|mcg|ml)\s+(daily|twice|once)\b",  # bare dose + frequency
    # Dosing math patterns (per §2 row 8: "Reconstitution math: 5mg vial + 2mL BAC water")
    r"\breconstitution\s+math\b",
    r"\d+\s*(mg|mcg|ml)\s*(?:vial|bottle)\s*[+\/]\s*\d+\s*(ml|mcg|cc|iu)",
    r"\d+\s*(?:mg|mcg|iu)\s*/\s*(?:ml|cc|iu)\s*=",  # concentration math
]

# S2 patterns allow intervening words between verb and metric (% / value)
S2_SUBSTANTIATION_PATTERNS = [
    r"\b(improved|reduced|dropped|increased|decreased)\b.{0,40}\d+\s*%",  # "X by Y%" with up to 40 chars between
    r"\bmy\s+(crp|hba1c|hrv|inflammation|biomarker|sleep|anxiety|flushing)\s+(dropped|improved|reduced|went\s+from)\b",
    r"\bworked\s+for\s+me\b",
    r"\bhelped\s+me\s+(with|reduce|improve)\b",
    r"\b(my|i)\s+(sleep|anxiety|flushing|inflammation|cramping|pain)\s+(improved|reduced|went\s+away|cleared)\b",  # personal outcome
    r"\b(peptide|treatment|stack)\s+(worked|fixed|cured|healed)\b",
    # Note: banned phrases (cure, heal, etc.) are in dop_compliance.py 8-item audit
]

S3_SOURCING_PATTERNS = [
    r"\bswiss\s*chems?\b",
    r"\bresearch\s*chem\b",
    r"\bgray[- ]?market\b",
    r"\bnot\s+for\s+human\s+consumption\b",
    r"\bwhere\s+i\s+get\s+mine\b",
    r"\bthe\s+only\s+place\s+i'?ve?\s+found\b",
    r"\bpeptide\s+sciences\b", r"\bonyx\b", r"\blimitless\s+life\b",
    r"\b(is|was|are|were)\s+only\s+available\s+at\b",  # spec §2: "This peptide is only available at"
    r"\bbuy\s+(here|now|from)\b",  # explicit purchase CTA
    r"\border\s+(from|via|through)\b.{0,20}\.(com|io|is|me)\b",  # ordering from vendor
]

# Hook families where substance mention without CTA is OK (substance is in passing, not the topic)
# Per spec §2: "FDA PCAC is reviewing peptide scheduling" (regulatory-reality) is CLEAR
# Per spec §2: "What LL-37 research actually shows" (literature-map) is CLEAR
S4_CTA_EXEMPT_HOOK_FAMILIES = {"regulatory-reality", "literature-map"}

# V4 routing check — only Substack (build-up) and licensed telehealth (post-PCAC) are valid
ALLOWED_ROUTING_HOSTS = [
    "doseofproof.substack.com",
    "marekhealth.com",
    "lifeforce.com",
]
BANNED_ROUTING_HOSTS = [
    "buffer.com", "vercel.com", "shopify.com", "amazon.com",
    "swisschems.is", "telegram.me", "t.me",
]
SUBSTANCE_TERMS_REGEX = re.compile(
    r"\b(peptide|bpc|tb-?500|tb-?4|ll-?37|ghk|cjc|ipamorelin|semaglutide|tirzepatide|"
    r"retatrutide|glp-?1|protocol|reconstitution|recon|bac\s*water|sermorelin)\b",
    re.IGNORECASE,
)

# V2: §2 sensitivity taxonomy examples (canonical — engine uses for self-classification sanity checks)
SENSITIVITY_TAXONOMY_EXAMPLES = [
    {"contains": "BPC-157 reduced my inflammation markers by 40%",                    "flags": "S2",       "reason": "outcome claim without inline citation"},
    {"contains": "I take 250mcg of X every morning — buy here",                     "flags": "S1+S3",    "reason": "prescribing + sourcing adjacency"},
    {"contains": "This peptide is only available at",                                "flags": "S3",       "reason": "sourcing, even without explicit endorsement"},
    {"contains": "Ask your doctor about GLP-1 protocols",                            "flags": "S1",       "reason": "borderline prescribing framing"},
    {"contains": "My CRP dropped after changing my protocol",                        "flags": "S2",       "reason": "outcome claim, no citation"},
    {"contains": "Here's the biomarker panel I track",                               "flags": "none",     "reason": "CLEAR — educational, routed"},
    {"contains": "FDA PCAC is reviewing peptide scheduling July 23-24",               "flags": "none",     "reason": "CLEAR — regulatory fact"},
    {"contains": "Reconstitution math: 5mg vial + 2mL BAC water = 2,500mcg/mL",     "flags": "S1",       "reason": "dosing math implies protocol"},
    {"contains": "What LL-37 research actually shows",                               "flags": "none",     "reason": "CLEAR — literature map with citation"},
    {"contains": "My sleep improved after fixing the vagus-cervical loop",           "flags": "S2",       "reason": "outcome claim, even personal"},
    {"contains": "Telehealth can now prescribe",                                     "flags": "S1",       "reason": "implicit prescribing even through provider"},
    {"contains": "5 biomarkers worth tracking for MCAS",                             "flags": "none",     "reason": "CLEAR — educational map, no claims"},
]

# V3: §3a block record schema (15 fields per triage-gate-spec §3a)
BLOCK_RECORD_FIELDS = [
    "POST_ID", "DATE_GENERATED", "PLATFORM", "HOOK_FAMILY",
    "SCHEDULED_SLOT", "CLASSIFICATION", "FLAGS_TRIGGERED", "FLAGS_DETAIL",
    "GENERATOR_NOTE", "MAVIS_NOTE", "STATUS", "RESOLVED_BY", "RESOLVED_AT",
    "RESOLUTION", "NOTES",
]

# Source asset schedule (date → source file + pillar override)
# Initial v0.1: first 14 days derived from existing Postiz CSV rows that
# weren't covered by the 22-row batch, mapped to source assets.
# Days after Jun 28: pull from prelaunch-calendar-FINAL.md plan.
SOURCE_SCHEDULE = {
    # Jun 26 (Fri) — FB post #2 (PCAC framework) → derive from x-thread-2-pcac-framework.md
    "2026-06-26": {
        "pillar_override": "P2",
        "primary_source": "x-thread-2-pcac-framework.md",
        "secondary_sources": ["linkedin-carousel-2-pcac-framework.md"],
    },
    # Jun 28 (Sun) — FB origin story → x-thread-3-7-months-broke-me.md
    "2026-06-28": {
        "pillar_override": "PCAC",
        "primary_source": "x-thread-3-7-months-broke-me.md",
        "secondary_sources": [],
    },
    # Jun 30 (Tue) — FB 5 biomarkers countdown → x-thread-1-5-biomarkers.md
    "2026-06-30": {
        "pillar_override": "P1",
        "primary_source": "x-thread-1-5-biomarkers.md",
        "secondary_sources": [],
    },
    # Jul 1 (Wed) — FB HRV 60sec + IG Reel (Reel blocked) → x-thread-1-5-biomarkers.md
    "2026-07-01": {
        "pillar_override": "P1",
        "primary_source": "x-thread-1-5-biomarkers.md",
        "secondary_sources": ["substack-post-2-read-your-own-bloodwork.md"],
    },
    # Jul 2 (Thu) — FB TyTron vs MRI → x-thread-1-5-biomarkers.md (Biomarker #2)
    "2026-07-02": {
        "pillar_override": "P1",
        "primary_source": "x-thread-1-5-biomarkers.md",
        "secondary_sources": [],
    },
    # Jul 3 (Fri) — FB supply chain + IG PCAC carousel → x-thread-4-supply-chain.md
    "2026-07-03": {
        "pillar_override": "P2",
        "primary_source": "x-thread-4-supply-chain.md",
        "secondary_sources": ["linkedin-carousel-3-category-1-transition.md"],
    },
    # Jul 5 (Sun) — FB recon math → x-thread-5-recon-math.md
    "2026-07-05": {
        "pillar_override": "P3",
        "primary_source": "x-thread-5-recon-math.md",
        "secondary_sources": ["linkedin-carousel-4-recon-math.md"],
    },
    # Jul 7 (Tue) — FB PCAC countdown → x-thread-2-pcac-framework.md
    "2026-07-07": {
        "pillar_override": "P2",
        "primary_source": "x-thread-2-pcac-framework.md",
        "secondary_sources": ["substack-post-terrain-mapping.md"],
    },
    # Jul 8 (Tue) — PCAC mechanics intro → x-thread-7-pcac-mechanics.md
    "2026-07-08": {
        "pillar_override": "P2",
        "primary_source": "x-thread-7-pcac-mechanics.md",
        "secondary_sources": ["linkedin-post-origin-story.md"],
    },
    # Jul 9 (Wed) — Upstream Terrain vs Downstream Whack-a-Mole carousel (NEW asset)
    "2026-07-09": {
        "pillar_override": "P1",
        "primary_source": "substack-post-terrain-mapping.md",
        "secondary_sources": ["x-thread-7-pcac-mechanics.md"],
    },
}


def read_source(filename: str) -> str:
    """Read a source asset file."""
    path = SOCIAL_DIR / filename
    if not path.exists():
        return ""
    return path.read_text()


# ============================================================================
# V1 + V2: Self-classification block per triage-gate-spec §1
# Decision rule: when in doubt, flag SENSITIVE (spec §1: "err toward SENSITIVE on ambiguity")
# ============================================================================

def classify_post(content: str, hook_family: str = "") -> dict:
    """
    V1+V2: Self-classification block per triage-gate-spec §1 + §2.

    Returns dict with:
        classification: "CLEAR" | "SENSITIVE"
        sensitive_reasons: list of triggered flags (S1/S2/S3/S4 — may overlap)
        sensitive_flags_detail: list of one-sentence explanations per flag

    Decision rule: when in doubt, flag SENSITIVE.
    """
    text = content.lower() if content else ""
    flags = []
    details = []

    # S1 — Prescribing
    for pattern in S1_PRESCRIBING_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            flags.append("S1")
            details.append(f"S1 (Prescribing): prescriptive language matches /{pattern}/")
            break

    # S2 — Substantiation (outcome claim without inline citation)
    for pattern in S2_SUBSTANTIATION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            # Has inline citation marker? [PMID:xxx] or pubmed/peer-reviewed/source:
            has_citation = bool(re.search(r"\[pmid[:\s]|pubmed|peer-reviewed|source:", text, re.IGNORECASE))
            if not has_citation:
                flags.append("S2")
                details.append(f"S2 (Substantiation): outcome claim /{pattern}/ without inline citation")
            break

    # S3 — Sourcing
    for pattern in S3_SOURCING_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            flags.append("S3")
            details.append(f"S3 (Sourcing): references /{pattern}/")
            break

    # S4 — Routing — URL extraction + host validation
    url_pattern = re.compile(r"https?://([a-z0-9.-]+)", re.IGNORECASE)
    urls = url_pattern.findall(content or "")
    has_allowed_routing = any(any(allowed in url for allowed in ALLOWED_ROUTING_HOSTS) for url in urls)
    has_banned_routing = any(any(banned in url for banned in BANNED_ROUTING_HOSTS) for url in urls)

    if has_banned_routing:
        flags.append("S4")
        details.append(f"S4 (Routing): contains banned host (buffer/vercel/shopify/swisschems/telegram)")
    elif urls and not has_allowed_routing:
        flags.append("S4")
        details.append(f"S4 (Routing): URL {urls[0]} not in allowed routing hosts (Substack/Marek/Lifeforce)")
    elif not urls and SUBSTANCE_TERMS_REGEX.search(text):
        # Substance/protocol mention with no CTA — spec §1 requires routing when substance touched.
        # EXCEPTION: regulatory-reality and literature-map hook families exempt (substance is in passing, not the topic).
        if hook_family not in S4_CTA_EXEMPT_HOOK_FAMILIES:
            flags.append("S4")
            details.append(f"S4 (Routing): substance/protocol mention with no CTA — spec §1 requires routing to licensed pathway")

    # Hook-family risk amplification: if content triggers HIGH-risk family (citizen-science,
    # reconstitution-math, community-proof) AND has any S2 outcome claim, default SENSITIVE
    # regardless of inline citation (spec §2: "S1/S2 risk highest here")
    if hook_family in {"citizen-science", "reconstitution-math", "community-proof"}:
        if "S2" not in flags:
            # Check for outcome claims without citation even if pattern didn't trigger above
            outcome_words = ["improved", "reduced", "dropped", "fixed", "cured", "healed"]
            if any(w in text for w in outcome_words) and not re.search(r"\[pmid|pubmed|peer-reviewed", text, re.IGNORECASE):
                flags.append("S2")
                details.append(f"S2 (Substantiation): outcome claim in HIGH-risk hook family '{hook_family}' without inline citation (spec §5 risk profile)")

    classification = "SENSITIVE" if flags else "CLEAR"
    return {
        "classification": classification,
        "sensitive_reasons": flags,
        "sensitive_flags_detail": details,
        "hook_family": hook_family,
    }


def write_blocked_record(post: dict, classification: dict, target_date: str, post_id: str, mavis_note: str = "") -> Path:
    """
    V3: Write a §3a block record for a SENSITIVE post. Returns path to file.

    Per triage-gate-spec §3a, the canonical block record has 15 fields:
        POST_ID, DATE_GENERATED, PLATFORM, HOOK_FAMILY, SCHEDULED_SLOT,
        CLASSIFICATION, FLAGS_TRIGGERED, FLAGS_DETAIL, GENERATOR_NOTE,
        MAVIS_NOTE, STATUS, RESOLVED_BY, RESOLVED_AT, RESOLUTION, NOTES

    STATUS=BLOCKED on creation. RESOLVED_BY/RESOLVED_AT/RESOLUTION are blank
    until Founder or Co-CEO unblocks.
    """
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    blocked_path = QUEUE_DIR / f"blocked-records-{target_date}.mdl"

    date_generated = datetime.now().isoformat()
    scheduled_slot = f"{post.get('date', target_date)}T{post.get('time', '??:??')}"
    flags_detail_str = " | ".join(classification.get("sensitive_flags_detail", []))
    mavis_recommendation = mavis_note or ("KILL" if "S3" in classification.get("sensitive_reasons", []) or "S1" in classification.get("sensitive_reasons", []) else "HOLD")

    # Build the block record as a structured markdown block
    record = f"""
───────────────────────────────────────────
BLOCK RECORD
───────────────────────────────────────────
POST_ID:         {post_id}
DATE_GENERATED:  {date_generated}
PLATFORM:        {post.get('channel', 'unknown')}
HOOK_FAMILY:     {classification.get('hook_family', 'unknown')}
SCHEDULED_SLOT:  {scheduled_slot}
CLASSIFICATION:  {classification.get('classification', 'SENSITIVE')}
FLAGS_TRIGGERED: {','.join(classification.get('sensitive_reasons', [])) or 'none'}
FLAGS_DETAIL:    {flags_detail_str or 'none'}
GENERATOR_NOTE:  {' | '.join(classification.get('sensitive_flags_detail', [])) or 'self-flagged SENSITIVE'}
MAVIS_NOTE:      Recommend: {mavis_recommendation}. (Mavis is first-pass screen, not compliance authority — Founder or Co-CEO unblock.)
STATUS:          BLOCKED
RESOLVED_BY:     [blank until unblocked]
RESOLVED_AT:     [blank until unblocked]
RESOLUTION:      [blank — will be: APPROVED | KILLED | REVISED]
NOTES:           Generated by dop_engine.py v0.3 per triage-gate-spec §3a. Auto-blocked by generator self-classification.
───────────────────────────────────────────
"""

    with open(blocked_path, "a") as f:
        f.write(record)

    return blocked_path


def emit_classification_header(post: dict, classification: dict, post_id: str) -> str:
    """
    V1: Emit the §1 self-classification block header for a post.
    Format (verbatim from spec §1):
        ---
        POST_ID: [YYYYMMDD-NNN]
        PLATFORM: [facebook | instagram | pinterest]
        HOOK_FAMILY: [see §5]
        CLASSIFICATION: [CLEAR | SENSITIVE]
        SENSITIVE_REASONS: [comma-separated list, or "none"]
        SENSITIVE_FLAGS_DETAIL: [one sentence per flag]
        ---

        [post body]
    """
    reasons = ",".join(classification.get("sensitive_reasons", [])) or "none"
    flags_detail = " | ".join(classification.get("sensitive_flags_detail", [])) or "none"

    header = (
        f"---\n"
        f"POST_ID: {post_id}\n"
        f"PLATFORM: {post.get('channel', 'unknown')}\n"
        f"HOOK_FAMILY: {classification.get('hook_family', 'unknown')}\n"
        f"CLASSIFICATION: {classification.get('classification', 'CLEAR')}\n"
        f"SENSITIVE_REASONS: {reasons}\n"
        f"SENSITIVE_FLAGS_DETAIL: {flags_detail}\n"
        f"---\n\n"
    )
    return header


def extract_hooks(content: str, max_hooks: int = 5) -> list[str]:
    """Extract standalone hooks (prose lines that look like opening hooks).
    Skip markdown metadata, headers, and short labels."""
    hooks = []
    skip_patterns = [
        r"^\*\*",        # bold metadata
        r"^---",         # horizontal rule
        r"^\[",          # bracket metadata
        r"^TWEET\s*\d",  # tweet number markers
        r"^\d+\.\s*$",   # lone numbers
        r"^https?://",   # raw URLs
        r"^#",           # markdown headers
        r"^>",           # blockquotes
        r"^\s*$",        # blank
    ]
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        # Skip metadata-ish lines
        if any(re.search(pat, line) for pat in skip_patterns):
            continue
        # Hooks are prose: 60-280 chars, end with sentence punctuation
        if 60 <= len(line) <= 280 and line[-1] in ".!?":
            hooks.append(line)
            if len(hooks) >= max_hooks:
                break
    return hooks


def extract_carousel_slides(content: str, max_slides: int = 9) -> list[str]:
    """Extract or synthesize 9 carousel slide bodies from source content."""
    # Simple heuristic: take the first 9 distinct paragraph blocks
    blocks = []
    for para in content.split("\n\n"):
        para = para.strip()
        if para and not para.startswith("#") and len(para) > 10:
            blocks.append(para)
    # Pad to 9 with synthesized hooks if needed
    while len(blocks) < max_slides:
        blocks.append(f"→ https://doseofproof.substack.com/")
    return blocks[:max_slides]


def fb_post_for_hook(hook: str, pillar: str, date: str, time: str) -> dict:
    """Build a Facebook text post from a hook."""
    substack_url = "https://doseofproof.substack.com/?utm_source=facebook&utm_medium=social&utm_campaign=pre_launch&utm_content=engine_v0_2"
    # Per-pillar hashtag sets
    pillar_hashtags = {
        "P1": "#ChronicIllness #Biomarkers #ProofOverHype",
        "P2": "#PCACFramework #MacroLongevity #RegulatoryWatch",
        "P3": "#ReconMath #Peptides #DataUtility",
        "PCAC": "#PCACFramework #ProofOverHype #FDA",
    }
    hashtags = pillar_hashtags.get(pillar, "#DoseOfProof")
    content = f"{hook}\n\n→ {substack_url}\n\n{hashtags}"
    return {
        "channel": "facebook",
        "content": content,
        "image_paths": [],
    }


def fb_multi_image_post(carousel_name: str, source_filename: str, pillar: str, date: str, time: str) -> dict:
    """Build a multi-image FB post reusing the IG carousel slides (FB supports up to 10)."""
    carousel_dir = VISUAL_DIR / carousel_name / "slides"
    if not carousel_dir.exists():
        return None
    slide_paths = sorted(str(p) for p in carousel_dir.glob("slide-*.png"))[:10]  # FB max 10
    if len(slide_paths) < 3:
        return None
    substack_url = "https://doseofproof.substack.com/?utm_source=facebook&utm_medium=social&utm_campaign=pre_launch&utm_content=multi_image_v0_2"
    content = f"[Multi-image post — carousel reused from {source_filename}]\n\nThe PCAC framework: Proof-Centered Approach to Craniocervical + Autoimmune Chaos.\n\nMap the terrain. Treat the upstream. Show me the data.\n\n→ {substack_url}\n\n#PCACFramework #Biomarkers #ProofOverHype"
    return {
        "channel": "facebook",
        "content": content,
        "image_paths": slide_paths,
    }


def pinterest_pin_for_source(source_content: str, source_filename: str, pillar: str, date: str, time: str, slot_idx: int = 1) -> dict:
    """Build a Pinterest pin entry. The actual image is rendered by Dre or by
    a separate visual pass; we write a brief for the UI push.
    slot_idx: 1=cover, 2=secondary, 3=tertiary slide"""
    # Map source to pin image (existing) for slot 1
    pin_map = {
        "x-thread-1-5-biomarkers.md": "pin-1-5biomarkers",
        "x-thread-2-pcac-framework.md": "pin-2-hrv-tracking",
    }
    # For slot 2/3, use carousel cover or other slides
    pin_name = pin_map.get(source_filename)
    if slot_idx == 1 and pin_name:
        pin_path = VISUAL_DIR / pin_name / f"{pin_name}.png"
    else:
        # Try to find a carousel cover or alt slide
        carousel_map_local = {
            "x-thread-1-5-biomarkers.md": "carousel-1-5biomarkers",
            "x-thread-2-pcac-framework.md": "carousel-2-pcac-framework",
            "x-thread-4-supply-chain.md": "carousel-3-pcac-meeting",
            "substack-post-terrain-mapping.md": "carousel-4-upstream-downstream",
        }
        carousel_name = carousel_map_local.get(source_filename)
        if carousel_name:
            carousel_dir = VISUAL_DIR / carousel_name / "slides"
            if carousel_dir.exists():
                slides = sorted(carousel_dir.glob("slide-*.png"))
                # Slot 1: cover, Slot 2: data slide (slide 8 in 9-slide, or similar), Slot 3: CTA (slide 9)
                if slot_idx == 1 and len(slides) >= 1:
                    pin_path = slides[0]  # cover
                elif slot_idx == 2 and len(slides) >= 8:
                    pin_path = slides[7]  # data slide
                elif slot_idx == 3 and len(slides) >= 9:
                    pin_path = slides[8]  # CTA
                else:
                    pin_path = slides[min(slot_idx - 1, len(slides) - 1)]
            else:
                return None
        else:
            return None

    if not pin_path.exists():
        return None
    substack_url = f"https://doseofproof.substack.com/?utm_source=pinterest&utm_medium=social&utm_campaign=pre_launch&utm_content=pin_v0_2_slot{slot_idx}"
    content = f"Pin slot {slot_idx}/3 from {source_filename}\n\n→ {substack_url}"
    return {
        "channel": "pinterest",
        "content": content,
        "image_paths": [str(pin_path)],
        "pin_status": "DRE_MANUAL_PUSH",
    }


def ig_carousel_for_source(source_content: str, source_filename: str, date: str) -> dict:
    """Build an Instagram carousel post. Reuses existing slides if a matching
    rendered carousel exists, else flags for fresh generation."""
    # Map source filenames to existing rendered carousels
    carousel_map = {
        "x-thread-1-5-biomarkers.md": "carousel-1-5biomarkers",
        "x-thread-2-pcac-framework.md": "carousel-2-pcac-framework",
        "x-thread-4-supply-chain.md": "carousel-3-pcac-meeting",
        "substack-post-terrain-mapping.md": "carousel-4-upstream-downstream",
    }
    carousel_name = carousel_map.get(source_filename)

    if carousel_name:
        # Use existing rendered slides
        carousel_dir = VISUAL_DIR / carousel_name / "slides"
        if not carousel_dir.exists():
            carousel_dir = VISUAL_DIR / carousel_name  # fallback for carousel-1
        if carousel_dir.exists():
            slide_paths = sorted(str(p) for p in carousel_dir.glob("slide-*.png"))
            if len(slide_paths) >= 9:
                substack_url = "https://doseofproof.substack.com/?utm_source=instagram&utm_medium=social&utm_campaign=pre_launch&utm_content=carousel_reuse"
                # Carousel caption (per PCAC framework voice)
                content = f"[Carousel reused from {source_filename}]\n\nThe PCAC framework: Proof-Centered Approach to Craniocervical + Autoimmune Chaos.\n\nMap the terrain. Treat the upstream. Show me the data.\n\n→ {substack_url}\n\n#PCACFramework #Biomarkers #ProofOverHype"
                # IG carousel max is 10 media attachments — cap at 10
                return {
                    "channel": "instagram",
                    "content": content,
                    "image_paths": slide_paths[:10],  # IG cap is 10 (not 12)
                }
    # Else: synthetic placeholder — real generation happens in the visual worker pass
    return {
        "channel": "instagram",
        "content": f"[Carousel — needs fresh generation for {source_filename}]\n\nSee queue/pins-{date}.mdl for the source content brief.\n\n→ https://doseofproof.substack.com/",
        "image_paths": [],
    }


def generate_for_date(target_date: str) -> list[dict]:
    """Generate the daily post set for a target date. v0.2 — higher volume."""
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    weekday = dt.weekday()
    pillar = PILLAR_ROTATION[weekday]

    # Look up source schedule; fall back to deriving from pillar
    schedule = SOURCE_SCHEDULE.get(target_date)
    if not schedule:
        # Fallback: use next sequential x-thread (after 1..10)
        day_idx = (dt - datetime(2026, 6, 26)).days
        thread_num = (day_idx % 10) + 1
        schedule = {
            "pillar_override": pillar,
            "primary_source": f"x-thread-{thread_num}-*.md",
            "secondary_sources": [],
        }
        # Try to resolve glob
        candidates = sorted(SOCIAL_DIR.glob(f"x-thread-{thread_num}-*.md"))
        if candidates:
            schedule["primary_source"] = candidates[0].name

    pillar = schedule.get("pillar_override", pillar)
    primary = schedule["primary_source"]
    secondary = schedule.get("secondary_sources", [])

    primary_content = read_source(primary)
    if not primary_content:
        print(f"WARN: source {primary} not found, generating placeholder posts")

    # Extract hooks from primary source
    hooks = extract_hooks(primary_content, max_hooks=8)  # v0.2: extract more hooks
    if not hooks:
        hooks = [
            f"The framework I built because Symptom Whack-a-Mole wasn't working.",
            f"Show me the data. The numbers move. They don't arrive at a finish line.",
        ]

    posts = []

    # V8: resolve hook_family once per generation from pillar (output tag = hook_family, not pillar)
    hook_family = PILLAR_TO_HOOK_FAMILY.get(pillar, "regulatory-reality")

    # v0.2: 6 Facebook text posts spread across the day (was 4)
    fb_times = ["08:00", "11:00", "13:30", "16:00", "18:30", "21:00"]
    for i, hook in enumerate(hooks[:6]):
        time = fb_times[i] if i < len(fb_times) else fb_times[-1]
        posts.append(fb_post_for_hook(hook, pillar, target_date, time))
        posts[-1]["time"] = time
        posts[-1]["date"] = target_date
        posts[-1]["pillar"] = pillar
        posts[-1]["hook_family"] = hook_family

    # v0.2: 1 multi-image FB post reusing the IG carousel source
    # Only if a matching carousel exists for the primary source
    carousel_map_local = {
        "x-thread-1-5-biomarkers.md": "carousel-1-5biomarkers",
        "x-thread-2-pcac-framework.md": "carousel-2-pcac-framework",
        "x-thread-4-supply-chain.md": "carousel-3-pcac-meeting",
        "substack-post-terrain-mapping.md": "carousel-4-upstream-downstream",
    }
    carousel_for_fb = carousel_map_local.get(primary)
    if carousel_for_fb:
        multi_img_post = fb_multi_image_post(carousel_for_fb, primary, pillar, target_date, "12:00")
        if multi_img_post:
            multi_img_post["date"] = target_date
            multi_img_post["time"] = "12:00"
            multi_img_post["pillar"] = pillar
            multi_img_post["hook_family"] = hook_family
            multi_img_post["post_label"] = "fb_multi_image"
            posts.append(multi_img_post)

    # 1 Instagram carousel (existing logic)
    ig_post = ig_carousel_for_source(primary_content, primary, target_date)
    ig_post["date"] = target_date
    ig_post["time"] = "15:00"
    ig_post["pillar"] = pillar
    ig_post["hook_family"] = hook_family
    posts.append(ig_post)

    # v0.2: 3 Pinterest pins (cover + secondary data slide + CTA) — Dre batch-pushes
    pin_times = ["09:30", "14:00", "19:00"]
    for slot in [1, 2, 3]:
        pin_post = pinterest_pin_for_source(primary_content, primary, pillar, target_date, pin_times[slot - 1], slot_idx=slot)
        if pin_post:
            pin_post["date"] = target_date
            pin_post["time"] = pin_times[slot - 1]
            pin_post["pillar"] = pillar
            pin_post["hook_family"] = hook_family
            pin_post["pin_slot"] = slot
            posts.append(pin_post)

    return posts


def write_queue(target_date: str, posts: list[dict]) -> tuple[Path, Path]:
    """
    Write posts to queue files with §1 self-classification header per triage-gate-spec.

    Per-post format (§1):
        ---
        POST_ID: YYYYMMDD-NNN
        PLATFORM: facebook | instagram | pinterest
        HOOK_FAMILY: <one of 8 from §5>
        CLASSIFICATION: CLEAR | SENSITIVE
        SENSITIVE_REASONS: S1,S2,S3,S4 or "none"
        SENSITIVE_FLAGS_DETAIL: <one sentence per flag>
        8_ITEM_COMPLIANCE: PASS | FAIL (N issues)
        ---

        [post body]

    SENSITIVE posts also written to queue/blocked-records-{date}.mdl with §3a schema.

    Returns (drafts_path, pins_path, blocked_path_or_None).
    """
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    drafts_path = QUEUE_DIR / f"drafts-{target_date}.mdl"
    pins_path = QUEUE_DIR / f"pins-{target_date}.mdl"
    blocked_path = QUEUE_DIR / f"blocked-records-{target_date}.mdl"

    # Initialize blocked-records file with header
    with open(blocked_path, "w") as bf:
        bf.write(f"# Dose of Proof — Block records for {target_date}\n")
        bf.write(f"# Generated {datetime.now().isoformat()} by dop_engine.py v0.3 (gate-implementing)\n")
        bf.write(f"# Schema: triage-gate-spec §3a (15 fields per block record)\n")
        bf.write(f"# All entries are STATUS=BLOCKED until Founder or Co-CEO unblocks.\n")
        bf.write(f"# See also: queue/drafts-{target_date}.mdl + queue/pins-{target_date}.mdl\n")
        bf.write(f"---\n\n")

    with open(drafts_path, "w") as f:
        f.write(f"# Dose of Proof — Daily drafts for {target_date}\n")
        f.write(f"# Generated {datetime.now().isoformat()} by dop_engine.py v0.3 (gate-implementing)\n")
        f.write(f"# Source corpus: 30 assets (X threads, LinkedIn carousels, Substack posts)\n")
        f.write(f"# Compliance: dop_compliance.py 8-item gate + triage-gate-spec §1 self-classification block\n")
        f.write(f"#\n")
        f.write(f"# Per-post format (triage-gate-spec §1):\n")
        f.write(f"# ---\n")
        f.write(f"# POST_ID | PLATFORM | HOOK_FAMILY | CLASSIFICATION | SENSITIVE_REASONS | 8_ITEM_COMPLIANCE\n")
        f.write(f"# [post body follows]\n")
        f.write(f"---\n\n")

    with open(pins_path, "w") as pf:
        pf.write(f"# Dose of Proof — Pinterest pins for {target_date}\n")
        pf.write(f"# Generated {datetime.now().isoformat()} by dop_engine.py v0.3 (gate-implementing)\n")
        pf.write(f"# POSTIZ BOARD ID REQUIRED for manual push via Postiz UI\n")
        pf.write(f"# Per-pin format: triage-gate-spec §1 self-classification block\n")
        pf.write(f"---\n\n")

    drafts_count = 0
    pins_count = 0
    blocked_count = 0
    post_idx = 1
    for post in posts:
        channel = post["channel"]
        content = post["content"]
        hook_family = post.get("hook_family", "regulatory-reality")

        # V1: Self-classification (§1)
        classification = classify_post(content, hook_family=hook_family)

        # Legacy 8-item compliance audit
        ok, fails = compliance.audit(content)
        compliance_str = "PASS" if ok else f"FAIL ({len(fails)} issues)"

        # Post ID
        channel_prefix = {"facebook": "fb", "instagram": "ig", "pinterest": "pin"}.get(channel, "x")
        post_id = f"dop-{channel_prefix}-{target_date.replace('-','')}-{post_idx:03d}"

        # Build image paths string
        img_str = " | ".join(post.get("image_paths", []))

        # V1: Emit §1 classification header
        header = emit_classification_header(post, classification, post_id)
        # Add 8-item compliance line to header for Mavis first-pass screen
        header += f"8_ITEM_COMPLIANCE: {compliance_str}\n"
        header += "---\n\n"

        # V3: If SENSITIVE, write block record
        if classification["classification"] == "SENSITIVE":
            write_blocked_record(post, classification, target_date, post_id)
            blocked_count += 1

        if channel == "pinterest":
            # Pinterest goes to pin queue (Dre UI push)
            with open(pins_path, "a") as pf:
                pf.write(header)
                pf.write(f"## Pin {post_idx} — {post_id}\n")
                pf.write(f"- Pillar: {post.get('pillar', '?')} (calendar logic only — output tag is HOOK_FAMILY)\n")
                pf.write(f"- Date/Time: {post['date']} {post['time']}\n")
                pf.write(f"- Status: DRE_MANUAL_PUSH\n")
                pf.write(f"- 8-Item Compliance: {compliance_str}\n")
                if fails:
                    pf.write(f"- Issues:\n")
                    for fail in fails:
                        pf.write(f"  - {fail}\n")
                if classification["classification"] == "SENSITIVE":
                    pf.write(f"- **⛔ BLOCKED — generator self-flagged SENSITIVE. See queue/blocked-records-{target_date}.mdl.**\n")
                pf.write(f"- Image: {img_str or '(NEEDS RENDER)'}\n")
                pf.write(f"- Content:\n```\n{content}\n```\n\n")
            pins_count += 1
        else:
            # Auto-push channels (FB + IG) go to drafts
            with open(drafts_path, "a") as f:
                f.write(header)
                f.write(f"POST_ID: {post_id}\n")
                f.write(f"PILLAR: {post.get('pillar', '?')} (calendar logic only)\n")
                f.write(f"CHANNEL: {channel}\n")
                f.write(f"DATE: {post['date']}\n")
                f.write(f"TIME: {post['time']}\n")
                f.write(f"8_ITEM_COMPLIANCE_ISSUES: {fails if fails else 'none'}\n")
                if classification["classification"] == "SENSITIVE":
                    f.write(f"STATUS: BLOCKED — generator self-flagged SENSITIVE. See queue/blocked-records-{target_date}.mdl\n")
                else:
                    f.write(f"STATUS: CLEAR — eligible for push (subject to Mavis first-pass screen)\n")
                f.write(f"CONTENT:\n")
                f.write(f"```\n{content}\n```\n")
                f.write(f"IMAGE_PATHS: {img_str or 'none'}\n")
                f.write(f"---\n\n")
            drafts_count += 1
        post_idx += 1

    print(f"✅ Wrote {drafts_count} auto-push posts → {drafts_path}")
    print(f"📌 Wrote {pins_count} Pinterest pins → {pins_path}")
    if blocked_count > 0:
        print(f"⛔ Wrote {blocked_count} BLOCKED records → {blocked_path}  (Founder or Co-CEO must unblock before push)")
    else:
        # If no posts were blocked, remove the empty blocked-records file
        blocked_path.unlink(missing_ok=True)
        blocked_path = None
    return drafts_path, pins_path, blocked_path


def main():
    # §3d HALT HARD INTERLOCK — Co-CEO rule 2026-06-25
    # First action in main(): refuse to run if engine is HALTED.
    halt_rc = check_halt_precondition()
    if halt_rc != 0:
        sys.exit(halt_rc)

    parser = argparse.ArgumentParser(description="Dose of Proof daily content engine")
    parser.add_argument("--date", default=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                        help="Target date (default: tomorrow)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to disk")
    args = parser.parse_args()

    print("=" * 70)
    print(f"Dose of Proof — Daily Content Engine v0.3 (gate-implementing)")
    print(f"Target date: {args.date}")
    print("=" * 70)

    posts = generate_for_date(args.date)
    print(f"\nGenerated {len(posts)} posts ({sum(1 for p in posts if p['channel']!='pinterest')} auto-push + {sum(1 for p in posts if p['channel']=='pinterest')} Pinterest)")

    # V1+V2 self-classification summary (per triage-gate-spec §1)
    print(f"\n--- Self-Classification (triage-gate-spec §1) ---")
    clear_count = 0
    sensitive_count = 0
    for post in posts:
        hook_family = post.get("hook_family", "regulatory-reality")
        classification = classify_post(post["content"], hook_family=hook_family)
        if classification["classification"] == "CLEAR":
            clear_count += 1
        else:
            sensitive_count += 1
            print(f"  ⛔ {post['channel']} ({hook_family}) — {','.join(classification['sensitive_reasons'])}")
            for detail in classification["sensitive_flags_detail"]:
                print(f"     {detail}")
    print(f"  ✅ CLEAR: {clear_count} | ⛔ SENSITIVE: {sensitive_count}")

    # Legacy 8-item compliance audit summary
    print(f"\n--- 8-Item Compliance Audit (dop_compliance.py) ---")
    fail_count = 0
    for post in posts:
        ok, fails = compliance.audit(post["content"])
        if not ok:
            fail_count += 1
            print(f"  ⚠️  {post['channel']} — {len(fails)} compliance issues: {fails[:2]}")
    if fail_count == 0:
        print(f"  ✅ All posts pass 8-item compliance gate")
    else:
        print(f"  ⚠️  {fail_count} posts flagged for human review")

    if not args.dry_run:
        drafts_path, pins_path, blocked_path = write_queue(args.date, posts)
        print(f"\n📁 Queue files:")
        print(f"   - {drafts_path}")
        print(f"   - {pins_path}")
        if blocked_path:
            print(f"   - {blocked_path}  ← Founder or Co-CEO must unblock before push")

            # V4 §3b: Bridge to Obsidian HITL daily note (Obsidian leg)
            try:
                from dop_hitl_logger import log_to_obsidian
                hitl_result = log_to_obsidian(args.date)
                print(f"\n📓 HITL Obsidian log:")
                print(f"   - {hitl_result['obsidian_path']}  ({hitl_result['records_logged']} records)")
                if hitl_result['status'] != "logged":
                    print(f"   - Status: {hitl_result['status']}")
            except Exception as e:
                print(f"\n⚠️  HITL Obsidian logger failed: {e}")
                print(f"   - Block records still in queue/blocked-records-{args.date}.mdl (source of truth)")
    else:
        print(f"\n[dry-run] No files written")


if __name__ == "__main__":
    main()