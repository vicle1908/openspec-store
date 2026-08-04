# Monitoring Plan: Post-Migration Observation

## Observation Period

- **Duration**: 24 hours after migration completion
- **Rollback deadline**: 24 hours post-migration

## Signals to Monitor

| Signal | Threshold | Escalation |
|--------|-----------|------------|
| `tdt config doctor` errors | > 0 | Immediate rollback |
| Consumer test failures | Any failure | Investigate, rollback if unresolved in 30min |
| Credential loading failures | Any `load_tdt_env()` error | Immediate rollback |
| Process crashes | Any segfault/traceback | Immediate rollback |

## Escalation Contacts

- Primary: Vinh Le (operator)
- Backup: None designated

## Rollback Trigger

Any of:
1. Doctor reports new errors post-migration
2. Consumer test suite fails
3. Credential loading fails for any consumer
4. Open file handle conflicts detected

## Post-Migration Checklist

- [ ] Doctor clean (or only pre-existing warnings)
- [ ] All 15 consumer smoke tests pass
- [ ] No new open file handles
- [ ] Scheduler config loads correctly
- [ ] 24-hour observation period passes
