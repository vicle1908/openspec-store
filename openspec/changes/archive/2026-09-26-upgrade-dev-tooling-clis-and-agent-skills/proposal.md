# Proposal: Upgrade Dev Tooling, CLIs, Applications, and Agent Skills

## Why

A comprehensive workspace and host audit across `/Users/androidteam` and `/Users/androidteam/Developer` identified version drift, binary desync, manifest divergence, and uncoordinated daily automation across developer runtimes, coding agent engines, Homebrew casks, and cross-agent skills.

Specifically:
1. **Coding Agent Version Lag:** Claude Code (`2.1.278` vs `2.1.283`), OpenAI Codex (`0.153.0` vs `0.157.0`), OpenCode (`1.18.25` vs `1.18.32`), and Droid (`0.222.0` vs `0.227.0`) have fallen behind active upstream releases. Pi coding agent extensions (`pi-subagents`, `pi-mcp-adapter`, `pi-web-access`) are up to 10 versions behind.
2. **Research & Code Intelligence Desync:** Graphify AST engine (`0.9.65` vs `0.9.68`) has lagged downstream agent skill installations (`0.9.64` in Pi, OpenCode, and Copilot). GitNexus suffers from prefix divergence (`1.6.10` in `~/.npm-global` vs `1.6.12` in `~/.local`).
3. **Application & Cask Staleness:** 13 Homebrew casks are outdated, including core infrastructure like Docker Desktop (`4.90.0` vs `4.92.0`), Zed editor (`1.20.2` vs `1.21.0`), and networking/utility applications.
4. **Skills Manifest Desync:** `sync-workspace-agent-skills.py --check` failed because of missing workspace path resolution for the `platform/` directory layout.
5. **OpenSpec Store Validator Update:** OpenSpec CLI (`1.11.0` vs `1.13.2`) needed alignment with upstream validator rules while protecting the integrity of 400 specs and 569 archived changes.
6. **Fragmented & Broken Daily Scheduled Updates:** Two conflicting LaunchAgents (`com.user.brew-npm-update` at 08:23 AM and `com.microservices.developer-workstation-tool-update` at 09:00 AM) were running daily. Both failed due to unconstrained `npm update -g` hitting 404 on local git-installed packages (`prime-agent`), and neither covered coding agents, uv tools, skills sync, or OpenSpec validation.

## What Changes

- **Applications & Casks Modernization:**
  - Upgrade 13 Homebrew casks: `docker-desktop`, `zed`, `chatgpt`, `cleanmymac`, `onedrive`, `tailscale-app`, `gcloud-cli`, `postman-cli`, `cockpit-tools`, `copilot-cli`, `antigravity-cli`, `orca`, and `droid`.
  - Verify Docker daemon and container networking remain functional.
- **Developer Utilities & Research CLIs Alignment:**
  - Upgrade `@brightdata/cli` (`0.3.5` -> `0.3.7`), `@kilocode/cli` (`7.5.6` -> `7.8.1`), `@qoder-ai/qodercli` (`1.1.38` -> `1.1.64`), `codexuse-cli` (`6.1.0` -> `6.3.0`), and `happy` (`1.2.2` -> `1.2.5`).
  - Align `gitnexus` to `1.6.12` in `~/.npm-global`.
  - Upgrade `graphifyy` to `0.9.68` via `uv tool`.
- **Cross-Agent Skills Synchronization:**
  - Re-generate Graphify agent skills for Pi, OpenCode, and Copilot using `graphify install --platform <platform>`.
  - Fix `WORKSPACE` directory resolution in `sync-workspace-agent-skills.py` to support `platform/openspec-store`.
  - Verify `sync-workspace-agent-skills.py --check` exits cleanly with code 0.
- **Coding Agent CLIs & Extensions Upgrade:**
  - Upgrade Claude Code to `2.1.283` via native self-updater; verify `~/.zshrc` provider wrappers.
  - Upgrade `@openai/codex` to `0.157.0` and `opencode-ai` to `1.18.32` in `~/.npm-global`.
  - Upgrade Pi extensions (`pi-subagents`, `pi-mcp-adapter`, `pi-web-access`, `pi-lens`, `pi-intercom`).
  - Execute live single-shot headless PONG probes across all agents.
- **OpenSpec Store Validation Gate:**
  - Upgrade `@fission-ai/openspec` to `1.13.2`.
  - Execute pre- and post-upgrade store validation sweeps across all 400 specs to confirm zero rule regressions.
- **Unified Daily Check & Update Automation:**
  - Retire duplicate/failing LaunchAgents (`com.user.brew-npm-update` and `com.microservices.developer-workstation-tool-update`).
  - Deploy a unified daily runner `~/Developer/scripts/workstation-daily-update.sh` with `--check` and `--apply` modes.
  - Register `com.developer.workstation-daily-update.plist` scheduled daily at 08:00 AM with log rotation and status reporting.

## Capabilities

### New Capabilities
- `ecosystem-tooling-and-skills-upgrade`: Staged upgrade specifications, pre-flight safety snapshots, cross-agent skill manifest parity, post-upgrade verification probes, and unified daily automated maintenance across runtimes, CLIs, and store validators.

## Impact & Verification

- **System Stability:** Staged execution prevents cascading environment breakage.
- **Provider Passthrough:** Verifies custom model launchers (`shopapikey`, `cockpit`, `omniroute`, `droid-fable`) remain intact.
- **Skill Integrity:** Reconciles workspace skill discovery without broken symlinks.
- **Store Safety:** Zero false-positive validation errors across all 400 specs in `openspec-store`.
- **Daily Maintenance Reliability:** Eliminates the `prime-agent` npm update 404 crash and consolidates maintenance into a single, observable daily job.
