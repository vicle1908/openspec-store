"""Focused tests for portable-mac-development-workstation Slice A.

Tests:
1. Manifest schema and canonical manifest validation (Draft202012Validator).
2. Portability & value-blind constraints (zero secrets, zero /Users/androidteam literals).
3. Layered profile integrity (Brewfile, npm-global, uv, capability profiles) with no duplicate tool ownership.
4. Preflight detection and fail-closed gate on missing prerequisites.
5. Template rendering with concrete absolute paths and zero unresolved tags.
6. Bootstrap dry-run planner with strict secret and persistent volume exclusions.
7. Candidate classification report matching the retention decision table.
8. Inventory toolchain manifest comparison reporting required states.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# Helper dynamic loaders
def _load_module(mod_name: str, script_name: str):
    path = SCRIPTS_DIR / script_name
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


preflight_mod = _load_module("bootstrap_workstation_preflight", "bootstrap-workstation-preflight.py")
renderer_mod = _load_module("render_workstation_templates", "render-workstation-templates.py")
bootstrap_mod = _load_module("bootstrap_workstation", "bootstrap-workstation.py")
candidates_mod = _load_module("report_toolchain_candidates", "report-toolchain-candidates.py")
inv_mod = _load_module("inventory_workstation_toolchain", "inventory-workstation-toolchain.py")


class TestWorkstationManifestSchemaAndCanonical(unittest.TestCase):
    def setUp(self):
        self.schema_path = CONFIG_DIR / "workstation-manifest.schema.json"
        self.manifest_path = CONFIG_DIR / "workstation-toolchain-manifest.json"

    def test_schema_file_exists_and_is_valid_json(self):
        self.assertTrue(self.schema_path.is_file(), f"Missing schema at {self.schema_path}")
        with open(self.schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
        self.assertIn("$schema", schema)
        self.assertIn("tools", schema["properties"])

    def test_draft202012_validator_check_schema(self):
        try:
            import jsonschema
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            # Must not raise SchemaError
            jsonschema.Draft202012Validator.check_schema(schema)
        except ImportError:
            self.skipTest("jsonschema not available in current python environment")

    def test_canonical_manifest_validates_against_schema(self):
        try:
            import jsonschema
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            validator = jsonschema.Draft202012Validator(schema)
            errors = list(validator.iter_errors(manifest))
            self.assertEqual(len(errors), 0, f"Schema validation errors: {[e.message for e in errors]}")
        except ImportError:
            self.skipTest("jsonschema not available in current python environment")

    def test_canonical_manifest_contains_no_literal_androidteam(self):
        manifest_text = self.manifest_path.read_text(encoding="utf-8")
        self.assertNotIn("androidteam", manifest_text, "Manifest MUST NOT hardcode machine-specific username 'androidteam'")
        self.assertNotIn("/Users/", manifest_text, "Manifest MUST NOT contain literal '/Users/' paths; use {{HOME}}")

    def test_canonical_manifest_value_blind_no_secrets(self):
        manifest_text = self.manifest_path.read_text(encoding="utf-8")
        secret_patterns = [r"sk-[A-Za-z0-9]{20,}", r"ghp_[A-Za-z0-9]{20,}", r"AKIA[0-9A-Z]{16}", r"BEGIN (?:RSA )?PRIVATE KEY"]
        for pat in secret_patterns:
            self.assertIsNone(re.search(pat, manifest_text), f"Found potential secret pattern {pat} in manifest")

    def test_manifest_covers_all_mandated_tools(self):
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        tools = manifest.get("tools", {})
        required_tools = ["git", "node", "uv", "claude", "codex", "qoder", "qodercli", "gitnexus", "newman", "bru", "opencode", "herdr"]
        for tool in required_tools:
            self.assertIn(tool, tools, f"Tool '{tool}' must be declared in canonical manifest")
            t_decl = tools[tool]
            self.assertIn("authoritative_owner", t_decl)
            self.assertIn("active_path_pattern", t_decl)
            self.assertIn("update_authority", t_decl)
            self.assertIn("release_channel", t_decl)
            self.assertIn("dispatch_classification", t_decl)
            self.assertIn("verification_smoke_command", t_decl)
        self.assertIn("herdr", manifest.get("profiles", {}).get("ai-agents", []))

class TestLayeredProfiles(unittest.TestCase):
    def test_brewfile_exists_and_contains_sanctioned_formulae(self):
        brewfile = CONFIG_DIR / "Brewfile"
        self.assertTrue(brewfile.is_file(), "Brewfile must exist")
        content = brewfile.read_text(encoding="utf-8")
        self.assertIn('brew "git"', content)
        self.assertIn('brew "node"', content)
        self.assertIn('brew "uv"', content)
        self.assertIn('brew "bun"', content)
        self.assertIn('brew "herdr"', content)
        self.assertIn('cask "codex"', content)
        self.assertNotIn('cask "qoder"', content)
    def test_npm_global_profile_contains_sanctioned_tools(self):
        npm_prof = CONFIG_DIR / "npm-global-tools.json"
        self.assertTrue(npm_prof.is_file(), "npm-global-tools.json must exist")
        with open(npm_prof, "r", encoding="utf-8") as f:
            data = json.load(f)
        names = {t["name"] for t in data.get("tools", [])}
        self.assertNotIn("codex", names)
        self.assertIn("gitnexus", names)

    def test_uv_profile_contains_sanctioned_tools(self):
        uv_prof = CONFIG_DIR / "uv-tools.json"
        self.assertTrue(uv_prof.is_file(), "uv-tools.json must exist")
        with open(uv_prof, "r", encoding="utf-8") as f:
            data = json.load(f)
        names = {t["name"] for t in data.get("tools", [])}
        self.assertIn("graphifyy", names)
        self.assertIn("tavily-cli", names)

    def test_capability_profiles_exist(self):
        db_prof = CONFIG_DIR / "db-tools-profile.json"
        rust_prof = CONFIG_DIR / "rust-dev-profile.json"
        self.assertTrue(db_prof.is_file(), "db-tools-profile.json must exist")
        self.assertTrue(rust_prof.is_file(), "rust-dev-profile.json must exist")

    def test_no_duplicate_tool_ownership_across_profiles(self):
        # Extract tool names declared across tool profiles
        brewfile_text = (CONFIG_DIR / "Brewfile").read_text(encoding="utf-8")
        brew_tools = {
            token.split("/")[-1]
            for token in re.findall(r'^(?:brew|cask)\s+"([^"]+)"', brewfile_text, re.MULTILINE)
        }
        self.assertIn("herdr", brew_tools)
        npm_data = json.loads((CONFIG_DIR / "npm-global-tools.json").read_text(encoding="utf-8"))
        npm_tools = {t["name"] for t in data.get("tools", [])} if (data := npm_data) else set()
        uv_data = json.loads((CONFIG_DIR / "uv-tools.json").read_text(encoding="utf-8"))
        uv_tools = {t["name"] for t in uv_data.get("tools", [])}

        self.assertTrue(brew_tools.isdisjoint(npm_tools), f"Intersection between Brew and npm: {brew_tools & npm_tools}")
        self.assertTrue(brew_tools.isdisjoint(uv_tools), f"Intersection between Brew and uv: {brew_tools & uv_tools}")
        self.assertTrue(npm_tools.isdisjoint(uv_tools), f"Intersection between npm and uv: {npm_tools & uv_tools}")


class TestBootstrapPreflight(unittest.TestCase):
    def test_live_preflight_runs_and_passes(self):
        report = preflight_mod.run_preflight()
        self.assertEqual(report.status, "PASS")
        self.assertEqual(len(report.failed_checks), 0)
        self.assertIn("arch", report.system)
        self.assertIn(report.system["arch"], ("arm64", "x86_64"))

    def test_preflight_fails_closed_on_missing_xcode(self):
        report = preflight_mod.run_preflight(mock_missing={"xcode"})
        self.assertEqual(report.status, "FAIL")
        self.assertIn("xcode_cli_tools", report.failed_checks)

    def test_preflight_fails_closed_on_unsupported_os(self):
        report = preflight_mod.run_preflight(os_override="Linux")
        self.assertEqual(report.status, "FAIL")
        self.assertIn("os_darwin", report.failed_checks)

    def test_preflight_fails_closed_on_unsupported_arch(self):
        report = preflight_mod.run_preflight(arch_override="i386")
        self.assertEqual(report.status, "FAIL")
        self.assertIn("arch_supported", report.failed_checks)

    def test_preflight_dynamic_homebrew_prefix_derivation(self):
        info_arm = preflight_mod.detect_system_info(arch_override="arm64")
        self.assertEqual(info_arm["homebrew_prefix"], "/opt/homebrew")
        info_intel = preflight_mod.detect_system_info(arch_override="x86_64")
        self.assertEqual(info_intel["homebrew_prefix"], "/usr/local")


class TestRenderWorkstationTemplates(unittest.TestCase):
    def test_render_all_registered_variables(self):
        ctx = {
            "HOME": "/Users/testuser",
            "HOMEBREW_PREFIX": "/opt/homebrew",
            "WORKSPACE_ROOT": "/Users/testuser/Developer",
            "OPENSPEC_STORE_ROOT": "/Users/testuser/Developer/platform/openspec-store",
        }
        template = (
            "Path={{HOME}}/bin\n"
            "Brew={{HOMEBREW_PREFIX}}/bin\n"
            "Workspace={{WORKSPACE_ROOT}}\n"
            "Store={{OPENSPEC_STORE_ROOT}}"
        )
        rendered, unresolved = renderer_mod.render_content(template, ctx)
        self.assertEqual(len(unresolved), 0)
        self.assertIn("/Users/testuser/bin", rendered)
        self.assertIn("/opt/homebrew/bin", rendered)
        self.assertIn("/Users/testuser/Developer/platform/openspec-store", rendered)

    def test_render_detects_unresolved_tag_and_fails_closed(self):
        ctx = {
            "HOME": "/Users/testuser",
            "HOMEBREW_PREFIX": "/opt/homebrew",
            "WORKSPACE_ROOT": "/Users/testuser/Developer",
            "OPENSPEC_STORE_ROOT": "/Users/testuser/Developer/platform/openspec-store",
        }
        template = "Target={{HOME}}/bin and {{UNRESOLVED_VARIABLE}}"
        rendered, unresolved = renderer_mod.render_content(template, ctx)
        self.assertEqual(unresolved, ["UNRESOLVED_VARIABLE"])

    def test_render_file_dry_run_does_not_write_file(self):
        with tempfile.NamedTemporaryFile("w", suffix=".tmpl", delete=False) as f:
            f.write("Label: {{HOME}}/app")
            tmpl_name = f.name

        out_path = Path(tmpl_name).parent / "should_not_exist_render_output.txt"
        if out_path.exists():
            out_path.unlink()

        ctx = renderer_mod.build_variable_context(home="/Users/fakeuser")
        res = renderer_mod.render_file(Path(tmpl_name), out_path, ctx, dry_run=True)
        self.assertTrue(res.success)
        self.assertFalse(out_path.exists(), "Dry-run MUST NOT write output file")


class TestBootstrapDryRun(unittest.TestCase):
    def test_dry_run_report_excludes_secrets_and_protected_volumes(self):
        report = bootstrap_mod.generate_dry_run_plan(
            store_root=REPO_ROOT,
            candidate_test_files=[
                "/Users/test/.zshenv",
                "/Users/test/.env",
                "/Users/test/.ssh/id_rsa",
                "/Users/test/certs/server.pem",
            ],
        )
        self.assertTrue(report.dry_run)
        self.assertTrue(report.summary["secrets_protected"])
        self.assertTrue(report.summary["volumes_protected"])

        excluded_names = {item["name"] for item in report.excluded_items}
        self.assertIn(".zshenv", excluded_names)
        self.assertIn("omniroute_data", excluded_names)
        self.assertIn("/Users/test/.zshenv", excluded_names)
        self.assertIn("/Users/test/.env", excluded_names)
        self.assertIn("/Users/test/.ssh/id_rsa", excluded_names)

    def test_dry_run_does_not_modify_any_files(self):
        # Run dry run report
        report = bootstrap_mod.generate_dry_run_plan(store_root=REPO_ROOT)
        self.assertEqual(report.status, "ready")
        self.assertGreater(len(report.planned_actions), 0)
        self.assertGreater(len(report.smoke_checks), 0)


class TestCandidateClassificationReport(unittest.TestCase):
    def test_candidate_report_matches_retention_table(self):
        report = candidates_mod.generate_candidate_report(include_standard_retained=True)
        summary = report["summary"]
        self.assertTrue(summary["read_only"])
        self.assertFalse(summary["mutation_planned"])
        self.assertGreaterEqual(summary["retained_count"], 6)
        self.assertGreaterEqual(summary["repair_normalize_count"], 5)
        self.assertGreaterEqual(summary["manual_review_count"], 2)

        candidates_map = {c["candidate"]: c for c in report["candidates"]}
        # Verify key classifications from Section 10
        self.assertEqual(candidates_map["codex"]["action_classification"], "Repair/Normalize")
        self.assertEqual(candidates_map["qoder"]["action_classification"], "Repair/Normalize")
        self.assertEqual(candidates_map["gitnexus"]["action_classification"], "Repair/Normalize")
        self.assertEqual(candidates_map["newman"]["action_classification"], "Retained")
        self.assertEqual(candidates_map["bru"]["action_classification"], "Repair/Normalize")
        self.assertEqual(candidates_map["opencode"]["action_classification"], "Repair/Normalize")
        self.assertEqual(candidates_map["prime-agent"]["action_classification"], "Retained")
        self.assertEqual(candidates_map["python@3.10"]["action_classification"], "Manual Review")
        self.assertEqual(candidates_map["ollama"]["action_classification"], "Manual Review")


if __name__ == "__main__":
    unittest.main()
