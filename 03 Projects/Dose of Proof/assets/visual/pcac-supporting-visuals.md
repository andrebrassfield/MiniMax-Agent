---
type: visual-assets
asset: pcac-supporting-visuals
format: Mermaid diagrams (textual — render via mermaid.live, GitHub markdown, or any Mermaid renderer to PNG/SVG)
status: ✅ FINAL (locked 2026-06-24, ship-now)
count: 5 diagrams
purpose: support the PCAC catalyst assets + Substack posts + Skool onboarding + LinkedIn carousels + launch sales assets
companion_to: specs/pcac-hair-trigger-activation.md + specs/macro-longevity-peptide-explainers.md + specs/substack-series-pcac.md
---

# PCAC Supporting Visuals — 5 Mermaid Diagrams

> Each diagram is a Mermaid block. Copy-paste into mermaid.live (https://mermaid.live) to render as PNG/SVG. The PNG/SVG versions are the ones used in Substack, Skool, LinkedIn, and sales surfaces.

---

## Diagram 1 — FDA Compounding Categories (Category 1 vs 2 vs 3)

**Use cases:**
- Substack post on PCAC meeting (Part 1 — pre-launch)
- LinkedIn carousel slide explaining FDA mechanics
- Skool onboarding Day 4 (vagus-neck mechanics + regulatory context)
- Sales page module explaining why PCAC framework operates upstream

**How to render:**
1. Copy the Mermaid block below
2. Paste into https://mermaid.live
3. Export as PNG (or SVG for higher quality)
4. Use filename: `pcac-category-mechanics.png`

```mermaid
flowchart TD
    A[Nominated Bulk Substance] --> B{FDA Safety +<br/>Data Review}
    B -->|Strong safety data<br/>+ clinical use| C1[Category 1<br/><br/>Compounder MAY<br/>produce for human use<br/>under 503A]
    B -->|Significant safety risk<br/>OR insufficient data| C2[Category 2<br/><br/>Compounding PROHIBITED<br/>for human use]
    B -->|Insufficient data<br/>+ more info needed| C3[Category 3<br/><br/>More data required<br/>before determination]

    C1 -.->|Examples:<br/>compounded hormones<br/>in specific use cases| EX1[Legal pathway:<br/>503A pharmacy +<br/>physician Rx]
    C2 -.->|Examples:<br/>BPC-157 currently<br/>KPV, Semax, TB-500, MOTs-C| EX2[No legal compounding<br/>for human use]
    C3 -.->|Examples:<br/>compounds awaiting<br/>additional data| EX3[Pending determination]

    style C1 fill:#1f4e3d,color:#fff
    style C2 fill:#5c1f1f,color:#fff
    style C3 fill:#4a4a1f,color:#fff
    style EX1 fill:#2a5a4a,color:#fff
    style EX2 fill:#6a2a2a,color:#fff
    style EX3 fill:#5a5a2a,color:#fff
```

---

## Diagram 2 — PCAC Timeline (FDA Process: Nomination → Committee → FDA Decision)

**Use cases:**
- Substack post on FDA PCAC meeting structure
- LinkedIn carousel explaining the 4-step process
- Hair-trigger activation reference (when does each step happen)
- Audio origin story chapter visual (optional B-roll)

**How to render:**
- Copy Mermaid → mermaid.live → PNG
- Filename: `pcac-timeline.png`

```mermaid
flowchart LR
    P1[Step 1<br/><br/>NOMINATION<br/><br/>Anyone can nominate<br/>a bulk substance<br/>with safety data<br/>+ proposed use<br/><br/>BPC-157, KPV, TB-500,<br/>MOTs-C, Semax all<br/>nominated years ago] -->|FDA reviews| P2[Step 2<br/><br/>FDA REVIEW<br/><br/>Animal toxicology<br/>+ human case reports<br/>+ manufacturing quality<br/>+ immunogenicity risk<br/>+ clinical indication]

    P2 -->|FDA assigns| P3[Step 3<br/><br/>CATEGORY ASSIGNMENT<br/><br/>Category 1<br/>OR<br/>Category 2<br/>OR<br/>Category 3]

    P3 -->|FDA refers to committee| P4[Step 4<br/><br/>PCAC COMMITTEE REVIEW<br/><br/>External expert committee<br/>reviews FDA's category<br/>+ makes NON-BINDING<br/>recommendation]

    P4 -->|FDA can follow<br/>or override| P5[Step 5<br/><br/>FDA FINAL DECISION<br/><br/>FDA issues final rule<br/>based on committee<br/>recommendation<br/>+ own review]

    style P1 fill:#1a3a5c,color:#fff
    style P2 fill:#1a3a5c,color:#fff
    style P3 fill:#5c4a1a,color:#fff
    style P4 fill:#5c1a4a,color:#fff
    style P5 fill:#1a5c4a,color:#fff
```

---

## Diagram 3 — Vagus-Neck-MCAS Vicious Loop (the upstream driver model)

**Use cases:**
- LinkedIn Carousel 1 (5 Biomarkers visualization)
- Substack Post — Terrain Mapping (already FINAL)
- Skool onboarding Day 4 (vagus-neck mechanics)
- Sales page Module 1
- Audio origin story The Data section (visual reference)

**How to render:**
- Copy Mermaid → mermaid.live → PNG
- Filename: `vagus-neck-mcas-loop.png`

```mermaid
flowchart TD
    UCC[Upper Cervical<br/>Instability<br/><br/>C1-C2 laxity<br/>Loss of curve] -->|Mechanical irritation| VN[Vagus Nerve<br/>Dysfunction<br/><br/>Brake off]

    VN -->|Loss of<br/>parasympathetic brake| MC[Mast Cell<br/>Activation<br/><br/>MCAS flares<br/>Tryptase elevation<br/>Urine mediators]

    MC -->|Inflammation +<br/>guarding| INF[Systemic<br/>Inflammation<br/><br/>ESR/CRP elevation<br/>Flushing episodes<br/>Heat sensitivity]

    INF -->|More guarding<br/>+ instability| UCC

    UCC -.->|Interruption point:<br/>Blair upper cervical<br/>adjustments + vagal work| TX[TREAT UPSTREAM<br/><br/>Address the neck<br/>+ restore vagal tone<br/><br/>Downstream symptoms<br/>resolve as a result]

    style UCC fill:#5c1a1a,color:#fff
    style VN fill:#5c4a1a,color:#fff
    style MC fill:#4a1a5c,color:#fff
    style INF fill:#5c1a4a,color:#fff
    style TX fill:#1a5c4a,color:#fff
```

---

## Diagram 4 — Symptom Whack-a-Mole vs Terrain Mapping (framework comparison)

**Use cases:**
- Substack Post 3 (PCAC framework long-form, Jul 8)
- LinkedIn Carousel 2 (PCAC framework visualization)
- Sales page Module 1
- Skool onboarding Day 1 (Welcome post framing)
- Audio origin story The Framework section (visual reference)

**How to render:**
- Copy Mermaid → mermaid.live → PNG
- Filename: `framework-comparison.png`

```mermaid
flowchart LR
    subgraph WAAM[SYMPTOM WHACK-A-MOLE<br/><br/>Each specialist treats<br/>ONE symptom<br/>Nobody connects the dots]
        S1[Specialist 1<br/>Anxiety<br/>SSRI Rx]
        S2[Specialist 2<br/>Fibromyalgia<br/>Pain med Rx]
        S3[Specialist 3<br/>MCAS<br/>Antihistamine Rx]
        S4[Specialist 4<br/>Stress<br/>Another SSRI]

        S1 -.->|No connection| S2
        S2 -.->|No connection| S3
        S3 -.->|No connection| S4
    end

    subgraph TM[TERRAIN MAPPING<br/><br/>Map the upstream terrain<br/>5-biomarker floor<br/>Prove it works or change]
        T1[HRV<br/>vagus tone]
        T2[TyTron<br/>autonomic scan]
        T3[Tryptase +<br/>urine MCAS]
        T4[ESR + CRP +<br/>symptom log]
        T5[Vitamin D +<br/>magnesium]

        T1 --> UPSTREAM[UPSTREAM DRIVER<br/>e.g., upper neck instability<br/>+ vagus dysfunction]
        T2 --> UPSTREAM
        T3 --> UPSTREAM
        T4 --> UPSTREAM
        T5 --> UPSTREAM

        UPSTREAM --> INTERVENTION[Treat upstream<br/>Biomarkers trend<br/>Symptoms resolve]
    end

    WAAM --> PATIENT[Patient<br/>5 Rx bottles<br/>0 connections<br/>Still sick]
    TM --> PATIENT2[Patient<br/>Owns their data<br/>Reads their own trends<br/>Tracks outcomes]

    style WAAM fill:#5c1a1a,color:#fff
    style TM fill:#1a5c4a,color:#fff
    style UPSTREAM fill:#1a4a5c,color:#fff
    style PATIENT fill:#5c1a1a,color:#fff
    style PATIENT2 fill:#1a5c4a,color:#fff
```

---

## Diagram 5 — The 5-Biomarker Floor (HRV / TyTron / Tryptase / ESR-CRP / Vitamin D-Mg)

**Use cases:**
- Substack Post 2 (How to read your own bloodwork)
- LinkedIn Carousel 1 (5 Biomarkers)
- Skool onboarding Day 2 (5 biomarkers intro)
- Lead magnet PDF (visual companion)
- Sales page Module 2 (terrain mapping)
- Audio origin story The Numbers section

**How to render:**
- Copy Mermaid → mermaid.live → PNG
- Filename: `5-biomarker-floor.png`

```mermaid
flowchart TD
    START[5-BIOMARKER FLOOR<br/><br/>Minimum data set<br/>that catches upstream drivers<br/>most doctors miss] --> M1

    M1[1. MORNING HRV<br/><br/>Vagus brake gauge<br/>Free phone app<br/>Before caffeine<br/><br/>Target trend:<br/>7-day average 50+<br/>SD under 8]

    M2[2. TYTRON SCAN<br/><br/>Autonomic infrared<br/>Paraspinal thermal<br/><br/>Look for:<br/>Left-right symmetry<br/>Straight lines<br/>Visual feedback<br/>on mechanical driver]

    M3[3. TRYPTASE + URINE MCAS<br/><br/>Catch during/after flare<br/>N-methylhistamine<br/>LTE4<br/>Prostaglandin D2<br/><br/>Baseline often normal<br/>Flare data is signal]

    M4[4. ESR + CRP + SYMPTOMS<br/><br/>ESR under 20<br/>hs-CRP under 1<br/>Daily guarding score 1-10<br/>Flushing episodes<br/><br/>Pattern: subjective<br/>+ objective = story]

    M5[5. VITAMIN D + MAGNESIUM<br/><br/>25-OH Vitamin D<br/>Target 50-60 ng/mL<br/><br/>RBC magnesium<br/>Target 5.5-6.5 mg/dL<br/><br/>Terrain foundation]

    M1 --> READ[READ YOUR OWN DATA<br/><br/>Trends not snapshots<br/>Personal optimal<br/>not population normal<br/>Patterns over values]
    M2 --> READ
    M3 --> READ
    M4 --> READ
    M5 --> READ

    READ --> FRAMEWORK[PCAC FRAMEWORK<br/><br/>Show me the data<br/>Show me the before/after<br/>Prove it works<br/>or change the approach]

    style START fill:#1a1a5c,color:#fff
    style READ fill:#1a5c4a,color:#fff
    style FRAMEWORK fill:#5c4a1a,color:#fff
```

---

## How to render all 5 in one pass

1. Open https://mermaid.live in your browser
2. Create a new diagram for each block above (5 separate pastes)
3. Export each as PNG (1000-2000px width for sharp LinkedIn/Substack use)
4. Save to: `assets/visual/diagrams/` (create folder if needed)
5. Filenames per the per-diagram "How to render" sections

**Time estimate:** 5 minutes per diagram = 25 minutes total. All 5 ship-ready within an hour.

## How to use these in production

**Substack posts:**
- Post 2 (Jul 1, How to read bloodwork): Use Diagram 5 (5-biomarker floor) — referenced in the "5-marker floor revisited" section
- Post 3 (Jul 8, PCAC framework): Use Diagram 4 (framework comparison) + Diagram 3 (vagus-neck loop)
- Series Part 1 (Jul 15-21): Use Diagram 1 (category mechanics) + Diagram 2 (timeline)
- Series Part 2 (Jul 23-24, live): Use Diagram 1 + Diagram 2 as the visual frame

**LinkedIn carousels:**
- Carousel 1 (5 Biomarkers): Use Diagram 5 as one of the slides
- Carousel 2 (PCAC Framework): Use Diagram 4 as one of the slides
- New Carousel 6 (FDA mechanics): Use Diagram 1 + Diagram 2

**Skool onboarding:**
- Day 2 (5 biomarkers): Use Diagram 5
- Day 4 (vagus-neck mechanics): Use Diagram 3
- Day 5 (Bring Your Data): Use Diagram 5 (lighter version)

**Sales page (when built):**
- Module 1: Diagram 4 (framework comparison)
- Module 2: Diagram 3 (vagus-neck loop) + Diagram 5 (5-biomarker floor)
- Module 5 (Recon math): add Diagram 6 later (recon formulas)
- Module 7 (PCAC framework): Diagram 1 + Diagram 2

---

## Why Mermaid, not commissioned illustration

- **Speed:** ship in 25 min vs 2-4 weeks
- **Cost:** $0 vs $500-3,000 per illustration
- **Editability:** text-based, Mavis can iterate instantly
- **Compliance:** no third-party art dependencies
- **Reuse:** copy-paste across all surfaces
- **Versioning:** change a node, re-render

**Trade-off:** less polished than commissioned work. Commissioning Tier 4 visual assets (per `assets/visual/b-roll-audio-repurposing.md` Part 1) is a Q3 2026 priority when budget allows.

---

*Last updated: 2026-06-24 (Live Execution pass)*
*Ship-ready: yes. Awaiting Dre to render PNG/SVG via mermaid.live (~25 min total).*