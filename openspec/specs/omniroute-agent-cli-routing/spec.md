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

Every OmniRoute model registration added or corrected by this change SHALL use one of the live requested namespace/model pairs: `pm/Claude-Fable` for the Anthropic Messages route or `sh/gpt-5.6-sol` for the OpenAI Responses route. The exact model ID SHALL be present in a fresh `GET http://localhost:20128/v1/models` response at apply time. Retired `dlg/*` inference routes SHALL NOT be added to or retained in an active OmniRoute registration owned by this change. Credentials SHALL use `OMNIROUTE_API_KEY` through the CLI's documented environment, helper, or provider-key mechanism; literal credentials are prohibited except for the documented Kimi Code limitation when its installed provider contract cannot resolve shell variables.

#### Scenario: Requested namespace IDs are validated against the live catalog

- **WHEN** an OmniRoute model entry is added or corrected
- **THEN** `pm/Claude-Fable` or `sh/gpt-5.6-sol` SHALL exist in the fresh live model response
- **AND** the entry SHALL preserve the exact namespace and punctuation
- **AND** no new `dlg/*` entry SHALL be written

#### Scenario: Credentials remain external

- **WHEN** a changed CLI supports environment-backed provider credentials
- **THEN** the configuration SHALL reference `OMNIROUTE_API_KEY` or an approved helper
- **AND** no literal credential value SHALL appear in the configuration, OpenSpec artifacts, logs, process arguments, or evidence
- **AND** the Kimi Code limitation SHALL be recorded if its mode-600 provider field must retain an existing literal value

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

The goose runtime blocker SHALL be documented as a two-part strict-decoder incompatibility, not a single server defect. Part 1: OmniRoute emits a malformed `response.in_progress` SSE heartbeat event (missing the `response` object and `sequence_number` fields) during slow first-token phases on the `/v1/responses` path; the frame and its 15s interval are build-inlined into the Next.js bundle, so the documented `SSE_HEARTBEAT_INTERVAL_MS` env var has no effect. Part 2: goose's strict Responses-API decoder also rejects the upstream's `response.created` event for lacking a `model` field, even when OmniRoute is bypassed. CLIs with strict Responses-API stream decoders SHALL be documented as blocked by these defects, and their registrations SHALL remain valid catalog entries. Vendor build artifacts SHALL NOT be hotfixed as a workaround.

#### Scenario: strict-decoder CLI registered but runtime-blocked

- **WHEN** a CLI with a strict Responses-API decoder (such as goose) is registered against OmniRoute
- **THEN** its catalog registration SHALL remain in place
- **AND** the evidence manifest SHALL record both blocker parts with their exact decoder errors
- **AND** the blocker SHALL be attributed to the goose decoder strictness combined with OmniRoute and upstream event shapes, not to the CLI registration

#### Scenario: heartbeat env var verified ineffective before workaround attempts

- **WHEN** a workaround for the malformed heartbeat is considered
- **THEN** `SSE_HEARTBEAT_INTERVAL_MS` SHALL first be tested at 0 and at a large value with per-event timestamp evidence
- **AND** if the build-inlined 15s interval is confirmed, env-var-based mitigation SHALL be recorded as ineffective

#### Scenario: vendor bundle hotfix is prohibited

- **WHEN** the malformed heartbeat frame is located in the built Next.js bundle chunks
- **THEN** in-container replacement of bundle files SHALL NOT be used as a durable fix
- **AND** any experimental bundle patch SHALL be reverted, with the container restored to its original state
- **AND** the resolution SHALL be pursued through upstream OmniRoute or goose fixes instead

#### Scenario: clean streaming path documented

- **WHEN** the `/v1/chat/completions` streaming path is tested with a slow prompt
- **THEN** it SHALL be recorded as emitting zero malformed heartbeat events
- **AND** CLIs able to use the chat-completions dialect SHALL be documented as unaffected by the heartbeat defect

#### Scenario: chat-completions route selected empirically

- **WHEN** a chat-completions route is selected to bypass the heartbeat defect for a strict-decoder CLI
- **THEN** the exact endpoint SHALL be selected from live per-model evidence rather than assumed, distinguishing SSE cleanliness from model availability: the versioned `/v1/chat/completions` path is SSE-clean but returned HTTP 502 for `sh/gpt-5.6-sol`, while the versionless `/chat/completions` path returned HTTP 200 with the expected sentinel
- **AND** the selected route SHALL pass the baseline-relative no-regression gate before any live configuration change

### Requirement: Codex registration SHALL use model_providers with env_key indirection

If Codex is mutated by this change, the omniroute `model_provider` entry in ~/.codex/config.toml SHALL set base_url `http://localhost:20128/v1`, wire_api `responses`, and env_key `OMNIROUTE_API_KEY`, SHALL make the live `sh/*` model IDs selectable, and SHALL leave the global default model unchanged. Codex is outside the nine-consumer registry, so this requirement lives in the routing capability.

#### Scenario: codex provider added without default change

- **WHEN** ~/.codex/config.toml is inspected after mutation
- **THEN** a `model_provider` named omniroute SHALL exist with base_url `http://localhost:20128/v1`, wire_api `responses`, and env_key `OMNIROUTE_API_KEY`
- **AND** the top-level model field SHALL remain `gpt-5.6-sol`

### Requirement: Goose transport changes SHALL pass a baseline-relative no-regression gate

Any live change to a goose OmniRoute provider configuration SHALL be preceded by an isolated variant matrix frozen at the current live settings, and a candidate SHALL be evaluated relative to that baseline for every model registered on the provider. A candidate SHALL NOT be applied if it newly breaks any model that passed at baseline. Failures present identically at baseline and under the candidate SHALL NOT disqualify the candidate and SHALL be recorded as separate findings.

#### Scenario: variant matrix run in isolation

- **WHEN** a transport variant (base_path or supports_streaming change) is evaluated
- **THEN** it SHALL run in isolated temporary HOMEs with the live provider file hash asserted unchanged before and after
- **AND** each registered model SHALL be probed at least three times per variant with assistant-content, usage, and error classification captured

#### Scenario: baseline-relative evaluation

- **WHEN** a candidate variant is evaluated
- **THEN** each registered model's result SHALL be compared against the frozen baseline matrix
- **AND** a model that passed at baseline SHALL still pass under the candidate for the candidate to be applied

#### Scenario: pre-existing failures recorded, not attributed

- **WHEN** a registered model fails identically at baseline and under the candidate (for example catalog-unavailable registrations returning the same HTTP 400)
- **THEN** the failure SHALL be recorded as a pre-existing separate finding
- **AND** it SHALL NOT disqualify the candidate or be attributed to it

#### Scenario: dedicated provider proven before live addition

- **WHEN** the preferred application is a separate dedicated provider
- **THEN** the provider file SHALL first pass an isolated 3x-per-model matrix in a temporary HOME
- **AND** it SHALL be proven selectable by explicit provider ID, including a negative control showing an unknown provider ID fails
- **AND** the existing provider SHALL be hash-verified unchanged

#### Scenario: live application is minimal and reversible

- **WHEN** the gate passes and the change is applied
- **THEN** either a new provider file is added whose registered models are exactly the proven set, with the existing provider byte-identical and rollback being file deletion, or a single proven field changes on the existing provider with a mode-600 backup and atomic restore
- **AND** three consecutive live rounds across the affected models SHALL pass with real assistant content before the change is considered complete
- **AND** no configured default SHALL change without explicit approval

### Requirement: Droid bare-exec default SHALL be classified as vendor behavior

The Droid CLI's bare `droid exec` default model (`claude-opus-5`, Factory cloud) SHALL be documented as vendor-owned CLI behavior. `sessionDefaultSettings.model` does not govern `exec`; the failure of a bare `droid exec` without Factory cloud auth SHALL NOT be classified as an OmniRoute route failure.

#### Scenario: vendor default recorded without mutation

- **WHEN** Droid verification results are recorded
- **THEN** the bare-exec default SHALL be documented with the help-text literal as evidence
- **AND** explicit OmniRoute custom-model invocations and the existing wrapper SHALL be verified to pass
- **AND** no Droid configuration SHALL be mutated by this change

### Requirement: Literal-credential configuration files SHALL be mode 600

Configuration files in the nine-CLI OmniRoute scope that contain literal credential values SHALL be mode 600. Permission hardening SHALL alter only file modes; credential values SHALL NOT be printed, compared, rotated, or overwritten by this change. The confirmed files for this change are `~/.pi/agent/mcp.json`, `~/.config/opencode/opencode.json`, `~/.kimi/config.toml`, and `~/.kimi-code/config.toml`.

#### Scenario: confirmed files hardened with identity proof

- **WHEN** a format-aware audit confirms a mode-644 file containing literal credentials
- **THEN** a timestamped mode-600 backup SHALL be created outside Git before the change
- **AND** the file SHALL be changed to mode 600 with SHA-256 byte-identity proven before and after
- **AND** a post-change functional probe SHALL confirm the owning CLI still loads its configuration

#### Scenario: rotation recorded as user-owned follow-up

- **WHEN** credential values have appeared in session tool output
- **THEN** rotation SHALL be recorded as a user-owned security follow-up
- **AND** the change itself SHALL NOT rotate, replace, or delete any credential value

### Requirement: Follow-up changes SHALL verify, roll back, and clean up

Every track in a follow-up change SHALL carry verification evidence, a rollback path, and probe-artifact cleanup before closure.

#### Scenario: verification before closure

- **WHEN** a track claims completion
- **THEN** it SHALL cite captured evidence (exit codes, assistant content, hashes) rather than narration
- **AND** unrelated files and uncommitted work SHALL be preserved and reported separately

#### Scenario: rollback on regression

- **WHEN** a post-mutation verification round fails
- **THEN** the mutated file SHALL be restored atomically from its backup, or an added file SHALL be deleted
- **AND** the regression SHALL be reported without blocking verification of independent tracks

#### Scenario: cleanup after evidence capture

- **WHEN** all evidence is captured
- **THEN** temporary scripts, evidence files, temp HOMEs, and probe-owned processes SHALL be removed
- **AND** long-lived unrelated services SHALL remain untouched

### Requirement: Prime Agent OmniRoute registration SHALL preserve the reviewed allowlist

Prime Agent's `omniroute` provider registration SHALL use its documented custom-provider configuration surface with base URL `http://localhost:20128/v1`, API `openai-responses`, and `OMNIROUTE_API_KEY` environment indirection. Its reviewed model allowlist SHALL be exactly `sh/codex` and `sh/gpt-5.6-sol`. Existing Prime Agent providers and default model selection SHALL remain unchanged.

#### Scenario: Prime Agent provider registration matches the reviewed allowlist

- **WHEN** `~/.prime/agent/models.json` is inspected
- **THEN** the `omniroute` provider SHALL have `baseUrl: http://localhost:20128/v1`, `api: openai-responses`, and `apiKey: OMNIROUTE_API_KEY`
- **AND** its model list SHALL contain exactly `sh/codex` and `sh/gpt-5.6-sol`

#### Scenario: Prime Agent defaults and providers remain preserved

- **WHEN** the Prime Agent configuration is inspected after the OmniRoute registration
- **THEN** the existing `phanmemvip`, `shopapikey`, and `cockpit` providers SHALL remain present
- **AND** the default provider and default model selection SHALL remain unchanged

### Requirement: Namespace and native wire dialect SHALL be bound explicitly

A consumer that supports Anthropic Messages SHALL route `pm/Claude-Fable` through its Anthropic Messages implementation and SHALL target the OmniRoute `/v1/messages` route. A consumer that supports OpenAI Responses SHALL route `sh/gpt-5.6-sol` through its Responses implementation and SHALL target the OmniRoute `/v1/responses` route. A model SHALL NOT be registered under the other native dialect merely because a cross-dialect raw request happens to return HTTP 200.

#### Scenario: Claude namespace uses Anthropic Messages

- **WHEN** a CLI's native Anthropic provider is configured for OmniRoute
- **THEN** its effective wire model SHALL be `pm/Claude-Fable`
- **AND** its effective request SHALL be `POST http://localhost:20128/v1/messages`
- **AND** it SHALL NOT use `sh/Claude-Fable` as the Claude model for that provider

#### Scenario: GPT namespace uses OpenAI Responses

- **WHEN** a CLI's native Responses provider is configured for OmniRoute
- **THEN** its effective wire model SHALL be `sh/gpt-5.6-sol`
- **AND** its effective request SHALL be `POST http://localhost:20128/v1/responses`
- **AND** its reasoning control SHALL use a live-supported effort tier

### Requirement: Chat Completions SHALL be an exception-only fallback

A CLI SHALL use the Chat Completions dialect for an OmniRoute requested model only when its native Messages or Responses implementation is unavailable or fails a product-specific compatibility gate. The fallback SHALL be selected from live endpoint evidence, SHALL preserve the exact requested model ID, and SHALL use the versionless `http://localhost:20128/chat/completions` target in the current deployment. The failing versioned `http://localhost:20128/v1/chat/completions` route SHALL NOT be substituted for `sh/gpt-5.6-sol`.

#### Scenario: Native client incompatibility selects the proven fallback

- **WHEN** a bounded product-specific probe demonstrates that the installed client cannot decode the required native stream
- **THEN** the configuration MAY select a documented Chat Completions provider
- **AND** the provider SHALL target the empirically proven versionless route
- **AND** the evidence SHALL name the native decoder failure and the fallback route separately

#### Scenario: Native route passes

- **WHEN** the product-specific native probe returns the exact sentinel, supported thinking output, and required tool lifecycle
- **THEN** the native provider SHALL remain selected
- **AND** the change SHALL NOT downgrade it to Chat Completions merely for uniformity

### Requirement: Thinking configuration SHALL match the requested model and provider dialect

Each changed CLI SHALL declare reasoning/thinking only through fields supported by its native provider implementation. `pm/Claude-Fable` SHALL use Anthropic thinking controls or the CLI's documented Anthropic effort mapping; `sh/gpt-5.6-sol` SHALL use OpenAI Responses reasoning effort from `none`, `low`, `medium`, `high`, or `xhigh`. A client SHALL NOT send an OpenAI `reasoning.effort` field on the Anthropic Messages route or an Anthropic `thinking` body on the Responses route unless its documented adapter explicitly translates that field.

#### Scenario: PM thinking is separated from answer text

- **WHEN** a native Anthropic Messages client invokes `pm/Claude-Fable` with thinking enabled
- **THEN** the provider request SHALL use the client's Anthropic thinking control
- **AND** the response SHALL be parsed with thinking and answer content as separate semantic blocks where the client exposes them
- **AND** a successful final answer alone SHALL NOT be recorded as proof that thinking was enabled

#### Scenario: SH reasoning effort is accepted

- **WHEN** a native Responses client invokes `sh/gpt-5.6-sol` with `high` or `xhigh` effort
- **THEN** the request SHALL use the client's Responses reasoning control
- **AND** the response SHALL preserve reasoning/message separation or report the client's documented normalization
- **AND** an unsupported effort value SHALL be rejected or downgraded only according to the CLI's documented behavior

### Requirement: Installed CLI support SHALL be classified before mutation

The change SHALL maintain a matrix for every installed coding-agent CLI, including executable identity, version, effective configuration surface, native protocol support, credential mechanism, default identity, and ownership classification. Unsupported, unconfigured, vendor-auth-only, alias, and separate-change-owned surfaces SHALL remain unchanged unless a later evidence-backed task explicitly reclassifies them.

#### Scenario: Matrix prevents unsupported mutation

- **WHEN** a CLI has no documented custom endpoint or environment/provider surface that can express the requested route
- **THEN** its configuration SHALL remain unchanged
- **AND** the evidence SHALL record the exact observed reason and classification

#### Scenario: Alias is verified once

- **WHEN** multiple command names resolve to the same canonical executable
- **THEN** the matrix SHALL identify the canonical executable and avoid duplicate mutation or duplicate success claims

### Requirement: Native route acceptance SHALL be client-specific

A raw HTTP success SHALL establish gateway protocol availability only. A CLI route SHALL be accepted only after a bounded explicit client call proves the exact model selection, final assistant content, exit status, configured endpoint, thinking/reasoning behavior where supported, and tool-call lifecycle where supported. Explicit-route evidence SHALL remain distinct from configured-default evidence.

#### Scenario: Raw success is not promoted to CLI success

- **WHEN** a raw Messages or Responses probe returns HTTP 200
- **THEN** the corresponding CLI SHALL remain unverified until its native invocation is separately exercised
- **AND** the evidence SHALL preserve the raw protocol result and CLI result as separate dimensions

#### Scenario: Default route is checked separately

- **WHEN** an explicit OmniRoute model selector passes
- **THEN** the CLI SHALL still receive a no-provider/no-model sentinel probe
- **AND** the resulting default provider/model SHALL be recorded independently
- **AND** an existing default SHALL not be changed implicitly

### Requirement: Per-file rollback SHALL cover dialect regressions

Every user configuration file mutated by this change SHALL receive a mode-600 backup and byte hash before mutation. A parse failure, wrong endpoint, wrong model namespace, thinking mismatch, tool lifecycle failure, or client decoder regression SHALL trigger immediate atomic restoration of that file without reverting unrelated user changes.

#### Scenario: Dialect regression rolls back one file

- **WHEN** a post-apply sentinel proves that a CLI is using the wrong namespace or dialect
- **THEN** only that file SHALL be restored atomically from its pre-apply backup
- **AND** the CLI SHALL be reported as blocked or unchanged
- **AND** independent CLI verification SHALL continue
