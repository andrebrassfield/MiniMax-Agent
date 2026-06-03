# Build Handoff — Researcher → Build Agents

> Implementation-ready product/workflow opportunities with evidence. Different from Hermes handoff: this is concrete enough that a builder can act on it without re-research.

## Pending

*Empty. First REFRESH produced two `hermes-handoff` items (Managed Agents adoption, GPT-5.5 default flip) but no `build-handoff` items — the build lane requires cross-validated product/workflow opportunities, and the first REFRESH surfaced a clear cross-source consensus on *current* state, not on *new buildable products* that the existing fleet should ship.*

## Convention

```yaml
- id: bld-handoff-YYYY-MM-DD-NNN
  title: "<one line, concrete>"
  user_pain: "<one sentence, sourced>"
  proposed_solution: "<one paragraph>"
  evidence:
    source_trail: [src-...]
    cross_validated: true
  integration_targets: [hermes, mavis, openclaw, ...]
  build_size: small | medium | large
  monetization_clue: yes | no | unknown
  routed_at: YYYY-MM-DD
```

## Recently Consumed (last 5)

*Empty.*

---

**Discipline:**
- Cross-validated evidence (≥2 primary sources, or 1 primary + 1 secondary with strong agreement).
- Solution is concrete enough to spec, not "build an AI tool."
- Mark `monetization_clue: yes` only with a clear buyer or willingness signal.
