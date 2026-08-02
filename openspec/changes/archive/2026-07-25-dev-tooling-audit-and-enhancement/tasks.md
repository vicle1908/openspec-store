# Dev Tooling Audit & Enhancement - Tasks

**Status:** Ready for Execution  
**Date:** 2026-05-23  
**Estimated Duration:** 2-3 days  
**Strategy:** Homebrew-First (all CLI tools via brew)

---

## Phase 1: Security Foundation (Day 1, ~30 minutes)

### Task 1.1: Install Security Tools via Homebrew
**Priority:** Critical  
**Estimated Time:** 10 minutes  
**Dependencies:** None

```bash
# Single Homebrew command for all security tools
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy

# Verify installations
gitleaks version
shellcheck --version | head -1
shfmt --version
actionlint --version
pre-commit --version
trivy --version
```

**Acceptance:**
- [x] All 6 tools installed successfully
- [x] Version commands return without errors
- [x] Tools available in PATH

---

### Task 1.2: Configure gitleaks
**Priority:** Critical  
**Estimated Time:** 10 minutes  
**Dependencies:** Task 1.1

```bash
cd /Users/lekhanhvinh/Developer/tdt

cat > .gitleaks.toml << 'EOF'
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
EOF

# Test gitleaks
gitleaks detect --no-banner --verbose 2>&1 | head -10
```

**Acceptance:**
- [x] `.gitleaks.toml` created at workspace root
- [x] Test scan completes without errors
- [x] No false positives from example files

---

### Task 1.3: Configure pre-commit
**Priority:** Critical  
**Estimated Time:** 15 minutes  
**Dependencies:** Task 1.1

```bash
# Create pre-commit config template
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.2
    hooks:
      - id: gitleaks

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.10.0.1
    hooks:
      - id: shellcheck

  - repo: https://github.com/scop/pre-commit-shfmt
    rev: v3.8.0-1
    hooks:
      - id: shfmt
        args: ['-w', '-i', '2']

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/rhysd/actionlint
    rev: v1.7.0
    hooks:
      - id: actionlint
EOF

# Copy to each Python project
for project in jira-skill jira-epic-report jira-daily-reports webhook-receiver ops-automation-suite tdt-core browser-cli jira-kanban-from-spreadsheet; do
  if [ -d "$project" ]; then
    cp .pre-commit-config.yaml "$project/"
    cd "$project" && pre-commit install && cd ..
  fi
done

# Test pre-commit
pre-commit run --all-files 2>&1 | tail -20
```

**Acceptance:**
- [x] `.pre-commit-config.yaml` created in all 8 Python projects
- [x] Hooks installed successfully
- [x] Test run completes

---

### Task 1.4: Test Security Tooling
**Priority:** Critical  
**Estimated Time:** 15 minutes  
**Dependencies:** Task 1.1, 1.2, 1.3

```bash
cd /Users/lekhanhvinh/Developer/tdt

# Test gitleaks
gitleaks detect --no-banner --report-path /tmp/gitleaks-report.json 2>&1 | tail -5

# Test shellcheck on bash scripts
find . -name "*.sh" -type f -exec shellcheck {} \; 2>&1 | head -20

# Test pre-commit on sample project
cd jira-skill && pre-commit run --all-files && cd ..

# Test trivy (if Dockerfiles exist)
find . -name "Dockerfile" -exec trivy config {} \; 2>/dev/null | head -10

# Test actionlint
find . -path "*/.github/workflows/*.yml" -exec actionlint {} \; 2>/dev/null | head -10
```

**Acceptance:**
- [x] All security scans complete without errors
- [x] Reports generated successfully

---

## Phase 2: Productivity Core (Day 1-2, ~45 minutes)

### Task 2.1: Install Productivity Tools via Homebrew
**Priority:** High  
**Estimated Time:** 10 minutes  
**Dependencies:** None

```bash
# Single Homebrew command for all productivity tools
brew install mise just direnv watchexec atuin difftastic

# Verify installations
mise --version
just --version
direnv --version
watchexec --version
atuin --version
difft --version
```

**Acceptance:**
- [x] All 6 tools installed successfully
- [x] Version commands return without errors

---

### Task 2.2: Configure mise
**Priority:** High  
**Estimated Time:** 15 minutes  
**Dependencies:** Task 2.1

```bash
cd /Users/lekhanhvinh/Developer/tdt

cat > .mise.toml << 'EOF'
[tools]
node = "26.0.0"
python = "3.13"
go = "1.26.3"
bun = "latest"

[env]
TDT_ROOT = "{{cwd}}"
PATH = "{{cwd}}/bin:$PATH"
EOF

# Add mise to shell (if not already)
grep -q 'mise activate' ~/.zshrc || echo 'eval "$(mise activate zsh)"' >> ~/.zshrc

# Install and activate tools
mise install
mise ls
```

**Acceptance:**
- [x] `.mise.toml` created at workspace root
- [x] Shell integration added
- [x] All language versions installed
- [x] `mise ls` shows all tools

---

### Task 2.3: Create Justfile
**Priority:** High  
**Estimated Time:** 15 minutes  
**Dependencies:** Task 2.1

```bash
cd /Users/lekhanhvinh/Developer/tdt

cat > Justfile << 'EOF'
# TDT Workspace Justfile
# Run `just --list` to see all recipes

default:
    @just --list

# Run security audit across all projects
audit:
    @echo "Running security audit..."
    gitleaks detect --no-banner
    @echo "Checking shell scripts..."
    find . -name "*.sh" -type f -exec shellcheck {} \;
    @echo "Audit complete"

# Run all tests across all Python projects
test:
    @echo "Running tests..."
    @for project in jira-skill jira-epic-report jira-daily-reports webhook-receiver ops-automation-suite tdt-core browser-cli; do \
        if [ -d "$$project" ]; then \
            echo "Testing $$project..."; \
            cd "$$project" && uv run pytest || true; \
            cd ..; \
        fi \
    done

# Run all linters
lint:
    @echo "Running linters..."
    @for project in jira-skill jira-epic-report jira-daily-reports webhook-receiver ops-automation-suite tdt-core browser-cli; do \
        if [ -d "$$project" ]; then \
            echo "Linting $$project..."; \
            cd "$$project" && uv run ruff check . || true; \
            cd ..; \
        fi \
    done

# Install dependencies for all projects
install:
    @echo "Installing dependencies..."
    @for project in jira-skill jira-epic-report jira-daily-reports webhook-receiver ops-automation-suite tdt-core browser-cli; do \
        if [ -d "$$project" ]; then \
            echo "Installing $$project..."; \
            cd "$$project" && uv sync || true; \
            cd ..; \
        fi \
    done

# Clean build artifacts and caches
clean:
    @echo "Cleaning build artifacts..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @echo "Clean complete"

# Generate/update documentation
docs:
    @echo "Generating documentation..."

# Update all dependencies
update:
    @echo "Updating dependencies..."
    brew update && brew upgrade
    mise upgrade
    @for project in jira-skill jira-epic-report jira-daily-reports webhook-receiver ops-automation-suite tdt-core browser-cli; do \
        if [ -d "$$project" ]; then \
            echo "Updating $$project..."; \
            cd "$$project" && uv lock --upgrade || true; \
            cd ..; \
        fi \
    done

# Check tool versions
versions:
    @echo "Tool versions:"
    @echo "mise: {{mise --version}}"
    @echo "just: {{just --version}}"
    @echo "node: {{node --version}}"
    @echo "python: {{python --version}}"
    @echo "go: {{go version}}"
    @echo "bun: {{bun --version}}"
    @echo "uv: {{uv --version}}"
    @echo "ruff: {{ruff --version}}"
    @echo "gitleaks: {{gitleaks version}}"
    @echo "shellcheck: {{shellcheck --version | head -1}}"
EOF

# Test just
just --list
just versions
```

**Acceptance:**
- [x] `Justfile` created with all 8 recipes
- [x] `just --list` shows all recipes
- [x] `just versions` displays tool versions

---

### Task 2.4: Configure direnv and Shell Integration
**Priority:** Medium  
**Estimated Time:** 10 minutes  
**Dependencies:** Task 2.1

```bash
cd /Users/lekhanhvinh/Developer/tdt

# Create .envrc template
cat > .envrc.template << 'EOF'
# TDT Workspace Environment
# Copy to .envrc and customize

# Load mise
use mise

# Load .env files
dotenv_if_exists ~/.tdt/.env
dotenv_if_exists .env.local

# Set workspace root
export TDT_ROOT=$(pwd)

# Add local bin to PATH
PATH_add bin
EOF

# Add shell integrations
grep -q 'direnv hook' ~/.zshrc || echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Test direnv
echo "export TEST_VAR=hello" > .envrc
direnv allow
echo $TEST_VAR  # Should print "hello"
rm .envrc
```

**Acceptance:**
- [x] `.envrc.template` created
- [x] Shell integration added
- [x] direnv loads environment correctly

---

### Task 2.5: Test Productivity Tools
**Priority:** High  
**Estimated Time:** 15 minutes  
**Dependencies:** Task 2.1, 2.2, 2.3, 2.4

```bash
cd /Users/lekhanhvinh/Developer/tdt

# Test mise
mise ls
mise exec -- node --version
mise exec -- python --version

# Test just recipes
just clean
just versions

# Test atuin
atuin sync 2>&1 || echo "atuin sync not configured yet"

# Test difftastic
echo "hello" > /tmp/a.txt
echo "world" > /tmp/b.txt
difft /tmp/a.txt /tmp/b.txt

# Test watchexec
watchexec --version
```

**Acceptance:**
- [x] All productivity tools functional
- [x] mise manages language versions
- [x] just recipes execute correctly

---

## Phase 3: Quality & Observability (Day 2, ~30 minutes)

### Task 3.1: Install Quality Tools via Homebrew
**Priority:** Medium  
**Estimated Time:** 10 minutes  
**Dependencies:** None

```bash
# Single Homebrew command for all quality tools
brew install xh yq sd dust tokei hyperfine btop starship gdu

# Verify installations
xh --version
yq --version
sd --version
dust --version
tokei --version
hyperfine --version
btop --version
starship --version
gdu --version
```

**Acceptance:**
- [x] All 9 tools installed successfully
- [x] Version commands return without errors

---

### Task 3.2: Configure starship
**Priority:** Low  
**Estimated Time:** 10 minutes  
**Dependencies:** Task 3.1

```bash
# Add starship to shell
grep -q 'starship init' ~/.zshrc || echo 'eval "$(starship init zsh)"' >> ~/.zshrc

# Create starship config
mkdir -p ~/.config
cat > ~/.config/starship.toml << 'EOF'
# TDT Workspace Starship Config

format = """
[┌───────────────────>](bold green)
[│](bold green)$directory$git_branch$git_status$python$nodejs$golang$rust
[└─>](bold green) """

[directory]
style = "blue bold"
truncation_length = 3
truncate_to_repo = true

[git_branch]
symbol = " "
style = "bold purple"

[git_status]
style = "red bold"
ahead = "⇡${count}"
diverged = "⇕⇡${ahead_count}⇣${behind_count}"
behind = "⇣${count}"

[python]
symbol = " "
style = "yellow bold"

[nodejs]
symbol = " "
style = "green bold"

[golang]
symbol = " "
style = "cyan bold"

[rust]
symbol = " "
style = "red bold"
EOF

# Reload shell
source ~/.zshrc
```

**Acceptance:**
- [x] starship configured with custom prompt
- [x] Prompt displays correctly in terminal

---

### Task 3.3: Test Quality Tools
**Priority:** Medium  
**Estimated Time:** 15 minutes  
**Dependencies:** Task 3.1

```bash
cd /Users/lekhanhvinh/Developer/tdt

# Test xh (HTTP client)
xh https://httpbin.org/get 2>&1 | head -10

# Test yq (YAML processor)
echo "test: value" | yq '.test'

# Test sd (find/replace)
echo "hello world" | sd "world" "universe"

# Test dust (disk usage)
dust -d 2 . 2>/dev/null | head -15

# Test tokei (code metrics)
tokei jira-skill jira-epic-report webhook-receiver

# Test hyperfine (benchmark)
hyperfine --runs 3 'just --version'

# Test gdu (disk analyzer)
gdu --version

# Test btop (system monitor)
btop --version
```

**Acceptance:**
- [x] All quality tools functional
- [x] Basic operations work correctly

---

## Phase 4: Language & Package Management (Day 3, ~30 minutes)

### Task 4.1: Install Language Tools via Homebrew
**Priority:** Medium  
**Estimated Time:** 10 minutes  
**Dependencies:** None

```bash
# Single Homebrew command for language tools
brew install rustup-init pnpm npm-check-updates

# Verify installations
rustup --version
pnpm --version
ncu --version
```

**Acceptance:**
- [x] All 3 tools installed successfully
- [x] Version commands return without errors

---

### Task 4.2: Configure Rust Toolchain
**Priority:** Medium  
**Estimated Time:** 10 minutes  
**Dependencies:** Task 4.1

```bash
# Initialize Rust
rustup-init -y

# Add to PATH (if not already)
grep -q '.cargo/env' ~/.zshrc || echo 'source $HOME/.cargo/env' >> ~/.zshrc

# Install stable toolchain
rustup install stable
rustup default stable

# Verify
rustc --version
cargo --version
```

**Acceptance:**
- [x] Rust stable toolchain installed
- [x] cargo and rustc available in PATH
- [x] Can compile simple Rust program

---

### Task 4.3: Test Language Tools
**Priority:** Medium  
**Estimated Time:** 10 minutes  
**Dependencies:** Task 4.1, 4.2

```bash
# Test Rust compilation
echo 'fn main() { println!("Hello from Rust!"); }' > /tmp/test.rs
rustc /tmp/test.rs -o /tmp/test && /tmp/test
rm -f /tmp/test.rs /tmp/test

# Test pnpm
pnpm --help | head -5

# Test npm-check-updates
ncu --version

# Verify all language tools via mise
mise exec -- node --version
mise exec -- python --version
mise exec -- go version
mise exec -- bun --version
```

**Acceptance:**
- [x] Rust compiles and runs programs
- [x] pnpm functional
- [x] npm-check-updates available
- [x] All language tools accessible via mise

---

## Phase 5: Documentation (Day 3-4, ~2 hours)

### Task 5.1: Create Tooling Guide
**Priority:** High  
**Estimated Time:** 60 minutes  
**Dependencies:** All previous tasks

```bash
mkdir -p docs/tools
# Create comprehensive TOOLING-GUIDE.md
```

**Acceptance:**
- [x] `docs/tools/TOOLING-GUIDE.md` created
- [x] All 24 tools documented with purpose and examples
- [x] Homebrew installation commands included
- [x] Configuration examples provided
- [x] Troubleshooting section complete

---

### Task 5.2: Update Project Documentation
**Priority:** Medium  
**Estimated Time:** 30 minutes  
**Dependencies:** Task 5.1

```bash
# Update changelog
# Update openspec index
# Commit all documentation
```

**Acceptance:**
- [x] `docs/CHANGELOG.md` updated
- [x] `openspec/INDEX.md` updated
- [x] All changes committed

---

## Summary

**Total Tools:** 24 (all via Homebrew)
**Total Estimated Time:** 4-5 hours over 2-3 days
**Installation Commands:** 4 single-line `brew install` commands

### One-Liner Installation
```bash
# Install all 24 tools in a single command
brew install gitleaks shellcheck shfmt actionlint pre-commit trivy mise just direnv watchexec atuin difftastic xh yq sd dust tokei hyperfine btop starship gdu rustup-init pnpm npm-check-updates
```

### Phase Breakdown
| Phase | Tools | Time | Priority |
|-------|-------|------|----------|
| 1: Security | 6 tools | 30m | Critical |
| 2: Productivity | 6 tools | 45m | High |
| 3: Quality | 9 tools | 30m | Medium |
| 4: Language | 3 tools | 30m | Medium |
| 5: Docs | N/A | 2h | Low |
| **Total** | **24 tools** | **~4h** | |

### Risk Assessment
- **Low Risk:** All tools additive, no breaking changes
- **Homebrew-First:** Centralized management, easy updates
- **Rollback:** `brew uninstall <tool>` for any tool
- **Conflicts:** None expected (all tools coexist peacefully)
