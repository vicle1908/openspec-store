import hashlib
#!/usr/bin/env python3
"""Canonical unit tests for the Droid benchmark harness.

Tests scoring functions, helpers, and command construction with synthetic data.
Does NOT require real Droid providers or network access.
"""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add harness directory to path
HARNESS_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(HARNESS_DIR))

# Import the harness module
import run_benchmark as hb


class TestIsSuccess(unittest.TestCase):
    """Test the is_success() gate function."""

    def test_success_normal(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0}
        self.assertTrue(hb.is_success(r))

    def test_fail_timeout(self):
        r = {"status": "timeout"}
        self.assertFalse(hb.is_success(r))

    def test_fail_empty(self):
        r = {"status": "empty_output"}
        self.assertFalse(hb.is_success(r))

    def test_fail_parse(self):
        r = {"status": "parse_error"}
        self.assertFalse(hb.is_success(r))

    def test_fail_error(self):
        r = {"status": "error", "error": "something"}
        self.assertFalse(hb.is_success(r))

    def test_fail_is_error(self):
        r = {"status": "parsed", "is_error": True}
        self.assertFalse(hb.is_success(r))

    def test_fail_subtype_failure(self):
        r = {"status": "parsed", "subtype": "failure"}
        self.assertFalse(hb.is_success(r))

    def test_fail_exit_nonzero(self):
        r = {"status": "parsed", "exit_code": 1}
        self.assertFalse(hb.is_success(r))

    def test_success_exit_zero(self):
        r = {"status": "parsed", "exit_code": 0}
        self.assertTrue(hb.is_success(r))


class TestScoreS1(unittest.TestCase):
    """Test exact-response scoring."""

    def test_pass(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0, "result": "BENCHMARK_OK"}
        score, reason = hb.score_s1(r)
        self.assertEqual(score, 1)
        self.assertIsNone(reason)

    def test_fail_surrounding_text(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0, "result": "Here is your answer: BENCHMARK_OK"}
        score, _ = hb.score_s1(r)
        self.assertEqual(score, 0)  # exact match required

    def test_fail_wrong_text(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0, "result": "WRONG"}
        score, reason = hb.score_s1(r)
        self.assertEqual(score, 0)
        self.assertIn("no exact BENCHMARK_OK", reason)

    def test_fail_timeout(self):
        r = {"status": "timeout"}
        score, reason = hb.score_s1(r)
        self.assertEqual(score, 0)

    def test_fail_is_error(self):
        r = {"status": "parsed", "is_error": True}
        score, _ = hb.score_s1(r)
        self.assertEqual(score, 0)


class TestScoreS2(unittest.TestCase):
    """Test tool round-trip scoring."""

    def test_pass(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "num_turns": 2, "result": "The directory is EMPTY_DIR"}
        score, _ = hb.score_s2(r)
        self.assertEqual(score, 1)

    def test_pass_empty_lower(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "num_turns": 2, "result": "No files found, directory is empty"}
        score, _ = hb.score_s2(r)
        self.assertEqual(score, 1)

    def test_fail_one_turn(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "num_turns": 1, "result": "EMPTY_DIR"}
        score, reason = hb.score_s2(r)
        self.assertEqual(score, 0)
        self.assertIn("1 turns", reason)

    def test_fail_no_empty(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "num_turns": 2, "result": "Files: file1.py"}
        score, _ = hb.score_s2(r)
        self.assertEqual(score, 0)

    def test_fail_timeout(self):
        r = {"status": "timeout"}
        score, _ = hb.score_s2(r)
        self.assertEqual(score, 0)


class TestScoreS3(unittest.TestCase):
    """Test multi-turn recall scoring."""

    def test_pass(self):
        t1 = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0, "result": "CONFIRMED"}
        t2 = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0, "result": "ALPHABET"}
        score, _ = hb.score_s3(t1, t2)
        self.assertEqual(score, 1)

    def test_pass_case_insensitive(self):
        t1 = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0, "result": "CONFIRMED"}
        t2 = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0, "result": "The word was alphabet."}
        score, _ = hb.score_s3(t1, t2)
        self.assertEqual(score, 1)

    def test_fail_turn1_error(self):
        t1 = {"status": "timeout"}
        t2 = {"status": "parsed", "result": "ALPHABET"}
        score, _ = hb.score_s3(t1, t2)
        self.assertEqual(score, 0)

    def test_fail_turn2_no_alphabet(self):
        t1 = {"status": "parsed", "result": "CONFIRMED"}
        t2 = {"status": "parsed", "result": "I don't remember"}
        score, reason = hb.score_s3(t1, t2)
        self.assertEqual(score, 0)
        self.assertIn("no ALPHABET", reason)

    def test_fail_turn2_timeout(self):
        t1 = {"status": "parsed", "result": "CONFIRMED"}
        t2 = {"status": "timeout"}
        score, _ = hb.score_s3(t1, t2)
        self.assertEqual(score, 0)


class TestScoreS4(unittest.TestCase):
    """Test planning scoring."""

    def test_pass_perfect(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "1. Add /health endpoint to FastAPI app\n2. Return 200 OK with status\n3. Update app.py with the route"}
        score, _ = hb.score_s4(r)
        self.assertEqual(score, 3)

    def test_pass_two(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "Step 1: Create /health route\nStep 2: Use FastAPI\nStep 3: Test it"}
        score, _ = hb.score_s4(r)
        self.assertEqual(score, 2)

    def test_fail_no_steps(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "You should add a health endpoint."}
        score, _ = hb.score_s4(r)
        self.assertEqual(score, 1)  # mentions "health" → 1 point

    def test_fail_timeout(self):
        r = {"status": "timeout"}
        score, _ = hb.score_s4(r)
        self.assertEqual(score, 0)


class TestScoreS5(unittest.TestCase):
    """Test bug diagnosis scoring."""

    def test_pass_perfect(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "BUG: divide reverses b/a instead of a/b\nBUG: accumulate overwrites instead of summing\nnormalize is correct"}
        score, _ = hb.score_s5(r)
        self.assertEqual(score, 3)

    def test_pass_two_findings(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "BUG: arguments are swapped in divide\nBUG: result gets overwritten in accumulate"}
        score, _ = hb.score_s5(r)
        self.assertEqual(score, 2)

    def test_fail_one_finding(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "BUG: divide is wrong"}
        score, _ = hb.score_s5(r)
        self.assertEqual(score, 1)

    def test_fail_timeout(self):
        r = {"status": "timeout"}
        score, _ = hb.score_s5(r)
        self.assertEqual(score, 0)


class TestScoreS6(unittest.TestCase):
    """Test code edit scoring."""

    def test_pass_all_conditions(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0}
        score, _ = hb.score_s6(r, test_exit=0, source_changed=True, test_file_hash_ok=True)
        self.assertEqual(score, 1)

    def test_fail_test_exit_nonzero(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0}
        score, reason = hb.score_s6(r, test_exit=1, source_changed=True, test_file_hash_ok=True)
        self.assertEqual(score, 0)
        self.assertIn("test_exit=1", reason)

    def test_fail_source_unchanged(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0}
        score, reason = hb.score_s6(r, test_exit=0, source_changed=False, test_file_hash_ok=True)
        self.assertEqual(score, 0)
        self.assertEqual(reason, "source_not_changed")

    def test_fail_test_file_tampered(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0}
        score, reason = hb.score_s6(r, test_exit=0, source_changed=True, test_file_hash_ok=False)
        self.assertEqual(score, 0)
        self.assertEqual(reason, "test_file_tampered")

    def test_fail_droid_error(self):
        r = {"status": "parsed", "subtype": "failure", "is_error": True, "exit_code": 0}
        score, _ = hb.score_s6(r, test_exit=0, source_changed=True, test_file_hash_ok=True)
        self.assertEqual(score, 0)

    def test_fail_timeout(self):
        r = {"status": "timeout"}
        score, _ = hb.score_s6(r, test_exit=0, source_changed=True, test_file_hash_ok=True)
        self.assertEqual(score, 0)


class TestScoreS7(unittest.TestCase):
    """Test patch review scoring."""

    def test_pass_perfect(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "FINDING: Hardcoded password in ADMIN_PASSWORD\nFINDING: MD5 hash is weak and deprecated\nFINDING: SQL injection via string interpolation in get_user_profile"}
        score, _ = hb.score_s7(r)
        self.assertEqual(score, 3)

    def test_pass_two_findings(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "FINDING: Hardcoded credential\nFINDING: Uses MD5 which is insecure"}
        score, _ = hb.score_s7(r)
        self.assertEqual(score, 2)

    def test_fail_one_finding(self):
        r = {"status": "parsed", "subtype": "success", "is_error": False, "exit_code": 0,
             "result": "FINDING: SQL injection risk"}
        score, _ = hb.score_s7(r)
        self.assertEqual(score, 1)

    def test_fail_timeout(self):
        r = {"status": "timeout"}
        score, _ = hb.score_s7(r)
        self.assertEqual(score, 0)


class TestRunDroidCommand(unittest.TestCase):
    """Test run_droid command construction (mocked subprocess)."""

    def test_basic_command(self):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = json.dumps({"type": "result", "subtype": "success", "result": "OK"})
            mock_proc.stderr = ""
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc

            result = hb.run_droid("custom:fable-5", "test prompt", reasoning="none")

            args = mock_run.call_args[0][0]
            self.assertIn("--model", args)
            self.assertIn("custom:fable-5", args)
            self.assertIn("--reasoning-effort", args)
            self.assertIn("none", args)
            self.assertIn("test prompt", args)
            self.assertEqual(result["status"], "parsed")

    def test_no_reasoning_flag(self):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = json.dumps({"type": "result", "subtype": "success", "result": "OK"})
            mock_proc.stderr = ""
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc

            result = hb.run_droid("custom:fable-5", "test", reasoning=None)

            args = mock_run.call_args[0][0]
            self.assertNotIn("--reasoning-effort", args)
            self.assertEqual(result["status"], "parsed")

    def test_session_id(self):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = json.dumps({"type": "result", "subtype": "success", "result": "OK"})
            mock_proc.stderr = ""
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc

            result = hb.run_droid("custom:fable-5", "test", reasoning="none",
                                  extra_args=["--session-id", "abc123"])

            args = mock_run.call_args[0][0]
            self.assertIn("--session-id", args)
            self.assertIn("abc123", args)

    def test_timeout_handling(self):
        import subprocess as sp
        with patch("subprocess.run", side_effect=sp.TimeoutExpired(cmd="test", timeout=120)):
            result = hb.run_droid("custom:fable-5", "test", reasoning="none")
            self.assertEqual(result["status"], "timeout")

    def test_empty_output(self):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = ""
            mock_proc.stderr = ""
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc

            result = hb.run_droid("custom:fable-5", "test", reasoning="none")
            self.assertEqual(result["status"], "empty_output")

    def test_parse_error(self):
        with patch("subprocess.run") as mock_run:
            mock_proc = MagicMock()
            mock_proc.stdout = "not json at all"
            mock_proc.stderr = ""
            mock_proc.returncode = 0
            mock_run.return_value = mock_proc

            result = hb.run_droid("custom:fable-5", "test", reasoning="none")
            self.assertEqual(result["status"], "parse_error")


class TestDeduplication(unittest.TestCase):
    """Test run_id deduplication."""

    def test_record_exists_false(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("")
            path = f.name
        try:
            hb.RESULTS_FILE = Path(path)
            self.assertFalse(hb.record_exists("nonexistent-id"))
        finally:
            os.unlink(path)

    def test_record_exists_true(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"run_id": "test-id-123"}) + "\n")
            path = f.name
        try:
            hb.RESULTS_FILE = Path(path)
            self.assertTrue(hb.record_exists("test-id-123"))
        finally:
            os.unlink(path)


class TestResultText(unittest.TestCase):
    """Test get_result_text helper."""

    def test_normal(self):
        r = {"result": "some text"}
        self.assertEqual(hb.get_result_text(r), "some text")

    def test_missing(self):
        r = {}
        self.assertEqual(hb.get_result_text(r), "")

    def test_empty(self):
        r = {"result": ""}
        self.assertEqual(hb.get_result_text(r), "")


class TestBaselineRecord(unittest.TestCase):
    """Test baseline infrastructure_unavailable recording."""

    def test_baseline_is_excluded_from_providers(self):
        """Baseline should not appear in the PROVIDERS list."""
        provider_labels = [p["label"] for p in hb.PROVIDERS]
        self.assertNotIn("baseline", provider_labels)

    def test_baseline_has_infra_status(self):
        """BASELINE dict should have status infrastructure_unavailable."""
        self.assertEqual(hb.BASELINE.get("status"), "infrastructure_unavailable")



class TestPrepareFixtures(unittest.TestCase):
    """Test fixture preparation from evidence to runtime."""

    def setUp(self):
        """Remove /tmp/droid-benchmark if it exists."""
        import shutil
        if os.path.exists("/tmp/droid-benchmark"):
            shutil.rmtree("/tmp/droid-benchmark")

    def tearDown(self):
        """Clean up runtime directory."""
        import shutil
        if os.path.exists("/tmp/droid-benchmark"):
            shutil.rmtree("/tmp/droid-benchmark")

    def test_prepare_fixtures_succeeds(self):
        result = hb.prepare_fixtures()
        self.assertTrue(result)
        self.assertTrue(os.path.exists("/tmp/droid-benchmark"))
        self.assertTrue(os.path.exists("/tmp/droid-benchmark/buggy-module/calculator.py"))
        self.assertTrue(os.path.exists("/tmp/droid-benchmark/edit-task/string_utils.py"))
        self.assertTrue(os.path.exists("/tmp/droid-benchmark/planning-project/app.py"))
        self.assertTrue(os.path.exists("/tmp/droid-benchmark/patch-review/auth.py"))

    def test_empty_dir_is_actually_empty(self):
        hb.prepare_fixtures()
        empty_dir = "/tmp/droid-benchmark/empty-dir"
        self.assertTrue(os.path.isdir(empty_dir))
        self.assertEqual(len(os.listdir(empty_dir)), 0)

    def test_deterministic_rerun(self):
        hb.prepare_fixtures()
        h1 = hashlib.sha256(Path("/tmp/droid-benchmark/buggy-module/calculator.py").read_bytes()).hexdigest()
        hb.prepare_fixtures()
        h2 = hashlib.sha256(Path("/tmp/droid-benchmark/buggy-module/calculator.py").read_bytes()).hexdigest()
        self.assertEqual(h1, h2)

    def test_git_repo_initialized(self):
        hb.prepare_fixtures()
        self.assertTrue(os.path.isdir("/tmp/droid-benchmark/.git"))

    def test_no_readme_in_runtime(self):
        hb.prepare_fixtures()
        self.assertFalse(os.path.exists("/tmp/droid-benchmark/README.md"))
        self.assertFalse(os.path.exists("/tmp/droid-benchmark/SHA256SUMS"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
