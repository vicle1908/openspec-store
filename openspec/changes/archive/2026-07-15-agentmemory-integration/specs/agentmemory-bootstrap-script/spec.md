# agentmemory-bootstrap-script Specification

## ADDED Requirements

### Requirement: The bootstrap script is a single, idempotent, multi-OS entry point
The `scripts/agentmemory-bootstrap.sh` script (invoked via `make agentmemory-bootstrap`) SHALL be the single entry point that a developer runs to bring up the agentmemory host process and wire the agents. The script SHALL detect the host OS (`darwin`/`linux`) and architecture (`arm64`/`x64`), SHALL refuse to run on Windows without WSL2, SHALL verify Node ≥ 20, and SHALL be safe to re-run.

#### Scenario: macOS arm64 bootstrap
- **WHEN** a developer runs `make agentmemory-bootstrap` on `darwin arm64` with Node 26.5 installed
- **THEN** the script downloads `iii-aarch64-apple-darwin.tar.gz` to `~/.agentmemory/bin/`, generates `~/.agentmemory/.env`, runs `npx skills add rohitg00/agentmemory -y -a '*'`, and exits 0

#### Scenario: Linux x64 bootstrap
- **WHEN** a developer runs `make agentmemory-bootstrap` on `linux x64` with Node 22.0 installed
- **THEN** the script downloads `iii-x86_64-unknown-linux-gnu.tar.gz` to `~/.agentmemory/bin/`, generates `~/.agentmemory/.env`, runs `npx skills add rohitg00/agentmemory -y -a '*'`, and exits 0

#### Scenario: Node too old
- **WHEN** a developer runs `make agentmemory-bootstrap` with Node 18.x
- **THEN** the script prints `Node >= 20 required (found 18.x). Install Node 20+ via nvm or asdf and retry.` and exits non-zero without touching the filesystem

#### Scenario: Windows without WSL2
- **WHEN** a developer runs `make agentmemory-bootstrap` on Windows without WSL2
- **THEN** the script prints `Windows requires WSL2. See docs/agentmemory-troubleshooting.md.` and exits non-zero

### Requirement: The bootstrap script surfaces every failure with a remediation hint
Every failure path in `scripts/agentmemory-bootstrap.sh` SHALL print a single-line, machine-greppable error of the form `FAIL: <step>: <message>` followed by a one-line `HINT: <how to fix>`. The script SHALL exit with a non-zero status on any failure and SHALL NOT proceed to subsequent steps.

#### Scenario: Engine download fails
- **WHEN** the GitHub release for `iii/v0.11.2` is unreachable and the curl returns non-zero
- **THEN** the script prints `FAIL: engine_download: HTTP 404 from https://github.com/iii-hq/iii/releases/download/iii/v0.11.2/...` and `HINT: check your network or set AGENTMEMORY_III_VERSION=<known-good-version>` and exits non-zero

#### Scenario: npm install fails with EACCES
- **WHEN** the global `npm install -g @agentmemory/agentmemory` fails with EACCES on a system Node install
- **THEN** the script prints `FAIL: npm_install: EACCES on global install` and `HINT: retry with: sudo npm install -g @agentmemory/agentmemory@latest` and exits non-zero

#### Scenario: Ollama not running
- **WHEN** the script reaches the LLM-provider detection step and Ollama is not reachable
- **THEN** the script prints a yellow `WARN: ollama_unreachable: Ollama is not running; Stop-hook compression will be a no-op until Ollama is started` and CONTINUES (does not exit) because Ollama is the zero-cost default but is not a hard requirement

### Requirement: Doctor is a one-shot health check with a green/yellow/red table
The `scripts/agentmemory-doctor.sh` script SHALL print a single table with one row per check and SHALL exit 0 when all rows are green or yellow, non-zero when any row is red. The rows SHALL cover: Node version (green if ≥ 20), `iii` binary present (green), `:3111` reachable (green), `:3113` reachable (green), `.env` present (green), `AGENTMEMORY_SECRET` set when `AGENTMEMORY_URL` is non-loopback (green), tool count (green if ≥ 11), Ollama reachable (green), and per-agent MCP wiring (green for each installed agent).

#### Scenario: All checks pass on a healthy machine
- **WHEN** `make agentmemory-doctor` runs on a freshly bootstrapped machine
- **THEN** the table is all green, the script exits 0, and the developer sees no warnings

#### Scenario: Tool count is below 11
- **WHEN** `make agentmemory-doctor` runs and only the MCP shim is running (full server is down)
- **THEN** the table includes a red row `tools: 7/53 (expected >=11, full server not running)` and the script exits 2

#### Scenario: Claude Code wiring is missing
- **WHEN** `make agentmemory-doctor` runs and `.claude/settings.json` exists but does not contain an `agentmemory` key
- **THEN** the table includes a yellow row `claude-code: mcp entry missing` and the script exits 0 (yellow is informational, not a failure)

### Requirement: Reset preserves the data directory
The `scripts/agentmemory-reset.sh` script SHALL call `agentmemory-down` to stop the server, SHALL remove `~/.agentmemory/run/` and `~/.agentmemory/log/`, and SHALL PRESERVE `~/.agentmemory/data/` and `~/.agentmemory/config/`. The script SHALL print a one-line summary of what was removed and what was preserved, and SHALL exit 0.

#### Scenario: Reset preserves data
- **WHEN** a developer runs `make agentmemory-reset`
- **THEN** the script prints `removed: run/, log/  preserved: data/, config/`, exits 0, and a subsequent `make agentmemory-up` boots the server with all prior memories intact
