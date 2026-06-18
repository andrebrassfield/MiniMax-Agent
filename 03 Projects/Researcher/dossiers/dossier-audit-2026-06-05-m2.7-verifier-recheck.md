# Re-Audit Checkpoint — Phase 1 Dossier Patches (M2.7 Verifier)
# Verifier session: mvs_e13adb75a2b348448c5fece3a845b9ed
# Date: 2026-06-05 20:40 CT
# Task: Re-audit 4 patches after VERDICT: FAIL (original audit mvs_5a70862ad465458bb216f5e0d5170edb)
# Source: 5 grep operations + line-level read of minimax_ecosystem_2026.md (208 lines)

## VERDICT: FAIL

**FAIL reason:** Downstream content (Implications, Watch sections) still uses unverified multiplier and TPS numbers without UNVERIFIED flags. The critical claims are correctly flagged in the body, but the implementation guidance built on them is not.

---

## Patch 1 — Owner→Leader: APPLIED CORRECTLY

**Evidence:**
- `grep -i "Owner"` on minimax_ecosystem_2026.md: **0 matches**
- `grep -i "Leader"` on minimax_ecosystem_2026.md: **5 matches** — lines 9, 83, 85, 100, 187
- Line 9: "the Leader/Worker/Verifier architecture is structurally identical to the Producer → Trust loop"
- Line 83: "The architecture is **Leader / Worker / Verifier**" with note: "Multiple independent launch-day Chinese press sources (腾讯新闻, 网易, 硅星Breaknews, 爱范儿, all 2026-05-13/14) confirm Leader as the canonical term."
- Line 83: "The primary technical blog (minimaxi.com/blog/minimax-agent-team-long-running, src-2026-06-05-028) returned 404 at verification time and could not be checked directly."
- Line 85, 100, 187: all use "Leader/Worker/Verifier" consistently

**Result: PASS**

---

## Patch 2 — Token Plan Multipliers Downgrade: PARTIALLY APPLIED

**Evidence (body text — correctly handled):**
- Line 73: "$0.30/M input, $1.20/M output" — verified base rates, no multiplier language
- Line 74: "M3 multiplier claims (1.3x input rate, 1.8x output rate, 0.2 token/char system-prompt surcharge): **UNVERIFIED in official MiniMax platform documentation.** The Token Plan FAQ (src-2026-06-05-021) and Rate Limits page (src-2026-06-05-022) contain no multiplier language. Secondary press (php.cn, IT之家) reports these figures but no primary source confirms them as of 2026-06-05. **NOT SAFE FOR PRODUCTION TOKEN ACCOUNTING** — apply only verified base rates until primary confirmation."
- Line 75: "Real-world M3 token consumption ~40% higher than M2.5 for similar tasks. **UNVERIFIED** — pending confirmation against primary source."
- Line 79: "The Mavis harness's token accounting must apply the 1.3x/1.8x/0.2 surcharge **after** the API response, not trust the SDK's number. **UNVERIFIED in our harness** — needs a test fixture."

**Evidence (downstream — NOT handled):**
- Line 189 (Implications / Build): "3. **Apply the Token Plan multipliers in our token accounting.** 1.3x input, 1.8x output, 0.2 token/char system-prompt surcharge. Do NOT trust the SDK's `total_tokens`."
  - **Problem:** No UNVERIFIED flag. Presented as implementation instruction, not as unverified numbers.
- Line 192 (Implications / Cache): "6. **Cache aggressively on the system prompt.** Token Plan charges 0.2 token/char system-prompt surcharge — a 50K-char system prompt costs 10K tokens per turn."
  - **Problem:** No UNVERIFIED flag. The surcharge is used in a cost calculation as if confirmed.
- Line 194 (Watch): "M3 open-weights release (~2026-06-11), Anthropic Mythos wider release, GPT-5.6 canary, MiniMax's rollout of the 1.3x/1.8x multiplier (already apologized once — second apology likely if user feedback continues)."
  - **Problem:** No UNVERIFIED flag. "Rollout of the 1.3x/1.8x multiplier" frames it as an ongoing confirmed program.

**Grep result:** `1.3x|1.8x|0.2 token` returns 5 matches. Only 2 (lines 74, 79) have UNVERIFIED flags. 3 matches (lines 189, 192, 194) do not.

**Result: PARTIALLY APPLIED** — the critical claims are correctly downgraded in the body, but the Implications and Watch sections still use the numbers without flags. A reader who skips to the Build implications will find "Apply the Token Plan multipliers" as a directive, not a warning.

---

## Patch 3 — Model Size Downgrade (196B/11B): APPLIED CORRECTLY

**Evidence:**
- Line 24: "Sparse MoE: **196B total / 11B active** parameter count circulates in secondary press but is **NOT confirmed in any accessible primary source** (MiniMax official blog, OpenRouter, Ollama all silent on model size as of 2026-06-05). **UNVERIFIED — MoE efficiency framing (11/196 = 5.6% active) pending primary confirmation.**"
- The "11/196 = 5.6% active" math is explicitly called out and flagged as pending, not presented as verified.

**Result: PASS**

---

## Patch 4 — TPS Downgrade (400 TPS): PARTIALLY APPLIED

**Evidence (correctly handled):**
- Line 21: "Throughput: **400 TPS** claim circulates in secondary press (php.cn, IT之家) but is **NOT confirmed in any accessible primary source** (MiniMax technical blog, OpenRouter, Ollama, rate limits page all silent on TPS as of 2026-06-05). **UNVERIFIED — NOT SAFE FOR PRODUCTION ROUTING.**"
- The 9.7x/15.6x speedup numbers are preserved (they are from the M3 technical report, not the 400 TPS claim).

**Evidence (not handled):**
- Line 176 (Contradictions / Open Questions): "The 400 TPS throughput is a throughput number, not a latency number."
  - **Problem:** "400 TPS throughput" referenced without UNVERIFIED flag. This is the same unverified number, re-used in a different context without warning.

**Result: PARTIALLY APPLIED** — the primary claim (line 21) is correctly flagged, but line 176 re-uses the number without the flag.

---

## Patch 5 — 404 URL Retry: APPLIED CORRECTLY

**Evidence:**
- Line 83: "The primary technical blog (minimaxi.com/blog/minimax-agent-team-long-running, src-2026-06-05-028) returned 404 at verification time and could not be checked directly."
- Line 164: "src-2026-06-05-028 MiniMax Agent Team technical blog (minimaxi.com/blog/minimax-agent-team-long-running) — 0.95" (still in source trail, correctly noting it was accessed but returned 404)
- The note is present in both the body text and the source trail.

**Result: PASS**

---

## Summary

| Patch | Result | Key evidence |
|---|---|---|
| 1. Owner→Leader | **APPLIED CORRECTLY** | 0 Owner matches, 5 Leader matches, Chinese press note present |
| 2. Token multipliers | **PARTIALLY APPLIED** | Body (lines 73-79) correctly flagged; Implications lines 189/192/194 unflagged |
| 3. Model size | **APPLIED CORRECTLY** | Line 24: UNVERIFIED + pending confirmation on efficiency framing |
| 4. TPS | **PARTIALLY APPLIED** | Line 21 correctly flagged; line 176 re-uses without flag |
| 5. 404 URL | **APPLIED CORRECTLY** | Lines 83 and 164 both note 404 status |

---

## Recommendation

To move to PASS, the Researcher needs one additional patch pass:

1. **Lines 189, 192, 194** — add "**[UNVERIFIED — multipliers not confirmed in official MiniMax docs as of 2026-06-05]**" to each instance of 1.3x/1.8x/0.2 in the Implications and Watch sections.
2. **Line 176** — add "**UNVERIFIED**" before "400 TPS throughput."

The body text is correct. The downstream content needs the same treatment.

---

*Verifier: mvs_e13adb75a2b348448c5fece3a845b9ed (M2.7)*
*Re-derived from source. No trust inherited from original (failed) session.*