---
title: 5 Biomarkers Lead Magnet — Visualization & Design Spec
type: design-spec
asset_id: lm-5biomarkers-visualization-v1
status: DRAFT — pending visual designer review
date: 2026-06-26
target_format: 9-page PDF (cover + 7 content + back), 1080x1350px pages, dark theme
voice_locked: source/2026-06-23-brand-voice.md
palette_locked: per "Carousel 1 — 5 Biomarkers" review-checklist (dark navy + teal/cyan)
---

# Visualization & Design Spec — 5 Biomarkers Lead Magnet PDF

## Brand palette

Aligned with `assets/visual/carousel-1-5biomarkers/` (existing visual system).

> **Production rule (Dre polish flag):** Render with these EXACT hex values. Do not approximate. The PDF must match the carousel visual system exactly so brand recognition carries across surfaces.

| Role | Color | Hex | Usage |
|---|---|---|---|
| Primary background | Deep charcoal | `#0A1628` | Page background (replaces pure black — easier on eyes for long reads) |
| Secondary background | Navy | `#0F2138` | Cards, tables, alternating sections |
| Accent — primary | Teal / cyan | `#00B4D8` | Headers, key callouts, "I'm still in this process" anchor |
| Accent — secondary | Burnt orange | `#E76F51` | Red flags only (uses Sparingly — this color means "warning") |
| Accent — tertiary | Soft amber | `#F4A261` | Yellow flags only (caution / monitor) |
| Text — primary | Off-white | `#F1FAEE` | Body text, headlines |
| Text — secondary | Light gray | `#A8B2BD` | Captions, footnotes, disclaimers |
| Text — inverted | Deep charcoal | `#0A1628` | Text on light backgrounds |

## Typography

| Role | Font | Size | Weight | Notes |
|---|---|---|---|---|
| Cover headline | Inter / Söhne | 48–60pt | Bold | Sentence case (brand voice preference) |
| Section header | Inter | 32pt | SemiBold | Sentence case |
| Subheader | Inter | 22pt | Medium | Sentence case |
| Body | Inter | 16pt | Regular | Line height 1.6 for readability |
| Caption / footnote | Inter | 12pt | Regular | Lower opacity (0.7) |
| Pull quote / hook | Inter | 24pt | Light italic | Used sparingly, max 1 per page |

All text sentence case — never Title Case except proper nouns. This is a brand voice rule per `assets/visual/carousel-1-5biomarkers/review-checklist.md`.

## Page structure (9 pages)

### Page 1 — Cover

**Composition:**
- Centered headline (Inter Bold, ~52pt) at top third
- Subheadline (Inter Medium, ~24pt) below
- Visual element: schematic of the 5 biomarker icons arranged in a horizontal row (HRV waveform + TyTron pattern + tryptase test tube + inflammation gauge + mineral pill)
- "I'm still in this process" anchor at bottom in teal accent
- Disclaimer line in small caps, light gray, at very bottom
- Andre Brassfield · Dose of Proof · https://doseofproof.substack.com/

**Visual notes:**
- Icons are flat geometric, line-art style — no photography, no human face
- Background gradient: deep charcoal at top fading to navy at bottom

### Page 2 — Disclaimer + Section 1 (The Problem with Fragmented Data)

**Composition:**
- Compliance disclaimer block in a subtle box at the very top (light gray, smaller)
- Section header in teal
- 4 paragraphs of body text in off-white
- Visual element: simplified "whack-a-mole" diagram showing fragmented specialists (4 separate icons) vs unified terrain mapping (1 connected system). The contrast is the message.

**Visual notes:**
- The whack-a-mole diagram uses muted gray for the fragmented icons and teal for the unified system — visual reinforcement that integration is the point

### Page 3 — The Vicious Loop Diagram

**Composition:**
- Centered diagram showing the loop:
  - Unstable upper neck → vagus irritation → mast cells fire → inflammation + guarding → more instability → repeat
- Circular arrows, each labeled
- Color coding: teal for mechanical (neck), orange for nerve (vagus), red-orange for mast cell, amber for inflammation, back to teal for instability
- One sentence below: "Every symptom downstream. One driver upstream."

**Visual notes:**
- This is the conceptual heart of the guide. Spend design effort here. Use the brand palette to make the loop feel inevitable but solvable.

### Page 4 — Section 2 opener + Biomarker 1 + Biomarker 2

**Composition:**
- Section 2 header
- Two biomarker cards side-by-side (or stacked on smaller pages)
- Each card has:
  - Biomarker number badge (teal circle)
  - Name + subtitle
  - 3-bullet "What / Why / How I tracked" summary
  - Trend sparkline (HRV going up, TyTron pattern going from asymmetric to straight)
- Footer micro-disclaimer

**Visual notes:**
- Sparklines are real-looking, not aspirational. They show the up-and-down of real data, not a smooth curve. Authenticity is the brand.

### Page 5 — Biomarker 3 + Biomarker 4

**Composition:**
- Same card structure as Page 4
- Biomarker 3 card includes tryptase level visual (bar showing baseline vs flare)
- Biomarker 4 card includes dual-axis chart: blood markers (ESR/CRP lines) + subjective score (guarding line) over 6 months. Both lines drop together.

**Visual notes:**
- The dual-axis chart is the most important visual in the guide — it shows the loop closing. Spend design effort here.

### Page 6 — Biomarker 5 + Section 3 opener (Terrain Layers)

**Composition:**
- Biomarker 5 card (Vitamin D + Magnesium)
- Section 3 header
- Layered terrain diagram: stack of 5 layers (minerals, redox, mold context, nervous system, connective tissue) — the deeper layers are the ones standard labs miss

**Visual notes:**
- The terrain stack is metaphor + literal. Make the layers visually distinct so a reader can see that "going deeper" reveals more.

### Page 7 — Section 4 (Build Your Own Proof System)

**Composition:**
- Daily protocol table (compact, 3 columns: morning / throughout day / evening)
- Weekly review checklist (5 items)
- Periodic labs calendar (quarterly)
- Pointer to the printable one-page template (separate file)

**Visual notes:**
- Tables are dense but readable. Use the navy secondary background for table headers.

### Page 8 — Section 5 (What Comes Next) + soft funnel

**Composition:**
- Section 5 text body
- Soft funnel block: Substack link + early-bird notice + community space (when open)
- Telehealth directory pointer: text-only, observational, no specific vendor promotion ("the Substack has a vetted directory of telehealth providers who can order the right labs")

**Visual notes:**
- Soft funnel is teal-accented, not orange. The orange is reserved for red flags.
- No buttons that look like e-commerce CTAs. This is observational educational content.

### Page 9 — Back cover / closing

**Composition:**
- "I'm still in this process" anchor (teal, large)
- Andre Brassfield · Dose of Proof
- Substack URL
- Compliance footer (full text, all-caps, smaller)
- Page number "9 / 9"

**Visual notes:**
- End on the anchor. The honesty is the brand.

## Chart specifications

### HRV trend line
- X-axis: dates (last 90 days)
- Y-axis: HRV (20-80 range)
- Single line, teal, 2pt stroke
- Annotations: "first Blair adjustment" / "mineral repletion complete" / "stable period"
- Background: navy secondary
- No gridlines (clean look)

### TyTron pattern comparison
- Two side-by-side thermal pattern diagrams
- Left: asymmetric / wavy (red-orange accent for problem areas)
- Right: near-symmetric / straight (teal accent)
- Single sentence below: "Direct visual feedback on whether the mechanical driver is being addressed."

### Tryptase bar comparison
- Two bars: baseline / flare
- Y-axis: tryptase ng/mL
- Colors: navy (baseline), red-orange (flare)
- Annotations: "Baseline tryptase often normal" / "Catch it during a flare"

### ESR/CRP + Guarding score dual-axis
- X-axis: months (6-month window)
- Y-axis (left): ESR/CRP mg/L (0-30 range)
- Y-axis (right): subjective guarding score (1-10)
- Two lines: teal (blood markers) + amber (subjective)
- Key annotation: "Both drop together — the loop is closing"

### Terrain stack
- 5 layers, stacked vertically
- Top layer (most superficial): "Symptoms" — light gray
- Layer 2: "Standard labs" — light gray
- Layer 3: "Specialist imaging (TyTron, X-ray)" — amber
- Layer 4: "Biomarkers (this guide)" — teal
- Bottom layer (deepest): "Terrain (minerals, redox, mold, nervous system)" — teal, larger
- Annotation: "Most standard workups stop at layer 2. The proof starts at layer 4."

## Table specifications

### Daily tracking table
- Header row (navy background, off-white text): Date / Morning HRV / Guarding (1-10) / Flushing count / Heat count / Sleep (1-10) / Notes
- Body rows: alternating charcoal/navy backgrounds
- Empty template ships with 14 blank rows (2 weeks)

### Weekly review table
- Header row: Week of / HRV trend / Subjective trend / Notable changes / Action items
- Empty template ships with 8 blank rows (2 months)

### Quarterly labs table
- Header row: Date / Lab / Result / Reference range / Notes
- Empty template ships with 12 blank rows (3 years)

## Personal data visualization safety notes

The guide includes real-looking personal data visualizations (HRV trends, biomarker bars). Safety notes for any version that ships:

- All visualizations use ANONYMIZED or SYNTHETIC-LOOKING data patterns, not literal screenshots of personal health records
- No identifying information in chart labels (no patient name, no date of birth, no medical record number)
- No specific dates that could re-identify (use "month 1, month 2, month 3" or relative dates, not "April 15, 2026")
- No medication names or dosages anywhere in visuals
- No specific clinic names, physician names, or geographic identifiers beyond what's already in the brand voice doc (which is public-facing)

## File deliverables

For visual designer:
- `5-biomarkers-guide.md` — full text source
- `5-biomarkers-visualization-spec.md` — this document
- `5-biomarkers-tracking-template.md` — printable template to be rendered as one-page PDF
- `assets/visual/carousel-1-5biomarkers/` — existing visual system to align with (do not reinvent the palette)

## Production notes

- Tooling: Mermaid + dark theme OR static SVG via Figma/Illustrator
- PDF export: 1080×1350 portrait, dark background
- File size target: <5MB (Substack email attachment limits)
- Font embedding: required (Inter is open source; ship embedded)
- Accessibility: alt text for all charts and diagrams

---

*End of design spec. Aligned with `assets/visual/carousel-1-5biomarkers/` review-checklist (brand voice + compliance + clarity + visual consistency).*