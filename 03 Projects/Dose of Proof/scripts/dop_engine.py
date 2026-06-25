#!/usr/bin/env python3
"""
Dose of Proof — Daily Content Engine v0.2

Reads source corpus, generates 8-11 posts per day for the Postiz channels,
runs compliance audit, writes to queue/drafts-YYYY-MM-DD.mdl.

v0.2 BEHAVIOR (volume bump — "take over the market"):
- Pillar rotation: P1 Mon/Thu/Sun | P2 Tue/Fri | P3 Wed/Sat | PCAC-Deep-Dive weekly
- Channel split: 6 Facebook text + 1 multi-image FB + 1 Instagram carousel + 3 Pinterest pins per day
- Source: prelaunch calendar (which asset for which date) + existing X thread / LinkedIn / Substack corpus
- FB text: programmatic from hooks in source asset
- FB multi-image: reuses the IG carousel slides (FB supports up to 10 images per post)
- IG carousel: reuses existing rendered slides
- Pinterest pins: cover + secondary data slide + CTA — 3 separate pins per source, Dre batch-pushes
- Compliance: programmatic 8-item audit (dop_compliance.py)

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

# Paths
PROJECT_ROOT = Path("/Users/brassfieldventuresllc/MiniMax-Agent/03 Projects/Dose of Proof")
SOCIAL_DIR = PROJECT_ROOT / "assets" / "social"
QUEUE_DIR = PROJECT_ROOT / "queue"
VISUAL_DIR = PROJECT_ROOT / "assets" / "visual"

# Pillar rotation by weekday (0=Mon, 6=Sun)
PILLAR_ROTATION = {
    0: "P1",  # Mon: Lived Protocol
    1: "P2",  # Tue: Macro-Longevity Economy
    2: "P3",  # Wed: Reconstitution & Data Utility
    3: "P1",  # Thu: Lived Protocol
    4: "P2",  # Fri: Macro-Longevity Economy
    5: "P3",  # Sat: Reconstitution & Data Utility
    6: "PCAC",  # Sun: PCAC deep-dive
}

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

    # v0.2: 6 Facebook text posts spread across the day (was 4)
    fb_times = ["08:00", "11:00", "13:30", "16:00", "18:30", "21:00"]
    for i, hook in enumerate(hooks[:6]):
        time = fb_times[i] if i < len(fb_times) else fb_times[-1]
        posts.append(fb_post_for_hook(hook, pillar, target_date, time))
        posts[-1]["time"] = time
        posts[-1]["date"] = target_date
        posts[-1]["pillar"] = pillar

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
            multi_img_post["post_label"] = "fb_multi_image"
            posts.append(multi_img_post)

    # 1 Instagram carousel (existing logic)
    ig_post = ig_carousel_for_source(primary_content, primary, target_date)
    ig_post["date"] = target_date
    ig_post["time"] = "15:00"
    ig_post["pillar"] = pillar
    posts.append(ig_post)

    # v0.2: 3 Pinterest pins (cover + secondary data slide + CTA) — Dre batch-pushes
    pin_times = ["09:30", "14:00", "19:00"]
    for slot in [1, 2, 3]:
        pin_post = pinterest_pin_for_source(primary_content, primary, pillar, target_date, pin_times[slot - 1], slot_idx=slot)
        if pin_post:
            pin_post["date"] = target_date
            pin_post["time"] = pin_times[slot - 1]
            pin_post["pillar"] = pillar
            pin_post["pin_slot"] = slot
            posts.append(pin_post)

    return posts


def write_queue(target_date: str, posts: list[dict]) -> tuple[Path, Path]:
    """Write posts to queue files. Returns (drafts_path, pins_path)."""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    drafts_path = QUEUE_DIR / f"drafts-{target_date}.mdl"
    pins_path = QUEUE_DIR / f"pins-{target_date}.mdl"

    with open(drafts_path, "w") as f:
        f.write(f"# Dose of Proof — Daily drafts for {target_date}\n")
        f.write(f"# Generated {datetime.now().isoformat()} by dop_engine.py v0.1\n")
        f.write(f"# Source corpus: 30 assets (X threads, LinkedIn carousels, Substack posts)\n")
        f.write(f"# Compliance: dop_compliance.py 8-item gate\n")
        f.write(f"#\n")
        f.write(f"# Format: post_id | pillar | channel | date | time | compliance | content | image_paths\n")
        f.write(f"---\n\n")

    with open(pins_path, "w") as pf:
        pf.write(f"# Dose of Proof — Pinterest pins for {target_date}\n")
        pf.write(f"# Generated {datetime.now().isoformat()} by dop_engine.py v0.1\n")
        pf.write(f"# POSTIZ BOARD ID REQUIRED for manual push via Postiz UI\n")
        pf.write(f"---\n\n")

    drafts_count = 0
    pins_count = 0
    post_idx = 1
    for post in posts:
        channel = post["channel"]
        content = post["content"]
        # Compliance audit
        ok, fails = compliance.audit(content)
        compliance_str = "PASS" if ok else f"FAIL ({len(fails)} issues)"
        # Post ID
        channel_prefix = {"facebook": "fb", "instagram": "ig", "pinterest": "pin"}.get(channel, "x")
        post_id = f"dop-{channel_prefix}-{target_date.replace('-','')}-{post_idx:03d}"

        # Build image paths string
        img_str = " | ".join(post.get("image_paths", []))

        if channel == "pinterest":
            # Pinterest goes to pin queue (Dre UI push)
            with open(pins_path, "a") as pf:
                pf.write(f"## Pin {post_idx} — {post_id}\n")
                pf.write(f"- Pillar: {post.get('pillar', '?')}\n")
                pf.write(f"- Date/Time: {post['date']} {post['time']}\n")
                pf.write(f"- Status: DRE_MANUAL_PUSH\n")
                pf.write(f"- Compliance: {compliance_str}\n")
                if fails:
                    pf.write(f"- Issues:\n")
                    for fail in fails:
                        pf.write(f"  - {fail}\n")
                pf.write(f"- Image: {img_str or '(NEEDS RENDER)'}\n")
                pf.write(f"- Content:\n```\n{content}\n```\n\n")
            pins_count += 1
        else:
            # Auto-push channels (FB + IG) go to drafts
            with open(drafts_path, "a") as f:
                f.write(f"{post_id} | {post.get('pillar','?')} | {channel} | {post['date']} | {post['time']} | {compliance_str} | {content.replace(chr(10), ' // ')} | {img_str}\n")
            drafts_count += 1
        post_idx += 1

    print(f"✅ Wrote {drafts_count} auto-push posts → {drafts_path}")
    print(f"📌 Wrote {pins_count} Pinterest pins → {pins_path}")
    return drafts_path, pins_path


def main():
    parser = argparse.ArgumentParser(description="Dose of Proof daily content engine")
    parser.add_argument("--date", default=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                        help="Target date (default: tomorrow)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to disk")
    args = parser.parse_args()

    print("=" * 70)
    print(f"Dose of Proof — Daily Content Engine v0.1")
    print(f"Target date: {args.date}")
    print("=" * 70)

    posts = generate_for_date(args.date)
    print(f"\nGenerated {len(posts)} posts ({sum(1 for p in posts if p['channel']!='pinterest')} auto-push + {sum(1 for p in posts if p['channel']=='pinterest')} Pinterest)")

    # Compliance summary
    fail_count = 0
    for post in posts:
        ok, fails = compliance.audit(post["content"])
        if not ok:
            fail_count += 1
            print(f"  ⚠️  {post['channel']} — {len(fails)} compliance issues: {fails[:2]}")
    if fail_count == 0:
        print(f"  ✅ All posts pass 8-item compliance gate")
    else:
        print(f"  ⚠️  {fail_count} posts flagged for human review (still written to queue with status: review)")

    if not args.dry_run:
        drafts_path, pins_path = write_queue(args.date, posts)
        print(f"\n📁 Queue files:")
        print(f"   - {drafts_path}")
        print(f"   - {pins_path}")
    else:
        print(f"\n[dry-run] No files written")


if __name__ == "__main__":
    main()