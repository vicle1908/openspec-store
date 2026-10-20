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

    def test_muse_code_caskroom_evaluated_as_brew_cask(self):
        path = "/opt/homebrew/Caskroom/muse-code/1.4.10-R6427.1/muse-aarch64-macos"
        root, src = inv.derive_install_root_and_source(path)
        self.assertEqual(src, "brew-cask")
        self.assertEqual(root, "/opt/homebrew/Caskroom/muse-code/1.4.10-R6427.1")

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
        if newman_item.has_duplication:
            self.assertGreaterEqual(len(newman_item.copies), 2)
            # Authoritative copy MUST be at index 0
            self.assertTrue(newman_item.copies[0].is_authoritative, "copies[0] must be authoritative copy")
            self.assertEqual(newman_item.copies[0].owning_manager, "brew")
            self.assertFalse(newman_item.copies[1].is_authoritative)
            self.assertIn(newman_item.copies[1].owning_manager, ("home-toolchain", "adhoc-home"))
        else:
            self.assertEqual(len(newman_item.copies), 1)
            self.assertTrue(newman_item.copies[0].is_authoritative, "copies[0] must be authoritative copy")
            self.assertEqual(newman_item.copies[0].owning_manager, "brew")
        self.assertFalse(newman_item.is_homebrew_adjacent, "Homebrew Cellar formula newman must not be flagged homebrew-adjacent")


class TestProductionWrapperInheritance(unittest.TestCase):
    def test_qoder_inherits_target_misalignment_from_qodercli(self):
        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        qoder_item = next((it for it in rec.items if it.name == "qoder"), None)
        self.assertIsNotNone(qoder_item)
        self.assertEqual(qoder_item.authority, "vendor_download")
        self.assertEqual(qoder_item.drift_status, "clean")
        self.assertTrue(qoder_item.prefix_aligned)
        self.assertIn("/.qoder", qoder_item.active_install_root)
        self.assertIsNone(qoder_item.consequence)


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


class TestMuseCodeAuthorityAndCollisionGovernance(unittest.TestCase):
    def test_muse_collision_disambiguation_and_clean_drift(self):
        tools = inv.inventory_tools()
        muse_item = next((t for t in tools if t.name == "muse"), None)
        self.assertIsNotNone(muse_item, "muse must be present in inventory")
        self.assertIn("Homebrew cask 'muse' is an unrelated disabled desktop app", muse_item.name_collision)
        self.assertEqual(muse_item.preferred_source, "cask muse-code")
        self.assertTrue(muse_item.preferred_source_available)

        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        auth_item = next((it for it in rec.items if it.name == "muse"), None)
        self.assertIsNotNone(auth_item, "muse must be present in authority reconciliation")
        self.assertEqual(auth_item.drift_status, "clean")
        self.assertEqual(auth_item.authority, "brew-cask")
        self.assertEqual(auth_item.writer, "brew")
        self.assertEqual(auth_item.updater_dispatch, "none")


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

    def test_muse_registered_in_updater_registry(self):
        decl = reg.get_supported_updater("muse", "brew-cask")
        self.assertIsNotNone(decl)
        self.assertEqual(decl.tool, "muse")
        self.assertEqual(decl.source_type, "brew-cask")
        self.assertEqual(decl.updater_dispatch, "none")
        self.assertEqual(decl.delegating_to, "brew")
        self.assertEqual(decl.status, "uncovered_declared")

        decl_code = reg.get_supported_updater("muse-code", "brew-cask")
        self.assertIsNotNone(decl_code)
        self.assertEqual(decl_code.tool, "muse-code")
        self.assertEqual(decl_code.source_type, "brew-cask")
        self.assertEqual(decl_code.updater_dispatch, "none")
        self.assertEqual(decl_code.delegating_to, "brew")
        self.assertEqual(decl_code.status, "uncovered_declared")

    def test_omp_registered_and_verified_in_registry_inventory_and_coverage(self):
        import tempfile
        from unittest.mock import patch

        decl = reg.get_supported_updater("omp", "brew-formula")
        self.assertIsNotNone(decl)
        self.assertEqual(decl.tool, "omp")
        self.assertEqual(decl.source_type, "brew-formula")
        self.assertIsNone(decl.supported_verb)
        self.assertEqual(decl.updater_dispatch, "none")
        self.assertEqual(decl.delegating_to, "brew")
        self.assertEqual(decl.status, "uncovered_declared")

        # Coverage evaluator verifies registry declaration and reports delegating_to=brew
        ok, msg = cov.evaluate_update_path("omp", "uncovered_declared", None, "package_manager", "Homebrew (formula/cask)")
        self.assertTrue(ok)
        self.assertIn("delegating_to=brew", msg)

        # Unregistered package_manager tool fails closed
        ok_unreg, msg_unreg = cov.evaluate_update_path("unregistered_brew_tool", "uncovered_declared", None, "package_manager", "Homebrew (formula/cask)")
        self.assertFalse(ok_unreg)
        self.assertIn("unregistered or mismatched", msg_unreg)

        # Live authority and drift evaluation for omp
        rep = inv.evaluate_authority_and_drift("~/.npm-global")
        omp_auth = next((i for i in rep.items if i.name == "omp"), None)
        self.assertIsNotNone(omp_auth, "omp must be present in authority reconciliation")
        self.assertEqual(omp_auth.authority, "brew-formula")
        self.assertEqual(omp_auth.writer, "brew")
        self.assertEqual(omp_auth.updater_dispatch, "none")
        self.assertEqual(omp_auth.drift_status, "clean")
        self.assertEqual(omp_auth.active_install_root, "/opt/homebrew/Cellar")
        self.assertTrue(omp_auth.prefix_aligned)

        # Inventory tools includes omp and qwen and detects omp shadow paths
        with tempfile.TemporaryDirectory() as tmp:
            home_dir = Path(tmp).resolve() / "home"
            bun_omp = home_dir / ".bun" / "bin" / "omp"
            bun_omp.parent.mkdir(parents=True, exist_ok=True)
            bun_omp.write_text("#!/bin/sh\n")
            items = inv.inventory_tools(home_dir=home_dir)
            omp_inv = next((t for t in items if t.name == "omp"), None)
            qwen_inv = next((t for t in items if t.name == "qwen"), None)
            self.assertIsNotNone(omp_inv)
            self.assertIsNotNone(qwen_inv)
            self.assertEqual(omp_inv.preferred_source, "formula can1357/tap/omp")
            self.assertEqual(qwen_inv.preferred_source, "formula qwen-code")
            self.assertTrue(omp_inv.has_duplication)
            self.assertTrue(any(c.location_path == str(bun_omp) and c.owning_manager == "bun-global" for c in omp_inv.copies))

            # Shadow binary active on PATH triggers target_misalignment
            orig_which = inv.shutil.which
            with patch.object(inv.shutil, "which", side_effect=lambda n: str(bun_omp) if n == "omp" else orig_which(n)):
                rep_shadow = inv.evaluate_authority_and_drift("~/.npm-global")
                omp_shadow = next(i for i in rep_shadow.items if i.name == "omp")
                self.assertEqual(omp_shadow.drift_status, "target_misalignment")
                self.assertFalse(omp_shadow.prefix_aligned)
                self.assertEqual(omp_shadow.compatible_command, "brew upgrade can1357/tap/omp")

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

            cce_it = next(i for i in rep.items if i.name == "cce")
            self.assertIsNone(cce_it.update_verb)
            self.assertEqual(cce_it.updater_dispatch, "none")
            self.assertEqual(cce_it.drift_status, "unknown")
            self.assertEqual(cce_it.authority, "unknown")
            self.assertEqual(cce_it.writer, "unknown")

            omp_it = next(i for i in rep.items if i.name == "omp")
            self.assertIsNone(omp_it.update_verb)
            self.assertEqual(omp_it.updater_dispatch, "none")
            self.assertEqual(omp_it.drift_status, "unknown")
            self.assertEqual(omp_it.authority, "unknown")

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



class TestCceStandaloneAuthority(unittest.TestCase):
    def test_cce_authority_resolves_to_standalone_clean_under_normal_registry(self):
        rep = inv.evaluate_authority_and_drift("~/.npm-global")
        cce_it = next((i for i in rep.items if i.name == "cce"), None)
        self.assertIsNotNone(cce_it, "cce must be evaluated in authority reconciliation")
        self.assertEqual(cce_it.authority, "standalone")
        self.assertEqual(cce_it.writer, "none")
        self.assertEqual(cce_it.drift_status, "clean")
        self.assertEqual(cce_it.updater_dispatch, "none")
        self.assertIsNone(cce_it.update_verb)
        self.assertEqual(cce_it.evidence_gaps, [])
        self.assertEqual(cce_it.selected_channel, "pinned standalone binary")


class TestOptionalRustDevProfileReconciliation(unittest.TestCase):
    def test_reconcile_with_manifest_skips_uninstalled_rust_dev(self):
        from unittest.mock import patch
        clean_path = ":".join(p for p in os.environ.get("PATH", "").split(":") if "/.venv" not in p)
        with patch.dict(os.environ, {"PATH": clean_path}):
            res = inv.reconcile_with_manifest()
            self.assertIsNotNone(res)
            self.assertEqual(res["missing_count"], 0)
            self.assertEqual(res["optional_skipped_count"], 2)
            self.assertEqual(set(res["summary"]["optional_skipped"]), {"rustup", "cargo"})
            self.assertNotIn("rustup", res["summary"]["missing"])
            self.assertNotIn("cargo", res["summary"]["missing"])
            self.assertEqual(res["status"], "aligned")

class TestDiscoveryPathNormalization(unittest.TestCase):
    def test_normalize_discovery_path_positions_homebrew_ahead_of_hermes_and_system(self):
        simulated_path = "/Users/androidteam/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin:/opt/homebrew/sbin"
        normalized = inv.normalize_discovery_path(simulated_path)
        parts = normalized.split(":")
        self.assertIn("/opt/homebrew/bin", parts)
        self.assertIn("/opt/homebrew/sbin", parts)
        brew_bin_idx = parts.index("/opt/homebrew/bin")
        hermes_idx = parts.index("/Users/androidteam/.hermes/node/bin")
        usr_bin_idx = parts.index("/usr/bin")
        self.assertLess(brew_bin_idx, hermes_idx)
        self.assertLess(brew_bin_idx, usr_bin_idx)

    def test_normalize_discovery_path_preserves_synthetic_test_bin_at_index_zero(self):
        simulated_path = "/tmp/synthetic_test/bin:/Users/androidteam/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin"
        normalized = inv.normalize_discovery_path(simulated_path)
        parts = normalized.split(":")
        self.assertEqual(parts[0], "/tmp/synthetic_test/bin")
        brew_bin_idx = parts.index("/opt/homebrew/bin")
        hermes_idx = parts.index("/Users/androidteam/.hermes/node/bin")
        self.assertLess(brew_bin_idx, hermes_idx)


class TestHomePrefixHijackReconciliation(unittest.TestCase):
    def test_clean_home_dir_reports_not_hijacked(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            home_dir = Path(tmp) / "home"
            ws_dir = home_dir / "Developer"
            ws_dir.mkdir(parents=True)
            rec = inv.check_prefix_reconciliation(
                "~/.npm-global", home_dir=home_dir, workspace_dir=ws_dir
            )
            self.assertFalse(rec.home_prefix_hijacked)
            self.assertEqual(rec.home_forbidden_artifacts, [])
            self.assertFalse(rec.has_split)
            self.assertEqual(rec.status, "reconciled")

    def test_dirty_home_dir_with_node_modules_and_lockfile_reports_hijacked(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            home_dir = Path(tmp) / "home"
            ws_dir = home_dir / "Developer"
            ws_dir.mkdir(parents=True)
            (home_dir / "node_modules").mkdir()
            (home_dir / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
            rec = inv.check_prefix_reconciliation(
                "~/.npm-global", home_dir=home_dir, workspace_dir=ws_dir
            )
            self.assertTrue(rec.home_prefix_hijacked)
            self.assertEqual(rec.home_forbidden_artifacts, ["pnpm-lock.yaml", "node_modules"])
            self.assertTrue(rec.has_split)
            self.assertEqual(rec.status, "split_detected")

    def test_unsanctioned_adhoc_home_copy_reported_with_sanctioned_replacement(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            home_dir = Path(tmp) / "home"
            (home_dir / "node_modules" / "gitnexus").mkdir(parents=True)
            (home_dir / "node_modules" / "@usebruno" / "cli").mkdir(parents=True)
            (home_dir / "node_modules" / "pyright").mkdir(parents=True)
            items = inv.inventory_tools(home_dir=home_dir)
            gn_item = next((i for i in items if i.name == "gitnexus"), None)
            bru_item = next((i for i in items if i.name == "bru"), None)
            self.assertIsNotNone(gn_item)
            self.assertIsNotNone(bru_item)
            gn_adhoc = next((c for c in gn_item.copies if c.owning_manager == "adhoc-home"), None)
            bru_adhoc = next((c for c in bru_item.copies if c.owning_manager == "adhoc-home"), None)
            self.assertIsNotNone(gn_adhoc)
            self.assertFalse(gn_adhoc.is_sanctioned)
            self.assertTrue(gn_adhoc.sanctioned_replacement.endswith("/.npm-global/lib/node_modules"))
            self.assertIsNotNone(bru_adhoc)
            self.assertFalse(bru_adhoc.is_sanctioned)
            self.assertTrue(bru_adhoc.sanctioned_replacement.endswith("/.local/share/home-toolchain/node_modules"))
            manifest_res = inv.reconcile_with_manifest(inventory_items=items, home_dir=home_dir)
            self.assertEqual(manifest_res["status"], "drift")
            self.assertGreaterEqual(manifest_res["unsanctioned_count"], 3)
            self.assertIn("gitnexus", manifest_res["summary"]["unsanctioned"])
            self.assertIn("bru", manifest_res["summary"]["unsanctioned"])
            self.assertIn("pyright", manifest_res["summary"]["unsanctioned"])


class TestTCCProvenanceAndBashFallback(unittest.TestCase):
    def test_workstation_daily_update_mirror_parity_and_bash_fail_closed(self):
        import hashlib
        import shutil
        import sqlite3
        import tempfile

        import tcc_provenance as tcc_mod

        store_script = SCRIPTS_DIR / "workstation-daily-update.sh"
        host_script = Path.home() / "Developer" / "scripts" / "workstation-daily-update.sh"
        if host_script.exists():
            h_store = hashlib.sha256(store_script.read_bytes()).hexdigest()
            h_host = hashlib.sha256(host_script.read_bytes()).hexdigest()
            self.assertEqual(h_store, h_host, "Host and store workstation-daily-update.sh mirrors must be byte-identical")

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # 1. Non-Darwin skip returns 0
            proc_linux = subprocess.run(
                ["bash", "-c", f'source "{store_script}" && verify_tcc_provenance'],
                env={**os.environ, "TCC_UNAME_S_OVERRIDE": "Linux"},
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc_linux.returncode, 0)

            # 2. Darwin missing DB returns nonzero
            proc_missing_db = subprocess.run(
                ["bash", "-c", f'source "{store_script}" && verify_tcc_provenance'],
                env={
                    **os.environ,
                    "TCC_UNAME_S_OVERRIDE": "Darwin",
                    "TCC_DB_PATH_OVERRIDE": str(tmp_path / "missing_TCC.db"),
                },
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_missing_db.returncode, 0)

            # 3. Darwin missing helper returns nonzero
            proc_missing_helper = subprocess.run(
                ["bash", "-c", f'source "{store_script}" && verify_tcc_provenance'],
                env={
                    **os.environ,
                    "TCC_UNAME_S_OVERRIDE": "Darwin",
                    "TCC_PROVENANCE_HELPER": str(tmp_path / "no_helper.py"),
                },
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc_missing_helper.returncode, 0)

            if sys.platform == "darwin":
                herdr_bin = tmp_path / "herdr"
                herdr_bin.write_bytes(Path("/usr/bin/true").read_bytes())
                herdr_bin.chmod(0o755)
                csreq_true = tcc_mod.copy_designated_csreq_blob("/usr/bin/true")

                db_path = tmp_path / "TCC.db"
                conn = sqlite3.connect(str(db_path))
                conn.execute(
                    "CREATE TABLE access (service TEXT, client TEXT, client_type INTEGER, auth_value INTEGER, csreq BLOB);"
                )
                real_herdr = str(herdr_bin.resolve())
                for svc in ("kTCCServiceAccessibility", "kTCCServiceScreenCapture", "kTCCServiceSystemPolicyAllFiles"):
                    conn.execute("INSERT INTO access VALUES (?, ?, 1, 2, ?);", (svc, real_herdr, csreq_true))
                conn.commit()
                conn.close()

                # Valid signed match exits 0
                proc_ok = subprocess.run(
                    ["bash", "-c", f'source "{store_script}" && verify_tcc_provenance --binary "{real_herdr}"'],
                    env={
                        **os.environ,
                        "TCC_UNAME_S_OVERRIDE": "Darwin",
                        "TCC_DB_PATH_OVERRIDE": str(db_path),
                    },
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(proc_ok.returncode, 0, proc_ok.stdout + proc_ok.stderr)

                # Same-path signature replacement exits nonzero
                herdr_bin.write_bytes(Path("/usr/bin/false").read_bytes())
                herdr_bin.chmod(0o755)
                proc_mismatch = subprocess.run(
                    ["bash", "-c", f'source "{store_script}" && verify_tcc_provenance --binary "{real_herdr}"'],
                    env={
                        **os.environ,
                        "TCC_UNAME_S_OVERRIDE": "Darwin",
                        "TCC_DB_PATH_OVERRIDE": str(db_path),
                    },
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(proc_mismatch.returncode, 0)

if __name__ == "__main__":
    unittest.main()
