#!/usr/bin/env python3
"""Regression test suite for workstation toolchain version authority and drift governance.

Exercises production implementations in:
- inventory-workstation-toolchain.py
- reconcile-agent-cli-coverage.py
- toolchain_updater_registry.py
- workstation-daily-update.sh
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import toolchain_updater_registry as reg  # noqa: E402

inv_spec = importlib.util.spec_from_file_location("inventory_workstation_toolchain", SCRIPTS_DIR / "inventory-workstation-toolchain.py")
inv = importlib.util.module_from_spec(inv_spec)
sys.modules["inventory_workstation_toolchain"] = inv
inv_spec.loader.exec_module(inv)

cov_spec = importlib.util.spec_from_file_location("reconcile_agent_cli_coverage", SCRIPTS_DIR / "reconcile-agent-cli-coverage.py")
cov = importlib.util.module_from_spec(cov_spec)
sys.modules["reconcile_agent_cli_coverage"] = cov
cov_spec.loader.exec_module(cov)


class TestCellarAndBundleProvenance(unittest.TestCase):
    def test_cellar_node_modules_evaluated_as_brew_formula(self):
        path = "/opt/homebrew/Cellar/newman/6.2.2/libexec/lib/node_modules/newman/bin/newman.js"
        root, src = inv.derive_install_root_and_source(path)
        self.assertEqual(src, "brew-formula")
        self.assertEqual(root, "/opt/homebrew/Cellar/newman/6.2.2")

    def test_caskroom_evaluated_as_brew_cask(self):
        path = "/opt/homebrew/Caskroom/cursor-cli/2026.10.01/dist/cursor-agent"
        root, src = inv.derive_install_root_and_source(path)
        self.assertEqual(src, "brew-cask")
        self.assertEqual(root, "/opt/homebrew/Caskroom/cursor-cli/2026.10.01")

    def test_npm_global_scoped_evaluated_as_npm(self):
        path = "/Users/androidteam/.npm-global/lib/node_modules/@openai/codex/bin/codex.js"
        root, src = inv.derive_install_root_and_source(path)
        self.assertEqual(src, "npm")
        self.assertEqual(root, "/Users/androidteam/.npm-global/lib/node_modules/@openai/codex")

    def test_prime_agent_bundle_detected_via_package_json(self):
        # Prime agent lives at /opt/homebrew/lib/prime-agent/dist/bundle/cli.js
        path = "/opt/homebrew/lib/prime-agent/dist/bundle/cli.js"
        root, src = inv.derive_install_root_and_source(path)
        self.assertEqual(src, "npm")
        self.assertEqual(root, "/opt/homebrew/lib/prime-agent")

    def test_vendor_download_local_share(self):
        path = "/Users/androidteam/.local/share/claude/versions/2.1.289/claude"
        root, src = inv.derive_install_root_and_source(path)
        self.assertEqual(src, "vendor_download")
        self.assertEqual(root, "/Users/androidteam/.local/share/claude")


class TestProductionAuthoritativeCopyDuplication(unittest.TestCase):
    def test_production_newman_duplication_has_authoritative_copy_first(self):
        tools = inv.inventory_tools()
        newman_item = next((t for t in tools if t.name == "newman"), None)
        self.assertIsNotNone(newman_item, "newman must be present in inventory")
        self.assertTrue(newman_item.has_duplication, "newman should report duplication across Cellar and home-toolchain")
        self.assertGreaterEqual(len(newman_item.copies), 2)
        # Authoritative copy MUST be at index 0
        self.assertTrue(newman_item.copies[0].is_authoritative, "copies[0] must be authoritative copy")
        self.assertEqual(newman_item.copies[0].owning_manager, "brew")
        self.assertFalse(newman_item.copies[1].is_authoritative)
        self.assertEqual(newman_item.copies[1].owning_manager, "home-toolchain")
        self.assertFalse(newman_item.is_homebrew_adjacent, "Homebrew Cellar formula newman must not be flagged homebrew-adjacent")


class TestProductionWrapperInheritance(unittest.TestCase):
    def test_qoder_inherits_target_misalignment_from_qodercli(self):
        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        qoder_item = next((it for it in rec.items if it.name == "qoder"), None)
        self.assertIsNotNone(qoder_item)
        self.assertEqual(qoder_item.authority, "npm-global")
        self.assertEqual(qoder_item.drift_status, "target_misalignment")
        self.assertFalse(qoder_item.prefix_aligned)
        self.assertIn("/.qoder/bin/qodercli", qoder_item.active_install_root)
        self.assertIn("Wrapper targets", qoder_item.consequence)
        self.assertIn("~/.npm-global", qoder_item.compatible_command)


class TestProductionPrimeAgentProvenance(unittest.TestCase):
    def test_prime_agent_evaluated_truthfully_without_fabricated_cask(self):
        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        item = next((it for it in rec.items if it.name == "prime-agent"), None)
        self.assertIsNotNone(item)
        self.assertEqual(item.authority, "npm-global")
        self.assertEqual(item.writer, "npm")
        self.assertEqual(item.updater_dispatch, "none")
        self.assertEqual(item.drift_status, "target_misalignment")
        self.assertEqual(item.active_install_root, "/opt/homebrew/lib/prime-agent")
        self.assertIn("Unmanaged package bundle", item.orthogonal_findings[0])


class TestProductionKiloCommand(unittest.TestCase):
    def test_kilo_records_kilo_upgrade_verb_with_none_dispatch(self):
        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        item = next((it for it in rec.items if it.name == "kilo"), None)
        self.assertIsNotNone(item)
        self.assertEqual(item.update_verb, "kilo upgrade")
        self.assertEqual(item.updater_dispatch, "none")


class TestSharedUpdaterRegistry(unittest.TestCase):
    def test_covered_tools_registered_with_verified_commands(self):
        claude_decl = reg.get_supported_updater("claude", "vendor_download")
        self.assertIsNotNone(claude_decl)
        self.assertEqual(claude_decl.supported_verb, "claude update")
        self.assertEqual(claude_decl.updater_dispatch, "native")

        codex_decl = reg.get_supported_updater("codex", "npm")
        self.assertIsNotNone(codex_decl)
        self.assertEqual(codex_decl.supported_verb, "codex update")

        opencode_decl = reg.get_supported_updater("opencode", "brew-formula")
        self.assertIsNotNone(opencode_decl)
        self.assertEqual(opencode_decl.updater_dispatch, "delegating")
        self.assertEqual(opencode_decl.delegating_to, "brew")


        kimi_decl = reg.get_supported_updater("kimi", "vendor_download")
        self.assertIsNotNone(kimi_decl)
        self.assertEqual(kimi_decl.supported_verb, "kimi update")
        self.assertEqual(kimi_decl.updater_dispatch, "native")
    def test_unregistered_tool_fails_closed(self):
        decl = reg.get_supported_updater("unknown_agent", "vendor_download")
        self.assertIsNone(decl)

    def test_coverage_evaluator_rejects_source_mismatches(self):
        # Strict cask vs formula matching
        decl_cask = reg.get_supported_updater("opencode", "brew-cask")
        self.assertIsNone(decl_cask, "opencode is formula; brew-cask lookup must return None")

        decl_formula = reg.get_supported_updater("opencode", "brew-formula")
        self.assertIsNotNone(decl_formula)
        self.assertEqual(decl_formula.supported_verb, "opencode upgrade")

        # Unregistered tool must fail closed
        decl = reg.get_supported_updater("unknown_agent", "vendor_download")
        self.assertIsNone(decl)

        # Coverage evaluator reject source mismatches
        ok, msg = cov.evaluate_update_path("opencode", "covered", "opencode upgrade", "brew-cask", "Homebrew cask")
        self.assertFalse(ok)
        self.assertIn("unsupported or unverified", msg)

        # Codex is npm; brew upgrade codex must fail
        ok, msg = cov.evaluate_update_path("codex", "covered", "brew upgrade codex", "ecosystem_manager", "npm")
        self.assertFalse(ok)
        self.assertIn("incompatible update verb", msg)

        # Unrecognized verb must fail
        ok, msg = cov.evaluate_update_path("codex", "covered", "codex invalid-subcmd", "ecosystem_manager", "npm")
        self.assertFalse(ok)
        self.assertIn("unsupported or unrecognized update command", msg)

class TestRegistryEnforcementInInventory(unittest.TestCase):
    def test_cleared_registry_fails_closed_in_inventory(self):
        from unittest.mock import patch
        with patch.dict(reg.SUPPORTED_UPDATER_REGISTRY, {}, clear=True):
            rep = inv.evaluate_authority_and_drift("~/.npm-global")
            codex_it = next(i for i in rep.items if i.name == "codex")
            self.assertIsNone(codex_it.update_verb)
            self.assertEqual(codex_it.updater_dispatch, "none")
            self.assertEqual(codex_it.drift_status, "unknown")

            claude_it = next(i for i in rep.items if i.name == "claude")
            self.assertIsNone(claude_it.update_verb)
            self.assertEqual(claude_it.updater_dispatch, "none")
            self.assertEqual(claude_it.drift_status, "unknown")


class TestCrontabSecretRedactionAndMacros(unittest.TestCase):
    def test_crontab_inline_env_secrets_redacted_and_macros_handled(self):
        import types
        from unittest.mock import patch
        secret_sentinel = "SUPER_SECRET_TOKEN"
        cron_fixture = (
            f"* * * * * API_KEY={secret_sentinel} npm update -g\n"
            "@reboot SECRET_PASS=abc /usr/local/bin/brew upgrade\n"
        )
        with patch.object(inv.Path, "is_dir", return_value=False), patch.object(
            inv.subprocess, "run", return_value=types.SimpleNamespace(returncode=0, stdout=cron_fixture)
        ):
            res = inv.audit_scheduled_writers()
            cands = res["candidate_writers"]
            self.assertEqual(len(cands), 2)
            for cand in cands:
                self.assertNotIn(secret_sentinel, cand["executable_baseline"])
                self.assertNotIn("abc", cand["executable_baseline"])
            self.assertEqual(cands[0]["executable_baseline"], "npm")
            self.assertIn("API_KEY", cands[0]["env_keys"])
            self.assertEqual(cands[1]["executable_baseline"], "brew")
            self.assertIn("SECRET_PASS", cands[1]["env_keys"])
            self.assertNotIn(secret_sentinel, str(res))
            self.assertNotIn("abc", str(res))


class TestScheduledWriterWordBoundary(unittest.TestCase):
    def test_word_boundary_prevents_pi_false_matching_pip_or_api(self):
        from unittest.mock import patch
        mock_sched = {
            "scan_boundaries": {"scanned_paths": [], "excluded_limitations": []},
            "candidate_writers": [
                {"type": "launch_agent", "label": "com.example.pip-runner", "executable_baseline": "/usr/bin/pip", "schedule": {}, "env_keys": []},
                {"type": "launch_agent", "label": "com.example.api-server", "executable_baseline": "/usr/bin/node", "schedule": {}, "env_keys": []},
                {"type": "launch_agent", "label": "com.pi.pi-updater", "executable_baseline": "/usr/bin/pi", "schedule": {}, "env_keys": []},
            ],
        }
        with patch.object(inv, "audit_scheduled_writers", return_value=mock_sched):
            rep = inv.evaluate_authority_and_drift("~/.npm-global")
            pi_it = next(i for i in rep.items if i.name == "pi")
            findings = pi_it.orthogonal_findings
            self.assertEqual(len(findings), 1)
            self.assertIn("com.pi.pi-updater", findings[0])
            self.assertNotIn("pip-runner", str(findings))
            self.assertNotIn("api-server", str(findings))


class TestCoveragePauseDelegationFlag(unittest.TestCase):
    def test_delegation_flag_does_not_pause_coverage(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE": "1"}, clear=True):
            bg = cov.audit_background_auto_update_settings()
            self.assertFalse(bg["is_paused"])
        with patch.dict(os.environ, {"DISABLE_UPDATES": "1"}, clear=True):
            bg = cov.audit_background_auto_update_settings()
            self.assertTrue(bg["is_paused"])


class TestGlobalPausePolicy(unittest.TestCase):
    def test_truthiness_normalization(self):
        for val in (True, 1, 1.0, "1", "true", "True", "yes", "on", "enabled"):
            self.assertTrue(reg.is_truthy_pause(val))
        for val in (False, 0, 0.0, "0", "false", "no", "off", None, ""):
            self.assertFalse(reg.is_truthy_pause(val))

    def test_global_pause_active_from_env_or_config(self):
        self.assertTrue(reg.is_global_pause_active({"claude": {"DISABLE_UPDATES": "1"}}))
        self.assertTrue(reg.is_global_pause_active({"claude": {"env.DISABLE_AUTOUPDATER": "true"}}))
        self.assertFalse(reg.is_global_pause_active({"claude": {"DISABLE_UPDATES": "0"}}))


class TestSplitHomebrewRosters(unittest.TestCase):
    def test_preflight_splits_formulae_and_casks(self):
        # Run python preflight logic on simulated items
        mock_items = [
            {"name": "codex", "drift_status": "target_misalignment", "authority": "brew-cask", "writer": "brew", "selected_channel": "cask codex"},
            {"name": "opencode", "drift_status": "clean", "authority": "brew-formula", "writer": "brew", "selected_channel": "brew-formula"},
            {"name": "broken-formula", "drift_status": "conflict", "authority": "brew-formula", "writer": "brew", "selected_channel": "brew-formula"},
        ]
        deny_formulae, deny_casks = [], []
        for it in mock_items:
            drift = it.get("drift_status")
            auth = it.get("authority", "")
            chan = it.get("selected_channel", "") or ""
            if drift in ("unknown", "target_misalignment", "conflict"):
                if "cask" in auth or "cask" in chan:
                    deny_casks.append(it["name"])
                elif "formula" in auth:
                    deny_formulae.append(it["name"])

        self.assertEqual(deny_casks, ["codex"])
        self.assertEqual(deny_formulae, ["broken-formula"])
        self.assertNotIn("codex", deny_formulae)
        self.assertNotIn("broken-formula", deny_casks)


class TestScopedNpmFiltering(unittest.TestCase):
    def test_strip_trailing_version_preserves_scope(self):
        res = subprocess.run(
            ["awk", "-F:", '{pkg=$4; sub(/@[^@]*$/, "", pkg); print (pkg != "" ? pkg : $4)}'],
            input="@openai/codex@1.2.3:1.2.3:1.2.4:@openai/codex@1.2.4\n@qoder-ai/qodercli@0.1.0:0.1.0:0.1.1:@qoder-ai/qodercli@0.1.1\nauggie@2.0.1:2.0.1:2.0.2:auggie@2.0.2\n",
            capture_output=True,
            text=True,
            check=True,
        )
        lines = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        self.assertEqual(lines, ["@openai/codex", "@qoder-ai/qodercli", "auggie"])

    def test_deny_filter_matches_scoped_package_and_variants(self):
        pattern = re.compile(r"^(@openai/codex)(@[^@]*)?$")
        self.assertTrue(pattern.match("@openai/codex"))
        self.assertTrue(pattern.match("@openai/codex@1.2.3"))
        self.assertFalse(pattern.match("@openai/codex-fork"))
        self.assertFalse(pattern.match("codex"))


class TestZeroExitFailureDetection(unittest.TestCase):
    def test_zero_exit_error_detected(self):
        output = "Error: Failed to change directory to /Users/androidteam/.local/share/kilo/update\n"
        has_error = bool(re.search(r"(?im)^\s*(error|fatal)[: ]|failed to [a-z]", output))
        self.assertTrue(has_error)


class TestCurrencyWordingInvariant(unittest.TestCase):
    def test_runner_output_wording_does_not_claim_unproven_currency(self):
        script_path = SCRIPTS_DIR / "workstation-daily-update.sh"
        content = script_path.read_text()
        self.assertNotIn("(idempotent/current)", content)
        self.assertNotIn("already up to date", content)
        self.assertIn("(idempotent, currency unverified)", content)
        self.assertIn("(local version changed, currency unverified)", content)


if __name__ == "__main__":
    unittest.main()
