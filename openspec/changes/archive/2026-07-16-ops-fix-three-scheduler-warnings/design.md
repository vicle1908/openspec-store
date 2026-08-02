# Design: ops-scheduler-warning-hygiene

## Three independent sub-changes, one umbrella spec

The three warnings live in three different repos and three different
code paths. The umbrella change pulls them together under a single
spec because they share a single operator-visible intent ("make the
scheduler log signal cleaner") and a single validation step
(restart the scheduler and grep the log). Keeping them as separate
changes would multiply the validation cost without operational
benefit — there is no scenario where the operator wants to ship
one and not the others.

## Sub-change 1 — Timezone alias map

### Code

`jira-daily-reports/src/jira_daily_reports/person_worklog_source.py`,
lines 57–71. The change is local to `_parse_report_timezone`:

```python
_REPORT_TZ_ALIASES: dict[str, str] = {
    "Asia/Saigon": "Asia/Ho_Chi_Minh",  # obsolete IANA alias; modern zoneinfo since tzdata 2018c
}

def _parse_report_timezone(name: str | None) -> Any:
    import zoneinfo
    if not name:
        return zoneinfo.ZoneInfo("UTC")
    canonical = _REPORT_TZ_ALIASES.get(name, name)
    try:
        return zoneinfo.ZoneInfo(canonical)
    except Exception:
        logger.warning("worklog_invalid_timezone tz=%s — falling back to UTC", name)
        return zoneinfo.ZoneInfo("UTC")
```

### Why a static map, not a broader alias resolver?

- The list of obsolete IANA aliases is small and stable (`Asia/Saigon`
  is the only one we have hit in 24+ months of operation).
- A static map is auditable in code review; a heuristic would have to
  guess the canonical name and might break when tzdata adds new aliases.
- The map is colocated with `_parse_report_timezone`, so future
  contributors see it together with the warning it suppresses.

### Why the warning text stays the same?

The spec already says: "AND it SHALL log a `worklog_invalid_timezone tz=<name>`
warning" (line 326 of
`openspec/changes/jira-person-capacity-worklog-mode/specs/person-capacity-worklog-mode/spec.md`).
We are adding a *silent success path* alongside the warning, not
removing the warning. Operators who rely on the warning to detect a
genuinely misconfigured `PERSON_CAPACITY_TIMEZONE` still see it.

## Sub-change 2 — Catalog remap warning dedupe

### Code

`jira-daily-reports/src/jira_daily_reports/catalog/differ.py`,
around line 73. The change is to *defer* warning emission from
the per-row loop to a final pass over a collected `dict[tuple, list]`.

Current code (lines 60–81): for each `new_row`, if the alt-key matches
a different row than the PK-key, append a `warn` string to
`warnings` immediately.

New code: for each `new_row`, instead of appending `warn`, do

```python
remap_collisions.setdefault((new_row.kind, new_row.name), []).append(new_row.field_id)
```

After the loop, for each `(kind, name) → [field_ids]` entry, emit
one warning:

```python
for (kind, name), fids in remap_collisions.items():
    sample = fids[:5]
    suffix = "..." if len(fids) > 5 else ""
    warn = (
        f"catalog.diff.primary_key_remap kind={kind} name={name!r} "
        f"collisions={len(fids)} field_ids={sample}{suffix}"
    )
    logger.warning(warn)
    warnings.append(warn)
```

`CatalogDelta` gains one new field:

```python
primary_key_remap_collisions: dict[tuple[str, str], list[str]] = field(default_factory=dict)
```

The CLI catalog subcommand appends one summary print line:

```python
total = sum(len(v) for v in delta.primary_key_remap_collisions.values())
print(
    f"catalog.diff.primary_key_remap "
    f"unique_collisions={len(delta.primary_key_remap_collisions)} "
    f"total_field_ids={total}"
)
```

### Why a new field on `CatalogDelta`?

A new field preserves the full diagnostic — the operator still wants
to know *which* 200 field IDs collided on the same `(Kind, Name)` slot.
Deduplicating the log lines does not lose information; the structured
field carries it. This is a strict upgrade: more data, less noise.

### Why one warning per pair, not one per snapshot row?

The `(Kind, Name)` slot is a single resource. Reporting it 200 times
in one refresh is repetitive — the first message already told the
operator which row lost the slot. The new field exposes the
collision count and the field-id sample so the operator can act
without re-parsing the log.

## Sub-change 3 — Env-loader diagnostics

### Code

`tdt-core/src/tdt_core/env.py`, replace `load_tdt_env()`
(lines 27–53). Add a private `_LogCaptureHandler` class and a
module-level `_last_load_diagnostics` list.

```python
class _LogCaptureHandler(logging.Handler):
    """Append each record to a shared list, as a dict."""

    def __init__(self, sink: list[dict[str, Any]]) -> None:
        super().__init__(level=logging.WARNING)
        self._sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._sink.append({
                "logger": record.name,
                "level": record.levelname,
                "msg": record.getMessage(),
                "line": _extract_dotenv_line(record),
                "key_attempted": _extract_dotenv_key(record),
            })
        except Exception:
            # Never let the capture handler break loading.
            pass


def _extract_dotenv_line(record: logging.LogRecord) -> int | None:
    msg = record.getMessage()
    m = re.search(r"line\s+(\d+)", msg)
    return int(m.group(1)) if m else None


def _extract_dotenv_key(record: logging.LogRecord) -> str | None:
    """Best-effort: dotenv's 'could not parse' doesn't carry the key.

    Fall back to the dict of variables the loader just attempted to set.
    """
    return _last_attempted_key  # populated by load_dotenv's caller
```

`load_tdt_env()` wraps the call sites:

```python
def load_tdt_env() -> None:
    global _loaded, _last_load_diagnostics
    if _loaded:
        return
    from dotenv import load_dotenv
    _last_load_diagnostics = []
    capture = _LogCaptureHandler(_last_load_diagnostics)
    dotenv_logger = logging.getLogger("dotenv")
    dotenv_logger.addHandler(capture)
    try:
        for path in (tdt_root() / ".env", Path(".") / ".env"):
            if path.exists():
                _last_attempted_key = _peek_key_at_parse_failure(path)
                load_dotenv(path)
    finally:
        dotenv_logger.removeHandler(capture)
    _loaded = True


def last_load_diagnostics() -> list[dict[str, Any]]:
    """Return the list of diagnostic records from the most recent load."""
    return list(_last_load_diagnostics)
```

### Why wrap instead of replace?

The `deployable-env-loading` baseline
(`openspec/specs/deployable-env-loading/spec.md`) explicitly says:

> AND python-dotenv SHALL log a warning for the malformed line

If we replace the call with our own parser, we lose the spec-mandated
log line. If we add a capture handler, both the spec-mandated log
and the new diagnostic coexist. This is the same pattern as the
TDT observability stack already uses (a capture handler on
`opentelemetry`).

### Why not use `dotenv.main._walk_to_root`'s internal Binding?

`python-dotenv`'s `Binding` objects carry the source line and the
attempted key, but accessing them requires reaching into private
API. A capture handler on the public `dotenv` logger is the stable
contract.

## Validation

After all three sub-changes land:

```bash
docker compose -f agent-core/compose.yaml restart scheduler
sleep 60
docker compose -f agent-core/compose.yaml exec -T scheduler grep -c worklog_invalid_timezone /home/agent/.tdt/logs/jira-reports.log
# expected: 0

docker compose -f agent-core/compose.yaml exec -T scheduler grep -c catalog.diff.primary_key_remap /home/agent/.tdt/logs/jira-reports.log
# expected: <= 20 (one per unique (Kind, Name) collision; not 280)

docker compose -f agent-core/compose.yaml exec -T scheduler grep -c "python-dotenv could not parse" /home/agent/.tdt/logs/scheduler-entrypoint.log
# expected: 1 BEFORE the env-file repair, 0 AFTER
```

The env-file repair is tracked as a separate operator action in
`tasks.md` so the code change and the env change are auditable
independently.
