# Verification Evidence: `standardize-python-315-and-uv-ecosystem`

**Date:** 2026-10-24  
**Change:** `standardize-python-315-and-uv-ecosystem`  
**Store:** `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)

---

## 1. Workstation Python 3.15 & `uv` Toolchain Verification (Tasks 1.1–1.4)

### 1.1 Managed Python 3.15 Installation & Legacy Removal
- **Command**: `uv python list --only-installed`
- **Result**:
  - `cpython-3.15.1-macos-aarch64-none` installed at `/Users/androidteam/.local/share/uv/python/cpython-3.15-macos-aarch64-none/bin/python3.15`
  - Legacy `uv` runtimes (`cpython-3.14.9` and `cpython-3.14.5`) uninstalled (`uv python uninstall 3.14.9 3.14.5`).
  - Shadow shim `/Users/androidteam/.local/bin/python3.15` removed.
- **Inventory Check**:
  - Command: `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py --json`
  - Result: `manifest_reconciliation.status == "aligned"`, `drift_count == 0`, `obsolete_candidate_count == 0`.

### 1.2 Global `uv tool` Environments
- **Command**: `for t in browser-use graphifyy infinity-emb tavily-cli; do ~/.local/share/uv/tools/$t/bin/python --version; done`
- **Result**:
  - `browser-use`: `Python 3.15.1`
  - `graphifyy` (`graphifyy[mcp,watch,office,pdf,postgres]==0.9.95`): `Python 3.15.1`
  - `infinity-emb`: `Python 3.15.1`
  - `tavily-cli`: `Python 3.15.1`

---

## 2. Core SDK Foundation & Framework Wave Verification (Tasks 2.1–3.5)

| Repository | `requires-python` | `.python-version` | `uv lock --check` | `ruff check .` | `mypy src` | `pytest -p no:cacheprovider` |
|---|---|---|---|---|---|---|
| `shb/shb-core` | `>=3.15` | `3.15` | Exit 0 | Exit 0 | Exit 0 (13 files) | `48 passed, 1 skipped` |
| `tdt/tdt-core` | `>=3.15` | `3.15` | Exit 0 | Exit 0 | Exit 0 (45 files) | `562 passed, 6 skipped` |
| `shb/shb-schedule` | `>=3.15` | `3.15` | Exit 0 | Exit 0 | Exit 0 (18 files) | `144 passed` |
| `tdt/agent-core` | `>=3.15` | `3.15` | Exit 0 | Exit 0 | Exit 0 (128 files) | `1,722 passed` |
| `tdt/agent-harness` | `>=3.15` | `3.15` | Exit 0 | Exit 0 | Exit 0 (52 files) | `418 passed` |

- **Specific Code & Typing Verifications**:
  - `tdt/tdt-core`: Updated `DBOSClient(system_database_url=...)`, `DBOSConfig`, and `DBOS.register_queue` call sites (replacing direct `Queue(...)` construction prohibited in `dbos>=3.3.0`) in `scheduling.py` and unit tests in `tdt-core` and `agent-core`; renamed `sentinel` variables in `registry_loader.py`, `test_http_session.py`, and `test_registry_loader.py` (`0` Ruff `A001` violations).
  - `tdt/agent-core` & `tdt/agent-harness`: Removed `<1.45.0` upper bounds on OpenTelemetry packages; migrated 7 `(str, Enum)` classes in `agent-harness` to `enum.StrEnum` (`0` Ruff `UP042` violations); renamed `sentinel` variables (`0` Ruff `A001` violations).
  - `shb/shb-schedule`: Renamed `sentinel` variables in `cli.py` and `test_server.py`; restored `TC` and `TCH` to `[tool.ruff.lint.select]`.

---

## 3. Ecosystem-Wide Wave Verification (Tasks 4.1–6.3)

All 34 first-party repositories verified against Python 3.15.1:

| Domain | Repositories Verified (34 Total) | `uv lock --check` | `ruff check .` | `pytest -p no:cacheprovider` |
|---|---|---|---|---|
| **SHB (13)** | `shb-core`, `shb-agent-core` (32 passed), `shb-agent-harness` (35 passed), `shb-agent-skills` (37 passed), `shb-ai-harness-skills` (16 passed), `shb-ai-review` (26 passed), `shb-browser-cli` (14 passed), `shb-jira-tools` (17 passed), `shb-mcp-servers` (23 passed), `shb-observability` (15 passed), `shb-schedule` (144 passed), `shb-tools` (16 passed), `shb-webhook-receiver` (14 passed) | 13/13 Exit 0 | 13/13 Exit 0 | 13/13 Exit 0 |
| **TDT (16)** | `tdt-core` (562 passed), `agent-core` (1722 passed), `agent-docs-sync` (426 passed), `agent-harness` (418 passed), `ai-harness-skills` (297 passed), `ai-review` (177 passed), `browser-cli` (69 passed), `code-daily-scan` (263 passed), `jira-daily-reports` (568 passed), `jira-epic-report` (354 passed), `jira-kanban-from-spreadsheet` (115 passed), `jira-skill` (889 passed), `ops-automation-suite` (45 passed), `tdt-observability` (93 passed), `tdt-sheets` (126 passed), `webhook-receiver` (97 passed) | 16/16 Exit 0 | 16/16 Exit 0 | 16/16 Exit 0 |
| **Platform / AI-Tooling / VDS (5)** | `platform/openspec-store` (233 passed), `platform/claude-code-provider-adapter` (25 passed), `ai-tooling/workspace-python-template`, `ai-tooling/wiki-mcp-server` (1 passed), `vds/viettel-excel-updater` (36 passed, `mypy src` 0 errors in 3 files, empty `config 2.py` deleted) | 5/5 Exit 0 | 5/5 Exit 0 | 5/5 Exit 0 |

---

## 4. End-to-End Live CLI Execution Proof (Python 3.15.1)

### 4.1 Global `uv tool` Live CLI Invocations
- **`tvly`**:
  - Command: `tvly search "Python 3.15 PEP 649" --max-results 2`
  - Result: Returned 2 search results in 1.16s via Tavily API on Python 3.15.1.
- **`graphify`**:
  - Command: `graphify query "src/tdt_core/scheduler/engine.py::SchedulerEngine" --graph tdt/tdt-core/graphify-out/graph.json`
  - Result: Successfully traversed and returned AST dependency graph nodes on Python 3.15.1.
- **`browser-use`**:
  - Command: `browser-use --version`
  - Result: `0.1.13` (running on Python 3.15.1).
- **`infinity_emb`**:
  - Command: `infinity_emb --help`
  - Result: Displayed CLI usage with zero import or runtime errors on Python 3.15.1.

### 4.2 DBOS 3.3.0 Live SQLite Runtime & CLI Execution
- **Live DBOS Queue Execution**:
  - Code: Instantiated real SQLite DBOS instance (`sqlite:///<tmp>/e2e_dbos.sqlite`), registered `@DBOS.workflow() def compute_square(n): return n * n`, enqueued task `12` via `QueueWrapper(name="e2e-critical", enabled=True, concurrency=2)`, executed workflow, and verified `handle.get_result() == 144`.
  - `SchedulerClient`: Initialized `SchedulerClient(system_database_url=...)` against live SQLite DBOS and queried `client.list_schedules()` with zero errors.
- **`shb-schedule` CLI**:
  - Commands: `shb-schedule list --dir ~/.shb/schedules` & `shb-schedule validate ~/.shb/schedules`
  - Result: Listed all 4 scheduled bank tasks (`daily-shb-docs-sync`, `eod-settlement-recon`, `nightly-compliance-scan`, `workstation-daily-update`) and printed `✓ All 4 manifests valid and approved`.

### 4.3 Core Agent Platform & Live Inference Invocations
- **Pydantic AI 2.61.0 Live LLM Inference**:
  - Invoked `OpenAIChatModel("gemini-4-argon", provider=OpenAIProvider("http://127.0.0.1:20128/v1"))` from `shb-agent-core` on Python 3.15.1.
  - Result: Model responded with `PYTHON_315_LIVE_OK`.
- **Workspace CLIs**:
  - `tdt`: `tdt --help` & `tdt config --help` executed cleanly.
  - `shb`: `shb --help` & `shb doctor --live-jev` executed with green configuration diagnostics.
  - `agent-core`: `agent-core --help` executed with active OTel tracer configuration.
  - `agent-harness`: `agent-harness --help` executed with clean command options.
  - `code-daily-scan`: `code-daily-scan --help` executed with scan subcommands.
  - `wiki-mcp-server`: `wiki_index("concepts")` and `wiki_search("OpenSpec")` queried local LLM wiki markdown pages cleanly on Python 3.15.1.
