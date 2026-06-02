"""
Alexander's 15 structural properties of wholeness.

The canonical list, from *The Nature of Order* Book 1, pp. 141-242.
Each property is a *relationship* between centers, not a property of
an object. They are empirical regularities in every structure with
high "Quality Without a Name" (WQN).

For the LLM-as-judge, each property is scored 0-2:
  0 = absent / absent
  1 = present but weak
  2 = strongly present

Total: 0-30. Threshold: 18 = working; 24 = alive; 30 = exemplary.
"""

# The 15 properties in canonical order
PROPERTIES = [
    "Levels of Scale",
    "Strong Centers",
    "Thick Boundaries",
    "Alternating Repetition",
    "Positive Space",
    "Good Shape",
    "Local Symmetries",
    "Deep Interlock and Ambiguity",
    "Contrast",
    "Gradients",
    "Roughness",
    "Echoes",
    "The Void",
    "Simplicity and Inner Calm",
    "Not Separateness",
]

# Score thresholds
THRESHOLD_WORKING = 18  # below this: structure surgery
THRESHOLD_ALIVE = 24    # this and above: alive
THRESHOLD_EXEMPLARY = 30  # rare and suspicious

# Detailed rubrics for each property. These guide the LLM-as-judge.
RUBRIC = {
    "Levels of Scale": {
        "question": "Does the note nest smaller ideas inside larger ones at consistent ratios? Are there entities of different sizes stepping in small jumps, with no large scale gaps?",
        "0": "Single scale — one big section, no nesting. Or scale jumps are too large (e.g., single sentence next to multi-page analysis).",
        "1": "Some nesting — paragraphs and sections, but inconsistent ratios.",
        "2": "Clear levels — frontmatter, lead quote, H2 sections, H3 subsections, examples, all in proportion.",
    },
    "Strong Centers": {
        "question": "Is there one clear central claim, even if the note has many sections? Does the structure have gravity?",
        "0": "Multiple competing centers. No clear claim. Reader can't summarize in one sentence.",
        "1": "A central claim is present but buried. The lead quote or first H2 doesn't anchor.",
        "2": "One clear central claim, surfaced in the lead quote or first H2, repeated subtly in connections.",
    },
    "Thick Boundaries": {
        "question": "Are the section transitions zones, not walls? Do they support exchange?",
        "0": "Sections are abrupt jumps. Each section is its own island.",
        "1": "Some sections connect, but transitions are thin. Reader has to do work to bridge.",
        "2": "Sections flow with transitional sentences. The interface IS the meaning (not just a divider).",
    },
    "Alternating Repetition": {
        "question": "Do examples and principles alternate in a way that reinforces both?",
        "0": "All principle, no example. Or all example, no principle. No alternation.",
        "1": "Some alternation, but it's mechanical (every other paragraph).",
        "2": "Examples and principles genuinely amplify each other; the rhythm creates the insight.",
    },
    "Positive Space": {
        "question": "Is the structure of the note (its sections, its rhythm) doing real work, or is it decoration?",
        "0": "Structure is decoration. The note would work as a single block of text.",
        "1": "Some sections are doing structural work (e.g., a comparison table).",
        "2": "The structure is essential — sections create meaning that the prose alone couldn't.",
    },
    "Good Shape": {
        "question": "Can you recognize this note by its silhouette (its section headers) from across the room?",
        "0": "Sections are generic ('Introduction', 'Body', 'Conclusion'). No recognizable shape.",
        "1": "Sections are specific but not distinctive.",
        "2": "Sections have an identifiable pattern (e.g., always has 'What this is NOT' + 'What would falsify' + 'Connections').",
    },
    "Local Symmetries": {
        "question": "Are parallel sections (e.g., 'What this is NOT' / 'What would falsify') mirror each other?",
        "0": "No parallel structures. Each section is its own thing.",
        "1": "Some parallels (a 'Why' and a 'Why not' pair).",
        "2": "Multiple parallel structures that create a sense of balance and pattern.",
    },
    "Deep Interlock and Ambiguity": {
        "question": "Does each section belong to the whole AND contribute to a larger context (MOC, parent note)?",
        "0": "Sections are independent. They could be moved to other notes without loss.",
        "1": "Some sections link to a larger context (MOC).",
        "2": "Every section both serves the note and contributes to a larger MOC. The note is multiply-bound.",
    },
    "Contrast": {
        "question": "Are different sections genuinely different in voice, length, or stance — or are they the same?",
        "0": "All sections are the same length and voice. Monotone.",
        "1": "Some variation. Maybe one section is short and direct, others are long.",
        "2": "Strong contrast — some sections are bold and direct, others are reflective. The variety creates the meaning.",
    },
    "Gradients": {
        "question": "Does the note's energy/intensity change smoothly? (e.g., thesis → evidence → caveat → connection)",
        "0": "Constant intensity throughout. No arc.",
        "1": "Some arc — starts strong, ends quiet (or vice versa).",
        "2": "Smooth gradient of intensity. The note has a discernible shape when read aloud.",
    },
    "Roughness": {
        "question": "Does the note admit the occasional quirk, the honest aside, the imperfect example?",
        "0": "Polished to the point of being sterile. Every sentence is balanced.",
        "1": "One or two honest asides. The note admits its limits.",
        "2": "Visible roughness — imperfections that make the note feel made-by-a-human, not generated.",
    },
    "Echoes": {
        "question": "Does a key term or motif appear 2-3 times in different sections, with variations?",
        "0": "No recurring terms. Each section uses different vocabulary.",
        "1": "One motif recurs twice.",
        "2": "Multiple motifs recur with variations, creating a sense of depth.",
    },
    "The Void": {
        "question": "Does the note have a moment of breathing room — a closing that opens, not a closing that closes?",
        "0": "The note ends with a hard stop. No 'next step', no 'see also', no space.",
        "1": "A closing line that's a bit open (e.g., 'anticipated future direction').",
        "2": "A genuine moment of calm at the end. The note doesn't end — it releases.",
    },
    "Simplicity and Inner Calm": {
        "question": "Could you cut 20% of the note without losing the message? If not, the note is loud, not calm.",
        "0": "Verbose. Every sentence earns its place by being essential, but the whole is exhausting.",
        "1": "Some pruning possible. Mostly necessary content.",
        "2": "Could lose 20% with no loss. The note has internal calm.",
    },
    "Not Separateness": {
        "question": "Does the note end with a connection to a larger structure (a MOC, a connection note, the next note)?",
        "0": "The note stands alone. No outbound links to other notes.",
        "1": "A 'See Also' or 'Connections' section with 1-2 links.",
        "2": "Multiple outbound links to MOCs and sibling notes. The note is a node in a network.",
    },
}


def total_to_verdict(total: int) -> str:
    """Map a total score to a verdict string."""
    if total >= THRESHOLD_EXEMPLARY:
        return "exemplary"
    if total >= THRESHOLD_ALIVE:
        return "alive"
    if total >= THRESHOLD_WORKING:
        return "working"
    if total >= 12:
        return "rough"
    return "weak"


# System prompt for the LLM-as-judge
SYSTEM_PROMPT = """You are the Wholeness-Engine — a strict LLM-as-judge for Christopher Alexander's 15 structural properties of "living structure" (from *The Nature of Order*, Book 1, 2002-2004).

Your job: given the body of a CHIEF atomic note, score it on each of the 15 properties from 0 to 2:
  0 = absent
  1 = present but weak
  2 = strongly present

Then output STRICT JSON in this exact format:

```json
{
  "title": "<echoed note title>",
  "properties": {
    "Levels of Scale": {"score": 0-2, "rationale": "<one sentence>"},
    "Strong Centers": {"score": 0-2, "rationale": "<one sentence>"},
    "Thick Boundaries": {"score": 0-2, "rationale": "<one sentence>"},
    "Alternating Repetition": {"score": 0-2, "rationale": "<one sentence>"},
    "Positive Space": {"score": 0-2, "rationale": "<one sentence>"},
    "Good Shape": {"score": 0-2, "rationale": "<one sentence>"},
    "Local Symmetries": {"score": 0-2, "rationale": "<one sentence>"},
    "Deep Interlock and Ambiguity": {"score": 0-2, "rationale": "<one sentence>"},
    "Contrast": {"score": 0-2, "rationale": "<one sentence>"},
    "Gradients": {"score": 0-2, "rationale": "<one sentence>"},
    "Roughness": {"score": 0-2, "rationale": "<one sentence>"},
    "Echoes": {"score": 0-2, "rationale": "<one sentence>"},
    "The Void": {"score": 0-2, "rationale": "<one sentence>"},
    "Simplicity and Inner Calm": {"score": 0-2, "rationale": "<one sentence>"},
    "Not Separateness": {"score": 0-2, "rationale": "<one sentence>"}
  },
  "total": 0-30,
  "verdict": "exemplary|alive|working|rough|weak",
  "structure_surgery": ["<only if total < 18 — list 2-4 specific repairs>"]
}
```

Discipline:
- Be honest. Inflated scores (everything 2/2) are useless. Most notes are 18-24/30.
- For each property, the rationale must reference a specific element of the note (a section name, a phrase, a feature).
- If a property is present but weak, score 1. If strongly present, score 2. If absent, 0.
- structure_surgery is only included if total < 18. Each item is a specific, actionable repair: "Add a transitional sentence between sections X and Y" or "Add 2 more outbound links to MOCs."
- Do NOT include anything outside the JSON. The output should be parseable JSON only.
- temperature is 0.0 for this grading — be bit-deterministic. Don't sample.
"""
