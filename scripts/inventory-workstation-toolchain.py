#!/usr/bin/env python3
"""Inventory workstation toolchain install locations, detect duplication, and verify ownership.

Standard library only. Read-only by contract: never removes or alters any installation.
"""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

# Add script directory for shared updater registry import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from toolchain_updater_registry import (  # noqa: E402
    get_supported_updater,
    is_global_pause_active,
)

# Ensure ~/.qoder/entry, ~/.kimi-code/bin, and /opt/homebrew/opt/libpq/bin are on PATH during discovery
_extra_paths = [
    str(Path.home() / ".qoder" / "entry"),
    str(Path.home() / ".kimi-code" / "bin"),
    "/opt/homebrew/opt/libpq/bin",
]


def normalize_discovery_path(raw_path: str | None = None, brew_dirs: list[str] | None = None) -> str:
    """Normalize PATH so that /opt/homebrew/bin and /opt/homebrew/sbin precede lower-priority dirs.

    Lower-priority directories include /usr/bin, /bin, /usr/sbin, /sbin, and isolated agent
    runtimes (e.g. ~/.hermes/node/bin).
    If /opt/homebrew/bin and /opt/homebrew/sbin exist on disk and appear after any lower-priority
    directory or are missing, they are placed immediately ahead of the first lower-priority
    directory, preserving any synthetic test directories (e.g. tmp_path/bin) prepended at index 0.
    """
    path_val = raw_path if raw_path is not None else os.environ.get("PATH", "")
    parts = [p for p in path_val.split(os.pathsep) if p]

    def _is_lower(p: str) -> bool:
        norm = os.path.normpath(p)
        return norm in ("/usr/bin", "/bin", "/usr/sbin", "/sbin") or "/.hermes/" in norm or "/.venv/" in norm or norm.endswith("/.venv/bin")

    lower_indices = [i for i, p in enumerate(parts) if _is_lower(p)]
    first_lower = lower_indices[0] if lower_indices else len(parts)

    # Ensure _extra_paths exist in parts; if missing, place before first_lower
    missing_extra = [ep for ep in _extra_paths if ep not in parts and Path(ep).is_dir()]
    if missing_extra:
        parts = parts[:first_lower] + missing_extra + parts[first_lower:]
        lower_indices = [i for i, p in enumerate(parts) if _is_lower(p)]
        first_lower = lower_indices[0] if lower_indices else len(parts)

    if brew_dirs is None:
        brew_candidates = ["/opt/homebrew/bin", "/opt/homebrew/sbin"]
        existing_brew = [b for b in brew_candidates if Path(b).is_dir()]
    else:
        existing_brew = brew_dirs

    if existing_brew and lower_indices:
        needs_move = False
        for b in existing_brew:
            if b not in parts or parts.index(b) > first_lower:
                needs_move = True
                break
        if needs_move:
            parts = [p for p in parts if p not in existing_brew]
            first_lower = next((i for i, p in enumerate(parts) if _is_lower(p)), len(parts))
            parts = parts[:first_lower] + existing_brew + parts[first_lower:]
    elif existing_brew and not lower_indices:
        for b in existing_brew:
            if b not in parts:
                parts.append(b)

    result = os.pathsep.join(parts)
    if raw_path is None:
        os.environ["PATH"] = result
    return result


normalize_discovery_path()


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
    owning_manager: str  # 'npm-global', 'brew-cask', 'brew-formula', 'home-toolchain', 'adhoc-local', 'adhoc-home'
    size_bytes: int
    size_human: str
    is_authoritative: bool
    is_symlinked_from_brew_bin: bool
    is_sanctioned: bool = True
    sanctioned_replacement: str | None = None


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
    unsanctioned_copies: list[str] = field(default_factory=list)


@dataclass
class PrefixReconciliation:
    npm_config_prefix: str
    maintenance_pipeline_prefix: str
    declared_prefix: str
    has_split: bool
    status: str
    home_prefix_hijacked: bool = False
    home_forbidden_artifacts: list[str] = field(default_factory=list)

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
    scheduled_writers: dict[str, Any] = field(default_factory=dict)

FORBIDDEN_HOME_ARTIFACTS = (
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "pnpm-workspace.yaml",
    "bun.lock",
    "bun.lockb",
    "yarn.lock",
    "node_modules",
)


def check_prefix_reconciliation(
    declared_prefix: str,
    home_dir: Path | None = None,
    workspace_dir: Path | None = None,
) -> PrefixReconciliation:
    try:
        res = subprocess.run(["npm", "config", "get", "prefix"], capture_output=True, text=True, check=True)
        npm_prefix = res.stdout.strip()
    except Exception:
        npm_prefix = "unknown"

    home_p = (home_dir or Path.home()).resolve()
    ws_p = (workspace_dir or (home_p / "Developer")).resolve()

    forbidden_found = [
        name for name in FORBIDDEN_HOME_ARTIFACTS if os.path.lexists(home_p / name)
    ]

    prefix_resolves_to_home = False
    if ws_p.is_dir() and ws_p != home_p:
        try:
            ws_res = subprocess.run(
                ["npm", "prefix"], cwd=str(ws_p), capture_output=True, text=True
            )
            if ws_res.returncode == 0 and ws_res.stdout.strip():
                prefix_resolves_to_home = Path(ws_res.stdout.strip()).resolve() == home_p
        except Exception:
            pass

    home_prefix_hijacked = bool(forbidden_found) or prefix_resolves_to_home

    pipeline_prefix = str(Path(os.path.expanduser("~/.npm-global")).resolve())
    declared_resolved = str(Path(os.path.expanduser(declared_prefix)).resolve())
    npm_resolved = str(Path(os.path.expanduser(npm_prefix)).resolve()) if npm_prefix != "unknown" else "unknown"

    has_split = (
        (npm_resolved != declared_resolved)
        or (npm_resolved != pipeline_prefix)
        or home_prefix_hijacked
    )
    status = "split_detected" if has_split else "reconciled"

    return PrefixReconciliation(
        npm_config_prefix=npm_prefix,
        maintenance_pipeline_prefix=pipeline_prefix,
        declared_prefix=declared_prefix,
        has_split=has_split,
        status=status,
        home_prefix_hijacked=home_prefix_hijacked,
        home_forbidden_artifacts=forbidden_found,
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
            home / ".kimi-code",
            home / ".qoder",
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
    # 6. ~/.kimi-code standalone tool manager
    if ".kimi-code" in parts:
        return str(Path.home() / ".kimi-code"), "vendor_download"
    if ".qoder" in parts:
        return str(Path.home() / ".qoder"), "vendor_download"
    # 6. Check for package.json in parent directories (npm package bundle without explicit node_modules in path)
    for parent in [p] + list(p.parents)[:4]:
        if (parent / "package.json").is_file():
            return str(parent), "npm"
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
        "kimi",
        "droid",
        "muse",
        "qwen",
        "herdr",
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
        "muse": [
            "brew-cask: muse-code",
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
        "kimi": [
            "vendor_download: official Moonshot AI standalone installer (~/.kimi-code/bin/kimi)",
        ],
        "qwen": [
            "brew-formula: qwen-code",
        ],
        "herdr": [
            "brew-formula: herdr",
            "vendor_download: standalone installer (https://herdr.dev/install.sh)",
        ],
    }

    # Audit scheduled writers upfront to link matching candidate writers to tools
    scheduled_writers = audit_scheduled_writers()
    candidate_writers = scheduled_writers.get("candidate_writers", [])

    claude_cfg = audit_claude_autoupdate()
    grok_cfg = audit_grok_autoupdate()
    global_pause = is_global_pause_active({"claude": claude_cfg, "grok": grok_cfg})

    normalize_discovery_path()
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
            decl = get_supported_updater("cce", "vendor_download")
            if decl and decl.status in ("covered", "uncovered_declared"):
                authority = "standalone"
                writer = "none"
                updater_dispatch = decl.updater_dispatch
                update_verb = decl.supported_verb
                delegating_to = decl.delegating_to
                selected_channel = "pinned standalone binary"
                evidence_gaps = []
                drift_status = "clean"
                consequence = None
                active_install_root = str(Path(auth_path).parent)
                prefix_aligned = True
                compatible_command = decl.supported_verb
            else:
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
            dyn_root, src = derive_install_root_and_source(resolved_path)
            decl = get_supported_updater("pi", src)
            if not decl or decl.status != "covered":
                authority = "unknown"
                writer = "unknown"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                drift_status = "unknown"
                consequence = f"No verified updater in registry for pi ({src})"
                active_install_root = dyn_root
                prefix_aligned = True
                compatible_command = None
            else:
                authority = "vendor_download"
                writer = "pi"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                selected_channel = "managed installer (https://pi.dev/install.sh)"
                active_install_root = str(home / ".pi" / "agent" / "install")
                prefix_aligned = True
                drift_status = "clean"
                consequence = None
                compatible_command = decl.supported_verb

        elif name == "kimi":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            decl = get_supported_updater("kimi", src)
            if not decl or decl.status != "covered":
                authority = "unknown"
                writer = "unknown"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                drift_status = "unknown"
                consequence = f"No verified updater in registry for kimi ({src})"
                active_install_root = dyn_root
                prefix_aligned = True
                compatible_command = None
            else:
                authority = "vendor_download"
                writer = "kimi"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                selected_channel = "official Moonshot AI standalone installer (~/.kimi-code/bin/kimi)"
                active_install_root = str(home / ".kimi-code")
                prefix_aligned = True
                drift_status = "clean"
                consequence = None
                compatible_command = decl.supported_verb

        elif name == "opencode":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            decl = get_supported_updater("opencode", src)
            if not decl or decl.status != "covered":
                authority = "unknown"
                writer = "unknown"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                drift_status = "unknown"
                consequence = f"No verified updater in registry for opencode ({src})"
                prefix_aligned = True
                compatible_command = None
            elif src == "brew-formula":
                authority = "brew-formula"
                writer = "brew"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                selected_channel = "brew-formula"
                drift_status = "clean"
                consequence = None
                prefix_aligned = True
                compatible_command = decl.supported_verb
            else:
                authority = "npm-global"
                writer = "npm"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                target_prefix = target_prefix_resolved
                prefix_aligned = active_install_root.startswith(target_prefix)
                drift_status = "clean" if prefix_aligned else "target_misalignment"
                selected_channel = f"npm ({active_install_root})"
                consequence = None if prefix_aligned else f"Active root {active_install_root} misaligned with prefix {target_prefix}"
                compatible_command = decl.supported_verb
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
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            decl = get_supported_updater("claude", src)
            if not decl or decl.status != "covered":
                authority = "unknown"
                writer = "unknown"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                drift_status = "unknown"
                consequence = f"No verified updater in registry for claude ({src})"
                prefix_aligned = True
                compatible_command = None
            else:
                auto_cfg = claude_cfg
                authority = "native"
                writer = "claude"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                selected_channel = "vendor_download (native standalone)"
                prefix_aligned = True
                is_paused = global_pause
                if is_paused:
                    update_verb = None
                    drift_status = "clean"
                    consequence = "Updates paused by user policy (DISABLE_UPDATES)"
                    compatible_command = None
                else:
                    update_verb = decl.supported_verb
                    drift_status = "clean"
                    consequence = None
                    compatible_command = decl.supported_verb
        elif name == "codex":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            decl = get_supported_updater("codex", src)
            if not decl or decl.status != "covered":
                authority = "unknown"
                writer = "unknown"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                drift_status = "unknown"
                consequence = f"No verified updater in registry for codex ({src})"
                prefix_aligned = True
                compatible_command = None
            elif src == "brew-cask":
                authority = "brew-cask"
                writer = "brew"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                selected_channel = "brew-cask (codex)"
                active_install_root = dyn_root
                prefix_aligned = True
                drift_status = "clean"
                consequence = None
                compatible_command = "brew upgrade --cask codex"
            else:
                authority = "npm-global"
                writer = "npm"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                target_prefix = target_prefix_resolved
                if not active_install_root.startswith(target_prefix):
                    prefix_aligned = False
                    drift_status = "target_misalignment"
                    selected_channel = f"npm (active: {active_install_root})"
                    consequence = f"Update action writes to {declared_prefix} while active binary resolves to {active_install_root}"
                    compatible_command = f"npm --prefix {declared_prefix} install -g @openai/codex"
                else:
                    prefix_aligned = True
                    drift_status = "clean"
                    selected_channel = f"npm-global ({declared_prefix})"
                    consequence = None
                    compatible_command = decl.supported_verb
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
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            decl = get_supported_updater("qoder", src)
            if not decl or decl.status != "covered":
                authority = "unknown"
                writer = "unknown"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                drift_status = "unknown"
                consequence = f"No verified updater in registry for qoder ({src})"
                prefix_aligned = True
                compatible_command = None
            elif src == "vendor_download":
                authority = "vendor_download"
                writer = "qoder"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                selected_channel = "vendor_download: ad-hoc wrapper (~/.qoder/entry/qoder)"
                active_install_root = str(home / ".qoder")
                prefix_aligned = True
                drift_status = "clean"
                consequence = None
                compatible_command = decl.supported_verb
            else:
                authority = "npm-global"
                writer = "npm"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                target_prefix = target_prefix_resolved
                if not active_install_root.startswith(target_prefix):
                    prefix_aligned = False
                    drift_status = "target_misalignment"
                    selected_channel = f"npm-wrapper (active target: {active_install_root})"
                    consequence = f"Wrapper targets {active_install_root} instead of declared prefix {declared_prefix}"
                    compatible_command = f"npm install -g --prefix {declared_prefix} @qoder-ai/qodercli"
                else:
                    prefix_aligned = True
                    drift_status = "clean"
                    selected_channel = f"npm-wrapper ({declared_prefix})"
                    consequence = None
                    compatible_command = decl.supported_verb
                continue
        elif name == "qodercli":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            decl = get_supported_updater("qodercli", src)
            if decl and src == "vendor_download":
                authority = "vendor_download"
                writer = "qoder"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                selected_channel = "vendor_download (~/.qoder)"
                active_install_root = str(home / ".qoder")
                prefix_aligned = True
                drift_status = "clean"
                consequence = None
                compatible_command = decl.supported_verb
            else:
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
            authority = "npm-global"
            writer = "npm"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = None
            target_prefix = target_prefix_resolved
            prefix_aligned = active_install_root.startswith(target_prefix)
            drift_status = "clean" if prefix_aligned else "target_misalignment"
            selected_channel = f"npm-bundle ({active_install_root}; uncovered in pipeline)"
            consequence = None if prefix_aligned else f"Active root {active_install_root} misaligned with declared prefix {declared_prefix}; package is uncovered"
            compatible_command = f"npm install -g --prefix {declared_prefix} prime-agent" if not prefix_aligned else None
            orthogonal_findings.append(f"Unmanaged package bundle in {active_install_root} (lacks Homebrew receipt)")
        elif name == "kilo":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = dyn_root
            decl = get_supported_updater("kilo", src)
            authority = "npm-global"
            writer = "npm"
            updater_dispatch = "none"
            delegating_to = None
            update_verb = decl.supported_verb if decl else "kilo upgrade"
            selected_channel = f"npm-global (@kilocode/cli; supported CLI: {update_verb}, uncovered in pipeline)"
            target_prefix = target_prefix_resolved
            prefix_aligned = active_install_root.startswith(target_prefix)
            drift_status = "clean" if prefix_aligned else "target_misalignment"
            consequence = None if prefix_aligned else f"Active root {active_install_root} misaligned with prefix {target_prefix}"
            compatible_command = None
        elif name == "auggie":
            dyn_root, src = derive_install_root_and_source(resolved_path)
            active_install_root = str(Path(resolved_path).parent.parent)
            decl = get_supported_updater("auggie", src)
            if not decl or decl.status != "covered":
                authority = "unknown"
                writer = "unknown"
                updater_dispatch = "none"
                delegating_to = None
                update_verb = None
                drift_status = "unknown"
                consequence = f"No verified updater in registry for auggie ({src})"
                prefix_aligned = True
                compatible_command = None
            else:
                authority = "native"
                writer = "npm"
                updater_dispatch = decl.updater_dispatch
                delegating_to = decl.delegating_to
                update_verb = decl.supported_verb
                selected_channel = "npm-global (@augmentcode/auggie)"
                target_prefix = target_prefix_resolved
                prefix_aligned = active_install_root.startswith(target_prefix)
                drift_status = "clean" if prefix_aligned else "target_misalignment"
                consequence = None if prefix_aligned else f"Active root {active_install_root} misaligned with prefix {target_prefix}"
                compatible_command = decl.supported_verb
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

        elif name in ("goose", "newman", "qwen", "herdr"):
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

        elif name in ("droid", "cursor-agent", "buzz", "muse"):
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

        for cw in candidate_writers:
            kw = name.lower()
            label_lower = cw.get("label", "").lower()
            base_lower = cw.get("executable_baseline", "").lower()
            pattern = rf"\b{re.escape(kw)}\b"
            if re.search(pattern, label_lower) or re.search(pattern, base_lower):
                orthogonal_findings.append(f"Scheduled background job detected: {cw['type']} '{cw['label']}'")

        # Apply global pause policy across all covered tools
        if global_pause and update_verb and name != "claude":
            update_verb = None
            consequence = "Updates paused by user policy (DISABLE_UPDATES)"
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

    # scheduled_writers already audited upfront
    return AuthorityReconciliation(
        status=status,
        drift_count=len(target_misaligned) + len(conflicts),
        conflict_count=len(conflicts),
        target_misalignment_count=len(target_misaligned),
        unknown_count=len(unknowns),
        items=items,
        scheduled_writers=scheduled_writers,
    )


def audit_scheduled_writers() -> dict[str, Any]:
    """Value-blind inspection of accessible user and system LaunchAgents and crontab.

    Extracts structural labels, executable baselines, schedule triggers, and env keys.
    Omit all environment variable values, tokens, and secrets.
    """
    home = Path.home()
    scanned_locations = [
        str(home / "Library" / "LaunchAgents"),
        "/Library/LaunchAgents",
    ]
    excluded_boundaries = [
        "Root-owned LaunchDaemons (/Library/LaunchDaemons, /System/Library/LaunchDaemons)",
        "System-internal launchd domains (/System/Library/LaunchAgents)",
        "Container and virtualization daemon engines (Docker, Podman)",
        "Arbitrary shell script indirection and nested wrapper sub-processes",
    ]

    candidate_writers: list[dict[str, Any]] = []
    agent_keywords = ("brew", "npm", "bun", "uv", "claude", "codex", "opencode", "auggie", "qoder", "pi", "kimi", "kilo")

    for loc in scanned_locations:
        p = Path(loc)
        if not p.is_dir():
            continue
        try:
            for plist_file in p.glob("*.plist"):
                try:
                    with open(plist_file, "rb") as f:
                        data = plistlib.load(f)
                    if not isinstance(data, dict):
                        continue
                    label = str(data.get("Label", plist_file.stem))
                    prog = data.get("Program")
                    args = data.get("ProgramArguments", [])
                    exec_baseline = str(prog) if prog else (str(args[0]) if args else "unknown")

                    match = False
                    for kw in agent_keywords:
                        pattern = rf"\b{re.escape(kw)}\b"
                        if re.search(pattern, label, re.IGNORECASE) or re.search(pattern, exec_baseline, re.IGNORECASE):
                            match = True
                            break
                        for a in args:
                            if re.search(pattern, str(a), re.IGNORECASE):
                                match = True
                                break
                    if match:
                        schedule = {}
                        if "StartInterval" in data:
                            schedule["interval_seconds"] = data["StartInterval"]
                        if "StartCalendarInterval" in data:
                            schedule["calendar"] = "present"
                        if "RunAtLoad" in data:
                            schedule["run_at_load"] = bool(data["RunAtLoad"])

                        env_keys: list[str] = []
                        if "EnvironmentVariables" in data and isinstance(data["EnvironmentVariables"], dict):
                            env_keys = sorted(data["EnvironmentVariables"].keys())

                        candidate_writers.append({
                            "type": "launch_agent",
                            "source_file": str(plist_file),
                            "label": label,
                            "executable_baseline": exec_baseline,
                            "schedule": schedule,
                            "env_keys": env_keys,  # VALUE-BLIND: key names only, never values
                        })
                except Exception:
                    continue
        except Exception:
            continue

    # User crontab inspection
    try:
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=5)
        if res.returncode == 0 and res.stdout:
            for line in res.stdout.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if not parts:
                    continue
                schedule_spec = ""
                cmd_tokens = []
                if parts[0].startswith("@"):
                    schedule_spec = parts[0]
                    cmd_tokens = parts[1:]
                elif len(parts) >= 6:
                    schedule_spec = " ".join(parts[:5])
                    cmd_tokens = parts[5:]
                else:
                    continue

                if not cmd_tokens:
                    continue

                # Extract inline environment variable assignments without disclosing values
                env_keys: list[str] = []
                idx = 0
                while idx < len(cmd_tokens):
                    tok = cmd_tokens[idx]
                    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok):
                        key_name = tok.split("=", 1)[0]
                        env_keys.append(key_name)
                        idx += 1
                    else:
                        break

                if idx < len(cmd_tokens):
                    cmd_baseline = os.path.basename(cmd_tokens[idx])
                else:
                    cmd_baseline = "unknown"

                # Check keywords against command baseline and cron line
                match = any(re.search(rf"\b{re.escape(kw)}\b", line, re.IGNORECASE) for kw in agent_keywords)
                if match:
                    candidate_writers.append({
                        "type": "user_crontab",
                        "source_file": "crontab -l",
                        "label": "user_crontab_entry",
                        "executable_baseline": cmd_baseline,
                        "schedule": {"cron_spec": schedule_spec},
                        "env_keys": sorted(env_keys),  # VALUE-BLIND: key names only, never values
                    })
    except Exception:
        pass

    return {
        "scan_boundaries": {
            "scanned_paths": scanned_locations + ["crontab -l"],
            "excluded_limitations": excluded_boundaries,
        },
        "candidate_writers": candidate_writers,
    }

def inventory_tools(home_dir: Path | None = None) -> list[ToolInventoryItem]:
    home = (home_dir or Path.home()).resolve()

    # Target search roots
    locations = {
        "npm-global": home / ".npm-global" / "lib" / "node_modules",
        "homebrew": Path("/opt/homebrew/lib/node_modules"),
        "home-toolchain": home / ".local" / "share" / "home-toolchain" / "node_modules",
        "adhoc-local": home / ".local" / "lib" / "node_modules",
        "adhoc-home": home / "node_modules",
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
        "kimi",
        "droid",
        "muse",
        "herdr",
    ]

    preferred_sources = {
        "codex": ("cask codex", True),
        "claude": ("cask claude-code", True),
        "cursor-agent": ("cask cursor-cli", True),
        "droid": ("cask droid", True),
        "muse": ("cask muse-code", True),
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
        "kimi": ("vendor_download: official Moonshot AI standalone installer", True),
        "prime-agent": ("none (official R2 Mach-O channel)", False),
        "happy": ("none", False),
        "herdr": ("formula herdr", True),
    }

    name_collisions = {
        "grok": "Homebrew formula 'grok' is an unrelated deprecated regex tool; official agent CLI is cask 'grok-build'",
        "opencode": "Homebrew formula 'opencode' originates from a third-party tap and shadows 'homebrew/core/opencode'",
        "muse": "Homebrew cask 'muse' is an unrelated disabled desktop app (muse.ai); official Meta Muse Code CLI is cask 'muse-code'",
    }

    results: list[ToolInventoryItem] = []

    normalize_discovery_path()

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
                if ("node_modules" in str(target) or ".npm" in str(target)) and "Cellar" not in target.parts and "Caskroom" not in target.parts:
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
        elif tool_name == "opencode":
            pkg_keys.append("opencode-ai")
        elif tool_name == "openspec":
            pkg_keys.append("@fission-ai/openspec")

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

                    is_sanc = loc_name not in ("adhoc-local", "adhoc-home")
                    sanc_repl: str | None = None
                    if not is_sanc:
                        if tool_name in ("bru", "pyright", "yaml-language-server", "newman-reporter-htmlextra"):
                            sanc_repl = str(home / ".local" / "share" / "home-toolchain" / "node_modules")
                        elif tool_name == "newman":
                            sanc_repl = "/opt/homebrew/bin/newman"
                        else:
                            sanc_repl = str(home / ".npm-global" / "lib" / "node_modules")
                    copies.append(
                        ToolCopy(
                            location_path=str(candidate),
                            owning_manager=loc_name,
                            size_bytes=sz,
                            size_human=format_bytes(sz),
                            is_authoritative=is_auth,
                            is_symlinked_from_brew_bin=is_symlink_target,
                            is_sanctioned=is_sanc,
                            sanctioned_replacement=sanc_repl,
                        )
                    )

        # Ensure authoritative copy is always first in copies list (copies[0])
        auth_idx = next((i for i, c in enumerate(copies) if c.is_authoritative), -1)
        if auth_idx > 0:
            copies.insert(0, copies.pop(auth_idx))
        elif auth_idx == -1 and auth_path != "not_found":
            try:
                resolved_auth = Path(auth_path).resolve()
                sz = get_dir_size_bytes(resolved_auth) if resolved_auth.is_dir() else (resolved_auth.stat().st_size if resolved_auth.exists() else 0)
                manager = "brew" if ("/Cellar/" in str(resolved_auth) or "/Caskroom/" in str(resolved_auth)) else "system"
                auth_copy = ToolCopy(
                    location_path=str(resolved_auth),
                    owning_manager=manager,
                    size_bytes=sz,
                    size_human=format_bytes(sz),
                    is_authoritative=True,
                    is_symlinked_from_brew_bin=(resolved_auth == brew_bin.resolve()) if brew_bin.is_symlink() else False,
                )
                copies.insert(0, auth_copy)
            except Exception:
                pass
        has_dups = len(copies) > 1
        est_reclaim = sum(c.size_bytes for c in copies if not c.is_authoritative) if has_dups else 0
        unsanc_paths = [c.location_path for c in copies if not c.is_sanctioned]
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
                unsanctioned_copies=unsanc_paths,
            )
        )

    return results
def reconcile_with_manifest(
    manifest_path: Path | str | None = None,
    inventory_items: list[ToolInventoryItem] | None = None,
    auth_items: list[ToolAuthorityItem] | None = None,
) -> dict[str, Any] | None:
    """Compare declared manifest intent with observed host resolution.

    Reports aligned, drift, missing, duplicate, obsolete_candidate, and unknown states.
    Read-only by contract: never modifies any file or directory.
    """
    if manifest_path is None:
        default_manifest = Path(__file__).resolve().parent.parent / "config" / "workstation-toolchain-manifest.json"
        if default_manifest.is_file():
            manifest_path = default_manifest
        else:
            return None

    m_path = Path(manifest_path)
    if not m_path.is_file():
        return None

    normalize_discovery_path()

    try:
        with open(m_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)
    except Exception:
        return None

    declared_tools = manifest_data.get("tools", {})
    home = Path.home()
    brew_prefix = "/opt/homebrew" if os.uname().machine == "arm64" else "/usr/local"
    if os.environ.get("HOMEBREW_PREFIX"):
        brew_prefix = os.environ["HOMEBREW_PREFIX"]

    # Build map of observed inventory tools, auto-running inventory if not supplied
    if inventory_items is None:
        inventory_items = inventory_tools()
    if auth_items is None:
        auth_items = evaluate_authority_and_drift().items

    inv_map = {item.name: item for item in (inventory_items or [])}
    auth_map = {item.name: item for item in (auth_items or [])}
    aligned: list[dict[str, Any]] = []
    drift: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    optional_skipped: list[dict[str, Any]] = []
    rust_dev_tools = set(manifest_data.get("profiles", {}).get("rust-dev", ["rustup", "cargo"]))
    duplicate: list[dict[str, Any]] = []
    unsanctioned: list[dict[str, Any]] = []
    obsolete_candidate: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    # Check each declared tool against observed host resolution
    for tool_name, t_meta in declared_tools.items():
        active_bin = shutil.which(tool_name)
        owner = t_meta.get("authoritative_owner", "unknown")
        path_pattern = t_meta.get("active_path_pattern", "")
        expected_path = path_pattern.replace("{{HOME}}", str(home)).replace("{{HOMEBREW_PREFIX}}", brew_prefix)

        # Check duplicates from inventory
        inv_item = inv_map.get(tool_name)
        if inv_item and inv_item.has_duplication:
            duplicate.append({
                "name": tool_name,
                "copies_count": len(inv_item.copies),
                "reclaimable_human": inv_item.estimated_reclaimable_human,
                "copies": [c.location_path for c in inv_item.copies],
            })
        # Unsanctioned copies are collected across all inventory items below
        if not active_bin:
            if expected_path and Path(expected_path).is_file():
                active_bin = expected_path
            else:
                if tool_name in rust_dev_tools:
                    optional_skipped.append({
                        "name": tool_name,
                        "state": "optional_skipped",
                        "profile": "rust-dev",
                        "expected_owner": owner,
                        "expected_path": expected_path,
                        "active_path": None,
                    })
                else:
                    missing.append({
                        "name": tool_name,
                        "state": "missing",
                        "expected_owner": owner,
                        "expected_path": expected_path,
                        "active_path": None,
                    })
                continue
        resolved_active = str(Path(active_bin).resolve())
        # Evaluate alignment
        auth_item = auth_map.get(tool_name)
        is_aligned = False
        if auth_item and auth_item.drift_status == "clean":
            is_aligned = True
        elif tool_name == "psql" and (resolved_active == expected_path or active_bin == expected_path or "libpq" in resolved_active):
            is_aligned = True
        elif tool_name == "cce" and owner == "standalone" and ".local/bin/cce" in active_bin:
            is_aligned = True
        elif tool_name == "prime-agent" and owner == "local-dev" and ("prime-agent" in resolved_active or "prime-agent" in active_bin):
            is_aligned = True
        elif tool_name == "qoder" and (auth_item and auth_item.drift_status == "clean" or ".qoder" in resolved_active or ".qoder" in active_bin or expected_path in (resolved_active, active_bin)):
            is_aligned = True
        elif tool_name == "kimi" and (auth_item and auth_item.drift_status == "clean" or ".kimi-code" in resolved_active or ".kimi-code" in active_bin or expected_path in (resolved_active, active_bin)):
            is_aligned = True
        else:
            if expected_path and (resolved_active == expected_path or active_bin == expected_path):
                is_aligned = True
            elif owner == "brew-formula" and ("/Cellar/" in resolved_active or "/opt/homebrew/" in resolved_active or "/usr/local/" in resolved_active):
                is_aligned = True
            elif owner == "brew-cask" and ("/Caskroom/" in resolved_active or "/Applications/" in resolved_active):
                is_aligned = True
            elif owner == "npm-global" and ".npm-global" in resolved_active:
                is_aligned = True
            elif owner == "isolated-node" and "home-toolchain" in resolved_active:
                is_aligned = True
            elif owner == "standalone" and (".local" in resolved_active or ".cargo" in resolved_active or ".pi" in resolved_active or ".kimi-code" in resolved_active or ".qoder" in resolved_active):
                is_aligned = True
            elif owner == "local-dev" and ("prime-agent" in resolved_active or "prime-agent" in active_bin):
                is_aligned = True
        if is_aligned:
            aligned.append({
                "name": tool_name,
                "state": "aligned",
                "owner": owner,
                "active_path": active_bin,
                "resolved_path": resolved_active,
            })
        else:
            drift.append({
                "name": tool_name,
                "state": "drift",
                "declared_owner": owner,
                "expected_path": expected_path,
                "active_path": active_bin,
                "resolved_path": resolved_active,
                "consequence": f"Active path {resolved_active} does not match declared owner {owner}",
            })

    # Collect unsanctioned copies across all inventoried tools (declared or not)
    seen_unsanc_paths: set[str] = set()
    for inv_name, inv_item in inv_map.items():
        if inv_item.unsanctioned_copies:
            for c in inv_item.copies:
                if not c.is_sanctioned and c.location_path not in seen_unsanc_paths:
                    seen_unsanc_paths.add(c.location_path)
                    unsanctioned.append({
                        "name": inv_name,
                        "unsanctioned_path": c.location_path,
                        "owning_manager": c.owning_manager,
                        "sanctioned_replacement": c.sanctioned_replacement,
                    })

    # Also check isolated toolbelt packages in adhoc-home / adhoc-local without inflating unknown_count
    for adhoc_mgr, adhoc_root in (
        ("adhoc-local", home / ".local" / "lib" / "node_modules"),
        ("adhoc-home", home / "node_modules"),
    ):
        for tb_pkg in ("pyright", "yaml-language-server", "newman-reporter-htmlextra"):
            cand = adhoc_root / tb_pkg
            if cand.exists() and str(cand) not in seen_unsanc_paths:
                seen_unsanc_paths.add(str(cand))
                unsanctioned.append({
                    "name": tb_pkg,
                    "unsanctioned_path": str(cand),
                    "owning_manager": adhoc_mgr,
                    "sanctioned_replacement": str(home / ".local" / "share" / "home-toolchain" / "node_modules"),
                })

    # Detect unknown tools on host (in inventory but not in manifest)
    for inv_name in inv_map:
        if inv_name not in declared_tools:
            unknown.append({
                "name": inv_name,
                "state": "unknown",
                "active_path": inv_map[inv_name].authoritative_path,
            })
    # Known obsolete candidates (e.g. deprecated python formula)
    deprecated_candidates = ["python@3.10"]
    for dep in deprecated_candidates:
        dep_path = Path(brew_prefix) / "opt" / dep
        if dep_path.exists():
            obsolete_candidate.append({
                "name": dep,
                "state": "obsolete_candidate",
                "location": str(dep_path),
                "rationale": "Deprecated formula in Homebrew; audit dependencies before uninstallation",
            })

    overall_status = "drift" if (drift or missing or unsanctioned) else "aligned"
    return {
        "manifest_path": str(m_path),
        "status": overall_status,
        "declared_tools_count": len(declared_tools),
        "aligned_count": len(aligned),
        "drift_count": len(drift),
        "missing_count": len(missing),
        "optional_skipped_count": len(optional_skipped),
        "duplicate_count": len(duplicate),
        "unsanctioned_count": len(unsanctioned),
        "obsolete_candidate_count": len(obsolete_candidate),
        "unknown_count": len(unknown),
        "summary": {
            "aligned": [i["name"] for i in aligned],
            "drift": [i["name"] for i in drift],
            "missing": [i["name"] for i in missing],
            "optional_skipped": [i["name"] for i in optional_skipped],
            "duplicate": [i["name"] for i in duplicate],
            "unsanctioned": [i["name"] for i in unsanctioned],
            "obsolete_candidate": [i["name"] for i in obsolete_candidate],
            "unknown": [i["name"] for i in unknown],
        },
        "items": {
            "aligned": aligned,
            "drift": drift,
            "missing": missing,
            "optional_skipped": optional_skipped,
            "duplicate": duplicate,
            "unsanctioned": unsanctioned,
            "obsolete_candidate": obsolete_candidate,
            "unknown": unknown,
        },
    }



def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory workstation toolchain install locations.")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--declared-prefix", default="~/.npm-global", help="Declared npm global prefix")
    parser.add_argument("--manifest", help="Path to declarative workstation-toolchain-manifest.json")
    args = parser.parse_args()

    prefix_check = check_prefix_reconciliation(args.declared_prefix)
    inventory = inventory_tools()
    auth_reconciliation = evaluate_authority_and_drift(args.declared_prefix)
    manifest_check = reconcile_with_manifest(args.manifest, inventory, auth_reconciliation.items)

    if args.json:
        data = {
            "prefix_reconciliation": asdict(prefix_check),
            "tools": [asdict(t) for t in inventory],
            "authority_reconciliation": asdict(auth_reconciliation),
            "manifest_reconciliation": manifest_check,
            "proposes_deletion": False,
        }
        print(json.dumps(data, indent=2))
    else:
        print("=== Workstation Prefix Reconciliation ===")
        print(f"  npm config get prefix:       {prefix_check.npm_config_prefix}")
        print(f"  maintenance pipeline prefix: {prefix_check.maintenance_pipeline_prefix}")
        print(f"  declared prefix:             {prefix_check.declared_prefix}")
        print(f"  home prefix hijacked:        {prefix_check.home_prefix_hijacked}")
        if prefix_check.home_forbidden_artifacts:
            print(f"  home forbidden artifacts:    {', '.join(prefix_check.home_forbidden_artifacts)}")
        print(f"  Status:                      {prefix_check.status.upper()}")
        print("\n=== Workstation Toolchain Inventory ===")
        for item in inventory:
            dup_tag = f" [DUPLICATES: {len(item.copies)} copies, reclaimable ~{item.estimated_reclaimable_human}]" if item.has_duplication else ""
            print(f"Tool: {item.name:15} -> {item.authoritative_path}{dup_tag}")
            for c in item.copies:
                role = "AUTHORITATIVE" if c.is_authoritative else "duplicate"
                adj = " (symlinked from /opt/homebrew/bin)" if c.is_symlinked_from_brew_bin else ""
                unsanc_note = f" [UNSANCTIONED -> sanctioned location: {c.sanctioned_replacement}]" if not c.is_sanctioned else ""
                print(f"    [{c.owning_manager:14}] {c.location_path} ({c.size_human}) -> {role}{adj}{unsanc_note}")
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

        if manifest_check:
            print("\n=== Manifest Intent Reconciliation ===")
            print(f"  Status:                      {manifest_check['status'].upper()}")
            print(f"  Declared Tools:              {manifest_check['declared_tools_count']}")
            print(f"  Aligned:                     {manifest_check['aligned_count']}")
            print(f"  Drift:                       {manifest_check['drift_count']}")
            print(f"  Missing:                     {manifest_check['missing_count']}")
            print(f"  Duplicates:                  {manifest_check['duplicate_count']}")
            print(f"  Unsanctioned:                {manifest_check['unsanctioned_count']}")
            print(f"  Obsolete Candidates:         {manifest_check['obsolete_candidate_count']}")
            print(f"  Unknown Tools:               {manifest_check['unknown_count']}")
            if manifest_check['summary']['drift']:
                print(f"  Drift items:                 {', '.join(manifest_check['summary']['drift'])}")
            if manifest_check['summary']['duplicate']:
                print(f"  Duplicate items:             {', '.join(manifest_check['summary']['duplicate'])}")
            if manifest_check['summary']['unsanctioned']:
                print(f"  Unsanctioned items:          {', '.join(manifest_check['summary']['unsanctioned'])}")
        print("\nPolicy Enforcement: Proposes deletion = False (Strictly read-only; explicit authorization required)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
