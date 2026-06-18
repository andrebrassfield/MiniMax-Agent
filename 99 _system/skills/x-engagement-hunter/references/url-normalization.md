# URL Normalization — x-engagement-hunter

Canonical URL forms for x.com. The chief normalizes BEFORE
navigation. The mavis browser tool receives a single canonical
form.

## Accepted input formats

| Input | Canonical output | Notes |
|---|---|---|
| `@<handle>` | `https://x.com/<handle>` | shorthand |
| `<handle>` (no @) | `https://x.com/<handle>` | handle only, no @ |
| `https://twitter.com/<handle>` | `https://x.com/<handle>` | twitter.com → x.com |
| `https://x.com/<handle>` | as-is | already canonical |
| `https://x.com/<handle>/status/<id>` | as-is | specific post |
| `https://x.com/<handle>/with_replies` | `https://x.com/<handle>` | reply tab → default tab |
| `https://x.com/<handle>/likes` | `https://x.com/<handle>` | likes tab → default tab |
| `https://x.com/<handle>/media` | `https://x.com/<handle>` | media tab → default tab |

## Normalization function (the deterministic layer)

```bash
normalize_url() {
  local input="$1"
  # Strip whitespace
  input=$(echo "$input" | tr -d '[:space:]')
  # Handle shorthand @handle
  [[ "$input" =~ ^@ ]] && input="${input#@}"
  # Add https:// if missing and contains x.com or twitter.com
  if [[ "$input" =~ ^(x\.com|twitter\.com) ]]; then
    input="https://$input"
  fi
  # Strip query/fragment
  input="${input%%\?*}"
  input="${input%%#*}"
  # twitter.com → x.com
  input="${input//twitter.com/x.com}"
  # Strip tab suffixes (with_replies, likes, media, highlights)
  input="${input%/with_replies}"
  input="${input%/likes}"
  input="${input%/media}"
  input="${input%/highlights}"
  # Strip trailing slash
  input="${input%/}"
  echo "$input"
}
```

## Output assertions (the test cases)

```bash
# Each must equal the canonical form
assert "https://x.com/NickHuber" "$(normalize_url '@NickHuber')"
assert "https://x.com/NickHuber" "$(normalize_url 'https://twitter.com/NickHuber')"
assert "https://x.com/NickHuber" "$(normalize_url 'https://x.com/NickHuber/with_replies')"
assert "https://x.com/NickHuber/status/1234567890" \
       "$(normalize_url 'https://x.com/NickHuber/status/1234567890')"
assert "https://x.com/NickHuber" "$(normalize_url 'https://x.com/NickHuber?lang=en')"
```

## URL components (for the snapshot)

After navigation, the snapshot must show:
- Profile page: `<handle>` in the header, topmost post visible
- Post page: post text + author handle in main content area

If neither renders, HALT (H4: target post not isolated).
