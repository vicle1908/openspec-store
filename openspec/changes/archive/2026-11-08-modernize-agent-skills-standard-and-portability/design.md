# Design

## Context

Our workstation ecosystem orchestrates multiple AI coding agents (Oh My Pi / OMP, Claude Code, Codex, Hermes, Cursor, Zed, OpenCode) across two primary skill directories:
- `~/Developer/.agents/skills/` (115 canonical shared skills, synced across agent profiles)
- `~/.omp/agent/managed-skills/` (106 OMP-managed runtime skills)

A technical audit against the official open Agent Skills specification (`agentskills.io` / `skills-ref`) revealed frontmatter schema violations across 18 locally-authored skills, hardcoded host paths across 15 OMP managed skills, lack of inline script dependency declarations in `github-actions-validation`, and the need to extend pre-flight checks in `sync-workspace-agent-skills.py`. See `proposal.md` for detailed motivation.

## Goals / Non-Goals

**Goals:**
- Bring all 18 locally-authored workspace skills and all 106 managed skills into 100% compliance with the `agentskills.io` specification schema (`ALLOWED_FIELDS`).
- Eliminate all hardcoded host usernames (`/Users/androidteam/`, `/Users/vinhlk/`) from skill bodies, scripts, and auxiliary references.
- Codify PEP 723 inline script metadata (`# /// script`) and `#!/usr/bin/env -S uv run` shebangs for bundled Python scripts (`validate_workflows.py`).
- Establish progressive disclosure boundaries (<500 lines for locally authored `SKILL.md`).
- Preserve all 64 upstream vendor skills tracked in `skills-lock.json` verbatim, maintaining complete lockfile immutability.
- Add automated specification validation to `sync-workspace-agent-skills.py --check`.

**Non-Goals:**
- Modifying or tampering with external vendor skills tracked in `skills-lock.json` (such as `ponytail`, `brightdata/*`, `temporalio/*`, or `browser-use`).
- Manually altering or forging `computedHash` values in `skills-lock.json`.
- Disabling or removing Claude Code native slash commands (`/opsx:*`).

## Decisions

### 1. Nesting Custom Vendor Fields under `metadata:` for 18 Locally-Authored Skills
- **Decision**: In the 18 locally-authored, untracked platform skills containing non-standard top-level fields (`user-invocable`, `argument-hint`, `version`, `author`, `platforms`), relocate these keys into the `metadata:` string-string map:
  - **7 AgentMemory skills**: `agentmemory-agents`, `agentmemory-architecture`, `agentmemory-config`, `agentmemory-hooks`, `agentmemory-mcp-tools`, `agentmemory-rest-api`, `write-agentmemory-skill` (`user-invocable: "false"`).
  - **10 Local session & memory action skills**: `commit-context`, `commit-history`, `forget`, `handoff`, `lesson`, `memory-discipline`, `recall`, `recap`, `remember`, `session-history` (`user-invocable: "true"`, `argument-hint: "..."`).
  - **1 Platform CI validation skill**: `github-actions-validation` (`version: "1.0.0"`, `author: "platform-team"`, `platforms: "linux,darwin"`).
  ```yaml
  ---
  name: recap
  description: Summarize recent user and agent activity across sessions...
  metadata:
    user-invocable: "true"
    argument-hint: "[days]"
  ---
  ```
- **Rationale**: `skills-ref validate` strictly permits only `name`, `description`, `license`, `allowed-tools`, `metadata`, and `compatibility`. Nesting preserves client-specific behavior while passing strict multi-agent validation. Because these 18 skills are platform-internal and untracked in `skills-lock.json`, modifying their frontmatters carries zero lockfile side effects.

### 2. Upstream Vendor Skill Exemption & Zero Lockfile Tampering
- **Decision**: All 64 vendor skills tracked in `skills-lock.json` (e.g. `DietrichGebert/ponytail`, `brightdata/skills`, `temporalio/skills`, `browser-use`) are strictly **exempt** from local frontmatter mutations.
- **Rationale**: Faking `computedHash` digests in `skills-lock.json` breaks upstream `skills update -y` idempotency, violates `agent-skill-distribution` and ponytail specification invariants, and causes upstream merge conflicts when updating packages. Leaving locked vendor skills untouched ensures `skills-lock.json` remains completely pristine and trusted.

### 3. Standardizing on PEP 723, Shebang & `uv run` for Bundled Python Scripts
- **Decision**: Require bundled Python scripts under `scripts/` to declare a `#!/usr/bin/env -S uv run` shebang and PEP 723 inline script metadata blocks, instructing agents to execute them directly or via `uv run scripts/<name>.py`:
  ```python
  #!/usr/bin/env -S uv run
  # /// script
  # requires-python = ">=3.11"
  # dependencies = [
  #     "pyyaml>=6.0",
  # ]
  # ///
  ```
- **Implementation in `validate_workflows.py`**:
  - Insert shebang and PEP 723 block on lines 1–8.
  - Retain runtime imports: `yaml` is guaranteed by `uv run` in the ephemeral virtualenv.
  - Preserve the 8-point automated pre-flight validation pipeline and non-interactive output contracts.
  - Update `github-actions-validation/SKILL.md` to instruct `uv run scripts/validate_workflows.py`.
- **Vendor Scripts**: The 8 scripts bundled inside locked vendor skills (`scrape/*`, `agent-onboarding/*`, `design-mirror/*`, `live-research/*`, `brightdata-proxy/*`) remain untouched to preserve vendor snapshot integrity.

### 4. Dynamic Home Expansion & Skill-Relative Path Resolution
- **Decision**: Replace all occurrences of `/Users/androidteam/` and other hardcoded home directories with `~`, `$HOME`, or skill-relative paths (`scripts/`, `references/`, `assets/`).
- **Scrubbing Scope**:
  - **15 OMP Managed Skills**: Scrub 41 matching lines across `agent-skills-standard-and-portability`, `browser-use-workstation-ops`, `kimi-code-standalone-migration`, `macos-tcc-permission-provisioning`, `mcp-router-fleet-and-bundle-verification`, `npx-skills-workstation-integration-audit`, `omniroute-fleet-model-catalog-rollout`, `tailscale-macos-cross-node-optimization`, `tailscale-macos-mesh-and-nat-audit`, `workspace-npx-skills-adoption`, `workspace-worktree-cleanliness-scan`, `workspace-worktree-cleanup-scan`, `workstation-homebrew-apply`, `archimate-agent-tooling-verification`, `restricted-icloud-copy-reconciliation`.
  - **3 Auxiliary References**: Scrub synthetic paths in `handoff/references/EXAMPLES.md`, `recap/references/EXAMPLES.md`, and `qi-hybrid-search/references/config-watcher.md`.
- **Rationale**: In a multi-workstation setup (`iosteam-mac-mini` with username `androidteam` vs `macbook-pro-m5` with username `vinhlk`), absolute path literals cause immediate execution failures. Skill-relative paths are universally portable across macOS, Linux, and containers.

### 5. Progressive Disclosure Factoring with Upstream Vendor Exemption
- **Decision**: For locally-authored and managed skills with instruction bodies exceeding 500 lines, extract auxiliary API reference tables and schemas into `references/REFERENCE.md`. Upstream vendor skills tracked via `skills-lock.json` (such as `scraper-builder` from `brightdata/skills` and `graphify` from `Graphify-Labs`) are explicitly exempt from local file splitting.
- **Rationale**: Preserving upstream vendor files avoids perpetual local merge conflicts and update overwrites during upstream refreshes, while local skills benefit from reduced context-token overhead during routine activation. All 18 locally-authored skills already remain well under 500 lines.

### 6. Automated Validation Gate in `sync-workspace-agent-skills.py`
- **Decision**: Implement `validate_skill_conformance(workspace: Path)` in `platform/openspec-store/scripts/sync-workspace-agent-skills.py` integrated into `--check` mode:
  - Asserts that top-level frontmatter keys match `{'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}` for locally-authored skills.
  - Verifies that `name` matches the directory name exactly and adheres to kebab-case regex `^[a-z0-9]+(-[a-z0-9]+)*$`.
  - Enforces description byte length <= 1,024 bytes.
  - Verifies zero occurrences of `/Users/` in `SKILL.md` files.
  - Verifies lockfile byte-equality and snapshot integrity on locked vendor skills.
- **Rationale**: Enforcing this check prevents regression during daily scheduled maintenance and CI runs without requiring any mutation to `skills-lock.json`.

## Risks / Trade-offs

- **Client Metadata Parsing**: Some clients may only inspect top-level YAML keys for custom features. Claude Code and modern agents gracefully parse or fall back when fields are nested under `metadata:`, whereas strict multi-agent validators reject invalid top-level keys entirely.
- **Vendor Non-Standard Fields**: Upstream vendor skills like `ponytail` or `brightdata` may continue to have top-level `argument-hint` or `user-invocable` in their upstream releases until upstream authors adopt `agentskills.io`. Exempting them prevents breaking their hash while accepting upstream's chosen format.
