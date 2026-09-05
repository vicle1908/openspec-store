## 1. Audit
- [ ] 1.1 Inventory every `.tdt/deployments/*` manifest and LaunchAgent reference; verify paths and owners.
- [ ] 1.2 Compare live process executable paths and listening ports with manifests; verify no credential values are captured.
- [ ] 1.3 Write deployment inventory evidence with timestamps and discrepancies.
## 2. Reconcile
- [ ] 2.1 Correct only stale non-secret provenance fields after evidence review; verify manifests parse.
- [ ] 2.2 Re-run process/path checks and verify live services remain healthy.
## 3. Finalize
- [ ] 3.1 Validate, archive, and commit the change; verify store is clean except unrelated active changes.
