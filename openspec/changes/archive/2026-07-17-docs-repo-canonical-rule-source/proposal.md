# Proposal: Make `poems-mobile3-docs/50.RCA/*` the canonical rule source for `code-daily-scan`

## Why

Today the daily scan has **two divergent sources of truth** for the same body of detection rules:

1. **`code-daily-scan/config/rule_patterns.yaml`** — a legacy YAML embedded in the scanner itself, which already self-declares as `__deprecated__` and advertises that the platform `docs/*/categories/*.md` files are the intended source of truth. It is also incomplete: it contains zero `RCA-STATE-*`, `RCA-PAT-*`, `RCA-NAME-*`, `RCA-TEST-*` rules even though those rules exist in the docs repo and are referenced by every active RCA post-mortem.
2. **`poems-mobile3-docs/20.Developments/40.AI/50.RCA/{10.iOS,20.AOS}/rules/categories/*.md`** — the live rulebook the team's AI workflow (`p3-rca-assistant`, `p3-bug-fixing-report`, `p3-scan-technical-debt`) reads from. Every rule addition after a bug RCA lands here first.

The two are loosely kept in sync by hand. Whenever someone writes a new RCA rule in the docs repo, the scanner doesn't pick it up until someone separately edits one of the two loader paths (`poems-mobile3-android/docs/rules/categories/*.md` for Android, `docs/technical-debt-scan/categories/*.md` for iOS). The result is that:
- Stale rules stay live in the scanner for weeks.
- New post-mortem-derived rules are *invisible* to the daily scan.
- Reviews for rule changes happen on the wrong side: sometimes in scanner PR, sometimes in docs PR, occasionally both.

The intent to fix this is documented in `config/rule_patterns.yaml` itself (`"edit the platform's docs/*/categories/*.md as the source of truth. This file is incomplete ... and will be removed in a future release."`).

## What Changes

Make `poems-mobile3-docs/50.RCA/<platform>/rules/categories/*.md` the **canonical** rule source for both daily scan and MR scan. The scanner reads the docs repo's rule files directly each scan run; the legacy `rule_patterns.yaml` is retained as a final fallback for one release and then removed.

### Scope

- In scope: `code-daily-scan` (Python), `poems-mobile3-docs` (rule source — changes happen by PRs to that repo thereafter).
- Out of scope: `tdt-core`, `webhook-receiver`, `ai-review`, `tdt-sheets`, agent-core, mobile apps.

### New behaviour

1. **Primary rule path.** The platform plugins (`android`, `ios`) resolve a new config key `rules_repo_path` (default `~/Developer/tdt/poems-mobile3-docs`) and load categories from `<rules_repo>/20.Developments/40.AI/50.RCA/<plat>/rules/categories/*.md`. The `<plat>` mapping is `android → 20.AOS`, `ios → 10.iOS`.
2. **Read fresh on every scan.** No caching layer between docs repo and scanner; each scan invocation re-reads the markdown so a rule PR merged at 09:00 is live by 09:05. This is acceptable given current file sizes (~10 markdown files, &lt; 200 KB total) and the simple parser cost. If profiling later proves it expensive, add a content-hash cache keyed on the docs repo's HEAD SHA — but that's a follow-up, not part of this change.
3. **Fallback chain preserved.** If the docs repo path is missing (e.g. CI runner without a workspace checkout), the scanner falls back to the existing locations: `target_root/docs/rules/categories/` (Android), `target_root/docs/technical-debt-scan/categories/` (iOS), then finally `config/rule_patterns.yaml`. The fallback chain is **deterministic and ordered** — see Design for the exact order.
4. **Legacy YAML retained for one release.** `config/rule_patterns.yaml` stays in place as a final fallback and a `__deprecated__` annotation is updated to reflect the new precedence. The legacy YAML is removed in the *next* release that uses this change. A `# TODO(remove)` comment marker records the version number it is to be deleted in.
5. **The existing platform-repo `docs/...` folders become optional caches.** They are still updated whenever rules change in docs repo (today this happens manually), but the scanner no longer requires them.
6. **No new CLI surface.** This change is configuration-driven; no new subcommand is added. A future "Stage 2: sync CLI + CI guard" change will add `code-daily-scan sync-rules` plus a CI guard for the platform repos.

### Non-goals (for v1 of this change)

- We do not change rule semantics, pattern parsers, post-filters, FP reducers, or any scanner code that operates *after* `load_category()` returns `list[RulePattern]`. The platform-plugin interface (`load_category(category) -> list[RulePattern]`) is unchanged.
- We do not port rules from `code-daily-scan`'s legacy `rule_patterns.yaml` into the docs repo as part of this change. That is a separate "inventory + port" effort tracked under a follow-up change.
- We do not back-port the new contract terms to existing rules. Existing rules MAY be missing `version`, `deprecated` markers, or cross-platform references — that is **out of scope** for the loader change itself but is in scope for the contract spec the docs repo must enforce going forward.
- We do not yet wire a docs-repo webhook into the scanner (real-time rule push). Today the scanner re-reads on every invocation; webhook-based invalidation is a Stage 2 follow-up.

### In-scope (v1)

This change has three concentric scopes. They are listed outermost-first because the **outermost** is what the rest of the team will see; the **innermost** is the code edit.

1. **Cross-team evolution contract** — declare the rules under which the docs repo **evolves over time**. Anyone writing a rule PR (human or AI agent) must follow these.
2. **Schema and provenance contract** — pin the 9-category taxonomy, the rule ID format, the `category` enum (the AI scan output schema currently lists 7, the rules have 9 — this is a real gap), the cross-platform reference syntax, and the provenance trail (issue-reports + todos).
3. **Scanner data-source wiring** — make `code-daily-scan` actually consume the docs repo per scan.

Each scope has its own dedicated section below.

## Capabilities

### 1. Cross-team evolution contract (`poems-mobile3-docs` repo)

The docs repo is the **single source of truth for the whole team** and will **evolve over time**. To prevent rule-set drift between the human RCA workflow, the AI agent workflow, the manual fix workflow, and the daily scanner workflow, this change declares five binding rules that any future PR to `poems-mobile3-docs/50.RCA/**/rules/categories/*.md` MUST follow (E-1..E-4 are the per-rule envelope markers; E-5 is the meta-rule that says docs-repo rule PRs do NOT need an OpenSpec change of their own).

#### E-1. Versioned rules

Every rule heading (`## <id> — <title>`) MAY carry a version line immediately after the title. When present, the format SHALL be a fenced HTML comment so Markdown renderers ignore it:

```markdown
## C1 — ViewPager2 stores fragment instances and reuses stale fragments
<!-- rule:version=3 last_reviewed=2026-07-08 -->

- Priority: `P0`
```

A scanner, AI agent, or RCA tool that reads the rule MUST treat the absence of `rule:version` as "v0, unversioned" and log a warning once per scan. This is non-blocking in v1 but signals intent.

#### E-2. Deprecation markers

A rule MAY be marked deprecated without removal. The marker SHALL be a fenced HTML comment placed between the title and the priority line:

```markdown
## A1 — MVVM violated by business logic living in the view
<!-- rule:deprecated=2026-08-01 replacement=RCA-ARCH-001 reason="Superseded by Clean Architecture rule" -->

- Priority: `P2`
```

A scanner loading a deprecated rule SHOULD (NOT MUST) emit an `INFO` log line on load. The rule's regex patterns remain valid until retirement.

#### E-3. Cross-platform reference

When a rule has a semantic counterpart on the other platform, the doc MAY declare it with a fenced HTML comment:

```markdown
<!-- rule:cross_platform=10.iOS/RCA-STATE-001 -->

## RCA-STATE-001 — Shared LiveData-backed lists must not be sorted or mutated in-place
```

A future "Stage 2" follow-up change MAY consume these references to compute a cross-platform coverage matrix. For v1, the contract is **declarative only**; the scanner does not act on it.

#### E-4. Retirement

A retired rule (no longer relevant, kept for historical reference) SHALL be moved to a sibling `categories/.retired/` subfolder and removed from `categories/`. The scanner MUST NOT load rules from `.retired/`. (v1: not implemented; documented contract only.)

#### E-5. Envelope: docs-repo evolution is its own OpenSpec change

Adding, removing, or re-versioning a rule in `poems-mobile3-docs/50.RCA/**/rules/categories/*.md` is **not** a code change in any Python TDT sub-repo. The pre-edit OpenSpec gate does **not** apply to docs-repo rule edits. The contract above (E-1..E-4) is the lightweight governance that takes its place.

### 2. Schema and provenance contract

#### S-1. 9-category taxonomy is fixed

The set of category filenames under each `rules/categories/` folder SHALL be exactly these nine:

```
crash-runtime.md
memory-lifecycle.md
performance-resource-usage.md
architecture-maintainability.md
security-network-hardening.md
state-mutation.md          # (4 new since v1.0.0; v1.1.0 lock-in)
pattern-consistency.md
naming-readability.md
testing-coverage.md
```

A PR that adds, renames, or removes any of these files is an **evolution** event and MUST include a `changelog.md` entry under the `[Unreleased]` heading (see S-4).

#### S-2. Rule ID format

Rule IDs MUST match the regex:

```
^[A-Z]+(?:-[A-Z]+)?-\d{3}$   # e.g. RCA-STATE-001, RCA-ARCH-001
^[A-Z]\d+$                    # e.g. C1, P4, A7, S2, L6
```

A scanner that encounters an ID outside these patterns SHOULD log a warning and skip the rule.

#### S-3. Category enum alignment

The 9 taxonomy files project to 9 internal `category` strings (Android: `Crash`, `Memory Leak`, `Performance`, `Architecture`, `Security`, `State Mutation`, `Pattern Consistency`, `Naming & Readability`, `Testing Coverage`). The legacy `scan-output-schema.md` in `50.RCA/<plat>/technical-debt-scan/scan-output-schema.md` enumerates **only 7** (`Crash`, `Performance`, `Memory Leak`, `Lifecycle`, `Architecture`, `Maintainability`, `Security`).

This change requires an **evolution PR to the docs repo** that updates `scan-output-schema.md` for both platforms to enumerate all 9 categories (mapped to scanner-dispatch targets per the existing remap table in `design.md §"iOS category-map gap"`). The follow-up is **mandatory** before v1 ships, because today's `p3-scan-technical-debt` skill explicitly says "do not invent new categories."

#### S-4. Changelog is the evolution event log

The top-level `50.RCA/changelog.md` SHALL be the single place where evolution events (category add/remove, rule add/deprecate, contract change) are recorded. Each entry MUST include the version, the date, and a short rationale. The `[Unreleased]` section is the working buffer.

#### S-5. Provenance: every rule has an origin

Each rule SHOULD (NOT MUST) carry a `rule:source` comment referencing either:

- A Jira ticket: `rule:source=STABI-1234`
- A short commit SHA: `rule:source=f8ec84a`
- An `issue-reports/<ticket>.md` filename: `rule:source=issue-reports/SR-2647.md`

When a future "RCA Handoff Block" is processed by `p3-rca-assistant` (the producer agent), it SHOULD populate this field automatically. v1: not enforced; documented contract only.

#### S-6. Cross-platform rule parity is intentional, not accidental

A rule ID like `C4` MAY exist on both platforms with different titles. Name-collision SHALL NOT be interpreted as rule identity. The optional `<!-- rule:cross_platform=... -->` (E-3) is the only sanctioned way to declare cross-platform rule identity. Anything else is treated as coincidence.

### 3. `code-daily-scan` scan engine and platform plugins

- `ANDROID` and `IOS` plugins MAY accept a configurable `rules_repo_path` pointing at the canonical docs repo.
- The plugin MUST attempt to load rules from `<rules_repo>/20.Developments/40.AI/50.RCA/{20.AOS,10.iOS}/rules/categories/*.md` first; if any rule category returns at least one rule from there, the result MUST be used as the authoritative set and earlier sources MUST be ignored for that category.
- The plugin MUST fall back, in order: platform-repo `docs/rules/categories/` (Android) or `docs/technical-debt-scan/categories/` (iOS), legacy `config/rule_patterns.yaml`.
- The plugin MUST emit a structured log line (`logger.info`) reporting which rule source was actually used for each category, including a SHA-style fingerprint computed from the path that won, so that downstream audit and incident review can correlate findings with the rule file revision.
- A scan run MUST NOT silently fall back to a lower-priority source. Either the primary source succeeds (live rules) or the operator is told (log line + non-zero exit in `dry-run` mode) that rules were loaded from a fallback.
- The plugin MUST validate that the resolved docs-repo rules folder contains all 9 taxonomy files (S-1) before treating it as authoritative. If fewer than 9 files are present, the plugin SHALL fall back to the local mirror and emit a `docs_repo_incomplete=true` log line identifying which categories are missing.

### 4. `poems-mobile3-docs` repo role

- The two rule folders (`50.RCA/10.iOS/rules/categories/` and `50.RCA/20.AOS/rules/categories/`) become the canonical, code-reviewed home of the rules. Any rule PR MUST land there. The daily scan picks it up on the next run without a scanner PR.
- The two `technical-debt-scan/scan-output-schema.md` files MUST be updated to enumerate the full 9-category set (S-3). This is part of the v1 evolution PR, not a follow-up.

### 5. Drift detection (NEW — expanded scope)

The v1.1.0 freeze verified that local mirrors have **already drifted** from the canonical source. Without a drift-detection + sync mechanism, the docs repo becomes the scanner's source of truth but the local mirrors remain a parallel source that diverges in silence. To make the docs repo the **whole-team single source of truth**, drift detection is in scope for v1.

- The scanner SHALL compare, for each platform, the canonical docs-repo category files against the local mirror, and SHALL emit a single `INFO` log line per scan: `docs_repo_drift=<true|false> platform=<plat> differing_files=<N> identical_files=<M>`. When drift is detected, an additional `WARNING` log line MUST be emitted per differing file (D-1).
- The scanner SHALL expose a `code-daily-scan check-docs-drift` subcommand that exits non-zero on drift and prints a per-file report. The command MUST be safe to run in CI without requiring a full scan (D-4).
- Drift detection SHALL be enabled by default but MAY be disabled via `android.drift_detection_enabled: false` (D-3). Drift checks are non-blocking at runtime (D-2).

### 6. Mirror sync & retirement (NEW — expanded scope)

Drift detection surfaces the problem; this capability provides the **mechanism** to fix it.

- The scanner SHALL expose a `code-daily-scan sync-rules [--platform=...] [--force] [--force-clobber] [--restructure]` subcommand that pushes canonical → mirror (M-1).
- The command MUST refuse to clobber a mirror file whose content differs from canonical unless `--force` is supplied (M-1).
- The command MUST refuse to run when the target repo has uncommitted local changes in the mirror folder unless `--force-clobber` is supplied (M-3).
- The command MUST back up overwritten files to `.sync-backup/<timestamp>/` (M-1, M-3).
- The command MUST append an audit entry to `<target_repo>/docs/.sync-history.md` (M-5).
- A separate `--platform=ios --restructure` path swaps the legacy 4-file `technical-debt-scan/categories/` mirror for the 9-file `rules/categories/` layout (M-1 scenario 4).

End state (post this change + the v2/v3 follow-ups in tasks §10.7/§10.8):

| Consumer | Today (before this change) | After v3 |
|---|---|---|
| `code-daily-scan` | Reads `code-daily-scan/config/rule_patterns.yaml` (legacy, incomplete) | Reads `poems-mobile3-docs/50.RCA/<plat>/rules/categories/*.md` (canonical) |
| `p3-scan-technical-debt` AI skill | Reads platform-repo `docs/technical-debt-scan/categories/` | Reads canonical via AI-side docs-repo path |
| `p3-rca-assistant` AI agent | Does not exist | Appends rules to canonical only |
| Human developer (Cursor session) | `load-project-rulebook.mdc` reads platform-repo rulebook | Cursor rule references canonical |
| Issue reports & todos | Live in app repos | Live in `poems-mobile3-docs/50.RCA/<plat>/issue-reports/` + `todos/` |

**Zero local mirrors at end state. One canonical source.**

## Impact

| Surface | Impact |
|---|---|
| Scanners | Small — `load_category()` gains a new search root; everything downstream (`grep_scanner`, `post_filters`, `cli`, `Phase3`) is untouched |
| Config file (`~/.tdt/code-daily-scan.yaml`) | Adds one optional key per platform: `rules_repo_path` (default: `~/Developer/tdt/poems-mobile3-docs`) |
| Migration tool (`code-daily-scan migrate-config`) | Updates its default `rules_repo_path` so newly migrated configs include the new key |
| Tests | New fixtures: a) docs-repo present but all 9 categories present → docs-repo wins; b) docs-repo present but some categories missing → fallback kicks in for missing ones; c) docs-repo absent → legacy YAML used; d) explicit empty `rules_repo_path` → primary skipped |
| Docs repo (`poems-mobile3-docs`) | **Required evolution PR**: update both `technical-debt-scan/scan-output-schema.md` files to enumerate all 9 categories (S-3). **Optional but recommended**: add `<!-- rule:version -->` and `<!-- rule:cross_platform -->` markers to existing rules in batches (E-1, E-3). |
| AI workflow (`p3-rca-assistant`, `p3-bug-fixing-report`) | Contract change: when these agents append a new rule, they MUST follow the E-1..E-5 envelope. No code change required — the contract is declarative. |
| `p3-scan-technical-debt` skill | Contract change: the skill's "do not invent new categories" rule is enforced by the scanner+schema contract; the skill's docs MAY be updated to reference the canonical category set |
| Drift detection (NEW) | Adds `code_daily_scan.drift` module + `docs_repo_drift=` log line on every scan. Adds `check-docs-drift` CLI. Default-on; opt-out via `drift_detection_enabled: false`. **Non-blocking at runtime.** |
| Mirror sync (NEW) | Adds `sync-rules` CLI with `--force`, `--force-clobber`, `--restructure` flags. Backups written to `.sync-backup/<timestamp>/`. Audit trail appended to `docs/.sync-history.md`. Default policy: refuse clobber without `--force`. |
| Local mirror retirement (NEW, 3-release phased) | v1: detection only. v2 (follow-up §10.7): sync CLI ships, CI guard runs `check-docs-drift`. v3 (follow-up §10.8): app-repo mirrors deleted, `load-project-rulebook.mdc` points at canonical docs-repo path. End state: zero mirrors. |
| Roadmap | A follow-up "Stage 2" change adds `sync-rules` CLI + CI guard in `poems-mobile3-android` and `poems-mobile3-ios` so the local mirrors in those repos stay current automatically |
| Rollback | One-line revert: switch `rules_repo_path` to an empty string or remove the key. The plugin must default to "docs repo at `~/Developer/tdt/poems-mobile3-docs`" only when the key is absent; an explicit empty value means "use the legacy path only" |

## Open questions (resolved during propose)

1. ~~Where should the new env var live?~~ → config-file key per-platform (`rules_repo_path`) with a per-platform env-var override (`CODE_DAILY_SCAN_ANDROID_RULES_REPO` / `CODE_DAILY_SCAN_IOS_RULES_REPO`). Mirrors the existing `*_REPO_PATH_ENV` pattern.
2. ~~Should we cache the loaded rules?~~ → No for this change. Each run re-reads. The full AOS+iOS markdown is ~78 KB; parse cost is sub-100 ms per scan on a developer laptop. Revisit when a Stage 2 change touches CI performance.
3. ~~Should we version-pin to a specific docs-repo commit?~~ → No for v1. If operators want to pin, they can `git checkout <sha>` in the docs repo themselves. A future change can add an optional `rules_repo_ref` key.
4. ~~Does the docs-repo path need pre-existing iOS category-map entries?~~ → **No.** The four missing keys (`naming-readability`, `pattern-consistency`, `state-mutation`, `testing-coverage`) are added in this change under tasks §4.4. Without that addition, the iOS loader would silently drop ~40 % of the docs-repo rules.
5. ~~What governance applies to docs-repo rule PRs?~~ → The pre-edit OpenSpec gate does **not** apply (docs is not a Python TDT sub-repo). The E-1..E-4 envelope in this proposal is the lightweight governance. Every rule PR is **not** required to ship its own OpenSpec change.
6. ~~What happens when the docs repo adds a 10th category file?~~ → The scanner's "9-category fixed" check (S-1) will reject the docs repo as incomplete (only 9/10). The team MUST bump the constant and the contract together. That is an explicit evolution event, not a silent change.

## Risks identified during research

| Risk | Mitigation |
|---|---|
| `PlatformConfig` is `@dataclass(frozen=True, slots=True)` and **rebuilt in 9 places** when any field changes (5 env overrides + 4 CLI overrides + 1 final `ScanConfig`). Adding `rules_repo_path` may miss a rebuild site. | Tasks §13.1 enumerates all 9 sites with line numbers. `mypy --strict` will catch the type error if one is missed. |
| `IOSRulesLoader.IOS_CATEGORY_MAP` lacks prefixes for `state-mutation`, `pattern-consistency`, `naming-readability`, `testing-coverage` — silent rule drop. | Task §4.4 closes the gap with four new entries and a scanner-dispatch remap table. |
| `config/rule_patterns.yaml`'s `__deprecated__` annotation currently uses a string that **says** "edit the platform's docs/*/categories/*.md as the source of truth" but the loader was never updated to do that. Stale guidance confuses contributors. | Task §5.1 updates the annotation text to point at `rules_repo_path`'s docs folder rather than the platform repos. |
| A scan invocation re-parses 18 markdown files (9 AOS + 9 iOS) on every call. For daily scans this is negligible; for CI it could be measurable. | Deferred to a follow-up "Stage 2" change that adds a SHA-keyed cache. Tracked in tasks §10.3. |
| `migrate-config` writes only an `android:` block; the iOS block does not exist in legacy imports. Generated configs for fresh operators will **lack** both `ios.rules_repo_path` and `ios.repo_path` defaults. | Task §13.2 specifies that the migrate logic MUST additionally create an `ios:` block with `repo_path: ~/Developer/tdt/poems-mobile3-ios` and `rules_repo_path: ~/Developer/tdt/poems-mobile3-docs` defaults. Idempotency check ensures no clobbering. |
| **The docs repo's `scan-output-schema.md` enumerates only 7 categories** (`Crash`, `Performance`, `Memory Leak`, `Lifecycle`, `Architecture`, `Maintainability`, `Security`), but the rule taxonomy has 9. AI agents told to "not invent new categories" will silently drop findings for `State Mutation`, `Pattern Consistency`, `Naming & Readability`, `Testing Coverage`. | Task §11.1 adds a docs-repo evolution PR that updates both `scan-output-schema.md` files to enumerate all 9. Mandatory before v1 ships. |
| **Cross-platform rule IDs are intentionally non-identical.** 32 iOS rules vs 45 AOS rules with only 11 name-shared. A scanner that treats `C4` on iOS as identical to `C4` on AOS will produce wrong findings. | Capability S-6 (cross-platform reference marker) makes the contract explicit. The scanner does not act on it in v1, but the contract is declared so future Stage-2 work can build a coverage matrix. |
| **The docs repo will evolve.** Every rule PR is a "mutation" event. Without a governance contract, the 9-category set, the rule ID format, and the schema enum will drift. | Capabilities E-1..E-4 + S-1..S-8 declare the envelope. The `changelog.md` `[Unreleased]` section is the visible record. |
| **The pre-edit OpenSpec gate does not apply to docs-repo edits** (docs is not a Python TDT sub-repo). Docs-repo rule PRs could ship ungoverned. | Capability E-5 explicitly removes the gate for docs-repo edits and substitutes the E-1..E-4 envelope as the lightweight governance. Every docs-repo PR is **not** required to ship its own OpenSpec change — that would over-process AI-agent outputs (the `p3-rca-assistant` agent produces many small rule appends). |
| **The 9-category "fixed set" is enforced by an assertion**, not a hard schema. A malicious or accidental PR could add a 10th file, and the scanner would log a `docs_repo_incomplete=true` line for the missing slot. | The scanner does **not** crash; it falls back to the local mirror for the missing slot. This is intentional — graceful degradation over hard failure. A future change MAY add a stricter mode. |
| **`load_category()` and `load()` currently MERGE results across all available roots** (e.g. Android `load_category` walks both `docs/rules/categories` AND `docs/technical-debt-scan/categories` and concatenates). After the docs-repo addition, MERGE behaviour would silently mix legacy YAML rules into docs-repo results. | Task §13.7 specifies that the methods MUST switch to priority-based per-category fallback: walk the first root, check the 9/10 count (S-1), and only fall back to the next root for the *specific category* that failed — not for all categories. |
| **`p3-rca-assistant` agent does not exist in the docs repo** (verified: no file found under `20.Developments/40.AI/30.AOS/agents/` or `20.IOS/agents/` matching `*rca*assistant*`). The RCA Handoff Block producer emits structured input for it, but the consumer is missing. | Capability S-7 documents this gap explicitly. Task §11.7 introduces the agent. Until that PR lands, the E-1..E-4 + S-5 envelope has **no automated producer** — only manual contributors. The scanner still works (it parses whatever it finds). |
| **iOS loader currently has a single search root** (`docs/technical-debt-scan/categories`), unlike Android's two. Blind mirroring of Android's resolution order would produce the wrong path scheme for iOS. | Task §13.4 enumerates the iOS-specific three-root priority order. Task §13.8 calls out the asymmetry between iOS local mirror and docs-repo paths. |
| **GrepScanner and OrchestratorMR pass only `repo_path` to the loader constructor** (`grep_scanner.py:707` and `orchestrator_mr.py:81` both call `loader_cls(repo_path)`). After adding `rules_repo: Path | None = None` to the constructor, the callers MUST be updated to pass the second argument, or the new field silently defaults to `None`. | Task §13.3 lists both call sites and requires an explicit update. Graceful degradation (the loader returns None and skips the docs-repo) masks the missing wiring unless a test asserts `rules_repo == configured_path`. |
| **`FILENAME_CATEGORY_MAP` is duplicated** (defined both at module level and as a class attribute on `AndroidRulesLoader`). After adding prefixes, divergence between the two definitions would produce subtle category-mapping bugs. | Task §13.6 keeps both definitions in sync and adds a runtime assertion in `AndroidRulesLoader.__init__` to detect drift. |
| **Local mirrors already differ from canonical** as of v1.1.0. Confirmed: 3 of 9 Android category files differ (`architecture-maintainability.md`, `crash-runtime.md`, `testing-coverage.md`); iOS has a 4-file legacy mirror with non-conforming names. | Drift-detection capability (D-1..D-5) surfaces the mismatch at every scan. `check-docs-drift` CLI is the day-zero check. `sync-rules` with `--force-clobber` brings mirrors in line. The 3-release retirement timeline (M-4) ends with zero mirrors. |
| **Drift detection could become a CI distraction** if it has too few knobs. A PR that legitimately edits a local-mirror rule (e.g., during a feature branch hot-fix) would fail CI on `check-docs-drift`. | Drift detection runs ONLY when `--platform` is set (D-4). The follow-up `code-daily-scan-mirror-retirement-v2` change adds a CI-level allowlist for known hot-fix branches and an opt-out comment marker. For v1, drift detection is logged but never blocks CI. |
| **Mirror retirement breaks offline development** if a developer doesn't have the docs repo checked out at the path configured in `rules_repo_path`. Today the fallback chain reads the mirror; after retirement, an offline dev scan fails. | The fallback chain (S-1 contract: primary → local mirror → legacy YAML) remains in v3. If the primary is unreachable, the local-mirror fallback (which has been removed) is skipped, then the legacy YAML is consulted. For offline-first operators who never have the docs repo, the spec declares `rules_repo_path: ""` (explicit empty) as the supported "legacy only" mode — same as today. |

## Verification plan (preview — full plan in tasks.md)

- Unit tests against a synthetic docs-repo fixture containing 1 each of `crash-runtime.md`, `memory-lifecycle.md`, `security-network-hardening.md`. Assert:
  - Primary load returns the fixture's rules
  - When the primary path is removed, the test fixture's local `target_root/docs/.../categories/crash-runtime.md` wins
  - When both primary and local are absent, legacy YAML wins
- Integration test: run `code-daily-scan dry-run --platform android` against a worktree that lacks any docs-repo rule files; expect a log line `"loaded_rules_source=legacy_yaml"` and exit 0.
- Manual: start a scan pointed at `HEAD` of `poems-mobile3-docs`. Edit a rule pattern in a local docs-repo working copy; rerun; expect the new pattern in the output.
