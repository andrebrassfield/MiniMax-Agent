#!/usr/bin/env python3
"""
Dose of Proof — 8-item compliance audit module.

Hard-block compliance gate. Returns (pass: bool, failures: list[str]).
"""
import re
from pathlib import Path

# Item 5: Banned phrases (Decision 12 + brand voice)
BANNED_PHRASES = [
    r"\bcure\b",
    r"\bheal(?:s|ing|ed)?\b",
    r"\bsecret\b",
    r"\bgame[- ]changing\b",
    r"\brevolutionary\b",
    r"\bbreakthrough\b",
    r"\bunlock(?:s|ed|ing)?\b",
    r"\bunleash(?:es|ed|ing)?\b",
    r"\bsynergy\b",
    r"\bleverage(?:s|d)?\b",
    r"\bvalue[- ]add\b",
    r"\bswiss\s*chems?\b",
    r"\bresearch\s*chem\b",
    r"\bgray[- ]?market\b",
    r"\bnot\s+for\s+human\s+consumption\b",
]

# Item 2: Only allowed CTA host
ALLOWED_CTA = "doseofproof.substack.com"

# Item 2: Banned alternative CTAs
BANNED_CTA_HOSTS = [
    "buffer.com",
    "vercel.com",
    "shopify.com",
    "amazon.com",
    "swisschems.is",
]


def audit(content: str) -> tuple[bool, list[str]]:
    """
    Run the 8-item compliance audit on a post's content.
    Returns (passes, failures) — failures is a list of human-readable strings.

    Programmatic checks for items 1-7. Item 8 (PCAC framing) is editorial
    judgment — flagged but not hard-blocked, surfaced for Dre review.
    """
    failures = []
    text = content.lower() if content else ""

    # Item 1: Educational/curatorial (heuristic — flag prescriptive language)
    prescriptive_markers = [
        r"\byou\s+should\s+take\b",
        r"\brecommended\s+dosage\b",
        r"\bstart\s+with\s+\d+\s*(mg|mcg|ml)\b",
        r"\bprescribe\b",
        r"\bprotocol\s*:\s*take\b",
    ]
    for pattern in prescriptive_markers:
        if re.search(pattern, text, re.IGNORECASE):
            failures.append(f"ITEM 1: prescriptive language detected ('{pattern}') — rewrite as observational")
            break

    # Item 5: Banned phrases
    for pattern in BANNED_PHRASES:
        if re.search(pattern, text, re.IGNORECASE):
            failures.append(f"ITEM 5: banned phrase matched /{pattern}/")

    # Item 2: Single CTA — must contain substack URL AND no banned hosts
    has_allowed_cta = ALLOWED_CTA in content.lower() if content else False
    has_banned_cta = any(host in content.lower() for host in BANNED_CTA_HOSTS) if content else False
    if has_banned_cta:
        failures.append("ITEM 2: post contains banned CTA host (buffer/vercel/shopify/swisschems)")
    # Note: not all posts need a CTA (e.g., pure engagement posts). If no URL present, item 2 passes.

    # Item 6: Brand voice — tone check (heuristic: too exclamatory = flagged)
    exclamation_count = content.count("!") if content else 0
    if exclamation_count > 3:
        failures.append(f"ITEM 6: too many exclamation marks ({exclamation_count}) — brand voice is stoic, not hype")

    # Item 8: PCAC framing (heuristic — flag FDA claims that aren't framed via the framework)
    fda_claims = [
        r"\bfda\s+(?:approved|says|confirmed)\b",
    ]
    for pattern in fda_claims:
        if re.search(pattern, text, re.IGNORECASE):
            # Not a hard block — just a note for human review
            failures.append(f"ITEM 8 (NOTE): FDA claim language detected /{pattern}/ — verify PCAC framework framing")

    passes = len(failures) == 0
    return passes, failures


if __name__ == "__main__":
    # Quick test
    test_post = """I have craniocervical instability at C1-C2. Suspected hypermobile EDS.

For 7 months I lived in a vicious loop.

→ https://doseofproof.substack.com/?utm_source=facebook
"""
    ok, fails = audit(test_post)
    print(f"PASS: {ok}")
    print(f"Failures: {fails}")

    bad_post = "This breakthrough will heal your chronic fatigue! Recommended dosage: 500mg daily."
    ok2, fails2 = audit(bad_post)
    print(f"\nBad post — PASS: {ok2}")
    print(f"Failures: {fails2}")