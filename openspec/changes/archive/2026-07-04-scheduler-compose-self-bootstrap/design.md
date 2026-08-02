# scheduler-compose-self-bootstrap — Design

> **Companion to:** `proposal.md` in this directory
> **Status:** Draft
> **Goal:** Specify the container-side architecture for self-bootstrapping all `~/.tdt/schedules/<repo>.yaml` manifests on startup, replacing the host-side `scripts/deploy.sh` pattern.

---

## Goals & Non-Goals

### Goals

1. The Docker scheduler service, started with **only** `compose.yaml`, `Dockerfile`, and `entrypoint.sh`, produces a working scheduler with the full expected manifest set.
2. Adding a new repo's manifests requires **zero changes** to `tdt_core`, `agent_core.scheduler_setup`, or any other "central" file. It requires only:
   - A generator function in `agent-core/deployments/scheduler/generators/<repo>.py`
   - A mount of the repo source in `compose.yaml`
3. Hot-reload via the `.reload` sentinel continues to work — the entrypoint touches it after all manifests are written, so the scheduler applies the full set in one shot, not three staggered reloads.
4. Generator errors **fail the entrypoint fast** — operators see broken manifests in logs, not silently-missing schedules.
5. The implementation is **deterministic** — running `docker compose up` twice with the same inputs produces byte-identical manifests (timestamps in `.reload` excluded).

### Non-Goals

- **No cloud-native / k8s deployment story.** This change is local-Docker-only. Production parity comes later.
- **No migration of the existing jira-side handwritten manifest to the new framework** — the existing `generate_jira_manifest.py` continues to work; it is refactored into the framework as one generator among N.
- **No changes to the YAML schema** or the loader logic.
- **No removal of legacy host-side scripts in a single release** — they are deprecated, not deleted. A follow-up change can remove them.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Host                                                                     │
│                                                                          │
│  ~/Developer/tdt/                                                        │
│  ├── compose.yaml           (mounts bind to /workspace/* below)          │
│  ├── agent-core/                                                           │
│  │   ├── deployments/scheduler/                                            │
│  │   │   ├── Dockerfile                (pinned python:3.14 + ripgrep)     │
│  │   │   ├── entrypoint.sh             (NEW: orchestrator)                 │
│  │   │   ├── generate_schedule_manifest.py                                 │
│  │   │   │   ├── generators/             (NEW: per-repo functions)          │
│  │   │   │   │   ├── __init__.py                                            │
│  │   │   │   │   ├── jira.py             (refactored from generate_jira_…)  │
│  │   │   │   │   ├── code_daily_scan.py (NEW)                              │
│  │   │   │   │   └── tdt_observability.py (NEW)                            │
│  │   │   │   └── __main__.py            (CLI wrapper, used by tests)       │
│  ├── code-daily-scan/                                                      │
│  │   └── scripts/deploy.sh           (REDUCED: only config-touch shim)    │
│  ├── tdt-observability/                                                    │
│  │   └── (no deploy script)           (NEW: no manual manifest either)    │
│  └── jira-daily-reports/                  (no change)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                  │ docker compose up --build
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Container (tdt-scheduler)                                                │
│                                                                          │
│  entrypoint.sh                                                           │
│  ├── chown /opt/scheduler/.venv                                          │
│  ├── mkdir -p /home/agent/.tdt/schedules                                  │
│  ├── for repo in jira code-daily-scan tdt-observability:                  │
│  │   └── uv run python3 /generate_schedule_manifest.py $repo \           │
│  │                                       /home/agent/.tdt/schedules/...   │
│  ├── touch /home/agent/.tds/schedules/.reload                             │
│  │   (atomic write via tmp + rename)                                      │
│  └── exec uv run tdt-scheduler serve                                      │
│                                                                          │
│  /workspace/                                                             │
│  ├── agent-core/src         (mounted from host)                           │
│  ├── tdt-core/              (mounted from host :ro)                       │
│  ├── jira-daily-reports/src (mounted from host :ro)                       │
│  ├── code-daily-scan/src    (mounted from host :ro)                       │
│  ├── tdt-observability/src  (mounted from host :ro)                       │
│  └── poems-mobile3-{android,ios} (mounted from host :rw)                  │
│                                                                          │
│  /home/agent/.tdt/  (mounted from host :rw)                               │
│  ├── .env                                                                  │
│  ├── code-daily-scan.yaml  ◀── source of cron/timezone for android/ios     │
│  ├── schedules/                                                            │
│  │   ├── .reload                                                           │
│  │   ├── jira-daily-reports.yaml  (generated)                              │
│  │   ├── code-daily-scan.yaml     (generated)                              │
│  │   └── tdt-observability.yaml   (generated)                              │
│  └── logs/scheduler-entrypoint.log                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Key Decisions

### Decision 1: Generators live in `agent-core/deployments/scheduler/generators/`

**Why not in each repo?** A generator's job is to emit `tdt-schedule/v1` YAML for the scheduler. The scheduler is the consumer. Putting generators in their respective repos would require importing `tdt_core` from those repos (already vendored) but also requires the scheduler to know how to load them generically — currently the scheduler only mounts specific paths. **Generators stay near the scheduler deployment. A repo's source tree provides the data (constants, configs); the generator function transforms it.**

**Rejected alternative:** A Python entry-point group `tdt_schedule_generators = {...}` declared in `pyproject.toml` of each repo. This requires every repo to know about and register with the entry-point group, plus the entry-point loader reads `sys.path` packages — fragile in a workspace where source is mounted directly without `pip install`.

**Rejected alternative:** A single mega-generator `generate_all.py` with inline calls for each repo. Hard to test in isolation; mixed concerns.

### Decision 2: Entry point invokes each generator explicitly

```bash
# entrypoint.sh
for repo in jira-daily-reports code-daily-scan tdt-observability; do
    uv run python3 /generate_schedule_manifest.py "$repo" \
        "/home/agent/.tdt/schedules/${repo}.yaml" \
        || { echo "manifest generation failed for $repo"; exit 1; }
done
```

**Why explicit list, not auto-discovery?** Auto-discovery (e.g., `pkgutil.iter_modules` of `generators/`) is seductive but ties the manifest order to filename ordering — fragile. The explicit list documents intent: "these three manifests exist, in this order, with this cascade."

**Rejected alternative:** YAML manifest-of-manifests declaring which generators exist. Adds a layer of indirection for no operational benefit.

### Decision 3: Atomic write + `.reload` touch happens **once, at the end**

```bash
# entrypoint.sh
for repo in jira-daily-reports code-daily-scan tdt-observability; do
    uv run python3 /generate_schedule_manifest.py "$repo" \
        "/home/agent/.tdt/schedules/${repo}.yaml.tmp"
    mv "/home/agent/.tdt/schedules/${repo}.yaml.tmp" \
       "/home/agent/.tdt/schedules/${repo}.yaml"
done
# All manifests stable → safe to reload
date -u +%FT%TZ > /home/agent/.tdt/schedules/.reload.tmp
mv /home/agent/.tdt/schedules/.reload.tmp /home/agent/.tdt/schedules/.reload
```

**Why one `.reload` at the end?** The scheduler polls `.reload` every 60s. Three `.reload` touches (one per generator) would cause up to **three hot-reload cycles**, each re-applying the schedule set. While DBOS upsert is idempotent, repeating three unnecessary reloads wastes startup time and pollutes logs with reload events. **One `.reload` = one re-registration cycle.**

**Rejected alternative:** No `.reload` touch from entrypoint; rely on the scheduler's first healthcheck cycle. This delays schedule activation by up to `start_period + 60s`.

### Decision 4: `code-daily-scan` generator reads host config, not source

`code-daily-scan` already has a per-platform config at `~/.tdt/code-daily-scan.yaml`. The generator must respect cron/timezone values from this config because operators tune them without rebuilding code. **The generator does NOT parse `code_daily_scan.config` AST — it imports and calls `code_daily_scan.config.load_config("android")` and `load_config("ios")` directly**, then projects to the manifest schema.

**Why direct import, not AST?** `code_daily_scan.config.load_config` is the canonical config loader — the source of truth that the daily-scan CLI itself uses. Importing guarantees we read the same values the CLI will use. AST parsing duplicates the parsing logic.

**Trade-off:** The generator runs inside the scheduler container, so `code_daily_scan.config` must be importable there. Verified: `compose.yaml:141-143` already mounts `code-daily-scan/src` (and `code-daily-scan/config`) into the container at `/workspace/code-daily-scan/src`. The `agent-core` venv does NOT need `code-daily-scan` installed — it's added to `PYTHONPATH` via the generator's `sys.path.insert`. The generator's `__main__` block handles this.

### Decision 5: `tdt-observability` generator reads constants from source, not from a sidecar config

Unlike `code-daily-scan`, `tdt-observability.retention` has no host-side config — its cron is hardcoded as `0 2 * * *` UTC in the runbook. The generator reads the cron constant **directly from the source module** via `inspect.getsource(tdt_observability.retention)` or a stable public constant.

**Decision: add a public constant `OBSERVABILITY_RETENTION_CRON` and `OBSERVABILITY_RETENTION_TZ` to `tdt_observability.retention`.** This makes the cron explicit and version-controlled in source rather than hand-written in runbook prose. The generator imports them.

**Why a constant, not `inspect.getsource`?** `inspect.getsource` reads source text and re-parses — duplicates the parsing, brittle on formatting changes. A public constant is the simplest contract.

**Trade-off:** This adds a small file change to `tdt-observability`. The `retention.py` module already imports `DuckDBStore` and has constants; adding two cron/tz constants is a 2-line change.

---

## Risks & Trade-offs

### Risk 1: Generator failures break scheduler startup

If `code_daily_scan.config.load_config()` fails (e.g., operator's `~/.tdt/code-daily-scan.yaml` is malformed), the entrypoint exits non-zero → the container `restart: unless-stopped` policy loops it indefinitely.

**Mitigation:**
1. Each generator wraps its body in `try / except / log` and **returns** the error (exit code 1) rather than crashing.
2. The entrypoint's `set -euo pipefail` propagates the exit code, but each generator is independent — a failed `code-daily-scan` manifest doesn't block `jira-daily-reports`.
3. Logging to `~/.tdt/logs/scheduler-entrypoint.log` (volume-mounted back to host) gives operators visibility.
4. The smoke test asserts: **no manifest** → container exits → healthcheck fails (because the `app` service sleep never starts) → operators see the failure within `start_period`.

**Trade-off accepted:** Better to fail loudly at startup than to silently skip a manifest and confuse operators when scans don't fire.

### Risk 2: Generator slow path delays DBOS registration

Each generator invocation takes ~2-3s (cold-start Python interpreter inside `uv run` per loop iteration). Three generators = ~6-9s added to startup, on top of `tdt-scheduler serve` itself.

**Mitigation:** Run all generators in a **single `uv run python3` invocation** rather than per-iteration forks. The new `generate_schedule_manifest.py` dispatches to per-repo generator functions inside one Python process.

```python
# generate_schedule_manifest.py — single entrypoint, forks per repo only when needed
if __name__ == "__main__":
    repos = sys.argv[1:-1]
    output_dir = Path(sys.argv[-1])
    for repo in repos:
        manifest = GENERATORS[repo]()  # cheap: in-process
        _write_atomic(output_dir / f"{repo}.yaml", manifest)
```

**Trade-off accepted:** Loss of per-repo failure isolation. If `jira` fails, the loop raises and `code-daily-scan` doesn't run. **Mitigated** by ordering: `jira` (most likely to succeed) first, with the others trailing. Documented in `entrypoint.sh`.

### Risk 3: Backward-compat break with existing manually-written manifests

Operators who manually wrote `~/.tdt/schedules/tdt-observability.yaml` will see it **rewritten** on container restart. If their hand-edit had different cron/timezone, they'll silently lose it.

**Mitigation:**
1. The generator logs `INFO manifest_overwrite: writing <path>` so operators see the change.
2. The smoke test asserts the **generated** content matches the expected canonical values — operators' surprise edits are caught at deploy time, not three weeks later.
3. **Backwards-compat clause:** if `/home/agent/.tdt/schedules/<repo>.yaml` exists AND mtime is older than container start AND the file is **NOT** parseable as `ScheduleManifest`, the generator logs `INFO preserving_unparseable_manifest: <path>` and **does NOT overwrite**. Operators can manually fix or delete the file.

**Trade-off accepted:** This adds a "preserve" branch that future operators may find surprising. Documented as a Phase 1 behavior; Phase 2 (next change) hard-overwrites to enforce canonical content.

### Risk 4: `ripgrep` install in Dockerfile adds image size

Adding `ripgrep` to `apt-get install` adds ~5-10 MB to the scheduler image.

**Mitigation:** Acceptable; `ripgrep` is industry-standard for code scanning. Image size impact is minor (current image is dominated by Python + uv + git + curl). Documented in `Dockerfile` rationale comment.

---

## Open follow-ups (next change candidates)

1. **Delete `code-daily-scan/scripts/deploy.sh` entirely** — once the heredoc is gone, the script becomes ~10 lines of `chmod` and `touch .reload`, which `agent-core` could subsume via a `code-daily-scan/scripts/touch-reload.sh`. Fold in next change.
2. **`webhook-receiver` and `ai-review` schedule manifests** are still in source tree (as part of their deploy.sh scripts) — they were removed from runtime on 2026-07-03 but the YAML fragments in those repos' `scripts/deploy.sh` are stale. Out of scope here.
3. **Source-of-truth cron/tz for `tdt-observability`** — once the constant is added to `tdt_observability.retention`, the documentation in `tdt-observability/README.md` should be updated to reference the constant rather than restate the cron. Out of scope here.
4. **CI integration of the compose-up smoke test** — needs a Linux agent with Docker Compose v2. Local-only for now.
