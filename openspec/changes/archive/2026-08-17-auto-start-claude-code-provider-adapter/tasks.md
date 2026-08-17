# Tasks: auto-start-claude-code-provider-adapter

## Phase 1: Wrapper Script and LaunchAgent

- [x] 1.1 Write `start-adapter.sh` in adapter repo: bounded Docker readiness retry (120s, 2s interval), `.env` existence check (no content print), `docker compose up -d --remove-orphans`, explicit PATH for launchd
- [x] 1.2 Write LaunchAgent plist: `com.workspace.claude-code-provider-adapter`, `RunAtLoad=true`, `KeepAlive=false`, absolute paths for `WorkingDirectory`, `ProgramArguments`, `StandardOutPath`, `StandardErrorPath`
- [x] 1.3 Write `scripts/install-launchagent.sh`: copies plist from `config/` to `~/Library/LaunchAgents/`, runs `launchctl bootstrap gui/$(id -u)`, idempotent bootout-before-bootstrap
- [x] 1.4 Write `scripts/uninstall-launchagent.sh`: `launchctl bootout gui/$(id -u)/com.workspace.claude-code-provider-adapter`, removes plist, stops container
- [x] 1.5 Write `scripts/adapter-status.sh`: checks `launchctl print` + `docker compose ps` + `curl /health`, explicit PATH for launchd

## Phase 2: Validation

- [x] 2.1 `plutil -lint` on plist → no errors
- [x] 2.2 `bash -n start-adapter.sh` → no syntax errors
- [x] 2.3 `openspec validate auto-start-claude-code-provider-adapter --store openspec-store`

## Phase 3: Live Testing

- [x] 3.1 Run `install-launchagent.sh` → LaunchAgent loaded (exit 0, `launchctl print` confirms state)
- [x] 3.2 Run `adapter-status.sh` → container healthy (`docker compose ps` shows `healthy`, `/health` returns 200)
- [ ] 3.3 `docker compose down` → container removed (intentionally NOT exercised — container left running)
- [x] 3.4 Wrapper script executed: logs show `Docker ready (0s)`, `.env verified`, `Adapter container started`; `launchctl last exit code = 0`
- [ ] 3.5 Run `uninstall-launchagent.sh` → LaunchAgent unloaded (intentionally NOT exercised — LaunchAgent left loaded)
- [x] 3.6 Verify `.env` not printed anywhere in logs or output (verified: scripts use `test -f` not `cat`; `adapter-status.sh` never reads `.env`; stdout/stderr logs contain no credential values)

## Phase 4: Documentation and Commit

- [x] 4.1 Update adapter repo `README.md` with Docker deployment section (shell helpers, caveats, lifecycle)
- [x] 4.2 Commit adapter repo (`3bf7b35` feat + `29b6981` PATH fix + `e1573e0` adapter-status fix)
- [x] 4.3 Commit openspec-store change (`fb6432f`)
- [x] 4.4 Final `openspec validate` → passed

## Closure Disposition

Implementation and non-destructive live verification are complete (phases 1–4).
Tasks 3.3 and 3.5 were intentionally not executed because they would stop or
remove the active installation. Rollback tasks R.1–R.4 are documented rollback
procedures, not completion criteria. All unchecked boxes are retained as honest
historical evidence and are accepted residuals at closure.

## Rollback (documented procedures — not executed during normal operation)

- [ ] R.1 Remove LaunchAgent via `launchctl bootout` (not exercised — LaunchAgent left loaded; documented procedure only)
- [ ] R.2 Remove plist from `~/Library/LaunchAgents/` (not exercised — documented procedure only)
- [ ] R.3 Remove `start-adapter.sh` and `scripts/` from adapter repo (not exercised — documented procedure only)
- [ ] R.4 `docker compose down` to stop container (not exercised — container left running; documented procedure only)
