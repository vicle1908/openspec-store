"""Spec coverage matrix: every Scenario: in spec.md → test function. Print gaps."""
import re
from pathlib import Path

SPEC = Path("/Users/lekhanhvinh/Developer/tdt/tdt-meta/openspec/changes/jira-person-capacity-worklog-mode/specs/person-capacity-worklog-mode/spec.md")
TESTS_UNIT = Path("/Users/lekhanhvinh/Developer/tdt/jira-daily-reports/tests/test_person_worklog_source.py")
TESTS_INT = Path("/Users/lekhanhvinh/Developer/tdt/jira-daily-reports/tests/test_sprint_report_sheet_person_capacity.py")
TESTS_LEG = Path("/Users/lekhanhvinh/Developer/tdt/jira-daily-reports/tests/test_sprint_report_sheet.py")

spec = SPEC.read_text()
unit = TESTS_UNIT.read_text()
integ = TESTS_INT.read_text()
legacy = TESTS_LEG.read_text()

# Extract requirements + scenarios in order
req_re = re.compile(r"^### Requirement: (.+?)$", re.M)
sc_re = re.compile(r"^#### Scenario: (.+?)$", re.M)

requirements = [(m.start(), m.group(1)) for m in req_re.finditer(spec)]
scenarios = []
for m in sc_re.finditer(spec):
    pos = m.start()
    req = next((r for s, r in requirements if s < pos), "<pre-req>")
    scenarios.append((req, m.group(1)))

# For each scenario, search the test files for likely coverage
unit_names = set(re.findall(r"^def (test_[a-z0-9_]+)\b", unit, re.M))
integ_names = set(re.findall(r"^def (test_[a-z0-9_]+)\b", integ, re.M))
legacy_names = set(re.findall(r"def (test_[a-z0-9_]+)\b", legacy))

def matches(text: str, scenario: str) -> list[str]:
    """Find test functions whose names hint at this scenario."""
    sl = scenario.lower()
    keywords = re.findall(r"[a-z]+", sl)
    cands = []
    for n in (*unit_names, *integ_names, *legacy_names):
        nl = n.lower()
        score = sum(1 for k in keywords if k in nl)
        if score >= 2:
            cands.append(n)
    return cands

# Per-scenario coverage report
covered, gaps = [], []
for req, sc in scenarios:
    cands = matches(unit + integ + legacy, sc)
    (covered if cands else gaps).append((req, sc, cands))

print(f"Total scenarios: {len(scenarios)}")
print(f"Auto-matched: {len(covered)}")
print(f"GAPS (no test name matches): {len(gaps)}\n")

print("=" * 80)
print("GAPS:")
print("=" * 80)
for req, sc, cands in gaps:
    print(f"\n  [{req}]")
    print(f"    Scenario: {sc}")
    print(f"    Auto-matches: {cands}")
