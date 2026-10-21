# Verification Evidence: `tune-omniroute-runtime-limits-and-bridge-provider-list`

**Date**: 2026-10-21
**Workstation**: macOS Darwin 27.0.0 (`arm64`)
**Target Service**: OmniRoute `v3.8.52` (`omniroute-base` container `omniroute`)
**Target Host Tooling**: `/Users/androidteam/.local/bin/omniroute`

---

## 1. Group 1: Environment Limits, Stream Resilience & Compose Deployment

### 1.1 Compose Syntax Validation
```text
$ docker compose -f /Users/androidteam/Omniroute/docker-compose.yml -f /Users/androidteam/Omniroute/docker-compose.override.yml config --services
omniroute-base
redis
```

### 1.2 Container Environment Inspection
```text
$ docker inspect omniroute --format '{{json .Config.Env}}' | jq '.[] | select(test("^(OMNIROUTE_MEMORY_MB|OMNIROUTE_MAX_TOOLS_LIMIT|STREAM_READINESS_STALL_RETRY|EMPTY_STREAM_SIBLING_RECOVERY_ENABLED)="))'
"EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true"
"OMNIROUTE_MAX_TOOLS_LIMIT=256"
"OMNIROUTE_MEMORY_MB=4096"
"STREAM_READINESS_STALL_RETRY=true"
```

### 1.3 Live Health Checks
```text
$ curl -fsS http://127.0.0.1:20128/livez
ok

$ curl -fsS http://127.0.0.1:20128/api/health | jq '{status, timestamp}'
{
  "status": "ok",
  "timestamp": "2026-10-21T13:51:43.623Z"
}
```

---

## 2. Group 2: Host CLI Bridge `providers list` Interception & Test Suite

### 2.1 Live `omniroute providers list` Table Output
```text
$ omniroute providers list
OmniRoute Providers

  b265a72c   github         github                   active
  0ee99889   codex          logmal@yahoomail.pro     expired
  ea0d6c23   agy            vicgnome19092@gmail.com  active
  6fb701a5   ollama-cloud   ollama-1                 active
  529fc317   openrouter     main                     active
  d52f9b6b   openai-compatible-responses-396066d4-c57b-44ab-9683-013cdaa89d49 main                     active
  c0ckp1t0   openai-compatible-responses-cockpit cockpit-daemon           active
  f3aaa87c   anthropic-compatible-6408e370-2373-4ae0-9942-7f4095ba976c main                     active
  fa1eb21a   jina-ai        vic-jina-1               active
  2ef1ce5f   anthropic-compatible-e20f69f5-fc87-4157-9f73-9bdf1d1e2573 main                     active
  a8d86dad   voyage-ai      vic-voyageai             active
  51795cf9   muse-code      muse-code                active
  cc9816d0   openai-compatible-responses-4b50733f-f160-4f63-bf71-088b0bd469ab main-2                   active
  c49089c3   openai-compatible-responses-b26c6aa4-19fa-4dcc-b64a-8e1b972e047e 9c                       active
  06c144f5   openai-compatible-responses-4eccdf3c-cf30-4b81-8b0a-fa993aae5b47 danglamgiau              active
  94b1380a   anthropic-compatible-3d66c3c8-b5be-4b8f-ada2-a151776e1715 main                     active
  7706eea5   openai-compatible-chat-b3b12caa-2cc3-450b-9c6c-9f99ea640536 danglamgiau-chat         active
```

### 2.2 Live `omniroute providers list` JSON Output
```text
$ omniroute providers list --output json | jq '.providers | length'
33
```

### 2.3 Automated Pytest Suite
```text
$ uv run --directory /Users/androidteam/Developer/platform/openspec-store pytest tests/test_omniroute_cli_bridge.py tests/test_omniroute_lock_and_watchdog.py -v
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_status_json_reports_remote_daemon_health_and_upstream_version PASSED [  6%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_status_rejects_unsupported_output_and_unknown_flags PASSED [ 12%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_keys_list_filters_apikey_connections_and_masks_strictly PASSED [ 18%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_keys_list_fails_closed_on_404_or_offline_without_local_db_fallback PASSED [ 25%]
tests/test_omniroute_cli_bridge.py::TestOmniRouteCliBridge::test_providers_list_formats_table_and_json_and_fails_closed PASSED [ 31%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_provenance_mirror_and_syntax PASSED [ 37%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_excluded_while_lock_held_and_ignores_old_metadata PASSED [ 43%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_exclusive_lock_and_safe_trap_cleanup PASSED [ 50%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_contention_exits_without_poll_loop PASSED [ 56%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_gate1_checkpoint_fail_closed_preserves_sidecars PASSED [ 62%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_digest_mismatch_and_post_deploy_data_gates_retain_flag PASSED [ 68%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_periodic_6h_integrity_check_pass_skip_and_fail PASSED [ 75%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_v3852_muse_wire_compat_and_updater_muse_catalog_and_backup_cleanup PASSED [ 81%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_restarts_only_base_service_and_leaves_redis PASSED [ 87%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_watchdog_skips_integrity_during_container_starting_grace_period PASSED [ 93%]
tests/test_omniroute_lock_and_watchdog.py::TestOmniRouteLockAndWatchdog::test_updater_handles_corrupt_or_absent_flag_gracefully PASSED [100%]

=========================== 16 passed in 14.37s ===========================
```
