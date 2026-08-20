## 1. Accept the Quality Result and Freeze Store Ownership

- [ ] 1.1 Verify `restore-agent-pydantic-quality-gates` has accepted agent-core, agent-harness, agent-docs-sync, and store result SHAs; record the cross-reference and leave this task incomplete if any required gate is missing.
- [ ] 1.2 Publish the sole openspec-store writer, dedicated worktree, 40-character base SHA, raw dirty inventory, content fingerprint, and preserved active/untracked paths; verify observability and JTI changes are not selected.
- [ ] 1.3 Add a minimal store-tooling `pyproject.toml` and `uv.lock` for Python 3.14 plus pytest, and verify a clean `uv sync --frozen` followed by `uv run --frozen pytest --version` succeeds without relying on the existing local `.venv`.
- [ ] 1.4 Define a redacted machine-readable archive-readiness evidence schema covering repository identity, dirty inventory, content hash, dependency origins, commands/exits, gate classification, authoritative spec paths/sync, rollback, and owner; verify valid/invalid fixtures parse deterministically.
- [ ] 1.5 Create a corrective ledger for the four reviewed archives with exact archived paths, incomplete or unsupported claims, owning corrective tasks, and closure gates; verify the archives themselves remain unchanged.

## 2. Implement Active-Change Preflight

- [ ] 2.1 Implement `scripts/validate-archive-readiness.py` task parsing that rejects any unchecked tracked task before archive readiness and verify fixtures for complete, incomplete, missing, and malformed task files.
- [ ] 2.2 Resolve required artifacts and authoritative delta specs from OpenSpec status/instruction JSON, including `artifactPaths.specs.existingOutputPaths`, and verify `skip_specs: true` is an explicit no-delta success while missing required deltas fail.
- [ ] 2.3 Validate the evidence manifest against current source identities and required gate outcomes, and verify source drift, failed/skipped/unavailable gates, missing dependency origins, and missing rollback each fail closed.
- [ ] 2.4 Emit stable redacted JSON and human-readable diagnostics with no credential values, and verify every failure identifies the owning task and remediation.

## 3. Detect Post-Archive Integrity Violations

- [ ] 3.1 Implement a base-ref-scoped audit for newly moved archive paths and verify it detects an archive move performed with incomplete tasks.
- [ ] 3.2 Detect completion-only task edits made after the archive move and verify the validator reports a corrective-ledger incident without rewriting history.
- [ ] 3.3 Scope legacy debt to the corrective baseline so unrelated pre-existing archives do not block all store validation, and verify any newly introduced violation still fails the range audit.

## 4. Integrate Standard and Claude Archive Workflows

- [ ] 4.1 Update `.agents/skills/openspec-archive-change/SKILL.md` and `.agents/skills/openspec-bulk-archive-change/SKILL.md` to require the validator before mutation and to block incomplete tasks/evidence; verify inline spec sync and user confirmation remain intact.
- [ ] 4.2 Update the matching `.claude/skills/openspec-{archive,bulk-archive}-change/SKILL.md` and `.claude/commands/opsx/{archive,bulk-archive}.md` through their store-owned workflow, and verify standard/Claude invocation semantics remain intentionally distinct.
- [ ] 4.3 Add `.github/workflows/validate-openspec-store.yml` to install uv and `@fission-ai/openspec@1.10.0`, print versions, run `uv sync --frozen`, strict store validation, `uv run --frozen pytest -q`, the managed-skill check, and the archive range audit against the PR base; verify a raw-CLI incomplete archive fixture fails the workflow commands locally.
- [ ] 4.4 Run `python3 scripts/sync-workspace-agent-skills.py` followed by `python3 scripts/sync-workspace-agent-skills.py --check` and verify workspace/user symlinks point to the reviewed store-owned targets without touching `.codex/skills`.

## 5. Validate, Roll Back, and Commit

- [ ] 5.1 Run `uv run --frozen pytest tests/test_validate_archive_readiness.py -q` covering clean success, incomplete tasks, missing evidence, drift, failed/unavailable gates, `skip_specs`, missing deltas, sync failure, and post-archive edits; record exact results.
- [ ] 5.2 Run `uv run --frozen pytest -q`, strict selected/full-store OpenSpec validation, store doctor, managed-skill checks, Python compile checks, workflow YAML validation, and `git diff --check`; verify no unrelated active/archived artifact changed.
- [ ] 5.3 Rehearse rollback by reverting only the validator/workflow integration in a disposable store worktree and verify prior store behavior plus unrelated histories remain intact.
- [ ] 5.4 Freeze final HEAD, raw dirty inventory, content fingerprint, validator evidence, and corrective ledger; commit the scoped store result and leave this change’s archive task incomplete until the validator passes against its own committed SHA.
