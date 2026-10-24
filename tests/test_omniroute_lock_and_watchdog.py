"""Behavioral regression tests for OmniRoute native lockf coordination,
periodic 6-hour physical SQLite integrity verification, and fail-closed
updater snapshot checkpointing.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STORE_WATCHDOG = REPO_ROOT / "scripts" / "omniroute-watchdog.sh"
DEV_WATCHDOG = Path("/Users/androidteam/Developer/scripts/omniroute-watchdog.sh")
UPDATE_SCRIPT = Path("/Users/androidteam/Omniroute/scripts/update.sh")
ENTRYPOINT_COMPAT = Path("/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh")
ENSURE_MUSE_COMPAT = Path("/Users/androidteam/Omniroute/scripts/ensure-muse-wire-compat.sh")


def _write_executable(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    path.chmod(0o755)


class TestOmniRouteLockAndWatchdog(unittest.TestCase):
    """End-to-end behavioral tests executing the real bash scripts in isolated HOME directories."""

    def setUp(self) -> None:
        self.tmp_dir = tempfile.mkdtemp(prefix="omniroute_lock_test_")
        self.home = Path(self.tmp_dir)
        self.local_bin = self.home / ".local" / "bin"
        self.local_bin.mkdir(parents=True, exist_ok=True)
        self.omni_state = self.home / ".omniroute"
        self.omni_state.mkdir(parents=True, exist_ok=True)
        self.compose_dir = self.home / "Omniroute"
        (self.compose_dir / "scripts").mkdir(parents=True, exist_ok=True)
        (self.compose_dir / "docker-compose.yml").write_text("services: {}\n", encoding="utf-8")
        (self.compose_dir / "docker-compose.override.yml").write_text("services: {}\n", encoding="utf-8")
        _write_executable(
            self.compose_dir / "scripts" / "ensure-muse-wire-compat.sh",
            "#!/bin/bash\nexit 0\n",
        )
        _write_executable(
            self.local_bin / "osascript",
            "#!/bin/bash\nexit 0\n",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _base_env(self) -> dict[str, str]:
        env = os.environ.copy()
        env["HOME"] = str(self.home)
        env["PATH"] = f"{self.local_bin}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
        return env

    def test_watchdog_provenance_mirror_and_syntax(self) -> None:
        """Developer and openspec-store omniroute-watchdog.sh must be byte-identical and valid bash."""
        dev_sha = hashlib.sha256(DEV_WATCHDOG.read_bytes()).hexdigest()
        store_sha = hashlib.sha256(STORE_WATCHDOG.read_bytes()).hexdigest()
        self.assertEqual(dev_sha, store_sha, "omniroute-watchdog.sh provenance mirror drifted")

        for script in (DEV_WATCHDOG, STORE_WATCHDOG, UPDATE_SCRIPT):
            res = subprocess.run(["/bin/bash", "-n", str(script)], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"bash -n failed for {script}: {res.stderr}")

    def test_watchdog_excluded_while_lock_held_and_ignores_old_metadata(self) -> None:
        """Watchdog skips cycle (exit 0) without calling docker while kernel lock is held, even if file contents look stale."""
        lock_file = self.omni_state / "update.lock"
        # Write old/stale-looking PID+epoch content and backdate mtime by 10 hours
        lock_file.write_text("99999 1000\n", encoding="utf-8")
        old_time = time.time() - 36000
        os.utime(lock_file, (old_time, old_time))

        docker_calls = self.home / "docker_calls.log"
        _write_executable(
            self.local_bin / "docker",
            f'#!/bin/bash\necho "$@" >> "{docker_calls}"\nexit 0\n',
        )

        holder = subprocess.Popen(
            [
                "/bin/bash",
                "-c",
                'exec 9>>"$1"; /usr/bin/lockf -s -t 0 9; echo READY; sleep 30',
                "_",
                str(lock_file),
            ],
            stdout=subprocess.PIPE,
            text=True,
        )
        try:
            ready_line = holder.stdout.readline().strip() if holder.stdout else ""
            self.assertEqual(ready_line, "READY")

            res = subprocess.run(
                ["/bin/bash", str(STORE_WATCHDOG)],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(res.returncode, 0)
            self.assertFalse(docker_calls.exists(), "Watchdog invoked docker while maintenance lock was held")
            self.assertTrue(lock_file.exists(), "Watchdog unlinked active update.lock")
            watchdog_log = (self.omni_state / "watchdog.log").read_text(encoding="utf-8")
            self.assertIn("Maintenance lock active", watchdog_log)
        finally:
            holder.terminate()
            holder.wait(timeout=5)

    def test_arbitrary_file_contents_do_not_block_after_owner_exits(self) -> None:
        """Persistent update.lock with arbitrary or ancient contents is acquired after previous holder exits."""
        lock_file = self.omni_state / "update.lock"
        lock_file.write_text("1 08 corrupt_metadata\n", encoding="utf-8")
        old_time = time.time() - 86400
        os.utime(lock_file, (old_time, old_time))

        # Keep integrity marker fresh so only Step 0-2 run
        marker = self.omni_state / "integrity-last-ok"
        marker.write_text("", encoding="utf-8")

        docker_calls = self.home / "docker_calls.log"
        _write_executable(
            self.local_bin / "docker",
            f"""#!/bin/bash
echo "$@" >> "{docker_calls}"
if [[ "$1" == "info" ]]; then exit 0; fi
if [[ "$1" == "inspect" ]]; then
  if [[ "$*" == *"State.Status"* ]]; then echo "running"; else echo "healthy"; fi
  exit 0
fi
exit 0
""",
        )
        _write_executable(self.local_bin / "curl", "#!/bin/bash\nexit 0\n")

        res = subprocess.run(
            ["/bin/bash", str(STORE_WATCHDOG)],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertTrue(docker_calls.exists(), "Watchdog did not proceed when lock was unheld")
        self.assertTrue(lock_file.exists(), "Persistent update.lock must not be unlinked")

    def test_non_contention_lock_open_error_fails_closed(self) -> None:
        """If update.lock cannot be opened as a file (e.g., is a directory), both watchdog and updater fail closed nonzero."""
        lock_dir = self.omni_state / "update.lock"
        lock_dir.mkdir(parents=True, exist_ok=True)

        w_res = subprocess.run(
            ["/bin/bash", str(STORE_WATCHDOG)],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(w_res.returncode, 0)

        flag_file = self.omni_state / "update-available"
        flag_file.write_text("sha256:1111111111111111111111111111111111111111111111111111111111111111\n", encoding="utf-8")
        u_res = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(u_res.returncode, 0)
        self.assertTrue(flag_file.exists(), "Update flag must be retained on lock open failure")

    def test_updater_no_flag_and_simultaneous_contention_and_cleanup_before_unlock(self) -> None:
        """Verify updater no-flag exit 0, simultaneous contention (only 1 enters pre-state), and temp snapshot cleanup before lock release."""
        # 1. No-flag branch exits 0 without creating update.lock
        res_no_flag = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(res_no_flag.returncode, 0)
        self.assertFalse((self.omni_state / "update.lock").exists())

        # 2. Simultaneous acquisition + cleanup ordering before lock release
        flag_file = self.omni_state / "update-available"
        flag_file.write_text("sha256:2222222222222222222222222222222222222222222222222222222222222222\n", encoding="utf-8")

        entered_preflight = self.home / "entered_preflight"
        release_holder = self.home / "release_holder"
        cleanup_lock_state = self.home / "cleanup_lock_state.txt"
        prestate_entries = self.home / "prestate_entries.log"

        _write_executable(
            self.local_bin / "docker",
            f"""#!/bin/bash
if [[ "$1" == "info" ]]; then
  echo "$$" >> "{prestate_entries}"
  touch "{entered_preflight}"
  while [[ ! -f "{release_holder}" ]]; do sleep 0.05; done
  exit 1
fi
if [[ "$1" == "exec" && "$*" == *"rm -f /tmp/pre-update-"* ]]; then
  # Verify kernel lock is STILL held while cleanup_update removes temp snapshot
  if /usr/bin/lockf -s -t 0 "{self.omni_state / 'update.lock'}" /usr/bin/true 2>/dev/null; then
    echo "UNLOCKED_DURING_CLEANUP" > "{cleanup_lock_state}"
  else
    echo "LOCKED_DURING_CLEANUP" > "{cleanup_lock_state}"
  fi
  exit 0
fi
exit 0
""",
        )
        _write_executable(self.local_bin / "sqlite3", "#!/bin/bash\nexit 0\n")
        _write_executable(self.local_bin / "curl", "#!/bin/bash\nexit 0\n")

        first = subprocess.Popen(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            deadline = time.time() + 10
            while not entered_preflight.exists() and time.time() < deadline:
                time.sleep(0.05)
            self.assertTrue(entered_preflight.exists(), "First updater did not reach preflight")

            # Contending second updater must fail closed with exit 1 and retain flag
            second = subprocess.run(
                ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(second.returncode, 1)
            self.assertIn("lockf exit 75", second.stdout)
            self.assertTrue(flag_file.exists())

            # Release first updater (which fails at docker info -> exit 1)
            release_holder.write_text("go\n", encoding="utf-8")
            first.communicate(timeout=10)
            self.assertEqual(first.returncode, 1)
        finally:
            if first.poll() is None:
                first.kill()
                first.wait(timeout=5)

        # Exactly one process entered preflight
        entries = prestate_entries.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(entries), 1)
        # Temp snapshot cleanup ran BEFORE lock was released
        self.assertEqual(cleanup_lock_state.read_text(encoding="utf-8").strip(), "LOCKED_DURING_CLEANUP")
        # After first exited, lock is immediately acquirable and persistent file mode is 0600
        lock_path = self.omni_state / "update.lock"
        self.assertTrue(lock_path.exists())
        self.assertEqual(stat.S_IMODE(lock_path.stat().st_mode), 0o600)
        probe = subprocess.run(
            ["/usr/bin/lockf", "-k", "-s", "-t", "0", str(lock_path), "/usr/bin/true"],
            capture_output=True,
        )
        self.assertEqual(probe.returncode, 0, "Lock remained held after updater exited")

    def test_updater_gate1_checkpoint_fail_closed_preserves_sidecars(self) -> None:
        """Gate 1 must fail closed and retain host -wal/-shm sidecars when PRAGMA wal_checkpoint(TRUNCATE) fails."""
        flag_file = self.omni_state / "update-available"
        flag_file.write_text("sha256:3333333333333333333333333333333333333333333333333333333333333333\n", encoding="utf-8")

        _write_executable(
            self.local_bin / "docker",
            """#!/bin/bash
if [[ "$1" == "info" || "$1" == "compose" ]]; then exit 0; fi
if [[ "$1" == "inspect" ]]; then echo "sha256:oldimage"; exit 0; fi
if [[ "$1" == "image" ]]; then echo "diegosouzapw/omniroute@sha256:0000"; exit 0; fi
if [[ "$1" == "exec" ]]; then
  if [[ "$*" == *"package.json"* ]]; then printf "3.8.51"; exit 0; fi
  if [[ "$*" == *"SELECT COUNT"* ]]; then printf "5"; exit 0; fi
  if [[ "$*" == *"quick_check"* ]]; then printf "ok"; exit 0; fi
  exit 0
fi
if [[ "$1" == "cp" ]]; then
  dest="$3"
  printf "SQLite dummy snapshot" > "$dest"
  printf "uncheckpointed wal frames" > "${dest}-wal"
  printf "shm state" > "${dest}-shm"
  exit 0
fi
exit 0
""",
        )
        _write_executable(
            self.local_bin / "sqlite3",
            """#!/bin/bash
sql="${!#}"
if [[ "$sql" == *"quick_check"* ]]; then
  echo "ok"
  exit 0
fi
if [[ "$sql" == *"wal_checkpoint"* ]]; then
  echo "1|4|0"
  exit 0
fi
exit 0
""",
        )
        _write_executable(self.local_bin / "curl", "#!/bin/bash\nexit 0\n")

        res = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(res.returncode, 1)
        self.assertIn("wal_checkpoint(TRUNCATE) failed", res.stdout)
        self.assertTrue(flag_file.exists())

        snapshots = list((self.omni_state / "snapshots").glob("pre-update-*.sqlite"))
        self.assertEqual(len(snapshots), 1)
        snap = snapshots[0]
        self.assertTrue(Path(f"{snap}-wal").exists(), "Host -wal sidecar was deleted despite checkpoint failure")
        self.assertTrue(Path(f"{snap}-shm").exists(), "Host -shm sidecar was deleted despite checkpoint failure")


    def test_updater_digest_mismatch_and_post_deploy_data_gates_retain_flag(self) -> None:
        """Gate 3 digest mismatch stops before recreate; Gate 9 baseline regression retains flag."""
        flag_file = self.omni_state / "update-available"
        flag_file.write_text("sha256:4444444444444444444444444444444444444444444444444444444444444444\n", encoding="utf-8")
        up_calls = self.home / "compose_up_calls.log"
        mode_file = self.home / "updater_mode.txt"
        mode_file.write_text("digest_mismatch\n", encoding="utf-8")

        _write_executable(
            self.local_bin / "docker",
            f"""#!/bin/bash
mode=$(cat "{mode_file}")
if [[ "$1" == "info" ]]; then exit 0; fi
if [[ "$1" == "compose" ]]; then
  if [[ "$*" == *" pull "* ]]; then touch "{self.home / 'pulled'}"; fi
  if [[ "$*" == *" up "* ]]; then echo "$@" >> "{up_calls}"; fi
  exit 0
fi
if [[ "$1" == "inspect" ]]; then
  if [[ "$*" == *"Health.Status"* ]]; then echo "healthy"; exit 0; fi
  if [[ -f "{self.home / 'pulled'}" && -f "{up_calls}" ]]; then
    echo "sha256:newimage"
  else
    echo "sha256:oldimage"
  fi
  exit 0
fi
if [[ "$1" == "image" ]]; then
  if [[ "$*" == *"RepoDigests"* ]]; then
    if [[ ! -f "{self.home / 'pulled'}" ]]; then
      echo "diegosouzapw/omniroute@sha256:0000000000000000000000000000000000000000000000000000000000000000"
    elif [[ "$mode" == "digest_mismatch" ]]; then
      echo "diegosouzapw/omniroute@sha256:9999999999999999999999999999999999999999999999999999999999999999"
    else
      echo "diegosouzapw/omniroute@sha256:4444444444444444444444444444444444444444444444444444444444444444"
    fi
  else
    echo "sha256:newimage"
  fi
  exit 0
fi
if [[ "$1" == "tag" ]]; then exit 0; fi
if [[ "$1" == "cp" ]]; then
  printf "SQLite snapshot" > "$3"
  exit 0
fi
if [[ "$1" == "exec" ]]; then
  if [[ "$*" == *"package.json"* ]]; then
    if [[ -f "{up_calls}" ]]; then printf "3.8.52"; else printf "3.8.51"; fi
    exit 0
  fi
  if [[ "$*" == *"quick_check"* ]]; then printf "ok"; exit 0; fi
  if [[ "$*" == *"FROM api_keys"* ]]; then printf "1"; exit 0; fi
  if [[ "$*" == *"FROM provider_connections"* ]]; then
    if [[ ! -f "{self.home / 'seen_baseline'}" ]]; then
      touch "{self.home / 'seen_baseline'}"
      printf "32"
    else
      printf "31"
    fi
    exit 0
  fi
  exit 0
fi
exit 0
""",
        )
        _write_executable(
            self.local_bin / "sqlite3",
            """#!/bin/bash
sql="${!#}"
if [[ "$sql" == *"quick_check"* ]]; then echo "ok"; exit 0; fi
if [[ "$sql" == *"wal_checkpoint"* ]]; then echo "0|0|0"; exit 0; fi
if [[ "$sql" == *"journal_mode"* ]]; then echo "delete"; exit 0; fi
""",
        )
        _write_executable(
            self.local_bin / "curl",
            """#!/bin/bash
if [[ "$*" == *"/healthz"* ]]; then printf "ok"; exit 0; fi
if [[ "$*" == *"/api/monitoring/health"* ]]; then printf '{"status":"healthy","setupComplete":true}'; exit 0; fi
if [[ "$*" == *"muse-code/models"* && "$*" != *"-w"* ]]; then printf '{"object":"list","data":[{"id":"muse-spark-1.3"}]}'; exit 0; fi
printf "200"
exit 0
""",
        )

        mismatch = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(mismatch.returncode, 1)
        self.assertIn("GATE FAILED [digest-match]", mismatch.stdout)
        self.assertFalse(up_calls.exists(), "Digest mismatch must stop before container deployment")
        self.assertTrue(flag_file.exists())

        (self.home / "seen_baseline").unlink(missing_ok=True)
        (self.home / "pulled").unlink(missing_ok=True)
        mode_file.write_text("post_deploy_regression\n", encoding="utf-8")
        regressed = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(regressed.returncode, 1)
        self.assertIn("GATE FAILED [post-deploy-data]", regressed.stdout)
        self.assertTrue(up_calls.exists())
        self.assertTrue(flag_file.exists())
    def test_watchdog_periodic_6h_integrity_check_pass_skip_and_fail(self) -> None:
        """Watchdog runs bounded 6h physical integrity_check when due, skips when fresh, and exits nonzero without restarting on failure."""
        marker = self.omni_state / "integrity-last-ok"
        integrity_mode_file = self.home / "integrity_mode.txt"
        restart_calls = self.home / "restart_calls.log"
        integrity_calls = self.home / "integrity_calls.log"

        bm_dir = self.home / "node_modules" / "better-sqlite3"
        bm_dir.mkdir(parents=True, exist_ok=True)
        (bm_dir / "index.js").write_text(
            """const fs = require("fs");
module.exports = function Database(dbPath, opts) {
  if (dbPath !== "/app/data/storage.sqlite" || !opts || opts.readonly !== true || opts.fileMustExist !== true || opts.timeout !== 15000) {
    throw new Error("Invalid Database args");
  }
  return {
    pragma(name) {
      if (name !== "integrity_check") throw new Error("Unexpected pragma: " + name);
      const mode = fs.readFileSync(process.env.MOCK_INTEGRITY_MODE_FILE, "utf8").trim();
      if (mode === "ok") return [{ integrity_check: "ok" }];
      return [{ integrity_check: "ok" }, { integrity_check: "row 7 missing from index" }];
    },
    close() {}
  };
};
""",
            encoding="utf-8",
        )

        _write_executable(
            self.local_bin / "docker",
            f"""#!/bin/bash
if [[ "$1" == "info" ]]; then exit 0; fi
if [[ "$1" == "inspect" ]]; then
  if [[ "$*" == *"State.Status"* ]]; then echo "running"; else echo "healthy"; fi
  exit 0
fi
if [[ "$1" == "compose" ]]; then
  echo "$@" >> "{restart_calls}"
  exit 0
fi
if [[ "$1" == "exec" && "$2" == "omniroute" && "$3" == "node" && "$4" == "-e" ]]; then
  echo "called" >> "{integrity_calls}"
  NODE_PATH="{self.home / 'node_modules'}" MOCK_INTEGRITY_MODE_FILE="{integrity_mode_file}" node -e "$5"
  exit $?
fi
exit 0
""",
        )
        _write_executable(self.local_bin / "curl", "#!/bin/bash\nexit 0\n")

        # 1. Missing marker -> runs check, succeeds, creates marker, exits 0
        integrity_mode_file.write_text("ok", encoding="utf-8")
        res1 = subprocess.run(
            ["/bin/bash", str(STORE_WATCHDOG)],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(res1.returncode, 0)
        self.assertTrue(marker.exists(), "integrity-last-ok marker was not created on pass")
        self.assertEqual(len(integrity_calls.read_text(encoding="utf-8").splitlines()), 1)

        # 2. Fresh marker (< 6h) -> skips physical integrity check
        res2 = subprocess.run(
            ["/bin/bash", str(STORE_WATCHDOG)],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(res2.returncode, 0)
        self.assertEqual(len(integrity_calls.read_text(encoding="utf-8").splitlines()), 1)

        # 3. Stale marker (> 6h) + failing integrity check -> exits nonzero, does NOT update marker mtime, does NOT restart gateway
        stale_mtime = int(time.time()) - 25000
        os.utime(marker, (stale_mtime, stale_mtime))
        integrity_mode_file.write_text("fail", encoding="utf-8")

        res3 = subprocess.run(
            ["/bin/bash", str(STORE_WATCHDOG)],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertNotEqual(res3.returncode, 0, "Watchdog must exit nonzero when physical integrity_check fails")
        self.assertEqual(len(integrity_calls.read_text(encoding="utf-8").splitlines()), 2)
        self.assertEqual(int(marker.stat().st_mtime), stale_mtime, "Failed integrity check must not update marker mtime")
        self.assertFalse(restart_calls.exists(), "Failed integrity check must not restart a healthy gateway")


    def test_v3852_muse_wire_compat_and_updater_muse_catalog_and_backup_cleanup(self) -> None:
        """v3.8.52 patches MUSE_CODE_REWRITE_V3 without touching chunks; Gate 8 fails closed on empty catalog (401 & 200); Gate 9 prunes pre-migration backups."""
        # a. Verify container-entrypoint-compat.sh and ensure-muse-wire-compat.sh patching against temp files
        peer_file = self.home / "peer-stamp.mjs"
        chunks_dir = self.home / "chunks"
        chunks_dir.mkdir(parents=True, exist_ok=True)
        chunk_file = chunks_dir / "8537.js"
        original_chunk = (
            'const frame = {type:"response.in_progress",sequence_number:0,response:{id:"resp_keepalive_omniroute",status:"in_progress"}};\n'
        )

        peer_file.write_text(
            "export function wrapRequestListenerWithPeerStamp(listener) {\n"
            "  return function peerStampingRequestHandler(req, res) {\n"
            "    stampPeerIp(req);\n"
            "    return listener.call(this, req, res);\n"
            "  };\n"
            "}\n",
            encoding="utf-8",
        )
        chunk_file.write_text(original_chunk, encoding="utf-8")

        patch_env = self._base_env()
        patch_env["OMNIROUTE_PEER_STAMP_PATH"] = str(peer_file)
        patch_env["OMNIROUTE_CHUNKS_DIR"] = str(chunks_dir)
        ep_res = subprocess.run(
            ["/bin/sh", str(ENTRYPOINT_COMPAT), "--patch-only"],
            env=patch_env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(ep_res.returncode, 0, ep_res.stderr)
        self.assertEqual(ep_res.stdout, "patched")
        patched_peer = peer_file.read_text(encoding="utf-8")
        patched_chunk = chunk_file.read_text(encoding="utf-8")
        self.assertIn("/* MUSE_CODE_REWRITE_V3 */", patched_peer)
        self.assertIn('req.url = "/v1" + req.url;', patched_peer)
        self.assertNotIn("MUSE_CODE_COMPAT_V2", patched_peer)
        self.assertNotIn("MUSE_CATALOG_DATA", patched_peer)
        self.assertEqual(patched_chunk, original_chunk, "chunk_file must remain completely untouched")

        # Verify container-entrypoint-compat.sh upgrades a MUSE_CODE_COMPAT_V2-patched peer-stamp.mjs to V3
        peer_file.write_text(
            "export function wrapRequestListenerWithPeerStamp(listener) {\n"
            "  return function peerStampingRequestHandler(req, res) {\n"
            "    /* MUSE_CODE_COMPAT_V2 */\n"
            '    const MUSE_CATALOG_DATA = [["muse-spark-1.3"]];\n'
            "    stampPeerIp(req);\n"
            "    return listener.call(this, req, res);\n"
            "  };\n"
            "}\n",
            encoding="utf-8",
        )
        ep_v2_res = subprocess.run(
            ["/bin/sh", str(ENTRYPOINT_COMPAT), "--patch-only"],
            env=patch_env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(ep_v2_res.returncode, 0, ep_v2_res.stderr)
        self.assertEqual(ep_v2_res.stdout, "patched")
        upgraded_from_v2 = peer_file.read_text(encoding="utf-8")
        self.assertIn("/* MUSE_CODE_REWRITE_V3 */", upgraded_from_v2)
        self.assertNotIn("MUSE_CODE_COMPAT_V2", upgraded_from_v2)
        self.assertNotIn("MUSE_CATALOG_DATA", upgraded_from_v2)
        self.assertEqual(chunk_file.read_text(encoding="utf-8"), original_chunk)

        # Verify container-entrypoint-compat.sh normalizes Gemini-4 trailing model turn and agy exact lockout chunks idempotently
        gemini_chunk = chunks_dir / "7449.js"
        lock_chunk = chunks_dir / "32946.js"
        gemini_chunk.write_text(
            "return!/(?:^|-)image(?:-|$)/.test(b)&&/^gemini-(?:3(?:\\.\\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/.test(b)}\n",
            encoding="utf-8",
        )
        lock_chunk.write_text(
            "const d=[/\\bmodel.*not.*(?:available|found|supported|accessible)\\b/i];"
            "function e(a){let b=String(a||\"\");return!!b&&(!!d.some(a=>a.test(b))||/\\bmodel\\b[\\s\\S]{0,80}?\\b(?:not\\s+supported|unsupported|unknown|unavailable)\\b/i.test(b))}"
            "function au(a,b,c,d,e,f){return!(!at(a,c,f)||!c||aE(a))&&((\"antigravity\"===ag(a)?bz:ap)(a,b,c,d,e),!0)}\n",
            encoding="utf-8",
        )
        ep_chunk_res1 = subprocess.run(
            ["/bin/sh", str(ENTRYPOINT_COMPAT), "--patch-only"],
            env=patch_env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(ep_chunk_res1.returncode, 0, ep_chunk_res1.stderr)
        self.assertEqual(ep_chunk_res1.stdout, "patched")
        self.assertIn("/^gemini-(?:[34](?:\\.\\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/", gemini_chunk.read_text(encoding="utf-8"))
        patched_lock_src = lock_chunk.read_text(encoding="utf-8")
        self.assertIn("/\\bmodel(?!\\s+turn\\b).*not.*(?:available|found|supported|accessible)\\b/i", patched_lock_src)
        self.assertIn("/\\bmodel(?!\\s+turn\\b)\\b[\\s\\S]{0,80}?\\b(?:not\\s+supported|unsupported|unknown|unavailable)\\b/i", patched_lock_src)
        self.assertIn("(\"antigravity\"===ag(a)||\"agy\"===ag(a)?bz:ap)(a,b,c,d,e)", patched_lock_src)
        ep_chunk_res2 = subprocess.run(
            ["/bin/sh", str(ENTRYPOINT_COMPAT), "--patch-only"],
            env=patch_env,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(ep_chunk_res2.returncode, 0, ep_chunk_res2.stderr)
        self.assertEqual(ep_chunk_res2.stdout, "already_ok")
        gemini_chunk.unlink()
        lock_chunk.unlink()

        # Also verify ensure-muse-wire-compat.sh upgrades v1 peer-stamp.mjs to V3, leaves chunk untouched, and is idempotent on second run
        peer_file.write_text(
            "export function wrapRequestListenerWithPeerStamp(listener) {\n"
            "  return function peerStampingRequestHandler(req, res) {\n"
            '    if (req.url && (req.url === "/muse-code" || req.url.startsWith("/muse-code/") || req.url.startsWith("/muse-code?"))) { req.url = "/v1" + req.url; }\n'
            "    stampPeerIp(req);\n"
            "    return listener.call(this, req, res);\n"
            "  };\n"
            "}\n",
            encoding="utf-8",
        )
        chunk_file.write_text(original_chunk, encoding="utf-8")
        _write_executable(
            self.local_bin / "docker",
            f"""#!/bin/bash
if [[ "$1" == "ps" ]]; then echo "omniroute"; exit 0; fi
if [[ "$1" == "restart" ]]; then exit 0; fi
if [[ "$1" == "exec" && "$2" == "omniroute" && "$3" == "test" ]]; then exit 0; fi
if [[ "$1" == "exec" && "$2" == "omniroute" && "$3" == "/app/container-entrypoint-compat.sh" && "$4" == "--patch-only" ]]; then
  if [[ -f "{self.home / 'fail_compat'}" ]]; then exit 1; fi
  OMNIROUTE_PEER_STAMP_PATH="{peer_file}" OMNIROUTE_CHUNKS_DIR="{chunks_dir}" /bin/sh "{ENTRYPOINT_COMPAT}" --patch-only
  exit $?
fi
exit 0
""",
        )
        em1 = subprocess.run(
            ["/bin/bash", str(ENSURE_MUSE_COMPAT), "omniroute"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(em1.returncode, 0, em1.stderr)
        self.assertIn("Applied Muse Code wire-compat normalization", em1.stdout)
        self.assertIn("/* MUSE_CODE_REWRITE_V3 */", peer_file.read_text(encoding="utf-8"))
        self.assertEqual(chunk_file.read_text(encoding="utf-8"), original_chunk)
        em2 = subprocess.run(
            ["/bin/bash", str(ENSURE_MUSE_COMPAT), "omniroute"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(em2.returncode, 0, em2.stderr)
        self.assertIn("already_ok", em2.stdout)

        # Verify ensure-muse-wire-compat.sh fails closed (exit 1) when container patch fails
        (self.home / "fail_compat").write_text("1\n", encoding="utf-8")
        em_fail = subprocess.run(
            ["/bin/bash", str(ENSURE_MUSE_COMPAT), "omniroute"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(em_fail.returncode, 1, "ensure-muse-wire-compat.sh must fail closed on error")
        (self.home / "fail_compat").unlink(missing_ok=True)
        # b & c. Verify update.sh Gate 8 empty catalog fail-closed (both 401 and 200 postures) and Gate 9 pre-migration backup cleanup
        flag_file = self.omni_state / "update-available"
        flag_file.write_text(
            "sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c\n",
            encoding="utf-8",
        )
        catalog_mode = self.home / "catalog_mode.txt"
        catalog_mode.write_text("empty\n", encoding="utf-8")
        vm_posture = self.home / "vm_posture.txt"
        vm_posture.write_text("401\n", encoding="utf-8")
        backup_cleanup_log = self.home / "backup_cleanup.log"

        _write_executable(
            self.local_bin / "docker",
            f"""#!/bin/bash
if [[ "$1" == "info" ]]; then exit 0; fi
if [[ "$1" == "compose" ]]; then
  if [[ "$*" == *" pull "* ]]; then touch "{self.home / 'pulled'}"; fi
  if [[ "$*" == *" up "* ]]; then touch "{self.home / 'deployed'}"; fi
  exit 0
fi
if [[ "$1" == "inspect" ]]; then
  if [[ "$*" == *"Health.Status"* ]]; then echo "healthy"; exit 0; fi
  if [[ -f "{self.home / 'deployed'}" ]]; then echo "sha256:newimage"; else echo "sha256:oldimage"; fi
  exit 0
fi
if [[ "$1" == "image" ]]; then
  if [[ "$*" == *"RepoDigests"* ]]; then
    if [[ -f "{self.home / 'pulled'}" ]]; then
      echo "diegosouzapw/omniroute@sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c"
    else
      echo "diegosouzapw/omniroute@sha256:8bd462c9f60d8eda79329cfbb6ea7ea723505fe7721beb944f3d43835409e218"
    fi
  else
    echo "sha256:newimage"
  fi
  exit 0
fi
if [[ "$1" == "tag" ]]; then exit 0; fi
if [[ "$1" == "cp" ]]; then printf "SQLite snapshot" > "$3"; exit 0; fi
if [[ "$1" == "exec" ]]; then
  if [[ "$*" == *"package.json"* ]]; then
    if [[ -f "{self.home / 'deployed'}" ]]; then printf "3.8.52"; else printf "3.8.51"; fi
    exit 0
  fi
  if [[ "$*" == *"quick_check"* ]]; then printf "ok"; exit 0; fi
  if [[ "$*" == *"omniroute-field-encryption-v1"* ]]; then
    MOCK_CATALOG_MODE_FILE="{catalog_mode}" node -e '
      const fs = require("fs");
      const crypto = require("crypto");
      const secret = "unit-test-storage-secret";
      process.env.STORAGE_ENCRYPTION_KEY = secret;
      const key = crypto.scryptSync(secret, "omniroute-field-encryption-v1", 32);
      const iv = Buffer.alloc(12, 7);
      const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
      const ct = cipher.update("sk-valid-v3852-key", "utf8", "hex") + cipher.final("hex");
      const tag = cipher.getAuthTag().toString("hex");
      const validEnc = "enc:v1:" + iv.toString("hex") + ":" + ct + ":" + tag;
      const corruptedEnc = "enc:v1:" + iv.toString("hex") + ":" + ct + ":00000000000000000000000000000000";
      const rows = [
        {{ key: corruptedEnc, expires_at: null }},
        {{ key: validEnc, expires_at: null }}
      ];
      const Module = require("module");
      const origLoad = Module._load;
      Module._load = function(req, parent, isMain) {{
        if (req === "better-sqlite3") {{
          return function FakeDb() {{
            return {{
              prepare: () => ({{ all: () => rows }}),
              close: () => {{}}
            }};
          }};
        }}
        return origLoad(req, parent, isMain);
      }};
      global.fetch = async (url, opts) => {{
        if (opts && opts.headers && opts.headers.Authorization === "Bearer sk-valid-v3852-key") {{
          if (String(url).includes("muse-code/models")) {{
            const mode = fs.readFileSync(process.env.MOCK_CATALOG_MODE_FILE, "utf8").trim();
            if (mode === "empty") return {{ status: 200, text: async () => "{{\\"object\\":\\"list\\",\\"data\\":[]}}" }};
            if (mode === "malformed") return {{ status: 200, text: async () => "{{\\"object\\":\\"list\\",\\"data\\":[{{\\"id\\":\\"muse-spark-1.3\\"}}" }};
            if (mode === "wrong_shape") return {{ status: 200, text: async () => "{{\\"object\\":\\"list\\",\\"data\\":[],\\"id\\":\\"muse-spark-1.3\\"}}" }};
            return {{ status: 200, text: async () => "{{\\"object\\":\\"list\\",\\"data\\":[{{\\"id\\":\\"muse-spark-1.3\\"}}]}}" }};
          }}
          return {{ status: 200, text: async () => JSON.stringify({{ data: [{{ id: "gemini-4-argon" }}] }}) }};
        }}
        return {{ status: 401, text: async () => "{{}}" }};
      }};
    '"$5"
    exit $?
  fi
  if [[ "$*" == *"FROM api_keys"* ]]; then printf "1"; exit 0; fi
  if [[ "$*" == *"FROM provider_connections"* ]]; then printf "32"; exit 0; fi
  if [[ "$*" == *"db_state-"*"_pre-migration.sqlite"* ]]; then
    echo "$@" >> "{backup_cleanup_log}"
    exit 0
  fi
  exit 0
fi
exit 0
""",
        )
        _write_executable(
            self.local_bin / "sqlite3",
            """#!/bin/bash
sql="${!#}"
if [[ "$sql" == *"quick_check"* ]]; then echo "ok"; exit 0; fi
if [[ "$sql" == *"wal_checkpoint"* ]]; then echo "0|0|0"; exit 0; fi
if [[ "$sql" == *"journal_mode"* ]]; then echo "delete"; exit 0; fi
exit 0
""",
        )
        _write_executable(
            self.local_bin / "curl",
            f"""#!/bin/bash
mode=$(cat "{catalog_mode}")
posture=$(cat "{vm_posture}")
if [[ "$*" == *"/healthz"* ]]; then printf "ok"; exit 0; fi
if [[ "$*" == *"/api/monitoring/health"* ]]; then printf '{{"status":"healthy","setupComplete":true}}'; exit 0; fi
if [[ "$*" == *"/v1/models"* && "$*" != *"-I"* ]]; then printf "%s" "$posture"; exit 0; fi
if [[ "$*" == *"muse-code/models"* && "$*" == *"-w"* ]]; then printf "%s" "$posture"; exit 0; fi
if [[ "$*" == *"muse-code/models"* && "$*" != *"-w"* ]]; then
  if [[ "$mode" == "empty" ]]; then
    printf '{{"object":"list","data":[]}}'
  elif [[ "$mode" == "malformed" ]]; then
    printf '{{"object":"list","data":[{{"id":"muse-spark-1.3"}}'
  elif [[ "$mode" == "wrong_shape" ]]; then
    printf '{{"object":"list","data":[],"id":"muse-spark-1.3"}}'
  else
    printf '{{"object":"list","data":[{{"id":"muse-spark-1.3"}}]}}'
  fi
  exit 0
fi
printf "200"
exit 0
""",
        )

        for bad_mode in ("empty", "malformed", "wrong_shape"):
            catalog_mode.write_text(f"{bad_mode}\n", encoding="utf-8")
            bad_res = subprocess.run(
                ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
                env=self._base_env(),
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(bad_res.returncode, 1, f"Expected Gate 8 failure for mode={bad_mode}")
            self.assertIn(
                "GATE FAILED [endpoints]: GET /v1/muse-code/models did not advertise muse-spark-1.3",
                bad_res.stdout,
            )
            self.assertTrue(
                flag_file.exists(),
                f"Gate 8 failure on {bad_mode} Muse catalog must retain update-available",
            )
            self.assertFalse(
                backup_cleanup_log.exists(),
                f"Gate 9 backup cleanup must not run when Gate 8 fails ({bad_mode})",
            )
        catalog_mode.write_text("ok\n", encoding="utf-8")
        pass_res = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(pass_res.returncode, 0, pass_res.stdout + pass_res.stderr)
        self.assertTrue(backup_cleanup_log.exists(), "Gate 9 did not execute pre-migration backup cleanup")
        self.assertIn("db_state-*_pre-migration.sqlite", backup_cleanup_log.read_text(encoding="utf-8"))
        self.assertFalse(flag_file.exists(), "Successful Gate 9 completion must clear update-available")

        # Also verify Gate 8 under 200 posture (catalog auth disabled)
        vm_posture.write_text("200\n", encoding="utf-8")
        flag_file.write_text(
            "sha256:b08a12e876baa8a5ccadd1ebbe346fe7267dba3b1c9f4fd6bb02070fae41ab6c\n",
            encoding="utf-8",
        )
        catalog_mode.write_text("empty\n", encoding="utf-8")
        bad_200_res = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(bad_200_res.returncode, 1)
        self.assertIn(
            "GATE FAILED [endpoints]: GET /v1/muse-code/models did not advertise muse-spark-1.3",
            bad_200_res.stdout,
        )
        self.assertTrue(flag_file.exists())
        catalog_mode.write_text("ok\n", encoding="utf-8")
        pass_200_res = subprocess.run(
            ["/bin/bash", str(UPDATE_SCRIPT), "3.8.52"],
            env=self._base_env(),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(pass_200_res.returncode, 0, pass_200_res.stdout + pass_200_res.stderr)
        self.assertFalse(flag_file.exists())

if __name__ == "__main__":
    unittest.main()
