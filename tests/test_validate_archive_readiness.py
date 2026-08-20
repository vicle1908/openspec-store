"""Tests for validate-archive-readiness.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

# Load the validator script as a module
SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate-archive-readiness.py"
spec = importlib.util.spec_from_file_location("validator", SCRIPT_PATH)
validator = importlib.util.module_from_spec(spec)
sys.modules["validator"] = validator
assert spec is not None and spec.loader is not None
spec.loader.exec_module(validator)


@pytest.fixture
def store_env(tmp_path: Path) -> Path:
    """Create a minimal mock OpenSpec store."""
    openspec_dir = tmp_path / "openspec"
    openspec_dir.mkdir()
    (openspec_dir / "config.yaml").write_text("context: test\n", encoding="utf-8")
    (openspec_dir / "specs").mkdir()
    (openspec_dir / "changes").mkdir()
    (openspec_dir / "changes" / "archive").mkdir()
    return tmp_path


def test_ready_change_passes(store_env: Path) -> None:
    change_dir = store_env / "openspec" / "changes" / "test-change"
    change_dir.mkdir()
    (change_dir / "proposal.md").write_text("# Proposal\nskip_specs: true\n", encoding="utf-8")
    (change_dir / "design.md").write_text("# Design\n", encoding="utf-8")
    (change_dir / "tasks.md").write_text("## Tasks\n- [x] Task 1\n- [x] Task 2\n", encoding="utf-8")

    report = validator.check_change_readiness(change_dir, store_env)
    assert report.status == "ready"
    assert report.exit_code == 0
    assert report.tasks.completed == 2
    assert report.tasks.remaining == 0


def test_incomplete_tasks_blocked(store_env: Path) -> None:
    change_dir = store_env / "openspec" / "changes" / "blocked-change"
    change_dir.mkdir()
    (change_dir / "proposal.md").write_text("# Proposal\nskip_specs: true\n", encoding="utf-8")
    (change_dir / "design.md").write_text("# Design\n", encoding="utf-8")
    (change_dir / "tasks.md").write_text("## Tasks\n- [x] Task 1\n- [ ] Task 2\n", encoding="utf-8")

    report = validator.check_change_readiness(change_dir, store_env)
    assert report.status == "blocked"
    assert report.exit_code == 3
    assert report.tasks.completed == 1
    assert report.tasks.remaining == 1
    assert "Task 2" in report.tasks.unchecked_tasks[0]


def test_missing_proposal_invalid(store_env: Path) -> None:
    change_dir = store_env / "openspec" / "changes" / "invalid-change"
    change_dir.mkdir()
    (change_dir / "design.md").write_text("# Design\n", encoding="utf-8")
    (change_dir / "tasks.md").write_text("## Tasks\n- [x] Task 1\n", encoding="utf-8")

    report = validator.check_change_readiness(change_dir, store_env)
    assert report.status == "invalid"
    assert report.exit_code == 4
    assert any("proposal.md" in err for err in report.errors)


def test_delta_spec_validation(store_env: Path) -> None:
    change_dir = store_env / "openspec" / "changes" / "spec-change"
    change_dir.mkdir()
    (change_dir / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
    (change_dir / "design.md").write_text("# Design\n", encoding="utf-8")
    (change_dir / "tasks.md").write_text("## Tasks\n- [x] Task 1\n", encoding="utf-8")

    specs_dir = change_dir / "specs" / "auth"
    specs_dir.mkdir(parents=True)
    valid_spec = specs_dir / "spec.md"
    valid_spec.write_text(
        "# Delta Spec\n\n## ADDED Requirements\n\n### Requirement: User Auth\n"
        "User SHALL be authenticated.\n\n#### Scenario: Login\nGiven user When login Then succeed.\n",
        encoding="utf-8",
    )

    report = validator.check_change_readiness(change_dir, store_env)
    assert report.status == "ready"
    assert report.exit_code == 0
    assert report.delta_specs_count == 1
