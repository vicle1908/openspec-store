# Tasks

## 1. Register Cockpit Provider Node in OmniRoute

- [x] 1.1 Verify Cockpit provider node `openai-compatible-responses-cockpit` and connection in OmniRoute's database.
- [x] 1.2 Verify `cockpit/gpt-5.6-luna`, `cockpit/gpt-6-astra`, `cockpit/gpt-6.1-sol`, `cockpit/gpt-5.6-sol`, and `cockpit/gpt-5.6-terra` appear in OmniRoute's live catalog.
- [x] 1.3 Smoke test native Anthropic Messages request to `http://127.0.0.1:20129/v1/messages` with model `cockpit/gpt-5.6-luna`.

## 2. Reconcile Claude Code Launcher & Profile

- [x] 2.1 Update `~/.claude/profiles/cockpit.json` with `ANTHROPIC_BASE_URL: http://localhost:20129`, model `cockpit/gpt-5.6-luna`, and `apiKeyHelper` pointing to `omniroute-key.sh`.
- [x] 2.2 Update `cockpit()` function in `~/.zshrc` to target `http://localhost:20129`.
- [x] 2.3 Smoke test `omniroute`, `shopapikey`, and `cockpit` launchers from interactive zsh.

## 3. Provider Adapter Container Drainage & LaunchAgent Unload

- [x] 3.1 Drain `claude-code-provider-adapter-adapter-1` container via `docker compose down` in `platform/claude-code-provider-adapter`.
- [x] 3.2 Bootout and unload LaunchAgent `com.workspace.claude-code-provider-adapter` from user launchd session `gui/502`.
- [x] 3.3 Move/disable LaunchAgent plist file at `~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist`.

## 4. Workstation Scripts & Watchdog Streamlining

- [x] 4.1 Update `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh` to retain strictly `~/Omniroute`.
- [x] 4.2 Remove port 8788 health probe block from `~/Developer/scripts/omniroute-watchdog.sh`.
- [x] 4.3 Verify `docker-service.sh up`, `drain`, and `status` operate cleanly without adapter references.

## 5. Documentation, Spec Sync & Verification

- [x] 5.1 Update ecosystem wiki entity pages `docker-workstation.md` and `omniroute.md`.
- [x] 5.2 Compile execution verification evidence in `evidence.md`.
- [x] 5.3 Validate change strictly via `openspec validate --strict --json --store openspec-store`.
