[Reading 146 lines from start (total: 146 lines, 0 remaining)]

[Reading 144 lines from start (total: 144 lines, 0 remaining)]

# Dev Tooling Audit & Enhancement - Proposal

**Status:** ✅ Finalized → See [spec.md](spec.md) for full architecture  
**Date:** 2026-05-23  
**Author:** Goose  

---

## Context

Development environment has 112 Homebrew packages and 23 npm global packages. Need systematic audit to identify:
- Missing critical tooling (security, productivity, quality)
- Redundant/unused tools
- Opportunities for Homebrew-first package management

### Current State Summary

| Category | Count | Status |
|----------|-------|--------|
| Homebrew packages | 112 | ✅ Well-managed via brew |
| npm global packages | 23 | ⚠️ AI/MCP focused, some overlap with bun |
| Bun global packages | 1 | ✅ Minimal |
| Python tools | via uv | ✅ Well managed |
| Go tools | 1.26.3 | ✅ Current |
| Rust toolchain | 0 | ❌ Missing |
| Security tools | 0 | ❌ Critical gap |

### Key Gaps Identified

1. **Security**: No secret scanning, shell linting, pre-commit hooks, container scanning
2. **Productivity**: No task runner, version manager, environment automation, shell history search
3. **Observability**: No system monitor, disk analyzer, benchmark tools
4. **Quality**: No YAML validation, modern HTTP client, structural diff, code metrics
5. **DevOps**: No Dockerfile linting, vulnerability scanning, SBOM generation

---

## Homebrew-First Strategy

**Principle:** Install ALL tools via Homebrew where available. This ensures:
- Centralized package management
- Automatic updates via `brew upgrade`
- Consistent dependency resolution
- No mixing of installation methods (brew vs npm vs cargo vs pip)
- Easier rollback and maintenance

### Tools Available via Homebrew (100% coverage for planned additions)

| Tool | Purpose | Priority | Homebrew Formula |
|------|---------|----------|------------------|
| gitleaks | Secret scanning | 🔴 Critical | `gitleaks` |
| shellcheck | Bash linting | 🔴 Critical | `shellcheck` |
| shfmt | Bash formatting | 🔴 Critical | `shfmt` |
| actionlint | GitHub Actions lint | 🔴 Critical | `actionlint` |
| pre-commit | Git hooks framework | 🔴 Critical | `pre-commit` |
| mise | Version manager | 🟡 High | `mise` |
| just | Task runner | 🟡 High | `just` |
| direnv | Auto environment | 🟡 High | `direnv` |
| watchexec | File watcher | 🟡 High | `watchexec` |
| xh | HTTP client | 🟡 Medium | `xh` |
| yq | YAML processor | 🟡 Medium | `yq` |
| sd | Find/replace | 🟡 Medium | `sd` |
| dust | Disk visualization | 🟡 Medium | `dust` |
| tokei | Code metrics | 🟡 Medium | `tokei` |
| hyperfine | Benchmark CLI | 🟡 Medium | `hyperfine` |
| btop | System monitor | 🟢 Low | `btop` |
| starship | Shell prompt | 🟢 Low | `starship` |
| gdu | Disk analyzer | 🟢 Low | `gdu` |
| rustup-init | Rust toolchain | 🟡 Medium | `rustup-init` |
| pnpm | Package manager | 🟡 Medium | `pnpm` |
| trivy | Container scanning | 🟡 Medium | `trivy` |
| atuin | Shell history search | 🟡 Medium | `atuin` |
| difftastic | Structural diff | 🟡 Medium | `difftastic` |

### npm Global Packages (Keep, don't replace with brew)

These are AI/MCP tools that don't have Homebrew equivalents:
- `@wonderwhy-er/desktop-commander` - MCP server
- `@earendil-works/pi-coding-agent` - AI coding assistant
- `pi-subagents`, `pi-lens`, `pi-web-access` - AI agents
- `gitnexus`, `deepwiki-cli` - Git/wiki tools
- `@brightdata/cli` - Web scraping
- `@fission-ai/openspec` - Spec management

**Decision:** Keep these as npm global packages. They serve specialized AI/MCP functions that Homebrew doesn't provide.

---

## Implementation Strategy

### Phase 1: Security Foundation (Day 1, ~30 minutes)
```bash
# Single Homebrew command for all security tools
brew install gitleaks shellcheck shfmt actionlint pre-commit
```

### Phase 2: Productivity Core (Day 1-2, ~45 minutes)
```bash
# Single Homebrew command for productivity tools
brew install mise just direnv watchexec atuin difftastic
```

### Phase 3: Quality & Observability (Day 2, ~30 minutes)
```bash
# Single Homebrew command for quality tools
brew install xh yq sd dust tokei hyperfine btop starship gdu
```

### Phase 4: Language & DevOps (Day 3, ~30 minutes)

**Total: 24 tools (6 security + 6 productivity + 9 quality + 3 language), all via Homebrew**
```bash
# Language tools + DevOps security
brew install rustup-init pnpm trivy
```

### Total Installation Command
```bash
# One-liner for everything (if desired)
brew install gitleaks shellcheck shfmt actionlint pre-commit mise just direnv watchexec atuin difftastic xh yq sd dust tokei hyperfine btop starship gdu rustup-init pnpm trivy
```

---

## Decision Criteria

| Criterion | npm/cargo/pip | Homebrew-First |
|-----------|---------------|----------------|
| Centralized management | ❌ Multiple managers | ✅ Single manager |
| Automatic updates | ❌ Manual per-tool | ✅ `brew upgrade` |
| Dependency resolution | ❌ Varies by tool | ✅ Handled by brew |
| Consistency | ❌ Mixed methods | ✅ Uniform approach |
| Rollback | ❌ Varies by tool | ✅ `brew uninstall` |
| Disk efficiency | ⚠️ Varies | ✅ Shared dependencies |

**Winner: Homebrew-First** - unified, maintainable, consistent with macOS best practices.

---

## Next Steps

1. Review and approve this proposal
2. Execute Phase 1-4 installation (all via Homebrew)
3. Configure tools (configs, shell integration, pre-commit hooks)
4. Update documentation
5. Archive change after completion