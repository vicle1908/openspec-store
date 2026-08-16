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


## P1: Authority invariant enforcement

- [x] Add RED test: `AuthorityConfig(allowed_shell=True)` rejects with `ValidationError`
- [x] Add RED test: `AuthorityConfig(allowed_code_execution=True)` rejects with `ValidationError`
- [x] Add RED test: `AuthorityConfig(allowed_external_mutation=True)` rejects with `ValidationError`
- [x] Add RED test: `AuthorityConfig(allowed_source_write=True)` rejects with `ValidationError`
- [x] Add RED test: `HarnessConfig(authority={"allowed_shell": True})` rejects with `ValidationError`
- [x] Implement `Literal[False]` for all four deny-only authority fields in `AuthorityConfig`
- [x] Add `validate_assignment=True` to `AuthorityConfig.model_config` if post-construction mutation is possible
- [x] Verify all 4 fields reject coercion candidates: `1`, `"true"`, `"1"`
- [x] Document Jira read-only structural boundary (not a config field)
- [x] Document GitLab structural boundary (not a config field)

## Verification

- [x] Run `uv run pytest tests/ -q` — all tests pass
- [x] Run `uv run ruff check src/ tests/` — clean
- [x] Run `uv run mypy src/agent_harness/ --strict` — clean

## P1: Stage composition authority boundary

- [x] Add tests: non-empty filesystem, shell, network, and runtime-authoring policies are rejected
- [x] Add test: non-empty authority grants are rejected
- [x] Add test: disabled audit policy is rejected
- [x] Add test: default empty capability policy remains accepted
- [x] Implement `StageCompositionContext.__post_init__` deny-only guard
- [x] Verify exact-false fields reject `0` and `0.0` coercions
- [x] Verify parent `HarnessConfig` assignment cannot replace `authority` with an unvalidated permissive mapping
