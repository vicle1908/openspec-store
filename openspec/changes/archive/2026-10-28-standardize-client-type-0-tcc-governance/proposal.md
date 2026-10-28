# Proposal: Standardize client_type=0 Bundle Attribution for Workstation TCC Permissions

## Why

Automated daily toolchain upgrades (`brew upgrade`, `claude update`) cause recurring macOS Transparency, Consent, and Control (TCC) permissions drift because bare Mach-O CLI binaries (`omp`, `node`, `claude`, `python3.15`) are registered as `client_type = 1` (ephemeral canonical filesystem realpaths). Whenever Homebrew or vendor updaters rotate versioned directories (`Cellar/<pkg>/<ver>/bin/<bin>`, `versions/<ver>`), old `TCC.db` rows become stale and the active binaries lose their Accessibility, Screen Recording, and Full Disk Access grants. Standardizing workstation agent tooling on `client_type = 0` (bundle-keyed attribution backed by stable `CFBundleIdentifier` metadata and local code signing) permanently prevents upgrade drift while satisfying macOS System Integrity Protection (SIP) boundaries.

## What Changes

1. **Standardize Workstation Agent Execution on `client_type = 0` Bundle Attribution**:
   - Establish `client_type = 0` (`CFBundleIdentifier`) as the authoritative target model for all TCC-governed agent capabilities (Accessibility, Screen Recording, Full Disk Access).
   - Standardize CLI execution under responsible supervisor bundles (`Python.app` `org.python.python`, `Orca.app` `com.stablyai.orca`, `CuaDriver.app` `com.trycua.driver`) where child processes inherit persistent bundle grants via `tccd` attribution chains.
   - For standalone agent executables, transition to bundle-wrapped structures (`.app/Contents/MacOS/`) or stable bundle proxies signed with `Developer Agent Code Signing` (`H"65340d85afd298131c682d8463087891292a2b59"`).

2. **Modernize TCC Provenance Verification (`scripts/tcc_provenance.py`)**:
   - Update `tcc_provenance.py` target evaluation to recognize and prioritize `client_type = 0` bundle identities (`org.python.python`, `com.stablyai.orca`, `com.trycua.driver`, `com.block.goose`, `com.anthropic.claude`, etc.).
   - Distinguish between bundle-attributed execution (immune to version directory rotation) and legacy unmanaged `client_type = 1` realpath probing.
   - Enforce automatic re-signing of bundle targets during daily maintenance so new versions seamlessly inherit existing `client_type = 0` grants.

3. **Reconcile Governance Specifications**:
   - Update `openspec/specs/workstation-remote-and-agent-permissions/spec.md` to require `client_type = 0` bundle attribution as the primary standard for all autonomous agents and developer toolchains.
   - Update `openspec/specs/portable-workstation-toolchain/spec.md` to codify post-upgrade bundle signing and eliminate expectations of fragile versioned Cellar path registrations in `TCC.db`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workstation-remote-and-agent-permissions`: Standardize on `client_type = 0` bundle identifiers (`CFBundleIdentifier`) for all agent automation and remote control permissions, deprecating ephemeral `client_type = 1` versioned realpaths as the primary authorization mechanism.
- `portable-workstation-toolchain`: Codify `client_type = 0` bundle-supervised execution and automatic post-upgrade code signing in workstation daily maintenance pipelines.

## Non-Goals

- Bypassing macOS System Integrity Protection (SIP) to write directly into `/Library/Application Support/com.apple.TCC/TCC.db` via SQLite.
- Injecting synthetic events into `SecurityAgent` authorization dialogs.
- Downgrading or disabling macOS security enforcement.

## Impact

- **Central OpenSpec Store (`platform/openspec-store`)**:
  - `openspec/specs/workstation-remote-and-agent-permissions/spec.md`
  - `openspec/specs/portable-workstation-toolchain/spec.md`
  - `scripts/tcc_provenance.py`
  - `scripts/workstation-daily-update.sh`
- **SHB Scheduler (`shb/shb-schedule`)**:
  - `src/shb_schedule/workflows/workstation_update.py`
- **Host Workstation Environment**:
  - Eliminates daily TCC drift failures (`PARTIAL` status in `data/updates/YYYY-MM-DD.json`).
