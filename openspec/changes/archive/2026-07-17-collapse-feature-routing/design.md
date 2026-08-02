## Context

`code-daily-scan` produces a `Finding.feature` string at scan time using
`feature_resolver.resolve_feature()`. The tab that this feature maps to
is determined by `feature_resolver.feature_to_tab()` (which uses
`FEATURE_TAB_MAP`). The full picture today:

| Path | Source of tab | Status |
|---|---|---|
| Production CLI (`sheets/writer.py:267`) | `finding.feature` -> `feature_to_tab` | Canonical |
| Plugin's `resolve_finding_tab()` (Android + iOS) | `finding.feature` -> `feature_to_tab` (fallback to `resolve_tab(file_path)`) | Canonical |
| Plugin's `resolve_tab(file_path)` (iOS) | `resolve_feature` + `feature_to_tab` | Canonical |
| Plugin's `resolve_tab(file_path)` (Android) | `resolve_feature` for `.kt` only; **falls through to `ANDROID_FEATURE_PATTERNS` for non-`.kt`** | Drifted |
| `SheetMapper` (with plugin) | delegates to plugin | Canonical |
| `SheetMapper` (no plugin) | `_fallback_tab_name` -> dynamic TitleCase tab names | Spec-silent, used by tests |
| `sheets/mapper.py:_DEFAULT_MODULE_PATTERNS` | substring matching with 30 fragment->tab pairs | Legacy fallback |

The Android-only local table (`ANDROID_FEATURE_PATTERNS`, 63 tokens) has
already diverged from the canonical `FEATURE_RULES` (99 tokens) by 57
tokens. The `SheetMapper` fallback emits fabricated tab names
(`Depositfunds`, `Profileviewmodel`) that no part of the spec or feature
taxonomy ever defined. The android plugin spec promises 21 tabs (10
features + 11 infrastructure) that the implementation never built.

The change is scoped to `code-daily-scan/` (Python) and
`tdt-meta/openspec/changes/unified-code-daily-scan/` (specs). It does not
touch the platform-level `tdt/AGENTS.md` or `tdt/CLAUDE.md`, the iOS or
Android mobile app repos, or any other TDT service.

## Goals / Non-Goals

**Goals:**

- Single source of truth for tab names: `feature_resolver.FEATURE_TAB_MAP`
  and `feature_to_tab()` are the only sanctioned entry points.
- Android plugin's `resolve_tab()` mirrors the iOS plugin (delegates to
  `resolve_feature` + `feature_to_tab`).
- Resource files in `res/` resolve to `Common` per the spec (this is
  already true via `ANDROID_ONLY_RULES`, but the old
  `.endswith((".xml", ...))` check could mask it; reorder so the
  resolver runs first).
- `SheetMapper` requires a plugin in production; the dynamic
  TitleCase fallback is deleted.
- Spec at `android-plugin/spec.md` matches the implementation (10
  features + `Common`).
- Contract tests pin the `FEATURE_TAB_MAP` vocabulary and the
  `feature_to_tab` mapping so future drift triggers a test failure.

**Non-Goals:**

- Implementing the 11 phantom infrastructure tabs. The implementation is
  the contract (Phase 9 unified taxonomy).
- Adding new feature tokens to `FEATURE_RULES`. The change is strictly
  about removing duplication.
- Touching the iOS plugin (already follows the desired pattern).
- Touching platform-level `AGENTS.md` / `CLAUDE.md` or mobile app repos.

## Decisions

### D1. Delete `ANDROID_FEATURE_PATTERNS` rather than merging it into `FEATURE_RULES`

**Rationale:** 57 of the 63 local tokens have no equivalent in the
canonical resolver. The simplest correct move is to delete the duplicate
and let every `.kt` / non-`.kt` path route through the same resolver. The
iOS plugin already does this. If the resolver drops a path to `Others`
that the local table used to bucket into a feature, the right long-term
fix is to add a token to the resolver (with a regression test), not to
recreate the local table.

**Alternative considered:** copy the 57 divergent tokens from the local
table into `FEATURE_RULES`. Rejected: this would silently re-introduce
the very duplication we are trying to remove, and the local tokens
are often redundant with the canonical ones (e.g. `mfa/` vs `mfa`).

### D2. Reorder resource-file routing to consult the resolver first

**Rationale:** The spec at
`android-plugin/spec.md:30` says "Resource files SHALL map to Common".
The current `resolve_tab()` checks `.endswith((".xml", ".layout",
...))` *before* calling the resolver, which would mask the resolver's
`Common` answer for any path where the resolver returned a non-`Others`
value. Since the resolver already routes `res/<X>` to `Common` via
`ANDROID_ONLY_RULES`, the only thing the extension check needs to do is
catch genuinely-unmapped files. We re-order: resolver first, extension
fallback last.

**Alternative considered:** delete the extension check entirely. Rejected:
the spec lets us keep it as a safety net for `.xml` files that the
resolver doesn't already recognise (e.g. `app/src/main/res/raw/data.xml`
in an unmapped subtree). The re-order preserves the safety net without
the masking.

### D3. Make `SheetMapper` plugin-required; delete `_fallback_tab_name`

**Rationale:** `_fallback_tab_name` emits dynamic TitleCase tab names
(`Depositfunds`, `Profileviewmodel`) that no spec, no test, and no human
ever designed. The fallback is only exercised when callers forget to
inject a plugin — which is exactly the failure mode we want to surface
in tests, not silently absorb in production. Three legacy test paths
construct `SheetMapper(plugin=None)`; they are migrated to inject a
plugin.

**Alternative considered:** keep the fallback and add a `DeprecationWarning`.
Rejected: a warning that fires on the test path is noise; a warning that
fires in production because of a bug is something we want to surface as
an error. There is no production code path that constructs
`SheetMapper(plugin=None)`, so a hard error is safe.

### D4. Add a contract test, do not rely on documentation

**Rationale:** The drift between `ANDROID_FEATURE_PATTERNS` and
`FEATURE_RULES` went unnoticed for weeks. A test in
`test_feature_resolver.py` that asserts `FEATURE_TAB_MAP` is a fixed
set, and a test in `test_sheet.py` that asserts
`_DEFAULT_MODULE_PATTERNS` is a subset of `FEATURE_TAB_MAP`, will catch
the same kind of drift in the future. The two tests are <50 lines and
run in milliseconds.

**Alternative considered:** lint the entire codebase for any new tab-name
constant. Rejected: too noisy, too easy to bypass with a typo.

### D5. Strike the 11 phantom tabs from the spec, do not implement them

**Rationale:** VERIFICATION.md:16 states "Cross-platform: Both platforms
use identical 10-feature taxonomy" as the Phase 9 goal. The
android-plugin spec was the only place that still committed to the
pre-Phase-9 module-based routing. Updating the spec to match the
implementation (10+1) is one paragraph; implementing the 11 tabs would
require new path normaliser rules, new tokens, and a new mapping in
`FEATURE_TAB_MAP`, with no clear demand from either platform's actual
findings.

**Alternative considered:** implement the 11 tabs. Rejected: cost
significantly outweighs benefit, and the iOS spec is the source of
truth for cross-platform parity.

## Risks / Trade-offs

- **Risk:** Existing `app/src/main/res/auth/login_button.xml` paths that
  the local table used to bucket into `Auth` will now resolve to
  `Common`. **Mitigation:** the contract test pins this behaviour, and
  the reordering is captured in the writer's updated docstring so
  reviewers know what changed.
- **Risk:** The 3 legacy test paths in `test_sheet.py` and
  `test_alignment_fixes.py` will need to be migrated to inject a plugin.
  **Mitigation:** each migration is a 1-line change
  (`plugin=PLUGINS["android"]` or equivalent).
- **Risk:** Someone reading the spec six months from now will not know
  why the 11 infrastructure tabs were dropped. **Mitigation:** the
  proposal.md and this design.md are archived with the change; the
  commit messages and the canvas both point back to the source.
- **Risk:** `SheetMapper` raising on `plugin=None` is a runtime change
  for any operator who constructed it that way. **Mitigation:** there
  is no production code path that does this; the production CLI always
  injects a plugin. The 3 test paths are migrated in the same change.
- **Trade-off:** We are NOT extracting the routing logic into a third
  shared module. The duplication is only 2 lines per platform
  (`resolve_feature(file_path, platform="x")` + `feature_to_tab(feature)`).
  Extracting it would add a layer of indirection that earns its keep
  only if a third platform joins, which is not on the roadmap.

## Migration Plan

The change is deployed as a single conventional-commit per task group
(R1, R2, R3, R4, R5, R6). Each commit is independently revertable.
Verification gates:

1. `uv run ruff check src/ tests/`
2. `uv run mypy src/`
3. `uv run pytest -q` (must show 378 -> 380 passing — the 2 new contract
   tests in R4)
4. `openspec validate collapse-feature-routing --strict`

The change is rolled out as a normal code-daily-scan change. There are
no schema changes, no config changes, and no operator-visible
behavioural changes for the production CLI path. The only observable
delta is:

- For the ~3 unmapped non-`.kt` paths that the local table used to
  bucket (e.g. `app/src/main/res/auth/foo.xml` -> `Auth`), the new
  behaviour is `Common`. This is the spec's stated contract.

**Rollback:** revert the R1 commit. The Android plugin falls back to
the previous behaviour (with the local table intact). The contract
tests in R4 are additive and safe to keep.

## Open Questions

None. The user has approved the recommendations via the prior canvas
review. The change is internally consistent with the verified
production behaviour.
