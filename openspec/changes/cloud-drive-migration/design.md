## Context

Code projects and artifacts are spread across iCloud Drive, Google Drive, Desktop, and Documents. iCloud-hosted Git trees risk filesystem corruption, and cloud-local mirror state must be checked before deletion.

See proposal.md - Why.

## Goals / Non-Goals

**Goals:**
- Provide a safe, evidence-backed workflow that moves only approved iCloud projects into ~/Developer.
- Delete only approved duplicates and migration artifacts.
- Stop before every destructive operation until exact path-level approval is recorded.

**Non-Goals:**
- Bulk migration of all cloud data.
- Automatic deletion of personal documents or unknown-ownership paths.
- Trusting stale remote listing snapshots without reconciling them against local filesystem evidence.

## Decisions

### 1. iCloud projects → ~/Developer (mv, not cp+rm)

Use a same-volume move for approved code projects under ~/Library/Mobile Documents/com~apple~CloudDocs/project/ and verify destination presence plus source absence after each move.

### 2. Delete iCloud build artifacts only when individually approved

Delete each proposed artifact path individually rather than blanket-removing a parent directory.

### 3. Google Drive cleanup must be approval-gated and documented

Delete only exact approved duplicate or code-mirror paths and preserve documentation, rollback bundles, and personal data unless explicitly approved.

### 4. Desktop/Documents cleanup must preserve personal-looking paths by default

Treat Desktop and Documents as protected by default and delete only exact approved stubs or migration leftovers.

### 5. Destination bundle deletion only when verified redundant

Delete the go-microservices cleanup bundle only when the current repository state confirms it is redundant.

## Risks / Trade-offs

- Local and remote directory state may temporarily disagree; risk is mitigated by requiring current evidence before deletion.
- Cloud deletions may propagate; risk is mitigated by approval gates and documented rollback paths.
- Personal data may be misclassified; risk is mitigated by preserving protected paths unless explicitly approved.
