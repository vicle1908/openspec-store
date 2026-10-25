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

### Requirement: Closure evidence SHALL cite the canonical route model IDs

Every closure, sentinel, or evidence row produced for an OmniRoute routing change of this family SHALL cite the canonical route model IDs it verified: `sh/gpt-5.6-sol` for the OpenAI Responses route and `pm/Claude-Fable` for the Anthropic Messages route. Evidence rows that substitute any other model ID for these routes are defective; because archived artifacts SHALL NOT be edited after archive, the defect SHALL be corrected through a superseding register in a subsequent active change.

#### Scenario: SH rows cite the SH route model

- **WHEN** closure evidence records the canonical SH route
- **THEN** the row SHALL cite `POST http://localhost:20128/v1/responses` with model `sh/gpt-5.6-sol`
- **AND** an SH row citing a different model ID SHALL be recorded as defective in the superseding register of an active change

#### Scenario: PM rows cite the PM route model

- **WHEN** closure evidence records the canonical PM route
- **THEN** the row SHALL cite `POST http://localhost:20128/v1/messages` with model `pm/Claude-Fable`
- **AND** a PM row citing a non-PM model ID for the Anthropic Messages route SHALL be recorded as defective in the superseding register

#### Scenario: superseding register does not edit archived artifacts

- **WHEN** a defect is found in archived closure evidence
- **THEN** the correction SHALL live in a new active change's evidence register with a citation to the archived file and line
- **AND** the archived artifact SHALL remain byte-identical

### Requirement: The applied-surface register SHALL match the final on-disk state

A routing change's applied-surface register SHALL enumerate every configuration file it applied, with per-file backup reference and rollback command, and SHALL be reconciled against the final on-disk hashes and modes before closure. A file applied after the register's freeze SHALL be appended with its apply timestamp and backup reference; closure SHALL NOT proceed while any applied file is absent from the register.

#### Scenario: post-freeze apply is appended

- **WHEN** a configuration file is applied after the applied-surface register was written
- **THEN** the register SHALL be updated with that file's target path, apply timestamp, backup reference, and current hash/mode before closure
- **AND** closure SHALL NOT proceed while any applied file is absent from the register

#### Scenario: unmapped new-file labels are reconciled

- **WHEN** a closure manifest's new-file list contains a label that maps to no verified applied target
- **THEN** the label SHALL be reconciled to a verified target path or recorded as defective with the verified created files enumerated explicitly
- **AND** the closure SHALL NOT report the unmapped label as a verified creation

#### Scenario: register reconciles against frozen baselines

- **WHEN** the final applied-surface register is produced
- **THEN** each entry SHALL record the frozen pre-apply baseline hash and the final on-disk hash and mode, value-blind
- **AND** any file whose baseline is absent from the register SHALL block closure

### Requirement: Mode tightenings SHALL be named-approved before apply

Any file-mode change that tightens permissions (for example 0644→0600) SHALL be recorded as a named approval in the change's manifest BEFORE the file is applied, identifying target path, old mode, new mode, and approver. An apply-time tightening found without a prior named approval SHALL be surfaced as a ratification gate: the owner either records a retroactive ratification decision or the mode SHALL be reverted with a fresh backup. No further mode tightening SHALL occur while the gate is open.

#### Scenario: unapproved tightening becomes a ratification gate

- **WHEN** a post-apply review finds a mode tightening without a prior named approval
- **THEN** the owning change SHALL record a ratification decision (approve or revert) before closure
- **AND** the file's current mode and pre-apply mode SHALL be recorded value-blind in that decision

#### Scenario: pre-recorded named approval precedes apply

- **WHEN** a planned apply will tighten a file mode
- **THEN** the named approval SHALL exist in the change manifest before the apply executes
- **AND** the apply log SHALL reference the approval entry

### Requirement: Live verification through credential-carrying configs SHALL be rotation-gated

When a configuration file carries literal credentials that were exposed in any session transcript, no live route verification SHALL be executed through that file until the owner explicitly confirms the credentials were rotated upstream or authorizes proceeding without rotation. The gate, its release condition, and the release decision SHALL be recorded in the active change; verification evidence for such surfaces SHALL remain at config level until release, and the surface SHALL NOT be reported as fully verified while blocked.

#### Scenario: rotation gate blocks live sentinel

- **WHEN** a routing change's closure requires a live sentinel through a config carrying exposed literal credentials
- **THEN** the sentinel SHALL be blocked pending the recorded release decision
- **AND** config-level route-contract evidence SHALL be recorded instead
- **AND** the surface SHALL NOT be reported as fully verified while blocked

#### Scenario: release decision is recorded, not assumed

- **WHEN** the rotation gate is to be released
- **THEN** the active change SHALL record an explicit user confirmation (rotation done upstream) or written authorization to proceed without rotation, with a timestamp
- **AND** the released live verification SHALL be executed and recorded before the surface is reported as fully verified

### Requirement: Cline custom provider entries SHALL be registry-backed

Every custom Cline provider entry used for OmniRoute SHALL have a matching provider registry entry in `~/.cline/data/settings/models.json` with the same provider ID, a non-empty model registry, and compatible endpoint metadata. Entries that are absent from the registry SHALL NOT remain as selectable OmniRoute settings entries.

#### Scenario: stale entry is removed

- **WHEN** a Cline settings provider ID has no matching `models.json` registry entry
- **THEN** the stale settings entry SHALL be removed
- **AND** unrelated providers SHALL remain unchanged
- **AND** the existing default selection SHALL remain unchanged unless it points to the removed stale entry, in which case it SHALL be repaired to the verified working provider.

#### Scenario: registry-backed entry is exercised

- **WHEN** a Cline custom provider is treated as a supported route
- **THEN** its ID SHALL resolve through the installed CLI
- **AND** an explicit sentinel call SHALL pass before the route is reported as verified.

### Requirement: The retained Cline OmniRoute provider SHALL use the canonical source-derived model

When the Cline OmniRoute cleanup retains `openai-compatible` as the working provider, its model SHALL be the source-derived canonical model `sh/gpt-5.6-sol`, and its endpoint SHALL remain `http://localhost:20128`.

#### Scenario: noncanonical retained model is corrected

- **WHEN** the retained `openai-compatible` entry uses a noncanonical model
- **THEN** the entry SHALL be updated to `sh/gpt-5.6-sol`
- **AND** a cleanup4-specific live sentinel through the final provider/model pair SHALL be recorded before closure.

### Requirement: Gemini combo SHALL be configured as default across supported coding agents

Supported coding-agent CLIs and editors (`pi`, `omp`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`, `kimi-code`, `zed`, `continue`, and Claude Code OmniRoute profile) SHALL configure the live `gemini-3.8-flash-high` combo as their active default model via OmniRoute using the OpenAI Responses API (`/v1/responses` or `api: openai-responses` / `wire_api: responses`) where supported by the client, or via OmniRoute's OpenAI-compatible ingress / Anthropic Messages ingress for dialect-specific clients. Pre-existing providers SHALL remain preserved. Hermes Agent SHALL preserve its default MoA (Mixture of Agents) configuration with `omniroute:gemini-3.8-flash-high` as aggregator.

#### Scenario: Supported CLIs default to Gemini combo
- **WHEN** coding agents are invoked with default model selection
- **THEN** requests SHALL route through OmniRoute's `gemini-3.8-flash-high` combo
- **AND** clients supporting the Responses API SHALL use `/v1/responses`
- **AND** all existing alternative providers SHALL remain preserved
- **AND** credentials SHALL resolve via environment indirection (`OMNIROUTE_API_KEY`) with zero literal secrets committed

#### Scenario: All supported coding agents default to OmniRoute Gemini 3.8 Flash High
- **WHEN** any supported coding agent CLI (`pi`, `omp`, `codex`, `opencode`, `grok`, `droid`, `prime-agent`, `goose`, `kimi-code`), editor (`zed`), or tool (`continue`) is launched without an explicit model override
- **THEN** it SHALL resolve `gemini-3.8-flash-high` via OmniRoute as its default model
- **AND** pre-existing secondary providers and fallback chains SHALL remain preserved and accessible

#### Scenario: Hermes Agent default MoA is preserved
- **WHEN** Hermes Agent configuration is inspected or loaded
- **THEN** `model.provider` SHALL remain `moa`
- **AND** `model.default` SHALL remain `default`
- **AND** the primary aggregator model SHALL route to `omniroute:gemini-3.8-flash-high`

#### Scenario: Kimi Code CLI defaults to OmniRoute Gemini 3.8 Flash High
- **WHEN** Kimi Code CLI (`kimi`) is launched without an explicit model override
- **THEN** it SHALL resolve `default_model = "gemini-3.8-flash-high"` in `~/.kimi-code/config.toml`
- **AND** model `gemini-3.8-flash-high` SHALL route through provider `omniroute-anthropic` targeting `http://localhost:20128`
- **AND** the model definition SHALL declare `max_context_size = 1000000`, `capabilities = ["thinking", "tool_use"]`, and `default_effort = "high"`
- **AND** the configuration file SHALL maintain permission mode `0600`

### Requirement: Goose CLI workstation runtime SHALL enforce 1M context limit and auto-compaction

The Goose CLI configuration in `~/.config/goose/config.yaml` SHALL specify the full 1,048,576 token context window for both execution and planning, enforce auto-compaction thresholds that trigger before context exhaustion, configure high thinking effort, and enable reasoning block rendering per official Goose specification (`docs/guides/sessions/smart-context-management.md` and `docs/guides/environment-variables.md`).

#### Scenario: Goose loads full 1M context window configuration
- **WHEN** `~/.config/goose/config.yaml` is parsed by Goose CLI
- **THEN** `GOOSE_CONTEXT_LIMIT` and `GOOSE_PLANNER_CONTEXT_LIMIT` SHALL both equal `1048576`
- **AND** `GOOSE_MAX_TOKENS` SHALL equal `65536`
- **AND** `GOOSE_THINKING_EFFORT` and `GEMINI3_THINKING_LEVEL` SHALL be set to `high`
- **AND** `GOOSE_CLI_SHOW_THINKING` SHALL equal `1` to render thinking blocks
- **AND** `GOOSE_TOOL_CALL_CUTOFF` SHALL equal `10`

#### Scenario: Auto-compaction thresholds reserve generation headroom
- **WHEN** a Goose session accumulates context exceeding the 80% threshold (`GOOSE_AUTO_COMPACT_THRESHOLD: 0.8`) of the 1,048,576 token limit (~838,860 tokens)
- **THEN** Goose auto-compaction SHALL trigger under `GOOSE_CONTEXT_STRATEGY: summarize`
- **AND** earlier conversation turns SHALL be condensed into a summary with recent tool outputs trimmed to `GOOSE_TOOL_CALL_CUTOFF: 10`, restoring working context headroom for continued execution

### Requirement: Goose provider declarations SHALL point to OmniRoute loopback without legacy port residue

The custom OmniRoute provider definition in `~/.config/goose/custom_providers/custom_omniroute.json` SHALL specify canonical local loopback routing to OmniRoute (`docs/getting-started/providers.md`), reflect the true 1M context capacity for `gemini-3.8-flash-high` under Tier 1 model configuration precedence, and omit decommissioned model routes. Configuration files SHALL NOT point default fallback URLs to legacy tool ports.

#### Scenario: Custom provider routes to canonical OmniRoute loopback
- **WHEN** `~/.config/goose/custom_providers/custom_omniroute.json` is inspected
- **THEN** `base_url` SHALL be `http://localhost:20128/v1`
- **AND** model `gemini-3.8-flash-high` SHALL declare `context_limit: 1048576`
- **AND** `timeout_seconds` SHALL equal `600`
- **AND** decommissioned model identifiers (`ollamacloud/*`, `sh/*`) SHALL be absent

#### Scenario: Legacy port residue eliminated from default configuration
- **WHEN** `~/.config/goose/config.yaml` is inspected
- **THEN** `OPENAI_BASE_URL` and `OPENAI_HOST` SHALL point to `http://localhost:20128/v1` or be cleared
- **AND** port `51006` SHALL NOT appear anywhere in `config.yaml`
- **AND** `OPENAI_BASE_PATH` SHALL NOT equal `v1/response` and SHALL point to `chat/completions` or be cleared

### Requirement: Goose configuration files and directories SHALL adhere to strict permission boundaries

Configuration directories and files holding Goose runtime and provider settings SHALL be restricted to user-only read/write access.

#### Scenario: Restrictive filesystem permissions enforced
- **WHEN** filesystem permissions for Goose configuration are audited
- **THEN** `~/.config/goose` and `~/.config/goose/custom_providers` SHALL be mode `0700`
- **AND** `~/.config/goose/config.yaml` and all JSON files in `~/.config/goose/custom_providers/` SHALL be mode `0600`

### Requirement: Goose MCP tool surface SHALL remain multiplexed via mcp-router stdio bridge

Goose CLI tool integrations SHALL remain unified under the `@mcp_router/cli` stdio bridge without creating redundant point-to-point server declarations.

#### Scenario: Single multiplexed MCP router extension verified
- **WHEN** active extensions in `~/.config/goose/config.yaml` are enumerated
- **THEN** `mcp-router` SHALL be enabled with `cmd: npx`, `args: ["-y", "@mcp_router/cli@latest", "connect"]`, and `env_keys: ["MCPR_TOKEN"]`
- **AND** no duplicate individual stdio entries for `gitnexus`, `graphify`, or `agentmemory` SHALL be declared

### Requirement: Muse Code CLI SHALL route default inference through OmniRoute combo `muse-spark-1.3` with sanctioned bearer transport pinning

Meta Muse Code (`muse`) SHALL target local OmniRoute (`http://127.0.0.1:20128/v1`) using explicit `endpoint_transport` bearer pinning (`"auth": "bearer"`) and default model `"muse-spark-1.3"`, while OmniRoute SHALL define a combo named `muse-spark-1.3` backed by the `gemini-3.8-flash-high` pool so `POST /v1/responses` requests are intercepted ahead of the unauthenticated static `muse-code` provider.

#### Scenario: Sanctioned front-door bearer transport prevents CLI auth withholding
- **WHEN** `~/.config/muse/settings.json` is loaded by Muse Code CLI (`v1.0.1+`)
- **THEN** `schema_version` SHALL equal `1`
- **AND** `endpoint_transport.base_url` SHALL equal `"http://127.0.0.1:20128/v1"` with `endpoint_transport.auth` set to `"bearer"`
- **AND** `provider` SHALL equal `"meta"` with `model` set to `"muse-spark-1.3"`
- **AND** Muse Code SHALL transmit the `Authorization: Bearer <OMNIROUTE_API_KEY>` header to `127.0.0.1:20128` without triggering front-door bearer withholding

#### Scenario: OmniRoute combo `muse-spark-1.3` intercepts bare model requests and preserves namespace tools
- **WHEN** Muse Code sends a streaming `POST /v1/responses` request with `"model": "muse-spark-1.3"` and `"type": "namespace"` tool definitions (such as `namespace: "muse"`)
- **THEN** OmniRoute's combo resolver SHALL match the `muse-spark-1.3` combo (`context_length: 1000000`, `context_cache_protection: true`) before static provider lookup and route inference to the `gemini-3.8-flash-high` Antigravity pool (with `agy/gemini-3.8-flash-medium` fallback)
- **AND** OmniRoute SHALL flatten incoming `namespace` tool groups for upstream execution and restore `{"namespace": "muse", "name": "<tool>"}` on returned `function_call` SSE items
- **AND** `GET /v1/muse-code/models` SHALL return HTTP 200 advertising `muse-spark-1.3`

#### Scenario: Unpinned `--base-url` override or missing combo fails closed
- **WHEN** a custom `--base-url` is invoked without matching `endpoint_transport` bearer configuration or when `OMNIROUTE_API_KEY` is absent from `~/.config/muse/auth.json`
- **THEN** the request SHALL be rejected with an explicit authentication error (`401`) or front-door withholding warning rather than falling back to unauthenticated external endpoints

#### Scenario: Pre-flight Responses keepalive and catalog compatibility with Rust SSE decoder
- **WHEN** `muse exec --disable-approval --no-session-log` executes prompt and tool-calling turns against `http://127.0.0.1:20128/v1`
- **THEN** the SSE stream and `/v1/muse-code/models` payload delivered to Muse Code SHALL NOT cause a Rust `serde` deserialization failure on synthetic `response.in_progress` frames or catalog metadata

### Requirement: Muse Code configuration, credentials, and MCP router bridge SHALL enforce workstation security and multiplexing standards

Muse Code user configuration and credential files under `~/.config/muse/` SHALL enforce restrictive user-only file permissions, connect to the workstation's central `mcp-router` over stdio without duplicate point-to-point MCP entries, and expose canonical workstation skills.

#### Scenario: Restrictive permissions on Muse Code configuration and credential stores
- **WHEN** filesystem permissions under `~/.config/muse` are audited
- **THEN** directory `~/.config/muse` SHALL have permission mode `0700`
- **AND** `~/.config/muse/settings.json` and `~/.config/muse/auth.json` SHALL have permission mode `0600`
- **AND** `OMNIROUTE_API_KEY` SHALL be seeded via `muse auth set --provider meta --api-key-stdin` (persisting either macOS Keychain pointer `schema_version: 2` or `TBH_CREDENTIAL_BACKEND=file` `schema_version: 1` in `~/.config/muse/auth.json`) without committing literal secrets to version control

#### Scenario: Multiplexed MCP router registration and skill discovery
- **WHEN** `~/.config/muse/settings.json` and available skills are inspected
- **THEN** `mcpServers.mcp-router` (or legacy alias `mcp_servers.mcp-router`) SHALL declare `"transport": "stdio"`, `"command": "npx"`, `"args": ["-y", "@mcp_router/cli@latest", "connect"]`, `"mode": "optional"`, and `env.MCPR_TOKEN`
- **AND** no redundant individual stdio definitions for `gitnexus`, `graphify`, or `agentmemory` SHALL be duplicated in `settings.json`
- **AND** workstation skills SHALL be discoverable via `muse skills list` (and imported via `muse skills import --from claude --apply` when applicable)

### Requirement: OmniRoute Muse Code compatibility layer SHALL persist across container recreations without dirtying upstream git

Any OmniRoute compatibility layer required by Meta Muse Code (`/muse-code` catalog path rewrite and full `response.in_progress` keepalive envelope on `/v1/responses`) SHALL be wired through untracked deployment overrides (`docker-compose.override.yml` and host-mounted runtime scripts) rather than ephemeral writable-layer container edits or modifications to git-tracked upstream source files in `~/Omniroute`.

#### Scenario: Compatibility layer survives compose down and up lifecycle
- **WHEN** `~/Developer/scripts/docker-service.sh stop` and `~/Developer/scripts/docker-service.sh start` (or `docker compose --profile base down` followed by `docker compose --profile base up -d`) recreate the `omniroute` container without invoking `~/Omniroute/scripts/update.sh`
- **THEN** `GET http://127.0.0.1:20128/v1/muse-code/models` and `GET http://127.0.0.1:20128/muse-code/models` SHALL both return HTTP 200 with a JSON `data` array containing the `muse-spark-1.3` model entry (even when `0` `muse-code` provider connections exist and `muse-spark-1.3` is served via an OmniRoute combo)
- **AND** `POST http://127.0.0.1:20128/v1/responses` pre-flight keepalive frames SHALL normalize both legacy `id:null` and `v3.8.52+` `id:"resp_keepalive_omniroute"` payloads to `response:{id:"resp_keepalive",object:"response",status:"in_progress",output:[],error:null}` compatible with Muse Code's Rust SSE decoder

#### Scenario: Upstream OmniRoute git worktree remains clean
- **WHEN** `git -C ~/Omniroute status --porcelain --untracked-files=no` is executed
- **THEN** the output SHALL be empty with zero modified tracked files (`open-sse/utils/sseHeartbeat.ts` and `scripts/dev/peer-stamp.mjs` restored to `HEAD`)
- **AND** this compose-mounted runtime override SHALL supersede the legacy transient bundle-patch prohibition for the Muse Code compatibility surface

### Requirement: Goose CLI runtime documentation SHALL accurately reflect Chat Completions wire routing

Ecosystem documentation and verification ledgers for the Goose CLI OmniRoute runtime SHALL accurately record that `custom_omniroute` routes over OpenAI Chat Completions (`/v1/chat/completions`) via `OPENAI_BASE_PATH: chat/completions` to avoid the `/v1/responses` pre-flight keepalive decoder incompatibility.

#### Scenario: Wiki and runtime config agree on Chat Completions wire dialect
- **WHEN** `wiki/entities/goose.md` and `~/.config/goose/config.yaml` are inspected
- **THEN** both artifacts SHALL identify `/v1/chat/completions` (`OPENAI_BASE_PATH: chat/completions`) as the active wire protocol for `custom_omniroute`
- **AND** neither artifact SHALL claim that Goose routes default turns through `/v1/responses`

### Requirement: Qwen Code CLI SHALL route default inference through OmniRoute and multiplex MCP via mcp-router

Qwen Code (`qwen` v0.25.2+) SHALL configure `~/.qwen/settings.json` (`$version: 4`, mode `0600`) with a `modelProviders.openai` array entry targeting `http://localhost:20128/v1` via `OMNIROUTE_API_KEY`, `security.auth.selectedType: "openai"`, `model.name: "gemini-3.8-flash-high"`, and a single `mcpServers.mcp-router` stdio bridge while preserving existing Orca lifecycle hooks.

#### Scenario: Qwen Code resolves OmniRoute default model and mcp-router
- **WHEN** `~/.qwen/settings.json` is loaded by Qwen Code CLI (`v0.25.2+`)
- **THEN** `modelProviders.openai` SHALL be a `ModelConfig[]` array containing `id: "gemini-3.8-flash-high"`, `baseUrl: "http://localhost:20128/v1"`, and `envKey: "OMNIROUTE_API_KEY"`
- **AND** `security.auth.selectedType` SHALL equal `"openai"` and `model.name` SHALL equal `"gemini-3.8-flash-high"`
- **AND** `mcpServers.mcp-router` SHALL connect via `command: "npx"`, `args: ["-y", "@mcp_router/cli@latest", "connect"]`, `trust: true`
- **AND** `~/.qwen/settings.json` SHALL have permission mode `0600` while retaining all 12 existing Orca lifecycle hook arrays

### Requirement: Credential-bearing MCP and provider backup files SHALL enforce mode 0600 across all agent surfaces

All MCP configuration files and provider backup files carrying `MCPR_TOKEN` or provider credentials across Copilot, Gemini/Antigravity, Kimi, and Goose SHALL be restricted to permission mode `0600` under named operator approval, audited with symlink-following `stat -L`, and OpenCode SHALL omit duplicate standalone `mcp.agentmemory` entries already multiplexed by `mcp-router`.

#### Scenario: Mode 0644 MCP config and backup files are tightened to 0600 and verified with symlink-following stat -L
- **WHEN** filesystem permissions are audited via `stat -L -f '%Mp%Lp %N'` across `~/.copilot/mcp-config.json`, `~/.gemini/config/mcp_config.json`, `~/.gemini/antigravity/mcp_config.json`, `~/.kimi/mcp.json`, and `~/.config/goose/custom_providers/*.bak*`
- **THEN** every resolved file target (including symlinked `~/.gemini/antigravity/mcp_config.json`) SHALL report permission mode `0600` with byte-identical content verified before and after mode tightening
- **AND** `~/.config/opencode/opencode.json` SHALL route `agentmemory` exclusively through `mcp.mcp-router` without a duplicate `mcp.agentmemory` process

### Requirement: Secondary CLI model selectors and upstream capability flags SHALL align with canonical OmniRoute routes

Kimi Code, Grok, Pi, Block Goose, and Claude Code configurations SHALL align their secondary model selectors with canonical `sh/gpt-5.6-sol` routes, remove decommissioned `ollamacloud/*` and `dlg/*` entries, and enable verified upstream capabilities (`supports_vision: true` in Goose, `minimumVersion` and retry watchdog in Claude Code).

#### Scenario: Kimi Code, Grok, Pi, Goose, and Claude Code reflect canonical selectors and upstream flags
- **WHEN** `~/.kimi-code/config.toml`, `~/.grok/config.toml`, `~/.pi/agent/models.json`, `~/.config/goose/custom_providers/custom_omniroute.json`, and `~/.claude/settings.json` are inspected
- **THEN** `[models.or-gpt-5-6-sol]` in `~/.kimi-code/config.toml` and `[model.omniroute-sol]` in `~/.grok/config.toml` SHALL specify `model = "sh/gpt-5.6-sol"`
- **AND** decommissioned `ollamacloud/*` entries in `~/.pi/agent/` and `dlg/kimi-k2.6` in `~/.kimi/config.toml` SHALL be removed
- **AND** `custom_omniroute.json` in Goose SHALL declare `"supports_vision": true` on `gemini-3.8-flash-high`
- **AND** `~/.claude/settings.json` SHALL configure top-level `"minimumVersion": "2.1.302"` and `env.CLAUDE_CODE_RETRY_WATCHDOG_MAX_USAGE_LIMIT_WAIT_MS: "300000"`

### Requirement: Container lifecycle helpers SHALL preserve OmniRoute Gate 4b SSE compatibility patches

Workstation container lifecycle scripts (`~/Developer/scripts/docker-service.sh` and `~/Developer/scripts/omniroute-watchdog.sh`) SHALL pass `--profile base` when managing `~/Omniroute` and invoke `~/Omniroute/scripts/ensure-muse-wire-compat.sh` whenever the `omniroute` container is started or recreated so the Gate 4b `muse-wire-compat` SSE keepalive and `/v1/muse-code/models` normalization remains applied.

#### Scenario: Container recreate via docker-service or watchdog preserves Muse wire compatibility
- **WHEN** `docker-service.sh up` or `omniroute-watchdog.sh` starts or recreates the `omniroute` container with `--profile base`
- **THEN** `~/Omniroute/scripts/ensure-muse-wire-compat.sh` SHALL verify that neither `response:{id:null,status:"in_progress"}` nor unexpanded `response:{id:"resp_keepalive_omniroute",status:"in_progress"}` remains in `/app/.build/next/server/chunks/*.js` and that `/v1/muse-code/models` and `/muse-code/models` both return HTTP 200 advertising `muse-spark-1.3`

### Requirement: OmniRoute Gemini 4 Argon Tier Combos SHALL Route Exclusively Through Entitled Ultra Antigravity CLI Connections

OmniRoute SHALL expose four top-level routing combos for Gemini 4 Argon (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon`) using `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.candidatePool: ["agy"]`. Each combo SHALL contain three model steps pinned to the three Google AI `Ultra` `agy` CLI connections (`62af823b-f3d7-4e6b-87a9-98069167d4f6` / `vicgnome19094@gmail.com`, `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`, and `338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com`).

#### Scenario: Tier combos resolve exclusively to the two Ultra agy CLI connections
- **WHEN** `GET http://127.0.0.1:20128/api/combos` is queried
- **THEN** combos `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `gemini-4-argon` SHALL each be present with `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.candidatePool: ["agy"]`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-argon-high` and `gemini-4-argon` SHALL each define three `kind: "model"` steps with `model: "agy/gemini-4-argon-high"`, `providerId: "agy"`, and matching email `label` pinned to `connectionId: "62af823b-f3d7-4e6b-87a9-98069167d4f6"` (`vicgnome19094@gmail.com`), `connectionId: "0532bad4-2486-4286-8f06-510e9c678620"` (`vinhvumobile@gmail.com`), and `connectionId: "338764b8-1cd7-4946-b789-ee5dad4c5073"` (`vinhghtk1908@gmail.com`)
- **AND** `gemini-4-argon-medium` SHALL define three `kind: "model"` steps with `model: "agy/gemini-4-argon-medium"`, `providerId: "agy"`, and matching email `label` pinned to those same three `connectionId` values
- **AND** `gemini-4-argon-low` SHALL define three `kind: "model"` steps with `model: "agy/gemini-4-argon-low"`, `providerId: "agy"`, and matching email `label` pinned to those same three `connectionId` values

#### Scenario: Combo health check and dual-protocol inference succeed across all Argon combos
- **WHEN** `POST /api/combos/test`, `POST /v1/responses`, or `POST /v1/chat/completions` is invoked for `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, or `gemini-4-argon`
- **THEN** OmniRoute SHALL dispatch to one of the three `Ultra` `agy` connections and return a valid `200 OK` completion

#### Scenario: Disabled sentinel or unentitled Pro connection fails closed without polluting Argon combos
- **WHEN** any of the 12 non-Ultra `agy` CLI connections is inspected or invoked for `gemini-4-argon*`
- **THEN** none of those 12 `connectionId` values SHALL appear in the `models[]` steps of `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`

### Requirement: Un-Suffixed Manual Antigravity Gemini 4 Argon Catalog Override SHALL Be Absent

OmniRoute's `agy` provider model catalog SHALL NOT retain a manual un-suffixed `gemini-4-argon` (`source: "manual"`) custom model override, ensuring that only upstream-supported tiered model IDs (`agy/gemini-4-argon-high`, `agy/gemini-4-argon-medium`, `agy/gemini-4-argon-low`) are advertised as callable `agy` chat models while top-level `gemini-4-argon` resolves via the combo engine.

#### Scenario: Manual un-suffixed agy/gemini-4-argon override removed from provider models
- **WHEN** `GET /api/provider-models` and `GET /v1/models` are inspected
- **THEN** no `source: "manual"` custom model entry with `id: "gemini-4-argon"` SHALL exist under the `agy` provider
- **AND** top-level `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` SHALL be advertised in `/v1/models` with `owned_by: "combo"`

### Requirement: Workstation Coding Agents and Editors SHALL Expose Tiered Gemini 4 Argon Combos Under Existing OmniRoute Providers Without Altering Startup Defaults
All configurable workstation coding agents and editor integrations SHALL register `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` (`1,000,000` context window; `65,536` max output tokens) under their existing active OmniRoute provider blocks, superseding earlier `sh/*`-only model-list restrictions while preserving every tool's pre-mutation startup default model.

#### Scenario: On-demand selection of Gemini 4 Argon tier combos across OpenAI Responses and Anthropic Messages CLIs
- **WHEN** a user invokes `pi`, `prime-agent`, `hermes`, `opencode`, `kilo`, `codex`, `kimi`, `droid`, `claude` (`omniroute-pm.json`), `qwen`, or `muse` with an explicit selector targeting `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low` under its active OmniRoute provider (`omniroute-responses`, `omniroute`, `omniroute-anthropic`, or `meta`)
- **THEN** the CLI resolves all four selectors in its local catalog parser, dispatches the request to `http://localhost:20128` (`http://127.0.0.1:20128/v1` for Muse Code) over its bound wire dialect (`/v1/responses`, `/v1/messages`, or `/v1/chat/completions`) with verified OmniRoute combo attribution (`X-OmniRoute-Combo-Trace` / zero fallback events), and leaves the tool's unflagged startup default model byte-identical to its pre-mutation snapshot

#### Scenario: Rust Serde Chat Completions clients preserve dialect invariants for Gemini 4 Argon combos
- **WHEN** `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` are registered in Block Goose (`~/.config/goose/custom_providers/custom_omniroute.json`) and Grok Build (`~/.grok/config.toml`)
- **THEN** Block Goose retains `OPENAI_BASE_PATH: chat/completions` (`context_limit: 1048576`, `supports_vision: true`) and Grok Build retains `api_backend = "chat_completions"` (`context_window = 1000000`) on `[model.omniroute-gemini-4-argon{,-high,-medium,-low}]` under `model_provider = "omniroute"`, preventing `/v1/responses` keepalive deserialization failures

#### Scenario: Hermes Agent and Claude Code expose all four Gemini 4 Argon selectors while preserving defaults
- **WHEN** `~/.hermes/config.yaml` and `~/.claude/profiles/omniroute-pm.json` are updated to expose the tiered Gemini 4 Argon combos
- **THEN** `~/.hermes/config.yaml` lists `"gemini-4-argon"`, `"gemini-4-argon-high"`, `"gemini-4-argon-medium"`, and `"gemini-4-argon-low"` in `providers.omniroute.models` while preserving `model.provider: "moa"`, and `~/.claude/profiles/omniroute-pm.json` declares all four selectors plus `"gemini-3.8-flash-high"` in `modelPicker.options` (`behavesAs: "claude-fable-5-1"`) while keeping `"model": "gemini-3.8-flash-high"`

### Requirement: Codex CLI and Muse Code Local Model Catalogs SHALL Advertise Tiered Gemini 4 Argon Selectors Without Dirtying Upstream Git
OpenAI Codex CLI (`~/.codex/cockpit-model-catalog.json`) and Meta Muse Code (`~/.config/muse/settings.json`) SHALL declare `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` in their local model catalogs so interactive `/model` and `/models` TUI pickers list all four selectors alongside existing defaults without modifying `~/.codex/config.toml` or any git-tracked file inside `/Users/androidteam/Omniroute`.

#### Scenario: Codex TUI model catalog lists Gemini 4 Argon tiers with standard tool mode and HTTP SSE transport
- **WHEN** `~/.codex/cockpit-model-catalog.json` is loaded via `model_catalog_json` in `~/.codex/config.toml`
- **THEN** the `models[]` array includes `slug` entries for `"gemini-4-argon"`, `"gemini-4-argon-high"`, `"gemini-4-argon-medium"`, and `"gemini-4-argon-low"` with `"visibility": "list"`, `"prefer_websockets": false`, `"use_responses_lite": false`, `"tool_mode": null`, `"apply_patch_tool_type": "freeform"`, `"context_window": 1000000`, and tier-matched `default_reasoning_level` (`"high"`, `"medium"`, `"low"`) while `~/.codex/config.toml` remains unchanged

#### Scenario: Muse Code composes visible Gemini 4 Argon catalog rows from user settings while keeping muse-spark-1.3 as default
- **WHEN** `muse` initializes its model catalog from `~/.config/muse/settings.json`
- **THEN** `model_catalog` declares `muse-spark-1.3` (`is_default: true`, `visibility: "visible"`) and `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low` (`is_default: false`, `provider_id: "meta"`, `profile_id: "tbh"`, `visibility: "visible"`, `context_limit: 1000000`, `output_limit: 65536`) with matching `model_reasoning_efforts`, top-level `"model"` remains `"muse-spark-1.3"`, and `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` outputs zero lines

### Requirement: External Host Config Writes, Mode Tightening, and Kimi Rotation Gates SHALL Enforce Pre-Mutation SHA-256 and Permission Boundaries
All external host configuration mutations under `/Users/androidteam/` SHALL verify pre-write SHA-256 equality against the mode-`0600` backup in `~/.omniroute/backups/register-gemini-4-argon-across-coding-agents/`, enforce mode `0600` on all provider/credential configuration files (`0644` preserved on `~/.codex/cockpit-model-catalog.json`), record named owner approval for `0644 -> 0600` mode tightening, and cite the accepted-risk rotation waiver for `~/.kimi-code/config.toml`.

#### Scenario: Atomic write verification, permission enforcement, and unconfigured CLI preservation
- **WHEN** configuration updates are applied across the coding-agent fleet
- **THEN** each target file's on-disk SHA-256 matches its pre-mutation backup immediately prior to atomic replacement, all provider/credential configs and backups verify at `0600` (`0644` for `~/.codex/cockpit-model-catalog.json`; `~/.factory/settings.json`, `~/.config/muse/settings.json`, and `~/.qwen/settings.json` tightened to `0600`) via `stat -L -f '%04Lp'`, stale `~/.prime/agent/*.bak*` files are relocated out of `~/.prime/agent/`, and unconfigured/vendor-locked CLIs (`qoder`, `cursor-agent`, `auggie`) and legacy `~/.kimi/config.toml` remain untouched

### Requirement: Muse Code entrypoint compatibility SHALL use URL-prefix rewriting without chunk mutation or static catalog bypass

The compose-mounted `/app/container-entrypoint-compat.sh` and `~/Omniroute/scripts/ensure-muse-wire-compat.sh` SHALL rewrite bare `/muse-code` request paths to `/v1/muse-code` in `/app/peer-stamp.mjs` (`MUSE_CODE_REWRITE_V3`) while delegating `/v1/muse-code/models` to upstream's native authenticated route handler and leaving compiled Next.js server chunks (`/app/.build/next/server/chunks/*.js`) unmodified.

#### Scenario: Entrypoint rewrites /muse-code paths without modifying Next.js server chunks
- **WHEN** `container-entrypoint-compat.sh` or `ensure-muse-wire-compat.sh` runs inside the `omniroute` container (`v3.8.52+`)
- **THEN** `/app/peer-stamp.mjs` SHALL strip any prior V1 or `MUSE_CODE_COMPAT_V2` block and contain the `MUSE_CODE_REWRITE_V3` URL prefix rewrite (`req.url = "/v1" + req.url` for `/muse-code`, `/muse-code/*`, and `/muse-code?*`) without injecting a static model catalog
- **AND** `/app/.build/next/server/chunks/*.js` SHALL remain byte-for-byte identical to the upstream container image layers
- **AND** authenticated `GET /muse-code/models` and `GET /v1/muse-code/models` SHALL return HTTP `200` from upstream's native route advertising `muse-spark-1.3`, while anonymous `GET` returns HTTP `401` when catalog authentication is enabled

#### Scenario: Muse Code binary resolves via canonical Homebrew cask symlink
- **WHEN** `/opt/homebrew/bin/muse` is inspected by workstation toolchain inventory (`inventory-workstation-toolchain.py`)
- **THEN** `/opt/homebrew/bin/muse` SHALL be a symbolic link to the installed Caskroom binary (`/opt/homebrew/Caskroom/muse-code/<version>/muse-binary`) with `is_symlinked_from_brew_bin == True`
- **AND** the macOS Keychain entry `ai.meta.dev.credentials` SHALL be seeded via `muse auth set --provider meta --api-key-stdin` with `~/.config/muse/auth.json` (`mode 0600`) on `schema_version: 2` (`"storage": "keychain"`) so `muse` executes non-interactively without requiring a `TBH_CREDENTIAL_BACKEND=file` override

### Requirement: Encapsulated Nested Combo on `muse-spark-1.3`, Auto-Scored Opus Pool on `claude-opus-5.5`, and Loopback API Bridge Port `20129`

OmniRoute SHALL configure `muse-spark-1.3` (`strategy: "priority"`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`) and `claude-opus-5.5` (`strategy: "auto"`, `nestedComboMode: "flatten"`, `targetTimeoutMs: 25000`) with `context_cache_protection: false`, SHALL pin `gemini-4-argon{,-high,-medium,-low}` to the three entitled `Ultra` `agy` accounts (`62af823b`, `0532bad4`, and `338764b8`), and SHALL set `API_HOST=0.0.0.0` in `/Users/androidteam/Omniroute/.env` so host loopback port `20129` serves bridge requests.

#### Scenario: `muse-spark-1.3` executes `gemini-3.8-flash-high` sub-combo without model-pin warning
- **WHEN** a request targets `muse-spark-1.3`
- **THEN** OmniRoute SHALL match `muse-spark-1.3` (`context_cache_protection: false`, `nestedComboMode: "execute"`, `targetTimeoutMs: 25000`) and execute `gemini-3.8-flash-high` using its 16-factor `auto` strategy without logging false `provider durably unhealthy — dropping pin` warnings

#### Scenario: `claude-opus-5.5` load-balances and pins across all 8 Opus accounts via `auto` strategy
- **WHEN** a request targets `claude-opus-5.5`
- **THEN** OmniRoute SHALL score all 8 `agy` Opus accounts using 16-factor `auto` routing (`tierPriority`, `health`, `quota`) and pin multi-turn sessions via `applySessionStickiness` before falling back to `gemini-3.8-flash-high` targets

#### Scenario: Host loopback port `20129` reaches container API bridge
- **WHEN** a request is sent to `http://127.0.0.1:20129/v1/models` or `http://127.0.0.1:20129/v1/responses`
- **THEN** `apiBridgeServer.ts` (`API_HOST=0.0.0.0` inside the container, mapped to `127.0.0.1:20129:20129` on the host) SHALL accept the connection and serve the response

### Requirement: 15-Account Antigravity Auto Pools for `claude-opus-5.5` and `claude-sonnet-5.5` Without Unentitled Custom 5.5 Model IDs

OmniRoute SHALL configure `claude-opus-5.5` (`15` `agy/claude-opus-4-6-thinking` steps, `targetTimeoutMs: 180000`, `predictiveTtftMs: 60000`) and `claude-sonnet-5.5` (`15` `agy/claude-sonnet-4-6` steps, `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`) with `strategy: "auto"` and `context_cache_protection: false`, and SHALL remove unentitled custom `claude-*-5-5-high` entries from `/api/provider-models` and unstable providers from `auto/*` `candidatePool` lists.

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route across 15 `agy` accounts with tier-matched timeouts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** `claude-opus-5.5` SHALL contain 15 `kind: "model"` steps targeting `agy/claude-opus-4-6-thinking` with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`
- **AND** `claude-sonnet-5.5` SHALL contain 15 `kind: "model"` steps targeting `agy/claude-sonnet-4-6` with `strategy: "auto"`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Unentitled `claude-*-5-5-high` custom models and unstable auto-pool providers are excluded without breaking dedicated combos
- **WHEN** `GET /api/provider-models`, `GET /api/models/alias`, `GET /api/providers`, and `GET /api/combos` are queried
- **THEN** `/api/provider-models` SHALL NOT contain custom `claude-opus-5-5-high` or `claude-sonnet-5-5-high` overrides under `agy` or `antigravity`, and `/api/models/alias` SHALL NOT contain `test-opus-55-high`
- **AND** expired connection `6fb701a5-d060-422c-bc34-0cca543d0eda` (`ollama-cloud`) SHALL have `isActive: false`, while `auto/*` combos SHALL restrict `config.candidatePool` to `["agy", "codex", "github"]` so dedicated combos (`phanmemvip` and `muse-spark-1.3`) remain intact
