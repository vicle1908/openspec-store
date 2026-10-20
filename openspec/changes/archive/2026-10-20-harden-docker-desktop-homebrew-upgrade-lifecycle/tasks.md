# Tasks

## 1. Docker Desktop Helper Provisioning & Bash 3.2 Hardening

- [x] 1.1 Update `/Users/androidteam/Developer/scripts/docker-service.sh` to add `ensure_helpers()` before `docker desktop start` and `docker desktop restart` (provisioning `/Library/PrivilegedHelperTools/com.docker.vmnetd` and `/Library/PrivilegedHelperTools/com.docker.socket` via `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}" set-vmnetd set-docker-socket`, kickstarting `system/com.docker.vmnetd`, and clearing any `/tmp/docker-desktop-privileged*` `osascript` prompt).
- [x] 1.2 Fix macOS Bash 3.2 `set -u` empty array expansion in `cmd_drain()` and `cmd_up()` in `/Users/androidteam/Developer/scripts/docker-service.sh` using `${profile_args[@]+"${profile_args[@]}"}` so `/Users/androidteam/Developer/shb/shb-schedule` and `/Users/androidteam/Omniroute` both drain and start cleanly.
- [x] 1.3 Verify simulated Homebrew cask `uninstall` recovery by removing `com.docker.vmnetd` (`sudo -n launchctl bootout system/com.docker.vmnetd` + removing `/Library/PrivilegedHelperTools/com.docker.vmnetd` and `/Library/LaunchDaemons/com.docker.vmnetd.plist`), running `/Users/androidteam/Developer/scripts/docker-service.sh start` and `/Users/androidteam/Developer/scripts/docker-service.sh up`, and confirming via Computer Use AX (`SecurityAgent windows: []`, `"Engine running"`) and `docker-service.sh status` that all helpers and registered stacks recover with zero `SecurityAgent` dialogs.

## 2. Daily Maintenance Integration & Provenance Mirroring

- [x] 2.1 Update `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (Stage 1 Homebrew Maintenance) to invoke `/Users/androidteam/Developer/scripts/docker-service.sh start` and `/Users/androidteam/Developer/scripts/docker-service.sh up` immediately after `brew upgrade --cask` when `/Applications/Docker.app/Contents/MacOS/install` is present.
- [x] 2.2 Update `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (and unit tests) so the durable `workstation-daily-update` workflow invokes `docker-service.sh start` and `docker-service.sh up` after `brew upgrade --cask`.
- [x] 2.3 Register `/Users/androidteam/Developer/scripts/docker-service.sh` -> `scripts/docker-service.sh` (`executed`) in `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv` and synchronize byte-identical copies of `docker-service.sh` and `workstation-daily-update.sh` into `/Users/androidteam/Developer/platform/openspec-store/scripts/`.

## 3. OpenSpec Governance & Canonical Spec Sync

- [x] 3.1 Author `proposal.md`, `design.md`, `specs/docker-lifecycle/spec.md`, `specs/portable-workstation-toolchain/spec.md`, `tasks.md`, and `evidence.md` under `/Users/androidteam/Developer/platform/openspec-store/openspec/changes/harden-docker-desktop-homebrew-upgrade-lifecycle/`.
- [x] 3.2 Append the new `### Requirement:` blocks to `/Users/androidteam/Developer/platform/openspec-store/openspec/specs/docker-lifecycle/spec.md` and `/Users/androidteam/Developer/platform/openspec-store/openspec/specs/portable-workstation-toolchain/spec.md`, and validate with `openspec validate harden-docker-desktop-homebrew-upgrade-lifecycle --strict --json` and `validate-archive-readiness.py --change harden-docker-desktop-homebrew-upgrade-lifecycle --store root --strict`.
