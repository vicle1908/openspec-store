# Spec Delta

## ADDED Requirements

### Requirement: Supported updater declarations are conservative and installation-aware
The inventory and coverage reports SHALL recognize an update command only when the command is verified for the tool and active installation source in the supported-updater registry. An absent, ambiguous, or unverified command MUST be reported as having no supported automated update path and MUST be excluded from automated mutation.

#### Scenario: Unverified command is rejected
- **WHEN** a declaration contains a nonempty command that is not registered for the tool and active source
- **THEN** the report SHALL classify the updater as unsupported or unknown
- **AND** the maintenance runner MUST NOT execute that command

#### Scenario: Kilo uses its supported command
- **WHEN** Kilo is installed through the active npm channel and its supported CLI command is inspected
- **THEN** the recorded command SHALL be `kilo upgrade`
- **AND** the report MUST NOT advertise `kilo update`

### Requirement: Wrapper entrypoints inherit resolved target authority
A wrapper or symlink entrypoint SHALL inherit the resolved target's installation source, actual writer, target scope, drift status, and update eligibility. Surface wrapper location or display name MUST NOT create a separate authority or bypass a target gate.

#### Scenario: Qoder wrapper targets a misaligned npm package
- **WHEN** `qoder` resolves through its wrapper to an npm package whose active target is prefix-misaligned
- **THEN** the inventory SHALL report the wrapper with the target's misalignment
- **AND** the pipeline SHALL deny the wrapper without a tool-name-specific exception

#### Scenario: Wrapper target cannot be resolved
- **WHEN** a wrapper target or its ownership evidence cannot be resolved
- **THEN** the report SHALL classify authority as unknown with an evidence gap
- **AND** automated mutation for the wrapper MUST be gated

### Requirement: Homebrew Node-backed formulas remain Homebrew-owned
A resolved path under a Homebrew Cellar or Caskroom SHALL remain package-manager-owned even when the path contains `node_modules` or a scoped package segment. Inventory duplication output SHALL include both the authoritative copy and every discovered duplicate.

#### Scenario: Cellar formula embeds node_modules
- **WHEN** a Homebrew formula executable resolves through `Cellar/.../libexec/.../node_modules/...`
- **THEN** the source SHALL be reported as Homebrew formula ownership
- **AND** it MUST NOT be reported as an ecosystem package symlink solely because `node_modules` appears in the path

#### Scenario: Authoritative copy coexists with a duplicate
- **WHEN** the active copy and another sanctioned copy of the same tool are discovered
- **THEN** the duplication report SHALL include both copies with authority labels and measured metadata
- **AND** it MUST NOT report a clean single-copy state

### Requirement: Remediation targets preserve the declared npm prefix
When an ecosystem-managed installation is outside the declared npm prefix, remediation guidance SHALL identify the declared sanctioned prefix as the migration target and SHALL distinguish that recommendation from the currently active root. It MUST NOT recommend writing to an inferred system prefix merely because the active package resides there.

#### Scenario: Scoped package is active under Homebrew
- **WHEN** a scoped npm package is active under `/opt/homebrew` while the declared global prefix is the user npm prefix
- **THEN** the report SHALL identify the active root as misaligned
- **AND** any migration command SHALL target the declared user prefix

### Requirement: Pause state is normalized and applied consistently
The reporters SHALL normalize boolean, numeric, and string representations of update-pause settings, including `DISABLE_UPDATES` and `DISABLE_AUTOUPDATER`, and SHALL apply a global pause policy to every covered tool without changing the user's configuration.

#### Scenario: Boolean pause setting is enabled
- **WHEN** a supported configuration contains `DISABLE_UPDATES=true`, `1`, or boolean `true`
- **THEN** the report SHALL mark automated updates paused
- **AND** the pipeline MUST skip eligible update mutations while retaining audit output

#### Scenario: Pause setting is absent
- **WHEN** no recognized pause setting is enabled
- **THEN** the report SHALL not mark tools paused solely from an unrelated configuration key
- **AND** normal authority gating SHALL still apply

### Requirement: Scheduled writer discovery is value-blind and bounded
The inventory SHALL inspect accessible user LaunchAgents, accessible system LaunchAgents, and the user's crontab for candidate update writers, recording only structural metadata and environment-variable keys. It SHALL state that root-owned LaunchDaemons, inaccessible system jobs, container engines, and arbitrary script indirection are outside the scan boundary.

#### Scenario: Scheduled updater is visible
- **WHEN** an accessible launchd plist or user crontab entry invokes a recognized package-manager or tool updater
- **THEN** the report SHALL identify its label or schedule, executable baseline, source path, and relevant environment-key names
- **AND** it MUST NOT emit environment values, tokens, passwords, or raw command secrets

#### Scenario: Scheduled writer is outside scope
- **WHEN** a possible writer is hidden behind inaccessible system ownership or arbitrary script indirection
- **THEN** the report SHALL record the bounded unknown or limitation
- **AND** it MUST NOT claim that no competing writer exists
