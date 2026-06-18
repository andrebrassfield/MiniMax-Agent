# Manual Detection — vault-daily-logger

The 100-byte threshold is the load-bearing detection logic. The
eval suite verifies the threshold is calibrated correctly.

## D1. The 100-byte threshold catches 1-paragraph manual dailies

**Setup:** An operator writes a manual daily with 1 paragraph (e.g.,
"Today I focused on the X-Content-Engine. The Scribe produced 3
drafts. I approved 1 and revised 1. The 3rd needs a hot-take fix
before posting."). Body content (excluding frontmatter) is ~180
bytes.

**Verification:** the skill halts and logs `skipped-manual-entry`.
The auto-generated daily is NOT generated.

**Failure mode this catches:** a threshold set too high (e.g., 500
bytes) would silently overwrite 1-paragraph manual dailies.

## D2. The 100-byte threshold catches the auto-generated stub itself

**Setup:** The auto-generated daily's body content (excluding
frontmatter) is ~1,200 bytes (the AUTO-GENERATED callout + 5
bullets + optional stubs + notes for the chief). The threshold
must be ≤ 1,200 bytes.

**Verification:** the threshold (default 100 bytes) is < 1,200 bytes.
The next cron run correctly identifies the file as auto-generated
(by the body-size check, not the tags check) and skips it.

**Failure mode this catches:** a threshold set too low (e.g., 50
bytes) would still detect the auto-generated daily correctly, but
a threshold set ABOVE 1,200 bytes would let the cron overwrite
previous auto-generated dailies with newer ones (silent loss of
historical record).

## D3. The 100-byte threshold is calibration-tunable

**Setup:** If the operator's manual dailies are consistently 50
bytes (e.g., a 1-line summary), the threshold needs to be lower.
If they're consistently 500+ bytes, the threshold is fine.

**Verification:** the threshold is exposed as a parameter in the
Inputs table of SKILL.md. The cron can be reconfigured without
code changes.

**Failure mode this catches:** a hard-coded threshold that doesn't
match the operator's actual writing style.

## D4. Body extraction strips frontmatter correctly

**Setup:** A daily has a frontmatter block (between two `---`
markers) and body content after it.

**Verification:**
```python
import re
content = open('01 Daily/2026-06-17.md').read()
m = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
body = content[m.end():] if m else content
print(len(body.strip()))
# Expected: body size in bytes (excluding frontmatter)
```

**Failure mode this catches:** a regex that doesn't strip the
frontmatter correctly. The body-size check would include the
frontmatter in the count, potentially exceeding the threshold and
false-positively halting on a "manual-looking" file that's actually
auto-generated.

## D5. The check uses byte size, not character count

**Setup:** A daily has multi-byte UTF-8 characters (emoji, CJK).
The Python `len()` on a string returns character count; the file
size in bytes is `os.path.getsize()` or the file content's
`len(body.encode('utf-8'))`.

**Verification:** the body-size check uses byte size (so a daily
with 100 emoji characters is 400 bytes, well over the 100-byte
threshold).

**Failure mode this catches:** a check that uses character count
might under-count multi-byte characters, missing the threshold on
a daily that's actually 100+ bytes.

## D6. The threshold is robust to whitespace

**Setup:** A manual daily is just whitespace + the AUTO-GENERATED
marker. Body size is 0 bytes (or a few bytes after stripping).

**Verification:** the body-size check strips whitespace before
counting (`body.strip()`). A whitespace-only file is detected as
empty and treated as auto-generatable.

**Failure mode this catches:** a daily that the operator opened
and saved without writing anything (leaving whitespace + the
template's frontmatter) being treated as "manual" and blocking
the cron. The cron should generate a real daily in that case.
