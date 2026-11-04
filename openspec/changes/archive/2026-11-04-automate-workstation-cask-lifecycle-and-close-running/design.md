# Design: Active Workstation Cask Lifecycle Management

## 1. Context & Architecture

Workstation automation in `shb_schedule.workflows.workstation_update` and `workstation-daily-update.sh` previously implemented passive deferral: any outdated cask whose process matched `CASK_PROCESS_NAMES` was skipped and recorded under `casks_skipped_running`.

Because background daemons (Tailscale, Docker, Cloudflare WARP, cloud sync agents, and developer utilities) run 24/7, passive deferral resulted in permanent non-upgrading of these critical packages during unattended 08:00 AM runs.

This design introduces **Active Graceful Lifecycle Management**:
1. Outdated casks are evaluated via `brew outdated --greedy --json=v2`.
2. Any running processes belonging to outdated casks are terminated gracefully using POSIX signals.
3. Special stateful services (`docker-desktop`) drain compose stacks before shutdown.
4. Cask upgrades execute non-interactively with standard input closed (`subprocess.DEVNULL`).
5. Applications registered in `CASK_RELAUNCH_APPS` are relaunched in the background immediately after successful upgrade.
6. Execution telemetry tracks `casks_updated` and `casks_restarted`.

## 2. Process Termination & Relaunch Specifications

### 2.1 POSIX Termination Helper
To eliminate `kTCCServiceAppleEvents` prompts triggered by `osascript`, process closure relies exclusively on POSIX signals:
```python
def terminate_cask_processes(process_names: tuple[str, ...], timeout: float = 6.0) -> bool:
    # 1. Send SIGTERM to all matched processes
    for proc in process_names:
        subprocess.run(["pkill", "-TERM", "-x", proc], capture_output=True)
    
    # 2. Poll pgrep up to timeout
    t_end = time.monotonic() + timeout
    while time.monotonic() < t_end:
        alive = any(
            subprocess.run(["pgrep", "-x", proc], capture_output=True).returncode == 0
            for proc in process_names
        )
        if not alive:
            return True
        time.sleep(0.5)
        
    # 3. Force SIGKILL fallback if unresponsive
    for proc in process_names:
        subprocess.run(["pkill", "-KILL", "-x", proc], capture_output=True)
    return True
```

### 2.2 Relaunch Manifest (`CASK_RELAUNCH_APPS`)
Background utilities and persistent daemons are mapped to their Application bundle names:
```python
CASK_RELAUNCH_APPS: dict[str, str] = {
    "tailscale-app": "Tailscale",
    "cloudflare-warp": "Cloudflare WARP",
    "google-drive": "Google Drive",
    "onedrive": "OneDrive",
    "orca": "Orca",
    "chatgpt": "ChatGPT",
    "realvnc-connect-viewer": "VNC Viewer",
}
```

### 2.3 Stateful Container Coordination (`docker-desktop`)
`docker-desktop` requires container lifecycle coordination:
1. Pre-upgrade: `~/Developer/scripts/docker-service.sh stop` (drains registered compose stacks).
2. Upgrade: `brew upgrade --cask -- docker-desktop`.
3. Post-upgrade: `docker-service.sh start` followed by `docker-service.sh up`.

## 3. Telemetry & Invariants
- `step_homebrew_update()` returns `casks_restarted: list[str]` alongside `casks_updated: list[str]`.
- All `brew upgrade --cask` executions supply `stdin=subprocess.DEVNULL` to prevent blocking on vendor uninstaller stdin prompts.
- Preserves permanent `client_type = 0` TCC bundle attribution.
