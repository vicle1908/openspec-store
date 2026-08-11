# Tasks: auto-start-claude-code-provider-adapter

## Phase 1: Wrapper Script and LaunchAgent

- [ ] 1.1 Write `start-adapter.sh` in adapter repo: bounded Docker readiness retry (120s, 2s interval), `.env` existence check (no content print), `docker compose up -d --remove-orphans`
- [ ] 1.2 Write LaunchAgent plist: `com.workspace.claude-code-provider-adapter`, `RunAtLoad=true`, `KeepAlive=false`, absolute paths for `WorkingDirectory`, `ProgramArguments`, `StandardOutPath`, `StandardErrorPath`
- [ ] 1.3 Write `scripts/install-launchagent.sh`: copies plist to `~/Library/LaunchAgents/`, runs `launchctl bootstrap gui/$(id -u)`
- [ ] 1.4 Write `scripts/uninstall-launchagent.sh`: `launchctl bootout gui/$(id -u)/com.workspace.claude-code-provider-adapter`, removes plist
- [ ] 1.5 Write `scripts/adapter-status.sh`: checks `launchctl list` + `docker compose ps` + `curl /health`

## Phase 2: Validation

- [ ] 2.1 `plutil -lint` on plist → no errors
- [ ] 2.2 `bash -n start-adapter.sh` → no syntax errors
- [ ] 2.3 `openspec validate auto-start-claude-code-provider-adapter --store openspec-store`

## Phase 3: Live Testing

- [ ] 3.1 Run `install-launchagent.sh` → LaunchAgent loaded
- [ ] 3.2 Run `adapter-status.sh` → container healthy
- [ ] 3.3 `docker compose down` → container removed
- [ ] 3.4 Invoke `start-adapter.sh` manually → container recreated, health 200
- [ ] 3.5 Run `uninstall-launchagent.sh` → LaunchAgent unloaded
- [ ] 3.6 Verify `.env` not printed anywhere in logs or output

## Phase 4: Documentation and Commit

- [ ] 4.1 Update adapter repo `README.md` with auto-start section
- [ ] 4.2 Commit adapter repo
- [ ] 4.3 Commit openspec-store change
- [ ] 4.4 Final `openspec validate`

## Rollback

- [ ] R.1 Remove LaunchAgent via `launchctl bootout`
- [ ] R.2 Remove plist from `~/Library/LaunchAgents/`
- [ ] R.3 Remove `start-adapter.sh` and `scripts/` from adapter repo
- [ ] R.4 `docker compose down` to stop container
