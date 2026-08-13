## 1. User-Level LSP Configuration

- [ ] 1.1 Create `~/.omp/agent/lsp.json` with `diagnosticsOnWrite: true`, `diagnosticsOnEdit: true`, `formatOnWrite: true`, `idleTimeoutMs: 300000`
- [ ] 1.2 Verify user-level LSP settings load by checking diagnostics appear on file edit

## 2. Go Project LSP

- [ ] 2.1 Create `~/Developer/go-microservices/.omp/lsp.json` with gopls settings: `staticcheck: true`, `gofumpt: true`, analyses `["shadow", "unusedwrite", "appendAssign"]`, buildFlags `["-tags=integration"]`
- [ ] 2.2 Verify gopls provides diagnostics and formatting in go-microservices

## 3. Python Project LSP (agent-core)

- [ ] 3.1 Create `~/Developer/agent-core/.omp/lsp.json` with basedpyright settings: `typeCheckingMode: "strict"`, `python.version: "3.14"`, `python.analysis.extraPaths: ["src"]`
- [ ] 3.2 Verify basedpyright provides strict type checking in agent-core

## 4. Python Project LSP (tdt-core)

- [ ] 4.1 Create `~/Developer/tdt-core/.omp/lsp.json` with basedpyright settings: `typeCheckingMode: "basic"`, `python.version: "3.14"`, `python.analysis.extraPaths: ["src"]`
- [ ] 4.2 Verify basedpyright provides basic type checking in tdt-core

## 5. Verification

- [ ] 5.1 Run `openspec verify --change "omp-lsp-integration" --json --store openspec-store` to confirm all artifacts align
- [ ] 5.2 Start new OMP sessions in each project and verify LSP servers start and provide diagnostics
