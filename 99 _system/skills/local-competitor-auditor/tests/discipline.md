# Discipline — local-competitor-auditor

The 5-floor quality check the audit itself must pass. The
auditor is a verifier — it must not become the thing it's
auditing (a generic content engine instead of a raw
intelligence producer).

## D1. No-interaction floor (the load-bearing rule)

**Verification:** the audit does NOT click into sub-pages,
fill forms, call the business, or DM.

```bash
# Per-competitor: count pages visited (should be 1: the homepage)
# Check the audit log for any click into a non-homepage URL
audit_log=~/.mavis/agents/mavis/memory/audit-logs/local-competitor-auditor.log

grep -cE "click.*ref=" "$audit_log"  # N competitors = N+1 (Google + N homepages)
# If > N+1, the audit deep-crawled (violation)

# Check for form fills or DMs (none should exist)
grep -cE "type|fill|submit|dm " "$audit_log"  # Should be 0
```

**Failure mode this catches:** the audit clicked into
sub-pages or filled forms. Read-only constraint violated.

## D2. One-homepage-only floor (per hard constraint #6)

**Verification:** each competitor is audited from one
homepage only. No sub-page clicks.

```bash
# Each competitor's section in the brief should reference 1 URL
for competitor in 1 2 3; do
  url_count=$(awk "/## Competitor $competitor/,/## Competitor $((competitor+1))/" "$brief" \
    | grep -cE "^\\*\\*URL:\\*\\*")
  if [ "$url_count" -ne 1 ]; then
    echo "FAIL: Competitor $competitor has $url_count URLs (should be 1)"
  fi
done
```

**Failure mode this catches:** the audit includes
sub-pages as separate URLs. One-homepage constraint
violated.

## D3. Friction filter applied floor

**Verification:** all 9 friction signals (Tier 1 + Tier 2)
are checked (PRESENT/ABSENT) per competitor.

```bash
for competitor in 1 2 3; do
  section=$(awk "/## Competitor $competitor/,/## Competitor $((competitor+1))/" "$brief")
  for signal in \
    "Phone-only after-hours" \
    "No 24/7 web chat" \
    "Call us for a quote" \
    "No instant-booking calendar" \
    "No service-area map" \
    "No online pricing" \
    "No reviews linked" \
    "No FAQ" \
    "Site is dated"; do
    echo "$section" | grep -qiF "$signal" \
      || echo "FAIL: Competitor $competitor missing friction signal: $signal"
  done
done
```

**Failure mode this catches:** a friction signal is skipped.
The 9-signal filter isn't fully applied.

## D4. Severity score present floor

**Verification:** each competitor has a 1-5 severity
score with the rubric's reasoning.

```bash
for competitor in 1 2 3; do
  section=$(awk "/## Competitor $competitor/,/## Competitor $((competitor+1))/" "$brief")
  score=$(echo "$section" | grep -oE "Severity score:\\*\\* [0-9]/5" | head -1)
  [ -z "$score" ] && echo "FAIL: Competitor $competitor missing severity score"
done
```

**Failure mode this catches:** a competitor is missing the
1-5 severity score. The operator's filter is incomplete.

## D5. No "Destroy or Defend" draft floor

**Verification:** the brief contains the "Destroy or
Defend" ANGLE (1 sentence) for the Scribe, not a DRAFT
post.

```bash
# The brief should have "Destroy or Defend" angle, not a full post
dd_section=$(awk '/### "Destroy or Defend" angle/,/^---/' "$brief")
# Length should be 1-2 sentences (the angle), not 180-280 chars (a post)
char_count=${#dd_section}
[ "$char_count" -gt 400 ] && echo "WARN: D&D section is $char_count chars (may be a full draft, not just an angle)"
```

**Failure mode this catches:** the auditor produced a full
"Destroy or Defend" draft (the Scribe's job). The auditor
stays as intelligence producer, not content producer.
