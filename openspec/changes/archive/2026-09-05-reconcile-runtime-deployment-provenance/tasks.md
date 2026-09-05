## 1. Audit
- [x] 1.1 Inventory `~/.tdt/deployments/ai-review/state/deployment-manifest.json`, `~/.tdt/deployments/webhook-receiver/state/deployment-manifest.json`, `~/Library/LaunchAgents/com.tdt.ai-review.plist`, and `~/Library/LaunchAgents/com.tdt.webhook-receiver.plist`; verify paths and owners.
- [x] 1.2 Compare live process executable paths and listening ports 8090/8080 with those manifests using `ps`, `launchctl list`, and `lsof`; verify no credential values are captured.
- [x] 1.3 Write `evidence/deployment-inventory.json` and `evidence/deployment-inventory.md` with timestamps, paths, owners, and discrepancies.
## 2. Reconcile
- [x] 2.1 Correct only stale non-secret provenance fields in the two deployment manifests after evidence review; verify both files parse as JSON and contain no secret values.
- [x] 2.2 Re-run `launchctl list`, `ps`, and `lsof -i :8090 -i :8080`; verify live services remain healthy and executable paths match the corrected manifests.
## 3. Finalize
- [x] 3.1 Validate, archive, and commit the change; verify store is clean except unrelated active changes.
