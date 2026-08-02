# Dev Tooling Audit & Enhancement - Specification

**Status:** Draft  
**Version:** 1.1.0 (Homebrew-First)  
**Date:** 2026-05-23  
**Scope:** Homebrew packages, npm global packages (AI/MCP only), shell tooling, security tooling

---

## 1. Package Management Strategy

### Homebrew-First Principle

**All CLI tools installed via Homebrew where available.** This ensures:
- Centralized package management (single `brew install` command)
- Automatic updates via `brew upgrade`
- Consistent dependency resolution across all tools
- No mixing of installation methods (brew vs npm vs cargo vs pip)
- Easy rollback with `brew uninstall`
- Shared dependencies between tools

### Exceptions (Non-Homebrew)

| Tool | Reason | Installation Method |
|------|--------|-------------------|
| npm AI/MCP packages | No Homebrew equivalents | npm global |
| Python packages | Already managed by uv | uv/pip |
| Language runtimes | Managed by mise | mise |

### Current State

**Homebrew packages:** 112 installed (well-managed)
**npm global packages:** 23 installed (AI/MCP focused)
**Bun global packages:** 1 installed
**Python:** uv-managed (excellent)
**Go:** 1.26.3 (current)
**Rust:** ❌ Missing (will add via brew)

---

## 2. Functional Requirements

### FR1: Security Tooling Installation

**Priority:** Critical  
**Installation:** All via Homebrew

**Tools to install:**
- `gitleaks` - Secret scanning in git repos
- `shellcheck` - Bash script linting
- `shfmt` - Bash script formatting
- `actionlint` - GitHub Actions workflow validation
- `pre-commit` - Git hooks framework
- `trivy` - Container/image vulnerability scanning

**Acceptance Criteria:**
- [ ] All 6 tools installed via `brew install`
- [ ] `.gitleaks.toml` created at workspace root
- [ ] `.pre-commit-config.yaml` created for each Python project
- [ ] pre-commit hooks configured for: gitleaks, shellcheck, shfmt, ruff, actionlint
- [ ] trivy configured for Dockerfile scanning (if applicable)

**Verification:**
```bash
# Single command to install all security tools
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy

# Verify installations
gitleaks version && shellcheck --version | head -1 && shfmt --version
actionlint --version && pre-commit --version && trivy --version
```

---

### FR2: Productivity Core Installation

**Priority:** High  
**Installation:** All via Homebrew

**Tools to install:**
- `mise` - Universal version manager (replaces nvm/fnm/pyenv)
- `just` - Task runner (Makefile alternative)
- `direnv` - Auto environment loading per directory
- `watchexec` - Run commands on file changes
- `atuin` - Shell history search with sync
- `difftastic` - Structural diff tool (syntax-aware)

**Acceptance Criteria:**
- [ ] All 6 tools installed via `brew install`
- [ ] `.mise.toml` created at workspace root with:
  - node 26.0.0
  - python 3.13
  - go 1.26.3
  - bun latest
- [ ] `Justfile` created at workspace root with recipes:
  - `audit` - run all security scans
  - `test` - run all project tests
  - `lint` - run all linters
  - `install` - install all dependencies
  - `clean` - clean build artifacts
  - `docs` - generate documentation
  - `versions` - show all tool versions
- [ ] `.envrc.template` created for direnv
- [ ] Shell integration added to `~/.zshrc`

**Verification:**
```bash
# Single command to install all productivity tools
brew install mise just direnv watchexec atuin difftastic

# Verify installations
mise --version && just --version && direnv --version
watchexec --version && atuin --version && difft --version

# Test mise
mise ls && mise exec -- node --version

# Test just
just --list && just versions
```

---

### FR3: Quality & Observability Tools

**Priority:** Medium  
**Installation:** All via Homebrew

**Tools to install:**
- `xh` - Modern HTTP client (curl alternative for interactive use)
- `yq` - YAML/XML processor
- `sd` - Modern sed alternative (simpler regex)
- `dust` - Disk usage visualization
- `tokei` - Code metrics (line counting)
- `hyperfine` - Command benchmarking
- `btop` - System resource monitor
- `starship` - Shell prompt customization
- `gdu` - Fast disk usage analyzer

**Acceptance Criteria:**
- [ ] All 9 tools installed via `brew install`
- [ ] `.config/starship.toml` created with TDT workspace theme
- [ ] Shell completions enabled for all tools

**Verification:**
```bash
# Single command to install all quality tools
brew install xh yq sd dust tokei hyperfine btop starship gdu

# Verify installations
xh --version && yq --version && sd --version && dust --version
tokei --version && hyperfine --version && btop --version
starship --version && gdu --version

# Test functionality
echo "test: value" | yq '.test'
echo "hello world" | sd "world" "universe"
tokei jira-skill jira-epic-report webhook-receiver
```

---

### FR4: Language & Package Enhancement

**Priority:** Medium  
**Installation:** All via Homebrew

**Tools to install:**
- `rustup-init` - Rust toolchain installer
- `pnpm` - Fast, disk-efficient npm alternative
- `npm-check-updates` - Dependency update checker

**Acceptance Criteria:**
- [ ] All 3 tools installed via `brew install`
- [ ] Rust stable toolchain installed via `rustup-init`
- [ ] pnpm configured as npm alternative
- [ ] npm global packages audited for redundancy

**Verification:**
```bash
# Single command to install language tools
brew install rustup-init pnpm npm-check-updates

# Verify installations
rustup --version && pnpm --version && ncu --version

# Test Rust
rustc --version && cargo --version

# Audit npm packages
npm list -g --depth=0 2>/dev/null | wc -l
```

---

### FR5: Shell & Environment Configuration

**Priority:** Medium  
**Installation:** Configuration only

**Description:** Configure shell environment for optimal productivity with all new tools.

**Acceptance Criteria:**
- [ ] `starship` configured with custom TDT workspace prompt
- [ ] Shell aliases created for common operations:
  - `tdt` -> cd to workspace root
  - `j` -> just
  - `ja` -> just audit
  - `jt` -> just test
  - `jl` -> just lint
- [ ] fzf enhanced with fd and ripgrep integration
- [ ] Shell completion enabled for: mise, just, starship, atuin
- [ ] Shell startup time increase < 100ms

**Verification:**
```bash
# Test shell aliases
alias | grep -E "(tdt|just|j[a-z])"

# Test completions
type _mise 2>/dev/null && echo "mise completion OK"
type _just 2>/dev/null && echo "just completion OK"

# Test startup time
time zsh -i -c exit 2>&1 | head -1
```

---

### FR6: Documentation & Knowledge Base

**Priority:** Low  
**Installation:** N/A

**Acceptance Criteria:**
- [ ] `docs/tools/TOOLING-GUIDE.md` created with:
  - Complete inventory of all 24 new tools
  - Purpose and usage examples for each tool
  - Homebrew installation commands
  - Configuration examples
  - Troubleshooting guide
- [ ] `VERIFICATION.md` created with test suite
- [ ] `docs/CHANGELOG.md` updated
- [ ] `openspec/INDEX.md` updated

---

## 3. Non-Functional Requirements

### NFR1: Homebrew-First Compliance

**Requirement:** All CLI tools MUST be installed via Homebrew where available.

**Validation:**
```bash
# Check all tools are brew-managed
for tool in gitleaks shellcheck shfmt actionlint pre-commit trivy mise just direnv watchexec atuin difftastic xh yq sd dust tokei hyperfine btop starship gdu rustup-init pnpm npm-check-updates; do
  brew info "$tool" 2>/dev/null | grep -q "Not installed" && echo "FAIL: $tool not brew-managed" || echo "PASS: $tool brew-managed"
done
```

### NFR2: Performance

**Requirements:**
- All tools start within 1 second
- Shell startup time increase < 100ms
- No impact on existing tool performance

### NFR3: Compatibility

**Requirements:**
- All tools compatible with macOS ARM64
- No conflicts with existing Homebrew packages
- No breaking changes to current workflows

### NFR4: Security

**Requirements:**
- All tools from trusted Homebrew formulas
- Secret scanning enabled by default
- Pre-commit hooks prevent credential commits

---

## 4. Tool Inventory

### Complete Installation List (24 tools via Homebrew)

| # | Tool | Category | Priority | Homebrew Formula |
|---|------|----------|----------|------------------|
| 1 | gitleaks | Security | 🔴 Critical | `gitleaks` |
| 2 | shellcheck | Security | 🔴 Critical | `shellcheck` |
| 3 | shfmt | Security | 🔴 Critical | `shfmt` |
| 4 | actionlint | Security | 🔴 Critical | `actionlint` |
| 5 | pre-commit | Security | 🔴 Critical | `pre-commit` |
| 6 | trivy | Security | 🟡 Medium | `trivy` |
| 7 | mise | Productivity | 🟡 High | `mise` |
| 8 | just | Productivity | 🟡 High | `just` |
| 9 | direnv | Productivity | 🟡 High | `direnv` |
| 10 | watchexec | Productivity | 🟡 High | `watchexec` |
| 11 | atuin | Productivity | 🟡 Medium | `atuin` |
| 12 | difftastic | Productivity | 🟡 Medium | `difftastic` |
| 13 | xh | Quality | 🟡 Medium | `xh` |
| 14 | yq | Quality | 🟡 Medium | `yq` |
| 15 | sd | Quality | 🟡 Medium | `sd` |
| 16 | dust | Quality | 🟡 Medium | `dust` |
| 17 | tokei | Quality | 🟡 Medium | `tokei` |
| 18 | hyperfine | Quality | 🟡 Medium | `hyperfine` |
| 19 | btop | Quality | 🟢 Low | `btop` |
| 20 | starship | Quality | 🟢 Low | `starship` |
| 21 | gdu | Quality | 🟢 Low | `gdu` |
| 22 | rustup-init | Language | 🟡 Medium | `rustup-init` |
| 23 | pnpm | Language | 🟡 Medium | `pnpm` |
| 24 | npm-check-updates | Language | 🟡 Medium | `npm-check-updates` |

### npm Global Packages (Keep, No Homebrew Equivalent)

| Package | Purpose | Decision |
|---------|---------|----------|
| `@wonderwhy-er/desktop-commander` | MCP server | ✅ Keep |
| `@earendil-works/pi-coding-agent` | AI coding assistant | ✅ Keep |
| `pi-subagents` | Multi-agent orchestration | ✅ Keep |
| `pi-lens` | Code analysis | ✅ Keep |
| `pi-web-access` | Web access | ✅ Keep |
| `pi-mermaid` | Diagram generation | ✅ Keep |
| `pi-simplify` | Code simplification | ✅ Keep |
| `gitnexus` | Git integration | ✅ Keep |
| `deepwiki-cli` | Wiki generation | ✅ Keep |
| `ctx7` | Context management | ✅ Keep |
| `context-mode` | Context switching | ✅ Keep |
| `@brightdata/cli` | Web scraping | ✅ Keep |
| `@fission-ai/openspec` | Spec management | ✅ Keep |
| `@oh-my-pi/pi-coding-agent` (bun) | AI agent | ⚠️ Review overlap |

---

## 5. Implementation Phases

### Phase 1: Security Foundation (Day 1, ~30 minutes)
```bash
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy
```

### Phase 2: Productivity Core (Day 1-2, ~45 minutes)
```bash
brew install mise just direnv watchexec atuin difftastic
```

### Phase 3: Quality & Observability (Day 2, ~30 minutes)
```bash
brew install xh yq sd dust tokei hyperfine btop starship gdu
```

### Phase 4: Language & Package Management (Day 3, ~30 minutes)
```bash
brew install rustup-init pnpm npm-check-updates
```

### Phase 5: Configuration & Documentation (Day 3-4, ~2 hours)
- Create configs (mise.toml, Justfile, starship.toml, etc.)
- Update shell integration
- Create documentation
- Run verification suite

---

## 6. One-Liner Installation

```bash
# Install all 24 tools in a single Homebrew command
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy mise just direnv watchexec atuin difftastic xh yq sd dust tokei hyperfine btop starship gdu rustup-init pnpm npm-check-updates
```

---

## 7. Success Criteria

### Must Have (All Required)
- [ ] All 24 tools installed via Homebrew
- [ ] Security tools configured and tested
- [ ] Shell environment updated with aliases and completions
- [ ] Documentation created and committed
- [ ] No breaking changes to existing workflows
- [ ] Shell startup time increase < 100ms

### Should Have (Highly Recommended)
- [ ] mise managing all language versions
- [ ] Justfile with all workspace recipes
- [ ] starship prompt customized
- [ ] npm global package audit completed
- [ ] pre-commit hooks in all Python projects

### Nice to Have (Optional)
- [ ] Performance benchmarks recorded
- [ ] Team training materials created
- [ ] CI/CD pipeline updated with new tools
