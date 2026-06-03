# Source Balance

> Tracks the mix of evidence by source type (primary / secondary / social) and by source lane. If a dossier or run is over-dependent on low-trust surfaces, it shows here.

## Run-level balance (last refresh: 2026-06-02 21:50 CT, manual, 2 lanes)

| Source lane | Primary | Secondary | Social | Total | Social % |
|-------------|---------|-----------|--------|-------|----------|
| ai_agents | 11 | 4 | 0 | 15 | 0% |
| frontier_ai | 7 | 4 | 0 | 11 | 0% |
| **Total (this run)** | **18** | **8** | **0** | **26** | **0%** |

Note: 23 unique sources in `sources.jsonl`; the table above breaks them out by lane. Several sources cross lanes (e.g. arXiv memory surveys → ai_agents primary, with secondary implications for memory_orchestration which is deferred).

## Dossier-level balance

### `dossiers/ai_agents.md`
- Primary sources: 11 (langchain.com, letta.com, anthropic.com, arxiv.org)
- Secondary sources: 4 (Medium, Substack, Alice Labs, nxcode)
- Social: 0
- Social %: 0% — well under 40% soft warning floor

### `dossiers/frontier_ai.md`
- Primary sources: 7 (openai.com, blog.google, anthropic.com, openai.com)
- Secondary sources: 4 (whatllm.org, Fazm, Releasebot, Linas Substack)
- Social: 0
- Social %: 0% — well under 40% soft warning floor

## Warnings

- **Soft warning:** social % > 40% for any dossier. **NOT TRIGGERED** this run.
- **Hard warning:** social % > 60% for any dossier. **NOT TRIGGERED** this run.
- **Hard fail:** social % > 80% for any dossier. **NOT TRIGGERED** this run.

## Notes

- First REFRESH deliberately used zero social-sourced findings. The reason: the social-only verification discipline says social should go to verification queue, not into dossiers. I did collect 0 X posts this run — partly because the source plan puts X on the "verify-only" lane, and partly because no X signal I could verify in 60 minutes met the cross-source bar.
- 1 SEO-contradicted claim (GPT-6 rumor) was identified, weighed at 0.15, and routed to verification queue. Not collapsed into any dossier. Not used as evidence anywhere.
- arXiv surveys (Du 2026, 47-author Hu 2025, Mnemonic Sovereignty) are weighted at 0.85 — primary, but with the caveat that surveys are aggregations, not original primary measurements. The individual papers they cite may warrant re-source later.

---

*Source balance is a quality floor. If a run is 90% X-posts, it is not a run; it is a feed reader.*
