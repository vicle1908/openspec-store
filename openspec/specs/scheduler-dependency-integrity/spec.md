# scheduler-dependency-integrity Specification

## Purpose
Ensures the scheduler container venv satisfies every hosted workload's declared dependency closure, with build-time and startup-time integrity gates and no reactive patch lines.
## Requirements
### Requirement: The scheduler venv SHALL satisfy every scheduled workload's declared dependency closure

The `tdt-scheduler` container's runtime virtual environment (`/opt/scheduler/.venv`)
SHALL contain the complete `[project.dependencies]` closure of every workload repo
that the scheduler hosts as a scheduled workflow. The set of hosted workloads is
defined by the mounted source trees and the manifest generators registered in
`agent-core/deployments/scheduler/generators/`: at minimum `jira-daily-reports`,
`jira-skill` (transitively imported by `jira-daily-reports`), `code-daily-scan`,
`tdt-observability`, and `webhook-receiver`.

Workload dependency resolution SHALL NOT rely on coincidental overlap with
`agent-core`'s dependency closure, nor on a hand-maintained `uv pip install` patch
list in the Dockerfile. Each workload's declared dependencies SHALL be installed by
`uv` from that workload's own `pyproject.toml`.

#### Scenario: Every declared workload dependency is importable in the built venv

- **GIVEN** a freshly built `tdt-scheduler:local` image
- **WHEN** each hosted workload's declared top-level packages are imported under
  `/opt/scheduler/.venv/bin/python` with the container runtime `PYTHONPATH`
- **THEN** every import SHALL succeed with no `ModuleNotFoundError`
- **AND** this SHALL include `redis`, `aiohttp`, `aiosqlite`, and `pyjwt`
  (declared by `jira-skill`) and `python-gitlab` (declared by `jira-daily-reports`
  and `jira-skill`)

#### Scenario: A newly declared workload dependency is present after rebuild

- **GIVEN** a workload repo adds a new entry to its `[project.dependencies]`
- **AND** the workload source tree is mounted into the scheduler container
- **WHEN** the scheduler image is rebuilt
- **THEN** the new dependency SHALL be present in `/opt/scheduler/.venv`
  without any manual edit to the Dockerfile's install steps

### Requirement: The image build SHALL fail on workload dependency drift

The scheduler image build SHALL include a dependency-integrity gate that runs
after the venv is provisioned. The gate SHALL attempt to import each hosted
workload's declared top-level package(s) under the final venv, and SHALL cause
`docker build` to exit non-zero if any import fails. This is the container
analogue of the launchd deploy scripts' `uv lock --check` pre-deploy gate defined
in the `host-deploy-script-consistency` spec.

#### Scenario: Build fails when a workload dependency is missing from the venv

- **GIVEN** a hosted workload declares a dependency that the venv does not provide
- **WHEN** `docker compose -f agent-core/compose.yaml build scheduler` runs
- **THEN** the build SHALL fail at the integrity-gate step
- **AND** the failure output SHALL name the missing module and the workload that
  declares it
- **AND** no `tdt-scheduler:local` image SHALL be tagged from the failed build

#### Scenario: Build passes when all workload dependencies resolve

- **GIVEN** every hosted workload's declared dependency closure is installed in
  the venv
- **WHEN** the integrity gate runs during the build
- **THEN** the gate SHALL print a success marker listing the workloads verified
- **AND** the build SHALL proceed to tag the image

### Requirement: Container startup SHALL verify workload imports before serving

The scheduler entrypoint SHALL run a startup self-test that imports each hosted
workload's scheduled entry module before `exec`-ing `tdt-scheduler serve`. If any
import fails, the entrypoint SHALL exit non-zero so Docker's `restart: unless-stopped`
policy surfaces the failure as a visible restart loop rather than allowing the
container to serve with a latent `ModuleNotFoundError` that would only appear at
tick time.

#### Scenario: Startup self-test fails fast on missing workload import

- **GIVEN** the built venv is missing a dependency required by a scheduled entry
  module
- **WHEN** the container starts and the entrypoint runs the self-test
- **THEN** the entrypoint SHALL exit non-zero before starting `tdt-scheduler serve`
- **AND** the failure SHALL be written to the scheduler entrypoint log with the
  failing module name
- **AND** `docker compose ps` SHALL show the scheduler in a restart loop

#### Scenario: Startup self-test passes and the scheduler serves

- **GIVEN** every scheduled entry module imports cleanly under the venv
- **WHEN** the container starts
- **THEN** the self-test SHALL pass
- **AND** the entrypoint SHALL proceed to generate manifests, touch the `.reload`
  sentinel, and `exec` `tdt-scheduler serve`

### Requirement: The Dockerfile SHALL NOT carry a reactive dependency patch list

Once workload repos are installed as packages, the scheduler Dockerfile SHALL NOT
contain ad-hoc `uv pip install` lines that exist solely to patch a workload's
missing runtime dependency (e.g. the `python-gitlab`, `google-api-python-client`,
`google-auth*` lines added reactively after runtime failures). Dependencies SHALL
be sourced from the workloads' `pyproject.toml` declarations.

#### Scenario: No reactive patch lines remain in the Dockerfile

- **WHEN** `agent-core/deployments/scheduler/Dockerfile` is inspected
- **THEN** it SHALL NOT contain `uv pip install` lines whose purpose is to supply a
  workload runtime dependency already declared in that workload's `pyproject.toml`
- **AND** any remaining `uv pip install` lines SHALL be documented with a reason
  that is not "a workload import crashed at runtime"

#### Scenario: python-gitlab resolves without a dedicated install line

- **GIVEN** the reactive `uv pip install "python-gitlab>=8.0.0"` line is removed
- **WHEN** the image is rebuilt and the integrity gate runs
- **THEN** `python-gitlab` SHALL still import cleanly in the venv because it is
  pulled in by `jira-daily-reports` / `jira-skill` declared dependencies

