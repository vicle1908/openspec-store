"""Shared workstation toolchain updater registry and pause policy definitions.

Standard library only. Single source of truth for:
- Supported updater commands keyed by (tool, source_type)
- Updater dispatch classifications (native, delegating, none)
- Pause setting normalization and global pause evaluation
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


def is_truthy_pause(val: Any) -> bool:
    """Normalize boolean, numeric, and string pause settings."""
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val.strip().lower() in ("1", "true", "yes", "on", "enabled")
    return False


@dataclass(frozen=True)
class UpdaterDeclaration:
    tool: str
    source_type: str  # 'vendor_download', 'npm', 'brew-cask', 'brew-formula', 'git_repo'
    supported_verb: str | None
    updater_dispatch: str  # 'native', 'delegating', 'none'
    delegating_to: str | None
    status: str  # 'covered', 'uncovered_declared'
    notes: str = ""


# Canonical shared registry of supported updater verbs per tool and active source
SUPPORTED_UPDATER_REGISTRY: dict[tuple[str, str], UpdaterDeclaration] = {
    # Covered tools with active automated updates
    ("claude", "vendor_download"): UpdaterDeclaration(
        tool="claude",
        source_type="vendor_download",
        supported_verb="claude update",
        updater_dispatch="native",
        delegating_to=None,
        status="covered",
        notes="Official native standalone auto-updater",
    ),
    ("codex", "npm"): UpdaterDeclaration(
        tool="codex",
        source_type="npm",
        supported_verb="codex update",
        updater_dispatch="native",
        delegating_to=None,
        status="covered",
        notes="Native CLI update verb invoking global npm install",
    ),
    ("opencode", "brew-formula"): UpdaterDeclaration(
        tool="opencode",
        source_type="brew-formula",
        supported_verb="opencode upgrade",
        updater_dispatch="delegating",
        delegating_to="brew",
        status="covered",
        notes="CLI upgrade verb delegates directly to brew upgrade",
    ),
    ("opencode", "npm"): UpdaterDeclaration(
        tool="opencode",
        source_type="npm",
        supported_verb="opencode upgrade",
        updater_dispatch="delegating",
        delegating_to="npm",
        status="covered",
        notes="CLI upgrade verb delegates directly to npm install -g",
    ),
    ("auggie", "npm"): UpdaterDeclaration(
        tool="auggie",
        source_type="npm",
        supported_verb="auggie update --skip-confirmation",
        updater_dispatch="native",
        delegating_to=None,
        status="covered",
        notes="Native CLI updater with non-interactive confirmation skip",
    ),
    ("qoder", "npm"): UpdaterDeclaration(
        tool="qoder",
        source_type="npm",
        supported_verb="qoder update",
        updater_dispatch="native",
        delegating_to=None,
        status="covered",
        notes="Wrapper routes to npm bundle qodercli with native update verb",
    ),
    ("pi", "vendor_download"): UpdaterDeclaration(
        tool="pi",
        source_type="vendor_download",
        supported_verb="pi update --self",
        updater_dispatch="native",
        delegating_to=None,
        status="covered",
        notes="Vendor release channel with --self update flag",
    ),
    # Declared uncovered tools
    ("kilo", "npm"): UpdaterDeclaration(
        tool="kilo",
        source_type="npm",
        supported_verb="kilo upgrade",  # Supported CLI command is 'kilo upgrade'
        updater_dispatch="none",         # Local updater failing; mutation suppressed in pipeline
        delegating_to=None,
        status="uncovered_declared",
        notes="CLI upgrade verb exists, but native updater fails locally; managed as uncovered",
    ),
    ("prime-agent", "npm"): UpdaterDeclaration(
        tool="prime-agent",
        source_type="npm",
        supported_verb=None,
        updater_dispatch="none",
        delegating_to=None,
        status="uncovered_declared",
        notes="Installed under node_modules bundle in /opt/homebrew; no automated mutation",
    ),
    ("droid", "brew-cask"): UpdaterDeclaration(
        tool="droid",
        source_type="brew-cask",
        supported_verb=None,
        updater_dispatch="none",
        delegating_to="brew",
        status="uncovered_declared",
        notes="Managed via Homebrew cask; bypassed during agent CLI update stage",
    ),
    ("cursor-agent", "brew-cask"): UpdaterDeclaration(
        tool="cursor-agent",
        source_type="brew-cask",
        supported_verb=None,
        updater_dispatch="none",
        delegating_to="brew",
        status="uncovered_declared",
        notes="Managed via Homebrew cask cursor-cli",
    ),
    ("goose", "brew-formula"): UpdaterDeclaration(
        tool="goose",
        source_type="brew-formula",
        supported_verb=None,
        updater_dispatch="none",
        delegating_to="brew",
        status="uncovered_declared",
        notes="Managed via Homebrew formula block-goose-cli",
    ),
    ("buzz", "brew-cask"): UpdaterDeclaration(
        tool="buzz",
        source_type="brew-cask",
        supported_verb=None,
        updater_dispatch="none",
        delegating_to="brew",
        status="uncovered_declared",
        notes="macOS Application bundle",
    ),
    ("grok", "brew-cask"): UpdaterDeclaration(
        tool="grok",
        source_type="brew-cask",
        supported_verb=None,
        updater_dispatch="delegating",
        delegating_to="brew",
        status="uncovered_declared",
        notes="Homebrew cask grok-build",
    ),
    ("hermes-agent", "git_repo"): UpdaterDeclaration(
        tool="hermes-agent",
        source_type="git_repo",
        supported_verb="hermes update",
        updater_dispatch="native",
        delegating_to=None,
        status="uncovered_declared",
        notes="Governed by Git checkout / virtualenv",
    ),
    ("happy", "vendor_download"): UpdaterDeclaration(
        tool="happy",
        source_type="vendor_download",
        supported_verb=None,
        updater_dispatch="none",
        delegating_to=None,
        status="uncovered_declared",
        notes="Standalone binary in ~/.local/bin",
    ),
    ("cce", "vendor_download"): UpdaterDeclaration(
        tool="cce",
        source_type="vendor_download",
        supported_verb=None,
        updater_dispatch="none",
        delegating_to=None,
        status="uncovered_declared",
        notes="Standalone binary in ~/.local/bin lacking automated update path",
    ),
}


def normalize_source_type(source_type: str) -> str:
    """Normalize source type aliases to canonical registry keys."""
    st = source_type.strip().lower()
    if st in ("npm", "npm-global", "ecosystem_manager"):
        return "npm"
    if st in ("brew-formula", "formula"):
        return "brew-formula"
    if st in ("brew-cask", "cask"):
        return "brew-cask"
    if st in ("vendor_download", "standalone", "manual"):
        return "vendor_download"
    if st in ("git_repo", "git"):
        return "git_repo"
    return st


def get_supported_updater(tool: str, source_type: str) -> UpdaterDeclaration | None:
    """Lookup supported updater declaration by tool name and installation source.

    Fails closed: brew-cask and brew-formula are strictly distinguished to avoid
    conflating formula commands with cask assets.
    """
    canonical = normalize_source_type(source_type)
    if (tool, canonical) in SUPPORTED_UPDATER_REGISTRY:
        return SUPPORTED_UPDATER_REGISTRY[(tool, canonical)]
    if (tool, source_type) in SUPPORTED_UPDATER_REGISTRY:
        return SUPPORTED_UPDATER_REGISTRY[(tool, source_type)]

    # Ambiguous generic manager fallback: resolve only if strictly unambiguous
    if canonical in ("brew", "package_manager"):
        has_formula = (tool, "brew-formula") in SUPPORTED_UPDATER_REGISTRY
        has_cask = (tool, "brew-cask") in SUPPORTED_UPDATER_REGISTRY
        if has_formula and not has_cask:
            return SUPPORTED_UPDATER_REGISTRY[(tool, "brew-formula")]
        if has_cask and not has_formula:
            return SUPPORTED_UPDATER_REGISTRY[(tool, "brew-cask")]

    return None

def is_global_pause_active(auto_updates_configs: dict[str, Any] | None = None) -> bool:
    """Check if global pause policy is enabled in environment or configurations."""
    for key in ("DISABLE_UPDATES", "DISABLE_AUTOUPDATER"):
        if is_truthy_pause(os.environ.get(key)):
            return True
    if auto_updates_configs:
        for cfg in auto_updates_configs.values():
            if isinstance(cfg, dict):
                for k in ("DISABLE_UPDATES", "env.DISABLE_UPDATES", "DISABLE_AUTOUPDATER", "env.DISABLE_AUTOUPDATER"):
                    if is_truthy_pause(cfg.get(k)):
                        return True
    return False
