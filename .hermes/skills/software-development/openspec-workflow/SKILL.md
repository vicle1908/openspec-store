---
name: openspec-workflow
description: "Spec-driven change lifecycle: apply, validate, archive."
version: 1.4.0
platforms: [linux, macos]
metadata:
  hermes:
    tags: [openspec, spec-driven, workflow, architecture]
---

# OpenSpec Workflow

## Purpose
References: use the linked change-review, alignment, five-provider, delegated-review security, shared-provider rollout, `references/knowledge-tools-integration.md`, `references/phase-rollout-evidence.md`, `references/implementation-pitfalls.md`, `references/pydantic-settings-migration.md`, `references/workspace-refresh-pitfalls.md`, `references/program-evidence-reconciliation.md`, `references/final-implementation-evidence-gates.md`, `references/pre-archive-validation.md`, `references/archive-delta-and-shared-store-concurrency.md`, `references/compaction-loop-anti-pattern.md`, and `references/gateway-to-model-spec-update-pattern.md` guides.

## Workflow

### 1. Create or review a change

**BEFORE writing any artifacts:** Load `references/workspace-tooling-integration.md` for integration/tooling changes. Verify actual tool installation, agent wiring, MCP registration, and usage state. Do not assume tools are unwired just because they seem unused — check per-agent configs, mcp-router registrations, and actual output directories. Most integration proposals are 50-70% smaller after ground truth verification reveals what already works.

Create with `openspec new change <kebab-case-name> --description "Brief description"`. Author proposal, design, executable tasks, delta specs, and `.openspec.yaml`; include compatibility, rollout, and rollback where relevant.

**Investigation-driven spec enhancement:** When reviewing or updating an existing active change — especially integration changes involving running services, ports, or hardware-dependent config — investigate actual runtime state BEFORE trusting the evidence bundle. Evidence goes stale: processes crash, ports change, models get un/pulled. See `references/investigation-driven-spec-enhancement.md` for the full investigation pattern (runtime verification, root cause analysis, hardware-aware model selection, stale evidence detection). For agentmemory-specific troubleshooting (iii-config.yaml root cause, split-provider .env, dimension migration, **gateway config watcher revert**, **WebSocket degradation without crash**, **launchd persistence with absolute PATH pitfall**), see `references/agentmemory-integration-troubleshooting.md`.

**Broader cross-repo search BEFORE creating changes:** Before finalizing the repos list in `.openspec.yaml`, run `grep -r "from <provider_module>" --include="*.py" -l <workspace>` across ALL repos to find every consumer. Initial intuition often misses repos that use the provider indirectly (e.g. `jira-kanban-from-spreadsheet` uses `load_tdt_env()` via a backup CLI). Use gitnexus `impact` and graphify `path`/`query` for blast-radius analysis. Missing repos from scope is a CRITICAL finding that blocks implementation. See `references/cross-repo-blast-radius-search.md` for the full search pattern and common misses.

**Knowledge context gathering (after cross-repo search):** For non-minimal-path changes (multi-repo, code touches, documented services), query knowledge tools for context before writing proposal. Use `graphify query` (structural), `gitnexus impact` (semantic), `wiki_search` (curated), `memory_smart_search` (episodic, filtered to metadata only). Save to `openspec/changes/<name>/knowledge-context.md`. Skip for minimal-path changes (≤1 repo, no docs, no core code). See `references/knowledge-tools-integration.md`.

**Config-only changes:** Set `skip_specs: true` in `.openspec.yaml` when the change is tooling/config only (no spec delta). There is no CLI flag for this — it must be set in the file.

Risky multi-repo/provider/filesystem work: read `references/high-risk-multi-repo-apply.md`; crash recovery: `references/crash-recovery.md`.

### 2. Design and review

Author proposal (Why + What Changes), design.md (architecture, trade-offs), executable tasks.md, and delta specs (ADDED/MODIFIED/REMOVED Requirements with `#### Scenario:` blocks). See `references/delta-spec-format-guide.md` for the complete directory structure, header format, and troubleshooting — the #1 validation failure source. Load `references/final-implementation-evidence-gates.md` and `references/pre-archive-validation.md` before review.

For multi-provider reviews: `references/five-provider-review.md`. For config/tooling change artifact reviews (skip_specs changes): `references/change-artifact-review-lenses.md`. For review governance: load `openspec-review-governance` skill.

**CLI agent review execution (task 1.3):** Pre-collect ALL evidence in the orchestrator (change artifacts, git diff stats, test counts, version pins, prior findings, dependency status) into one sanitized fixture under 20 KB. Dispatch **external CLI agents** in batches of **max 3 concurrent** — never more, to avoid FD exhaustion. Use `claude -p`, `codex exec`, `agy -p`, `kimi -p`, `opencode run`, `pi -p`, and `goose run`, plus Hermes as the inline orchestrator. Use each CLI's configured default model/provider; do not add model/provider overrides. Run exact batches Claude/Agy/Goose, OpenCode/Codex/Kimi, then Pi alone. Pi bounded no-tool reviews use `--no-session --no-tools --no-extensions`; its MCP adapter uses proxy mode (`directTools: false`). Capture native child status before filtering and require substantive `VERDICT`, `FINDINGS`, and `RECOMMENDATIONS` content. **IMPORTANT:** "use coding agents review" means ACTUAL CLI agents, not Hermes `delegate_task` subagents. See `references/five-provider-review-orchestration.md`, `references/cli-based-review-workflow.md`, `references/cli-review-troubleshooting.md`, and `openspec-review-governance`.

### 3. Apply and implement

```bash
openspec instructions apply --change <name> --store openspec-store
```

Implement in vertical slices with RED→GREEN→review→commit per slice. See `references/implementation-pitfalls.md` for practical issues.

**Post-apply knowledge update (after ALL slices complete):** Run `graphify update .` on affected repos to keep graphs current. Do NOT run per-commit — batch after all slices.

### 4. Validate

```bash
openspec validate <name> --store openspec-store              # focused
openspec validate --all --store openspec-store               # full
```

**Note:** The CLI uses positional args, not `--change`. `openspec validate --change <name>` is wrong — use `openspec validate <name>`.

**Knowledge freshness check (before final validation):** Verify knowledge tools reflect current state: `graphify check-update .` on affected repos, `wiki_stale` for outdated pages, `gitnexus list` staleness check via MCP. Mark knowledge freshness as UNKNOWN if tools are unavailable.

### 5. Archive

```bash
openspec archive <name> --store openspec-store --yes
```

Then commit the store:
```bash
cd ~/Developer/openspec-store
git add openspec/
git commit -m "archive: <change-name> — merged delta specs into main specs"
```

**Post-archive knowledge capture (best-effort):** For each affected repo: `graphify update .` (if code changed), `gitnexus analyze . --skip-agents-md --skip-skills --index-only` (if symbols changed). For affected wiki pages: `wiki_search` to find related, update with `write_file` if stale. Weekly crons (graphify Mon 8AM, wiki Mon 9AM) provide safety net.

### Task Progress Tracking

For any active change, assess progress instantly:

```bash
cd ~/Developer/openspec-store
done=$(grep -c '\[x\]' openspec/changes/<name>/tasks.md)
todo=$(grep -c '\[ \]' openspec/changes/<name>/tasks.md)
echo "$done/$((done+todo)) tasks ($(( done * 100 / (todo > 0 ? done+todo : 1) ))%)"
```

**Pitfall (store-connected repos + `openspec init --tools`):** Repos that use an external store (have `store: openspec-store` in `openspec/config.yaml`) CANNOT run `openspec init --tools`. The CLI errors: "Remove the store: line first to convert this repo to a local OpenSpec root." Tool initialization (generating `.hermes/skills/`, `.claude/skills/`, `.agents/skills/`) must be done on the STORE itself (`cd ~/Developer/openspec-store && openspec init --tools hermes,claude,codex`). Store-connected repos inherit the store's skills. After upgrading OpenSpec CLI, re-run `openspec init --tools` on the store to regenerate skills at the new version, then copy the vendor-neutral `.agents/skills/openspec-*` to the workspace-level `~/Developer/.agents/skills/` to update all tools. The workspace-level skills need manual version tracking — compare `generatedBy` field in SKILL.md frontmatter. For the full workspace skill architecture (two-source-of-truth pattern, agent discovery paths, deduplication rules), see `agent-skills-ecosystem` skill's "Workspace Skill Architecture" section and `references/workspace-skill-setup.md`.

**Pitfall:** `.openspec.yaml` must have `schema: spec-driven` for `skip_specs: true` to be honored. Non-standard fields like `change:` or `description:` in `.openspec.yaml` cause validation failures. Fix by replacing with canonical `schema: spec-driven` + `created: YYYY-MM-DD`.

**Pitfall:** When writing multiple files to a change directory via `write_file`, the `.openspec.yaml` created by `openspec new change` may be deleted if batch writes don't include it. Always re-create `.openspec.yaml` after batch writes to a change directory. Verify with `ls -la` before validation. For `skip_specs: true` changes, the file must contain `schema: spec-driven`, `created: YYYY-MM-DD`, and `skip_specs: true`.

**Pitfall:** For tooling/config-only changes (new skills, CLI setup, agent wiring), use `skip_specs: true` in `.openspec.yaml`. The CLI flag `--skip-specs` does not exist — it MUST be set in the YAML file. Without it, validation fails with "no deltas found" even when skip_specs was intended.

**Pitfall:** When source implementation exists on a feature branch but tests haven't been verified against the current HEAD, run the focused test suite (`make knowledge-test`, `make agentmemory-test`, etc.) before marking tasks complete. Don't mark tasks complete based solely on code existence.

**Pitfall:** Change proposals may contain fabricated or outdated factual claims (version numbers, rule counts, dependency states, pre-commit hook patterns). Before executing or reviewing a change, independently verify its claims against actual workspace state. Use `execute_code` for efficient batch scanning of 10+ repos. This catches errors before they propagate into multi-repo rollouts. See `python-project-maintenance` skill's `references/cross-repo-enforcement-drift-patterns.md` for the verification technique.

**Pitfall:** After correcting change artifacts based on review findings, re-validate against official upstream sources (GitHub releases API, `.pre-commit-hooks.yaml` raw URLs, docs sites) before marking ready for execution. Tool hook IDs, rev versions, and rule names can change between versions — never assume from memory. See `python-project-maintenance`'s `references/cross-repo-enforcement-drift-patterns.md` "Official Source Validation" section for the verification commands.

**Pitfall:** When implementing changes that update tool versions or APIs, ALWAYS update tests to match the new API — never create workarounds (symlinks, compatibility shims, path aliases). Workarounds create hidden coupling to the old API. If the new tool has different subcommands, update the test to call the correct new subcommands. If the new tool rejects inputs the old one accepted (e.g. non-code files), adjust the test fixture, not the tool. See `references/tool-version-migration.md` for the full workflow.

**Pitfall:** "Simple" tooling changes (skill installation, CLI setup, agent wiring) still require the full OpenSpec lifecycle — create change, proposal, design, tasks, execute, archive. The user explicitly corrected skipping this: even a one-command skill install gets a change with `skip_specs: true`. Do not jump straight to execution.

**Pitfall:** Tool upgrades can silently change output directory layouts. After upgrading a tool (graphify, gitnexus, etc.), ALWAYS verify the actual filesystem output location before referencing paths in tasks, skills, or documentation. Do not assume the new version uses the same layout as the old one — run the tool, check where files actually land, then update all path references. A single wrong path assumption propagates into global graphs, skill files, AGENTS.md sections, and task evidence. This was caught in a second verification round that found graphify v0.9.34 changed `.graphify/graph.json` → `graphify-out/graph.json` while internal state stayed in `.graphify/`.

**Pitfall:** Multi-round verification is not optional for integration changes. First round catches functional bugs (missing tools, wrong paths). Second round catches state assumptions (stale manifest paths, wrong directory layouts, missing token permissions). Third round catches documentation drift (skills referencing wrong paths, AGENTS.md using outdated layouts). Each round catches different categories of issues — do not stop after one pass.

**Pitfall:** Retrospective changes (work already done, spec after) still require the full OpenSpec lifecycle — create change, proposal, design, tasks, validate, archive. The user explicitly corrected skipping this: even when implementation is complete and committed, you must create a change documenting what was done, write proposal/design/tasks with all checkboxes marked `[x]`, validate, and archive. The proposal should describe what changed (not what will change), and tasks should reflect completed work. Do not skip the lifecycle just because the code already exists.

**Pitfall (user correction — verification order):** When creating changes for new tool integrations, run ACTUAL verification tests BEFORE writing design.md claims. Do not write "✅ Verified" next to features you have not tested. The user corrected this explicitly: "Run actual check first, update openspec changes match validated features." Sequence: (1) create change skeleton, (2) run real tests against the tool, (3) update design.md to reflect ONLY what was observed, (4) then implement. Writing design docs with unverified claims wastes a correction cycle.

**Pitfall (user correction):** When the user says "follow openspec workflow properly" or "update openspec", they expect this SEQUENCE: (1) cross-repo blast-radius search, (2) create change with all artifacts, (3) implement (or mark tasks `[x]` if already done), (4) validate, (5) archive. Do NOT do all the implementation first and then try to document it after — the user finds this frustrating. Create the change early, even if tasks are initially empty, and fill them in as you go.

**Pitfall:** Archive fails when MODIFIED delta spec headers don't exactly match existing spec headers. The archive tool does exact string matching on `### Requirement:` lines. If your delta spec adds a new requirement (e.g. "Config.toml injection is deprecated") that doesn't exist in the base spec, use `## ADDED Requirements` instead of `## MODIFIED Requirements`. Check the base spec's requirement headers before writing delta specs. See `references/archive-delta-spec-headers.md` for the pattern.

**Pitfall:** Unicode box-drawing characters (┌─┐│└─┘) in markdown files cause `read_file` to detect the file as "Python script text executable" or "Binary file — cannot display as text." This blocks `read_file`, `patch`, and any tool that relies on text detection. **Fix:** Use ASCII-safe characters in architecture diagrams: `+---+` instead of `┌───┐`, `|` instead of `│`, `v` instead of `▼`. Also avoid starting files with ` ```python ` code blocks followed by Unicode art — this triggers the Python script heuristic. If a file is already corrupted by this, use `terminal(cat ...)` to read it and `write_file` to rewrite with ASCII characters.

**Pitfall — delegate_task reviews crash with vars() serialization bug (USE CLI AGENTS INSTEAD):** The Hermes `conversation_loop.py:2631` calls `vars(response)` without try/except on Pydantic models with `__slots__`. This can crash delegated subagent reviews when max_iterations is reached. Use external CLI agents (`claude -p`, `codex exec`, `agy -p`, `kimi -p`, `opencode run`, `pi -p`, `goose run`) for coding-agent reviews. `goose run -t "..." --no-session -q --max-turns N` runs headless without PTY. Each CLI runs as an independent process with its own error handling, bypassing the Hermes turn_finalizer entirely. Root cause chain: origin at `conversation_loop.py:2631` → propagation at `turn_finalizer.py:141` → `chat_completion_helpers.py:2119` summary call → response hits unguarded `vars()`. Do NOT patch hermes-agent framework code — report upstream. See `references/subagent-serialization-error-fallback.md`.

**Pitfall:** When tracing errors in delegation or serialization, trace to the PROPAGATION point (where the error becomes the user-visible output), not just the ORIGIN (where the error first occurs). The vars() bug wasoriginally found at `conversation_loop.py:2631` but fixing it there didn't help — the real propagation point was `turn_finalizer.py:142` where `_handle_max_iterations()` lacked a try/except. Always trace the full chain: origin → intermediate handlers → propagation point → user-visible output.

**Pitfall:** ALWAYS pass inline content in the `context` parameter to delegate_task, NEVER file paths. File paths cause reviewers to exhaust their iteration budget reading files instead of producing analysis. Pre-collect ALL evidence (artifacts, tool outputs, config state) as a string and pass it directly. The `references/five-provider-review-orchestration.md` has the correct pattern.

**Pitfall:** Do NOT patch hermes-agent framework code to fix the vars() serialization error. The framework gets overwritten on every update. Report the bug upstream instead. Work around it by accepting ~60% automated review rate and doing manual consolidation for failures. See `references/subagent-serialization-error-fallback.md`.

**Pitfall:** When deleting source packages (e.g. `llm_gateway/`, `resilience/`), always check for test files that import from them. Tests at `tests/<package>/` or `tests/test_<package>.py` in the same or consumer repos will break with `ModuleNotFoundError` if the source is deleted but the tests remain. Add test deletion to the task list explicitly — the review workflow will miss this if only source files are enumerated. Example: deleting `resilience/` requires also deleting `tests/resilience/` (22 tests) and `agent-docs-sync/tests/test_resilience.py` (14 tests).

**Pitfall (bulk sed replacement in test migrations):** When migrating parameter names across test files (e.g. `gateway=` → `model=`), sed's blind string replacement hits unintended contexts: `ConsumerRuntimeProfile(model=...)` where `model=` is a profile field, not the agent parameter; `assert request.tool_call_id == model` becoming corrupted; duplicate `model=model,` lines creating syntax errors. **Fix:** Use Python with targeted regex per file, not sed. For each test file: (1) read the file, (2) identify only the lines where the replacement applies (e.g., `build_agent(... gateway=...)` or `BaseAgent(... gateway=...)`), (3) replace only those lines, (4) verify with `python3 -m py_compile` before committing. Bulk sed across test files is a known trap for multi-parameter API migrations.

**Pitfall (context compaction loops):** After context compaction, the agent may lose track of completed operations and loop on the same failing command indefinitely (160+ retries observed). BEFORE issuing any git commit, verify the working tree state: `git status --short` and `git log --oneline -1`. If the tree is clean or the commit already exists, STOP — do not retry. If a command fails with the same output 3+ times, BREAK the loop and re-verify state from scratch. The compaction summary may reference staged files that were already committed in a prior context window. **The 3-strike rule:** same failure 3 times → stop, re-verify state. See `references/compaction-loop-anti-pattern.md` for the full pattern and recovery steps.

**Pitfall (context compaction — completed-operation trap):** A subtler variant: after compaction, the agent may re-issue terminal commands that SUCCEED but the tool cache marks them `[Duplicate output]`. The agent then keeps polling/reading the same results in a loop, convinced work is still pending. The signal is repeated `[Duplicate output]` markers or identical tool outputs appearing 3+ times. **Fix:** After any compaction event, run `git status --short` and `git log --oneline -3` to verify actual repo state before continuing. If the tree is clean, STOP — the work is done.

**Pitfall:** Knowledge tools can return stale data — always verify freshness before using as evidence. `graphify check-update .`, `wiki_stale`, and `gitnexus list` staleness checks are in `references/knowledge-tools-integration.md`. agentmemory outputs must be filtered to exclude credentials/secrets before entering context bundles.

**Pitfall:** After large code changes (API migrations, package deletions), graphify and gitnexus indexes become stale and return pre-migration references. ALWAYS rebuild before querying: `graphify update .` and `gitnexus analyze` (with `GITNEXUS_EMBEDDING_DIMS=768` for nomic-embed-text). Stale indexes waste time chasing phantom references that no longer exist in source. See `references/knowledge-tools-integration.md` for the rebuild workflow.

**Pitfall:** After large code changes (API migrations, package deletions), sweep ALL of: `src/`, `tests/`, `docs/`, `examples/`, `AGENTS.md`, `CLAUDE.md`, `pyproject.toml`, `Makefile`, `.github/`, openspec specs, wiki entries, and hermes skills references. Graphify and gitnexus can catch references that grep misses (cross-repo, stale indexes, embedded in comments/docstrings). See `references/cross-repo-cleanup-workflow.md` for the full multi-round verification pattern.

**Pitfall (agent-config spec staleness):** After model resolution or settings changes, check `agent-config` spec for stale fields. The `AgentConfig` dataclass may have new fields (`toolsets`, `model_settings`, `tool_search`, `source_file`, harness capability configs) or removed fields (`thinking` — moved to `ModelSettings`). The spec must match the actual `AgentConfig` dataclass in `agent_core/_ai/config.py`. Use `grep -n 'class AgentConfig' src/agent_core/_ai/config.py` to check actual fields, then update the spec accordingly.

**Pitfall (model_names vs prefix ambiguity):** When adding provider configs with `model_names`, verify that no model name collides with a prefix in `_PROVIDER_BY_PREFIX`. For example, `fable-5` is a model name (used in `nhà cung cấp dịch vụ AI-chat:fable-5`), not a provider prefix. Adding `fable-5` to `_PROVIDER_BY_PREFIX` would incorrectly match `openai-chat:fable-5` and route it to the wrong provider. The resolution order should be: exact `model_names` match first, then prefix fallback. See `references/model-resolution-provider-routing.md` for the full pattern.

**Pitfall:** Bash for-loops over directory structures with edge cases (empty files, missing tasks.md, files with no checkboxes) cause syntax errors like `0\n0: syntax error in expression`. Use `execute_code` (Python) instead of bash for directory traversal and counting. Python's `re.findall(r'\[x\]', content)` is reliable; bash `grep -c` with arithmetic on empty results is not. See the alignment audit pattern below.

**Pitfall:** GitNexus MCP tools have specific parameter schemas that differ from CLI flags. `ask_question` uses `repoName` (not `repo`) and `question` (not `query`). `context` uses `repoName` and `symbolName`. Always check the tool schema before calling — do not assume CLI flag names map directly.

### Model/Protocol Resolution Audit

For OpenSpec changes involving model factories, provider maps, proxy URLs, API modes, or protocol routing, treat model resolution as a two-layer contract: the resolver selects endpoint/credentials/provider configuration, while the model library may independently select a model class and request protocol from the model ID. A provider-class assertion alone is not endpoint evidence.

1. Trace the complete precedence chain: explicit kwargs, explicit environment, provider map, legacy model config, and native-provider fallback. Test partial pairs and collisions between provider-map and legacy settings.
2. Inspect how the model library calls the provider factory and record both the factory argument and resulting model/client/provider classes. A `codex_responses` factory returning `OpenAIProvider` does not prove an `OpenAIResponsesModel`; an Anthropic client injected into an `openai-*` model is a protocol mismatch.
3. Run no-network construction probes for each declared mode plus one deliberate prefix/mode mismatch. Record model class, provider/client class, normalized base URL, and request method/path when available. Include documented compatible prefixes (for example `google:*`) and unmapped providers, not only the hard-coded happy path.
4. Compare claims of configuration-driven routing with hard-coded prefix-to-provider tables. A provider entry containing `api_mode` is not a selector unless the resolver can reach it through a documented mapping or explicit field.
5. Require resolver-to-public-factory tests that assert every tuple field, mode propagation, provider precedence, fallback resolution, invalid-mode behavior, and missing-key behavior. Direct helper/factory tests are insufficient for task completion.
6. Reconcile contradictory prose such as "model kind is the single source of truth" versus "api_mode overrides protocol". Define precedence once in the canonical spec and update current docs; label archived historical behavior as superseded rather than mixing contracts.

See `references/model-resolution-provider-routing.md` for a compact evidence matrix, pydantic-ai shape-probe recipe, provider support matrix, and the two-layer contract (model prefix owns protocol/endpoint; `api_mode` owns provider class only). For config-driven capability injection (Thinking, model_settings merge, extra_model_settings security), see `references/pydantic-ai-capability-injection.md`.

### Spec Quality Review (read-only)

When reviewing all specs in a class (for example, every `agent-core-*` spec), treat CLI validation as the structural floor, not as evidence that the prose is current or coherent. Use a read-only review sequence:

1. Enumerate recursively with Python and filter the exact class prefix; do not rely on shell glob behavior that can silently miss nested specs.
2. Run `openspec validate <name> --strict --store openspec-store` for every matched spec and record the result.
3. Parse each file for `## Purpose`, `## Requirements`, `### Requirement:`, and `#### Scenario:`. Confirm every requirement has at least one scenario and every requirement body contains normative `SHALL`/`MUST` language.
4. Cross-check claims against the live consumer/code repos: actual package paths, exported symbols, function signatures, current config, CI workflows, and tests. CLI validity does not catch stale paths, removed APIs, phase-deferral text left behind after a successor spec, contradictory requirements, or snapshot counts.
5. Separate findings into (a) stale spec text, (b) an implementation gap against a still-valid spec, and (c) an underspecified/untestable requirement. Cite the spec and implementation paths and do not silently rewrite either side.
6. For code-backed claims, run focused tests plus the relevant full test collection when practical. For live-provider or deployment scenarios, record whether evidence is mocked, hermetic, or credential/network dependent; do not treat a non-deterministic real-service prompt as a portable acceptance test.
7. Check cross-spec ownership and precedence when multiple specs cover the same subsystem (especially memory, scheduler, authority, and public API). Report contradictory source-of-truth statements explicitly.
8. Preserve repository state during a review. Check `git status --short` at the end; do not revert pre-existing changes or create a report file unless requested.

For the reusable checklist and evidence classifications, see `references/spec-quality-review.md`.

### Direct Main-Spec Migration Workflow

When the user explicitly asks for a bounded cleanup of current `openspec/specs/<name>/spec.md` files (rather than an active change's delta specs), use a direct-baseline workflow without inventing a new change directory:

1. Read every named spec before editing; batch the reads when possible. Search both the exact legacy symbols and broader semantic references because a prior migration may already have removed class names while leaving generic `gateway`, provider-config, or resilience prose.
2. Classify each match before changing it. Replace legacy LLM API references with the target contract (`Model`, `model=`, `ModelSettings`, `ModelAPIError`, `create_model()`, and `FallbackModel`), but preserve valid unrelated infrastructure terminology such as an MCP router or an OTel collector. Do not blanket-replace every occurrence of `gateway`.
3. For an obsolete deployment spec that the user explicitly says needs a full rewrite, ground the replacement in the live successor deployment and current native model contract. Keep the filename stable unless renaming is requested; replace the requirements and scenarios, not just the title.
4. Keep all non-target requirements and scenarios unchanged. Use targeted `patch` operations for partial edits and `write_file` only for an explicitly requested full rewrite.
5. Run strict focused validation for all edited specs. A repository-wide validation may contain unrelated baseline failures; report those separately from the focused result.
6. Run the exact user-requested legacy grep after editing. `grep` exit status 1 is the expected no-match result, not a task failure; capture it explicitly rather than hiding a real error.
7. Review `git diff --check`, confirm exactly the requested files changed, then commit only those files with the requested message. Verify the post-commit status, HEAD, and grep result.

See `references/gateway-to-model-spec-update-pattern.md` for the migration table and provider/error naming caveat.

### Structural Baseline Reconciliation

Treat mcp-router or GitNexus structural findings as comparative evidence, not automatic migration failures. Capture the pre-change baseline for cycles and stale-index findings; only classify a finding as a regression when it is new or touches the migration-owned symbols. Keep generated graph output out of source commits unless explicitly owned.

### Post-Migration Cleanup Workflow

After a large multi-repo migration (API removal, package deletion, parameter rename), remaining work follows a standard sequence:

1. **Classify remaining issues** into three categories:
   - **Actionable** — stale generated artifacts (graphify-out, coverage.json, .gitnexus), unreferenced test files, stale documentation
   - **Structural baseline** — import cycles, dependency patterns that are pre-existing and work at runtime
   - **Historical references** — CHANGELOG entries, research docs with deprecation notes that describe what was removed
2. **Create an OpenSpec change** (`skip_specs: true`) documenting all three categories with tasks marked `[x]` for completed work
3. **Fix actionable items** — regenerate artifacts, rebuild indexes, commit
4. **Validate and archive** — `openspec validate <name> --type change`, then `openspec archive`
5. **Verify** — full spec validation, structural checks, grep for remaining legacy references

This pattern ensures no gaps are forgotten and provides a clean audit trail.

### Alignment Audit Workflow

When the user asks to "verify and run real operations" or "archive completed changes, sync specs, update docs":

1. **Audit active changes** — use `execute_code` (Python) to scan `openspec/changes/*/tasks.md` for completion status. Count `[x]` vs `[ ]` checkboxes. Bash for-loops fail on edge cases.
2. **Validate all specs** — `openspec validate --all --store openspec-store`
3. **Run real operations** — test GitNexus (`list_repos`, `context`, `query`), Graphify (`query`, `path`), Wiki MCP (`wiki_search`, `wiki_index`) to verify tools actually work
4. **Fix drift** — update AGENTS.md, skills, and OpenSpec config to match actual state
5. **Archive completed changes** — `openspec archive <name> --store openspec-store --yes`
6. **Commit and push** — `git add openspec/ && git commit` then `git push`

**Greenfield projects:** When documenting a codebase, check if it's greenfield (no legacy data, no migration constraints). If so, explicitly mark it in AGENTS.md and OpenSpec config: "No legacy data, no migration constraints, rewrite freely." This prevents future agents from treating existing schemas as immutable.

### GitNexus MCP Parameter Reference

| Tool | Required Params | Notes |
|------|----------------|-------|
| `list_repos` | (none) | Returns all 18 repos with stats |
| `context` | `repoName`, `symbolName` | 360° view of a symbol |
| `query` | `repoName`, `searchQuery` | Semantic search across codebase |
| `impact` | `repoName`, `target` | Blast radius analysis |
| `detect_changes` | `repoName` | Uncommitted change detection |
| `ask_question` | `repoName`, `question` | Natural language Q&A about code |

**Pitfall:** MoA preset config requires provider health verification. MoA presets reference provider/model pairs for advisors and aggregator. If ANY provider is unreachable (expired token, wrong base URL, API key restrictions), the preset silently degrades or fails. BEFORE proposing MoA changes, test inference on every model in every provider — do not trust config.yaml model lists. See `references/hermes-config-audit-methodology.md` Step 2.5 and `references/hermes-moa-configuration.md` for the full pattern.

**Pitfall:** Legacy flat-level moa config (`moa.reference_models`, `moa.aggregator`, `moa.fanout`) is a deprecated format that coexists with the preset system. When reconfiguring MoA, always remove the legacy block first (`hermes config unset moa.reference_models`, etc.), then create presets. Verify with `hermes moa list` that only presets remain.

**Pitfall:** `hermes config set moa.presets.<name> '{...}'` stores the value as a JSON string instead of a proper YAML dict, causing `hermes moa list` to show garbage or builtin defaults. For complex nested MOA config changes, edit `~/.hermes/config.yaml` directly via Python (`yaml.safe_load` → modify → `yaml.dump`). Verify with `hermes moa list` after every direct edit. See `references/hermes-moa-configuration.md` pitfalls section.

**Pitfall:** `hermes moa delete` refuses to delete the only preset ("Cannot delete the only MoA preset"). Create the replacement preset first, then delete the old one — or use `hermes config set --force moa '{...}'` to replace the entire section atomically.

## Key Rules

- Always use `--store openspec-store` from repo directories
- From store directory, auto-discovery works without `--store`
- `skip_specs: true` changes don't need delta specs
- `.openspec.yaml` must have `schema: spec-driven` for skip_specs to be honored
- Proposal must have `## Why` and `## What Changes` sections
- Never commit to main directly — use git worktrees, unless the user explicitly directs a direct commit in the current workspace
- AGENTS.md must stay ≤ 550 words (validated by `make validate-agent-guidance`)
- **v1.8.0+:** `retire_capabilities: true` in `.openspec.yaml` lets archive cleanly delete a spec when its last requirement is removed — no more "wall at archive time"
- **v1.8.0+:** Nested checkboxes in `tasks.md` count toward progress — "✓ Complete" actually means complete
- **v1.8.0+:** `validate` catches scenario loss at authoring time (MODIFIED requirement dropping a scenario fails early, naming scenarios to copy back)
- **v1.8.0+:** `SHALL`/`MUST` treated as guidance in normal mode — non-English specs pass. Strict mode still enforces
