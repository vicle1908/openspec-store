## MODIFIED Requirements

### Requirement: Public module-level cleanup helpers

The system SHALL provide public module-level functions `cancel_stale_error_workflows`
and `cancel_stale_enqueued_workflows` in `tdt_core.scheduler.cli`. The original
underscore-prefixed names SHALL remain as thin delegating wrappers so existing
internal callers and tests continue to work without modification.

#### Scenario: Public helpers exist and are callable

- **WHEN** `from tdt_core.scheduler.cli import cancel_stale_error_workflows` is
  executed
- **THEN** the import SHALL succeed and the function SHALL be callable with
  `(engine: SchedulerEngine, *, current_version: str | None = None, ...)`

#### Scenario: Legacy underscore-prefixed names still work

- **WHEN** `from tdt_core.scheduler.cli import _cancel_stale_error_workflows` is
  executed
- **THEN** the import SHALL succeed and the function SHALL behave identically to
  the new public `cancel_stale_error_workflows` (delegation, not a copy)

### Requirement: Default error_class_names tuple

The system SHALL default `_cancel_stale_error_workflows` (and its public alias
`cancel_stale_error_workflows`) to match the following exception classes:

```python
(
    "ModuleNotFoundError",
    "AttributeError",
    "ImportError",
    "UnpicklingError",
    "FileNotFoundError",
    "OSError",
    "subprocess.CalledProcessError",
    "subprocess.SubprocessError",
)
```

#### Scenario: Default tuple catches real-world stale exceptions

- **WHEN** the cleanup function encounters an `ERROR` row whose pickled
  exception decodes to `subprocess.CalledProcessError` with `returncode=128`
- **THEN** the row SHALL be cancelled (class name matches the default tuple)

- **WHEN** the cleanup function encounters an `ERROR` row whose pickled
  exception decodes to `FileNotFoundError(2, "No such file or directory")`
- **THEN** the row SHALL be cancelled

#### Scenario: Callers may override the default tuple

- **WHEN** `cancel_stale_error_workflows(engine, current_version=None, error_class_names=("MyError",))` is called
- **THEN** the function SHALL use ONLY the caller-provided `("MyError",)` tuple,
  not the default — overrides are explicit and complete