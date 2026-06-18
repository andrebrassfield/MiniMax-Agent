---
name: research-summary
description: Output format skill for research summaries. Load when producing briefing sections that require citations and structured synthesis.
version: 1.0.0
---

# Research Summary Output Format

## Purpose
Standardize how research findings are formatted for inclusion in daily briefings. Ensures consistent citation style, claim density, and readability.

## Output Template

```markdown
## [Topic Title]

**TL;DR**: [One-sentence summary of the key finding]

### Key Claims
1. **[Claim 1]** — [source: path/to/file.md#L10-L15]
2. **[Claim 2]** — [source: https://example.com/article#section]
3. **[Claim 3]** — [source: vault/notes/topic.md]

### Supporting Detail
[2-3 paragraphs synthesizing the evidence. No more than 200 words.]

### Open Questions
- [Question 1]
- [Question 2]
```

## Rules

1. **Every claim needs a source** — inline citation in square brackets
2. **Max 3 key claims per section** — forces prioritization
3. **TL;DR is mandatory** — reader should get the gist in one line
4. **Supporting detail is optional** — include only if evidence is complex
5. **Open questions encouraged** — signals where follow-up research is needed

## Usage

Load this skill when:
- Writing briefing sections from research
- Summarizing any source material for the daily briefing
- The output will be consumed by the writer agent

The writer agent (which may be the same agent in a later turn) should apply this format automatically when producing briefing content.