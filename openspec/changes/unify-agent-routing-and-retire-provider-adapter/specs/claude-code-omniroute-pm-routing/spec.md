# Spec Delta: claude-code-omniroute-pm-routing

## MODIFIED Requirements

### Requirement: OmniRoute pm launcher SHALL route Claude Code through the gateway Messages endpoint

The `omniroute()` launcher in `~/.zshrc` SHALL select the `~/.claude/profiles/omniroute-pm.json` profile via `claude --settings`, set `ANTHROPIC_BASE_URL` to the OmniRoute loopback API port, unset `ANTHROPIC_AUTH_TOKEN`, and default the model to the phanmemvip channel Fable model. All Claude Code custom launcher profiles in the developer workspace SHALL route directly without intermediate container translation hops on port 8788.

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
- **THEN** requests MUST NOT route through port 8788 or require container `claude-code-provider-adapter` to be running
- **AND** `omniroute` MUST continue communicating directly with `http://127.0.0.1:20129/v1/messages` using the `omniroute-pm.json` profile.
