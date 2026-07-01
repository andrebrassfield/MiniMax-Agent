---
date: 2026-06-26
type: connection
trigger: nightly-finder
strength: strong
thesis-relevant: true
thesis-link: Thesis 4 (long-term knowledge in vault, not in always-on context) + Active Thesis 1 (spec throughput is the bottleneck)
domains-crossed: [dose-of-proof-brand, dose-of-proof-engine, objective-intent-doctrine]
---

# Connection: Dose of Proof brand poster aesthetic ↔ Engine compliance gate (citation_gate.py + ComplianceGate component)

**Why this connection matters:** Reading the brand-kit v2 report and the engine v0.4 review package side by side reveals something neither document names: **the brand layer and the engine layer are encoding the same trust posture through two different surfaces.** The brand kit v2 paints the *human-facing* expression (warning-yellow `.dop-yellow-box` stamp + black canvas + clinical seriousness + ComplianceGate yellow-tape edge in `src/components/compliance/ComplianceGate.tsx`); the engine v0.4 builds the *machine-facing* expression (citation_gate.py BLOCK on PMID:37421564 because the real paper — "Electroacupuncture Alleviates Neuropathic Pain..." — has zero topic overlap with the CCI/mast-cell claim it was attached to). Both reference the same spec — the 5 unbreakable rules in `business-model-v1.md` + the Objective Intent Doctrine — but they are *different artifacts*. Reading them as a pair surfaces a third, unstated finding: **Mavis is encoding the Objective Intent Doctrine at three layers** — (1) regulatory/copy layer (the 5 unbreakable rules themselves), (2) engine/runtime layer (regex + LLM + citation_gate fail-closed UNION), (3) visual/UX layer (the brand poster aesthetic). The visual layer is the one nobody has called out yet, and it is doing load-bearing work that the engine cannot do.

**Note A:**
- Title: Dose of Proof — Brand Kit v2 Alignment Report (commit db04078, 2026-06-26)
- Path: `~/MiniMax-Agent/apps/doseofproof/BRAND_KIT_V2_REPORT.md`
- Claim: The brand's "deep black canvas + warning-yellow accents + clinical seriousness" aesthetic is applied surgically across hero, products, ComplianceGate, and Footer; the ComplianceGate component gets a yellow-stamp treatment ("EDUCATIONAL BRIDGE ONLY" + 4px yellow tape down left edge + dark mono body) that visually equates the brand's surface with the FDA's prescription-drug warning aesthetic; the design intent is "this content has been audited" — and the audit posture is built into the visual language itself.

**Note B:**
- Title: v0.4 Gate Fix — Review Package §9.3 (citation gate regression test, Co-CEO directive 2026-06-25 21:38 CT)
- Path: `~/MiniMax-Agent/03 Projects/Dose of Proof/specs/v0.4-review-package.md`
- Claim: `scripts/citation_gate.py` runs at engine level and BLOCKS the rev1 body that cited PMID:37421564 in support of "unstable neck → vagus irritation → mast cell activation" because the real PubMed ID resolves to an electroacupuncture/ferroptosis paper with 0.0 keyword overlap to the CCI/MCAS claim; the BLOCK message is the runtime equivalent of the brand's yellow stamp — "this claim was checked, and the citation does not support it."

**What reading both reveals:**

The brand kit v2 and the citation gate are not two unrelated work items. They are the *human-facing* and *machine-facing* expressions of the same audit discipline, and they have complementary failure modes that the other cannot cover.

The brand layer encodes the audit in the visual cortex: when a reader sees a `.dop-yellow-box` stamp on a Substack post, the reader's threat model activates ("this is being flagged as not-medical-advice"). The reader does not need to read a single word of the 5 unbreakable rules to receive the signal. **The visual stamp is the audit posture at zero-cognitive-cost.** This is the only layer where the signal reaches the reader *before* they read the claim.

The engine layer encodes the audit at the publish gate: when the engine sees a `Citation: PMID:37421564` claim that resolves to a paper about electroacupuncture and ferroptosis, the engine BLOCKS the post. The reader will never see the post because the engine never approved it. **The runtime gate is the audit posture at zero-trust-cost** — the engine doesn't need the reader to notice anything; the engine just refuses to publish.

Neither layer alone is sufficient:
- A visual stamp on a post with a fabricated citation tells the reader "this is audited" while the engine silently allowed a claim that fails the audit. The visual layer cannot detect citation fabrication.
- An engine-level BLOCK without a visual stamp tells the engine "this is wrong" but doesn't tell the reader why *this specific post* is presented with clinical seriousness. The engine layer cannot signal "this content has been vetted."

The brand kit v2 + citation_gate together form the **two-end audit posture**: the brand layer makes the audit *visible to readers*, the engine layer makes the audit *binding on publication*. Both are required for the audit to be load-bearing.

The deeper observation: **Mavis currently has no spec that names these as a pair.** The `objective-intent-ftc.md` doctrine encodes the regulatory posture. The `triage-gate-spec.md` encodes the engine gate. The brand-kit v2 doc encodes the visual aesthetic. None of the three documents cross-reference the others. Reading them together reveals that the Objective Intent Doctrine is being expressed at three layers without anyone having explicitly designed it as a three-layer expression. The next time the doctrine is updated (e.g., a new banned phrase, a new citation-failure mode, a new visual treatment), the three docs will drift unless the audit posture is *codified as one spec with three expression surfaces*, not three separate specs that happen to reference the same doctrine.

The active-thesis connection is sharpest here. **Thesis 1 says "spec throughput is the bottleneck, not implementation."** This connection is a worked example: the implementation works at all three layers (rules are written, gates fire, visual treatment is shipped). The bottleneck is the spec that says "these are the same audit posture at three layers and they must move together." Reading the three docs together reveals that the spec doesn't exist — and the next drift will start at the layer where someone updates one doc without updating the other two.

**Suggested next step:**
- Add a new doc at `03 Projects/Dose of Proof/specs/audit-posture-three-layer.md` (1-2KB) that names the three layers (regulatory/copy, engine/runtime, visual/UX) and the discipline that all three must move together when any one is updated. Reference it from `business-model-v1.md`, `triage-gate-spec.md`, and `BRAND_KIT_V2_REPORT.md` so the cross-link is bidirectional.
- Surface in tomorrow's morning brief as a `thesis-relevant: true` connection (Thesis 4 — long-term knowledge belongs in the vault, not in always-on context — applies here as: the audit posture is a permanent note, not a one-off spec).
- When v0.5 calibration ships, add a row to the new spec: "Engine-layer audit primitives (regex set, LLM prompt, citation_gate) are versioned in lockstep with visual-layer primitives (`.dop-yellow-box`, `.dop-caption`, ComplianceGate stamp). PRs that touch one without updating the spec get flagged at review."
- The 2026-06-23 `dose-pcac-sft-format` connection named the SFT-format relationship between PCAC rebrand and the 5-Stage pipeline. This connection extends that: the brand's *visual language* is the SFT-format for the audit posture, the engine's *gates* are the SFT-format for the runtime check. Both teach the same shape (audit-passed → ship; audit-failed → block) through different substrates.
