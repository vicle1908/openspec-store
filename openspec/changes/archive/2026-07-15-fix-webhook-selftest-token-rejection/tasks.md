# Tasks: fix-webhook-selftest-token-rejection

## webhook-selftest token forwarding

- [x] 1. Patch the registration wrapper in `webhook-receiver/src/webhook_receiver/dbos_scheduling.py` to forward `_secret` instead of `""`
- [x] 2. Update the stale comment block above the registration (was: "no token because receiver has none") to reflect the new behaviour
- [x] 3. Add regression test asserting the wrapper forwards `GITLAB_WEBHOOK_SECRET` to `webhook_selftest_workflow`
- [x] 4. Add regression test asserting the wrapper forwards empty string when `GITLAB_WEBHOOK_SECRET` is unset
- [x] 5. Run `ruff check webhook-receiver/ --fix && ruff format webhook-receiver/`
- [x] 6. Run `mypy webhook-receiver/ --strict`
- [x] 7. Run `pytest -x webhook-receiver/tests/` and confirm green
- [x] 8. Rebuild scheduler image, restart container, verify next `webhook-selftest` probe logs `primary_status=ok`
- [x] 9. Verify no `WEBHOOK_SELFTEST_ESCALATION` is emitted for 30 minutes after restart

## scheduler entrypoint dual-sink logging

- [x] 10. Change `entrypoint.sh` PID 1 redirect from `exec >> $LOG_FILE 2>&1` to `exec > >(tee -a $LOG_FILE) 2>&1`
- [x] 11. Functional-test the tee+exec pattern in a sandbox to confirm both console and file receive post-`exec` output
- [x] 12. Rebuild scheduler image and `docker compose up -d --force-recreate scheduler`
- [x] 13. Verify `docker logs agent-core-local-scheduler-1` now returns lines that were previously only in the host file

## specs / docs

- [x] 14. Add `MODIFIED Requirements` delta to `webhook-delivery-self-test/spec.md` (token-forwarding clause + 2 scenarios)
- [x] 15. Add `MODIFIED Requirements` delta to `scheduler-entrypoint/spec.md` (dual-sink stdout clause + scenario)
- [x] 16. Add `design.md` covering problem recap, fix, behaviour matrix, testing, live verification
- [x] 17. Add `[Unreleased]` section to `docs/CHANGELOG.md` with both fixes + spec changes

## archive

- [ ] 18. Promote change via `openspec archive fix-webhook-selftest-token-rejection`