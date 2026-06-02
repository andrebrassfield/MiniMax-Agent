#!/usr/bin/env python3
"""
M3-summary driver for the MCP architecture page.

Esalen posture: this script is the deterministic shim. It:
  1. Loads the regex-compressed text (already produced by direct_intake.ingest)
  2. Builds an M3SummaryRequest (stores in CCR)
  3. Writes the request to a sidecar JSON
  4. Reads the M3 summary from a file (produced externally — by M3, the orchestrator)
  5. Applies the summary, computes the end-to-end ratio
  6. Writes the M3SummaryResult to a sidecar JSON

The M3 call itself happens in the orchestrator (Mavis in her own session, or
a human reviewer) — NOT in this script. The script accepts the summary text
as a file input, never imports any LLM client, and never makes any network call.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Direct-intake lives at <vault>/99 _system/mcps/direct-intake
DIRECT_INTAKE = HERE.parent / "mcps" / "direct-intake"
if not DIRECT_INTAKE.exists():
    raise SystemExit(f"direct-intake not found at {DIRECT_INTAKE}")
sys.path.insert(0, str(DIRECT_INTAKE))

from intake import compress, summarize  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", required=True,
        help="Source URL/file the text came from (for the request meta)",
    )
    parser.add_argument(
        "--raw-md", required=True, type=Path,
        help="Path to the regex-compressed markdown (output of direct_intake)",
    )
    parser.add_argument(
        "--summary-md", required=True, type=Path,
        help="Path to the M3-produced summary markdown (written by the orchestrator)",
    )
    parser.add_argument(
        "--out-dir", required=True, type=Path,
        help="Directory to write request/result sidecar JSONs into",
    )
    parser.add_argument(
        "--hint", default="",
        help="Optional prompt hint for M3 (focus area, etc.)",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_text = args.raw_md.read_text(encoding="utf-8")

    # Step 1: regex-compress the raw markdown (in case the file is the raw
    # output, not the already-compressed version)
    compressed = compress.compress(
        raw_text,
        aggressive=False,
        min_tokens_to_compress=200,
    )

    # Step 2: build the M3 request (stores regex-compressed text in CCR)
    req = summarize.make_request(
        source=args.source,
        compressed=compressed,
        prompt_hint=args.hint,
    )

    request_path = args.out_dir / f"{req.request_id}-request.json"
    summarize.save_request_json(req, request_path)

    # Step 3: render the prompt (for transparency — the orchestrator can
    # use this to see what M3 saw)
    prompt_path = args.out_dir / f"{req.request_id}-prompt.txt"
    prompt_path.write_text(summarize.render_prompt(req), encoding="utf-8")

    # Step 4: apply the M3 summary (read from the file the orchestrator wrote)
    summary_text = args.summary_md.read_text(encoding="utf-8")
    result = summarize.apply_summary(
        req,
        summary_text,
        store_summary_in_ccr=True,
    )
    summary_path = args.out_dir / f"{req.request_id}-summary.json"
    summarize.save_summary_json(result, summary_path)

    # Step 5: write the end-to-end ratio report
    overall = summarize.overall_ratio(compressed, result)
    overall_path = args.out_dir / f"{req.request_id}-ratio.json"
    overall_path.write_text(json.dumps(overall, indent=2), encoding="utf-8")

    # Print a one-line report
    print(f"OK  request_id       = {req.request_id}")
    print(f"    source           = {args.source}")
    print(f"    original_tokens  = {overall['original_tokens']}")
    print(f"    regex_tokens     = {overall['regex_compressed_tokens']}  (ratio {overall['regex_ratio']}, {round((1-overall['regex_ratio'])*100,1)}% savings)")
    print(f"    m3_summary_tokens= {overall['m3_summary_tokens']}  (ratio {overall['end_to_end_ratio']}, {overall['end_to_end_savings_pct']}% savings)")
    print(f"    ccr_hash         = {overall['ccr_hash'][:16]}...")
    print(f"    sidecars in      = {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
