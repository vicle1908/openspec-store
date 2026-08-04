# Release Notes: tdt-core 0.2.0 — TDT Home Security Kernel

## Summary

Provider-first deployment of the governed TDT Home configuration and
environment loading mechanism.  All consumer repositories continue to
load credentials via `load_tdt_env()` from `~/.tdt/.env` — no consumer
source changes are required.

## What Changed

- **Filesystem kernel** (`fs_kernel.py`): descriptor-relative, no-follow
  operations for safe TDT_HOME traversal
- **Strict schemas** (`control_plane_schema.py`): Pydantic models for
  journal headers, records, backup metadata, and secret references
- **Source registry** (`source_registry.py`): 15-participant provider
  registry with manifest validation
- **Config loader** (`config_loader.py`): typed config with secret
  classification and `${VAR}` reference validation
- **Config ownership** (`config_ownership.py`): governed scheduler config
  parser with duplicate detection
- **Source audit** (`source_audit.py`): AST-based + regex detection of
  hard-coded TDT_HOME paths
- **Migration engine** (`migration_engine.py`): journaled plan compilation,
  apply, backup/restore, verification, and crash recovery
- **CLI** (`cli.py`): `tdt config doctor`, `tdt config create-manifest`,
  `tdt config source-audit`

## Breaking Changes

None.  All changes are provider-internal.  Consumer repositories require
no source modifications.

## Upgrade Path

1. Install `tdt-core>=0.2.0` in your environment
2. Run `tdt config doctor` to verify your `~/.tdt` layout
3. No consumer code changes required

## Known Limitations

- Internal package registry publication not yet executed (no approved
  registry coordinate)
- Staged consumer rollout pending per-consumer deployment owner approval

## Verification

- 507+ tests pass (0 failures, 16 skipped)
- ruff lint clean
- mypy --strict clean
- 356/356 OpenSpec specs valid
