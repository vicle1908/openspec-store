# Tasks

## 1. Provider Adapter Container Drainage & LaunchAgent Unload

- [ ] 1.1 Drain `claude-code-provider-adapter-adapter-1` container via `docker compose down` in `platform/claude-code-provider-adapter`.
- [ ] 1.2 Bootout and unload LaunchAgent `com.workspace.claude-code-provider-adapter` from user launchd session `gui/502`.
- [ ] 1.3 Disable LaunchAgent plist file at `~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist`.

## 2. Workstation Scripts & Watchdog Streamlining

- [ ] 2.1 Update `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh` to retain strictly `~/Omniroute`.
- [ ] 2.2 Remove port 8788 health probe block from `~/Developer/scripts/omniroute-watchdog.sh`.
- [ ] 2.3 Verify `docker-service.sh up`, `drain`, and `status` operate cleanly without adapter references.

## 3. Claude Code & Agent Launcher Reconciliation

- [ ] 3.1 Reconcile `cockpit()` in `~/.zshrc` and `~/.claude/profiles/cockpit.json` to eliminate port 8788 dependency.
- [ ] 3.2 Smoke test `omniroute`, `shopapikey`, and `cockpit` launchers from interactive shell.

## 4. Documentation, Spec Sync & Verification

- [ ] 4.1 Update ecosystem wiki entity pages `docker-workstation.md` and `omniroute.md`.
- [ ] 4.2 Compile execution verification evidence in `evidence.md`.
- [ ] 4.3 Validate change strictly via `openspec validate --strict --json --store openspec-store`.
