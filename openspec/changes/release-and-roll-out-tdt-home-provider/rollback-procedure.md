# Rollback Procedure: tdt-core Provider

## Prerequisites

- Pre-change tdt-core wheel preserved at `/tmp/tdt-wheelhouse/`
- Consumer test suite accessible
- No live `~/.tdt` data modified during rehearsal

## Rollback Steps (per consumer)

### 1. Stop consumer services
```bash
# Identify processes using tdt-core
ps aux | grep tdt | grep -v grep
# Stop each consumer gracefully
```

### 2. Restore pre-change provider
```bash
# In the consumer's virtual environment:
pip install /tmp/tdt-wheelhouse/tdt_core-OLD_VERSION-py3-none-any.whl --force-reinstall
```

### 3. Verify consumer behavior
```bash
cd ~/Developer/<consumer>
uv run pytest -q --tb=short
uv run python -c "from tdt_core import __version__; print(__version__)"
```

### 4. Verify no live data modified
```bash
# Check ~/.tdt was not changed by rehearsal
cd ~/Developer/tdt-core
uv run tdt config doctor --json | python3 -c "import sys,json; print(json.load(sys.stdin)['error_count'])"
```

## Time Estimate

- Per consumer: ~5 minutes (stop, restore, verify)
- Full rollback (all 15 consumers): ~75 minutes
- Total with verification: ~2 hours

## Rollback Evidence

Record per consumer:
- Exit code of restore command
- Test output after restore
- Time taken
- Any anomalies observed
