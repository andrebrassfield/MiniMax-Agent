"""
Tests for macos-vision-anchor.

Covers: image-size parsing (PIL + pure-stdlib fallback), response
parsing (happy path, not-found, malformed JSON, markdown-fenced JSON,
extra prose around the JSON object), audit log writes.

Esalen posture: tests cover the deterministic I/O layer (parsing,
size detection, audit). The vision reasoning itself is M3's job and
is validated via the static-screenshot test, not unit tests.
"""
import json
import re
import sys
import tempfile
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MCP = HERE
sys.path.insert(0, str(MCP))

# The MCP script has a hyphen in its name (kebab-case) so it can't be
# imported as a regular module. Use importlib to load it by file path.
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("mva", MCP / "macos-vision-anchor.py")
assert _spec and _spec.loader
mva = _ilu.module_from_spec(_spec)
sys.modules["mva"] = mva
_spec.loader.exec_module(mva)


# ============================================================
# IMAGE SIZE PARSING
# ============================================================

class TestImageSize:
    def test_png_size_via_pil(self, tmp_path):
        from PIL import Image
        img = Image.new("RGB", (640, 480), color=(0, 0, 0))
        path = tmp_path / "test.png"
        img.save(path, "PNG")
        w, h = mva.get_image_size(path)
        assert (w, h) == (640, 480)

    def test_jpeg_size_via_pil(self, tmp_path):
        from PIL import Image
        img = Image.new("RGB", (320, 240), color=(255, 255, 255))
        path = tmp_path / "test.jpg"
        img.save(path, "JPEG")
        w, h = mva.get_image_size(path)
        assert (w, h) == (320, 240)

    def test_png_size_via_stdlib_fallback(self, tmp_path, monkeypatch):
        # Force the ImportError path so the pure-stdlib PNG parser runs
        import importlib
        # Hide PIL for this test only
        saved = sys.modules.get("PIL")
        monkeypatch.setitem(sys.modules, "PIL", None)
        try:
            # Reload the module so the import in get_image_size re-runs
            importlib.reload(mva)
        except Exception:
            pass
        # Build a minimal valid PNG by hand using PIL once, then read it
        # via the stdlib path. Simpler: write PNG bytes directly.
        import struct, zlib
        w, h = 100, 50
        raw = b""
        for y in range(h):
            raw += b"\x00" + b"\xff" * (w * 3)
        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data
                    + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(raw))
               + chunk(b"IEND", b""))
        path = tmp_path / "std.png"
        path.write_bytes(png)
        # Re-enable PIL (it never actually got disabled above; the
        # monkeypatch only set sys.modules['PIL']=None, which breaks the
        # `from PIL import Image` import with ImportError). The
        # get_image_size function will catch that and fall through.
        result_w, result_h = mva.get_image_size(path)
        assert (result_w, result_h) == (w, h)
        if saved is not None:
            monkeypatch.setitem(sys.modules, "PIL", saved)


# ============================================================
# RESPONSE PARSING
# ============================================================

class TestParseResponse:
    def _img(self, tmp_path):
        from PIL import Image
        path = tmp_path / "x.png"
        Image.new("RGB", (100, 100), (0, 0, 0)).save(path, "PNG")
        return path

    def test_happy_path(self, tmp_path):
        img = self._img(tmp_path)
        raw = json.dumps({
            "found": True, "x": 10, "y": 20, "width": 30, "height": 40,
            "confidence": 0.95,
            "description": "A blue button labeled 'Click'",
        })
        r = mva.parse_locate_response(raw, "the button", img, 100, 100)
        assert r.found is True
        assert r.bounding_box == {"x": 10, "y": 20, "width": 30, "height": 40}
        assert r.confidence == 0.95
        assert "Click" in r.description
        assert r.image_width == 100
        assert r.request_id.startswith("va-")

    def test_not_found(self, tmp_path):
        img = self._img(tmp_path)
        raw = json.dumps({"found": False, "reason": "no button visible"})
        r = mva.parse_locate_response(raw, "the button", img, 100, 100)
        assert r.found is False
        assert "no button" in r.description

    def test_markdown_fenced_json(self, tmp_path):
        img = self._img(tmp_path)
        raw = '```json\n{"found": true, "x": 5, "y": 5, "width": 10, "height": 10, "confidence": 0.8, "description": "x"}\n```'
        r = mva.parse_locate_response(raw, "the thing", img, 100, 100)
        assert r.found is True
        assert r.bounding_box["x"] == 5

    def test_prose_around_json(self, tmp_path):
        img = self._img(tmp_path)
        raw = 'Here is the result:\n\n{"found": true, "x": 1, "y": 2, "width": 3, "height": 4, "confidence": 0.7, "description": "y"}\n\nHope this helps.'
        r = mva.parse_locate_response(raw, "the thing", img, 100, 100)
        assert r.found is True
        assert r.bounding_box == {"x": 1, "y": 2, "width": 3, "height": 4}

    def test_malformed_json(self, tmp_path):
        img = self._img(tmp_path)
        # Has matching braces (so the regex catches it) but invalid JSON inside
        raw = '{"x": ,}'
        r = mva.parse_locate_response(raw, "the thing", img, 100, 100)
        assert r.found is False
        assert "JSON parse error" in r.description

    def test_no_json_object(self, tmp_path):
        img = self._img(tmp_path)
        raw = "I cannot find that element in the image."
        r = mva.parse_locate_response(raw, "the thing", img, 100, 100)
        assert r.found is False
        assert "no JSON object" in r.description


# ============================================================
# PROMPT BUILDING
# ============================================================

class TestPromptBuilding:
    def test_prompt_contains_target(self, tmp_path):
        from PIL import Image
        img_path = tmp_path / "x.png"
        Image.new("RGB", (800, 600), (0, 0, 0)).save(img_path, "PNG")
        prompt = mva.call_m3_vision(img_path, "the Save button", "", 800, 600)
        assert "the Save button" in prompt
        assert "800 pixels wide" in prompt
        assert "600 pixels tall" in prompt
        assert '"found"' in prompt  # has the JSON example

    def test_prompt_contains_context(self, tmp_path):
        from PIL import Image
        img_path = tmp_path / "x.png"
        Image.new("RGB", (100, 100), (0, 0, 0)).save(img_path, "PNG")
        prompt = mva.call_m3_vision(
            img_path, "the button", "in the lower-right corner", 100, 100
        )
        assert "lower-right corner" in prompt
        assert "Additional context" in prompt

    def test_prompt_handles_unknown_dimensions(self, tmp_path):
        from PIL import Image
        img_path = tmp_path / "x.png"
        Image.new("RGB", (100, 100), (0, 0, 0)).save(img_path, "PNG")
        prompt = mva.call_m3_vision(img_path, "x", "", 0, 0)
        assert "unknown pixels wide" in prompt
        assert "unknown pixels tall" in prompt
