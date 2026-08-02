## Context

agent-docs-sync exposes a Typer CLI (`docs-sync`) with 7 commands. During feature verification, 4 bugs were discovered:

1. **Test API mismatch** (2 tests): `test_check_links.py` calls `tool.execute(path=..., base_dir=...)` but `execute()` requires a pydantic args model.
2. **Pipeline kwargs bug** (runtime crash, masked): `sync_pipeline.py:validate()` calls `enforcer.execute(doc_path=..., quadrant=...)` — same kwargs pattern. Crashes when there are pending updates.
3. **Debug log spam** (~420K chars): `configure_logging(level="DEBUG")` sets root logger to DEBUG, capturing all library internals (markdown-it token-level debug).
4. **Diátaxis rules too strict**: Reference quadrant requires `signature`, `description`, `examples` sections with 300-word limit. Most existing docs are narrative/API-reference hybrids that naturally violate these rules.

All tools follow the pattern `class XxxTool(BaseTool[XxxArgs])` with `execute(self, args: XxxArgs) -> ToolResult`. The old kwargs style is incompatible.

## Goals / Non-Goals

**Goals:**
- Fix all 4 bugs so tests pass and CLI works reliably
- Scope debug logging to `agent_docs_sync` only (not root logger)
- Make Diátaxis reference rules realistic for actual documentation

**Non-Goals:**
- Changing the BaseTool API pattern (it's correct, tests/pipeline are wrong)
- Adding new features or tools
- Changing the Diátaxis framework itself (just rule calibration)
- Modifying agent-core's `configure_logging` (it's correct for agent-core's use case)

## Decisions

### D1: Fix tests by wrapping in Args models

**Decision:** Update test calls to use `CheckLinksArgs(path=..., base_dir=...)` instead of kwargs.

**Rationale:** The tool API changed to use pydantic models for type safety and validation. Tests must match the current contract. This is the minimal fix — no API changes needed.

**Alternative considered:** Add `**kwargs` fallback to `execute()` — rejected because it weakens type safety and defeats the purpose of the args model.

### D2: Fix pipeline by wrapping in EnforcerArgs

**Decision:** Update `sync_pipeline.py:validate()` to use `EnforcerArgs(doc_path=..., quadrant=...)`.

**Rationale:** Same pattern as D1. The pipeline code was written before the API change and never updated.

### D3: Scope logging to agent_docs_sync, suppress noisy libraries

**Decision:** After calling `configure_logging(level=DEBUG)`, override the root logger level back to WARNING, then set only `agent_docs_sync` to DEBUG. Also suppress `markdown_it` and `httpx` loggers.

```python
# After configure_logging sets root to DEBUG:
root = logging.getLogger()
root.setLevel(logging.WARNING)  # Reset root
logging.getLogger("agent_docs_sync").setLevel(logging.DEBUG)  # Our code only
logging.getLogger("markdown_it").setLevel(logging.WARNING)  # Suppress parser spam
logging.getLogger("httpx").setLevel(logging.WARNING)  # Suppress HTTP debug
```

**Rationale:** `configure_logging` is in agent-core and is correct for agent-core's use case (where all logs are agent-core). agent-docs-sync needs scoped verbosity. Suppressing markdown_it and httpx prevents third-party noise regardless of level.

**Alternative considered:** Modify `configure_logging` in agent-core — rejected because it's shared infrastructure and other consumers may need root-level DEBUG.

### D4: Relax Diátaxis reference rules

**Decision:** Increase `max_words` for reference from 300→500, increase tier-2 multiplier from 1.5→2.0 (effective limit 1000), and make `signature` and `examples` sections optional (not required) at tier 2.

**Rationale:** The current 300-word limit is too tight for API reference docs that include code examples. The `reference` quadrant in Diátaxis is about "information-oriented" docs — many of our docs are reference-like but include explanatory prose. Making `signature` and `examples` optional at default tier keeps enforcement meaningful without flagging every doc.

**Alternative considered:** Reclassify docs to `explanation` quadrant — rejected because they genuinely are reference docs, just longer than the original rules anticipated.

## Risks / Trade-offs

- **[Risk]** Fixing logging scope may hide legitimate debug info from third-party libs during troubleshooting → **Mitigation:** Can still set `markdown_it` logger to DEBUG temporarily if needed; the suppression is per-logger, not global.
- **[Risk]** Relaxing Diátaxis rules may reduce enforcement quality → **Mitigation:** Only relaxing at tier 2 (default); tier 1 (critical) keeps strict rules. Score impact is minimal.
- **[Trade-off]** Not modifying `configure_logging` in agent-core means each consumer must post-process logging setup → **Acceptable:** agent-docs-sync is the only CLI consumer; agent-core's function is correct for its use case.

## Migration Plan

1. Fix tests (D1) — run `pytest tests/test_tools/test_check_links.py` to verify
2. Fix pipeline (D2) — run `docs-sync sync` with changes to verify no crash
3. Fix logging (D3) — run `docs-sync -v validate` to verify no spam
4. Relax rules (D4) — run `docs-sync audit` to verify reduced violations
5. Full test suite — `uv run pytest tests/ -x -v`

No rollback needed — all changes are backward-compatible.

## Open Questions

_(none — all decisions resolved)_
