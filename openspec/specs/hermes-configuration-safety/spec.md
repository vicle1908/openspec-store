## Purpose

Provides a safe, repeatable contract for migrating, storing, backing up, validating, and rolling back Hermes configuration without disclosing credentials or losing unrelated local state.

## ADDED Requirements

### Requirement: Configuration SHALL use the supported migration path

Hermes configuration changes SHALL use the installed Hermes CLI's supported configuration commands, and the resulting configuration SHALL match the installed schema before the gateway is restarted.

#### Scenario: Migration is available
- **WHEN** the installed Hermes version reports an older configuration schema
- **THEN** the operator can run the supported migration command and inspect the resulting non-secret configuration before activation

#### Scenario: Migration leaves unsupported keys
- **WHEN** configuration validation still reports deprecated or unknown keys after migration
- **THEN** activation is blocked until each key is removed, replaced, or explicitly documented as compatible

### Requirement: Credentials SHALL remain outside tracked planning artifacts

OpenSpec artifacts, reports, logs, and diagnostics SHALL contain only credential names or redacted status and SHALL NOT contain secret values, tokens, passwords, authorization headers, or credential-bearing file contents.

#### Scenario: Configuration is audited
- **WHEN** the operator records current configuration findings
- **THEN** secret-bearing values are represented only by redacted placeholders or presence/absence status

#### Scenario: A credential is found in a settings file
- **WHEN** a credential-like value is found in `config.yaml` or another non-secret settings artifact
- **THEN** the operator records the finding without repeating the value and handles rotation/migration as a separately authorized action

### Requirement: Full-access approval policy SHALL be explicit

The shared default profile used by authorized CLI/Desktop and Telegram sessions SHALL explicitly configure Hermes command approvals off, headless dangerous-command and subagent-thread approval on, destructive session confirmations off, MCP reload confirmation off, and memory/skill write approval off. User deny, permanent allowlist, and globally disabled-toolset overrides SHALL resolve to empty lists. Hermes SHALL retain secret redaction, protected credential-path guards, the immutable hardline command blocklist, gateway user authorization, and runtime prerequisite checks.

#### Scenario: Authorized command executes without a Hermes prompt
- **WHEN** an authorized session requests a dangerous command that is not part of the immutable hardline blocklist
- **THEN** Hermes executes it without an approval prompt and records normal command output/diagnostics

#### Scenario: Headless cron command executes
- **WHEN** an authorized cron job requests a dangerous command outside the hardline blocklist
- **THEN** Hermes applies the configured cron approval policy and executes it without waiting for an unavailable interactive response

#### Scenario: Delegated command executes unattended
- **WHEN** a subagent thread requests a dangerous command outside the immutable hardline blocklist
- **THEN** `delegation.subagent_auto_approve` permits the command without falling back to an unavailable terminal prompt

#### Scenario: Security floor remains enforced
- **WHEN** a session requests an immutable catastrophic terminal command or asks `write_file` or `patch` to mutate a protected credential path
- **THEN** Hermes rejects the operation even though normal approvals are disabled

#### Scenario: Autonomous profile state changes
- **WHEN** the agent's memory or skill learning loop creates, edits, or removes profile-local state
- **THEN** the change is applied without write-approval staging and remains observable through the supported profile status/review surfaces

### Requirement: Backups SHALL be proportionate and recoverable

The Hermes update policy SHALL select a supported pre-update backup mode appropriate to the default profile's state size and operational value. Before CRITICAL-risk in-place activation, the operator SHALL create and verify both a quick critical-state snapshot and a full archive outside Hermes home, and SHALL record the version-correct stop/restore/start procedure.

#### Scenario: Routine update is prepared
- **WHEN** an operator prepares a routine Hermes update
- **THEN** a supported quick or full pre-update backup is created according to the selected policy and its artifact path and size are recorded without exposing contents

#### Scenario: High-risk activation is prepared
- **WHEN** the operator prepares to apply full-access configuration to the shared default profile
- **THEN** `hermes backup --quick` produces a complete manifest with no failed or oversized-skipped databases and full backup produces a zip with no skipped-file warnings, valid zip integrity, and Hermes marker files

#### Scenario: Update recovery is required
- **WHEN** an update fails or introduces a regression
- **THEN** the operator can identify the pre-update revision and restore Hermes state using the documented rollback procedure with all Hermes processes stopped before restarting the gateway

#### Scenario: Quick state restore is required
- **WHEN** the operator restores a v0.19.0 quick snapshot
- **THEN** the restore is invoked through classic CLI `/snapshot restore <id>` rather than a nonexistent top-level `hermes snapshot` command, with gateway/Desktop/TUI processes stopped first

### Requirement: Configuration validation SHALL precede activation

A default-profile configuration change SHALL be validated with Hermes diagnostics before the existing gateway is restarted.

#### Scenario: Validation passes
- **WHEN** `hermes config check`, `hermes doctor`, and the relevant profile/tool/MCP inventories report no blocking issue
- **THEN** the profile is eligible for activation

#### Scenario: Validation fails
- **WHEN** a blocking diagnostic reports invalid configuration, missing authorization, unsafe MCP transport, or an unavailable required capability
- **THEN** the gateway remains on the last known-good configuration and the failure is recorded for correction

### Requirement: Sensitive local state SHALL use restrictive permissions

Hermes credential stores and transcript-bearing state SHALL be readable only by the owning user unless Hermes explicitly requires broader permissions for a documented service integration.

#### Scenario: Permission audit is performed
- **WHEN** the operator checks Hermes home permissions
- **THEN** the audit reports the modes of configuration, environment, auth, session, and database files without reading their contents

#### Scenario: Permission is too broad
- **WHEN** a credential or transcript-bearing file is readable by other users
- **THEN** the operator can correct its permissions through a separately authorized local maintenance action before exposing the gateway

### Requirement: Full-access network and browser policy SHALL be explicit

The shared default profile SHALL permit private/local-network URL access and unrestricted browser evaluation when the browser capability is available, while retaining Hermes' documented secret-redaction pipeline. Cloud-metadata and link-local credential endpoints SHALL remain blocked by the immutable URL-safety floor.

#### Scenario: Private URL is requested
- **WHEN** an authorized session navigates to a localhost, RFC1918, CGNAT, or other permitted private-network URL
- **THEN** Hermes permits the request when the browser/web backend is available, except for immutable metadata/link-local credential endpoints

#### Scenario: Browser evaluation is requested
- **WHEN** an authorized session evaluates JavaScript in the configured browser context
- **THEN** Hermes permits the evaluation without the optional evaluate restriction denylist

#### Scenario: Synthetic secret canary reaches a documented redaction surface
- **WHEN** an approved test sends a synthetic canary through a Hermes-managed conversation/tool-output surface covered by the redaction pipeline
- **THEN** the canary is redacted from conversation context and user-facing delivery, while arbitrary third-party subprocess or adapter logs are reviewed separately and are not claimed to have an absolute guarantee
