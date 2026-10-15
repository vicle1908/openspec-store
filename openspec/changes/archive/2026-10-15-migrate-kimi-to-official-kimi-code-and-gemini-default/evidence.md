# Verification Evidence

## Kimi Code Official Migration & OmniRoute Gemini Combo Routing

### 1. Official Standalone Installation & Single-Owner Verification

- **Homebrew Uninstallation**:
  - `brew uninstall kimi-code` completed cleanly.
  - Purged `/opt/homebrew/Cellar/kimi-code` and `/opt/homebrew/bin/kimi`.
- **Official Moonshot AI Installer**:
  - Executed official `install.sh` from `https://code.kimi.com/kimi-code/install.sh`.
  - Installed native arm64 Mach-O binary `2.2.0` into `/Users/androidteam/.kimi-code/bin/kimi`.
  - Binary SHA-256: `dab42ead275f8a49e9ce30a6263f614fce5926455bed103d0d16940655619bf5`.
  - Version command: `kimi --version` → `2.2.0`.
- **PATH Resolution Consistency**:
  - `~/.zprofile`: `export PATH="$HOME/.kimi-code/bin:$PATH"`
  - `~/.zshrc`: `export PATH="/Users/androidteam/.kimi-code/bin:$PATH"`
  - Shell command resolution (`zsh -lc 'which -a kimi'`):
    ```
    /Users/androidteam/.kimi-code/bin/kimi
    ```

### 2. Legacy Migration & Config Hardening

- **Migration Execution**:
  - `kimi migrate --run` executed without errors.
  - Migrated 3 sessions, MCP servers (`mcp-router`), user history, and plans.
  - Completion marker recorded in `~/.kimi-code/migration-report.json`.
- **Configuration Permission Hardening**:
  - `ls -la ~/.kimi-code/config.toml` → mode `0600` (`-rw------- 1 androidteam staff`).

### 3. OmniRoute Gemini 3.8 Flash High Default Model Configuration

- **Configuration File (`~/.kimi-code/config.toml`)**:
  - `default_model = "gemini-3.8-flash-high"`
  - `[models.gemini-3-8-flash-high]`: `provider = "omniroute-anthropic"`, `model = "gemini-3.8-flash-high"`, `max_context_size = 1000000`, `capabilities = ["thinking", "tool_use"]`, `default_effort = "high"`.
  - `[providers.omniroute-anthropic]`: `type = "anthropic"`, `base_url = "http://localhost:20128"`.
- **Kimi Doctor Audit (`kimi doctor`)**:
  ```
  OK config.toml  /Users/androidteam/.kimi-code/config.toml
  OK tui.toml     /Users/androidteam/.kimi-code/tui.toml
  All checked config files are valid.
  ```
- **Kimi Provider Listing (`kimi provider list`)**:
  ```
  omniroute-anthropic  type=anthropic  models=3  source=inline
  Default model: gemini-3.8-flash-high
  ```

### 4. End-to-End Live Inference Proof

- **CLI Call**:
  ```bash
  kimi -p "reply only: pong"
  ```
  **Output**:
  ```
  kimi version 2.2.0
  • pong
  To resume this session: kimi -r session_4513279c-1bca-4cbb-be3b-c7ba20504934
  ```
- **OmniRoute Telemetry (`docker logs omniroute`)**:
  - Endpoint: `http://localhost:20128` (Anthropic Messages API translated to Antigravity upstream).
  - Model: `gemini-3.8-flash-high`
  - Upstream Response: `Model agy/gemini-3.8-flash-high succeeded (12739ms, 0 fallbacks)`
  - Token Accounting: `ANTIGRAVITY | in=327857 | out=118 | account=62af823b... | cache_read=325603`
