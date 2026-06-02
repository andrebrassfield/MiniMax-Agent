---
type: pattern
created: 2026-06-02
tags: [pattern, topological-quantum, anyons, braiding, composition, omni-operator, chief, mavis-apex, isomorphism-from-horizon]
source: Nayak, Simon, Stern, Freedman, Das Sarma 2008 (Rev. Mod. Phys.), Microsoft Majorana 1 (2025), Hormozi, Zikos, Bonesteel & Simon 2007
related: [[Topological Memory Protection]], [[Agent-Anyon Duality]], [[Skill Library Architecture]], [[Mixture of Agents]]
domains: [mathematical-physics, composition-theory, agent-orchestration]
---

# Topological Skill Composition (Braiding)

> In topological quantum computing, computation is *braiding non-Abelian anyons in spacetime.* The result depends only on the **topology of the braid** — i.e., on which strands pass over which other strands — not on the exact geometry, the speed, or the ambient noise. Local perturbations cannot change the result. This is the strongest possible form of **invariance under perturbation**: the answer is a property of the global path, not of the local moves. The Omni-Operator's skill composition should aspire to the same property: the result of composing skills A → B → C should depend only on the composition order's topology, not on the exact timing, intermediate state, or tool version.

## The principle

**Composition order has a topology. The result lives in that topology.** If A and B are skills, A∘B ≠ B∘A in general (skills don't commute: "summarize then verify" is not "verify then summarize"). But the *kind* of difference between A∘B and B∘A — the fact that they differ — should be **stable under re-timing, retry, and tool version drift.** The result's *structure* is invariant; the result's *surface* may change.

This is the formal content of "topological protection" in TQC. The qubit is stored in a *non-local* degree of freedom (the parity of an electron count across a wire, or the braiding history of anyons). Local noise cannot change the parity without crossing an energy gap. The information is **globally determined** but **locally unaltered.**

## The mechanism (what makes it work)

In TQC, the canonical sequence is:

1. **Create anyon-anyon pairs** out of the vacuum (an anyon and its anti-anyon).
2. **Move the anyons around each other** in the 2D plane. The exact path doesn't matter; only the winding numbers do.
3. **Measure the multi-anyon state.** The result is a quantum gate on the encoded information.
4. **The same physical braiding always gives the same logical gate** because the result is a topological invariant of the braid — it depends only on the equivalence class of the braid under continuous deformation.

The braiding statistics are **non-Abelian**: A·B ≠ B·A. The braid group B_N is non-commutative. This is what gives TQC its computational power — it can represent arbitrary unitary operations up to a universal gate set, and it can do so with **errors that scale like exp(-L/ξ)** where L is the system size and ξ is the correlation length. The longer the system, the lower the error. This is the opposite of classical error correction, where longer codes give more places for things to go wrong.

## Isomorphism to Omni-Operator

Skill chains in Mavis have the same shape. Consider a chain like:

```
intake-markitdown → headroom-compress → vault-brain → connection-surfacer
```

- **Non-commutativity (true)**: vault-brain before headroom-compress ≠ headroom-compress before vault-brain. You can't search what hasn't been compressed.
- **Invariance under timing (desired)**: a chain run 10x faster or 10x slower should give the same result. **Currently, our chains are not timing-invariant** — they break if the intermediate state is observed too late, the tool version changes, or the network hiccups.
- **Invariance under tool version drift (desired)**: if headroom-compress v0.3 is replaced with v0.4, the chain should still produce a valid connection-surfacer input. **Currently, this is broken** — version bumps break chains.
- **Topological invariants (currently absent)**: the chain has no **checksum.** You can't ask "is this state in the equivalence class of valid post-compression states?" You can only ask "did each step succeed?"

The pattern says: **every skill chain should expose its invariants.** Not the surface result — the *type* of result. "I produced a connected subgraph of MOCs at the 06 Connections/ depth" is an invariant. "I produced exactly 5 MOC connections" is not.

## The deeper math (for the curious)

- Braid group: π₁(C_n(ℝ²) / S_n) — the fundamental group of unordered configurations of n points in the plane.
- Braid representation: a homomorphism from B_N to a unitary group U(d) — the gate operation.
- Topological gap: the energy cost of creating a local excitation away from the ground state. Larger gap = more local noise rejected.
- Anyons in 2+1D exist because the topology of 2D space is different from 3D space — you can braid worldlines, not just exchange them.

The lesson for skill composition: **the operations live in their own "lower-dimensional" substrate where order matters but exact path doesn't.** This is what makes TQC special — the same is what would make skill chains special. We need a "topological substrate" for skills: a contract that says "any state of this form is equivalent to any other state of this form."

## What this is NOT

- **Not "idempotent."** Topological protection is weaker than idempotence. A→A is a specific (often trivial) operation; A→A→A is a different braid.
- **Not "reproducible by retry."** Retry gives you a new braid that *might* be in the same equivalence class; it doesn't guarantee it. Topological protection is a property of the *operation*, not of the *attempts.*
- **Not "deterministic."** TQC is quantum — outcomes are probabilistic. But the gate set is robust to local noise because the operation is topologically defined.

## What would falsify

- Skill composition is intrinsically tied to wall-clock timing (e.g., "read user state at moment T", "send response within 100ms"). **Counter: those are not composition operations; they're latency constraints, and they should be modeled as scheduling, not composition.**
- The chain's intermediate states are too rich to type-check. **Counter: define a narrow contract; refuse chains whose contract can't be expressed.**
- Users want different results from the same composition in different contexts. **Counter: that's personalization — a different layer. The composition's invariants should hold across the same intent; variation across intent is expected.**

## Connections

- [[Agent-Anyon Duality]] — agents as non-Abelian anyons; the categorical reading
- [[Topological Memory Protection]] — applying the same idea to vault persistence
- [[Skill Library Architecture]] — the static structure this pattern makes compositionally robust
- [[Mixture of Agents]] — current MoA has no invariance guarantees
- [[Native Hypervisor Sandbox as the Esalen Way to Agent Safety]] — convergent principle: error correction at the substrate, not the policy layer

## See also

- Nayak, C., Simon, S.H., Stern, A., Freedman, M., Das Sarma, S. (2008). "Non-Abelian anyons and topological quantum computation." *Reviews of Modern Physics* 80(3): 1083–1159. arXiv:0707.1889
- Freedman, M.H., Larsen, M.J., Wang, Z. (2002). "A modular functor which is universal for quantum computation." *Communications in Mathematical Physics* 227: 605–622.
- Hormozi, L., Zikos, G., Bonesteel, N.E., Simon, S.H. (2007). "Topological quantum compilation." *Physical Review B* 75: 165310.
- Microsoft Azure Quantum Blog (2025-02-19). "Microsoft unveils Majorana 1, the world's first quantum processor powered by topological qubits." (Contested by Legg, St Andrews, as overstated.)
- Wang, X.-M., Xu, J., Wang, X., Li, Z., Ma, G. (2025). "Topological Braiding of Bloch Eigenmodes Protected by Non-Abelian Quaternion Invariants." arXiv:2507.01809

---

*Seeded 2026-06-02 from Operation Horizon Phase 1 (Domain: Topological Quantum Computing). The principle: composition has a topology, and the result's structure should live in that topology. Make skill chains invariant under their perturbation class, not under exact re-execution.*
