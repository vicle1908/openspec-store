# Knowledge Context: Ecosystem Index Freshness Automation

Captured 2026-08-14 from the live workspace and official Graphify-Labs sources.

## Provider evidence

- Official upstream: https://github.com/Graphify-Labs/graphify
- Official package: PyPI `graphifyy`
- Official CLI: `graphify`
- Installed/pinned version after upgrade: `0.9.42`
- Runtime: Python `3.12.13`
- License: Apache-2.0
- GitNexus: `1.6.9`

## Upgrade evidence

- `uv tool install --python 3.12 --force 'graphifyy[all,postgres]==0.9.42'` completed successfully.
- `graphify install --strict` updated the installed Graphify skill; `.graphify_version` reports `0.9.42` in Claude, Codex, and Hermes skill copies.
- FIFO canary: `graphify extract . --code-only --no-cluster` completed with exit 0 and did not hang on a FIFO.
- Incremental canary: `graphify update .` completed with exit 0 after a same-length source rewrite.
- Full canary extraction completed with `built_at_commit` equal to the canary repository HEAD and a non-empty graph.
- `graphify-mcp --help` completed successfully.
- Active watcher is running from the upgraded uv tool environment.

## Workspace evidence

- Eighteen repositories have Graphify hook state.
- The existing Graphify tool is Graphify-Labs `graphifyy`; no alternate Graphify provider is in scope.
- `go-microservices/scripts/knowledge-tools.sh` now pins `GRAPHIFY_VERSION="0.9.42"` and `graphifyy[all,postgres]`.
- Existing worktrees are heterogeneous: most lack `.gitnexus/` and/or `graphify-out/`; the design therefore reports uninitialized worktrees instead of creating state implicitly.
- The scheduler design uses a reviewed inventory, dirty-tree guard, PID-aware locks, watcher coordination, bounded timeouts, and explicit local-hook limitations.

## Artifact alignment

- `workspace-index-freshness` is a new ADDED capability.
- `developer-code-intelligence` has a MODIFIED delta replacing the obsolete Graphify provider identity and state assumptions.
- `gitnexus-stable-contract` has an ADDED narrow authorization for the workspace-local scheduled recovery path; consumer MCP mutation remains rejected.
