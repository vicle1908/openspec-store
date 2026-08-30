# claude-code-omniroute-pm-routing Specification

## Purpose
TBD - created by archiving change add-claude-code-omniroute-pm-launcher. Update Purpose after archive.

## Requirements

### Requirement: OmniRoute pm launcher SHALL route Claude Code through the gateway Messages endpoint

The `omniroute()` launcher in `~/.zshrc` SHALL select the
`~/.claude/profiles/omniroute-pm.json` profile via `claude --settings`, set
`ANTHROPIC_BASE_URL` to the OmniRoute loopback API port, unset
`ANTHROPIC_AUTH_TOKEN`, and default the model to the phanmemvip channel Fable
model. The launcher SHALL verify the credential helper and the `claude`
binary before launch and fail with a diagnostic otherwise.

#### Scenario: Launcher routes through OmniRoute

- **WHEN** `omniroute` is invoked in an interactive zsh shell
- **THEN** Claude Code MUST start with `ANTHROPIC_BASE_URL=http://127.0.0.1:20129`
- **AND** the selected model MUST be `pm/Claude-Fable[1m]` unless the caller passes `--model`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST NOT be set in the launched process

#### Scenario: Claude Code talks the native Messages protocol

- **WHEN** Claude Code runs under the omniroute profile
- **THEN** requests MUST be sent to `/v1/messages` on the OmniRoute API port
- **AND** the wire model MUST NOT carry the `[1m]` suffix
- **AND** the request MUST succeed against the phanmemvip channel

### Requirement: The omniroute profile SHALL be credential-free and helper-gated

`~/.claude/profiles/omniroute-pm.json` MUST be mode 600, MUST NOT contain any
secret values, and MUST declare `apiKeyHelper` pointing at
`~/.claude/helpers/omniroute-key.sh`. The helper MUST write exactly one line
(the `OMNIROUTE_API_KEY` shared-tier value) to stdout, resolve the value
env-first, and fall back to a restricted single-key parse of `~/.zshenv`
without sourcing it.

#### Scenario: Profile is credential-free

- **WHEN** `~/.claude/profiles/omniroute-pm.json` is inspected
- **THEN** it MUST NOT contain `ANTHROPIC_AUTH_TOKEN`, `API_KEY`, `TOKEN`, or `SECRET` in its `env` block
- **AND** its permissions MUST be `600`

#### Scenario: Helper supplies the shared-tier key when OmniRoute is keyed

- **WHEN** the helper runs in a zsh environment and `OMNIROUTE_API_KEY` is exported by the managed shared-agent-secrets block
- **THEN** the helper MUST print exactly that value as a single line
- **AND** with the variable absent from the environment, the helper MUST recover the value by parsing `~/.zshenv` for that single key without sourcing the file

### Requirement: The gateway alias SHALL be declared to Claude Code

The omniroute profile SHALL map the gateway model ID to itself in
`modelOverrides` so the gateway alias is a declared model selection rather
than an unrecognized string, and SHALL declare the `pm/Claude-Fable[1m]`
selector for the Fable 1M context stance with `xhigh` effort. The 1M
selector SHALL NOT be treated as proof of provider-side 1M capacity.

#### Scenario: Gateway alias is declared

- **WHEN** the omniroute profile is loaded
- **THEN** `modelOverrides` MUST contain an entry mapping the phanmemvip Fable channel ID to itself

#### Scenario: One launcher per provider surface

- **WHEN** any of `shopapikey`, `cockpit`, or `omniroute` launchers is used
- **THEN** each MUST select exactly its own profile via `claude --settings`
- **AND** `claude_reset` MUST continue to clear all provider-specific variables for a default launch
