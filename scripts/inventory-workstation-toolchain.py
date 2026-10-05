#!/usr/bin/env python3
"""Inventory workstation toolchain install locations, detect duplication, and verify ownership.

Standard library only. Read-only by contract: never removes or alters any installation.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


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


@dataclass
class ToolAuthorityItem:
    name: str
    authority: str
    writer: str
    actual_writer: str
    verb: str | None
    update_verb: str | None
    updater_dispatch: str
    delegating_to: str | None
    drift_status: str
    consequence: str | None
    authoritative_path: str
    resolved_path: str
    wrapper_chain: list[str] = field(default_factory=list)
    active_install_root: str | None = None
    target_prefix: str | None = None
    prefix_aligned: bool = True
    documented_channels: list[str] = field(default_factory=list)
    selected_channel: str | None = None
    orthogonal_findings: list[str] = field(default_factory=list)
    evidence_gaps: list[str] = field(default_factory=list)
    auto_updates_config: dict[str, Any] = field(default_factory=dict)
    compatible_command: str | None = None


@dataclass
class AuthorityReconciliation:
    status: str
    drift_count: int
    conflict_count: int
    target_misalignment_count: int
    unknown_count: int
    items: list[ToolAuthorityItem] = field(default_factory=list)

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

def is_path_sanctioned(p: Path) -> bool:
    """Check whether a path or its real destination resides within sanctioned workstation locations."""
    try:
        resolved = p.resolve()
        home = Path.home()
        sanctioned_roots = [
            home / ".npm-global",
            home / ".local" / "share",
            home / ".local" / "bin",
            home / ".hermes",
            home / ".grok",
            Path("/opt/homebrew"),
            Path("/Applications"),
            home / ".pi",
        ]
        for root in sanctioned_roots:
            try:
                r = root.resolve()
                if resolved == r or r in resolved.parents:
                    return True
            except Exception:
                pass
    except Exception:
        pass
    return False

def derive_npm_prefix(install_root: str | Path) -> str:
    """Derive npm prefix dynamically from install root containing node_modules."""
    p = Path(install_root)
    parts = p.parts
    if "node_modules" in parts:
        idx = parts.index("node_modules")
        parent = Path(*parts[:idx])
        if parent.name == "lib":
            return str(parent.parent)
        return str(parent)
    return str(p)


def derive_install_root_and_source(resolved_path: str) -> tuple[str, str]:
    """Derive install root and source detail dynamically from resolved path."""
    p = Path(resolved_path)
    parts = p.parts
    # 1. Homebrew Cellar formula
    if "Cellar" in parts:
        idx = parts.index("Cellar")
        if idx + 2 < len(parts):
            return str(Path(*parts[:idx + 3])), "brew-formula"
        elif idx + 1 < len(parts):
            return str(Path(*parts[:idx + 2])), "brew-formula"
    # 2. Homebrew Caskroom
    if "Caskroom" in parts:
        idx = parts.index("Caskroom")
        if idx + 2 < len(parts):
            return str(Path(*parts[:idx + 3])), "brew-cask"
        elif idx + 1 < len(parts):
            return str(Path(*parts[:idx + 2])), "brew-cask"
    # 3. Node modules package
    if "node_modules" in parts:
        idx = parts.index("node_modules")
        if idx + 1 < len(parts) and parts[idx + 1].startswith("@") and idx + 2 < len(parts):
            pkg_root = Path(*parts[:idx + 3])
            return str(pkg_root), "npm"
        elif idx + 1 < len(parts):
            pkg_root = Path(*parts[:idx + 2])
            return str(pkg_root), "npm"
    if "Applications" in parts:
        for parent in [p] + list(p.parents):
            if parent.suffix == ".app":
                return str(parent), "app_bundle"
        return str(p.parent), "app_bundle"
    # 5. ~/.local/share language / tool manager
    if ".local" in parts and "share" in parts:
        idx = parts.index("share")
        if idx + 1 < len(parts):
            return str(Path(*parts[:idx + 2])), "vendor_download"
    return str(p.parent), "standalone"


def audit_claude_autoupdate() -> dict[str, Any]:
    """Audit Claude Code background auto-update settings non-destructively as-is."""
    cfg: dict[str, Any] = {}
    claude_json = Path.home() / ".claude.json"
    if claude_json.exists():
        try:
            data = json.loads(claude_json.read_text(errors="ignore"))
            for k in ["autoUpdatesChannel", "autoUpdates", "autoUpdatesProtectedForNative"]:
                if k in data:
                    cfg[k] = data[k]
        except Exception:
            pass
    claude_settings = Path.home() / ".claude" / "settings.json"
    if claude_settings.exists():
        try:
            data = json.loads(claude_settings.read_text(errors="ignore"))
            for k in ["autoUpdatesChannel", "autoUpdate"]:
                if k in data:
                    cfg[k] = data[k]
            env_block = data.get("env", {})
            if isinstance(env_block, dict):
                for k in ["autoUpdatesChannel", "DISABLE_AUTOUPDATER", "DISABLE_UPDATES", "CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE"]:
                    if k in env_block:
                        cfg[f"env.{k}"] = env_block[k]
        except Exception:
            pass
    for env_var in ("DISABLE_AUTOUPDATER", "DISABLE_UPDATES", "CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE"):
        if env_var in os.environ:
            cfg[env_var] = os.environ[env_var]
    return cfg


def audit_grok_autoupdate() -> dict[str, Any]:
    """Audit Grok background auto-update and installer settings non-destructively as-is."""
    cfg: dict[str, Any] = {}
    grok_toml = Path.home() / ".grok" / "config.toml"
    if grok_toml.exists():
        try:
            text = grok_toml.read_text()
            for line in text.splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if k in ("installer", "auto_update"):
                        cfg[k] = v
        except Exception:
            pass
    return cfg

def evaluate_authority_and_drift(declared_prefix: str = "~/.npm-global") -> AuthorityReconciliation:
    """Evaluate elected version authority, actual version writers, and drift for workstation tools."""
    home = Path.home()
    target_prefix_resolved = str(Path(os.path.expanduser(declared_prefix)).resolve())

    tools_to_evaluate = [
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
        "droid",
    ]

    documented_channels_map = {
        "claude": [
            "vendor_download: standalone binary installer (curl -fsSL https://code.claude.com/install.sh)",
            "brew-cask: claude-code",
            "npm: @anthropic-ai/claude-code",
        ],
        "codex": [
            "npm: @openai/codex",
            "brew-cask: codex",
        ],
        "opencode": [
            "brew-formula: opencode (anomalyco/tap/opencode)",
            "npm: opencode",
        ],
        "qoder": [
            "vendor_download: ad-hoc wrapper (~/.qoder/entry/qoder)",
            "npm: @qoder-ai/qodercli",
        ],
        "qodercli": [
            "npm: @qoder-ai/qodercli",
        ],
        "prime-agent": [
            "vendor_download: official R2 Mach-O channel (~/.local/bin/prime-agent)",
            "package_wrapper: /opt/homebrew/lib/prime-agent",
        ],
        "grok": [
            "brew-cask: grok-build",
        ],
        "goose": [
            "brew-formula: block-goose-cli",
            "brew-cask: block-goose (GUI application)",
        ],
        "droid": [
            "brew-cask: droid",
        ],
        "kilo": [
            "npm: @kilocode/cli",
        ],
        "auggie": [
            "npm: @augmentcode/auggie",
        ],
        "happy": [
            "npm: happy",
        ],
        "cursor-agent": [
            "brew-cask: cursor-cli",
        ],
        "hermes-agent": [
            "git_checkout: ~/.hermes/hermes-agent",
            "brew-formula: hermes-agent",
        ],
        "buzz": [
            "brew-cask: buzz",
        ],
        "gitnexus": [
            "npm: gitnexus",
        ],
        "bru": [
            "home-toolchain: @usebruno/cli (~/.local/share/home-toolchain)",
            "brew-formula: bruno-cli",
            "npm: @usebruno/cli",
        ],
        "newman": [
            "brew-formula: newman",
            "npm: newman",
        ],
        "cce": [],
        "pi": [
            "vendor_download: managed installer (https://pi.dev/install.sh)",
        ],
    }

    items: list[ToolAuthorityItem] = []

    for name in tools_to_evaluate:
        auth_path = shutil.which(name)
        doc_channels = documented_channels_map.get(name, [])
        orthogonal_findings: list[str] = []
        evidence_gaps: list[str] = []
        auto_cfg: dict[str, Any] = {}

        if not auth_path:
            items.append(
                ToolAuthorityItem(
                    name=name,
                    authority="none",
                    writer="none",
                    actual_writer="none",
                    verb=None,
                    update_verb=None,
                    updater_dispatch="none",
                    delegating_to=None,
                    drift_status="not_installed",
                    consequence=None,
                    authoritative_path="not_found",
                    resolved_path="not_found",
                    wrapper_chain=[],
                    active_install_root=None,
                    target_prefix=None,
                    prefix_aligned=True,
                    documented_channels=doc_channels,
                    selected_channel=None,
                    orthogonal_findings=[],
                    evidence_gaps=[],
                    auto_updates_config={},
                    compatible_command=None,
                )
            )
            continue

        # Trace provenance and wrapper chains
        chain = [auth_path]
        curr = Path(auth_path)
        while curr.is_symlink():
            target = curr.resolve()
            if str(target) not in chain:
                chain.append(str(target))
            curr = target

        if curr.is_file():
            try:
                with open(curr, "rb") as f:
                    header = f.read(256)
                if header.startswith(b"#!"):
                    text = curr.read_text(errors="ignore")
                    if name == "qoder" and "qodercli" in text:
                        qcli = shutil.which("qodercli")
                        if qcli:
                            if qcli not in chain:
                                 chain.append(qcli)
                            qcli_real = str(Path(qcli).resolve())
                            if qcli_real not in chain:
                                chain.append(qcli_real)
                    elif "exec " in text:
                        m = re.search(r"exec\s+([^\s]+)", text)
                        if m:
                            exec_target = m.group(1)
                            if os.path.exists(exec_target) and exec_target not in chain:
                                chain.append(exec_target)
            except Exception:
                pass

        resolved_path = chain[-1]

        # Sanctioned location check
        if not is_path_sanctioned(Path(resolved_path)):
            orthogonal_findings.append(f"Installed outside sanctioned locations: {resolved_path}")
        elif not is_path_sanctioned(Path(auth_path)):
            orthogonal_findings.append(f"Installed outside sanctioned locations: {auth_path}")

        # Tool classification
        if name == "cce":
            authority = "unknown"
            writer = "unknown"
            updater_dispatch = "none"
            update_verb = None
            delegating_to = None
            selected_channel = "standalone binary"
            evidence_gaps = [
                "Standalone Mach-O binary in ~/.local/bin/cce has no package manager receipt, updater subcommand, or documented vendor release channel"
            ]
            drift_status = "unknown"
            consequence = "Authority is unknown; automated mutations are gated until provenance is established"
            active_install_root = str(Path(auth_path).parent)
            prefix_aligned = True
            compatible_command = None

        elif name == "pi":
            authority = "vendor_download"
            writer = "pi"
            updater_dispatch = "native"
            delegating_to = None
            update_verb = "pi update --self"
            selected_channel = "managed installer (https://pi.dev/install.sh)"
            active_install_root = str(home / ".pi" / "agent" / "install")
            prefix_aligned = True
            drift_status = "clean"
            consequence = None
            compatible_command = "pi update --self"

        elif name == "opencode":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            if src == "brew-formula":
                authority = "brew-formula"
                writer = "brew"
                updater_dispatch = "delegating"
                delegating_to = "brew"
                update_verb = "opencode upgrade"
                selected_channel = "brew-formula"
                drift_status = "clean"
                consequence = None
                prefix_aligned = True
                compatible_command = "opencode upgrade"
            else:
                authority = "npm-global"
                writer = "npm"
                updater_dispatch = "native"
                delegating_to = None
                update_verb = "opencode upgrade"
                target_prefix = target_prefix_resolved
                prefix_aligned = active_install_root.startswith(target_prefix)
                drift_status = "clean" if prefix_aligned else "target_misalignment"
                selected_channel = f"npm ({active_install_root})"
                consequence = None if prefix_aligned else f"Active root {active_install_root} misaligned with prefix {target_prefix}"
                compatible_command = "opencode upgrade"
        elif name == "grok":
            auto_cfg = audit_grok_autoupdate()
            dyn_root, _ = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            prefix_aligned = True
            if auto_cfg.get("installer") == "internal" and auto_cfg.get("auto_update") == "true":
                authority = "conflict"
                writer = "competing: grok (internal) vs brew (cask)"
                updater_dispatch = "native"
                delegating_to = None
                update_verb = "grok update"
                selected_channel = "competing (internal updater vs brew cask grok-build)"
                drift_status = "conflict"
                consequence = "Uncoordinated competing writers: grok internal auto-updater competes with Homebrew cask grok-build"
                compatible_command = "brew upgrade --cask grok-build"
            else:
                authority = "brew-cask"
                writer = "brew"
                updater_dispatch = "delegating"
                delegating_to = "brew"
                update_verb = None
                selected_channel = "brew-cask (grok-build)"
                drift_status = "clean"
                consequence = None
                compatible_command = "brew upgrade --cask grok-build"
        elif name == "claude":
            auto_cfg = audit_claude_autoupdate()
            authority = "native"
            writer = "claude"
            updater_dispatch = "native"
            delegating_to = None
            selected_channel = "vendor_download (native standalone)"
            dyn_root, _ = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            prefix_aligned = True
            is_paused = (auto_cfg.get("DISABLE_UPDATES") == "1" or auto_cfg.get("env.DISABLE_UPDATES") == "1")
            if is_paused:
                update_verb = None
                drift_status = "clean"
                consequence = "Updates paused by user policy (DISABLE_UPDATES=1)"
                compatible_command = None
            else:
                update_verb = "claude update"
                drift_status = "clean"
                consequence = None
                compatible_command = "claude update"
        elif name == "codex":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            authority = "npm-global"
            writer = "npm"
            updater_dispatch = "native"
            delegating_to = None
            update_verb = "codex update"
            target_prefix = target_prefix_resolved
            if not active_install_root.startswith(target_prefix):
                prefix_aligned = False
                drift_status = "target_misalignment"
                selected_channel = f"npm (active: {active_install_root})"
                consequence = f"Update action writes to {declared_prefix} while active binary resolves to {active_install_root}, leaving active binary stale and unupdated"
                compatible_command = f"npm install -g --prefix {derive_npm_prefix(active_install_root)} @openai/codex"
            else:
                prefix_aligned = True
                drift_status = "clean"
                selected_channel = f"npm ({declared_prefix})"
                consequence = None
                compatible_command = "codex update"
        elif name == "gitnexus":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            authority = "npm-global"
            writer = "npm"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = None
            target_prefix = target_prefix_resolved
            if not active_install_root.startswith(target_prefix):
                prefix_aligned = False
                drift_status = "target_misalignment"
                selected_channel = f"npm (active: {active_install_root})"
                consequence = f"Installed in {active_install_root} instead of declared prefix {declared_prefix}; update actions targeting {declared_prefix} will not update active executable"
                compatible_command = f"npm install -g --prefix {declared_prefix} gitnexus"
            else:
                prefix_aligned = True
                drift_status = "clean"
                selected_channel = f"npm ({declared_prefix})"
                consequence = None
                compatible_command = None
        elif name == "qoder":
            authority = "native"
            writer = "qoder"
            updater_dispatch = "native"
            delegating_to = None
            update_verb = "qoder update"
            selected_channel = "vendor_download (ad-hoc wrapper at ~/.qoder/entry/qoder)"
            drift_status = "clean"
            consequence = None
            active_install_root = str(Path(auth_path).parent)
            prefix_aligned = True
            compatible_command = "qoder update"

        elif name == "qodercli":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            authority = "npm-global"
            writer = "npm"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = None
            target_prefix = target_prefix_resolved
            if not active_install_root.startswith(target_prefix):
                prefix_aligned = False
                drift_status = "target_misalignment"
                selected_channel = f"npm (active: {active_install_root})"
                consequence = f"Installed in {active_install_root} instead of declared prefix {declared_prefix}"
                compatible_command = f"npm install -g --prefix {declared_prefix} @qoder-ai/qodercli"
            else:
                prefix_aligned = True
                drift_status = "clean"
                selected_channel = f"npm ({declared_prefix})"
                consequence = None
                compatible_command = None

        elif name == "prime-agent":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            prefix_aligned = True
            if "/opt/homebrew" in resolved_path or "package_wrapper" in src:
                authority = "package-wrapper"
                writer = "package-manager"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                selected_channel = f"package_wrapper ({active_install_root})"
                drift_status = "clean"
                consequence = None
                compatible_command = None
            else:
                authority = "native"
                writer = "prime-agent"
                updater_dispatch = "native"
                delegating_to = None
                update_verb = "prime-agent update"
                selected_channel = "vendor_download (official R2 Mach-O channel)"
                drift_status = "clean"
                consequence = None
                compatible_command = "prime-agent update"
        elif name in ("kilo", "auggie"):
            authority = "native"
            writer = "npm"
            updater_dispatch = "native"
            delegating_to = None
            update_verb = "kilo update" if name == "kilo" else "auggie update --skip-confirmation"
            selected_channel = "npm-global"
            active_install_root = str(Path(resolved_path).parent.parent)
            target_prefix = target_prefix_resolved
            prefix_aligned = active_install_root.startswith(target_prefix)
            drift_status = "clean" if prefix_aligned else "target_misalignment"
            consequence = None if prefix_aligned else f"Active root {active_install_root} misaligned with prefix {target_prefix}"
            compatible_command = update_verb

        elif name == "hermes-agent":
            authority = "native"
            writer = "git"
            updater_dispatch = "native"
            delegating_to = None
            update_verb = "hermes update"
            selected_channel = "git_checkout (~/.hermes/hermes-agent)"
            drift_status = "clean"
            consequence = None
            active_install_root = str(home / ".hermes" / "hermes-agent")
            prefix_aligned = True
            compatible_command = "hermes update"

        elif name == "happy":
            authority = "npm-global"
            writer = "npm"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = None
            selected_channel = "npm-global"
            active_install_root = str(Path(resolved_path).parent.parent)
            target_prefix = target_prefix_resolved
            prefix_aligned = active_install_root.startswith(target_prefix)
            drift_status = "clean" if prefix_aligned else "target_misalignment"
            consequence = None if prefix_aligned else f"Active root {active_install_root} misaligned with prefix {target_prefix}"
            compatible_command = None

        elif name == "bru":
            authority = "home-toolchain"
            writer = "npm"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = None
            selected_channel = "home-toolchain (~/.local/share/home-toolchain)"
            active_install_root = str(home / ".local" / "share" / "home-toolchain")
            prefix_aligned = True
            drift_status = "clean"
            consequence = None
            compatible_command = None

        elif name in ("goose", "newman"):
            authority = "brew-formula"
            writer = "brew"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = None
            selected_channel = "brew-formula"
            active_install_root = "/opt/homebrew/Cellar"
            prefix_aligned = True
            drift_status = "clean"
            consequence = None
            compatible_command = None

        elif name in ("droid", "cursor-agent", "buzz"):
            authority = "brew-cask"
            writer = "brew"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = None
            selected_channel = "brew-cask"
            active_install_root = "/opt/homebrew/Caskroom" if name != "buzz" else "/Applications"
            prefix_aligned = True
            drift_status = "clean"
            consequence = None
            compatible_command = None

        else:
            authority = "unknown"
            writer = "unknown"
            updater_dispatch = "unknown"
            delegating_to = None
            update_verb = None
            selected_channel = "unknown"
            active_install_root = None
            prefix_aligned = True
            drift_status = "unknown"
            consequence = "Tool authority unclassified"
            compatible_command = None

        items.append(
            ToolAuthorityItem(
                name=name,
                authority=authority,
                writer=writer,
                actual_writer=writer,
                verb=update_verb,
                update_verb=update_verb,
                updater_dispatch=updater_dispatch,
                delegating_to=delegating_to,
                drift_status=drift_status,
                consequence=consequence,
                authoritative_path=auth_path,
                resolved_path=resolved_path,
                wrapper_chain=chain,
                active_install_root=active_install_root,
                target_prefix=target_prefix_resolved if authority == "npm-global" else None,
                prefix_aligned=prefix_aligned,
                documented_channels=doc_channels,
                selected_channel=selected_channel,
                orthogonal_findings=orthogonal_findings,
                evidence_gaps=evidence_gaps,
                auto_updates_config=auto_cfg,
                compatible_command=compatible_command,
            )
        )

    target_misaligned = [i for i in items if i.drift_status == "target_misalignment"]
    conflicts = [i for i in items if i.drift_status == "conflict"]
    unknowns = [i for i in items if i.drift_status == "unknown"]
    has_drift = (len(target_misaligned) > 0) or (len(conflicts) > 0) or (len(unknowns) > 0)
    status = "drift_detected" if has_drift else "reconciled"

    return AuthorityReconciliation(
        status=status,
        drift_count=len(target_misaligned) + len(conflicts),
        conflict_count=len(conflicts),
        target_misalignment_count=len(target_misaligned),
        unknown_count=len(unknowns),
        items=items,
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
        "droid",
    ]

    preferred_sources = {
        "codex": ("cask codex", True),
        "claude": ("cask claude-code", True),
        "cursor-agent": ("cask cursor-cli", True),
        "droid": ("cask droid", True),
        "hermes-agent": ("formula hermes-agent", True),
        "buzz": ("cask buzz", True),
        "grok": ("cask grok-build", True),
        "goose": ("formula block-goose-cli", True),
        "opencode": ("formula opencode (third-party tap)", True),
        "qoder": ("none", False),
        "qodercli": ("cask qoder", True),
        "Claude-Fable": ("none", False),
        "kilo": ("none", False),
        "auggie": ("none", False),
        "cce": ("none", False),
        "pi": ("vendor_download: managed installer", True),
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
        elif tool_name == "pi":
            pkg_keys.append("@earendil-works/pi-coding-agent")

        for loc_name, loc_dir in locations.items():
            for key in pkg_keys:
                candidate = loc_dir / key
                if candidate.exists():
                    sz = get_dir_size_bytes(candidate)
                    is_auth = False
                    if auth_path != "not_found":
                        try:
                            resolved_auth = Path(auth_path).resolve()
                            resolved_cand = candidate.resolve()
                            is_auth = (
                                resolved_auth == candidate
                                or candidate in resolved_auth.parents
                                or resolved_auth == resolved_cand
                                or resolved_cand in resolved_auth.parents
                            )
                        except Exception:
                            pass

                    is_symlink_target = False
                    if brew_bin.is_symlink():
                        try:
                            brew_target = brew_bin.resolve()
                            resolved_cand = candidate.resolve()
                            is_symlink_target = (
                                brew_target == candidate
                                or candidate in brew_target.parents
                                or brew_target == resolved_cand
                                or resolved_cand in brew_target.parents
                            )
                        except Exception:
                            pass

                    copies.append(
                        ToolCopy(
                            location_path=str(candidate),
                            owning_manager=loc_name,
                            size_bytes=sz,
                            size_human=format_bytes(sz),
                            is_authoritative=is_auth,
                            is_symlinked_from_brew_bin=is_symlink_target,
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

    auth_reconciliation = evaluate_authority_and_drift(args.declared_prefix)

    if args.json:
        data = {
            "prefix_reconciliation": asdict(prefix_check),
            "tools": [asdict(t) for t in inventory],
            "authority_reconciliation": asdict(auth_reconciliation),
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

        reconciled = [i for i in auth_reconciliation.items if i.drift_status == "clean"]
        print("\n=== Version Authority & Drift Reconciliation ===")
        print(f"  Status:                      {auth_reconciliation.status.upper()}")
        print(f"  Total Evaluated Tools:       {len(auth_reconciliation.items)}")
        print(f"  Reconciled / Clean:          {len(reconciled)}")
        print(f"  Target Misalignments:        {auth_reconciliation.target_misalignment_count}")
        print(f"  Authority Conflicts:         {auth_reconciliation.conflict_count}")
        print(f"  Unknown Authority:           {auth_reconciliation.unknown_count}")
        print("\nTool Authority Roster:")
        for it in auth_reconciliation.items:
            status_tag = f"[{it.drift_status.upper()}]"
            verb_info = f", verb: '{it.update_verb}'" if it.update_verb else ""
            disp_info = f", dispatch: {it.updater_dispatch}"
            if it.delegating_to:
                disp_info += f" -> {it.delegating_to}"
            print(f"  {it.name:15} -> authority: {it.authority:14} (writer: {it.writer}{verb_info}{disp_info}) {status_tag}")
            if it.consequence:
                print(f"                     Consequence:   {it.consequence}")
            if it.target_prefix and not it.prefix_aligned:
                print(f"                     Active root:   {it.active_install_root}")
                print(f"                     Target prefix: {it.target_prefix}")
            if it.orthogonal_findings:
                for fnd in it.orthogonal_findings:
                    print(f"                     Orthogonal:    {fnd}")
            if it.evidence_gaps:
                for gap in it.evidence_gaps:
                    print(f"                     Evidence gaps: {gap}")
            if it.compatible_command and not it.prefix_aligned:
                print(f"                     Compatible:    {it.compatible_command}")

        print("\nPolicy Enforcement: Proposes deletion = False (Strictly read-only; explicit authorization required)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
