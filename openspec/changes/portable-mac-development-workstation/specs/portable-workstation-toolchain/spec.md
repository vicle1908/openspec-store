# Spec Delta

## Purpose

This capability defines reproducible, owner-aware macOS development tooling that can be inspected, bootstrapped, verified, and documented across workstations without migrating secrets, persistent volumes, or machine-local state.

## ADDED Requirements

### Requirement: Tool ownership and update authority SHALL be explicit

Every managed development tool SHALL declare exactly one authoritative installation owner, active executable path pattern, update authority, release channel, dispatch mode (`native`, `delegating`, `none`), and verification smoke command within the versioned manifest. A tool with multiple installations across different roots SHALL be reported as drifted until duplicate copies are reconciled under explicit gates.

#### Scenario: Duplicate executable resolution
- **WHEN** the inventory finds multiple installations for one executable across different roots (e.g. Homebrew, npm-global, standalone)
- **THEN** verification SHALL report the resolved active executable, all detected duplicate paths, and the owner mismatch without deleting any file

#### Scenario: Aligned executable
- **WHEN** the resolved active executable matches the declared authoritative installation owner and path pattern
- **THEN** verification SHALL report the tool as aligned and record its active version evidence

#### Scenario: Unsanctioned or ambiguous updater
- **WHEN** a maintenance updater is configured to update a tool from a package manager that does not own the active executable
- **THEN** the update runner SHALL suppress automated mutation for that tool and record the updater as misaligned

#### Scenario: Updater dispatch classification matches vendor authority
- **WHEN** an updater is registered for a tool in the updater registry
- **THEN** the registration SHALL record the authoritative writer binary, dispatch mode (`native`, `delegating`, `none`), and supported verb
- **AND** an npm-installed tool lacking a native updater command (e.g. `codex`) SHALL NOT be dispatched via an invalid self-update command

### Requirement: Central authoring and external execution SHALL be strictly gated

Workstation automation SHALL separate central schema and manifest authoring in `platform/openspec-store` from external execution on host roots and remote services. Any modification to external directories (`~/Developer/scripts/`, `~/.zshrc`, `~/.zshenv`, `~/Library/LaunchAgents/`, `/opt/homebrew`, `~/.npm-global`, Notion, AgentMemory) SHALL require explicit external scope authorization and an External Execution Packet.

#### Scenario: Central authoring root boundary
- **WHEN** planning artifacts, schemas, or manifest templates are authored or revised
- **THEN** all file writes SHALL remain within `platform/openspec-store`
- **AND** central `/opsx:apply` `allowedEditRoots` SHALL NOT authorize modifications outside `platform/openspec-store`

#### Scenario: External execution packet verification
- **WHEN** an authorized external execution action completes
- **THEN** the runner SHALL emit an execution packet recording target root, source commit, bounded command, timestamps, exit code, item counts, source-preservation status, read-back verification data, and evidence hashes

#### Scenario: Missing external authorization blocks mutation
- **WHEN** an external action lacks an explicit scope authorization or exact-path approval
- **THEN** the workflow SHALL fail closed, emitting a blocked status without altering any host file or service

### Requirement: Bootstrap SHALL be user-portable and render concrete launchd paths

The bootstrap engine SHALL derive user paths and the Homebrew prefix from the active environment. It SHALL render concrete absolute paths into LaunchAgent plists before registration. Portable manifests SHALL exclude secrets, private keys, signed-in state, and Docker volumes.

#### Scenario: Different username and home directory
- **WHEN** bootstrap runs under a different macOS username or home directory path
- **THEN** generated shell configuration and LaunchAgent plists SHALL target the active user's home directory without referencing `/Users/androidteam`

#### Scenario: launchd template variable rendering
- **WHEN** a LaunchAgent plist is rendered from its template
- **THEN** all registered variables (`{{HOME}}`, `{{HOMEBREW_PREFIX}}`, `{{WORKSPACE_ROOT}}`, `{{OPENSPEC_STORE_ROOT}}`) SHALL be replaced with concrete absolute paths
- **AND** verification SHALL confirm that no unexpanded placeholders or shell variables exist in the rendered plist

#### Scenario: Secret-bearing state exclusion
- **WHEN** a candidate file contains credentials, API keys, or signed-in session state (such as `.zshenv`)
- **THEN** bootstrap SHALL exclude the file from tracking and template generation, reporting the required manual secret injection step

#### Scenario: Repeat bootstrap is idempotent
- **WHEN** bootstrap runs repeatedly against an already configured workstation
- **THEN** no duplicate symlinks, duplicate PATH entries, or broken file states SHALL be created
- **AND** verification SHALL report that all existing configurations are already aligned

#### Scenario: Unsupported CPU architecture or missing prerequisite
- **WHEN** bootstrap executes on an unsupported CPU architecture or is missing required development prerequisites (such as Xcode Command Line Tools)
- **THEN** bootstrap SHALL fail closed with an informative diagnostic error and exit code non-zero without writing partial configurations

### Requirement: Verification SHALL fail closed on unsafe drift and service collisions

Workstation verification SHALL fail closed when an active executable lacks a declared owner, an update target differs from the active path, required prerequisites are missing, or mutually exclusive services claim the same development port. Verification SHALL generate structured audit evidence without performing destructive modifications.

#### Scenario: Update target mismatch
- **WHEN** a scheduled updater targets a different prefix than the active executable
- **THEN** verification SHALL classify the tool as misaligned and SHALL suppress that tool's automated mutation

#### Scenario: Port collision reported without killing or stopping services
- **WHEN** two installed services or background daemons claim the same development port (e.g. Ollama daemon and Docker runner on port 11434)
- **THEN** verification SHALL report the port collision and foreign PID in a quarantine report
- **AND** verification SHALL NOT terminate arbitrary processes, restart services, or reconfigure network bindings

#### Scenario: AgentMemory health verification via `/agentmemory/health` and package metadata
- **WHEN** AgentMemory health is evaluated
- **THEN** the probe SHALL request HTTP GET `/agentmemory/health` on port 3111
- **AND** the probe SHALL verify that installed package metadata aligns with the pinned `iii-engine` version
- **AND** the probe SHALL NOT evaluate health using root `/` which returns 404

#### Scenario: Incompatible AgentMemory engine or API process quarantined
- **WHEN** port 49134 has an incompatible engine or port 3111 is occupied by an unexpected API process
- **THEN** the verification engine SHALL record the offending PID, port, and version evidence in a quarantine audit
- **AND** the engine SHALL NOT execute an un-gated process kill or mutate the SQLite database

### Requirement: Package changes SHALL be staged with pre- and post-mutation native smoke checks

Toolchain maintenance workflows SHALL distinguish inspection, normalization, removal, upgrade, and rollback stages. Any upgrade or removal action SHALL require both pre-mutation and post-mutation native smoke checks.

#### Scenario: Upgrade candidate staging and native smoke check
- **WHEN** an installed package has an available upstream release
- **THEN** the workflow SHALL run the tool's pre-mutation native smoke check (`<tool> --version`, `<tool> help`, or MCP status)
- **AND** after applying the update, the workflow SHALL run the post-mutation native smoke check and record active version readback

#### Scenario: Command failure with exit zero detected
- **WHEN** an updater command exits with status code 0 but emits an error message or fails to change directory
- **THEN** the runner SHALL classify the update as FAILED rather than successful

#### Scenario: Already at target version (already_target)
- **WHEN** an updater runs and the tool was already at the target release version
- **THEN** the runner SHALL record the outcome as `already_target` provided the post-mutation smoke check passes
- **AND** the runner SHALL NOT treat unchanged version as a failure

#### Scenario: Duplicate removal authorized only after five-point check
- **WHEN** a duplicate or shadowed installation is proposed for removal
- **THEN** removal SHALL be blocked unless all five checks pass:
  1. Reference check confirms no script or wrapper depends on the target path
  2. Process check confirms no active process holds open handles to the binary
  3. Manifest reconciliation confirms the retained path is declared authoritative
  4. Dependency check confirms shared libraries and modules remain operational
  5. Explicit external gate authorization exists for the exact target path

#### Scenario: Partial or failed rollback detected (no false green)
- **WHEN** an upgrade fails post-mutation smoke checks and rollback is triggered
- **THEN** the workflow SHALL verify that the previous binary is fully restored and passes native smoke checks
- **AND** if rollback is partial or fails, the workflow SHALL report a hard BLOCKER rather than a clean rollback

### Requirement: Shell startup optimization SHALL be measured and maintain PATH precedence

Interactive shells (`~/.zshrc`) and scheduled maintenance runners (`workstation-daily-update.sh`) SHALL share the same documented PATH precedence policy. Shell startup optimizations SHALL be empirically measured using repeated cold and warm benchmarks, deferring expensive completions and runtimes while preserving immediate command availability.

#### Scenario: PATH consistency between interactive and scheduled runners
- **WHEN** a command is resolved from an interactive zsh shell and from `workstation-daily-update.sh`
- **THEN** both environments SHALL resolve the identical authoritative binary on PATH

#### Scenario: Safe startup measurement with repeated medians and variance
- **WHEN** shell startup performance is benchmarked
- **THEN** the harness SHALL measure repeated cold and warm execution times across N runs (at least 5 runs each)
- **AND** the report SHALL publish median times and variance rather than unverified fixed targets

#### Scenario: Lazy runtime initialization preserves command resolution
- **WHEN** NVM or versioned runtime loading is deferred
- **THEN** system Node SHALL remain immediately available from Homebrew
- **AND** any invocation requiring a versioned Node runtime SHALL trigger lazy initialization without breaking execution

### Requirement: Persistent development data and Docker volumes SHALL be protected

Routine workstation maintenance and cleanup workflows SHALL protect persistent named Docker volumes and local databases. Broad, un-gated system prunes SHALL be prohibited.

#### Scenario: Protected named Docker volume preserved during cleanup
- **WHEN** a routine disk hygiene or Docker cleanup command runs
- **THEN** named volumes declared in the protected inventory (including OmniRoute's `omniroute_data` and persistent database volumes) SHALL remain intact

#### Scenario: Generic broad prune prohibited
- **WHEN** automated or scheduled maintenance runs
- **THEN** generic broad prunes (`docker system prune -a --volumes -f`) SHALL NOT be executed
- **AND** cleanup SHALL be restricted to volume-preserving prune commands (`docker system prune` without `--volumes` or `--all`)

### Requirement: Knowledge synchronization SHALL be fail-closed, write-receipt gated, and idempotent

Knowledge synchronization via `sync-notion-knowledge.sh` SHALL publish sanitized, human-facing onboarding and architecture runbooks to Notion without disclosing local usernames, tokens, or credentials. State progression in `MANIFEST_FILE` SHALL strictly require confirmed write receipts from the Notion API.

#### Scenario: Idempotent knowledge sync yields fresh_noop
- **WHEN** sanitized source Markdown content matches the recorded document SHA-256 in `MANIFEST_FILE`
- **THEN** synchronization SHALL report `fresh_noop` without executing Notion API write requests

#### Scenario: Dynamic home redaction and residual secret scanning
- **WHEN** source documents contain local home directories or sensitive patterns
- **THEN** dynamic regex SHALL replace `/Users/[^/]+/` with `~/` or `~/Developer/`
- **AND** a residual secret scanner SHALL verify that no tokens matching credential patterns exist in the payload before transmission

#### Scenario: Write receipt required before manifest SHA update
- **WHEN** `ntn pages edit` or `ntn pages create` executes
- **THEN** `MANIFEST_FILE` SHALL ONLY be updated with the new SHA-256 hash when the command exits 0 and returns a valid JSON payload containing a page ID
- **AND** if the write command fails or returns non-zero, the previous SHA SHALL be retained

#### Scenario: Offline sync preserves unchanged manifest for retry
- **WHEN** network connectivity is unavailable during synchronization
- **THEN** synchronization SHALL fail closed without advancing document SHA-256 hashes
- **AND** the subsequent sync run SHALL automatically retry the pending documents

#### Scenario: Genuinely read-only dry run
- **WHEN** `sync-notion-knowledge.sh` runs with `--dry-run`
- **THEN** the script SHALL NOT touch log files, create missing manifest directories, or mutate section page IDs in `MANIFEST_FILE`
