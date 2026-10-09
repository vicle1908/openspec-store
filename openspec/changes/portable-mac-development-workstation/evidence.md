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
- Newman/Bruno: Newman resolves from `/opt/homebrew/bin` at 6.2.2; Bruno resolves from `~/.local/bin` at 4.2.0. This differs from the documented isolated-toolchain matrix and requires reconciliation.
- Scheduled updater: launchd job is enabled and loaded with state `not running` between scheduled executions.
- Docker: `desktop-linux` context is active. Protected Compose volumes `omniroute_omniroute-data` and `omniroute-redis-data` exist and are inspectable.
- AgentMemory: package metadata `@agentmemory/agentmemory` 0.9.30 pins iii dependencies 0.22.1, but `/agentmemory/health` returned HTTP 404. Legacy `iii` process PID 22310 owns ports 3111 and 49134; service health is blocked by runtime/port conflict.

## Remaining blockers

1. GitNexus active path reconciliation is complete and verified against native CLI and MCP stdio protocol.
2. Reconcile Newman/Bruno documented ownership and versions with their actual active paths.
3. Resolve or explicitly reclassify the AgentMemory runtime conflict before claiming healthy knowledge tooling.
4. A physical second-Mac execution has not been performed; the runbook is ready for that external gate, not evidence of successful secondary-host execution.

This evidence records observed state and does not claim implementation completeness beyond the checks listed above.
