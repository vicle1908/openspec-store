# Cloud Drive Migration Inventory

Read-only inventory captured 2026-09-05. No files were moved or deleted.

| Path | Owner classification | Approximate size | Proposed action |
|---|---|---:|---|
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/vds/` | REVIEW_REQUIRED; code/data ownership unconfirmed | 8.0G | Do not move without explicit path approval and checksum comparison |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/microservices/` | REVIEW_REQUIRED; code tree | 604M | Compare with canonical workspace before any move |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/airbridge/` | REVIEW_REQUIRED | 12K | Inspect only; no action proposed |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/camunda/` | REVIEW_REQUIRED | 12K | Inspect only; no action proposed |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/camunda-async/` | REVIEW_REQUIRED | 0B | Inspect only; no action proposed |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/camunda7/` | REVIEW_REQUIRED | 40K | Inspect only; no action proposed |
| `~/Library/Mobile Documents/com~apple~CloudDocs/project/tmz/` | REVIEW_REQUIRED | 8K | Inspect only; no action proposed |
| `~/My Drive/TDT (1)/` | REVIEW_REQUIRED; possible code mirror | 2.9G | Compare with canonical repositories; no deletion |
| `~/My Drive/VinID/` | PROTECTED/REVIEW_REQUIRED; ownership unclear | 2.3G | Preserve; no deletion |
| `~/My Drive/tdt/` | REVIEW_REQUIRED; possible code mirror | 6.9G | Compare with canonical repositories; no deletion |
| `~/Desktop/` | PROTECTED by default | 184K | No action |
| `~/Documents/` | PROTECTED by default | 104K | No action |

The required approval gate remains open. Exact source paths, destination paths, and destructive targets require explicit approval before mutation tasks can begin. Checksums, Git status, and rclone metadata were not asserted where recursive inspection timed out; this evidence does not authorize any operation.
