# Design: SHB Developer Tooling and Knowledge Infrastructure Integration

## Context

The SHB engineering ecosystem consists of 12 distinct Git repositories under `~/Developer/shb/`. Prior to this change, repositories lacked in-repo configuration for code intelligence (`.gitnexusrc`), automated AST knowledge graphs (`graphify-out/`), full-featured episodic memory flags, and verified Notion workspace CLI toolchains. To enable effective pair programming and autonomous execution across multiple coding agents (Hermes, Claude Code, Codex, Pi, OpenCode), local-first code intelligence and developer tools must be standardized, upgraded to their latest releases, and fully configured.

See `proposal.md` for motivation and scope boundaries.

## Goals / Non-Goals

**Goals:**
- Standardize `.gitnexusrc` in all 12 SHB repositories with Ollama `nomic-embed-text` (768-dim) local embeddings.
- Maintain `.gitignore` hygiene ensuring `.gitnexus/` vector databases remain uncommitted while `graphify-out/graph.json` is tracked.
- Automate AST graph updates with Graphify merge drivers and Git post-commit hooks in each repository.
- Register all 12 SHB repositories into the global cross-repo graph (`~/.graphify/global-graph.json`).
- Ensure all 4 developer tools (`ntn`, `graphify`, `gitnexus`, `agentmemory`) run at their latest upstream releases with all optional feature sets active.

**Non-Goals:**
- Modifying underlying SHB banking business logic, API schemas, or test suites.
- Storing unencrypted credentials, tokens, or sensitive banking connection details in version control.
- Replacing or modifying existing upstream package managers (`uv`, `npm`).

## Decisions

### Decision 1: Ollama nomic-embed-text for GitNexus Semantic Indexing
- **Rationale**: Ollama runs locally on Apple Silicon (`http://localhost:11434/v1`), providing GPU-accelerated 768-dimensional embeddings without external network roundtrips or API costs.
- **Alternatives considered**:
  - Default local ONNX (384-dim): Rejected due to lower semantic retrieval accuracy across complex Python banking domains.
  - Remote OpenAI embedding API: Rejected to prevent proprietary banking code snippets from leaking to third-party endpoints.

### Decision 2: Git Tracking of graphify-out/graph.json with 20*/ Snapshot Pruning
- **Rationale**: Tracking `graphify-out/graph.json` ensures fresh clones and automated agents immediately possess structural code graphs without running a full re-parse. Date-stamped snapshots (`graphify-out/20*/`) are ignored to keep repository size bounded.
- **Alternatives considered**:
  - Pure ephemeral graphs: Rejected because cold-start AST generation adds friction and delays agent task startups.
  - Tracking all history: Rejected because date-stamped snapshots inflate git tree by gigabytes.

### Decision 3: Launchd-Managed AgentMemory Server with B+ Feature Flags
- **Rationale**: AgentMemory provides 9/9 diagnostics passing with local observation compression, temporal graphs, reflection, and context injection. Managing via `launchd` guarantees daemon persistence across session restarts.
- **Alternatives considered**:
  - Pure in-memory SQLite without daemon: Rejected because episodic session learnings across multi-agent workflows would be lost between turns.

### Decision 4: Notion CLI (ntn) Upgrade to v0.23.10
- **Rationale**: Direct official shell installer (`curl -fsSL https://ntn.dev/install.sh | bash`) cleanly upgrades `ntn` to `v0.23.10` on `darwin-arm64`, resolving Public API and Workers capabilities.

## Risks / Trade-offs

- **[Risk] Large vector index size in repositories** → *Mitigation*: Ensure `.gitignore` explicitly ignores `.gitnexus/` across all 12 repositories before running initial analysis.
- **[Risk] Stale graph diffs during git merges** → *Mitigation*: Run `graphify hook install` in every repo to install the native git merge driver for `graphify-out/graph.json`.
- **[Risk] High memory consumption from AgentMemory compression** → *Mitigation*: Memory RSS alerts are monitored; LLM observation compression is bound to fast shopapikey cloud routing (`claude-fable`).
