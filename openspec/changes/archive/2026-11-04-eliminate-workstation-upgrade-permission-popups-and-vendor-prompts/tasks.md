# Tasks: Eliminate Workstation Upgrade Permission Popups and Vendor Prompts

## 1. Helper Script Modernization in `docker-service.sh`

- [x] 1.1 Remove obsolete `is_vmnetd_up()`, `app_vmnetd`, `set-vmnetd`, and `launchctl kickstart system/com.docker.vmnetd` from `/Users/androidteam/Developer/scripts/docker-service.sh`.
- [x] 1.2 Update `ensure_helpers()` in `docker-service.sh` to call `/Applications/Docker.app/Contents/MacOS/install remove-vmnetd` and configure `com.docker.socket` via `install config --user "${USER:-$(id -un)}"` and `socket-symlink-on-startup`.
- [x] 1.3 Sync changes to `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh` and verify identical diff parity.

## 2. Specification & Validation

- [x] 2.1 Author delta specification in `specs/workstation-remote-and-agent-permissions/spec.md` establishing requirements for non-interactive privileged helper provisioning and eliminating obsolete `vmnetd` checks.
- [x] 2.2 Validate change artifacts via `openspec validate eliminate-workstation-upgrade-permission-popups-and-vendor-prompts --store openspec-store --strict`.

## 3. End-to-End Verification & Archival

- [x] 3.1 Execute `docker-service.sh status` and `docker-service.sh restart` with non-interactive verification.
- [x] 3.2 Verify system logs show zero `SecurityAgent.ExecuteWithPrivileges` or `kTCCServiceAppleEvents` events during helper checks.
- [x] 3.3 Run `openspec-store` test suite (`pytest`) and `shb-schedule` test suite (`uv run pytest -q`).
- [x] 3.4 Archive OpenSpec change, commit all repositories, and persist memories.
