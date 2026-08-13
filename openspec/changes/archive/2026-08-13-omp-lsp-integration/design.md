# Design: omp-lsp-integration

## Context

OMP's LSP subsystem auto-detects servers by intersecting root markers (go.mod, pyproject.toml) with binary availability on PATH. Config merges from multiple sources: ~/lsp.json → ~/.omp/agent/lsp.json → <cwd>/.omp/lsp.json → <cwd>/lsp.json (lowest to highest precedence). No customization exists today — diagnosticsOnEdit defaults false, formatOnWrite defaults false, no server-specific settings.

## Goals / Non-Goals

Goals:
- Enable real-time diagnostics (diagnosticsOnEdit: true) and auto-formatting (formatOnWrite: true)
- Configure gopls for Go with staticcheck, gofumpt, and relevant analyses
- Configure pyright/basedpyright for Python with appropriate type checking modes
- Create per-project overrides for Go and Python projects
- Set global idle timeout for all language servers

Non-Goals:
- Configuring TypeScript, Swift, Kotlin, or other languages
- Modifying OMP source code or LSP engine
- Adding new language servers not in the built-in list
- Changing model roles or provider configuration

## Decisions

1. User-level lsp.json at ~/.omp/agent/lsp.json — single source for global LSP defaults, highest user-level precedence
2. diagnosticsOnEdit: true — enables real-time feedback, may increase CPU on large files (acceptable trade-off)
3. formatOnWrite: true — auto-format on save using language server formatter, consistent code style
4. idleTimeoutMs: 300000 — 5-minute idle shutdown, balances memory savings vs cold-start latency
5. Go: gopls with staticcheck + gofumpt — industry-standard Go toolchain, staticcheck catches real bugs
6. Python: basedpyright with per-project typeCheckingMode — strict for agent-core (library quality), basic for tdt-core (application code)
7. Per-project .omp/lsp.json — leverages OMP's config merging, project-specific overrides don't affect other projects
8. Config merging is shallow per server — higher-precedence overrides replace entire server objects, not deep-merge fields

## Risks / Trade-offs

- formatOnWrite may conflict with user's manual formatting habits (can disable per-project)
- diagnosticsOnEdit may cause lag on very large files (mitigated by lazy startup)
- gopls analyses add CPU overhead but catch real bugs (worth it)
- Per-project configs add maintenance burden but prevent cross-project interference
