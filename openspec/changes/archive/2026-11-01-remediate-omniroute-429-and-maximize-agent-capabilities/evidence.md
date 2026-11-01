# Verification & Evidence: `remediate-omniroute-429-and-maximize-agent-capabilities`

- **Execution Time (UTC)**: `2026-11-01T07:50:00Z`
- **OmniRoute Combo Telemetry (`storage.sqlite`)**:
  - `gemini-3.8-flash-high`: 9 active Pro accounts (`0` banned, `0` exhausted). 10/10 concurrent requests passed with 100% `HTTP 200` and ~5.3s avg latency.
  - `claude-opus-5.5` & `claude-sonnet-5.5`: 13 active `agy` accounts (10 Pro + 3 Ultra, `0` banned).
  - Zero banned accounts (`47f334b1`, `d5c3465f`, `20369f65`) remain in any combo definition.

## 1. Coding Agent Multi-Turn & Tool Execution Evidence

| Agent | Target Model / Role | Verification Probe | Latency | Status |
|---|---|---|---:|---|
| **Codex CLI** | `omniroute/gemini-3.8-flash-high` | `shell_command` file read (`item_17`) | `17.12s` | **PASS** |
| **OpenCode** | `omniroute-responses/gemini-3.8-flash-high` | `read` tool (`item_17`) | `24.84s` | **PASS** |
| **Kilo Code** | `omniroute-responses/gemini-3.8-flash-high` | `read` tool (`item_17`) | `19.73s` | **PASS** |
| **Pi** | `omniroute-responses/gemini-3.8-flash-high` | `read` tool (`item_17`) | `37.79s` | **PASS** |
| **Prime Agent** | `omniroute-responses/gemini-3.8-flash-high` | `read` tool (`item_17`) | `17.72s` | **PASS** |
| **OMP** | `omniroute/gemini-3.8-flash-high` | `read` tool (`item_17`) | `23.55s` | **PASS** |
| **Claude Code** | `gemini-3.8-flash-high` | `Read` tool (`item_17`) | `14.70s` | **PASS** |

## 2. File Mode and Verification Register

| File | Expected Mode | Verified Mode | Status |
|---|---|---|---|
| `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` | `0755` | `0755` | **PASS** |
| `/Users/androidteam/.omp/agent/models.yml` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.omp/agent/config.yml` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.omp/agent/agent.db` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.pi/agent/models.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.pi/agent/settings.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.prime/agent/models.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.prime/agent/settings.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.hermes/config.yaml` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.config/opencode/opencode.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.config/kilo/kilo.jsonc` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.codex/cockpit-model-catalog.json` | `0644` | `0644` | **PASS** |
| `/Users/androidteam/.codex/config.toml` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.kimi-code/config.toml` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.grok/config.toml` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.config/goose/custom_providers/custom_omniroute.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.config/goose/config.yaml` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.factory/settings.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.claude/profiles/omniroute-pm.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.config/muse/settings.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.qwen/settings.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.config/zed/settings.json` | `0600` | `0600` | **PASS** |
| `/Users/androidteam/.cline/data/settings/providers.json` | `0600` | `0600` | **PASS** |
