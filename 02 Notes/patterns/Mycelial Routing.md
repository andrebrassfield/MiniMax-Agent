---
type: pattern
created: 2026-06-02
tags: [pattern, mycology, physarum, routing, flow-optimization, omni-operator, chief, mavis-apex, isomorphism-from-horizon]
source: Tero et al. 2010 (Science), Reid 2025 (J. Roy. Soc. Interface), Reginato/Proverbio/Giordano 2024-2025
related: [[Mycelial Shuttle-Streaming as Resolver Principle]], [[Wood Wide Web as MOC Topology]], [[Mother-Tree MOC Topology]], [[Self-Healing via Reflection Layer]]
domains: [biological-computing, distributed-systems, knowledge-routing]
---

# Mycelial Routing

> The plasmodium of *Physarum polycephalum* — a single multi-nucleate cell with no brain or nervous system — solves mazes, recreates the Tokyo rail network, solves the Traveling Salesman Problem in linear time, exhibits habituation (a simple form of learning), and stores **externalized spatial memory in extracellular slime trails**. The mechanism is a positive feedback loop: signaling molecules propagate via shuttle-streaming, the resulting flow patterns cause fluid to thicken in well-traveled tubes, and dead-end tubes retract. The network that emerges is globally near-optimal without any central controller. This is the same shape as a capability router that learns from usage — only the path that is actually used, gets reinforced.

## The principle

**Routing is a flow-reinforcement problem, not a static-graph problem.** In Physarum, the network is not designed; it is the residue of what worked. Every tube that carries flow thickens; every tube that doesn't, retracts. The system has no model of the optimal path — it just has a body that records which direction its mass has been moving.

For an Omni-Operator, the structural lesson is: **the best skill router is one that updates its topology from observed invocations, not one that ships a fixed routing table.**

## The mechanism (what makes it work)

1. **Shuttle streaming** — the cytoplasm rhythmically flows back and forth inside tubes at ~60-90 second periods. This carries signaling molecules (calcium waves, possibly others) faster than diffusion would.
2. **Positive feedback on flow** — thicker tubes have lower resistance, so they carry more flow, which makes them thicker still. The reinforcement is local but the optimization is global.
3. **Pruning** — unused tubes lose mass to the parent network and retract. Dead ends are not stored forever; they are recycled.
4. **Externalized state** — the extracellular slime is **not the organism** but **the organism's memory of where it has been**. Reid et al. (2025) showed this memory is overwritable: a Physarum in a Y-maze will cross its own slime trail if the food is high-quality enough. **Memory is a heuristic, not a hard rule.**
5. **No central controller** — there is no "router node" deciding which tube to thicken. Every part of the network decides locally based on local flow. The global optimum emerges from local feedback.

The result, demonstrated by Tero, Takagi, Saigusa, Ito, Bebber, Fricker, Yumiki, Kobayashi, Soga & Nakagaki (2010, *Science*): a Physarum placed on a map of the Tokyo region with oat flakes at the city positions recreates the Tokyo rail network in days, with comparable cost-efficiency to the human-engineered system.

## Isomorphism to Omni-Operator

The shape is the same:

| Physarum | Omni-Operator |
|---|---|
| Single multi-nucleate cell | Single Mavis runtime with many skills |
| No brain, no central router | No "router service" — the catalog IS the state |
| Positive feedback on flow | Reinforce hot skill-invocation paths |
| Pruning of dead ends | Archive / cold-store unused skills |
| Externalized memory in slime | Externalized state in vault + MAVIS.md |
| Overwritable memory | Captures are revisable; instinct drift is allowed |
| Globally optimal without model | Catalog emerges from observed intent, not pre-design |

The operational takeaway: **a static skill catalog is dead.** A catalog that observes its own use, thickens hot paths, and prunes cold ones is *alive*. The catalog is not a reference document; it is the network.

## The deeper math (for the curious)

The Physarum-inspired optimization algorithm (the "Physarum solver") is provably near-optimal for shortest-path problems. Recent work (Reginato, Proverbio, Giordano, 2024-2025) shows the same algorithm reproduces robust foraging even under noise and partial information. The key invariant: the algorithm never needs to know the global graph; it only needs to sense the local flow gradient.

This is a **substrate-independent principle**: any system that can sense local gradients and amplify them globally can find near-optimal solutions without global knowledge. Slime molds, neural networks, marketplaces, and skill routers all do this.

## What this is NOT

- **Not "the catalog learns your preferences"** (that's personalization). This is about *the routing topology itself* adapting to flow.
- **Not a recommendation system.** The reinforcement is on the path, not on a ranked list of options.
- **Not centralization.** There is no master node. Each skill edge decides locally whether to thicken.
- **Not a free pass to ship bad skills.** A skill that's never invoked is correctly pruned — that's a feature, not a bug.

## What would falsify

- A static, pre-ranked catalog outperforms a flow-reinforced one in latency, hit rate, AND user satisfaction. (Counter: likely true for tiny skill libraries where the static ranking is already correct, but flips as N grows.)
- The cost of sensing and reinforcing flow exceeds the routing-quality gain. (Counter: the sensing is implicit in invocation counts; the reinforcement is metadata, not a real-time update.)
- Users find the catalog "moving under them" disorienting. (Counter: the user-facing view can stay static; only the internal routing topology changes.)

## Connections

- [[Mycelial Shuttle-Streaming as Resolver Principle]] — the operationalization of this pattern in the Resolver MCP
- [[Wood Wide Web as MOC Topology]] — the cross-organism version of the same routing principle
- [[Mother-Tree MOC Topology]] — the hub-and-spoke analog at the knowledge-graph scale
- [[Self-Healing via Reflection Layer]] — the in-band repair layer that complements the routing layer
- [[Skill Library Architecture]] — the static structure this pattern makes dynamic
- [[Tero et al. 2010, Science — Physarum recreates Tokyo rail network]] — the canonical experiment

## See also

- Tero, A., Takagi, S., Saigusa, T., Ito, K., Bebber, D.P., Fricker, M.D., Yumiki, K., Kobayashi, R., Soga, M., Nakagaki, T. (2010). "Rules for Biologically Inspired Adaptive Network Design." *Science* 327(5964): 439-442. doi:10.1126/science.1177894
- Reid, C.R., Latty, T., Dussutour, A., Beekman, M. (2025). "Slime mold uses an externalized spatial 'memory' to navigate." *Journal of the Royal Society Interface*. (PMC version also available.)
- Reginato, D., Proverbio, D., Giordano, G. (2025). "Bottom-up robust modelling for the foraging behaviour of Physarum polycephalum." *J R Soc Interface* 22(223): 20240701. arXiv:2412.19790
- Adamatzky, A. (2010). *Physarum Machines: Computers from Slime Mould*. World Scientific.
- Nakagaki, T., Yamada, H., Tóth, Á. (2000). "Intelligence: Maze-solving by an amoeboid organism." *Nature* 407: 470.

---

*Seeded 2026-06-02 from Operation Horizon Phase 1 (Domain: Mycelial Computing). The principle: routing is flow-reinforcement, not static-graph search. The Omni-Operator should make its skill catalog adaptive, not authoritative.*
