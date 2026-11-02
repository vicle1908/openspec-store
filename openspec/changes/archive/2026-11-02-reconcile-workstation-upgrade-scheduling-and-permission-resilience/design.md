# Design: Reconcile Workstation Upgrade Scheduling and Permission Prompt Resilience

## Architecture Overview

```
                      Scheduled / On-Demand Pipeline Trigger
                                        │
             ┌──────────────────────────┴──────────────────────────┐
             ▼                                                     ▼
┌───────────────────────────────┐               ┌─────────────────────────────────────┐
│ shb-schedule (Durable DBOS)   │               │ workstation-daily-update.sh         │
│ step_homebrew_update()        │               │ Stage 1 / Stage 7 agent CLIs        │
└────────────┬──────────────────┘               └──────────────────┬──────────────────┘
             │                                                     │
             ├─────────────────────────────────────────────────────┤
             │
             ▼
   [1. Cask Discovery]
     brew outdated --greedy --json=v2
     ├── Formulae: ast-grep, qwen-code, etc.
     └── Casks: docker-desktop, chatgpt, zed, tailscale-app, etc.
             │
             ▼
   [2. Process Safety & POSIX Signal Drain]
     CASK_PROCESS_NAMES map audit:
     ├── Running? → Record in casks_skipped_running (unattended safe deferral)
     └── Manual / Drain mode? → pkill -TERM <proc> (NO osascript / AppleEvents)
             │
             ▼
   [3. Non-Interactive Sub-Pipelines]
     ├── docker-desktop: docker-service.sh stop (drain) -> brew upgrade -> start/up
     ├── ntn: curl -fsSL https://ntn.dev/install.sh | bash (replaces no-op ntn update)
     └── cloudflare-warp: non-interactive uninstaller flag preservation
             │
             ▼
   [4. Integrity & Provenance Verification]
     ├── tcc_provenance.py --bundles (verify client_type=0 for all 8 bundles)
     └── verify-workstation-toolchain.py --json (5/5 checks PASS)
```

## Detailed Component Design

### 1. Greedy Cask Audit in `shb_schedule.workflows.workstation_update`
- Modify `step_homebrew_update()` in `workstation_update.py` to query `brew outdated --greedy --json=v2`.
- Expand `CASK_PROCESS_NAMES`:
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
  }
  ```
- Retain the non-disruptive guarantee: when any process associated with a cask is running, the cask is recorded in `casks_skipped_running` and skipped.

### 2. POSIX Signal-Based Process Termination
- In automated scripts and runners, replace `osascript -e 'quit app "..."'` with `pkill -TERM -x "<name>"` followed by a bounded grace period (default 5s) and `kill -0` checks.
- This prevents `tccd` from raising `Prompting policy for hardened runtime; service: kTCCServiceAppleEvents requires entitlement com.apple.security.automation.apple-events`.

### 3. Non-Interactive Agent CLI Updates
- Update `STATIC_AGENT_COMMANDS["ntn"]` to:
  ```python
  "ntn": ["bash", "-c", 'curl -fsSL https://ntn.dev/install.sh | NTN_INSTALL_DIR="$HOME/.local/bin" bash'],
  ```
- Ensure execution uses `timeout=180` and suppresses interactive prompts.

### 4. TCC Invariant & Attribution Verification
- Re-assert that all 8 canonical agent bundles (`org.python.python`, `com.stablyai.orca`, `com.trycua.driver`, `com.electron.goose`, `ai.opencode.desktop`, `com.openai.codex`, `com.nousresearch.hermes`, `org.p0deje.Maccy`) must maintain `client_type = 0` in `TCC.db`.
- Post-upgrade checks run `tcc_provenance.py --bundles` to fail closed if any bundle signature or grant drifts.
