# Dossier — First Principles

> Living topic file. Built 2026-06-04 for the vault knowledge base buildout. The canonical reference for what "first principles" means — in physics, in software engineering, in agent design, in life. The companion piece to the harness-engineering dossier: first principles is the *epistemology* the harness engineering *applies*.
>
> **Cross-references:** [`dossiers/harness-engineering.md`](harness-engineering.md) for the agent-design application · [`dossiers/ai-landscape.md`](ai-landscape.md) for the model layer that the first-principles analysis cuts through · [`dossiers/philosophy-of-mind.md`](philosophy-of-mind.md) for the deeper epistemological questions.

## Why this topic matters to Andre

Andre's directives (per the 2026-06-04 capture) explicitly call out "first principles" as one of the 10 topics for the vault buildout. First principles thinking is the discipline that lets a builder *see through* the model/framework/agent stack to what the underlying constraints actually are. It's the difference between "everybody's using LangGraph" and "what does our worker actually need to do, and is LangGraph the smallest thing that solves it." Without first principles, the vault compounds *trends*; with it, the vault compounds *judgments*.

## Current signal (as of 2026-06-04 02:45 CT)

### 1. The canonical definition

**First principles** (Greek: *archai*; Latin: *principia*): foundational propositions or assumptions that cannot be derived from any other proposition. Self-evident axioms from which all further truths are deduced.

The term is ancient — Aristotle (384–322 BCE) is the canonical source. In *Posterior Analytics* and *Metaphysics*, Aristotle distinguishes between (a) first principles, which are self-evident and known by *nous* (intuition), and (b) derived truths, which are deduced from first principles through syllogistic reasoning. (src-2026-06-04-067, src-2026-06-04-068, src-2026-06-04-069)

> "We must look for first principles themselves, those which cannot be demonstrated from anything prior." — Aristotle, *Posterior Analytics* I.1

The 2026 popular meaning — "break the problem down to its fundamental truths, then reason up" — comes from three sources:

- **Richard Feynman** (1988, *Surely You're Joking, Mr. Feynman!*): "What I cannot create, I do not understand. ... First principles." The quote is from a blackboard; the method is the discipline of rebuilding knowledge from the ground up.
- **Charlie Munger** (multiple, Berkshire Hathaway annual meetings 1986-2023): the "worldly wisdom" of "knowing the big ideas in all the big disciplines and using them routinely." Munger treats first principles as a lattice of mental models — physics, biology, psychology, economics, statistics — that compose into judgment.
- **Elon Musk** (2013, Kevin Rose interview; 2008 SpaceX interview): "I tend to approach things from a physics framework. Physics teaches you to reason from first principles rather than by analogy." The Tesla/SpaceX batteries-and-rockets cost analysis is the canonical example: instead of accepting "batteries cost $600/kWh" (analogy), reason from raw material costs (cobalt, nickel, lithium, aluminum, carbon, separator polymer) and discover that the fundamental floor is ~$80/kWh.

(src-2026-06-04-070, src-2026-06-04-071, src-2026-06-04-072, src-2026-06-04-073)

### 2. The four-step method (the operational discipline)

From James Clear's "First Principles: Elon Musk on the Power of Thinking for Yourself" (jamesclear.com/first-principles) and Addy Osmani's "First Principles for Software Engineers" (addyosmani.com): (src-2026-06-04-070, src-2026-06-04-074)

1. **Identify the problem.** Strip the framing. The problem is rarely what it first appears.
2. **Decompose to fundamental truths.** What do we *know* to be true, beyond all reasonable doubt? List them. These are the axioms.
3. **Reason up from the axioms.** Deduce the solution from the axioms, not from analogy to prior solutions.
4. **Reassemble and validate.** Build the solution from the ground up. Test against the original problem. If it doesn't satisfy the problem, one of the axioms was wrong.

The discipline is *decompositional*, not *intuitive*. It is the opposite of pattern-matching.

### 3. The three applications (and where they break)

**3a. First principles in physics.** The most rigorous form. The "three first principles of physics" (per SCIRP): the principle of relativity, the principle of least action, and the principle of regularity. From these three, the entire apparatus of classical mechanics, electromagnetism, quantum field theory, and general relativity is derived. Newton's *Principia* (1687) is the founding text: the axioms are the three laws of motion + universal gravitation, and *every* terrestrial and celestial mechanical phenomenon follows. (src-2026-06-04-075, src-2026-06-04-076)

The discipline in physics: every derivation must terminate in a *measurable quantity*. First principles are not free-floating; they are anchored to experiment.

**3b. First principles in software engineering.** The least rigorous form, but the most applied. Addy Osmani's framing: "First principles thinking can be helpful for solving complex problems because it allows you to break down a problem into its core elements and then systematically build up a solution from there." The four-step method applied to a software problem: identify the constraint, decompose to the user/IO/compute/state layer, reason up from the data flow, reassemble. (src-2026-06-04-074, src-2026-06-04-077)

Where it breaks in software: there is no agreed-upon set of axioms. The 1994 IEEE paper "Fifteen Principles of Software Engineering" (Bertrand Meyer, et al.) lists 15: quality number one, high-quality software is possible, give products to customers early, determine the problem before writing code, etc. But these are *heuristics*, not axioms. Software engineering has no Newton's three laws.

The pragmatic discipline: in software, "first principles" means *consciously questioning the conventional solution* — not "the framework everyone uses is wrong" but "what does this specific problem actually need, and is the conventional solution the smallest thing that satisfies it?" Andre's tool audit (the dossier's recurring theme) is exactly this discipline.

**3c. First principles in agent design.** The emergent 2026 application. Cameron Wolfe's "AI Agents from First Principles" (Deep (Learning) Focus, Substack) and the OpenAI community thread "Generate AI Agents Using First Principles Reasoning" both apply the same four-step method to agent design: (src-2026-06-04-078, src-2026-06-04-079)

- **Step 1 (identify the problem).** What is the worker actually supposed to do? E.g., "the Verifier audits subagent output against a rubric" — not "the Verifier is an LLM-as-judge."
- **Step 2 (decompose to axioms).** The minimal capabilities: read input, compare against rubric, score, return verdict. *No state, no tool use, no subagent delegation required for the simplest case.* The Verifier is *fundamentally* a comparison function.
- **Step 3 (reason up from axioms).** Given the comparison function, what infrastructure do we need? An LLM (to interpret the rubric semantically), structured output (to parse the verdict), a context window (to read the input + rubric), a memory (to track scoring consistency across calls). No MCP servers required for the comparison itself.
- **Step 4 (reassemble and validate).** Build the Verifier as a thin harness around the comparison function. Add MCP servers only when a real benchmark shows the Verifier is bottlenecked on a tool it lacks.

This is the discipline that the harness-engineering dossier's "Scaffolding Metaphor" and "Harness Thickness" sections formalize. The Mavis tool audit is *first principles applied* to the tool surface.

### 4. The BAAI brain-from-first-principles framework (the 2026 frontier)

BAAI's "AI of Brain and Cognitive Sciences: From the Perspective of First Principles" (arXiv:2301.08382, 2023) identifies six first principles the brain uses to extract, represent, manipulate, and retrieve information: (src-2026-06-04-080)

1. **Attractor networks** — stable states that the brain converges to (memory = attractor basin)
2. **Criticality** — the brain operates near a phase transition (between ordered and chaotic regimes), which maximizes information capacity and dynamic range
3. **Sparse coding** — only a small fraction of neurons fire at any moment (the brain is sparse, not dense)
4. **Predictive coding** — the brain is a prediction machine; perception = prediction + error signal
5. **Hierarchical temporal memory** — the brain represents time at multiple scales (HTM)
6. **Free-energy principle / active inference** — the brain minimizes surprise by updating its model or acting on the world (Friston)

The 2026 LLM architecture conversation — sparse mixture-of-experts, sparse attention, MSA (MiniMax Sparse Attention), early-exit mechanisms — is a *partial convergence* on principle 3 (sparse coding) and principle 4 (predictive coding). The 2026 frontier is the architectural implementation of brain-first-principles.

### 5. The MBZUAI / NYU "minimum necessary principle" for AI agents (2026)

The 2026 paper "AI Agent Scenarios: The Specific Connotation and Judgment Criteria of the Minimum Necessary Principle" (BUAA Journal, 2026) extends the GDPR minimum-necessary principle to AI agents. The argument: AI agents are personalized by design, so they need to collect and process as much personal information as possible — but the uncertainty in basic functions makes the minimum-necessary judgment hard. The paper proposes a four-criteria test: (src-2026-06-04-081)

1. **Necessity test** — is the data collection strictly necessary for the agent's stated function?
2. **Proportionality test** — is the data collection proportional to the function's scope?
3. **Purpose-limitation test** — is the data collection limited to the specific, declared purpose?
4. **Storage-limitation test** — is the data retained only as long as necessary for the purpose?

This is *first principles applied to AI agent ethics* — the axiom is "personal information is owned by the person, not the system," and every data-handling decision is derived from that axiom.

### 6. The OpenAI community's first-principles reasoning for agent generation

The OpenAI community thread "Generate AI Agents Using First Principles Reasoning" formalizes the four-step method for agent design: (src-2026-06-04-079)

1. **Define the agent's atomic purpose.** E.g., "categorize inbound support tickets."
2. **Identify the irreducible inputs/outputs.** Input = ticket text + ticket metadata. Output = category label. *Nothing else.*
3. **List the irreducible state.** E.g., category taxonomy (a static list). *No dynamic state for the simple case.*
4. **Identify the irreducible tools.** E.g., a label-lookup table. *No API calls, no MCP servers.*

The implementation is then: an LLM call with a system prompt that defines the taxonomy, a structured output that returns the label, and a single-shot completion. *No agent loop required.* The "agent" is just a function call.

The discipline: most "agents" built today are over-harnessed. They have state, memory, tool use, and subagent delegation when all they actually need is a function call. The first-principles analysis reveals the minimum infrastructure.

### 7. The "thinking from first principles vs thinking by analogy" — the Mavis lens

From Musk's Kevin Rose interview: "Physics teaches you to reason from first principles rather than by analogy. ... With first principles, you say, 'What are we *sure* is true?' ... and then reason from there." The Musk 3-step framework (Medium / "The Mission"): (src-2026-06-04-082)

1. **Identify your assumptions.** Write them down. Question every one.
2. **Break the problem down into its fundamental truths.** These are the axioms.
3. **Create new solutions from scratch.** Don't pattern-match to existing solutions.

The contrast:
- **Reasoning by analogy** = "everyone's using LangGraph, so we'll use LangGraph."
- **Reasoning from first principles** = "what does our worker actually need? A stateful graph? A function call? A multi-agent orchestration? A simple LLM call?"

**For Andre's fleet:** the Mavis tool audit is the canonical first-principles analysis. The question is not "what tool should we add?" but "what tool, if removed, would actually degrade the system?" The same for the agents: "what agent, if removed, would actually degrade the system?" The Verifier, the Researcher — these pass the first-principles test. The Designer (proposed) — questionable. The Scribe — situational.

### 8. The Munger mental models (the lattice of first principles)

Charlie Munger's "worldly wisdom" is a *lattice* of first principles across disciplines. The core models: (src-2026-06-04-083)

- **Physics** — equilibrium, leverage, critical mass, inertia
- **Biology** — evolution, ecosystems, niche, symbiosis
- **Psychology** — incentive, bias, social proof, loss aversion
- **Economics** — supply/demand, comparative advantage, opportunity cost
- **Statistics** — regression to the mean, sample size, base rate
- **History** — patterns repeat, contingent vs inevitable
- **Mathematics** — compound interest, limits, topology

The discipline: a first-principles thinker *lattices* these models to get a multi-dimensional view of any problem. Single-discipline first-principles is shallow. Latticed first-principles is deep.

**For Andre's fleet:** the EA (Mavis) is the lattice. The Verifier brings statistics and psychology (bias, base rate). The Researcher brings epistemology (the methodology of evidence). The Builder brings engineering (constraints, optimization, complexity). The Scribe brings rhetoric and narrative. The Designer (proposed) brings aesthetics and human factors. The lattice is *the fleet's value-add*, not any single agent.

### 9. The Feynman Technique (the learning-from-first-principles method)

Richard Feynman's technique for learning anything:

1. **Choose a concept.** Write it down.
2. **Teach it to a 12-year-old.** If you can't, you don't understand it.
3. **Identify the gaps.** Where does your explanation break? Go back to the source.
4. **Simplify and use analogies.** But not as a substitute for understanding.

The discipline: the explanation is the test. The moment you can't teach it simply, you don't understand it. This is *first principles applied to learning*, and it underlies the harness's "verification loops" component — the Verifier's job is to *teach the rubric* to the model in a way that surfaces gaps.

### 10. The cognitive bias against first principles (the friction)

First-principles thinking is *uncomfortable*. It requires:
- Questioning authority (the conventional solution is probably fine, but maybe not)
- Suspending intuition (the pattern that "feels right" is probably analogy, not axiom)
- Tolerating ambiguity (the axioms take time to identify)
- Resisting the social proof (everyone's using the same framework)

The Munger warning: "The human mind is a machine for pattern-matching, not for reasoning from first principles. ... It is easier to copy a successful pattern than to derive a solution from axioms." This is why the *discipline* of first principles is the valuable part — the result is less interesting than the process.

### 11. The first-principles discipline in agent design (the Mavis application)

**For each agent in the fleet, apply the four-step method:**

| Agent | Atomic purpose | Irreducible I/O | Irreducible state | Irreducible tools | Over-harness risk |
|---|---|---|---|---|---|
| **Verifier** | Audit subagent output vs rubric | Input: output + rubric. Output: verdict + score | Rubric taxonomy | None (LLM + structured output) | **Low.** The Verifier is fundamentally a function call. No MCP, no state, no subagents. |
| **Researcher** | Collect, weigh, route evidence | Input: topic. Output: dossier + handoff | Source ledger (JSONL) | Web search, web fetch, Obsidian MCP | **Medium.** The Researcher has a substantial tool surface. The question: are all 4-5 tools actually needed? |
| **Builder** | Implement what the harness specs | Input: spec. Output: working code | Workspace dir, scratchpad | Read, Write, Edit, Bash, Git, Docker | **High.** The Builder is the most tool-heavy agent. The first-principles audit: which tools are *required* vs *nice-to-have*? |
| **Scribe** | Compose, publish, distribute | Input: source + audience. Output: artifact | Drafts dir | Web search, content tools | **Medium.** The Scribe's tool surface is the writing/visual stack. Audit: which tools produce the highest-quality output per token? |
| **Designer (proposed)** | Translate intent to visual artifact | Input: spec. Output: HTML/CSS/image | Component library | Image generation, markdown-it, Obsidian | **High.** The Designer is the newest proposed agent and the least battle-tested. First-principles test: what is the irreducible capability? |

The audit cycle: every 6 months, re-apply the four-step method to each agent. The harness should *thin* over time, not thicken.

### 12. The 2026 frontier of first principles in agent research

Three open research directions (June 2026):

1. **Auto-harness optimization** — let the LLM optimize its own harness. The 76.4% TerminalBench pass rate result (cited in `dossiers/harness-engineering.md`) is the first canonical demonstration. The frontier: harness optimization as a meta-task the model can do for itself.
2. **First-principles evals** — instead of benchmarking against fixed tests, derive the test from the axioms of the problem. The frontier: a generation task's evaluation rubric is itself a derivation from the problem's first principles.
3. **Scaffolding-removal discipline** — Anthropic's pattern of *deleting planning steps* from Claude Code as models improve. The frontier: a CI test that asserts the harness shrinks when the model gets better.

## Source trail

See `knowledge/sources.jsonl`. Key primary sources for this dossier (all fetched 2026-06-04 02:35-02:55 CT):

- `src-2026-06-04-067` Wikipedia: "First principle" (en.wikipedia.org) — weight 0.9
- `src-2026-06-04-068` Terence Irwin: "Aristotle's First Principles" (Oxford 1990, lexile.com summary) — weight 0.85
- `src-2026-06-04-069` Aristotle's First Principles — Eric Kim Photography (erickimphotography.com) — weight 0.8
- `src-2026-06-04-070` James Clear: "First Principles: Elon Musk on the Power of Thinking for Yourself" (jamesclear.com) — weight 0.9
- `src-2026-06-04-071` The Book of Elon Musk: First-Principles Thinking (elonmuskbook.org) — weight 0.85
- `src-2026-06-04-072` Elon Musk Kevin Rose interview (YouTube transcript, NV3sBlRgzTI) — weight 0.85
- `src-2026-06-04-073` Medium: "Elon Musk's 3-Step First Principles Thinking" (medium/the-mission) — weight 0.8
- `src-2026-06-04-074` Addy Osmani: "First Principles for Software Engineers" (addyosmani.com) — weight 0.9
- `src-2026-06-04-075` SCIRP: "First Principles in Fundamental Physics" (scirp.org/journal/paperid=142226) — weight 0.85
- `src-2026-06-04-076` Galileo / Newton tradition in physics — derived claim (corroborated across multiple physics primers) — weight 0.85
- `src-2026-06-04-077` ResearchGate: "Fifteen Principles of Software Engineering" (Bertrand Meyer, IEEE Software 1994) — weight 0.85
- `src-2026-06-04-078` Cameron Wolfe: "AI Agents from First Principles" (cameronrwolfe.substack.com) — weight 0.9
- `src-2026-06-04-079` OpenAI Community: "Generate AI Agents Using First Principles Reasoning" — weight 0.85
- `src-2026-06-04-080` BAAI: "AI of Brain and Cognitive Sciences: From the Perspective of First Principles" (arXiv:2301.08382) — weight 0.9
- `src-2026-06-04-081` BUAA Journal: "AI Agent Scenarios: The Specific Connotation and Judgment Criteria of the Minimum Necessary Principle" (2026) — weight 0.9
- `src-2026-06-04-082` Renaissance Man Journal: "Elon Musk Problem Solving: Applications Of First Principles Thinking" — weight 0.75
- `src-2026-06-04-083` Munger mental models — derived from Poor Charlie's Almanack and Berkshire annual meeting transcripts — weight 0.85
- `src-2026-06-04-084` Reddit r/explainlikeimfive: "Elon Musk keeps talking about applying First Principles" — weight 0.7 (community)
- `src-2026-06-04-085` Reddit r/programming: "First Principles Thinking In Software Development" — weight 0.7 (community)
- `src-2026-06-04-086` Medium: "The Power of First Principles Thinking in Software Development" (Asankhaya Sharma) — weight 0.75
- `src-2026-06-04-087` FourWeekMBA: "First-principles Thinking In A Nutshell" — weight 0.75
- `src-2026-06-04-088` YouTube: "5 Ways First Principles Thinking Helps You Code Better" — weight 0.7
- `src-2026-06-04-089` Laws of Software Engineering: First-Principles Thinking (lawsofsoftwareengineering.com) — weight 0.8
- `src-2026-06-04-090` FPrin: "First Principles Engineering & Design" (fprin.com) — weight 0.7
- `src-2026-06-04-091` Reddit r/AI_Agents: "Learning AI Agents from First Principles. No Frameworks, Just..." — weight 0.7
- `src-2026-06-04-092` GitHub: miltonian/principles — first-principles reasoning for AI agents — weight 0.7
- `src-2026-06-04-093` ZJU Philosophy Forum: "Aristotelian logic: why do 'first principles' not need to be proven?" — weight 0.8
- `src-2026-06-04-094` WordNet / Youdao: "first_principle" — elementary stages, fundamental assumptions — weight 0.85
- `src-2026-06-04-095` NetEase: "如何理解 Elon Musk 的第一性原理?" — secondary commentary — weight 0.7
- `src-2026-06-04-096` Facebook Derivation post (community) — weight 0.65
- `src-2026-06-04-097` gainweightjournal: "Elon Musk Problem Solving" — weight 0.7
- `src-2026-06-04-098` kancloud: "First Principles Thinking Elon Musk" — weight 0.75
- `src-2026-06-04-099` LinkedIn: Asankhaya Sharma "The Power of First Principles Thinking" — weight 0.7
- `src-2026-06-04-100` Zhihu: "Elon Musk 的思考方法" — secondary — weight 0.65
- `src-2026-06-04-101` CSDN: "10 分钟搭建专属 AI Agent" — first-principles agent design (Chinese) — weight 0.7

## Contradictions and open questions

- **Musk's first-principles attribution is contested.** Some commentators attribute the popularization to Aristotle, others to Feynman, others to Munger. The honest answer: all three, and the lineage is ancient. Musk's contribution is the *operational discipline* in business and engineering contexts.
- **"First principles in software engineering" is the most contested application.** Critics argue software has no agreed-upon axioms (unlike physics), so calling any software design "first principles" is a category error. The pragmatic answer: the discipline is *consciously questioning the conventional solution* — not "we found the axioms of software."
- **The BAAI "six first principles of brain function" is a research program, not a settled framework.** The six principles (attractor networks, criticality, sparse coding, predictive coding, HTM, free energy) are *candidates* for the brain's first principles, not a consensus. Re-verification watch on the 2027-2028 BAAI updates.
- **Open question for Andre's fleet — first-principles audit cadence.** The four-step method should be applied to each agent every 6 months. The current "agent.md" doesn't codify this. Worth a follow-up: add a "first-principles review" step to the Mavis eval cycle.
- **Open question — the first-principles framing of the Designer (proposed) is unresolved.** The Designer is the newest proposed agent and the least first-principles-justified. The four-step method would say: what's the irreducible capability? "Translate intent to visual artifact" — but this could be a sub-mode of the Scribe, not a separate agent. Worth a Mavis review.
- **Re-verification watch — Munger lattice as the EA's value-add:** the "lattice of mental models" framing is canonical in Munger scholarship, but the *specific* assertion that "the lattice is the fleet's value-add, not any single agent" is original to this dossier. Worth a second-source check via Munger's *Poor Charlie's Almanack* (2005) and Tren Griffin *Charlie Munger: The Complete Investor* (2015).

## Implications

- **Build:** the Mavis tool audit (recurring theme) is the canonical first-principles analysis. Recommend Builder runs the audit (per-worker tool usage, per-MCP token cost) within 2 weeks. **High priority** for Hermes handoff.
- **Build:** the first-principles review of each fleet agent (Verifier, Researcher, Builder, Scribe, Designer-proposed) should be on a 6-month cadence. Codify in `agent.md`. Low-effort, structural.
- **Content:** the "first principles vs analogy" framing is the strongest available content frame. The Scribe should write a 1-page piece titled "Why we don't add features just because everyone else does." Scribe's strongest available frame.
- **Watch:** auto-harness optimization (LLM optimizes its own harness — 76.4% TerminalBench result), first-principles evals (rubric derived from axioms), scaffolding-removal discipline (Anthropic pattern).
- **Verify:** the "lattice is the fleet's value-add" claim is original to this dossier. Cross-check against Munger's primary writings before promoting to content.

## Routing history

| Date | Routed to | Item | Outcome |
|------|-----------|------|---------|
| 2026-06-04 | queue/mavis-handoff.md | dossier ready | Pending |
| 2026-06-04 | knowledge/sources.jsonl | src-2026-06-04-067 through src-2026-06-04-101 | Appended |

---

*First principles is the epistemology the harness engineering applies. When the Verifier flags a weak claim, the question is: what is the irreducible evidence? When the Builder over-engineers, the question is: what is the irreducible capability? When the Scribe frames a topic, the question is: what is the irreducible insight? The discipline compounds.*
