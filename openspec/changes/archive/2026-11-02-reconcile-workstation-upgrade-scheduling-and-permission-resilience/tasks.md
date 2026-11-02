# Tasks: Reconcile Workstation Upgrade Scheduling and Permission Prompt Resilience

## 1. Greedy Cask Inspection & Process Safety in `shb-schedule`

- [x] 1.1 Update `step_homebrew_update()` in `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` to pass `--greedy` to `brew outdated --json=v2`, ensuring auto-updating casks are evaluated.
- [x] 1.2 Expand `CASK_PROCESS_NAMES` in `workstation_update.py` to cover `docker-desktop`, `chatgpt`, `zed`, `google-drive`, `onedrive`, `cloudflare-warp`, `tailscale-app`, `sourcetree`, and `lark` to prevent unintended shutdowns during unattended runs.
- [x] 1.3 Add pre-upgrade stack drain and post-upgrade stack startup via `~/Developer/scripts/docker-service.sh` for `docker-desktop` cask upgrades in `workstation_update.py`.

## 2. Non-Interactive CLI & App Upgrade Resilience

- [x] 2.1 Update `STATIC_AGENT_COMMANDS["ntn"]` in `workstation_update.py` to execute the official installer pipe `curl -fsSL https://ntn.dev/install.sh | NTN_INSTALL_DIR="$HOME/.local/bin" bash` so `ntn` updates apply non-interactively.
- [x] 2.2 Standardize workstation application shutdown routines on POSIX `pkill -TERM` and graceful timeout loops, eliminating `osascript` AppleEvents and preventing `kTCCServiceAppleEvents` authorization prompts.

## 3. Spec Updates & Verification

- [x] 3.1 Author delta specifications for `workstation-toolchain-inventory` and `workstation-remote-and-agent-permissions` reflecting greedy cask discovery, POSIX termination safety, and `client_type=0` permanence.
- [x] 3.2 Validate change artifacts via `openspec validate --change reconcile-workstation-upgrade-scheduling-and-permission-resilience --store openspec-store --strict`.
- [x] 3.3 Execute test suite in `shb-schedule` (`uv run pytest`) and verify TCC bundle provenance via `tcc_provenance.py --bundles`.
