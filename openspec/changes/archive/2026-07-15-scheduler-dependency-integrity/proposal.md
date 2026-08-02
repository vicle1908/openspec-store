## Why

The `tdt-scheduler` Docker container resolves every scheduled workload against a
Python venv (`/opt/scheduler/.venv`) that was **never built from those workloads'
dependency declarations**. The venv contains `agent-core`'s dependency closure
plus a hand-curated `uv pip install` patch list; each workload repo
(`jira-daily-reports`, `jira-skill`, `code-daily-scan`, `tdt-observability`,
`webhook-receiver`) is only placed on `PYTHONPATH`, never installed as a package.
A workload's `[project.dependencies]` are therefore satisfied only by coincidental
overlap with `agent-core`'s closure.

This already caused a production incident (2026-07-14: `python-gitlab`
`ModuleNotFoundError` at a scheduled tick, patched reactively into the Dockerfile),
and live inspection confirms four more declared deps (`redis`, `aiohttp`,
`aiosqlite`, `pyjwt`) are **absent from the running venv today**. They have not
broken only because the importing submodules (`jira_skill.state.store`,
`jira_skill.backup.storage`) are not on any currently-scheduled import path — an
accidental safety net that any refactor can remove. Unlike the launchd deploy
scripts (`ai-review`, `webhook-receiver`), which run a `uv lock --check` gate and
SHA-256 source/runtime verification before deploying, the scheduler container path
has **zero dependency-drift detection**. Drift surfaces only as a runtime crash at
the latest, least-observable point in the lifecycle.

## What Changes

- Install each scheduled workload repo as a real package (resolved by `uv`) so its
  full `[project.dependencies]` closure is present in the scheduler venv, instead
  of relying on `PYTHONPATH` plus a hand-maintained `uv pip install` list.
- **Remove** the reactive `uv pip install` patch lines from the scheduler
  Dockerfile (`google-api-python-client`, `google-auth*`, `python-gitlab`) once the
  workloads' declared closures cover them.
- Add a **build-time dependency-integrity gate**: after the venv is built, assert
  that every scheduled workload's declared top-level package imports cleanly under
  the final venv, failing the image build on any `ModuleNotFoundError`. This is the
  container analogue of the launchd `uv lock --check` gate.
- Extend the **scheduler healthcheck / startup self-test** to exercise each
  scheduled workload's entry module import, so residual drift surfaces at container
  start (loud, restart loop) rather than at tick time (silent).

## Capabilities

### New Capabilities
- `scheduler-dependency-integrity`: The scheduler container's runtime venv SHALL
  satisfy the complete dependency closure of every scheduled workload it hosts;
  drift between declared workload dependencies and the installed venv SHALL be
  detected at build time and at container startup, never first observed as a
  scheduled-tick runtime error.

### Modified Capabilities
<!-- No existing spec's requirements change. scheduler-dockerfile-canonicalization
     and scheduler-docker-deployment remain valid; this adds a new orthogonal
     capability rather than altering their requirements. -->

## Impact

- **Code:** `agent-core/deployments/scheduler/Dockerfile` (venv build + patch-list
  removal + integrity gate), `agent-core/deployments/scheduler/entrypoint.sh`
  (optional startup self-test), `agent-core/compose.yaml` healthcheck (workload
  import probe). Possibly a dedicated scheduler `pyproject.toml` that declares the
  workload repos as path dependencies.
- **Dependencies:** No new third-party dependencies added to the ecosystem; the
  change makes *already-declared* workload dependencies actually resolvable in the
  scheduler venv.
- **Systems:** The Docker scheduler stack (`agent-core-local` compose project).
  Rebuild required to take effect. No change to launchd-managed services
  (`webhook-receiver`, `ai-review`) or to the host `deploy.sh` scripts.
- **Risk:** Rebuild is the only deployment action; existing schedules and DBOS
  state in PostgreSQL are unaffected. Verified via the existing
  `scripts/verify_scheduler_compose_up.sh` smoke test.
