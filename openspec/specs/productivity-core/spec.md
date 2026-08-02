# Productivity Core Specification

**Status:** Draft
**Date:** 2026-05-24
**Version:** 1.0

---

## Purpose

Productivity core provides version management, task running, environment automation, and file watching to streamline development workflow.

---

## Requirements

### Requirement: Workspace productivity tooling is standardized

The workspace SHALL standardize on Homebrew-managed CLI tools for productivity automation, shell helpers, and task execution, with mise, just, direnv, watchexec, atuin, and difftastic integrated at the workspace level.

#### Scenario: Fresh workspace setup
- **WHEN** a developer installs the workspace tooling set on a new machine
- **THEN** the standard productivity tools are available via Homebrew and the workspace configuration files are present

#### Scenario: Shell integration is loaded
- **WHEN** a developer opens a new shell in the workspace
- **THEN** mise, direnv, atuin, and the workspace aliases are active without manual setup

#### Scenario: Workspace tasks are discoverable
- **WHEN** a developer runs `just --list`
- **THEN** the shared workspace tasks are listed with the expected recipes

### Requirement: Version management with mise

The workspace SHALL use mise for managing multiple language versions (Node, Python, Go, Rust, Bun).

#### Scenario: mise configuration exists
- **WHEN** a developer clones the workspace
- **THEN** `.mise.toml` exists at workspace root with version specifications

#### Scenario: Language versions are managed
- **WHEN** `mise ls` is run
- **THEN** it shows all configured language versions

### Requirement: Task runner with just

The workspace SHALL use just as the task runner with standardized recipes.

#### Scenario: Justfile exists
- **WHEN** a developer clones the workspace
- **THEN** `Justfile` exists at workspace root with standard recipes

#### Scenario: Standard recipes are available
- **WHEN** `just --list` is run
- **THEN** recipes for audit, test, lint, install, clean, docs, update, and versions are listed

### Requirement: Environment automation with direnv

The workspace SHALL use direnv for auto-loading environment variables per project.

#### Scenario: direnv configuration exists
- **WHEN** a developer clones the workspace
- **THEN** `.envrc.template` exists with mise integration and workspace variables

#### Scenario: Environment loads automatically
- **WHEN** a developer enters the workspace directory
- **THEN** direnv loads the environment without manual intervention

### Requirement: File watching with watchexec

The workspace SHALL use watchexec for running commands when files change.

#### Scenario: watchexec is available
- **WHEN** a developer needs to watch file changes
- **THEN** `watchexec` command is available and functional

### Requirement: Shell history search with atuin

The workspace SHALL use atuin for shell history search with fuzzy matching.

#### Scenario: atuin is available
- **WHEN** a developer presses Ctrl+R
- **THEN** atuin provides fuzzy history search

### Requirement: Structural diff with difftastic

The workspace SHALL use difftastic for syntax-aware diffs.

#### Scenario: difftastic is available
- **WHEN** a developer runs git diff
- **THEN** difftastic provides syntax-aware diff output

---

## Integration

### Shell Configuration

```bash
# ~/.zshrc additions

# mise (must be before other tool hooks)
eval "$(mise activate zsh)"

# direnv
eval "$(direnv hook zsh)"

# atuin
eval "$(atuin init zsh)"
```

### Configuration Files

```
tdt/
├── .mise.toml
├── Justfile
├── .envrc.template
```

---

## Success Metrics

- All language versions managed by mise
- Just recipes cover all common workspace operations
- direnv auto-loads environment per project
- File watching works for development workflows
- Shell history search improves productivity
- Structural diffs enhance code review
