## MODIFIED Requirements

### Requirement: Single config loading function

The system SHALL provide a single function `load_agent_config(agent_name)` in `tdt_core.config_loader` that returns a merged configuration dictionary. All agents SHALL use this function instead of independently reading `~/.tdt/config.yaml`.

When `allowed_overlay_keys` is provided, extra top-level keys in the agent overlay that fall within the allowed set SHALL be accepted without error. Keys outside the allowed set SHALL still raise `ConfigError`. The allowed keys are validated but NOT merged into the returned dict — only `model` and `runtime` sections participate in the merge regardless of the policy.

The cache key SHALL incorporate the effective `allowed_overlay_keys` as a `frozenset`, so a strict call cannot return permissive results and vice versa.

#### Scenario: Function returns merged config

- **WHEN** `load_agent_config("agent-docs-sync")` is called
- **THEN** it SHALL return a dict containing the merged model and runtime sections from global and agent-specific configs

#### Scenario: Explicit agent config path overrides the standard overlay

- **WHEN** `load_agent_config("agent-docs-sync", config_path="/custom/agent.yaml")` is called
- **AND** `/custom/agent.yaml` contains `model: { primary: "openai-chat:fable-5" }`
- **THEN** the resolved config SHALL use `/custom/agent.yaml` as the agent-specific overlay instead of `~/.tdt/agents/agent-docs-sync.yaml`

#### Scenario: Function is idempotent within a process

- **WHEN** `load_agent_config("agent-core")` is called twice in the same process
- **THEN** the second call SHALL return the cached result from the first call without re-reading files

#### Scenario: Unknown agent name returns global config only

- **WHEN** `load_agent_config("unknown-agent")` is called
- **AND** `~/.tdt/agents/unknown-agent.yaml` does not exist
- **THEN** it SHALL return the global config from `~/.tdt/config.yaml` without error

#### Scenario: Default strict key policy

- **WHEN** `load_agent_config("agent-core")` is called without `allowed_overlay_keys`
- **AND** the agent YAML contains a top-level key `gate: {approvers: ["x"]}`
- **THEN** a `ConfigError` SHALL be raised (the default `{"model", "runtime"}` policy applies)

#### Scenario: Harness-expanded key policy accepts domain keys without error

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate", "persistence", "authority"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}` and `persistence: {durable: true}`
- **THEN** the call SHALL succeed without `ConfigError`
- **AND** the returned dict SHALL retain unrelated global sections unchanged; only `model` and `runtime` are affected by the overlay merge; domain keys validated by the allowed set SHALL not cause `ConfigError` but SHALL not be merged

#### Scenario: Cache isolation by allowed-key set

- **GIVEN** `load_agent_config("agent", allowed_overlay_keys={"model", "runtime"})` is called
- **WHEN** `load_agent_config("agent", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **THEN** both calls SHALL resolve independently with no cache collision

#### Scenario: Domain keys excluded from merged result

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}`
- **THEN** the returned dict SHALL retain unrelated global sections unchanged
- **AND** the agent overlay's `gate` section SHALL NOT be merged into or override any global section
- **AND** agent-harness SHALL obtain `gate` from `load_agent_overlay()`

### Requirement: Unknown top-level keys rejected

Agent-specific YAML files MUST NOT contain top-level keys other than those permitted by the caller's `allowed_overlay_keys` policy. Unknown top-level keys SHALL be rejected with a clear error message listing the offending keys.

#### Scenario: Unknown top-level key in agent YAML is rejected

- **WHEN** `~/.tdt/agents/agent-core.yaml` contains `gateway: { enabled: true }`
- **THEN** the system SHALL raise a `ConfigError` indicating only `model` and `runtime` are allowed

#### Scenario: Multiple unknown keys reported

- **WHEN** `~/.tdt/agents/agent-core.yaml` contains `gateway: { enabled: true }` and `auth: { type: "oauth" }`
- **THEN** the system SHALL raise a `ConfigError` listing both `auth` and `gateway` as unknown

#### Scenario: Allowed keys accepted without error

- **WHEN** `load_agent_config("agent-harness", allowed_overlay_keys={"model", "runtime", "gate"})` is called
- **AND** the agent YAML contains `gate: {approvers: ["x"]}`
- **THEN** the call SHALL succeed without `ConfigError` for the `gate` key

## ADDED Requirements

### Requirement: Secure YAML mapping loader

`load_config_mapping(path: Path) -> dict[str, Any]` SHALL load a YAML file and return a validated dictionary. The function SHALL NOT merge with any other source and SHALL NOT cache its result.

#### Scenario: Valid YAML mapping loaded

- **GIVEN** a YAML file at `path` contains a mapping with `model: {primary: "x"}`
- **WHEN** `load_config_mapping(path)` is called
- **THEN** it SHALL return `{"model": {"primary": "x"}}`

#### Scenario: Empty YAML file returns empty dict

- **GIVEN** an empty YAML file at `path`
- **WHEN** `load_config_mapping(path)` is called
- **THEN** it SHALL return `{}`

#### Scenario: Missing file returns empty dict

- **GIVEN** no file exists at `path`
- **WHEN** `load_config_mapping(path)` is called
- **THEN** it SHALL return `{}`

#### Scenario: Malformed YAML raises ConfigError

- **GIVEN** a file at `path` contains invalid YAML syntax
- **WHEN** `load_config_mapping(path)` is called
- **THEN** a `ConfigError` SHALL be raised with the file path in the message

#### Scenario: Non-mapping YAML raises ConfigError

- **GIVEN** a file at `path` contains a YAML list (not a mapping)
- **WHEN** `load_config_mapping(path)` is called
- **THEN** a `ConfigError` SHALL be raised

#### Scenario: Secret-shaped value rejected

- **GIVEN** a file at `path` contains `secret: literal_value`
- **WHEN** `load_config_mapping(path)` is called
- **THEN** a `ConfigError` SHALL be raised with the key path

#### Scenario: api_key_env under providers accepted

- **GIVEN** a file at `path` contains `providers: {shopapikey: {api_key_env: "MY_API_KEY"}}`
- **WHEN** `load_config_mapping(path)` is called
- **THEN** it SHALL accept the value without error

#### Scenario: api_key_env with invalid env var name rejected

- **GIVEN** a file at `path` contains `providers: {x: {api_key_env: "lowercase"}}`
- **WHEN** `load_config_mapping(path)` is called
- **THEN** a `ConfigError` SHALL be raised

### Requirement: Agent overlay loader with key policy

`load_agent_overlay(agent_name: str, *, config_path: Path | None = None, allowed_keys: Collection[str] | None = None) -> dict` SHALL load only the agent-specific YAML file without reading or merging the global config. The returned dict preserves source provenance: every key came from the agent file.

#### Scenario: Agent overlay loaded without global merge

- **GIVEN** `~/.tdt/agents/agent-core.yaml` contains `model: {primary: "x"}`
- **AND** `~/.tdt/config.yaml` contains `providers: {giaoduc: {base_url: "y"}}`
- **WHEN** `load_agent_overlay("agent-core")` is called
- **THEN** the result SHALL contain `{"model": {"primary": "x"}}`
- **AND** `providers` SHALL NOT appear in the result

#### Scenario: Unknown top-level key rejected

- **GIVEN** `~/.tdt/agents/agent-core.yaml` contains `unknown_key: value`
- **WHEN** `load_agent_overlay("agent-core", allowed_keys={"model", "runtime"})` is called
- **THEN** a `ConfigError` SHALL be raised listing the unknown key

#### Scenario: allowed_keys=None uses default set

- **GIVEN** an agent YAML file with keys `model` and `runtime`
- **WHEN** `load_agent_overlay("agent")` is called without `allowed_keys`
- **THEN** it SHALL accept only `{"model", "runtime"}` and reject all others

#### Scenario: Missing agent file returns empty dict

- **GIVEN** no file exists at `~/.tdt/agents/agent-core.yaml`
- **WHEN** `load_agent_overlay("agent-core")` is called
- **THEN** it SHALL return `{}`
