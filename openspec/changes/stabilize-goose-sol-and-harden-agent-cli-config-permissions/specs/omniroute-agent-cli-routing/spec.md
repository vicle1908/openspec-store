# omniroute-agent-cli-routing Delta

## MODIFIED Requirements

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

## ADDED Requirements

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
