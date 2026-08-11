# Phase-1 Corrective Evidence Manifest

Change: standardize-agent-llm-environment-resolution-v2

Corrective capture: begun 2026-08-11T07:01:39Z; independently corrected
through 2026-08-11T07:44:00Z

Writer history: codex-luna produced the first corrective draft and was released
after an interrupted response; codex-sol is the sole current corrective writer.

Scope: tasks 1.1-1.4 evidence only. This manifest is credential-safe and
contains no secret values, dotenv contents, remote URLs, provider tokens, or
live TDT_HOME data.

## 0. Incident preservation and current planning state

The corrective assignment requires preserving the incident commit and the
existing task reversion. Both were verified before editing this file:

~~~
git rev-parse HEAD
80d6a0404e69bb30364ba63dd38090adb6ee36c7

git status --porcelain=v1 -uall -- openspec/changes/standardize-agent-llm-environment-resolution-v2/tasks.md
 M openspec/changes/standardize-agent-llm-environment-resolution-v2/tasks.md

git diff -- openspec/changes/standardize-agent-llm-environment-resolution-v2/tasks.md
~~~

The task diff contains only the authorized reversion of tasks 1.1, 1.2, 1.3,
and 1.4 from [x] to [ ]. No task is checked by this correction. The incident
HEAD, branch, and task reversion are preserved after this manifest edit; no
stage, commit, reset, amend, or revert operation is authorized or performed.

Current OpenSpec identity:

| Field | Current value |
|---|---|
| Planning root | /Users/androidteam/Developer/.worktrees/openspec-llm-env-v2 |
| Change | standardize-agent-llm-environment-resolution-v2 |
| Branch | openspec/standardize-agent-llm-environment-resolution-v2 |
| HEAD | 80d6a0404e69bb30364ba63dd38090adb6ee36c7 |
| Apply progress | 0/79; tasks 1.1-1.4 unchecked |
| Planning state | ready; planning artifacts structurally complete |
| Pre-correction status fingerprint | eec0e2ade337810287f6f80ab8b2da83adc63d001e0f453dcbc55c3911d59fc4 |

The pre-correction fingerprint above was captured before this tracked manifest
was edited, using the same command used for
every repository:

~~~bash
git status --porcelain=v1 -uall | shasum -a 256
~~~

The command hashes the exact UTF-8 porcelain-v1 -uall byte stream, including
its terminating newline when non-empty. A clean tree therefore hashes the
empty stream as e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

The current OpenSpec dirty inventory is this modified manifest, the modified
tasks.md reversion, plus the
pre-existing untracked v2 artifact tree (.openspec.yaml, README.md, design.md,
proposal.md, and the nine specs/*/spec.md files). The manifest itself is
tracked by the incident commit and is the only file changed by this corrective
edit. The independently reviewed pre-commit full-untracked porcelain fingerprint is
`3eb6b0e324f6d796df4ba3de504e113102fc6fdf5183e2c62ff4c34a3e889734`.
The fingerprint hashes path/status records rather than file content, so recording
it here does not change the stream while the same dirty-path set is preserved.

## 1. Exact repository identity and ownership inventory

All repository identity rows were captured with this command, run from each
listed root:

~~~bash
git rev-parse --show-toplevel
git rev-parse HEAD
git branch --show-current
git config user.name
git config user.email
git status --porcelain=v1 -uall
git status --porcelain=v1 -uall | shasum -a 256
~~~

The repository-local Git identity was vinhlk2 <vinhlk2@ghtk.co> for every
implementation repository and the OpenSpec worktree. This identity is recorded
for evidence only; no commit is being made.

### Frozen implementation bases

These are the v2 implementation bases against which the original Phase-1
baseline was intended to be captured:

| Repository | Worktree | Branch | Frozen HEAD | Frozen status interpretation |
|---|---|---|---|---|
| tdt-core | /Users/androidteam/Developer/.worktrees/llm-env-v2/tdt-core | work/llm-env-v2-tdt-core | 135268d18628b9c774b2303c37aa877a21def29c | Source base; later tdt implementation edits are separated in §2 |
| agent-core | /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core | work/llm-env-v2-agent-core | e5fb49d18a2c8b3462b41626d088e766c8563b67 | Clean |
| agent-docs-sync | /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-docs-sync | work/llm-env-v2-agent-docs-sync | e0ba6000476c724de748c64fced1161a323cb5ed | Clean |
| agent-harness | /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness | work/llm-env-v2-agent-harness | f0ce05643a17667353f3e9c6e8536a54392b9fe4 | Clean |
| ai-harness-skills | /Users/androidteam/Developer/.worktrees/llm-env-v2/ai-harness-skills | work/llm-env-v2-ai-harness | e7e1b2a94de2806175306d67d76ba8ce0908469a | Clean |
| ai-review | /Users/androidteam/Developer/.worktrees/llm-env-v2/ai-review | work/llm-env-v2-ai-review | a5195409a124830607e92bc4bd8d16a4d068d9b5 | Clean; supported dependency is missing |

The clean implementation worktrees all produced the same empty-status hash:
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.

### Timestamped implementation status

The following status was captured after the tdt-core writer's in-progress
implementation probes and is intentionally separate from the frozen bases:

| Repository | Current HEAD | Current dirty paths | Current fingerprint |
|---|---|---|---|
| tdt-core handoff snapshot at 2026-08-11T07:30:35Z | 135268d18628b9c774b2303c37aa877a21def29c | src/tdt_core/__init__.py; src/tdt_core/agent_profile.py; src/tdt_core/config_loader.py; src/tdt_core/config_models.py; src/tdt_core/data/environment-key-registry.json; src/tdt_core/env.py; src/tdt_core/fs_kernel.py; src/tdt_core/paths.py; tests/test_agent_config.py; tests/test_llm_profile_v2.py | c8fc927333ff89e3192be8fe2289049008875344ddc171d742732f44e4a7594d |
| agent-core | e5fb49d18a2c8b3462b41626d088e766c8563b67 | none | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| agent-docs-sync | e0ba6000476c724de748c64fced1161a323cb5ed | none | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| agent-harness | f0ce05643a17667353f3e9c6e8536a54392b9fe4 | none | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| ai-harness-skills | e7e1b2a94de2806175306d67d76ba8ce0908469a | none | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| ai-review | a5195409a124830607e92bc4bd8d16a4d068d9b5 | none | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

The tdt-core row is a timestamped handoff, not a claim that an actively edited
tree remains current. Goose remains its sole writer. Agent-core, docs-sync, agent-harness,
ai-harness-skills, and ai-review remain application-editing-paused. The former
opencode-gd-1 harness assignment is released; harness currently has no writer.

### Imported module paths and OpenSpec executable identity

Each supported import was checked from its own worktree with its own uv
environment. The retained results below are path evidence; task 1.1 remains
open because ai-review cannot be installed from the six-worktree dependency set.

Results and exit codes:

| Repository | Command result | Exit |
|---|---|---:|
| tdt-core | /Users/androidteam/Developer/.worktrees/llm-env-v2/tdt-core/src/tdt_core/__init__.py | 0 |
| agent-core | /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src/agent_core/__init__.py | 0 |
| agent-docs-sync | /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-docs-sync/src/agent_docs_sync/__init__.py | 0 |
| agent-harness | /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness/src/agent_harness/__init__.py | 0 |
| ai-harness-skills (package ai_harness) | /Users/androidteam/Developer/.worktrees/llm-env-v2/ai-harness-skills/src/ai_harness/__init__.py | 0 |
| ai-review | uv could not determine the installation plan: Distribution not found at file:///Users/androidteam/Developer/.worktrees/llm-env-v2/code-daily-scan | 2 |
| OpenSpec CLI (cwd: OpenSpec worktree) | `/opt/homebrew/bin/openspec`; version `1.8.0` | 0 |

The ai-review row is a prerequisite-aware blocker, not an import success. No
editable dependency was created or substituted.

### GitNexus and Graphify freshness limitations

Fresh knowledge-tool results were not claimed:

| Tool | Exact evidence | Classification | Action |
|---|---|---|---|
| GitNexus | the corrective writer's `gitnexus status` exited 127; earlier direct audits retained stale indexed/current SHA mismatches for the core Python repositories | unavailable in this shell and known stale where previously observed; ai-harness-skills, ai-review, and OpenSpec were not freshly proven | no refresh, delete, or overwrite |
| Graphify | generated outputs exist in default checkouts, but no output is bound to all seven exact worktree HEAD/fingerprint pairs | present contextual data only; per-root freshness is unresolved | no refresh or generated-state mutation |

The existing generated surfaces were treated as contextual only. Direct source
inspection and bounded tests are the declared fallback evidence.

## 2. Frozen pre-implementation evidence versus current tdt-core state

### Frozen RED baseline for task 1.3

The required tdt-core RED was captured before Goose's source implementation
edits. The retained exact command was:

~~~bash
UV_CACHE_DIR=/private/tmp/uv-cache-llm-v2-red
PYTHONDONTWRITEBYTECODE=1
uv run --offline --frozen pytest -p no:cacheprovider tests/test_llm_profile_v2.py -q
~~~

Captured result at the pre-implementation snapshot:

~~~text
9 failed, 0 passed, exit 1
~~~

The failures were expected missing-public-API failures, including missing
CredentialResolver, load_config_mapping, load_agent_overlay, the profile
module, and the load_tdt_env(env_file=...) signature. This is the Phase-2 RED
evidence; it is not replaced by a later in-progress result.

### Timestamped tdt-core implementation snapshot

At an earlier dirty implementation snapshot, the same focused command returned:

~~~text
15 passed, 0 failed, exit 0
~~~

This is historical implementation-progress evidence only. It does not mark
tasks 2.1-2.13 or 6.1 complete and does not alter the frozen Phase-1 RED
baseline. A later timestamped dirty-path snapshot and fingerprint are recorded in
§1.

### Supplemental package-suite baseline commands and results

The consumer rows below are retained historical probes. They use the assigned
consumer sources but `/Users/androidteam/Developer/tdt-core/src`, the
source-clean default tdt-core checkout at the same frozen base HEAD. They are not
assigned-tdt-worktree proofs and do not mark implementation tasks.

| Repository | Exact command/result | Exit | Interpretation |
|---|---|---:|---|
| tdt-core | Focused RED command in §2: retained pre-implementation 9 failed; an earlier dirty snapshot separately passed 15 tests | 1 frozen RED / 0 earlier focused | Full tdt suite is not used as a frozen baseline while Goose's worktree is dirty |
| agent-core | PYTHONPATH=/Users/androidteam/Developer/tdt-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src PYTHONDONTWRITEBYTECODE=1 /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/.venv/bin/pytest -q -p no:cacheprovider; 746 collected, 726 passed, 20 skipped, 0 failed | 0 | Skips are missing optional source/Docker/gitleaks fixtures; no application changes |
| agent-docs-sync | PYTHONPATH=/Users/androidteam/Developer/tdt-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-docs-sync/src PYTHONDONTWRITEBYTECODE=1 /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-docs-sync/.venv/bin/pytest -q -p no:cacheprovider; 245 collected, 241 passed, 3 failed, 1 skipped, 4 warnings | 1 | Three cross-process lifecycle tests timed out at their 30-second join; this is not a v2 task pass |
| agent-harness | PYTHONPATH=/Users/androidteam/Developer/tdt-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness/src PYTHONDONTWRITEBYTECODE=1 /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness/.venv/bin/pytest -q -p no:cacheprovider; 332 collected, 325 passed, 1 failed, 6 skipped | 1 | test_default_fail_fast_contract_in_separate_process raised TimeoutExpired after 15 seconds; six Docker/gitleaks-dependent tests skipped |
| ai-harness-skills | PYTHONPATH=/Users/androidteam/Developer/tdt-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/ai-harness-skills/src PYTHONDONTWRITEBYTECODE=1 /Users/androidteam/Developer/.worktrees/llm-env-v2/ai-harness-skills/.venv/bin/pytest -q -p no:cacheprovider; 584 collected, 571 passed, 9 failed, 4 skipped | 3 | Nine existing contract failures; pytest coverage teardown raised coverage.exceptions.DataError because its SQLite data file could not be opened |
| ai-review | UV_CACHE_DIR=/private/tmp/uv-cache-llm-v2-import-ai-review PYTHONDONTWRITEBYTECODE=1 uv run --offline --frozen python -c 'import ai_review; print(ai_review.__file__)'; dependency resolution failed because code-daily-scan is absent | 2 | Prerequisite-aware blocked; no suite claim |

The exact package commands and exit codes above are retained even when the
result is not green. A green OpenSpec structure check does not convert these
runtime or prerequisite failures into passes.

## 3. Required task-1.3 defect probes

Each probe uses only synthetic model IDs and disposable /private/tmp data. No
live TDT files or credentials are read or changed.

Retained command provenance: probes 2, 3, and 4 were run from their assigned
agent-docs-sync or agent-harness worktrees through `uv run`; their original
one-line records omitted the cwd, which is an evidence limitation. Probe 1 uses
absolute source and interpreter paths but launches the default agent-core
virtual environment; its assigned agent-core source and the source-clean default
tdt-core source were at the recorded frozen HEADs. Probes 5 and 6 below are the
replacement fully isolated commands and include their cwd explicitly. Task 1.3
remains unchecked pending independent acceptance of these provenance limits.

### Probe 1 — agent-core environment precedence

Exact frozen-source command:

~~~bash
PYTHONPATH=/Users/androidteam/Developer/tdt-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src PYTHONDONTWRITEBYTECODE=1 /Users/androidteam/Developer/agent-core/.venv/bin/python -c 'exec("import os,tempfile\\nfrom pathlib import Path\\nfrom agent_core.foundation.settings import load_settings\\nfrom tdt_core.config_loader import load_agent_config, reset_agent_config_cache\\nfor k in (\\"MODEL_PRIMARY\\",\\"MODEL_FALLBACK\\",\\"AGENT_NAME\\"):\\n    os.environ.pop(k,None)\\nwith tempfile.TemporaryDirectory(dir=\\"/private/tmp\\") as d:\\n    root=Path(d); (root/\\"agents\\").mkdir()\\n    (root/\\"config.yaml\\").write_text(\\"agent:\\n  name: agent-core\\nmodel:\\n  primary: openai-chat:global\\n\\")\\n    (root/\\"agents\\"/\\"agent-core.yaml\\").write_text(\\"model:\\n  primary: openai-chat:agent\\n  fallback: [openai-responses:fallback]\\n\\")\\n    os.environ[\\"TDT_HOME\\"]=str(root); os.environ[\\"MODEL_PRIMARY\\"]=\\"openai-chat:env\\"\\n    reset_agent_config_cache(); settings=load_settings(); agent=load_agent_config(\\"agent-core\\")\\n    print(\\"settings.model.primary\\",settings.model.primary); print(\\"agent_config.model.primary\\",agent[\\"model\\"][\\"primary\\"]); print(\\"effective_cli_expression\\",agent[\\"model\\"][\\"primary\\"] or settings.model.primary); print(\\"expected\\",settings.model.primary)")'
~~~

Observed, exit 0:

~~~text
settings.model.primary openai-chat:env
agent_config.model.primary openai-chat:agent
effective_cli_expression openai-chat:agent
expected openai-chat:env
~~~

Expected behavior is effective openai-chat:env; the current CLI expression
selects agent YAML. The direct construction defect is at
agent-core/src/agent_core/cli/utils.py:155-169 and the SDK equivalent is at
agent-core/src/agent_core/sdk/agents.py:140-162. The fixture command above is
the exact probe body used; only its disposable directory is generated at run
time.

### Probe 2 — docs-sync projection disagreement

Exact command:

~~~bash
UV_CACHE_DIR=/private/tmp/uv-cache-llm-v2-probe-docs-projection PYTHONDONTWRITEBYTECODE=1 uv run --offline --frozen python -c 'exec("import os,tempfile\\nfrom pathlib import Path\\nfrom agent_docs_sync.config import load_config\\nfrom tdt_core.config_loader import reset_agent_config_cache\\nfor k in (\\"MODEL_PRIMARY\\",\\"MODEL_FALLBACK\\",\\"DOCS_SYNC_MODEL\\"):\\n    os.environ.pop(k,None)\\nwith tempfile.TemporaryDirectory() as d:\\n    root=Path(d); (root/\\"agents\\").mkdir(); (root/\\"config.yaml\\").write_text(\\"\\")\\n    (root/\\"agents\\"/\\"agent-docs-sync.yaml\\").write_text(\\"model:\\n  primary: openai-chat:yaml-model\\n\\")\\n    os.environ[\\"TDT_HOME\\"]=str(root); os.environ[\\"DOCS_SYNC_MODEL\\"]=\\"anthropic:env\\"\\n    reset_agent_config_cache(); c=load_config(root)\\n    print(\\"shortcut\\",c.model); print(\\"settings.primary\\",c.settings.model.primary); print(\\"expected_same_effective_profile\\",c.model==c.settings.model.primary)")'
~~~

Observed, exit 0:

~~~text
shortcut anthropic:env
settings.primary anthropic:Advance
expected_same_effective_profile False
~~~

Expected behavior is one effective profile shared by shortcut, settings,
generation, and diagnostics. The current projections are at
agent-docs-sync/src/agent_docs_sync/config.py:109-117; generation separately
loads the agent mapping at agent-docs-sync/src/agent_docs_sync/agents/generation.py:64-100.

### Probe 3 — harness production model propagation

Exact command:

~~~bash
UV_CACHE_DIR=/private/tmp/uv-cache-llm-v2-probe-harness-model PYTHONDONTWRITEBYTECODE=1 uv run --offline --frozen python -c 'exec("from tempfile import TemporaryDirectory\\nfrom agent_core.sdk.config import ConsumerRuntimeProfile\\nfrom agent_harness.config import AuthorityConfig,HarnessConfig\\nfrom agent_harness.models.artifacts import Stage\\nfrom agent_harness.services import HarnessServices\\nwith TemporaryDirectory() as d:\\n    c=HarnessConfig(runtime=ConsumerRuntimeProfile(model=\\"openai-chat:fixture\\"), authority=AuthorityConfig(artifact_root=d)); s=HarnessServices.production_services(c)\\n    print(\\"config.model\\",c.model); print(\\"services.model\\",s.model); print(\\"stage.model\\",s.for_stage(Stage.CONTEXT).model); print(\\"expected_equal\\",s.model==c.model)")'
~~~

Observed, exit 0:

~~~text
config.model openai-chat:fixture
services.model None
stage.model None
expected_equal False
~~~

Expected production_services().model == config.model and every agent-backed
stage to receive the same value. The omission is visible at
agent-harness/src/agent_harness/services.py:117-143, where runtime=config.runtime
is passed but model=config.model is not.

### Probe 4 — harness explicit-config error masking

Exact command:

~~~bash
UV_CACHE_DIR=/private/tmp/uv-cache-llm-v2-probe-harness-error PYTHONDONTWRITEBYTECODE=1 uv run --offline --frozen python -c 'exec("import os\\nfrom pathlib import Path\\nfrom tempfile import TemporaryDirectory\\nimport agent_harness.config as module\\nfrom agent_harness.config import HarnessConfig\\nmodule.load_tdt_env=lambda: None\\nwith TemporaryDirectory() as d:\\n    os.environ[\\"TDT_HOME\\"]=d; p=Path(d)/\\"malformed.yaml\\"; p.write_text(\\"harness:\\n  runtime: [\\n\\")\\n    c=HarnessConfig.load(config_path=p); print(\\"returned_default_model\\",repr(c.model)); print(\\"expected_fail_closed\\",False)")'
~~~

Observed, exit 0:

~~~text
returned_default_model 'anthropic:Advance'
expected_fail_closed False
~~~

Expected malformed explicit configuration to fail closed with an actionable
error. _load_yaml_section catches the parse failure and returns an empty
mapping; the call path is agent-harness/src/agent_harness/config.py:180-183.

### Probe 5 — agent-core load_settings(env_file=...) ignored

Working directory:

~~~text
/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core
~~~

Credential-safe exact command:

~~~bash
env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/androidteam/Developer/tdt-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/.venv/bin/python -c 'exec("import os,tempfile\nfrom pathlib import Path\nfrom agent_core.foundation.settings import load_settings\nwith tempfile.TemporaryDirectory(dir=\"/private/tmp\") as d:\n    root=Path(d)\n    config=root/\"config.yaml\"\n    selected=root/\"selected.env\"\n    config.write_text(\"model:\\n  primary: anthropic:Advance\\n\", encoding=\"utf-8\")\n    selected.write_text(\"MODEL_PRIMARY=openai-chat:fable-5\\n\", encoding=\"utf-8\")\n    os.environ[\"TDT_HOME\"]=str(root)\n    settings=load_settings(config_path=config, env_file=selected)\n    print(\"requested_env_file\", selected.name)\n    print(\"resolved_primary\", settings.model.primary)\n    print(\"expected_primary\", \"openai-chat:fable-5\")\n    print(\"explicit_env_file_honored\", settings.model.primary == \"openai-chat:fable-5\")")'
~~~

Observed, exit 0:

~~~text
requested_env_file selected.env
resolved_primary anthropic:Advance
expected_primary openai-chat:fable-5
explicit_env_file_honored False
~~~

Expected the selected file to control the environment identity. The current
hardcoded TDT_HOME/.env construction is at
agent-core/src/agent_core/foundation/settings.py:408-447. This replacement probe
starts with `env -i`, sets `TDT_HOME` only to a disposable directory, and reads
no operator TDT configuration. The source-clean default tdt-core checkout is at
the same frozen base HEAD but is not the assigned dirty implementation worktree.

### Probe 6 — literal default harness artifact-root expansion

Working directory:

~~~text
/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness
~~~

Environment-isolated exact command:

~~~bash
env -i PATH=/usr/bin:/bin HOME=/private/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/androidteam/Developer/tdt-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src:/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness/src /Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness/.venv/bin/python -c 'from agent_harness.config import HarnessConfig; config=HarnessConfig(); value=config.authority.artifact_root; print("tdt_home_present", False); print("artifact_root", repr(value)); print("contains_literal_placeholder", "$TDT_HOME" in value)'
~~~

Observed, exit 0:

~~~text
tdt_home_present False
artifact_root '$TDT_HOME/agent-harness/artifacts'
contains_literal_placeholder True
~~~

Expected the default root to be derived from the canonical root object and
validated for containment before ArtifactStore construction. The literal
default is at agent-harness/src/agent_harness/config.py:77-79. The process has
an empty environment, so neither `TDT_HOME` nor a harness override is present.

The tdt API RED, ai-harness drift, and missing code-daily-scan dependency are
retained in §2 and §3 as separate evidence; they do not substitute for these
six required task-1.3 probes.

## 4. Redacted model/environment registry inventory

This is a redacted working inventory of model, configuration,
credential-reference, consumer, and compatibility surfaces found across the six
participating repositories. It intentionally remains an incomplete evidence
ledger: task 1.4 stays unchecked until every row is tied to retained searched
roots/patterns and exact source locations.
Values are never recorded. Canonical target is the v2 registry disposition;
Current precedence records the observed legacy path when it differs from the
required target.

| Key or alias | Owner | Type | Secret class | Consumers | Current precedence | Canonical target | Alias status |
|---|---|---|---|---|---|---|---|
| TDT_HOME | tdt-core | absolute root path | non-secret path | all six | process environment/default ~/.tdt | canonical root identity | canonical |
| TDT_ENV_FILE / env_file | tdt-core | explicit dotenv path | non-secret path | tdt-core and consumers | partially observed; agent-core parameter ignored | explicit env-file identity | env_file is legacy API requiring correction |
| MODEL_PRIMARY | tdt-core registry | canonical provider:model string | non-secret | agent-core, docs-sync, harness, CLI projection | environment intended above YAML; consumers diverge | shared-model environment layer | canonical |
| MODEL | tdt-core/agent-core compatibility | canonical provider:model string | non-secret | shared model consumers | compatibility alias for MODEL_PRIMARY; typed settings parity is unresolved | MODEL_PRIMARY | source-backed alias; status under review |
| MODEL_FALLBACK | tdt-core registry | ordered canonical ID list | non-secret | agent-core, docs-sync, harness | environment/YAML merge differs by consumer | shared-model environment layer | canonical |
| MODEL_FALLBACKS | tdt-core/agent-core compatibility | ordered canonical ID list | non-secret | shared model consumers | compatibility alias for MODEL_FALLBACK | MODEL_FALLBACK | source-backed alias; status under review |
| MODEL_THINKING | tdt-core registry | enum/bool | non-secret | agent-core and consumers | environment over YAML in settings path | resolved behavior profile | canonical |
| MODEL_TEMPERATURE | tdt-core registry | bounded float | non-secret | agent-core and consumers | environment over YAML in settings path | resolved behavior profile | canonical |
| MODEL_MAX_TOKENS | tdt-core registry | bounded integer | non-secret | agent-core and consumers | environment over YAML in settings path | resolved behavior profile | canonical |
| MODEL_TOP_P | agent-core ModelSettings | bounded float | non-secret | agent-core and future direct consumers | agent-core settings environment path; absent from the current packaged tdt registry | registry decision unresolved | current agent-core field, not yet tdt-owned |
| MODEL_SERVICE_TIER | agent-core ModelSettings | enum | non-secret | agent-core and future direct consumers | agent-core settings environment path; absent from the current packaged tdt registry | registry decision unresolved | current agent-core field, not yet tdt-owned |
| MODEL_API_KEY_ENV | tdt-core registry | credential-reference name | secret reference only | provider construction | consumer/model-layer lookup | validated CredentialRef | legacy direct lookup |
| MODEL_API_KEY | tdt-core registry | credential value input | secret | agent-core legacy model layer | process environment and dotenv | process-local resolver only | legacy; never serialize |
| MODEL_BASE_URL | tdt-core registry | provider endpoint URL | potentially sensitive | agent-core legacy model layer | process environment/model mapping | provider route metadata | legacy generic key |
| ANTHROPIC_API_KEY | native provider boundary | credential value | secret | native Claude/Anthropic routes | native process environment | isolated resolver/native CLI auth | native secret; never copy |
| OPENAI_API_KEY | native provider boundary | credential value | secret | native OpenAI routes | native process environment | isolated resolver/native auth | native secret; never copy |
| AZURE_OPENAI_API_KEY | native CLI boundary | credential value | secret | Claude/Codex adapter capability sets | native process environment | native adapter auth only | native boundary |
| CODEX_API_KEY | native CLI boundary | credential value | secret | Codex adapter | native process environment | native adapter auth only | native boundary |
| TDT_MODEL_KEY | provider-specific registry entry | credential value | secret | agent-core tests/provider metadata | provider env reference | registered credential reference | test/provider-specific |
| DOCS_SYNC_MODEL | docs-sync owner through tdt-core registry | canonical provider:model string | non-secret | agent-docs-sync | consumer env above local config/TDT defaults | consumer-environment layer | canonical consumer key |
| DOCS_SYNC_FALLBACK | docs-sync | ordered canonical ID list | non-secret | agent-docs-sync | consumer environment above shared/YAML/defaults | resolved fallback profile | canonical; no short DOCS_* alias exists in frozen docs-sync source |
| DOCS_SYNC_THINKING | docs-sync | enum/bool | non-secret | agent-docs-sync | consumer environment above shared/YAML/defaults | resolved behavior profile | canonical; no short DOCS_* alias exists in frozen docs-sync source |
| DOCS_SYNC_TEMPERATURE | docs-sync | bounded float | non-secret | agent-docs-sync | consumer environment above shared/YAML/defaults | resolved behavior profile | canonical; no short DOCS_* alias exists in frozen docs-sync source |
| DOCS_SYNC_MAX_TOKENS | docs-sync | bounded integer | non-secret | agent-docs-sync | consumer environment above shared/YAML/defaults | resolved behavior profile | canonical; no short DOCS_* alias exists in frozen docs-sync source |
| DOCS_SYNC_MAX_ITERATIONS | docs-sync | integer | non-secret | agent-docs-sync | consumer env above YAML/default | resolved behavior profile | canonical |
| DOCS_SYNC_TIMEOUT_SECONDS | docs-sync | float | non-secret | agent-docs-sync | consumer env above YAML/default | resolved behavior profile | canonical |
| DOCS_SYNC_ALLOWED_DOC_ROOTS | docs-sync | bounded list | non-secret path policy | agent-docs-sync | consumer env above YAML/default | docs-sync domain projection | canonical |
| DOCS_SYNC_DURABLE_GENERATION | docs-sync | bool | non-secret | agent-docs-sync | consumer env above YAML/default | docs-sync domain projection | canonical |
| DOCS_SYNC_GENERATION_ENABLED | docs-sync | bool | non-secret | agent-docs-sync | consumer env above YAML/default | docs-sync domain projection | canonical |
| DOCS_SYNC_RESUME_ENABLED | docs-sync | bool | non-secret | agent-docs-sync | consumer env above YAML/default | docs-sync domain projection | canonical |
| DOCS_SYNC_APPROVAL_ACTORS | docs-sync | bounded identity list | non-secret identity metadata | agent-docs-sync | consumer env above YAML/default | docs-sync domain projection | canonical |
| HARNESS_MODEL | harness through tdt-core registry | canonical provider:model string | non-secret | agent-harness | consumer env above YAML/default, with explicit path divergence | harness runtime profile | canonical consumer key |
| HARNESS_MAX_ITERATIONS | harness | integer | non-secret | agent-harness | consumer env above YAML/default | harness runtime profile | canonical |
| HARNESS_TIMEOUT_SECONDS | harness | float | non-secret | agent-harness | consumer env above YAML/default | harness runtime profile | canonical |
| HARNESS_DURABLE | harness | bool | non-secret | agent-harness | consumer env above YAML/default | harness persistence projection | canonical |
| HARNESS_ARTIFACT_ROOT | harness | contained path | non-secret path | agent-harness | consumer env above YAML/default | tdt-root-derived contained path | canonical |
| HARNESS_PERSISTENCE_DURABLE | harness | bool | non-secret | agent-harness | legacy nested alias rejected by current code | migration error; no silent alias | rejected legacy alias |
| TDT_POSTGRES_URL | harness infrastructure | connection URL | potentially secret-bearing | agent-harness | process environment | infrastructure credential boundary | operational, not LLM |
| TDT_POSTGRES_TEST_URL | harness test infrastructure | connection URL | potentially secret-bearing | agent-harness tests | test environment only | prerequisite-aware test input | operational, not LLM |
| AI_HARNESS_LIVE_SMOKE | ai-harness-skills | bool gate | non-secret | ai-harness-skills | process environment | live CLI smoke prerequisite | canonical live-gate control |
| AI_HARNESS_LIVE_WORKFLOW_QUALITY | ai-harness-skills | bool gate | non-secret | ai-harness-skills | process environment | live workflow-quality prerequisite | canonical live-gate control |
| Claude/Codex auth allowlists | ai-harness-skills native adapters | allowlisted key names | secret references | Claude/Codex adapters | native CLI environment | native authentication only | no tdt credential copy |
| AI_REVIEW_ENABLE_KIMI / ENABLE_KIMI | ai-review | bool | non-secret | ai-review | modern key then legacy alias | registry-owned reviewer setting | ENABLE_KIMI legacy |
| AI_REVIEW_ENABLE_CLAUDE / ENABLE_CLAUDE | ai-review | bool | non-secret | ai-review | modern key then legacy alias | registry-owned reviewer setting | ENABLE_CLAUDE legacy |
| AI_REVIEW_ENABLE_CODEX / ENABLE_CODEX | ai-review | bool | non-secret | ai-review | modern key then legacy alias | registry-owned reviewer setting | ENABLE_CODEX legacy |
| AI_REVIEW_ENABLE_PI / ENABLE_PI | ai-review | bool | non-secret | ai-review | modern key then legacy alias | registry-owned reviewer setting | ENABLE_PI legacy |
| AI_REVIEW_ENABLE_CODESCAN / ENABLE_CODE_SCAN | ai-review | bool | non-secret | ai-review | modern key then legacy alias | registry-owned reviewer setting | ENABLE_CODE_SCAN legacy |
| AI_REVIEW_ENABLE_DUAL_MODE / ENABLE_DUAL_MODE | ai-review | bool | non-secret | ai-review | modern key then legacy alias | registry-owned reviewer setting | ENABLE_DUAL_MODE legacy |
| AI_REVIEW_INCLUDE_RAW_REVIEWS / INCLUDE_RAW_REVIEWS | ai-review | bool | non-secret | ai-review | modern key then legacy alias | registry-owned output setting | INCLUDE_RAW_REVIEWS legacy |
| AI_REVIEW_KIMI_MAX_STEPS / KIMI_MAX_STEPS | ai-review | integer | non-secret | ai-review | modern key then legacy alias | bounded reviewer limit | KIMI_MAX_STEPS legacy |
| AI_REVIEW_KIMI_TIMEOUT | ai-review | positive seconds | non-secret | ai-review | modern process environment | bounded reviewer timeout | canonical |
| AI_REVIEW_REVIEW_TIMEOUT / REVIEW_TIMEOUT | ai-review | positive seconds | non-secret | ai-review | modern key then legacy alias | bounded review timeout | REVIEW_TIMEOUT legacy |
| AI_REVIEW_WORKTREE_TIMEOUT / WORKTREE_TIMEOUT | ai-review | positive seconds | non-secret | ai-review | modern key then legacy alias | bounded worktree timeout | WORKTREE_TIMEOUT legacy |
| AI_REVIEW_LOCAL_REPO_PATHS / LOCAL_REPO_PATHS | ai-review | bounded path list | non-secret path | ai-review | modern key then legacy alias | bounded reviewer input | LOCAL_REPO_PATHS legacy |
| TDT_WORKSPACE_ROOT | ai-review | workspace path | non-secret path | ai-review | process environment/default | registry-owned workspace boundary | canonical infrastructure key |
| claude, codex, kimi, sonnet | CLI consumers | provider/model aliases | non-secret | ai-harness-skills, ai-review | localized/native alias lookup | non-secret CLI projection only | not valid direct Pydantic-AI IDs |

The canonical precedence target for all registered LLM fields is:

~~~text
explicit run override
  > consumer environment
  > shared model environment
  > agent YAML
  > global YAML
  > typed defaults
~~~

An environment value therefore outranks YAML. A present empty or invalid
higher-priority value fails closed unless the registry explicitly authorizes a
clearing operation. Direct provider IDs must be registered canonical
provider:model identifiers; claude, codex, kimi, and sonnet remain CLI/native
aliases and must not be routed through direct Pydantic-AI model construction.

### Explicit ecosystem boundary cases

| Repository/runtime | Classification | Correct boundary |
|---|---|---|
| prime-agent | excluded independent runtime | TypeScript/provider runtime with its own model registry and authentication store; no credential or model-registry substitution |
| claude-code-provider-adapter | excluded protocol/provider infrastructure | Provider protocol and upstream-key boundary; native authentication remains isolated |
| code-daily-scan | deterministic downstream smoke boundary | Import/config regression consumer of integrated agent-core/tdt-core; deterministic scoring remains non-LLM; its absence blocks ai-review installation/tests |

These are explicit boundary classifications, not claims that the runtimes are empty
or devoid of provider behavior.

## 5. Writer assignments, dedicated worktrees, and dependency gates

| Area | Current owner | State |
|---|---|---|
| Phase-1 ledger and this manifest | codex-sol | sole current corrective writer; tasks 1.1-1.4 remain unchecked |
| tdt-core tasks 2.1-2.13 and 6.1 | goose-luna | sole application writer; bounded corrections active at the timestamped dirty paths in §1 |
| agent-core tasks 3.1-3.9 | unassigned after codex-luna release | clean dedicated worktree; application edits blocked |
| agent-docs-sync | none currently active | paused at clean base |
| agent-harness | none currently active; opencode-gd-1 released | paused at clean base |
| ai-harness-skills and ai-review | grok-fable when foundation opens | paused at clean bases |
| legacy drafts, default store, live TDT_HOME | no writer authorized | untouched |

The six dedicated worktrees listed in §1 exist on separate `work/llm-env-v2-*`
branches. Assignment coverage is intentionally incomplete while agent-core,
docs-sync, and harness have no active writer; therefore task 1.2 remains
unchecked. The downstream dependency gate remains closed until Goose publishes
a verified tdt-core public interface, implementation SHA, and full required
evidence.

## 6. Validation and final correction status

The selected validation was independently run from the OpenSpec worktree:

~~~bash
openspec validate standardize-agent-llm-environment-resolution-v2 --strict --no-interactive
~~~

Result: exit 0, `Change 'standardize-agent-llm-environment-resolution-v2' is
valid`. `git diff --check` also exited 0. HEAD remains
`80d6a0404e69bb30364ba63dd38090adb6ee36c7`; apply progress is 0/79.

The correction-owned path is this manifest. The separately preserved existing
task correction remains dirty and contains only the reversion of 1.1-1.4:

~~~text
openspec/changes/standardize-agent-llm-environment-resolution-v2/EVIDENCE_MANIFEST.md
openspec/changes/standardize-agent-llm-environment-resolution-v2/tasks.md
~~~

No task checkbox is changed by this manifest correction. The independently
reviewed pre-commit full-untracked porcelain fingerprint was
`3eb6b0e324f6d796df4ba3de504e113102fc6fdf5183e2c62ff4c34a3e889734`.
No commit, stage,
reset, amend, revert, sync, archive, application edit, credentialed call, or
legacy-draft cleanup is part of Phase 1.
