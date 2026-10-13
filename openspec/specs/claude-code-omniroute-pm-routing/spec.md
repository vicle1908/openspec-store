# claude-code-omniroute-pm-routing Specification

## Purpose
Defines how the `omniroute()` zsh launcher routes Claude Code through the
local OmniRoute AI gateway's native Anthropic Messages endpoint (`/v1/messages`)
using the phanmemvip `pm/` model channel: the launcher function contract in
`~/.zshrc`, the credential-free `omniroute-pm.json` profile with its
`apiKeyHelper` gate, `[1m]` wire-suffix stripping, and the failure diagnostics
when the helper or `claude` binary is missing.

## Requirements

### Requirement: OmniRoute pm launcher SHALL route Claude Code through the gateway Messages endpoint

The `omniroute()` launcher in `~/.zshrc` SHALL select `omniroute-pm.json` via `claude --settings`, set `ANTHROPIC_BASE_URL` to the OmniRoute loopback port, unset `ANTHROPIC_AUTH_TOKEN`, and default model to `pm/Claude-Fable`. All Claude Code custom launcher profiles in the workspace (`omniroute`, `cockpit`, `shopapikey`) SHALL route directly through OmniRoute's Messages port (`http://127.0.0.1:20129`), eliminating intermediate container sidecars on port 8788.

#### Scenario: Launcher routes through OmniRoute
- **WHEN** `omniroute` is invoked in an interactive zsh shell
- **THEN** Claude Code MUST start with `ANTHROPIC_BASE_URL=http://127.0.0.1:20129`
- **AND** the selected model MUST be `pm/Claude-Fable` unless the caller passes `--model`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST NOT be set in the launched process

#### Scenario: Claude Code talks the native Messages protocol
- **WHEN** Claude Code runs under the omniroute profile
- **THEN** requests MUST be sent to `/v1/messages` on the OmniRoute API port
- **AND** the selected model MUST NOT carry the `[1m]` suffix, because the client catalog does not describe the suffixed phanmemvip alias
- **AND** the wire model MUST preserve the `pm/` channel prefix the gateway requires
- **AND** the request MUST succeed against the phanmemvip channel

#### Scenario: Direct native routing for coding agent profiles
- **WHEN** any Claude Code launcher (`omniroute`, `cockpit`, or `shopapikey`) is executed
- **THEN** requests MUST route directly to OmniRoute's native Messages endpoint on port 20129 without requiring container `claude-code-provider-adapter` to be running on port 8788
- **AND** for `cockpit`, the requested model SHALL route to `cockpit/gpt-5.6-luna` using OmniRoute's registered Cockpit Responses provider node.

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
than an unrecognized string, and SHALL declare the `pm/Claude-Fable`
selector for the Fable context stance with `xhigh` effort. Selector
acceptance by Claude Code SHALL NOT be treated as proof of provider-side
capacity, and no model value SHALL carry a `[1m]` suffix.

#### Scenario: Gateway alias is declared

- **WHEN** the omniroute profile is loaded
- **THEN** `modelOverrides` MUST contain an entry mapping the phanmemvip Fable channel ID to itself
- **AND** its top-level `model` MUST be `pm/Claude-Fable`

#### Scenario: One launcher per provider surface
