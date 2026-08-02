# agentmemory-mcp-wiring Specification

## ADDED Requirements

### Requirement: Each of the 7 supported agents is wired to the same memory server
The repository SHALL contain, at the repo root, agent configuration files that wire each of the 7 supported agents (Cursor, Claude Code, Codex CLI, OpenCode, pi, Hermes, OpenClaw) to the agentmemory MCP server. Each wiring file SHALL be non-destructive (preserve any existing MCP servers and agent settings), SHALL set `AGENTMEMORY_URL=http://localhost:3111` (overridable via shell env), SHALL set a per-agent `AGENT_ID` value, and SHALL merge into the agent's native `mcpServers` (or equivalent) object using the standard snippet from the upstream agentmemory README.

#### Scenario: Cursor mcp.json is non-destructive
- **WHEN** the bootstrap script runs and `.cursor/mcp.json` already contains a `github` MCP server
- **THEN** the script merges an `agentmemory` entry next to `github` and the resulting JSON parses to a `mcpServers` object with both `github` and `agentmemory` keys

#### Scenario: Each agent has its own AGENT_ID
- **WHEN** the server receives writes from Cursor, Claude Code, Codex CLI, OpenCode, pi, Hermes, and OpenClaw
- **THEN** the writes are tagged with `agentId` values of `cursor`, `claude-code`, `codex-cli`, `opencode`, `pi`, `hermes`, and `openclaw` respectively, and a `GET /agentmemory/audit?agentId=cursor` returns only the writes from Cursor

#### Scenario: AGENTMEMORY_URL is overridable
- **WHEN** a developer exports `AGENTMEMORY_URL=http://10.0.0.5:3111` and starts Claude Code
- **THEN** Claude Code connects to `10.0.0.5:3111` and not to `localhost:3111` (verifiable by the audit log showing the remote IP)

### Requirement: 15 skills are installed for every agent
The 15 upstream agentmemory skills (8 invocable: `remember`, `recall`, `recap`, `handoff`, `forget`, `commit-context`, `commit-history`, `session-history`; 7 reference: `agentmemory-mcp-tools`, `agentmemory-rest-api`, `agentmemory-config`, `agentmemory-agents`, `agentmemory-hooks`, `agentmemory-architecture`, `write-agentmemory-skill`) SHALL be installed into every agent's native skill directory. The `npx skills add rohitg00/agentmemory -y -a '*'` command SHALL be the canonical install path; for agents not covered by the skills CLI (Zed pre-1.3.x only, not in scope), the 15 `SKILL.md` files SHALL be copied manually to the agent's native skill directory.

#### Scenario: skills add detects installed agents
- **WHEN** a developer runs `npx skills add rohitg00/agentmemory -y -a '*'`
- **THEN** the command installs the 15 skills into every installed agent's skill directory and reports the list of agents it touched

#### Scenario: invocable skills appear in the agent's slash-command palette
- **WHEN** a developer opens Claude Code and types `/` in the prompt
- **THEN** the palette includes `/remember`, `/recall`, `/recap`, `/handoff`, `/forget`, `/commit-context`, `/commit-history`, and `/session-history` with descriptions pulled from the upstream `SKILL.md` files

#### Scenario: reference skills are loaded on demand
- **WHEN** an agent needs to call a memory tool and resolves the `agentmemory-mcp-tools` reference skill
- **THEN** the skill is loaded from the agent's skill directory and the 53-tool data table is current as of the upstream version (the data table is generated from source per the upstream README, so it never drifts)

### Requirement: .env is generated from a committed template and never committed
The `infrastructure/agentmemory.env.template` file SHALL be committed to the repository and SHALL contain the B+ feature flag set with placeholders for LLM provider keys. The `~/.agentmemory/.env` file SHALL be generated from this template by the bootstrap script and SHALL NOT be committed to the repository. The bootstrap script SHALL chmod 600 the generated `.env` file.

#### Scenario: Template is committed
- **WHEN** `git ls-files infrastructure/agentmemory.env.template` runs
- **THEN** the file appears in the output

#### Scenario: Generated .env is never committed
- **WHEN** `git status` runs after `make agentmemory-bootstrap`
- **THEN** `~/.agentmemory/.env` does not appear in the untracked-files list (it is outside the repo) and the repo's own `.gitignore` does not exclude the template path (only the home-directory path is excluded via the developer's global gitignore)

#### Scenario: .env permissions are restrictive
- **WHEN** the bootstrap script generates `~/.agentmemory/.env`
- **THEN** the file mode is `0600` and `ls -l ~/.agentmemory/.env` shows `-rw-------`

#### Scenario: AGENTMEMORY_SECRET is required when the server is exposed
- **WHEN** a developer exports `AGENTMEMORY_URL` to a non-loopback address
- **THEN** the bootstrap script refuses to start the server unless `AGENTMEMORY_SECRET` is set in `~/.agentmemory/.env` and is at least 32 characters long

### Requirement: The Codex Desktop silent-hooks issue is mitigated
The Codex CLI wiring SHALL include a comment in `.codex/config.toml` and a corresponding step in `scripts/agentmemory-bootstrap.sh` that runs `agentmemory connect codex --with-hooks` to mirror the plugin's hook commands into `~/.codex/hooks.json` because the upstream Codex Desktop build does not dispatch plugin-local `hooks.json` (openai/codex#16430). The bootstrap SHALL re-run this command on every invocation to refresh the absolute paths in the mirrored hooks file.

#### Scenario: connect codex --with-hooks merges into ~/.codex/hooks.json
- **WHEN** the bootstrap script runs and `~/.codex/hooks.json` does not contain an `agentmemory` block
- **THEN** the script calls `npx @agentmemory/agentmemory connect codex --with-hooks` and the resulting `~/.codex/hooks.json` contains an idempotent `agentmemory` block referencing absolute paths to the bundled scripts

#### Scenario: Refresh on upgrade
- **WHEN** the agentmemory package is upgraded and `make agentmemory-bootstrap` is re-run
- **THEN** the script re-runs `connect codex --with-hooks`, which overwrites the previous `agentmemory` block with paths pointing at the new version, and preserves any user-defined hooks outside the block
