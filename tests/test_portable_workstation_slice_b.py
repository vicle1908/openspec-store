"""Focused tests for portable-mac-development-workstation Slice B.

Covers:
1. Smoke check suite (scripts/smoke-test-toolchain.py)
   - Per-tool PASS/FAIL status without file mutation.
   - Exit-0 error pattern detection.
   - Already-target outcome and version readback handling.
2. Prune duplicate removal authorization gate (scripts/prune-toolchain-duplicates.py)
   - Five-point verification check (references, processes, manifest reconciliation, dependency integrity, external approval).
   - Fail-closed behavior on any missing check.
   - Dry-run default and approval gating.
3. Shell startup benchmarking harness (scripts/benchmark-shell-startup.sh)
   - Cold and warm repeated runs (min 5).
   - Numerical median and variance computation.
   - JSON report schema validity.
4. Service port collision detector (scripts/check-service-ports.py)
   - Ollama (11434), AgentMemory API (3111), Engine (49134), and Docker inspection.
   - Foreign process detection and quarantine without process termination.
   - Value-blind reporting.
5. AgentMemory health probe (scripts/check-agentmemory-health.py)
   - HTTP GET /agentmemory/health target; strict rejection of root /.
   - Package metadata resolution for pinned iii-engine (0.22.1).
   - Engine mismatch detection and foreign process quarantine.
6. AgentMemory decision seeding (scripts/seed-agentmemory-decisions.py)
   - Dry-run default (WOULD_SEED).
   - Duplicate observation suppression via REST API without SQLite access.
7. LaunchAgent watchdog template (config/launchd/com.agentmemory.server.plist.tmpl)
   - ThrottleInterval: 30 and KeepAlive SuccessfulExit: false.
   - plutil -lint validation on template and rendered concrete paths.
8. Reconciled updater registry and daily update runner
   - Codex npm authority and writer binary.
   - Qoder standalone ~/.qoder/entry dispatcher mapping.
   - Documented PATH precedence in workstation-daily-update.sh.
   - Target prefix divergence suppression.
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
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _load_script_module(mod_name: str, script_name: str):
    path = SCRIPTS_DIR / script_name
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


smoke_mod = _load_script_module("smoke_test_toolchain", "smoke-test-toolchain.py")
prune_mod = _load_script_module("prune_toolchain_duplicates", "prune-toolchain-duplicates.py")
ports_mod = _load_script_module("check_service_ports", "check-service-ports.py")
am_health_mod = _load_script_module("check_agentmemory_health", "check-agentmemory-health.py")
am_seed_mod = _load_script_module("seed_agentmemory_decisions", "seed-agentmemory-decisions.py")
reg_mod = _load_script_module("toolchain_updater_registry", "toolchain_updater_registry.py")
render_mod = _load_script_module("render_workstation_templates", "render-workstation-templates.py")


class TestSmokeTestToolchain(unittest.TestCase):
    def test_clean_smoke_pass_without_mutation(self):
        def mock_runner(cmd: str, timeout: float):
            return 0, "mock-tool version 1.2.3", "", 12.0

        res = smoke_mod.run_tool_smoke_check("mock-tool", stage="pre", runner=mock_runner)
        self.assertEqual(res.status, "PASS")
        self.assertEqual(res.version_readback, "mock-tool version 1.2.3")
        self.assertEqual(res.exit_code, 0)
        self.assertIsNone(res.error)

    def test_nonzero_exit_detected_as_fail(self):
        def mock_runner(cmd: str, timeout: float):
            return 1, "", "Binary not found", 5.0

        res = smoke_mod.run_tool_smoke_check("missing-tool", stage="pre", runner=mock_runner)
        self.assertEqual(res.status, "FAIL")
        self.assertEqual(res.exit_code, 1)
        self.assertIn("Binary not found", res.error)

    def test_zero_exit_with_error_marker_detected_as_fail(self):
        def mock_runner(cmd: str, timeout: float):
            return 0, "error: command failed to initialize runtime", "", 8.0

        res = smoke_mod.run_tool_smoke_check("buggy-tool", stage="pre", runner=mock_runner)
        self.assertEqual(res.status, "FAIL")
        self.assertIn("status code 0 but reported error", res.error)

    def test_already_target_version_matched_in_post_mutation(self):
        def mock_runner(cmd: str, timeout: float):
            return 0, "tool version 2.5.0 (stable)", "", 15.0

        res = smoke_mod.run_tool_smoke_check(
            "tool",
            stage="post",
            target_version="2.5.0",
            runner=mock_runner,
        )
        self.assertEqual(res.status, "PASS")
        self.assertTrue(res.already_target)
        self.assertEqual(res.version_readback, "tool version 2.5.0 (stable)")

    def test_command_template_placeholder_resolution(self):
        cmd = smoke_mod.resolve_command_template(
            "{{HOMEBREW_PREFIX}}/bin/git --version",
            home="/Users/testuser",
            brew_prefix="/opt/custombrew",
        )
        self.assertEqual(cmd, "/opt/custombrew/bin/git --version")


class TestPruneToolchainDuplicatesGate(unittest.TestCase):
    def setUp(self):
        self.manifest_fixture = {
            "tools": {
                "codex": {
                    "authoritative_owner": "npm-global",
                    "active_path_pattern": "{{HOME}}/.npm-global/bin/codex",
                },
                "qoder": {
                    "authoritative_owner": "standalone",
                    "active_path_pattern": "{{HOME}}/.local/bin/qodercli",
                },
            }
        }

    def test_missing_approval_fails_closed(self):
        packet = prune_mod.evaluate_prune_gate(
            tool_name="codex",
            target_path="/Users/testuser/.local/bin/codex",
            retained_path="/Users/testuser/.npm-global/bin/codex",
            manifest_data=self.manifest_fixture,
            home="/Users/testuser",
            mock_references=[],
            mock_pids=[],
            mock_operational=True,
            approval_token=None,
        )
        self.assertEqual(packet.status, "BLOCKED")
        self.assertFalse(packet.checks["external_approval"].passed)
        self.assertIn("External approval check failed", packet.blocked_reasons[0])
        self.assertEqual(packet.action_taken, "BLOCKED_NO_MUTATION")

    def test_active_process_holding_binary_fails_closed(self):
        packet = prune_mod.evaluate_prune_gate(
            tool_name="codex",
            target_path="/Users/testuser/.local/bin/codex",
            retained_path="/Users/testuser/.npm-global/bin/codex",
            manifest_data=self.manifest_fixture,
            home="/Users/testuser",
            mock_references=[],
            mock_pids=[4242],
            mock_operational=True,
            approval_token="FORCE_APPROVED_FOR_TEST",
        )
        self.assertEqual(packet.status, "BLOCKED")
        self.assertFalse(packet.checks["processes"].passed)
        self.assertIn("Active processes holding binary: [4242]", packet.checks["processes"].details)
        self.assertEqual(packet.action_taken, "BLOCKED_NO_MUTATION")

    def test_reference_in_scripts_fails_closed(self):
        packet = prune_mod.evaluate_prune_gate(
            tool_name="codex",
            target_path="/Users/testuser/.local/bin/codex",
            retained_path="/Users/testuser/.npm-global/bin/codex",
            manifest_data=self.manifest_fixture,
            home="/Users/testuser",
            mock_references=["/Users/testuser/scripts/old-wrapper.sh"],
            mock_pids=[],
            mock_operational=True,
            approval_token="FORCE_APPROVED_FOR_TEST",
        )
        self.assertEqual(packet.status, "BLOCKED")
        self.assertFalse(packet.checks["references"].passed)
        self.assertEqual(packet.action_taken, "BLOCKED_NO_MUTATION")

    def test_manifest_reconciliation_rejects_non_authoritative_retained_path(self):
        packet = prune_mod.evaluate_prune_gate(
            tool_name="codex",
            target_path="/Users/testuser/.local/bin/codex",
            retained_path="/opt/homebrew/bin/codex",  # Diverges from declared ~/.npm-global/bin/codex
            manifest_data=self.manifest_fixture,
            home="/Users/testuser",
            mock_references=[],
            mock_pids=[],
            mock_operational=True,
            approval_token="FORCE_APPROVED_FOR_TEST",
        )
        self.assertEqual(packet.status, "BLOCKED")
        self.assertFalse(packet.checks["manifest_reconciliation"].passed)

    def test_manifest_reconciliation_rejects_pruning_authoritative_path(self):
        packet = prune_mod.evaluate_prune_gate(
            tool_name="codex",
            target_path="/Users/testuser/.npm-global/bin/codex",  # Declared authoritative path
            retained_path="/Users/testuser/.npm-global/bin/codex",
            manifest_data=self.manifest_fixture,
            home="/Users/testuser",
            mock_references=[],
            mock_pids=[],
            mock_operational=True,
            approval_token="FORCE_APPROVED_FOR_TEST",
        )
        self.assertEqual(packet.status, "BLOCKED")
        self.assertFalse(packet.checks["manifest_reconciliation"].passed)

    def test_dependency_integrity_failure_fails_closed(self):
        packet = prune_mod.evaluate_prune_gate(
            tool_name="codex",
            target_path="/Users/testuser/.local/bin/codex",
            retained_path="/Users/testuser/.npm-global/bin/codex",
            manifest_data=self.manifest_fixture,
            home="/Users/testuser",
            mock_references=[],
            mock_pids=[],
            mock_operational=False,  # Retained binary failed smoke test
            approval_token="FORCE_APPROVED_FOR_TEST",
        )
        self.assertEqual(packet.status, "BLOCKED")
        self.assertFalse(packet.checks["dependency_integrity"].passed)

    def test_all_five_checks_pass_dry_run_approved(self):
        packet = prune_mod.evaluate_prune_gate(
            tool_name="codex",
            target_path="/Users/testuser/.local/bin/codex",
            retained_path="/Users/testuser/.npm-global/bin/codex",
            manifest_data=self.manifest_fixture,
            home="/Users/testuser",
            mock_references=[],
            mock_pids=[],
            mock_operational=True,
            approval_token="FORCE_APPROVED_FOR_TEST",
            execute=False,
        )
        self.assertEqual(packet.status, "APPROVED")
        self.assertTrue(packet.dry_run)
        self.assertEqual(packet.action_taken, "APPROVED_DRY_RUN")
        self.assertEqual(len(packet.blocked_reasons), 0)


class TestBenchmarkShellStartupHarness(unittest.TestCase):
    def test_benchmark_script_runs_with_mock_timings_in_json(self):
        script_path = SCRIPTS_DIR / "benchmark-shell-startup.sh"
        proc = subprocess.run(
            [
                str(script_path),
                "--mock-cold", "120.5,119.0,121.2,118.8,122.0",
                "--mock-warm", "45.0,44.8,45.2,44.9,45.1",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["runs_count"], 5)
        self.assertIn("cold", data)
        self.assertIn("warm", data)
        self.assertEqual(len(data["cold"]["timings_ms"]), 5)
        self.assertEqual(len(data["warm"]["timings_ms"]), 5)
        self.assertAlmostEqual(data["cold"]["median_ms"], 120.5, delta=0.5)
        self.assertAlmostEqual(data["warm"]["median_ms"], 45.0, delta=0.5)
        self.assertGreater(data["cold"]["variance"], 0.0)
        self.assertGreater(data["warm"]["variance"], 0.0)

    def test_fewer_than_five_runs_fails_closed(self):
        script_path = SCRIPTS_DIR / "benchmark-shell-startup.sh"
        proc = subprocess.run(
            [str(script_path), "--runs", "3"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("must be at least 5", proc.stderr)


class TestCheckServicePorts(unittest.TestCase):
    def test_ports_clean_when_no_listeners_or_aligned(self):
        fixture = {
            "ports": {
                "11434": [{"pid": 100, "name": "ollama", "command_line": "ollama serve", "is_foreign": False}],
                "3111": [{"pid": 101, "name": "node", "command_line": "node agentmemory server", "is_foreign": False}],
                "49134": [{"pid": 102, "name": "iii-engine", "command_line": "iii-engine daemon", "is_foreign": False}],
            }
        }
        report = ports_mod.inspect_service_ports(fixture_data=fixture, check_docker=False)
        self.assertEqual(report["status"], "PASS")
        self.assertFalse(report["has_quarantine"])
        self.assertEqual(report["quarantined_processes_count"], 0)

    def test_foreign_process_on_ollama_port_quarantined_without_kill(self):
        fixture = {
            "ports": {
                "11434": [{"pid": 9999, "name": "rogue-daemon", "command_line": "rogue-daemon --port 11434", "is_foreign": True}],
                "3111": [],
                "49134": [],
            }
        }
        report = ports_mod.inspect_service_ports(fixture_data=fixture, check_docker=False)
        self.assertEqual(report["status"], "COLLISION_QUARANTINED")
        self.assertTrue(report["has_quarantine"])
        self.assertEqual(report["quarantined_processes_count"], 1)
        self.assertTrue(report["ports"]["11434"]["quarantined"])
        self.assertEqual(report["ports"]["11434"]["status"], "FOREIGN_PROCESS")

    def test_port_collision_multiple_listeners_quarantined(self):
        fixture = {
            "ports": {
                "3111": [
                    {"pid": 201, "name": "node", "command_line": "node am1", "is_foreign": False},
                    {"pid": 202, "name": "python3", "command_line": "python3 am2", "is_foreign": True},
                ],
                "11434": [],
                "49134": [],
            }
        }
        report = ports_mod.inspect_service_ports(fixture_data=fixture, check_docker=False)
        self.assertEqual(report["status"], "COLLISION_QUARANTINED")
        self.assertEqual(report["collisions_count"], 1)
        self.assertEqual(report["ports"]["3111"]["status"], "COLLISION")
        self.assertTrue(report["ports"]["3111"]["quarantined"])


class TestCheckAgentMemoryHealth(unittest.TestCase):
    def test_root_path_strictly_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            am_health_mod.check_health_and_alignment(url="http://localhost:3111/")
        self.assertIn("Root '/' endpoint is forbidden", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            am_health_mod.check_health_and_alignment(url="http://localhost:3111")
        self.assertIn("Root '/' endpoint is forbidden", str(ctx2.exception))

    def test_healthy_endpoint_with_aligned_engine(self):
        report = am_health_mod.check_health_and_alignment(
            url="http://localhost:3111/agentmemory/health",
            expected_engine="0.22.1",
            mock_http_response=(200, {"status": "ok", "engine": "0.22.1"}),
            mock_processes={3111: [{"pid": 50, "name": "node", "command_line": "node agentmemory"}], 49134: []},
        )
        self.assertEqual(report.status, "HEALTHY")
        self.assertEqual(report.http_status, 200)
        self.assertTrue(report.alignment.is_aligned)
        self.assertEqual(len(report.quarantine), 0)

    def test_engine_version_mismatch_detected(self):
        report = am_health_mod.check_health_and_alignment(
            url="http://localhost:3111/agentmemory/health",
            expected_engine="0.22.1",
            mock_http_response=(200, {"status": "ok", "engine": "0.19.0"}),
            mock_processes={3111: [], 49134: []},
        )
        self.assertEqual(report.status, "MISALIGNED")
        self.assertFalse(report.alignment.is_aligned)
        self.assertIn("diverges from pinned '0.22.1'", report.alignment.details)

    def test_foreign_engine_process_quarantined_on_port_49134(self):
        report = am_health_mod.check_health_and_alignment(
            url="http://localhost:3111/agentmemory/health",
            expected_engine="0.22.1",
            mock_http_response=(200, {"status": "ok", "engine": "0.22.1"}),
            mock_processes={
                3111: [{"pid": 10, "name": "node", "command_line": "node agentmemory"}],
                49134: [{"pid": 999, "name": "legacy-iii-0.19", "command_line": "legacy-iii --port 49134"}],
            },
        )
        self.assertEqual(report.status, "QUARANTINED")
        self.assertEqual(len(report.quarantine), 1)
        self.assertEqual(report.quarantine[0].pid, 999)
        self.assertEqual(report.quarantine[0].port, 49134)


class TestSeedAgentMemoryDecisions(unittest.TestCase):
    def test_dry_run_is_default_and_non_mutating(self):
        report = am_seed_mod.seed_decisions(
            dry_run=True,
            mock_existing=[],
        )
        self.assertTrue(report["dry_run"])
        self.assertEqual(report["seeded_count"], 0)
        self.assertEqual(report["would_seed_count"], 6)
        self.assertEqual(report["duplicate_skipped_count"], 0)
        self.assertEqual(report["status"], "PASS")

    def test_duplicate_observations_suppressed(self):
        mock_existing = [
            {"concepts": ["codex-update-authority"], "content": "Codex update authority"},
            {"concepts": ["qoder-standalone-authority"], "content": "Qoder update authority"},
        ]
        report = am_seed_mod.seed_decisions(
            dry_run=True,
            mock_existing=mock_existing,
        )
        self.assertEqual(report["duplicate_skipped_count"], 2)
        self.assertEqual(report["would_seed_count"], 4)

    def test_apply_seeds_unregistered_decisions_via_hook(self):
        mock_existing = [
            {"concepts": ["docker-persistent-volumes"], "content": "Docker volume hygiene"},
        ]
        posted_decisions = []

        def mock_post_hook(dec: dict[str, Any]) -> bool:
            posted_decisions.append(dec["id"])
            return True

        report = am_seed_mod.seed_decisions(
            dry_run=False,
            mock_existing=mock_existing,
            post_hook=mock_post_hook,
        )
        self.assertFalse(report["dry_run"])
        self.assertEqual(report["duplicate_skipped_count"], 1)
        self.assertEqual(report["seeded_count"], 5)
        self.assertNotIn("docker-persistent-volumes", posted_decisions)
        self.assertIn("codex-update-authority", posted_decisions)


class TestAgentMemoryLaunchAgentWatchdogTemplate(unittest.TestCase):
    def setUp(self):
        self.template_path = CONFIG_DIR / "launchd" / "com.agentmemory.server.plist.tmpl"

    def test_template_file_exists_and_contains_bounded_restart_keys(self):
        self.assertTrue(self.template_path.is_file(), f"Missing template at {self.template_path}")
        content = self.template_path.read_text(encoding="utf-8")
        self.assertIn("<key>ThrottleInterval</key>", content)
        self.assertIn("<integer>30</integer>", content)
        self.assertIn("<key>KeepAlive</key>", content)
        self.assertIn("<key>SuccessfulExit</key>", content)
        self.assertIn("<false/>", content)

    def test_template_passes_plutil_lint(self):
        proc = subprocess.run(
            ["plutil", "-lint", str(self.template_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("OK", proc.stdout)

    def test_rendered_template_has_zero_unresolved_tags_and_passes_plutil(self):
        render_res = render_mod.render_file(
            self.template_path,
            None,
            context={
                "HOME": "/Users/testuser",
                "HOMEBREW_PREFIX": "/opt/homebrew",
                "WORKSPACE_ROOT": "/Users/testuser/Developer",
                "OPENSPEC_STORE_ROOT": "/Users/testuser/Developer/platform/openspec-store",
            },
            dry_run=True,
        )
        rendered_text = render_res.content
        unresolved = render_res.unresolved_tags
        self.assertEqual(unresolved, [])
        self.assertNotIn("{{", rendered_text)
        self.assertIn("/opt/homebrew/bin/node", rendered_text)
        self.assertIn("/Users/testuser/.npm-global/bin/agentmemory", rendered_text)

        with tempfile.NamedTemporaryFile("w", suffix=".plist", delete=False) as tf:
            tf.write(rendered_text)
            temp_plist_path = tf.name

        try:
            proc = subprocess.run(
                ["plutil", "-lint", temp_plist_path],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("OK", proc.stdout)
        finally:
            os.unlink(temp_plist_path)


class TestReconciledToolchainUpdaterAndDailyRunner(unittest.TestCase):
    def test_updater_registry_declares_codex_npm_authority_and_writer(self):
        codex_decl = reg_mod.get_supported_updater("codex", "npm")
        self.assertIsNotNone(codex_decl)
        self.assertIn("npm", str(codex_decl.supported_verb))
        self.assertEqual(codex_decl.writer_binary, "npm")
        self.assertNotEqual(codex_decl.updater_dispatch, "native")  # Native verb is invalid and replaced

    def test_updater_registry_declares_qoder_standalone_dispatcher(self):
        qoder_decl = reg_mod.get_supported_updater("qoder", "vendor_download")
        self.assertIsNotNone(qoder_decl)
        self.assertIn(".qoder/entry", str(qoder_decl.writer_binary))
        self.assertEqual(qoder_decl.updater_dispatch, "native")

    def test_daily_update_script_path_precedence_order(self):
        runner_path = SCRIPTS_DIR / "workstation-daily-update.sh"
        self.assertTrue(runner_path.is_file())
        content = runner_path.read_text(encoding="utf-8")

        # Verify PATH puts .local/bin ahead of /opt/homebrew/bin and /opt/homebrew/bin ahead of .npm-global/bin
        path_line = [line for line in content.splitlines() if line.startswith("export PATH=")][0]
        npm_idx = path_line.find(".npm-global/bin")
        local_idx = path_line.find(".local/bin")
        brew_idx = path_line.find("/opt/homebrew/bin")

        self.assertNotEqual(npm_idx, -1)
        self.assertNotEqual(local_idx, -1)
        self.assertNotEqual(brew_idx, -1)
        self.assertLess(local_idx, brew_idx, "local/bin must precede /opt/homebrew/bin")
        self.assertLess(brew_idx, npm_idx, "/opt/homebrew/bin must precede .npm-global/bin")

    def test_daily_update_script_handles_codex_and_qoder_target_misalignment(self):
        runner_path = SCRIPTS_DIR / "workstation-daily-update.sh"
        content = runner_path.read_text(encoding="utf-8")

        # Qoder target prefix check
        self.assertIn('[[ "${bin}" == "qoder" ]] && [[ "${real_bin}" != "${HOME}/.local"* && "${real_bin}" != "${HOME}/.qoder"* ]]', content)
        # Codex update execution
        self.assertIn('codex update', content)


if __name__ == "__main__":
    unittest.main()
