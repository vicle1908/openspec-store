# Tasks

## 1. Upgrade System Formulae

- [x] 1.1 Upgrade `node` via `brew upgrade --formula node` and verify version `26.10.0_2`
- [x] 1.2 Upgrade `simdjson` via `brew upgrade --formula simdjson` and verify version `5.0.0`

## 2. Upgrade Desktop Application Casks

- [x] 2.1 Upgrade `google-drive` via `brew upgrade --cask google-drive` and verify version >= 132.0.0
- [x] 2.2 Upgrade `lark` via `brew upgrade --cask lark` and verify version >= 8.1.22
- [x] 2.3 Upgrade `teamviewer` via `brew upgrade --cask teamviewer` and verify version >= 15.82.6

## 3. Upstream Hermes Agent Fast-Forward

- [x] 3.1 Fast-forward merge `~/.hermes/hermes-agent` to `origin/main` (commit `8b66a51036`)
- [x] 3.2 Verify `git -C ~/.hermes/hermes-agent status` reports clean and up to date

## 4. Verification and Evidence

- [x] 4.1 Verify `node --version`, `brew info simdjson`, and `hermes --version`
- [x] 4.2 Verify container daemons via `docker ps`
- [x] 4.3 Author `evidence.md` with verifiable output
