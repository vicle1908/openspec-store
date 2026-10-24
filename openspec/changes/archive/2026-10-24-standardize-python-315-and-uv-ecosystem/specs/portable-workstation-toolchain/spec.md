# Spec Delta: portable-workstation-toolchain

## MODIFIED Requirements

### Requirement: Standardized uv Python runtime management and pyproject.toml lockfile hygiene
The workstation maintenance pipeline and Python repositories SHALL standardize on `uv`-managed Python (`>=3.15` without `<` upper bounds), automated `uv python upgrade` and `uv tool upgrade` execution, and fresh `uv.lock` files across all workspace projects while keeping `scripts/tcc_provenance.py` strictly read-only.

#### Scenario: Automated uv managed Python upgrade and legacy Python removal
- **WHEN** `workstation_update.py` (`step_uv_tools_update`) or `workstation-daily-update.sh` (Stage 4) executes
- **THEN** both runners SHALL execute `uv python upgrade` alongside `uv tool upgrade` (`--all` in bash, dynamic discovery in `shb-schedule`) while keeping `scripts/tcc_provenance.py` strictly read-only
- **AND** all installed `uv` tools (`browser-use`, `graphifyy`, `infinity-emb`, `tavily-cli`) SHALL resolve their virtualenv interpreter to `uv`-managed Python `3.15` (`~/.local/share/uv/python/cpython-3.15.*-macos-aarch64-none`)
- **AND** zero-dependent legacy Python installations (`uv` `3.11`/`3.12`/`3.14`, `~/.local/bin/python3.11`, and Homebrew `python@3.10`, `python@3.11`, `python@3.12`) SHALL be absent so `inventory-workstation-toolchain.py` reports `obsolete_candidate_count == 0`.

#### Scenario: Workspace pyproject.toml clean-break requires-python and lockfile freshness
- **WHEN** `uv lock --check` is evaluated across `platform/openspec-store`, `shb/shb-schedule`, `tdt/tdt-core`, `ai-tooling/workspace-python-template`, and `ai-tooling/wiki-mcp-server` and `uv run pytest` is evaluated across `platform/openspec-store`, `shb/shb-schedule`, and `tdt/tdt-core`
- **THEN** each `pyproject.toml` SHALL declare `requires-python = ">=3.15"` without `<` upper bounds and `[tool.uv]` with `python-preference = "only-managed"` (plus `package = false` for non-package repositories)
- **AND** `uv lock --check` SHALL exit `0` across all 35 workspace `pyproject.toml` repositories.
