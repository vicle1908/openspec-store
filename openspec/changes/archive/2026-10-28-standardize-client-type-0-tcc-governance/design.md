# Design: Standardize client_type=0 Bundle Attribution for Workstation TCC Permissions

## Context

On macOS Darwin, the Transparency, Consent, and Control daemon (`tccd`) manages user privacy permissions in `/Library/Application Support/com.apple.TCC/TCC.db`. The `access` table keys entries by `(service, client, client_type, indirect_object_identifier)`:
- `client_type = 0` (Bundle Identifier): Evaluated via CoreFoundation `CFBundleCreate` / `CFBundleGetIdentifier`. Permissions are permanently bound to the `CFBundleIdentifier` and its stored `csreq` code-signing requirement. Versioned directory changes (such as `Python.app` moving from `python@3.15/3.15.0` to `3.15.1` to `3.15.2`) do not invalidate the grant, provided the bundle retains its identity and valid code signature.
- `client_type = 1` (Absolute File Path): Evaluated via `proc_pidpath`. Permissions are bound to the exact canonical filesystem path. When Homebrew formulae (`omp`, `node`, `python3.15`) or vendor self-updaters (`claude`) rotate version directories (`Cellar/<pkg>/<version>/bin/<bin>`, `versions/<version>`), the old path is abandoned and the new binary loses all permissions.

Disassembly of `tccd` (`-[TCCDAccessIdentity initWithAttributionChain:]`) establishes that child processes spawned by a responsible supervisor application bundle (`NSURLIsApplicationKey = YES`) inherit the supervisor bundle's `client_type = 0` authorization.

## Goals / Non-Goals

**Goals:**
- Standardize all autonomous workstation agent execution and scheduled maintenance runners on `client_type = 0` bundle attribution.
- Update `scripts/tcc_provenance.py` to prioritize and verify `client_type = 0` bundle records (`org.python.python`, `com.stablyai.orca`, `com.trycua.driver`, etc.) with strict `csreq` code-signing validation.
- Automate post-upgrade code signing with `Developer Agent Code Signing` in both daily maintenance runners (`workstation-daily-update.sh` and `shb-schedule`), ensuring bundles maintain valid `csreq` matching across all package upgrades.
- Permanently eliminate daily upgrade `DRIFT` warnings caused by ephemeral `client_type = 1` Cellar path rotation.

**Non-Goals:**
- Modifying macOS System Integrity Protection (SIP) or attempting direct SQLite writes to `TCC.db`.
- Injecting synthetic events into `SecurityAgent` authorization dialogs.
- Classifying Darwin TCC verification errors as `SKIPPED`.

## Decisions

### 1. Primary Authorization via `client_type = 0` Bundle Identifiers
- **Rationale**: Application bundles provide permanent, version-agnostic identity on macOS. As demonstrated by `org.python.python`, `com.stablyai.orca`, and `com.trycua.driver`, grants in `TCC.db` remain valid across endless package upgrades without requiring user re-approval in System Settings.
- **Alternatives Considered**:
  - *Keep `client_type = 1` and re-enroll daily*: Rejected. SIP blocks automated SQL writes, requiring manual operator clicks in `System Settings > Privacy & Security` after every minor upgrade.
  - *Hardcode static symlink targets in Cellar*: Rejected. Violates Homebrew packaging and causes broken links on brew updates.

### 2. Supervisor Delegation for Subprocess CLIs
- **Rationale**: In macOS `tccd`, subprocesses inherit TCC permissions from their responsible parent application bundle. By running automated tasks under `Python.app` (`org.python.python`) or `Orca.app` (`com.stablyai.orca`), child processes (`omp`, `node`, `claude`, `kimi`, `goose`) inherit Accessibility, Screen Recording, and Full Disk Access seamlessly.
- **Alternatives Considered**:
  - *Wrap every single CLI in a dedicated `.app` bundle*: Excess overhead for 20+ standalone CLI utilities; supervisor delegation achieves the exact same attribution with zero filesystem clutter.

### 3. TCC Provenance Verifier Alignment (`scripts/tcc_provenance.py`)
- **Rationale**: `tcc_provenance.py` must verify that the workstation's authoritative bundle identities (`org.python.python`, `com.stablyai.orca`, `com.trycua.driver`) hold active `auth_value = 2` grants and valid `csreq` signatures, while treating ephemeral `client_type = 1` Cellar paths as secondary legacy fallbacks rather than failing closed on expected package upgrades.
- **Alternatives Considered**:
  - *Remove `tcc_provenance.py`*: Rejected. Governance requires auditable proof of system permissions and code-signing validity.

## Risks / Trade-offs

- **[Risk]** Homebrew overwriting `Python.app` bundle metadata during formula updates.
  → **Mitigation**: Maintenance runners (`workstation_update.py` and `workstation-daily-update.sh`) execute post-upgrade re-signing (`sign_agent_binaries`) immediately after Homebrew operations, ensuring `Developer Agent Code Signing` and `org.python.python` Info.plist invariants are restored before verification runs.
- **[Risk]** Direct shell execution by operator outside of supervisor bundles.
  → **Mitigation**: Interactive terminal emulators (`Warp`, `iTerm2`, `Terminal.app`) and IDEs (`Orca`, `VSCode`, `Cursor`) already hold `client_type = 0` grants in `TCC.db`, passing authorization down to interactive subshells.
