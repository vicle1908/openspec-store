# Design: Docs-Repo as Canonical Rule Source

## Architectural shape

`code-daily-scan` already has a clean seam at `PlatformPlugin.rules_loader_cls`. Each platform (Android, iOS) ships a `RulesLoader` whose sole job is to translate markdown rule files into `list[RulePattern]`. Today the loader only knows two roots:

```python
# AndroidRulesLoader.load / load_category
target_root / "docs" / "rules" / "categories"
target_root / "docs" / "technical-debt-scan" / "categories"  # legacy fallback
```

We're adding a **third, higher-priority root**:

```python
rules_repo_root / "20.Developments/40.AI/50.RCA" / "<platform-key>" / "rules" / "categories"
```

and teaching the plugin to consult the new `ScanConfig` field `rules_repo_path`.

### Three concentric layers

The change has three layers, **outermost** = team-facing contract, **innermost** = scanner data-source wiring.

| Layer | Audience | Stability | Owner |
|---|---|---|---|
| **L1 — Cross-team evolution envelope (E-1..E-5)** | Anyone who edits the docs repo (humans, AI agents) | Living document, evolves with each rule PR | PM/Scanner lead |
| **L2 — Schema and provenance contract (S-1..S-8)** | Anyone who reads the docs repo (AI agents, scanners, RCA tools) | Bumps require changelog entry | Scanner lead |
| **L3 — Scanner data-source wiring** | `code-daily-scan` operators | Code, evolves via OpenSpec | Scanner team |

The scanner is **just one consumer** of L1+L2. The AI `p3-scan-technical-debt` skill, the `p3-bug-fixing-report` agent, the `p3-rca-assistant` agent, and the daily `code-daily-scan` scanner all consume the same contract. The contract is therefore the product; the wiring is a delivery mechanism.

### Two operational surfaces (added by the team-wide SoT expansion)

In the team-wide SoT expansion, the architecture gains two new operational surfaces that sit alongside L3:

| Surface | Purpose | Audience |
|---|---|---|
| **L4 — Drift detection (D-1..D-5)** | Compares canonical vs mirror and surfaces drift at runtime, via a dedicated `check-docs-drift` CLI, and as a non-blocking CI guard in v2 | Operators; CI |
| **L5 — Mirror sync (M-1..M-5)** | Pushes canonical → mirror with safety guards (`--force`, `--force-clobber`); produces an audit trail | Operators maintaining app-repo mirrors |

**Surfacing decisions:**
- Drift detection is **runtime-only in v1** (D-5 scenario). It emits log lines; CI integration lands in v2.
- `sync-rules` is **explicit, opt-in** — never auto-runs. The default policy is to refuse writes when mirror content diverges (M-1 scenario 2).
- Mirror retirement is **phased over 3 releases** (M-4): v1 detection, v2 sync + CI guard, v3 mirrors deleted from app repos.
- **Offline-first operators** (developers without a docs-repo checkout) remain supported via the `rules_repo_path: ""` explicit-empty-string mode, which falls through to legacy YAML exactly as today.

### Resolution order

Each rule-category file (`crash-runtime.md`, `memory-lifecycle.md`, ...) is loaded **once per scan** from the highest-priority root that contains at least one matching file:

```
Priority 1 (authoritative):
  /<rules_repo>/20.Developments/40.AI/50.RCA/<plat>/rules/categories/<file>.md
  - "20.AOS"  for android
  - "10.iOS"  for ios

Priority 2 (per-platform local mirror):
  /<target_root>/docs/rules/categories/<file>.md                 [android]
  /<target_root>/docs/technical-debt-scan/categories/<file>.md  [ios]

Priority 3 (legacy, final fallback):
  /<scanner_pkg_root>/config/rule_patterns.yaml                 [deprecated; one release]
```

We stop at the first priority whose category contains rules. We **never** merge rules from multiple layers for the same category — that would silently re-introduce the divergence this change exists to eliminate.

### iOS category-map gap (must be closed before rollout)

The current `IOS_CATEGORY_MAP` in `plugins/ios/rules_loader.py` has **no prefix entries** for four of the nine docs-repo category files:

- `naming-readability.md`
- `pattern-consistency.md`
- `state-mutation.md`
- `testing-coverage.md`

Without these prefixes, `load_category()` silently drops those rules. This change **MUST extend `IOS_CATEGORY_MAP`** with these four prefixes mapped to existing scanner categories. The Android `FILENAME_CATEGORY_MAP` already contains the equivalent mappings so no Android changes are needed.

Two acceptable resolutions for the scanner-dispatch mismatch (e.g. parsed `State Mutation` has no matching `IOSStateMutationScanner`):

1. **Recommended.** Remap the four categories at parse time to canonical scanner categories they semantically subsume (`State Mutation → Lifecycle`, `Naming & Readability → Maintainability`, `Pattern Consistency → Maintainability`, `Testing Coverage → Maintainability`). The persisted `RulePattern.category` stays as parsed (RCA reports keep their names); only the GrepScanner dispatch uses the remapped name.
2. Alternative: add four new scanner classes. Larger diff, no functional advantage.

The spec adopts option (1); tasks §4.4 covers it.

### Frozen-dataclass rebuild pattern

`PlatformConfig` (`config.py`) is `@dataclass(frozen=True, slots=True)`. **Every env / CLI override rebuilds the full instance** with every field (`config.py:218–307`, **nine explicit rebuild sites**: 5 for environment variables plus 4 for CLI overrides, plus the final `ScanConfig` construction). Adding `rules_repo_path` requires touching **all nine** rebuild sites plus the `default_repo_path` callers. `mypy --strict` catches any miss loudly.

The change adopts a `RULES_REPO_PATH_ENV` constant per platform (`CODE_DAILY_SCAN_ANDROID_RULES_REPO`, `CODE_DAILY_SCAN_IOS_RULES_REPO`) for parity with the existing `*_REPO_PATH_ENV` pattern.

### Identifying "the docs repo"

A new `rules_repo_path` field on both `PlatformConfig` (Android) and the iOS platform cfg, defaulting to `~/Developer/tdt/poems-mobile3-docs` when unset. The field is:

- **Required** in the sense that `ScanConfig` will populate it; the operator can override per platform.
- **Optional** in the sense that, if the resolved path doesn't exist or contains no matching categories, the loader falls back transparently and logs the source chosen.

Default resolver chain:

```python
def resolve_rules_repo_path(platform: str) -> Path:
    env_key = f"CODE_DAILY_SCAN_{platform.upper()}_RULES_REPO"
    explicit = os.environ.get(env_key)
    if explicit:
        return Path(explicit).expanduser()
    config_value = _scan_config[platform].get("rules_repo_path")
    if config_value:
        return Path(config_value).expanduser()
    return (Path.home() / "Developer" / "tdt" / "poems-mobile3-docs").resolve()
```

This mirrors the existing resolution pattern in `config.get_config_path()` (which honours `TDT_HOME` before falling back to `~/.tdt/`).

### Logger contract

Every scan emits one log line per category describing the source that won:

```
[android] category=Crash resolved_source=docs_repo:/abs/path/to/poems-mobile3-docs/.../crash-runtime.md rule_count=9 fingerprint_sha=ab12...
[android] category=Memory Leak resolved_source=local_mirror:/abs/path/.../memory-lifecycle.md rule_count=6 fingerprint_sha=...
[android] category=Security resolved_source=legacy_yaml:rule_patterns.yaml rule_count=4 fingerprint_sha=...
```

`fingerprint_sha` is `hashlib.sha256(path.read_bytes()).hexdigest()[:12]`. This lets ops corroborate the rule version with a docs-repo SHA without the scanner depending on a git library.

### Path-resolution implementation

In `code_daily_scan/plugins/android/rules_loader.py` and the iOS twin:

```python
class AndroidRulesLoader:
    # Existing attribute - new accepted kwarg in the constructor:
    def __init__(self, root: Path | None = None, rules_repo: Path | None = None) -> None:
        self.root = root
        self.rules_repo = rules_repo

    def load(self, root: Path, *, rules_repo: Path | None = None) -> list[RulePattern]:
        target_root = root
        rules_repo_root = rules_repo or self.rules_repo
        ...

        # Priority 1 — docs repo
        if rules_repo_root:
            primary = rules_repo_root / "20.Developments/40.AI/50.RCA" / "20.AOS" / "rules" / "categories"
            if primary.exists():
                rules = self._parse_dir(primary, source_label=f"docs_repo:{primary}")
                if rules:
                    return rules

        # Priority 2 — local mirror
        local = target_root / "docs" / "rules" / "categories"
        if local.exists():
            rules = self._parse_dir(local, source_label=f"local_mirror:{local}")
            if rules:
                return rules

        legacy = target_root / "docs" / "technical-debt-scan" / "categories"
        ...

        # Priority 3 — legacy YAML
        ...
```

`load_category()` follows the same priority order but is filtered to the requested category. The fingerprint log line is emitted in both `load()` (one-per-scan summary) and `load_category()` (per-category, in case callers want fine-grained provenance).

### Config schema additions

`~/.tdt/code-daily-scan.yaml`:

```yaml
android:
  repo_path: ~/Developer/tdt/poems-mobile3-android
  spreadsheet_id: "..."
  rules_repo_path: ~/Developer/tdt/poems-mobile3-docs        # NEW (Optional)
  cron: "0 7 * * *"
  timezone: "Asia/Ho_Chi_Minh"

ios:
  repo_path: ~/Developer/tdt/poems-mobile3-ios
  spreadsheet_id: "..."
  rules_repo_path: ~/Developer/tdt/poems-mobile3-docs        # NEW (Optional)
```

`PlatformConfig.rules_repo_path: Path | None = None` (Optional). When `None`, the resolver above falls back to the default `~/Developer/tdt/poems-mobile3-docs`.

`migrate-config` writes this key when generating a fresh config so newly migrated operators get canonical behaviour immediately.

### Test layering

```
tests/test_rules_loader_android.py     # existing — extend
tests/test_rules_loader_ios.py         # existing — extend
tests/fixtures/
  rules_repo_with_all_categories/     # NEW — full set, all 9 categories
  rules_repo_partial/                  # NEW — 3 categories only
  legacy_local_only/                   # NEW — no docs repo, only local mirror
  legacy_yaml_only/                    # NEW — no docs repo, no local, force YAML
```

Each fixture is a tiny on-disk tree. Each test exercises the same permutations: primary wins / primary partial / primary absent / category filtered.

### Sequencing and rollout

| Step | Effect | Rev | Owner |
|---|---|---|---|
| 1 | Add `rules_repo_path` to `PlatformConfig` (default `~/Developer/tdt/poems-mobile3-docs`). Loader accepts it. Logs source. | this change | scanner-team |
| 2 | Update `migrate-config` to write the new key. Refresh `config/code-daily-scan.yaml.example`. | this change | scanner-team |
| 3 | Update `docs/MIGRATION.md` to mention the new precedence (one paragraph). | this change | scanner-team |
| 4 | Mark `config/rule_patterns.yaml` with the new `__deprecated__` blurb noting the next-release removal. | this change | scanner-team |
| 5 | (next release) Remove `config/rule_patterns.yaml` after one release in production. | follow-up change | scanner-team |

No rule semantics change in this change, so rollout is on-the-button. If a freshly-installed CI runner complains that the default docs repo path doesn't exist, the fallback chain handles it.

### Why no Stage 2 in this change

`sync-rules` CLI + platform-repo CI guards are *operationally* valuable but introduce a new CLI surface and another moving part. Splitting them into a dedicated follow-up change keeps this one's blast radius tight to: (a) one config key, (b) two loader classes, (c) test fixtures.
