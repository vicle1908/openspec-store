#!/usr/bin/env python3
"""Replay the canonical agent mutation sequence against the canonical fixture.

CI gate for the ``add-enterprise-architecture-modeling`` change (tasks 6.4
and the "Agent mutation regression" scenario): the sequence create element +
create relationship + update element name is applied twice to a temporary
copy of ``docs/architecture/models/canonical.xml`` through the headless
engine API, then the script asserts:

1. the mutated model still passes structural + semantic validation,
   both through the engine API and through the CLI ``validate`` command;
2. the second application is idempotent (no duplicate objects);
3. identifiers are stable across both applications (no churn);
4. unmodified content (views, bendpoints, organization folders, property
   definitions, vendor extensions, pre-existing elements and relationships)
   is preserved;
5. the repository fixture itself is untouched (same bytes, no backup or lock
   files created next to it).

Any failed assertion makes the script exit non-zero.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.archimate.engine import (  # noqa: E402
    ArchimateModel,
    ModelError,
    deterministic_id,
)

ENGINE = REPO_ROOT / "scripts" / "archimate" / "engine.py"
CANONICAL = REPO_ROOT / "docs" / "architecture" / "models" / "canonical.xml"

# Canonical agent mutation sequence: create a BusinessRole, assign the
# existing Claims Administrator actor to it, then update the new element's
# name. Assignment (actor -> role) is a legal ArchiMate 3.2 pairing.
ASSIGNMENT_SOURCE = "ea-a87d473086132d9f"  # Claims Administrator (BusinessActor)
NEW_ELEMENT = {"op": "create_element", "type": "BusinessRole",
               "name": "Claims Intake Specialist", "layer": "business"}
NEW_ELEMENT_ID = deterministic_id("element", "BusinessRole", "Claims Intake Specialist")
REVIEWED_NAME = "Claims Intake Specialist (Reviewed)"
NEW_RELATIONSHIP = {"op": "create_relationship", "type": "Assignment",
                    "source": ASSIGNMENT_SOURCE, "target": NEW_ELEMENT_ID}
NEW_RELATIONSHIP_ID = deterministic_id(
    "relationship", "Assignment", f"{ASSIGNMENT_SOURCE}->{NEW_ELEMENT_ID}"
)
UPDATE_NAME = {"op": "update_element", "identifier": NEW_ELEMENT_ID, "name": REVIEWED_NAME}
OPERATIONS = [NEW_ELEMENT, NEW_RELATIONSHIP, UPDATE_NAME]

failures: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    status = "ok" if condition else "FAIL"
    suffix = f" :: {detail}" if detail else ""
    print(f"[{status}] {label}{suffix}")
    if not condition:
        failures.append(label)


def census(path: Path) -> dict[str, object]:
    """Independent structural census of an exchange XML model file."""
    root = ET.parse(path).getroot()
    elements = {
        node.get("identifier", ""): (
            (node.get("{http://www.w3.org/2001/XMLSchema-instance}type") or "").split(":")[-1],
            next((c.text or "" for c in node if c.tag.endswith("}name")), ""),
        )
        for node in root.iter() if node.tag.endswith("}element")
    }
    relationships = {
        node.get("identifier", ""): (
            (node.get("{http://www.w3.org/2001/XMLSchema-instance}type") or "").split(":")[-1],
            node.get("source", ""),
            node.get("target", ""),
        )
        for node in root.iter() if node.tag.endswith("}relationship")
    }
    return {
        "model_identifier": root.get("identifier", ""),
        "elements": elements,
        "relationships": relationships,
        "views": sorted(node.get("identifier", "") for node in root.iter()
                        if node.tag.endswith("}view")),
        "bendpoints": sum(1 for node in root.iter() if node.tag.endswith("}bendpoint")),
        "organization_items": sorted(node.get("identifier", "") for node in root.iter()
                                     if node.tag.endswith("}item") and node.get("identifier")),
        "property_definitions": sorted(node.get("identifier", "") for node in root.iter()
                                       if node.tag.endswith("}propertyDefinition")),
        "vendor_extensions": sorted(node.get("id", "") for node in root.iter()
                                    if node.tag.endswith("}extension")),
    }


def snapshot(model: ArchimateModel) -> dict[str, object]:
    """Engine-side identifier snapshot for churn detection."""
    return {
        "elements": {e["identifier"]: (e["type"], e["name"]) for e in model.elements(limit=10**6)},
        "relationships": {r["identifier"]: (r["type"], r["source"], r["target"])
                          for r in model.relationships(limit=10**6)},
    }


def apply_sequence(model: ArchimateModel, label: str) -> None:
    """Apply the canonical batch, recording a rejection as a failed check."""
    try:
        model.mutate(OPERATIONS)
    except ModelError as exc:
        check(f"{label}: batch accepted", False, str(exc))
        raise SystemExit(1) from exc


def main() -> int:
    if not CANONICAL.is_file():
        print(f"REPLAY FAILED: canonical fixture missing: {CANONICAL}", file=sys.stderr)
        return 1

    original_bytes = CANONICAL.read_bytes()
    original_sha = hashlib.sha256(original_bytes).hexdigest()
    models_dir = CANONICAL.parent
    stray_before = sorted(p.name for p in models_dir.iterdir()
                          if p.name.endswith(".bak") or ".lock" in p.name)

    with tempfile.TemporaryDirectory(prefix="archimate-replay-") as temp:
        work = Path(temp) / "canonical.xml"
        shutil.copy2(CANONICAL, work)

        baseline = census(work)
        model = ArchimateModel.load(work)
        apply_sequence(model, "first application")
        after_first = census(work)
        engine_snapshot_first = snapshot(model)

        # -- assertions after the first application -------------------------
        issues = model.validate()
        check("first application: model still validates via engine API",
              not issues, str([i.rule for i in issues]))
        check("first application: element added exactly once",
              NEW_ELEMENT_ID in after_first["elements"]
              and len(after_first["elements"]) == len(baseline["elements"]) + 1,
              f"expected {NEW_ELEMENT_ID}")
        check("first application: element name updated",
              after_first["elements"].get(NEW_ELEMENT_ID, ("", ""))[1] == REVIEWED_NAME)
        check("first application: relationship added exactly once",
              NEW_RELATIONSHIP_ID in after_first["relationships"]
              and len(after_first["relationships"]) == len(baseline["relationships"]) + 1)

        # -- second (idempotent) application --------------------------------
        apply_sequence(model, "second application")
        after_second = census(work)
        engine_snapshot_second = snapshot(model)

        issues = model.validate()
        check("second application: model still validates via engine API",
              not issues, str([i.rule for i in issues]))
        check("idempotent: no new elements added",
              after_second["elements"] == after_first["elements"],
              f"{len(after_second['elements'])} vs {len(after_first['elements'])}")
        check("idempotent: no new relationships added",
              after_second["relationships"] == after_first["relationships"])
        check("identifiers stable: engine element identifiers unchanged",
              engine_snapshot_second["elements"] == engine_snapshot_first["elements"])
        check("identifiers stable: engine relationship identifiers unchanged",
              engine_snapshot_second["relationships"] == engine_snapshot_first["relationships"])

        # -- unmodified content preserved ----------------------------------
        for key in ("model_identifier", "views", "bendpoints",
                    "organization_items", "property_definitions", "vendor_extensions"):
            check(f"preserved: {key} identical to fixture",
                  after_second[key] == baseline[key],
                  f"{after_second[key]!r} vs {baseline[key]!r}")
        original_elements = {k: v for k, v in after_second["elements"].items()
                             if k in baseline["elements"]}
        check("preserved: all pre-existing elements unchanged",
              original_elements == baseline["elements"])
        original_relationships = {k: v for k, v in after_second["relationships"].items()
                                  if k in baseline["relationships"]}
        check("preserved: all pre-existing relationships unchanged",
              original_relationships == baseline["relationships"])

        # -- CLI surface also validates the mutated model -------------------
        cli = subprocess.run(
            [sys.executable, str(ENGINE), "--model", str(work), "validate"],
            capture_output=True, text=True, timeout=120,
        )
        check("CLI validate exits 0 on mutated model", cli.returncode == 0,
              f"exit={cli.returncode} {cli.stdout.strip()[:200]} {cli.stderr.strip()[:200]}")
        check("CLI validate reports model as valid", '"valid": true' in cli.stdout)

    # -- repository fixture untouched ----------------------------------------
    final_sha = hashlib.sha256(CANONICAL.read_bytes()).hexdigest()
    check("repository fixture bytes unchanged", final_sha == original_sha)
    stray_after = sorted(p.name for p in models_dir.iterdir()
                         if p.name.endswith(".bak") or ".lock" in p.name)
    check("no backup/lock files left next to repository fixture",
          stray_after == stray_before, f"{stray_after} vs {stray_before}")

    if failures:
        print(f"REPLAY FAILED: {len(failures)} assertion(s) failed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1
    print("REPLAY PASSED: canonical mutation sequence is valid, idempotent, "
          "identifier-stable, preservation-safe, and leaves the fixture untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
