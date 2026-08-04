# Consumer Migration Guide: tdt-core 0.2.0

## For Consumer Repository Owners

No source changes are required.  The provider update is transparent.

## What You Need To Do

1. **Update dependency floor** in your `pyproject.toml`:
   ```toml
   [project]
   dependencies = ["tdt-core>=0.2.0"]
   ```

2. **Run `uv sync`** to pull the new version

3. **Run your test suite** to verify no regressions:
   ```bash
   uv run pytest -q --tb=short
   ```

4. **Run `tdt config doctor`** to verify your `~/.tdt` layout:
   ```bash
   tdt config doctor --json
   ```

## What Changed For You

- **Nothing visible.**  All changes are provider-internal.
- `load_tdt_env()` still loads from `~/.tdt/.env`
- Client factories (Jira, GitLab, Sheets) work identically
- Scheduler settings load through the governed config parser

## If Doctor Reports Issues

| Finding | Action |
|---------|--------|
| `config_ambiguity` | Remove `config.toml` scheduler section; use `config.yaml` |
| `permission` | Run `chmod 700 ~/.tdt && chmod 600 ~/.tdt/.env` |
| `broken_symlink` | Remove broken symlinks in `~/.tdt/credentials/` |
| `governed_config` | Ensure `${VAR}` references in config.yaml resolve |

## Rollback

If issues arise, pin to the previous version:
```toml
dependencies = ["tdt-core==0.1.0"]
```
Then run `uv sync` and your test suite.
