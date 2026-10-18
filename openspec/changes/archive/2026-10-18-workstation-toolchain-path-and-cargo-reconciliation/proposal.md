# Proposal: Workstation Toolchain Path and Cargo Manifest Reconciliation

## Why

Recent deep runtime audits of workstation toolchain governance revealed three specific root causes for observed drift:

1. **Subshell & Inventory PATH Precedence Drift:**
   - In `~/.zshrc:121-126`, the helper `_path_prepend` operates as a skip-if-present guard (`*":$1:"*) ;;`) rather than a move-to-front operation. If `/opt/homebrew/bin` already appears after system paths (such as Apple Xcode CLT `/usr/bin`) or isolated agent runtimes (`~/.hermes/node/bin`) in an inherited `PATH`, `_path_prepend "/opt/homebrew/bin"` at line 139 is a no-op.
   - Non-login, non-interactive subshells (`zsh -c`, Python `subprocess.run`) source only `~/.zshenv:1-44`, bypassing both `~/.zprofile` and `~/.zshrc`. Because `~/.zshenv` does not inject `/opt/homebrew/bin`, subshells fall back to `/usr/bin/git` instead of Homebrew's `/opt/homebrew/bin/git`.
   - In `scripts/inventory-workstation-toolchain.py:28-36`, `_extra_paths` (`~/.qoder/entry`, `~/.kimi-code/bin`, `/opt/homebrew/opt/libpq/bin`) are prepended to `os.environ["PATH"]` before calling `shutil.which(name)` directly, without ensuring `/opt/homebrew/bin` and `/opt/homebrew/sbin` precede `/usr/bin` or isolated agent runtime paths (`~/.hermes/node/bin`).

2. **Optional `rust-dev` Profile Manifest & Inventory Reconciliation:**
   - `rustup` and `cargo` are declared in `config/workstation-toolchain-manifest.json:64-67` under the optional capability profile `profiles.rust-dev` and configured via `config/rust-dev-profile.json`.
   - The manifest schema (`config/workstation-manifest.schema.json:71-143`) sets `"additionalProperties": false` on both tool entries and root, strictly forbidding ad-hoc unvalidated keys on tool entries.
   - While `scripts/inventory-workstation-toolchain.py:1471-1473` and `scripts/smoke-test-toolchain.py:118-132` exclude `rust-dev` from triggering mandatory failure status (`manifest_reconciliation.status == "aligned"`), `reconcile_with_manifest()` in `scripts/inventory-workstation-toolchain.py:1392-1399` still appends uninstalled `rust-dev` tools to `missing` (`missing_count: 2`). Furthermore, `scripts/bootstrap-workstation.py:198-225` generates unconditional `toolchain_sync` actions and smoke checks for `rustup`/`cargo`.

3. **Declared Standalone `cce` Binary Authority Evaluation:**
   - `/Users/androidteam/.local/bin/cce` (`cce 0.2.7`, arm64 Rust Mach-O binary) is actively wired into `~/.zshrc:172-225` (`__cce_lazy_init`, `cce()`, `claude()`) and `~/.cce/config.toml` per `portable-workstation-toolchain/spec.md:273-282` and must NOT be removed.
   - `cce` is already cataloged in `config/workstation-toolchain-manifest.json:43,384-396` (`authoritative_owner: "standalone"`, `update_authority: "none"`), `scripts/toolchain_updater_registry.py:259-267` (`status="uncovered_declared"`, `updater_dispatch="none"`), and `scripts/reconcile-agent-cli-coverage.py:159-160`.
   - The warning `authority_reconciliation.unknown_count: 1` reported by `inventory-workstation-toolchain.py --json` originates from a hardcoded `if name == "cce":` branch in `scripts/inventory-workstation-toolchain.py:495-509` (`evaluate_authority_and_drift()`), which hardcodes `authority = "unknown"` without consulting `toolchain_updater_registry.py` or the manifest.

## What Changes

1. **Subshell & Inventory PATH Normalization (`scripts/inventory-workstation-toolchain.py`, `~/.zshenv`, `~/.zshrc`)**:
   - Update PATH normalization in `scripts/inventory-workstation-toolchain.py` (`_extra_paths` / PATH ordering) so `/opt/homebrew/bin` and `/opt/homebrew/sbin` deterministically precede `/usr/bin` and isolated agent runtime directories (`~/.hermes/node/bin`) even when invoked from non-login agent subshells.
   - Prepare an operator-gated shell profile snippet for `~/.zshenv` / `~/.zshrc` (move-to-front `path=("/opt/homebrew/bin" "/opt/homebrew/sbin" ${path:#"/opt/homebrew/bin"})` ordered after lower-priority paths) respecting `portable-workstation-toolchain` external mutation boundaries.
   - Verify that `inventory-workstation-toolchain.py --json` resolves `git` to `/opt/homebrew/bin/git` and `node` to `/opt/homebrew/bin/node` under both interactive login shells and simulated non-login/Hermes subshell environments (`PATH="$HOME/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin"`).

2. **Optional `rust-dev` Profile Reconciliation (`scripts/inventory-workstation-toolchain.py`, `scripts/bootstrap-workstation.py`, `config/workstation-toolchain-manifest.json`)**:
   - Update `reconcile_with_manifest()` in `scripts/inventory-workstation-toolchain.py` and `plan_bootstrap()` in `scripts/bootstrap-workstation.py` so uninstalled tools belonging exclusively to the optional `rust-dev` capability profile (`profiles.rust-dev` / `config/rust-dev-profile.json`) are tracked as `optional_skipped` rather than `missing` (`missing_count: 0`) and skipped by default bootstrap planning unless the `rust-dev` profile is requested, while preserving strict `config/workstation-manifest.schema.json` compliance.
   - Verify `python3 scripts/inventory-workstation-toolchain.py --json` reports `manifest_reconciliation.status == "aligned"` and `missing_count == 0` when `rust-dev` is not installed.

3. **`cce` Standalone Authority Reconciliation (`scripts/inventory-workstation-toolchain.py:495-509`)**:
   - Update the `if name == "cce":` branch in `scripts/inventory-workstation-toolchain.py:495-509` to consult `get_supported_updater("cce", "vendor_download")` from `toolchain_updater_registry.py` (matching `reconcile-agent-cli-coverage.py:159-160`) and classify `~/.local/bin/cce` as a declared pinned standalone binary (`authority="standalone"`, `writer="none"`, `updater_dispatch="none"`, `drift_status="clean"`, `evidence_gaps=[]`).
   - Run `python3 scripts/inventory-workstation-toolchain.py --json` and verify `authority_reconciliation.unknown_count == 0` and `manifest_reconciliation.unknown_count == 0` (while preserving the `prime-agent` `target_misalignment` invariant enforced by `scripts/test-version-authority-governance.py:101-110`).

4. **Comprehensive Governance & Schema Test Gates**:
   - Run full portable workstation and authority regression suites: `uv run pytest tests/test_portable_workstation_slice_a.py tests/test_portable_workstation_slice_b.py tests/test_portable_workstation_slice_c.py scripts/test-version-authority-governance.py -v` (including schema validation of `config/workstation-toolchain-manifest.json` against `config/workstation-manifest.schema.json`).
   - Verify all governance unit tests pass with zero regressions and preserve `skip_specs: true` in `proposal.md`.

## Capabilities / Scope

- Repository: `~/Developer/platform/openspec-store` and external shell profile configuration snippets (`~/.zshenv`, `~/.zshrc`)
- Spec impact: None (`skip_specs: true`).
