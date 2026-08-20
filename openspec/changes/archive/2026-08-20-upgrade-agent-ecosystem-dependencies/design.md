## Design: Agent Ecosystem Dependency Upgrade

### Version Constraint Changes

#### Pydantic AI (`pydantic-ai`)

| Repo | Current | Target | Rationale |
|---|---|---|---|
| agent-core | `>=2.31.0,<2.32` | `>=2.31.0,<2.33` | Unlock v2.32.0 capability primitives |
| agent-harness | `>=2.31.0,<2.32` | `>=2.31.0,<2.33` | Align with agent-core |
| agent-docs-sync | `>=2.31.0,<2.32` | `>=2.31.0,<2.33` | Align with agent-core |

**v2.32.0 key features unlocked:**
- Capability Primitive: single composable unit for instructions, tools, hooks, settings
- Built-in capabilities: `Thinking(effort='high')`, `CodeMode()`, `WebSearch()`, `ToolSearch()`
- Core/Harness split: `pydantic-ai` (core, stable) vs `pydantic-ai-harness` (fast-moving)
- Native MCP support through capabilities

**Breaking changes from v2.31.x to v2.32.0:**
- OpenAI model names now use Responses API by default (use `openai-chat:` prefix for Chat Completions)
- WebSearch/WebFetch native by default; `MCP(url=...)` runs locally by default
- Instrumentation defaults to v5 with aggregated token-usage attributes
- Function tools alongside successful output now run instead of being skipped

**Migration path:** The workspace does not use OpenAI models directly (routes through custom API endpoint), does not use WebSearch/WebFetch tools, and instrumentation version is configured explicitly. Risk of breakage is LOW.

#### pydantic-ai-harness

| Repo | Current | Target | Rationale |
|---|---|---|---|
| agent-core | `==0.11.0` | Latest stable | Remove exact pin, reduce coordination overhead |
| agent-harness | `==0.11.0` | Latest stable | Align with agent-core |
| agent-docs-sync | `==0.11.0` | Latest stable | Align with agent-core |

**Investigation required:**
1. Check PyPI for latest stable version of `pydantic-ai-harness`
2. Review changelog for breaking changes since 0.11.0
3. Determine if version bump is safe or if exact pin should be preserved at a newer version

**Fallback:** If harness has breaking changes, keep exact pin at latest known-working version rather than using range.

#### OpenTelemetry SDK

| Repo | Current | Target | Rationale |
|---|---|---|---|
| agent-core | `>=1.40.0,<1.45.0` | Keep or widen slightly | No urgent need; review if v1.45+ has needed features |
| agent-harness | `>=1.40.0,<1.45.0` | Keep or widen slightly | Align with agent-core |

**Decision:** Defer OTel changes unless investigation reveals needed features in newer versions.

### Verification Strategy

#### Per-Repo Verification Gates

```bash
# From each repo worktree
uv sync                              # Resolve updated lockfile
uv run pytest                        # Full test suite
uv run ruff check . --select I001    # Import ordering
uv run ruff format --check .         # Format check
uv run mypy src/ --strict            # Type checking
```

#### Cross-Repo Verification

- agent-harness imports agent-core (editable path) — verify import chain works
- agent-docs-sync imports agent-core (editable path) — verify import chain works
- Both consumer repos must pass full test suites after agent-core upgrade

#### Pre-Upgrade Baseline

Capture test counts and lint findings before upgrade:
```bash
# Per repo
uv run pytest --co -q | tail -1     # Count tests
uv run ruff check . --select I001   # Baseline I001 count
```

### Rollback Approach

1. **Per-repo:** `git checkout main -- pyproject.toml uv.lock` reverts dependency changes
2. **OpenSpec change:** Preserved in archive with full context
3. **Lockfile:** `uv sync` regenerates from pyproject.toml constraints

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| pydantic-ai v2.32.0 breaking changes | Low | Medium | Workspace doesn't use affected features (OpenAI models, WebSearch) |
| pydantic-ai-harness breaking changes | Medium | Medium | Investigate first; pin to exact version if needed |
| Lockfile resolution conflicts | Low | Low | `uv sync` handles resolution; revert if needed |
| Type errors from new pydantic-ai | Low | High | Run mypy strict; fix any new errors |

### Approach

1. **Investigate** latest stable versions (pydantic-ai-harness, pydantic-ai changelog)
2. **Update** pyproject.toml in all 3 repos
3. **Resolve** lockfiles via `uv sync`
4. **Verify** full test suites pass
5. **Fix** any type errors or test failures
6. **Commit** per repo
7. **Archive** OpenSpec change
