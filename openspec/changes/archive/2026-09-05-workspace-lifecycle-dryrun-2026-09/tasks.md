## 1. Observation Collection

- [x] 1.1 Build observation JSON for orca residue: the 6 orphaned checkout dirs under `~/orca/workspaces/agent-core/`, empty `tdt-core`/`tdt-scheduler` orca dirs, and `~/orca/workspaces/openspec-store/review-hermes-cron` with git/orca/runtime facts. Verify: JSON validates against the `observations.py` contract shape.
- [x] 1.2 Build observation JSON for workspace-root untracked files: omniroute review bundles ×6, `go-microservices-cleanup-20260817.bundle`, `--help`, `yield`, `context.md`, `icloud-cleanup-plan.md`, `check_spec_alignment.py`, `skills-lock.json`, `GEMINI.md`, `tdt-v2-accept/`. Verify: each entry carries authority, path, observed_at.
- [x] 1.3 Build observation JSON for empty dirs (`deployments/`, `poems-mobile3-android/`, `poems-mobile3-ios/`), stray repos (`wiki-mcp-server/`, `wiki-cron-validator/`, `ntu-keynote/`, `workspace-python-template/`, `docs/`), and `review-hermes-cron` git facts (8 unique commits, branch state). Verify: file-count and mtime facts recorded.
- [x] 1.4 Build observation JSON for `tdt/` tree including live `com.tdt.ai-review` service facts (plist ProgramArguments, running PID, port 8090) and `~/.tdt/deployments` comparison facts. Verify: runtime authority entries present with process evidence.

## 2. Dry-Run Execution

- [x] 2.1 Run `workspace-lifecycle.py --observations <file> --retention ~/Developer/.workspace-retention/retention-inventory.json` and produce manifest + summary in `~/Developer/.workspace-lifecycle/`. Verify: exit 0, manifest written, no mutation flags.
- [x] 2.2 Verify classification results respect the retention inventory: orca-root-derived entries not marked reclaimable, live-service paths PROTECTED, unknown-ownership paths REVIEW_REQUIRED. Verify: spot-check at least 5 classifications against spec precedence.
- [x] 2.3 Copy manifest, summary, and observation file into the change's `evidence/` directory. Verify: files exist and sizes match the runtime output.

## 3. Repo Hygiene (gitignore normalization)

- [x] 3.1 Add `.claude/` to `.gitignore` in the 16 repos missing it (agent-docs-sync, agent-harness, ai-review, browser-cli, code-daily-scan, jira-daily-reports, jira-epic-report, jira-kanban-from-spreadsheet, jira-skill, ops-automation-suite, tdt-observability, tdt-sheets, webhook-receiver, claude-code-provider-adapter, tdt-scheduler, ai-harness-skills if still missing after recheck). Verify: `git status --short` shows no `?? .claude/` in any repo.
- [x] 3.2 Commit each repo's `.gitignore` change with message `chore: ignore .claude/ agent-local config directory`. Verify: all 19 repos report clean status afterward.

## 4. Final Verification

- [x] 4.1 Re-scan workspace root and orca dirs for any new unclassified residue since research. Verify: no unobserved candidates appeared; any found are appended to evidence with classification notes.
- [x] 4.2 Record follow-up recommendations in evidence: (a) orca orphan checkouts need a retention-inventory amendment after agent-state proof, (b) `tdt/` ai-review migration is a runtime-owner change, (c) root junk files with RECLAIMABLE classification are ready for a future approved-retirement change. Verify: recommendations reference manifest classifications.
