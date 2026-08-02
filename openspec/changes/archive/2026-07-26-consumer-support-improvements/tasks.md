## 1. Bug Fix

- [x] 1.1 Fix syntax error in `sdk/memory.py:63` — changed `except TimeoutError, Exception:` to `except (TimeoutError, Exception):`

## 2. Memory Vector Integration

- [x] 2.1 Added `"vector"` to `MemoryLayer` literal in `memory/types.py`
- [x] 2.2 Added `vector: VectorMemory | None = None` parameter to `Memory.__init__()` in `memory/facade.py`
- [x] 2.3 Added `layer="vector"` handling to `Memory.store()` — delegates to `self.vector.store()`
- [x] 2.4 Added `layer="vector"` handling to `Memory.retrieve()` — delegates to `self.vector.retrieve()`
- [x] 2.5 Added `layer="vector"` handling to `Memory.list_keys()` — delegates to `self.vector.list_keys()`
- [x] 2.6 Updated `Memory.recall()` to include vector search results when vector backend is provided
- [x] 2.7 Updated `Memory.close()` to close vector backend when present
- [x] 2.8 Added `enable_vector: bool = False` and `vector_dsn: str | None = None` parameters to `create_consumer_memory()`
- [x] 2.9 Wired VectorMemory creation in `create_consumer_memory()` with try/except degradation

## 3. SDK Improvements

- [x] 3.1 Added `flavors: list[Flavor] | None = None` parameter to `build_agent()`
- [x] 3.2 When flavors provided, passes to `BaseAgent(flavors=flavors)`; when None, builds default Flavor from config
- [x] 3.3 Added `include_builtins: bool = True` parameter to `build_toolkit()`
- [x] 3.4 Passed include_builtins to `ToolRegistry(include_builtins=include_builtins)`

## 4. Documentation

- [x] 4.1 Added hooks vs capabilities decision matrix to AGENTS.md

## 5. Verification

- [x] 5.1 Ruff check — no new errors
- [x] 5.2 mypy strict — no new errors (5/5 files pass)
- [x] 5.3 pytest — all 497 tests pass
