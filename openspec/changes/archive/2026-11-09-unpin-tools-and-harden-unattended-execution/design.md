# Design: Unpin Dev Tooling and Harden Unattended Privilege-Free Execution

## 1. Context & Motivation

Scheduled background maintenance workflows across `shb-schedule` (DBOS engine) and `launchd` must run unattended without human intervention, modal OS prompts, or terminal hangs.
Two operational deficiencies were identified:
1. **Tool Pinning Inflexibility**: Exact version pinning (e.g. `graphifyy==0.9.95`) caused `uv tool upgrade` to silently no-op with `hint: ... is pinned ... reinstall with @latest`, leaving tools out of date. All standalone tools must dynamically track `@latest` with automatic unpin recovery.
2. **Interactive & Privilege Gating**: Scheduled runs degrade or stall when encountering privilege boundaries or package manager collisions:
   - `mas upgrade 747648890` (Telegram) fails daily with installer receipt errors because `/Applications/Telegram.app` is already managed by Homebrew Cask, violating single-authority rules and risking Apple ID credential dialogs.
   - Background runners must never invoke `sudo` or block on `stdin`.
   - Updating Mach-O binaries invalidates macOS TCC permissions unless application bundles (`client_type = 0`, `CFBundleIdentifier`) and persistent code-signing identities (`Developer Agent Code Signing`) are enforced.

## 2. Architecture of Unpinned Modern Tooling

### Floating `@latest` Specifications
All standalone tool manifests (`platform/openspec-store/config/uv-tools.json`, `npm-global-tools.json`) declare `"version": "latest"`.

### Dynamic Discovery & Automatic Unpin Recovery
In `shb_schedule.workflows.workstation_update`:
When `uv tool upgrade -- <tool>` outputs `"is pinned"` or `"Nothing to upgrade (hint: ... reinstall with @latest)"`, the step automatically runs:
```python
subprocess.run([uv_bin, "tool", "install", "--upgrade", f"{tool_name}@latest"], ...)
```
In `workstation-daily-update.sh`:
Stage 4 executes `uv tool upgrade --all`. If pinned tools are reported, it extracts the tool names and runs `uv tool install --upgrade <tool>@latest`.

## 3. Architecture of Non-Interactive & Privilege-Free Execution

### Non-Interactive Environment Invariants
All background runners must inject strict non-interactive flags:
```python
env["CI"] = "1"
env["NONINTERACTIVE"] = "1"
env["DEBIAN_FRONTEND"] = "noninteractive"
env["HOMEBREW_NO_AUTO_UPDATE"] = "1"
env["HOMEBREW_NO_INSTALL_CLEANUP"] = "1"
env["HOMEBREW_NO_INTERVENTIONS"] = "1"
env["PIP_NO_INPUT"] = "1"
env["NPM_CONFIG_YES"] = "true"
```
All subprocess invocations must redirect `stdin` from `/dev/null` (`stdin=subprocess.DEVNULL` / `< /dev/null`).

### Single Authority Enforcement (MAS vs Cask)
Before running `mas upgrade`, the runner queries `brew list --cask`. Any application managed by Homebrew Cask (e.g. `telegram`) is skipped by MAS, preventing package manager collisions and installer receipt failures.

### Zero-Sudo / User-Space Confinement
All developer tools reside in user-writable paths (`~/.local/bin`, `~/.npm-global`, `~/.bun`, `/opt/homebrew`). Scheduled maintenance never invokes `sudo`. Any step requesting privilege elevation fails fast with `SKIPPED`.

### macOS TCC Invariants & Code Signing
- Supervisor application bundles (`client_type = 0`, `CFBundleIdentifier`) hold system permissions (`kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, `kTCCServiceSystemPolicyAllFiles`).
- Updated Mach-O agent binaries are re-signed post-upgrade using the persistent local certificate `Developer Agent Code Signing`. Because the leaf hash and identifier remain constant across upgrades, `tccd` preserves existing grants with zero user prompts.
