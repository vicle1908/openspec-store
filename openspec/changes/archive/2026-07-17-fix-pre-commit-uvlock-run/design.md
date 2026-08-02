# agent-core pre-commit uv.lock auto-sync fix — Design

## Hook ordering

The `.pre-commit-config.yaml` defines four hook IDs in order:

1. `gitleaks` — secrets scan (external repo)
2. `ruff-check` — ruff lint auto-fix
3. `ruff-format` — format
4. `mypy` — local hook, `entry: uv run mypy src/agent_core/`
5. `pytest` — local hook, `entry: uv run pytest tests/ -q --tb=short`

The first three are external hooks and are unaffected. We only edit the two `local` hook entries.

## Why `uv run --frozen`

`uv run --frozen <cmd>` behaves like `uv run <cmd>` but does NOT update the lockfile. The lockfile must already match `pyproject.toml` or the command fails with:

```
error: The lockfile at `uv.lock` needs to be updated, but `--frozen` was provided.
```

The lockfile is already committed-as-of (well, ignored-as-of) HEAD, so `--frozen` is safe.

## Alternative: pipe through `git checkout`

```yaml
entry: bash -c "uv run --frozen mypy src/agent_core/ && git checkout uv.lock"
```

This protects against any future hooks that might still write to `uv.lock`. Belt-and-braces.

## Why NOT a global fix

This change is scoped to `agent-core/.pre-commit-config.yaml` because:

1. `agent-core` is the only repo where we observed the failure repeatedly during this session.
2. Other repos have their own pre-commit setups and lifecycle; editing them unilaterally violates the workspace rule about explicit per-repo OpenSpec changes.
3. If other repos need the same fix, the fix is one search-and-replace per repo and can be done under their own OpenSpec changes.

## Validation

After applying:

1. Modify any pre-existing file (e.g., add a comment).
2. Stage it: `git add <file>`.
3. Commit: `git commit -m "test pre-commit"`.
4. Pre-commit should run ruff/mypy/pytest cleanly without writing to `uv.lock`.
5. `git status --short` post-commit should show ONLY the new commit, no leftover dirty files.

Then run the full test suite:

```bash
uv run ruff check src/
uv run mypy src/ --strict
uv run pytest tests/ -q
```

All three should still pass.
