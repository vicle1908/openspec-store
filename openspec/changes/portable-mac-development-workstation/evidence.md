# Evidence: portable-mac-development-workstation

## Verification scope

Read-only end-to-end verification was run after the approved Homebrew-first workstation changes. No package, service, Docker, AgentMemory, or Notion mutations were performed during this verification pass.

## Structural status

- `openspec validate portable-mac-development-workstation --strict --json --store openspec-store`: PASS.
- Current task ledger: 16/16 complete; Task 3.2 completed following verified non-destructive quarantine of `~/.local/bin/gitnexus` symlink, with active path now resolving strictly to declared npm-global owner `~/.npm-global/bin/gitnexus`.
- Archive-readiness validator: PASS (exit code 0, 16 of 16 tasks complete).

## Runtime verification

- Homebrew Bundle check: PASS; all declared Brewfile dependencies are satisfied.
- Homebrew versions: Codex Cask 0.162.0, Bun 1.4.2, Node 26.11.0, pnpm 12.10.1, uv 0.12.24, jq 1.8.2, zsh 5.9.2, libpq 18.6_1, Redis 8.10.2_1.
- Native smoke probes: Node, Bun, jq, `psql`, `redis-cli`, and isolated zsh arithmetic PASS.
- Codex: `/opt/homebrew/bin/codex` resolves to Homebrew Cask 0.162.0; npm-global and Homebrew-prefix npm Codex copies absent.
- Qoder: vendor dispatcher and `~/.local/bin/qodercli` resolve to 1.1.58; npm Qoder copies absent.
- GitNexus: Cutover verified. Active path resolves strictly to declared owner `/Users/androidteam/.npm-global/bin/gitnexus` (version 1.6.12). Native binding `lbugjs.node` loaded successfully via `gitnexus doctor`. Live stdio MCP protocol initializes cleanly, returning 17 registered tools. Non-authoritative symlink `~/.local/bin/gitnexus` safely quarantined at `~/.local/quarantine/gitnexus-symlink-rollback/gitnexus` (retaining full rollback capability without file deletion).
- Newman/Bruno: Newman resolves from `/opt/homebrew/bin` at 6.2.2 (Homebrew formula); Bruno resolves from `~/.local/bin` at 4.2.0 (isolated toolbelt entry point in `~/.local/share/home-toolchain`). Documented and aligned in `docs/mac-development-setup.md`.
- Scheduled updater: launchd job is enabled and loaded with state `not running` between scheduled executions.
- Docker: `desktop-linux` context is active. Protected Compose volumes `omniroute_omniroute-data` and `omniroute-redis-data` exist and are inspectable.
- AgentMemory: Legacy iii v0.11.2 process (PID 22310) was stopped via native `agentmemory stop --force`. Service restarted under `com.agentmemory.server` on pinned iii-engine v0.22.1. Native verification via `agentmemory status` reports `Health: ✓ healthy`, `v0.9.30 at http://localhost:3111`, 1990 sessions, 24732 observations, 196 memories, and 2743 graph nodes.

## External Gates & Remaining Considerations

- GitNexus active path reconciliation is complete and verified against native CLI and MCP stdio protocol.
- Newman and Bruno ownership paths are verified and documented in the runbook.
- AgentMemory runtime conflict is resolved; service is verified healthy under pinned iii-engine v0.22.1.
- A physical second-Mac execution has not been performed; the runbook is ready for that external gate, not evidence of successful secondary-host execution.

This evidence records observed state and does not claim implementation completeness beyond the checks listed above.
