# Verification Evidence Ledger: `onboard-muse-code-cli-with-omniroute-combo`

**Date**: 2026-10-17  
**Change**: `onboard-muse-code-cli-with-omniroute-combo`  
**Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)

---

## 1. Official Homebrew Cask Installation & Workstation Toolchain Governance

### Task 1.1: Homebrew Cask Installation & Single-Owner PATH Resolution

- **Command**:
  ```bash
  HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_CASK_OPTS="--no-quarantine" brew install --cask muse-code
  ```
- **Output (`exit 0`)**:
  ```text
  ==> Fetching downloads for: muse-code
  ✔︎ Cask muse-code (1.4.10-R6427.1)
  ==> Installing Cask muse-code
  ==> Linking Binary 'muse-aarch64-macos' to '/opt/homebrew/bin/muse'
  🍺  muse-code was successfully installed!
  ```
- **Version & Shell PATH Resolution (`exit 0`)**:
  ```bash
  /opt/homebrew/bin/muse --version && zsh -lc 'which -a muse' && zsh -ic 'which -a muse'
  ```
  ```text
  Muse Code 1.4.10 (1.4.10-R6427.1)
  /opt/homebrew/bin/muse
  /opt/homebrew/bin/muse
  ```

### Tasks 1.2 & 1.3: Toolchain Updater Registry, Inventory, Manifest, & Coverage Reconciliation

- **Files Modified**:
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/toolchain_updater_registry.py` (`("muse", "brew-cask")` and `("muse-code", "brew-cask")` registered with `source_type="brew-cask"`, `supported_verb=None`, `updater_dispatch="none"`, `delegating_to="brew"`, `status="uncovered_declared"`)
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py` (`tools_to_evaluate`, `documented_channels_map["muse"]`, `elif name in ("droid", "cursor-agent", "buzz", "muse"):`, `tools_to_check`, `preferred_sources["muse"]`, `name_collisions["muse"]`)
  - `/Users/androidteam/Developer/platform/openspec-store/config/workstation-toolchain-manifest.json` (`profiles["ai-agents"]` and `tools.muse`)
  - `/Users/androidteam/Developer/platform/openspec-store/scripts/reconcile-agent-cli-coverage.py` (`known_agents` and `--include-uncovered`)
  - `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` & `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` (`AGENT_CLI_KNOWN_UNCOVERED`, byte-identical SHA-256 `437b20d10167654cbdc63c679887f4bc81cbb4474c06b320dbaec4e2133b61f2`)
- **Inventory Verification (`python3 /Users/androidteam/Developer/platform/openspec-store/scripts/inventory-workstation-toolchain.py --json`, `exit 0`)**:
  ```json
  {
    "unknown_count": 0,
    "muse_tool": {
      "name": "muse",
      "authoritative_path": "/opt/homebrew/bin/muse",
      "preferred_source": "cask muse-code",
      "preferred_source_available": true,
      "has_duplication": false,
      "name_collision": "Homebrew cask 'muse' is an unrelated disabled desktop app (muse.ai); official Meta Muse Code CLI is cask 'muse-code'"
    },
    "muse_auth": {
      "name": "muse",
      "authority": "brew-cask",
      "writer": "brew",
      "updater_dispatch": "none",
      "drift_status": "clean",
      "authoritative_path": "/opt/homebrew/bin/muse",
      "resolved_path": "/opt/homebrew/Caskroom/muse-code/1.4.10-R6427.1/muse-aarch64-macos"
    }
  }
  ```
- **Coverage Verification (`python3 /Users/androidteam/Developer/platform/openspec-store/scripts/reconcile-agent-cli-coverage.py`, `exit 0`)**:
  ```text
  === Workstation Agent CLI Coverage Reconciliation ===
    Total Installed Agents: 18
    Declared Covered:       7 (auggie, claude, codex, kimi, opencode, pi, qoder)
    Declared Uncovered:     11 (buzz, cce, cursor-agent, droid, goose, grok, happy, hermes-agent, kilo, muse, prime-agent)
    Undeclared Count:       0
    ...
    muse            -> /opt/homebrew/bin/muse (real: /opt/homebrew/Caskroom/muse-code/1.4.10-R6427.1/muse-aarch64-macos) [UNCOVERED_DECLARED] (package_manager: Homebrew (formula/cask))
  ```

### Task 1.4: Governance Unit Tests

- **Command**:
  ```bash
  python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py
  ```
- **Output (`exit 0`)**:
  - `test_muse_code_caskroom_evaluated_as_brew_cask`: PASS
  - `test_muse_registered_in_updater_registry`: PASS
  - `TestMuseCodeAuthorityAndCollisionGovernance.test_muse_collision_disambiguation_and_clean_drift`: PASS
  - All tests in `test-version-authority-governance.py` passed (`OK`).

### Task 1.5: SHB Schedule Active-Process Exclusion & Pytest Verification

- **Files Modified**:
  - `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`CASK_PROCESS_NAMES = {"muse-code": ("muse-code", "muse", "muse-aarch64-macos")}` in `step_homebrew_update`)
  - `/Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py` (`test_step_homebrew_update_skips_running_muse_code`)
- **Verification (`uv run --directory /Users/androidteam/Developer/shb/shb-schedule pytest`, `exit 0`)**:
  ```text
  93 passed in 103.51s
  ```

---

## 2. OmniRoute `muse-spark-1.3` Combo Registration

### Task 2.1: Pre-Mutation Combo Snapshot & `/v1/muse-code/models` Verification

- **Snapshot**: Saved to `/tmp/omniroute-combos-pre-muse.json` (mode `0600`).
  - Existing combos: `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`), `phanmemvip` (`ad4dace4-9072-42a8-8503-e6188e325890`), `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`), `gemini-4-argon` (`f1cefc64-7662-4f0a-9234-84f70603cbe4`).
- **Catalog Check (`GET http://127.0.0.1:20128/v1/muse-code/models`)**:
  - HTTP `200 OK`, returned `id: "muse-spark-1.3"` with `limit: 1048576`, `reasoning: true`, `tool_call: true`.

### Task 2.2: `muse-spark-1.3` Combo Creation (`POST /api/combos`)

- **HTTP Status**: `201 Created`
- **Created Combo UUID (`id`)**: `453c5dd3-f7f4-4c44-bd4b-6c3c1d0f4e5b`
- **Normalized Combo Entry**:
  ```json
  {
    "id": "453c5dd3-f7f4-4c44-bd4b-6c3c1d0f4e5b",
    "name": "muse-spark-1.3",
    "strategy": "priority",
    "context_length": 1000000,
    "context_cache_protection": true,
    "models": [
      {
        "id": "muse-spark-1-3-ref-1-gemini-3-8-flash-high",
        "kind": "combo-ref",
        "comboName": "gemini-3.8-flash-high",
        "weight": 0
      },
      {
        "id": "muse-spark-1-3-model-2-agy-gemini-3-8-flash-medium",
        "kind": "model",
        "model": "agy/gemini-3.8-flash-medium",
        "providerId": "agy",
        "weight": 0
      }
    ]
  }
  ```
- **Expected Shadow Warning (`#8530`)**: `{"code": "COMBO_NAME_SHADOWS_MODEL", "modelId": "muse-spark-1.3", "providerId": "opencode-zen"}`.

### Task 2.3: Streaming `/v1/responses` Namespace Tool-Call Probe

- Sent `POST http://127.0.0.1:20128/v1/responses` with `"model": "muse-spark-1.3"`, `"stream": true`, and `"type": "namespace", "name": "muse"` (`read_file` tool).
- **Result**: HTTP `200 OK`; `response.output_item.done` emitted:
  ```json
  {
    "type": "response.output_item.done",
    "output_index": 1,
    "item": {
      "id": "fc_call_3740183",
      "type": "function_call",
      "arguments": "{\"path\":\"/etc/hosts\"}",
      "call_id": "call_3740183",
      "name": "read_file",
      "status": "completed",
      "namespace": "muse"
    },
    "sequence_number": 12
  }
  ```

---

## 3. Muse Code Configuration, Credential Seeding, & MCP / Skills Integration

### Task 3.1: `~/.config/muse` & `~/.config/muse/auth.json`

- Seeded via `TBH_CREDENTIAL_BACKEND=file /opt/homebrew/bin/muse auth set --provider meta --api-key-stdin` (`schema_version: 1`) and macOS Keychain (`/opt/homebrew/bin/muse auth set --provider meta --api-key-stdin`, `schema_version: 2` with `{"providers": {"meta": {"storage": "keychain"}}}` backed by Keychain `svce="ai.meta.dev.credentials"` so `muse exec` works in all shells without requiring `TBH_CREDENTIAL_BACKEND=file`).
- **Permissions (`stat -f '%Lp'`)**:
  - `~/.config/muse`: `700`
  - `~/.config/muse/auth.json`: `600`
- **Sanitized Structure (`~/.config/muse/auth.json`)**:
  - `{"schema_version": 2, "providers": {"meta": {"storage": "keychain"}}}` (and `["providers", "schema_version"]`, `["meta"]`, `["api_key"]` under `TBH_CREDENTIAL_BACKEND=file`).

### Task 3.2: `~/.config/muse/settings.json`

- **Permissions (`stat -f '%Lp' ~/.config/muse/settings.json`)**: `600`
- **Sanitized Contents (`~/.config/muse/settings.json`, canonicalized by `muse` `1.4.10-R6427.1` from `mcp_servers` to `mcpServers`)**:
  ```json
  {
    "schema_version": 1,
    "model": "muse-spark-1.3",
    "provider": "meta",
    "endpoint_transport": {
      "base_url": "http://127.0.0.1:20128/v1",
      "auth": "bearer"
    },
    "run": {
      "subagent_delegation_mode": "auto"
    },
    "mcpServers": {
      "mcp-router": {
        "transport": "stdio",
        "command": "npx",
        "args": [
          "-y",
          "@mcp_router/cli@latest",
          "connect"
        ],
        "env": {
          "MCPR_TOKEN": "[REDACTED]"
        },
        "mode": "optional"
      }
    },
    "tui": {
      "foreign_context_notice_shown": true
    }
  }
  ```

### Task 3.3: Skills Import & Discovery

- Executed `/opt/homebrew/bin/muse skills import --from claude --scope user`.
- Verified via `/opt/homebrew/bin/muse skills list --json`: **137** user-scoped skills discovered and active.

---

## 4. End-to-End Smoke Verification & Runtime Keepalive Normalization

### Runtime Wire Normalization Applied During Task 4.1 / 4.2

1. **Discovery URL Normalization (`/muse-code/models` $\rightarrow$ `/v1/muse-code/models`)**:
   - `muse` 1.4.10 issues `GET /muse-code/models` at the origin root. Added URL normalization in OmniRoute's listener (`/app/peer-stamp.mjs` and host `/Users/androidteam/Omniroute/scripts/dev/peer-stamp.mjs:360-362`) rewriting `^/muse-code(/.*|\?.*)?$` to `/v1/muse-code$1` (HTTP `200`).
2. **Rust `serde` Keepalive Frame Normalization (`response.in_progress`) & Recreate Durability**:
   - Confirmed the predicted Rust `serde` deserialization failure when OmniRoute's 1,000 ms startup keepalive emits `response: { id: null, status: "in_progress" }` (`muse` 1.4.10 expects `struct Response` with non-nullable `id: String`, `object: "response"`, `output: []`, `error: null`).
   - Updated the synthetic `response.in_progress` startup payload in the running `omniroute` container (`/app/.build/next/server/chunks/20286.js`), in host `/Users/androidteam/Omniroute/open-sse/utils/sseHeartbeat.ts:17`, and via idempotent `Gate 4b` in `/Users/androidteam/Omniroute/scripts/update.sh:185-224` so container recreates preserve the normalized payload:
     ```json
     {
       "type": "response.in_progress",
       "sequence_number": 1,
       "response": {
         "id": "resp_keepalive",
         "object": "response",
         "status": "in_progress",
         "output": [],
         "error": null
       }
     }
     ```

### Task 4.1: Non-Interactive Prompt Smoke Verification

- **Command**:
  ```bash
  /opt/homebrew/bin/muse exec --disable-approval --no-session-log "Reply with exactly: OMNIROUTE_MUSE_OK"
  ```
- **CLI Output (`exit 0`)**:
  ```text
  OMNIROUTE_MUSE_OK
  ```
- **OmniRoute Call Log Receipt**:
  - `2026-10-17T10-30-20.559Z_29be378e-2203-4ed5-a40a-2f74e881fe52.json`: `status: 200`, `comboName: "muse-spark-1.3"`, `model: "gemini-3.8-flash-high"`, `duration: 3224 ms`.

### Task 4.2: Non-Interactive Tool-Calling Smoke Verification

- **Command**:
  ```bash
  /opt/homebrew/bin/muse exec --disable-approval --no-session-log "Read the file /tmp/muse-smoke-check.txt using your file reading tool and reply with its exact contents."
  ```
- **CLI Output (`exit 0`)**:
  ```text
  The exact contents of [muse-smoke-check.txt](/tmp/muse-smoke-check.txt:1):

  ```
  MUSE_TOOL_CALL_VERIFIED_2026
  ```
  ```
- **OmniRoute Call Log Receipts**:
  - `2026-10-17T10-32-30.702Z_440c6366-f682-4e3b-baee-65732804d7e9.json` & `2026-10-17T10-32-34.373Z_085c16af-6966-42de-8afe-531f88f66ab6.json`: both HTTP `200`, served via `comboName: "muse-spark-1.3"`, executing built-in `muse` namespaced tools (`read_file` and `muse__submit_reminder_decision`).
