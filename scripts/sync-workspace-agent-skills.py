#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.15"
# dependencies = []
# ///
"""Synchronize tracked OpenSpec targets and selected cross-agent skill links.

Authoritative generated targets live in openspec-store. Shared non-generated
skills remain canonical in ~/Developer/.agents/skills. Real user-level skill
directories are preserved; only links owned by this script are reconciled.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HOME = Path.home()
STORE = Path(__file__).resolve().parents[1]
WORKSPACE = STORE.parent if (STORE.parent / ".agents").exists() else STORE.parent.parent
WORKSPACE_AGENTS = WORKSPACE / ".agents" / "skills"
WORKSPACE_CLAUDE_SKILLS = WORKSPACE / ".claude" / "skills"
WORKSPACE_CLAUDE_COMMANDS = WORKSPACE / ".claude" / "commands" / "opsx"
USER_AGENTS = HOME / ".agents" / "skills"
USER_CLAUDE_SKILLS = HOME / ".claude" / "skills"
USER_CLAUDE_COMMANDS = HOME / ".claude" / "commands" / "opsx"
USER_HERMES_SKILLS = HOME / ".hermes" / "skills"
STORE_STANDARD = STORE / ".agents" / "skills"
STORE_CLAUDE_SKILLS = STORE / ".claude" / "skills"
STORE_CLAUDE_COMMANDS = STORE / ".claude" / "commands" / "opsx"
CODEX_MANIFEST = STORE / "config" / "codex-user-skill-manifest.txt"
CLAUDE_MANIFEST = STORE / "config" / "claude-user-skill-manifest.txt"
HERMES_MANIFEST = STORE / "config" / "hermes-user-skill-manifest.txt"
HERMES_MANAGED_MARKER = ".hermes-managed-links.txt"
OPENSPEC_SYNC_LOCK = Path("/tmp/openspec-skill-sync.lock")

MAX_VENDOR_DESCRIPTION_BYTES = 1024
ADVISORY_VENDOR_DESCRIPTION_BYTES = 800
MAX_INTERNAL_DESCRIPTION_CHARS = 60
# Pre-existing upstream brightdata/skills entry outside user-scope manifests
LEGACY_VENDOR_BYTE_EXCEPTIONS = {"scraper-studio": 1235}
ALLOWED_WORKSPACE_SKILL_PARENTS = (".agents", ".claude", ".hermes", ".codex")
ALLOWED_CODEX_PROJECT_ENTRIES = (".system", "migrate-to-codex")
PONYTAIL_SKILLS = (
    "ponytail",
    "ponytail-audit",
    "ponytail-debt",
    "ponytail-gain",
    "ponytail-help",
    "ponytail-review",
)
HEX40_RE = re.compile(r"^[0-9a-f]{40}$")


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


# Directories that make an agent treat a skill directory as a plugin container,
# causing a case-sensitive catalog walk to stop before reaching SKILL.md. They are
# not part of the Agent Skills layout and are absent from upstream skill sources.
NON_OFFICIAL_ENTRY_DIRS = (".cursor-plugin", "cursor-plugin", "claude-plugin")
AGENT_SKILLS_ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def decode_frontmatter_description(skill_md_path: Path) -> str:
    """Decode YAML frontmatter `description` supporting folded, literal, and plain/quoted scalars."""
    text = skill_md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"{skill_md_path}: missing opening YAML frontmatter delimiter")
    lines = text.splitlines()
    fm_lines: list[str] = []
    closed = False
    for line in lines[1:]:
        if line.strip() in ("---", "..."):
            closed = True
            break
        fm_lines.append(line)
    if not closed:
        raise ValueError(f"{skill_md_path}: missing closing YAML frontmatter delimiter")

    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        match = re.match(r"^description\s*:\s*(.*)$", line)
        if not match:
            i += 1
            continue
        rest = match.group(1).strip()
        if rest in (">", ">-", ">+", "|", "|-", "|+"):
            block_lines: list[str] = []
            i += 1
            indent: int | None = None
            while i < len(fm_lines):
                bline = fm_lines[i]
                if not bline.strip():
                    block_lines.append("")
                    i += 1
                    continue
                cur_indent = len(bline) - len(bline.lstrip(" "))
                if indent is None:
                    if cur_indent == 0:
                        break
                    indent = cur_indent
                elif cur_indent < indent:
                    break
                block_lines.append(bline[indent:])
                i += 1
            trailing_empty = 0
            while block_lines and block_lines[-1] == "":
                block_lines.pop()
                trailing_empty += 1
            if rest.startswith(">"):
                paragraphs: list[str] = []
                cur: list[str] = []
                for bl in block_lines:
                    if bl == "":
                        if cur:
                            paragraphs.append(" ".join(cur))
                            cur = []
                        paragraphs.append("")
                    else:
                        cur.append(bl.strip())
                if cur:
                    paragraphs.append(" ".join(cur))
                body = "\n".join(paragraphs)
            else:
                body = "\n".join(block_lines)
            if not body:
                return ""
            if rest.endswith("-"):
                return body
            if rest.endswith("+"):
                return body + "\n" * max(1, trailing_empty + 1)
            return body + "\n"

        if (rest.startswith('"') and rest.endswith('"') and len(rest) >= 2) or (
            rest.startswith("'") and rest.endswith("'") and len(rest) >= 2
        ):
            quote = rest[0]
            inner = rest[1:-1]
            if quote == '"':
                inner = inner.replace('\\"', '"').replace("\\n", "\n").replace("\\\\", "\\")
            else:
                inner = inner.replace("''", "'")
            return inner

        parts = [rest] if rest else []
        i += 1
        while i < len(fm_lines):
            bline = fm_lines[i]
            if not bline.strip():
                break
            cur_indent = len(bline) - len(bline.lstrip(" "))
            if cur_indent == 0:
                break
            parts.append(bline.strip())
            i += 1
        return " ".join(parts)

    raise ValueError(f"{skill_md_path}: missing description in YAML frontmatter")


def measure_description_bytes(skill_md_path: Path) -> dict[str, int]:
    desc = decode_frontmatter_description(skill_md_path)
    trimmed = desc.rstrip("\r\n")
    return {
        "raw_bytes": len(desc.encode("utf-8")),
        "trimmed_bytes": len(trimmed.encode("utf-8")),
        "char_length": len(trimmed),
    }


def check_description_budget(skill_md_path: Path, is_vendor: bool = True) -> bool:
    try:
        metrics = measure_description_bytes(skill_md_path)
    except (OSError, ValueError):  # fmt: skip
        return False
    if metrics["raw_bytes"] == 0 or metrics["raw_bytes"] > MAX_VENDOR_DESCRIPTION_BYTES:
        return False
    return not (not is_vendor and metrics["char_length"] > MAX_INTERNAL_DESCRIPTION_CHARS)


def _load_locked_skill_names(start: Path) -> set[str]:
    for candidate in (
        start / "skills-lock.json",
        start.parent / "skills-lock.json",
        start.parent.parent / "skills-lock.json",
        start.parent.parent.parent / "skills-lock.json",
    ):
        if candidate.is_file():
            try:
                return set(
                    json.loads(candidate.read_text(encoding="utf-8")).get("skills", {}).keys()
                )
            except Exception:
                pass
    return set()


def _skill_entry_violations(path: Path, locked_skills: set[str] | None = None) -> list[str]:
    findings: list[str] = []
    try:
        names = os.listdir(path)
    except OSError:
        return [f"{path.name}:unreadable-directory"]
    if "SKILL.md" not in names:
        variants = sorted(name for name in names if name.lower() == "skill.md")
        findings.append(f"{path.name}:entry-not-canonical-case(has {','.join(variants)})")
    present = sorted(name for name in names if name in NON_OFFICIAL_ENTRY_DIRS)
    if present:
        findings.append(f"{path.name}:plugin-container-dir(shadows SKILL.md:{','.join(present)})")
    skill_md = path / "SKILL.md"
    if "SKILL.md" in names and skill_md.is_file():
        try:
            raw_text = skill_md.read_text(encoding="utf-8")
            if not raw_text.startswith("---"):
                findings.append(f"{path.name}:missing-yaml-frontmatter")
            else:
                parts = raw_text.split("---", 2)
                if len(parts) < 3:
                    findings.append(f"{path.name}:unclosed-yaml-frontmatter")
                else:
                    fm_lines = parts[1].splitlines()
                    top_keys: set[str] = set()
                    name_val: str | None = None
                    for line in fm_lines:
                        m = re.match(r"^([a-zA-Z0-9_-]+)\s*:", line)
                        if m and not line.startswith(" ") and not line.startswith("	"):
                            k = m.group(1)
                            top_keys.add(k)
                            if k == "name":
                                name_val = line.split(":", 1)[1].strip().strip('"').strip("'")
                    if not name_val:
                        findings.append(f"{path.name}:missing-frontmatter-name")
                    else:
                        if name_val != path.name:
                            findings.append(f"{path.name}:name-directory-mismatch({name_val})")
                        if not SKILL_NAME_RE.match(name_val):
                            findings.append(f"{path.name}:invalid-name-format({name_val})")
                    if locked_skills is None:
                        locked_skills = _load_locked_skill_names(path)
                    is_vendor = path.name in locked_skills
                    if not is_vendor:
                        extras = sorted(top_keys - AGENT_SKILLS_ALLOWED_FIELDS)
                        if extras:
                            findings.append(
                                f"{path.name}:unexpected-frontmatter-fields({','.join(extras)})"
                            )
                        if "/Users/" in raw_text:
                            findings.append(f"{path.name}:hardcoded-user-path")

            metrics = measure_description_bytes(skill_md)
            raw_bytes = metrics["raw_bytes"]
            allowed_max = LEGACY_VENDOR_BYTE_EXCEPTIONS.get(path.name, MAX_VENDOR_DESCRIPTION_BYTES)
            if raw_bytes == 0:
                findings.append(f"{path.name}:empty-description")
            elif raw_bytes > allowed_max:
                findings.append(f"{path.name}:description-exceeds-1024-bytes({raw_bytes})")
        except (OSError, ValueError):  # fmt: skip
            findings.append(f"{path.name}:invalid-frontmatter-description")
    return findings


def malformed_entries(root: Path) -> list[str]:
    """Report skill entries that resolve but are not discoverable or violate frontmatter bounds."""
    findings: list[str] = []
    if not root.is_dir():
        return findings
    locked_skills = _load_locked_skill_names(root)
    for path in sorted(root.iterdir()):
        if path.name.startswith(".") or not path.is_dir():
            continue
        if not (path / "SKILL.md").is_file():
            continue
        findings.extend(_skill_entry_violations(path, locked_skills=locked_skills))
    return findings


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
            path.relative_to(left): file_digest(path) for path in left.rglob("*") if path.is_file()
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
        shutil.rmtree(path, ignore_errors=True)


def reconcile_links(
    *,
    destination: Path,
    desired: dict[str, Path],
    managed_target_roots: tuple[Path, ...],
    check: bool,
    preserve_unlisted_workspace_links: bool = False,
) -> Result:
    if not destination.is_dir():
        if not desired:
            return Result([], [], [], [])
        if check:
            return Result([], [], [f"missing-destination:{destination}"], [])
        destination.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    removed: list[str] = []
    conflicts: list[str] = []
    broken: list[str] = []

    resolved_roots = tuple(root.resolve() for root in managed_target_roots)

    def _is_managed(t: Path) -> bool:
        for root in resolved_roots:
            try:
                if t == root or t.is_relative_to(root):
                    return True
            except ValueError:
                continue
        return False

    marker_path = destination / HERMES_MANAGED_MARKER
    previously_managed: set[str] = set()
    if preserve_unlisted_workspace_links and marker_path.is_file():
        previously_managed = manifest(marker_path)

    for path in sorted(destination.iterdir()):
        if path.name.startswith("."):
            continue
        if not path.is_symlink():
            continue
        is_broken = not path.exists()
        raw = Path(os.path.normpath(path.parent / path.readlink()))
        immediate_target = raw.parent.resolve() / raw.name
        resolved_target = Path(os.path.realpath(path))
        if not (_is_managed(immediate_target) or _is_managed(resolved_target)):
            continue
        target = resolved_target
        expected = desired.get(path.name)
        if expected is None:
            if (
                preserve_unlisted_workspace_links
                and not is_broken
                and path.name not in previously_managed
            ):
                continue
            removed.append(path.name)
            if not check:
                path.unlink()
        elif is_broken or target != expected.resolve():
            removed.append(path.name)
            if not check:
                path.unlink()

    for name, source in sorted(desired.items()):
        target = destination / name
        if points_to(target, source):
            continue
        if target.exists() or target.is_symlink():
            if not target.exists() or equivalent(target, source):
                if name not in removed:
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

    if preserve_unlisted_workspace_links and not check:
        active_managed = sorted(
            name for name, source in desired.items() if points_to(destination / name, source)
        )
        marker_path.write_text(
            "# Managed by sync-workspace-agent-skills.py (hermes-user-skill-manifest.txt)\n"
            + "".join(f"{name}\n" for name in active_managed),
            encoding="utf-8",
        )

    if destination.is_dir():
        for path in sorted(destination.iterdir()):
            if path.name.startswith("."):
                continue
            if path.is_symlink() and not path.exists():
                if path.name not in removed:
                    broken.append(path.name)

    if not desired and not check and destination.is_dir():
        try:
            if not any(destination.iterdir()):
                destination.rmdir()
                parent = destination.parent
                if parent.name == "commands" and parent.is_dir() and not any(parent.iterdir()):
                    parent.rmdir()
        except OSError:
            pass
    return Result(created, removed, conflicts, broken)


def prune_unallowlisted_skill_surfaces(workspace: Path) -> list[str]:
    """Remove unallowlisted data/skills and agent/skills trees recreated by `skills update -y`."""
    pruned: list[str] = []
    if not workspace.is_dir():
        return pruned
    for forbidden_rel in ("data/skills", "agent/skills", "agent"):
        p = workspace / forbidden_rel
        if forbidden_rel == "agent" and p.is_dir() and not p.is_symlink():
            # Only remove `agent` if it is empty or contains only `skills`
            entries = [e.name for e in p.iterdir()]
            if entries and entries != ["skills"]:
                continue
        if p.exists() or p.is_symlink():
            remove_path(p)
            pruned.append(forbidden_rel)
    return pruned


def check_workspace_agent_surface(workspace: Path) -> list[str]:
    """Verify no unallowlisted project skill trees exist in workspace root."""
    violations: list[str] = []
    if not workspace.is_dir():
        return violations
    for forbidden_rel in ("skills", "agent", "data/skills"):
        p = workspace / forbidden_rel
        if p.exists() or p.is_symlink():
            violations.append(forbidden_rel)
    for entry in sorted(workspace.iterdir()):
        if not entry.name.startswith(".") or not entry.is_dir():
            continue
        if entry.name in ALLOWED_WORKSPACE_SKILL_PARENTS:
            continue
        sub_skills = entry / "skills"
        if sub_skills.exists() or sub_skills.is_symlink():
            violations.append(f"{entry.name}/skills")
    codex_skills = workspace / ".codex" / "skills"
    if codex_skills.is_dir():
        for entry in sorted(codex_skills.iterdir()):
            if entry.name not in ALLOWED_CODEX_PROJECT_ENTRIES:
                violations.append(f".codex/skills/{entry.name}")
    return violations


def collect_skill_files(skill_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    if not skill_dir.is_dir():
        return files
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file() and not path.is_symlink():
            rel = path.relative_to(skill_dir).as_posix()
            files[rel] = file_digest(path)
    return files


def atomic_write_bytes(target: Path, data: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
        os.replace(tmp_name, target)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def detect_cli_version() -> str:
    skills_bin = shutil.which("skills") or "/opt/homebrew/bin/skills"
    if os.path.exists(skills_bin):
        try:
            proc = subprocess.run(
                [skills_bin, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return proc.stdout.strip().splitlines()[0]
        except Exception:
            pass
    return "unknown"


def load_lockfile(lock_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not lock_path.is_file():
        return None, [f"missing-lockfile:{lock_path}"]
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"invalid-lockfile-json:{lock_path}:{exc}"]
    if (
        not isinstance(data, dict)
        or data.get("version") not in (1, 2)
        or not isinstance(data.get("skills"), dict)
    ):
        return None, [f"invalid-lockfile-schema:{lock_path}"]
    return data, []


def diff_against_snapshot(workspace: Path, snapshot_dir: Path) -> tuple[bool, list[str], list[str]]:
    """Compare live workspace against snapshot_dir.

    Returns (has_drift, drift_findings, mutated_skills).
    """
    findings: list[str] = []
    mutated_skills: set[str] = set()
    manifest_path = snapshot_dir / "manifest.json"
    snap_lock_path = snapshot_dir / "skills-lock.json"
    root_lock_path = workspace / "skills-lock.json"
    replica_lock_path = workspace / ".agents" / "skills-lock.json"

    if not manifest_path.is_file() or not snap_lock_path.is_file():
        return True, ["snapshot-incomplete"], []

    try:
        snap_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return True, [f"snapshot-manifest-corrupt:{exc}"], []

    if not root_lock_path.is_file():
        findings.append("missing-root-lockfile")
    elif file_digest(root_lock_path) != file_digest(snap_lock_path):
        findings.append("root-lockfile-differs-from-snapshot")

    if not replica_lock_path.is_file():
        findings.append("missing-replica-lockfile")
    elif root_lock_path.is_file() and file_digest(root_lock_path) != file_digest(replica_lock_path):
        findings.append("replica-lockfile-differs-from-root")

    snap_skills = snap_manifest.get("skills", {})
    skills_root = workspace / ".agents" / "skills"
    for name, meta in sorted(snap_skills.items()):
        expected_files = meta.get("files", {})
        live_files = collect_skill_files(skills_root / name)
        if live_files != expected_files:
            mutated_skills.add(name)
            findings.append(f"skill-bytes-drifted:{name}")

    return bool(findings), findings, sorted(mutated_skills)


def accept_or_bootstrap_snapshot(
    *, workspace: Path, bootstrap: bool
) -> tuple[bool, list[str], list[str]]:
    """Validate registry-tracked skills and publish snapshot + .agents/skills-lock.json.

    Returns (ok, errors, mutated_skills).
    """
    errors: list[str] = []
    root_lock_path = workspace / "skills-lock.json"
    replica_lock_path = workspace / ".agents" / "skills-lock.json"
    skills_root = workspace / ".agents" / "skills"
    snapshot_root = workspace / ".agents" / ".skill-snapshots"
    current_dir = snapshot_root / "current"
    previous_dir = snapshot_root / "previous"

    prune_unallowlisted_skill_surfaces(workspace)
    surface_violations = check_workspace_agent_surface(workspace)
    for v in surface_violations:
        errors.append(f"surface-violation:{v}")

    lock_data, lock_errs = load_lockfile(root_lock_path)
    if lock_errs or lock_data is None:
        errors.extend(lock_errs)
        _, _, mutated = (
            diff_against_snapshot(workspace, current_dir)
            if (current_dir / "manifest.json").is_file()
            else (False, [], [])
        )
        return False, errors, mutated

    locked_skills: dict[str, Any] = lock_data["skills"]
    current_manifest: dict[str, Any] | None = None
    if (current_dir / "manifest.json").is_file():
        try:
            current_manifest = json.loads(
                (current_dir / "manifest.json").read_text(encoding="utf-8")
            )
        except Exception as exc:
            errors.append(f"corrupt-current-manifest:{exc}")

    if current_manifest is not None:
        prev_skills = current_manifest.get("skills", {})
        for prev_name, prev_meta in sorted(prev_skills.items()):
            if prev_name not in locked_skills:
                errors.append(f"missing-previously-tracked-skill:{prev_name}")
                continue
            new_source = locked_skills[prev_name].get("source")
            old_source = prev_meta.get("source")
            if old_source and new_source != old_source:
                errors.append(f"source-collision:{prev_name}:{old_source}->{new_source}")

    for pt_name in PONYTAIL_SKILLS:
        if pt_name in locked_skills:
            pt_entry = locked_skills[pt_name]
            if pt_entry.get("source") != "DietrichGebert/ponytail":
                errors.append(f"{pt_name}:unexpected-source:{pt_entry.get('source')}")
            if pt_entry.get("sourceType") != "github":
                errors.append(f"{pt_name}:unexpected-sourceType:{pt_entry.get('sourceType')}")
            if pt_entry.get("skillPath") != f"skills/{pt_name}/SKILL.md":
                errors.append(f"{pt_name}:unexpected-skillPath:{pt_entry.get('skillPath')}")

    manifest_skills: dict[str, Any] = {}
    for name, entry in sorted(locked_skills.items()):
        if not isinstance(entry, dict):
            errors.append(f"{name}:invalid-lock-entry")
            continue
        source = entry.get("source", "")
        source_type = entry.get("sourceType", "")
        skill_path = entry.get("skillPath", "")
        computed_hash = entry.get("computedHash", "")
        if not source or not source_type or not skill_path or not computed_hash:
            errors.append(f"{name}:incomplete-lock-metadata")
            continue

        skill_dir = skills_root / name
        if not skill_dir.is_dir():
            errors.append(f"{name}:missing-skill-dir")
            continue
        entry_violations = _skill_entry_violations(
            skill_dir, locked_skills=set(locked_skills.keys())
        )
        if entry_violations:
            errors.extend(entry_violations)
            continue

        skill_md = skill_dir / "SKILL.md"
        desc_metrics = measure_description_bytes(skill_md)
        files_map = collect_skill_files(skill_dir)
        if "SKILL.md" not in files_map:
            errors.append(f"{name}:missing-SKILL.md-digest")
            continue

        # If not bootstrapping and computedHash did not change from current snapshot,
        # local bytes MUST match the accepted snapshot (catches silent local tampering).
        if not bootstrap and current_manifest is not None:
            prev_meta = current_manifest.get("skills", {}).get(name)
            if prev_meta and prev_meta.get("computedHash") == computed_hash:
                if files_map != prev_meta.get("files", {}):
                    errors.append(f"{name}:local-byte-tampering-without-hash-change")
                    continue

        raw_ref = str(entry.get("ref", "") or entry.get("commit", "") or "")
        if HEX40_RE.match(raw_ref):
            source_revision = raw_ref
            upstream_verified = True
        else:
            source_revision = "unknown"
            upstream_verified = False

        manifest_skills[name] = {
            "source": source,
            "sourceType": source_type,
            "skillPath": skill_path,
            "computedHash": computed_hash,
            "source_revision": source_revision,
            "upstream_verified": upstream_verified,
            "description_bytes": desc_metrics["raw_bytes"],
            "description_trimmed_bytes": desc_metrics["trimmed_bytes"],
            "files": files_map,
        }

    if errors:
        _, _, mutated = (
            diff_against_snapshot(workspace, current_dir)
            if (current_dir / "manifest.json").is_file()
            else (False, [], [])
        )
        return False, errors, mutated

    root_lock_bytes = root_lock_path.read_bytes()
    has_current = (current_dir / "manifest.json").is_file() and (
        current_dir / "skills-lock.json"
    ).is_file()
    state_changed = True
    if has_current and current_manifest is not None:
        same_lock = file_digest(root_lock_path) == file_digest(current_dir / "skills-lock.json")
        prev_files = {k: v.get("files", {}) for k, v in current_manifest.get("skills", {}).items()}
        curr_files = {k: v["files"] for k, v in manifest_skills.items()}
        if same_lock and prev_files == curr_files:
            state_changed = False

    if not has_current or state_changed or bootstrap:
        snapshot_root.mkdir(parents=True, exist_ok=True)
        staging_dir = Path(tempfile.mkdtemp(prefix=".staging-", dir=str(snapshot_root)))
        try:
            files_root = staging_dir / "files"
            files_root.mkdir(parents=True, exist_ok=True)
            total_bytes = 0
            for name in sorted(manifest_skills):
                src_dir = skills_root / name
                dst_dir = files_root / name
                shutil.copytree(src_dir, dst_dir, symlinks=False)
                for fpath in dst_dir.rglob("*"):
                    if fpath.is_file():
                        total_bytes += fpath.stat().st_size

            (staging_dir / "skills-lock.json").write_bytes(root_lock_bytes)
            total_bytes += len(root_lock_bytes)

            manifest_payload = {
                "version": 1,
                "accepted_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "cli_version": detect_cli_version(),
                "total_bytes": total_bytes,
                "skills": manifest_skills,
            }
            manifest_bytes = (json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n").encode(
                "utf-8"
            )
            (staging_dir / "manifest.json").write_bytes(manifest_bytes)

            if has_current and state_changed:
                if previous_dir.exists():
                    shutil.rmtree(previous_dir)
                os.replace(current_dir, previous_dir)
                os.replace(staging_dir, current_dir)
            else:
                if current_dir.exists():
                    shutil.rmtree(current_dir)
                os.replace(staging_dir, current_dir)
                if previous_dir.exists():
                    shutil.rmtree(previous_dir)
                shutil.copytree(current_dir, previous_dir, symlinks=False)
        finally:
            if staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)

    atomic_write_bytes(replica_lock_path, root_lock_bytes)
    return True, [], []


def recover_from_snapshot(*, workspace: Path) -> tuple[bool, list[str], list[str]]:
    """Restore mutated registry-tracked skills and root skills-lock.json from current snapshot."""
    snapshot_root = workspace / ".agents" / ".skill-snapshots"
    current_dir = snapshot_root / "current"
    manifest_path = current_dir / "manifest.json"
    snap_lock_path = current_dir / "skills-lock.json"
    files_root = current_dir / "files"

    if not manifest_path.is_file() or not snap_lock_path.is_file() or not files_root.is_dir():
        return (
            False,
            [
                "recovery-failed:missing-accepted-snapshot(computedHash-alone-cannot-reconstruct-bytes)"
            ],
            [],
        )

    try:
        snap_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"recovery-failed:corrupt-snapshot-manifest:{exc}"], []

    snap_skills = snap_manifest.get("skills", {})
    if not isinstance(snap_skills, dict) or not snap_skills:
        return False, ["recovery-failed:empty-snapshot-manifest"], []

    # Verify snapshot payload digests before restoring
    for name, meta in sorted(snap_skills.items()):
        snap_skill_dir = files_root / name
        expected_files = meta.get("files", {})
        if not snap_skill_dir.is_dir() or collect_skill_files(snap_skill_dir) != expected_files:
            return False, [f"recovery-failed:corrupt-snapshot-payload:{name}"], []

    _, findings, mutated_skills = diff_against_snapshot(workspace, current_dir)
    skills_root = workspace / ".agents" / "skills"
    skills_root.mkdir(parents=True, exist_ok=True)

    for name in mutated_skills:
        target_dir = skills_root / name
        source_dir = files_root / name
        if target_dir.exists() or target_dir.is_symlink():
            remove_path(target_dir)
        shutil.copytree(source_dir, target_dir, symlinks=False)

    root_lock_path = workspace / "skills-lock.json"
    snap_lock_bytes = snap_lock_path.read_bytes()
    if not root_lock_path.is_file() or root_lock_path.read_bytes() != snap_lock_bytes:
        atomic_write_bytes(root_lock_path, snap_lock_bytes)

    replica_lock_path = workspace / ".agents" / "skills-lock.json"
    if not replica_lock_path.is_file() or replica_lock_path.read_bytes() != snap_lock_bytes:
        atomic_write_bytes(replica_lock_path, snap_lock_bytes)

    return True, findings, mutated_skills


def extract_skill_metadata(skill_md_path: Path) -> dict[str, str]:
    """Extract string fields from `metadata:` block in YAML frontmatter."""
    if not skill_md_path.is_file():
        return {}
    try:
        raw_text = skill_md_path.read_text(encoding="utf-8")
    except OSError:
        return {}
    if not raw_text.startswith("---"):
        return {}
    parts = raw_text.split("---", 2)
    if len(parts) < 3:
        return {}
    fm_lines = parts[1].splitlines()
    in_metadata = False
    metadata: dict[str, str] = {}
    for line in fm_lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        top_match = re.match(r"^([a-zA-Z0-9_-]+)\s*:", line)
        if top_match and not line.startswith(" ") and not line.startswith("	"):
            in_metadata = top_match.group(1) == "metadata"
            continue
        if in_metadata:
            sub_match = re.match(r"^\s+([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
            if sub_match:
                key = sub_match.group(1)
                val = sub_match.group(2).strip().strip('"').strip("'")
                metadata[key] = val
    return metadata


OWN_FILES_SKILL_DIRS: dict[str, str] = {
    "claude": ".claude/skills",
    "kiro": ".kiro/skills",
    "hermes": ".hermes/skills",
}

OPENSPEC_RETIRED_COMMAND_DIRS: tuple[str, ...] = (
    ".agents/workflows",
    ".claude/commands/opsx",
    ".factory/commands",
    ".junie/commands",
    ".kilocode/workflows",
    ".kiro/prompts",
    ".pi/prompts",
    ".qoder/commands/opsx",
)


def _build_openspec_subprocess_env(home: Path | None, config_path: Path | None) -> dict[str, str]:
    env = dict(os.environ)
    if home is not None:
        env["HOME"] = str(home)
    if config_path is not None:
        env["XDG_CONFIG_HOME"] = str(config_path.parent.parent)
    return env


def _parse_cli_major(cli_version: str) -> int:
    match = re.match(r"^v?(\d+)", cli_version.strip())
    return int(match.group(1)) if match else 0


def _inspect_shared_skill_layout(store: Path, cli_version: str) -> list[str]:
    """Inspect OpenSpec 2.0 shared canonical skill layout, own-files links, and retired host copies."""
    reasons: list[str] = []
    target_file = store / ".agents" / "skills" / ".openspec-target"
    canonical_dir = store / ".agents" / "skills"
    cli_major = _parse_cli_major(cli_version)

    kept_skills: set[str] = set()
    own_files_tools: set[str] = set()

    if cli_major >= 2:
        if not target_file.is_file():
            reasons.append("openspec-missing-target-list")
        else:
            for raw_line in target_file.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) == 2 and parts[0] == "keep" and parts[1].startswith("openspec-"):
                    kept_skills.add(parts[1])
                elif (
                    len(parts) == 2
                    and parts[1] == "own-files"
                    and parts[0] not in {"keep", "own-files"}
                ):
                    own_files_tools.add(parts[0])
                elif len(parts) == 1 and parts[0] not in {"keep", "own-files"}:
                    pass
                else:
                    reasons.append(f"openspec-invalid-target-line:{line}")
            if "claude" not in own_files_tools:
                reasons.append("openspec-missing-claude-own-files")

    canonical_skills: list[str] = []
    found_versions: set[str] = set()
    if canonical_dir.is_dir():
        for entry in sorted(canonical_dir.glob("openspec-*")):
            skill = entry.name
            if skill in kept_skills:
                if not entry.exists():
                    reasons.append(f"openspec-missing-kept-skill:{skill}")
                continue
            if entry.is_symlink():
                reasons.append(f"openspec-canonical-symlink:{skill}")
                continue
            if not entry.is_dir():
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.is_file() or skill_md.is_symlink():
                reasons.append(f"openspec-missing-skill-md:{skill}")
                continue
            canonical_skills.append(skill)
            extra_mds = [p.name for p in sorted(entry.glob("*.md")) if p.name != "SKILL.md"]
            if extra_mds:
                reasons.append(f"openspec-unexpected-split-files:{skill}")
            meta = extract_skill_metadata(skill_md)
            gen = meta.get("generatedBy", "").strip()
            if not gen:
                reasons.append(f"openspec-missing-generatedBy:{skill}")
            else:
                found_versions.add(gen)

    if not canonical_skills and not kept_skills:
        reasons.append("openspec-missing-canonical-skills")
    elif found_versions and found_versions != {cli_version}:
        reasons.append(
            f"openspec-version-drift:cli={cli_version},skills={','.join(sorted(found_versions))}"
        )

    canonical_set = set(canonical_skills)
    for tool in sorted(own_files_tools):
        rel_dir = OWN_FILES_SKILL_DIRS.get(tool, f".{tool}/skills")
        tool_dir = store / rel_dir
        for skill in canonical_skills:
            entry = tool_dir / skill
            expected_target = (canonical_dir / skill).resolve()
            is_valid_rel_symlink = (
                entry.is_symlink()
                and not entry.readlink().is_absolute()
                and entry.exists()
                and Path(os.path.realpath(entry)) == expected_target
            )
            if not is_valid_rel_symlink:
                reasons.append(f"openspec-broken-own-files-link:{tool}/{skill}")
        if tool_dir.is_dir():
            for entry in sorted(tool_dir.glob("openspec-*")):
                if entry.name in kept_skills:
                    if not entry.exists():
                        reasons.append(f"openspec-broken-own-files-link:{tool}/{entry.name}")
                elif entry.name not in canonical_set:
                    reasons.append(f"openspec-stale-own-files-entry:{tool}/{entry.name}")

    declared_own_files_rel_dirs = {
        OWN_FILES_SKILL_DIRS.get(tool, f".{tool}/skills") for tool in own_files_tools
    }
    for dot_dir in sorted(store.glob(".*")):
        if not dot_dir.is_dir() or dot_dir.name in {".agents", ".git"}:
            continue
        rel_skills_dir = f"{dot_dir.name}/skills"
        if rel_skills_dir in declared_own_files_rel_dirs:
            continue
        skills_dir = dot_dir / "skills"
        if skills_dir.is_dir():
            for entry in sorted(skills_dir.glob("openspec-*")):
                reasons.append(f"openspec-retired-host-copy:{dot_dir.name}/skills/{entry.name}")

    for cdir in OPENSPEC_RETIRED_COMMAND_DIRS:
        target_dir = store / cdir
        if target_dir.is_dir() and any(target_dir.glob("*.md")):
            reasons.append(f"openspec-retired-command-present:{cdir}")

    return reasons


def _verify_openspec_dry_run_clean(exe: str, store: Path, env: dict[str, str]) -> list[str]:
    try:
        proc = subprocess.run(
            [exe, "update", "--dry-run", "--json", str(store)],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
            env=env,
        )
    except OSError as err:
        return [f"openspec-dry-run-failed:oserror:{err}"]
    except subprocess.TimeoutExpired:
        return ["openspec-dry-run-failed:timeout"]

    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout).strip()
        return [f"openspec-dry-run-failed:rc={proc.returncode}:{detail}"]

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as err:
        return [f"openspec-dry-run-failed:invalid-json:{err}"]

    if not isinstance(data, dict):
        return ["openspec-dry-run-failed:invalid-json:expected-object"]

    changes = data.get("changes", [])
    notes = data.get("notes", [])
    failures = data.get("failures", [])
    if changes or notes or failures:
        payload = json.dumps({"changes": changes, "notes": notes, "failures": failures})
        return [
            f"openspec-dry-run-drift:changes={len(changes)},notes={len(notes)},failures={len(failures)}:{payload}"
        ]
    return []


def reconcile_openspec_generator_parity(
    store: Path,
    *,
    check: bool,
    openspec_bin: str | None = None,
    config_path: Path | None = None,
    home: Path | None = None,
) -> tuple[bool, list[str]]:
    """Verify and reconcile parity between OpenSpec CLI version and shared skill layout."""
    target_file = store / ".agents" / "skills" / ".openspec-target"
    canonical_dir = store / ".agents" / "skills"
    has_openspec_metadata = False
    if canonical_dir.is_dir():
        for sdir in sorted(canonical_dir.glob("openspec-*")):
            skill_md = sdir / "SKILL.md"
            if skill_md.is_file():
                meta = extract_skill_metadata(skill_md)
                if meta.get("author") == "openspec" or "generatedBy" in meta:
                    has_openspec_metadata = True
                    break
    # Important test-compatibility guard: if .openspec-target is absent and zero
    # openspec-*/SKILL.md files declare openspec metadata, return (True, []) so
    # minimal synthetic unit-test fixtures remain isolated.
    if not target_file.exists() and not has_openspec_metadata:
        return True, []

    if config_path is not None and (
        config_path.name != "config.json" or config_path.parent.name != "openspec"
    ):
        msg = f"openspec-invalid-config-path:{config_path}"
        print(f"openspec_generator_parity=failed reasons={msg}", file=sys.stderr)
        return False, [msg]

    exe = openspec_bin or shutil.which("openspec")
    if not exe:
        return True, []

    env = _build_openspec_subprocess_env(home, config_path)
    try:
        proc = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
            env=env,
        )
    except OSError as err:
        return False, [f"openspec-version-error:{err}"]
    except subprocess.TimeoutExpired:
        return False, ["openspec-version-error:timeout"]

    if proc.returncode != 0 or not proc.stdout.strip():
        return False, [f"openspec-version-error:rc={proc.returncode}"]

    cli_version = proc.stdout.strip().splitlines()[0].strip()
    layout_drift = _inspect_shared_skill_layout(store, cli_version)

    if check:
        if layout_drift:
            print(
                f"openspec_generator_parity=drift cli={cli_version} reasons={','.join(layout_drift)}",
                file=sys.stderr,
            )
            return False, layout_drift
        dry_run_drift = _verify_openspec_dry_run_clean(exe, store, env)
        if dry_run_drift:
            print(
                f"openspec_generator_parity=drift cli={cli_version} reasons={','.join(dry_run_drift)}",
                file=sys.stderr,
            )
            return False, dry_run_drift
        print(f"openspec_generator_parity=ok cli={cli_version}")
        return True, []

    if not layout_drift:
        dry_run_drift = _verify_openspec_dry_run_clean(exe, store, env)
        if not dry_run_drift:
            print(f"openspec_generator_parity=ok cli={cli_version}")
            return True, []

    if os.environ.get("DISABLE_UPDATES", "").strip().lower() in {"1", "true", "yes"}:
        print(f"openspec_generator_parity=paused cli={cli_version}")
        return True, []

    try:
        upd = subprocess.run(
            [exe, "update", str(store)],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
            env=env,
        )
    except OSError as err:
        msg = f"openspec-update-failed:{err}"
        print(f"openspec_generator_parity=failed cli={cli_version} reasons={msg}", file=sys.stderr)
        return False, [msg]
    except subprocess.TimeoutExpired:
        msg = "openspec-update-failed:timeout"
        print(f"openspec_generator_parity=failed cli={cli_version} reasons={msg}", file=sys.stderr)
        return False, [msg]

    if upd.returncode != 0:
        detail = (upd.stderr or upd.stdout).strip()
        msg = f"openspec-update-failed:rc={upd.returncode}" + (f":{detail}" if detail else "")
        print(f"openspec_generator_parity=failed cli={cli_version} reasons={msg}", file=sys.stderr)
        return False, [msg]

    post_layout = _inspect_shared_skill_layout(store, cli_version)
    post_dry_run = _verify_openspec_dry_run_clean(exe, store, env)
    post_msgs = post_layout + post_dry_run
    if post_msgs:
        print(
            f"openspec_generator_parity=failed cli={cli_version} reasons={','.join(post_msgs)}",
            file=sys.stderr,
        )
        return False, post_msgs

    print(f"openspec_generator_parity=reconciled cli={cli_version}")
    return True, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Synchronize workspace agent skill symlinks and manage accepted skill snapshots."
    )
    parser.add_argument("--check", action="store_true", help="verify only (strictly non-mutating)")
    parser.add_argument(
        "--bootstrap-snapshot",
        action="store_true",
        help="verify registry-tracked skills, initialize .skill-snapshots/{current,previous}, and publish .agents/skills-lock.json",
    )
    parser.add_argument(
        "--accept-refresh",
        action="store_true",
        help="verify completed skills refresh, rotate .skill-snapshots/{current,previous}, and publish .agents/skills-lock.json",
    )
    parser.add_argument(
        "--recover-from-snapshot",
        action="store_true",
        help="restore mutated registry-tracked skill directories and root skills-lock.json from .skill-snapshots/current",
    )
    parser.add_argument("--workspace-root", type=Path, default=None, help="override workspace root")
    parser.add_argument(
        "--store-root", type=Path, default=None, help="override openspec-store root"
    )
    parser.add_argument("--home-dir", type=Path, default=None, help="override user home directory")
    parser.add_argument(
        "--openspec-bin",
        type=str,
        default=None,
        help="path to openspec executable (default: resolved from PATH)",
    )
    parser.add_argument(
        "--openspec-config",
        type=Path,
        default=None,
        help="path to openspec config.json (default: ~/.config/openspec/config.json)",
    )
    parser.add_argument(
        "--sync-lock",
        dest="sync_lock",
        type=Path,
        default=None,
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args(argv)

    workspace = args.workspace_root.resolve() if args.workspace_root else WORKSPACE
    store = args.store_root.resolve() if args.store_root else STORE
    home = args.home_dir.resolve() if args.home_dir else HOME

    workspace_agents = workspace / ".agents" / "skills" if args.workspace_root else WORKSPACE_AGENTS
    workspace_claude_skills = (
        workspace / ".claude" / "skills" if args.workspace_root else WORKSPACE_CLAUDE_SKILLS
    )
    workspace_claude_commands = (
        workspace / ".claude" / "commands" / "opsx"
        if args.workspace_root
        else WORKSPACE_CLAUDE_COMMANDS
    )
    user_agents = home / ".agents" / "skills" if args.home_dir else USER_AGENTS
    user_claude_skills = home / ".claude" / "skills" if args.home_dir else USER_CLAUDE_SKILLS
    user_claude_commands = (
        home / ".claude" / "commands" / "opsx" if args.home_dir else USER_CLAUDE_COMMANDS
    )
    user_hermes_skills = home / ".hermes" / "skills" if args.home_dir else USER_HERMES_SKILLS

    store_standard = store / ".agents" / "skills" if args.store_root else STORE_STANDARD
    store_claude_skills = store / ".claude" / "skills" if args.store_root else STORE_CLAUDE_SKILLS
    store_claude_commands = (
        store / ".claude" / "commands" / "opsx" if args.store_root else STORE_CLAUDE_COMMANDS
    )
    codex_manifest_path = (
        store / "config" / "codex-user-skill-manifest.txt" if args.store_root else CODEX_MANIFEST
    )
    claude_manifest_path = (
        store / "config" / "claude-user-skill-manifest.txt" if args.store_root else CLAUDE_MANIFEST
    )
    hermes_manifest_path = (
        store / "config" / "hermes-user-skill-manifest.txt" if args.store_root else HERMES_MANIFEST
    )
    if args.recover_from_snapshot and not args.accept_refresh and not args.bootstrap_snapshot:
        ok, findings, recovered = recover_from_snapshot(workspace=workspace)
        print(f"snapshot_recovery={'ok' if ok else 'failed'}")
        if findings:
            print("mutated_findings=" + ",".join(findings))
        print("recovered_skills=" + ",".join(recovered))
        return 0 if ok else 1

    if args.bootstrap_snapshot or args.accept_refresh:
        ok, errors, mutated = accept_or_bootstrap_snapshot(
            workspace=workspace, bootstrap=args.bootstrap_snapshot
        )
        mode_label = "bootstrap_snapshot" if args.bootstrap_snapshot else "accept_refresh"
        print(f"{mode_label}={'ok' if ok else 'failed'}")
        if errors:
            for err in errors:
                print(f"{mode_label}.error={err}")
        if mutated:
            print("mutated_skills=" + ",".join(mutated))
        if not ok and args.recover_from_snapshot:
            rec_ok, _, recovered = recover_from_snapshot(workspace=workspace)
            print(f"snapshot_recovery={'ok' if rec_ok else 'failed'}")
            print("recovered_skills=" + ",".join(recovered))
        return 0 if ok else 1

    def _execute_sync() -> int:
        open_spec_names = tuple(
            sorted(
                path.name
                for path in store_standard.glob("openspec-*")
                if (path / "SKILL.md").is_file()
            )
        )
        workspace_roots, containers = skill_roots(workspace_agents)
        codex_selected = manifest(codex_manifest_path) if codex_manifest_path.is_file() else set()
        claude_selected = (
            manifest(claude_manifest_path) if claude_manifest_path.is_file() else set()
        )
        hermes_selected = (
            manifest(hermes_manifest_path) if hermes_manifest_path.is_file() else set()
        )
        selected = codex_selected | claude_selected | hermes_selected
        missing = sorted(selected - workspace_roots.keys())
        if missing:
            print("missing_manifest_entries=" + ",".join(missing))
            return 1

        standard_openspec = {name: store_standard / name for name in open_spec_names}
        claude_openspec = {name: store_claude_skills / name for name in open_spec_names}
        claude_commands = (
            {path.name: path for path in sorted(store_claude_commands.glob("*.md"))}
            if store_claude_commands.is_dir()
            else {}
        )

        results = {
            "workspace_agents": reconcile_links(
                destination=workspace_agents,
                desired=standard_openspec,
                managed_target_roots=(store_standard,),
                check=args.check,
            ),
            "user_agents": reconcile_links(
                destination=user_agents,
                desired={name: workspace_roots[name] for name in codex_selected},
                managed_target_roots=(workspace_agents,),
                check=args.check,
            ),
            "workspace_claude_skills": reconcile_links(
                destination=workspace_claude_skills,
                desired=claude_openspec,
                managed_target_roots=(store_claude_skills, store_standard),
                check=args.check,
            ),
            "user_claude_skills": reconcile_links(
                destination=user_claude_skills,
                desired={
                    **claude_openspec,
                    **{name: workspace_roots[name] for name in claude_selected},
                },
                managed_target_roots=(store_claude_skills, store_standard, workspace_agents),
                check=args.check,
            ),
            "user_hermes_skills": reconcile_links(
                destination=user_hermes_skills,
                desired={name: workspace_roots[name] for name in hermes_selected},
                managed_target_roots=(workspace_agents,),
                check=args.check,
                preserve_unlisted_workspace_links=True,
            ),
            "workspace_claude_commands": reconcile_links(
                destination=workspace_claude_commands,
                desired=claude_commands,
                managed_target_roots=(store_claude_commands,),
                check=args.check,
            ),
            "user_claude_commands": reconcile_links(
                destination=user_claude_commands,
                desired=claude_commands,
                managed_target_roots=(store_claude_commands,),
                check=args.check,
            ),
        }

        print(
            f"canonical_direct_roots={len(workspace_roots)} "
            f"containers={len(containers)} codex_selected={len(codex_selected)} "
            f"claude_selected={len(claude_selected)} hermes_selected={len(hermes_selected)} "
            f"openspec_targets={len(open_spec_names)} "
            f"claude_commands={len(claude_commands)} check={args.check}"
        )
        if containers:
            print("containers=" + ",".join(containers))

        malformed = malformed_entries(workspace_agents)
        print(f"malformed_entries={len(malformed)}")
        for finding in malformed:
            print("malformed_entries.finding=" + finding)

        if not args.check:
            prune_unallowlisted_skill_surfaces(workspace)
        surface_violations = check_workspace_agent_surface(workspace)
        if surface_violations:
            print("surface_violations=" + ",".join(surface_violations))

        failed = bool(malformed) or bool(surface_violations)
        if args.check and not parity_ok:
            failed = True
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
            if (
                result.conflicts
                or result.broken
                or (args.check and (result.created or result.removed))
            ):
                failed = True

        if args.check:
            current_snap = workspace / ".agents" / ".skill-snapshots" / "current"
            if (current_snap / "manifest.json").is_file():
                has_drift, drift_findings, mutated = diff_against_snapshot(workspace, current_snap)
                print(f"snapshot_check={'failed' if has_drift else 'ok'}")
                for df in drift_findings:
                    print(f"snapshot_drift={df}")
                if mutated:
                    print("mutated_skills=" + ",".join(mutated))
                if has_drift:
                    failed = True

        return 1 if failed else 0

    parity_ok = True
    if args.check:
        parity_ok, _ = reconcile_openspec_generator_parity(
            store,
            check=True,
            openspec_bin=args.openspec_bin,
            config_path=args.openspec_config,
            home=home,
        )
        return _execute_sync()
    else:
        lock_path = args.sync_lock if args.sync_lock else OPENSPEC_SYNC_LOCK
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        with open(lock_path, "a+") as lock_fh:
            with contextlib.suppress(OSError):
                os.chmod(lock_path, 0o600)
            fcntl.flock(lock_fh.fileno(), fcntl.LOCK_EX)
            try:
                parity_ok, _ = reconcile_openspec_generator_parity(
                    store,
                    check=False,
                    openspec_bin=args.openspec_bin,
                    config_path=args.openspec_config,
                    home=home,
                )
                if not parity_ok:
                    return 1
                return _execute_sync()
            finally:
                with contextlib.suppress(OSError):
                    fcntl.flock(lock_fh.fileno(), fcntl.LOCK_UN)


if __name__ == "__main__":
    raise SystemExit(main())
