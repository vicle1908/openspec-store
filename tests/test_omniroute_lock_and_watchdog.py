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
exit 0
""",
        )
        _write_executable(
            self.local_bin / "curl",
            """#!/bin/bash
if [[ "$*" == *"/healthz"* ]]; then printf "ok"; exit 0; fi
if [[ "$*" == *"/api/monitoring/health"* ]]; then printf '{"status":"healthy","setupComplete":true}'; exit 0; fi
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


if __name__ == "__main__":
    unittest.main()
