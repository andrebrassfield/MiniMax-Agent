---
type: capture
created: 2026-06-02T18:30:00+00:00
source: crucible-synthetic
category: technical
tags: [crucible, technical, synthetic, m3-eval-lab]
---

# CRDTs for Collaborative Vault Editing

The vault is currently a git-tracked directory of markdown files. If two people (or two agents) edit the same note simultaneously, we get merge conflicts on the prose. For sections (## headings), the conflict is recoverable (keep both, human resolves). For inline edits within a paragraph, the conflict is ugly.

Three approaches:
1. **Git merge with hunks** — current approach, manual resolution, lossless but slow.
2. **Operational transform (OT)** — like Google Docs; requires a central server to serialize operations.
3. **CRDTs (Conflict-free Replicated Data Types)** — like Figma, Riak, Automerge; no central server, eventually consistent, semantically lossless.

For an Obsidian-style vault, the natural unit of CRDT is the **section**. Each `## H2` heading delimits a CRDT region. Within a section, edits are character-level CRDTs. Cross-section edits don't conflict (the section IDs are stable).

The library options:
- **Yjs** — battle-tested, used by Figma, Affine. Tree-based, integrates with markdown via y-markdown.
- **Automerge** — CRDT-native, more academic, slower convergence.
- **Diamond Types** — newest, fastest, alpha-quality.

I'm leaning Yjs because it's the most mature. The integration would be:
- Replace plain `*.md` files with `*.md` (text) + `.yjs` (binary state)
- A small daemon watches the vault and applies remote Yjs updates
- On save, export the merged state back to `*.md`

The killer feature: **two agents can edit the same note simultaneously, in their own context windows, and the merge is automatic.** That unlocks the MycelialResolver's parallel-routing vision in a way that git-merge can't.

But the cost is high: every agent now needs to be Yjs-aware. And the binary `.yjs` files clutter the vault.

Worth doing? Or is the right answer "agents should never edit the same file" and we use file-level locking?
