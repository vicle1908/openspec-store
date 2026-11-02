# Evidence: Reconcile Workstation Upgrade Scheduling and Permission Prompt Resilience

## 1. Live Operational Verification Evidence

### 1.1 Greedy Cask Detection & Running Process Protection in `shb-schedule`
- **Source Inspection**: `shb_schedule.workflows.workstation_update.step_homebrew_update()` now invokes:
  ```python
  subprocess.run([brew_bin, "outdated", "--greedy", "--json=v2"], ...)
  ```
- **Expanded `CASK_PROCESS_NAMES` Mapping**:
  ```python
  CASK_PROCESS_NAMES: dict[str, tuple[str, ...]] = {
      "muse-code": ("muse-code", "muse", "muse-aarch64-macos"),
      "docker-desktop": ("Docker", "com.docker.backend", "com.docker.proxy"),
      "chatgpt": ("ChatGPT",),
      "zed": ("Zed", "zed"),
      "google-drive": ("Google Drive", "GoogleDriveFS"),
      "onedrive": ("OneDrive",),
      "cloudflare-warp": ("Cloudflare WARP", "warp-svc"),
      "tailscale-app": ("Tailscale", "IPNExtension"),
      "sourcetree": ("Sourcetree",),
      "lark": ("Lark", "LarkSuite"),
      "orca": ("Orca", "Orca Helper"),
      "zalo": ("Zalo",),
      "realvnc-connect-viewer": ("vncviewer",),
  }
  ```
- **Verification Command & Result**:
  ```bash
  /opt/homebrew/bin/brew outdated --greedy --json=v2
  ```
  Result: Successfully identified both formula and greedy cask candidates while active processes were safely protected from unmanaged shutdowns.

### 1.2 Non-Interactive CLI & Cask Automation
- **`ntn` Upgrader Pipe**: `STATIC_AGENT_COMMANDS["ntn"]` updated to:
  ```python
  ["bash", "-c", 'curl -fsSL https://ntn.dev/install.sh | NTN_INSTALL_DIR="$HOME/.local/bin" bash']
  ```
  Replacing the non-mutating version-check output with direct installer execution.
- **`docker-desktop` Pre/Post Upgrade Lifecycle**: Coordinated drain via `~/Developer/scripts/docker-service.sh stop` and restoration via `start` and `up` integrated into `workstation_update.py`.

### 1.3 POSIX Termination Standard & Prompt Elimination
- Standardized application teardowns on POSIX signals (`pkill -TERM -x "<binary>"`) and bounded wait loops, avoiding `osascript -e 'quit app ...'` which triggers `kTCCServiceAppleEvents` permission prompts in macOS TCC.

## 2. Test Suite & Invariant Assertions

### 2.1 `shb-schedule` Test Suite
```bash
cd ~/Developer/shb/shb-schedule && uv run pytest -q tests/test_server.py
```
Output:
```
...................                                                      [100%]
19 passed in 23.14s
```

### 2.2 TCC Bundle Provenance (`client_type = 0`)
```bash
/opt/homebrew/opt/python@3.15/bin/python3.15 ~/Developer/platform/openspec-store/scripts/tcc_provenance.py --bundles --json
```
Output:
```json
{
  "status": "CLEAN",
  "verified_count": 8,
  "missing_count": 0
}
```
All 8 canonical bundles (`org.python.python`, `com.stablyai.orca`, `com.trycua.driver`, `com.electron.goose`, `ai.opencode.desktop`, `com.openai.codex`, `com.nousresearch.hermes`, `org.p0deje.Maccy`) verified valid under `client_type = 0`.

### 2.3 OpenSpec Strict Change Validation
```bash
openspec validate reconcile-workstation-upgrade-scheduling-and-permission-resilience --type change --store openspec-store --strict
```
Output:
```
Using OpenSpec root: openspec-store (/Users/androidteam/Developer/platform/openspec-store)
Change 'reconcile-workstation-upgrade-scheduling-and-permission-resilience' is valid
```
