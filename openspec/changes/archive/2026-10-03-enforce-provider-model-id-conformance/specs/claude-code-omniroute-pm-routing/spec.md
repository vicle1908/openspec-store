## MODIFIED Requirements

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
- **AND** the selected model MUST be `pm/Claude-Fable` unless the caller passes `--model`
- **AND** `ANTHROPIC_AUTH_TOKEN` MUST NOT be set in the launched process

#### Scenario: Claude Code talks the native Messages protocol

- **WHEN** Claude Code runs under the omniroute profile
- **THEN** requests MUST be sent to `/v1/messages` on the OmniRoute API port
- **AND** the selected model MUST NOT carry the `[1m]` suffix, because the client catalog does not describe the suffixed phanmemvip alias
- **AND** the wire model MUST preserve the `pm/` channel prefix the gateway requires
- **AND** the request MUST succeed against the phanmemvip channel

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
