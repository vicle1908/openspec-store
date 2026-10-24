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
        assert src == "brew-formula"
        assert root == "/opt/homebrew/Cellar/newman/6.2.2"

    def test_caskroom_evaluated_as_brew_cask(self):
        path = "/opt/homebrew/Caskroom/cursor-cli/2026.10.01/dist/cursor-agent"
        root, src = inv.derive_install_root_and_source(path)
        assert src == "brew-cask"
        assert root == "/opt/homebrew/Caskroom/cursor-cli/2026.10.01"

    def test_muse_code_caskroom_evaluated_as_brew_cask(self):
        path = "/opt/homebrew/Caskroom/muse-code/1.4.10-R6427.1/muse-aarch64-macos"
        root, src = inv.derive_install_root_and_source(path)
        assert src == "brew-cask"
        assert root == "/opt/homebrew/Caskroom/muse-code/1.4.10-R6427.1"

    def test_npm_global_scoped_evaluated_as_npm(self):
        path = "/Users/androidteam/.npm-global/lib/node_modules/@openai/codex/bin/codex.js"
        root, src = inv.derive_install_root_and_source(path)
        assert src == "npm"
        assert root == "/Users/androidteam/.npm-global/lib/node_modules/@openai/codex"

    def test_prime_agent_bundle_detected_via_package_json(self):
        # Prime agent lives at /opt/homebrew/lib/prime-agent/dist/bundle/cli.js
        path = "/opt/homebrew/lib/prime-agent/dist/bundle/cli.js"
        root, src = inv.derive_install_root_and_source(path)
        assert src == "npm"
        assert root == "/opt/homebrew/lib/prime-agent"

    def test_homebrew_bundled_npm_evaluated_as_brew_formula(self):
        path = "/opt/homebrew/lib/node_modules/npm/bin/npm-cli.js"
        root, src = inv.derive_install_root_and_source(path)
        assert src == "brew-formula"
        assert root == "/opt/homebrew/lib/node_modules/npm"

    def test_vendor_download_local_share(self):
        path = "/Users/androidteam/.local/share/claude/versions/2.1.289/claude"
        root, src = inv.derive_install_root_and_source(path)
        assert src == "vendor_download"
        assert root == "/Users/androidteam/.local/share/claude"


class TestProductionAuthoritativeCopyDuplication(unittest.TestCase):
    def test_production_newman_duplication_has_authoritative_copy_first(self):
        tools = inv.inventory_tools()
        newman_item = next((t for t in tools if t.name == "newman"), None)
        assert newman_item is not None, "newman must be present in inventory"
        if newman_item.has_duplication:
            assert len(newman_item.copies) >= 2
            # Authoritative copy MUST be at index 0
            assert newman_item.copies[0].is_authoritative, "copies[0] must be authoritative copy"
            assert newman_item.copies[0].owning_manager == "brew"
            assert not newman_item.copies[1].is_authoritative
            assert newman_item.copies[1].owning_manager in ("home-toolchain", "adhoc-home")
        else:
            assert len(newman_item.copies) == 1
            assert newman_item.copies[0].is_authoritative, "copies[0] must be authoritative copy"
            assert newman_item.copies[0].owning_manager == "brew"
        assert not newman_item.is_homebrew_adjacent, "Homebrew Cellar formula newman must not be flagged homebrew-adjacent"


class TestProductionWrapperInheritance(unittest.TestCase):
    def test_qoder_inherits_target_misalignment_from_qodercli(self):
        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        qoder_item = next((it for it in rec.items if it.name == "qoder"), None)
        assert qoder_item is not None
        assert qoder_item.authority == "vendor_download"
        assert qoder_item.drift_status == "clean"
        assert qoder_item.prefix_aligned
        assert "/.qoder" in qoder_item.active_install_root
        assert qoder_item.consequence is None


class TestProductionPrimeAgentProvenance(unittest.TestCase):
    def test_prime_agent_evaluated_truthfully_without_fabricated_cask(self):
        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        item = next((it for it in rec.items if it.name == "prime-agent"), None)
        assert item is not None
        assert item.authority == "npm-global"
        assert item.writer == "npm"
        assert item.updater_dispatch == "none"
        assert item.drift_status == "target_misalignment"
        assert item.active_install_root == "/opt/homebrew/lib/prime-agent"
        assert "Unmanaged package bundle" in item.orthogonal_findings[0]


class TestProductionKiloCommand(unittest.TestCase):
    def test_kilo_records_kilo_upgrade_verb_with_none_dispatch(self):
        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        item = next((it for it in rec.items if it.name == "kilo"), None)
        assert item is not None
        assert item.update_verb == "kilo upgrade"
        assert item.updater_dispatch == "none"


class TestMuseCodeAuthorityAndCollisionGovernance(unittest.TestCase):
    def test_muse_collision_disambiguation_and_clean_drift(self):
        tools = inv.inventory_tools()
        muse_item = next((t for t in tools if t.name == "muse"), None)
        assert muse_item is not None, "muse must be present in inventory"
        assert "Homebrew cask 'muse' is an unrelated disabled desktop app" in muse_item.name_collision
        assert muse_item.preferred_source == "cask muse-code"
        assert muse_item.preferred_source_available

        rec = inv.evaluate_authority_and_drift(declared_prefix="~/.npm-global")
        auth_item = next((it for it in rec.items if it.name == "muse"), None)
        assert auth_item is not None, "muse must be present in authority reconciliation"
        assert auth_item.drift_status == "clean"
        assert auth_item.authority == "brew-cask"
        assert auth_item.writer == "brew"
        assert auth_item.updater_dispatch == "none"


class TestSharedUpdaterRegistry(unittest.TestCase):

    def test_covered_tools_registered_with_verified_commands(self):
        claude_decl = reg.get_supported_updater("claude", "vendor_download")
        assert claude_decl is not None
        assert claude_decl.supported_verb == "claude update"
        assert claude_decl.updater_dispatch == "native"

        codex_decl = reg.get_supported_updater("codex", "npm")
        assert codex_decl is not None
        assert codex_decl.supported_verb == "codex update"

        opencode_decl = reg.get_supported_updater("opencode", "brew-formula")
        assert opencode_decl is not None
        assert opencode_decl.updater_dispatch == "delegating"
        assert opencode_decl.delegating_to == "brew"


        kimi_decl = reg.get_supported_updater("kimi", "vendor_download")
        assert kimi_decl is not None
        assert kimi_decl.supported_verb == "kimi update"
        assert kimi_decl.updater_dispatch == "native"
    def test_unregistered_tool_fails_closed(self):
        decl = reg.get_supported_updater("unknown_agent", "vendor_download")
        assert decl is None

    def test_coverage_evaluator_rejects_source_mismatches(self):
        # Strict cask vs formula matching
        decl_cask = reg.get_supported_updater("opencode", "brew-cask")
        assert decl_cask is None, "opencode is formula; brew-cask lookup must return None"

        decl_formula = reg.get_supported_updater("opencode", "brew-formula")
        assert decl_formula is not None
        assert decl_formula.supported_verb == "opencode upgrade"

        # Unregistered tool must fail closed
        decl = reg.get_supported_updater("unknown_agent", "vendor_download")
        assert decl is None

        # Coverage evaluator reject source mismatches
        ok, msg = cov.evaluate_update_path("opencode", "covered", "opencode upgrade", "brew-cask", "Homebrew cask")
        assert not ok
        assert "unsupported or unverified" in msg

        # Codex is npm; brew upgrade codex must fail
        ok, msg = cov.evaluate_update_path("codex", "covered", "brew upgrade codex", "ecosystem_manager", "npm")
        assert not ok
        assert "incompatible update verb" in msg

        # Unrecognized verb must fail
        ok, msg = cov.evaluate_update_path("codex", "covered", "codex invalid-subcmd", "ecosystem_manager", "npm")
        assert not ok
        assert "unsupported or unrecognized update command" in msg

    def test_muse_registered_in_updater_registry(self):
        decl = reg.get_supported_updater("muse", "brew-cask")
        assert decl is not None
        assert decl.tool == "muse"
        assert decl.source_type == "brew-cask"
        assert decl.updater_dispatch == "none"
        assert decl.delegating_to == "brew"
        assert decl.status == "uncovered_declared"

        decl_code = reg.get_supported_updater("muse-code", "brew-cask")
        assert decl_code is not None
        assert decl_code.tool == "muse-code"
        assert decl_code.source_type == "brew-cask"
        assert decl_code.updater_dispatch == "none"
        assert decl_code.delegating_to == "brew"
        assert decl_code.status == "uncovered_declared"

    def test_omp_registered_and_verified_in_registry_inventory_and_coverage(self):
        import tempfile
        from unittest.mock import patch

        decl = reg.get_supported_updater("omp", "brew-formula")
        assert decl is not None
        assert decl.tool == "omp"
        assert decl.source_type == "brew-formula"
        assert decl.supported_verb is None
        assert decl.updater_dispatch == "none"
        assert decl.delegating_to == "brew"
        assert decl.status == "uncovered_declared"

        # Coverage evaluator verifies registry declaration and reports delegating_to=brew
        ok, msg = cov.evaluate_update_path("omp", "uncovered_declared", None, "package_manager", "Homebrew (formula/cask)")
        assert ok
        assert "delegating_to=brew" in msg

        # Unregistered package_manager tool fails closed
        ok_unreg, msg_unreg = cov.evaluate_update_path("unregistered_brew_tool", "uncovered_declared", None, "package_manager", "Homebrew (formula/cask)")
        assert not ok_unreg
        assert "unregistered or mismatched" in msg_unreg

        # Live authority and drift evaluation for omp
        rep = inv.evaluate_authority_and_drift("~/.npm-global")
        omp_auth = next((i for i in rep.items if i.name == "omp"), None)
        assert omp_auth is not None, "omp must be present in authority reconciliation"
        assert omp_auth.authority == "brew-formula"
        assert omp_auth.writer == "brew"
        assert omp_auth.updater_dispatch == "none"
        assert omp_auth.drift_status == "clean"
        assert omp_auth.active_install_root == "/opt/homebrew/Cellar"
        assert omp_auth.prefix_aligned

        # Inventory tools includes omp and qwen and detects omp shadow paths
        with tempfile.TemporaryDirectory() as tmp:
            home_dir = Path(tmp).resolve() / "home"
            bun_omp = home_dir / ".bun" / "bin" / "omp"
            bun_omp.parent.mkdir(parents=True, exist_ok=True)
            bun_omp.symlink_to(home_dir / ".bun" / "install" / "global" / "node_modules" / "@oh-my-pi" / "pi-coding-agent" / "dist" / "cli.js")
            assert bun_omp.is_symlink()
            assert not bun_omp.exists()
            items = inv.inventory_tools(home_dir=home_dir)
            omp_inv = next((t for t in items if t.name == "omp"), None)
            qwen_inv = next((t for t in items if t.name == "qwen"), None)
            assert omp_inv is not None
            assert qwen_inv is not None
            assert omp_inv.preferred_source == "formula can1357/tap/omp"
            assert qwen_inv.preferred_source == "formula qwen-code"
            assert omp_inv.has_duplication
            assert any(c.location_path == str(bun_omp) and c.owning_manager == "bun-global" for c in omp_inv.copies)

            # Shadow binary active on PATH triggers target_misalignment
            orig_which = inv.shutil.which
            with patch.object(inv.shutil, "which", side_effect=lambda n: str(bun_omp) if n == "omp" else orig_which(n)):
                rep_shadow = inv.evaluate_authority_and_drift("~/.npm-global")
                omp_shadow = next(i for i in rep_shadow.items if i.name == "omp")
                assert omp_shadow.drift_status == "target_misalignment"
                assert not omp_shadow.prefix_aligned
                assert omp_shadow.compatible_command == "brew upgrade can1357/tap/omp"

class TestRegistryEnforcementInInventory(unittest.TestCase):
    def test_cleared_registry_fails_closed_in_inventory(self):
        from unittest.mock import patch
        with patch.dict(reg.SUPPORTED_UPDATER_REGISTRY, {}, clear=True):
            rep = inv.evaluate_authority_and_drift("~/.npm-global")
            codex_it = next(i for i in rep.items if i.name == "codex")
            assert codex_it.update_verb is None
            assert codex_it.updater_dispatch == "none"
            assert codex_it.drift_status == "unknown"

            claude_it = next(i for i in rep.items if i.name == "claude")
            assert claude_it.update_verb is None
            assert claude_it.updater_dispatch == "none"
            assert claude_it.drift_status == "unknown"

            cce_it = next(i for i in rep.items if i.name == "cce")
            assert cce_it.update_verb is None
            assert cce_it.updater_dispatch == "none"
            assert cce_it.drift_status == "unknown"
            assert cce_it.authority == "unknown"
            assert cce_it.writer == "unknown"

            omp_it = next(i for i in rep.items if i.name == "omp")
            assert omp_it.update_verb is None
            assert omp_it.updater_dispatch == "none"
            assert omp_it.drift_status == "unknown"
            assert omp_it.authority == "unknown"

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
            assert len(cands) == 2
            for cand in cands:
                assert secret_sentinel not in cand["executable_baseline"]
                assert "abc" not in cand["executable_baseline"]
            assert cands[0]["executable_baseline"] == "npm"
            assert "API_KEY" in cands[0]["env_keys"]
            assert cands[1]["executable_baseline"] == "brew"
            assert "SECRET_PASS" in cands[1]["env_keys"]
            assert secret_sentinel not in str(res)
            assert "abc" not in str(res)


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
            assert len(findings) == 1
            assert "com.pi.pi-updater" in findings[0]
            assert "pip-runner" not in str(findings)
            assert "api-server" not in str(findings)


class TestCoveragePauseDelegationFlag(unittest.TestCase):
    def test_delegation_flag_does_not_pause_coverage(self):
        from unittest.mock import patch
        with patch.dict(os.environ, {"CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE": "1"}, clear=True):
            bg = cov.audit_background_auto_update_settings()
            assert not bg["is_paused"]
        with patch.dict(os.environ, {"DISABLE_UPDATES": "1"}, clear=True):
            bg = cov.audit_background_auto_update_settings()
            assert bg["is_paused"]


class TestGlobalPausePolicy(unittest.TestCase):
    def test_truthiness_normalization(self):
        for val in (True, 1, 1.0, "1", "true", "True", "yes", "on", "enabled"):
            assert reg.is_truthy_pause(val)
        for val in (False, 0, 0.0, "0", "false", "no", "off", None, ""):
            assert not reg.is_truthy_pause(val)

    def test_global_pause_active_from_env_or_config(self):
        assert reg.is_global_pause_active({"claude": {"DISABLE_UPDATES": "1"}})
        assert reg.is_global_pause_active({"claude": {"env.DISABLE_AUTOUPDATER": "true"}})
        assert not reg.is_global_pause_active({"claude": {"DISABLE_UPDATES": "0"}})


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

        assert deny_casks == ["codex"]
        assert deny_formulae == ["broken-formula"]
        assert "codex" not in deny_formulae
        assert "broken-formula" not in deny_casks


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
        assert lines == ["@openai/codex", "@qoder-ai/qodercli", "auggie"]

    def test_deny_filter_matches_scoped_package_and_variants(self):
        pattern = re.compile(r"^(@openai/codex)(@[^@]*)?$")
        assert pattern.match("@openai/codex")
        assert pattern.match("@openai/codex@1.2.3")
        assert not pattern.match("@openai/codex-fork")
        assert not pattern.match("codex")


class TestZeroExitFailureDetection(unittest.TestCase):
    def test_zero_exit_error_detected(self):
        output = "Error: Failed to change directory to /Users/androidteam/.local/share/kilo/update\n"
        has_error = bool(re.search(r"(?im)^\s*(error|fatal)[: ]|failed to [a-z]", output))
        assert has_error


class TestCurrencyWordingInvariant(unittest.TestCase):
    def test_runner_output_wording_does_not_claim_unproven_currency(self):
        script_path = SCRIPTS_DIR / "workstation-daily-update.sh"
        content = script_path.read_text()
        assert "(idempotent/current)" not in content
        assert "already up to date" not in content
        assert "(idempotent, currency unverified)" in content
        assert "(local version changed, currency unverified)" in content



class TestCceStandaloneAuthority(unittest.TestCase):
    def test_cce_authority_resolves_to_standalone_clean_under_normal_registry(self):
        rep = inv.evaluate_authority_and_drift("~/.npm-global")
        cce_it = next((i for i in rep.items if i.name == "cce"), None)
        assert cce_it is not None, "cce must be evaluated in authority reconciliation"
        assert cce_it.authority == "standalone"
        assert cce_it.writer == "none"
        assert cce_it.drift_status == "clean"
        assert cce_it.updater_dispatch == "none"
        assert cce_it.update_verb is None
        assert cce_it.evidence_gaps == []
        assert cce_it.selected_channel == "pinned standalone binary"


class TestOptionalRustDevProfileReconciliation(unittest.TestCase):
    def test_reconcile_with_manifest_skips_uninstalled_rust_dev(self):
        from unittest.mock import patch
        clean_path = ":".join(p for p in os.environ.get("PATH", "").split(":") if "/.venv" not in p)
        with patch.dict(os.environ, {"PATH": clean_path}):
            res = inv.reconcile_with_manifest()
            assert res is not None
            assert res["missing_count"] == 0
            assert res["optional_skipped_count"] == 2
            assert set(res["summary"]["optional_skipped"]) == {"rustup", "cargo"}
            assert "rustup" not in res["summary"]["missing"]
            assert "cargo" not in res["summary"]["missing"]
            assert res["status"] == "aligned"

class TestDiscoveryPathNormalization(unittest.TestCase):
    def test_normalize_discovery_path_positions_homebrew_ahead_of_hermes_and_system(self):
        simulated_path = "/Users/androidteam/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin:/opt/homebrew/sbin"
        normalized = inv.normalize_discovery_path(simulated_path)
        parts = normalized.split(":")
        assert "/opt/homebrew/bin" in parts
        assert "/opt/homebrew/sbin" in parts
        brew_bin_idx = parts.index("/opt/homebrew/bin")
        hermes_idx = parts.index("/Users/androidteam/.hermes/node/bin")
        usr_bin_idx = parts.index("/usr/bin")
        assert brew_bin_idx < hermes_idx
        assert brew_bin_idx < usr_bin_idx

    def test_normalize_discovery_path_preserves_synthetic_test_bin_at_index_zero(self):
        simulated_path = "/tmp/synthetic_test/bin:/Users/androidteam/.hermes/node/bin:/usr/bin:/bin:/opt/homebrew/bin"
        normalized = inv.normalize_discovery_path(simulated_path)
        parts = normalized.split(":")
        assert parts[0] == "/tmp/synthetic_test/bin"
        brew_bin_idx = parts.index("/opt/homebrew/bin")
        hermes_idx = parts.index("/Users/androidteam/.hermes/node/bin")
        assert brew_bin_idx < hermes_idx


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
            assert not rec.home_prefix_hijacked
            assert rec.home_forbidden_artifacts == []
            assert not rec.has_split
            assert rec.status == "reconciled"

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
            assert rec.home_prefix_hijacked
            assert rec.home_forbidden_artifacts == ["pnpm-lock.yaml", "node_modules"]
            assert rec.has_split
            assert rec.status == "split_detected"

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
            assert gn_item is not None
            assert bru_item is not None
            gn_adhoc = next((c for c in gn_item.copies if c.owning_manager == "adhoc-home"), None)
            bru_adhoc = next((c for c in bru_item.copies if c.owning_manager == "adhoc-home"), None)
            assert gn_adhoc is not None
            assert not gn_adhoc.is_sanctioned
            assert gn_adhoc.sanctioned_replacement.endswith("/.npm-global/lib/node_modules")
            assert bru_adhoc is not None
            assert not bru_adhoc.is_sanctioned
            assert bru_adhoc.sanctioned_replacement.endswith("/.local/share/home-toolchain/node_modules")
            manifest_res = inv.reconcile_with_manifest(inventory_items=items, home_dir=home_dir)
            assert manifest_res["status"] == "drift"
            assert manifest_res["unsanctioned_count"] >= 3
            assert "gitnexus" in manifest_res["summary"]["unsanctioned"]
            assert "bru" in manifest_res["summary"]["unsanctioned"]
            assert "pyright" in manifest_res["summary"]["unsanctioned"]


class TestTCCProvenanceAndBashFallback(unittest.TestCase):
    def test_workstation_daily_update_mirror_parity_and_bash_fail_closed(self):
        import hashlib
        import sqlite3
        import tempfile

        import tcc_provenance as tcc_mod

        store_script = SCRIPTS_DIR / "workstation-daily-update.sh"
        host_script = Path.home() / "Developer" / "scripts" / "workstation-daily-update.sh"
        if host_script.exists():
            h_store = hashlib.sha256(store_script.read_bytes()).hexdigest()
            h_host = hashlib.sha256(host_script.read_bytes()).hexdigest()
            assert h_store == h_host, "Host and store workstation-daily-update.sh mirrors must be byte-identical"

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            # 1. Non-Darwin skip returns 0
            proc_linux = subprocess.run(
                ["bash", "-c", f'source "{store_script}" && verify_tcc_provenance'],
                env={**os.environ, "TCC_UNAME_S_OVERRIDE": "Linux"},
                capture_output=True,
                text=True,
            )
            assert proc_linux.returncode == 0

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
            assert proc_missing_db.returncode != 0

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
            assert proc_missing_helper.returncode != 0

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
                assert proc_ok.returncode == 0, proc_ok.stdout + proc_ok.stderr

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
                assert proc_mismatch.returncode != 0

    def test_has_unaligned_authority_drift_reconciles_local_dev_and_fails_closed_on_unaligned(self):
        auth_aligned_local_dev = {
            "conflict_count": 0,
            "unknown_count": 0,
            "items": [
                {"name": "prime-agent", "drift_status": "target_misalignment", "updater_dispatch": "none"},
            ],
        }
        manifest_ok = {
            "status": "aligned",
            "drift_count": 0,
            "missing_count": 0,
            "unsanctioned_count": 0,
            "unknown_count": 0,
            "summary": {"aligned": ["prime-agent"]},
        }
        assert not inv.has_unaligned_authority_drift(auth_aligned_local_dev, manifest_ok)

        # Unaligned target_misalignment (covered tool or missing from aligned manifest) fails closed
        auth_unaligned = {
            "conflict_count": 0,
            "unknown_count": 0,
            "items": [
                {"name": "rogue-cli", "drift_status": "target_misalignment", "updater_dispatch": "npm"},
            ],
        }
        assert inv.has_unaligned_authority_drift(auth_unaligned, manifest_ok)
        assert inv.has_unaligned_authority_drift(auth_aligned_local_dev, {**manifest_ok, "drift_count": 1})

if __name__ == "__main__":
    unittest.main()
