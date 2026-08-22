# Preflight Evidence Report: Repair TDT Observability Compose Deployment

**Date:** 2026-08-22  
**Task ID:** `task_c00f3592676d`  
**Dispatch ID:** `ctx_14ff92e1c70a`  
**Target Change:** `repair-tdt-observability-compose-deployment`  
**Status:** ⚠️ **PASS (Structural & Preflight Inventory) / BLOCKED (Runtime Execution)**  
**Executive Summary:** Preflight tasks 1.1–1.6 completed read-only across all 4 writable repositories and 11 scheduler dependency inputs. Docker Desktop daemon is currently unavailable, blocking live container builds, port binding, and runtime acceptance while preserving all existing host and volume assets. All 12 upstream container images have been re-resolved to exact multi-architecture manifests (`linux/amd64` and `linux/arm64`).

> Follow-up, 2026-08-22 18:27 +07:00: the operator subsequently started
> Docker Desktop. `docker desktop status` became `running`, the selected
> `desktop-linux` socket was recreated, and `docker version` exposed Docker
> Desktop 4.87.0 / Engine 29.7.2. This does not rewrite the point-in-time
> preflight inventory below; daemon-backed acceptance is being captured in
> separate exact-commit runtime reports.

---

## 1. Writable Repositories Inventory (Tasks 1.1 & 1.2)

Each repository has an independent Git root, designated toolchain, dedicated implementation worktree, and focused verification suite. Generated Graphify dirt and pre-existing Docker edits are explicitly classified and isolated from change-owned work.

| Repository | Canonical Path | HEAD SHA | Branch | Worktree Path & Branch | Nearest AGENTS.md | Toolchain |
|---|---|---|---|---|---|---|
| `agent-core` | `/Users/androidteam/Developer/agent-core` | `f1a4a9e02f85e75cda5d8bbbebd692814b44a933` | `main` | `/Users/androidteam/Developer/agent-core/agent-core-compose-repair`<br>`[agent-core-compose-repair]` | `agent-core/AGENTS.md` | Python 3.14 (`3.14.7-slim-trixie`), uv `0.12.5` |
| `tdt-scheduler` | `/Users/androidteam/Developer/tdt-scheduler` | `cf54156e5e76c2addb0589a57bec72bc31b83268` | `master` | `/Users/androidteam/Developer/tdt-scheduler/tdt-scheduler-compose-repair`<br>`[tdt-scheduler-compose-repair]` | `tdt-scheduler/AGENTS.md` | Python 3.14 (`3.14.7-slim-trixie`), uv `0.12.5` |
| `tdt-observability` | `/Users/androidteam/Developer/tdt-observability` | `a41cfbee1c44166f893cbffe726319b05ce9e647` | `main` | Foundation: `tdt-observability-foundation`<br>Coordinator: `tdt-observability-coordinator`<br>Backends: `tdt-observability-backends`<br>Integrated: `tdt-observability-integrated` | `tdt-observability/AGENTS.md` | Python 3.14 (`3.14.7-slim-trixie`), uv `0.12.5` |
| `openspec-store` | `/Users/androidteam/Developer/openspec-store` | `e7407735e247d856ed7d77291c6f808cb8fdc0ae` | `main` | `/Users/androidteam/Developer/openspec-store`<br>`[main]` (Store Root) | `openspec-store/AGENTS.md` | OpenSpec CLI, Git |

### Detailed Repository Status & Dirt Classification

#### `agent-core`
- **HEAD:** `f1a4a9e02f85e75cda5d8bbbebd692814b44a933` (`main`)
- **Staged Changes:** None
- **Unstaged Changes:**
  - `M graphify-out/.graphify_labels.json`
  - `M graphify-out/.graphify_labels.json.sig`
  - `M graphify-out/GRAPH_REPORT.md`
  - `D graphify-out/graph.html`
  - `M graphify-out/graph.json`
  - `M graphify-out/manifest.json`
- **Untracked Paths:** `?? agent-core-compose-repair/` (dedicated worktree)
- **Dirt Classification:** Pure generated Graphify dirt. Preserved and excluded from change commits.
- **Focused Verification Commands:**
  ```bash
  uv run ruff check src/ tests/
  uv run mypy src/
  uv run pytest tests/test_docker_local_dev.py tests/test_observability.py
  ```

#### `tdt-scheduler`
- **HEAD:** `cf54156e5e76c2addb0589a57bec72bc31b83268` (`master`)
- **Staged Changes:** None
- **Unstaged Changes:**
  - `M graphify-out/.graphify_labels.json`
  - `M graphify-out/.graphify_labels.json.sig`
  - `M graphify-out/GRAPH_REPORT.md`
  - `M graphify-out/cache/stat-index.json`
  - `D graphify-out/graph.html`
  - `M graphify-out/graph.json`
  - `M graphify-out/manifest.json`
- **Untracked Paths:** `?? graphify-out/2026-08-20/`, `?? graphify-out/2026-08-21/`, `?? graphify-out/2026-08-22/`, `?? graphify-out/cache/ast/`, `?? graphify-out/cache/last_query_stamp`, `?? tdt-scheduler-compose-repair/` (dedicated worktree)
- **Dirt Classification:** Pure generated Graphify dirt. Preserved and excluded from change commits.
- **Focused Verification Commands:**
  ```bash
  python3 -m unittest discover -s tests -q
  python3 dependency_integrity_gate.py
  ```

#### `tdt-observability`
- **HEAD:** `a41cfbee1c44166f893cbffe726319b05ce9e647` (`main`)
- **Staged Changes:** None
- **Unstaged Changes:**
  - `M Dockerfile` (pre-existing uncommitted repair mixing system Python and venv)
  - `M deploy/docker-compose.services.yaml` (pre-existing uncommitted service overlay)
  - `M deploy/docker-compose.yaml` (pre-existing uncommitted base Compose file)
  - `M graphify-out/.graphify_labels.json`
  - `M graphify-out/.graphify_labels.json.sig`
  - `M graphify-out/GRAPH_REPORT.md`
  - `M graphify-out/graph.json`
  - `M graphify-out/manifest.json`
- **Untracked Paths:** `?? docker-desktop-diagnostics/`, `?? graphify-out/graph.html`, `?? tdt-observability-backends/`, `?? tdt-observability-coordinator/`, `?? tdt-observability-foundation/`, `?? tdt-observability-integrated/`
- **Dirt Classification:**
  - Graphify output: Generated knowledge graph dirt (preserved).
  - `Dockerfile` & `deploy/*.yaml`: Legacy uncommitted edits from prior session (to be superseded by the clean federated target models without mutating canonical checkouts).
- **Focused Verification Commands:**
  ```bash
  uv run ruff check src/ tests/
  uv run mypy src/
  uv run pytest tests/ -q
  uv lock --check
  ```

#### `openspec-store`
- **HEAD:** `e7407735e247d856ed7d77291c6f808cb8fdc0ae` (`main`)
- **Staged Changes:** None
- **Unstaged Changes:**
  - `M openspec/specs/infrastructure-postgresql/spec.md`
  - `M openspec/specs/postgresql-18-migration/spec.md`
- **Untracked Paths:**
  - `?? openspec/changes/repair-tdt-observability-compose-deployment/`
  - `?? openspec/reports/openspec-store-verification-2026-08-21.md`
- **Dirt Classification:** Active OpenSpec change proposal, design, tasks, and delta specifications in progress. Change-owned planning artifacts.
- **Focused Verification Commands:**
  ```bash
  openspec validate repair-tdt-observability-compose-deployment --strict --store openspec-store
  openspec validate --all --strict --store openspec-store
  openspec doctor --store openspec-store
  ```

---

## 2. Docker Daemon, Host Ports & Services Inventory (Task 1.3)

### Docker Status: **UNAVAILABLE**
- **Docker Client:** Version `29.7.2`, API `1.55`, Go `go1.26.5`, Platform `darwin/arm64`, Context `desktop-linux`
- **Docker Server Daemon:** `null` — Connection refused at `unix:///Users/androidteam/.docker/run/docker.sock`
- **Containers Running/Total:** 0 / 0 (Daemon offline)
- **Images / Volumes / Networks:** Unavailable via Docker API (Daemon offline)
- **Docker Resource Allocation:** Blocked (Cannot inspect daemon memory/CPU limits)
- **Runtime Work Verdict:** **BLOCKED**. Image builds, container startups, cross-container network aliases, and runtime telemetry acceptance cannot proceed until Docker Desktop is started. All structural validations, static model tests, schema validations, and file checks remain functional.

### Host TCP Listening Ports (Presence-Only)
| Port | Process / Service | PID | Description |
|---|---|---|---|
| `3080` | `node` | 75894 | Web application |
| `3111`, `3112`, `49134` | `iii` | 8604 | Agent memory engine / III server |
| `3113` | `node` | 48467 | Node service |
| `3282` | `MCP Router` | 89077 | MCP Router Electron / CLI |
| `3283` | `ARDAgent` | 1151 | Apple Remote Desktop Agent |
| `5000`, `7000` | `ControlCenter` | 1109 | macOS AirPlay / Control Center |
| `6768`, `65120` | `Orca` | 32616 | Orca orchestration engine |
| `8045` | `antigravity` | 1300 | Antigravity CLI daemon |
| `8787` | `python3.14` | 48844 | Python web service |
| `11434`, `59383` | `ollama` / `Ollama` | 40042, 40662 | Ollama local model server |
| `19528`, `61599` | `cockpit-t` | 61317 | Cockpit tool service |
| `65114` | `buzz-desktop` | 32628 | Buzz desktop companion |
| `5432` | *(free)* | — | PostgreSQL standard host port (available for loopback override) |
| `9100` | *(free)* | — | TDT Scheduler health port (available) |
| `3000` | *(free)* | — | Grafana UI standard host port (available) |
| `4317`, `4318` | *(free)* | — | OTel Gateway gRPC/HTTP ports (available) |

### Active Launchd Services & Schedules (Presence-Only)
- **User Launchd Agents (`~/Library/LaunchAgents`):**
  - `ai.hermes.gateway.plist` (PID 90477)
  - `Antigravity Tools.plist`
  - `com.agentmemory.server.plist`
  - `com.agentmemory.watchdog.plist`
  - `com.developer.index-refresh.plist` (Nightly 02:30 AM knowledge index refresh)
  - `com.microservices.developer-workstation-tool-update.plist`
  - `com.omniroute.server.plist` & `com.omniroute.updater.plist`
  - `com.user.brew-npm-update.plist`
  - `com.victory1908.hermes-webui.plist`
  - `com.workspace.claude-code-provider-adapter.plist`
  - `homebrew.mxcl.herdr.plist`
- **Crontab:** None configured for `androidteam`.
- **TDT File-Based Schedules (`~/.tdt/schedules/`):**
  - `code-daily-scan.yaml`
  - `jira-daily-reports.yaml`
  - `jira-epic-report.yaml`
  - `tdt-observability.yaml`
  - `webhook-receiver.yaml`
  - `.reload` sentinel
- **Presence-Only Secret Verification (No Secrets Printed):**
  - `~/.tdt/.env` present (`6,388 bytes`, permissions `0600`) — environment definitions
  - `~/.tdt/credentials/` present (permissions `0700`) — service accounts and token stores
  - `~/.tdt/philip-project-1-496009-aecd4c291640.json` present (permissions `0600`) — GCP service account

---

## 3. Upstream Image Baseline & Registry Manifest Matrix (Task 1.4)

Every upstream release was queried directly from Docker Hub and GitHub Container Registry (GHCR) on **2026-08-22**. All image tags match the proposal and expose official `linux/amd64` and `linux/arm64` manifests.

| Component | Exact Image Reference & Tag | Multi-Arch Index Digest | `linux/amd64` Manifest Digest | `linux/arm64` Manifest Digest | Upstream Status |
|---|---|---|---|---|---|
| **Python** | `library/python:3.14.7-slim-trixie` | `sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4` | `sha256:d6e0850f13fda0e2305d4c3c1c2f7930fe1042d34ddd958e49bba6ef685d0bb2` | `sha256:c65a4a1140b75416bbc7f28807f82a3746bd6567645d5848123b6a6587f86962` | Verified latest 3.14 patch |
| **uv** | `ghcr.io/astral-sh/uv:0.12.5` | `sha256:e85be844203885286c60ffad8a858d48afb6c5a5c237ca0e67f12e74b8f174b1` | `sha256:db2d5999728c5837e1bf9ba278ee6b05cef1e95e82a20e27b0c915cb4478b9d7` | `sha256:8ba8ac26ed7be9ce3f0fbd510f8d26a3fb9b19056efe6c08433baf9762129edd` | Verified latest release |
| **PostgreSQL** | `library/postgres:18.6-trixie` | `sha256:06cad38a5d9f5d24b4d83d86def30795d5e4b757fedbf5281172b576dedcd941` | `sha256:cd78ca58eb75f929698e117a589488ccb2bd45107247fe02400b50ff6c418324` | `sha256:772ab753f714afefc07b096906b4961e2bb576938c7d007beaa9b62d80680c48` | Verified latest PG18 patch |
| **LGTM** | `grafana/otel-lgtm:0.31.0` | `sha256:f1e548c20c99d2678744be9d90955c0ab208ecc273db2a7a0b5dc5673d0b57fd` | `sha256:20d748ba7439789a0e897d9821a50bca9ba41bba734ec53569d4c01a8dd8f9f2` | `sha256:3827b9b279a2eaf316303c2a2459c61cc8606749f8e08755da858e040c50dfca` | Verified latest release |
| **OTel Collector** | `otel/opentelemetry-collector-contrib:0.159.0` | `sha256:1f2c54a30e713fac6b3ae77a1ec84010c2007e29ced8ec666214fc2f6739c1cc` | `sha256:4f4276c07cee9055f2ab630a86330243f85e208c388ee697bea2a44dab896c3f` | `sha256:64c13b48dd3c4bab8b54b0acf8af0d92b5d80a3b4558b8aeb1d1f11f7fdc9970` | Verified latest release |
| **Langfuse Web** | `langfuse/langfuse:4.16.0` | `sha256:e8459747001aa00da1bdecdc5d46c48d37c2e9b4c2c99743b27efeb2872e0583` | `sha256:2e40c4940c526acf123183d06a46b2d44af6fd9d6c4bff38ac52ae028e874d19` | `sha256:2c6ce0aa8a950ef66fed3d8c08c6bd295e3ab0bec044674ba71e7e2bbeca788a` | Verified latest release |
| **Langfuse Worker** | `langfuse/langfuse-worker:4.16.0` | `sha256:b4490170d5bc18e873f7ca7c3edad5af16022156487a5c47c328d571a9063dc1` | `sha256:7316e5026a00555f8b4b89558f4a100c0f3f0ba6f0f6b1b5f85403e099cc1d6d` | `sha256:f486526acad5367f933f5f638a6e5b0d7d944a374ad4569193de80c4abce654b` | Coupled latest release |
| **Redis** | `library/redis:8.10.1-alpine` | `sha256:becdda6c7f4b3fb42e42fd7f120bbf5c54c4caaaf16f26da24e4563d2c1f0576` | `sha256:9c3ecc609a8087c0f11c494fefaf37a8f7bf9a967631d4a0da8967a9810be354` | `sha256:6e628df1eb8b32f8bced77d65e798d4a1b42cf0a3b30ba0e31eb37411187ca83` | Verified latest Redis 8 |
| **ClickHouse** | `clickhouse/clickhouse-server:26.7.5.10-alpine` | `sha256:0a45b864c73322d4360dea1973ee9b77f29c51af1242ad2d47409908071fa56e` | `sha256:229492c4d1d9c819264ed94fa7e5a85b20d43b3477017fdbb1832ee829812239` | `sha256:d1b0fb95ff47ec18cdd2f47ec9cd326f5bd869a021b56db15bf876f2fda36121` | Verified latest stable 26.7 |
| **MinIO Server** | `minio/minio:RELEASE.2025-09-07T16-13-09Z` | `sha256:14cea493d9a34af32f524e538b8346cf79f3321eff8e708c1e2960462bd8936e` | `sha256:a1a8bd4ac40ad7881a245bab97323e18f971e4d4cba2c2007ec1bedd21cbaba2` | `sha256:9966a92a734f9411e32f4f41d7d9d826fcdc0f68c4e20b70295bd4e7c11f8a2f` | Newest official multi-arch image |
| **MinIO Client** | `minio/mc:RELEASE.2025-08-13T08-35-41Z` | `sha256:a7fe349ef4bd8521fb8497f55c6042871b2ae640607cf99d9bede5e9bdf11727` | `sha256:eb4ea9884b77704230e2423e9004d2fa738dc272876b9cc41a297d29443b8780` | `sha256:37d109dddbbb2c95873f5fc81ac93f37023264770fc580a7564148892087b1b7` | Verified latest release |
| **MLflow** | `ghcr.io/mlflow/mlflow:v3.15.1` | `sha256:ea84a0b879f08b35a6f22f22b294024413e780b8fc978eecf5f760ac16cc9ce5` | `sha256:66fdd38e2fb84741343f34a0aeb2c274781a2b10f96468c2350d235ad61c7bb9` | `sha256:88de73a5b98b2907d6ee71b9a8e87b573e4e1567f781a5ac466e50028f245cf8` | Verified latest release |

*Note on MinIO:* Upstream MinIO has newer git source releases, but `RELEASE.2025-09-07T16-13-09Z` is the latest officially published multi-architecture container image on Docker Hub with verified arm64/amd64 layers.

---

## 4. Volume, Host State & Storage Asset Classification (Task 1.5)

No host storage, database file, or volume was modified or deleted during preflight.

| Asset / Location | Type | Current Size / State | Ownership | Classification & Retention Rule |
|---|---|---|---|---|
| `~/.tdt/observability/events.duckdb` | Host DuckDB database | `101.7 MB` (mod 2026-07-27) | `tdt-observability` (Legacy) | **Preserved Blocker**. Contains historical event telemetry. Retained untouched. |
| `~/.tdt/observability/health.duckdb` | Host DuckDB database | `22.8 MB` (mod 2026-08-03) | `tdt-observability` (Legacy) | **Preserved Blocker**. Contains historical poller health cycles. Retained untouched. |
| `~/.tdt/observability/log-aggregator-state.json` | Host state JSON | `698 bytes` | `tdt-observability` (Legacy) | **Preserved Blocker**. Retained untouched. |
| `~/.tdt/state/observability/log-aggregator-state.json` | Canonical host state JSON | `3.0 KB` (mod 2026-08-22) | `tdt-observability` (Canonical) | **Active State**. Canonical `$TDT_HOME/state/observability` layout. |
| `~/.tdt/backups/postgres/` | Host backup directory | Present (empty) | `agent-core` / Backup | **Preserved Target**. Designated destination for `pg_dump` dumps. |
| `/var/log/tdt` | Host filesystem path | Not present on host | System / Legacy | **Non-existent**. Replaced by canonical `$TDT_HOME/logs` mount. |
| `postgres-data` | Named Docker volume | Inaccessible (Daemon offline) | Legacy / Ambiguous | **Preserved Blocker**. Must not be deleted or auto-migrated. |
| `agent-core-postgres-18-data` | Named Docker volume | Target versioned volume | `agent-core` | **Target Canonical**. Versioned volume for PostgreSQL 18.6 data. |
| `langfuse-postgres-data` / `langfuse-postgres-18-data` | Named Docker volume | Inaccessible (Daemon offline) | `tdt-observability` (Langfuse) | **Preserved Blocker / Target**. Isolated to Langfuse profile. |
| `langfuse-clickhouse-data` | Named Docker volume | Inaccessible (Daemon offline) | `tdt-observability` (Langfuse) | **Preserved Blocker / Target**. Isolated to Langfuse profile. |
| `langfuse-minio-data` | Named Docker volume | Inaccessible (Daemon offline) | `tdt-observability` (Langfuse) | **Preserved Blocker / Target**. Isolated to Langfuse profile. |
| `mlflow-postgres-data` / `mlflow-postgres-18-data` | Named Docker volume | Inaccessible (Daemon offline) | `tdt-observability` (MLflow) | **Preserved Blocker / Target**. Isolated to MLflow profile. |
| `mlflow-artifacts-3-data` | Named Docker volume | Target versioned volume | `tdt-observability` (MLflow) | **Target Canonical**. Local named volume mounted at `/mlartifacts`. |
| `lgtm-data` | Named Docker volume | Inaccessible (Daemon offline) | `tdt-observability` (Base LGTM) | **Preserved Blocker / Target**. Base profile telemetry storage. |

---

## 5. Read-Only Scheduler Dependency-Input Matrix (Task 1.6)

All 11 scheduler dependency inputs were inspected. None receives write ownership during this change.

| Input Name | Absolute Host Path | Git HEAD / Revision Fingerprint | Active Branch | Dirt Status & Classification | Scheduler Use (Context / Mount) | Sequencing & Write Ownership |
|---|---|---|---|---|---|---|
| `tdt-core` | `/Users/androidteam/Developer/tdt-core` | `3043854a006ddccd71270073409a7b94f058cd67` | `fix/remove-api-key-env-loader-exemption` | Graphify dirt only (`.graphify_labels.json`, `graph.json`, etc.) | Declared build context + `:ro` source mount | Read-only input. No write ownership. |
| `jira-daily-reports` | `/Users/androidteam/Developer/jira-daily-reports` | `1eb1ccaae2562e620971705d6fe28bc96147451c` | `main` | Graphify dirt + `M uv.lock` | Mounted `config:ro` and `src:ro` | Read-only input. No write ownership. |
| `jira-skill` | `/Users/androidteam/Developer/jira-skill` | `e78d6e207054d1e9dc043906fd783037914f4492` | `main` | Graphify dirt + `M uv.lock` | Mounted `src:ro` | Read-only input. No write ownership. |
| `webhook-receiver` | `/Users/androidteam/Developer/webhook-receiver` | `baa49981af1ff772b3a760177de3fe0e21150290` | `main` | Graphify dirt + `M uv.lock` | Mounted `src:ro`, `pyproject.toml:ro` | Read-only input. No write ownership. |
| `ai-review` | `/Users/androidteam/Developer/ai-review` | `033de308f78eb2ee65c36c250320a097bd8512fb` | `main` | Graphify dirt + `M uv.lock` | Polled host endpoint via gateway | Read-only input. No write ownership. |
| `code-daily-scan` | `/Users/androidteam/Developer/code-daily-scan` | `580eae6ee8e792113344ed168fe5fc2ef9492a04` | `main` | Graphify dirt + `?? artifact-disposition-audit.md` | Mounted `src:ro`, `config:ro`, `README.md:ro` | Read-only input. No write ownership. |
| `tdt-sheets` | `/Users/androidteam/Developer/tdt-sheets` | `804b690cec2ffbec0e1b33a66b5256da6ff5a6c5` | `main` | Graphify manifest dirt | Mounted `src:ro` | Read-only input. No write ownership. |
| `tdt-observability` | `/Users/androidteam/Developer/tdt-observability` | `a41cfbee1c44166f893cbffe726319b05ce9e647` | `main` | Graphify dirt + uncommitted Docker edits | Mounted `src:ro` into scheduler | Writable in change; read-only to scheduler. |
| `jira-epic-report` | `/Users/androidteam/Developer/jira-epic-report` | `5d5aeb51a9867d69c7ef4174de7a9657c4042f0e` | `main` | Graphify dirt only | Mounted `epic_report:ro`, `pyproject.toml:ro` | Read-only input. No write ownership. |
| `poems-mobile3-android` | `/Users/androidteam/Developer/poems-mobile3-android` | Directory exists (`d41d8cd98f00b204e9800998ecf8427e`) | — (Non-git workspace) | Clean local directory | Mounted `/workspace/poems-mobile3-android` | Read-only input. No write ownership. |
| `poems-mobile3-ios` | `/Users/androidteam/Developer/poems-mobile3-ios` | Directory exists (`d41d8cd98f00b204e9800998ecf8427e`) | — (Non-git workspace) | Clean local directory | Mounted `/workspace/poems-mobile3-ios` | Read-only input. No write ownership. |

---

## 6. Preflight Conclusions & Runtime Blockers

1. **Preflight Inventory Complete:** All repository identities, branches, worktrees, nearest `AGENTS.md` instructions, toolchains, focused test commands, upstream registry multi-arch image digests, host assets, and scheduler dependencies are captured without leaking any secret values.
2. **Key Findings:**
   - Upstream image tags remain 100% current and resolve to verified multi-arch `linux/amd64` and `linux/arm64` manifests.
   - Legacy host state in `~/.tdt/observability` (`events.duckdb` and `health.duckdb`) is preserved and classified as non-disposable.
   - All scheduler inputs are confirmed read-only with no conflicting write ownership.
3. **Runtime Blocker:**
   - **Docker Desktop daemon is offline.** Runtime container builds, live database initialization, OTel gateway tracing probes, and profile acceptance cannot execute until the operator starts Docker Desktop. Structural validations and static tests are unaffected.
