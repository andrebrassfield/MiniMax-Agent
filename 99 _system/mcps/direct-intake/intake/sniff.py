"""
sniff.py — the Sniff router.

Input → (type, converter). The type detection is the source of truth for routing.
Downstream converters don't re-detect.

Supported types:
    - url        (http://, https://, or .txt/.url/.webloc containing a URL)
    - pdf        (.pdf)
    - pptx       (.pptx, .ppt)
    - docx       (.docx, .doc)
    - xlsx       (.xlsx, .xls, .csv)
    - image      (.jpg, .jpeg, .png, .heic, .webp, .tiff, .gif)
    - audio      (.wav, .mp3, .m4a, .ogg, .flac)
    - video      (.mp4, .mov, .webm)
    - text       (.txt, .md, .rtf)
    - data       (.json, .xml, .yaml, .yml)
    - youtube    (URLs matching youtube.com / youtu.be)
    - epub       (.epub)
    - zip        (.zip)
    - outlook    (.msg, .eml)
    - unknown    (extension not recognized)

Security: the Sniff also enforces a hard file-size cap and rejects paths that
escape the drop folder. This is the I/O boundary — anything that crosses
must be validated here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# ============================================================
# TYPE DETECTION
# ============================================================

# Map extension (lowercase, with dot) → canonical type
EXTENSION_MAP: dict[str, str] = {
    # Documents
    ".pdf": "pdf",
    ".pptx": "pptx",
    ".ppt": "pptx",
    ".docx": "docx",
    ".doc": "docx",
    ".xlsx": "xlsx",
    ".xls": "xlsx",
    ".csv": "xlsx",  # routed through the same converter
    # Media
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".heic": "image",
    ".webp": "image",
    ".tiff": "image",
    ".tif": "image",
    ".gif": "image",
    ".bmp": "image",
    ".wav": "audio",
    ".mp3": "audio",
    ".m4a": "audio",
    ".ogg": "audio",
    ".flac": "audio",
    ".mp4": "video",
    ".mov": "video",
    ".webm": "video",
    ".mkv": "video",
    # Text / data
    ".txt": "text",
    ".md": "text",
    ".markdown": "text",
    ".rtf": "text",
    ".json": "data",
    ".xml": "data",
    ".yaml": "data",
    ".yml": "data",
    # Containers / ebooks / mail
    ".epub": "epub",
    ".zip": "zip",
    ".msg": "outlook",
    ".eml": "outlook",
}

# Map canonical type → converter name
CONVERTER_MAP: dict[str, str] = {
    "pdf": "markitdown",
    "pptx": "markitdown",
    "docx": "markitdown",
    "xlsx": "markitdown",
    "image": "markitdown",       # markitdown-ocr plugin (LLM-vision)
    "audio": "markitdown",       # markitdown audio-transcription
    "epub": "markitdown",
    "outlook": "markitdown",
    "video": "m3-native",        # M3 native video understanding
    "text": "passthrough",
    "data": "passthrough",
    "zip": "markitdown-iter",
    "url": "scrapling",
    "youtube": "markitdown-youtube",
    "unknown": "reject",
}

# ============================================================
# URL DETECTION
# ============================================================

URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
YOUTUBE_RE = re.compile(
    r"^https?://(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/)",
    re.IGNORECASE,
)

# Disallowed URL schemes
ALLOWED_SCHEMES = {"http", "https"}


def looks_like_url(text: str) -> bool:
    """True if the trimmed input is a single URL on a line."""
    return bool(URL_RE.match(text.strip()))


def is_youtube_url(url: str) -> bool:
    return bool(YOUTUBE_RE.match(url.strip()))


# ============================================================
# SECURITY BOUNDARIES
# ============================================================

# Hard cap on file size. Larger files go to ~/Mavis-Inbox/over-size/ for
# manual review. 100MB matches the design doc.
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024

# URL hostnames that must never be fetched (SSRF / metadata-service defense)
BLOCKED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "::1",
    "0.0.0.0",
    "metadata.google.internal",
    "metadata.goog",
    "169.254.169.254",  # AWS / GCP / Azure metadata service
}

# URL schemes that are never allowed
BLOCKED_SCHEMES = {
    "file",
    "gopher",
    "ftp",
    "ftps",
    "ldap",
    "ldaps",
    "dict",
    "ssh",
    "telnet",
}


@dataclass
class SniffResult:
    """The Sniff output. Routing decision for the ingestion engine."""

    type: str                     # canonical type (see EXTENSION_MAP)
    converter: str                # converter name (see CONVERTER_MAP)
    is_url: bool
    source: str                   # the input (file path or URL)
    size_bytes: Optional[int]     # file size (None for URLs)
    extra: dict                   # type-specific extras (e.g., youtube_id)


class SniffError(ValueError):
    """Raised when the input cannot be routed safely."""


def sniff(input_str: str, drop_root: Optional[Path] = None) -> SniffResult:
    """Route an input string to (type, converter).

    Args:
        input_str: Either an absolute file path or a URL.
        drop_root: If set, file paths must resolve under this directory.
            Used to prevent path traversal in the intake drop folder.

    Returns:
        SniffResult with type, converter, source, and metadata.

    Raises:
        SniffError: If the input is unsafe (path traversal, blocked URL,
            unknown extension, oversize file, etc.).
    """
    s = input_str.strip()
    if not s:
        raise SniffError("empty input")

    # Case 1: looks like a URL
    if looks_like_url(s):
        return _sniff_url(s)

    # Case 2: file path (absolute or relative)
    path = Path(s).expanduser().resolve()
    return _sniff_path(path, drop_root)


def _sniff_url(url: str) -> SniffResult:
    """Validate a URL and route it."""
    parsed = urlparse(url)
    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise SniffError(
            f"blocked URL scheme: {parsed.scheme!r} (allowed: {sorted(ALLOWED_SCHEMES)})"
        )
    if not parsed.hostname:
        raise SniffError(f"URL has no hostname: {url!r}")

    host = parsed.hostname.lower()
    if host in BLOCKED_HOSTS:
        raise SniffError(f"blocked host: {host!r} (metadata-service / loopback defense)")

    # Detect IP literal (block private ranges)
    if _is_private_ip(host):
        raise SniffError(f"blocked private IP literal: {host!r}")

    # YouTube gets its own route (transcript, not full HTML scrape)
    if is_youtube_url(url):
        return SniffResult(
            type="youtube",
            converter=CONVERTER_MAP["youtube"],
            is_url=True,
            source=url,
            size_bytes=None,
            extra={"youtube_id": _extract_youtube_id(url)},
        )

    return SniffResult(
        type="url",
        converter=CONVERTER_MAP["url"],
        is_url=True,
        source=url,
        size_bytes=None,
        extra={},
    )


def _sniff_path(path: Path, drop_root: Optional[Path]) -> SniffResult:
    """Validate a file path and route it."""
    if not path.exists():
        raise SniffError(f"file not found: {path}")

    if not path.is_file():
        raise SniffError(f"not a regular file: {path}")

    # Path-traversal defense: if a drop_root is set, the resolved path
    # must be under it.
    if drop_root is not None:
        try:
            path.relative_to(drop_root.resolve())
        except ValueError:
            raise SniffError(
                f"path escapes drop root: {path} not under {drop_root}"
            )

    # Size cap
    size = path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise SniffError(
            f"file too large: {size} bytes > {MAX_FILE_SIZE_BYTES} cap"
        )

    ext = path.suffix.lower()
    canonical_type = EXTENSION_MAP.get(ext, "unknown")

    if canonical_type == "unknown":
        return SniffResult(
            type="unknown",
            converter=CONVERTER_MAP["unknown"],
            is_url=False,
            source=str(path),
            size_bytes=size,
            extra={"extension": ext},
        )

    return SniffResult(
        type=canonical_type,
        converter=CONVERTER_MAP[canonical_type],
        is_url=False,
        source=str(path),
        size_bytes=size,
        extra={},
    )


def _is_private_ip(host: str) -> bool:
    """Crude check: if host looks like an IP literal and is in a private range,
    block it. DNS resolution would be more thorough (DNS-rebinding defense) but
    requires async — kept simple here, the network layer will re-check.
    """
    import ipaddress
    try:
        ip = ipaddress.ip_address(host)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
        )
    except ValueError:
        return False  # not an IP literal — hostname, allow (DNS layer re-checks)


def _extract_youtube_id(url: str) -> Optional[str]:
    """Extract the YouTube video ID from a watch URL or short URL."""
    m = re.search(r"v=([\w-]{11})", url)
    if m:
        return m.group(1)
    m = re.search(r"youtu\.be/([\w-]{11})", url)
    if m:
        return m.group(1)
    m = re.search(r"shorts/([\w-]{11})", url)
    if m:
        return m.group(1)
    return None
