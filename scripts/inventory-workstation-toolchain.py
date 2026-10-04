#!/usr/bin/env python3
"""Inventory workstation toolchain install locations, detect duplication, and verify ownership.

Standard library only. Read-only by contract: never removes or alters any installation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path


def get_dir_size_bytes(path: Path) -> int:
    """Calculate directory size in bytes."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size_bytes(Path(entry.path))
    except (OSError, PermissionError):
        pass
    return total


def format_bytes(n: int) -> str:
    """Format bytes into human readable format."""
    if n < 1024:
        return f"{n} B"
    for unit in ("KiB", "MiB", "GiB", "TiB"):
        n /= 1024
        if n < 1024:
            return f"{n:.2f} {unit}"
    return f"{n:.2f} PiB"


@dataclass
class ToolCopy:
    location_path: str
    owning_manager: str  # 'npm-global', 'brew-cask', 'brew-formula', 'home-toolchain', 'adhoc'
    size_bytes: int
    size_human: str
    is_authoritative: bool
    is_symlinked_from_brew_bin: bool


@dataclass
class ToolInventoryItem:
    name: str
    authoritative_path: str
    copies: list[ToolCopy] = field(default_factory=list)
    has_duplication: bool = False
    preferred_source: str = "none"  # formula / cask name or 'none'
    preferred_source_available: bool = False
    is_homebrew_adjacent: bool = False
    name_collision: str | None = None
    estimated_reclaimable_bytes: int = 0
    estimated_reclaimable_human: str = "0 B"
    proposes_deletion: bool = False


@dataclass
class PrefixReconciliation:
    npm_config_prefix: str
    maintenance_pipeline_prefix: str
    declared_prefix: str
    has_split: bool
    status: str


def check_prefix_reconciliation(declared_prefix: str) -> PrefixReconciliation:
    try:
        res = subprocess.run(["npm", "config", "get", "prefix"], capture_output=True, text=True, check=True)
        npm_prefix = res.stdout.strip()
    except Exception:
        npm_prefix = "unknown"

    pipeline_prefix = str(Path(os.path.expanduser("~/.npm-global")).resolve())
    declared_resolved = str(Path(os.path.expanduser(declared_prefix)).resolve())
    npm_resolved = str(Path(os.path.expanduser(npm_prefix)).resolve()) if npm_prefix != "unknown" else "unknown"

    has_split = (npm_resolved != declared_resolved) or (npm_resolved != pipeline_prefix)
    status = "split_detected" if has_split else "reconciled"

    return PrefixReconciliation(
        npm_config_prefix=npm_prefix,
        maintenance_pipeline_prefix=pipeline_prefix,
        declared_prefix=declared_prefix,
        has_split=has_split,
        status=status,
    )


def inventory_tools() -> list[ToolInventoryItem]:
    home = Path.home()
    
    # Target search roots
    locations = {
        "npm-global": home / ".npm-global" / "lib" / "node_modules",
        "homebrew": Path("/opt/homebrew/lib/node_modules"),
        "home-toolchain": home / ".local" / "share" / "home-toolchain" / "node_modules",
        "adhoc-local": home / ".local" / "lib" / "node_modules",
    }

    # Tools to evaluate
    tools_to_check = [
        "gitnexus",
        "codex",
        "qodercli",
        "qoder",
        "prime-agent",
        "bru",
        "newman",
        "claude",
        "grok",
        "goose",
        "opencode",
        "kilo",
        "auggie",
        "happy",
        "cursor-agent",
        "hermes-agent",
        "buzz",
        "cce",
        "pi",
    ]

    preferred_sources = {
        "codex": ("cask codex", True),
        "claude": ("cask claude", True),
        "cursor-agent": ("cask cursor-cli", True),
        "droid": ("cask droid", True),
        "hermes-agent": ("formula hermes-agent", True),
        "buzz": ("cask buzz", True),
        "grok": ("cask grok-build", True),
        "goose": ("formula block-goose-cli", True),
        "opencode": ("formula opencode (third-party tap)", True),
        "Claude-Fable": ("none", False),
        "kilo": ("none", False),
        "auggie": ("none", False),
        "cce": ("none", False),
        "pi": ("none", False),
        "prime-agent": ("none (official R2 Mach-O channel)", False),
        "happy": ("none", False),
    }

    name_collisions = {
        "grok": "Homebrew formula 'grok' is an unrelated deprecated regex tool; official agent CLI is cask 'grok-build'",
        "opencode": "Homebrew formula 'opencode' originates from a third-party tap and shadows 'homebrew/core/opencode'",
    }

    results: list[ToolInventoryItem] = []

    for tool_name in tools_to_check:
        auth_path = shutil.which(tool_name) or "not_found"
        pref_src, pref_avail = preferred_sources.get(tool_name, ("none", False))
        collision = name_collisions.get(tool_name)

        copies: list[ToolCopy] = []
        is_hb_adjacent = False

        # Check symlink in /opt/homebrew/bin
        brew_bin = Path(f"/opt/homebrew/bin/{tool_name}")
        if brew_bin.is_symlink():
            try:
                target = brew_bin.resolve()
                if "node_modules" in str(target) or ".npm" in str(target):
                    is_hb_adjacent = True
            except Exception:
                pass

        # Check npm locations
        pkg_keys = [tool_name]
        if tool_name == "codex":
            pkg_keys.append("@openai/codex")
        elif tool_name == "qodercli" or tool_name == "qoder":
            pkg_keys.extend(["@qoder-ai/qodercli", "@qoder-ai/qoder"])
        elif tool_name == "bru":
            pkg_keys.append("@usebruno/cli")

        for loc_name, loc_dir in locations.items():
            for key in pkg_keys:
                candidate = loc_dir / key
                if candidate.exists():
                    sz = get_dir_size_bytes(candidate)
                    is_auth = False
                    if auth_path != "not_found":
                        try:
                            resolved_auth = Path(auth_path).resolve()
                            is_auth = str(candidate) in str(resolved_auth)
                        except Exception:
                            pass
                    
                    copies.append(
                        ToolCopy(
                            location_path=str(candidate),
                            owning_manager=loc_name,
                            size_bytes=sz,
                            size_human=format_bytes(sz),
                            is_authoritative=is_auth,
                            is_symlinked_from_brew_bin=is_hb_adjacent,
                        )
                    )

        # Check single primary if not found in npm dirs
        if not copies and auth_path != "not_found":
            resolved_auth = Path(auth_path).resolve()
            sz = resolved_auth.stat().st_size if resolved_auth.exists() else 0
            manager = "brew" if "/Cellar/" in str(resolved_auth) or "/Caskroom/" in str(resolved_auth) else "system"
            copies.append(
                ToolCopy(
                    location_path=str(resolved_auth),
                    owning_manager=manager,
                    size_bytes=sz,
                    size_human=format_bytes(sz),
                    is_authoritative=True,
                    is_symlinked_from_brew_bin=False,
                )
            )

        has_dups = len(copies) > 1
        est_reclaim = sum(c.size_bytes for c in copies if not c.is_authoritative) if has_dups else 0

        results.append(
            ToolInventoryItem(
                name=tool_name,
                authoritative_path=auth_path,
                copies=copies,
                has_duplication=has_dups,
                preferred_source=pref_src,
                preferred_source_available=pref_avail,
                is_homebrew_adjacent=is_hb_adjacent,
                name_collision=collision,
                estimated_reclaimable_bytes=est_reclaim,
                estimated_reclaimable_human=format_bytes(est_reclaim),
                proposes_deletion=False,
            )
        )

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory workstation toolchain install locations.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--declared-prefix", default="~/.npm-global", help="Declared npm global prefix")
    args = parser.parse_args()

    prefix_check = check_prefix_reconciliation(args.declared_prefix)
    inventory = inventory_tools()

    if args.json:
        data = {
            "prefix_reconciliation": asdict(prefix_check),
            "tools": [asdict(t) for t in inventory],
            "proposes_deletion": False,
        }
        print(json.dumps(data, indent=2))
    else:
        print("=== Workstation Prefix Reconciliation ===")
        print(f"  npm config get prefix:       {prefix_check.npm_config_prefix}")
        print(f"  maintenance pipeline prefix: {prefix_check.maintenance_pipeline_prefix}")
        print(f"  declared prefix:             {prefix_check.declared_prefix}")
        print(f"  Status:                      {prefix_check.status.upper()}")
        print("\n=== Workstation Toolchain Inventory ===")
        for item in inventory:
            dup_tag = f" [DUPLICATES: {len(item.copies)} copies, reclaimable ~{item.estimated_reclaimable_human}]" if item.has_duplication else ""
            print(f"Tool: {item.name:15} -> {item.authoritative_path}{dup_tag}")
            for c in item.copies:
                role = "AUTHORITATIVE" if c.is_authoritative else "duplicate"
                adj = " (symlinked from /opt/homebrew/bin)" if c.is_symlinked_from_brew_bin else ""
                print(f"    [{c.owning_manager:14}] {c.location_path} ({c.size_human}) -> {role}{adj}")
            if item.preferred_source != "none":
                print(f"    preferred_source: {item.preferred_source}")
            if item.name_collision:
                print(f"    name_collision:   {item.name_collision}")
        print("\nPolicy Enforcement: Proposes deletion = False (Strictly read-only; explicit authorization required)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
