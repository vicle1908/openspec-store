# Delta Specification: jev-decision-runtime

## ADDED Requirements

### Requirement: Clean git working trees and fresh code graphs across SHB Jev repositories

All 13 `/Users/androidteam/Developer/shb/shb-*` repositories participating in the Jev System One runtime and CLI surface SHALL maintain clean committed git working trees (`git status --short` empty) and `FRESH` GitNexus and Graphify indexes (`indexed_commit == HEAD`).

#### Scenario: Post-archive Jev runtime and CLI fixes committed and indexed
- **WHEN** `shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`, `shb-observability`, `shb-ai-review`, and `shb-mcp-servers` are verified with `uv run pytest`, `uv run ruff check`, and `uv run mypy --strict`
- **THEN** all modified source and test files SHALL be committed to git so `git status --short` is empty across all 13 `shb/shb-*` repositories and `tdt/agent-core`
- **AND** `knowledge-status.sh` SHALL report `FRESH` for both GitNexus and Graphify across all 13 `shb/shb-*` repositories
