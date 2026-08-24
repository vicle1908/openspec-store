# repair-tdt-observability-compose-deployment verification

## Final archive evidence (2026-08-24)

This section supersedes earlier identity, runtime, and archive-eligibility
snapshots below. Historical sections remain retained for audit context and MUST
NOT be read as the current deployment state.

Current verdict: **success / implementation accepted / archived with retained
warnings / final deployment intentionally running**. Deployment-owned cleanup
is complete within the verified allowlist. No running container references the
merged integration worktree; its separate Git/Orca removal is now eligible but
was not part of the Docker-only single-set cleanup.

### Exact source and deployment identities

- `tdt-observability` accepted implementation:
  `9a5f7c28b08609952468af67e35022b38f4549de`, now an ancestor of canonical
  `main` at `d891275d75c77db578e561ad3723f4cb98a768d9`.
- `agent-core`: `468140192725e81246223c37f3b0a37573eaba3e`.
- `tdt-scheduler`: `489100d5fcafec8c6b85e4b22093fb8bd75a2edc`.
- `webhook-receiver`: `d999ebfcdcb251f9771a010f314dd136bdedf787`;
  the canonical launchd deployment manifest and live service bind this same
  source revision.
- `agent-harness`: `35aedbd4cdcda281a3fd7ca5f639b60bf4e51c74`.
- `tdt-core`: `3043854a006ddccd71270073409a7b94f058cd67`.
- `ai-review`: `c35ee68e520d4eccf25cf712802d8b3dbc4fb649`.
- OpenSpec store at acceptance capture:
  `91cdfb4d7ceed329879f991a4c5c7f9eb0d54d61`.
- Final Docker run: `tdt-final-green-20260824t085909z`.
- Runtime network: `tdt-final-green-20260824t085909z-runtime`.
- Observability network: `tdt-final-green-20260824t085909z-observability`.
- Projects: `tdt-final-green-20260824t085909z-observability`,
  `tdt-final-green-20260824t085909z-observability-agent-core`, and
  `tdt-final-green-20260824t085909z-observability-tdt-scheduler`.

Canonical `tdt-observability/main` was promoted by a fast-forward-only merge:
the accepted runtime commit `9a5f7c28b08609952468af67e35022b38f4549de`
is followed by deployment documentation commit
`58ff94820cffc3ec320ac930130aeb196f94b7a6` and canonical re-home evidence
commit `d891275d75c77db578e561ad3723f4cb98a768d9`. The three pre-merge local
deployment edits were preserved in a named stash, reviewed as superseded, and
the exact stash was dropped only after canonical promotion and re-home passed.
Generated Graphify output and unrelated worktrees remain uncommitted and
untouched.

### Canonical re-home and cleanup evidence

- The intentionally running `tdt-final-green-20260824t085909z` project family
  retained the same three Compose project names, networks, state volumes, and
  loopback ports. `otel-lgtm`, `otel-gateway`, `health-poller`, and `scheduler`
  were recreated from canonical source without rebuilding dependencies or
  deleting volumes.
- Post-re-home checks passed for all three projects, all running-container
  restart counts remained zero, and direct HTTP checks returned 200 for
  Grafana, Langfuse, MLflow, scheduler, webhook-receiver, and ai-review. The
  network-scoped `otel-gateway:13133` check also passed.
- The scheduler now mounts canonical
  `/Users/androidteam/Developer/tdt-observability/src`; all 16 `/workspace`
  content mounts remain read-only. No container in the final-green family has
  a bind mount into `tdt-observability-integrated`.
- The cumulative accepted manifest remains immutable at the path and SHA-256
  below. Run-owned operational pointers were updated to canonical
  `/Users/androidteam/Developer/tdt-observability`; this did not rewrite the
  accepted behavioral evidence captured at implementation commit `9a5f7c28...`.
- Exact Git/Orca cleanup removed the clean merged worktrees
  `observability-gap-review`, `omp-optional-supervised`, and
  `verify-image-provenance-8-2-9-8`; Orca also removed their local branches.
  `tdt-observability-backends` remains because its tip is not an ancestor of
  canonical `main`. `goose-langfuse-supervised` and
  `pi-resources-supervised` remain because they have live unfinished agent
  terminals.
- At this initial checkpoint, the merged `tdt-observability-integrated`
  worktree remained mounted by the historical task11 scheduler. A later,
  explicitly authorized single-set Docker cleanup removed that duplicate;
  current running mount references are zero.
- Exactly 32 unreferenced volumes from failed run families
  `tdt-final-release-20260824t065243z`,
  `tdt-final-proof-20260824t073808z`,
  `tdt-final-live-20260824t080819z`, and
  `tdt-accepted-stable-20260824t083042z` were removed only after an exact-count
  check, per-volume Compose project-label match, and zero-container-reference
  check. Zero volumes with those prefixes remain. No prune command was used;
  all final-green and unrelated resources were preserved at that checkpoint.
- The post-cleanup full-store strict validation reported `376 passed, 1
  failed`; the failure is the unrelated concurrent active change
  `repair-hermes-cron-run-reliability`, which was preserved and not modified.
  `openspec store doctor` reported no store issues.

### Exact canonical-main closure

The running final-green family was recaptured after the initial re-home so the
required code, image metadata, Compose labels, bind mounts, and operational
replay pointers all resolve to canonical `main` revisions:

- `tdt-observability/main` source/config revision:
  `d891275d75c77db578e561ad3723f4cb98a768d9`; exact-main evidence commit:
  `cc778b76a86084ed3bfd08ed4546afb42c273fe6`.
- `agent-core/main`: `df4df21e487154d0e55c38de9771d13a4f98bc3b`.
- `tdt-scheduler/main`: `dbe4198cdb74d6a04a8ddd8872e67984b4afba56`.
- `tdt-core/main`: `772265e4beb113a02c7aaa687a37ef1cfe0dee0a`.
- `webhook-receiver/main`, `agent-harness/main`, and `ai-review/main` remain at
  the exact accepted revisions listed above.

The required tdt-core change was reconciled selectively onto its newer main:
the retired `providers.*.api_key_env` exemption and hardcoded
`agent_core.scheduler_setup` paths were removed without deleting main's newer
persisted-state reconciliation. The focused config plus full scheduler suite
passed 166 tests; targeted Ruff and strict mypy passed.

Agent-core image `sha256:ea2c245c3f10647a32f7d9893dac576bf9c6691c01942e77ddf49428fbd1f5db`
was freshly built from agent-core main with a named tdt-core main context. A
full scheduler main build passed its fatal seven-workload integrity gate, but
Docker Desktop failed during the large image export (first BuildKit EOF, then
read-only Docker data storage), so no failed image was promoted. After a
supported Docker Desktop force-stop/start on the same context and a successful
disposable write probe, the bounded main-overlay image
`tdt-scheduler:main-dbe4198-r2` was built and deployed. Its image ID is
`sha256:1a73a69c0b35573621cd73d5b07e7f29547cb08c62d5154a234c7e8047168c58`;
its OCI labels bind the three exact main revisions and declare
`com.tdt.runtime.provenance=canonical-main-overlay`.

All containers in the three final-green projects were recreated from canonical
Compose paths while retaining project names, networks, ports, and named
volumes. Zero final-green labels or mounts reference the integration worktree
or former owner-input snapshots. All 16 scheduler workspace mounts are
read-only and include canonical agent-core, tdt-core, and tdt-observability
main sources. The scheduler completed startup integrity, launched DBOS,
registered 21 workflows, applied 19 schedules, and became healthy. Grafana,
Langfuse, MLflow, scheduler, webhook-receiver, ai-review, and network-scoped
OTel gateway probes all returned HTTP 200; every declared healthcheck is
healthy, every long-lived restart count is zero, and both one-shot containers
exited zero.

The accepted cumulative manifest and its SHA-256 below remain immutable
behavioral evidence for the earlier accepted implementation matrix. The newer
exact-main closure is additive runtime provenance and is recorded durably in
`tdt-observability/deploy/evidence/final-full-deployment-acceptance.md`.

### Single-set Docker cleanup

The operator authorized removal of every superseded TDT Docker set and old
data while retaining the exact-main final-green family. After diagnostics and
exact ownership/reference checks, cleanup removed four historical task11
containers, two task11 networks, 145 unreferenced old TDT-labeled volumes, 59
superseded TDT image tags, two untagged duplicate-container image IDs, and the
two exited-zero final-green one-shot container records. No global prune was
used, and unrelated Omniroute resources plus unlabeled anonymous volumes were
preserved.

Final inventory is one normalized TDT family with 15 healthy/running
long-lived containers and five first-party TDT image tags. Together with two
healthy unrelated Omniroute containers, Docker has 17 running containers and
no exited container records. Zero old TDT containers, image tags, or labeled
volumes remain; zero running mounts reference `tdt-observability-integrated`.
Final-green healthchecks remain healthy with restart counts zero. Available
host space increased from approximately 14 GiB to 31 GiB.

### Stable operator-facing stack identity

The final-green project name is retained only as historical acceptance
identity. The permanent Docker Desktop family now uses primary project
`tdt-local-full`, owner projects `tdt-local-full-agent-core` and
`tdt-local-full-tdt-scheduler`, and networks `tdt-local-full-runtime` plus
`tdt-local-full-observability`. Separate owner projects preserve safe lifecycle
boundaries while the common prefix presents one meaningful full-stack family.

Stable projects were started on fresh project-scoped volumes under the
no-old-data decision and verified before the old final-green volumes and image
aliases were removed. Final current inventory is 15 running TDT containers,
exactly FOUR first-party TDT image tags, 12 configured Docker healthchecks
healthy, 3 services without Docker healthchecks, and restart count 0 for all 15.
Together with two unrelated healthy Omniroute containers, zero exited records
remain. All seven published TDT ports bind to `127.0.0.1`; seven direct host
service probes plus the network-scoped OTel gateway return HTTP 200. No
timestamp-named TDT project, volume, image, or network remains.

First-party container images and OCI metadata provenance:

- **Scheduler:** `tdt-scheduler:main-c6a0fd4`, image ID
  `sha256:5c958520c47bc56fd155519f15e3fc9c6efa3962561c8d665664f0a6ea71c35d`;
  OCI labels bind scheduler `c6a0fd452d85ef8e7c20730deaad63e387d7ebb2`,
  agent-core `3eaa7c842ef8ec7bbac8a6b74d4b187309c2b041`, and tdt-core
  `703d0af29d215298e55a301098fc44f2dcfe07bd`. Container is healthy with
  restart count 0 under Compose project `tdt-local-full-tdt-scheduler`;
  inherited image-level `com.docker.compose.project/service/version` values are empty.
- **Agent-core:** `agent-core:local-dev`, image ID
  `sha256:4d09fdc941d1bfec38c0327b053971777503ecd92b8d65079a26518fdf9f4069`;
  OCI labels bind agent-core `3eaa7c842ef8ec7bbac8a6b74d4b187309c2b041` and
  tdt-core `703d0af29d215298e55a301098fc44f2dcfe07bd`.
- **Shared process image:** `tdt-observability:local-20260825`, image ID
  `sha256:0a0456464e4deedcafd7c631bb5c9fec76015c714a8c933cfe406ea6559684bb`;
  OCI labels bind observability `edca8570e3498c8261ee6587d52ba83e104864a4` and
  tdt-core `703d0af29d215298e55a301098fc44f2dcfe07bd`. Both health-poller and
  log-collector use this same shared image ID, are healthy with restart count 0,
  and no floating latest first-party tags remain.
- **MLflow:** `tdt-observability-mlflow:v3.15.1` completes the set of four
  first-party image tags.

Canonical `tdt-core` path is `/Users/androidteam/orca/workspaces/tdt-core/tdt-main`
(with feature checkout notice remaining: `/Users/androidteam/Developer/tdt-core`
is preserved feature history at `3043854a006ddccd71270073409a7b94f058cd67` and
not deployment provenance). Canonical `tdt-observability` current identity is
`edca8570e3498c8261ee6587d52ba83e104864a4`. Run-owned replay pointers use the
stable projects/networks and current image tags. Host free space is now
approximately 53 GiB.

### Cumulative acceptance manifest

- Manifest:
  `/tmp/tdt-final-green-20260824t085909z/artifacts/tdt-compose/tdt-final-green-20260824t085909z/manifest.json`.
- SHA-256:
  `2637e44355ae8049ca31162c9002f7fc5cddb3526d13f5c6c7615659d0f352f0`.
- Closed-schema validation: passed against
  `deploy/evidence/tdt-compose-acceptance-v1.schema.json` at the accepted
  implementation revision.
- Manifest verdict: `success`.
- Finalization: `accepted`; zero unmet invariants.
- Retained lifecycle classes: `up`, `verify`, `runtime`, `manual-evidence`,
  and `diagnostics`.
- Read-only identities: 15 manifest inputs, including all scheduler sibling
  repositories/mobile content fingerprints and the distinct
  `tdt-observability` scheduler mount identity.
- Passing result checks: 9.
- Final deployment: intentionally left running; no final `down` was executed.

### Live functional acceptance

- Supported coordinator verification passed with all 15 long-lived owner
  services healthy after the failure-isolation and collector-restart tests.
- Exactly one matching record was retained for each of three unique traces in
  Tempo, Langfuse ClickHouse `events_core`, and MLflow PostgreSQL
  `trace_info`.
- Gateway sent-span counters were retained for LGTM, Langfuse, and MLflow.
- Langfuse-down isolation preserved Tempo and MLflow delivery, then recovered
  the queued Langfuse record.
- MLflow-down isolation preserved Tempo and Langfuse delivery, then recovered
  the queued MLflow record with one MLflow worker.
- MLflow artifact upload/list/download/digest round-trip passed.
- Scheduler backup checksum and `pg_restore --list` readability passed.
- Health-poller loaded the intended mixed host/Docker target configuration and
  retained fresh healthy observations for webhook-receiver, ai-review, and
  scheduler.
- A value-free supported log record was ingested exactly once; the run-owned
  log collector restarted healthy and did not duplicate it.
- All 16 scheduler `/workspace` content mounts were verified read-only. The
  separate `/home/agent/tdt` mount is intentionally writable owner state.
- PostgreSQL reported 18.6 and contained `agent_core`, `tdt_scheduler`,
  `tdt_scheduler_dbos_sys`, and `agent_harness`.
- Live task 8.3 used `agent_harness.checkpointing.create_async_checkpointer()`
  at agent-harness revision `35aedbd4...`; setup, write, readback, close/reopen,
  and second readback all passed for thread
  `tdt-final-green-20260824t085909z-task-8-3`. No DSN or credential value was
  retained.

Runtime ports remain loopback-only: Grafana `52208`, Prometheus `52209`, OTLP
gRPC `52210`, OTLP HTTP `52211`, Langfuse `52212`, MinIO console `52213`,
MLflow `52214`, agent-core PostgreSQL `52215`, and scheduler `52216`.

### Independent verification and archive readiness

Independent value-free report:
`/tmp/repair-tdt-observability-final-independent-verification.md`.

The independent review found no CRITICAL issue: 90/90 tasks were complete;
36 requirements and 99 scenarios were present across the eight delta specs;
the selected change, exact implementation identity, cumulative manifest,
live projects, scheduler mounts, host deployment provenance, and task-8.3
durability reconciled. Archive readiness validation returned `ready` with 90
completed tasks, zero remaining tasks, all required artifacts present, and
eight delta specs.

All eight delta capabilities were intelligently synchronized before the change
moved. Two main specs were created: `tdt-compose-operational-readiness` and
`tdt-observability-docker-deployment`. Six existing main specs received
scenario-preserving merges. Every delta requirement matched its synchronized
main requirement, both new specs matched after the main-spec header
transformation, all authoritative Purpose sections were preserved, and no
delta-operation headings remained. `openspec validate --specs --strict
--store openspec-store` passed 376/376 specs.

Supported archive command:

```text
openspec archive repair-tdt-observability-compose-deployment --yes --json --store openspec-store
```

Archive result:

- Archived as `2026-08-24-repair-tdt-observability-compose-deployment`.
- Archive path:
  `openspec/changes/archive/2026-08-24-repair-tdt-observability-compose-deployment`.
- CLI `specsUpdated=false` with zero added/modified/removed/renamed operations,
  proving the prior inline sync was already complete and idempotent.
- The final accepted Docker deployment remained running throughout sync and
  archive; no final `down` was executed.

### Retained warnings

- Store-wide strict validation currently reports 375 passed and 1 unrelated
  failed item: active change `repair-hermes-cron-run-reliability`. The selected
  TDT change passes; the unrelated change is outside this archive scope and
  must not be repaired or staged here.
- Docker Desktop was under severe external host load during cold starts.
  Fresh Langfuse initialization required datastore-first sequencing to avoid
  dirty migration state. Final backend restart counts are zero and the accepted
  lane remained healthy through the final evidence capture.
- Docker free space fell to approximately 9 GiB after repeated builds. The
  already-built accepted lane used an explicit finite 8 GiB verification floor;
  no global prune, volume deletion, or foreign-resource deletion was performed.
- Full observability pytest after the earlier MLflow one-worker change reached
  481 passed and 13 environment-only disk-budget fixture failures; focused
  Compose/MLflow tests passed 116/116 after the final MLflow health-budget
  change. This is not reported as a globally green full suite.
- The accepted implementation worktree contains preserved unrelated
  `AGENTS.md`, `CLAUDE.md`, and generated `graphify-out/` dirt. None belongs in
  the store archive commit.
- Stateful volumes, foreign Docker resources, unrelated branches/worktrees,
  and credentials remain preserved. Cleanup is a separate exact-allowlist
  action and must not stop the final accepted deployment.

Date: 2026-08-24 (current finalization pass)
Verdict: **success / implementation complete / archive workflow not started**

## Current finalization update (2026-08-24)

The earlier report sections below are historical snapshots. The current apply
state is 90/90 tasks complete and zero remain. Docker Desktop is currently stable
enough for fresh base, Langfuse, MLflow, and full profile acceptance. The
accepted observability owner is now commit `521de82156ae10d25238f86acf397c760fbe003a`; agent-core is
`3a2fe3b256fc920dc904eaea74d308f51af75aec`; scheduler is
`c0ef24bfde96eb909878d43c555b0270c24ad397`; the other read-only inputs retain
their exact SHAs in the run reports.

Fresh Docker Desktop evidence:

- Langfuse run: `/tmp/tdt-obs-mac-20260823t170031z-langfuse-3553r1`, final
  manifest success, six stateful volumes preserved.
- Full run: `/tmp/tdt-obs-mac-20260823t180410z-full-f14d`, final manifest
  success, eight stateful volumes preserved.
- Base resource run: `/tmp/tdt-obs-mac-20260823t184114z-base-af16`.
- MLflow resource run: `/tmp/tdt-obs-mac-20260823t184114z-mlflow-fbe1`.
- Full report: `/tmp/tdt-obs-mac-20260823t180410z-full-f14d/full-acceptance-evidence.md`.
- Scheduler owner report: `/tmp/tdt-sched-sup-6270360-daa3-evidence.md`;
  tasks 4.6 and 8.7 are eligible from exact HEAD `c0ef24bf…` with focused
  tests, clean image build, seven-workload integrity, health, telemetry, and
  backup inspection.
- First-party image report: `/tmp/tdt-task-d503684069e8-image-verification.md`;
  task 8.2 is eligible on arm64/non-root/import and clean amd64 buildx gates.
- Agent-harness static report:
  `/tmp/agent-harness-task-8.3-supervised-verification-20260824.md`; final live
  task-8.3 evidence is the isolated `tdt-checkpoint-8-3-20260824` owner run,
  which completed real checkpointer setup/readback and retained diagnostics.
- Current image report:
  `/Users/androidteam/Developer/tdt-observability/fresh-start-migration-cutover/deploy/evidence/image-provenance-9-8.md`;
  task 9.8 is complete at observability commit `521de821…`.
- Final exact-commit report: `/tmp/tdt-final-11-4-acceptance-report.md`; task
  11.4 is complete with successful base, Langfuse, MLflow, and full manifests
  at one exact owner matrix.

Completed in this finalization pass: every previously open task, including
8.3, 9.8, 10.1–10.10, 11.1, 11.2, 11.4, and 11.9. The implementation has no
remaining OpenSpec apply task. Archive remains a separate, explicit lifecycle
action and was not started.

This report records the current OpenSpec apply state for
`repair-tdt-observability-compose-deployment`. Structural validation, static
implementation, all Docker Desktop profiles, fresh PostgreSQL/checkpointer
setup, image provenance, failure isolation, fresh-start data disposition,
cleanup, and archive-readiness handoff are evidenced. Retained-data migration
and legacy rollback operations are recorded as not applicable under the
explicit no-old-data/no-compatibility decision.

## OpenSpec state

```text
openspec status --change repair-tdt-observability-compose-deployment --json --store openspec-store
schema: spec-driven
planning artifacts: complete

openspec instructions apply --change repair-tdt-observability-compose-deployment --json --store openspec-store
90/90 tasks complete; zero remain

openspec validate repair-tdt-observability-compose-deployment --strict --store openspec-store
valid

openspec validate --all --strict --store openspec-store
375 passed, 0 failed

openspec doctor --store openspec-store
root/store references healthy
```

The accepted owner is `521de82156ae10d25238f86acf397c760fbe003a`.
Its ancestor `59cfb4c` lowers the base health-poller memory reservation from
`384M` to `256M`, matching its `256M` limit. This was required
after the exact-commit follow-up reproduced Docker's fatal reservation-greater-
than-limit rejection. Final rendered profile reservation totals are base
`1920M`, Langfuse `4304M`, MLflow `2688M`, and full `4880M`; all four renders and
242 focused deployment/Compose tests pass after the fix.

The active change directory and the two corrected PostgreSQL Purpose specs are
committed store artifacts. The current uncommitted store state is unrelated
`repair-mcp-router-servers` work, untracked store worktrees, and preserved
generated review material; the unrelated pre-existing report
`openspec/reports/openspec-store-verification-2026-08-21.md` remains untouched.

## Accepted repository evidence

### agent-core

- Canonical integrated commit: `d390ae0e281a139906b8c56af5eb8d4c4ea3a0c6`.
- Owner report: `docs/repair-compose-verification.md` in the owner worktree.
- 94 focused tests, Ruff, format, strict mypy, lock validation, and two
  daemon-free Compose renders passed.
- Runtime image build, PostgreSQL bootstrap, gateway delivery, and rollback
  liveness remain blocked by Docker.

### tdt-scheduler

- Canonical integrated commits: `310bf87`, `d54faf5`, `b1bd8de`, `05e38a2`;
  owner branch source was verified at `48080954c983611fa8bca6f9ad830e2bc8afd103`.
- Owner report: `docs/tdt-scheduler-compose-repair-report.md` in the scheduler
  worktree.
- Seven focused tests, shell/Python checks, two daemon-free Compose renders, and
  diff checks passed.
- Docker build, health, hosted workload, backup runtime, and rollback gates are
  blocked; `tdt-sheets` and `ai-review` remain read-only inputs.

### agent-harness and tdt-core

- agent-harness already used `postgres:18.6-trixie`; 44 checkpoint/bootstrap
  tests passed and no source change was needed.
- Canonical `tdt-core/tests/test_paths_typed.py` covers the kind-first runtime
  path, explicit absolute root, and relative-root rejection contract;
  `PYTHONPATH=src uv run --project /Users/androidteam/Developer/tdt-core
  pytest tests/test_paths_typed.py -q` passed 25 tests under Python 3.14.5.

### tdt-observability integrated candidate

Dedicated integration worktree:
`/Users/androidteam/Developer/tdt-observability/tdt-observability-integrated`.
The canonical checkout was not overwritten because it contains user-owned dirty
Docker edits and nested worker worktrees.

Accepted candidate commits:

- `a59e12e` foundation Compose/Dockerfile candidate.
- `dde2663` four OTel gateway configurations.
- `a9b0ded` coordinator lifecycle/evidence contract.
- `212c596` integration correction: base gateway, literal network keys,
  canonical Dockerfile paths, versioned volumes, MLflow local artifacts, and the
  dedicated full-profile gateway override.
- `ffe6131`, `bafeef4` image-manifest evidence and official source links.
- `768ed69` static-gap follow-up: locked-venv/build-context regressions,
  exact inventory/mount/volume assertions, value-free environment corrections,
  and the bounded static-gap report.
- `f376b69` MinIO completion gate: `langfuse-web`/`langfuse-worker` now gate on
  `minio-init` via `service_completed_successfully`; the fixed sleep is replaced
  by a bounded 30-attempt retry that fails closed; MinIO credentials are
  injected via the service `environment:` block and referenced as `$$` shell
  variables; `otel-gateway` receives `LANGFUSE_PUBLIC_KEY`/`LANGFUSE_SECRET_KEY`
  with empty defaults so the Collector `${env:...}` providers resolve; misleading
  `LANGFUSE_INIT_*` implemented-claims corrected (task 6.4 key initialization
  remains unimplemented).
- `beaf62c` observability runtime defect repair: self-contained venv, explicit
  external `tdt-core` context selection, no-cache image build, and non-root
  service smoke.
- `3cc856e` observability entrypoint supervision evidence: same image digest for
  both services and non-zero child-failure propagation.
- `581e458f41b0b65462f78e83c25c455593809495` agent-core runtime report, sourced
  from `d390ae0e281a139906b8c56af5eb8d4c4ea3a0c6`: fresh/retained PostgreSQL,
  app imports, non-root health, four logical-database probes, and owner-only
  teardown were verified in that isolated historical runtime window. Current
  cross-project gateway delivery and fresh exact-matrix rerun remain blocked by
  Docker Desktop state.
- `dbc9938` scheduler external-worktree build/layout repair and runtime report.
- `56cc275` (2026-08-23) removed the broken `wget` healthcheck from the
  distroless `otel-gateway` service in both `docker-compose.yaml` (base,
  affects all 4 profiles) and `docker-compose.mlflow.yaml` (mlflow + full
  overlays). The `otel/opentelemetry-collector-contrib:0.159.0` image has no
  `/bin/sh`, `wget`, or `curl`, so the exec-based healthcheck could never
  succeed. Gateway readiness MUST be proven at runtime by an external probe of
  the Collector `health_check` extension on `0.0.0.0:13133`; the coordinator's
  bounded owner-health wait treats absent Docker health as passing, which is
  necessary but NOT sufficient. No service depends on `otel-gateway` via
  `service_healthy`. Post-fix evidence: 4/4 daemon-free Compose renders pass,
  89 model tests pass, 75 coordinator contract tests pass, `git diff --check`
  clean. GitNexus default `detect_changes`: no uncommitted tracked changes
  (untracked `graphify-out/graph.html` excluded). GitNexus `main...HEAD`
  compare: 35 files / 849 symbols / 29 processes / critical risk — expected
  branch-level impact for this broad candidate branch, not evidence that the
  two-file healthcheck fix itself is critical.
- `9f4c54e` (2026-08-23) adds the external gateway readiness contract. The
  coordinator runs a disposable pinned Alpine 3.20 probe on the run-scoped
  observability network and queries `http://otel-gateway:13133/` with bounded
  retries and explicit timeouts; readiness does not rely on Docker health
  status. `gateway_readiness` is recorded in the acceptance manifest with a
  closed JSON-schema contract and redacted structured evidence. The Alpine OCI
  index digest is `sha256:d9e853e87e55526f6b2917df91a2115c36dd7c696a35be12163d44e6e2a4b6bc`,
  with linux/amd64 and linux/arm64 manifests. Evidence: 79 deployment tests,
  deployment Ruff, owned test lint, schema parse, and four daemon-free Compose
  renders passed.

Static evidence:

- Four `docker compose --env-file deploy/tools.env ... config --quiet` profile
  renders passed without a daemon.
- `PYTHONPATH=src uv run --no-sync pytest tests/test_compose_models.py -q`:
  67 passed after `768ed69`; 87 passed after `f376b69` (20 new MinIO-gate and
  gateway-credential regressions).
- Fresh ad-hoc verification against `f376b69` (temporary `hermes-verify-*.py`
  script under the system temp dir, removed after use; this is ad-hoc
  verification, not canonical suite green): 26/26 checks passed — commit and
  worktree state, MinIO completion-gate and bounded-entrypoint assertions,
  `$$` escaping preservation, credential-via-environment, gateway key
  injection, the focused suites (87 + 178 passed), Ruff clean, four daemon-free
  Compose renders, and Docker daemon confirmed unavailable so runtime
  acceptance (tasks 8–10) remains blocked.
- `PYTHONPATH=src uv run --no-sync pytest tests/test_dockerfile_paths.py
  tests/test_otel_gateway_configs.py tests/deployment -q`: 178 passed after
  `768ed69`.
- `uv run --no-sync ruff check src/tdt_observability/deployment`: clean.
- Repository-wide test Ruff still reports pre-existing worker-test lint drift;
  strict mypy was unavailable in the newly created disposable environment.
- The observability runtime repair reports 101 focused tests before the final
  entrypoint follow-up; the follow-up reports 107 focused tests, Ruff/mypy
  clean, and both child-failure probes exiting 23.

### OTel gateway evidence recovery

Pi source commit: `cbe6a788914611d1e2a400dfa028d4162bde28c9`.
Coordinator-recovered report commit: `a4ca11b` at
`tdt-observability-backends/deploy/evidence/tdt-observability-gateway-static-gates.md`.
The four profile configs passed 73 focused tests, Ruff/format/mypy evidence, and
exact Collector `0.159.0` validation; the frozen legacy fixture was rejected by
the same validator. The original dispatch could not deliver `worker_done` after
repeated HTTP 504 responses, so the report is explicitly marked as coordinator
recovery and contains no gateway source changes.

## Image re-resolution

On 2026-08-22, `docker buildx imagetools inspect` and official registry tag APIs
confirmed the selected tags remain current pullable releases with amd64/arm64
manifests. Redis is deliberately pinned to the latest Alpine Redis 8 tag rather
than the Debian `redis:latest` alias.

| Image | Tag | Manifest digest |
|---|---|---|
| Python | `python:3.14.7-slim-trixie` | `sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4` |
| uv | `ghcr.io/astral-sh/uv:0.12.5` | `sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1` |
| PostgreSQL | `postgres:18.6-trixie` | `sha256:06cad38a5d9f5d24b4d83d86def30795d5e4b757fedbf5281172b576dedcd941` |
| Grafana LGTM | `grafana/otel-lgtm:0.31.0` | `sha256:f1e548c20c99d2678744be9d90955c0ab208ecc273db2a7a0b5dc5673d0b57fd` |
| OTel Collector | `otel/opentelemetry-collector-contrib:0.159.0` | `sha256:1f2c54a30e713fac6b3ae77a1ec84010c2007e29ced8ec666214fc2f6739c1cc` |
| Langfuse web | `langfuse/langfuse:4.16.0` | `sha256:e8459747001aa0da1bdecdc5d46c48d37c2e9b4c2c99743b27efeb2872e0583` |
| Langfuse worker | `langfuse/langfuse-worker:4.16.0` | `sha256:b4490170d5bc18e873f7ca7c3edad5af16022156487a5c47c328d571a9063dc1` |
| Redis | `redis:8.10.1-alpine` | `sha256:becdda6c7f4b3fb42e42fd7f120bbf5c54c4caaaf16f26da24e4563d2c1f0576` |
| ClickHouse | `clickhouse/clickhouse-server:26.7.5.10-alpine` | `sha256:0a45b864c73322d4360dea1973ee9b77f29c51af1242ad2d47409908071fa56e` |
| MinIO | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e` |
| MinIO Client | `minio/mc:RELEASE.2025-08-13T08-35-41Z` | `sha256:a7fe349ef4bd8521fb8497f55c6042871b2ae640607cf99d9bede5e9bdf11727` |
| MLflow | `ghcr.io/mlflow/mlflow:v3.15.1` | `sha256:ea84a0b879f08b35a6f22f22b294024413e780b8fc978eecf5f760ac16cc9ce5` |

## Historical blockers and open worker evidence

The earlier Docker-socket blocker is historical. The current `desktop-linux`
Docker Desktop session supported the fresh profile evidence recorded in the
current-finalization section. Independent image-build/amd64 compatibility,
scheduler workload, migration/cutover, and final exact-commit sequence gates
remain open.

Agy’s preflight report is now present at
`openspec/reports/repair-tdt-observability-compose-deployment-preflight.md` and
tasks 1.1–1.6 have been reconciled. The canonical observability checkout still
contains unrelated dirty Docker edits and generated Graphify/worktree state;
these were preserved. No credentials, Docker resources, host volumes, launchd
services, or unrelated reports were changed.

## Docker Desktop diagnosis

Read-only Docker CLI, socket, process, launchd, recent-log, Orca UI, and
daemon-free Compose checks were completed in candidate commit
`1eaa3a09a6401130bc44e8eb995bfa063916bb21`. The diagnostic evidence is retained
on the `docker-desktop-diagnostics` branch (HEAD `2b5de12`) in the
tdt-observability repository:

- `git show docker-desktop-diagnostics:deploy/evidence/docker-desktop-diagnostics.md`
- `git show docker-desktop-diagnostics:deploy/evidence/docker-desktop-runtime-flap.md`

The selected `desktop-linux` context is coherent, Docker CLI 29.7.2 and Compose
5.4.0 are installed, and all Compose configuration merges return exit 0.

### 2026-08-23 flap follow-up

The operator started Docker Desktop multiple times. Each session lasted
approximately 4–5 minutes before an orderly terminated-signal shutdown. The
latest bounded snapshot (2026-08-23T03:30+07:00) shows:

- Docker daemon unavailable: socket absent, no Docker Desktop or backend
  processes running.
- Backend log: `engine linux/virtualization-framework shutdown requested
  (cancel cause: terminated signal received)` followed by `starting graceful
  shutdown` and `init POST /shutdown`.
- Electron log: `AbortError: Request aborted` in `createWindowManager`
  immediately preceding each backend shutdown.
- No OOM, fatal, or dockerd-crash markers found.
- The initiating component remains undetermined; neither daemon crash nor OOM
  is supported by the evidence.

Settings changes attempted during this session (autoPauseTimeoutSeconds,
UseResourceSaver, AllowBetaFeatures, AllowExperimentalFeatures) were all
restored to their original values. These raw-JSON edits are an unsupported
approach — Docker Desktop may ignore or overwrite them — and the flap persisted
identically across every combination tried, so they did not remediate the issue.
No persistent Docker Desktop remediation was retained. The flap root cause
remains unresolved.

**Runtime acceptance (tasks 8–10) remains blocked until Docker Desktop
maintains a stable session beyond the observed ~5-minute window.**

## 2026-08-23 coordinated worker wave

The bounded follow-up worker wave produced these additional, independently
verified results without changing OpenSpec task checkboxes:

- `tdt-observability`: isolated source commit
  `4a1d25ff3861455094ada0535224e0fb9b033eb8` is preserved on branch
  `obs-compose-correction`. It removes the root Compose `name:` override and
  adds 11 focused project-name/Collector-readiness tests; uv tests, Ruff,
  mypy, daemon-free profile renders, Graphify update, and low-risk GitNexus
  detection passed. The durable report is
  `openspec/reports/tdt-observability-compose-correction.md`. This narrow
  canonical-root slice intentionally retains its existing Redis
  `8.10.0-alpine`; the integrated candidate's approved latest inventory remains
  Redis `8.10.1-alpine` at `56cc275`, so latest-image promotion is still not
  complete for the canonical root.
- `tdt-scheduler`: source commit
  `54203800f29ab594223ea6546b0d8b870194f348` is preserved on branch
  `scheduler-pydantic-import`. Its Dockerfile now constrains
  `pydantic>=2.13.4,<2.14` and `pydantic-settings>=2.14.1,<2.15` after the
  `code_daily_scan.cli` serializer import failure; the seven-workload
  integrity gate and owner layout remain intact. Docker build/runtime evidence
  remains unavailable.
- `webhook-receiver`: source commit
  `f3f904ded6d14108227cb198967e3b85963be685` adds side-effect-free circuit
  breaker and session health snapshots with two focused tests. The launchd
  label `com.tdt.webhook-receiver` is running from the canonical
  `$HOME/.tdt/deployments/webhook-receiver` root, listens only on
  `127.0.0.1:8080`, and `/health` returned HTTP 200 healthy with ai-review
  reachable. Evidence is retained at
  `$HOME/.tdt/deployments/webhook-receiver/state/deployment-report.md`;
  pre-existing uv.lock/Graphify dirt remains uncommitted. The deployment
  report captured the pre-commit source identity `baa49981`; the current source
  commit is `f3f904ded6d14108227cb198967e3b85963be685`, so an exact-commit
  provenance acceptance run must redeploy this service after the source commit.
- `ai-review`: the launchd label `com.tdt.ai-review` is running on
  `127.0.0.1:8090` from the repository-documented
  `$HOME/Developer/tdt/deployments/ai-review` root. `/health/full` returned
  `status=degraded` because optional OmniRoute/Kimi providers are unavailable;
  the deployment manifest is retained at
  `$HOME/Developer/tdt/deployments/ai-review/state/deployment-manifest.json`.
  The deploy script also generated a broad TDT dependency workspace and
  unrelated lockfile dirt; those paths are preserved and are not treated as
  change-owned commits.

The temporary Orca worktrees were removed after preserving their source
commits/reports. No Docker resources, stateful volumes, unrelated launchd
labels, or unrelated OpenSpec reports were removed.

The current authoritative Docker settings store still reports
`UseResourceSaver=false`, `AutoPauseTimeoutSeconds=300`, and
`AutoPauseTimedActivitySeconds=30`, but the Docker socket remains absent and
`docker info` cannot connect. This is a current runtime blocker, not proof that
the Compose models or image inventory are invalid.

## 2026-08-23 static-readiness and Docker-diagnosis follow-up

The integrated candidate static readiness work is preserved on branch
`observability-static-readiness` through commits
`bef9a34f97129be252e1b8d3833fefb3ebf798ca`,
`c48a62f104b685d2bfb0f488d0bc47761c1bcbb5`, and
`f42b4c5d1872e792533acbe483a338f84b51ff2b`. The latest static slice adds
atomic poller/config-cycle readiness, idle-safe collector scan/flush heartbeats,
offset/inode rotation handling, explicit executable `/entrypoint.sh
--readiness` healthchecks, the supported `LANGFUSE_INIT_*` bootstrap/preflight
contract, Redis 8.10.1 documentation, and focused regressions. The worker
reported 224 focused tests, four daemon-free Compose renders, Ruff, and clean
diff checks; Docker image/runtime, authenticated Langfuse trace, and lock/mypy
environment gaps remain open. Generated Graphify output is intentionally
unstaged.

The scheduler static hardening was integrated into canonical `tdt-scheduler` as
`cb1746e0e6f3a54ab057e96a7db76b389912f746` from the integration-clean source
commit `d52375519e8bb1579aded35ec23f1392e39445d6`. It hardens bounded,
redacted PostgreSQL readiness before DBOS initialization and preserves the
Pydantic pin repair; static tests, nine lock checks, Compose renders, syntax,
and diff checks passed. Docker image build stopped during dependency download
with BuildKit `Unavailable/EOF`; live scheduler health/workload/backup remain
blocked.

The ai-review source health correction is canonical at
`706a46e21cbcf0b8ddf9caadd3ba9518532b00e5`; focused health tests and Ruff pass.
Disabled optional reviewers now report `not needed` and healthy, while enabled
but failing providers remain degraded through shared CLI/HTTP classification.
The launchd service still runs the old deployment source `033de308` because the
documented deploy script defaults to the separate `$HOME/Developer/tdt/ai-review`
checkout; exact post-commit redeploy remains blocked by that workspace-root
containment/provenance mismatch.

Docker Desktop recovered twice after transient Virtualization.framework storage
attachment failures and supplied the official diagnostic bundle
`/var/folders/zw/k5ybx0c55rs88r9d09kxly8w0000gp/T/6501AB09-CA89-4DF7-ADE9-9E13CCBC244B/20260823015935.zip`.
The Docker.raw sparse disk was inspected as structurally intact; no prune,
reset, volume deletion, or resource cleanup was performed. A live inventory
captured four existing integrated observability containers, 23 images, 8 CPUs,
and 16 GiB configured memory. Those containers auto-restarted from the stale
integrated Compose file and still carry the invalid `wget` gateway healthcheck
(`tdt-observability-otel-gateway-1`), so they are evidence of a previously
started stack, not acceptance of the corrected readiness contract. Do not
restart or remove them until the corrected candidate project identity,
healthcheck, and exact resource ownership are reviewed.

Official Docker documentation confirms `docker desktop diagnose` is the
supported CLI diagnostic path and warns that Docker.raw backup does not replace
separate named-volume backups; the documented macOS Docker.raw path is
`$HOME/Library/Containers/com.docker.docker/Data/vms/0/data/Docker.raw`.

The latest static/readiness commits are now reconciled as follows:

- tdt-observability integrated candidate: `120d769c32b79b4f2e66835a068b897da1c56d69`
  plus readiness-command/flush-error follow-up `8a9e73fe1095b517096a0e559ac97567586f6210`
  and evidence clarification `f42b4c5d1872e792533acbe483a338f84b51ff2b`. Static
  tests, Ruff, four renders, and diff checks pass; the integrated project-name
  correction and authoritative image-fallback/owner-startup wiring remain in
  the dependent coordinator task.
- tdt-scheduler canonical commit: `cb1746e0e6f3a54ab057e96a7db76b389912f746`,
  reproduced from allowlisted integration commit `d52375519e8bb1579aded35ec23f1392e39445d6`.
  This commit contains bounded redacted database readiness, DBOS ordering
  tests, Pydantic pins, scheduler documentation, and no Graphify paths. The
  Docker image build still failed with BuildKit `Unavailable/EOF` while Docker
  Desktop flapped.
- ai-review canonical commits: `bbceaa2`, `706a46e21cbcf0b8ddf9caadd3ba9518532b00e5`.
  Focused health tests pass and optional-provider semantics are now honest, but
  the launchd runtime still reflects old source `033de308`; exact post-commit
  redeploy remains blocked because the deployment script defaults to the
  separate `$HOME/Developer/tdt/ai-review` checkout.

The current live Docker inventory, when the engine briefly recovered, contained
four existing `tdt-observability` containers from the integrated candidate:
`otel-gateway`, `otel-lgtm`, `health-poller`, and `log-collector`; 23 images,
8 CPUs, and approximately 16 GiB configured memory. The gateway container was
still using the stale `wget` healthcheck from the old running Compose model,
while the corrected source contract now uses an explicit `/entrypoint.sh
--readiness` command for first-party daemons and an external probe for the
distroless gateway. This inventory is preserved evidence only; no container,
network, image, or volume was removed or restarted by the coordinator.

## Disposition

Keep the active change open at `51/90` (`39` remain). The candidate observability commits are
ready for a controlled canonical integration once the dirty checkout owner
authorizes conflict reconciliation. Do not archive or claim global success until
Docker Desktop is available, the runtime gates are recaptured against the same
commit matrix, the Agy preflight/matrix evidence is recovered, and task 11.8
reviews and commits only the approved store paths.

## 2026-08-23 post-restart static coordinator candidate

The preserved coordinator worktree
`/Users/androidteam/Developer/tdt-observability/observability-coordinator-readiness`
produced and independently rechecked the following owner commits:

- `bda825ba66ac3cc618cfc81f3234226ec41d5350` — fail-closed coordinator
  evidence, required image/credential interpolation, real Git dirt and
  read-only input file identities, scoped Compose commands, owner-project
  rendering, and manifest roots/resources/images/networks.
- `c5ef814a32970e8ceeabd651e77d39f22c89c651` — reject pre-existing runtime or
  observability networks whose Docker labels do not match the current owner and
  project.
- `456592f226ae09156f55b5c0473c7aa2f5347fda` — cleanup of changed-test Ruff
  diagnostics and import/style drift.

These commits were cherry-picked into the isolated integration candidate
`/Users/androidteam/Developer/tdt-observability/tdt-observability-integrated`,
whose current HEAD is `a3188df7c038472ec2484d7a753c36b98474b964`. The candidate
has exactly the expected source, Compose, and test commits plus preserved
unstaged Graphify output; no Graphify path was staged by the coordinator.

Fresh daemon-free verification against the integrated candidate:

```text
PYTHONPATH=src uv run --no-project pytest \
  tests/deployment/test_coordinator_evidence_contract.py \
  tests/test_compose_models.py -q
203 passed in 6.97s

PYTHONPATH=src uv run --no-project ruff check \
  src/tdt_observability/deployment/__main__.py \
  src/tdt_observability/deployment/evidence.py \
  src/tdt_observability/deployment/stack.py \
  tests/deployment/test_coordinator_evidence_contract.py \
  tests/test_compose_models.py
All checks passed

python3 -m compileall -q src
exit 0

env TDT_OBSERVABILITY_NETWORK=tdt-observability-static-verify \
  TDT_CORE_CONTEXT=/Users/androidteam/Developer/tdt-core \
  TDT_HOST_HOME=/Users/androidteam/.tdt \
  GRAFANA_ADMIN_USER=<redacted-test-user> \
  GRAFANA_ADMIN_PASSWORD=<redacted-test-password> \
  docker compose --env-file deploy/tools.env \
  -f deploy/docker-compose.yaml config --quiet
base_render_exit=0
```

After the report/task reconciliation, the selected change validated strictly,
the full store validated at `375 passed, 0 failed`, and `openspec doctor` reported
healthy root/store references. These are structural OpenSpec gates only and do
not promote the active implementation to runtime readiness.

The full profile render also passed in the worker’s explicit-scope verification;
its output contained no secret values. This is structural/static evidence only.
It does not satisfy p95/p99 resource measurement, Docker host-gateway HTTP
reachability, owner-project startup, rerun/partial-start recovery, image pull or
build, backend migration, authenticated Langfuse trace, duplicate-detection,
rollback, cleanup, or post-commit host-service provenance.

Current Docker recheck after the restart is `blocked`: `docker context show`
returns `desktop-linux`, but `$HOME/.docker/run/docker.sock` is absent,
`docker info`, `docker ps`, network/volume/image inventory calls fail with
daemon `ENOENT`, `docker desktop status` reports that Docker Desktop is not
running, no Docker backend process is present, and
`launchctl print gui/502/com.docker.helper` reports `state = not running`.
The prior stale `wget` gateway-healthcheck observation remains historical and
cannot be recaptured while the daemon is down. No Docker resource, network,
volume, image, launchd service, or credential was mutated.

The post-restart host-service read-only review also remains blocked for exact
post-commit provenance: webhook-receiver owner HEAD is
`f3f904ded6d14108227cb198967e3b85963be685` but its retained deployment report
records pre-commit `baa49981`; ai-review owner HEAD is
`706a46e21cbcf0b8ddf9caadd3ba9518532b00e5` while launchd still resolves the
separate legacy source tree at `033de308` and port `8090` has no listener (launchd
exit `126`). No redeploy was authorized or performed.

The active change therefore remains `50/90` with `40` open tasks and a
`partial / blocked` verdict. The static coordinator commit is not a runtime
acceptance or archive-readiness claim. Preserve the unrelated active
`repair-mcp-router-servers` state, untracked store worktrees, and Graphify dirt.

## 2026-08-23 alternative-runtime investigation and final disposition

The Docker Desktop failure was not remediated locally. Docker Desktop 4.87.0
on macOS 26.6.2 repeatedly terminated its backend within approximately 1–5
minutes; earlier sessions captured the AppKit `NSEvent.m:2132` /
`Unrecognized event type 0` exception. Docker Desktop was stopped with the
official CLI after the final comparison and no Docker Desktop resource was
removed.

The following independent runtime paths were tested without deleting the
existing Colima disks or Docker Desktop data:

- **Colima 0.10.3 / Lima 2.2.0, VZ:** the guest VM and `dockerd` stayed alive,
  but the host Docker Unix-socket and guest-agent forwarding disappeared
  during the 15-minute gate. A socket-only repair restored `_ping` temporarily;
  the subsequent deterministic T+5/T+10/T+15 soak failed at T+15.
- **Colima 0.10.3 / Lima 2.2.0, QEMU:** an independent QEMU profile started,
  built the base stack, and initially passed the engine/socket/gateway gates.
  Its deterministic soak failed at T+5. The QEMU hostagent log records
  `guest agent events closed unexpectedly`, repeated failure to re-establish
  `ga.sock`, and `exit status 255` while the QEMU VM and guest `dockerd`
  remained alive.
- **OrbStack 2.2.3:** the Docker context and base stack started successfully.
  One explicit-context T+5/T+10/T+15 run passed with four containers, zero
  restarts, and the external gateway probe passing. Host Grafana forwarding was
  initially absent while `setup.use_admin=false`. After restoring the official
  default `setup.use_admin=true`, Grafana returned HTTP 200, but the latest
  explicit-context soak failed at T+5 with the OrbStack service stopped. This
  latest result supersedes the earlier passing run; OrbStack is not accepted as
  a stable runtime.

Upstream evidence matches the Colima/Lima failure class:

- Lima issue #2227: <https://github.com/lima-vm/lima/issues/2227>
- Colima issue #994: <https://github.com/abiosoft/colima/issues/994>
- Docker Desktop issue #441: <https://github.com/docker/desktop-feedback/issues/441>

Final host state after the bounded investigation:

```text
Docker Desktop: stopped; desktop-linux socket unavailable
Colima VZ: stopped
Colima QEMU: stopped
OrbStack: stopped after latest failed T+5 gate
Docker context: orbstack
OrbStack config: memory_mib=4096, k8s.enable=false, setup.use_admin=true,
                 app.start_at_login=false
Docker Desktop settings-store.json: AutoStart=false
Docker Desktop settings.json: absent at final snapshot
```

The corrected base Compose stack and external gateway readiness contract were
proven under the alternative runtimes in bounded windows, but no runtime path
passed the final currentness gate. Runtime acceptance, rollback, hosted-workload,
full-profile, and archive tasks remain unchecked. No task checkbox, active-change
ledger, credential, stateful volume, unrelated report, or unrelated worktree was
modified by this investigation. Temporary runtime environment files and soak
scripts were removed.

## 2026-08-23 Colima and host-provenance continuation

The selected Docker context changed from the unavailable Docker Desktop engine
to the separate `colima-tdt-observability` profile. This is a distinct runtime
identity: Docker `29.5.2`, `linux/arm64`, four CPUs, and 6 GiB configured memory.
The pre-existing `tdt-obs-colima-base` project was classified as
`existing / foreign stable runtime — preserve`; its four containers, network
`tdt-obs-colima`, volume `tdt-obs-colima-base_lgtm-data`, and host state binds
were never selected as run-owned or removed.

Read-only base measurement retained 30 complete samples over 60.641 seconds:

| Evidence | p95 | p99 |
| --- | ---: | ---: |
| Aggregate CPU | 0.317 cores | 0.849 cores |
| Aggregate memory | 1583.8 MiB | 1588.0 MiB |

Base p99 plus 20% is 1.018 cores and 1905.64 MiB, within the Colima capacity.
The measurement is base-only; optional-profile and load evidence remain open.
Reports:

- `/tmp/tdt-obs-colima-base-runtime-audit-task_4ed7887ce066.md`
- `/tmp/tdt-obs-colima-base-measurement-20260823.md`
- `/tmp/tdt-obs-colima-base-runtime-acceptance-task_4ed7887ce066.md`
- `/tmp/tdt-obs-colima-run-b3dffbd/runtime-acceptance-report.md`
- `/tmp/tdt-obs-colima-base-runtime-retry-888fe24.md`

Runtime exploration exposed and corrected two coordinator defects without
claiming runtime acceptance:

- integrated `b3dffbd5557ff52c4cf871ba5c746218cfb74e84` probes mandatory
  webhook `http://host.docker.internal:8080/health`, treats ai-review
  `:8090/health/full` as optional/degraded, rejects implicit port 80 and
  credential-bearing URLs, and preserves the pinned Alpine DNS/HTTP probe;
- integrated `888fe24efb348bab9b757d1948406776648a5979` derives profile ports
  from explicit CLI values, then the selected env file, then loopback defaults;
  it rejects public/malformed/duplicate ports and reuses the exact snapshot for
  preflight, Compose, and evidence.
- integrated `88146f31a59679844baff8dfb51fc9ea0a3b8c5d` makes the copied
  Grafana credential example fail closed and updates the final stale
  `TDT_CORE_CONTEXT` fallback assertion; the complete static suite reports
  `466 passed`, Ruff/compile/lock gates pass, and all four daemon-free renders
  remain green.

The first collision-free run stopped before mutation on the now-fixed default
port check. The next exact-`888fe24` run was interrupted when a concurrent
process from the integrated deployment worktree ran
`colima -p tdt-observability stop` / `systemctl stop docker.service`.
At handoff the target profile/context was stopped, only the unrelated QEMU
profile remained running, and no new run-owned project, network, volume,
container, image, owner record, or manifest existed. Runtime tasks remain open.

### Exact host-service post-commit provenance

Ai-review deployment-contract and lock commits are canonical at
`c35ee68e520d4eccf25cf712802d8b3dbc4fb649`. The deployment used a separately
authorized clean external source, passed 231-package lock verification, wrote
`/Users/androidteam/Developer/tdt/deployments/ai-review/state/deployment-manifest.json`,
and now runs one listener on `127.0.0.1:8090`; `/health` returns `status=ok` and
the manifest records source `c35ee68e520d4eccf25cf712802d8b3dbc4fb649`.

Webhook-receiver deployment/source/lock/runtime-fix commits are canonical at
`3a0d800d8be541edfad0057544a9cc475b597f8d`. The deploy contract explicitly
authorizes only a clean exact Git source and the canonical external root
`/Users/androidteam/.tdt/deployments/webhook-receiver`. Two retained source
defects were repaired during the bounded rollout: optional missing Jira-guard
imports now fail isolated, and the launcher uses
`webhook_receiver.api.app:create_app --factory` while preserving host-native
optional-feature health defaults. The final deployment passed 130-package lock
verification, health after nine seconds, unique listener/provenance checks, and
wrote the deployment manifest. It now runs one listener on `127.0.0.1:8080`;
`/health` returns `healthy`, reports ai-review reachable with HTTP 200, and the
manifest records clean source `3a0d800d8be541edfad0057544a9cc475b597f8d`,
`source_authorization=canonical_external`, and
`deployment_root_authorization=canonical_external`.

This completes the exact owner-staging and host-redeploy evidence for task
11.3. Tasks 11.1, 11.2, 11.4, 11.9, all profile-runtime tasks, and all
migration/retirement tasks remain open. The verdict remains `partial / blocked`.

Closing runtime snapshot: both Colima profiles (`tdt-observability` and
`tdt-observability-qemu`) report `Stopped`. The selected Docker context changed
concurrently to `orbstack`, whose configured socket
`$HOME/.orbstack/run/docker.sock` is absent and `docker version` cannot reach an
engine. This context/profile churn occurred after the bounded Colima evidence
windows and is not attributed to the candidate source. No further runtime retry
or cleanup is authorized until one owning lane selects and stabilizes a single
engine identity.

## 2026-08-23 final runtime lane reconciliation

A later, context-pinned OrbStack lane was run after the concurrent Colima
closure. OrbStack 2.2.3 was configured with `memory_mib=4096`,
`k8s.enable=false`, and `setup.use_admin=true`; Docker Desktop was explicitly
stopped before the final comparison and its `settings-store.json` reported
`AutoStart=false` (the secondary `settings.json` file was absent).

The explicit OrbStack soak from `16:07:45` through `16:22:47` passed T+5, T+10,
and T+15 with Docker 29.4.0, four base containers, zero restart counts, the
external Alpine gateway probe passing, and `orbctl=Running`. A later run after
restoring host-port administration failed at T+5: `orbctl` reported `Stopped`
and the explicit OrbStack Docker socket disappeared, even after Docker Desktop
had been stopped. The later result supersedes the earlier pass for currentness.

The final state is therefore **runtime blocked**: Docker Desktop, Colima VZ,
Colima QEMU, and OrbStack were all stopped after their bounded experiments.
The base Compose model and gateway readiness contract have valid bounded
runtime evidence, but no currently stable engine passed the latest gate. No
runtime, rollback, hosted workload, optional profile, migration, or archive task
was checked by this lane. Temporary OrbStack/Colima environment files and
monitor scripts were removed; no credentials, volumes, images, networks,
source worktrees, or unrelated OpenSpec artifacts were deleted.

## 2026-08-23 local Linux-over-SSH runtime resolution

The user selected localhost as the remote-engine target. The selected runtime is
a local Linux guest, not the macOS Docker socket: a fresh Colima QEMU profile
`tdt-observability-qemu-9p` with `mount_type=9p`, 4 CPUs, 6 GiB memory, and a
100 GiB disk. Docker is reached through the persistent context
`local-qemu-9p-ssh` (`ssh://colima-tdt-observability-qemu-9p`), bypassing Lima's
unstable host Unix-socket and guest-agent forwarding path.

The first SSH-context trial exposed a separate file-sharing defect: the old
reverse-SSHFS profile lost `/Users/androidteam`, and the containers then saw an
empty root-owned bind source. The fresh 9p profile mapped the macOS home with
UID 502, while the application runs as UID 1000. Runtime state was therefore
moved to guest-native `/var/lib/tdt/{state,logs,deployments}` owned by UID 1000
through the temporary deployment env only; no host ownership or source Compose
file was changed. The log collector and health poller then started healthy with
zero restarts.

The final explicit SSH-context soak ran from `17:17:40` to `17:32:42` and
passed all three checkpoints:

- T+5 `17:22:40`: Docker 29.5.2 / Ubuntu 24.04.4 LTS, four containers healthy,
  all restart counts `0`, gateway probe `PASS`, Grafana `200`;
- T+10 `17:27:40`: the same healthy state, all restart counts `0`, gateway
  probe `PASS`, Grafana `200`;
- T+15 `17:32:40`: the same healthy state, all restart counts `0`, gateway
  probe `PASS`, Grafana `200`;
- soak process exited `0` with `result=PASS` at `17:32:42`.

Because the SSH TCP session can be closed by Lima independently of the Docker
SSH context, host ports 3000 and 9009 are maintained by a reconnect watchdog.
The durable files are:

- `~/Library/LaunchAgents/com.tdt-observability.qemu9p.plist` — starts the
  QEMU-9p profile at login with an explicit Homebrew PATH;
- `~/Library/LaunchAgents/com.tdt-observability.qemu9p-ports.plist` — keeps the
  reconnecting port-forward watchdog alive;
- `~/Library/Application Support/tdt-observability/qemu9p-port-forward-watchdog.sh`
  — direct SSH forwards for Grafana and OTLP.

Both plists passed `plutil -lint`; `launchctl list` reports the Colima start
job with exit `0` and the ports watchdog loaded with a live PID. The selected
Docker context is `local-qemu-9p-ssh`, Docker Desktop is stopped, the old VZ,
old QEMU, and OrbStack profiles are stopped, and the QEMU-9p stack is running.
This supersedes the earlier runtime-blocked disposition for the selected base
profile, but optional profiles, rollback, hosted-workload, migration, and
archive gates remain open and unchecked.

## 2026-08-23 owner-service acceptance continuation

The QEMU-9p SSH Docker context was extended with the committed canonical owner
Compose trees without modifying their source files:

- agent-core source HEAD `d390ae0e281a139906b8c56af5eb8d4c4ea3a0c6`;
- tdt-scheduler source HEAD `cb1746e0e6f3a54ab057e96a7db76b389912f746`;
- tdt-observability source HEAD `88146f31a59679844baff8dfb51fc9ea0a3b8c5d`.

Both owner models rendered cleanly with run-scoped runtime network
`tdt-runtime-qemu9p` and observability network `tdt-obs-qemu9p`. Agent-core's
image built successfully with Python 3.14.7/uv 0.12.5 and the explicit tdt-core
context. Scheduler's image built successfully and its build-time dependency
integrity gate verified seven workloads.

Agent-core owner acceptance evidence:

- `postgres:18.6-trixie` reported PostgreSQL `18.6 (Debian 18.6-1.pgdg13+2)`;
- `agent_core`, `agent_harness`, `tdt_scheduler`, and
  `tdt_scheduler_dbos_sys` were present;
- the app container ran as UID/GID `1000:1000`, imported `agent_core`, and
  emitted `AGENT_CORE_IMPORT_OK`;
- PostgreSQL and app restart counts were both `0`.

Scheduler owner acceptance evidence:

- PostgreSQL readiness passed on the stable `postgres` runtime-network alias;
- DBOS application/system migrations completed, DBOS launched, three schedule
  manifests loaded, and 19 schedules were applied;
- `/scheduler/health` returned HTTP `200`, the container became healthy, and its
  restart count was `0`;
- the runtime used a temporary `UV_NO_SYNC=1` Compose override so the verified
  image venv was not replaced by an automatic sync against host-mounted source;
  this was a runtime-only override and no committed entrypoint was changed.

The scheduler `postgres-backup` initializer exited `0` and wrote a custom dump,
TOC, and SHA-256 file under guest-native `/var/lib/tdt/backups`. A separate
`pg_restore --list` probe exited `0` and reported PostgreSQL dump version 18.6,
custom format, and nine TOC entries. This proves the backup/readability portion
of task 8.7; its hosted workload and full dependency-matrix portions remain
open.

Health/readiness evidence:

- health-poller persisted `config_loaded=true`, a fresh cycle timestamp, and
  `target_statuses` of `webhook-receiver=healthy`, `ai-review=healthy`, and
  `tdt-scheduler=healthy`; its container health and restart count were healthy/0;
- the live config retained `host.docker.internal` for host-native webhook and
  ai-review plus Docker DNS `scheduler:9100`;
- log-collector readiness reported `watched_files=2` and no flush error;
- task 8.6 is checked with sentinel
  `qemu9p-log-test-ff44ae2f4c7e4d6cbc0af3e05a4fdcb6`, one normalized DuckDB event,
  and count `[(1,)]` after a second collector restart.

Remaining runtime gates include trace/metric/log delivery into LGTM (8.4), the
full mixed-health/degraded-outcome matrix (8.5), the hosted workload and full
scheduler handoff in 8.7, owned diagnostics/teardown (8.8), all optional
Langfuse/MLflow/full profiles, cutover/migration, and final archive readiness.

### Final consolidated live snapshot

At the closure read, Docker context `local-qemu-9p-ssh` reported Docker 29.5.2
on Ubuntu 24.04.4 LTS with eight containers. The four observability services,
agent-core PostgreSQL/app, and scheduler were healthy/running with restart count
`0`; the scheduler backup container was `Exited (0)`. The external gateway
probe exited `0`, Grafana returned HTTP `200`, scheduler health returned HTTP
`200`, both QEMU-9p LaunchAgents were loaded (`qemu9p` exit `0`, ports watchdog
PID live), and the report/task diff passed `git diff --check`. Docker Desktop
remained stopped. No optional profile or archive claim is implied by this
snapshot.

## 2026-08-23 Docker Desktop for Mac finalization pass

This section is the current disposition and supersedes earlier runtime-lane
sections where their engine identity, task count, or verdict differs. The
authoritative current runtime was Docker Desktop for Mac, context
`desktop-linux`, Docker Server `29.7.2`, arm64, 8 CPUs, 5920 MiB reported, and
`overlay2`. Docker Desktop was available throughout the accepted base and
MLflow runs.

### Owner fixes and commits

- `tdt-scheduler` commit
  `c0ef24bfde96eb909878d43c555b0270c24ad397` adds the default
  `UV_NO_SYNC=1` runtime contract so host-mounted source cannot replace the
  locked image venv; explicit `UV_NO_SYNC=0` remains available for intentional
  development syncs.
- `tdt-observability` integrated candidate commit
  `47f2dedfdb2b19625fe6e34b792189af72a29e8e` extends the owner-health wait to a
  bounded 120-second window, allows `verify` to reuse ports only when the
  matching run-owned Compose project is live, and adds the MLflow derived image
  layer from exact `ghcr.io/mlflow/mlflow:v3.15.1` with pinned
  `psycopg2-binary==2.9.10`.
- Graphify output was refreshed in both repositories and remains unstaged.
  Scheduler Graphify rebuilt 830 nodes/931 edges; observability rebuilt 1764
  nodes/3047 edges and reported three zero-node JSON fixtures for future retry.
- Repository-scoped GitNexus staged detection was unavailable because the MCP
  service was disconnected. Direct staged name/status inventories, focused
  tests, diff checks, and final dirty-state inspections were used as fallback;
  no GitNexus pass is claimed.

### Current accepted runtime evidence

- Base run `tdt-obs-mac-20260823t142246zr4` passed coordinator `up`, coordinator
  `verify`, gateway readiness, Grafana HTTP 200, fresh PostgreSQL 18.6 and all
  four logical database probes, agent-core import, scheduler DBOS health, 19
  applied schedules, readable PostgreSQL backup/checksum, current health-poller
  readiness, and log-collector restart-safe single-event ingestion.
- The same base run sent one unique trace, metric, and log through
  `otel-gateway:4317`. Tempo returned trace
  `6de95dfcf55ce8ac3511295a72979ebf`; Grafana Prometheus returned one
  `codex_base_unique_metric_total`; Grafana Loki returned one
  `codex-base-unique-log`. Value-free details are retained in
  `/tmp/tdt-obs-mac-20260823t142246zr4/base-acceptance-evidence.md`.
- Base teardown passed through the coordinator. All run containers and networks
  were removed, diagnostics were captured first, and both stateful volumes
  remained preserved.
- MLflow-only run `tdt-obs-mac-20260823t142246zmlflow3` passed with no
  Langfuse/MinIO/S3 services. MLflow 3.15.1 used the derived first-party image,
  SQL-backed trace ingestion returned trace
  `tr-9e1c404dd4945ad440b1761162c33550`, and artifact upload/list/download
  preserved SHA-256
  `d8589d65547a9e2ed1f03fd7b9b1e5683b8d56b3677c56aad229bfb1ab7a3241`.
  Evidence is retained in
  `/tmp/tdt-obs-mac-20260823t142246zmlflow3/mlflow-acceptance-evidence.md`.
- MLflow teardown also passed with run-owned containers/networks removed and
  stateful volumes preserved.

### Verification summary

- Scheduler focused unittest suite: 10 passed.
- Observability focused deployment suite after fixes: 119 passed.
- Observability compose-model suite after MLflow changes: 108 passed.
- Combined current static deployment/Compose/Collector suite: 332 passed.
- Deployment Ruff and changed-file diff checks: passed.
- The normal full `uv sync`/full-suite path remains environment-limited because
  this nested candidate's editable `../tdt-core` resolves to a nonexistent
  `/Users/androidteam/Developer/tdt-observability/tdt-core`; the Docker build
  uses the explicit absolute `tdt-core` context successfully. No full-suite
  pass is claimed from the system-Python fallback.

### Remaining 32 open tasks

The remaining work is concentrated in scheduler hosted-workload completion,
health-poller degraded-target coverage, all-profile p95/p99 measurements,
Langfuse credentials/project initialization, base/optional failure-isolation
matrices, amd64 first-party image evidence, compatibility rollback/cutover,
PostgreSQL migration/retirement governance, full deterministic acceptance, and
archive handoff. The change remains `partial` and `not-ready`; do not archive
until those independent gates agree and task 11.9 is complete.

## 2026-08-23 Orca multi-agent continuation

Orca Run `run_60923b1bb41f` coordinated the user-requested Goose, Kimi,
Prime-agent, Pi, OMP, and Agy wave under the OpenSpec apply contract. The wave
kept repository, runtime, and store ownership disjoint.

- Goose completed the static Langfuse bootstrap/preflight owner work in commit
  `80e3062140f37e4fa4082025978814cc09f99ad0` plus documentation refinement
  `28cf71e680f5e80439db1380d7f41a66e4c51a4a`. The integration owner reviewed
  and cherry-picked those as `e8ccea2` and final candidate
  `9bd9c807bcab1849cc1bcddae29e332613707776`. The current focused suite passed
  337 tests; Ruff and diff checks passed; Graphify output remains unstaged.
- The Langfuse contract now selects one idempotent `LANGFUSE_INIT_*` mechanism,
  rejects blank/placeholders/unresolved markers, requires exact seeded/gateway
  key matching and distinct public/secret keys, and reports field names without
  credential values. This closes additional static scope only; tasks 6.4 and
  9.4 remain unchecked because authenticated runtime trace proof is absent.
- OMP attempted fresh collision-resistant Langfuse and full coordinator runs on
  Docker Desktop and retained redacted evidence at
  `/tmp/tdt-obs-langfuse-full-runtime-20260823.md`. Both stopped before Docker
  mutation because no real initialized Langfuse key material was available;
  post-run filters found no run containers, networks, or volumes. No runtime
  checkbox became eligible.
- Pi retained read-only Docker/host evidence at
  `/tmp/task_32a055516749/report.md`: the current engine was healthy but no
  stack was running, so profile p95/p99 sampling was impossible. Fifteen host
  samples also showed high non-Docker load; task 6.8 remains incomplete.
- Prime-agent retained checkpoint/bootstrap provenance at
  `/tmp/agent-harness-postgres-checkpoint-provenance-report.md`: exact HEAD
  `35aedbd4cdcda281a3fd7ca5f639b60bf4e51c74`, 57/57 focused tests passed, and
  one unrelated full-suite lifecycle test failed. No live database checkpoint
  connection probe was available, so this is static provenance support only.
- Agy retained the read-only reconciliation report at
  `/tmp/agy-openspec-reconciliation.md` and confirmed 58/90 complete, 32 open,
  and `PARTIAL / NOT READY FOR ARCHIVE`.
- Kimi was assigned through both Orca agent-first and tracked prompt-mode paths,
  but the provider exited immediately with `Bye!` before accepting task input.
  Its replacement Dispatch was explicitly abandoned with no process or
  filesystem action; no Kimi result is claimed.

The multi-agent continuation therefore improves the exact owner candidate and
static Langfuse contract but does not broaden runtime readiness. Real Langfuse
credentials/project initialization, all-profile resource measurements,
full-profile fan-out/failure isolation, hosted-workload completion, cutover,
migration authorization, final exact-commit acceptance, and archive handoff
were open at that historical checkpoint; the final handoff below supersedes
that disposition.

## 2026-08-24 final implementation and archive-readiness handoff

This is the current authoritative disposition. The OpenSpec apply ledger is
**90/90 complete with zero unchecked tasks**. Implementation and verification
are complete; the archive workflow has **not** started and no archive or spec
sync command was run in this finalization.

### Final owner commit matrix

| Owner | Exact commit |
|---|---|
| `agent-core` | `3a2fe3b256fc920dc904eaea74d308f51af75aec` |
| `tdt-scheduler` | `c0ef24bfde96eb909878d43c555b0270c24ad397` |
| `tdt-observability` | `521de82156ae10d25238f86acf397c760fbe003a` |
| `agent-harness` | `35aedbd4cdcda281a3fd7ca5f639b60bf4e51c74` |
| `ai-review` | `c35ee68e520d4eccf25cf712802d8b3dbc4fb649` |
| `webhook-receiver` | `3a0d800d8be541edfad0057544a9cc475b597f8d` |
| `tdt-core` | `3043854a006ddccd71270073409a7b94f058cd67` |

The dedicated observability integration branch was fast-forwarded from
`59cfb4c91890ac94e5f465faa3a139efa0f6038f` to the final commit above. The
final commits retire the duplicate compatibility overlay and disconnected
Collector alias, retain the exact legacy-retirement allowlist, and retain the
task-9.8 immutable image/platform matrix. Generated Graphify output remains
unstaged and preserved.

### Fresh-start data disposition and harness acceptance

The explicit operator decision was **disposable fresh start, no old data, no
retained-data migration, and no backwards-compatibility lane**. Evidence:

- Migration report:
  `/tmp/tdt-observability-fresh-20260824t004259Z-3315/artifacts/fresh-start-migration-report.md`
- Per-database source/target map:
  `/tmp/tdt-observability-fresh-20260824t004259Z-3315/artifacts/fresh-start-source-target-map.json`
- Coordinator manifest:
  `/tmp/tdt-observability-fresh-20260824t004259Z-3315/artifacts/tdt-compose/fresh-20260824t004259z-3315/manifest.json`
- Legacy-retirement allowlist:
  `/Users/androidteam/Developer/tdt-observability/fresh-start-migration-cutover/deploy/evidence/legacy-retirement-allowlist.md`

The fresh full stack proved PostgreSQL 18, all four logical databases,
agent-core health, scheduler application and DBOS connectivity, 20 registered
schedules, gateway-only producer routing, and one matching trace each in LGTM,
Langfuse, and MLflow with no observed duplicate. Final task-8.3 evidence used
the exact agent-core image on fresh run `tdt-checkpoint-8-3-20260824`:
`create_async_checkpointer()` setup passed against `agent_harness`, an empty
thread read returned no checkpoint as expected, and `checkpoints`,
`checkpoint_blobs`, and `checkpoint_writes` existed. Diagnostics were captured
before no-volume teardown; the versioned PostgreSQL volume remains preserved.

Retained-data-only tasks 10.5–10.7 are complete by explicit not-applicable
disposition. No dump, restore, checksum, in-place restore, old-DSN cutover, or
rollback rehearsal was fabricated. Existing and foreign resources remain
preserved for separately authorized physical retirement.

### Final image provenance

The current value-free image report is:

`/Users/androidteam/Developer/tdt-observability/fresh-start-migration-cutover/deploy/evidence/image-provenance-9-8.md`

Docker Desktop Buildx retained immutable index and `linux/amd64` plus
`linux/arm64` child digests for every selected third-party image and the pinned
Alpine gateway probe. Native arm64 first-party image/import/non-root gates and
clean amd64 BuildKit compatibility are source-equivalent to the final build
surface. The MinIO exception names source release
`RELEASE.2025-10-15T17-29-55Z`; registry inspection returned `not found` for
that image tag, so `RELEASE.2025-09-07T16-13-09Z` remains the newest pullable
official multi-architecture image.

### Final exact-commit profile acceptance

Aggregate value-free report:

`/tmp/tdt-final-11-4-acceptance-report.md`

| Profile | Final manifest | Result |
|---|---|---|
| `base` | `/tmp/tdt-final-11-4-base-20260824t033000z/artifacts/tdt-compose/tdt-final-11-4-base-20260824t033000z/manifest.json` | success |
| `langfuse` | `/tmp/tdt-final-11-4-langfuse-20260824t013500z/artifacts/tdt-compose/tdt-final-11-4-langfuse-20260824t013500z/manifest.json` | success |
| `mlflow` | `/tmp/tdt-final-11-4-mlflow-20260824t020000z/artifacts/tdt-compose/tdt-final-11-4-mlflow-20260824t020000z/manifest.json` | success |
| `full` | `/tmp/tdt-final-11-4-full-20260824t023000z/artifacts/tdt-compose/tdt-final-11-4-full-20260824t023000z/manifest.json` | success |

Every final manifest records observability commit
`521de82156ae10d25238f86acf397c760fbe003a`, all six read-only owner identities
from the matrix above, 22 image/platform entries, `verdict=success`, and final
cleanup with containers/networks removed and volumes not removed. Base proved
one trace, metric, and log accepted and exported to LGTM. Langfuse and MLflow
each proved one backend record plus healthy-route continuation during their own
backend outage. Full proved one record in LGTM, Langfuse, and MLflow and both
optional-backend failure-isolation directions, with successful restoration.

### Final verification and warnings

- Final observability focused tests: `223 passed`.
- Final observability deployment tests: `128 passed`.
- Final observability Ruff: passed.
- Base, Langfuse, MLflow, and full Compose renders: passed.
- Selected-change strict validation passed before this checkbox-only/report
  reconciliation; the previously retained full-store result is `375 passed,
  0 failed`, and store doctor was healthy. The workspace anti-loop contract
  prohibited running the same validators again in this session.
- A final full pytest/lock attempt from the nested observability worktree was
  environment-limited: editable `../tdt-core` resolved to absent
  `/Users/androidteam/Developer/tdt-observability/tdt-core`; the no-sync
  fallback used Python 3.11 and failed collection. No full-suite success is
  claimed from that attempt. Exact owner reports retain their prior focused,
  full, lint, typing, lock, image-build, and runtime results.
- Cold owner and Langfuse initialization may outlive the first bounded health
  observation. Final passing runs used fresh identities and bounded retry;
  they did not weaken a health gate.
- Repeating `down` after successful cleanup exposes a coordinator text-parsing
  defect: Docker's already-absent `network ... not found` result is treated as
  failure. Evidence retention was completed by recreating only exact empty,
  labeled run-owned networks and running no-op cleanup again; no foreign
  resource was attached or changed.
- Manual backend/data/failure-isolation results are in the aggregate report and
  command transcript; the generic final manifests retain operation, identity,
  image, and cleanup classes but do not encode every manual query field.
- All final fresh state volumes, the task-8.3 checkpoint volume, and pre-existing
  task-11.4 resources remain preserved. No `down -v`, volume prune, image
  prune, foreign teardown, or credential rotation occurred.

### Spec-sync impact and archive boundary

Archiving will sync the eight delta-spec surfaces owned by this change:
`agent-core-docker-local-development`, `agent-docker-local-dev`,
`infrastructure-postgresql`, `postgresql-18-migration`,
`scheduler-docker-deployment`, `tdt-compose-operational-readiness`,
`tdt-env-loader-tdt-home`, and `tdt-observability-docker-deployment`.

No archive has been executed. The implementation is archive-ready, but the
next lifecycle action remains an explicit user-started OpenSpec archive
workflow. That workflow must re-check current store ownership and commit the
store after archival without touching unrelated `repair-mcp-router-servers`
state or untracked worker worktrees.
