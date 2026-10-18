# Tasks: Workstation Toolchain Path and Cargo Manifest Reconciliation

## 1. Subshell & Inventory PATH Normalization

- [x] 1.1 Update PATH normalization in `scripts/inventory-workstation-toolchain.py` (`_extra_paths` / PATH ordering) so `/opt/homebrew/bin` and `/opt/homebrew/sbin` deterministically precede `/usr/bin` and isolated agent runtime directories (`~/.hermes/node/bin`) even when invoked from non-login agent subshells, and prepare an operator-gated shell profile snippet for `~/.zshenv` / `~/.zshrc` (move-to-front `path=("/opt/homebrew/bin" "/opt/homebrew/sbin" ${path:#"/opt/homebrew/bin"})` ordered after lower-priority paths) respecting `portable-workstation-toolchain` external mutation boundaries.
- [x] 1.2 Verify `inventory-workstation-toolchain.py --json` resolves `git` to `/opt/homebrew/bin/git` and `node` to `/opt/homebrew/bin/node` under both interactive login shells and simulated non-login/Hermes subshell `PATH` (`PATH="$HOME/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin"`).

## 2. Optional `rust-dev` Profile Reconciliation

- [x] 2.1 Update `reconcile_with_manifest()` in `scripts/inventory-workstation-toolchain.py` and `plan_bootstrap()` in `scripts/bootstrap-workstation.py` so uninstalled tools belonging exclusively to the optional `rust-dev` capability profile (`profiles.rust-dev` / `config/rust-dev-profile.json`) are tracked as `optional_skipped` rather than `missing` (`missing_count: 0`) and skipped by default bootstrap planning unless the `rust-dev` profile is requested, while preserving strict `config/workstation-manifest.schema.json` compliance.
- [x] 2.2 Verify `python3 scripts/inventory-workstation-toolchain.py --json` reports `manifest_reconciliation.status == "aligned"` and `missing_count == 0` when `rust-dev` is not installed.

## 3. `cce` Standalone Authority Reconciliation

- [x] 3.1 Update the `if name == "cce":` branch in `scripts/inventory-workstation-toolchain.py:495-509` to consult `get_supported_updater("cce", "vendor_download")` from `toolchain_updater_registry.py` (matching `reconcile-agent-cli-coverage.py:159-160`) and classify `~/.local/bin/cce` as a declared pinned standalone binary (`authority="standalone"`, `writer="none"`, `updater_dispatch="none"`, `drift_status="clean"`, `evidence_gaps=[]`).
- [x] 3.2 Run `python3 scripts/inventory-workstation-toolchain.py --json` and verify `authority_reconciliation.unknown_count == 0` and `manifest_reconciliation.unknown_count == 0` (while preserving the `prime-agent` `target_misalignment` invariant enforced by `scripts/test-version-authority-governance.py:101-110`).

## 4. Comprehensive Governance & Schema Test Gates

- [x] 4.1 Run `uv run pytest tests/test_portable_workstation_slice_a.py tests/test_portable_workstation_slice_b.py tests/test_portable_workstation_slice_c.py scripts/test-version-authority-governance.py -v` (including schema validation of `config/workstation-toolchain-manifest.json` against `config/workstation-manifest.schema.json`).
- [x] 4.2 Verify all governance unit tests pass with zero regressions and preserve `skip_specs: true` in `proposal.md`.
