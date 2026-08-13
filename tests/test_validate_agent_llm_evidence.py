from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-agent-llm-evidence.py"
SCHEMA_SOURCE = (
    ROOT
    / "openspec"
    / "changes"
    / "complete-agent-llm-config-integration"
    / "evidence"
    / "schema"
    / "v1"
    / "evidence-record.schema.json"
)
FIXTURES = Path(__file__).parent / "fixtures" / "agent-llm-evidence"
CHANGE = "complete-agent-llm-config-integration"
EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def raw_git_status(path: Path) -> bytes:
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=path,
        check=True,
        capture_output=True,
        text=False,
    )
    return bytes(process.stdout)


def classified_content_sha(path: Path, relative: str) -> str:
    return sha256_bytes(f"{relative}\0{sha256_file(path / relative)}\n".encode())


def corrective_tree_digest(store: Path, change_root: Path) -> str:
    lines: list[str] = []
    root = store / change_root
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(store)
        if path.is_symlink():
            raise AssertionError(
                f"fixture corrective tree contains symlink: {relative}"
            )
        if path.is_file() and (change_root / "evidence" / "results") not in [
            relative,
            *relative.parents,
        ]:
            lines.append(f"{relative.as_posix()}\0{sha256_file(path)}\n")
    return sha256_bytes("".join(lines).encode("utf-8"))


def write_distribution_metadata(
    site_packages: Path,
    *,
    distribution: str,
    version: str,
    import_name: str,
) -> None:
    dist_info = site_packages / f"{distribution.replace('-', '_')}-{version}.dist-info"
    dist_info.mkdir()
    (dist_info / "METADATA").write_text(
        f"Metadata-Version: 2.4\nName: {distribution}\nVersion: {version}\n",
        encoding="utf-8",
    )
    (dist_info / "RECORD").write_text(
        f"{import_name.replace('.', '/')}/__init__.py,,\n",
        encoding="utf-8",
    )


def run(
    argv: list[str],
    *,
    cwd: Path,
    check: bool = True,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        env=env,
    )


def git(path: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *args], cwd=path, check=check)


def init_repository(path: Path, files: dict[str, str]) -> str:
    path.mkdir(parents=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Validator Fixture")
    git(path, "config", "user.email", "validator-fixture@example.invalid")
    for relative, content in files.items():
        target = path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    git(path, "add", "--all")
    git(path, "commit", "-m", "fixture baseline")
    return git(path, "rev-parse", "HEAD").stdout.strip()


def render_template(name: str, values: dict[str, str]) -> dict[str, object]:
    text = (FIXTURES / name).read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("${" + key + "}", value)
    unresolved = sorted(
        part.split("}", 1)[0] for part in text.split("${")[1:] if "}" in part
    )
    if unresolved:
        raise AssertionError(f"unresolved template values: {unresolved}")
    loaded = json.loads(text)
    if not isinstance(loaded, dict):
        raise TypeError(f"fixture {name} is not an object")
    return loaded


class EvidenceFixture:
    def __init__(self, base: Path) -> None:
        self.base = base
        self.store = base / "openspec-store"
        self.tdt = base / "tdt-core"
        self.consumer = base / "agent-core"
        self.review = base / "ai-review"
        self.inputs = base / "inputs"
        self.site_packages = base / "site-packages"
        self.review_site_packages = base / "review-site-packages"
        self.bin = base / "bin"
        self.inputs.mkdir()
        self.site_packages.mkdir()
        self.review_site_packages.mkdir()
        self.bin.mkdir()

        change_root = Path("openspec") / "changes" / CHANGE
        schema_relative = (
            change_root / "evidence" / "schema" / "v1" / "evidence-record.schema.json"
        )
        capability_specs = (
            "agent-config-resolution",
            "agent-core-model-resolution",
            "agent-docs-sync",
            "cli-provider-profile-resolution",
            "provider-model-profile-resolution",
        )
        store_files = {
            str(change_root / "proposal.md"): "## Why\nfixture proposal\n",
            str(change_root / "design.md"): "## Context\nfixture design\n",
            str(change_root / "tasks.md"): "## 1. Fixture\n\n- [ ] 1.1 fixture\n",
            str(schema_relative): SCHEMA_SOURCE.read_text(encoding="utf-8"),
        }
        for capability in capability_specs:
            store_files[str(change_root / "specs" / capability / "spec.md")] = (
                f"## ADDED Requirements\nfixture {capability}\n"
            )
        self.store_sha = init_repository(self.store, store_files)
        self.tdt_sha = init_repository(
            self.tdt,
            {
                "pyproject.toml": "[project]\nname='tdt-core'\nversion='1.0.0'\n",
                "src/tdt_core/__init__.py": (
                    "raise RuntimeError('TARGET_PACKAGE_MUST_NOT_BE_IMPORTED')\n"
                ),
            },
        )
        self.consumer_sha = init_repository(
            self.consumer,
            {
                "pyproject.toml": (
                    "[project]\nname='agent-core'\nversion='1.0.0'\n"
                    "dependencies=['tdt-core']\n"
                ),
                "uv.lock": "version = 1\nrevision = 1\n",
                "src/agent_core.py": "MODEL = 'fixture'\n",
                "tests/test_agent_core.py": "def test_fixture():\n    assert True\n",
            },
        )
        self.review_sha = init_repository(
            self.review,
            {
                "pyproject.toml": (
                    "[project]\nname='ai-review'\nversion='1.0.0'\n"
                    "dependencies=['agent-core']\n"
                ),
                "uv.lock": "version = 1\nrevision = 1\n",
                "src/ai_review.py": "REVIEWER = 'fixture'\n",
                "tests/test_ai_review.py": "def test_fixture():\n    assert True\n",
            },
        )
        package_link = self.site_packages / "tdt_core"
        package_link.symlink_to(self.tdt / "src" / "tdt_core", target_is_directory=True)
        write_distribution_metadata(
            self.site_packages,
            distribution="tdt-core",
            version="1.0.0",
            import_name="tdt_core",
        )
        agent_core_package = self.consumer / "src" / "agent_core"
        agent_core_package.mkdir()
        (agent_core_package / "__init__.py").write_text(
            "VALUE = 'agent-core-package'\n", encoding="utf-8"
        )
        git(self.consumer, "add", "src/agent_core/__init__.py")
        git(self.consumer, "commit", "-m", "fixture package")
        self.consumer_sha = git(self.consumer, "rev-parse", "HEAD").stdout.strip()
        review_link = self.review_site_packages / "agent_core"
        review_link.symlink_to(agent_core_package, target_is_directory=True)
        write_distribution_metadata(
            self.review_site_packages,
            distribution="agent-core",
            version="1.0.0",
            import_name="agent_core",
        )

        proposal = change_root / "proposal.md"
        specs = [
            change_root / "specs" / capability / "spec.md"
            for capability in capability_specs
        ]
        design = change_root / "design.md"
        tasks = change_root / "tasks.md"
        artifacts = [proposal, *specs, design, tasks]
        schema_path = self.store / schema_relative
        artifact_hashes = {
            str(path): sha256_file(self.store / path) for path in artifacts
        }
        schema_hash = sha256_file(schema_path)
        digest_lines = [
            f"{path}\0{artifact_hashes[str(path)]}\n" for path in artifacts
        ] + [f"{schema_relative}\0{schema_hash}\n"]
        planning_digest = sha256_bytes("".join(sorted(digest_lines)).encode())
        baseline_tree_sha = git(
            self.store, "rev-parse", f"{self.store_sha}:{change_root}"
        ).stdout.strip()
        origin = (self.tdt / "src" / "tdt_core" / "__init__.py").resolve()
        agent_core_origin = (agent_core_package / "__init__.py").resolve()
        substitutions = {
            "STORE_SHA": self.store_sha,
            "BASELINE_TREE_SHA": baseline_tree_sha,
            "CORRECTIVE_TREE_SHA256": corrective_tree_digest(self.store, change_root),
            "PLANNING_DIGEST": planning_digest,
            "PROPOSAL_SHA256": artifact_hashes[str(proposal)],
            "AGENT_CONFIG_SPEC_SHA256": artifact_hashes[str(specs[0])],
            "AGENT_CORE_SPEC_SHA256": artifact_hashes[str(specs[1])],
            "DOCS_SYNC_SPEC_SHA256": artifact_hashes[str(specs[2])],
            "CLI_SPEC_SHA256": artifact_hashes[str(specs[3])],
            "PROVIDER_SPEC_SHA256": artifact_hashes[str(specs[4])],
            "DESIGN_SHA256": artifact_hashes[str(design)],
            "TASKS_SHA256": artifact_hashes[str(tasks)],
            "SCHEMA_SHA256": schema_hash,
            "STORE_ROOT": str(self.store.resolve()),
            "TDT_SHA": self.tdt_sha,
            "TDT_ROOT": str(self.tdt.resolve()),
            "CONSUMER_SHA": self.consumer_sha,
            "CONSUMER_ROOT": str(self.consumer.resolve()),
            "REVIEW_ROOT": str(self.review.resolve()),
            "CLEAN_DIRT_SHA256": EMPTY_SHA256,
            "PYPROJECT_SHA256": sha256_file(self.consumer / "pyproject.toml"),
            "LOCK_SHA256": sha256_file(self.consumer / "uv.lock"),
            "TDT_ORIGIN": str(origin),
            "AGENT_CORE_ORIGIN": str(agent_core_origin),
            "SOURCE_SHA256": sha256_file(self.consumer / "src" / "agent_core.py"),
            "MECHANISM_SHA256": sha256_file(
                self.consumer / "tests" / "test_agent_core.py"
            ),
            "SITE_PACKAGES": str(self.site_packages.resolve()),
            "REVIEW_SITE_PACKAGES": str(self.review_site_packages.resolve()),
            "ATTESTATION_SHA256": sha256_bytes(b"fixture-containment-check"),
            "PROPOSAL_PATH": str((self.store / proposal).resolve()),
            "AGENT_CONFIG_SPEC_PATH": str((self.store / specs[0]).resolve()),
            "AGENT_CORE_SPEC_PATH": str((self.store / specs[1]).resolve()),
            "DOCS_SYNC_SPEC_PATH": str((self.store / specs[2]).resolve()),
            "CLI_SPEC_PATH": str((self.store / specs[3]).resolve()),
            "PROVIDER_SPEC_PATH": str((self.store / specs[4]).resolve()),
            "DESIGN_PATH": str((self.store / design).resolve()),
            "TASKS_PATH": str((self.store / tasks).resolve()),
        }
        self.record = render_template("record-template.json", substitutions)
        self.repository_map = render_template(
            "repository-map-template.json", substitutions
        )
        self.status = render_template("openspec-status-template.json", substitutions)
        self.schema = schema_path
        self.record_path = self.inputs / "record.json"
        self.map_path = self.inputs / "repository-map.json"
        self.status_path = self.inputs / "openspec-status.json"
        openspec = self.bin / "openspec"
        openspec.write_text(
            '#!/bin/sh\nexec /bin/cat "$VALIDATOR_STATUS_JSON"\n',
            encoding="utf-8",
        )
        openspec.chmod(0o755)
        self.write_inputs()

    def write_inputs(self) -> None:
        self.record_path.write_text(
            json.dumps(self.record, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.map_path.write_text(
            json.dumps(self.repository_map, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.status_path.write_text(
            json.dumps(self.status, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def make_live_record(self, *, include_execution: bool = False) -> None:
        record = self.record
        record["record_id"] = "ai-review-live"
        record["record_kind"] = "live_row"
        record["repositories"] = [
            entry
            for entry in record["repositories"]
            if entry["id"] in {"openspec-store", "tdt-core", "agent-core"}
        ]
        record["repositories"].append(
            {
                "id": "ai-review",
                "head_sha": self.review_sha,
                "branch": "main",
                "worktree_path": str(self.review.resolve()),
                "dirt_sha256": EMPTY_SHA256,
                "dirt_inventory": [],
            }
        )
        original_dependency = copy.deepcopy(record["dependencies"][0])
        tdt_dependency = copy.deepcopy(original_dependency)
        tdt_dependency["id"] = "ai-review-to-tdt-core"
        tdt_dependency["consumer_repository"] = "ai-review"
        for key in ("declaration", "lock"):
            tdt_dependency[key]["repository"] = "ai-review"
        tdt_dependency["declaration"]["id"] = "ai-review-pyproject"
        tdt_dependency["declaration"]["path"] = "pyproject.toml"
        tdt_dependency["declaration"]["sha256"] = sha256_file(
            self.review / "pyproject.toml"
        )
        tdt_dependency["lock"]["id"] = "ai-review-lock"
        tdt_dependency["lock"]["path"] = "uv.lock"
        tdt_dependency["lock"]["sha256"] = sha256_file(self.review / "uv.lock")
        agent_dependency = copy.deepcopy(tdt_dependency)
        agent_dependency["id"] = "ai-review-to-agent-core"
        agent_dependency["upstream_repository"] = "agent-core"
        agent_dependency["source_checkout"] = {
            "repository": "agent-core",
            "path": str(self.consumer.resolve()),
            "head_sha": self.consumer_sha,
        }
        agent_dependency["installed"] = {
            "environment": "ai-review-env",
            "distribution": "agent-core",
            "import_name": "agent_core",
            "origin_path": str(
                (self.consumer / "src" / "agent_core" / "__init__.py").resolve()
            ),
            "origin_repository": "agent-core",
            "origin_sha": self.consumer_sha,
        }
        record["dependencies"] = [tdt_dependency, agent_dependency]
        record["sources"] = [
            {
                "id": "ai-review-source",
                "repository": "ai-review",
                "path": "src/ai_review.py",
                "sha256": sha256_file(self.review / "src" / "ai_review.py"),
            }
        ]
        record["mechanisms"] = [
            {
                "id": "ai-review-test-mechanism",
                "repository": "ai-review",
                "path": "tests/test_ai_review.py",
                "sha256": sha256_file(self.review / "tests" / "test_ai_review.py"),
            }
        ]
        command_shape = ["uv", "run", "ai-review", "<contained-target>"]
        live: dict[str, object] = {
            "consumer_boundary": {
                "id": "ai-review-reviewer",
                "repository": "ai-review",
                "kind": "reviewer",
            },
            "provider_route": {
                "cli_adapter_id": "codex",
                "canonical_provider_id": "tdt-codex",
                "canonical_alias": "fixture-model",
                "wire_model": "fixture-wire-model",
                "behavior_sha256": sha256_bytes(b"fixture-behavior"),
            },
            "mechanism": {
                "id": "ai-review-test-mechanism",
                "command_shape_sha256": sha256_bytes(
                    json.dumps(command_shape, separators=(",", ":")).encode()
                ),
                "redacted_command_shape": command_shape,
            },
            "authorization": {
                "status": "authorized",
                "attestation_id": "contained-target",
                "source_id": "fixture-containment-check",
                "source_sha256": sha256_bytes(b"fixture-containment-check"),
            },
        }
        if include_execution:
            live["execution"] = {
                "process_reachable": True,
                "process_exit_code": 0,
                "monotonic_duration_ms": 10,
                "nested_outcome": {
                    "status": "succeeded",
                    "provider_error": False,
                    "completion_state": "complete",
                },
                "proof": {
                    "kind": "nonce",
                    "expected": {
                        "id": "fixture-nonce",
                        "sha256": sha256_bytes(b"fixture-nonce"),
                    },
                    "observed": True,
                },
                "target_preservation": {
                    "status": "preserved",
                    "source_id": "fixture-target-check",
                    "source_sha256": sha256_bytes(b"fixture-target-check"),
                },
                "row_status": "passed",
            }
        record["live"] = live
        self.write_inputs()

    def invoke(
        self,
        gate: str = "handoff_acceptance",
        *,
        output: Path | None = None,
        observed_at: str | None = None,
        env: dict[str, str] | None = None,
        record_path: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        argv = [
            sys.executable,
            str(SCRIPT),
            "--record",
            str(record_path or self.record_path),
            "--schema",
            str(self.schema),
            "--gate",
            gate,
            "--repository-map",
            str(self.map_path),
        ]
        if output is not None:
            argv.extend(["--output", str(output)])
        if observed_at is not None:
            argv.extend(["--observed-at", observed_at])
        environment = os.environ.copy()
        if env is not None:
            environment.update(env)
        environment["VALIDATOR_STATUS_JSON"] = str(self.status_path)
        environment["PATH"] = f"{self.bin}{os.pathsep}{environment.get('PATH', '')}"
        return run(argv, cwd=self.store, check=False, env=environment)

    def result(
        self, *args: object, **kwargs: object
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        process = self.invoke(*args, **kwargs)
        result = json.loads(process.stdout)
        if not isinstance(result, dict):
            raise TypeError("validator result is not an object")
        return process, result


class ValidateAgentLlmEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.fixture = EvidenceFixture(Path(self.temporary.name))

    def assertDecision(
        self,
        process: subprocess.CompletedProcess[str],
        result: dict[str, object],
        *,
        exit_code: int,
        decision: str,
    ) -> None:
        self.assertEqual(process.returncode, exit_code, process.stderr)
        self.assertEqual(result["exit_code"], exit_code)
        self.assertEqual(result["decision"], decision)

    def comparison(self, result: dict[str, object], field: str) -> dict[str, object]:
        return next(item for item in result["comparisons"] if item["field"] == field)

    def test_current_deterministic_record_is_stable_and_current(self) -> None:
        first, result = self.fixture.result()
        second = self.fixture.invoke()
        self.assertDecision(first, result, exit_code=0, decision="current")
        self.assertEqual(first.stdout, second.stdout)
        self.assertNotIn("observed_at", result)
        self.assertEqual(result["affected_records"], [])
        comparisons = result["comparisons"]
        self.assertEqual(
            [item["field"] for item in comparisons],
            sorted(item["field"] for item in comparisons),
        )

    def test_current_live_row_passes_live_launch_gate(self) -> None:
        self.fixture.make_live_record()
        process, result = self.fixture.result("live_launch")
        self.assertDecision(process, result, exit_code=0, decision="current")

    def test_all_eight_lifecycle_gates_are_supported(self) -> None:
        deterministic_gates = (
            "handoff_acceptance",
            "evidence_reuse",
            "downstream_unblock",
            "task_completion",
            "spec_sync",
            "archive_readiness",
        )
        for gate in deterministic_gates:
            with self.subTest(gate=gate):
                process, result = self.fixture.result(gate)
                self.assertDecision(process, result, exit_code=0, decision="current")

        self.fixture.make_live_record()
        for gate in ("live_authorization", "live_launch"):
            with self.subTest(gate=gate):
                process, result = self.fixture.result(gate)
                self.assertDecision(process, result, exit_code=0, decision="current")

    def test_drifted_planning_artifact_invalidates_every_record(self) -> None:
        proposal = self.fixture.store / "openspec" / "changes" / CHANGE / "proposal.md"
        proposal.write_text("## Why\ndrifted proposal\n", encoding="utf-8")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        expected = sorted(item["id"] for item in self.fixture.repository_map["records"])
        self.assertEqual(result["affected_records"], expected)

    def test_each_concrete_planning_artifact_drift_is_stale(self) -> None:
        relative_paths = [
            entry["path"] for entry in self.fixture.record["planning"]["artifacts"]
        ]
        for relative in relative_paths:
            with (
                self.subTest(path=relative),
                tempfile.TemporaryDirectory() as temporary,
            ):
                fixture = EvidenceFixture(Path(temporary))
                path = fixture.store / relative
                path.write_text(path.read_text(encoding="utf-8") + "drift\n")
                process, result = fixture.result()
                self.assertDecision(process, result, exit_code=2, decision="stale")
                self.assertEqual(
                    result["affected_records"],
                    sorted(item["id"] for item in fixture.repository_map["records"]),
                )

    def test_record_must_contain_exact_five_delta_specs(self) -> None:
        artifacts = self.fixture.record["planning"]["artifacts"]
        artifacts.remove(
            next(item for item in artifacts if item["artifact_id"] == "specs")
        )
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_corrective_tree_drift_outside_results_is_stale(self) -> None:
        evidence = (
            self.fixture.store
            / "openspec"
            / "changes"
            / CHANGE
            / "evidence"
            / "owned-note.json"
        )
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("{}\n", encoding="utf-8")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        self.assertEqual(
            self.comparison(result, "planning.corrective_tree_sha256")["decision"],
            "stale",
        )

    def test_results_subtree_is_excluded_from_corrective_tree_digest(self) -> None:
        result_file = (
            self.fixture.store
            / "openspec"
            / "changes"
            / CHANGE
            / "evidence"
            / "results"
            / "unselected.json"
        )
        result_file.parent.mkdir(parents=True)
        result_file.write_text("{}\n", encoding="utf-8")
        store_repository = self.fixture.record["repositories"][0]
        raw_status = git(
            self.fixture.store,
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ).stdout.encode()
        store_repository["dirt_sha256"] = sha256_bytes(raw_status)
        store_repository["dirt_inventory"] = [
            {
                "status": "??",
                "paths": [str(result_file.relative_to(self.fixture.store))],
                "category": "generated",
                "content_classification": "metadata_only",
                "content_sha256": None,
            }
        ]
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=0, decision="current")

    def test_descendant_evidence_only_commit_does_not_self_invalidate(self) -> None:
        evidence = (
            self.fixture.store
            / "openspec"
            / "changes"
            / CHANGE
            / "evidence"
            / "results"
            / "prior.json"
        )
        evidence.parent.mkdir(parents=True)
        evidence.write_text('{"decision":"current"}\n', encoding="utf-8")
        git(self.fixture.store, "add", str(evidence.relative_to(self.fixture.store)))
        git(self.fixture.store, "commit", "-m", "evidence only")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=0, decision="current")
        self.assertNotEqual(result["observed_store_head"], self.fixture.store_sha)

    def test_missing_or_nonancestor_baseline_is_stale(self) -> None:
        self.fixture.record["planning"]["baseline_sha"] = "f" * 40
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        self.assertEqual(
            result["affected_records"],
            sorted(item["id"] for item in self.fixture.repository_map["records"]),
        )

    def test_baseline_tree_mismatch_is_stale(self) -> None:
        self.fixture.record["planning"]["baseline_tree_sha"] = "a" * 40
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")

    def test_existing_nonancestor_baseline_is_stale(self) -> None:
        tree = git(self.fixture.store, "write-tree").stdout.strip()
        alternate = git(
            self.fixture.store,
            "commit-tree",
            tree,
            check=True,
        ).stdout.strip()
        self.fixture.record["planning"]["baseline_sha"] = alternate
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")

    def test_unclassified_upstream_dirt_propagates_to_actual_dependents(self) -> None:
        (self.fixture.tdt / "untracked.txt").write_text("dirt\n", encoding="utf-8")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        self.assertEqual(
            result["affected_records"],
            [
                "agent-core-handoff",
                "agent-docs-sync-handoff",
                "agent-harness-handoff",
                "ai-harness-skills-live",
                "ai-review-live",
            ],
        )

    def test_nul_delimited_dirt_handles_newline_in_filename(self) -> None:
        unusual = self.fixture.consumer / "untracked\nname.txt"
        unusual.write_text("dirt\n", encoding="utf-8")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        comparison = next(
            item
            for item in result["comparisons"]
            if item["field"] == "repository.agent-core.dirt_sha256"
        )
        self.assertEqual(
            comparison["current"], sha256_bytes(raw_git_status(self.fixture.consumer))
        )

    def test_rename_porcelain_pair_matches_raw_bytes_exactly(self) -> None:
        old = self.fixture.consumer / "tests" / "test_agent_core.py"
        new = self.fixture.consumer / "tests" / "renamed\nagent_core.py"
        old.rename(new)
        git(self.fixture.consumer, "add", "--all")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        mechanism = self.comparison(result, "mechanism.agent-core-test-mechanism")
        self.assertEqual(mechanism["current"], "missing")
        self.assertEqual(mechanism["decision"], "stale")
        dependency_dirt = self.comparison(
            result, "repository.agent-core.dependency_relevant_dirt"
        )
        self.assertEqual(dependency_dirt["current"], [])
        self.assertEqual(result["affected_records"], ["agent-core-handoff"])
        comparison = self.comparison(result, "repository.agent-core.dirt_sha256")
        self.assertEqual(
            comparison["current"], sha256_bytes(raw_git_status(self.fixture.consumer))
        )

    def test_classified_non_secret_dirt_matches_content_and_raw_porcelain(self) -> None:
        relative = "tests/generated proof.txt"
        path = self.fixture.consumer / relative
        path.write_text("fixture proof\n", encoding="utf-8")
        repository = next(
            item
            for item in self.fixture.record["repositories"]
            if item["id"] == "agent-core"
        )
        repository["dirt_sha256"] = sha256_bytes(raw_git_status(self.fixture.consumer))
        repository["dirt_inventory"] = [
            {
                "status": "??",
                "paths": [relative],
                "category": "test",
                "content_classification": "non_secret",
                "content_sha256": classified_content_sha(
                    self.fixture.consumer, relative
                ),
            }
        ]
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=0, decision="current")

    def test_unclassified_dirt_is_stale_not_invalid(self) -> None:
        (self.fixture.consumer / "unexpected.py").write_text(
            "VALUE = 1\n", encoding="utf-8"
        )
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        inventory = self.comparison(result, "repository.agent-core.dirt_inventory")
        self.assertEqual(inventory["current"][0]["category"], "unclassified")

    def test_invalid_beats_blocked_and_stale(self) -> None:
        self.fixture.record["dependencies"] = []
        self.fixture.repository_map["attestations"] = {}
        (self.fixture.consumer / "uv.lock").write_text("drift\n", encoding="utf-8")
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_blocked_beats_stale(self) -> None:
        self.fixture.repository_map["attestations"] = {}
        (self.fixture.consumer / "uv.lock").write_text("drift\n", encoding="utf-8")
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_lock_drift_is_stale(self) -> None:
        (self.fixture.consumer / "uv.lock").write_text(
            "version = 1\nrevision = 2\n", encoding="utf-8"
        )
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")

    def test_installed_origin_drift_is_stale(self) -> None:
        alternate = self.fixture.base / "other-tdt-core"
        init_repository(
            alternate,
            {"src/tdt_core/__init__.py": "VALUE = 'other'\n"},
        )
        link = self.fixture.site_packages / "tdt_core"
        link.unlink()
        link.symlink_to(alternate / "src" / "tdt_core", target_is_directory=True)
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")

    def test_missing_installed_origin_is_blocked(self) -> None:
        link = self.fixture.site_packages / "tdt_core"
        link.unlink()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_distribution_metadata_must_own_import_origin(self) -> None:
        record = self.fixture.site_packages / "tdt_core-1.0.0.dist-info" / "RECORD"
        record.write_text("other_package/__init__.py,,\n", encoding="utf-8")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_uv_style_editable_pth_origin_is_discovered_without_import(self) -> None:
        link = self.fixture.site_packages / "tdt_core"
        link.unlink()
        dist_info = self.fixture.site_packages / "tdt_core-1.0.0.dist-info"
        launcher = self.fixture.site_packages / "_editable_impl_tdt_core.pth"
        launcher.write_text(
            str((self.fixture.tdt / "src").resolve()) + "\n", encoding="utf-8"
        )
        (dist_info / "RECORD").write_text(
            "_editable_impl_tdt_core.pth,,\n", encoding="utf-8"
        )
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=0, decision="current")
        self.assertNotIn("TARGET_PACKAGE_MUST_NOT_BE_IMPORTED", process.stderr)

    def test_origin_discovery_does_not_import_target_package(self) -> None:
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=0, decision="current")
        self.assertNotIn("TARGET_PACKAGE_MUST_NOT_BE_IMPORTED", process.stderr)

    def test_required_dependency_cannot_be_omitted(self) -> None:
        self.fixture.record["dependencies"] = []
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_dependency_observation_wrong_origin_is_stale(self) -> None:
        observation = self.fixture.repository_map["dependency_observations"][0]
        observation["origin_path"] = str(self.fixture.base / "other-origin.py")
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")

    def test_source_symlink_escape_is_invalid(self) -> None:
        source = self.fixture.consumer / "src" / "agent_core.py"
        external = self.fixture.base / "external.py"
        external.write_text("VALUE = 'external'\n", encoding="utf-8")
        source.unlink()
        source.symlink_to(external)
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_malformed_secret_record_is_invalid_without_echoing_canary(self) -> None:
        malformed = FIXTURES / "malformed-record.json"
        process = self.fixture.invoke(record_path=malformed)
        result = json.loads(process.stdout)
        self.assertDecision(process, result, exit_code=4, decision="invalid")
        combined = process.stdout + process.stderr
        self.assertNotIn("VALIDATOR_CREDENTIAL_CANARY_DO_NOT_EMIT", combined)

    def test_missing_attestation_is_blocked(self) -> None:
        self.fixture.repository_map["attestations"] = {}
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_duplicate_record_inventory_is_invalid(self) -> None:
        duplicate = copy.deepcopy(self.fixture.repository_map["records"][0])
        self.fixture.repository_map["records"].append(duplicate)
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_duplicate_repository_root_identity_is_invalid(self) -> None:
        self.fixture.repository_map["repositories"]["ai-review"]["root"] = str(
            self.fixture.consumer.resolve()
        )
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_repository_map_credential_key_is_invalid_and_redacted(self) -> None:
        self.fixture.repository_map["credential_value"] = (
            "REPOSITORY_MAP_CANARY_MUST_NOT_APPEAR"
        )
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")
        self.assertNotIn("REPOSITORY_MAP_CANARY_MUST_NOT_APPEAR", process.stdout)

    def test_attestation_state_rejects_arbitrary_string(self) -> None:
        self.fixture.repository_map["attestations"]["contained-target"]["state"] = (
            "ARBITRARY_ATTESTATION_VALUE_MUST_NOT_APPEAR"
        )
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")
        self.assertNotIn("ARBITRARY_ATTESTATION_VALUE_MUST_NOT_APPEAR", process.stdout)

    def test_tdt_core_drift_propagates_to_actual_downstream_records(self) -> None:
        source = self.fixture.tdt / "src" / "tdt_core" / "__init__.py"
        source.write_text("VALUE = 'changed'\n", encoding="utf-8")
        git(self.fixture.tdt, "add", str(source.relative_to(self.fixture.tdt)))
        git(self.fixture.tdt, "commit", "-m", "upstream drift")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        self.assertEqual(
            result["affected_records"],
            [
                "agent-core-handoff",
                "agent-docs-sync-handoff",
                "agent-harness-handoff",
                "ai-harness-skills-live",
                "ai-review-live",
            ],
        )

    def test_agent_core_committed_drift_propagates_only_to_ai_review(self) -> None:
        source = self.fixture.consumer / "src" / "agent_core" / "__init__.py"
        source.write_text("VALUE = 'changed'\n", encoding="utf-8")
        git(
            self.fixture.consumer, "add", str(source.relative_to(self.fixture.consumer))
        )
        git(self.fixture.consumer, "commit", "-m", "agent-core drift")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        self.assertEqual(
            result["affected_records"], ["agent-core-handoff", "ai-review-live"]
        )

    def test_consumer_mechanism_drift_affects_only_current_record(self) -> None:
        mechanism = self.fixture.consumer / "tests" / "test_agent_core.py"
        mechanism.write_text(
            "def test_fixture():\n    assert False\n", encoding="utf-8"
        )
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")
        self.assertEqual(result["affected_records"], ["agent-core-handoff"])

    def test_environment_presence_never_serializes_value(self) -> None:
        self.fixture.record["prerequisites"].append(
            {
                "id": "provider-key-present",
                "kind": "environment_presence",
                "environment_name": "VALIDATOR_PROVIDER_KEY",
                "expected_present": True,
            }
        )
        self.fixture.write_inputs()
        environment = os.environ.copy()
        environment["VALIDATOR_PROVIDER_KEY"] = "ENVIRONMENT_VALUE_MUST_NOT_APPEAR"
        process, result = self.fixture.result(env=environment)
        self.assertDecision(process, result, exit_code=0, decision="current")
        self.assertNotIn("ENVIRONMENT_VALUE_MUST_NOT_APPEAR", process.stdout)

    def test_executable_and_path_prerequisites_are_current(self) -> None:
        executable = self.fixture.bin / "fixture-tool"
        executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        executable.chmod(0o755)
        self.fixture.record["prerequisites"].extend(
            [
                {
                    "id": "fixture-executable",
                    "kind": "executable",
                    "executable_name": "fixture-tool",
                    "expected_path": str(executable.resolve()),
                    "expected_sha256": sha256_file(executable),
                },
                {
                    "id": "fixture-path",
                    "kind": "path_exists",
                    "repository": "agent-core",
                    "path": "src/agent_core.py",
                    "expected_exists": True,
                },
            ]
        )
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=0, decision="current")

    def test_missing_executable_prerequisite_is_blocked(self) -> None:
        self.fixture.record["prerequisites"].append(
            {
                "id": "missing-executable",
                "kind": "executable",
                "executable_name": "validator-command-that-does-not-exist",
                "expected_path": "/nonexistent/validator-command",
            }
        )
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_path_prerequisite_symlink_escape_is_invalid(self) -> None:
        external = self.fixture.base / "external-path.txt"
        external.write_text("external\n", encoding="utf-8")
        link = self.fixture.consumer / "escaped-path"
        link.symlink_to(external)
        self.fixture.record["prerequisites"].append(
            {
                "id": "escaped-path",
                "kind": "path_exists",
                "repository": "agent-core",
                "path": "escaped-path",
                "expected_exists": True,
            }
        )
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_nonzero_openspec_status_is_blocked(self) -> None:
        openspec = self.fixture.bin / "openspec"
        openspec.write_text("#!/bin/sh\nexit 9\n", encoding="utf-8")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_malformed_openspec_status_is_blocked(self) -> None:
        openspec = self.fixture.bin / "openspec"
        openspec.write_text("#!/bin/sh\nprintf 'not-json'\n", encoding="utf-8")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_default_run_has_no_repository_side_effects(self) -> None:
        before = {
            path: (
                git(path, "rev-parse", "HEAD").stdout,
                git(
                    path, "status", "--porcelain=v1", "-z", "--untracked-files=all"
                ).stdout,
            )
            for path in (self.fixture.store, self.fixture.tdt, self.fixture.consumer)
        }
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=0, decision="current")
        after = {
            path: (
                git(path, "rev-parse", "HEAD").stdout,
                git(
                    path, "status", "--porcelain=v1", "-z", "--untracked-files=all"
                ).stdout,
            )
            for path in (self.fixture.store, self.fixture.tdt, self.fixture.consumer)
        }
        self.assertEqual(before, after)

    def test_selected_output_is_atomic_contained_and_self_excluded(self) -> None:
        output = (
            self.fixture.store
            / "openspec"
            / "changes"
            / CHANGE
            / "evidence"
            / "results"
            / "current.json"
        )
        first, result = self.fixture.result(output=output)
        self.assertDecision(first, result, exit_code=0, decision="current")
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), result)
        second, second_result = self.fixture.result(output=output)
        self.assertDecision(second, second_result, exit_code=0, decision="current")
        self.assertEqual(first.stdout, second.stdout)

    def test_output_outside_evidence_results_is_invalid_and_not_written(self) -> None:
        output = self.fixture.base / "outside.json"
        process, result = self.fixture.result(output=output)
        self.assertDecision(process, result, exit_code=4, decision="invalid")
        self.assertFalse(output.exists())

    def test_symlinked_results_root_is_invalid_and_never_written(self) -> None:
        external = self.fixture.base / "external-results"
        external.mkdir()
        results_root = (
            self.fixture.store
            / "openspec"
            / "changes"
            / CHANGE
            / "evidence"
            / "results"
        )
        results_root.parent.mkdir(parents=True, exist_ok=True)
        results_root.symlink_to(external, target_is_directory=True)
        output = results_root / "escape.json"
        process, result = self.fixture.result(output=output)
        self.assertDecision(process, result, exit_code=4, decision="invalid")
        self.assertFalse((external / "escape.json").exists())

    def test_output_prefix_collision_is_not_self_excluded(self) -> None:
        output = (
            self.fixture.store
            / "openspec"
            / "changes"
            / CHANGE
            / "evidence"
            / "results"
            / "current.json"
        )
        output.parent.mkdir(parents=True)
        backup = output.with_name("current.json.backup")
        backup.write_text("unrelated\n", encoding="utf-8")
        process, result = self.fixture.result(output=output)
        self.assertDecision(process, result, exit_code=2, decision="stale")
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), result)
        self.assertEqual(backup.read_text(encoding="utf-8"), "unrelated\n")

    def test_observed_at_is_metadata_only(self) -> None:
        plain, plain_result = self.fixture.result()
        stamped, stamped_result = self.fixture.result(
            observed_at="2026-08-13T12:00:00Z"
        )
        self.assertDecision(plain, plain_result, exit_code=0, decision="current")
        self.assertDecision(stamped, stamped_result, exit_code=0, decision="current")
        self.assertEqual(
            plain_result["comparison_digest"], stamped_result["comparison_digest"]
        )
        self.assertEqual(stamped_result["observed_at"], "2026-08-13T12:00:00Z")

    def test_status_artifact_set_mismatch_is_invalid(self) -> None:
        self.fixture.status["artifactPaths"]["specs"]["existingOutputPaths"] = []
        self.fixture.write_inputs()
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_schema_drift_is_stale(self) -> None:
        with self.fixture.schema.open("a", encoding="utf-8") as stream:
            stream.write("\n")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")

    def test_live_gate_rejects_deterministic_record(self) -> None:
        process, result = self.fixture.result("live_launch")
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_live_row_requires_live_payload(self) -> None:
        self.fixture.record["record_id"] = "ai-review-live"
        self.fixture.record["record_kind"] = "live_row"
        self.fixture.write_inputs()
        process, result = self.fixture.result("live_launch")
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_live_execution_is_required_for_evidence_reuse(self) -> None:
        self.fixture.make_live_record()
        process, result = self.fixture.result("evidence_reuse")
        self.assertDecision(process, result, exit_code=4, decision="invalid")

    def test_passed_live_execution_is_current_for_evidence_reuse(self) -> None:
        self.fixture.make_live_record(include_execution=True)
        process, result = self.fixture.result("evidence_reuse")
        self.assertDecision(process, result, exit_code=0, decision="current")

    def test_failed_nested_live_result_blocks_evidence_reuse(self) -> None:
        self.fixture.make_live_record(include_execution=True)
        execution = self.fixture.record["live"]["execution"]
        execution["nested_outcome"]["provider_error"] = True
        execution["nested_outcome"]["status"] = "failed"
        execution["row_status"] = "failed"
        self.fixture.write_inputs()
        process, result = self.fixture.result("evidence_reuse")
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_missing_live_authorization_is_blocked(self) -> None:
        self.fixture.make_live_record()
        self.fixture.repository_map["attestations"] = {}
        self.fixture.write_inputs()
        process, result = self.fixture.result("live_authorization")
        self.assertDecision(process, result, exit_code=3, decision="blocked")

    def test_branch_drift_is_stale(self) -> None:
        git(self.fixture.consumer, "switch", "-c", "other-branch")
        process, result = self.fixture.result()
        self.assertDecision(process, result, exit_code=2, decision="stale")

    def test_malformed_schema_is_canonical_invalid_without_echoing_input(self) -> None:
        malformed_schema = self.fixture.inputs / "malformed-schema.json"
        malformed_schema.write_text(
            '{"$defs":{"leak":"SCHEMA_CANARY_MUST_NOT_APPEAR"}',
            encoding="utf-8",
        )
        process = run(
            [
                sys.executable,
                str(SCRIPT),
                "--record",
                str(self.fixture.record_path),
                "--schema",
                str(malformed_schema),
                "--gate",
                "handoff_acceptance",
                "--repository-map",
                str(self.fixture.map_path),
                "--openspec-status-json",
                str(self.fixture.status_path),
            ],
            cwd=self.fixture.store,
            check=False,
        )
        result = json.loads(process.stdout)
        self.assertDecision(process, result, exit_code=4, decision="invalid")
        self.assertNotIn("SCHEMA_CANARY_MUST_NOT_APPEAR", process.stdout)

    def test_malformed_cli_arguments_return_canonical_invalid_json(self) -> None:
        process = run(
            [
                sys.executable,
                str(SCRIPT),
                "--record",
                "CLI_ARGUMENT_CANARY_MUST_NOT_APPEAR",
            ],
            cwd=self.fixture.store,
            check=False,
        )
        result = json.loads(process.stdout)
        self.assertDecision(process, result, exit_code=4, decision="invalid")
        self.assertEqual(process.stderr, "")
        self.assertNotIn("CLI_ARGUMENT_CANARY_MUST_NOT_APPEAR", process.stdout)

    def test_subprocess_surface_is_one_guarded_local_runner(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")
        tree = ast.parse(source)
        parents: dict[ast.AST, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[child] = parent
        calls = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
            and node.func.attr == "run"
        ]
        self.assertEqual(len(calls), 1)
        current: ast.AST | None = calls[0]
        while current is not None and not isinstance(
            current, (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            current = parents.get(current)
        self.assertIsInstance(current, ast.FunctionDef)
        self.assertEqual(current.name, "run_local")

        forbidden_attributes = {
            "urlopen",
            "create_connection",
            "import_module",
            "exec_module",
        }
        used_attributes = {
            node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
        }
        self.assertTrue(forbidden_attributes.isdisjoint(used_attributes))

    def test_result_contains_no_temporary_output_files(self) -> None:
        output = (
            self.fixture.store
            / "openspec"
            / "changes"
            / CHANGE
            / "evidence"
            / "results"
            / "atomic.json"
        )
        process, result = self.fixture.result(output=output)
        self.assertDecision(process, result, exit_code=0, decision="current")
        leftovers = list(output.parent.glob(f".{output.name}.*"))
        self.assertEqual(leftovers, [])


if __name__ == "__main__":
    unittest.main()
