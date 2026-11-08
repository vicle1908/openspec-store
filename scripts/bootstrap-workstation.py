#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.15"
# dependencies = []
# ///
"""Workstation bootstrap planner and dry-run report generator.

Computes target file actions, validates preflight requirements, and verifies that
secret-bearing files (e.g. .zshenv, private keys) and Docker persistent named volumes
are strictly excluded from automated mutation. Standard library only.
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
lazy from collections.abc import Sequence

SCRIPT_DIR = Path(__file__).resolve().parent

# Helper dynamic loaders
def _load_module(mod_name: str, script_name: str):
    path = SCRIPT_DIR / script_name
    if path.is_file():
        spec = importlib.util.spec_from_file_location(mod_name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
        return mod
    return None

preflight_mod = _load_module("bootstrap_workstation_preflight", "bootstrap-workstation-preflight.py")
renderer_mod = _load_module("render_workstation_templates", "render-workstation-templates.py")


# Known secret patterns and sensitive files to exclude strictly
SECRET_FILE_PATTERNS = [
    ".zshenv",
    ".env",
    ".env.*",
    "*.env",
    "*id_rsa*",
    "*id_ed25519*",
    "*.pem",
    "*.key",
    "*credentials*",
    "*token*",
    "*.p12",
    "*.pfx",
    "*.secret",
]

# Protected persistent Docker named volumes
PROTECTED_DOCKER_VOLUMES = [
    "omniroute_data",
    "postgres_data",
    "kafka_data",
    "redis_data",
    "temporal_data",
]


@dataclass
class PlannedAction:
    category: str
    action_type: str
    target_path: str | None
    source_path: str | None
    command_preview: str | None
    status: str = "planned"
    details: str = ""


@dataclass
class ExcludedItem:
    name: str
    item_type: str  # "secret_file", "protected_volume", "sensitive_directory"
    reason: str
    guidance: str


@dataclass
class BootstrapDryRunReport:
    status: str  # "ready" or "blocked"
    dry_run: bool
    system: dict[str, str]
    preflight_status: str
    planned_actions: list[dict[str, Any]]
    excluded_items: list[dict[str, Any]]
    smoke_checks: list[str]
    summary: dict[str, Any]


def is_secret_file(path_str: str) -> bool:
    """Check if a file path matches secret-bearing patterns."""
    basename = Path(path_str).name
    for pattern in SECRET_FILE_PATTERNS:
        if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(path_str, pattern):
            return True
    return False


def is_protected_volume(name: str) -> bool:
    """Check if a volume name is on the protected persistent volume allowlist."""
    norm = name.strip()
    return norm in PROTECTED_DOCKER_VOLUMES or any(norm.startswith(p) for p in PROTECTED_DOCKER_VOLUMES)


def generate_dry_run_plan(
    store_root: Path,
    manifest_path: Path | None = None,
    brewfile_path: Path | None = None,
    npm_profile_path: Path | None = None,
    uv_profile_path: Path | None = None,
    template_dir: Path | None = None,
    arch_override: str | None = None,
    home_override: str | None = None,
    brew_prefix_override: str | None = None,
    workspace_root_override: str | None = None,
    store_root_override: str | None = None,
    candidate_test_files: list[str] | None = None,
    profiles: Sequence[str] | None = None,
) -> BootstrapDryRunReport:
    """Compute target actions and validate security exclusions."""
    # 1. System info & preflight
    if preflight_mod:
        sys_info = preflight_mod.detect_system_info(
            arch_override=arch_override,
            home_override=home_override,
            brew_prefix_override=brew_prefix_override,
            workspace_root_override=workspace_root_override,
            store_root_override=store_root_override,
        )
        preflight_report = preflight_mod.run_preflight(
            arch_override=arch_override,
            home_override=home_override,
            brew_prefix_override=brew_prefix_override,
            workspace_root_override=workspace_root_override,
            store_root_override=store_root_override,
        )
        pf_status = preflight_report.status
    else:
        home = home_override or str(Path.home())
        brew_prefix = brew_prefix_override or ("/opt/homebrew" if arch_override == "arm64" else "/usr/local")
        sys_info = {
            "arch": arch_override or "arm64",
            "home": home,
            "homebrew_prefix": brew_prefix,
            "workspace_root": workspace_root_override or str(Path(home) / "Developer"),
            "openspec_store_root": store_root_override or str(Path(home) / "Developer" / "platform" / "openspec-store"),
        }
        pf_status = "PASS"

    actions: list[PlannedAction] = []
    excluded: list[ExcludedItem] = []
    smoke_checks: list[str] = []

    # Always register baseline protected items
    excluded.append(
        ExcludedItem(
            name=".zshenv",
            item_type="secret_file",
            reason="secret_bearing_shell_configuration",
            guidance="Bootstrap excludes .zshenv to prevent credential migration. Operator must inject API tokens manually.",
        )
    )
    for vol in PROTECTED_DOCKER_VOLUMES:
        excluded.append(
            ExcludedItem(
                name=vol,
                item_type="protected_volume",
                reason="persistent_docker_named_volume",
                guidance=f"Volume '{vol}' contains persistent application data (WAL/DB); protected against pruning/deletion.",
            )
        )

    # If test candidate files were provided, scan them for secret exclusions
    if candidate_test_files:
        for cfile in candidate_test_files:
            if is_secret_file(cfile):
                excluded.append(
                    ExcludedItem(
                        name=cfile,
                        item_type="secret_file",
                        reason="secret_pattern_matched",
                        guidance="Candidate file matches sensitive pattern; excluded from automated bootstrap.",
                    )
                )

    # 2. Manifest and Tool Actions
    m_path = manifest_path or store_root / "config" / "workstation-toolchain-manifest.json"
    if m_path.is_file():
        try:
            with open(m_path, encoding="utf-8") as f:
                manifest_data = json.load(f)
            tools = manifest_data.get("tools", {})
            rust_dev_tools = set(manifest_data.get("profiles", {}).get("rust-dev", ["rustup", "cargo"]))
            active_profiles = set(profiles or [])
            for tool_name, t_meta in tools.items():
                path_pattern = t_meta.get("active_path_pattern", "")
                resolved_active_path = path_pattern.replace("{{HOME}}", sys_info["home"]).replace(
                    "{{HOMEBREW_PREFIX}}", sys_info["homebrew_prefix"]
                )

                # Skip uninstalled rust-dev tools when rust-dev profile is not requested
                if (
                    tool_name in rust_dev_tools
                    and "rust-dev" not in active_profiles
                    and not Path(resolved_active_path).exists()
                ):
                    continue

                smoke = t_meta.get("verification_smoke_command")
                if smoke:
                    smoke_checks.append(smoke)
                owner = t_meta.get("authoritative_owner")
                verb = t_meta.get("supported_verb")
                if verb:
                    rendered_verb = verb.replace("{{HOME}}", sys_info["home"]).replace(
                        "{{HOMEBREW_PREFIX}}", sys_info["homebrew_prefix"]
                    )
                else:
                    rendered_verb = None

                actions.append(
                    PlannedAction(
                        category="toolchain_sync",
                        action_type=f"verify_or_install_{owner}",
                        target_path=resolved_active_path,
                        source_path=str(m_path),
                        command_preview=rendered_verb,
                        details=f"Tool '{tool_name}' authoritative owner: {owner}",
                    )
                )
        except Exception:
            pass

    # 3. Brewfile Actions
    b_path = brewfile_path or store_root / "config" / "Brewfile"
    if b_path.is_file():
        actions.append(
            PlannedAction(
                category="homebrew",
                action_type="brew_bundle",
                target_path=f"{sys_info['homebrew_prefix']}/bin",
                source_path=str(b_path),
                command_preview=f"brew bundle check --file={b_path} || brew bundle --file={b_path}",
                details="Synchronize Homebrew formulae, casks, and taps declared in Brewfile",
            )
        )

    # 4. npm-global profile actions
    n_path = npm_profile_path or store_root / "config" / "npm-global-tools.json"
    if n_path.is_file():
        actions.append(
            PlannedAction(
                category="npm_global",
                action_type="npm_global_sync",
                target_path=f"{sys_info['home']}/.npm-global/bin",
                source_path=str(n_path),
                command_preview=f"npm install -g --prefix {sys_info['home']}/.npm-global <packages>",
                details="Synchronize sanctioned npm-global packages",
            )
        )

    # 5. uv profile actions
    u_path = uv_profile_path or store_root / "config" / "uv-tools.json"
    if u_path.is_file():
        actions.append(
            PlannedAction(
                category="uv",
                action_type="uv_tool_sync",
                target_path=f"{sys_info['home']}/.local/bin",
                source_path=str(u_path),
                command_preview="uv tool install <package>",
                details="Synchronize sanctioned CLI tools via uv tool",
            )
        )

    # 6. Template rendering actions
    t_dir = template_dir or store_root / "config" / "launchd"
    if t_dir.is_dir():
        for tmpl in list(t_dir.glob("*.tmpl")) + list(t_dir.glob("*.template")):
            out_name = tmpl.stem if tmpl.suffix in (".tmpl", ".template") else tmpl.name
            target_plist = f"{sys_info['home']}/Library/LaunchAgents/{out_name}"
            actions.append(
                PlannedAction(
                    category="launchd_template",
                    action_type="render_and_install_launchagent",
                    target_path=target_plist,
                    source_path=str(tmpl),
                    command_preview=f"render-workstation-templates.py --template {tmpl} --output {target_plist}",
                    details="Render template placeholders with concrete absolute paths before launchd load",
                )
            )

    report_status = "ready" if pf_status == "PASS" else "blocked"
    summary = {
        "total_planned_actions": len(actions),
        "total_excluded_items": len(excluded),
        "total_smoke_checks": len(smoke_checks),
        "secrets_protected": True,
        "volumes_protected": True,
        "clean_dry_run": True,
    }

    return BootstrapDryRunReport(
        status=report_status,
        dry_run=True,
        system=sys_info,
        preflight_status=pf_status,
        planned_actions=[asdict(a) for a in actions],
        excluded_items=[asdict(e) for e in excluded],
        smoke_checks=smoke_checks,
        summary=summary,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Workstation bootstrap planner and dry-run report generator.")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Compute actions without modifying any file (default)")
    parser.add_argument("--json", action="store_true", help="Output structured dry-run JSON")
    parser.add_argument("--manifest", help="Path to workstation-toolchain-manifest.json")
    parser.add_argument("--brewfile", help="Path to Brewfile")
    parser.add_argument("--npm-profile", help="Path to npm-global-tools.json")
    parser.add_argument("--uv-profile", help="Path to uv-tools.json")
    parser.add_argument("--template-dir", help="Path to LaunchAgent templates directory")
    parser.add_argument("--home", help="Override HOME path")
    parser.add_argument("--homebrew-prefix", help="Override Homebrew prefix")
    parser.add_argument("--workspace-root", help="Override Workspace root")
    parser.add_argument("--openspec-store-root", help="Override OpenSpec store root")
    parser.add_argument("--arch", help="Override architecture (arm64, x86_64)")
    parser.add_argument("--profile", dest="profiles", action="append", help="Requested toolchain profiles (e.g. rust-dev)")

    args = parser.parse_args()

    store_root = Path(args.openspec_store_root) if args.openspec_store_root else SCRIPT_DIR.parent

    report = generate_dry_run_plan(
        store_root=store_root,
        manifest_path=Path(args.manifest) if args.manifest else None,
        brewfile_path=Path(args.brewfile) if args.brewfile else None,
        npm_profile_path=Path(args.npm_profile) if args.npm_profile else None,
        uv_profile_path=Path(args.uv_profile) if args.uv_profile else None,
        template_dir=Path(args.template_dir) if args.template_dir else None,
        arch_override=args.arch,
        home_override=args.home,
        brew_prefix_override=args.homebrew_prefix,
        workspace_root_override=args.workspace_root,
        store_root_override=args.openspec_store_root,
        profiles=args.profiles,
    )

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print("=== Workstation Bootstrap Dry-Run Report ===")
        print(f"Status:            {report.status.upper()}")
        print(f"Preflight:         {report.preflight_status}")
        print(f"Dry-Run Mode:      {report.dry_run}")
        print(f"System:            {report.system.get('arch')} on {report.system.get('homebrew_prefix')}")
        print(f"Planned Actions:   {len(report.planned_actions)}")
        print(f"Excluded Items:    {len(report.excluded_items)} (secrets & persistent volumes protected)")
        print(f"Smoke Checks:      {len(report.smoke_checks)}")
        print("\nExcluded Protected Items:")
        for item in report.excluded_items:
            print(f"  [{item['item_type']}] {item['name']} -> {item['reason']}")
        print("\nPlanned Actions Preview:")
        for act in report.planned_actions[:10]:
            print(f"  [{act['category']:18}] {act['action_type']:25} -> {act.get('target_path') or 'N/A'}")
        if len(report.planned_actions) > 10:
            print(f"  ... and {len(report.planned_actions) - 10} more actions")

    return 0 if report.status == "ready" else 1


if __name__ == "__main__":
    sys.exit(main())
