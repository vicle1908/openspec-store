from __future__ import annotations

import fcntl
import os
import shutil
from pathlib import Path

import pytest

from scripts.archimate.engine import ArchimateModel, ModelError, deterministic_id

ROOT = Path(__file__).resolve().parents[1] / "docs" / "architecture" / "models"
CANONICAL = ROOT / "canonical.xml"


def copy_model(tmp_path: Path, name: str = "canonical.xml") -> Path:
    target = tmp_path / name
    shutil.copy2(ROOT / name if name == "canonical.xml" else ROOT / "regression" / name, target)
    return target


def test_read_queries_are_side_effect_free_and_bounded(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    before, mtime = path.read_bytes(), path.stat().st_mtime_ns
    model = ArchimateModel.load(path)
    assert model.metadata()["elements"] == 14
    assert model.elements(layer="business", limit=2)
    assert model.relationships(type="Serving", limit=1)
    result = model.neighbors("ea-a87d473086132d9f", depth=2, limit=1)
    assert result["truncated"] is True
    assert path.read_bytes() == before and path.stat().st_mtime_ns == mtime


def test_create_element_identity_and_idempotence(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    model = ArchimateModel.load(path)
    op = {"op": "create_element", "type": "BusinessActor", "name": "Smoke Actor"}
    model.mutate([op])
    expected = deterministic_id("element", "BusinessActor", "Smoke Actor")
    assert expected.startswith("ea-") and len(expected) == 19
    assert sum(e["identifier"] == expected for e in model.elements()) == 1
    model.mutate([op])
    assert sum(e["identifier"] == expected for e in model.elements()) == 1


def test_relationship_reversal_rejected_byte_identical(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    before = path.read_bytes()
    model = ArchimateModel.load(path)
    with pytest.raises(ModelError, match="SEMANTIC_SERVING_REVERSED"):
        model.mutate([{"op": "create_relationship", "type": "Serving", "source": "ea-a87d473086132d9f", "target": "ea-b31c7f23b5ca624e"}], backup=False)
    assert path.read_bytes() == before


def test_update_delete_and_reference_safety(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    model = ArchimateModel.load(path)
    model.mutate([{"op": "update_element", "identifier": "ea-a87d473086132d9f", "name": "Updated"}], backup=False)
    assert model.elements(name="Updated")[0]["identifier"] == "ea-a87d473086132d9f"
    with pytest.raises(ModelError, match="MUTATION_REFERENCED_ELEMENT"):
        model.mutate([{"op": "delete_element", "identifier": "ea-a87d473086132d9f"}], backup=False)
    with pytest.raises(ModelError, match="MUTATION_REFERENCED_ELEMENT"):
        model.mutate([{"op": "delete_element", "identifier": "ea-f86d28d9bf0cf00b"}], backup=False)


def test_batch_atomicity_and_backup(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    before = path.read_bytes()
    model = ArchimateModel.load(path)
    with pytest.raises(ModelError):
        model.mutate([{"op": "create_element", "type": "BusinessActor", "name": "Transient"}, {"op": "unsupported"}])
    assert path.read_bytes() == before
    model.mutate([{"op": "create_element", "type": "BusinessActor", "name": "Committed"}])
    assert path.with_name("canonical.xml.bak").exists()


def test_preservation_and_fail_closed_inputs(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    model = ArchimateModel.load(path)
    model.mutate([{"op": "update_element", "identifier": "ea-d01ae79cb61c7f9d", "name": "Registry Updated"}], backup=False)
    output = path.read_text(encoding="utf-8")
    assert "bendpoint" in output and "organizations" in output and "ext:extension" in output and "propertyDefinitionRef" in output
    for marker in ("<!DOCTYPE x>", "<![CDATA[unsafe]]>"):
        bad = tmp_path / ("doctype.xml" if "DOCTYPE" in marker else "cdata.xml")
        bad.write_text(f"<?xml version='1.0'?><model>{marker}<elements/></model>", encoding="utf-8")
        with pytest.raises(ModelError, match="PRESERVATION_FAIL_CLOSED|STRUCTURE_XML_NOT_WELL_FORMED"):
            ArchimateModel.load(bad).mutate([{"op": "create_element", "type": "BusinessActor", "name": "x"}], backup=False)

def test_reload_round_trip_and_lock_serialization(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    model = ArchimateModel.load(path)
    model.mutate([{"op": "update_element", "identifier": "ea-d01ae79cb61c7f9d", "name": "Reloaded"}], backup=False)
    assert ArchimateModel.load(path).elements(name="Reloaded")
    lock = path.parent / f".{path.name}.lock"
    with lock.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(ModelError, match="PERSISTENCE_SINGLE_WRITER_BUSY"):
            ArchimateModel.load(path).mutate([{"op": "update_element", "identifier": "ea-d01ae79cb61c7f9d", "name": "Blocked"}], backup=False)
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def test_reversed_serving_rejected_after_ns_fallback_reload(tmp_path: Path) -> None:
    """Regression: after one persisted mutation the serialized file may use an
    nsN-prefixed fallback form, so a reload has default_ns=None. Semantic rules
    must still see xsi:type on created nodes and reject a reversed Serving."""
    path = copy_model(tmp_path)
    model = ArchimateModel.load(path)
    model.mutate([{"op": "create_element", "type": "BusinessRole", "name": "Policy Owner"}], backup=False)
    reloaded = ArchimateModel.load(path)
    before = path.read_bytes()
    role = reloaded.elements(name="Policy Owner")[0]["identifier"]
    service = "ea-b31c7f23b5ca624e"  # ApplicationService Register Claim
    with pytest.raises(ModelError, match="SEMANTIC_SERVING_REVERSED"):
        reloaded.mutate(
            [{"op": "create_relationship", "type": "Serving", "source": role, "target": service}],
            backup=False,
        )
    # Direct no-default-ns path: a model whose elements use a prefixed
    # namespace (default_ns None) must still expose xsi:type to the
    # semantic rules for nodes created by the engine.
    prefixed = tmp_path / "prefixed.xml"
    prefixed.write_text(
        '<model xmlns:ar="http://www.opengroup.org/xsd/archimate/3.0/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        "<ar:elements>"
        '<ar:element identifier="ea-1" xsi:type="BusinessRole"><ar:name>R</ar:name></ar:element>'
        '<ar:element identifier="ea-2" xsi:type="BusinessService"><ar:name>S</ar:name></ar:element>'
        "</ar:elements>"
        "<ar:relationships/>"
        "</model>",
        encoding="utf-8",
    )
    prefixed_model = ArchimateModel.load(prefixed)
    assert prefixed_model.default_ns is None
    prefixed_model._apply(
        {"op": "create_relationship", "type": "Serving", "source": "ea-1", "target": "ea-2"}
    )
    assert [issue.rule for issue in prefixed_model.validate()] == ["SEMANTIC_SERVING_REVERSED"]


def test_attribute_reference_safety_and_organization_listing(tmp_path: Path) -> None:
    path = copy_model(tmp_path)
    model = ArchimateModel.load(path)
    assert len(model.organizations()) == 8
    assert {item["label"] for item in model.organizations()} >= {"Business", "Application", "Technology"}
    before = path.read_bytes()
    with pytest.raises(ModelError, match="MUTATION_REFERENCED_RELATIONSHIP"):
        model.mutate([{"op": "delete_relationship", "identifier": "rel-43946800a5879cc4"}], backup=False)
    assert path.read_bytes() == before
    with pytest.raises(ModelError, match="MUTATION_REFERENCED_ELEMENT"):
        model.mutate([{"op": "delete_element", "identifier": "ea-a87d473086132d9f"}], backup=False)
    dangling = tmp_path / "dangling-connection.xml"
    text = path.read_text(encoding="utf-8").replace('relationshipRef="rel-43946800a5879cc4"', 'relationshipRef="rel-missing"')
    dangling.write_text(text, encoding="utf-8")
    assert any(issue.rule == "STRUCTURAL_IDREF_UNRESOLVED" and issue.construct == "rel-missing" for issue in ArchimateModel.load(dangling).validate())


def test_organization_item_view_reference_resolves(tmp_path: Path) -> None:
    """Regression: organization items may reference views (identifierRef to
    view@identifier), per the Open Exchange schema — Archi 5.10.0 round-trip
    output contains <item identifierRef="view-..."/>. Such refs must validate
    clean, while a genuinely dangling identifierRef must still be flagged."""
    path = copy_model(tmp_path)
    text = path.read_text(encoding="utf-8").replace(
        '<item identifierRef="ea-a87d473086132d9f"/>',
        '<item identifierRef="view-07de3e07c916f9f7"/>',
        1,
    )
    view_ref = tmp_path / "org-view-ref.xml"
    view_ref.write_text(text, encoding="utf-8")
    assert [
        issue.rule for issue in ArchimateModel.load(view_ref).validate()
    ] == []
    dangling = tmp_path / "org-dangling-ref.xml"
    dangling.write_text(
        text.replace(
            '<item identifierRef="view-07de3e07c916f9f7"/>',
            '<item identifierRef="view-nonexistent"/>',
        ),
        encoding="utf-8",
    )
    issues = ArchimateModel.load(dangling).validate()
    assert [issue.rule for issue in issues] == ["STRUCTURAL_IDREF_UNRESOLVED"]
    assert issues[0].construct == "view-nonexistent"
