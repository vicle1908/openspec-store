# Tasks: auto-start-claude-code-provider-adapter

## Phase 1: Wrapper Script and LaunchAgent

- [x] 1.1 Write `start-adapter.sh` in adapter repo: bounded Docker readiness retry (120s, 2s interval), `.env` existence check (no content print), `docker compose up -d --remove-orphans`, explicit PATH for launchd
- [x] 1.2 Write LaunchAgent plist: `com.workspace.claude-code-provider-adapter`, `RunAtLoad=true`, `KeepAlive=false`, absolute paths for `WorkingDirectory`, `ProgramArguments`, `StandardOutPath`, `StandardErrorPath`
- [x] 1.3 Write `scripts/install-launchagent.sh`: copies plist from `config/` to `~/Library/LaunchAgents/`, runs `launchctl bootstrap gui/$(id -u)`, idempotent bootout-before-bootstrap
- [x] 1.4 Write `scripts/uninstall-launchagent.sh`: `launchctl bootout gui/$(id -u)/com.workspace.claude-code-provider-adapter`, removes plist, stops container
- [x] 1.5 Write `scripts/adapter-status.sh`: checks `launchctl print` + `docker compose ps` + `curl /health`

## Phase 2: Validation

- [x] 2.1 `plutil -lint` on plist → no errors
- [x] 2.2 `bash -n start-adapter.sh` → no syntax errors
- [x] 2.3 `openspec validate auto-start-claude-code-provider-adapter --store openspec-store`

## Phase 3: Live Testing

- [ ] 3.1 Run `install-launchagent.sh` → LaunchAgent loaded (**BLOCKED**: gateway process guard blocks `launchctl bootstrap`. Must be run manually from a separate terminal.)
- [ ] 3.2 Run `adapter-status.sh` → container healthy (**blocked by 3.1**)
- [ ] 3.3 `docker compose down` → container removed (**blocked by 3.1**)
- [ ] 3.4 Invoke `start-adapter.sh` manually → container recreated, health 200 (**blocked by 3.1**)
- [ ] 3.5 Run `uninstall-launchagent.sh` → LaunchAgent unloaded (**blocked by 3.1**)
- [ ] 3.6 Verify `.env` not printed anywhere in logs or output (verified by code inspection: scripts use `test -f` not `cat`, `adapter-status.sh` never reads `.env`)

## Phase 4: Documentation and Commit

- [x] 4.1 Update adapter repo `README.md` with Docker deployment section (includes shell helpers, caveats, lifecycle)
- [x] 4.2 Commit adapter repo (`3bf7b35` feat + `29b6981` PATH fix)
- [x] 4.3 Commit openspec-store change (`fb6432f`)
- [x] 4.4 Final `openspec validate` → passed

## Rollback

- [ ] R.1 Remove LaunchAgent via `launchctl bootout` (**not exercised — LaunchAgent never loaded**)
- [ ] R.2 Remove plist from `~/Library/LaunchAgents/` (procedure documented, not exercised)
- [ ] R.3 Remove `start-adapter.sh` and `scripts/` from adapter repo (procedure documented, not exercised)
- [ ] R.4 `docker compose down` to stop container (container is running — not exercised)
