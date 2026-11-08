# Spec Delta: uv-runtime-management

## ADDED Requirements

### Requirement: Self-contained maintenance and toolchain scripts with PEP 723
Standalone maintenance, validation, and governance Python scripts under `scripts/` directories across `~/Developer/` and `platform/openspec-store/` SHALL declare `#!/usr/bin/env -S uv run` shebangs and PEP 723 inline dependency metadata. Scripts SHALL run hermetically under `uv run` without assuming an activated host virtual environment.

#### Scenario: Maintenance script runs hermetically via uv run
- **WHEN** an operator or automation executes a script in `platform/openspec-store/scripts/*.py`
- **THEN** `uv` SHALL resolve the declared Python version and dependencies in an isolated ephemeral environment
- **AND** the script SHALL NOT fail due to missing dependencies in the host Python environment
- **AND** the script SHALL execute cleanly regardless of whether `/usr/bin/python3` or a host `.venv` is on PATH
