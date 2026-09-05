## Context
Several Python repositories and service deployments use uv-managed environments. Runtime ownership must be established before consolidation.
## Decisions
- LaunchAgent and container command paths are authoritative for live services.
- Repo `.venv` remains developer-owned unless proven unused.
- First pass is read-only; deletions require a separate approved retirement change.
## Risks / Trade-offs
- Removing a seemingly duplicate venv can break restart recovery; require process and plist evidence before proposing removal.
