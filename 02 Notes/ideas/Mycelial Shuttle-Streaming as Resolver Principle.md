---
type: idea
created: 2026-06-02
status: seed
tags: [idea, resolver, physarum, mycelium, routing, omni-operator, mavis-apex, horizon, isomorphism-from-horizon]
related: [[Mycelial Routing]], [[Topological Skill Composition (Braiding)]], [[Skill Library Architecture]]
domains: [mcp-design, distributed-routing, biological-computing]
source: Tero et al. 2010 (Science), Reid 2025 (J. R. Soc. Interface), Reginato 2025 (J. R. Soc. Interface)
---

# Mycelial Shuttle-Streaming as Resolver Principle

> *Physarum polycephalum* solves mazes, finds shortest paths, and even reconstructs the Tokyo rail network — not by computing, but by **reinforcing flow.** Theoplasm in well-traveled tubes thickens; theoplasm in dead-ends retracts. The network is the residue of what was used. **The hypothesis:** the Resolver MCP should work the same way. It should not ship a fixed catalog-rank; it should observe its own invocations, thicken the hot paths, and prune the cold ones. The "catalog" is not a reference document; it is a network.

## What would have to be true for this to be right

1. **Skill invocation is the right unit of "flow."** Every skill call is a positive reinforcement event; every miss is a negative one.
2. **The cost of flow tracking is negligible compared to the routing-quality gain.** Invocation counts are essentially free to record.
3. **Routing topologies converge faster than the skill library changes.** We don't want the routing to be chasing a moving target.
4. **The user-facing catalog (the list you read) stays readable**, even if the internal routing topology is non-uniform.
5. **The pruning of cold skills is reversible.** Archived skills can be re-promoted if new evidence emerges.

## What would falsify

- **Hot-path reinforcement creates a winner-takes-all dynamic** that buries new skills regardless of merit. Counter: introduce a "freshness bonus" — new skills get a small exploration boost for their first N invocations. This is the Physarum analog of phototaxis (light avoidance) that lets the mold explore new terrain.
- **The optimal routing is identical to a pre-computed static ranking** for our actual skill library. Counter: this is a testable hypothesis. Run both for a week and compare user satisfaction / task success. If static wins, the library is too small for flow to matter.
- **Skill invocations are too sparse** for flow to converge. Counter: aggregate across the entire session, not per user. The vault is a single-vault system; the routing can be cross-session.
- **Users find the catalog "shifting under them" disorienting.** Counter: the user sees a stable, ranked list. The *internal* reinforcement is on the routing weights, not on the display order.

## Where this came from

The Physarum literature is rich and well-replicated. Tero et al. (2010) is the canonical experiment. Reid et al. (2025) showed externalized memory (slime trail) is overwritable — i.e., the network is *not* permanently committed. Reginato, Proverbio, Giordano (2024-2025) showed the bottom-up model is robust to noise. Adamatzky's *Physarum Machines* (2010) catalogued a decade of Physarum-as-computer work. The convergent claim: **simple local feedback + global flow reinforcement = near-optimal routing without a global model.**

This is the same shape as a properly-designed Resolver. The current Resolver is a static, pre-computed ranking. The hypothesis is that the right Resolver is a *dynamically reinforced network* that learns from its own invocations.

## What this means for the Omni-Operator

Operationally:

1. **The Resolver records every (intent → skill) pairing** with timestamp, success/fail, and duration.
2. **Hot paths thicken.** A skill that's invoked 100x/week for "summarize a document" gets a +5 routing weight on that intent; a skill invoked 1x gets a 0.
3. **Cold paths get archived, not deleted.** If a skill isn't invoked in 90 days, move it to `99 _system/skills/_archive/` with metadata. The skill still exists, the routing just doesn't surface it.
4. **Cold skills can be re-promoted.** A weekly sweep checks archive for skills that have gained new connections (e.g., a new note in the vault linking to it). If so, restore.
5. **The catalog display is stable.** The user sees a sorted, deduplicated list of available skills. The internal reinforcement is on the routing weights, not the display.
6. **The flow data is itself a CHIEF artifact.** A periodic `99 _system/reports/resolver-flow.md` is generated showing hot paths, cold paths, dead ends, and the routing's own "introspection." This is the analog of the Wood Wide Web's defense signaling — the network reports on itself.

The system becomes **a forest, not a registry.** A forest grows; a registry is filled. The Esalen posture: let the network be alive.

## The deeper claim (what this is really about)

Static catalogs are dead. The right skill library is a **living system** that adapts to its own use. Physarum is not just a clever algorithm — it's a model for what any long-lived, large, complex routing system should look like: **reinforce what's used, prune what isn't, never trust a pre-computed ranking more than the observed flow.**

This is the same as the broader EA principle: **observe, then encode.** Don't pre-compute the workflow; let it emerge from the invocations. The catalog is the *output* of the EA's work, not its input.

## Connections

- [[Mycelial Routing]] — the underlying pattern
- [[Topological Skill Composition (Braiding)]] — the composition-order analog
- [[Skill Library Architecture]] — the static structure this idea makes dynamic
- [[Wood Wide Web as MOC Topology]] — the knowledge-graph analog
- [[Self-Healing via Reflection Layer]] — the in-band repair layer; this idea is the out-of-band routing layer
- [[Mavis-Apex-Architecture]] — the Resolver sits inside this stack

## See also

- Tero, A., et al. (2010). "Rules for Biologically Inspired Adaptive Network Design." *Science* 327: 439-442.
- Reid, C.R., et al. (2025). "Slime mold uses an externalized spatial 'memory' to navigate." *J. R. Soc. Interface* (PMC3491460 / published version).
- Reginato, D., Proverbio, D., Giordano, G. (2024-2025). "Bottom-up robust modelling for the foraging behaviour of Physarum polycephalum." *J. R. Soc. Interface* 22(223): 20240701.
- Adamatzky, A. (2010). *Physarum Machines: Computers from Slime Mould.* World Scientific.

---

*Seed 2026-06-02. Hypothesis: the Resolver should be a flow-reinforced network, not a static ranking. To be validated by running the static Resolver and the flow-Reinforced Resolver side-by-side and comparing routing quality, exploration depth, and cold-skill recovery. To be prototyped in a future session once the Resolver MCP is structurally stable.*
