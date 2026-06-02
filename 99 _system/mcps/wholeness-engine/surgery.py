"""
Structure surgery — recommendations for notes below the 18/30 threshold.

When a note scores below 18, the Wholeness-Engine emits a `structure_surgery`
list: 2-4 specific, actionable repairs. This module formats and validates
the surgery plan.
"""

from typing import Optional


def validate_surgery(surgery: list[str]) -> list[str]:
    """Validate a surgery plan. Returns cleaned list (empty if invalid)."""
    if not isinstance(surgery, list):
        return []
    cleaned = []
    for item in surgery:
        if isinstance(item, str) and len(item.strip()) > 0:
            cleaned.append(item.strip())
    return cleaned[:6]  # Cap at 6 items


def format_surgery(surgery: list[str], total: int) -> str:
    """Format a surgery plan for human-readable display."""
    if total >= 18 or not surgery:
        return ""
    lines = [
        "",
        f"⚠️  STRUCTURE SURGERY REQUIRED (score: {total}/30, below 18 threshold)",
        "=" * 60,
    ]
    for i, item in enumerate(surgery, 1):
        lines.append(f"  {i}. {item}")
    lines.append("")
    lines.append("Apply each repair, then re-run `mavis-vault wholeness <path>` to verify.")
    return "\n".join(lines)


def surgery_template(properties: dict) -> list[str]:
    """Generate a default surgery plan from the lowest-scoring properties.

    Used when the LLM didn't emit a surgery plan but the score is below 18.
    """
    # Find the bottom 3 properties
    sorted_props = sorted(
        properties.items(),
        key=lambda x: (x[1].get("score", 0), x[0]),
    )
    repairs = []
    for name, info in sorted_props[:3]:
        if info.get("score", 0) >= 1:
            continue  # Skip properties that are already OK
        repair = generate_repair(name, info)
        if repair:
            repairs.append(repair)
    return repairs


def generate_repair(prop_name: str, info: dict) -> Optional[str]:
    """Generate a specific repair for a low-scoring property."""
    template_repairs = {
        "Levels of Scale": "Add an H3 subsection or break long paragraphs into smaller, named ideas.",
        "Strong Centers": "Add or strengthen a lead quote that anchors the central claim in one sentence.",
        "Thick Boundaries": "Add transitional sentences between sections that explain how they relate.",
        "Alternating Repetition": "Add a concrete example after each principle. The example should illustrate, not just restate.",
        "Positive Space": "Use a table, list, or other structural element to make the structure do real work.",
        "Good Shape": "Use distinctive section headers — replace generic 'Introduction' with the specific question you're answering.",
        "Local Symmetries": "Add a 'What this is NOT' section to mirror the 'What this is' structure.",
        "Deep Interlock and Ambiguity": "Add 2-3 outbound links to MOCs or sibling notes in the 'Connections' section.",
        "Contrast": "Vary section lengths and voices. One section should be short and bold; another should be long and reflective.",
        "Gradients": "Build a clear arc: thesis → evidence → caveat → connection. Don't start and end at the same intensity.",
        "Roughness": "Add one honest aside — a place where the note admits its limits or surprises itself.",
        "Echoes": "Pick 2-3 key terms and use them 2-3 times each in different sections, with variations.",
        "The Void": "Replace the closing with a moment of breathing — 'Anticipated future direction' or a question that opens.",
        "Simplicity and Inner Calm": "Cut 20% of the note. If you can't, the note is loud, not calm. Find the redundant 20%.",
        "Not Separateness": "Add a 'Connections' section with 3+ outbound links to MOCs and related notes.",
    }
    return template_repairs.get(prop_name)
