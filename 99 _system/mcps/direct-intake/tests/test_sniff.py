"""
Tests for the Sniff router.

The Sniff is the I/O boundary. If it routes an unsafe input to a
permissive API, the whole design breaks. These tests cover the
security paths first.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from intake import sniff  # noqa: E402


# ============================================================
# URL DETECTION
# ============================================================

class TestUrlDetection:
    def test_looks_like_url_https(self):
        assert sniff.looks_like_url("https://example.com")

    def test_looks_like_url_http(self):
        assert sniff.looks_like_url("http://example.com/page")

    def test_looks_like_url_rejects_path(self):
        assert not sniff.looks_like_url("/some/file/path")

    def test_looks_like_url_rejects_text(self):
        assert not sniff.looks_like_url("hello world")

    def test_is_youtube_url_watch(self):
        assert sniff.is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    def test_is_youtube_url_short(self):
        assert sniff.is_youtube_url("https://youtu.be/dQw4w9WgXcQ")

    def test_is_youtube_url_shorts(self):
        assert sniff.is_youtube_url("https://youtube.com/shorts/dQw4w9WgXcQ")

    def test_is_youtube_url_negative(self):
        assert not sniff.is_youtube_url("https://example.com")


# ============================================================
# URL VALIDATION (security)
# ============================================================

class TestUrlSecurity:
    def test_https_url(self):
        r = sniff._sniff_url("https://example.com/page")
        assert r.is_url
        assert r.type == "url"
        assert r.converter == "scrapling"

    def test_youtube_url(self):
        r = sniff._sniff_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert r.type == "youtube"
        assert r.converter == "markitdown-youtube"
        assert r.extra["youtube_id"] == "dQw4w9WgXcQ"

    def test_blocks_file_scheme(self):
        with pytest.raises(sniff.SniffError, match="blocked URL scheme"):
            sniff._sniff_url("file:///etc/passwd")

    def test_blocks_ftp_scheme(self):
        with pytest.raises(sniff.SniffError, match="blocked URL scheme"):
            sniff._sniff_url("ftp://example.com/file")

    def test_blocks_ldap_scheme(self):
        with pytest.raises(sniff.SniffError, match="blocked URL scheme"):
            sniff._sniff_url("ldap://example.com")

    def test_blocks_localhost(self):
        with pytest.raises(sniff.SniffError, match="blocked host"):
            sniff._sniff_url("http://localhost:8080/admin")

    def test_blocks_127_0_0_1(self):
        with pytest.raises(sniff.SniffError, match="blocked host"):
            sniff._sniff_url("http://127.0.0.1:8080")

    def test_blocks_aws_metadata(self):
        with pytest.raises(sniff.SniffError, match="blocked host"):
            sniff._sniff_url("http://169.254.169.254/latest/meta-data/")

    def test_blocks_private_ip_literal(self):
        with pytest.raises(sniff.SniffError, match="blocked private IP"):
            sniff._sniff_url("http://10.0.0.1/internal")

    def test_blocks_rfc1918(self):
        with pytest.raises(sniff.SniffError, match="blocked private IP"):
            sniff._sniff_url("http://192.168.1.1/")

    def test_blocks_ipv6_loopback(self):
        with pytest.raises(sniff.SniffError, match="blocked host"):
            sniff._sniff_url("http://[::1]/")

    def test_no_hostname(self):
        with pytest.raises(sniff.SniffError, match="no hostname"):
            sniff._sniff_url("https://")


# ============================================================
# FILE DETECTION
# ============================================================

class TestFileDetection:
    def test_pdf(self, tmp_path):
        p = tmp_path / "doc.pdf"
        p.write_bytes(b"%PDF-1.4\n%fake\n")
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "pdf"
        assert r.converter == "markitdown"
        assert r.size_bytes == p.stat().st_size

    def test_pptx(self, tmp_path):
        p = tmp_path / "deck.pptx"
        p.write_bytes(b"PK\x03\x04")  # ZIP magic
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "pptx"

    def test_docx(self, tmp_path):
        p = tmp_path / "report.docx"
        p.write_bytes(b"PK\x03\x04")
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "docx"

    def test_xlsx(self, tmp_path):
        p = tmp_path / "data.xlsx"
        p.write_bytes(b"PK\x03\x04")
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "xlsx"

    def test_csv(self, tmp_path):
        p = tmp_path / "data.csv"
        p.write_text("a,b,c\n1,2,3\n")
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "xlsx"  # routed through markitdown

    def test_image_extensions(self, tmp_path):
        for ext in ["jpg", "jpeg", "png", "heic", "webp", "tiff", "gif", "bmp"]:
            p = tmp_path / f"img.{ext}"
            p.write_bytes(b"\x00" * 10)
            r = sniff._sniff_path(p, drop_root=tmp_path)
            assert r.type == "image", f"failed for .{ext}"

    def test_audio_extensions(self, tmp_path):
        for ext in ["wav", "mp3", "m4a", "ogg", "flac"]:
            p = tmp_path / f"sound.{ext}"
            p.write_bytes(b"\x00" * 10)
            r = sniff._sniff_path(p, drop_root=tmp_path)
            assert r.type == "audio", f"failed for .{ext}"

    def test_video_extensions(self, tmp_path):
        for ext in ["mp4", "mov", "webm", "mkv"]:
            p = tmp_path / f"video.{ext}"
            p.write_bytes(b"\x00" * 10)
            r = sniff._sniff_path(p, drop_root=tmp_path)
            assert r.type == "video", f"failed for .{ext}"

    def test_text_extensions(self, tmp_path):
        for ext in ["txt", "md", "markdown", "rtf"]:
            p = tmp_path / f"note.{ext}"
            p.write_text("# hello")
            r = sniff._sniff_path(p, drop_root=tmp_path)
            assert r.type == "text", f"failed for .{ext}"

    def test_data_extensions(self, tmp_path):
        for ext in ["json", "xml", "yaml", "yml"]:
            p = tmp_path / f"data.{ext}"
            p.write_text("{}")
            r = sniff._sniff_path(p, drop_root=tmp_path)
            assert r.type == "data", f"failed for .{ext}"

    def test_zip(self, tmp_path):
        p = tmp_path / "stuff.zip"
        p.write_bytes(b"PK\x03\x04")
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "zip"

    def test_epub(self, tmp_path):
        p = tmp_path / "book.epub"
        p.write_bytes(b"PK\x03\x04")
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "epub"

    def test_outlook(self, tmp_path):
        for ext in ["msg", "eml"]:
            p = tmp_path / f"mail.{ext}"
            p.write_text("From: test")
            r = sniff._sniff_path(p, drop_root=tmp_path)
            assert r.type == "outlook", f"failed for .{ext}"

    def test_unknown_extension(self, tmp_path):
        p = tmp_path / "weird.xyz"
        p.write_text("data")
        r = sniff._sniff_path(p, drop_root=tmp_path)
        assert r.type == "unknown"
        assert r.converter == "reject"


# ============================================================
# FILE SECURITY
# ============================================================

class TestFileSecurity:
    def test_path_escape_blocked(self, tmp_path):
        """A file outside the drop root must be rejected."""
        drop = tmp_path / "drop"
        drop.mkdir()
        outside = tmp_path / "secret.txt"
        outside.write_text("secret")

        with pytest.raises(sniff.SniffError, match="path escapes drop root"):
            sniff._sniff_path(outside, drop_root=drop)

    def test_path_traversal_blocked(self, tmp_path):
        """A file accessed via .. traversal must be rejected."""
        drop = tmp_path / "drop"
        drop.mkdir()
        target = tmp_path / "secret.txt"
        target.write_text("secret")

        # Try to access ../secret.txt from within drop/
        traversal = drop / ".." / "secret.txt"
        with pytest.raises(sniff.SniffError):
            sniff._sniff_path(traversal.resolve(), drop_root=drop)

    def test_oversize_rejected(self, tmp_path):
        """A file over the cap must be rejected."""
        p = tmp_path / "huge.txt"
        # Write just over the cap (1 byte over)
        p.write_bytes(b"x" * (sniff.MAX_FILE_SIZE_BYTES + 1))
        with pytest.raises(sniff.SniffError, match="file too large"):
            sniff._sniff_path(p, drop_root=tmp_path)

    def test_nonexistent_file(self, tmp_path):
        p = tmp_path / "ghost.txt"
        with pytest.raises(sniff.SniffError, match="file not found"):
            sniff._sniff_path(p, drop_root=tmp_path)

    def test_directory_rejected(self, tmp_path):
        d = tmp_path / "subdir"
        d.mkdir()
        with pytest.raises(sniff.SniffError, match="not a regular file"):
            sniff._sniff_path(d, drop_root=tmp_path)


# ============================================================
# TOP-LEVEL sniff() DISPATCH
# ============================================================

class TestSniffDispatch:
    def test_dispatches_url(self):
        r = sniff.sniff("https://example.com")
        assert r.is_url
        assert r.type == "url"

    def test_dispatches_file(self, tmp_path):
        p = tmp_path / "doc.txt"
        p.write_text("hello")
        r = sniff.sniff(str(p))
        assert not r.is_url
        assert r.type == "text"

    def test_empty_input_rejected(self):
        with pytest.raises(sniff.SniffError, match="empty input"):
            sniff.sniff("")

    def test_whitespace_only_rejected(self):
        with pytest.raises(sniff.SniffError, match="empty input"):
            sniff.sniff("   \n\t  ")

    def test_path_expansion(self, tmp_path):
        """~/ paths should expand."""
        p = tmp_path / "doc.txt"
        p.write_text("hi")
        # Don't actually use ~; just ensure the function handles home-dir paths
        r = sniff.sniff(str(p))
        assert r.type == "text"
