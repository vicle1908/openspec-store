## Context

See `proposal.md - Why`. The two target archives are immutable historical records: `openspec/changes/archive/2026-09-05-ecosystem-cleanup/` and `openspec/changes/archive/2026-09-04-fix-corrupted-brew-casks/`. Their checked task ledgers do not contain durable operational output. Current observations also show the two sideloaded app executables present, while `ai-review` and `agent-harness` have unrelated dirty worktrees and `tdt-scheduler` lacks a local virtual environment by design.

## Goals / Non-Goals

**Goals:**

- Create one corrective evidence register covering the two cleanup archives.
- Use metadata-only checks and explicit status classifications.
- Separate verified observations, archive claims, and user-owned blockers.
- Preserve enough provenance to detect future drift without storing secrets.

**Non-Goals:**

- No mutation of applications, worktrees, repositories, branches, or virtual environments.
- No interpretation of unrelated dirty paths as cleanup failures.
- No credential or provider remediation.

## Decisions

1. Store evidence under this change in `evidence/cleanup-verification.json` and `evidence/cleanup-verification.md`; both are corrective records, not edits to the archive.
2. Record hashes, modes, sizes, paths, and boolean existence results only. Omit credentials, raw command output, and application data.
3. Verify sideloaded apps using executable paths (`Wrapper/Runner.app/Runner` and `Wrapper/Telegram.app/Telegram`) in addition to plist paths.
4. Pin the authoritative 19-repository inventory as the 18 repositories listed in `/Users/androidteam/Developer/AGENTS.md:365-368` (`agent-core`, `agent-docs-sync`, `agent-harness`, `ai-harness-skills`, `ai-review`, `browser-cli`, `claude-code-provider-adapter`, `code-daily-scan`, `hermes-webui`, `jira-daily-reports`, `jira-epic-report`, `jira-kanban-from-spreadsheet`, `jira-skill`, `ops-automation-suite`, `tdt-core`, `tdt-observability`, `tdt-sheets`, `webhook-receiver`) plus `tdt-scheduler` (the archive's Docker-built `.venv` exception). Record the list and a sha256 digest of the ordered list file inside the evidence manifest; a partial live sample (such as the earlier 10-repository probe) is reconnaissance only and must not be promoted into the evidence manifest.
5. Record the manual reinstall gate conditionally: blocked and user-owned if executable verification fails; resolved/currently unnecessary if both binaries verify with existence, nonzero size, and executable mode, without claiming reinstall provenance.
6. Validate this change strictly before any implementation or archive operation.

## Risks / Trade-offs

- Filesystem presence checks prove current presence, not application integrity or provenance.
- Workspace state can change concurrently; evidence includes a timestamp and repository status snapshot.
- A corrective record can establish current facts but cannot retroactively make an original archive's prose evidence durable.
