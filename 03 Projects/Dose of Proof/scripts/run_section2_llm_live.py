#!/usr/bin/env python3
"""
Run all 12 §2 examples through v0.4 hybrid classifier with LLM live.
Saves results to specs/v0.4-llm-live-section2-results.json + prints summary table.
"""
import json
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from dop_engine_v0_4 import classify_hybrid, SENSITIVITY_TAXONOMY_EXAMPLES


def main():
    results = []
    start = time.time()
    for i, ex in enumerate(SENSITIVITY_TAXONOMY_EXAMPLES, start=1):
        text = ex["contains"]
        expected = ex["flags"]
        expected_class = "CLEAR" if expected == "none" else "SENSITIVE"

        t0 = time.time()
        result = classify_hybrid(text, hook_family="regulatory-reality", use_llm=True)
        elapsed = time.time() - t0

        regex_flags = sorted(set(result["regex_layer"]["flags"]))
        llm_flags = sorted(set(result["llm_layer"]["flags"]))
        combined_flags = sorted(set(result["sensitive_reasons"]))
        combined_class = result["classification"]

        expected_set = set() if expected == "none" else set(expected.split("+"))
        regex_set = set(regex_flags)
        llm_set = set(llm_flags)
        combined_set = set(combined_flags)

        regex_pass = (
            (expected_class == "CLEAR" and result["regex_layer"]["classification"] == "CLEAR")
            or (expected_class == "SENSITIVE" and expected_set.issubset(regex_set))
        )
        llm_pass = (
            (expected_class == "CLEAR" and result["llm_layer"]["classification"] == "CLEAR")
            or (expected_class == "SENSITIVE" and expected_set.issubset(llm_set))
        )
        combined_pass = (
            (expected_class == combined_class)
            and (expected_class == "CLEAR" or expected_set.issubset(combined_set))
        )
        disagreement = regex_set != llm_set

        results.append({
            "num": i,
            "text": text,
            "expected_class": expected_class,
            "expected_flags": sorted(expected_set),
            "regex_class": result["regex_layer"]["classification"],
            "regex_flags": regex_flags,
            "llm_class": result["llm_layer"]["classification"],
            "llm_flags": llm_flags,
            "llm_error": result["llm_layer"].get("error"),
            "combined_class": combined_class,
            "combined_flags": combined_flags,
            "regex_pass": regex_pass,
            "llm_pass": llm_pass,
            "combined_pass": combined_pass,
            "disagreement": disagreement,
            "elapsed_sec": round(elapsed, 1),
        })
        print(f"[{i}/12] elapsed={elapsed:.1f}s regex={result['regex_layer']['classification']}/{regex_flags} llm={result['llm_layer']['classification']}/{llm_flags} combined={combined_class}/{combined_flags} {'PASS' if combined_pass else 'FAIL'}", flush=True)

    total_elapsed = time.time() - start
    pass_count = sum(1 for r in results if r["combined_pass"])
    disagreements = sum(1 for r in results if r["disagreement"])

    print(f"\nCombined PASS: {pass_count}/12 (total {total_elapsed:.1f}s)")
    print(f"Regex↔LLM disagreements: {disagreements}/12")
    print(f"Regex-only PASS: {sum(1 for r in results if r['regex_pass'])}/12")
    print(f"LLM-only PASS: {sum(1 for r in results if r['llm_pass'])}/12")

    out_path = SCRIPT_DIR.parent / "specs" / "v0.4-llm-live-section2-results.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()