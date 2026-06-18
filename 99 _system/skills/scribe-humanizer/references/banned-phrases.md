# Banned Phrases — Stage 1 (Fluff Purge)

12 categories of AI-flavored phrases the Humanizer flags. Case-insensitive
regex, with word boundaries to avoid false positives. Match the FULL phrase,
not just a substring.

## The 12 categories

```
1.  \bdive\s+into\b | \bdelve\s+into\b | \bexplore\s+the\s+world\s+of\b
2.  \bin\s+today'?s\s+(fast-paced|ever-evolving|modern|rapidly\s+changing)\s+(world|landscape|era)\b
    | \bin\s+this\s+day\s+and\s+age\b | \bin\s+the\s+ever-evolving\s+landscape\b
3.  \bit'?s\s+not\s+just\s+about\s+\w+,?\s+it'?s\s+about\s+\w+\b     # the false-dialectic tic
4.  \blet'?s\s+(unpack|break\s+this\s+down|explore|dive\s+in)\b
5.  \bharness\s+the\s+power\s+of\b | \bunlock\s+(the\s+potential\s+of|your\s+)\b
    | \bunleash\b | \bsupercharge\b | \bsuper-charge\b
6.  \bthe\s+truth\s+is\b | \bthe\s+reality\s+is\b | \bhere'?s\s+the\s+thing\b
7.  \bgame[\s-]?changer\b | \bgame[\s-]?changing\b | \brevolutionary\b | \bparadigm\s+shift\b
8.  \bat\s+the\s+end\s+of\s+the\s+day\b | \bin\s+conclusion\b | \bthat'?s\s+a\s+wrap\b | \bto\s+wrap\s+up\b
9.  \bseamlessly\b | \beffortlessly\b | \bfrictionlessly\b          # AI's favorite adverb cluster
10. \belevate\s+your\b | \btake\s+it\s+to\s+the\s+next\s+level\b | \bgame[\s-]?changer\b
11. \bnavigate\s+the\s+complexities\b | \bin\s+the\s+world\s+of\b | \bin\s+the\s+realm\s+of\b
12. \bI'?m\s+excited\s+to\s+(announce|share|introduce)\b | \bI'?m\s+thrilled\s+to\s+(share|announce)\b
    | \bI\s+wanted\s+to\s+take\s+a\s+moment\s+to\b
```

## The 2 meta-rules

These are caught by Stage 1 even if not in the 12 list:

- **Em-dash filler:** "— and that's why" / "— which means" / "— leading to"
  (em-dashes used as conjunction-tics rather than real parenthetical asides)
- **Medium-article openers:** any sentence that could open a Medium
  article ("In this post, I'll explore..." / "Let me tell you a story..."
  / "Here's what I learned...")

## Match output format

For each match, write:

```markdown
### Match N — "[banned phrase]" in Draft K

**Original:** "[verbatim 1-2 sentence context around the match]"
**Suggested fix:** "[proposed rewrite in persona voice — staccato, no AI fluff, hard numbers]"
**Rationale:** [1 sentence on why this is AI-flavored and what the persona would do instead]
```

## Discipline

Stage 1 is mechanical. Don't editorialize. Don't suggest rewrites that go
beyond fixing the match. The fix for "dive into" is not "rewrite the whole
sentence" — it's "replace 'dive into' with the verb the sentence actually
meant." If the rewrite requires restructuring the sentence, that's Stage 2
territory.

The cross-reference check: the persona file (`agents/persona.md`) has its
own banned-phrases list, less rigorous than this one. The Humanizer's list
is the load-bearing version. If the two diverge, the Humanizer's list wins.
