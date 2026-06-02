"""
convert.py — markitdown adapter.

The narrow convert_local() / convert_stream() APIs only. Never convert()
(the permissive one that can fetch URLs).

Esalen posture: deterministic file → markdown. No NLP. The model does the
understanding.
"""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)


class ConvertError(RuntimeError):
    """markitdown could not convert the file."""


def convert_local(path: str | Path) -> str:
    """Convert a local file to markdown via markitdown. Narrow API.

    Supported types: PDF, PPTX, DOCX, XLSX, image (via markitdown-ocr if
    installed), audio (via audio-transcription), HTML, CSV/JSON/XML, ZIP,
    YouTube URLs, EPUBs, Outlook messages.

    Returns:
        The markdown text.

    Raises:
        ConvertError: If the file cannot be converted.
    """
    path = Path(path)
    if not path.exists():
        raise ConvertError(f"file not found: {path}")
    if not path.is_file():
        raise ConvertError(f"not a regular file: {path}")

    try:
        from markitdown import MarkItDown
    except ImportError as e:
        raise ConvertError(
            f"markitdown not installed. pip install 'markitdown[pdf,docx,pptx,xlsx]': {e}"
        )

    try:
        md = MarkItDown(enable_plugins=False)  # plugins need API keys; keep off for now
        result = md.convert_local(str(path))
        return result.text_content
    except Exception as e:
        log.exception("markitdown failed on %s", path)
        raise ConvertError(f"markitdown failed on {path}: {e}") from e


def convert_stream(content: bytes, content_type: str = "text/html") -> str:
    """Convert a byte stream to markdown. Used for HTML fetched by scrapling.

    Args:
        content: The raw bytes.
        content_type: MIME type. Defaults to "text/html" (the most common
            case for scrapling output).

    Returns:
        The markdown text.
    """
    try:
        from markitdown import MarkItDown
        from markitdown._markitdown import StreamInfo
    except ImportError as e:
        raise ConvertError(f"markitdown not installed: {e}")

    try:
        md = MarkItDown(enable_plugins=False)
        # markitdown's convert_stream expects a file-like object + a StreamInfo
        # hint for content type. Use the proper StreamInfo class, not a dict.
        stream_info = StreamInfo(mimetype=content_type)
        result = md.convert_stream(io.BytesIO(content), stream_info=stream_info)
        return result.text_content
    except Exception as e:
        log.exception("markitdown stream conversion failed (%s)", content_type)
        raise ConvertError(f"markitdown stream conversion failed: {e}") from e


def convert_text(text: str) -> str:
    """Pass-through for text/data files. Returned unchanged (with normalization).

    The model can already read plain text. No transformation needed.
    """
    return text
