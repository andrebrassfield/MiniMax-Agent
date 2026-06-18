"""
Example tools demonstrating the @tool decorator.
"""

from mini_harness.tools.registry import tool, registry
from typing import List, Dict, Any, Optional
import json
import os


@tool
def read_file(path: str) -> str:
    """Read a file from the filesystem.
    
    Args:
        path: Path to the file to read
    """
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file.
    
    Args:
        path: Path to write to
        content: Content to write
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool
def search_files(pattern: str, directory: str = ".") -> List[str]:
    """Search for files matching a pattern.
    
    Args:
        pattern: Glob pattern to match
        directory: Directory to search in
    """
    import glob
    matches = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    return matches


@tool
def run_command(command: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
    """Run a shell command and return the result.
    
    Args:
        command: Command to execute
        working_dir: Working directory for the command
    """
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_dir,
            timeout=30
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "Command timed out", "returncode": -1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "returncode": -1}


@tool
def web_search(query: str, limit: int = 5) -> List[Dict[str, str]]:
    """Search the web for information.
    
    Args:
        query: Search query
        limit: Maximum number of results
    """
    # Placeholder - would integrate with actual search API
    return [
        {"title": f"Result {i} for '{query}'", "url": f"https://example.com/{i}", "snippet": "..."}
        for i in range(1, limit + 1)
    ]


if __name__ == "__main__":
    # Print all registered tool schemas
    print(json.dumps(registry.get_schemas(), indent=2))