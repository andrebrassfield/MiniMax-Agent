# Audit Discipline — client-pov-tracker

The 5-floor quality check the audit itself must pass. The
roadmap is a client deliverable — it must not become the
thing it's auditing (a generic pitch deck instead of a
client-specific POV).

## D1. No-fabrication floor (the load-bearing element)

**Verification:** every claim in the roadmap has source
citation in the Appendix.

```bash
# Section 1 (Friction): every signal must cite a local-audit brief
friction=$(awk '/^## 1\. The Friction/,/^## 2\./' "$roadmap")
echo "$friction" | grep -E "Tier [123]" | grep -v "local-audit\|brief" \
  && echo "WARN: friction signal without brief citation"

# Section 3 (Target ROI): every dollar amount must cite a source
roi=$(awk '/^## 3\. Target ROI/,/^## 4\./' "$roadmap")
echo "$roi" | grep -oE "\\\$[0-9,]+" | sort -u | while read amount; do
  echo "$roi" | grep -F "$amount" | grep -qE "whitepaper|client" \
    || echo "FAIL: $amount lacks source citation"
done

# Section 2 (Agentic Standard): every criterion must be applied specifically
agentic=$(awk '/^## 2\. The Agentic Standard/,/^## 3\./' "$roadmap")
echo "$agentic" | grep -E "^- \\*\\*[A-Z]" | grep -E "specific|FSM|ServiceTitan|Jobber|Housecall|FieldEdge" \
  || echo "WARN: Agentic Standard not applied to specific FSM"
```

**Failure mode this catches:** the roadmap has claims
without source citations. The no-fabrication constraint
is violated.

## D2. Client-specific floor (NOT a generic pitch deck)

**Verification:** the roadmap names the client's name, city,
niche, and FSM. Generic language ("we help businesses")
indicates a generic deck, not a POV.

```bash
# Frontmatter must have client-specific data
grep -qE "^client: [A-Z]" "$roadmap" || echo "FAIL: frontmatter missing client name"
grep -qE "^city: [A-Z]" "$roadmap" || echo "FAIL: frontmatter missing city"
grep -qE "^niche: [A-Za-z]" "$roadmap" || echo "FAIL: frontmatter missing niche"

# Section 2 must name a specific FSM
agentic=$(awk '/^## 2\. The Agentic Standard/,/^## 3\./' "$roadmap")
echo "$agentic" | grep -qiE "service titan|jobber|housecall|fieldedge|shopify" \
  || echo "FAIL: Section 2 doesn't name a specific FSM"
```

**Failure mode this catches:** the roadmap is a generic
pitch deck (no client name, city, niche, FSM). The POV is
not client-specific.

## D3. ROI math is anchored floor

**Verification:** the Target ROI table references the
whitepaper §4 math defaults (or cites client-provided
data).

```bash
# Section 3 should reference whitepaper §4 or client-specific data
roi=$(awk '/^## 3\. Target ROI/,/^## 4\./' "$roadmap")
echo "$roi" | grep -qiE "whitepaper.*§4|client.provided|client.specific|capture assumption|payback" \
  || echo "WARN: ROI table doesn't reference whitepaper §4 math or client data"
```

**Failure mode this catches:** the ROI math is invented
(not anchored to whitepaper §4 or client data). The
no-fabrication constraint is violated.

## D4. Blueprint-to-friction mapping floor

**Verification:** every Tier 1 friction has a Blueprint
phase that addresses it.

```bash
# Extract Tier 1 frictions
tier1=$(awk '/### Tier 1/,/### Tier 2/' "$roadmap" | grep -oE "^[*-] .*" | head -10)

# Extract Phase 2 (Voice Path) — addresses all 4 Tier 1 frictions
blueprint=$(awk '/^## 4\. The Blueprint/,/^## 5\./' "$roadmap")
echo "$blueprint" | grep -qE "Phase 2.*Voice Path" \
  || echo "FAIL: Blueprint missing Phase 2 (Voice Path)"

# For trades-only clients, Phase 3 (Inventory/Ops) is optional
# For e-com clients, Phase 3 is required
niche=$(grep "^niche:" "$roadmap" | head -1)
if echo "$niche" | grep -qiE "shopify|tiktok|amazon|e-com"; then
  echo "$blueprint" | grep -qE "Phase 3.*Inventory" \
    || echo "FAIL: e-com client missing Phase 3 (Inventory/Ops Path)"
fi
```

**Failure mode this catches:** a Tier 1 friction has no
Blueprint phase. The install is incomplete.

## D5. Mavis territory floor (no cross-team work)

**Verification:** the roadmap does not include work for
other agents (Hermes, OpenClaw, Socratic).

```bash
# No references to other agent's territory
forbidden='~/\.hermes|~/\.openclaw|~/\.gbrain|~/\.hermes-evolution'
grep -qE "$forbidden" "$roadmap" && echo "FAIL: roadmap references other agent's tree"

# Mavis territory: only references Clients/, X-Content-Engine/, Mavis EA Design/, 02 Notes/, 01 Daily/
allowed='03 Projects/Clients|03 Projects/X-Content-Engine|03 Projects/Mavis EA Design|02 Notes|01 Daily'
echo "$roadmap" | grep -oE "03 Projects/[A-Za-z _-]+|02 Notes/[A-Za-z _-]+|01 Daily/[A-Za-z _-]+" \
  | sort -u | while read ref; do
    if ! echo "$ref" | grep -qE "$allowed"; then
      echo "WARN: roadmap references surface outside Mavis territory: $ref"
    fi
  done
```

**Failure mode this catches:** the roadmap references work
in other agents' trees. Mavis territory rule violation.
