#!/usr/bin/env python3
"""Non-destructive inventory scanner for OpenSpec change cleanup-icloud-project-artifacts.

Metadata-only: uses os.scandir/lstat; never opens file contents.
Exact-basename directory matching; prunes walk at matched roots.
Writes manifest JSON to the change's evidence directory.
"""
import json
import os
import sys
from datetime import datetime

ROOTS = [
    "/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/microservices",
    "/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/vds",
]

# Exact-basename directory removal candidates (never prefix-matched)
DIR_CANDIDATES = {
    "node_modules": "package-cache",
    ".gradle": "build-cache",
    "build": "build-output",
    "dist": "build-output",
    "target": "build-output",
    "out": "build-output",
    "__pycache__": "python-cache",
    ".pytest_cache": "test-cache",
    ".ruff_cache": "lint-cache",
    ".mypy_cache": "lint-cache",
    ".hypothesis": "test-cache",
    "bin/obj": None,  # placeholder removed below; keep exact map clean
}
DIR_CANDIDATES.pop("bin/obj", None)

# Exact-basename file removal candidates
FILE_CANDIDATES = {".DS_Store": "os-metadata", ".coverage": "test-cache"}

# File-pattern removal candidates: mid-name marker (substring) vs suffix glob (endswith)
PATTERN_SUBSTR = [(".corrupted.", "sync-conflict")]
PATTERN_SUFFIX = [(".tmp", "temp-file"), (".log", "log-file")]

# Directory-pattern removal candidates (substring marker in basename)
DIR_PATTERN_CANDIDATES = [(".corrupted.", "sync-conflict")]


# Keep-list: basename-exact (files)
KEEP_FILE_NAMES = {
    ".env", ".gitignore", ".dockerignore", "Dockerfile", "compose.yml", "compose.yaml",
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "bun.lock",
    "bun.lockb", "build.gradle.kts", "build.gradle", "settings.gradle.kts", "pom.xml",
    "go.mod", "go.sum", "gradle.lockfile", "gradle-wrapper.properties", "Cargo.toml",
    "Cargo.lock", "Makefile", "requirements.txt", "pyproject.toml", "poetry.lock",
    "uv.lock", "Pipfile.lock", "setup.py", "tsconfig.json", "vite.config.ts",
    "next.config.js", "cloudbuild.yaml", "docker-compose.yml",
}

# Keep-list: file extensions (code, config, docs)
KEEP_EXTENSIONS = {
    ".go", ".py", ".pyi", ".kt", ".kts", ".java", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".proto", ".sql", ".yaml", ".yml", ".json", ".xml", ".toml", ".md", ".rst", ".adoc",
    ".pdf", ".sh", ".bash", ".zsh", ".tf", ".hcl", ".properties", ".conf", ".ini", ".cfg",
    ".html", ".css", ".scss", ".env", ".example", ".template", ".dockerfile", ".txt",
    ".gitattributes", ".editorconfig", ".gitkeep", ".nvmrc", ".node-version", ".python-version",
    ".bpmn", ".dmn", ".avsc", ".graphql", ".gql", ".hbs", ".ejs", ".vue", ".svelte",
    ".gradle", ".kts", ".jvm", ".plist", ".xcconfig", ".cmake", ".Dockerfile",
}

# Keep-list: basename-exact directories that must never be traversed as candidates
KEEP_DIR_NAMES = {
    ".git", ".git_disabled", "gradle", "buildSrc", "src", "lib", "pkg", "docs", "doc", "design-artifacts",
    "Documents", "documents", "scripts", "ci", ".github", ".terraform", "migrations",
}

TOP_LEVEL_ONLY_FILE_SCAN = True  # *.log/*.tmp/.DS_Store/.coverage found everywhere


def classify_file(name: str):
    """Return (is_candidate, category) or (False, None). Keep-list wins."""
    if name in KEEP_FILE_NAMES:
        return False, None
    base = name.lower()
    ext = os.path.splitext(name)[1].lower()
    if base.endswith(".env") or base.startswith(".env."):
        return False, None  # .env, .env.*, *.env kept
    # Keep-extension check BEFORE any pattern test: *.md, *.py etc. never match
    if ext in KEEP_EXTENSIONS:
        return False, None
    if name in FILE_CANDIDATES:
        return True, FILE_CANDIDATES[name]
    for marker, cat in PATTERN_SUBSTR:
        if marker in name:
            return True, cat
    for suffix, cat in PATTERN_SUFFIX:
        if name.endswith(suffix):
            return True, cat
    # Unknown extension: conservative keep (verification via manifest review)
    return False, None


def count_tree(path: str):
    """Metadata-only count of files+dirs under path (also collects dataless count)."""
    n_files = n_dirs = n_dataless = 0
    stack = [path]
    while stack:
        cur = stack.pop()
        try:
            with os.scandir(cur) as it:
                for entry in it:
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except OSError:
                        st = None
                    if entry.is_dir(follow_symlinks=False):
                        n_dirs += 1
                        stack.append(entry.path)
                    else:
                        n_files += 1
                        if st is not None and st.st_flags & 0x40000000:
                            n_dataless += 1
        except OSError:
            pass
    return n_files, n_dirs, n_dataless


def main():
    manifest = {
        "generatedAt": datetime.now().isoformat(timespec="seconds"),
        "roots": ROOTS,
        "directoryTargets": [],
        "fileTargets": [],
        "skippedKeepDirs": [],
        "scanNotes": "metadata-only; pruned at matched roots; exact-basename matching",
    }

    for root in ROOTS:
        if not os.path.isdir(root):
            continue
        # Top-level pass for file candidates in root itself
        with os.scandir(root) as it:
            for entry in it:
                if entry.is_dir(follow_symlinks=False):
                    continue
                cand, cat = classify_file(entry.name)
                if cand:
                    manifest["fileTargets"].append(
                        {"path": entry.path, "category": cat}
                    )

        # Walk with pruning at candidate/keep roots
        stack = [root]
        while stack:
            cur = stack.pop()
            try:
                entries = list(os.scandir(cur))
            except OSError:
                continue
            # Classify files in this dir once, at pop time
            for e in entries:
                if e.is_dir(follow_symlinks=False):
                    continue
                cand, cat = classify_file(e.name)
                if cand:
                    manifest["fileTargets"].append(
                        {"path": e.path, "category": cat}
                    )
            for entry in entries:
                name = entry.name
                if not entry.is_dir(follow_symlinks=False):
                    continue
                if name in KEEP_DIR_NAMES:
                    manifest["skippedKeepDirs"].append(entry.path)
                    continue  # kept, not descended for candidates
                if name in DIR_CANDIDATES:
                    nf, nd, ndl = count_tree(entry.path)
                    manifest["directoryTargets"].append(
                        {
                            "path": entry.path,
                            "category": DIR_CANDIDATES[name],
                            "files": nf,
                            "dirs": nd,
                            "datalessFiles": ndl,
                        }
                    )
                    continue  # pruned: never descend
                dir_cat = next((c for mk, c in DIR_PATTERN_CANDIDATES if mk in name), None)
                if dir_cat == "sync-conflict" and not os.path.isdir(
                    os.path.join(cur, name.split(".corrupted.")[0])
                ):
                    # Spec: conflict copies are removed only when the canonical
                    # counterpart exists in the same parent directory.
                    manifest.setdefault("conflictWithoutCanonical", []).append(entry.path)
                    continue  # kept: no canonical counterpart verified
                if dir_cat is not None:
                    nf, nd, ndl = count_tree(entry.path)
                    manifest["directoryTargets"].append(
                        {
                            "path": entry.path,
                            "category": dir_cat,
                            "files": nf,
                            "dirs": nd,
                            "datalessFiles": ndl,
                        }
                    )
                    continue  # pruned
                # Descend into ordinary directories
                stack.append(entry.path)

    # Dedup file targets (same entry may be seen twice: parent scan + push order)
    seen = set()
    uniq_files = []
    for ft in manifest["fileTargets"]:
        if ft["path"] not in seen:
            seen.add(ft["path"])
            uniq_files.append(ft)
    manifest["fileTargets"] = uniq_files

    # Summaries
    manifest["summary"] = {
        "directoryTargets": len(manifest["directoryTargets"]),
        "directoryTargetFiles": sum(d["files"] for d in manifest["directoryTargets"]),
        "directoryTargetDirs": sum(d["dirs"] for d in manifest["directoryTargets"]),
        "fileTargets": len(manifest["fileTargets"]),
    }

    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/cleanup-manifest.json"
    with open(out, "w") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest["summary"], indent=2))
    print(f"manifest written to {out}")


if __name__ == "__main__":
    main()
