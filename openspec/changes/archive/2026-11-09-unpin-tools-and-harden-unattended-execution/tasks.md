# Tasks

## 1. Specification & Manifest Unpinning

- [x] 1.1 Unpin standalone Python CLI tools in `platform/openspec-store/config/uv-tools.json` (`graphifyy` version set to `latest`).
- [x] 1.2 Verify `config/npm-global-tools.json` and agent manifests already declare `version: latest`.
- [x] 1.3 Author delta specification for `portable-workstation-toolchain` defining unpinned tool maintenance, automatic unpin recovery, authority-gated MAS skipping, and zero-sudo non-interactive execution.
- [x] 1.4 Validate OpenSpec change strictly via `openspec validate --changes unpin-tools-and-harden-unattended-execution --strict --store openspec-store`.

## 2. Hardening Unattended Toolchain Maintenance (`shb-schedule`)

- [x] 2.1 Update `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` `step_uv_tools_update`: detect pinned hints from `uv tool upgrade` and automatically fall back to `uv tool install --upgrade <tool>@latest`.
- [x] 2.2 Update `workstation_update.py` `step_mas_update`: query installed Homebrew casks and skip any application managed by Cask (`telegram`) to avoid package manager collisions and installer receipt errors.
- [x] 2.3 Update `workstation_update.py` `_get_env()` to export complete non-interactive flags (`HOMEBREW_NO_INTERVENTIONS=1`, `PIP_NO_INPUT=1`, `NPM_CONFIG_YES=true`, `DEBIAN_FRONTEND=noninteractive`).
- [x] 2.4 Verify all tests pass in `shb/shb-schedule` via `env -u PYTHONPATH uv run pytest -q`.

## 3. Hardening Shell Maintenance Runner (`scripts/workstation-daily-update.sh`)

- [x] 3.1 Update `scripts/workstation-daily-update.sh` Stage 1b (MAS): check installed Homebrew casks and skip Cask-managed applications.
- [x] 3.2 Update `scripts/workstation-daily-update.sh` Stage 4 (`uv tool`): detect pinned tools in `uv tool upgrade --all` output and automatically re-install with `@latest`.
- [x] 3.3 Synchronize mirror atomically to `platform/openspec-store/scripts/workstation-daily-update.sh` using `cp then chmod` and update `config/script-provenance-manifest.tsv`.
- [x] 3.4 Execute `workstation-daily-update.sh --check` to verify zero drift, clean stage completions, and zero prompts.

## 4. Verification & OpenSpec Archival

- [x] 4.1 Trigger `shb-schedule run-now workstation-daily-update` to verify end-to-end execution without degraded steps.
- [x] 4.2 Validate OpenSpec store strictly via `openspec validate --all --strict --store openspec-store`.
- [x] 4.3 Archive and commit completed change `unpin-tools-and-harden-unattended-execution` to `platform/openspec-store`.
