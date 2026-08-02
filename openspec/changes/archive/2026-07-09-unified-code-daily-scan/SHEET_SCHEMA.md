# SHEET_SCHEMA.md

## Overview

Each platform (Android, iOS) writes findings to its own spreadsheet. Spreadsheet IDs are configured in `~/.tdt/code-daily-scan.yaml`.

**Design Philosophy:** One sheet per scan (branch tab), feature-based grouping within sheet, rule-based intelligent mapping.

---

## Unified Scan Sheet Schema

### Tab Naming Convention

| Scan Type | Tab Name Format | Example |
|-----------|----------------|---------|
| Branch scan (no feature) | `BRANCH-{branch-slug}` | `BRANCH-modules-ewallet-develop_newdesignsystem` |
| Branch scan (with `--feature`) | `BRANCH-{branch-slug}-{feature-slug}` | `BRANCH-modules-ewallet-develop_newdesignsystem-Ewallet` |
| MR scan | `MR-{project-slug}-{iid}` | `MR-pspl-poems-mobile3-android-23318` |
| Full scan | `FULL-{YYYY-MM-DD}` | `FULL-2026-06-13` |

The branch-scan convention is **deterministic**: a given
`(source_branch, --feature)` pair always produces the same tab name,
so the first run creates the tab and every subsequent run reuses it.
The exact slug rules are specified in
[`specs/code-daily-scan-core/spec.md`](../specs/code-daily-scan-core/spec.md)
under the *Branch-Scan Tab Name Is Deterministic And Reusable*
requirement.

### Feature-Based Column Layout

| Col | Field | Type | Description |
|-----|-------|------|-------------|
| A | Rule ID | string | e.g., `C3`, `L4`, `M1` |
| B | CWE | string | e.g., `CWE-664`, `CWE-798` |
| C | Related Rules | string | Comma-separated rule IDs |
| D | Title | string | Finding title |
| E | Priority | enum | `P0`, `P1`, `P2`, `P3` |
| F | Category | string | e.g., `Crash`, `Memory Leak` |
| G | Feature | string | **Intelligent mapped feature** (Auth, Trade, etc.) |
| H | File Path | string | Workspace-relative path |
| I | Symbol | string | Class/file name |
| J | Issue | string | Evidence snippet |
| K | Recommended Solution | string | Suggested fix |
| L | Solution Review by Team Lead | string | Manual review |
| M | Impact / Scope Testing | string | Testing notes |
| N | Man Day | number | Estimated effort |
| O | Status | enum | `Open`, `In Progress`, `Done` |
| P | Jira Ticket | string | Linked ticket |
| Q | Target Fix in Version | string | Target version |
| R | MR Context | string | Diff hunk (MR scans only) |
| S | Is False Positive | boolean | FP flag |
| T | FP Reason | string | Why marked as FP |

### Section Layout (Within Sheet)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    BRANCH-modules-ewallet-develop_newdesignsystem    ║
╠═══════════════════════════════════════════════════════════════════════╣
║ === Auth ===                                                         ║
║ P0 | C1 | CWE-789 | File | Issue...                                ║
║ P1 | L2 |         | File | Issue...                                ║
║ P2 | A1 |         | File | Issue...                                ║
║                                                                       ║
║ === Home ===                                                         ║
║ P0 | C3 | CWE-123 | File | Issue...                                ║
║ P1 | P1 |         | File | Issue...                                 ║
║                                                                       ║
║ === WatchList ===                                                    ║
║ ...                                                                  ║
║                                                                       ║
║ === Trade ===                                                        ║
║ ...                                                                  ║
║                                                                       ║
║ === Market ===                                                        ║
║ ...                                                                  ║
║                                                                       ║
║ === Community ===                                                     ║
║ ...                                                                  ║
║                                                                       ║
║ === Me/Settings ===                                                  ║
║ ...                                                                  ║
║                                                                       ║
║ === Deposit/Withdraw ===                                             ║
║ ...                                                                  ║
║                                                                       ║
║ === Others ===                                                        ║
║ ...                                                                  ║
║                                                                       ║
║ === Form ===                                                          ║
║ ...                                                                  ║
╠═══════════════════════════════════════════════════════════════════════╣
║ SUMMARY BY FEATURE                                                    ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Feature       | Total | P0 | P1 | P2 | P3 | % of Total             ║
║ --------------------------------------------------------------------  ║
║ Auth          |    12 |  1 |  5 |  4 |  2 | 11.5%                  ║
║ Home          |     8 |  0 |  3 |  3 |  2 |  7.7%                   ║
║ WatchList     |     5 |  0 |  2 |  2 |  1 |  4.8%                   ║
║ Market        |    15 |  2 |  6 |  5 |  2 | 14.4%                  ║
║ Trade         |    25 |  3 | 10 |  8 |  4 | 24.0%                  ║
║ Community     |     6 |  0 |  2 |  3 |  1 |  5.8%                   ║
║ Me/Settings   |    10 |  1 |  4 |  3 |  2 |  9.6%                   ║
║ Deposit/Withdraw|     8 |  0 |  3 |  3 |  2 |  7.7%                   ║
║ Form          |     3 |  0 |  1 |  1 |  1 |  2.9%                   ║
║ Others        |    15 |  1 |  6 |  5 |  3 | 14.4%                  ║
║ --------------------------------------------------------------------  ║
║ TOTAL         |   104 |  8 | 41 | 36 | 19 |100.0%                  ║
╠═══════════════════════════════════════════════════════════════════════╣
║ SUMMARY BY CATEGORY                                                   ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Category      | Total | P0 | P1 | P2 | P3 | % of Total             ║
║ --------------------------------------------------------------------  ║
║ Crash         |    30 |  5 | 15 |  8 |  2 | 28.8%                  ║
║ Memory Leak   |    25 |  2 | 12 |  8 |  3 | 24.0%                  ║
║ Lifecycle     |    20 |  1 |  8 |  7 |  4 | 19.2%                  ║
║ Performance   |    15 |  0 |  4 |  7 |  4 | 14.4%                  ║
║ Architecture  |    10 |  0 |  2 |  5 |  3 |  9.6%                   ║
║ Security      |     4 |  0 |  0 |  1 |  3 |  3.8%                   ║
║ --------------------------------------------------------------------  ║
║ TOTAL         |   104 |  8 | 41 | 36 | 19 |100.0%                  ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## Intelligent Feature Mapping

### FeatureResolver Architecture

```python
# Rule-based pattern matching with priority order
FEATURE_RULES: list[tuple[str, list[str]]] = [
    # (Feature Name, [list of path patterns - any match returns that feature])
    # Order matters: more specific patterns first

    ("Trade", [
        "tradeticket", "tradesubmit", "tradesell", "tradebuy",
        "tradeorder", "tradecfd", "tradefuture", "tradeoption",
        "traderegular", "tradestocks", "tradebonds",
    ]),
    ("Deposit/Withdraw", [
        "tradedeposit", "tradewithdraw", "depositfunds",
        "fundinghistory", "withdrawfunds", "ewallet",
        "digitalassetewallet", "coinhistory",
    ]),
    ("Auth", [
        "auth", "login", "logout", "register", "signup",
        "biometric", "mfa", "otp", "password", "forgotpassword",
    ]),
    ("Home", [
        "home", "homescreen", "dashboard", "tabbar",
        "mainactivity", "mainfragment",
    ]),
    ("WatchList", [
        "watchlist", "watch_list", "watchlistview", "watchlistscreener",
    ]),
    ("Form", [
        "form", "cdp", "chatgpt", "egiro", "smartpark",
    ]),
    ("Market", [
        "market", "counter", "quotes", "stock",
        "marketview", "marketdetail", "stockdetail",
        "counterdetail", "counterhistory", "globalsearch",
    ]),
    ("Community", [
        "community", "discover", "social", "announcement",
        "corporateaction", "fxinvest", "stockoption",
        "promo", "promotions",
    ]),
    ("Me/Settings", [
        "profile", "setting", "notification", "help",
        "announcement", "inbox", "milestone", "alert",
        "promotions", "cdpshare", "carcka", "rsp",
    ]),
]

# Fallback: "Others" for any unmapped paths
```

### Platform-Specific Path Normalization

| Platform | Base Path | Pattern Example |
|----------|-----------|-----------------|
| Android | `app/src/main/java/com/tdt/pmobile3/` | `ui/screens/auth/` |
| iOS | `Pmobile3/Modules/` | `Auth/`, `Trade/` |

### Resolution Algorithm

```python
def resolve_feature(file_path: str) -> str:
    """
    Resolve a file path to its feature category.

    Algorithm:
    1. Normalize path (lowercase, replace separators)
    2. Match against FEATURE_RULES in priority order
    3. Return first matching feature, or "Others"
    """
    normalized = _normalize_path(file_path)

    for feature, patterns in FEATURE_RULES:
        for pattern in patterns:
            if pattern in normalized:
                return feature

    return "Others"

def _normalize_path(path: str) -> str:
    """Normalize path for matching: lowercase, strip base path."""
    # Remove common base paths
    for base in ["app/src/main/java/com/tdt/pmobile3/", "Pmobile3/Modules/"]:
        if base in path:
            path = path.split(base)[-1]
    return path.lower().replace("/", "").replace("\\", "")
```

### Feature → Tab Section Mapping

Findings within a sheet are grouped by feature using **section headers** (spacer rows with `=== {Feature} ===`).

---

## MR Tab Schema

For MR-scoped scans, findings are written to a dedicated tab:

**Tab name:** `MR-{project-slug}-{iid}` (e.g., `MR-poems-team-poems-mobile3-ios-42`)

Same column format as above, with the following additions:

1. **MR Context column (R):** Contains the git diff hunk that triggered the finding
2. **Summary row at top:**
   ```
   MR Scan Summary | Total: N | P0: N | P1: N | P2: N | P3: N | ...
   ```
   The row remains 20 columns wide to match the standard schema.

---

## Config Reference

Priority comes from each rule's `- Priority:` field, not from the rule-ID prefix.
The table below is indicative; the rule markdown is authoritative.

| Priority | Description | Android Rule IDs | iOS Rule IDs (indicative) |
|----------|-------------|-----------------|--------------|
| P0 | Crash risk | `C*`, `RCA-ARCH-*` | `M1`–`M4`, crash/concurrency `C*` (P0 ones) |
| P1 | Performance / Lifecycle / Memory | `L*`, `P*`, `S*`, `PC*`, `SM*` | `M5`–`M8`, `L1`, `L2`, `L4`, SwiftUI `S*` (P1 ones) |
| P2 | Architecture | `A*` | `L3`, `A1`–`A5` |
| P3 | Hygiene / Dead code | `N*`, `T*` | `A6` |

## Rule ID Convention

### Android

- `C*` — Crash risk
- `L*` — Memory & Lifecycle
- `P*` — Performance
- `A*` — Architecture
- `S*` — Security

### iOS

iOS uses **feature-based tab routing** (same as Android) for consistency:
`finding.feature` → `FEATURE_TAB_MAP` → tab name.

Feature field is populated via `feature_resolver.resolve_feature()` from file paths.

| Feature | Tab |
|---------|-----|
| Auth | Auth |
| Home | Home |
| WatchList | WatchList |
| Market | Market |
| Trade | Trade |
| Community | Community |
| Me/Settings | Me/Settings |
| Deposit/Withdraw | Deposit/Withdraw |
| Form | Form |
| Common | Common |
| Others | Others |

Rule-ID prefixes are documented for reference but **not used** for tab routing.

## MR Tab Schema

For MR-scoped scans, findings are written to a dedicated tab:

**Tab name:** `MR-{project-slug}-{iid}` (e.g., `MR-poems-team-poems-mobile3-ios-42`)

Same column format as platform tabs, with the following additions:

1. **MR Context column (P):** Contains the git diff hunk that triggered the finding
2. **Summary row at top:**
   ```
   MR Scan Summary | Total: N | P0: N | P1: N | P2: N | P3: N | ...
   ```
   The row remains 16 columns wide to match the standard schema.

## Config Reference

```yaml
# ~/.tdt/code-daily-scan.yaml
android:
  spreadsheet_id: "1DSaaBD3-..."
  repo_path: "~/Developer/tdt/poems-mobile3-android"

ios:
  spreadsheet_id: "1DSaaBD3-..."
  repo_path: "~/Developer/tdt/poems-mobile3-ios"

rules_tracking:
  spreadsheet_id: "1XYZ789-..."
  tabs:
    - RULES_INDEX
    - ANDROID_RULES
    - IOS_RULES
    - COVERAGE_MATRIX
    - CHANGELOG
    - FALSE_POSITIVES
```

---

## Rules Tracking Sheet

A dedicated spreadsheet for tracking all scanner rules across platforms.

### Purpose

1. **Rule Inventory**: Complete view of all available rules
2. **Coverage Tracking**: Identify gaps vs industry standards
3. **Rule Lifecycle**: Track rule additions, modifications, deprecations
4. **Quality Metrics**: Rule accuracy, false positive rates
5. **Maintenance**: Rule ownership and review schedules

### Tabs

| Tab | Purpose |
|-----|---------|
| `RULES_INDEX` | Master list of all rules (379 rules total) |
| `ANDROID_RULES` | Android-specific rule details (264 rules) |
| `IOS_RULES` | iOS-specific rule details (115 rules) |
| `COVERAGE_MATRIX` | Rules vs industry standards |
| `CHANGELOG` | Rule additions/modifications |
| `FALSE_POSITIVES` | False positive tracking |
| `FP-Tracking` | False positive records with content hash |
| `Metrics` | Scan KPI tracking (Findings/KLOC, FP Rate) |

### Key Metrics

| Metric | Android | iOS | Total |
|--------|---------|-----|-------|
| Unique Rules | 45 | 37 | 82 |
| Detection Patterns | ~264 | ~115 | ~379 |
| Rules with CWE | 100% | 100% | 100% |
| P0 Rules | ~16 | ~12 | ~28 |

### Industry Alignment

| Standard | Android | iOS | CWE Coverage |
|----------|---------|-----|--------------|
| Platform Guidelines | 100% | 95% | — |
| Security (OWASP) | 100% | N/A | 100% |
| Static Analysis | 90% | 80% | 100% |

### Enhancement Roadmap

See: `specs/enhancement-cwe-baseline-integration/SPEC.md`

| Phase | Feature | Priority | Status |
|-------|---------|---------|--------|
| 8.1 | CWE Mapping | High | ✅ Complete |
| 8.2 | False Positive Tracking | High | ✅ Complete |
| 8.3 | Metrics Framework | Medium | ✅ Complete |
| 8.4 | Tooling Integration | Medium | ⏸ Optional |

### Related Documentation

- `docs/RULES_TRACKING_SCHEMA.md` - Full schema definition
- `docs/ANDROID_RULES_INVENTORY.md` - Android rules details
- `docs/IOS_RULES_INVENTORY.md` - iOS rules details
- `docs/industry-standards-comparison.md` - Industry comparison
- `docs/RCA_FIX_EVALUATION.md` - Fix quality evaluation
- `docs/SOLUTION_ASSESSMENT.md` - Solution assessment
- `specs/enhancement-cwe-baseline-integration/SPEC.md` - Enhancement spec
