#!/usr/bin/env python3
"""
PCAC Series — Buffer CSV Generator
=================================

Reads the 11 locked thread markdown files from:
  - 03 Projects/Dose of Proof/assets/social/4-traps/
  - 03 Projects/Dose of Proof/assets/social/pcac-peptides/

Produces a Buffer-bulk-upload CSV at:
  03 Projects/Dose of Proof/assets/scheduling/buffer-bulk-upload-pcac-series-june27-july7.csv

CSV columns (matching buffer-bulk-upload-week-1-2.csv):
  date, time, channel, type, content, media, link, tags, folder, asset_source, notes

Thread structure:
  Each .md file is parsed into individual tweets by splitting on `**Tweet N ...**` headers
  (and `---` separators). Tweets are joined with `---` (Buffer thread format).

Mapping rules:
  - 4-traps/trap-1-kitting.md          → 2026-06-27 09:00 ET
  - 4-traps/trap-2-seo.md              → 2026-06-28 09:00 ET
  - 4-traps/trap-3-testimonials.md     → 2026-06-29 09:00 ET
  - 4-traps/trap-4-community.md        → 2026-06-30 09:00 ET
  - pcac-peptides/2026-07-01-bpc-157.md       → 2026-07-01 09:00 ET
  - pcac-peptides/2026-07-02-kpv.md           → 2026-07-02 09:00 ET
  - pcac-peptides/2026-07-03-tb-500.md        → 2026-07-03 09:00 ET
  - pcac-peptides/2026-07-04-mots-c.md        → 2026-07-04 09:00 ET
  - pcac-peptides/2026-07-05-semax.md         → 2026-07-05 09:00 ET
  - pcac-peptides/2026-07-06-dsip-epitalon.md → 2026-07-06 09:00 ET
  - pcac-peptides/2026-07-07-recap-bridge-biomarkers.md → 2026-07-07 09:00 ET

Compliance gates:
  - Single Substack CTA only (no Buffer/Vercel/Shopify URL in content)
  - Thread format (type=thread, joined with ---)
  - Tags + folder + asset_source all set for traceability
"""

import csv
import re
from pathlib import Path

# Repo root
ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")

# Asset directories
SOCIAL_DIR = ROOT / "03 Projects" / "Dose of Proof" / "assets" / "social"
TRAPS_DIR = SOCIAL_DIR / "4-traps"
PEPTIDES_DIR = SOCIAL_DIR / "pcac-peptides"

# Output CSV path
OUT_CSV = ROOT / "03 Projects" / "Dose of Proof" / "assets" / "scheduling" / "buffer-bulk-upload-pcac-series-june27-july7.csv"

# Schedule — ordered list of (date, time, asset_path, type, compound_or_trap, tags, notes)
SCHEDULE = [
    # date, time, asset, type, topic, tags, notes
    ("2026-06-27", "09:00", TRAPS_DIR / "trap-1-kitting.md",         "thread", "Trap 1: Kitting",
     "pre_launch,pcac,regulatory,trap,objective_intent,21cfr201_128",
     "PCAC Traps series — Trap 1 (4 of 4). First trap in regulatory mechanics education."),
    ("2026-06-28", "09:00", TRAPS_DIR / "trap-2-seo.md",             "thread", "Trap 2: SEO",
     "pre_launch,pcac,regulatory,trap,objective_intent,seo_metadata",
     "PCAC Traps series — Trap 2 (4 of 4). Backend signals regulators crawl."),
    ("2026-06-29", "09:00", TRAPS_DIR / "trap-3-testimonials.md",    "thread", "Trap 3: Testimonials",
     "pre_launch,pcac,regulatory,trap,section_505a,testimonial_adoption",
     "PCAC Traps series — Trap 3 (4 of 4). Section 505(a) testimonial adoption."),
    ("2026-06-30", "09:00", TRAPS_DIR / "trap-4-community.md",       "thread", "Trap 4: Community",
     "pre_launch,pcac,regulatory,trap,ecosystem_integration",
     "PCAC Traps series — Trap 4 (4 of 4). Single ecosystem problem. Series close."),
    ("2026-07-01", "09:00", PEPTIDES_DIR / "2026-07-01-bpc-157.md",   "thread", "BPC-157",
     "pre_launch,pcac,peptide,bpc157,ulcerative_colitis,503a_bulks_list",
     "PCAC peptide series — BPC-157 (1 of 7). July 23 docket — ulcerative colitis indication."),
    ("2026-07-02", "09:00", PEPTIDES_DIR / "2026-07-02-kpv.md",       "thread", "KPV",
     "pre_launch,pcac,peptide,kpv,wound_healing,503a_bulks_list",
     "PCAC peptide series — KPV (2 of 7). July 23 docket — wound healing + inflammatory conditions."),
    ("2026-07-03", "09:00", PEPTIDES_DIR / "2026-07-03-tb-500.md",    "thread", "TB-500",
     "pre_launch,pcac,peptide,tb500,thymosin_beta4,wound_healing,503a_bulks_list",
     "PCAC peptide series — TB-500 (3 of 7). July 23 docket — wound healing."),
    ("2026-07-04", "09:00", PEPTIDES_DIR / "2026-07-04-mots-c.md",    "thread", "MOTs-C",
     "pre_launch,pcac,peptide,motsc,obesity,osteoporosis,503a_bulks_list",
     "PCAC peptide series — MOTs-C (4 of 7). July 4 — Saturday. July 23 docket — obesity + osteoporosis dual indication. 11-tweet thread."),
    ("2026-07-05", "09:00", PEPTIDES_DIR / "2026-07-05-semax.md",     "thread", "Semax",
     "pre_launch,pcac,peptide,semax,cerebral_ischemia,503a_bulks_list",
     "PCAC peptide series — Semax (5 of 7). July 24 docket — cerebral ischemia indication."),
    ("2026-07-06", "09:00", PEPTIDES_DIR / "2026-07-06-dsip-epitalon.md", "thread", "DSIP + Epitalon",
     "pre_launch,pcac,peptide,dsip,emideltide,epitalon,sleep,circadian,503a_bulks_list",
     "PCAC peptide series — DSIP + Epitalon combined (6 of 7). July 24 docket — sleep + longevity-adjacent."),
    ("2026-07-07", "09:00", PEPTIDES_DIR / "2026-07-07-recap-bridge-biomarkers.md", "thread", "PCAC Recap + Biomarker Bridge",
     "pre_launch,pcac,recap,biomarkers,lead_magnet_bridge",
     "PCAC peptide series — Recap (7 of 7). All 7 compounds consolidated + hard pivot to 5 Biomarkers lead magnet. Lead magnet drops 48-72h after this thread."),
]

FOLDER = "pcac_series"
SUBSTACK_LINK = "https://doseofproof.substack.com/"


def parse_thread(md_path: Path) -> str:
    """Parse a thread markdown file into Buffer-ready content.

    Strategy: find the FIRST `**Tweet N` header (which is Tweet 1, the hook).
    Body starts there. Stop body at "## Visual direction" or "## Compliance verification".
    Extract each tweet's content via regex. Join with `---` (Buffer thread separator).
    """
    text = md_path.read_text(encoding="utf-8")

    # Find the first tweet header — that's where the thread body starts
    first_tweet_match = re.search(r"\*\*Tweet\s+\d+", text)
    if first_tweet_match:
        body = text[first_tweet_match.start():]
    else:
        body = text

    # Stop at visual direction / compliance verification / sources sections
    for marker in ["## Visual direction", "## Compliance verification", "## Sources"]:
        if marker in body:
            body = body.split(marker)[0]

    # Extract each tweet block. Tweet block = text between `**Tweet N**` header and
    # the next `**Tweet N+1**` header (or end of body).
    tweet_pattern = re.compile(
        r"\*\*Tweet\s+\d+(?:\s*\([^)]*\))?\s*(?:\([^)]*\))?\s*:?\s*\*\*\s*\n(.*?)(?=\*\*Tweet\s+\d+|\Z)",
        re.DOTALL,
    )
    matches = tweet_pattern.findall(body)
    if not matches:
        return body.strip()

    cleaned_tweets = []
    for tweet in matches:
        tweet = tweet.strip()
        # Strip any `---` separators that ended up inside the tweet block
        tweet = re.sub(r"^---\s*$", "", tweet, flags=re.MULTILINE).strip()
        # Strip markdown bold (`**text**` → `text`) — Buffer posts literal asterisks
        tweet = re.sub(r"\*\*([^*]+)\*\*", r"\1", tweet)
        # Collapse 3+ newlines to 2 (preserve paragraph breaks but clean up excess)
        tweet = re.sub(r"\n{3,}", "\n\n", tweet)
        if tweet:
            cleaned_tweets.append(tweet)

    return "\n\n---\n\n".join(cleaned_tweets)


def build_csv():
    rows = []
    # Header
    rows.append([
        "date", "time", "channel", "type", "content", "media", "link",
        "tags", "folder", "asset_source", "notes",
    ])
    for date, time, asset_path, post_type, topic, tags, notes in SCHEDULE:
        if not asset_path.exists():
            print(f"⚠️  Missing: {asset_path}")
            continue
        content = parse_thread(asset_path)
        asset_relpath = str(asset_path.relative_to(ROOT))
        rows.append([
            date,
            time,
            "x",  # channel — X.com (post to @doseofproof or @DreTheSalesGuy per index)
            post_type,
            content,
            "",  # media — none per Flag 5 closure (text-first)
            SUBSTACK_LINK,  # link — single Substack CTA
            tags,
            FOLDER,
            f"✅ FINAL — {asset_relpath}",
            notes,
        ])

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(rows)
    print(f"✅ Wrote {OUT_CSV}")
    print(f"   Total rows: {len(rows)} (1 header + {len(rows)-1} threads)")


if __name__ == "__main__":
    build_csv()