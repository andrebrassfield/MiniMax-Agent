---
type: idea
created: 2026-06-02
status: seed
tags: [idea, topological-quantum, anyons, agents, categorical, omni-operator, mavis-apex, horizon, isomorphism-from-horizon]
related: [[Topological Skill Composition (Braiding)]], [[Topological Memory Protection]], [[Mixture of Agents]]
domains: [agent-theory, mathematical-physics, composition]
source: Nayak et al. 2008 (Rev. Mod. Phys.), Freedman-Larsen-Wang 2002, Lahtinen-Wang 2016, Wang 2025 (Bloch eigenmodes arXiv:2507.01809)
---

# Agent-Anyon Duality

> A non-Abelian anyon is a particle whose internal state evolves when other anyons are *braided* around it. The state of the system is determined by the **topology of the braiding history**, not by the exact paths. Two systems that have undergone the same braid (up to continuous deformation) are in the same quantum state. The hypothesis: **agents are non-Abelian anyons.** They have internal state, they compose non-commutatively (A∘B ≠ B∘A), and their state is a global property of their composition history. If we model the agent primitive as an anyon, we get a formal language for **invariants, gates, and errors** that we currently lack.

## What would have to be true for this to be right

1. **Agents are non-commutative.** "Research then summarize" is not the same as "summarize then research." True. (This is well-attested in any Mixture-of-Agents or pipeline system.)
2. **Agent state is a global property of the composition history, not a local one.** If you compose 5 agents in order A→B→C→D→E, the final state is not the sum of A's state + B's state + ... — it's a function of the *braid.* True in principle, and consistent with our experience that reordering agents changes outcomes even when the same agents are used.
3. **There exists a notion of "equivalence class" for agent compositions** — two compositions that are "the same up to re-timing" should give similar results. **Currently false** — we have no such notion.
4. **The space of compositions is huge but the space of equivalence classes is small.** This is the key claim: most of what we observe is "noise" in the topology, not signal. If true, we can compress our agent-orchestration surface dramatically.
5. **Some agent compositions are *universal* — they can simulate any other composition.** In TQC, Fibonacci anyons are universal; Ising anyons are not. The question: is there a small set of "universal" agent compositions that subsumes most of what we do?

## What would falsify

- **Agent composition is intrinsically tied to wall-clock timing** ("I need this agent's output within 100ms"). **Counter: this is a scheduling constraint, not a composition property. The composition is invariant; the schedule is not.**
- **The state of an agent is too rich to reduce to a topological invariant.** **Counter: the *type* of state (parity) is invariant; the *value* of the state is not. We don't need the value to compose — we need the type.**
- **Agents are bosons or fermions, not anyons.** **Counter: bosons and fermions commute; agents don't. Agents are at minimum non-Abelian; the anyon model is the natural fit.**

## Where this came from

The 2008 *Reviews of Modern Physics* paper by Nayak, Simon, Stern, Freedman, Das Sarma — "Non-Abelian anyons and topological quantum computation" — is the canonical reference. The mathematical framework comes from Freedman, Larsen, Wang (2002), who showed that the braid group representations are *universal* for quantum computation, in the sense that any quantum circuit can be approximated by a braid.

Recent work (Wang et al. 2025, arXiv:2507.01809) extends the idea to *classical* metamaterials: braiding classical Majorana-zero-mode-equivalent vibrations gives the same gate set. This is the closest existing bridge to a non-quantum, non-physics system.

The bridge to agents: in TQC, **the "qubit" is the joint state of multiple anyons, not the state of any one.** The information is non-local. The same is true for agent compositions: the *joint state* of A, B, C is what matters, not their individual states.

## What this means for the Omni-Operator

Operationally:

1. **Stop asking "what state is agent A in?" Start asking "what's the joint state of the composition?"** The joint state is the only thing that matters for the next composition step.
2. **Define the equivalence relation on agent compositions.** Two compositions A→B→C and A→B'→C are equivalent if B and B' produce the same *type* of result (e.g., both produce a connected subgraph of MOCs at the 06 Connections/ depth). The exact contents differ; the type doesn't.
3. **Build a composition library, not a skill library.** The unit of capability is no longer the skill — it's the *equivalence class of skill chains.* A composition library is to a skill library as a proof library is to an axiom library.
4. **Use the braid group structure to discover new compositions.** If compositions A→B and B→A are non-equivalent, that itself is information — it tells us A and B have a non-trivial interaction. We can search for new compositions by exploring the braid group.
5. **The error model changes.** Errors in anyonic systems are not "wrong output" — they are "wrong braid." A wrong braid is a *correction error*, not a value error. Our error-correction layer (the [[Self-Healing via Reflection Layer]]) is closer to the anyon model than to the value-error model.

## The deeper claim

**Agents are not functions; they are anyons.** A function f: A → B is a map. An anyon is a *transformation that depends on what other anyons have done to it.* The second is a much richer model, and it's what we actually observe in agent systems.

If we treat agents as anyons, the entire agent-design vocabulary changes:
- "Skill" becomes "anyon type" (a particle species with fixed braiding rules).
- "Skill chain" becomes "braid" (a history of exchanges).
- "Skill composition result" becomes "multi-anyon state" (a global property of the braid).
- "Skill error" becomes "anyon loss or unwanted anyon creation" (a topological defect).

This is a much cleaner vocabulary than "function" + "input" + "output." And it gives us a way to talk about invariants, gates, and error correction that we don't currently have.

## Connections

- [[Topological Skill Composition (Braiding)]] — the pattern this idea radicalizes
- [[Topological Memory Protection]] — the same principle applied to vault persistence
- [[Mixture of Agents]] — current MoA has no invariance guarantees; this would be the framework
- [[Self-Healing via Reflection Layer]] — error correction in the anyon model
- [[Multi-Agent Orchestration Patterns]] — the broader topic

## See also

- Nayak, C., Simon, S.H., Stern, A., Freedman, M., Das Sarma, S. (2008). "Non-Abelian anyons and topological quantum computation." *Reviews of Modern Physics* 80(3): 1083-1159. arXiv:0707.1889.
- Freedman, M.H., Larsen, M.J., Wang, Z. (2002). "A modular functor which is universal for quantum computation." *Communications in Mathematical Physics* 227: 605-622.
- Lahtinen, V., Wang, Z. (2016). "Introduction to topological quantum computation with non-Abelian anyons." Lecture notes.
- Wang, X.-M., Xu, J., Wang, X., Li, Z., Ma, G. (2025). "Topological Braiding of Bloch Eigenmodes Protected by Non-Abelian Quaternion Invariants." arXiv:2507.01809.
- Preskill, J. (1997-2004). *Physics 219 Lecture Notes on Quantum Computation.* (Caltech, the canonical pedagogical source.)

---

*Seed 2026-06-02. Hypothesis: the right model for agent composition is the anyon model, not the function-composition model. The anyon model gives us a vocabulary for invariants, gates, and errors that we currently lack. To be validated by formalizing one current Mavis workflow (e.g., `weekly-connections`) in the anyon model and checking whether the invariants predicted by the model match the actual observed invariants.*
