# Tasks: agent-harness-gate-boundary-hardening

## P1: Security fixes

- [ ] Fix `validate_artifact_root()` in workspace.py: scan components before resolve()
- [ ] Add test: symlink component in artifact root is rejected
- [ ] Add test: direct symlink as artifact root is rejected
- [ ] Add test: clean path (no symlinks) is accepted and resolved
- [ ] Add docstring documenting platform-safe policy and TOCTOU caveat

## P1: Authorization boundary tests

- [ ] Add test: unavailable resolver rejects valid assertion
- [ ] Add test: unavailable resolver rejects even with TDT_ACTOR_ID
- [ ] Add test: separation of duties enforced (initiator cannot approve own gate)
- [ ] Add test: expired gate fails before resolver call

## P2: Generated artifact cleanup

- [ ] Remove .graphify_labels.json from git tracking
- [ ] Remove .graphify_labels.json.sig from git tracking
- [ ] Update .gitignore to exclude graphify label/sig files
- [ ] Document regeneration command

## Verification

- [ ] Run `uv run pytest tests/ -q` — all tests pass
- [ ] Run `uv run ruff check src/ tests/` — clean
- [ ] Run `uv run mypy src/agent_harness/ --strict` — clean
