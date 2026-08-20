#!/usr/bin/env python3
"""Synchronize tracked OpenSpec targets and selected cross-agent skill links.

Authoritative generated targets live in openspec-store. Shared non-generated
skills remain canonical in ~/Developer/.agents/skills. Real user-level skill
directories are preserved; only links owned by this script are reconciled.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

HOME = Path.home()
STORE = Path(__file__).resolve().parents[1]
WORKSPACE = STORE.parent
WORKSPACE_AGENTS = WORKSPACE / ".agents" / "skills"
WORKSPACE_CLAUDE_SKILLS = WORKSPACE / ".claude" / "skills"
WORKSPACE_CLAUDE_COMMANDS = WORKSPACE / ".claude" / "commands" / "opsx"
USER_AGENTS = HOME / ".agents" / "skills"
USER_CLAUDE_SKILLS = HOME / ".claude" / "skills"
USER_CLAUDE_COMMANDS = HOME / ".claude" / "commands" / "opsx"
STORE_STANDARD = STORE / ".agents" / "skills"
STORE_CLAUDE_SKILLS = STORE / ".claude" / "skills"
STORE_CLAUDE_COMMANDS = STORE / ".claude" / "commands" / "opsx"
CODEX_MANIFEST = STORE / "config" / "codex-user-skill-manifest.txt"
CLAUDE_MANIFEST = STORE / "config" / "claude-user-skill-manifest.txt"

OPEN_SPEC_NAMES = tuple(
    sorted(path.name for path in STORE_STANDARD.glob("openspec-*") if (path / "SKILL.md").is_file())
)


@dataclass
class Result:
    created: list[str]
    removed: list[str]
    conflicts: list[str]
    broken: list[str]


def manifest(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def skill_roots(root: Path) -> tuple[dict[str, Path], list[str]]:
    direct: dict[str, Path] = {}
    containers: list[str] = []
    if not root.is_dir():
        return direct, containers
    for path in sorted(root.iterdir()):
        if path.name.startswith(".") or not path.is_dir():
            continue
        if (path / "SKILL.md").is_file():
            direct[path.name] = path
        else:
            containers.append(path.name)
    return direct, containers


def points_to(link: Path, target: Path) -> bool:
    return link.is_symlink() and Path(os.path.realpath(link)) == target.resolve()


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def equivalent(left: Path, right: Path) -> bool:
    if left.is_file() and right.is_file():
        return file_digest(left) == file_digest(right)
    if left.is_dir() and right.is_dir():
        left_files = {
            path.relative_to(left): file_digest(path)
            for path in left.rglob("*")
            if path.is_file()
        }
        right_files = {
            path.relative_to(right): file_digest(path)
            for path in right.rglob("*")
            if path.is_file()
        }
        return left_files == right_files
    return False


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def reconcile_links(
    *,
    destination: Path,
    desired: dict[str, Path],
    managed_target_roots: tuple[Path, ...],
    check: bool,
) -> Result:
    if not destination.is_dir():
        if check:
            return Result([], [], [f"missing-destination:{destination}"], [])
        destination.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    removed: list[str] = []
    conflicts: list[str] = []
    broken: list[str] = []

    for path in sorted(destination.iterdir()):
        if not path.is_symlink():
            continue
        target = Path(os.path.realpath(path))
        if not any(target == root.resolve() or root.resolve() in target.parents for root in managed_target_roots):
            continue
        expected = desired.get(path.name)
        if expected is None or target != expected.resolve():
            removed.append(path.name)
            if not check:
                path.unlink()

    for name, source in sorted(desired.items()):
        target = destination / name
        if points_to(target, source):
            continue
        if target.exists() or target.is_symlink():
            if equivalent(target, source):
                removed.append(name)
                created.append(name)
                if not check:
                    remove_path(target)
                    target.symlink_to(source, target_is_directory=source.is_dir())
                continue
            conflicts.append(name)
            continue
        created.append(name)
        if not check:
            target.symlink_to(source, target_is_directory=source.is_dir())

    for path in sorted(destination.iterdir()):
        if path.is_symlink() and not path.exists():
            broken.append(path.name)

    return Result(created, removed, conflicts, broken)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify only")
    args = parser.parse_args()

    workspace_roots, containers = skill_roots(WORKSPACE_AGENTS)
    codex_selected = manifest(CODEX_MANIFEST)
    claude_selected = manifest(CLAUDE_MANIFEST)
    selected = codex_selected | claude_selected
    missing = sorted(selected - workspace_roots.keys())
    if missing:
        print("missing_manifest_entries=" + ",".join(missing))
        return 1

    # Generated OpenSpec roots are adapter-specific; link each workspace surface
    # to the matching generated target instead of copying files between adapters.
    standard_openspec = {name: STORE_STANDARD / name for name in OPEN_SPEC_NAMES}
    claude_openspec = {name: STORE_CLAUDE_SKILLS / name for name in OPEN_SPEC_NAMES}
    claude_commands = {
        path.name: path for path in sorted(STORE_CLAUDE_COMMANDS.glob("*.md"))
    }

    results = {
        "workspace_agents": reconcile_links(
            destination=WORKSPACE_AGENTS,
            desired=standard_openspec,
            managed_target_roots=(STORE_STANDARD,),
            check=args.check,
        ),
        "user_agents": reconcile_links(
            destination=USER_AGENTS,
            desired={name: workspace_roots[name] for name in codex_selected},
            managed_target_roots=(WORKSPACE_AGENTS,),
            check=args.check,
        ),
        "workspace_claude_skills": reconcile_links(
            destination=WORKSPACE_CLAUDE_SKILLS,
            desired=claude_openspec,
            managed_target_roots=(STORE_CLAUDE_SKILLS,),
            check=args.check,
        ),
        "user_claude_skills": reconcile_links(
            destination=USER_CLAUDE_SKILLS,
            desired={
                **claude_openspec,
                **{name: workspace_roots[name] for name in claude_selected},
            },
            managed_target_roots=(STORE_CLAUDE_SKILLS, WORKSPACE_AGENTS),
            check=args.check,
        ),
        "workspace_claude_commands": reconcile_links(
            destination=WORKSPACE_CLAUDE_COMMANDS,
            desired=claude_commands,
            managed_target_roots=(STORE_CLAUDE_COMMANDS,),
            check=args.check,
        ),
        "user_claude_commands": reconcile_links(
            destination=USER_CLAUDE_COMMANDS,
            desired=claude_commands,
            managed_target_roots=(STORE_CLAUDE_COMMANDS,),
            check=args.check,
        ),
    }

    print(
        f"canonical_direct_roots={len(workspace_roots)} "
        f"containers={len(containers)} codex_selected={len(codex_selected)} "
        f"claude_selected={len(claude_selected)} openspec_targets={len(OPEN_SPEC_NAMES)} "
        f"claude_commands={len(claude_commands)} check={args.check}"
    )
    if containers:
        print("containers=" + ",".join(containers))

    failed = False
    for label, result in results.items():
        print(
            f"{label}: created={len(result.created)} removed={len(result.removed)} "
            f"conflicts={len(result.conflicts)} broken={len(result.broken)}"
        )
        if result.created:
            print(f"{label}.created=" + ",".join(result.created))
        if result.removed:
            print(f"{label}.removed=" + ",".join(result.removed))
        if result.conflicts:
            print(f"{label}.conflicts=" + ",".join(result.conflicts))
        if result.broken:
            print(f"{label}.broken=" + ",".join(result.broken))
        if result.conflicts or result.broken or (args.check and (result.created or result.removed)):
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
