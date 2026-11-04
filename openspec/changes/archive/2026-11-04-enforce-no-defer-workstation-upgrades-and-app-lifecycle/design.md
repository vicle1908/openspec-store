# Design: Enforce Zero-Deferral Workstation Upgrades and Comprehensive Application Lifecycle

## 1. Context & Architecture

Workstation automation in `shb_schedule.workflows.workstation_update` and `workstation-daily-update.sh` historically supported passive deferral mechanisms:
- `step_homebrew_update`: Recorded running GUI applications in `casks_skipped_running` and skipped upgrading them.
- `step_mas_update`: Recorded running App Store apps in `skipped_running` and large packages in `skipped_large_bundle` (e.g. Xcode `497799835`).
- `workstation-daily-update.sh`: Native fallback runner lacked Mac App Store integration and relied on passive deferral during cask updates.

This design establishes a **Comprehensive Zero-Deferral Policy**: every outdated package and application across Homebrew formulae, Homebrew casks, Mac App Store, Bun globals, uv tools, npm globals, and coding agent CLIs is upgraded during maintenance runs without manual deferral.

## 2. Core Lifecycle Mechanisms

### 2.1 POSIX Process Teardown & Avoidance of AppleEvents
To eliminate `kTCCServiceAppleEvents` prompts in macOS TCC, applications are closed exclusively via POSIX signals:
```python
def terminate_cask_processes(process_names: tuple[str, ...], timeout: float = 6.0) -> bool:
    for proc in process_names:
        subprocess.run(["pkill", "-TERM", "-x", proc], capture_output=True)
    t_end = time.monotonic() + timeout
    while time.monotonic() < t_end:
        alive = any(
            subprocess.run(["pgrep", "-x", proc], capture_output=True).returncode == 0
            for proc in process_names
        )
        if not alive:
            return True
        time.sleep(0.5)
    for proc in process_names:
        subprocess.run(["pkill", "-KILL", "-x", proc], capture_output=True)
    return True
```

### 2.2 Active Graceful Lifecycle for Mac App Store (`step_mas_update`)
- Remove passive skipping of running apps (`skipped_running`).
- If an outdated Mac App Store application is running (e.g., `Telegram 2`, `Telegram`), gracefully terminate its process via `pkill -TERM -x <app_name>`.
- Upgrade the application using `mas upgrade <app_id>` (with generous 1800s timeout to accommodate large bundles such as Xcode `497799835`).
- Automatically relaunch running applications in the background post-upgrade (`open -a "<app_name>" --background`).
- Record upgraded applications in `updated` and relaunched applications in `restarted`.

### 2.3 Comprehensive Cask Application Mapping & Relaunch
Expand `CASK_PROCESS_NAMES` and `CASK_RELAUNCH_APPS` to cover all potential GUI and daemon process names across the workstation:
- Menu bar utilities and continuous daemons: `tailscale-app`, `cloudflare-warp`, `google-drive`, `onedrive`, `orca`, `chatgpt`, `realvnc-connect-viewer`.
- Desktop editors and browsers: `zed`, `lark`, `sourcetree`, `cursor`, `visual-studio-code`, `google-chrome`.

### 2.4 Sequential Runner Parity (`workstation-daily-update.sh`)
- Incorporate Mac App Store inspection and upgrade (`mas outdated` and `mas upgrade`) with stdin decoupling.
- Ensure all cask and formula commands run with `stdin < /dev/null`.
- Implement background relaunching for active daemons.

## 3. Data & Telemetry Invariants
- `step_homebrew_update()` returns `casks_restarted: list[str]`. `casks_skipped_running` evaluates to `[]`.
- `step_mas_update()` returns `restarted: list[str]`. `skipped_running` and `skipped_large_bundle` evaluate to `[]`.
- All executions preserve permanent `client_type = 0` TCC bundle attribution.
