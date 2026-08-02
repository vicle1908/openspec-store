## Context

The TDT ecosystem consists of 14 Python repos, all using pyproject.toml for packaging. While agent-core has comprehensive uv practices documented in AGENTS.md, other repos have inconsistent adoption:
- Some have uv.lock, some don't
- Some have .python-version, some don't
- Docs reference pip instead of uv
- No standardized [tool.uv] configuration

## Goals / Non-Goals

**Goals:**
- All Python repos have uv.lock committed
- All Python repos have .python-version committed
- All AGENTS.md files document uv practices
- No pip references in active documentation
- Standardized [tool.uv] config across repos

**Non-Goals:**
- Modify CI/CD pipelines (separate change)
- Change existing dependency versions
- Modify runtime code behavior
- Create shared uv wrapper scripts

## Decisions

### D1: Standard [tool.uv] configuration

**Decision:** All repos SHALL use this standard [tool.uv] section (validated against official uv docs):

```toml
[tool.uv]
default-groups = ["dev"]
required-version = ">=0.11.15"
python-preference = "only-managed"
package = true
```

**Rationale:** 
- `default-groups = ["dev"]` — dev dependencies installed by default with `uv sync`
- `required-version = ">=0.11.15"` — ensures minimum uv version for compatibility
- `python-preference = "only-managed"` — uv uses its own Python installs, not system Python (per uv docs: "not recommended" to target system Python)
- `package = true` — force editable install for development (source changes reflect immediately)

### D2: .python-version per repo

**Decision:** Each repo SHALL have .python-version matching its `requires-python` in pyproject.toml:
- `>=3.14,<3.15` → `.python-version` contains `3.14.5`
- `>=3.12` → `.python-version` contains `3.12` (or latest 3.12.x)

**Rationale:** uv uses .python-version to select Python interpreter. Must match pyproject.toml constraints.

### D3: AGENTS.md uv practices section

**Decision:** All Python repos SHALL have a uv practices section in AGENTS.md with:
- Adding dependencies (`uv add`)
- Syncing (`uv sync`)
- Running commands (`uv run`)
- Managing packages (`uv pip`)
- Key rules (never pip, .venv managed by uv, etc.)

**Rationale:** Enforces consistent developer behavior across repos.

### D4: Fix pip references in docs

**Decision:** All active documentation SHALL reference uv commands instead of pip. Research docs with external pip references may keep them as historical context.

**Rationale:** Developers follow docs; pip references teach wrong practices.

## Risks / Trade-offs

- [Risk] Some repos may have constraints preventing uv adoption → Check each repo's pyproject.toml before changing
- [Risk] .python-version changes may affect existing developer environments → Document in AGENTS.md
- [Trade-off] Standardized config reduces flexibility but ensures consistency
