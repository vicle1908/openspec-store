# Tasks

## 1. Frontmatter Normalization for 18 Locally-Authored Skills

- [x] 1.1 Migrate non-standard top-level YAML keys (`user-invocable`, `argument-hint`) into `metadata:` across the 7 AgentMemory skills:
  - `~/Developer/.agents/skills/agentmemory-agents/SKILL.md`
  - `~/Developer/.agents/skills/agentmemory-architecture/SKILL.md`
  - `~/Developer/.agents/skills/agentmemory-config/SKILL.md`
  - `~/Developer/.agents/skills/agentmemory-hooks/SKILL.md`
  - `~/Developer/.agents/skills/agentmemory-mcp-tools/SKILL.md`
  - `~/Developer/.agents/skills/agentmemory-rest-api/SKILL.md`
  - `~/Developer/.agents/skills/write-agentmemory-skill/SKILL.md`
- [x] 1.2 Migrate non-standard top-level YAML keys (`user-invocable`, `argument-hint`) into `metadata:` across the 10 local session/memory action skills:
  - `~/Developer/.agents/skills/commit-context/SKILL.md`
  - `~/Developer/.agents/skills/commit-history/SKILL.md`
  - `~/Developer/.agents/skills/forget/SKILL.md`
  - `~/Developer/.agents/skills/handoff/SKILL.md`
  - `~/Developer/.agents/skills/lesson/SKILL.md`
  - `~/Developer/.agents/skills/memory-discipline/SKILL.md`
  - `~/Developer/.agents/skills/recall/SKILL.md`
  - `~/Developer/.agents/skills/recap/SKILL.md`
  - `~/Developer/.agents/skills/remember/SKILL.md`
  - `~/Developer/.agents/skills/session-history/SKILL.md`
- [x] 1.3 Migrate non-standard top-level YAML keys (`version`, `author`, `platforms`) into `metadata:` in `~/Developer/.agents/skills/github-actions-validation/SKILL.md`
- [x] 1.4 Verify all 64 vendor skills tracked in `~/Developer/.agents/skills-lock.json` are preserved verbatim without frontmatter edits or lockfile modifications
- [x] 1.5 Verify directory name and `name` frontmatter field equality across all workspace skills (`~/Developer/.agents/skills/`) and managed skills (`~/.omp/agent/managed-skills/`)

## 2. Portability & Machine Path Scrubbing

- [x] 2.1 Replace hardcoded `/Users/androidteam/` absolute paths with portable `$HOME`, `~`, or relative paths across the 15 OMP managed skills:
  - `~/.omp/agent/managed-skills/agent-skills-standard-and-portability/SKILL.md`
  - `~/.omp/agent/managed-skills/browser-use-workstation-ops/SKILL.md`
  - `~/.omp/agent/managed-skills/kimi-code-standalone-migration/SKILL.md`
  - `~/.omp/agent/managed-skills/macos-tcc-permission-provisioning/SKILL.md`
  - `~/.omp/agent/managed-skills/mcp-router-fleet-and-bundle-verification/SKILL.md`
  - `~/.omp/agent/managed-skills/npx-skills-workstation-integration-audit/SKILL.md`
  - `~/.omp/agent/managed-skills/omniroute-fleet-model-catalog-rollout/SKILL.md`
  - `~/.omp/agent/managed-skills/tailscale-macos-cross-node-optimization/SKILL.md`
  - `~/.omp/agent/managed-skills/tailscale-macos-mesh-and-nat-audit/SKILL.md`
  - `~/.omp/agent/managed-skills/workspace-npx-skills-adoption/SKILL.md`
  - `~/.omp/agent/managed-skills/workspace-worktree-cleanliness-scan/SKILL.md`
  - `~/.omp/agent/managed-skills/workspace-worktree-cleanup-scan/SKILL.md`
  - `~/.omp/agent/managed-skills/workstation-homebrew-apply/SKILL.md`
  - `~/.omp/agent/managed-skills/archimate-agent-tooling-verification/SKILL.md`
  - `~/.omp/agent/managed-skills/restricted-icloud-copy-reconciliation/SKILL.md`
- [x] 2.2 Scrub hardcoded developer username paths in workspace auxiliary references:
  - `~/Developer/.agents/skills/handoff/references/EXAMPLES.md` (replace `/Users/androidteam/...` with generic test path)
  - `~/Developer/.agents/skills/recap/references/EXAMPLES.md` (replace `/Users/androidteam/...` with generic test path)
  - `~/Developer/.agents/skills/qi-hybrid-search/references/config-watcher.md` (replace `/Users/lekhanhvinh/...` with `$HOME/...`)
- [x] 2.3 Verify zero occurrences of `/Users/` across all `SKILL.md` files in `~/Developer/.agents/skills/` and `~/.omp/agent/managed-skills/`

## 3. Self-Contained Scripts & PEP 723 Dependency Declaration

- [x] 3.1 Inject `#!/usr/bin/env -S uv run` shebang and PEP 723 inline script metadata block declaring `dependencies = ["pyyaml>=6.0"]` and `requires-python = ">=3.11"` into `~/Developer/.agents/skills/github-actions-validation/scripts/validate_workflows.py`
- [x] 3.2 Update execution instructions in `~/Developer/.agents/skills/github-actions-validation/SKILL.md` to document direct `./scripts/validate_workflows.py` and `uv run scripts/validate_workflows.py` execution
- [x] 3.3 Verify all 8 upstream vendor scripts across `scrape`, `agent-onboarding`, `design-mirror`, `live-research`, and `brightdata-proxy` are preserved verbatim
- [x] 3.4 Audit bundled scripts to ensure non-interactive execution contracts (zero TTY prompts, machine-readable output to stdout, diagnostics to stderr, exit codes)

## 4. Progressive Disclosure Factoring for Local Skills

- [x] 4.1 Audit instruction line counts for locally-authored and managed skills, verifying that all local skills remain under 500 lines
- [x] 4.2 Enforce formal exemption for upstream vendor skills (`scraper-builder`, `graphify`) from local file splitting to prevent upstream merge conflicts

## 5. Automated Validation & Workspace Tooling

- [x] 5.1 Implement `validate_skill_conformance()` in `~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` asserting:
  - Allowed frontmatter keys (`ALLOWED_FIELDS = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}`) on locally-authored skills
  - Frontmatter `name` equality with parent directory and regex `^[a-z0-9]+(-[a-z0-9]+)*$`
  - Description byte cap (`<= 1024` UTF-8 bytes)
  - Zero hardcoded host user `/Users/` paths
  - Verbatim byte-equality and snapshot integrity on the 64 locked vendor skills
- [x] 5.2 Execute `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` and verify clean exit status across all 115 canonical skill roots
