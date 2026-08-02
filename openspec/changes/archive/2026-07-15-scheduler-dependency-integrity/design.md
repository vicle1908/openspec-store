## Context

The `tdt-scheduler` runs as a long-lived DBOS host in the `agent-core-local` compose
project. It hosts scheduled workflows for several sibling repos. Two independently
versioned sources back every scheduled run inside the container:

- **First-party code** — the workload repos, bind-mounted read-only at
  `/workspace/<repo>/src` (see `agent-core/compose.yaml`). This is live: read fresh
  from the host on every process start, and CLIs run as fresh subprocesses per tick.
- **Third-party dependencies** — `/opt/scheduler/.venv`, built once at image build
  time by `uv sync` against `agent-core/uv.lock`, plus a hand-curated
  `uv pip install` list (`google-api-python-client`, `google-auth*`, editable
  `tdt-sheets` / `tdt-observability`, and `python-gitlab`).

The workload repos are placed on `PYTHONPATH` by `entrypoint.sh` but are **never
installed as packages**. Their `[project.dependencies]` are satisfied only where
they happen to overlap `agent-core`'s closure or the hand list. This asymmetry —
live code against a frozen, hand-maintained venv with no reconciliation — is the
root cause validated during exploration:

- 2026-07-14 `python-gitlab` incident: a top-level `import gitlab` was added to a
  live-mounted module; the code looked deployed but the venv lacked the dep, so the
  scheduled tick crashed with `ModuleNotFoundError`. Fixed reactively by hardcoding
  `uv pip install python-gitlab` into the Dockerfile.
- Live probe (running container, real runtime `PYTHONPATH`): `redis`, `aiohttp`,
  `aiosqlite`, `pyjwt` — all declared by `jira-skill` — are **absent** from the
  venv. They survive only because their importing submodules
  (`jira_skill.state.store`, `jira_skill.backup.storage`) are lazy/off the scheduled
  import path. `jira_skill/__init__.py` eagerly imports only `.config`.

The launchd deploy scripts (`ai-review`, `webhook-receiver`) already solve the
equivalent problem with a `uv lock --check` gate plus SHA-256 source/runtime
verification (`host-deploy-script-consistency` spec). The scheduler container path
has no analogue.

## Goals / Non-Goals

**Goals:**
- Make the scheduler venv provably satisfy the full dependency closure of every
  hosted workload, resolved from the workloads' own `pyproject.toml`.
- Detect drift at **build time** (fail the build) and at **container startup** (fail
  fast into a visible restart loop), never first at a scheduled tick.
- Eliminate the reactive `uv pip install` patch list as a maintenance liability.

**Non-Goals:**
- Unifying the two deployment models (launchd vs Docker). Out of scope.
- Adding a unified `tdt deploy status` CLI or auto-rebuild-on-commit automation.
  Those are the later "B" and "C" layers from the exploration; this change is the
  "A" (close-the-drift) layer only.
- Changing any workload's declared dependencies, cron schedules, or DBOS state.
- Touching the launchd `deploy.sh` scripts or the `host-deploy-script-consistency`
  spec (this adds an orthogonal capability).

## Decisions

### Decision 1: Install each workload editable, extending the existing post-sync install list

Extend the Dockerfile's existing `uv pip install -e /workspace/<repo>` block
(currently `tdt-sheets` and `tdt-observability` at L83-84) to cover **all** hosted
workloads: add `jira-skill`, `jira-daily-reports`, `code-daily-scan`, and
`webhook-receiver`. Each editable install resolves that workload's own
`[project.dependencies]` closure against the already-built venv.

- **Why:** It is the smallest delta that fixes the root cause, and it reuses a
  pattern already proven in this exact Dockerfile. The path-dep rewrite at L60-73
  already normalizes `../<repo>` → `/workspace/<repo>` in every workload's
  `pyproject.toml`, so the editable installs resolve their first-party path deps
  correctly with no additional rewrite. The install target (`/workspace/<repo>`) is
  the same path the compose volumes bind-mount, so code stays live and the
  PYTHONPATH-only mechanism becomes redundant.
- **Critical constraint — dependency cycle:** `code-daily-scan` declares
  `agent-core` as an editable path dep (`code-daily-scan/pyproject.toml`
  `[tool.uv.sources]`). Any approach that folds the workloads into **agent-core's own
  dependency closure** (a `[project.optional-dependencies]` extra, or a dedicated
  scheduler `pyproject.toml` that `uv sync` resolves as one graph) creates the back-edge
  `agent-core → code-daily-scan → agent-core`. Imperative, sequential
  `uv pip install -e` sidesteps this because each package resolves against the venv
  already containing `agent-core` (installed by the `uv sync` of the agent-core
  project itself), rather than in a single simultaneous resolution graph.
- **Alternatives considered:**
  - *`[project.optional-dependencies]` extra on `agent-core/pyproject.toml` +
    `uv sync --extra`.* Rejected — triggers the `code-daily-scan → agent-core` cycle
    above, forces agent-core's `uv.lock` to absorb the entire workload closure (large
    lock churn that also affects the `app` compose service which shares the manifest),
    and the scheduler pyproject is a **symlink** to agent-core's, so the extra could
    not be scheduler-scoped without breaking that symlink.
  - *Dedicated scheduler `pyproject.toml` (break the symlink) + separate lockfile.*
    Rejected — introduces a second lockfile that can drift from the workloads'
    lockfiles, which is the very class of problem this change exists to eliminate.
  - *Keep PYTHONPATH + expand the hand `uv pip install` list.* Rejected — it is the
    status quo that caused the incident; every new dep is a manual, reactive edit.
- **Trade-off accepted:** `uv pip install -e` resolves third-party transitive deps by
  range, not from a unified lockfile, so it is less reproducible than `uv sync`. This
  is the *same* posture already in effect for the two existing editable installs
  (L83-84); full lockfile unification is explicitly a Non-Goal and is blocked by the
  cycle anyway. The build-time integrity gate (Decision 2) backstops any resolution
  surprise by failing the build.

### Decision 2: Build-time integrity gate as a distinct Dockerfile step

After the venv is provisioned, run a gate that imports each workload's declared
top-level packages under the final venv and exits non-zero on any failure.

- **Why:** Fails the build before an image is ever tagged — the cheapest place to
  catch drift. Directly mirrors the launchd `uv lock --check` gate.
- **Alternatives considered:**
  - *Rely only on the startup self-test.* Rejected — that catches drift after an
    image is built and deployed; the build gate shifts detection left.
  - *`uv pip check`.* Insufficient — it validates installed-package metadata
    consistency, not that a workload's declared imports actually resolve under the
    runtime `PYTHONPATH`.

### Decision 3: Startup self-test in entrypoint.sh, before `exec serve`

The entrypoint imports each scheduled entry module and exits non-zero on failure,
so `restart: unless-stopped` turns latent drift into a visible restart loop.

- **Why:** Defense in depth for anything the build gate cannot see (e.g. a
  host-mounted source change made after the image was built). Startup is loud;
  tick-time is silent.
- **Alternatives considered:**
  - *Only extend the compose healthcheck.* Kept as a complementary layer (Decision 4)
    but insufficient alone — the current healthcheck imports only
    `tdt_core.scheduler.cli`, so "healthy" says nothing about workloads.

### Decision 4: Healthcheck exercises a representative workload import

Extend the healthcheck to import at least one scheduled workload entry module in
addition to the core CLI, so monitoring reflects workload-import health.

- **Why:** Makes the green/red signal meaningful for the failure mode that actually
  bites. Low cost, high observability value.

## Risks / Trade-offs

- **[Editable installs may shadow the read-only mounts]** → The venv install and the
  `PYTHONPATH` mount could resolve a workload from different locations. Mitigation:
  keep a single resolution order; verify with the startup self-test that the
  imported module path is the mounted source, and rely on the existing
  `verify_scheduler_compose_up.sh` smoke test.
- **[Larger venv / longer build]** → Installing full closures for five workloads
  increases build time and image size. Mitigation: `uv` caching; this is a build-time
  cost only, paid once per rebuild.
- **[Transitive dep conflicts]** → Resolving all workload closures together could
  surface version conflicts that the partial venv masked. Mitigation: this is
  desirable — a conflict is real and should fail the build rather than hide behind a
  partial install. Resolve by aligning the offending version pins.
- **[Removing patch lines regresses a needed dep]** → Mitigation: the build-time
  integrity gate is added in the same change, so any regression fails the build
  immediately with a named module.

## Migration Plan

1. Extend the Dockerfile post-sync install block (L83-84) to `uv pip install -e` all
   hosted workloads (`jira-skill`, `jira-daily-reports`, `code-daily-scan`,
   `webhook-receiver`) in dependency order — `jira-skill` before `jira-daily-reports`
   (which depends on it), and `code-daily-scan` after `agent-core` is present. No new
   lockfile; the existing L60-73 path-dep rewrite already prepares each workload's
   `pyproject.toml`.
2. Add the build-time integrity gate step to the Dockerfile.
3. Add the startup self-test to `entrypoint.sh`; extend the compose healthcheck.
4. Remove the reactive `uv pip install` patch lines.
5. `docker compose -f agent-core/compose.yaml build scheduler` — expect the gate to
   pass; if it fails, it has found real drift to fix.
6. Run `scripts/verify_scheduler_compose_up.sh` (clean rebuild + health + schedule
   count assertions).
7. **Rollback:** re-tag and run the previous image; DBOS state in PostgreSQL is
   untouched, so rollback is a pure image swap.

## Open Questions

- Should the workload set for the gate be derived automatically from the registered
  manifest generators (`generators.GENERATORS`) plus the compose mount list, rather
  than hardcoded? Deriving it avoids a second place to update when a workload is
  added. Leaning yes — derive from the mounts.
  - **Resolved (implementation):** the gate reads each workload's declared
    `[project.dependencies]` from its own `pyproject.toml` and derives module names
    from installed-distribution metadata (`top_level.txt` / RECORD), so a newly
    declared dependency is covered without editing the gate. The workload *set*
    itself (`HOSTED_WORKLOADS`) remains an explicit tuple aligned with the Dockerfile
    editable-install block and compose mounts — a single, intentional place to add a
    workload. Full generator-derived discovery is deferred as a non-goal (no drift
    risk today because the set is asserted by the build gate).
- Should `webhook-receiver` be in the gate given it is launchd-managed in production
  but its CLIs (`webhook-selftest`, `dlq-reaper`) are mounted for scheduler
  subprocesses? Leaning yes — if it is mounted and reachable by a schedule, its
  closure must resolve.
  - **Resolved:** yes. `webhook-receiver` is in both `HOSTED_WORKLOADS` (build gate)
    and `ENTRY_MODULES` (startup self-test), because its CLIs are mounted and
    reachable by scheduler subprocesses.

### Decision 4 resolution: healthcheck extended to a workload import

The Dockerfile `HEALTHCHECK` (task 6.1) was extended from importing only
`tdt_core.scheduler.cli` to also importing a representative scheduled workload entry
module (`jira_daily_reports.cli`). Because the editable installs (Decision 1) now put
every workload in `/opt/scheduler/.venv`, the workload is importable directly under
the venv Python without relying on the entrypoint's `PYTHONPATH`, so the probe is
low-cost and makes the green/red health signal reflect workload-import health — the
failure mode that actually bites — not just core-CLI health. Kept minimal (one
representative workload) to bound healthcheck latency; the build gate and startup
self-test remain the exhaustive checks.
