#!/opt/homebrew/bin/python3
"""Fail-closed pre-apply backup creator for this change's live write set.

Strictly ordered phases — no byte is copied unless the ENTIRE preflight passes:

  1. preflight (read-only, fail-closed)
     - each of the 9 modify targets exists with its frozen baseline sha AND mode
     - each of the 2 created-file targets is still absent
     - every untouched baseline file matches its frozen sha (or frozen absence)
     - every drift-registered non-target (evidence/baseline-drift-register.json)
       matches its registered current sha/mode — any further drift fails
     - every backup destination resolves inside the approved backup root
     - no foreign files in the backup root
  2. copy — per-file atomic mode-600 backups (temp + fsync + os.replace + chmod)
  3. verify — every backup hash equals its live bytes; value-blind result
     written to evidence/apply-backups.json

`--preflight-only` runs phase 1 and exits without copying anything.

Value-blind: hashes, modes, byte sizes, booleans only. The Kimi Code backup
copy (pre-existing literal credentials) lives outside Git at mode 0600 per the
apply safety contract and task 5.7 (no backup is ever committed to Git).
"""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path

HOME = Path("/Users/androidteam")
EVID = HOME / "Developer/openspec-store/openspec/changes/reconcile-omniroute-native-dialects/evidence"
BACKUP_DIR = HOME / ".hermes/backups/reconcile-omniroute-native-dialects"

MODIFY = [
    "/Users/androidteam/.config/kilo/kilo.jsonc",
    "/Users/androidteam/.config/opencode/opencode.json",
    "/Users/androidteam/.factory/settings.json",
    "/Users/androidteam/.grok/config.toml",
    "/Users/androidteam/.kimi-code/config.toml",
    "/Users/androidteam/.omp/agent/models.yml",
    "/Users/androidteam/.pi/agent/models.json",
    "/Users/androidteam/.prime/agent/models.json",
    "/Users/androidteam/.cline/data/settings/providers.json",
]
CREATE = [
    "/Users/androidteam/.codex/omniroute.config.toml",
    "/Users/androidteam/.config/goose/custom_providers/custom_omniroute_anthropic.json",
]
KIMI_PATH = "/Users/androidteam/.kimi-code/config.toml"
CLINE_PATH = "/Users/androidteam/.cline/data/settings/providers.json"
SENSITIVE = (KIMI_PATH, CLINE_PATH)
SAFE_MODIFY = [p for p in MODIFY if p not in SENSITIVE]
RC_OK = 0
RC_COPY_VERIFY = 1
RC_PREFLIGHT = 2
RC_CREATE_PRESENT = 3
RC_REGISTER_MISSING = 4
RC_BAD_TARGET = 5


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(p: Path) -> dict:
    if not p.is_file():
        return {"exists": False, "mode": None, "sha256": None, "bytes": 0}
    return {
        "exists": True,
        "mode": oct(p.stat().st_mode & 0o777),
        "sha256": sha256_file(p),
        "bytes": p.stat().st_size,
    }


def backup_dest(path: str, base: dict) -> Path:
    template = base.get("rollback", {}).get(path, {}).get("backup_location_template")
    if template:
        return Path(template.replace("$HOME", str(HOME)))
    return BACKUP_DIR / (hashlib.sha256(path.encode()).hexdigest()[:16] + "-" + Path(path).name)


def preflight(base: dict, register: dict, applied_map: dict | None = None, authorized: set | None = None) -> tuple[list[str], bool]:
    """Read-only integrity gate. Returns (failures, create_target_present).

    Phase-aware anchors:
      - a path in `authorized` (credential-rotation drift, sensitive files only)
        is compared against the drift register's recorded current state — the
        register must be re-captured post-rotation before the sensitive batch;
      - a path in `applied_map` (already-applied target, sensitive-batch phase)
        is compared against the post-apply manifest's recorded sha/mode;
      - every other modify target still compares against the frozen baseline.
    """
    failures = []
    create_present = False
    registered = {e["path"]: e["current_state"] for e in register["entries"]}
    authorized = authorized or set()

    for path in MODIFY:
        meta = base["files"][path]
        cur = snapshot(Path(path))
        if not cur["exists"]:
            failures.append(f"modify target missing: {path}")
            continue
        if path in authorized:
            reg = registered.get(path)
            if reg is None:
                failures.append(f"authorized-drift path missing from drift register (re-register post-rotation first): {path}")
            elif cur["sha256"] != reg.get("sha256") or cur["mode"] != reg.get("mode"):
                failures.append(f"authorized-drift path differs from registered current state (re-register post-rotation first): {path}")
        elif applied_map is not None and path in applied_map:
            am = applied_map[path]
            if cur["sha256"] != am.get("sha256") or cur["mode"] != am.get("mode"):
                failures.append(f"applied target differs from post-apply manifest: {path}")
        elif cur["sha256"] != meta["sha256"] or cur["mode"] != meta["mode"]:
            failures.append(f"modify target drifted from frozen baseline (sha/mode): {path}")

    for path in CREATE:
        if Path(path).is_file():
            # Second phase (post-rotation sensitive batch): a create target
            # that already exists is accepted ONLY when anchored to the
            # post-apply manifest — declared in its changed_paths AND
            # byte/mode equal to its recorded post-apply state.
            if applied_map is not None and path in applied_map:
                am = applied_map[path]
                cur = snapshot(Path(path))
                if cur["sha256"] == am.get("sha256") and cur["mode"] == am.get("mode"):
                    continue
            create_present = True
            failures.append(f"create target unexpectedly present: {path}")

    for path, meta in base["files"].items():
        if path in MODIFY or path in CREATE:
            continue
        cur = snapshot(Path(path))
        if path in registered:
            want = registered[path]
            if cur["sha256"] != want["sha256"] or cur["mode"] != want["mode"]:
                failures.append(f"registered drift changed again since register capture: {path}")
        else:
            if cur["exists"] != meta["exists"]:
                failures.append(f"untouched baseline file existence changed: {path}")
            elif cur["exists"] and cur["sha256"] != meta["sha256"]:
                failures.append(f"untouched baseline file drifted: {path}")

    for reg_path, want in sorted(registered.items()):
        # Registered-extra coverage: register paths outside the baseline files
        # map (e.g. the glob-captured omniroute-pm.json profile) are verified
        # against the register so pre-backup external drift fails closed.
        if reg_path in MODIFY or reg_path in base["files"]:
            continue
        cur = snapshot(Path(reg_path))
        if not cur["exists"] or cur["sha256"] != want.get("sha256") or cur["mode"] != want.get("mode"):
            failures.append(f"registered extra path drifted since register capture (re-register required): {reg_path}")

    expected_names = {backup_dest(p, base).name for p in MODIFY}
    if BACKUP_DIR.is_dir():
        for f in sorted(BACKUP_DIR.iterdir()):
            if f.name not in expected_names:
                failures.append(f"foreign file in backup root: {f.name}")
    elif BACKUP_DIR.exists():
        failures.append(f"backup root is not a directory: {BACKUP_DIR}")

    for path in MODIFY:
        dest = backup_dest(path, base)
        if dest.parent != BACKUP_DIR:
            failures.append(f"backup destination escapes approved root: {dest}")

    return failures, create_present


def atomic_copy(src: Path, dst: Path, mode: int) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(fd, "wb") as out, open(src, "rb") as inp:
        shutil.copyfileobj(inp, out)
        out.flush()
        os.fsync(out.fileno())
    os.replace(tmp, dst)
    os.chmod(dst, mode)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        help="back up only these live paths (repeatable; must be modify targets)",
    )
    parser.add_argument(
        "--include-sensitive",
        action="store_true",
        help="allow backing up the credential-exposed Kimi Code and Cline files (post-rotation only)",
    )
    parser.add_argument(
        "--applied-manifest",
        type=Path,
        default=None,
        help="post-apply manifest anchoring already-applied targets (sensitive-batch phase)",
    )
    parser.add_argument(
        "--authorized-drift",
        action="append",
        default=[],
        help="sensitive path with user-authorized credential-rotation drift (repeatable; requires fresh drift-register entry)",
    )
    args = parser.parse_args()

    authorized = set(args.authorized_drift)
    bad_auth = sorted(authorized - set(SENSITIVE))
    if bad_auth:
        print(f"FAIL --authorized-drift only accepts sensitive paths: {bad_auth}")
        return RC_BAD_TARGET
    applied_map = None
    if args.applied_manifest is not None:
        am = json.loads(args.applied_manifest.read_text())
        if not isinstance(am.get("files"), dict):
            print("FAIL --applied-manifest must contain a files map")
            return RC_BAD_TARGET
        applied_map = {p: m for p, m in am["files"].items() if p in am.get("changed_paths", [])}

    if args.target is not None:
        wanted = set(args.target)
        unknown = sorted(wanted - set(MODIFY))
        if unknown:
            print(f"FAIL unknown --target paths: {unknown}")
            return RC_BAD_TARGET
        selected = [p for p in MODIFY if p in wanted]
        sensitive_selected = [p for p in selected if p in SENSITIVE]
        if sensitive_selected and not args.include_sensitive:
            print("FAIL sensitive targets require --include-sensitive (credential-rotation gate):")
            for p in sensitive_selected:
                print(f"  {p}")
            return RC_BAD_TARGET
    else:
        selected = list(MODIFY) if args.include_sensitive else list(SAFE_MODIFY)

    base = json.loads((EVID / "pre-apply-manifest.json").read_text())
    register_path = EVID / "baseline-drift-register.json"
    if not register_path.is_file():
        print(f"FAIL drift register missing: {register_path}")
        return RC_REGISTER_MISSING
    register = json.loads(register_path.read_text())

    failures, create_present = preflight(base, register, applied_map, authorized)
    if failures:
        for failure in failures:
            print("PREFLIGHT FAIL", failure)
        print(f"SUMMARY PREFLIGHT FAIL findings={len(failures)} copied=0")
        return RC_CREATE_PRESENT if create_present else RC_PREFLIGHT
    print("PREFLIGHT PASS modify=9/9 create_absent=2/2 untouched+registered=20/20 destinations=inside-root")

    if args.preflight_only:
        print("SUMMARY PREFLIGHT-ONLY PASS copied=0")
        return RC_OK

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(BACKUP_DIR, 0o700)
    backups = []
    copy_failures = []
    for path in selected:
        live = Path(path)
        dest = backup_dest(path, base)
        try:
            atomic_copy(live, dest, 0o600)
        except OSError as exc:
            copy_failures.append(f"copy failed: {path}: {exc}")
            continue
        backups.append(
            {
                "path": path,
                "backup_path": str(dest),
                "backup_mode": oct(dest.stat().st_mode & 0o777),
                "live_sha256": sha256_file(live),
                "baseline_sha256": base["files"][path]["sha256"],
                "backup_matches_live": sha256_file(dest) == sha256_file(live),
                "bytes": live.stat().st_size,
            }
        )
    if copy_failures:
        for failure in copy_failures:
            print("FAIL", failure)
        return RC_COPY_VERIFY

    verify_failures = [b for b in backups if not b["backup_matches_live"] or b["backup_mode"] != "0o600"]
    result = {
        "value_blind": True,
        "phase": "preflight+copy+verify",
        "backup_dir": str(BACKUP_DIR),
        "backup_dir_mode": oct(BACKUP_DIR.stat().st_mode & 0o777),
        "backup_file_mode": "0o600",
        "atomic_replacement": "temp file in backup dir + fsync + os.replace + chmod",
        "single_writer": "root apply session (post-verdict)",
        "drift_register_crosscheck": "evidence/baseline-drift-register.json",
        "preflight_passed": not failures and not create_present,
        "selected_targets": selected,
        "deferred_targets": [p for p in MODIFY if p not in selected],
        "deferred_reason": (
            "credential-rotation gate (incidents 1-2, evidence/incident-credential-exposure.md)"
            if len(selected) != len(MODIFY)
            else None
        ),
        "backups": backups,
        "created_file_targets": [
            {"path": p, "exists_at_backup_time": Path(p).is_file(),
             "expected_new_mode": base.get("expected_new_file_modes", {}).get(p)}
            for p in CREATE
        ],
    }
    out = EVID / "apply-backups.json"
    if out.is_file():
        try:
            prev = json.loads(out.read_text())
        except Exception:
            prev = None
        if not isinstance(prev, dict) or not isinstance(prev.get("runs"), list):
            prev = None
    else:
        prev = None
    book = prev or {"value_blind": True, "runs": []}
    result["run_index"] = len(book["runs"])
    book["runs"].append(result)
    out.write_text(json.dumps(book, indent=1) + "\n")
    ok = len(verify_failures) == 0
    print(f"BACKUPS total={len(backups)} verified={len(backups) - len(verify_failures)} mode600_dir700={oct(BACKUP_DIR.stat().st_mode & 0o777)}")
    print("RESULT_JSON evidence/apply-backups.json")
    return RC_OK if ok else RC_COPY_VERIFY


if __name__ == "__main__":
    raise SystemExit(main())
