# Design: Refresh Knowledge Tooling and Wiki Integrity

## Architecture Decisions

### AD1: Tooling upgrades via official package managers
- `gitnexus`: Installed globally via `npm install -g gitnexus@latest`.
- `graphify`: Managed via `uv tool upgrade graphifyy`.
- Platform skills: Deployed using `graphify install --platform <name>` for each supported assistant platform (`hermes`, `agents`, `claude`, `codex`).

### AD2: Wiki freshness and deterministic linting
- Wiki pages maintain a strict schema (`title`, `tags`, `created`, `updated`, `status`).
- Pages with `updated` older than 30 days are reviewed and timestamped once verified.
- `wiki-lint.py` implements a zero-byte stdout contract when clean, allowing Hermes cron to run in `no-agent` mode and suppress silent notifications on clean runs.

### AD3: Strict adherence to the Knowledge Refresh Contract
- Repositories with uncommitted changes (`DIRTY`) are safely skipped during scheduled and manual batch refreshes to prevent indexing unstable or transient intermediate states.
- Force-refresh is restricted to clean repositories or explicitly targeted single repositories.
- Generated `graphify-out/` changes in clean repos are committed cleanly to avoid chicken-and-egg commit equality staleness.

## Trade-offs

- **Immediate vs. Deferred Refresh for Dirty Repos**: Rather than force-cleaning dirty working trees across 19 repos, we preserve developer worktrees and defer index refresh until the respective owners commit clean revisions.
