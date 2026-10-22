# workstation-toolchain-inventory Specification

## Purpose
Defines the sanctioned install locations for workstation tooling, the single declared npm global
prefix, the preferred package-manager source per tool, the authoritative-location rule, and how
duplication and name collisions are detected and reported before any copy is treated as
reclaimable.

## Requirements

### Requirement: Sanctioned install locations

Workstation tooling SHALL be installed only into sanctioned roots (`~/.npm-global`, `~/.bun`, `~/.local/share/home-toolchain`, `/opt/homebrew`, `~/.local/share`, `~/.local/bin`, `~/.kimi-code`, `~/.qoder`, `~/.pi`, `~/.hermes`, `~/.grok`) and SHALL NOT be installed into unscoped `$HOME` directories (`~/node_modules` or `~/.local/lib/node_modules`).

#### Scenario: Tool installed into an unsanctioned location
- **WHEN** a node package is installed into a directory that is not a sanctioned location, such as `~/.local/lib/node_modules` or `~/node_modules`
- **THEN** the inventory SHALL report it as an unsanctioned installation
- **AND** the report SHALL identify the sanctioned location that would own it instead

#### Scenario: All installations are sanctioned
- **WHEN** every installed copy of every inventoried tool resolves into one of the sanctioned locations and no `~/node_modules` or `~/.local/lib/node_modules` exists
- **THEN** the inventory SHALL report no unsanctioned installations
### Requirement: The declared npm global prefix is authoritative and singular

The workstation SHALL declare one npm global prefix (`npm config get prefix` matching the
maintenance pipeline prefix), and `$HOME` SHALL NOT contain `package.json`, lockfiles
(`package-lock.json`, `pnpm-lock.yaml`, `pnpm-workspace.yaml`, `bun.lock`, `bun.lockb`,
`yarn.lock`), or `node_modules` that hijack `npm prefix` from `~/Developer`. Any prefix split or
`$HOME` hijack SHALL be reported as a defect.

#### Scenario: npm's effective prefix disagrees with the intended prefix

- **WHEN** npm's reported global prefix differs from the prefix the maintenance pipeline passes
  to `npm install -g`, as when `node` is installed by the system package manager and sets npm's
  default prefix while the pipeline targets a user prefix
- **THEN** the inventory SHALL report both prefixes, identify which one `npm install -g` without
  `--prefix` would use, and identify which one the pipeline uses
- **AND** it SHALL classify the split as a defect to be reconciled by declaration

#### Scenario: Home directory artifacts hijack local npm prefix resolution

- **WHEN** `$HOME` contains `node_modules`, `package.json`, `package-lock.json`, `pnpm-lock.yaml`,
  `pnpm-workspace.yaml`, or `bun.lock`, causing `npm prefix` executed in `~/Developer` to resolve
  to `$HOME`
- **THEN** `inventory-workstation-toolchain.py` SHALL report `home_prefix_hijacked: true` and
  list the offending `$HOME` artifacts in `prefix_reconciliation`
- **AND** it SHALL classify the prefix reconciliation status as `split_detected`

#### Scenario: Prefixes agree

- **WHEN** npm's reported global prefix equals the prefix the maintenance pipeline installs into
  and equals the declared prefix, no package-manager artifacts or `node_modules` exist directly
  in `$HOME`, and `npm prefix` in `~/Developer` resolves to `~/Developer`
- **THEN** the inventory SHALL report the prefix as reconciled (`home_prefix_hijacked: false`)
- **AND** no prefix defect SHALL be raised

### Requirement: Preferred package-manager source is used where one exists

Where a system or vendor package manager provides a tool and official documentation names it as
an installation channel, that source SHALL be preferred over unsigned downloads or manual
placement, and the inventory SHALL report installations bypassing a documented source. When
multiple channels are documented, the inventory SHALL record all documented channels and resolve
version authority from the active installation.

#### Scenario: Homebrew ships the tool

- **WHEN** a tool is installed by means other than Homebrew while Homebrew provides it as a
  formula or cask, including a third-party tap or cask
- **THEN** the inventory SHALL report the available Homebrew asset and the current installation
  method
- **AND** the report SHALL identify the Homebrew-managed installation as a documented preferred
  source where the tool's documentation names Homebrew as an installation channel

#### Scenario: No package manager provides the tool

- **WHEN** no system or vendor package manager provides a tool, so it is available only through
  an ecosystem package manager or a vendor download
- **THEN** the inventory SHALL record that no preferred package-manager source exists
- **AND** the inventory SHALL record the installed copy's verified ecosystem manager or vendor
  release channel as its source of record, or record unknown ownership with evidence gaps

#### Scenario: Vendor documentation names multiple channels

- **WHEN** a tool's official documentation names both an ecosystem package manager and Homebrew
  as installation channels, as `codex` documents both `npm install -g @openai/codex` and
  `brew install --cask codex`
- **THEN** the inventory SHALL record both channels as documented
- **AND** the selection SHALL be resolved by the version-authority rule rather than by
  preference alone

#### Scenario: Active installation resolves channel tie

- **WHEN** a tool's documentation names multiple channels and the tool is installed via an
  authorized documented channel
- **THEN** the inventory SHALL recognize the active installation's channel as the authoritative
  source
- **AND** it MUST NOT report an uninstalled documented channel as bypassing a preferred source

### Requirement: Homebrew-adjacent installations are not misattributed

An installation whose executable is a symbolic link placed inside the system package manager's
binary directory, but which resolves into an ecosystem package manager's module directory, SHALL
be recorded as owned by the ecosystem package manager and SHALL NOT be reported as
package-manager-managed.

#### Scenario: Ecosystem install symlinked into the package manager's bin directory

- **WHEN** an executable under the system package manager's `bin` directory resolves, through a
  symbolic link, into another package manager's global module directory
- **THEN** the inventory SHALL report the resolved target's owning package manager as the owner
- **AND** it SHALL report the package manager as not owning that installation

#### Scenario: Genuinely package-manager-managed installation

- **WHEN** an executable under the package manager's `bin` directory resolves into the package
  manager's own versioned cellar or caskroom
- **THEN** the inventory SHALL report the package manager as the owner

### Requirement: Name collisions are recorded before a migration is proposed

Where a preferred source provides a similarly named but different tool, the collision SHALL be
recorded and the tools SHALL be distinguished, so that a migration to the preferred source cannot
silently replace one tool with another.

#### Scenario: Preferred source provides a different tool of the same name

- **WHEN** a package manager provides an asset whose name matches an installed tool but whose
  purpose differs, or which originates from a different upstream
- **THEN** the inventory SHALL record both the installed tool's identity and the available
  asset's identity
- **AND** it MUST NOT propose replacing the installed tool with that asset

#### Scenario: Preferred source shadows another package

- **WHEN** a package manager's available asset for a tool originates from a third-party tap and
  shadows a package of the same name in the primary tap
- **THEN** the inventory SHALL record the originating tap
- **AND** the shadowing relationship SHALL be reported alongside the preferred-source result

### Requirement: Authoritative location per tool

Each tool SHALL have exactly one authoritative installation, defined as the copy the shell
resolves when the tool is invoked by name. Every other installed copy of the same tool SHALL be
classified as a duplicate and marked non-authoritative.

#### Scenario: Tool resolves to a determined copy

- **WHEN** a tool is invoked by name
- **THEN** the inventory SHALL record the resolved executable path as that tool's authoritative
  installation
- **AND** it SHALL record every other copy of the same tool as a duplicate

#### Scenario: Duplicate copies exist

- **WHEN** a tool is present in more than one sanctioned location, as with a global command and a
  toolbelt dependency of the same name
- **THEN** the inventory SHALL report each location, its measured size, and which copy is
  authoritative
- **AND** it MUST NOT delete or relocate any copy without separate operator authorization

### Requirement: Duplication is reported before it is reclaimable

Duplicated tool installations SHALL be reported with measured sizes and the identifiers of the
owning tools, and SHALL remain non-reclaimable until the owning tool is confirmed to resolve
correctly from the intended location alone.

#### Scenario: Duplicate is reported with its owner

- **WHEN** the inventory detects a tool installed in multiple locations
- **THEN** it SHALL record the tool name, each installation path, each measured size, and the
  owning package manager for each
- **AND** the total reclaimable estimate SHALL be labelled an estimate, not a guarantee

#### Scenario: Removal is not implied by duplication

- **WHEN** a duplicate installation is identified
- **THEN** the inventory MUST NOT remove it
- **AND** it SHALL state the verification required before the duplicate can be reclaimed

### Requirement: Path resolution correctness is verifiable

The inventory SHALL verify that each tool still resolves and executes from its authoritative
location after any consolidation, so that removing a duplicate cannot silently break the tool.

#### Scenario: Authoritative tool still executes after consolidation

- **WHEN** a duplicate installation is reclaimed
- **THEN** the authoritative installation's entry point SHALL execute and report a version with
  exit status zero

#### Scenario: Tool fails to resolve after consolidation

- **WHEN** a tool no longer resolves or executes after a duplicate is reclaimed
- **THEN** the consolidation SHALL be treated as failed and the duplicate restored
- **AND** the inventory SHALL record the failing resolution path

### Requirement: Exactly one version authority per tool

Each installed tool SHALL have exactly one version authority: the single mechanism permitted to determine the version installed. The inventory SHALL record the active executable entrypoint, installing asset, update command, actual version writer, target scope, and release channel as distinct facts. Delegated commands SHALL NOT be recorded as separate writers. Where configured or scheduled independent writers target the same tool, the inventory SHALL report an authority conflict.

#### Scenario: Tool-native updater with compatible manager delegation

- **WHEN** a tool provides a native update command that inspects its installation context and delegates
  to its installing package manager, as `opencode upgrade` delegates to `brew upgrade`
- **THEN** the inventory SHALL record the installing manager as the actual version writer and the native
  command as a compatible update entrypoint
- **AND** no authority conflict SHALL be reported between that entrypoint and manager for that verified
  installation scope
- **AND** this determination SHALL NOT suppress any independently detected target, channel, or location
  findings

#### Scenario: Configured or scheduled independent writers produce authority conflict

- **WHEN** an installed tool has an active update mechanism and a configured or scheduled independent
  writer capable of modifying its installation without coordination
- **THEN** the inventory SHALL report a version-authority conflict finding naming both mechanisms and
  their write paths
- **AND** it SHALL record the consequence that uncoordinated updates risk version divergence or unintended
  reversion

#### Scenario: Update path presents target-misalignment risk

- **WHEN** an update action's effective write target (evaluated across environment variables, package
  receipts, and updater configuration) targets a directory or prefix different from the active
  installation root on `$PATH`
- **THEN** the inventory SHALL report a target-misalignment risk identifying the active installation root
  and the divergent write target
- **AND** this risk SHALL be reported distinctly from an authority conflict or measured version drift

#### Scenario: Tool without compatible native update path uses supported manager authority

- **WHEN** an installed tool has no compatible supported native update path for its active installation
  and is managed by a system or ecosystem package manager
- **THEN** the package manager SHALL be recorded as the actual version writer and authority
- **AND** no authority conflict SHALL be reported for that installation path

#### Scenario: Version authority or source version cannot be determined

- **WHEN** available evidence is insufficient to determine a tool's active executable provenance,
  actual version writer, or owning asset
- **THEN** the inventory SHALL record the version authority as unknown with explicit evidence gaps
- **AND** automated update actions for that tool SHALL be gated until resolved

### Requirement: Elected version authority governs tool updates and pipeline backstops

The elected version authority SHALL govern tool update handling across all pipeline mutation stages. Standalone local authority audits SHALL execute offline without mutations. Full check mode SHALL execute no update verbs and mutate no installations, configurations, or manager metadata. In apply mode, the pipeline SHALL invoke authorized update paths, verifying active entrypoint resolution on `$PATH` and active install root currency while respecting user background settings as-is.

#### Scenario: Local authority audit executes non-mutating check

- **WHEN** local inventory and coverage reporters execute during an authority audit or check run
- **THEN** they SHALL run locally without executing update verbs or mutating installations,
  configuration, or package-manager metadata
- **AND** standalone local reporter executions SHALL require no network access

#### Scenario: Pipeline apply mode invokes backstop via elected authority

- **WHEN** the maintenance pipeline runs in apply mode
- **THEN** it SHALL invoke the authorized update command for each eligible covered tool according to
  its elected version authority, permitting compatible native delegators or verified manager commands
- **AND** it MUST NOT execute unauthorized or misaligned write actions against that tool

#### Scenario: Backstop invocation is idempotent and verifies outcome

- **WHEN** the pipeline invokes an authorized update command for a tool that is already current
- **THEN** the invocation SHALL complete with an observable successful outcome without unintended
  version alteration
- **AND** the runner SHALL verify that the active executable entrypoint on `$PATH` resolves to the
  current version within the active installation root

#### Scenario: Native background auto-update status is audited as-is

- **WHEN** an installed tool provides native background auto-update configuration
- **THEN** the inventory SHALL audit and report the observed configuration settings as-is
- **AND** the pipeline MUST NOT mutate or overwrite the user's update configuration

#### Scenario: All mutation stages respect elected version authority

- **WHEN** the maintenance pipeline executes package-manager upgrade stages, including Homebrew, Bun,
  and npm
- **THEN** the pipeline SHALL guard package upgrades to exclude tools whose version authority is elected
  as native and lacks manager delegation
- **AND** it MUST NOT permit earlier stages to execute unauthorized writes against tools governed by
  later stages

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

### Requirement: Manifest and registry single-owner alignment for dual-installed and standalone tools

`config/workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, `config/uv-tools.json`, `config/Brewfile`, and `scripts/toolchain_updater_registry.py` SHALL declare consistent single-owner records for `codex`, `opencode`, `openspec`, `newman`, `hermes`, `qwen`, `ruff`, `pytest`, `prime-agent`, `cce`, `goose`, `droid`, and `copilot-cli`.

#### Scenario: Manifest and Brewfile agree on Homebrew Cask/Formula vs npm-global authority
- **WHEN** `inventory-workstation-toolchain.py --json` evaluates `codex`, `opencode`, `openspec`, `newman`, `ruff`, `pytest`, `qwen`, `prime-agent`, `cce`, and `hermes`
- **THEN** `codex` and `opencode` SHALL have a single declared authority matching `config/Brewfile` (`brew-cask` `codex` and `brew-formula` `anomalyco/tap/opencode`) once shadowed `~/.npm-global` duplicates are reclaimed
- **AND** `openspec` SHALL declare `npm-global` (`~/.npm-global/bin/openspec`, `@fission-ai/openspec`) as its sole authority once the undeclared `/opt/homebrew/bin/openspec` formula is removed
- **AND** `hermes` (`hermes-agent`) SHALL declare `standalone` (`~/.hermes/hermes-agent`, updated via `hermes update`) rather than an uninstalled `brew-formula`
- **AND** `qwen` (`qwen-code`), `newman`, `ruff`, and `pytest` SHALL declare `brew-formula` matching their `/opt/homebrew/bin/` installations

### Requirement: Sanitized reporter PATH and vendor-download recognition for Qoder and Kimi

`inventory-workstation-toolchain.py` SHALL include `~/.qoder` and `~/.kimi-code` in `sanctioned_roots`, include `~/.qoder/entry` and `~/.kimi-code/bin` in its inspection `PATH`, and classify `~/.qoder/bin/qodercli/qodercli-*` and `~/.kimi-code/bin/kimi` as sanctioned `vendor_download` installations rather than misaligned npm packages.

#### Scenario: Qoder, qodercli, and kimi resolve cleanly without false-positive target misalignment
- **WHEN** `inventory-workstation-toolchain.py --json` runs in standalone or scheduled check mode
- **THEN** `qoder` (`~/.qoder/entry/qoder`), `qodercli` (`~/.local/bin/qodercli` -> `~/.qoder/bin/qodercli/*`), and `kimi` (`~/.kimi-code/bin/kimi`) SHALL resolve as `INSTALLED` under `vendor_download` authority
- **AND** none of the three tools SHALL emit a false-positive `TARGET_MISALIGNMENT`, `NOT_INSTALLED`, or unsanctioned-location defect

### Requirement: Homebrew Cellar symlink integrity and Cask self-update reconciliation

The inventory and operator runbook SHALL detect unlinked regular binaries in `/opt/homebrew/bin/` that shadow newer Homebrew Cellar versions (such as `/opt/homebrew/bin/goose` `1.54.0` blocking `/opt/homebrew/Cellar/block-goose-cli/1.55.0`) and Cask binaries mutated in-place by internal self-updaters (`droid` `0.238.0` Caskroom receipt vs `0.242.0` binary vs `0.244.0` upstream).

#### Scenario: Unlinked Homebrew binary blocking Cellar symlink is reconciled
- **WHEN** `/opt/homebrew/bin/goose` is a regular file (`1.54.0`) while `/opt/homebrew/Cellar/block-goose-cli/1.55.0` is installed
- **THEN** operator-authorized `brew link --overwrite block-goose-cli` SHALL restore the symlink to Cellar `1.55.0`
- **AND** `goose --version` SHALL report `1.55.0`

#### Scenario: Cask receipt drift is reconciled via Homebrew Cask upgrade
- **WHEN** `droid` (`0.238.0` Cask receipt / `0.242.0` binary) and `copilot-cli` (`1.0.95` Cask) lag upstream (`0.244.0` and `1.0.98`)
- **THEN** upgrading via `brew upgrade --cask droid copilot-cli` SHALL align both the Caskroom receipt and active binary version with upstream

### Requirement: Multi-root duplicate reclamation gates for gitnexus, bun, newman, and buf

Before reclaiming duplicate installations of `gitnexus` (`~/.local/share/home-toolchain` and `~/.local/lib/node_modules/gitnexus`, ~1.21 GiB), `bun` (`~/.bun/bin/bun`), `newman`, and `~/go/bin/buf`, the inventory SHALL record each path and size (including `opencode-ai` in `node_modules`) and verify post-removal resolution from the sole authoritative path.

#### Scenario: Authoritative gitnexus and buf remain functional after duplicate cleanup
- **WHEN** duplicate non-authoritative copies of `gitnexus` and `~/go/bin/buf` (`1.72.0`) are removed under operator authorization
- **THEN** `which gitnexus` SHALL resolve to `~/.npm-global/bin/gitnexus` (`1.6.12`) and `which buf` SHALL resolve to `/opt/homebrew/bin/buf` (`1.74.0`) with exit status `0`

### Requirement: Workstation toolchain manifest registration and non-standard installation auditing

`config/workstation-toolchain-manifest.json` SHALL register `tools.orca` under `profiles.ai-agents` with `brew-cask` authoritative ownership, `orca --version` verification command, and `brew upgrade --cask stablyai/orca/orca` supported verb, and workstation health inspections SHALL audit non-standard installations including corrupted Caskroom receipts, orphaned formulae, shadowed duplicates, and PATH precedence inversions.

#### Scenario: Orca registered as first-class AI agent tool
- **WHEN** `config/workstation-toolchain-manifest.json` is validated by `python3 scripts/test-version-authority-governance.py`
- **THEN** `tools.orca` SHALL specify `authoritative_owner: "brew-cask"` and `update_authority: "brew"`
- **AND** `orca` SHALL be listed in `profiles.ai-agents`
- **AND** the test suite SHALL pass with exit code `0`

#### Scenario: Non-standard package installation and metadata audit reporting
- **WHEN** system-wide toolchain and package audits are performed
- **THEN** package managers SHALL report any corrupted Caskroom metadata (such as missing receipts in `/opt/homebrew/Caskroom/`), orphaned formulae with no upstream taps, deprecated versions, and shadowed duplicates in `~/.local/share/home-toolchain`
- **AND** the findings SHALL be recorded for operator remediation rather than silently discarded or destructively purged

### Requirement: Workstation toolchain manifest and inventory classification for Herdr

The workstation toolchain manifest and inventory scripts SHALL register `herdr` under `profiles.ai-agents` with `brew-formula` authoritative ownership, `brew` update authority, and `herdr --version` smoke verification.

#### Scenario: Herdr registered as Homebrew-formula AI agent tool in manifest
- **WHEN** the actual manifest and read-only inventory report are inspected
- **THEN** `tools.herdr` SHALL specify `authoritative_owner: "brew-formula"`, `active_path_pattern: "{{HOMEBREW_PREFIX}}/bin/herdr"`, `update_authority: "brew"`, `supported_verb: "brew upgrade herdr"`, and `verification_smoke_command: "herdr --version"`
- **AND** `herdr` SHALL be listed in `profiles.ai-agents` without containing literal user home paths

#### Scenario: Toolchain inventory classifies Herdr under Homebrew formula authority
- **WHEN** the read-only inventory evaluates Herdr's active executable
- **THEN** `herdr` SHALL resolve under its declared Homebrew formula authority without a Herdr-specific unknown-source or target-misalignment finding
- **AND** unrelated installed-tool findings SHALL remain visible rather than be suppressed to make this change pass

#### Scenario: Shadowed ~/.local/bin/herdr duplicate is flagged if present
- **WHEN** a standalone installer copy exists at `{{HOME}}/.local/bin/herdr` alongside `/opt/homebrew/bin/herdr`
- **THEN** the inventory SHALL report `{{HOME}}/.local/bin/herdr` as a shadow path under `known_shadow_paths`

### Requirement: Scheduler integrity validation SHALL reconcile authority and manifest drift without false degradation on aligned local-dev tools

The scheduler integrity validation step SHALL reconcile `authority_reconciliation` against `manifest_reconciliation` so uncovered local-dev tools that are aligned in the workstation manifest do not trigger false-positive degradation, while true manifest drift, authority conflicts, or unknown tools fail closed.

#### Scenario: Aligned manifest with uncovered local-dev bundle passes integrity validation
- **WHEN** `step_integrity_and_store_validation()` evaluates `inventory-workstation-toolchain.py --json` where `manifest_reconciliation` has `status: "aligned"` (`drift_count == 0`, `missing_count == 0`, `unsanctioned_count == 0`, `unknown_count == 0`) and `authority_reconciliation` has `conflict_count == 0` and `unknown_count == 0`
- **THEN** uncovered `target_misalignment` entries (`updater_dispatch == "none"`, such as `prime-agent`) that are `state: "aligned"` in `manifest_reconciliation` SHALL NOT mark `step_integrity_and_store_validation()` as `DEGRADED`
- **AND** `step_integrity_and_store_validation()` SHALL return `status: "SUCCESS"` with `errors: []`

#### Scenario: Unaligned target misalignment, manifest drift, conflict, or unknown tool degrades integrity validation
- **WHEN** `inventory-workstation-toolchain.py --json` reports `conflict_count > 0`, `unknown_count > 0`, `manifest_reconciliation` drift/missing/unsanctioned/unknown counts `> 0`, or a `target_misalignment` item that is not `aligned` in `manifest_reconciliation`
- **THEN** `step_integrity_and_store_validation()` SHALL return `status: "DEGRADED"` and append a diagnostic entry to `errors`

### Requirement: Workstation toolchain manifest and inventory classification for OMP

The workstation toolchain manifest, Homebrew bundle manifest, updater registry, and inventory scripts SHALL register `omp` under `profiles.ai-agents` with `brew-formula` authoritative ownership (`can1357/tap/omp`, `/opt/homebrew/bin/omp`), `brew` update authority, `omp --version` smoke verification, and symlink-aware shadow-path (`os.path.lexists`) and Cellar source verification.

#### Scenario: OMP registered as Homebrew-formula AI agent tool in manifest and Brewfile
- **WHEN** `config/workstation-toolchain-manifest.json`, `config/Brewfile`, and `python3 -m unittest tests/test_portable_workstation_slice_a.py` are inspected and executed
- **THEN** `tools.omp` SHALL specify `authoritative_owner: "brew-formula"`, `active_path_pattern: "{{HOMEBREW_PREFIX}}/bin/omp"`, `update_authority: "brew"`, `release_channel: "stable"`, `dispatch_classification: "none"`, `verification_smoke_command: "omp --version"`, `writer_binary: "brew"`, `supported_verb: "brew upgrade can1357/tap/omp"`, `delegating_to: null`, `package_name: "can1357/tap/omp"`, and `category: "ai-agent"`
- **AND** `omp` SHALL be listed in `profiles.ai-agents` and `config/Brewfile`, and `test_portable_workstation_slice_a.py` and `scripts/test-version-authority-governance.py` SHALL exit `0`

#### Scenario: Toolchain inventory classifies OMP under Homebrew formula authority and monitors shadow paths
- **WHEN** `python3 scripts/inventory-workstation-toolchain.py --json` evaluates installed tools
- **THEN** `.manifest_reconciliation.items.aligned` SHALL contain an entry with `name: "omp"` and `state: "aligned"`, and `.authority_reconciliation.items` SHALL contain an entry with `name: "omp"`, `authority: "brew-formula"`, and `drift_status: "clean"` verified via `derive_install_root_and_source`
- **AND** `inventory_tools()` SHALL map `omp` to `@oh-my-pi/pi-coding-agent` and inspect `known_shadow_paths` (`{{HOME}}/.bun/bin/omp` and `{{HOME}}/.npm-global/bin/omp`) using symlink-aware existence checks (`sh_path.is_symlink() or sh_path.exists()`) so any non-Homebrew shadow binary or dangling symlink is flagged as a duplicate and `target_misalignment`

### Requirement: Core JavaScript runtime and package-manager manifest and global roster parity

`config/workstation-toolchain-manifest.json`, `scripts/toolchain_updater_registry.py`, `scripts/inventory-workstation-toolchain.py`, and `config/npm-global-tools.json` SHALL declare complete, non-overlapping ownership records for the core JavaScript/TypeScript runtimes and package managers (`node`, `npm`, `pnpm`, `bun`) and for all sanctioned CLI packages installed under `~/.npm-global`.

#### Scenario: Core JavaScript runtimes and package managers registered in manifest and updater registry
- **WHEN** `config/workstation-toolchain-manifest.json`, `scripts/toolchain_updater_registry.py`, and `scripts/inventory-workstation-toolchain.py` are validated by `tests/test_portable_workstation_slice_a.py` and `scripts/test-version-authority-governance.py`
- **THEN** `tools.node`, `tools.npm`, `tools.pnpm`, and `tools.bun` SHALL be declared in `config/workstation-toolchain-manifest.json` under `profiles.core` with `authoritative_owner: "brew-formula"`, `update_authority: "brew"`, `writer_binary: "brew"`, and `active_path_pattern` under `{{HOMEBREW_PREFIX}}/bin/`
- **AND** `derive_install_root_and_source()` in `scripts/inventory-workstation-toolchain.py` SHALL classify Homebrew's bundled `/opt/homebrew/lib/node_modules/npm` (and `/usr/local/lib/node_modules/npm`) under `brew-formula`
- **AND** `tools.bun` SHALL list `{{HOME}}/.bun/bin/bun` in `known_shadow_paths` and `tools.pnpm` SHALL list `{{HOME}}/Library/pnpm/pnpm` and `{{HOME}}/.npm-global/bin/pnpm` in `known_shadow_paths`
- **AND** `sanctioned_roots` in `config/workstation-toolchain-manifest.json` and `is_path_sanctioned()` in `scripts/inventory-workstation-toolchain.py` SHALL include `~/.bun`

#### Scenario: Sanctioned npm-global-tools.json matches installed global CLI packages without profile overlap
- **WHEN** `config/npm-global-tools.json` is compared against `npm list -g --depth=0 --prefix ~/.npm-global` and validated by `TestLayeredProfiles`
- **THEN** `config/npm-global-tools.json` SHALL declare all 15 sanctioned global CLI packages (`openspec`, `gitnexus`, `kilo`, `auggie`, `happy`, `agentmemory`, `agentmemory-mcp`, `brightdata`, `anydoc`, `grepai`, `mcpr`, `deepwiki`, `codexuse`, `exa`, `node-gyp`)
- **AND** the declared tool names in `config/npm-global-tools.json` SHALL remain strictly disjoint from `config/Brewfile` and `config/uv-tools.json`
