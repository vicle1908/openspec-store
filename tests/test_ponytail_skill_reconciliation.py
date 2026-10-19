"""Unit tests for reconcile-ponytail-agent-skills in platform/openspec-store.

Covers:
1. Shared 13-case canonical fixture matrix (F01-F13) against classify_refresh()
   in scripts/workstation-daily-update.sh via /bin/bash.
2. YAML frontmatter description decoding (>, >-, >+, |, |-, |+, plain, quoted),
   60-char internal vs 1,024-byte vendor budget checks, and exact byte counts
   (142-371 raw bytes / 141-370 trimmed bytes) on the 6 Ponytail SKILL.md files.
3. Non-destructive Hermes user-scope symlink reconciliation in tmp_path.
4. Snapshot lifecycle (--bootstrap-snapshot, --accept-refresh rotation from
   current -> previous, --check drift/tampering detection, and
   --recover-from-snapshot partial-mutation restoration) in tmp_path without
   mutating live workstation files.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

STORE_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = STORE_ROOT / "scripts"
DAILY_UPDATE_SH = SCRIPTS_DIR / "workstation-daily-update.sh"
SYNC_SCRIPT = SCRIPTS_DIR / "sync-workspace-agent-skills.py"
LIVE_SKILLS_DIR = STORE_ROOT.parent.parent / ".agents" / "skills"


def _load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_workspace_agent_skills", SYNC_SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sync_workspace_agent_skills"] = mod
    spec.loader.exec_module(mod)
    return mod


sync_mod = _load_sync_module()


CANONICAL_FIXTURES = [
    (
        "F01_v172_project_all_current",
        "Checking 6 skill(s)…\n✓ All project skills are up to date",
        "",
        0,
        {"drift": 0, "refreshed": 0, "already_current": 1, "path_ambiguous": 0, "failed": 0},
    ),
    (
        "F02_global_all_current",
        "Checking 4 skill(s)…\n✓ All global skills are up to date",
        "",
        0,
        {"drift": 0, "refreshed": 0, "already_current": 1, "path_ambiguous": 0, "failed": 0},
    ),
    (
        "F03_v172_per_skill_plus_summary",
        "  ✓ Updated ponytail\n  ✓ Updated ponytail-help\n✓ Updated 2 skill(s)",
        "",
        0,
        {"drift": 1, "refreshed": 2, "already_current": 0, "path_ambiguous": 0, "failed": 0},
    ),
    (
        "F04_explicit_zero_updated",
        "Updated 0 skill(s)\n✓ All project skills are up to date",
        "",
        0,
        {"drift": 0, "refreshed": 0, "already_current": 1, "path_ambiguous": 0, "failed": 0},
    ),
    (
        "F05_global_found_refreshing_completed",
        "Found 3 global update(s)\nRefreshing 3 skill(s)\n  ✓ Updated a\n  ✓ Updated b\n  ✓ Updated c",
        "",
        0,
        {"drift": 1, "refreshed": 3, "already_current": 0, "path_ambiguous": 0, "failed": 0},
    ),
    (
        "F06_refreshing_without_completion_fails",
        "Found 2 global update(s)\nRefreshing 2 skill(s)",
        "",
        0,
        {"drift": 1, "refreshed": 0, "already_current": 0, "path_ambiguous": 0, "failed": 1},
    ),
    (
        "F07_ambiguous_only_no_current",
        'Checking 1 skill(s)…\nWarning: Multiple current paths match "docfork-docs" — skipping them.',
        "",
        0,
        {"drift": 0, "refreshed": 0, "already_current": 0, "path_ambiguous": 1, "failed": 0},
    ),
    (
        "F08_ambiguous_with_explicit_current",
        'Checking 60 skill(s)…\nWarning: Multiple current paths match "docfork-docs" — skipping them.\n✓ All project skills are up to date',
        "",
        0,
        {"drift": 0, "refreshed": 0, "already_current": 1, "path_ambiguous": 1, "failed": 0},
    ),
    (
        "F09_numeric_summary_with_counts",
        "42 skills updated\n3 skills already current\n1 skills drifted\n2 path ambiguous",
        "",
        0,
        {"drift": 1, "refreshed": 42, "already_current": 3, "path_ambiguous": 2, "failed": 0},
    ),
    (
        "F10_partial_mutation_then_failure",
        "  ✓ Updated ponytail\nError: clone failed for repo",
        "",
        1,
        {"drift": 1, "refreshed": 1, "already_current": 0, "path_ambiguous": 0, "failed": 1},
    ),
    (
        "F11_stderr_fatal_error",
        "Checking 6 skill(s)…\n",
        "Error: EACCES: permission denied, open '/Users/androidteam/Developer/skills-lock.json'\n",
        1,
        {"drift": 0, "refreshed": 0, "already_current": 0, "path_ambiguous": 0, "failed": 1},
    ),
    (
        "F12_timeout_124",
        "Checking 60 skill(s)…\nRefreshing 1 skill(s)",
        "",
        124,
        {"drift": 1, "refreshed": 0, "already_current": 0, "path_ambiguous": 0, "failed": 1},
    ),
    (
        "F13_unrecognized_exit_zero",
        "something unexpected happened",
        "",
        0,
        {"drift": 0, "refreshed": 0, "already_current": 0, "path_ambiguous": 0, "failed": 1},
    ),
]


class TestClassifyRefreshBashFixtures(unittest.TestCase):
    """Verify all 13 canonical fixtures (F01-F13) in /bin/bash."""

    def _run_classify_refresh(self, stdout: str, stderr: str, rc: int) -> dict[str, int]:
        combined = f"{stdout}\n{stderr}" if stderr else stdout
        cmd = [
            "/bin/bash",
            "-c",
            'source "$1" && clean="$(printf "%s" "$2" | strip_ansi)" && classify_refresh "$clean" "$3"',
            "bash",
            str(DAILY_UPDATE_SH),
            combined,
            str(rc),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        line = proc.stdout.strip()
        parsed: dict[str, int] = {}
        for token in line.split():
            k, v = token.split("=", 1)
            parsed[k] = int(v)
        return parsed

    def test_all_13_canonical_fixtures(self):
        for name, stdout, stderr, rc, expected in CANONICAL_FIXTURES:
            with self.subTest(fixture=name):
                actual = self._run_classify_refresh(stdout, stderr, rc)
                self.assertEqual(actual, expected, f"{name}: got {actual}, expected {expected}")


class TestYamlFrontmatterAndPonytailBudgets(unittest.TestCase):
    """Verify YAML block scalar decoding and Ponytail 142-371 byte measurements."""

    def test_real_ponytail_skill_md_byte_measurements(self):
        expected_raw = {
            "ponytail": 367,
            "ponytail-audit": 347,
            "ponytail-debt": 202,
            "ponytail-gain": 161,
            "ponytail-help": 142,
            "ponytail-review": 371,
        }
        expected_trimmed = {k: v - 1 for k, v in expected_raw.items()}

        raw_lengths = []
        trimmed_lengths = []
        for slug, exp_raw in expected_raw.items():
            skill_md = LIVE_SKILLS_DIR / slug / "SKILL.md"
            self.assertTrue(skill_md.is_file(), f"Missing {skill_md}")
            metrics = sync_mod.measure_description_bytes(skill_md)
            self.assertEqual(metrics["raw_bytes"], exp_raw, f"{slug} raw_bytes mismatch")
            self.assertEqual(
                metrics["trimmed_bytes"], expected_trimmed[slug], f"{slug} trimmed_bytes mismatch"
            )
            self.assertTrue(sync_mod.check_description_budget(skill_md, is_vendor=True))
            raw_lengths.append(metrics["raw_bytes"])
            trimmed_lengths.append(metrics["trimmed_bytes"])

        self.assertEqual(min(raw_lengths), 142)
        self.assertEqual(max(raw_lengths), 371)
        self.assertEqual(min(trimmed_lengths), 141)
        self.assertEqual(max(trimmed_lengths), 370)

    def test_block_scalar_variants_and_budget_helper(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # Folded strip (>-)
            p_strip = tmp_path / "SKILL_strip.md"
            p_strip.write_text(
                "---\nname: test\ndescription: >-\n  first line\n  second line\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(
                sync_mod.decode_frontmatter_description(p_strip), "first line second line"
            )
            self.assertTrue(sync_mod.check_description_budget(p_strip, is_vendor=False))

            # Literal clip (|)
            p_lit = tmp_path / "SKILL_lit.md"
            p_lit.write_text(
                "---\nname: test\ndescription: |\n  line one\n  line two\n---\n",
                encoding="utf-8",
            )
            self.assertEqual(
                sync_mod.decode_frontmatter_description(p_lit), "line one\nline two\n"
            )

            # Internal skill > 60 chars fails internal budget but passes vendor budget <= 1024B
            p_mid = tmp_path / "SKILL_mid.md"
            p_mid.write_text(
                f"---\nname: test\ndescription: {'a' * 120}\n---\n",
                encoding="utf-8",
            )
            self.assertFalse(sync_mod.check_description_budget(p_mid, is_vendor=False))
            self.assertTrue(sync_mod.check_description_budget(p_mid, is_vendor=True))

            # Vendor skill > 1024 bytes fails both budgets and malformed_entries
            skill_dir = tmp_path / "oversized-skill"
            skill_dir.mkdir()
            p_over = skill_dir / "SKILL.md"
            p_over.write_text(
                f"---\nname: oversized-skill\ndescription: >\n  {'x' * 1050}\n---\n",
                encoding="utf-8",
            )
            self.assertFalse(sync_mod.check_description_budget(p_over, is_vendor=True))
            findings = sync_mod.malformed_entries(tmp_path)
            self.assertEqual(len(findings), 1)
            self.assertIn("oversized-skill:description-exceeds-1024-bytes", findings[0])


class TestHermesAndSnapshotLifecycleInTmpPath(unittest.TestCase):
    """Verify Hermes symlink reconciliation, snapshots, drift detection, and recovery in tmp_path."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.workspace = self.root / "workspace"
        self.store = self.root / "store"
        self.home = self.root / "home"

        (self.workspace / ".agents" / "skills").mkdir(parents=True)
        (self.workspace / ".claude" / "skills").mkdir(parents=True)
        (self.workspace / ".claude" / "commands" / "opsx").mkdir(parents=True)
        (self.workspace / ".hermes" / "skills").mkdir(parents=True)
        (self.workspace / ".codex" / "skills" / ".system").mkdir(parents=True)

        (self.store / ".agents" / "skills" / "openspec-explore").mkdir(parents=True)
        (self.store / ".agents" / "skills" / "openspec-explore" / "SKILL.md").write_text(
            "---\nname: openspec-explore\ndescription: Use to explore OpenSpec ideas.\n---\n",
            encoding="utf-8",
        )
        (self.store / ".claude" / "skills" / "openspec-explore").mkdir(parents=True)
        (self.store / ".claude" / "skills" / "openspec-explore" / "SKILL.md").write_text(
            "---\nname: openspec-explore\ndescription: Use to explore OpenSpec ideas.\n---\n",
            encoding="utf-8",
        )
        (self.store / ".claude" / "commands" / "opsx").mkdir(parents=True)
        (self.store / ".claude" / "commands" / "opsx" / "explore.md").write_text(
            "# Explore\n", encoding="utf-8"
        )
        (self.store / "config").mkdir(parents=True)

        # Populate the 6 Ponytail skills + 1 extra workspace skill
        lock_skills = {}
        for slug in sync_mod.PONYTAIL_SKILLS:
            sdir = self.workspace / ".agents" / "skills" / slug
            sdir.mkdir(parents=True)
            real_md = LIVE_SKILLS_DIR / slug / "SKILL.md"
            if real_md.is_file():
                (sdir / "SKILL.md").write_bytes(real_md.read_bytes())
            else:
                (sdir / "SKILL.md").write_text(
                    f"---\nname: {slug}\ndescription: >\n  Ponytail skill {slug}.\n---\n",
                    encoding="utf-8",
                )
            lock_skills[slug] = {
                "source": "DietrichGebert/ponytail",
                "sourceType": "github",
                "skillPath": f"skills/{slug}/SKILL.md",
                "computedHash": hashlib.sha256((sdir / "SKILL.md").read_bytes()).hexdigest(),
            }

        # Extra workspace skill not in hermes manifest
        extra_dir = self.workspace / ".agents" / "skills" / "extra-ws-skill"
        extra_dir.mkdir(parents=True)
        (extra_dir / "SKILL.md").write_text(
            "---\nname: extra-ws-skill\ndescription: Use for extra workspace checks.\n---\n",
            encoding="utf-8",
        )

        # Untracked local skill (not in skills-lock.json)
        untracked_dir = self.workspace / ".agents" / "skills" / "local-untracked"
        untracked_dir.mkdir(parents=True)
        (untracked_dir / "SKILL.md").write_text(
            "---\nname: local-untracked\ndescription: Use for local untracked work.\n---\n",
            encoding="utf-8",
        )

        (self.workspace / "skills-lock.json").write_text(
            json.dumps({"version": 1, "skills": lock_skills}, indent=2) + "\n",
            encoding="utf-8",
        )

        manifest_body = "\n".join(sync_mod.PONYTAIL_SKILLS) + "\n"
        (self.store / "config" / "codex-user-skill-manifest.txt").write_text(
            manifest_body, encoding="utf-8"
        )
        (self.store / "config" / "claude-user-skill-manifest.txt").write_text(
            manifest_body, encoding="utf-8"
        )
        (self.store / "config" / "hermes-user-skill-manifest.txt").write_text(
            manifest_body, encoding="utf-8"
        )

    def tearDown(self):
        self._tmp.cleanup()

    def _cli_args(self, *extra: str) -> list[str]:
        return [
            "--workspace-root",
            str(self.workspace),
            "--store-root",
            str(self.store),
            "--home-dir",
            str(self.home),
            *extra,
        ]

    def test_hermes_symlink_reconciliation_and_non_destructive_preservation(self):
        hermes_dir = self.home / ".hermes" / "skills"
        hermes_dir.mkdir(parents=True)

        # 1. Native Hermes directory (outside workspace) must be preserved
        native_dir = hermes_dir / "autonomous-ai-agents"
        native_dir.mkdir()
        (native_dir / "SKILL.md").write_text("---\nname: autonomous-ai-agents\ndescription: x\n---\n")

        # 2. Pre-existing resolvable symlink to WORKSPACE_AGENTS NOT in hermes manifest must be preserved
        unlisted_link = hermes_dir / "extra-ws-skill"
        unlisted_link.symlink_to(self.workspace / ".agents" / "skills" / "extra-ws-skill")

        # 3. Broken symlink to WORKSPACE_AGENTS must be removed
        broken_link = hermes_dir / "dead-ws-skill"
        broken_link.symlink_to(self.workspace / ".agents" / "skills" / "nonexistent")

        rc = sync_mod.main(self._cli_args())
        self.assertEqual(rc, 0)

        for slug in sync_mod.PONYTAIL_SKILLS:
            link = hermes_dir / slug
            self.assertTrue(link.is_symlink(), f"Expected symlink at {link}")
            self.assertEqual(
                Path(os.path.realpath(link)),
                (self.workspace / ".agents" / "skills" / slug).resolve(),
            )

        self.assertTrue(native_dir.is_dir() and not native_dir.is_symlink())
        self.assertTrue(unlisted_link.is_symlink() and unlisted_link.exists())
        self.assertFalse(broken_link.exists() or broken_link.is_symlink())

        # --check must pass with rc=0
        self.assertEqual(sync_mod.main(self._cli_args("--check")), 0)

        # Removing ponytail-gain from hermes-user-skill-manifest.txt prunes ponytail-gain
        # (because it was tracked in .hermes-managed-links.txt) while still preserving extra-ws-skill
        reduced = [s for s in sync_mod.PONYTAIL_SKILLS if s != "ponytail-gain"]
        (self.store / "config" / "hermes-user-skill-manifest.txt").write_text(
            "\n".join(reduced) + "\n", encoding="utf-8"
        )
        self.assertEqual(sync_mod.main(self._cli_args()), 0)
        self.assertFalse((hermes_dir / "ponytail-gain").is_symlink())
        self.assertTrue(unlisted_link.is_symlink())

    def test_bootstrap_accept_refresh_drift_detection_and_recovery(self):
        # First reconcile symlinks
        self.assertEqual(sync_mod.main(self._cli_args()), 0)

        # 1. Bootstrap snapshot
        self.assertEqual(sync_mod.main(self._cli_args("--bootstrap-snapshot")), 0)
        snap_root = self.workspace / ".agents" / ".skill-snapshots"
        current_manifest_path = snap_root / "current" / "manifest.json"
        previous_manifest_path = snap_root / "previous" / "manifest.json"
        replica_lock = self.workspace / ".agents" / "skills-lock.json"

        self.assertTrue(current_manifest_path.is_file())
        self.assertTrue(previous_manifest_path.is_file())
        self.assertTrue(replica_lock.is_file())
        self.assertEqual(
            replica_lock.read_bytes(), (self.workspace / "skills-lock.json").read_bytes()
        )

        m_data = json.loads(current_manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(m_data["skills"]["ponytail"]["source_revision"], "unknown")
        self.assertFalse(m_data["skills"]["ponytail"]["upstream_verified"])
        self.assertIn(m_data["skills"]["ponytail"]["description_bytes"], range(142, 372))

        # --check passes when snapshot and replica match live state
        self.assertEqual(sync_mod.main(self._cli_args("--check")), 0)

        # 2. Simulate manual CLI update (updates root skills-lock.json + ponytail/SKILL.md)
        ponytail_md = self.workspace / ".agents" / "skills" / "ponytail" / "SKILL.md"
        original_ponytail_bytes = ponytail_md.read_bytes()
        updated_ponytail_bytes = original_ponytail_bytes + b"\n# Updated upstream line\n"
        ponytail_md.write_bytes(updated_ponytail_bytes)

        lock_data = json.loads((self.workspace / "skills-lock.json").read_text(encoding="utf-8"))
        old_hash = lock_data["skills"]["ponytail"]["computedHash"]
        new_hash = hashlib.sha256(updated_ponytail_bytes).hexdigest()
        lock_data["skills"]["ponytail"]["computedHash"] = new_hash
        (self.workspace / "skills-lock.json").write_text(
            json.dumps(lock_data, indent=2) + "\n", encoding="utf-8"
        )

        # Before --accept-refresh, --check MUST detect unaccepted manual CLI drift and fail
        self.assertEqual(sync_mod.main(self._cli_args("--check")), 1)
        # Default link-sync must NOT overwrite .agents/skills-lock.json
        self.assertEqual(sync_mod.main(self._cli_args()), 0)
        self.assertNotEqual(
            replica_lock.read_bytes(), (self.workspace / "skills-lock.json").read_bytes()
        )

        # 3. Run --accept-refresh: rotates current -> previous, writes new current, updates replica
        self.assertEqual(sync_mod.main(self._cli_args("--accept-refresh")), 0)
        prev_m = json.loads(previous_manifest_path.read_text(encoding="utf-8"))
        curr_m = json.loads(current_manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(prev_m["skills"]["ponytail"]["computedHash"], old_hash)
        self.assertEqual(curr_m["skills"]["ponytail"]["computedHash"], new_hash)
        self.assertEqual(
            replica_lock.read_bytes(), (self.workspace / "skills-lock.json").read_bytes()
        )
        self.assertEqual(sync_mod.main(self._cli_args("--check")), 0)

        # 4. Simulate partial mutation / corrupt refresh (tamper with ponytail-debt & lockfile,
        # while modifying untracked local-untracked skill)
        debt_md = self.workspace / ".agents" / "skills" / "ponytail-debt" / "SKILL.md"
        good_debt_bytes = debt_md.read_bytes()
        debt_md.write_text("corrupted without frontmatter", encoding="utf-8")

        untracked_md = self.workspace / ".agents" / "skills" / "local-untracked" / "SKILL.md"
        untracked_custom = "---\nname: local-untracked\ndescription: Local edit preserved.\n---\n"
        untracked_md.write_text(untracked_custom, encoding="utf-8")

        # --accept-refresh must fail closed and refuse to update replica
        self.assertEqual(sync_mod.main(self._cli_args("--accept-refresh")), 1)
        self.assertEqual(sync_mod.main(self._cli_args("--check")), 1)

        # 5. --recover-from-snapshot restores ponytail-debt to good_debt_bytes
        # while leaving local-untracked untouched!
        self.assertEqual(sync_mod.main(self._cli_args("--recover-from-snapshot")), 0)
        self.assertEqual(debt_md.read_bytes(), good_debt_bytes)
        self.assertEqual(untracked_md.read_text(encoding="utf-8"), untracked_custom)
        self.assertEqual(sync_mod.main(self._cli_args("--check")), 0)

        # 6. Surface check rejects agent/skills and data/skills while allowing data/updates
        (self.workspace / "data" / "updates").mkdir(parents=True)
        (self.workspace / "data" / "updates" / "2026-10-19.json").write_text("{}", encoding="utf-8")
        self.assertEqual(sync_mod.check_workspace_agent_surface(self.workspace), [])

        (self.workspace / "agent" / "skills").mkdir(parents=True)
        (self.workspace / "data" / "skills").mkdir(parents=True)
        violations = sync_mod.check_workspace_agent_surface(self.workspace)
        self.assertEqual(violations, ["agent", "data/skills"])
        self.assertEqual(sync_mod.main(self._cli_args("--check")), 1)


if __name__ == "__main__":
    unittest.main()
