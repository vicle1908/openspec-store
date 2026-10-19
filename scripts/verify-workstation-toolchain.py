#!/usr/bin/env python3
"""Unified read-only workstation verification runner.

Combines inventory reconciliation, preflight checks, shell/LaunchAgent template audit,
development service port conflict check, and Notion sanitization check into a single
JSON evidence bundle.

Contract:
- Strictly read-only: never modifies any file, kills any process, or mutates state.
- Emits structured JSON evidence bundle with SHA-256 integrity hash.
- Standard library only.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import plistlib
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
CONFIG_DIR = REPO_ROOT / "config"


def _load_script_module(mod_name: str, script_name: str) -> Any:
    """Dynamically load a script from scripts directory."""
    path = SCRIPTS_DIR / script_name
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


# 1. Inventory Reconciliation Check
def check_inventory_reconciliation(manifest_path: Path | None = None) -> dict[str, Any]:
    manifest_p = manifest_path or (CONFIG_DIR / "workstation-toolchain-manifest.json")
    if not manifest_p.is_file():
        return {
            "status": "FAIL",
            "details": f"Manifest not found at {manifest_p}",
            "declared_tools_count": 0,
        }

    try:
        inv_mod = _load_script_module("inventory_workstation_toolchain", "inventory-workstation-toolchain.py")
        if not inv_mod:
            return {"status": "FAIL", "details": "Could not load inventory script"}

        prefix_res = inv_mod.check_prefix_reconciliation("~/.npm-global")
        inventory = inv_mod.inventory_tools()
        auth_recon = inv_mod.evaluate_authority_and_drift("~/.npm-global")
        manifest_res = inv_mod.reconcile_with_manifest(str(manifest_p), inventory, auth_recon.items)
        if not manifest_res:
            return {"status": "FAIL", "details": "Failed to reconcile with manifest"}

        declared_count = manifest_res.get("declared_tools_count", 0)
        aligned_count = manifest_res.get("aligned_count", 0)
        drift_count = manifest_res.get("drift_count", 0)
        missing_count = manifest_res.get("missing_count", 0)
        dup_count = manifest_res.get("duplicate_count", 0)
        unsanc_count = manifest_res.get("unsanctioned_count", 0)
        has_failure = (
            manifest_res.get("status") != "aligned"
            or drift_count > 0
            or missing_count > 0
            or unsanc_count > 0
            or prefix_res.has_split
        )

        return {
            "status": "FAIL" if has_failure else "PASS",
            "manifest_file": str(manifest_p),
            "declared_tools_count": declared_count,
            "aligned_count": aligned_count,
            "drift_count": drift_count,
            "missing_count": missing_count,
            "duplicate_count": dup_count,
            "unsanctioned_count": unsanc_count,
            "prefix_reconciliation": {
                "status": prefix_res.status,
                "has_split": prefix_res.has_split,
                "home_prefix_hijacked": prefix_res.home_prefix_hijacked,
                "home_forbidden_artifacts": prefix_res.home_forbidden_artifacts,
            },
            "summary": manifest_res.get("summary", {}),
            "proposes_deletion": False,
            "details": f"Reconciled {declared_count} declared tools ({aligned_count} aligned, {drift_count} drift, {missing_count} missing, {unsanc_count} unsanctioned, prefix={prefix_res.status})",
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "details": f"Inventory reconciliation error: {e}",
            "declared_tools_count": 0,
        }


# 2. Preflight Check
def check_preflight() -> dict[str, Any]:
    try:
        preflight_mod = _load_script_module("bootstrap_workstation_preflight", "bootstrap-workstation-preflight.py")
        if not preflight_mod:
            return {"status": "FAIL", "details": "Could not load preflight script"}

        report = preflight_mod.run_preflight()
        return {
            "status": report.status,
            "system": report.system,
            "prerequisites": report.prerequisites,
            "failed_checks": report.failed_checks,
            "details": f"Preflight {report.status} ({len(report.prerequisites) - len(report.failed_checks)}/{len(report.prerequisites)} checks passed)",
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "details": f"Preflight error: {e}",
            "failed_checks": ["exception"],
        }


# 3. Shell / LaunchAgent Template Audit
def check_templates() -> dict[str, Any]:
    try:
        renderer_mod = _load_script_module("render_workstation_templates", "render-workstation-templates.py")
        if not renderer_mod:
            return {"status": "FAIL", "details": "Could not load template renderer"}

        launchd_dir = CONFIG_DIR / "launchd"
        templates = list(launchd_dir.glob("*.tmpl")) + list(launchd_dir.glob("*.template"))
        if not templates:
            return {
                "status": "WARN",
                "details": f"No template files found in {launchd_dir}",
                "unresolved_tags_count": 0,
                "audited_templates": [],
            }

        ctx = renderer_mod.build_variable_context()
        audited = []
        total_unresolved = 0
        all_passed = True

        for tmpl_p in templates:
            text = tmpl_p.read_text(encoding="utf-8")
            rendered, unresolved = renderer_mod.render_content(text, ctx)
            total_unresolved += len(unresolved)

            # Validate plist if it is an XML plist
            plist_valid = True
            if rendered.strip().startswith("<?xml") or "<plist" in rendered:
                try:
                    plistlib.loads(rendered.encode("utf-8"))
                except Exception:
                    plist_valid = False
                    all_passed = False

            item = {
                "template": tmpl_p.name,
                "unresolved_tags": unresolved,
                "plist_valid": plist_valid,
                "success": len(unresolved) == 0 and plist_valid,
            }
            audited.append(item)
            if len(unresolved) > 0:
                all_passed = False

        return {
            "status": "PASS" if all_passed else "FAIL",
            "audited_templates_count": len(templates),
            "unresolved_tags_count": total_unresolved,
            "audited_templates": audited,
            "details": f"Audited {len(templates)} templates with {total_unresolved} unresolved tags",
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "details": f"Template audit error: {e}",
            "unresolved_tags_count": -1,
        }

# 4. Port Conflict Check
def check_port_conflicts() -> dict[str, Any]:
    try:
        ports_mod = _load_script_module("check_service_ports", "check-service-ports.py")
        if not ports_mod:
            return {"status": "FAIL", "details": "Could not load service port checker"}

        report = ports_mod.inspect_service_ports()
        return {
            "status": report.get("status", "FAIL"),
            "has_quarantine": report.get("has_quarantine", False),
            "quarantined_processes_count": report.get("quarantined_processes_count", 0),
            "collisions_count": report.get("collisions_count", 0),
            "ports": report.get("ports", {}),
            "docker": report.get("docker"),
            "details": f"Service ports {report.get('status')} ({report.get('collisions_count', 0)} collisions, {report.get('quarantined_processes_count', 0)} quarantined)",
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "details": f"Port conflict check error: {e}",
            "collisions_count": -1,
        }


# 5. Notion Sanitization Check
def check_notion_sanitization() -> dict[str, Any]:
    sync_script = SCRIPTS_DIR / "knowledge-refresh" / "sync-notion-knowledge.sh"
    if not sync_script.is_file():
        return {
            "status": "FAIL",
            "details": f"Sync script not found at {sync_script}",
        }

    results = {}

    # 1. Dynamic home redaction verification
    test_input = "/Users/sample_dev/Developer/repo\n/Users/another_operator/.zshrc\n/Users/some_user\n"
    try:
        cmd = f'source "{sync_script}" && printf "%s" "{test_input}" | sanitize_content'
        out = subprocess.check_output(["bash", "-c", cmd], text=True)
        no_user_literals = "sample_dev" not in out and "another_operator" not in out and "some_user" not in out
        has_tilde = "~/Developer/repo" in out and "~/.zshrc" in out
        results["dynamic_home_redaction"] = "PASS" if (no_user_literals and has_tilde) else "FAIL"
    except Exception as e:
        results["dynamic_home_redaction"] = f"FAIL: {e}"

    # 2. Secret redaction verification
    secret_input = "OPENAI_API_KEY=sk-test12345678901234567890\npostgres://usr:pwd123@localhost/db\n"
    try:
        cmd = f'source "{sync_script}" && printf "%s" "{secret_input}" | sanitize_content'
        out = subprocess.check_output(["bash", "-c", cmd], text=True)
        secret_redacted = "sk-test12345678901234567890" not in out and "pwd123" not in out and "REDACTED" in out
        results["secret_redaction"] = "PASS" if secret_redacted else "FAIL"
    except Exception as e:
        results["secret_redaction"] = f"FAIL: {e}"

    # 3. Residual secret scan verification
    # 3a. Raw token should be rejected (fail-closed)
    try:
        bad_token = "Here is a token: ghp_123456789012345678901234"
        cmd = f'source "{sync_script}" && scan_residual_secrets "{bad_token}"'
        proc = subprocess.run(["bash", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        results["residual_token_fail_closed"] = "PASS" if proc.returncode != 0 else "FAIL"
    except Exception as e:
        results["residual_token_fail_closed"] = f"FAIL: {e}"

    # 3b. Private key should be rejected (fail-closed)
    try:
        bad_key = "-----BEGIN RSA PRIVATE KEY-----\nMIIE...\n-----END RSA PRIVATE KEY-----"
        cmd = f'source "{sync_script}" && scan_residual_secrets "{bad_key}"'
        proc = subprocess.run(["bash", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        results["residual_key_fail_closed"] = "PASS" if proc.returncode != 0 else "FAIL"
    except Exception as e:
        results["residual_key_fail_closed"] = f"FAIL: {e}"

    # 3c. Redacted content should pass
    try:
        good_content = "OPENAI_API_KEY=REDACTED\n# Clean Documentation\n"
        cmd = f'source "{sync_script}" && scan_residual_secrets "{good_content}"'
        proc = subprocess.run(["bash", "-c", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        results["residual_allowlist_pass"] = "PASS" if proc.returncode == 0 else "FAIL"
    except Exception as e:
        results["residual_allowlist_pass"] = f"FAIL: {e}"

    all_pass = all(v == "PASS" for v in results.values())
    return {
        "status": "PASS" if all_pass else "FAIL",
        "script_path": str(sync_script),
        "checks": results,
        "details": "Fail-closed dynamic redaction and residual secret scanning verified",
    }


def run_workstation_verification(manifest_path: Path | None = None) -> dict[str, Any]:
    """Execute unified read-only workstation verification and return evidence bundle."""
    now_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    inv_res = check_inventory_reconciliation(manifest_path)
    preflight_res = check_preflight()
    templates_res = check_templates()
    ports_res = check_port_conflicts()
    notion_res = check_notion_sanitization()

    checks = {
        "inventory_reconciliation": inv_res,
        "preflight": preflight_res,
        "templates": templates_res,
        "port_conflicts": ports_res,
        "notion_sanitization": notion_res,
    }

    statuses = {k: v.get("status", "FAIL") for k, v in checks.items()}
    passed_count = sum(1 for s in statuses.values() if s in ("PASS", "WARN"))
    failed_count = sum(1 for s in statuses.values() if s == "FAIL")

    overall_status = "PASS" if failed_count == 0 else "FAIL"

    checks_json = json.dumps(checks, sort_keys=True)
    evidence_hash = hashlib.sha256(checks_json.encode("utf-8")).hexdigest()

    evidence_bundle = {
        "schema_version": "1.0",
        "generated_at": now_utc,
        "read_only": True,
        "overall_status": overall_status,
        "summary": {
            "total_checks": len(checks),
            "passed_checks": passed_count,
            "failed_checks": failed_count,
            "checks_status": statuses,
        },
        "checks": checks,
        "evidence_hash": evidence_hash,
    }

    return evidence_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Unified read-only workstation toolchain verification.")
    parser.add_argument("--json", action="store_true", default=True, help="Output machine-readable JSON (default: True)")
    parser.add_argument("--output", "-o", help="Write evidence bundle to file")
    parser.add_argument("--manifest", help="Path to workstation-toolchain-manifest.json")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any check fails")
    args = parser.parse_args()

    manifest_p = Path(args.manifest) if args.manifest else None
    bundle = run_workstation_verification(manifest_p)

    json_str = json.dumps(bundle, indent=2)

    if args.output:
        out_p = Path(args.output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_text(json_str + "\n", encoding="utf-8")

    print(json_str)

    if args.strict and bundle.get("overall_status") != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
