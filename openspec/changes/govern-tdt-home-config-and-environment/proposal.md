# Govern TDT_HOME Provider Foundations

## Why

The TDT ecosystem has one intended `TDT_HOME` root but multiple consumers still resolve paths, environment files, configuration, and credentials with incompatible rules; this change establishes the secure provider contract before any downstream or live migration is attempted.

## What Changes

- Make `tdt-core` the provider for call-time `TDT_HOME` resolution and bounded runtime path helpers.
- Preserve development compatibility while adding an explicit production environment profile that cannot be selected by a dotenv file.
- Govern typed non-secret configuration and require full-scalar environment references for secret-shaped settings.
- Add fail-closed private filesystem primitives for provider-owned directory and file operations.
- Add a redacting `tdt config doctor` command that works from an installed provider package and does not require sibling repositories.
- Validate mandatory packaged provider registry/schema data before provider behavior is considered usable.
- Verify the provider from a clean local wheelhouse, without an editable checkout or `PYTHONPATH` dependency.
- Keep all live filesystem mutation, downstream migration, deployment rollout, and consumer-owned facts outside this change.

## Capabilities

### New Capabilities

- None. This change extends the existing `tdt-env-loader-tdt-home` capability.

### Modified Capabilities

- `tdt-env-loader-tdt-home`: make root selection, environment precedence, bounded paths, private provider operations, diagnostics, and provider packaging behavior explicit and testable.

## Ownership Boundaries

- `tdt-core` owns provider APIs, environment/config behavior, the descriptor-relative security kernel, provider schemas, packaged registry validation, diagnostics, and provider release verification.
- Consumer repositories own their executable legacy paths, dependency floors, deployment writers, reader/writer principals, launch mechanisms, compatibility adapters, and consumer verification evidence.
- `openspec-store` owns the normative planning artifacts only; it does not own application code or operator runtime files.
- `~/.tdt` remains operator-owned and is not modified by this change.
- The existing `tdt-core-home-security-kernel` worktree is the implementation candidate. The staged `tdt-core-home-control-plane` worktree is retained as superseded review evidence and is not merged automatically.

## Explicit Non-Goals

- Migrating consumer source paths or changing consumer dependency metadata.
- Compiling or applying a cross-repository migration plan.
- Implementing live migration, deployment restart, rollback of deployed consumers, or operator cutover.
- Changing `tdt-observability` Python compatibility or other repository-specific configuration schemas.
- Publishing to Nexus or changing provider credentials.
- Repairing permissions, links, configuration, credentials, logs, databases, schedules, or state under the live `~/.tdt` root.
- Replacing `/opsx:verify` or introducing a new OpenSpec workflow schema.

## Deferred Successor Changes

The following work is intentionally deferred and SHALL receive separate owned changes:

1. `govern-tdt-home-source-conformance` — consumer/deployment manifests, source audit, and repository-owned exceptions.
2. `build-tdt-home-synthetic-migration-engine` — typed plans, attestations, journaled apply/recovery, and synthetic interruption testing.
3. One provider-gated adoption change per consumer repository — source migration, metadata, deployment ownership, and consumer tests.
4. `release-and-roll-out-tdt-home-provider` — provider-first deployment and reverse rollback rehearsal.
5. `cut-over-live-tdt-home` — separately approved operator plan for the real `~/.tdt` tree.

## Impact

- Primary implementation repository: `tdt-core` (Python 3.14, `uv`, pytest, Ruff, strict mypy).
- Primary provider surfaces: `src/tdt_core/paths.py`, `env.py`, `config.py`, CLI/diagnostics, provider schemas, packaged registry data, and focused tests.
- Current provider release remains `0.2.x` until all provider gates pass; the change does not authorize a version bump by itself.
- Verification must include focused tests, full provider gates, strict OpenSpec validation, and a clean wheelhouse installation.

## Rollback

Provider implementation can be rolled back by restoring the pre-change `tdt-core` artifact and metadata in the provider worktree. Because this change does not alter consumers or live `~/.tdt`, rollback does not require deleting or rewriting operator data. Any consumer or live migration rollback belongs to its successor change.
