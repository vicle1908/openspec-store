"""Focused tests for portable-mac-development-workstation Slice C.

Covers:
1. Fail-closed Notion knowledge synchronization (scripts/knowledge-refresh/sync-notion-knowledge.sh):
   - Strict read-only guarantee of --dry-run (zero file mutations, no log touching, no manifest creation/mutation).
   - Dynamic home directory redaction (/Users/[^/]+/ to ~/) eliminating user literals.
   - Fail-closed secret sanitization and residual scanning against private keys and raw tokens.
   - Verified Notion API write receipt requirement (exit 0 and non-empty page ID) before advancing manifest SHA.
   - Offline resilience: failed writes retain previous SHA for automatic retry; unchanged docs trigger fresh_noop.
   - Parameterization via environment variables (NOTION_KNOWLEDGE_ROOT_ID and section IDs).
2. External Execution Packet generator and validator (scripts/create-external-execution-packet.py):
   - Packet generation with required fields (target root, source commit, command, timestamps, counts, exclusions).
   - Validation of conforming packets and rejection of missing required fields or invalid timestamps.
   - Scope authorization gate: unauthorized packets fail closed and cannot be COMPLETED.
   - Mandatory exclusion verification (secrets, private keys, Docker volumes).
   - Value-blind integrity check rejecting unredacted credentials.
3. Unified read-only workstation verification runner (scripts/verify-workstation-toolchain.py):
   - Read-only execution producing a single JSON evidence bundle with SHA-256 hash.
   - Combined coverage of inventory reconciliation, preflight, templates, ports, and Notion sanitization.
   - Clean audit of config/launchd templates with zero unresolved tags.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
CONFIG_DIR = REPO_ROOT / "config"
SYNC_SCRIPT = SCRIPTS_DIR / "knowledge-refresh" / "sync-notion-knowledge.sh"


def _load_module(mod_name: str, script_name: str):
    path = SCRIPTS_DIR / script_name
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


eep_mod = _load_module("create_external_execution_packet", "create-external-execution-packet.py")
verify_mod = _load_module("verify_workstation_toolchain", "verify-workstation-toolchain.py")


class TestNotionKnowledgeSync(unittest.TestCase):
    """Test suite for scripts/knowledge-refresh/sync-notion-knowledge.sh."""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="slice_c_sync_test_")
        self.tmp_path = Path(self.tmp_dir)
        self.state_dir = self.tmp_path / ".knowledge-refresh"
        self.manifest_file = self.state_dir / "notion-sync-manifest.json"
        self.log_file = self.state_dir / "notion-sync.log"
        self.wiki_dir = self.tmp_path / "wiki" / "concepts"
        self.wiki_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _run_sync_cmd(self, args: list[str], extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["WORKSPACE_ROOT"] = str(self.tmp_path)
        env["STATE_DIR"] = str(self.state_dir)
        env["MANIFEST_FILE"] = str(self.manifest_file)
        env["LOG_FILE"] = str(self.log_file)
        env["PACING_DELAY_SEC"] = "0"
        if extra_env:
            env.update(extra_env)

        cmd = [str(SYNC_SCRIPT)] + args
        return subprocess.run(cmd, env=env, capture_output=True, text=True)

    def test_dry_run_is_strictly_read_only(self):
        """--dry-run MUST NOT touch log file, invoke mkdir -p, or mutate manifest."""
        res = self._run_sync_cmd(["--dry-run"])
        self.assertEqual(res.returncode, 0, f"Dry-run failed: {res.stderr}")

        # Target state dir should not even exist
        self.assertFalse(self.state_dir.exists(), "STATE_DIR was created during --dry-run")
        self.assertFalse(self.log_file.exists(), "LOG_FILE was created during --dry-run")
        self.assertFalse(self.manifest_file.exists(), "MANIFEST_FILE was created during --dry-run")

        # Zero files created in entire temp root
        created_files = list(self.tmp_path.glob("**/*"))
        # Only self.wiki_dir hierarchy should exist
        non_wiki_files = [f for f in created_files if not str(f).startswith(str(self.tmp_path / "wiki"))]
        self.assertEqual(len(non_wiki_files), 0, f"Found unexpected files created: {non_wiki_files}")

    def test_dry_run_does_not_mutate_existing_manifest(self):
        """--dry-run MUST NOT alter existing manifest or mutate section IDs."""
        self.state_dir.mkdir(parents=True, exist_ok=True)
        initial_manifest = {
            "version": "1.0",
            "knowledge_root_id": "test-root-uuid",
            "sections": {"concepts": "sec-concepts-original"},
            "documents": {},
            "last_synced_at": None,
        }
        self.manifest_file.write_text(json.dumps(initial_manifest, indent=2), encoding="utf-8")
        before_content = self.manifest_file.read_text(encoding="utf-8")

        res = self._run_sync_cmd(["--dry-run"])
        self.assertEqual(res.returncode, 0)
        after_content = self.manifest_file.read_text(encoding="utf-8")
        self.assertEqual(before_content, after_content, "Manifest content changed during --dry-run")

    def test_dynamic_home_redaction(self):
        """Dynamic regex s#/Users/[^/]+/#~/#g replaces arbitrary usernames with ~/."""
        test_cases = (
            "Path: /Users/androidteam/Developer/repo/main.go\n"
            "Home: /Users/custom_user/.zshrc\n"
            "Work: /Users/some_dev_99/Developer/project\n"
            "Prefix: /Users/isolated_user\n"
        )
        bash_cmd = f'source "{SYNC_SCRIPT}" && printf "%s" "{test_cases}" | sanitize_content'
        proc = subprocess.run(["bash", "-c", bash_cmd], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        out = proc.stdout

        self.assertNotIn("androidteam", out)
        self.assertNotIn("custom_user", out)
        self.assertNotIn("some_dev_99", out)
        self.assertNotIn("isolated_user", out)
        self.assertIn("~/Developer/repo/main.go", out)
        self.assertIn("~/.zshrc", out)
        self.assertIn("~/Developer/project", out)
        self.assertIn("~", out)

    def test_secret_redaction_and_allowlist(self):
        """Sanitization redacts credentials while allowing explicitly allowlisted terms."""
        secret_payload = (
            "OPENAI_API_KEY=sk-test12345678901234567890\n"
            "GITHUB_TOKEN=\"ghp_12345678901234567890\"\n"
            "database_url=postgres://user:secretpass123@localhost:5432/db\n"
            "api_key=your_api_key\n"
        )
        bash_cmd = f'source "{SYNC_SCRIPT}" && printf "%s" "{secret_payload}" | sanitize_content'
        proc = subprocess.run(["bash", "-c", bash_cmd], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        out = proc.stdout

        self.assertNotIn("sk-test12345678901234567890", out)
        self.assertNotIn("ghp_12345678901234567890", out)
        self.assertNotIn("secretpass123", out)
        self.assertIn("OPENAI_API_KEY=REDACTED", out)
        self.assertIn("GITHUB_TOKEN=REDACTED", out)
        self.assertIn("postgres://REDACTED@localhost:5432/db", out)

    def test_residual_secret_scan_fails_closed(self):
        """Residual secret scanner MUST reject unredacted tokens and private keys."""
        # 1. Private key detection
        bad_key = "-----BEGIN " + "RSA PRIVATE KEY-----\\nKEYDATA\\n-----END RSA PRIVATE KEY-----"
        cmd_key = f'source "{SYNC_SCRIPT}" && scan_residual_secrets "{bad_key}"'
        proc_key = subprocess.run(["bash", "-c", cmd_key], capture_output=True, text=True)
        self.assertNotEqual(proc_key.returncode, 0, "Private key was not caught by residual scanner")

        # 2. Raw unredacted token detection
        bad_token = "Here is raw token: sk-ant-api03-abcdef12345678901234567890"
        cmd_token = f'source "{SYNC_SCRIPT}" && scan_residual_secrets "{bad_token}"'
        proc_token = subprocess.run(["bash", "-c", cmd_token], capture_output=True, text=True)
        self.assertNotEqual(proc_token.returncode, 0, "Raw API key token was not caught by residual scanner")

        # 3. Clean content passes
        clean = "# Curated Knowledge\nOPENAI_API_KEY=REDACTED\n`api_key=your_api_key`\n"
        cmd_clean = f'source "{SYNC_SCRIPT}" && scan_residual_secrets "{clean}"'
        proc_clean = subprocess.run(["bash", "-c", cmd_clean], capture_output=True, text=True)
        self.assertEqual(proc_clean.returncode, 0, f"Clean content failed residual scanner: {proc_clean.stderr}")

    def test_write_receipt_required_before_manifest_advances(self):
        """Manifest SHA-256 MUST ONLY advance when ntn returns exit 0 with valid JSON page ID."""
        bin_dir = self.tmp_path / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        mock_ntn = bin_dir / "ntn"

        # Mock ntn failing on create
        mock_ntn.write_text(
            "#!/usr/bin/env bash\n"
            "if [[ \"$1\" == \"pages\" && \"$2\" == \"create\" ]]; then\n"
            "  echo 'Error: Connection timeout' >&2\n"
            "  exit 1\n"
            "fi\n",
            encoding="utf-8",
        )
        mock_ntn.chmod(0o755)

        test_doc = self.tmp_path / "wiki" / "concepts" / "test.md"
        test_doc.write_text("# Test Document\nInitial content\n", encoding="utf-8")

        self.state_dir.mkdir(parents=True, exist_ok=True)
        initial_manifest = {
            "version": "1.0",
            "knowledge_root_id": "test-root",
            "sections": {"concepts": "sec-concepts"},
            "documents": {},
            "last_synced_at": None,
        }
        self.manifest_file.write_text(json.dumps(initial_manifest, indent=2), encoding="utf-8")

        bash_cmd = (
            f'export PATH="{bin_dir}:$PATH"\n'
            f'export NTN_BIN="{mock_ntn}"\n'
            f'export WORKSPACE_ROOT="{self.tmp_path}"\n'
            f'export STATE_DIR="{self.state_dir}"\n'
            f'export MANIFEST_FILE="{self.manifest_file}"\n'
            f'export LOG_FILE="{self.log_file}"\n'
            f'export PACING_DELAY_SEC=0\n'
            f'source "{SYNC_SCRIPT}"\n'
            f'sync_document "wiki/concepts/test.md" "concepts"\n'
        )
        proc = subprocess.run(["bash", "-c", bash_cmd], capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0, "sync_document should fail when ntn fails")

        # Manifest must NOT have recorded the document
        data = json.loads(self.manifest_file.read_text(encoding="utf-8"))
        self.assertNotIn("wiki/concepts/test.md", data.get("documents", {}))

    def test_offline_resilience_and_successful_retry(self):
        """Failed write retains previous state; subsequent successful run advances SHA and enables fresh_noop."""
        bin_dir = self.tmp_path / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        mock_ntn = bin_dir / "ntn"

        test_doc = self.tmp_path / "wiki" / "concepts" / "retry.md"
        test_doc.write_text("# Retry Test\nSome content\n", encoding="utf-8")

        self.state_dir.mkdir(parents=True, exist_ok=True)
        initial_manifest = {
            "version": "1.0",
            "knowledge_root_id": "test-root",
            "sections": {"concepts": "sec-concepts"},
            "documents": {
                "wiki/concepts/retry.md": {
                    "page_id": "page-orig",
                    "sha256": "old-sha-digest",
                    "title": "Retry Test",
                    "last_synced": "2026-10-08T00:00:00Z",
                }
            },
            "last_synced_at": None,
        }
        self.manifest_file.write_text(json.dumps(initial_manifest, indent=2), encoding="utf-8")

        # 1. First run: ntn edit fails (network outage)
        mock_ntn.write_text(
            "#!/usr/bin/env bash\n"
            "echo 'Notion API 503 Service Unavailable' >&2\n"
            "exit 1\n",
            encoding="utf-8",
        )
        mock_ntn.chmod(0o755)

        base_env = (
            f'export PATH="{bin_dir}:$PATH"\n'
            f'export NTN_BIN="{mock_ntn}"\n'
            f'export WORKSPACE_ROOT="{self.tmp_path}"\n'
            f'export STATE_DIR="{self.state_dir}"\n'
            f'export MANIFEST_FILE="{self.manifest_file}"\n'
            f'export LOG_FILE="{self.log_file}"\n'
            f'export PACING_DELAY_SEC=0\n'
            f'source "{SYNC_SCRIPT}"\n'
        )

        proc1 = subprocess.run(["bash", "-c", base_env + 'sync_document "wiki/concepts/retry.md" "concepts"\n'], capture_output=True, text=True)
        self.assertNotEqual(proc1.returncode, 0)

        # Confirm old SHA retained
        data1 = json.loads(self.manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(data1["documents"]["wiki/concepts/retry.md"]["sha256"], "old-sha-digest")

        # 2. Second run: connectivity restored; ntn edit succeeds returning receipt JSON
        mock_ntn.write_text(
            "#!/usr/bin/env bash\n"
            "echo '{\"id\": \"page-orig\", \"object\": \"page\"}'\n"
            "exit 0\n",
            encoding="utf-8",
        )
        mock_ntn.chmod(0o755)

        proc2 = subprocess.run(["bash", "-c", base_env + 'sync_document "wiki/concepts/retry.md" "concepts"\n'], capture_output=True, text=True)
        self.assertEqual(proc2.returncode, 0, f"Retry sync failed: {proc2.stderr}")

        data2 = json.loads(self.manifest_file.read_text(encoding="utf-8"))
        new_sha = data2["documents"]["wiki/concepts/retry.md"]["sha256"]
        self.assertNotEqual(new_sha, "old-sha-digest")

        # 3. Third run: unchanged document triggers fresh_noop without calling ntn edit
        proc3 = subprocess.run(["bash", "-c", base_env + 'sync_document "wiki/concepts/retry.md" "concepts"\n'], capture_output=True, text=True)
        self.assertEqual(proc3.returncode, 0)
        self.assertIn("fresh_noop", proc3.stderr)

    def test_environment_variable_parameterization(self):
        """KNOWLEDGE_ROOT_ID and section page IDs can be supplied via environment."""
        extra_env = {
            "NOTION_KNOWLEDGE_ROOT_ID": "custom-root-uuid-42",
            "NOTION_SECTION_CONCEPTS_ID": "custom-concepts-uuid-1",
            "NOTION_SECTION_ENTITIES_ID": "custom-entities-uuid-2",
            "NOTION_SECTION_SPECS_ID": "custom-specs-uuid-3",
            "NOTION_SECTION_FRESHNESS_ID": "custom-freshness-uuid-4",
        }
        res = self._run_sync_cmd(["--dry-run"], extra_env=extra_env)
        self.assertEqual(res.returncode, 0, f"Dry-run with env vars failed: {res.stderr}")


class TestExternalExecutionPacket(unittest.TestCase):
    """Test suite for scripts/create-external-execution-packet.py."""

    def test_create_and_validate_conforming_packet(self):
        """Conforming execution packet generates cleanly and passes schema validation."""
        packet = eep_mod.create_packet(
            target_root="/opt/homebrew",
            source_commit="abcdef0123456789abcdef0123456789abcdef01",
            command="npm install --global @openai/codex@0.9.8",
            exit_code=0,
            item_counts={"inspected": 1, "modified": 1, "created": 0, "retained": 0},
            source_preserved=True,
            collision_detected=False,
            readback_verified=True,
            readback_status="PASSED",
            active_version="0.9.8",
            scope_authorized=True,
            approved_by="operator",
            approval_token_or_reason="Workstation normalization plan",
            target_root_approved=True,
        )

        valid, errors = eep_mod.validate_packet(packet)
        self.assertTrue(valid, f"Conforming packet failed validation: {errors}")
        self.assertEqual(packet["status"], "COMPLETED")
        self.assertEqual(packet["schema_version"], "1.0")
        self.assertIn(".env", packet["exclusions"])
        self.assertIn("omniroute_data", packet["exclusions"])

    def test_missing_scope_authorization_fails_closed(self):
        """Unauthorized packet defaults to BLOCKED; claiming COMPLETED without authorization is rejected."""
        # 1. Un-authorized packet defaults to BLOCKED
        blocked_packet = eep_mod.create_packet(
            target_root="/opt/homebrew",
            command="rm -rf /opt/homebrew/lib/node_modules/shadow-copy",
            scope_authorized=False,
        )
        self.assertEqual(blocked_packet["status"], "BLOCKED")
        valid, _ = eep_mod.validate_packet(blocked_packet)
        self.assertTrue(valid, "BLOCKED state should be valid representation of unauthorized packet")

        # 2. Fabricated COMPLETED status without scope authorization must fail validation
        blocked_packet["status"] = "COMPLETED"
        valid, errors = eep_mod.validate_packet(blocked_packet)
        self.assertFalse(valid, "Validation must reject COMPLETED status when scope_authorized is False")
        self.assertTrue(any("scope authorization" in e.lower() for e in errors))

    def test_mandatory_exclusions_enforced(self):
        """Validation MUST reject packets lacking secret or Docker volume exclusions."""
        packet = eep_mod.create_packet(
            target_root="~/.npm-global",
            command="npm prune",
            scope_authorized=True,
            exclusions=["only_temp_files"],  # Missing .env and volumes
        )
        valid, errors = eep_mod.validate_packet(packet)
        self.assertFalse(valid, "Validation must reject packet with inadequate exclusions")
        self.assertTrue(any("secret" in e.lower() or "exclusions" in e.lower() for e in errors))

    def test_value_blind_scan_rejects_credentials_in_packet(self):
        """Packet containing unredacted API key or private key MUST fail validation."""
        packet = eep_mod.create_packet(
            target_root="/opt/homebrew",
            command="curl -H 'Authorization: Bearer sk-ant-api03-abcdef12345678901234567890'",
            scope_authorized=True,
        )
        valid, errors = eep_mod.validate_packet(packet)
        self.assertFalse(valid, "Validation must reject packet containing unredacted API key")
        self.assertTrue(any("unredacted credential" in e.lower() for e in errors))

    def test_cli_create_and_validate_roundtrip(self):
        """CLI create piped to validate over stdin confirms command-line usability."""
        proc_create = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "create-external-execution-packet.py"),
                "create",
                "--target-root",
                "~/.local/bin",
                "--command",
                "ln -sf /opt/homebrew/bin/qodercli ~/.local/bin/qoder",
                "--scope-authorized",
                "--approved-by",
                "operator",
                "--approval-reason",
                "Point-of-risk normalization gate",
                "--target-root-approved",
                "--inspected",
                "1",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_create.returncode, 0, f"CLI create failed: {proc_create.stderr}")

        proc_validate = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "create-external-execution-packet.py"),
                "validate",
                "-",
            ],
            input=proc_create.stdout,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc_validate.returncode, 0, f"CLI validate failed: {proc_validate.stderr}")
        self.assertIn("VALID", proc_validate.stdout)


class TestUnifiedWorkstationVerification(unittest.TestCase):
    """Test suite for scripts/verify-workstation-toolchain.py."""

    def test_unified_verification_produces_evidence_bundle(self):
        """Unified verification runs in read-only mode and outputs structured JSON evidence bundle."""
        bundle = verify_mod.run_workstation_verification()

        self.assertEqual(bundle.get("schema_version"), "1.0")
        self.assertTrue(bundle.get("read_only"), "Evidence bundle must assert read_only: True")
        self.assertIn("evidence_hash", bundle)
        self.assertIn("summary", bundle)
        self.assertIn("checks", bundle)

        summary = bundle["summary"]
        self.assertEqual(summary["total_checks"], 5)
        self.assertIn("inventory_reconciliation", summary["checks_status"])
        self.assertIn("preflight", summary["checks_status"])
        self.assertIn("templates", summary["checks_status"])
        self.assertIn("port_conflicts", summary["checks_status"])
        self.assertIn("notion_sanitization", summary["checks_status"])

    def test_template_audit_validates_concrete_launchd_plists(self):
        """Audited templates in config/launchd must have 0 unresolved {{...}} tags."""
        res = verify_mod.check_templates()
        self.assertIn(res["status"], ("PASS", "WARN"))
        self.assertEqual(res["unresolved_tags_count"], 0, f"Found unresolved tags: {res}")

    def test_notion_sanitization_audit_passes(self):
        """Notion sanitization audit within unified runner confirms all security checks pass."""
        res = verify_mod.check_notion_sanitization()
        self.assertEqual(res["status"], "PASS")
        checks = res.get("checks", {})
        self.assertEqual(checks.get("dynamic_home_redaction"), "PASS")
        self.assertEqual(checks.get("secret_redaction"), "PASS")
        self.assertEqual(checks.get("residual_token_fail_closed"), "PASS")
        self.assertEqual(checks.get("residual_key_fail_closed"), "PASS")
        self.assertEqual(checks.get("residual_allowlist_pass"), "PASS")

    def test_cli_execution_in_read_only_mode(self):
        """Running verify-workstation-toolchain.py via CLI outputs valid JSON and exits 0."""
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "verify-workstation-toolchain.py"), "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, f"Runner failed: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertEqual(data.get("overall_status"), "PASS")
        self.assertTrue(data.get("read_only"))


if __name__ == "__main__":
    unittest.main()
