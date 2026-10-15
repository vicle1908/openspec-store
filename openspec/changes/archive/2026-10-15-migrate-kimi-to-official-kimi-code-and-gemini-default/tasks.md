# Tasks

## 1. Homebrew Deprecation & Official Standalone Installation

- [x] 1.1 Uninstall outdated Homebrew `kimi-code` (v2.1.1) formula and purge ad-hoc symlinks
- [x] 1.2 Install official Moonshot AI standalone native arm64 binary (v2.2.0) into `~/.kimi-code/bin/kimi` via official installer
- [x] 1.3 Configure consistent PATH export `export PATH="$HOME/.kimi-code/bin:$PATH"` across `~/.zprofile` and `~/.zshrc`
- [x] 1.4 Verify single-owner resolution via `which -a kimi` and version check (`kimi --version` = 2.2.0)

## 2. Legacy Migration & Configuration Hardening

- [x] 2.1 Clean `.DS_Store` metadata artifacts in `~/.kimi/sessions` and run `kimi migrate --run`
- [x] 2.2 Verify migration completion marker in `~/.kimi-code/migration-report.json`
- [x] 2.3 Harden `~/.kimi-code/config.toml` permissions to mode `0600`

## 3. OmniRoute Gemini Combo Default Model Routing

- [x] 3.1 Define `gemini-3.8-flash-high` model entry in `~/.kimi-code/config.toml` with 1,000,000 context limit and thinking/tool_use capabilities
- [x] 3.2 Set `default_model = "gemini-3.8-flash-high"` backed by provider `omniroute-anthropic` (`http://localhost:20128`)
- [x] 3.3 Validate configuration health via `kimi doctor` and `kimi provider list`

## 4. End-to-End Verification & Spec Synchronization

- [x] 4.1 Execute non-interactive prompt test `kimi -p "reply only: pong"`
- [x] 4.2 Verify OmniRoute gateway logs confirming upstream model execution and token generation
- [x] 4.3 Record verification evidence ledger in `evidence.md`
- [x] 4.4 Synchronize delta specs to canonical specs in `platform/openspec-store`
