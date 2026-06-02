"""
Local test harness for PatternForge.

Verifies:
- The CLI help works
- The template subcommand works (no LLM)
- The examples subcommand works (no LLM)
- The forge subcommand works (full LLM call, with a short intent)

Usage:
    .venv/bin/python test_forge.py
"""

import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).parent.resolve()
VENV_PY = _HERE.parent / "glass-server" / ".venv" / "bin" / "python"
SCRIPT = _HERE / "pattern_forge.py"


def run(args, **kwargs):
    """Run the pattern_forge.py script via the Glass Server's venv."""
    return subprocess.run(
        [str(VENV_PY), str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        timeout=kwargs.get("timeout", 300),
    )


def test_help():
    print("=== test_help ===")
    result = run(["--help"])
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "PatternForge" in result.stdout
    assert "forge" in result.stdout
    print("OK — help works")
    print()


def test_template():
    print("=== test_template ===")
    result = run(["template", "--name", "Test Workflow"])
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "# GENERATIVE CODE: Test Workflow" in result.stdout
    assert "## 1. The design problem" in result.stdout
    assert "## 8. Wholeness check" in result.stdout
    print("OK — template works")
    print()


def test_examples():
    print("=== test_examples ===")
    result = run(["examples"])
    assert result.returncode == 0, f"Failed: {result.stderr}"
    assert "Email Triage" in result.stdout or "triage" in result.stdout.lower()
    print("OK — examples work")
    print()


def test_forge_short():
    print("=== test_forge_short (full M3 call) ===")
    # Short intent for fast test
    result = run([
        "forge",
        "--intent", "A workflow to remind me to stand up and stretch every 90 minutes.",
        "--temperature", "0.7",
    ], timeout=240)
    if result.returncode != 0:
        print(f"FAILED: {result.stderr}")
        return False
    output = result.stdout
    assert "GENERATIVE CODE" in output, "Missing GENERATIVE CODE header"
    # Count sections
    section_count = output.count("## ")
    assert section_count >= 6, f"Expected 6+ sections, found {section_count}"
    print(f"OK — forge produced {len(output)} chars, {section_count} sections")
    return True


if __name__ == "__main__":
    test_help()
    test_template()
    test_examples()
    # Only run the LLM test if not skipped
    if "--no-llm" not in sys.argv:
        try:
            test_forge_short()
        except Exception as e:
            print(f"LLM test failed: {e}")
    print("All tests complete.")
