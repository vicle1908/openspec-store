# Spec Delta

## ADDED Requirements

### Requirement: Local OMP Auth-Broker and Gateway LaunchAgent Service Provisioning
On `iosteam-mac-mini`, macOS user LaunchAgents `local.shb.omp.auth-broker.plist` (binding `127.0.0.1:8765`) and `local.shb.omp.auth-gateway.plist` (binding `127.0.0.1:4000`, `--no-auth`) SHALL be provisioned under `~/Library/LaunchAgents/` and kept active via `launchctl`, establishing local OMP failover capabilities.

#### Scenario: Local OMP services are active and listening
- **WHEN** `launchctl list` and `lsof -iTCP -sTCP:LISTEN -P -n` are inspected on `iosteam-mac-mini`
- **THEN** jobs `local.shb.omp.auth-broker` and `local.shb.omp.auth-gateway` SHALL report exit code `0`
- **AND** TCP ports `8765` and `4000` SHALL be listening on `127.0.0.1`
- **AND** `GET http://127.0.0.1:4000/v1/models` SHALL return HTTP `200` advertising native Google Antigravity models

### Requirement: Shell Switcher Functions and Dynamic Goose Limit Alignment
In `~/.zshenv` and `~/.zshrc` on `iosteam-mac-mini`, shell environment variables and model/gateway switcher functions SHALL default to `gemini-4-neon` (`512K`) and call `_sync_goose_limits` to dynamically adjust `GOOSE_CONTEXT_LIMIT` and `GOOSE_AUTO_COMPACT_TOKEN_LIMIT` when switching models.

#### Scenario: Shell defaults and model switchers adapt Goose limits dynamically
- **WHEN** a fresh interactive Zsh shell starts on `iosteam-mac-mini`
- **THEN** `GOOSE_MODEL` and `ANTHROPIC_DEFAULT_MODEL` SHALL default to `'gemini-4-neon'`
- **AND** `GOOSE_CONTEXT_LIMIT` SHALL default to `'512000'` and `GOOSE_AUTO_COMPACT_TOKEN_LIMIT` SHALL default to `'400000'`
- **AND** invoking `switch-model-argon` or `switch-model-hydrogen` SHALL dynamically set `GOOSE_CONTEXT_LIMIT=1000000` and `GOOSE_AUTO_COMPACT_TOKEN_LIMIT=800000` via `_sync_goose_limits`
