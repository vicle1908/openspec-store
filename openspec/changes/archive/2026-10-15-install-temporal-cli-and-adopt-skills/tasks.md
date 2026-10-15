# Tasks

## 1. Toolchain Installation

- [x] 1.1 Install official Temporal CLI via Homebrew to `/opt/homebrew/bin/temporal` and verify `temporal --version` exits with code 0 reporting v1.9.1
- [x] 1.2 Verify `/opt/homebrew/bin/temporal` is executable in non-interactive subshells and prints development server help via `temporal server start-dev --help`

## 2. Skill Adoption and Multi-Agent Discovery

- [x] 2.1 Add official `temporalio/skill-temporal-developer` to canonical workspace skills root `~/Developer/.agents/skills/` via `npx skills add`
- [x] 2.2 Add official `temporalio/skill-temporal-ops` to canonical workspace skills root `~/Developer/.agents/skills/` via `npx skills add`
- [x] 2.3 Run `sync-workspace-agent-skills.py --check` and verify zero malformed entries across all agent harnesses

## 3. OpenSpec Change Authoring and Validation

- [x] 3.1 Author proposal, design, tasks, and new capability specification `workstation-temporal-toolchain`
- [x] 3.2 Validate change strictly against all store rules via `openspec validate --all --strict --store openspec-store`
