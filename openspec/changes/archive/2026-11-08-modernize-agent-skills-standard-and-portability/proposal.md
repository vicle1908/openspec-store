# Proposal

## Why

Following an architectural audit against the official open Agent Skills specification (`agentskills.io` / `skills-ref` by Keith Lazuka @ Anthropic) and cross-workstation verification between `iosteam-mac-mini` and `macbook-pro-m5`, our current skill authoring and distribution approaches exhibit four critical forms of drift:

1. **Non-Standard YAML Frontmatter Fields in Locally-Authored Skills**: 18 locally-authored platform skills (`agentmemory-*`, `commit-*`, `recap`, `handoff`, `github-actions-validation`, etc.) place client-specific extension keys (`user-invocable`, `argument-hint`, `version`, `author`, `platforms`) at the top level of YAML frontmatter instead of encapsulating them within the specification's allowed `metadata:` dictionary.
2. **Machine-Specific Path Hardcoding**: 15 OMP managed skills contain hardcoded `/Users/androidteam/` absolute paths across 41 lines, which breaks skill execution and discovery on other nodes such as `macbook-pro-m5` (where the operator home is `/Users/vinhlk/`) and in containerized runtimes.
3. **Lack of Self-Contained Inline Script Dependencies**: Bundled Python scripts lack PEP 723 inline script metadata blocks and executable shebangs, relying on manual host `pip install` checks instead of zero-setup, reproducible execution via `uv run`.
4. **Absence of Specification Conformance Gates in Workspace Tooling**: `platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` validates directory existence, casing, and plugin container absence, but does not assert frontmatter schema whitelist compliance on locally-authored skills, or path portability.

Standardizing our locally-authored skills ensures 100% interoperability across all coding agents (Claude Code, Codex, Cursor, Hermes, OMP, OpenCode), eliminates cross-workstation path failure modes, and makes skill scripts fully self-contained while preserving external vendor skill immutability.

## What Changes

- **YAML Frontmatter Normalization for Locally-Authored Skills**:
  - Restrict top-level YAML frontmatter fields strictly to the `agentskills.io` specification whitelist: `name`, `description`, `license`, `allowed-tools`, `metadata`, and `compatibility`.
  - Migrate all tool-specific or client-specific properties (e.g. `user-invocable`, `argument-hint`, `version`, `author`) into the `metadata:` string-string map across the 18 locally-authored, untracked platform skills.
  - Enforce that `name` matches the parent directory name exactly and satisfies `^[a-z0-9]+(-[a-z0-9]+)*$`.
- **Strict Upstream Vendor Skill Exemption & Lockfile Invariance**:
  - All 64 vendor skills tracked in `skills-lock.json` (such as `ponytail` from `DietrichGebert/ponytail`, `brightdata/*`, `temporalio/*`, and `browser-use`) are strictly **exempt** from local frontmatter mutations and file splitting.
  - This prevents local divergence, eliminates any need to forge `computedHash` digests in `skills-lock.json`, and preserves 100% upstream `skills update -y` idempotency.
- **Machine-Agnostic Portability & Path Scrubbing**:
  - Replace all hardcoded `/Users/androidteam/` paths across managed and workspace skills with portable `$HOME`, `~`, or relative paths (`scripts/`, `references/`, `assets/`).
- **Self-Contained Script Architecture**:
  - Codify PEP 723 inline script metadata blocks (`# /// script ... dependencies = [...] ///`) with `#!/usr/bin/env -S uv run` shebangs in bundled Python scripts.
  - Require execution instructions in `SKILL.md` to invoke `uv run scripts/<name>.py` (or `bun run scripts/<name>.ts`) rather than assuming host-managed global packages.
  - Mandate non-interactive execution contracts (CLI flags/streams, zero TTY prompts, machine-readable JSON/TSV to stdout, diagnostics to stderr).
- **Progressive Disclosure Boundaries for Local Skills**:
  - Codify the 3-tier progressive disclosure model: Tier 1 (~100 tokens: name + description), Tier 2 (<500 lines / <5,000 tokens: `SKILL.md` body), and Tier 3 (on-demand: `references/`, `scripts/`, `assets/`).
  - Require locally-authored and managed skills exceeding 500 lines to offload auxiliary schemas, deep API catalogs, and secondary manuals into `references/`.
- **Automated Validation in Workspace Tooling**:
  - Enhance `platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` with an automated Agent Skills conformance check that enforces `ALLOWED_FIELDS` and zero `/Users/` paths on locally-authored skills, while verifying lockfile snapshot integrity on vendor-tracked skills.

## Capabilities

### New Capabilities
- `agent-skills-standard-and-portability`: Defines the normative specification for Agent Skills frontmatter schema compliance on locally-authored skills, upstream vendor lockfile immutability, PEP 723 self-contained script dependency execution, machine-agnostic path portability, progressive disclosure structure, and automated pre-flight integrity verification across the workspace.

## Impact

- **Locally-Authored Workspace Skills**: `~/Developer/.agents/skills/` (18 untracked platform skills normalized into `metadata:`).
- **Upstream Vendor Skills**: (64 locked skills preserved verbatim; zero tampering with `skills-lock.json`).
- **OMP Managed Skills**: `~/.omp/agent/managed-skills/` (15 managed skills path-scrubbed and normalized across 41 lines).
- **Maintenance Scripts**: `platform/openspec-store/scripts/sync-workspace-agent-skills.py` (enhanced validation).
- **Supported Coding Agents**: Claude Code, Codex, OMP, Hermes, Cursor, Zed, OpenCode.
