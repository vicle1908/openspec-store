[Reading 367 lines from start (total: 367 lines, 0 remaining)]

[Reading 365 lines from start (total: 365 lines, 0 remaining)]

[Reading 363 lines from start (total: 363 lines, 0 remaining)]

# Dev Tooling Audit & Enhancement - Verification

**Strategy:** Homebrew-First (24 tools via brew)
**Status:** Not Started  
**Date:** 2026-05-23  
**Version:** 1.0

---

## Verification Checklist

### Phase 1: Security Tools

```bash
#!/bin/bash
# Run this script to verify Phase 1 installation

echo "=== Phase 1: Security Tools Verification (brew install gitleaks shellcheck shfmt actionlint pre-commit trivy) ==="
echo

# Check tool installations
echo "Checking gitleaks..."
gitleaks version 2>&1 || echo "FAIL: gitleaks not installed"

echo "Checking shellcheck..."
shellcheck --version 2>&1 | head -1 || echo "FAIL: shellcheck not installed"

echo "Checking shfmt..."
shfmt --version 2>&1 || echo "FAIL: shfmt not installed"

echo "Checking actionlint..."
actionlint --version 2>&1 || echo "FAIL: actionlint not installed"

echo "Checking pre-commit..."
pre-commit --version 2>&1 || echo "FAIL: pre-commit not installed"

echo
echo "Checking gitleaks config..."
test -f /Users/lekhanhvinh/Developer/tdt/.gitleaks.toml && echo "PASS: .gitleaks.toml exists" || echo "FAIL: .gitleaks.toml missing"

echo
echo "Checking pre-commit configs..."
for project in jira-skill jira-epic-report jira-daily-reports webhook-receiver ops-automation-suite tdt-core browser-cli jira-kanban-from-spreadsheet; do
  if [ -d "$project" ]; then
    test -f "$project/.pre-commit-config.yaml" && echo "PASS: $project/.pre-commit-config.yaml exists" || echo "FAIL: $project/.pre-commit-config.yaml missing"
  fi
done

echo
echo "Running gitleaks scan..."
cd /Users/lekhanhvinh/Developer/tdt
gitleaks detect --no-banner --report-path /tmp/gitleaks-verify.json 2>&1 | tail -5

echo
echo "Phase 1 Verification Complete"
```

### Phase 2: Productivity Core

```bash
#!/bin/bash
# Run this script to verify Phase 2 installation

echo "=== Phase 2: Productivity Core Verification ==="
echo

echo "Checking mise..."
mise --version 2>&1 || echo "FAIL: mise not installed"

echo "Checking just..."
just --version 2>&1 || echo "FAIL: just not installed"

echo "Checking direnv..."
direnv --version 2>&1 || echo "FAIL: direnv not installed"

echo "Checking watchexec..."
watchexec --version 2>&1 || echo "FAIL: watchexec not installed"

echo
echo "Checking configs..."
test -f /Users/lekhanhvinh/Developer/tdt/.mise.toml && echo "PASS: .mise.toml exists" || echo "FAIL: .mise.toml missing"
test -f /Users/lekhanhvinh/Developer/tdt/Justfile && echo "PASS: Justfile exists" || echo "FAIL: Justfile missing"
test -f /Users/lekhanhvinh/Developer/tdt/.envrc.template && echo "PASS: .envrc.template exists" || echo "FAIL: .envrc.template missing"

echo
echo "Testing mise..."
mise ls 2>&1 || echo "FAIL: mise ls failed"
mise exec -- node --version 2>&1 || echo "FAIL: mise exec node failed"

echo
echo "Testing just recipes..."
just --list 2>&1 || echo "FAIL: just --list failed"
just versions 2>&1 || echo "FAIL: just versions failed"

echo
echo "Phase 2 Verification Complete"
```

### Phase 3: Quality & Observability

```bash
#!/bin/bash
# Run this script to verify Phase 3 installation

echo "=== Phase 3: Quality & Observability Verification ==="
echo

# Check each tool
for tool in xh yq sd dust tokei hyperfine btop starship gdu; do
  echo "Checking $tool..."
  $tool --version 2>&1 || echo "FAIL: $tool not installed"
done

echo
echo "Testing starship config..."
test -f ~/.config/starship.toml && echo "PASS: starship.toml exists" || echo "FAIL: starship.toml missing"

echo
echo "Testing xh..."
xh --help 2>&1 | head -3 || echo "FAIL: xh not functional"

echo
echo "Testing yq..."
echo "test: value" | yq '.test' 2>&1 || echo "FAIL: yq not functional"

echo
echo "Testing sd..."
echo "hello world" | sd "world" "universe" 2>&1 || echo "FAIL: sd not functional"

echo
echo "Phase 3 Verification Complete"
```

### Phase 4: Language & Package Enhancement

```bash
#!/bin/bash
# Run this script to verify Phase 4 installation

echo "=== Phase 4: Language & Package Enhancement Verification ==="
echo

echo "Checking rustup..."
rustup --version 2>&1 || echo "FAIL: rustup not installed"

echo "Checking cargo..."
cargo --version 2>&1 || echo "FAIL: cargo not installed"

echo "Checking rustc..."
rustc --version 2>&1 || echo "FAIL: rustc not installed"

echo "Checking pnpm..."
pnpm --version 2>&1 || echo "FAIL: pnpm not installed"

echo "Checking npm-check-updates..."
ncu --version 2>&1 || echo "FAIL: ncu not installed"

echo
echo "Testing Rust compilation..."
echo 'fn main() { println!("Hello from Rust!"); }' > /tmp/test-rust.rs
rustc /tmp/test-rust.rs -o /tmp/test-rust 2>&1 && /tmp/test-rust 2>&1 || echo "FAIL: Rust compilation failed"
rm -f /tmp/test-rust.rs /tmp/test-rust

echo
echo "Testing pnpm..."
pnpm --help 2>&1 | head -3 || echo "FAIL: pnpm not functional"

echo
echo "Phase 4 Verification Complete"
```

### Phase 5: Documentation

```bash
#!/bin/bash
# Run this script to verify Phase 5 completion

echo "=== Phase 5: Documentation Verification ==="
echo

echo "Checking tooling guide..."
test -f docs/tools/TOOLING-GUIDE.md && echo "PASS: TOOLING-GUIDE.md exists" || echo "FAIL: TOOLING-GUIDE.md missing"

echo "Checking changelog..."
grep -q "dev-tooling-audit" docs/CHANGELOG.md 2>/dev/null && echo "PASS: CHANGELOG.md updated" || echo "FAIL: CHANGELOG.md not updated"

echo "Checking openspec index..."
grep -q "dev-tooling-audit-and-enhancement" openspec/INDEX.md 2>/dev/null && echo "PASS: INDEX.md updated" || echo "FAIL: INDEX.md not updated"

echo
echo "Phase 5 Verification Complete"
```

---

## Full Verification Suite

Run all phases in sequence:

```bash
#!/bin/bash
# Full verification suite

cd /Users/lekhanhvinh/Developer/tdt

echo "============================================"
echo "  Dev Tooling Audit - Full Verification    "
echo "============================================"
echo

PASS=0
FAIL=0

# Function to check and count
check() {
  if eval "$1" > /dev/null 2>&1; then
    echo "PASS: $2"
    PASS=$((PASS + 1))
  else
    echo "FAIL: $2"
    FAIL=$((FAIL + 1))
  fi
}

# Phase 1: Security
echo "--- Phase 1: Security Tools ---"
check "gitleaks version" "gitleaks installed"
check "shellcheck --version" "shellcheck installed"
check "shfmt --version" "shfmt installed"
check "actionlint --version" "actionlint installed"
check "pre-commit --version" "pre-commit installed"
check "test -f .gitleaks.toml" ".gitleaks.toml exists"
check "test -f jira-skill/.pre-commit-config.yaml" "jira-skill pre-commit config"
check "test -f jira-epic-report/.pre-commit-config.yaml" "jira-epic-report pre-commit config"
echo

# Phase 2: Productivity
echo "--- Phase 2: Productivity Core ---"
check "mise --version" "mise installed"
check "just --version" "just installed"
check "direnv --version" "direnv installed"
check "watchexec --version" "watchexec installed"
check "test -f .mise.toml" ".mise.toml exists"
check "test -f Justfile" "Justfile exists"
check "test -f .envrc.template" ".envrc.template exists"
check "just --list" "just recipes available"
echo

# Phase 3: Quality
echo "--- Phase 3: Quality Tools ---"
check "xh --version" "xh installed"
check "yq --version" "yq installed"
check "sd --version" "sd installed"
check "dust --version" "dust installed"
check "tokei --version" "tokei installed"
check "hyperfine --version" "hyperfine installed"
check "btop --version" "btop installed"
check "starship --version" "starship installed"
check "gdu --version" "gdu installed"
check "test -f ~/.config/starship.toml" "starship config exists"
echo

# Phase 4: Language
echo "--- Phase 4: Language Tools ---"
check "rustup --version" "rustup installed"
check "cargo --version" "cargo installed"
check "rustc --version" "rustc installed"
check "pnpm --version" "pnpm installed"
check "ncu --version" "npm-check-updates installed"
echo

# Phase 5: Documentation
echo "--- Phase 5: Documentation ---"
check "test -f docs/tools/TOOLING-GUIDE.md" "TOOLING-GUIDE.md exists"
check "test -f openspec/changes/dev-tooling-audit-and-enhancement/VERIFICATION.md" "VERIFICATION.md exists"
check "grep -q dev-tooling-audit docs/CHANGELOG.md" "CHANGELOG.md updated"
check "grep -q dev-tooling-audit openspec/INDEX.md" "INDEX.md updated"
echo

# Summary
echo "============================================"
echo "  Results: $PASS passed, $FAIL failed       "
echo "============================================"

if [ $FAIL -eq 0 ]; then
  echo "ALL CHECKS PASSED"
  exit 0
else
  echo "SOME CHECKS FAILED"
  exit 1
fi
```

---

## Performance Benchmarks

After installation, record baseline performance:

```bash
#!/bin/bash
# Performance benchmarks

echo "=== Shell Startup Time ==="
time zsh -i -c exit 2>&1

echo "=== Tool Startup Times ==="
hyperfine --runs 5 'gitleaks version'
hyperfine --runs 5 'just --list'
hyperfine --runs 5 'mise ls'
hyperfine --runs 5 'xh --version'
hyperfine --runs 5 'tokei --version'

echo "=== Disk Usage ==="
echo "Workspace size:"
dust -d 1 /Users/lekhanhvinh/Developer/tdt 2>/dev/null | head -10

echo "Homebrew packages:"
brew list --formula | wc -l

echo "New tools disk usage:"
brew info gitleaks shellcheck shfmt actionlint pre-commit mise just direnv watchexec xh yq sd dust tokei hyperfine btop starship gdu rustup-init pnpm 2>/dev/null | grep "Installed" | awk '{sum += $NF} END {print sum " MB total"}'
```

---

## Acceptance Criteria

### Must Pass
- [ ] All 24 new tools installed and functional
- [ ] `.gitleaks.toml` at workspace root
- [ ] `.pre-commit-config.yaml` in all 8 Python projects
- [ ] `.mise.toml` at workspace root
- [ ] `Justfile` with all 8 recipes
- [ ] `docs/tools/TOOLING-GUIDE.md` created
- [ ] `VERIFICATION.md` created (this file)
- [ ] Full verification suite passes (0 failures)
- [ ] No breaking changes to existing workflows
- [ ] Shell startup time increase < 100ms

### Should Pass
- [ ] `starship.toml` configured
- [ ] `.envrc.template` created
- [ ] npm audit completed
- [ ] Performance benchmarks recorded
- [ ] All just recipes tested successfully

### Nice to Have
- [ ] Team documentation created
- [ ] CI/CD pipeline updated
- [ ] Automated tool update checks
- [ ] Custom shell aliases documented

---

## Sign-off

| Role | Name | Date | Status |
|------|------|------|--------|
| Author | Goose | 2026-05-23 | Draft |
| Reviewer | [Pending] | [Pending] | [Pending] |
| Approver | [Pending] | [Pending] | [Pending] |

**Change Ready for Execution:** [ ] Yes