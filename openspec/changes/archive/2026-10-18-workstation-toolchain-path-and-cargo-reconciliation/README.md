# workstation-toolchain-path-and-cargo-reconciliation

Reconcile workstation PATH precedence, rustup/cargo manifests, and unmanaged cce binary

## Summary

This change reconciles four critical workstation toolchain governance findings identified during deep runtime audits:

1. **Subshell & Inventory PATH Normalization (`scripts/inventory-workstation-toolchain.py`, `~/.zshenv`, `~/.zshrc`)**:
   Ensures `/opt/homebrew/bin` and `/opt/homebrew/sbin` deterministically take precedence over `/usr/bin` (Apple Xcode CLT) and isolated agent runtimes (`~/.hermes/node/bin`) across interactive shells, non-login subshells (`zsh -c`, Python subprocesses), and inventory PATH discovery. Prepares an operator-gated shell profile snippet adhering to `portable-workstation-toolchain` boundaries.

2. **Optional `rust-dev` Profile Reconciliation (`scripts/inventory-workstation-toolchain.py`, `scripts/bootstrap-workstation.py`, `config/workstation-toolchain-manifest.json`)**:
   Aligns inventory reconciliation and bootstrap planning with optional capability profiles (`profiles.rust-dev` in `config/workstation-toolchain-manifest.json:64-67` and `config/rust-dev-profile.json`). Tracks uninstalled optional Rust tools as `optional_skipped` instead of `missing` (`missing_count: 0`) and excludes them from default bootstrap sync actions while maintaining strict compliance with `config/workstation-manifest.schema.json` (`additionalProperties: false`).

3. **`cce` Standalone Authority Reconciliation (`scripts/inventory-workstation-toolchain.py:495-509`)**:
   Resolves the `authority_reconciliation.unknown_count: 1` warning by updating `inventory-workstation-toolchain.py` to consult `get_supported_updater("cce", "vendor_download")` from `toolchain_updater_registry.py` (matching `reconcile-agent-cli-coverage.py:159-160`). Confirms `/Users/androidteam/.local/bin/cce` (`cce 0.2.7`, arm64 Rust binary wired to `~/.zshrc` and `~/.cce/config.toml`) as a declared pinned standalone binary (`authority="standalone"`, `writer="none"`, `updater_dispatch="none"`, `drift_status="clean"`), preserving `prime-agent` target misalignment invariants.

4. **Comprehensive Governance & Schema Test Gates**:
   Executes full regression test suites across portable workstation slices A, B, C, version authority governance, and schema validation.
