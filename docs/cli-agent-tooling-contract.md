# CLI Agent Tooling Contract

Shared contract for all knowledge-base CLI tools. All OpenSpec changes that
modify tool versions, indexes, or generated artifacts MUST reference this
document.

## Canonical Tool Registry

### Graphify

| Field | Value |
|-------|-------|
| executable | `graphify` |
| distribution | `graphifyy` (PyPI) |
| install | `uv tool install graphifyy==<pinned>` |
| service | None (offline extractor) |
| engine | Built-in Python AST + tree-sitter |
| global graph | `~/.graphify/global-graph.json` |
| artifact root | `graphify-out/` per repository |
| supported platforms | hermes, pi, claude, codex, opencode |
| supported platforms verified | `graphify install --help` (Aug 2026) |
| version discovery | `graphify --version` |
| skill generation | `graphify install --platform <name>` |
| version marker | Pi: `.graphify_version` file; Hermes: no explicit version field |

### GitNexus

| Field | Value |
|-------|-------|
| executable | `gitnexus` |
| distribution | `gitnexus` (npm) |
| install | `npm i -g gitnexus@<pinned>` |
| service | None (local index) |
| index root | `.gitnexus/` per repository |
| freshness criterion | `json.load('.gitnexus/gitnexus.json')['lastCommit'] == git rev-parse HEAD` |
| supported agents | Pi (npm:pi-gitnexus), Claude (skills), Hermes (skill) |
| version discovery | `gitnexus --version` |
| doctor | `gitnexus doctor` (safe, read-only) |

### Agentmemory

| Field | Value |
|-------|-------|
| executable | `agentmemory` |
| distribution | `@agentmemory/agentmemory` (npm) |
| install | `npm i -g @agentmemory/agentmemory@<pinned>` |
| service | `http://localhost:3111` |
| engine | `iii`, installer-managed at `~/.agentmemory/bin/iii` |
| adapter pattern | MCP server via `mcpServers.agentmemory` in agent config |
| verified adapters | Hermes (configured) |
| optional adapters | Pi, Claude, OpenCode (available, not wired — opt-in) |
| not an adapter target | Goose (no agentmemory support) |
| version discovery | `agentmemory --version` |
| health check | `agentmemory doctor` (reads live state, safe) |
| service health | `curl localhost:3111/agentmemory/health` |

## Ownership Boundaries

| Component | Owns | Does NOT Own |
|---|---|---|
| **Graphify** | `graphify-out/` artifacts, Graphify skills (hermes/pi/claude/fable-5), `~/.graphify/global-graph.json` | `.gitnexus/`, agentmemory data, cron scheduling |
| **GitNexus** | `.gitnexus/` indexes, freshness via commit hash, pre-commit advisory hooks | `graphify-out/`, agentmemory data, cron scheduling |
| **Agentmemory** | Local memory service, `~/.agentmemory/`, adapter configs in agents | Graphify, GitNexus, MCP Router |
| **Cron** | Orchestration, scheduling, reporting only | Tool internals, data ownership |

## Noninteractive Invocation Requirements

All tools MUST support noninteractive (cron/agent) invocation:

| Requirement | Graphify | GitNexus | Agentmemory |
|---|---|---|---|
| No interactive prompts | Yes | Yes | Yes |
| No network required | Yes (extraction is offline) | Yes (local index) | Depends (compression needs LLM) |
| Bounded runtime | 30s per repo typical | 60s per repo typical | Health check: <5s |
| Exit 0 on success | Yes | Yes | Yes |
| Exit non-zero on failure | Yes | Yes | Yes |
| JSON output option | `--json` (query/explain) | Default is JSON | N/A (health endpoint) |

## Timeout Defaults

| Context | Max Runtime | Action on Timeout |
|---|---|---|
| Pre-commit hook | 5s | Exit 0 (advisory-only, never block) |
| Cron weekly freshness | 300s total | Report partial results, exit non-zero |
| Agent invocation | 120s per repo | Abort repo, continue batch |
| Skill generation | 30s per platform | Abort platform, continue others |

## Locking Requirements

| Operation | Lock Type | Scope | Rationale |
|---|---|---|---|
| Graphify batch rebuild | `shlock -f ~/.hermes/locks/graphify-build.lock` | Workspace-wide | Prevent concurrent graph corruption |
| GitNexus reindex | `shlock -f ~/.hermes/locks/gitnexus-reindex.lock` | Workspace-wide | Prevent concurrent index corruption |
| Graphify + GitNexus | Serialized (graphify first, then gitnexus) | Ordering constraint | Graphify rebuild advances HEAD; GitNexus must reindex after |
| Agentmemory restart | `agentmemory stop && agentmemory &` | Service-level | Brief downtime, safe to restart |

## Freshness Definitions

Two independent freshness metrics exist and must not be conflated:

1. **Graphify artifact freshness**: `graphify-out/graph.json` exists and was generated from the current source tree. Checked via file existence + content hash or modification time.

2. **GitNexus index freshness**: `json.load('.gitnexus/gitnexus.json')['lastCommit'] == git rev-parse HEAD`. Checked via exact commit comparison.

Cron reports MUST include both fields independently.

## Exit-Code Semantics

| Exit Code | Meaning | Caller Action |
|---|---|---|
| 0 | Success | Record result, continue |
| 1 | Tool error (bad args, missing file) | Log error, continue batch |
| 2 | Runtime error (extraction failed, index corrupted) | Log error, skip repo, continue |
| 124 | Timeout (from `timeout` wrapper) | Log timeout, skip repo, continue |
| 126/127 | Binary not found or not executable | Log missing, skip all repos |

**Special for Goose**: Goose returns exit code 0 for provider/tool failures. Automation MUST inspect `metadata.status` and validate output content — never trust exit code alone.

## Credential Redaction Rules

- Never print tokens, passwords, private keys, or connection strings in tool output or OpenSpec evidence files.
- Replace values with `<REDACTED>` in committed evidence.
- MCP tokens in configs are operational state, not secrets — but must not appear in OpenSpec artifacts, reports, or cron output.

## Rollback Requirements

Each tool upgrade MUST retain:

1. The pre-upgrade tool version and installation command.
2. A snapshot of representative graph/index statistics.
3. The pre-upgrade skill file checksums (where applicable).
4. A redacted config backup before any live mutations.

Rollback procedure: reinstall the prior pinned version, restore skill files from snapshot, re-run canary validation.

## Installed vs Configured vs Verified

| State | Meaning |
|---|---|
| **Installed** | Binary exists on PATH at a specific version |
| **Configured** | Agent config file references the tool (e.g., MCP entry, skill symlink) |
| **Verified** | End-to-end functionality tested (e.g., query returns results, health check passes) |

A tool can be installed without being configured (e.g., GitNexus in Goose).
A tool can be configured without being verified (e.g., agentmemory in Claude).

## Agent Compatibility Matrix (Verified Aug 2026)

| Agent | Graphify | GitNexus | Agentmemory | MCP Router |
|---|---|---|---|---|
| Hermes v0.20.0 | Installed + skill generated | Installed + skill present | Configured (3 refs) | Embedded |
| Pi v0.84.1 | Installed + skill generated | Installed (npm:pi-gitnexus) | Optional adapter | Via pi-mcp-adapter |
| Claude v2.1.226 | Installed + skill generated | Installed + 6 skills | Optional adapter | Via MCP |
| Goose v1.45.0 | Skill symlink exists | Not configured | Not an adapter target | stdio extension |
| OpenCode v1.18.16 | Not configured | Not configured | Optional adapter | stdio |
| Codex v0.147.0 | Installed + skill generated | Not configured | Not wired | Not configured |
| Prime Agent v0.7.1 | Not configured | Not configured | Not wired | Not configured |
| agy v1.1.11 | Not configured | Not configured | Not wired | Not configured |
