# Tasks

## 1. Grok Homebrew Cask Migration

- [x] 1.1 Install official Homebrew cask `brew install --cask grok-build`
- [x] 1.2 Verify `which grok` resolves to `/opt/homebrew/bin/grok` and `grok --version` reports `1.0.46`
- [x] 1.3 Remove legacy symlinks in `~/.grok/bin/` (`grok`, `agent`) so all executions resolve via Homebrew

## 2. Maintenance Script Updates (Zero-Drift Parity)

- [x] 2.1 Update Stage 1 in `~/Developer/scripts/workstation-daily-update.sh` to include `brew upgrade --cask 2>&1 || true`
- [x] 2.2 Add `prime-agent:Prime Agent:update` and `grok:Grok:update` to `AGENT_CLI_COVERED` in `~/Developer/scripts/workstation-daily-update.sh` Stage 5
- [x] 2.3 Synchronously copy updates to `platform/openspec-store/scripts/workstation-daily-update.sh` and verify content hash parity via `shasum -a 256`

## 3. Verification and Evidence

- [x] 3.1 Execute `bash ~/Developer/scripts/workstation-daily-update.sh --check` and verify Stage 5 reports `prime-agent` and `grok`, and Stage 1 checks casks
- [x] 3.2 Verify `prime-agent update`, `goose --version`, and `grok --version`
- [x] 3.3 Author `evidence.md` with verifiable command outputs
