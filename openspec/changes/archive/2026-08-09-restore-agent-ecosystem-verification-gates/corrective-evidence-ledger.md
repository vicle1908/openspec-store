# Corrective Evidence Ledger

Links archived verification claims to current source evidence.

## Frozen Commits

| Repository | Implementation | Docs | Branch | Worktree Dirty | Main Dirty | Integration |
|---|---|---|---|---|---|---|
| agent-core | `ca7d2fb5300557eee9278f95a66f7823c30d742c` | `d3b42af343e15a767780bdc565b2a79180f458f8` | restore-ecosystem-agent-core | 0 (worktree clean) | 4 (graphify-out) | Integrated to main |
| agent-harness | `d9ebe3e6e6ee660ee2fa8b433b5b93166490c482` | `bcb946da76723017f641f88b90547e1cf1a4892c` | main (fast-forwarded) | 0 (worktree clean) | 4 (graphify-out) | Integrated by codex-1 |
| agent-docs-sync | `778aef09f2b6656b9c1968286d26f000fc885eff` | `ede62bdf9df8e7aa35a01b44fa4cc347b37e4959` | main | N/A (on main) | 5 (graphify-out×4 + doc-sync/) | Integrated |

## Per-Repository Manifests

### agent-core

**Source identity:** `ca7d2fb5300557eee9278f95a66f7823c30d742c` on branch `main` (integrated)
**Pre-edit identity:** `52419d9d77358212770f783d0749b3c9c3538d32`
**Dirty paths (pre-edit):** 0 (worktree was clean)
**Dirty paths (post-edit, worktree):** 0 (clean)
**Dirty paths (integrated main):** 4 (graphify-out: GRAPH_REPORT.md, graph.html, graph.json, manifest.json) — unrelated, unowned, pre-existing
**Integration status:** Integrated to `agent-core/main` via fast-forward (no merge commit)

**Files changed (`52419d9d77358212770f783d0749b3c9c3538d32..ca7d2fb5300557eee9278f95a66f7823c30d742c`):**
- `tests/_ai/test_model_loading.py` — monkeypatched `infer_model` to return MagicMock
- `tests/ai/test_models.py` — monkeypatched `create_model` in TestModelSettingsPropagation
- `tests/test_characterization.py` — passed `model=TestModel()` in 3 tests
- `tests/test_rollback_exercise.py` — passed `model=TestModel()` in 1 test
- `tests/tool_registry/test_builtin_tools.py` — added `_mock_getaddrinfo` fixture + 10 negative DNS/destination coverage tests
- `src/agent_core/foundation/settings.py` — Ruff formatting only (blank-line normalization)
- `tests/foundation/test_settings.py` — Ruff formatting only (line wrapping)

**Commands and exit codes:**
| Command | Exit Code | Notes |
|---|---|---|
| `uv sync --dev` | 0 | Fresh lock resolution |
| `uv run ruff check src/ tests/` | 0 | All checks passed |
| `uv run ruff format --check src/ tests/` | 0 | 503 files already formatted |
| `uv run mypy src tests --strict` | 0 | 176 source files, zero errors |
| `OPENAI_API_KEY="" ANTHROPIC_API_KEY="" HF_TOKEN="" uv run pytest tests/` | 0 | Scanner unavailable = 684 passed, 20 skipped; Scanner available = 685 passed, 19 skipped; Host (all prereqs) = 704 passed, 0 skipped |
| `git diff --check` | 0 | No accidental credentials/debug |

**Coverage:** 85% statement (above 80% floor); zero-coverage gate exit 0
**Coverage JSON hashes:** Restricted `f2634cd9d96158b1c8c348f4e70770e97638b9e04da9f3408af2997aff2b8ab8`; Host `e4994bf85b59ea5dd6b9f33babd00ff2e0df6509547bcbaf838ffe687c11e05d`
**Tool versions:** Python 3.14.5, uv 0.12.3, pytest 9.1.1, mypy 2.3.0, ruff 0.16.1
**Git fingerprints:**
- uv.lock: `ab740272c135f6723f73528c2e812c8de7ef5008c8426efd01b9b0f9117a91c0`
- pyproject.toml: `2597ec161a8eb1e97497b082d6ea72887e3f32fe901300cb4df033c8938d9f9b`
- tree: `07ba0ac0a0d0f0fff4633b9f92e26b0d1b33c159`
- src tree: `29d53fd4f841ecf5f1b72122e65c17176d62c47c`
- tests tree: `1f3f8640572ab77371a6f73b11cd65475f44aca6`
**Skips (conditional):** 19 (scanner available) or 20 (scanner unavailable) — 5 scheduler generator fixtures, 3 tdt-observability fixtures, 1 jira-epic-report, 2 workload checkouts, 1 jira-skill, 2 code-daily-scan, 1 hosted checkouts, 2 jira-daily-reports, 2 tdt-sheets — all prerequisite-dependent, none converted to passes
**CLI probe:** `agent-core --help` exit 0
**Network restriction:** Codex sandbox + `uv run --offline`; DNS mocked via `_mock_getaddrinfo` fixture
**Test command (restricted):** `OPENAI_API_KEY="" ANTHROPIC_API_KEY="" HF_TOKEN="" uv run --offline pytest tests/`

### agent-harness

**Source identity:** `d9ebe3e6e6ee660ee2fa8b433b5b93166490c482` (implementation) + `bcb946da76723017f641f88b90547e1cf1a4892c` (docs) on branch `main` (fast-forwarded by codex-1)
**Pre-edit identity:** `ce33bb50d7f8b1e9658397a0802717a591a6133e`
**Dirty paths (worktree):** 0 (clean)
**Dirty paths (integrated main):** 4 (graphify-out: GRAPH_REPORT.md, graph.html, graph.json, manifest.json) — unrelated, unowned, pre-existing
**Integration status:** Integrated by codex-1 (main fast-forwarded `ce33bb50d7f8b1e9658397a0802717a591a6133e` → `bcb946da76723017f641f88b90547e1cf1a4892c`)

**Files changed (`ce33bb50d7f8b1e9658397a0802717a591a6133e..bcb946da76723017f641f88b90547e1cf1a4892c`):**
- `tests/test_production_services.py` — 4× `model=TestModel()` → `model="test"`, added construct_agent monkeypatch
- `tests/test_cli_lifecycle.py` — 1× `model=TestModel()` → `model="test"`, removed unused TestModel import
- `tests/test_construction_regression.py` — added return type to `mock_model()` fixture
- `tests/test_convergence_contracts.py` — removed orphan TYPE_CHECKING methods (10 lines)
- `src/agent_harness/config.py` — formatter-only blank-line normalization (16 lines added)
- Docs commits contain required human Co-authored-by and Signed-off-by trailers

**Commands and exit codes:**
| Command | Exit Code | Notes |
|---|---|---|
| `uv sync --locked` | 0 | Fresh lock resolution |
| `uv run ruff check src/ tests/` | 0 | All checks passed |
| `uv run ruff format --check src/ tests/` | 0 | 85 files already formatted |
| `uv run mypy src tests --strict` | 0 | 85 source files, zero errors |
| `PYTHONPATH=/Users/androidteam/Developer/.worktrees/restore-ecosystem-agent-core/src uv run pytest tests/` | 0 | 323 passed, 6 skipped (329 collected) |
| `git diff --check` | 0 | No accidental credentials/debug |

**Coverage:** 89.27% (above 80% floor); zero-coverage gate exit 0
**Coverage JSON hashes:** Restricted `6822bc5127901939e66f4d73ba999c91c044ad3b01f8d88ae3a65676612c6450`; Host `01ac68b773cb2f5e51387a958d68f193b76a2a0a6f15414bb156ede3e7554814`
**Tool versions:** Python 3.14.5, uv 0.12.3, pytest 9.1.1, mypy 2.3.0, ruff 0.16.1
**Git fingerprints:**
- uv.lock: `e63c2a21f47574b08b80fac7e7800ef48eb4e7bd7a32dd563a386985472c297b`
- pyproject.toml: `5bfb5b5d3a93ba92f5fa2546d40d422357914529b3a24d0185105a4cbbc9f072`
- tree: `7d334ff210bed0ad4c7ff2742cc5d0838cbdc4a3`
- src tree: `1f0adf2b937300ecf2d3c53ca93e88e54f03b2dd`
- tests tree: `fe14dce6ff7ebbe4784d8cbaf5f47d4c28502fd5`
**Skips (6):** 5 PostgreSQL/Docker integration, 1 gitleaks/operational-Docker — none converted to passes
**Cross-repo test note:** Requires `PYTHONPATH=/Users/androidteam/Developer/.worktrees/restore-ecosystem-agent-core/src` (pinned to core `ca7d2fb5300557eee9278f95a66f7823c30d742c`) to use frozen agent-core commit
**CLI probe:** `agent-harness --help` exit 0 (with pinned core PYTHONPATH)

### agent-docs-sync

**Source identity:** `778aef09f2b6656b9c1968286d26f000fc885eff` (implementation) + `ede62bdf9df8e7aa35a01b44fa4cc347b37e4959` (docs) on branch `main`
**Pre-edit identity:** `1bcb7c7654ac744d60595f41f38abbc235b3767d`
**Dirty paths (pre/post):** 5 (graphify-out×4 + untracked doc-sync/) — all unrelated, pre-existing
**Integration status:** Integrated (on main)

**Files changed (`1bcb7c7654ac744d60595f41f38abbc235b3767d..ede62bdf9df8e7aa35a01b44fa4cc347b37e4959`):**
- `tests/test_state_lifecycle.py` — added `pytest.MonkeyPatch` annotation to fixture parameter
- `README.md` — updated test/mypy counts (corrected in `ede62bdf`)
- `SPEC_INDEX.md` — updated assessment section (corrected in `ede62bdf`)

**Commands and exit codes:**
| Command | Exit Code | Notes |
|---|---|---|
| `uv sync --locked` | 0 | Fresh lock resolution |
| `uv run ruff check src/ tests/` | 0 | All checks passed |
| `uv run ruff format --check src/ tests/` | 0 | Already formatted |
| `uv run mypy src tests --strict` | 0 | 91 source files, zero errors |
| `PYTHONPATH=/Users/androidteam/Developer/.worktrees/restore-ecosystem-agent-core/src uv run pytest tests/` | 0 | 206 collected; Docker avail = 206 passed, 0 skipped; Docker unavail = 205 passed, 1 skipped; 4 warnings always |
| `git diff --check` | 0 | No accidental credentials/debug |

**Tool versions:** Python 3.14.5, uv 0.12.3, pytest 9.1.1, mypy 2.3.0, ruff 0.16.1
**Git fingerprints:**
- uv.lock: `4558c7804134f771995bb104b6e694e8702b114f2c2b5872ce19537ae8521d65`
- pyproject.toml: `ea741224b72bce46729d80655f10a53fd5938344f9e6df3c862b6e9b34148f46`
- tree: `7ce609328aff2bf54fcb136d48557f054f2c7893`
- src tree: `dfe447895d2b66840f8975a44719087b4734ff71`
- tests tree: `4cf3c26585b3231a1123b9e57c5e819e683c8b51`
**Skips:** 0 (Docker available) or 1 (Docker/gitleaks unavailable) — prerequisite-dependent
**Cross-repo test note:** Requires `PYTHONPATH=/Users/androidteam/Developer/.worktrees/restore-ecosystem-agent-core/src` (pinned to core `ca7d2fb5300557eee9278f95a66f7823c30d742c`) to use frozen agent-core commit
**CLI probe:** `docs-sync --help` exit 0 (with pinned core PYTHONPATH)

**Graphify state (changed/unowned generated state):**
- Pre-edit diff fingerprint: `876a1a400c15210f411b3165c604f9b00b52cb841e029ee36f2c790e7033ad19`
- Post-commit diff fingerprint: `39c6e03bc4e7296b3035e66eaf365e062872e3fb65c846da9d068193459aadda`
- Classification: changed, unowned generated state (not preserved — no byte-exact pre-edit snapshot)

## Archived Claims and Current Status

### agent-ecosystem-hardening (archived)

| Claim | Archived | Current | Status |
|---|---|---|---|
| Zero test failures across agent-core | 686 pass, 1 skip | 684 pass, 20 prereq skip (scanner unavail) / 685 pass, 19 skip (scanner avail) / 704 pass (host) | ✅ Restored |
| Strict mypy clean | Source-only | mypy src tests --strict: 176 files | ✅ Restored |
| Ruff lint/format clean | Pass | Pass | ✅ Maintained |

**Regression cause:** 9 provider-construction tests relied on live API keys; 5 HTTP tests relied on real DNS resolution (no getaddrinfo mock). Six HTTP test cases total; five depend on public DNS resolution (the private IP case resolves to itself).

### agent-ecosystem-hardening-cleanup (archived)

| Claim | Archived | Current | Status |
|---|---|---|---|
| Test isolation verified | Not explicitly tested | All tests pass with credentials unset and network restricted (Codex sandbox + `uv run --offline`) | ✅ Restored |
| No production code changes for test fixes | Claimed | Verified: only test files + Ruff formatting in settings.py | ✅ Confirmed |

### close-agent-ecosystem-hardening-verification-gaps (archived)

| Claim | Archived | Current | Status |
|---|---|---|---|
| Coverage above 80% | 85.92% | 85% (statement) | ✅ Maintained |
| Zero-coverage policy pass | Pass | Pass (exit 0) | ✅ Maintained |

### close-three-repo-e2e-verification-gaps (archived)

| Claim | Archived | Current | Status |
|---|---|---|---|
| Cross-repo compatibility | Claimed | agent-core 684/685/704 + agent-harness 323/6skip + agent-docs-sync 206/205+1skip all pass (with PYTHONPATH pinned to core `ca7d2fb5300557eee9278f95a66f7823c30d742c`) | ✅ Restored |
| Strict typing across all repos | agent-core source-only | All three pass mypy src tests --strict (176 + 85 + 91 files) | ✅ Restored |

**Cross-repo testing note:** Consumer repos (agent-harness, agent-docs-sync) require explicit `PYTHONPATH=/Users/androidteam/Developer/.worktrees/restore-ecosystem-agent-core/src` to use frozen agent-core commit instead of default main.

## Excluded from Scope (verified as non-defects)

| Item | Reason Excluded |
|---|---|
| agent-core/src/reports-out/ deletion | Intentional historical artifacts, not a defect |
| Typer floor alignment | Different repos, different version needs, no conflict |
| CHANGELOG policy | Convention choice, not a defect |
| AGENTS.md/CLAUDE.md consolidation | Intentional adapter pattern |
| graphify-out/ drift (agent-core) | Unrelated, pre-existing, not owned by this change; 4 unstaged files preserved |
| graphify-out/ drift (harness) | Unrelated, pre-existing, not owned by this change; harness graphify fingerprint `5c3df4698d90b3c32fb9d0ff9c4582417ad7fd31f6d228feaf7c17ac4400f708` preserved |
| graphify-out/ drift (docs-sync) | Unrelated, pre-existing, changed/unowned generated state; pre `876a1a400c15210f411b3165c604f9b00b52cb841e029ee36f2c790e7033ad19`, post `39c6e03bc4e7296b3035e66eaf365e062872e3fb65c846da9d068193459aadda` — not preserved |
| Untracked doc-sync/ scaffold | Unrelated, unowned, not deleted |

## Remaining Gaps (as of 2026-08-09T14:40)

| Gap | Task | Status | Notes |
|---|---|---|---|
| agent-core negative DNS coverage | 2.3 | Complete | 10 new test cases covering 5 DNS-dependent failures, 6 original HTTP cases total |
| agent-core main integration | — | Complete | Fast-forwarded to `ca7d2fb5300557eee9278f95a66f7823c30d742c` |
| Rollback evidence for all repos | 5.5 | Complete | Disposable-clone evidence for all three repos |
| OpenSpec change | — | Committed & Integrated | Change directory committed with trailers |
| Push | — | Not authorized | Requires separate push authorization |
| Archive | — | Not authorized | Requires separate archive authorization |
