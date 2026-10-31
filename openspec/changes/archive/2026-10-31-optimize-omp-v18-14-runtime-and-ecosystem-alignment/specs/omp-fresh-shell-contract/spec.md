# omp-fresh-shell-contract Specification Delta

## MODIFIED Requirements

### Requirement: Fresh-shell custom credentials

A fresh zsh shell SHALL load the managed shared-agent-secrets block from `~/.zshenv`. The shell SHALL expose the five active `HERMES_CUSTOM_*_API_KEY` variables without printing their values. The retired `~/.config/agent-llm/load-hermes-custom-credentials.zsh` MAY remain as a silent compatibility stub but SHALL NOT be required for credential visibility.

#### Scenario: clean login shell receives custom keys

- **GIVEN** `~/.zshenv` contains the managed shared-agent-secrets block
- **WHEN** a clean environment starts `/bin/zsh -lic`
- **THEN** `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`, `HERMES_CUSTOM_ANTIGRAVITY_API_KEY`, and `HERMES_CUSTOM_LOCALHOST_51006_API_KEY` SHALL be set.

#### Scenario: missing env file does not break shell startup

- **GIVEN** the managed shared-agent-secrets block is absent from `~/.zshenv`
- **WHEN** a login zsh shell starts
- **THEN** the shell SHALL remain syntactically valid and start without an error from credential loading.

#### Scenario: non-login shell receives custom keys

- **GIVEN** `~/.zshenv` contains the managed shared-agent-secrets block
- **WHEN** a clean environment runs `/bin/zsh -c` (non-login)
- **THEN** the five active `HERMES_CUSTOM_*_API_KEY` variables SHALL be set
- **AND** unrelated variables such as `DISCORD_BOT_TOKEN` SHALL remain unset.

#### Scenario: loader produces no credential output

- **GIVEN** the retired loader is sourced in any shell context
- **WHEN** stdout and stderr are captured
- **THEN** no credential values or `export KEY=value` lines SHALL appear.
- **AND** Note: interactive zsh `-i` legitimately emits OSC 1337 terminal integration metadata unrelated to credential loading.

### Requirement: One-million-token custom model contexts

The omp model entries for `shopapikey/Claude-Fable`, `phanmemvip/gpt-5.6-sol`, and `cockpit/gpt-5.6-luna` SHALL declare `contextWindow: 1000000`.

#### Scenario: custom model context metadata

- **GIVEN** `~/.omp/agent/models.yml`
- **WHEN** the three custom model entries are inspected programmatically
- **THEN** each SHALL have `contextWindow` equal to `1000000`.

### Requirement: Existing omp routing preserved

The change SHALL preserve all existing provider endpoints, transports, model IDs, non-default role assignments, equivalence mappings, and credential values. The current `default` role SHALL resolve to `phanmemvip/gpt-5.6-sol:max`.

#### Scenario: three explicit providers remain usable

- **GIVEN** the fresh-shell custom provider credentials are loaded
- **WHEN** each explicit selector is run through omp
- **THEN** `cockpit/gpt-5.6-luna`, `shopapikey/Claude-Fable`, and `phanmemvip/gpt-5.6-sol` SHALL return `pong` with exit code 0, subject to provider-side rate limits.

#### Scenario: current default uses native Cockpit

*Deprecated heading: retained only for canonical scenario carry-over compatibility; the scenario now verifies the phanmemvip default and does not assert a Cockpit default.*

- **GIVEN** the custom provider credentials are loaded in a fresh login shell
- **WHEN** `omp --no-session --mode json -p "reply only: pong"` is run without `--model`
- **THEN** the served provider/model attribution SHALL be `phanmemvip/gpt-5.6-sol`
- **AND** no fallback event SHALL occur
- **AND** the command SHALL return `pong` with exit code 0.

### Requirement: Cockpit default role

The omp `default` role SHALL resolve to `phanmemvip/gpt-5.6-sol:max`.

#### Scenario: fresh-shell default uses Cockpit

*Deprecated heading: retained only for canonical scenario carry-over compatibility; the scenario now verifies the phanmemvip default and does not assert a Cockpit default.*

- **GIVEN** the custom provider credentials are loaded in a fresh login shell
- **WHEN** `omp --no-session --mode json -p "reply only: pong"` is run without `--model`
- **THEN** the served provider/model attribution SHALL be `phanmemvip/gpt-5.6-sol`
- **AND** the default thinking level SHALL be `max`
- **AND** the command SHALL return `pong` with exit code 0.

### Requirement: Supersession of Legacy Cockpit Default Role Assertions in Fresh-Shell Contract

The earlier clauses in `omp-fresh-shell-contract` asserting that OMP's `default` role resolves to `phanmemvip/gpt-5.6-sol:max` ARE SUPERSEDED by `omp-provider-routing` (`modelRoles.default: omniroute/gemini-4-argon`), and `/Users/androidteam/Developer/.claude/CLAUDE.md` SHALL import `@../AGENTS.md` so `/Users/androidteam/Developer/AGENTS.md` loads without `@-import: file not found` warnings or duplicate skill symlinks.

#### Scenario: Fresh-shell default role and context imports resolve cleanly without warnings
- **WHEN** `omp --no-session -p "reply only: pong"` is executed from `/Users/androidteam/Developer` in a fresh login shell
- **THEN** `modelRoles.default` SHALL resolve to `omniroute/gemini-4-argon` and `/Users/androidteam/Developer/.claude/CLAUDE.md` SHALL reference `@../AGENTS.md`
- **AND** the session log under `~/.omp/logs/` SHALL record zero `@-import: file not found` warnings for `/Users/androidteam/Developer/.claude/AGENTS.md` and `~/.omp/agent/skills/herdr` SHALL not duplicate `.agents/skills/herdr`

## ADDED Requirements

### Requirement: Antigravity OAuth Credential Hygiene, Throwaway Profile Cleanup, and MCP Timeout

`~/.omp/agent/agent.db` SHALL omit the permanently HTTP 403-rejected `google-antigravity` OAuth credential (`identity_key='email:vicgnome19091@gmail.com'`) while retaining the 15 healthy `google-antigravity` OAuth accounts, `~/.omp/profiles/` SHALL contain no leftover `omp-fresh-*` throwaway smoke profiles, and `~/.omp/agent/mcp.json` (`mode 0600`) SHALL declare `"$schema"`, `"type": "stdio"`, and `"timeout": 300000` on `mcpServers.mcp-router` while preserving `env.MCPR_TOKEN`.

#### Scenario: Rejected Antigravity OAuth account removed and healthy accounts preserved
- **WHEN** `~/.omp/agent/agent.db` is queried read-only for `auth_credentials`
- **THEN** `SELECT COUNT(*) FROM auth_credentials WHERE provider='google-antigravity' AND identity_key='email:vicgnome19091@gmail.com'` SHALL equal `0`
- **AND** `SELECT COUNT(*) FROM auth_credentials WHERE provider='google-antigravity' AND disabled_cause IS NULL` SHALL equal `15`
- **AND** fresh OMP session logs under `~/.omp/logs/` SHALL record zero `status=403` Antigravity usage-fetch or model-discovery warnings for `vicgnome19091@gmail.com`

#### Scenario: Stale throwaway smoke profiles absent and mcp.json hardened
- **WHEN** `/Users/androidteam/.omp/profiles` and `/Users/androidteam/.omp/agent/mcp.json` are inspected
- **THEN** `/Users/androidteam/.omp/profiles/omp-fresh-cockpit`, `omp-fresh-giaoduc`, and `omp-fresh-shopapikey` SHALL not exist
- **AND** `/Users/androidteam/.omp/agent/mcp.json` SHALL have permissions `0600`, declare `"$schema"`, configure `mcpServers.mcp-router.type == "stdio"` and `mcpServers.mcp-router.timeout == 300000`, and preserve a non-empty `env.MCPR_TOKEN`
