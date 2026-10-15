# Tasks

## 1. Preflight & Backup

- [x] 1.1 Verify OmniRoute loopback health on port 20128 and confirm combo `gemini-3.8-flash-high` is responsive
- [x] 1.2 Create timestamped mode `0600` backups of `~/.config/goose/config.yaml` and `~/.config/goose/custom_providers/custom_omniroute.json` outside Git

## 2. Configuration Mutation

- [x] 2.1 Update `~/.config/goose/custom_providers/custom_omniroute.json` to declare `context_limit: 1048576` and `timeout_seconds: 600` for `gemini-3.8-flash-high` and prune decommissioned routes (`ollamacloud/*`, `sh/*`)
- [x] 2.2 Update `~/.config/goose/config.yaml` context limits (`GOOSE_CONTEXT_LIMIT: 1048576`, `GOOSE_PLANNER_CONTEXT_LIMIT: 1048576`)
- [x] 2.3 Configure auto-compaction and token headroom in `~/.config/goose/config.yaml` (`GOOSE_MAX_TOKENS: 65536`, `GOOSE_AUTO_COMPACT_THRESHOLD: 0.8`, `GOOSE_CONTEXT_STRATEGY: summarize`, `GOOSE_TOOL_CALL_CUTOFF: 10`)
- [x] 2.4 Normalize thinking effort levels and reasoning rendering in `~/.config/goose/config.yaml` (`GOOSE_THINKING_EFFORT: high`, `GEMINI3_THINKING_LEVEL: high`, `GOOSE_CLI_SHOW_THINKING: 1`)
- [x] 2.5 Reconcile legacy Cockpit port 51006 residue in `~/.config/goose/config.yaml`: point `OPENAI_BASE_URL` and `OPENAI_HOST` to `http://localhost:20128/v1` and set `OPENAI_BASE_PATH: chat/completions` (replacing legacy `v1/response`)
- [x] 2.6 Enforce strict filesystem permissions (`chmod 700 ~/.config/goose ~/.config/goose/custom_providers` and `chmod 600 ~/.config/goose/config.yaml ~/.config/goose/custom_providers/*.json`)

## 3. Verification & Governance

- [x] 3.1 Verify Goose loads valid YAML configuration without warnings via `goose info`
- [x] 3.2 Execute non-interactive end-to-end sentinel probe using `goose run --no-session --text "Respond with exactly: PONG"` and assert exit code 0
- [x] 3.3 Inspect OmniRoute container logs (`omniroute-base`) to verify receipt on `/v1/responses` with combo `gemini-3.8-flash-high` and context resolution `1048576`
- [x] 3.4 Validate OpenSpec change strictly with `openspec validate standardize-goose-omniroute-runtime --store openspec-store --strict`
