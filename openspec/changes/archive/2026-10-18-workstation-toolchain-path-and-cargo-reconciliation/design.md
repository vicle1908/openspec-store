# Design: Workstation Toolchain Path and Cargo Manifest Reconciliation

## Context

The workstation toolchain governance framework (`config/workstation-toolchain-manifest.json`, `scripts/inventory-workstation-toolchain.py`, `scripts/toolchain_updater_registry.py`, and `scripts/bootstrap-workstation.py`) defines canonical executable locations, owning package managers (`brew`, `npm-global`, `uv`, `cargo`), update dispatch classifications, and drift detection rules across macOS developer workstations.

Recent deep runtime and codebase audits identified three specific failure modes causing divergence between actual system state, inventory reports, and governance assertions:

1. **PATH Resolution Divergence in Subshells and Inventory Scripts:**
   `_path_prepend` in `~/.zshrc:121-126` is implemented as an idempotency skip-if-present guard (`*":$1:"*) ;;`), not a move-to-front operation. If `/opt/homebrew/bin` appears anywhere in an inherited `PATH` (even after `/usr/bin` or isolated agent runtimes like `~/.hermes/node/bin`), `_path_prepend "/opt/homebrew/bin"` is a no-op. Furthermore, non-login and non-interactive subshells (`zsh -c`, Python `subprocess.run`) source only `~/.zshenv:1-44`, bypassing `~/.zprofile` and `~/.zshrc` entirely, where `/opt/homebrew/bin` is absent. Additionally, `scripts/inventory-workstation-toolchain.py:28-36` prepends `_extra_paths` to `os.environ["PATH"]` and invokes `shutil.which` without ensuring `/opt/homebrew/bin` and `/opt/homebrew/sbin` precede `/usr/bin` or isolated runtimes.

2. **Uninstalled Optional Profile Tools Counted as Missing Drift:**
   `rustup` and `cargo` are already cataloged under optional capability profile `profiles.rust-dev` in `config/workstation-toolchain-manifest.json:64-67` and `config/rust-dev-profile.json`. The schema `config/workstation-manifest.schema.json:71-143` strictly enforces `"additionalProperties": false` on both tool entries and the root document, preventing ad-hoc tool-level flags. While `scripts/inventory-workstation-toolchain.py:1471-1473` and `scripts/smoke-test-toolchain.py:118-132` correctly exclude `rust-dev` from marking overall status as drift, `reconcile_with_manifest()` (`inventory-workstation-toolchain.py:1392-1399`) unconditionally places uninstalled `rust-dev` tools into `missing` (`missing_count: 2`). Concurrently, `scripts/bootstrap-workstation.py:198-225` iterates over all declared tools and schedules mandatory `toolchain_sync` actions and smoke verifications for `rustup` and `cargo` even when the `rust-dev` capability profile is unselected.

3. **Hardcoded Standalone Binary Authority Blind Spot for `cce`:**
   `/Users/androidteam/.local/bin/cce` (`cce 0.2.7`, arm64 Rust Mach-O binary) is actively wired into `~/.zshrc:172-225` (`__cce_lazy_init`, `cce()`, `claude()`) and `~/.cce/config.toml` per `portable-workstation-toolchain/spec.md:273-282` and must NOT be removed. `cce` is already registered in `config/workstation-toolchain-manifest.json:43,384-396` (`authoritative_owner: "standalone"`, `update_authority: "none"`), `scripts/toolchain_updater_registry.py:259-267` (`status="uncovered_declared"`, `updater_dispatch="none"`), and `scripts/reconcile-agent-cli-coverage.py:159-160`. However, `scripts/inventory-workstation-toolchain.py:495-509` (`evaluate_authority_and_drift()`) executes a hardcoded branch `if name == "cce":` that sets `authority = "unknown"`, `drift_status = "unknown"`, bypassing `toolchain_updater_registry.py` and producing `authority_reconciliation.unknown_count: 1`.

## Decisions

### D1: Subshell & Inventory PATH Normalization

1. **Inventory PATH Re-ordering (`scripts/inventory-workstation-toolchain.py`)**:
   Update the startup PATH initialization in `scripts/inventory-workstation-toolchain.py` (around lines 28-36) so that `/opt/homebrew/bin` and `/opt/homebrew/sbin` are deterministically prepended or repositioned ahead of `/usr/bin`, `/bin`, and isolated agent runtimes (`~/.hermes/node/bin`). When `shutil.which(name)` executes during tool discovery, Homebrew binaries (e.g. `git`, `node`) will consistently resolve ahead of system CLT stubs or agent-bundled runtimes, even if invoked from non-login agent subshells.

2. **Operator-Gated Shell Profile Snippet (`~/.zshenv` / `~/.zshrc`)**:
   Prepare an operator-gated shell configuration snippet that respects `portable-workstation-toolchain` external file mutation boundaries. The snippet utilizes Zsh array manipulation to move Homebrew paths to the front of `path`:
   ```zsh
   # Move Homebrew directories to front of path array idempotently
   path=("/opt/homebrew/bin" "/opt/homebrew/sbin" ${path:#/opt/homebrew/bin} ${path:#/opt/homebrew/sbin})
   ```
   This snippet avoids the skip-if-present flaw of `*":$1:"*) ;;` while preserving lower-priority isolated toolchain paths.

3. **Verification Contract**:
   Verify `inventory-workstation-toolchain.py --json` resolves `git` to `/opt/homebrew/bin/git` and `node` to `/opt/homebrew/bin/node` under both normal interactive shells and synthetic non-login subshells where `PATH="$HOME/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin"`.

### D2: Optional Capability Profile Reconciliation (`rust-dev`)

1. **Schema-Compliant Profile Partitioning**:
   `rustup` and `cargo` remain declared under `profiles.rust-dev` in `config/workstation-toolchain-manifest.json:64-67` and `config/rust-dev-profile.json`. To maintain strict compliance with `config/workstation-manifest.schema.json` (`additionalProperties: false`), no unvalidated fields (e.g. `optional: true`) will be injected into tool definitions in the manifest.

2. **Inventory Manifest Reconciliation (`scripts/inventory-workstation-toolchain.py`)**:
   Update `reconcile_with_manifest()` in `scripts/inventory-workstation-toolchain.py` (around lines 1392-1399 and 1471-1473):
   - Determine the active set of optional profile tools (e.g. tools in `manifest_data.get("profiles", {}).get("rust-dev", [])` that do not belong to mandatory profiles like `core` or `base`).
   - If an optional profile tool is not installed on the filesystem, record it as `optional_skipped` rather than `missing`.
   - Report `missing_count: 0` when all mandatory tools are present, ensuring `missing` only contains genuinely missing required tools.

3. **Bootstrap Plan Filtering (`scripts/bootstrap-workstation.py`)**:
   Update `plan_bootstrap()` in `scripts/bootstrap-workstation.py` (around lines 198-225):
   - Check tool capability profile membership before generating `toolchain_sync` actions or adding `verification_smoke_command` entries.
   - If a tool belongs exclusively to `rust-dev` (or another unrequested optional capability profile), skip generating unconditional bootstrap actions and smoke tests unless the operator explicitly passes `--profile rust-dev`.

### D3: Standalone `cce` Authority Reconciliation

1. **Preserve Host Binary and Shell Integration**:
   Keep `/Users/androidteam/.local/bin/cce` (`cce 0.2.7`) in place and preserve its integration in `~/.zshrc:172-225` and `~/.cce/config.toml` per `portable-workstation-toolchain/spec.md:273-282`.

2. **Align Authority Evaluation in Inventory (`scripts/inventory-workstation-toolchain.py:495-509`)**:
   Replace the hardcoded `authority = "unknown"` assignment in `evaluate_authority_and_drift()` with registry lookup:
   - Call `decl = get_supported_updater("cce", "vendor_download")` from `toolchain_updater_registry.py` (matching `reconcile-agent-cli-coverage.py:159-160`).
   - When `decl` is found with `status="uncovered_declared"`, classify `~/.local/bin/cce` as:
     * `authority = "standalone"`
     * `writer = "none"`
     * `updater_dispatch = "none"`
     * `drift_status = "clean"`
     * `evidence_gaps = []`
     * `consequence = None`
   - This resolves the false positive warning and drives `authority_reconciliation.unknown_count` to `0`.

3. **Preserve Target Misalignment Invariants**:
   Ensure the reconciliation logic strictly preserves existing authority invariants for other tools, specifically the `prime-agent` `target_misalignment` invariant tested by `scripts/test-version-authority-governance.py:101-110`.

### D4: Comprehensive Governance & Schema Test Gates

1. **Automated Test Matrix**:
   All changes must pass the full suite of portable workstation and governance test gates:
   ```bash
   uv run pytest \
     tests/test_portable_workstation_slice_a.py \
     tests/test_portable_workstation_slice_b.py \
     tests/test_portable_workstation_slice_c.py \
     scripts/test-version-authority-governance.py \
     -v
   ```

2. **Schema & JSON Consistency Gates**:
   - Validate `config/workstation-toolchain-manifest.json` against `config/workstation-manifest.schema.json` using `jsonschema`.
   - Execute `python3 scripts/inventory-workstation-toolchain.py --json` and assert:
     * `manifest_reconciliation.status == "aligned"`
     * `manifest_reconciliation.missing_count == 0`
     * `manifest_reconciliation.unknown_count == 0`
     * `authority_reconciliation.unknown_count == 0`

3. **Governance Contract Integrity**:
   Preserve `skip_specs: true` in `proposal.md` and `.openspec.yaml`. No new specification deltas or spec modifications are created.
