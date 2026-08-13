# Tasks: harden-shared-coding-agent-credential-loading

## 1. Preflight — loader isolated verification

- [x] 1.1 Loader syntax check: `zsh -n ~/.config/agent-llm/load-hermes-custom-credentials.zsh` — PASS
- [x] 1.2 No stdout/stderr when sourced — PASS
- [x] 1.3 Five allowlisted variables set (ANTIGRAVITY, COCKPIT, GIAODUC, LOCALHOST_51006, SHOPAPIKEY) — PASS
- [x] 1.4 No unrelated token leakage — PASS
- [x] 1.5 Pre-exported sentinel preserved — PASS
- [x] 1.6 Parser temporary variables absent after sourcing — PASS
- [x] 1.7 Missing `.env` is nonfatal (exit 0, no error) — PASS
- [x] 1.8 Value lengths correct (35, 42, 37, 42, 36 chars) — PASS

## 2. Backup and wiring

- [x] 2.1 Timestamped backups at `~/.omp/backups/zprofile-loader-harden-20260813_142732/` (mode 600)
- [x] 2.2 Strict OpenSpec validation passes
- [x] 2.3 Loader wired into `~/.zshenv` (single block, syntax clean)
- [x] 2.4 Broad `.hermes/.env` source removed from `~/.zprofile`

## 3. Post-wiring syntax checks

- [x] 3.1 `zsh -n ~/.zshenv` — PASS
- [x] 3.2 `zsh -n ~/.zprofile` — PASS
- [x] 3.3 `zsh -n ~/.config/agent-llm/load-hermes-custom-credentials.zsh` — PASS
- [x] 3.4 Loader mode 700, `.hermes/.env` mode 600 confirmed

## 4. Genuine clean-shell acceptance

- [x] 4.1 Non-interactive login (`zsh -lc`): five vars SET — PASS
- [x] 4.2 Non-interactive login: no unrelated vars leaked — PASS
- [x] 4.3 Non-interactive login: no credential output — PASS
- [x] 4.4 Non-login (`zsh -c`): five vars SET — PASS
- [x] 4.5 Non-login: no unrelated vars leaked — PASS
- [x] 4.6 Non-login: no credential output — PASS
- [x] 4.7 Parser temps absent after sourcing — PASS
- [x] 4.8 Interactive `zsh -lic` emits OSC 1337 terminal metadata (not credentials) — classified and documented

## 5. Missing-source and inheritance

- [x] 5.1 Missing `.env`: shell starts, exit 0, no error — PASS
- [x] 5.2 Missing loader: shell starts, exit 0, no error — PASS
- [x] 5.3 Pre-existing variable sentinel preserved — PASS
- [x] 5.4 Python subprocess inherits all five keys — PASS

## 6. Real omp acceptance

- [x] 6.1 `cockpit/gpt-5.6-luna:high` — pong, exit 0
- [x] 6.2 `shopapikey/fable-5` — pong, exit 0
- [x] 6.3 `giaoduc/Advance` — pong, exit 0
- [x] 6.4 Default role without `--model` — pong, exit 0

## 7. Config preservation

- [x] 7.1 `models.yml` hash unchanged: `747167245051c2fe546636b98beb112a`
- [x] 7.2 `config.yml` hash unchanged: `0358ecccb895fd8844d1cd9e48730dab`
- [x] 7.3 Role map unchanged: `default: cockpit/gpt-5.6-luna:high`
- [x] 7.4 Context windows unchanged: all three at 1,000,000
- [x] 7.5 Native Cockpit endpoint preserved: `http://localhost:51006/v1`, `openai-responses`
- [x] 7.6 OmniRoute preserved: 3 models, unchanged

## 8. Pre-archive readiness

- [x] 8.1 Strict OpenSpec validation passes
- [x] 8.2 Scoped `git diff --check` clean
- [x] 8.3 All implementation tasks marked [x] with evidence
- [x] 8.4 Documentation reviewed for credential fragments

## Evidence

- Loader: `~/.config/agent-llm/load-hermes-custom-credentials.zsh` (mode 700, sourceable allowlist parser)
- Canonical source: `~/.hermes/.env` (mode 600, 52 variables, loader exports 5)
- Backup: `~/.omp/backups/zprofile-loader-harden-20260813_142732/`
- .zshenv hash: `da1b24adb5d42ae13c01c62faf2bc97e`
- .zprofile hash: `bfe845a043c214a67381e8cd8b3a4469`
