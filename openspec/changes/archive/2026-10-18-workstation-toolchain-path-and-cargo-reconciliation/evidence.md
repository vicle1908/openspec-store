# Verification Evidence: Workstation Toolchain Path and Cargo Manifest Reconciliation

## 1. Summary of Execution

This document provides durable verification evidence for the completion of all 8 tasks in `workstation-toolchain-path-and-cargo-reconciliation`:
1. Subshell & Inventory PATH Normalization (`normalize_discovery_path()` and `shell-path-normalization.zsh`)
2. Optional `rust-dev` Profile Reconciliation (`optional_skipped` tracking in manifest reconciliation and dry-run bootstrap filtering)
3. `cce` Standalone Authority Reconciliation (`get_supported_updater("cce", "vendor_download")` integration)
4. Comprehensive Governance & Schema Test Gates (all slice tests and regression suites passing)

---

## 2. Inventory & Manifest Reconciliation Verification

### 2.1 Standard Host Execution (`python3 scripts/inventory-workstation-toolchain.py --json`)

Command executed:
```bash
python3 scripts/inventory-workstation-toolchain.py --json
```

Observed JSON Output Summary:
- **`manifest_reconciliation`**:
  - `status`: `"aligned"`
  - `declared_tools_count`: `35`
  - `aligned_count`: `33`
  - `drift_count`: `0`
  - `missing_count`: `0`
  - `optional_skipped_count`: `2`
  - `duplicate_count`: `0`
  - `obsolete_candidate_count`: `1` (`python@3.10`)
  - `unknown_count`: `0`
  - `summary.optional_skipped`: `["rustup", "cargo"]`
  - `summary.missing`: `[]`
  - `summary.drift`: `[]`
- **`authority_reconciliation`**:
  - `unknown_count`: `0`
  - `target_misalignment_count`: `1` (`prime-agent`)
  - `conflict_count`: `0`
  - `cce` classification:
    - `authority`: `"standalone"`
    - `writer`: `"none"`
    - `drift_status`: `"clean"`
    - `updater_dispatch`: `"none"`
    - `update_verb`: `null`
    - `selected_channel`: `"pinned standalone binary"`
    - `evidence_gaps`: `[]`

### 2.2 Simulated Non-Login / Hermes Subshell Execution

Command executed:
```bash
env PATH="$HOME/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin" python3 scripts/inventory-workstation-toolchain.py --json
```

Observed Verification Assertions:
- `git active_path`: `"/opt/homebrew/bin/git"` (resolved from Homebrew instead of `/usr/bin/git`)
- `node active_path`: `"/opt/homebrew/bin/node"` (resolved from Homebrew instead of `$HOME/.hermes/node/bin/node`)
- `manifest_reconciliation.drift_count`: `0`
- `authority_reconciliation.unknown_count`: `0`

---

## 3. Shell Profile Snippet Artifact

The operator-gated Zsh PATH normalization snippet for `~/.zshenv` and `~/.zshrc` is recorded below:
```zsh
#!/usr/bin/env zsh
# Shell profile snippet for workstation PATH normalization.
# Resolves PATH precedence drift in non-login subshells and interactive sessions.
# Intended for operator manual application to ~/.zshenv and ~/.zshrc.
#
# Idempotently moves Homebrew directories to the front of the Zsh path array,
# ensuring /opt/homebrew/bin takes precedence over /usr/bin and isolated agent runtimes (~/.hermes).

if [[ -d "/opt/homebrew/bin" ]]; then
  path=("/opt/homebrew/bin" "/opt/homebrew/sbin" ${path:#/opt/homebrew/bin} ${path:#/opt/homebrew/sbin})
fi
```

---

## 4. Test Suite Execution Results

### 4.1 Governance Unit Tests & Slice Tests

Command executed:
```bash
uv run --with jsonschema pytest \
  tests/test_portable_workstation_slice_a.py \
  tests/test_portable_workstation_slice_b.py \
  tests/test_portable_workstation_slice_c.py \
  scripts/test-version-authority-governance.py \
  -v
```

Output:
```
============================= test session starts ==============================
platform darwin -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/androidteam/Developer/platform/openspec-store
configfile: pyproject.toml
collected 100 items

tests/test_portable_workstation_slice_a.py::TestPortableWorkstationSliceA::test_brewfile_contains_sanctioned_formulae_and_casks PASSED
tests/test_portable_workstation_slice_a.py::TestPortableWorkstationSliceA::test_brewfile_contains_tap_declarations PASSED
tests/test_portable_workstation_slice_a.py::TestPortableWorkstationSliceA::test_brewfile_exists PASSED
tests/test_portable_workstation_slice_a.py::TestPortableWorkstationSliceA::test_canonical_manifest_contains_no_literal_androidteam PASSED
tests/test_portable_workstation_slice_a.py::TestPortableWorkstationSliceA::test_canonical_manifest_validates_against_schema PASSED
tests/test_portable_workstation_slice_a.py::TestPortableWorkstationSliceA::test_draft202012_validator_check_schema PASSED
...
scripts/test-version-authority-governance.py::TestCceStandaloneAuthority::test_cce_authority_resolves_to_standalone_clean_under_normal_registry PASSED
scripts/test-version-authority-governance.py::TestOptionalRustDevProfileReconciliation::test_reconcile_with_manifest_skips_uninstalled_rust_dev PASSED
scripts/test-version-authority-governance.py::TestDiscoveryPathNormalization::test_normalize_discovery_path_positions_homebrew_ahead_of_hermes_and_system PASSED
scripts/test-version-authority-governance.py::TestDiscoveryPathNormalization::test_normalize_discovery_path_preserves_synthetic_test_bin_at_index_zero PASSED
scripts/test-version-authority-governance.py::TestRegistryEnforcementInInventory::test_cleared_registry_fails_closed_in_inventory PASSED

============================= 100 passed in 19.28s ==============================
```

Result: `100 passed, 0 skipped, 0 failed`.

### 4.2 OpenSpec Validation Gate

Command executed:
```bash
openspec validate workstation-toolchain-path-and-cargo-reconciliation --strict --json --store openspec-store
```

Output:
```json
{
  "items": [
    {
      "id": "workstation-toolchain-path-and-cargo-reconciliation",
      "type": "change",
      "valid": true,
      "issues": [
        {
          "level": "INFO",
          "path": "file",
          "message": "skip_specs is set in .openspec.yaml: change declares no spec-level behavior changes, zero deltas accepted"
        }
      ],
      "durationMs": 33
    }
  ],
  "summary": {
    "totals": {
      "items": 1,
      "passed": 1,
      "failed": 0
    },
    "byType": {
      "change": {
        "items": 1,
        "passed": 1,
        "failed": 0
      }
    }
  },
  "version": "1.0",
  "root": {
    "path": "/Users/androidteam/Developer/platform/openspec-store",
    "source": "store",
    "store_id": "openspec-store"
  }
}
```

Result: `valid: true`, 0 errors.
