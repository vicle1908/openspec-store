# Tasks: agent-harness-gate-boundary-hardening

## P1: Security fixes

- [x] Fix `validate_artifact_root()` in workspace.py: scan components before resolve()
- [x] Add test: symlink component in artifact root is rejected
- [x] Add test: direct symlink as artifact root is rejected
- [x] Add test: clean path (no symlinks) is accepted and resolved
- [x] Add docstring documenting platform-safe policy and TOCTOU caveat

## P1: Authorization boundary tests

- [x] Add test: unavailable resolver rejects valid assertion
- [x] Add test: unavailable resolver rejects even with TDT_ACTOR_ID
- [x] Add test: separation of duties enforced (initiator cannot approve own gate)
- [x] Add test: expired gate fails before resolver call

## P2: Generated artifact cleanup

- [x] Remove .graphify_labels.json from git tracking
- [x] Remove .graphify_labels.json.sig from git tracking
- [x] Update .gitignore to exclude graphify label/sig files
- [x] Document regeneration command


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

## Evidence

Code closure: `4ba7478` (closure/gate-boundary-hardening branch)

| Task | Commit | Verification |
|------|--------|-------------|
| Symlink validation | `d41a653` | 7 tests pass: component, direct, clean, relative, env, platform, dangling |
| TOCTOU documentation | `d41a653` | Docstring in workspace.py |
| Resolver rejection | `82dbdaf` | `test_default_resolver_is_typed_unavailable` passes |
| TDT_ACTOR_ID bypass rejection | `82dbdaf` | `test_default_resolver_rejects_even_with_tdt_actor_id` passes |
| Separation of duties | `82dbdaf` | `test_spoof_and_self_approval_fail_closed[separation_of_duties_required]` passes |
| Expired gate fails first | `82dbdaf` | `test_expired_gate_fails_before_resolver_call` passes |
| Labels removed from tracking | `4ba7478` | `git ls-files` returns empty, `git check-ignore` confirms |
| Gitignore corrected | `4ba7478` | Negation lines removed, broad `.graphify_*` rule catches labels |
| Regeneration documented | `4ba7478` | AGENTS.md updated with `graphify label` instruction |
| `validate_contained` re-export preserved | `f132b6e` | Regression test passes |
| Verified main | `2a5f327` (style commit: import-order-only, 0 semantic changes) |
| Full suite green | `2a5f327` | 414 passed, 0 failed |

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
