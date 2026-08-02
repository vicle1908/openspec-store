# Implementation evidence

Verified on 2026-07-28 against the dirty-source identities below. A repository
commit alone is not the verified identity; tracked diff hashes and untracked
paths are part of the result.

## Source identity

| Repository | HEAD | Tracked binary-diff SHA-256 | Untracked implementation paths |
| --- | --- | --- | --- |
| `agent-core` | `3aff416eca0801ea3a1804892bc5700aac71ebf5` | `ce202335994dca60c501fe7254b8f3ea174afca3626b6833bbfa31ca6cbd3807` | `docker-entrypoint-initdb.d/20-create-harness-db.sql` |
| `agent-docs-sync` | `47e37e9a7c055e4db82e391b956a14f6d651d1b1` | `fed3ced9ee43a958c9b3aed02d8a09327bdd616a4752be5e4825cbe6af9a9bfe` | none |
| `agent-harness` | `087c064d83045f6262481355fc30fcf6d1ee1641` | `f2d2b0b068fabac1127fe0ab41b0d0e41ca383de58350c44acf9da60a1b442e7` | `tests/test_dependency_baseline.py`, `tests/test_postgres_integration.py` |

## Scope completed

- Replaced inherited harness configuration with a composed immutable runtime
  profile and warning-backed legacy projections.
- Delegated dotenv loading to `tdt_core.env.load_tdt_env()`, mapped
  `HARNESS_DURABLE` and `TDT_POSTGRES_URL`, rejected
  `HARNESS_PERSISTENCE_DURABLE`, and kept workspace repository resolution out
  of the `extra="forbid"` harness model.
- Added explicit gateway resolution, static frozen stage contracts, and one
  checkpoint state schema.
- Reconciled every accumulator with its declared semantic reducer, kept scalar
  lifecycle fields unreduced, and executed a native LangGraph test proving a
  `Command(update=..., goto=...)` target observes the source update in the next
  step.
- Replaced the shared gate with dedicated post-stage nodes and native
  interrupt-ID resume validation.
- Unified run, stream, status, history, and resume around the core async
  checkpointer boundary and public graph state APIs.
- Added non-destructive fresh-volume bootstrap validation for the isolated
  `agent_harness` database. A read-only check confirmed the existing local
  database and all three checkpoint tables already exist; no migration ran.
- Added a marked real-Postgres suite that starts from an empty disposable
  database, provisions through `AsyncPostgresSaver.setup()`, streams to a gate,
  inspects bounded history, resumes from a separate CLI process, and proves the
  completed spec artifact is not regenerated.
- Kept the measured workflow sequential because no candidate branch passed the
  reducer, ordering, gate, authority, and budget safety analysis.

## Verification

| Gate | Result |
| --- | --- |
| `agent-core`: Ruff, format, strict mypy, full pytest | passed; 535 tests |
| `agent-docs-sync`: Ruff, format, strict mypy, full pytest | passed; 166 tests |
| `agent-harness`: Ruff, format, strict mypy, full pytest | passed; 196 tests, including the real PostgreSQL marker |
| Frozen dependency tuple | passed in all three repositories: Pydantic AI 2.18.0, Harness 0.11.0, LangGraph 1.2.9, checkpoint 4.1.1, Postgres saver 3.1.0 |
| Disposable fresh resolution | `/tmp/tdt-framework-matrix.agSVSy`; 221/217/215 packages, no lockfile changes, focused contracts passed 24/6/12 |
| Independent rollback | passed: core 16, docs 11, harness 97 including real PostgreSQL |
| OpenSpec strict validation | both active changes passed after the final artifact refresh |

## Scope verification

GitNexus final comparison reports:

- `agent-core`: no indexed tracked-symbol changes; the untracked init SQL and
  focused tests are recorded explicitly above.
- `agent-docs-sync`: one test symbol, no affected processes, LOW risk.
- `agent-harness`: seven indexed files/symbols, eleven affected report,
  approve, reject, and status flows, HIGH risk. These are the approved
  configuration/topology roots, and the complete CLI plus negative-path suites
  passed after the final edit.

No unexpected production symbol or execution-flow change was found.
