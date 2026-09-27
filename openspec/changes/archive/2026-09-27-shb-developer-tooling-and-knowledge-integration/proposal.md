# Proposal: SHB Developer Tooling and Knowledge Infrastructure Integration

## Why

The Saigon - Hanoi Commercial Joint Stock Bank (SHB) ecosystem comprises 12 autonomous Git repositories under `~/Developer/shb/`, but previously lacked standardized in-repo code intelligence (`.gitnexusrc`), automated AST knowledge graphs (`graphify-out/`), full-featured episodic memory flags, and verified Notion workspace CLI toolchains. Establishing unified developer tooling and local-first knowledge extraction ensures AI coding agents and human engineers navigate, query, and maintain high-compliance banking codebases with zero drift and full structural context.

## What Changes

- Provision standardized `.gitnexusrc` configuration files across all 12 SHB repositories with Ollama `nomic-embed-text` (768-dim) local embedding parameters.
- Configure repository `.gitignore` files to quarantine `.gitnexus/` vector databases while tracking AST knowledge graphs in `graphify-out/graph.json` (excluding date-stamped snapshots `graphify-out/20*/`).
- Install Graphify Git merge drivers and `post-commit` hooks in each repository, index local AST graphs, and register all 12 repositories into the global workspace knowledge graph (`~/.graphify/global-graph.json`).
- Upgrade and verify developer toolchains:
  - `ntn` (Notion CLI Beta) upgraded to `v0.23.10` with active workspace and Workers/Public API access validated.
  - `graphify` upgraded to `0.9.69` with complete optional extras (`graphifyy[all,postgres]`) and refreshed platform skills across all 10 agent runtimes.
  - `gitnexus` verified at `v1.6.12` with LadybugDB, vector extensions, and full-text search.
  - `agentmemory` upgraded to `0.9.29` with full B+ feature flags enabled (`AGENTMEMORY_AUTO_COMPRESS`, `AGENTMEMORY_SLOTS`, `AGENTMEMORY_REFLECT`, `AGENTMEMORY_ALLOW_AGENT_SDK`) and all 9/9 diagnostics passing.
- Update `shb-ecosystem-tooling` canonical specification to enforce in-repo knowledge infrastructure and toolchain standards across the SHB organization.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `shb-ecosystem-tooling`: Extends tooling and code intelligence requirements to mandate `.gitnexusrc` configuration, `.gitignore` hygiene, Graphify hook and global graph registration, and modernized developer tooling baselines.

## Impact

- **Repositories**: All 12 SHB repositories (`shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-browser-cli`, `shb-ai-review`, `shb-webhook-receiver`, `shb-jira-tools`, `shb-mcp-servers`, `shb-observability`, `shb-tools`).
- **Disk & Git**: ~88MB tracked graph data; `.gitnexus/` LadybugDB directories safely ignored.
- **Agent Workflows**: All coding agents (Hermes, Claude Code, Codex, Pi, OpenCode) gain instant cross-repository structural navigation, blast radius calculation, and semantic code search.
