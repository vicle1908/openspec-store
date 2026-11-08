#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.15"
# dependencies = []
# ///
"""Reconcile workstation agent CLI coverage declarations against installed binaries.

Standard library only. Read-only by contract: never executes update verbs or removes tools.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from toolchain_updater_registry import get_supported_updater, is_truthy_pause


@dataclass
class AgentCLIRecord:
    name: str
    binary_path: str
    status: str  # 'covered', 'uncovered_declared', 'undeclared'
    source_type: str  # 'package_manager', 'ecosystem_manager', 'vendor_download'
    source_detail: str
    update_verb: str | None
    real_path: str | None = None
    has_update_path: bool = True
    update_path_detail: str | None = None


def resolve_binary_target(binary_path: str) -> str:
    """Resolve active binary target through symlinks and shell wrapper scripts."""
    p = Path(binary_path)
    try:
        resolved = p.resolve()
    except Exception:
        return str(p)

    if not resolved.is_file():
        return str(resolved)

    try:
        with open(resolved, "rb") as f:
            header = f.read(4096)
        if b"\x00" in header:
            return str(resolved)
        content = header.decode("utf-8", errors="ignore")
    except Exception:
        return str(resolved)

    # 1. Qoder entry dispatcher: routes to qodercli or ide
    if "qodercli" in content or p.name == "qoder":
        qcli = shutil.which("qodercli")
        if not qcli:
            for cand in [
                Path.home() / ".local" / "bin" / "qodercli",
                Path.home() / ".qoder" / "bin" / "qodercli" / "qodercli",
                Path("/opt/homebrew/bin/qodercli"),
            ]:
                if cand.is_file() and os.access(cand, os.X_OK):
                    qcli = str(cand)
                    break
        if qcli:
            try:
                return str(Path(qcli).resolve())
            except Exception:
                return str(qcli)

    # 2. General exec wrappers (e.g. exec /path/to/real/binary "$@")
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("exec "):
            parts = line.split()
            if len(parts) > 1:
                target_str = parts[1]
                target_path = Path(target_str)
                if target_path.is_file():
                    return str(target_path.resolve())

    return str(resolved)


def classify_source(binary_path: str) -> tuple[str, str]:
    resolved = resolve_binary_target(binary_path)
    if "/Cellar/" in resolved or "/Caskroom/" in resolved:
        return "package_manager", "Homebrew (formula/cask)"
    elif "/.npm-global/" in resolved or "/home-toolchain/" in resolved:
        return "ecosystem_manager", "npm"
    if "/.local/share/claude/" in resolved or "/.grok/downloads/" in resolved or "/.hermes/" in resolved or "/.pi/" in resolved or "/.kimi-code/" in resolved or "/.qoder/" in resolved:
        return "vendor_download", "vendor release channel"
    p = Path(resolved)
    home = Path.home()
    for parent in [p, *list(p.parents)[:4]]:
        if parent in (home, home / ".local", home / ".local" / "bin"):
            continue
        if (parent / "package.json").is_file():
            return "ecosystem_manager", "npm"
    if "/node_modules/" in resolved:
        return "ecosystem_manager", "npm"
    elif "/Applications/" in resolved:
        return "package_manager", "macOS Application bundle"
    return "vendor_download", "standalone binary"


def find_agent_binary(name: str) -> str | None:
    bin_path = shutil.which(name)
    if bin_path:
        return bin_path
    home = Path.home()
    if name == "qoder":
        cand = home / ".qoder" / "entry" / "qoder"
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    elif name == "claude":
        cand = home / ".local" / "bin" / "claude"
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    elif name == "hermes-agent":
        cand = home / ".local" / "bin" / "hermes-agent"
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    elif name == "pi":
        cand = home / ".pi" / "agent" / "bin" / "pi"
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    elif name == "kimi":
        cand = home / ".kimi-code" / "bin" / "kimi"
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    return None


def evaluate_update_path(
    name: str,
    status: str,
    update_verb: str | None,
    source_type: str,
    source_detail: str,
) -> tuple[bool, str]:
    """Check if the CLI has a compatible supported native update path or manager path."""
    decl = get_supported_updater(name, source_type)
    if status == "covered":
        if not update_verb:
            return False, "covered CLI missing update verb"
        if "npm" in source_detail and update_verb.startswith("brew "):
            return False, f"incompatible update verb: '{update_verb}' for npm-managed installation"
        if "Homebrew" in source_detail and update_verb.startswith("npm "):
            return False, f"incompatible update verb: '{update_verb}' for Homebrew-managed installation"
        if not decl or decl.status != "covered":
            return False, f"unsupported or unverified covered tool: '{name}' for source '{source_type}'"
        if update_verb != decl.supported_verb:
            return False, f"unsupported or unrecognized update command: '{update_verb}' for {name} (expected '{decl.supported_verb}')"
        return True, f"native/delegated update verb: '{update_verb}'"
    if name == "cce":
        return True, "pinned standalone binary (manual/no-op in pipeline)"
    if name == "kilo":
        supported_cmd = decl.supported_verb if decl else "kilo upgrade"
        return True, f"managed by ecosystem manager ({source_detail}; supported CLI: '{supported_cmd}', uncovered in pipeline)"
    if name == "prime-agent":
        return True, f"managed by ecosystem manager ({source_detail}; uncovered in pipeline)"
    if source_type == "package_manager":
        if not decl or decl.status != "uncovered_declared":
            return False, f"unregistered or mismatched package_manager tool: '{name}'"
        return True, f"managed by package manager ({source_detail}; delegating_to={decl.delegating_to})"
    if source_type == "ecosystem_manager":
        return True, f"managed by ecosystem manager ({source_detail})"
    if name == "hermes-agent":
        return True, "governed by Git checkout / hermes update"
    if name == "grok":
        return True, "governed by Homebrew cask grok-build / vendor download channel"
    return False, "lacks native updater and supported package manager"

def audit_background_auto_update_settings() -> dict[str, Any]:
    """Non-destructively audit native background auto-update configuration and environment keys."""
    settings: dict[str, Any] = {
        "environment": {},
        "configurations": {},
    }

    env_keys = [
        "DISABLE_AUTOUPDATER",
        "DISABLE_UPDATES",
        "CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE",
    ]
    for k in env_keys:
        val = os.environ.get(k)
        if val is not None:
            settings["environment"][k] = val

    home = Path.home()

    # Claude settings.json
    claude_settings_path = home / ".claude" / "settings.json"
    if claude_settings_path.is_file():
        try:
            data = json.loads(claude_settings_path.read_text(errors="ignore"))
            claude_keys = {}
            for k in ["autoUpdatesChannel", "DISABLE_AUTOUPDATER", "DISABLE_UPDATES", "autoUpdate"]:
                if k in data:
                    claude_keys[k] = data[k]
            env_block = data.get("env", {})
            if isinstance(env_block, dict):
                for k in ["autoUpdatesChannel", "DISABLE_AUTOUPDATER", "DISABLE_UPDATES"]:
                    if k in env_block:
                        claude_keys[f"env.{k}"] = env_block[k]
            if claude_keys:
                settings["configurations"]["claude_settings"] = {
                    "path": str(claude_settings_path),
                    "settings": claude_keys,
                }
        except Exception:
            pass

    # Claude .claude.json
    claude_json_path = home / ".claude.json"
    if claude_json_path.is_file():
        try:
            data = json.loads(claude_json_path.read_text(errors="ignore"))
            claude_json_keys = {}
            for k in ["autoUpdatesChannel", "autoUpdates", "autoUpdatesProtectedForNative"]:
                if k in data:
                    claude_json_keys[k] = data[k]
            if claude_json_keys:
                settings["configurations"]["claude_json"] = {
                    "path": str(claude_json_path),
                    "settings": claude_json_keys,
                }
        except Exception:
            pass

    # Grok config.toml
    grok_config_path = home / ".grok" / "config.toml"
    if grok_config_path.is_file():
        try:
            content = grok_config_path.read_text(errors="ignore")
            grok_keys = {}
            for line in content.splitlines():
                line = line.strip()
                if line.startswith(("auto_update", "installer")):
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        k = parts[0].strip()
                        v = parts[1].strip().strip('"').strip("'")
                        grok_keys[k] = v
            if grok_keys:
                settings["configurations"]["grok_config"] = {
                    "path": str(grok_config_path),
                    "settings": grok_keys,
                }
        except Exception:
            pass

    is_paused = any(
        is_truthy_pause(settings["environment"][k])
        for k in ("DISABLE_UPDATES", "DISABLE_AUTOUPDATER")
        if k in settings["environment"]
    )
    for cfg_data in settings["configurations"].values():
        cfg_settings = cfg_data.get("settings", {})
        for k in ("DISABLE_UPDATES", "env.DISABLE_UPDATES", "DISABLE_AUTOUPDATER", "env.DISABLE_AUTOUPDATER"):
            if k in cfg_settings and is_truthy_pause(cfg_settings[k]):
                is_paused = True
                break
    settings["is_paused"] = is_paused

    return settings

def reconcile_agent_clis(declared_covered: dict[str, str], declared_uncovered: list[str]) -> list[AgentCLIRecord]:
    known_agents = [
        "claude",
        "codex",
        "opencode",
        "kilo",
        "auggie",
        "qoder",
        "pi",
        "kimi",
        "prime-agent",
        "grok",
        "goose",
        "droid",
        "happy",
        "cursor-agent",
        "hermes-agent",
        "buzz",
        "cce",
        "muse",
        "qwen",
        "ntn",
        "herdr",
        "omp",
    ]

    records: list[AgentCLIRecord] = []

    for name in sorted(known_agents):
        bin_path = find_agent_binary(name)
        if not bin_path:
            continue

        real_path = resolve_binary_target(bin_path)
        src_type, src_detail = classify_source(bin_path)

        if name in declared_covered:
            status = "covered"
            verb = declared_covered[name]
        elif name in declared_uncovered:
            status = "uncovered_declared"
            verb = None
        else:
            status = "undeclared"
            verb = None

        has_up, up_detail = evaluate_update_path(name, status, verb, src_type, src_detail)

        records.append(
            AgentCLIRecord(
                name=name,
                binary_path=bin_path,
                status=status,
                source_type=src_type,
                source_detail=src_detail,
                update_verb=verb,
                real_path=real_path if real_path != bin_path else None,
                has_update_path=has_up,
                update_path_detail=up_detail,
            )
        )

    return records


def main() -> int:
    parser = argparse.ArgumentParser(description="Reconcile agent CLI coverage.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument(
        "--include-uncovered",
        default="droid,goose,grok,prime-agent,happy,cursor-agent,hermes-agent,buzz,cce,kilo,muse,qwen,herdr,omp",
        help="Comma-separated declared uncovered CLIs",
    )
    parser.add_argument(
        "--simulate-initial",
        action="store_true",
        help="Simulate initial state where happy, cursor-agent, hermes-agent, buzz, cce are undeclared",
    )
    args = parser.parse_args()

    covered = {
        "claude": "claude update",
        "codex": "codex update",
        "opencode": "opencode upgrade",
        "auggie": "auggie update --skip-confirmation",
        "qoder": "qoder update",
        "pi": "pi update --self",
        "kimi": "kimi update",
        "ntn": "ntn update",
    }

    if args.simulate_initial:
        uncovered = ["droid", "goose", "grok", "prime-agent", "kilo"]
    else:
        uncovered = [x.strip() for x in args.include_uncovered.split(",") if x.strip()]

    records = reconcile_agent_clis(covered, uncovered)
    undeclared = [r for r in records if r.status == "undeclared"]
    lacking_update = [r for r in records if not r.has_update_path and r.status != "undeclared"]
    bg_settings = audit_background_auto_update_settings()

    if args.json:
        out = {
            "declared_covered": covered,
            "declared_uncovered": uncovered,
            "total_installed": len(records),
            "undeclared_count": len(undeclared),
            "lacking_update_path": [r.name for r in lacking_update],
            "background_settings": bg_settings,
            "records": [asdict(r) for r in records],
        }
        print(json.dumps(out, indent=2))
    else:
        print("=== Workstation Agent CLI Coverage Reconciliation ===")
        print(f"  Total Installed Agents: {len(records)}")
        print(f"  Declared Covered:       {len(covered)} ({', '.join(sorted(covered.keys()))})")
        print(f"  Declared Uncovered:     {len(uncovered)} ({', '.join(sorted(uncovered))})")
        print(f"  Undeclared Count:       {len(undeclared)}")

        print("\nBackground Auto-Update Settings:")
        if bg_settings.get("environment"):
            print("  Environment:")
            for k, v in sorted(bg_settings["environment"].items()):
                print(f"    {k}: is_paused={is_truthy_pause(v)}")
        else:
            print("  Environment: (none set)")

        if bg_settings.get("configurations"):
            print("  Configurations:")
            for cfg_name, cfg in sorted(bg_settings["configurations"].items()):
                settings_str = ", ".join(f"{k}={v}" for k, v in sorted(cfg["settings"].items()))
                print(f"    {cfg_name}: {settings_str} (path: {cfg['path']})")
        else:
            print("  Configurations: (none detected)")

        print("\nInstalled Agent Roster:")
        for r in records:
            tag = f"[{r.status.upper()}]"
            verb = f" (verb: '{r.update_verb}')" if r.update_verb else ""
            real_info = f" (real: {r.real_path})" if r.real_path else ""
            print(f"  {r.name:15} -> {r.binary_path}{real_info} {tag} ({r.source_type}: {r.source_detail}){verb}")

        if lacking_update:
            print("\nDeclared CLIs Lacking Supported Update Path:")
            for item in lacking_update:
                print(f"  - {item.name}: {item.update_path_detail}")

        if undeclared:
            print("\nUndeclared Installations Detected:")
            for u in undeclared:
                print(f"  - {u.name} ({u.binary_path})")

    return 1 if undeclared else 0


if __name__ == "__main__":
    sys.exit(main())
