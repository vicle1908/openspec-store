## Context

Three Jira epic-reporting changes were archived after implementation and manual verification. Later independent review found narrower evidence gaps: optional empty collections were not each covered by explicit dashboard tests; spreadsheet health and capacity behavior had diverged from detailed historical expectations; filtering was absent; and archived task checkboxes overstated deferred spreadsheet work. Canonical specs already describe the intended capability at a stable level and use `tdt-core` and `tdt-sheets` correctly.

## Goals / Non-Goals

**Goals:**

- Close the identified behavior and test gaps in `jira-epic-report` under one active OpenSpec change.
- Keep manual Jira smoke verification distinct from hermetic automated tests.
- Make risk, status, health, and utilization semantics explicit and observable.
- Preserve stakeholder-owned workbook tabs and existing authenticated `tdt-sheets` flows.

**Non-Goals:**

- Reopen historical archives or erase their original artifacts.
- Require live Jira or Google credentials in the unit-test suite.
- Add dependencies or bypass `tdt_core.clients` and `tdt-sheets` factories.

## Decisions

### Use fixture-backed edge tests plus a documented live smoke procedure

Empty subtasks, bugs, sprints, and items are deterministic and SHALL be tested with fixtures. Live Jira verification remains a manual smoke procedure that records date, scope, command class, and output artifacts without storing credentials or Jira payloads.

### Resolve thresholds through configuration, not duplicate constants

Risk and dashboard code SHALL consume named effective configuration values. Tests SHALL assert defaults and overrides. Completion weights SHALL have one authoritative mapping or an explicit documented translation when dashboard-only statuses are normalized.

### Never label item-count proxies as time utilization

Effective utilization requires logged effort, planned estimate, and blocked time from authoritative inputs. When those values are absent, the spreadsheet SHALL display an unavailable state and MAY show a separately named item-flow metric. Role grouping is conditional on normalized role data.

### Keep `tdt-sheets` as the authenticated integration boundary

The reporter continues to use public `tdt-sheets` reads, writes, and clears. Structural Google API operations may use the authenticated backend exposed by the same client until public equivalents exist. Filter and formatting failures remain managed-output failures.

## Risks / Trade-offs

- **Live smoke runs are not reproducible in CI** -> Preserve a hermetic suite and document manual evidence separately.
- **Capacity inputs may remain unavailable for some projects** -> Render unavailable states and avoid misleading percentages.
- **Threshold alignment may alter report labels** -> Add characterization tests and document the chosen defaults before changing output.
- **Role data differs across Jira projects** -> Normalize optional input and retain an ungrouped fallback.

## Migration Plan

1. Add characterization and edge tests before changing implementation.
2. Align configuration, analyzer, and reporter semantics with the delta specs.
3. Add spreadsheet filtering and truthful capacity/role behavior.
4. Update architecture and verification records, then run ruff, mypy, pytest, and strict OpenSpec validation.
5. Roll back individual reporter changes if managed workbook validation fails; no data migration is required.

## Open Questions

- Which Jira field or planning source is authoritative for role across all supported projects?
- Is blocked time available directly, or must it be derived from status-transition history?
- Should existing four-tier health labels remain while thresholds are aligned, or should output use three canonical traffic-light labels?
