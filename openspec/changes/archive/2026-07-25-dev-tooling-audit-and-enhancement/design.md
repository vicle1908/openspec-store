[Reading 400 lines from start (total: 400 lines, 0 remaining)]

# Dev Tooling Audit & Enhancement - Design

**Status:** Draft  
**Date:** 2026-05-23  
**Version:** 1.1 (Homebrew-First)

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    TDT Workspace Tooling                          │
│                   (All via Homebrew)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Security Layer          Productivity Layer    Quality Layer    │
│  ┌────────────────┐    ┌────────────────┐   ┌──────────────┐  │
│  │ gitleaks       │    │ mise           │   │ xh (HTTP)    │  │
│  │ shellcheck     │    │ just           │   │ yq (YAML)    │  │
│  │ shfmt          │    │ direnv         │   │ sd (replace) │  │
│  │ actionlint     │    │ watchexec      │   │ dust (disk)  │  │
│  │ pre-commit     │    │ atuin          │   │ tokei (code) │  │
│  │ trivy          │    │ difftastic     │   │ hyperfine    │  │
│  └────────┬───────┘    └────────┬───────┘   └──────┬───────┘  │
│           │                    │                   │           │
│           └────────────────────┼───────────────────┘           │
│                                │                               │
│                    Language Layer                               │
│              ┌──────────────────────────┐                       │
│              │ rustup-init + cargo      │                       │
│              │ pnpm (npm alternative)   │                       │
│              │ npm-check-updates        │                       │
│              └──────────────────────────┘                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Total: 24 tools, all installed via `brew install`**

---

## 2. Homebrew-First Design Decisions

### Decision 1: All CLI Tools via Homebrew

**Rationale:**
- Centralized package management (single manager for all CLI tools)
- Automatic updates via `brew upgrade`
- Consistent dependency resolution
- No mixing of installation methods
- Easy rollback with `brew uninstall`
- Shared dependencies between tools

**Impact:** 24 tools, one manager. No npm global, no cargo install, no pip install for CLI tools.

### Decision 2: npm Global for AI/MCP Only

**Rationale:**
- AI/MCP packages (`@earendil-works/pi-coding-agent`, `desktop-commander`, etc.) don't have Homebrew equivalents
- These are specialized Node.js packages that require npm runtime
- Keep existing 23 npm global packages as-is
- No new npm global packages added

**Impact:** npm global stays for AI/MCP, Homebrew for everything else.

### Decision 3: Keep Existing Homebrew Packages

**Rationale:**
- 112 existing packages are well-managed
- Tools like `fzf`, `fd`, `ripgrep`, `bat`, `eza` are optimal
- No need to replace, only augment with missing capabilities

**Impact:** 112 existing + 24 new = 136 total Homebrew packages.

### Decision 4: mise Instead of nvm/fnm/pyenv

**Rationale:**
- Single tool manages all language versions
- `.mise.toml` per-project configuration
- No shell startup overhead like nvm
- Complements existing `uv` for Python

**Impact:** Disable existing nvm/fnm hooks if any, use mise for all version management.

### Decision 5: just Instead of Makefile for Workspace Tasks

**Rationale:**
- Justfile syntax is cleaner (no tab hell)
- Better error messages
- Built-in recipe grouping and documentation
- Works well with mise for tool versioning

**Impact:** Existing Makefiles in projects stay (for builds), `Justfile` at workspace root for cross-project operations.

### Decision 6: xh Complementary to curl

**Rationale:**
- `xh` better for interactive use (JSON output, syntax highlighting)
- `curl` better for scripts and automation
- Both coexist without conflict

**Impact:** Interactive HTTP debugging uses `xh`, scripts continue using `curl`.

---

## 3. Tool Compatibility Matrix

### Coexistence

| Tool | Conflicts With | Resolution |
|------|---------------|------------|
| `mise` | `nvm`, `fnm`, `pyenv` | Disable old managers, use mise |
| `just` | `make` | Keep make for builds, just for tasks |
| `xh` | `curl` | Both coexist, different use cases |
| `sd` | `sed` | Both coexist, sd for simple patterns |
| `dust` | `du` | Both coexist, dust for interactive |
| `gdu` | `ncdu` | Both coexist, gdu faster |
| `starship` | Custom PS1 | Replace PS1 with starship |
| `direnv` | Manual .env loading | direnv auto-loads .env |
| `pre-commit` | Manual linting | pre-commit runs linters automatically |
| `atuin` | Shell history | Replaces shell history with searchable DB |
| `difftastic` | `git diff` | Used as git diff driver optionally |
| `trivy` | None | Standalone security scanner |

### Shell Integration

```bash
# ~/.zshrc additions (at the end)

# mise (must be before other tool hooks)
eval "$(mise activate zsh)"

# direnv
eval "$(direnv hook zsh)"

# atuin (shell history)
eval "$(atuin init zsh)"

# starship (must be at the end)
eval "$(starship init zsh)"

# Custom aliases for TDT workspace
alias tdt='cd /Users/lekhanhvinh/Developer/tdt'
alias j='just'
alias ja='just audit'
alias jt='just test'
alias jl='just lint'
alias ji='just install'
alias jc='just clean'
alias jv='just versions'
alias jd='just docs'
alias ju='just update'
```

---

## 4. Security Design

### gitleaks Configuration

```toml
# .gitleaks.toml
title = "TDT Workspace Gitleaks Config"

[extend]
useDefault = true

[allowlist]
description = "Allowlist for known false positives"
paths = [
    '''\.env\.example$''',
    '''\.env\.template$''',
    '''\.env\.local$''',
]
```

### trivy Configuration

```yaml
# .trivy.yaml (optional)
scan:
  security-checks:
    - vuln
    - config
    - secret
  skip-dirs:
    - node_modules
    - __pycache__
    - .git
```

### pre-commit Hook Order

Hooks run in this order (fastest to slowest):

1. `shfmt` - Bash formatting (fast)
2. `shellcheck` - Bash linting (fast)
3. `ruff` - Python linting (fast)
4. `ruff-format` - Python formatting (fast)
5. `actionlint` - GitHub Actions (medium)
6. `gitleaks` - Secret scanning (medium)
7. `trivy` - Config scanning (medium)
8. `mypy` - Type checking (slow, optional)

### Rollback Plan

If any tool causes issues:

```bash
# Remove specific tool
brew uninstall <tool>

# Disable pre-commit
pre-commit uninstall

# Remove mise
rm -rf ~/.local/share/mise
# Remove from shell config

# Remove just
brew uninstall just

# Remove starship
brew uninstall starship
# Remove from shell config

# Remove atuin
brew uninstall atuin
# Remove from shell config
```

---

## 5. Project Structure

### New Files Created

```
tdt/
├── .gitleaks.toml                    # Security config
├── .trivy.yaml                       # Container security config (optional)
├── Justfile                          # Task runner
├── .mise.toml                        # Version management
├── .envrc.template                   # Auto-environment template
├── .pre-commit-config.yaml           # (in each Python project)
├── docs/
│   └── tools/
│       └── TOOLING-GUIDE.md          # Usage documentation
└── openspec/
    └── changes/
        └── dev-tooling-audit-and-enhancement/
            ├── proposal.md
            ├── spec.md
            ├── design.md             # This file
            ├── tasks.md
            └── VERIFICATION.md
```

### Existing Files Modified

- `~/.zshrc` - Add tool integrations (mise, direnv, atuin, starship)
- `docs/CHANGELOG.md` - Add entry
- `openspec/INDEX.md` - Add reference

---

## 6. Homebrew Installation Strategy

### One-Liner Installation

```bash
# Install all 24 tools in a single Homebrew command
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy \
  mise just direnv watchexec atuin difftastic \
  xh yq sd dust tokei hyperfine btop starship gdu \
  rustup-init pnpm npm-check-updates
```

### Phased Installation (Recommended)

**Phase 1: Security** (Day 1, ~30 min)
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy

**Phase 2: Productivity** (Day 1-2, ~45 min)
brew install mise just direnv watchexec atuin difftastic

**Phase 3: Quality** (Day 2, ~30 min)
brew install xh yq sd dust tokei hyperfine btop starship gdu

**Phase 4: Language** (Day 3, ~30 min)
brew install rustup-init pnpm npm-check-updates

**Phase 5: Configuration & Docs** (Day 3-4, ~2h)
- Create configs (mise.toml, Justfile, starship.toml, etc.)
- Update shell integration
- Create documentation
- Run verification suite


```bash
# Phase 1: Security
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy

# Phase 2: Productivity
brew install mise just direnv watchexec atuin difftastic

# Phase 3: Quality
brew install xh yq sd dust tokei hyperfine btop starship gdu

# Phase 4: Language
brew install rustup-init pnpm npm-check-updates
```

### Homebrew Cleanup

```bash
# After installation, clean up
brew cleanup
brew autoremove  # Remove orphaned dependencies

# Check what's taking space
brew info --json=v2 --installed | jq '[.[] | {name: .name, size: .installed_size}] | sort_by(-.size) | .[0:20]'
```

---

## 7. Testing Strategy

### Unit Tests (per tool)

Each tool gets a simple test:

```bash
# gitleaks
echo "password = 'test123'" > /tmp/test.env && gitleaks detect --source /tmp --no-banner

# shellcheck
echo '#!/bin/bash\necho $1' > /tmp/test.sh && shellcheck /tmp/test.sh

# just
just --list

# mise
mise ls

# xh
xh https://httpbin.org/get

# yq
echo "test: value" | yq '.test'

# sd
echo "hello world" | sd "world" "universe"

# tokei
tokei --version

# hyperfine
hyperfine 'echo test'

# trivy
trivy --version

# atuin
atuin --version

# difftastic
difft --version
```

### Integration Tests

- `just audit` runs all security scans
- `just test` runs all project tests
- `just lint` runs all linters
- `just clean` removes all build artifacts

### Acceptance Tests

- All 24 tools respond to `--version`
- No shell startup errors
- No conflicts with existing 112 Homebrew packages
- All Python projects pass pre-commit checks
- Workspace tools functional via `just` commands
- Shell startup time increase < 100ms

---

## 8. Future Considerations

### Potential Additions (Not in This Change)

| Tool | Reason | Priority | Homebrew? |
|------|--------|----------|-----------|
| `k9s` | Kubernetes management | Low (if using K8s) | ✅ |
| `helm` | K8s package manager | Low (if using K8s) | ✅ |
| `k6` | Load testing | Low (if needed) | ✅ |
| `grpcurl` | gRPC client | Low (if using gRPC) | ✅ |
| `csvkit` | CSV processing | Low (if needed) | ❌ pip |
| `hadolint` | Dockerfile linting | Medium (if using Docker) | ✅ |
| `tfsec` | Terraform security | Low (if using Terraform) | ✅ |
| `syft` | SBOM generator | Low | ✅ |

### Workspace Scaling

When team grows beyond 1 person:

1. **Shared Justfile recipes** - Standardize across all projects
2. **CI/CD integration** - Run `just test` and `just lint` in CI
3. **Tool version pinning** - Use `.mise.toml` for consistent versions
4. **Pre-commit CI** - Run hooks in CI to catch issues early

### Tool Updates

- **Weekly**: `brew update && brew upgrade`
- **Monthly**: `mise upgrade` for language versions
- **Quarterly**: Review and remove unused tools
- **As needed**: `ncu -g` for npm global updates