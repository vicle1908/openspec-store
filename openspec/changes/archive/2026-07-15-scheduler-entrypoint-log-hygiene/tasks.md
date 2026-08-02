# Tasks: scheduler-entrypoint-log-hygiene

- [x] 1. Update `agent_core/deployments/scheduler/entrypoint.sh`: add `stdbuf -oL` to tee redirect
- [x] 2. Add startup-size-check + rename before tee redirect (50 MB cap)
- [x] 3. Update the file-header comment to document both changes
- [x] 4. Run `bash -n entrypoint.sh` to verify syntax
- [x] 5. Add `MODIFIED Requirements` to `scheduler-entrypoint/spec.md` inside the change: line-buffering + startup-rotation scenarios
- [x] 6. Validate change: `openspec validate --strict scheduler-entrypoint-log-hygiene`
- [x] 7. Rebuild scheduler image, `docker compose up -d --force-recreate scheduler`
- [x] 8. Verify `docker logs --since 5m` shows structlog heartbeat lines immediately
- [x] 9. Verify host file shows structlog lines immediately
- [ ] 10. Archive via `openspec archive scheduler-entrypoint-log-hygiene`