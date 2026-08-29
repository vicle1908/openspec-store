#!/usr/bin/env python3
"""Focused tests for validate-retention-inventory.py.

Covers the verification clauses for tasks 2.1 (schema rejection), 2.2
(store/load/approval), 2.3 (provenance freshness downgrade), 3.1 (exclusion
handoff with recorded reasons), 3.2 (review-only candidates, no mutation), and
4.2 (unavailable adapter -> UNKNOWN blocks reclamation). All fixtures live in a
temporary directory; no retained path or runtime state is touched.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "validate-retention-inventory.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("vri", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


vri = load_tool()

NOW = "2026-08-25T08:56:00Z"


def make_entry(**overrides):
    entry = {
        "path": "/tmp/example/graphify-out",
        "class": "generated index or cache",
        "policy_state": "PROTECTED",
        "owner": "knowledge-refresh",
        "provenance": {
            "type": "runtime_observation",
            "revision": None,
            "evidence": None,
            "observed_at": NOW,
        },
        "justification": "generated output owned by approved refresh contract",
        "last_reference": NOW,
        "candidate": False,
        "review": {"reviewed_at": NOW, "reviewed_by": "test", "note": None},
    }
    entry.update(overrides)
    return entry


def make_doc(entries=None, **overrides):
    doc = {
        "policy": "workspace-artifact-retention-policy",
        "policy_version": "1.0.0",
        "policy_identity": "warp-1.0.0-test",
        "approval": {
            "approved": True,
            "digest": "placeholder",
            "approved_at": NOW,
            "approved_by": "test",
        },
        "generated_at": NOW,
        "entries": entries if entries is not None else [make_entry()],
    }
    doc.update(overrides)
    return doc


def write_inventory(tmp: Path, doc) -> Path:
    """Write inventory with a correct approval digest and return its path."""
    inventory_path = tmp / "retention-inventory.json"
    # The digest field seals the entries; the sibling file seals the document.
    doc["approval"]["digest"] = hashlib.sha256(
        json.dumps(doc.get("entries", []), sort_keys=True).encode("utf-8")
    ).hexdigest()
    raw = json.dumps(doc, indent=2).encode("utf-8")
    inventory_path.write_bytes(raw)
    approval_path = tmp / "retention-inventory.approval.sha256"
    approval_path.write_text(
        hashlib.sha256(raw).hexdigest() + "  retention-inventory.json\n"
    )
    return inventory_path


def run_cli(inventory_path: Path, approval_path=None):
    cmd = [sys.executable, str(TOOL), "--inventory", str(inventory_path), "--json"]
    if approval_path:
        cmd += ["--approval", str(approval_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    report = None
    if result.stdout.strip():
        try:
            report = json.loads(result.stdout)
        except Exception:
            report = None
    return result.returncode, report, result.stderr


class SchemaRejectionTests(unittest.TestCase):
    """Task 2.1: schema validation rejects missing identity, stale/malformed
    provenance, and secret/request-body fields."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_missing_policy_identity_rejected(self):
        doc = make_doc(policy_identity="")
        path = write_inventory(self.dir, doc)
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_SCHEMA)
        self.assertIn("policy_identity", err)

    def test_missing_policy_version_rejected(self):
        doc = make_doc(policy_version="")
        path = write_inventory(self.dir, doc)
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_SCHEMA)
        self.assertIn("policy_version", err)

    def test_secret_field_rejected(self):
        entry = make_entry()
        entry["password"] = "hunter2"
        path = write_inventory(self.dir, make_doc([entry]))
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_SCHEMA)
        self.assertIn("forbidden field 'password'", err)

    def test_request_body_field_rejected(self):
        entry = make_entry()
        entry["request_body"] = {"k": "v"}
        path = write_inventory(self.dir, make_doc([entry]))
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_SCHEMA)
        self.assertIn("request_body", err)

    def test_malformed_provenance_type_rejected(self):
        entry = make_entry(provenance={"type": "bogus"})
        path = write_inventory(self.dir, make_doc([entry]))
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_SCHEMA)
        self.assertIn("provenance.type", err)

    def test_invalid_class_rejected(self):
        entry = make_entry()
        entry["class"] = "not a reviewed class"
        path = write_inventory(self.dir, make_doc([entry]))
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_SCHEMA)
        self.assertIn("class", err)


class ApprovalTests(unittest.TestCase):
    """Task 2.2: reload preserves policy identity and rejects an unapproved or
    malformed inventory."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_approved_reload_preserves_identity(self):
        doc = make_doc()
        path = write_inventory(self.dir, doc)
        code, report, _ = run_cli(path)
        self.assertEqual(code, vri.EXIT_OK)
        self.assertTrue(report["approved"])
        self.assertEqual(report["policy_identity"], "warp-1.0.0-test")
        self.assertEqual(report["policy_version"], "1.0.0")

    def test_digest_mismatch_rejected_as_unapproved(self):
        doc = make_doc()
        path = write_inventory(self.dir, doc)
        # Tamper with the inventory after approval.
        tampered = json.loads(path.read_text())
        tampered["entries"][0]["justification"] = "changed after approval"
        path.write_text(json.dumps(tampered))
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_UNAPPROVED)
        self.assertIn("digest mismatch", err)

    def test_missing_approval_file_rejected(self):
        doc = make_doc()
        path = write_inventory(self.dir, doc)
        (self.dir / "retention-inventory.approval.sha256").unlink()
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_UNAPPROVED)
        self.assertIn("not found", err)

    def test_malformed_json_rejected(self):
        path = self.dir / "retention-inventory.json"
        path.write_text("{ not valid json")
        code, _, err = run_cli(path)
        self.assertEqual(code, vri.EXIT_SCHEMA)
        self.assertIn("malformed JSON", err)


class FreshnessTests(unittest.TestCase):
    """Task 2.3: stale or missing provenance downgrades entries to
    REVIEW_REQUIRED."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def _write_and_load(self, doc):
        path = write_inventory(self.dir, doc)
        code, report, _ = run_cli(path)
        return code, report

    def test_missing_observed_at_downgrades(self):
        entry = make_entry(provenance={"type": "runtime_observation",
                                       "observed_at": None})
        code, report = self._write_and_load(make_doc([entry]))
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["entries"][0]["effective_state"], "REVIEW_REQUIRED")
        self.assertEqual(report["summary"]["stale_downgraded"], 1)

    def test_missing_evidence_reference_downgrades(self):
        entry = make_entry(provenance={"type": "evidence_identity",
                                       "evidence": str(self.dir / "absent.md")})
        code, report = self._write_and_load(make_doc([entry]))
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["entries"][0]["effective_state"], "REVIEW_REQUIRED")

    def test_present_evidence_reference_is_fresh(self):
        evidence = self.dir / "evidence.md"
        evidence.write_text("reviewed\n")
        entry = make_entry(provenance={"type": "evidence_identity",
                                       "evidence": str(evidence)})
        code, report = self._write_and_load(make_doc([entry]))
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["entries"][0]["effective_state"], "PROTECTED")
        self.assertTrue(report["entries"][0]["fresh"])

    def test_stale_repo_revision_downgrades(self):
        repo = self.dir / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "f.txt").write_text("x\n")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-qm", "c1"], check=True)
        entry = make_entry(path=str(repo / "f.txt"),
                           provenance={"type": "repo_revision",
                                       "revision": "0" * 40})
        code, report = self._write_and_load(make_doc([entry]))
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["entries"][0]["effective_state"], "REVIEW_REQUIRED")
        self.assertIn("stale", report["entries"][0]["freshness_reason"])

    def test_fresh_repo_revision_stays_protected(self):
        repo = self.dir / "repo2"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "f.txt").write_text("x\n")
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t",
             "commit", "-qm", "c1"], check=True)
        head = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True).stdout.strip()
        entry = make_entry(path=str(repo / "f.txt"),
                           policy_state="PROTECTED",
                           provenance={"type": "repo_revision", "revision": head})
        code, report = self._write_and_load(make_doc([entry]))
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["entries"][0]["effective_state"], "PROTECTED")
        self.assertTrue(report["entries"][0]["fresh"])


class ExclusionHandoffTests(unittest.TestCase):
    """Task 3.1: protected evidence, rollback, permanent fixtures, and
    active-index paths are handed off as exclusions with recorded reasons."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_protected_classes_appear_as_exclusions_with_reasons(self):
        evidence = self.dir / "evidence.md"
        evidence.write_text("reviewed\n")
        prov = {"type": "evidence_identity", "evidence": str(evidence)}
        entries = [
            make_entry(path="/tmp/x/reports",
                       **{"class": "retained evidence or report"},
                       owner="evidence owner", provenance=prov),
            make_entry(path="/tmp/x/snapshots",
                       **{"class": "retained rollback or snapshot"},
                       owner="rollback owner", provenance=prov),
            make_entry(path="/tmp/x/fixture",
                       **{"class": "tracked permanent fixture"},
                       owner="owning repo", provenance=prov),
            make_entry(path="/tmp/x/index",
                       **{"class": "active index state"},
                       owner="index watcher", provenance=prov),
        ]
        path = write_inventory(self.dir, make_doc(entries))
        code, report, _ = run_cli(path)
        self.assertEqual(code, vri.EXIT_OK)
        excluded_paths = {e["path"] for e in report["exclusions"]}
        self.assertEqual(
            excluded_paths,
            {"/tmp/x/reports", "/tmp/x/snapshots", "/tmp/x/fixture", "/tmp/x/index"},
        )
        for exclusion in report["exclusions"]:
            self.assertIn(exclusion["class"], exclusion["reason"])
            self.assertIn(exclusion["owner"], exclusion["reason"])
            self.assertIn("SHALL skip", exclusion["reason"])
        self.assertEqual(report["summary"]["exclusions"], 4)

    def test_review_required_entry_is_not_an_exclusion(self):
        entry = make_entry(provenance={"type": "runtime_observation",
                                       "observed_at": None})
        path = write_inventory(self.dir, make_doc([entry]))
        code, report, _ = run_cli(path)
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["exclusions"], [])


class ReviewProposalTests(unittest.TestCase):
    """Task 3.2: an ephemeral fixture produces a review proposal and no
    filesystem mutation."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_ephemeral_fixture_produces_review_proposal_no_mutation(self):
        fixture = self.dir / "ephemeral-fixture.dat"
        fixture.write_text("disposable test fixture\n")
        entry = make_entry(
            path=str(fixture),
            **{"class": "temporary or ephemeral test fixture"},
            policy_state="RECLAIMABLE",
            owner="test-owner",
            candidate=True,
            provenance={"type": "evidence_identity", "evidence": str(fixture)},
            justification="untracked disposable fixture cleared by review evidence",
        )
        doc = make_doc([entry])
        path = write_inventory(self.dir, doc)
        before_inventory = path.read_bytes()
        before_fixture = fixture.read_bytes()
        approval = self.dir / "retention-inventory.approval.sha256"
        before_approval = approval.read_bytes()

        code, report, _ = run_cli(path)
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(len(report["review_proposals"]), 1)
        proposal = report["review_proposals"][0]
        self.assertEqual(proposal["path"], str(fixture))
        self.assertIn("do not auto-delete", proposal["reason"])
        self.assertEqual(report["exclusions"], [])
        # No filesystem mutation anywhere.
        self.assertEqual(path.read_bytes(), before_inventory)
        self.assertEqual(approval.read_bytes(), before_approval)
        self.assertEqual(fixture.read_bytes(), before_fixture)
        self.assertTrue(fixture.exists())

    def test_unknown_owner_candidate_is_not_reclaimable_proposal(self):
        entry = make_entry(policy_state="RECLAIMABLE", owner="UNKNOWN",
                           candidate=True)
        path = write_inventory(self.dir, make_doc([entry]))
        code, report, _ = run_cli(path)
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["entries"][0]["effective_state"], "REVIEW_REQUIRED")
        self.assertEqual(report["review_proposals"], [])
        self.assertEqual(report["summary"]["reclaimable"], 0)


class AdapterFailClosedTests(unittest.TestCase):
    """Task 4.2: unavailable LaunchAgent or container adapters produce UNKNOWN
    and block reclamation."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def _load(self, entry):
        path = write_inventory(self.dir, make_doc([entry]))
        code, report, _ = run_cli(path)
        return code, report

    def test_launchagent_adapter_unavailable_blocks_reclamation(self):
        entry = make_entry(
            path="/tmp/x/launchagent-state",
            policy_state="RECLAIMABLE",
            owner="UNKNOWN",
            justification="LaunchAgent adapter unavailable; ownership unconfirmed",
        )
        entry["review"]["note"] = "adapter=launchagent; unavailable at review time"
        code, report = self._load(entry)
        self.assertEqual(code, vri.EXIT_OK)
        result = report["entries"][0]
        self.assertEqual(result["effective_state"], "REVIEW_REQUIRED")
        self.assertNotEqual(result["effective_state"], "RECLAIMABLE")
        self.assertIn("owner UNKNOWN blocks reclamation", result["freshness_reason"])
        self.assertEqual(report["summary"]["reclaimable"], 0)
        self.assertEqual(report["review_proposals"], [])

    def test_container_adapter_unavailable_blocks_reclamation(self):
        entry = make_entry(
            path="docker-volume:example-unavailable",
            policy_state="RECLAIMABLE",
            owner="UNKNOWN",
            justification="container adapter unavailable; ownership unconfirmed",
        )
        entry["review"]["note"] = "adapter=container; unavailable at review time"
        code, report = self._load(entry)
        self.assertEqual(code, vri.EXIT_OK)
        result = report["entries"][0]
        self.assertEqual(result["effective_state"], "REVIEW_REQUIRED")
        self.assertEqual(report["summary"]["reclaimable"], 0)
        self.assertEqual(report["exclusions"], [])

    def test_unknown_owner_reclaimed_claim_downgraded(self):
        entry = make_entry(policy_state="RECLAIMED", owner="UNKNOWN")
        code, report = self._load(entry)
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(report["entries"][0]["effective_state"], "REVIEW_REQUIRED")
        self.assertEqual(report["summary"]["reclaimed"], 0)


class ReadOnlyTests(unittest.TestCase):
    """The producer must not mutate any file it inspects."""

    def test_load_does_not_mutate_inventory(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        dirpath = Path(tmp.name)
        doc = make_doc()
        path = write_inventory(dirpath, doc)
        before = path.read_bytes()
        approval = dirpath / "retention-inventory.approval.sha256"
        approval_before = approval.read_bytes()
        code, _, _ = run_cli(path)
        self.assertEqual(code, vri.EXIT_OK)
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(approval.read_bytes(), approval_before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
