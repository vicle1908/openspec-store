# Evidence: portable-mac-development-workstation

## 1. Central Store Implementation Summary
All 31 central authoring tasks for `portable-mac-development-workstation` have been implemented and verified in `/Users/androidteam/Developer/platform/openspec-store`.

Key artifacts delivered:
- **Schema & Manifests**: `config/workstation-manifest.schema.json` (Draft 2020-12), `config/workstation-toolchain-manifest.json` (29 declared tools with authoritative owners, release channels, dispatch classifications, smoke tests).
- **Profiles**: `config/Brewfile`, `config/npm-global-tools.json`, `config/uv-tools.json`, `config/db-tools-profile.json`, `config/rust-dev-profile.json`.
- **Preflight & Templating**: `scripts/bootstrap-workstation-preflight.py`, `scripts/render-workstation-templates.py` (`{{HOME}}`, `{{HOMEBREW_PREFIX}}`, etc.), `scripts/bootstrap-workstation.py` (`--dry-run`).
- **Updater & Mutation Gates**: `scripts/smoke-test-toolchain.py`, `scripts/prune-toolchain-duplicates.py` (5-point verification gate), `scripts/toolchain_updater_registry.py` (Codex/Qoder alignment), `scripts/workstation-daily-update.sh`.
- **Shell & Storage Protection**: `scripts/benchmark-shell-startup.sh`, `scripts/check-service-ports.py` (Ollama 11434, AgentMemory 3111/49134 value-blind quarantine).
- **AgentMemory Health**: `scripts/check-agentmemory-health.py`, `config/launchd/com.agentmemory.server.plist.tmpl` (bounded restart watchdog), `scripts/seed-agentmemory-decisions.py`.
- **Notion Sync Hardening**: `scripts/knowledge-refresh/sync-notion-knowledge.sh` (read-only `--dry-run`, dynamic `/Users/[^/]+/` home redaction, residual token scan, write-receipt verification before SHA advance).
- **Multi-Root Governance**: `scripts/create-external-execution-packet.py` (EEP schema & validator), `scripts/verify-workstation-toolchain.py` (unified read-only audit bundle).

---

## 2. Test Verification Matrix (71 Passing Tests)

| Test Suite | Commands & Results |
|:---|:---|
| **Slice A Tests** | `python3 tests/test_portable_workstation_slice_a.py`: **23 passed** |
| **Slice B Tests** | `uv run pytest tests/test_portable_workstation_slice_b.py`: **31 passed** |
| **Slice C Tests** | `python3 tests/test_portable_workstation_slice_c.py`: **17 passed** |
| **Unified Pytest** | `uv run pytest tests/test_portable_workstation_slice_*.py`: **69 passed, 2 skipped** (in 10.87s) |

---

## 3. Unified Toolchain Verification Output

Command: `python3 scripts/verify-workstation-toolchain.py --json`
- **Overall Status**: `PASS`
- **Total Checks**: 5 / 5 passed
  1. `inventory_reconciliation`: PASS (29 declared tools, 17 aligned, 8 drift, 4 missing, proposals strictly read-only)
  2. `preflight`: PASS (Darwin arm64 confirmed, 6/6 system prerequisites verified)
  3. `templates`: PASS (0 unresolved template tags)
  4. `port_conflicts`: PASS (0 collisions, 0 foreign quarantined processes)
  5. `notion_sanitization`: PASS (Dynamic home redaction, residual token fail-closed scans verified)
- **Evidence Hash**: `4558962ddf0427d467b301938ce1cc7c77acac6e1f73db91b44e38b92f03a295`

---

## 4. External Execution & Deployment Gate Boundary
In strict accordance with the OpenSpec multi-root governance specification:
- **Central Store Boundary**: All code, schemas, and tests remain encapsulated in `openspec-store`.
- **External Mutations Blocked**: No mutations were performed against external host roots (`~/.zshrc`, `/opt/homebrew`, `~/.npm-global`, `~/Library/LaunchAgents`, remote Notion databases).
- **Task 8.3 Status**: Physical deployment to a secondary Mac is recorded as `PENDING_EXTERNAL_RUNTIME_EVIDENCE`, governed by the validated External Execution Packet schema (`scripts/create-external-execution-packet.py`).
