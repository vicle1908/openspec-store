# omniroute-agent-cli-routing Specification

## Purpose
Define how coding-agent CLIs register and route OmniRoute `sh/*` models through
documented OpenAI-compatible configuration surfaces, with classification before
mutation, credential indirection, provider and default preservation, and
per-file backup, rollback, and real-call evidence.

## Requirements

### Requirement: Installed CLIs SHALL be inventoried and deduplicated before mutation

Before any configuration mutation, the change SHALL inventory installed coding-agent CLIs, resolve aliases and wrappers to canonical executables, and classify each canonical CLI as supported, profile-only, unconfigured, unsupported, alias, or separate-change-owned.

#### Scenario: Classification recorded before mutation

- **WHEN** the support matrix is produced
- **THEN** each canonical CLI SHALL have a recorded configuration path, official configuration mechanism, protocol compatibility, current default, and classification
- **AND** no CLI SHALL be mutated before its classification row exists

### Requirement: Only documented OpenAI-compatible surfaces SHALL be configured

A CLI SHALL be mutated only when its official documentation or configuration schema exposes an OpenAI-compatible or custom-provider surface that accepts `http://localhost:20128/v1` and environment-backed credentials.

#### Scenario: Supported CLI configured through official surface

- **WHEN** a CLI classified as supported receives an OmniRoute registration
- **THEN** the mutation SHALL use only its documented provider or model configuration surface
- **AND** no framework source, binary wrapper, or unofficial adapter SHALL be modified

#### Scenario: Unsupported or unconfigured CLI left unchanged

- **WHEN** a CLI has no documented mechanism for a custom OpenAI-compatible endpoint, or requires vendor authentication that is not present
- **THEN** its configuration SHALL remain unchanged
- **AND** it SHALL be reported as unsupported or unconfigured with the observed reason

### Requirement: OmniRoute registrations SHALL use the live `sh/*` namespace with credential indirection

Every OmniRoute model registration added by this change SHALL use a model ID present in the live `sh/*` registry at apply time, and SHALL reference `OMNIROUTE_API_KEY` through the CLI's environment-variable mechanism rather than a literal credential value. A CLI with no documented environment indirection for provider keys MAY retain a literal key in its mode-600 configuration file as a documented exception.

#### Scenario: Model IDs validated against the live registry

- **WHEN** a `sh/*` model ID is written into a CLI configuration
- **THEN** that ID SHALL exist in a fresh `GET http://localhost:20128/v1/models` response captured during apply
- **AND** retired `dlg/*` inference routes SHALL NOT be added to any active configuration

#### Scenario: No literal credentials where env indirection exists

- **WHEN** a configuration file changed by this change supports environment indirection
- **THEN** it SHALL contain no literal API key value
- **AND** the OmniRoute credential SHALL be referenced only through `OMNIROUTE_API_KEY` or the CLI's documented environment indirection

### Requirement: Registration SHALL preserve existing providers and defaults

Adding OmniRoute provider or model entries SHALL NOT remove existing providers or change a CLI's default model unless a specific default change is explicitly approved for that CLI.

#### Scenario: Existing providers preserved

- **WHEN** an OmniRoute provider entry is added to a CLI configuration
- **THEN** all providers present before the mutation SHALL remain present afterward
- **AND** the configuration SHALL parse cleanly after the mutation

#### Scenario: Default unchanged without explicit approval

- **WHEN** a CLI's default model selection is not explicitly approved for change
- **THEN** the default SHALL be byte-identical before and after the mutation

### Requirement: Every mutation SHALL carry backup, rollback, and real-call evidence

Each configuration file mutated by this change SHALL receive a mode-600 backup with recorded hash before mutation, and the mutated CLI SHALL pass an isolated real sentinel call before the mutation is considered complete.

#### Scenario: Backup captured before mutation

- **WHEN** a configuration file is about to be mutated
- **THEN** a backup copy with mode 600 and a recorded content hash SHALL be created first
- **AND** the backup SHALL remain available until the change is archived

#### Scenario: Real sentinel call verifies the route

- **WHEN** a CLI configuration has been mutated
- **THEN** one isolated, read-only, one-turn real call with an exact sentinel string SHALL be executed against the OmniRoute endpoint
- **AND** the call SHALL exit 0 with the expected sentinel and no authentication or reconnect error
- **AND** credential values SHALL NOT appear in the recorded evidence

#### Scenario: Failed gate triggers per-file rollback

- **WHEN** parse validation or the sentinel call fails for a mutated CLI
- **THEN** that file SHALL be restored atomically from its backup
- **AND** the CLI SHALL be reported as a blocker without blocking verification of independent CLIs

### Requirement: Known OmniRoute SSE heartbeat defect SHALL be documented as a routing blocker

The OmniRoute server emits a malformed `response.in_progress` SSE heartbeat event (missing the `response` object and `sequence_number` fields) during slow first-token phases. CLIs with strict Responses-API stream decoders SHALL be documented as blocked by this server-side defect, and their registrations SHALL remain valid catalog entries even while runtime routing through the Responses dialect fails.

#### Scenario: strict-decoder CLI registered but runtime-blocked

- **WHEN** a CLI with a strict Responses-API decoder (such as goose) is registered against OmniRoute
- **THEN** its catalog registration SHALL remain in place
- **AND** the evidence manifest SHALL record the heartbeat defect as the runtime blocker
- **AND** the blocker SHALL be attributed to the OmniRoute server, not to the CLI registration
