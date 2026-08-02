# Productivity Core Specification

**Status:** Draft  
**Date:** 2026-05-24  
**Version:** 1.0

---

## ADDED Requirements

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

## 1. Overview

Productivity core provides version management, task running, environment automation, and file watching to streamline development workflow.

---

## 2. Requirements

### REQ-1: Version Management

**Tool:** mise  
**Purpose:** Manage multiple language versions (Node, Python, Go, Rust, Bun)  
**Configuration:** `.mise.toml` at workspace root

**Acceptance Criteria:**
- [ ] mise installed via Homebrew
- [ ] `.mise.toml` created with:
  - node 26.0.0
  - python 3.13
  - go 1.26.3
  - bun latest
- [ ] Shell integration added to `~/.zshrc`
- [ ] `mise ls` shows all installed tools

**Verification:**
```bash
mise --version && mise ls
mise exec -- node --version
mise exec -- python --version
```

---

### REQ-2: Task Runner

**Tool:** just  
**Purpose:** Run workspace tasks with simple syntax  
**Configuration:** `Justfile` at workspace root

**Acceptance Criteria:**
- [ ] just installed via Homebrew
- [ ] `Justfile` created with recipes:
  - `just audit` - run security scans
  - `just test` - run all project tests
  - `just lint` - run all linters
  - `just install` - install all dependencies
  - `just clean` - clean build artifacts
  - `just docs` - generate documentation
  - `just update` - update all dependencies
  - `just versions` - show tool versions
- [ ] `just --list` shows all recipes
- [ ] All recipes execute without errors

**Verification:**
```bash
just --list
just versions
just clean
```

---

### REQ-3: Environment Automation

**Tool:** direnv  
**Purpose:** Auto-load environment variables per project  
**Configuration:** `.envrc` template at workspace root

**Acceptance Criteria:**
- [ ] direnv installed via Homebrew
- [ ] `.envrc.template` created with:
  - mise integration
  - `.env` file loading
  - workspace root variable
  - local bin PATH addition
- [ ] Shell integration added to `~/.zshrc`
- [ ] direnv loads environment correctly when entering workspace

**Verification:**
```bash
direnv --version
cd ~/Developer/tdt && direnv allow
echo $TDT_ROOT  # Should show workspace root
```

---

### REQ-4: File Watching

**Tool:** watchexec  
**Purpose:** Run commands when files change  
**Configuration:** None needed

**Acceptance Criteria:**
- [ ] watchexec installed via Homebrew
- [ ] Can watch file changes in workspace
- [ ] Integrates with development workflow

**Verification:**
```bash
watchexec --version
watchexec --exts py,sh,md 'echo "File changed"' &
```

---

### REQ-5: Shell History Search

**Tool:** atuin  
**Purpose:** Search shell history with fuzzy matching and sync  
**Configuration:** None needed initially

**Acceptance Criteria:**
- [ ] atuin installed via Homebrew
- [ ] Shell integration added to `~/.zshrc`
- [ ] Can search history with `Ctrl+R`

**Verification:**
```bash
atuin --version
atuin sync 2>&1 || echo "atuin sync not configured yet"
```

---

### REQ-6: Structural Diff

**Tool:** difftastic  
**Purpose:** Syntax-aware diff tool for better code review  
**Configuration:** None needed

**Acceptance Criteria:**
- [ ] difftastic installed via Homebrew
- [ ] Can use as git diff driver optionally
- [ ] Shows syntax-aware diffs

**Verification:**
```bash
difft --version
echo "hello" > /tmp/a.txt
echo "world" > /tmp/b.txt
difft /tmp/a.txt /tmp/b.txt
```

---

## 3. Integration

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
└── openspec/changes/dev-tooling-audit-and-enhancement/specs/productivity-core/spec.md
```

---

## 4. Success Metrics

- All language versions managed by mise
- Just recipes cover all common workspace operations
- direnv auto-loads environment per project
- File watching works for development workflows
- Shell history search improves productivity
- Structural diffs enhance code review
