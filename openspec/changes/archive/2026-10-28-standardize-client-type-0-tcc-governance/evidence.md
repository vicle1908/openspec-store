# Verification Evidence: `standardize-client-type-0-tcc-governance`

- **Date**: `2026-10-28`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Change**: `standardize-client-type-0-tcc-governance`
- **Discipline**: Strictly value-blind (SHA-256 digests, permissions, exit codes, and structural metadata only; zero secrets or raw tokens).

---

## 1. TCC Provenance Verifier Alignment (Tasks 1.1–1.2)

- **Target File**: `/Users/androidteam/Developer/platform/openspec-store/scripts/tcc_provenance.py`
- **Bundle Governance Standard (`client_type = 0`)**:
  - Implemented `CANONICAL_TCC_BUNDLES` defining 8 authoritative workstation bundle identities:
    - `org.python.python` (`Python.app`): `Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`
    - `com.stablyai.orca` (`/Applications/Orca.app`): `Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`
    - `com.trycua.driver` (`/Applications/CuaDriver.app`): `Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`
    - `com.electron.goose` (`/Applications/Goose.app`): `Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`
    - `ai.opencode.desktop` (`/Applications/OpenCode.app`): `Accessibility`, `SystemPolicyAllFiles`
    - `com.openai.codex` (`/Applications/ChatGPT.app`): `Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`
    - `com.nousresearch.hermes` (`/Applications/Hermes.app`): `Accessibility`, `ScreenCapture`, `SystemPolicyAllFiles`
    - `org.p0deje.Maccy` (`/Applications/Maccy.app`): `Accessibility`, `PostEvent`
- **Verification (`python3 scripts/tcc_provenance.py --bundles --json`)**:
  - `status`: `"CLEAN"`
  - `verified_binaries`: `8/8` bundle identities verified
  - `missing_binaries`: `0`
  - `errors`: `[]`

---

## 2. Maintenance Runners Post-Upgrade Code Signing & Parity (Tasks 2.1–2.2)

- **Target Files**:
  - `platform/openspec-store/scripts/workstation-daily-update.sh`
  - `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`
  - `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`
- **Runner Parity & Synchronization**:
  - Updated Stage 7 in `workstation-daily-update.sh` to invoke `verify_tcc_provenance --bundles`.
  - Updated `workstation_update.py:verify_tcc_provenance` with `bundles` support and configured `step_integrity_and_store_validation()` to call `verify_tcc_provenance(bundles=True)`.
  - Synchronized `platform/openspec-store/scripts/workstation-daily-update.sh` to `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (`cp then chmod 755`).
  - `diff -u` verified: 0 diff.

---

## 3. Script Provenance and Snapshot Growth Hygiene (Tasks 3.1–3.2)

- **Target Files**:
  - `/Users/androidteam/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh`
  - `platform/openspec-store/scripts/knowledge-refresh/refresh-knowledge-indexes.sh`
  - `platform/openspec-store/config/script-provenance-manifest.tsv`
- **Verification**:
  - Synchronized executed copy to store mirror (`cp then chmod +x`).
  - Live SHA-256 matching: `65afe5d0aaf5ec906f5b614e4d5d502cb7312177b2a8b85413c63ecf4255cc62` across both paths.
  - Snapshot repository (`~/.agentmemory/snapshots`): `158.96 MiB` (`WITHIN_BOUNDS` vs 1.0 GiB ceiling).

---

## 4. OpenSpec Strict Validation and Live Execution (Tasks 4.1–4.2)

- **Strict OpenSpec Validation**:
  - `openspec validate standardize-client-type-0-tcc-governance --strict --json --store openspec-store` → `passed: 1`, `failed: 0` (Exit Code: `0`).
- **Test Suite Verification**:
  - `python3 scripts/test-version-authority-governance.py` → `Ran 37 tests in 5.256s - OK` (Exit Code: `0`).
  - `uv run --project shb/shb-schedule pytest tests/test_workstation_update_workflow.py` → `42 passed in 48.48s` (Exit Code: `0`).
- **Live Pipeline Verification**:
  - `bash /Users/androidteam/Developer/scripts/workstation-daily-update.sh --check` → `2026-10-28 09:32:41 +07 — Complete [MODE=check]` (Exit Code: `0`).
  - Verified 9 executed scripts match recorded mirrors without drift (`checked=9 drifted=0 missing_record=0`).
  - Verified all 8 canonical `client_type = 0` bundle identities passed with valid native `csreq` signatures.
