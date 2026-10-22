# Verification Evidence: `minimize-omniroute-customizations-and-env-drift`

**Date**: 2026-10-22
**Workstation**: macOS Darwin 27.0.0 (`arm64`)
**Target Container**: `omniroute` (`v3.8.52`, `diegosouzapw/omniroute:latest`)
**Target Host Tooling**: `/Users/androidteam/.local/bin/omniroute` and `/opt/homebrew/bin/muse`

---

## §1 Group 1: Entrypoint Simplification (`MUSE_CODE_REWRITE_V3`) & Gate 8 Catalog Auth Alignment

### 1.1 `container-entrypoint-compat.sh` & `ensure-muse-wire-compat.sh` Syntax & Size Reduction
- Reduced `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` from 85 lines to 28 lines (`-57` lines), removing the `/app/.build/next/server/chunks/*.js` regex mutation loop and the 42-line `MUSE_CODE_COMPAT_V2` unauthenticated static catalog block, retaining only the `MUSE_CODE_REWRITE_V3` `/muse-code` → `/v1/muse-code` URL prefix rewrite in `/app/peer-stamp.mjs`.
- Updated `/Users/androidteam/Omniroute/scripts/update.sh` Gate 8 (`endpoints`) so the single in-container `AUTH_PROBE` validates `/v1/models`, `/v1/muse-code/models`, and `/muse-code/models` (`id === "muse-spark-1.3"` in `data[]`) under the `401` opt-out catalog auth posture (or via `verify_muse_catalog_json` when anonymous `GET` returns `200`).

```text
$ sh -n /Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh && echo "sh -n OK"
sh -n OK

$ bash -n /Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh && echo "bash -n OK"
bash -n OK

$ bash -n /Users/androidteam/Omniroute/scripts/update.sh && echo "update.sh bash -n OK"
update.sh bash -n OK
```

---

## §2 Group 2: Host CLI Bridge Bun `.env` Pre-Load & Shadow Warning Suppression

### 2.1 Live Pass-Through CLI Execution (`omniroute health --json` & `omniroute --version`)
```text
$ /Users/androidteam/.local/bin/omniroute health --json 2>&1 | grep -c 'is ignored' || true
0

$ /Users/androidteam/.local/bin/omniroute --version 2>&1
3.8.52
```

### 2.2 Automated Pytest Suite (`test_omniroute_lock_and_watchdog.py` & `test_omniroute_cli_bridge.py`)
```text
$ uv run --directory /Users/androidteam/Developer/platform/openspec-store pytest tests/test_omniroute_lock_and_watchdog.py tests/test_omniroute_cli_bridge.py -v
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_contention_exits_without_poll_loop PASSED [  5%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_digest_mismatch_and_post_deploy_data_gates_retain_flag PASSED [ 11%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_exclusive_lock_and_safe_trap_cleanup PASSED [ 17%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_gate1_checkpoint_fail_closed_preserves_sidecars PASSED [ 23%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_handles_corrupt_or_absent_flag_gracefully PASSED [ 29%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_v3852_muse_wire_compat_and_updater_muse_catalog_and_backup_cleanup PASSED [ 35%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_excluded_while_lock_held_and_ignores_old_metadata PASSED [ 41%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_periodic_6h_integrity_check_pass_skip_and_fail PASSED [ 47%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_provenance_mirror_and_syntax PASSED [ 52%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_restarts_only_base_service_and_leaves_redis PASSED [ 58%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_skips_integrity_during_container_starting_grace_period PASSED [ 64%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_keys_list_fails_closed_on_404_or_offline_without_local_db_fallback PASSED [ 70%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_keys_list_filters_apikey_connections_and_masks_strictly PASSED [ 76%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_passthrough_commands_emit_zero_env_shadow_warnings_on_stderr PASSED [ 82%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_providers_list_formats_table_and_json_and_fails_closed PASSED [ 88%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_status_json_reports_remote_daemon_health_and_upstream_version PASSED [ 94%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_status_rejects_unsupported_output_and_unknown_flags PASSED [100%]

=========================== 17 passed in 16.42s ===========================
```

---

## §3 Group 3: Canonical Homebrew Cask Symlink Restoration & Live Container Verification

### 3.1 Canonical Homebrew Cask Symlink & Native Keychain Storage (`schema_version: 2`)
```text
$ ls -la /opt/homebrew/bin/muse
lrwxr-xr-x 1 androidteam admin 48 Oct 22 11:15 /opt/homebrew/bin/muse -> ../Caskroom/muse-code/1.4.11-R6667.1/muse-binary

$ python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py
....................................
----------------------------------------------------------------------
Ran 36 tests in 7.496s

OK
```

`~/.config/muse/auth.json` (`mode 0600`):
```json
{
  "schema_version": 2,
  "providers": {
    "meta": {
      "storage": "keychain"
    }
  }
}
```

### 3.2 Live Container Recreate, Unmodified Chunks, Opt-Out Catalog Auth, and `muse exec` Probe
```text
$ /usr/bin/lockf -s -t 30 /Users/androidteam/.omniroute/update.lock docker compose -f /Users/androidteam/Omniroute/docker-compose.yml -f /Users/androidteam/Omniroute/docker-compose.override.yml --project-directory /Users/androidteam/Omniroute --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base
 Container omniroute Recreate
 Container omniroute Recreated
 Container omniroute Starting
 Container omniroute Started
HEALTHY after 6x2s

$ /Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh omniroute
Muse Code wire-compat normalization verified (already_ok)

$ curl -s -o /dev/null -w 'ANON_V1=%{http_code}\n' http://127.0.0.1:20128/v1/muse-code/models
ANON_V1=401

$ curl -s -o /dev/null -w 'ANON_REWRITE=%{http_code}\n' http://127.0.0.1:20128/muse-code/models
ANON_REWRITE=401

$ curl -fsS -H "Authorization: Bearer $(/Users/androidteam/.claude/helpers/omniroute-key.sh)" http://127.0.0.1:20128/v1/muse-code/models | jq '{v1_count: (.data | length), v1_first: .data[0].id}'
{
  "v1_count": 40,
  "v1_first": "muse-spark-1.3"
}

$ curl -fsS -H "Authorization: Bearer $(/Users/androidteam/.claude/helpers/omniroute-key.sh)" http://127.0.0.1:20128/muse-code/models | jq '{rewrite_count: (.data | length), rewrite_first: .data[0].id}'
{
  "rewrite_count": 40,
  "rewrite_first": "muse-spark-1.3"
}

$ docker exec omniroute node -e 'const fs=require("fs"); const p=fs.readFileSync("/app/peer-stamp.mjs","utf8"); const c=fs.readFileSync("/app/.build/next/server/chunks/20286.js","utf8"); console.log(JSON.stringify({has_v3:p.includes("MUSE_CODE_REWRITE_V3"),has_v2:p.includes("MUSE_CODE_COMPAT_V2"),chunk_unmodified:!c.includes("resp_keepalive\"")}));'
{"has_v3":true,"has_v2":false,"chunk_unmodified":true}

$ env -u TBH_CREDENTIAL_BACKEND /opt/homebrew/bin/muse exec --disable-approval --disable-reminders --no-session-log "Reply with the single word MUSE_OK"
MUSE_OK
```

---

## §4 End-to-End 10-Gate Updater, CLI Bridge, and Multi-Dialect Feature Verification

### 4.1 Full 10-Gate `update.sh 3.8.52` Run (Exercising Gate 4b `MUSE_CODE_REWRITE_V3` & Unified Gate 8 `AUTH_PROBE`)
```text
[2026-10-22 11:38:30] === OmniRoute update starting: target version 3.8.52, target digest sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c ===
[2026-10-22 11:38:31] Preflight passed
[2026-10-22 11:38:31] Pre-state: old_version=3.8.52 old_image_id=sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65 old_digest=diegosouzapw/omniroute@sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c baseline_api_keys=1 baseline_provider_connections=34
[2026-10-22 11:38:52] Snapshot verified: /Users/androidteam/.omniroute/snapshots/pre-update-20261022-113830.sqlite (live + host quick_check ok, wal_checkpoint=0|0|0, sidecars consolidated)
[2026-10-22 11:38:55] Pulled image verified: digest=sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c id=sha256:fababa40ede0927ecb9d95b8c7255247fe2da16d0df1bd75a6e390a7fa224a65
[2026-10-22 11:38:55] ALREADY_TARGET: container already on expected version + target image — skipping rollback tag and recreation, continuing verification gates
[2026-10-22 11:38:55] Gate 4b: Muse Code wire-compat normalization verified
[2026-10-22 11:38:55] Healthy after 1x5s
[2026-10-22 11:38:58] Model catalog: anonymous GET=401 (catalog auth enabled — v3.8.50 opt-out); authenticated GET=200 count=1303
[2026-10-22 11:38:58] Endpoints verified: /healthz=ok dashboard=HTTP307 monitoring=healthy/setupComplete=true HEAD/v1/models=HTTP200 GET/v1/models=HTTP401 muse_v1=HTTP200(muse-spark-1.3) muse_rewrite=HTTP200(muse-spark-1.3)
[2026-10-22 11:39:01] Post-deploy data verified: quick_check=ok api_keys=1(>=1) provider_connections=34(>=34) pre_migration_backups=cleaned
[2026-10-22 11:39:01] All gates passed. Update flag cleared.
[2026-10-22 11:39:02] === OmniRoute update complete: 3.8.52 -> 3.8.52 ===
```

### 4.2 Host CLI Bridge & Multi-Dialect Inference Probes
```text
PROVIDERS_JSON_COUNT=34
KEYS_JSON_COUNT=14
HEALTH_STDERR_WARNINGS=0
MODELS_COUNT=1303
LEAKED_TMP=0
MUSE_SYMLINK=../Caskroom/muse-code/1.4.11-R6667.1/muse-binary
{"dialect":"chat","model":"gemini-3.8-flash-high","answer":"437"}
{"dialect":"messages","model":"gemini-3.8-flash-high","answer":"ANTHROPIC_E2E_OK"}
{"dialect":"responses-sse","content_type":"text/event-stream; charset=utf-8","event_count":10,"completed":true,"answer":"RESPONSES_SSE_OK"}
```
