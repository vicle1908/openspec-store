# Verification Evidence: `align-uv-containers-templates-and-tooling`

## Summary

- **Change**: `align-uv-containers-templates-and-tooling`
- **Store**: `/Users/androidteam/Developer/platform/openspec-store` (`openspec-store`)
- **Date**: `2026-10-25`
- **Tasks Completed**: `11/11` (all primary tasks, review fixes, and live end-to-end operational verifications passed)

---

## 1. Real Container Builds & Runtime Probes (5 Stacks)

1. **`shb/shb-schedule` (Live Stack)**:
   - Command: `docker compose -f compose.yaml -f compose.override.yaml up -d --build scheduler`
   - Latency: `5.11s` build, `1.48s` recreate. Image `sha256:6ef91741b5a4e2bc167408592d0accfae37ee6a87fd129fb5960cc006cbd4a15`.
   - Healthcheck: `Up (healthy)` on `127.0.0.1:9110`.
   - Runtime Python: `docker exec shb-schedule-scheduler-1 python --version` -> `Python 3.15.1`.
   - HTTP Probes:
     - `curl -i http://127.0.0.1:9110/scheduler/health` -> `HTTP/1.1 200 OK` (`{"status":"healthy","app":"shb-schedule","is_leader":true,"backend":"postgres"}`)
     - `curl -i http://127.0.0.1:9110/scheduler/schedules` -> `HTTP/1.1 200 OK` (`{"total":4,"schedules":{...}}`)
   - Unit tests: `uv run pytest` -> `122 passed in 141.29s` (`rc=0`).

2. **`tdt/agent-core`**:
   - Hardened `Dockerfile` with `libc6-dev` (for sdist compilation of C extensions on Python 3.15.1 arm64), `UV_COMPILE_BYTECODE=1`, `UV_PYTHON_PREFERENCE=only-system`, `UV_PYTHON_DOWNLOADS=never`.
   - Build: `docker compose -f compose.yaml build app` -> `exit 0` (`agent-core:local-dev` `sha256:8793f65a3afd38636dc38946a9763f1bc7b6bedea52bae1c28bb26a9210b7a4d`).
   - Runtime Smoke: `docker run --rm agent-core:local-dev python -c "import sys, agent_core; print(sys.version, agent_core.__file__)"` -> `3.15.1 (main, Oct 21 2026) /workspace/agent-core/src/agent_core/__init__.py`.
   - `uv` version in container: `uv 0.13.5 (aarch64-unknown-linux-musl)`.
   - Contract tests: `uv run pytest tests/test_docker_local_dev.py` -> `16 passed in 0.05s` (`rc=0`).

3. **`tdt/tdt-observability`**:
   - Build: `docker build --build-context tdt-core=/Users/androidteam/Developer/tdt/tdt-core -t tdt-observability:e2e-verify .` -> `exit 0` (`sha256:28ed3c6305d31d71dd6b04d4070d0a613f2dfc8324ec3c25a22bd6508c57caff`).
   - Runtime Smoke: `docker run --rm --entrypoint /app/.venv/bin/python tdt-observability:e2e-verify -c "import sys, tdt_observability; print(sys.version, tdt_observability.__file__)"` -> `3.15.1` (`rc=0`). Image untagged/removed.
   - Unit tests: `uv run pytest` -> `613 passed in 35.70s` (`rc=0`).

4. **`platform/claude-code-provider-adapter`**:
   - Build: `docker build -t claude-code-provider-adapter:e2e-verify .` -> `exit 0` (`sha256:737a27f2b6aae15db15330de16bcac757cf6a14d8295212dd41f258bec590fff`).
   - Runtime Smoke: `docker run --rm claude-code-provider-adapter:e2e-verify /app/.venv/bin/python -c "import sys, claude_code_provider_adapter; print(sys.version, claude_code_provider_adapter.__file__)"` -> `3.15.1` (`rc=0`). Image untagged/removed.
   - Unit tests: `uv run pytest` -> `55 passed in 0.33s` (`rc=0`).

5. **`tdt/tdt-scheduler`**:
   - Compose config validation: `docker compose -f compose.yaml config -q` -> `exit 0`.
   - Dependency integrity gate CLI: `uv run python3 dependency_integrity_gate.py --help` -> `exit 0`.
   - Contract tests: `uv run pytest tests/` -> `13 passed in 0.76s` (`rc=0`).

---

## 2. Real End-to-End CLI & Runtime Operations

1. **`tdt/agent-core` Project Scaffolding in `/tmp`**:
   - Executed `uv run agent-core init "$TMP_DIR/demo-reviewer" --template reviewer` -> `exit 0` (`3.71s`).
   - Created files verified: `.python-version` (`3.15`), `pyproject.toml` (`requires-python = ">=3.15"`, `[tool.uv] required-version = ">=0.13.5"`). Cleanly removed `/tmp` scaffold after test.
2. **`platform/prime-agent` REPL Snapshot/Restore & Skill CLIs**:
   - Real `_snapshot_state` and `_restore_state` on Python 3.15.1: successfully persisted and restored function `def add(a, b): return a + b`, asserting `restored_ns["add"](20, 22) == 42` (`exit 0`). Cleaned up `/tmp/snap-*` files.
   - Skill CLIs: `./.venv/bin/attach_image --help` and `./.venv/bin/websearch --help` executed with `exit 0`.
3. **`shb/shb-ai-review` CLI Execution**:
   - Registered `shb-review` CLI console script alias and added positional path argument support in `scan()`.
   - Ran `uv run shb-review scan src/shb_review/validation/hunk_gate.py` -> `exit 0` (`Zero compliance or security findings detected. Clean scan!`).
4. **`platform/hermes-webui` Runtime Smoke**:
   - Tested `/Users/androidteam/Developer/platform/hermes-webui/.venv/bin/python` -> `Python 3.13.17` (`yaml 6.0.3`, `cryptography 50.0.2`).
   - Run `./.venv/bin/pytest tests/test_ci_hygiene.py -q` -> `7 passed in 91.22s` (`exit 0`). Clean git working tree preserved.

---

## 3. 37-Root Ecosystem-Wide Consistency Table

Audited via automated script across all 37 first-party project roots:
- `.python-version == "3.15"`: **37/37 (100%)**
- `pyproject.toml` `requires-python == ">=3.15"`: **37/37 (100%)**
- Zero `<` upper bounds across dependencies and dev groups: **37/37 (100%)**
- `[tool.uv]` `required-version = ">=0.13.5"` & `python-preference = "only-managed"`: **37/37 (100%)**
- `.venv` resolves `Python 3.15.1`: **37/37 (100%)**
- `uv lock --check --offline` exits `0` (average latency `24–45ms`): **37/37 (100%)**
- Zero stale `*cpython-314*.pyc` files in `__pycache__/`: **0 found (100% clean)**

---

## 4. Host Toolchain & Governance Manifests

1. **`uv tool` Fleet (`Python 3.15.1`)**:
   - `graphify --version` -> `graphify 0.9.95` (`exit 0`)
   - `tvly --version` -> `tavily-cli 0.1.8` (`exit 0`)
   - `browser-use --help` -> `Browser Use v0.13.13` (`exit 0`)
   - `infinity_emb --help` -> `infinity-emb v0.0.78` (`exit 0`)
2. **Workstation Manifest Reconciliation**:
   - `inventory-workstation-toolchain.py --json`: `{"status": "aligned", "drift_count": 0, "obsolete_candidate_count": 0}`.
3. **OpenSpec Store Validation**:
   - `openspec validate align-uv-containers-templates-and-tooling --strict --json --store openspec-store`: `passed: 1, failed: 0`.
   - `validate-archive-readiness.py`: `Status: READY (exit code 0)`.
