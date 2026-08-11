# claude-code-provider-routing Specification

## Purpose
TBD - created by archiving change claude-code-model-effort-alias-routing. Update Purpose after archive.
## Requirements
### Requirement: Provider launchers SHALL use the documented model alias, `[1m]` suffix, and effort contract

Each provider launcher MUST use lowercase `[1m]` on its model selector to request the 1 million token context window, declare the capability needed for its requested effort, and set `CLAUDE_CODE_EFFORT_LEVEL` in its subshell. The shopapikey launcher MUST use the built-in `fable` alias pinned with `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]`; giaoduc and cockpit MUST use custom model options with `[1m]` for `Advance[1m]` and `gpt-5.6-luna[1m]` respectively.

Claude Code MUST strip the `[1m]` suffix before transmitting the model ID to the provider. The wire model ID MUST be the bare base name without the `[1m]` suffix. Selector acceptance by Claude Code MUST NOT be interpreted as proof of provider-side 1M context window capacity.

#### Scenario: Shopapikey resolves the Fable alias with 1M context

- **WHEN** `shopapikey` launches Claude Code with `ANTHROPIC_MODEL=fable[1m]` and `ANTHROPIC_DEFAULT_FABLE_MODEL=fable-5[1m]`
- **THEN** Claude Code MUST send `model=fable-5` (suffix stripped) and `output_config.effort=xhigh`

#### Scenario: Giaoduc selects its custom model with 1M context

- **WHEN** `giaoduc` launches Claude Code with `ANTHROPIC_MODEL=Advance[1m]` and `ANTHROPIC_CUSTOM_MODEL_OPTION=Advance[1m]`
- **THEN** Claude Code MUST send `model=Advance` (suffix stripped) and `output_config.effort=xhigh`

#### Scenario: Cockpit selects its custom model with 1M context

- **WHEN** `cockpit` launches Claude Code with `ANTHROPIC_MODEL=gpt-5.6-luna[1m]` and `ANTHROPIC_CUSTOM_MODEL_OPTION=gpt-5.6-luna[1m]`
- **THEN** Claude Code MUST send `model=gpt-5.6-luna` (suffix stripped) and `output_config.effort=max`

### Requirement: The cockpit adapter SHALL preserve requested effort

The adapter MUST translate a valid Anthropic `output_config.effort` value to OpenAI Responses `reasoning.effort` for both streaming and non-streaming requests. It MUST omit the Anthropic-only `output_config` and `thinking` fields from the upstream body.

#### Scenario: Max effort is translated

- **WHEN** the adapter receives `output_config={"effort":"max"}`
- **THEN** the upstream Responses body MUST contain `reasoning={"effort":"max"}`

#### Scenario: Effort is absent

- **WHEN** the adapter receives no `output_config.effort`
- **THEN** the upstream body MUST omit `reasoning` and retain existing default behavior

#### Scenario: Unsupported effort is rejected

- **WHEN** the adapter receives an effort value outside the supported set
- **THEN** the adapter MUST return HTTP 400 without forwarding the request upstream

### Requirement: Provider acceptance SHALL be evidence-gated

The change MUST NOT be archived as complete until all three launchers have fresh live smoke evidence, the cockpit outbound body independently proves the requested effort field, and the wire model excludes the `[1m]` suffix.

#### Scenario: A provider is rate limited

- **WHEN** a provider returns an account or capacity error
- **THEN** its acceptance gate MUST remain pending and the error MUST be recorded as an external blocker rather than a pass

#### Scenario: `[1m]` selector acceptance does not prove provider 1M capacity

- **WHEN** Claude Code accepts a `[1m]` selector and strips it before transmission
- **THEN** the provider-side 1M context window capacity MUST be verified separately before claiming 1M support
