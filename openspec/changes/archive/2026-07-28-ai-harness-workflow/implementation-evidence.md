# Implementation evidence

## Scope

- Change: `ai-harness-workflow`
- Implementation repository: `/Users/lekhanhvinh/Developer/tdt/ai-harness-skills`
- Product boundary: standalone alternative to `agent-harness`; no shared imports,
  runtime state, checkpoints, or APIs
- Package/command: `ai_harness` / `harness`
- Python: 3.14
- OpenSpec schema: `harness-13`
- Portable skills: `harness-workflow`, `harness-gates`, `harness-traceability`

## Deterministic release gate

Run from `ai-harness-skills`:

```bash
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run mypy src tests --strict
uv run pytest -q
openspec schema validate harness-13
npx skills-ref validate skills/harness-workflow
npx skills-ref validate skills/harness-gates
npx skills-ref validate skills/harness-traceability
```

Results on 2026-07-28:

- frozen sync: passed, 30 packages checked
- ruff lint: passed
- ruff format: 99 files formatted
- strict mypy: passed, 62 source files
- pytest: 142 passed, 2 opt-in live-provider smoke tests skipped
- coverage: 86.88%, exceeding the approved 80% threshold
- `harness-13`: valid under installed OpenSpec 1.6.0
- all three portable skills: valid under `skills-ref` 0.1.5

The two skipped tests require `AI_HARNESS_LIVE_SMOKE=1`, authenticated local
provider CLIs, read-only execution, and explicit finite budgets. Their documented
skip is the accepted non-live environment outcome.

## Installation and clean-checkout evidence

- `npx skills add <local-source> --agent codex --skill harness-workflow
  harness-gates harness-traceability --copy -y` installed exactly three skills in
  an isolated Git project.
- A clean temporary Git checkout built successfully with `uv sync --frozen` and
  `uv run harness --help`.
- Initializer tests cover dry-run, clean install, symlinked OpenSpec roots,
  idempotent repeat install, compatible upgrade, unmanaged/modified conflict,
  partial-failure transaction rollback, and ownership-safe rollback.

## Security evidence

```bash
uvx pip-audit --path .venv/lib/python3.14/site-packages \
  --progress-spinner off --skip-editable
```

Result: no known dependency vulnerabilities. The editable first-party distribution
is intentionally excluded from dependency CVE lookup; ruff, strict mypy, focused
security/failure tests, and review cover that residual risk.

Security tests cover shell metacharacters and option-like input, traversal and
symlink escape, provider-side artifact tampering, stale/replayed/cross-boundary gate
decisions, clarification identity, concurrent advancement and stale leases,
timeouts/cancellation/output/request/token/cost limits, changing capabilities, and
secret-safe persistence/output/events.

## OpenSpec verification

Run from `tdt-meta`:

```bash
openspec validate --strict ai-harness-workflow
openspec instructions apply --change ai-harness-workflow --json
```

Expected result: strict validation passes and progress reports `180/180` complete.
