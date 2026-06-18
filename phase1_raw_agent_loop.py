#!/usr/bin/env python3
"""
Phase 1 Build #1: Raw Agent Loop — Anthropic SDK
~45 lines. Three tools: web_search, read_file, write_file.
Run: python3 phase1_raw_agent_loop.py
"""

import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "max_results": {"type": "integer", "default": 5}
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_file",
        "description": "Read a local file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    }
]

def web_search(query, max_results=5):
    # Stub - in real use, call a search API
    return f"[Search results for: {query}]\n1. Result 1\n2. Result 2\n3. Result 3"

def read_file(path):
    try:
        with open(os.path.expanduser(path), 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading {path}: {e}"

def write_file(path, content):
    try:
        os.makedirs(os.path.dirname(os.path.expanduser(path)) or '.', exist_ok=True)
        with open(os.path.expanduser(path), 'w') as f:
            f.write(content)
        return f"Written {len(content)} chars to {path}"
    except Exception as e:
        return f"Error writing {path}: {e}"

TOOL_FUNCS = {"web_search": web_search, "read_file": read_file, "write_file": write_file}

SYSTEM = """You are a daily briefing agent. Read Markdown notes + RSS feeds, write a summarized briefing to disk every morning.
Tools: web_search, read_file, write_file. Be concise. Always cite sources."""

def main():
    messages = [{"role": "user", "content": "Generate today's briefing from ~/vault/daily-notes/ and RSS feeds. Write to ~/briefings/$(date +%F).md"}]

    for i in range(10):  # max iterations
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=SYSTEM,
            messages=messages,
            tools=TOOLS
        )

        if not response.content or not any(c.type == "tool_use" for c in response.content):
            print(response.content[0].text if response.content else "No response")
            break

        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_FUNCS[block.name](**block.input)
                messages.append({"role": "assistant", "content": [block]})
                messages.append({
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": block.id, "content": result}]
                })
            else:
                messages.append({"role": "assistant", "content": [block]})

if __name__ == "__main__":
    main()