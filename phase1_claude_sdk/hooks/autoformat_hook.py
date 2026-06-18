#!/usr/bin/env python3
"""
AutoFormat PostToolUse Hook
Runs after every write_file / edit_file tool call.
Formats Python files with ruff (format + check).
"""

import json
import os
import subprocess
import sys

def run_cmd(cmd, cwd=None):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "timeout"

def main():
    # Read hook input from stdin (JSON)
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    tool_result = hook_input.get("tool_result", {})

    # Only act on write_file and edit_file
    if tool_name not in ("write_file", "edit_file", "patch"):
        sys.exit(0)

    # Get the file path from tool_result or tool_input
    file_path = None
    if "path" in tool_result:
        file_path = tool_result["path"]
    elif "tool_input" in hook_input and "path" in hook_input["tool_input"]:
        file_path = hook_input["tool_input"]["path"]

    if not file_path or not file_path.endswith(".py"):
        sys.exit(0)

    # Resolve path
    file_path = os.path.expanduser(file_path)
    if not os.path.exists(file_path):
        sys.exit(0)

    # Run ruff format
    ok, out, err = run_cmd(f"ruff format {file_path}")
    if not ok:
        print(f"AutoFormat: ruff format failed on {file_path}: {err}", file=sys.stderr)

    # Run ruff check --fix
    ok, out, err = run_cmd(f"ruff check --fix {file_path}")
    if not ok:
        print(f"AutoFormat: ruff check --fix failed on {file_path}: {err}", file=sys.stderr)

    # Run isort
    ok, out, err = run_cmd(f"isort {file_path}")
    if not ok:
        print(f"AutoFormat: isort failed on {file_path}: {err}", file=sys.stderr)

    sys.exit(0)

if __name__ == "__main__":
    main()