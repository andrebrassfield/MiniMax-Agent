#!/usr/bin/env python3
"""
Mavis Isolated Vault Server
==========================

A minimal, isolated HTTP server for the MiniMax-Agent vault.
Replicates a useful subset of the obsidian-local-rest-api endpoints
without touching the running Obsidian instance (which is on a
different vault and can't be switched without boundary violation).

Scope:
  - Reads my apiKey from the vault's data.json
  - Serves ONLY files under /Users/brassfieldventuresllc/MiniMax-Agent/
  - Refuses any path that escapes the vault (path traversal protection)
  - Listens on 127.0.0.1:28080 (non-standard, no conflict with Obsidian)

Endpoints:
  GET    /             server status
  GET    /vault/       list vault root
  GET    /vault/<path> read file
  PUT    /vault/<path> create/overwrite file (body = content)
  POST   /vault/<path> append to file (body = content)
  DELETE /vault/<path> delete file
  POST   /search/simple/ full-text search (body = {"query": "..."})
  GET    /active/     returns the latest daily note (best-effort)
"""

import http.server
import json
import os
import re
import socketserver
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path

VAULT = Path("/Users/brassfieldventuresllc/MiniMax-Agent")
PORT = 28080
HOST = "127.0.0.1"
PLUGIN_DATA = VAULT / ".obsidian" / "plugins" / "obsidian-local-rest-api" / "data.json"


def load_api_key():
    """Load apiKey from the vault's plugin data.json."""
    if not PLUGIN_DATA.exists():
        return None
    try:
        with open(PLUGIN_DATA) as f:
            data = json.load(f)
        return data.get("apiKey")
    except (OSError, json.JSONDecodeError):
        return None


API_KEY = load_api_key()


def auth_ok(headers):
    """Verify Bearer auth against my vault's apiKey."""
    if not API_KEY:
        return False, "apiKey not loaded from vault data.json"
    auth = headers.get("Authorization", "")
    # Accept both "Bearer <key>" and bare "<key>" (lenient, like the original plugin)
    if auth.startswith("Bearer "):
        token = auth[7:].strip()
    else:
        token = auth.strip()
    if token == API_KEY:
        return True, None
    return False, f"apiKey mismatch (vault has {API_KEY[:8]}..., you sent {token[:8]}...)"


def safe_path(requested: str) -> Path:
    """Resolve a vault-relative path, refusing to escape the vault."""
    # Strip leading slash, decode URL escapes
    rel = urllib.parse.unquote(requested.lstrip("/"))
    if not rel:
        return VAULT
    candidate = (VAULT / rel).resolve()
    # Make sure resolved path is inside VAULT
    try:
        candidate.relative_to(VAULT.resolve())
    except ValueError:
        raise PermissionError(f"path escapes vault: {requested}")
    return candidate


def list_dir(rel_path: str) -> dict:
    target = safe_path(rel_path)
    if not target.exists() or not target.is_dir():
        return {"files": [], "error": "not a directory"}
    entries = []
    for entry in sorted(target.iterdir()):
        rel = entry.relative_to(VAULT)
        entries.append({
            "path": str(rel),
            "type": "directory" if entry.is_dir() else "file",
            "size": entry.stat().st_size if entry.is_file() else None,
        })
    return {"files": entries}


def read_file(rel_path: str) -> tuple[int, str, str]:
    target = safe_path(rel_path)
    if not target.exists():
        return 404, "application/json", json.dumps({"error": "not found", "path": rel_path})
    if target.is_dir():
        return 400, "application/json", json.dumps({"error": "is a directory", "path": rel_path})
    try:
        with open(target, "rb") as f:
            data = f.read()
        # Try to determine content type
        if target.suffix.lower() in (".md", ".markdown", ".txt", ".canvas"):
            ctype = "text/markdown; charset=utf-8"
        elif target.suffix.lower() == ".json":
            ctype = "application/json"
        else:
            ctype = "application/octet-stream"
        return 200, ctype, data.decode("utf-8", errors="replace")
    except OSError as e:
        return 500, "application/json", json.dumps({"error": str(e), "path": rel_path})


def write_file(rel_path: str, body: str, create_parents: bool = True) -> dict:
    target = safe_path(rel_path)
    if create_parents:
        target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_dir():
        return {"error": "is a directory", "path": rel_path}, 400
    with open(target, "w") as f:
        f.write(body)
    return {"ok": True, "path": rel_path, "size": target.stat().st_size}, 200


def append_file(rel_path: str, body: str) -> dict:
    target = safe_path(rel_path)
    if not target.exists():
        return {"error": "not found (use PUT to create)", "path": rel_path}, 404
    if target.is_dir():
        return {"error": "is a directory", "path": rel_path}, 400
    with open(target, "a") as f:
        f.write(body)
    return {"ok": True, "path": rel_path, "size": target.stat().st_size}, 200


def delete_file(rel_path: str) -> dict:
    target = safe_path(rel_path)
    if not target.exists():
        return {"error": "not found", "path": rel_path}, 404
    if target.is_dir():
        return {"error": "is a directory (recursive delete not supported)", "path": rel_path}, 400
    target.unlink()
    return {"ok": True, "path": rel_path}, 200


def simple_search(query: str) -> dict:
    """Full-text search across all .md files in the vault."""
    if not query:
        return {"results": [], "error": "empty query"}
    results = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    for md_file in VAULT.rglob("*.md"):
        # Skip hidden directories
        if any(part.startswith(".") for part in md_file.relative_to(VAULT).parts):
            continue
        # Skip auto-generated tool data
        if any(part in (".claude", ".claudian", ".smart-env") for part in md_file.relative_to(VAULT).parts):
            continue
        try:
            content = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if pattern.search(content):
            # Find first matching line + position
            lines = content.splitlines()
            matches = []
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    matches.append({"line": i, "text": line[:200]})
                    if len(matches) >= 3:
                        break
            results.append({
                "path": str(md_file.relative_to(VAULT)),
                "matches": matches,
            })
    return {"results": results, "count": len(results)}


def latest_daily() -> Path | None:
    """Return the most recent daily note (yyyy-mm-dd.md in 01 Daily/)."""
    daily_dir = VAULT / "01 Daily"
    if not daily_dir.exists():
        return None
    candidates = sorted(daily_dir.glob("????-??-??.md"), reverse=True)
    return candidates[0] if candidates else None


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        # Custom log to stdout with timestamp
        sys.stdout.write(f"[{datetime.now().isoformat(timespec='seconds')}] {self.address_string()} {fmt % args}\n")
        sys.stdout.flush()

    def _send(self, status, ctype, body):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, payload):
        self._send(status, "application/json", json.dumps(payload, indent=2))

    def _check_auth(self):
        ok, msg = auth_ok(self.headers)
        if not ok:
            self._send_json(401, {"error": "Authorization required", "detail": msg, "errorCode": 40101})
            return False
        return True

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Public status endpoint (no auth)
        if path == "/":
            self._send_json(200, {
                "status": "OK",
                "service": "Mavis Isolated Vault Server",
                "vault": str(VAULT),
                "port": PORT,
                "apiKeyLoaded": API_KEY is not None,
                "endpoints": [
                    "GET    /",
                    "GET    /vault/  (list root)",
                    "GET    /vault/<path>",
                    "PUT    /vault/<path>",
                    "POST   /vault/<path>  (append)",
                    "DELETE /vault/<path>",
                    "POST   /search/simple/  (body: {\"query\": \"...\"})",
                    "GET    /active/  (latest daily note)",
                ],
            })
            return

        if not self._check_auth():
            return

        if path == "/vault/" or path == "/vault":
            self._send_json(200, list_dir(""))
            return

        if path.startswith("/vault/"):
            rel = path[len("/vault/"):]
            status, ctype, body = read_file(rel)
            self._send(status, ctype, body)
            return

        if path == "/active/" or path == "/active":
            latest = latest_daily()
            if not latest:
                self._send_json(404, {"error": "no daily note found"})
                return
            rel = str(latest.relative_to(VAULT))
            status, ctype, body = read_file(rel)
            self._send(status, ctype, body)
            return

        self._send_json(404, {"error": "not found", "path": path})

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if not self._check_auth():
            return
        if not path.startswith("/vault/"):
            self._send_json(404, {"error": "PUT only on /vault/<path>"})
            return
        rel = path[len("/vault/"):]
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        result, status = write_file(rel, body)
        self._send_json(status, result)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if not self._check_auth():
            return
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        # Determine: append or search?
        if path.startswith("/vault/"):
            rel = path[len("/vault/"):]
            result, status = append_file(rel, body)
            self._send_json(status, result)
            return
        if path == "/search/simple/" or path == "/search/simple":
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                payload = {}
            query = payload.get("query", "")
            self._send_json(200, simple_search(query))
            return
        self._send_json(404, {"error": "not found", "path": path})

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if not self._check_auth():
            return
        if not path.startswith("/vault/"):
            self._send_json(404, {"error": "DELETE only on /vault/<path>"})
            return
        rel = path[len("/vault/"):]
        result, status = delete_file(rel)
        self._send_json(status, result)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    if not API_KEY:
        print(f"FATAL: could not load apiKey from {PLUGIN_DATA}", file=sys.stderr)
        sys.exit(1)
    print(f"Mavis Isolated Vault Server")
    print(f"  vault: {VAULT}")
    print(f"  bind:  http://{HOST}:{PORT}")
    print(f"  apiKey: {API_KEY[:8]}...{API_KEY[-4:]} (loaded from data.json)")
    print(f"  scope: only files inside {VAULT}")
    print(f"  auth:  Authorization: Bearer {API_KEY[:8]}...")
    print()
    with ThreadingServer((HOST, PORT), Handler) as httpd:
        print(f"Listening... (Ctrl-C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down.")


if __name__ == "__main__":
    main()
