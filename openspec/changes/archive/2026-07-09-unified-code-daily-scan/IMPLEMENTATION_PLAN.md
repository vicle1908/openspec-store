# Phase 8 Implementation Plan

**Date**: 2026-06-11
**Change**: `unified-code-daily-scan`
**Priority**: High

---

## Executive Summary

Based on research and SPEC.md analysis, the Phase 8 enhancements will add:

1. **CWE Mapping** - Security taxonomy alignment
2. **False Positive Tracking** - Noise reduction
3. **Metrics Framework** - KPI tracking
4. **Tooling Integration** - Extended capabilities

---

## Phase 8.1: CWE Mapping

### Requirements Analysis

| Requirement | Current State | Action |
|------------|--------------|--------|
| `cwe_id` field in `RulePattern` | ❌ Missing | Add to model |
| Parse `- CWE:` from markdown | ❌ Not implemented | Update rules loader |
| Propagate CWE to `Finding` | ❌ Not implemented | Update models + mapper |
| Sheet output with CWE column | ✅ In SHEET_SCHEMA | Verify implementation |

### Implementation Tasks

#### Task 1: Update `models.py`

```python
@dataclass(slots=True, frozen=True)
class RulePattern:
    # ... existing fields ...
    cwe_id: str | None = None  # NEW

@dataclass(slots=True, frozen=True)
class Finding:
    # ... existing fields ...
    cwe_id: str | None = None  # NEW
```

#### Task 2: Update iOS Rules Loader

Add CWE parsing from markdown:
```markdown
## M1 — Combine sink without weak capture

- Priority: `P1`
- CWE: `CWE-400`  <!-- NEW -->
- Category: `Memory Leak`
```

#### Task 3: Update Android Rules Loader

Same pattern as iOS.

#### Task 4: Add CWE to iOS Rules (45 rules)

| Category | Rules | CWE |
|----------|-------|-----|
| Memory Leak (M1-M8) | 8 | CWE-400 |
| Lifecycle (L1-L6) | 6 | CWE-401, CWE-400 |
| Crash (C1-C6) | 6 | CWE-664, CWE-129 |
| SwiftUI (S1-S4) | 4 | Various |
| Concurrency (C7-C10) | 4 | CWE-662 |
| Architecture (A1-A6) | 6 | CWE-1008 |

#### Task 5: Add CWE to Android Rules

| Category | Rules | CWE |
|----------|-------|-----|
| Crash (C*) | 12 | CWE-664, CWE-129 |
| Memory (L*) | 8 | CWE-400, CWE-401 |
| Security (S*) | 5 | CWE-798, CWE-319, CWE-295 |
| Architecture (A*) | 10 | CWE-710 |
| Performance (P*) | 5 | CWE-400 |

#### Task 6: Update Sheet Mapper

Ensure CWE propagates to sheet output.

### Effort Estimate

| Task | Estimate |
|------|----------|
| Model updates | 1 hour |
| Rules loader updates | 2 hours |
| CWE mapping (iOS) | 2 hours |
| CWE mapping (Android) | 2 hours |
| Sheet mapper | 1 hour |
| **Total** | **8 hours (1 day)** |

---

## Phase 8.2: False Positive Tracking

### Requirements Analysis

| Requirement | Current State | Action |
|------------|--------------|--------|
| `is_false_positive` field | ❌ Missing | Add to model |
| `FP-Tracking` sheet tab | ❌ Not created | Design schema |
| Auto-detection heuristics | ❌ Not implemented | Build patterns |
| `mark-false-positive` CLI | ❌ Not implemented | Add command |

### Implementation Tasks

#### Task 1: Update `Finding` Model

```python
@dataclass(slots=True, frozen=True)
class Finding:
    # ... existing fields ...
    is_false_positive: bool = False
    false_positive_reason: str | None = None
    verified_by: str | None = None
    verified_at: datetime | None = None
```

#### Task 2: Create `FP-Tracking` Sheet

| Column | Type | Description |
|--------|------|-------------|
| A | Text | Rule ID |
| B | Text | File Path |
| C | Text | Content Hash (MD5) |
| D | Boolean | Is False Positive |
| E | Text | Reason |
| F | Text | Verified By |
| G | Date | Verified At |
| H | Text | Comment |

#### Task 3: Implement Auto-Detection

```python
FALSE_POSITIVE_PATTERNS = [
    r"/test[s]?/.*\.(kt|swift)$",
    r"/androidTest/.*\.kt$",
    r"/iosTests/.*\.swift$",
    r"/generated/.*\.(kt|swift)$",
    r"/build/.*\.(kt|swift)$",
    r"//.*#noinspection.*",
    r"//.*#pragma.*",
]
```

#### Task 4: Add CLI Command

```bash
code-daily-scan mark-false-positive \
  --rule-id M1 \
  --file-path "src/ViewController.swift" \
  --reason "Test file - excluded"
```

### Effort Estimate

| Task | Estimate |
|------|----------|
| Model update | 1 hour |
| FP-Tracking sheet | 2 hours |
| Auto-detection | 3 hours |
| CLI command | 2 hours |
| **Total** | **8 hours (1 day)** |

---

## Phase 8.3: Metrics Framework

### Requirements Analysis

| Requirement | Current State | Action |
|------------|--------------|--------|
| `Metrics` sheet tab | ❌ Not created | Design + implement |
| KPI calculations | ❌ Not implemented | Build formulas |
| `report-metrics` CLI | ❌ Not implemented | Add command |

### KPI Definitions

| KPI | Formula | Target |
|-----|---------|--------|
| Findings/KLOC | `findings / kloc` | < 5 |
| FP Rate | `fp_count / total` | < 5% |
| P0 Remediation | `avg(days_to_fix(p0))` | < 7 days |
| PR Blocking | `blocked_prs / total` | < 10% |

### Implementation Tasks

#### Task 1: Create `Metrics` Sheet

| Column | Type | Description |
|--------|------|-------------|
| A | Date | Scan Date |
| B | Number | Total Findings |
| C-N | Number | P0-P3 counts |
| O | Number | FP Count |
| P | Number | KLOC |
| Q | Number | Findings/KLOC |
| R | Number | FP Rate % |

#### Task 2: Implement KPI Calculator

```python
@dataclass
class ScanMetrics:
    scan_date: date
    total_findings: int
    p0_count: int
    p1_count: int
    p2_count: int
    p3_count: int
    fp_count: int
    kloc: float
    findings_per_kloc: float
    fp_rate: float
```

#### Task 3: Add CLI Command

```bash
code-daily-scan report-metrics --platform ios --days 30
```

### Effort Estimate

| Task | Estimate |
|------|----------|
| Metrics sheet | 2 hours |
| KPI calculator | 4 hours |
| CLI command | 2 hours |
| **Total** | **8 hours (1 day)** |

---

## Phase 8.4: Tooling Integration (Optional)

### Requirements Analysis

| Requirement | Current State | Action |
|------------|--------------|--------|
| `--full-scan` flag | ❌ Not implemented | Add to CLI |
| Semgrep export | ❌ Not implemented | Build exporter |
| MobSF integration | ❌ Not implemented | Build scanner |
| Dependency scanner | ❌ Not implemented | Build scanner |

### Implementation Tasks

#### Task 1: Add `--full-scan` Flag

```python
@app.command()
def scan(
    platform: Platform,
    full_scan: bool = False,  # NEW
):
```

#### Task 2: Semgrep Rule Exporter

```yaml
# Export format
rules:
  - id: tdt-ios-M1
    pattern: '\.sink\s*\{(?![^}]*\[weak)'
    message: Combine sink without weak capture
    severity: ERROR
    languages: [swift]
    metadata:
      cwe: "CWE-400"
```

#### Task 3: MobSF Integration

```python
class MobSFScanner:
    def scan_binary(self, apk_path: Path) -> list[Finding]:
        # Use MobSF REST API
        # Map findings to Finding format
```

#### Task 4: Dependency Scanner

```python
class DependencyScanner:
    def check_vulnerabilities(self, sbom_path: Path) -> list[Finding]:
        # Parse SBOM
        # Check against CVE database
        # Return Findings
```

### Effort Estimate

| Task | Estimate |
|------|----------|
| Full-scan flag | 1 hour |
| Semgrep export | 4 hours |
| MobSF scanner | 8 hours |
| Dependency scanner | 6 hours |
| **Total** | **19 hours (3 days)** |

---

## Implementation Order

### Recommended Sequence

```
Week 1:
├── Day 1: Phase 8.1 - CWE Mapping (1 day)
│   ├── Task 1: Update models.py
│   ├── Task 2: Update rules loaders
│   ├── Task 3: Add CWE to iOS rules
│   └── Task 4: Add CWE to Android rules
│
├── Day 2: Phase 8.2 - False Positive Tracking (1 day)
│   ├── Task 1: Update Finding model
│   ├── Task 2: Create FP-Tracking sheet
│   ├── Task 3: Implement auto-detection
│   └── Task 4: Add CLI command
│
└── Day 3: Phase 8.3 - Metrics Framework (1 day)
    ├── Task 1: Create Metrics sheet
    ├── Task 2: Implement KPI calculator
    └── Task 3: Add CLI command

Week 2 (Optional):
└── Day 4-6: Phase 8.4 - Tooling Integration (3 days)
    ├── Task 1: Full-scan flag
    ├── Task 2: Semgrep export
    ├── Task 3: MobSF integration
    └── Task 4: Dependency scanner
```

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| CWE mapping errors | Low | Medium | Review against MITRE CWE |
| FP auto-detection false negatives | Medium | Low | Allow manual override |
| MobSF API changes | Low | Low | Version pinning |
| Performance impact of metrics | Low | Low | Async calculation |

---

## Dependencies

| Phase | Depends On |
|-------|-----------|
| 8.2 FP Tracking | 8.1 CWE Mapping |
| 8.3 Metrics | 8.2 FP Tracking |
| 8.4 Tooling | 8.1, 8.2, 8.3 |

---

## Success Criteria

- [ ] All 85 rules have CWE mapping
- [ ] False positive rate tracked (< 5% target)
- [ ] KPI dashboard updated per scan
- [ ] Semgrep export functional
- [ ] MobSF integration (optional)
- [ ] No regression in 213 tests

---

## Research Sources

| Topic | Key Takeaways |
|-------|---------------|
| CWE Mapping | Use MITRE CWE as source of truth; maintain mapping file; quarterly review cadence |
| FP Detection | Auto-detect test/generated files; ML/LLM triage for complex cases; < 5% target |
| Metrics | Track Findings/KLOC, FP Rate, Remediation Time; visualize in dashboard |
| MobSF | REST API integration; suppression for FP; Docker deployment |
| Semgrep | YAML rule export; IDE integration via VS Code/IntelliJ; SARIF output |
