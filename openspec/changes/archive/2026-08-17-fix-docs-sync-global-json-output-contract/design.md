# Design: Fix docs-sync global --json output contract

## Root Cause

The CLI callback stores `--json` in a module-level `_json_output` boolean and
configures JSON logging, but each command checks only its local `output` option:

```python
if output == "json":
    typer.echo(json.dumps(result, indent=2))
else:
    _print_check_report(result)
```

The global flag is never consulted at output dispatch time.

## Implementation

### `_effective_output()` helper

```python
def _effective_output(command_output: str) -> str:
    """Resolve the effective output mode from global --json and local --output."""
    return "json" if _json_output else command_output
```

### Per-command change

Replace `if output == "json":` with `if _effective_output(output) == "json":` at
every output dispatch point. The affected commands (based on grep) are:

- `check` (line ~96)
- `validate` (line ~194)
- `discover` (line ~279)
- `audit` (line ~442)
- `update` (line ~509)
- `sync` (line ~394)
- `pending` (line ~532)
- `list` (line ~555)

### Logging separation

JSON logging (`log_format="json"`) already writes to the configured log handler,
not stdout. No change needed there.

## Test Matrix

| Invocation | Expected stdout |
|---|---|
| `docs-sync check --repo F --output json` | Valid JSON (unchanged) |
| `docs-sync --json check --repo F` | Valid JSON (new) |
| `docs-sync check --repo F` (no flags) | Text report (unchanged) |
