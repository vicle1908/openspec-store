---
name: goose
description: "Delegate coding to Goose CLI (AAIF)."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Coding-Agent, Goose, AAIF, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, antigravity, opencode, hermes-agent]
---

# Goose — Hermes Orchestration Guide

Delegate coding, review, research, and background work to [Goose](https://goose-docs.ai). Goose is a general-purpose AI agent by the Agentic AI Foundation (AAIF) at the Linux Foundation. It supports MCP extensions (70+), subagents, recipes, ACP server mode, and built-in code review. This guide was validated against goose v1.45.0 on 2026-08-08.

### Verified local setup

Goose v1.45.0 at `/opt/homebrew/bin/goose`. Four providers configured: `nhà cung cấp dịch vụ AI` (fable-5.6-luna, active), `custom_shopapikey` (fable-5), `custom_giaoduc` (Advance), `custom_omniroute` (dlg/deepseek-v4-pro). 17 extensions enabled including developer, analyze, orchestrator, and mcp-router. ACP server registered in Zed.

**Known issue:** The `mcp-router` stdio extension currently fails to start in goose's extension context. This causes hangs or extended cold starts. See pitfall #13 for mitigation.

## Readiness

```bash
command -v goose
goose --version
goose info
goose skills list
```

**Note:** `goose doctor` exists but launches a full model-backed diagnostic session — it is NOT a quick health check. Use the simple smoke test below instead:

```bash
goose run -t "Reply OK" --no-session -q --max-turns 1
```

Installation:

```bash
curl -fsSL https://github.com/aaif-goose/goose/releases/download/stable/download_cli.sh | bash
# or
brew install block-goose-cli
```

Config lives at `~/.config/goose/config.yaml`. Credentials stored in macOS Keychain. Sessions DB at `~/.local/share/goose/sessions/sessions.db`.

## Preferred orchestration: headless mode (run mode)

Use `goose run` for bounded noninteractive work. It does not require a PTY.
**Always use `--no-session` and `-q`** for clean delegation — suppresses session persistence and non-response output.

```python
terminal(
    command=(
        "goose run -t 'Implement the requested change and run tests.' "
        "--no-session -q --max-turns 20"
    ),
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True,
)
```

Goose has **no `--dangerously-skip-permissions`** or `--bypass-permissions` flag. Headless mode (`goose run`) executes tools via enabled extensions without interactive approval prompts — the `developer` extension (file/shell tools) must be enabled in `~/.config/goose/config.yaml`.

**Key flags (validated):**

| Flag | Description |
|------|-------------|
| `-t "text"` | Inline prompt text |
| `-i <FILE>` | Instructions from file (use `-` for stdin) |
| `-q` | Quiet mode — suppress non-response output |
| `--no-session` | No session persistence |
| `--max-turns <N>` | Limit agent iterations |
| `--provider <NAME>` | Override provider (e.g. `custom_shopapikey`) |
| `--model <MODEL>` | Override model (e.g. `fable-5`) |
| `--system "text"` | Additional system instructions |
| `--stats` | Print TTFT, tokens/sec, output tokens |
| `--output-format <FMT>` | `text` (default), `json`, or `stream-json` |
| `--recipe <NAME>` | Use a YAML recipe config |
| `--no-profile` | Skip default extensions, only CLI-specified |
| `--debug` | Full tool responses without truncation |
| `--max-tool-repetitions <N>` | Prevent infinite tool loops |

### MCP Router access

**⚠️ Currently broken for goose.** The `mcp-router` stdio extension fails to start in goose's extension context. The 136 MCP tools listed in Hermes are NOT available to goose until this is resolved. Use `--no-profile --with-builtin developer` to skip the broken extension and rely on shell fallbacks instead.

### Output formats

**Text** (default, quiet mode):
```
OK
```

**JSON** — full conversation envelope:
```json
{
  "messages": [
    {"id": "...", "role": "user", "content": [{"type": "text", "text": "..."}]},
    {"id": "...", "role": "assistant", "content": [{"type": "text", "text": "..."}]}
  ],
  "metadata": {
    "total_tokens": 13442,
    "input_tokens": 13437,
    "output_tokens": 5,
    "cache_read_input_tokens": 9984,
    "cost_usd": 0.0045,
    "status": "completed"
  }
}
```

**Stream-JSON** — streaming events:
```
{"type":"message","message":{"id":"...","role":"assistant","content":[{"type":"text","text":"Hi"}]}}
{"type":"complete","total_tokens":14366,"cost_usd":0.0018}
```

## Providers (validated local setup)

| Provider | Model | Base URL | Notes |
|----------|-------|----------|-------|
| `openai` (active) | `gpt-5.6-luna` | localhost:51006/v1 | Responses API |
| `custom_shopapikey` | `fable-5` | api.phanmemvip.shop | |
| `custom_giaoduc` | `Advance` | api.giaoduc.online | |
| `custom_omniroute` | `dlg/deepseek-v4-pro` | Omniroute | |

Override at runtime:
```bash
goose run --provider custom_shopapikey --model fable-5 -t "task"
```

## Code review

Goose has built-in code review via `goose review`:

```bash
# Dry run — print review prompt and discovered checks
goose review --dry-run

# Review working tree changes
goose review

# Review specific diff range
goose review main...HEAD

# Restrict to specific files
goose review --files src/auth.py src/middleware.py

# Custom model/provider
goose review --model fable-5 --provider custom_shopapikey -q

# Additional instructions
goose review --instructions "This is a refactor, flag any behavior change"

# Filter by check name
goose review --check-filter security perf

# Set turn limit for orchestrated checks
goose review --turn-limit 10
```

Review features:
- Discovers `.agents/checks/*.md` subagent reviewers
- Supports `--model`, `--provider`, `--turn-limit`
- Parallel orchestrator for multiple checks (capped at 4 concurrent)
- `--severity` filter (default: `medium`; use `--severity low` for all)
- `--checks-only` to skip main correctness pass
- `--summary-only` for diff summary only
- `--no-orchestrate` to disable parallel orchestrator (single-prompt fallback)
- `--instructions <TEXT>` to prepend context to review
- `--check-filter <NAME>` to run specific checks only
- `--check-scope <DIR>` to search for checks in alternate directory
- `--prompt <FILE>` to use custom base review prompt

Output format: JSONL — one JSON object per line per finding with `severity`, `path`, `line_start`, `line_end`, `summary`, `check`. Review exits 0 even when HIGH severity findings exist.

## Recipes

Goose supports YAML recipe files for portable workflow configs:

```bash
goose recipe list           # list available recipes
goose recipe validate <f>   # validate a recipe
goose recipe deeplink <f>   # generate deeplink
```

Use recipes with: `goose run --recipe <name-or-path>`

Additional recipe flags: `--params KEY=VALUE` (repeatable), `--sub-recipe <path>` (repeatable), `--explain` (show recipe details), `--render-recipe` (print rendered recipe without running).

No recipes are currently installed locally.

## Sessions and state management

Goose persists sessions by default (unless `--no-session`). Key session flags:

| Flag | Description |
|------|-------------|
| `-r, --resume` | Resume the most recent session |
| `-n, --name <NAME>` | Name the session (use with `--resume` to target specific session) |
| `--session-id <ID>` | Resume by exact session ID |
| `-s, --interactive` | Continue interactively after initial input |

**Important:** `--no-session` and `--name` are mutually exclusive. To create a named session for later resume, omit `--no-session`:

```bash
# Create a named session
goose run -t "Set up the project" --name my-feature -q --max-turns 20

# Resume it later
goose run -t "Continue where we left off" -r --name my-feature -q --max-turns 20
```

List sessions: `goose session list`
Remove sessions: `goose session remove`

## Subagents and orchestration

Goose has a built-in `orchestrator` extension for managing subagent sessions:

- `summon` extension: load knowledge and delegate tasks to subagents
- `orchestrator` extension: manage agent sessions (list, view, start, send, interrupt, stop)

These are interactive features primarily — in headless mode, the model decides whether to invoke them based on the prompt.

## Skills system

Goose discovers skills from the filesystem and built-in sources:

```bash
goose skills list
```

Skill count is **context-dependent** — it varies by working directory because goose scans `.agents/skills/` in the CWD and parent directories. In `~/Developer` it may find 100+; in a small project, only the built-in `goose-doc-guide`. Custom skills can be placed in `.agents/skills/` in any project.

## Extensions reference

All 17 extensions verified enabled in local config:

| Extension | Type | Purpose |
|-----------|------|---------|
| developer | platform | File read/write/edit, shell commands |
| analyze | platform | Tree-sitter code structure analysis |
| orchestrator | platform | Subagent management |
| todo | platform | Task tracking |
| memory | builtin | Preference learning |
| skills | platform | Skill discovery and loading |
| code_execution | platform | Token-saving extension calls |
| summarize | platform | File/directory LLM summaries |
| chatrecall | platform | Session history search |
| apps | platform | HTML/CSS/JS sandbox apps |
| computercontroller | builtin | Desktop automation |
| autovisualiser | builtin | Data visualization |
| extensionmanager | platform | Extension management |
| tutorial | builtin | Interactive tutorials |
| tom | platform | Top-of-mind context injection |
| summon | platform | Knowledge loading, subagent delegation |
| mcp-router | stdio | ⚠️ Broken for goose (see pitfall #13) |

## ACP server mode

Goose can act as an ACP (Agent Client Protocol) server for IDE integration:

```bash
goose acp                    # Run as ACP server on stdio
goose serve                  # Start ACP server over HTTP/WebSocket
```

`goose serve` options: `--host` (default: 127.0.0.1), `--port` (default: 3284), `--tls`, `--dangerously-unauthenticated` (skip auth), `--allowed-origin`, `--enable-scheduler`.

**Security:** `--dangerously-unauthenticated` disables the `GOOSE_SERVER__SECRET_KEY` requirement. Never use in production without authentication. Bind to localhost only unless explicitly required.

Already registered in Zed's `agent_servers` config.

## Offline / Air-gapped Docs

The `goose-doc-guide` builtin skill reads official goose documentation. By default it fetches from `https://goose-docs.ai`. For offline access, set `GOOSE_DOCS_ROOT` in `~/.config/goose/config.yaml`:

```yaml
GOOSE_DOCS_ROOT: /opt/goose-docs
```

**Local setup:** `GOOSE_DOCS_ROOT: /opt/goose-docs` — 1,481 files, built from v1.45.0.

**Source repo:** `~/Developer/goose-docs/` (1.9GB) — full clone with node_modules for quick rebuilds.

To rebuild when goose upgrades:

```bash
cd ~/Developer/goose-docs
git fetch --tags
git checkout v<NEW_VERSION>
cd documentation && npm install && npm run build
sudo cp -r build/* /opt/goose-docs
```

## Additional CLI commands

| Command | Purpose | Key subcommands |
|---------|---------|-----------------|
| `goose schedule` | Manage scheduled recipe jobs | `add`, `list`, `remove`, `run-now`, `cron-help` |
| `goose gateway` | External platform integrations | `status`, `start`, `stop`, `pair` |
| `goose plugin` | Manage git-backed plugins | `install`, `update` |
| `goose local-models` | Local GGUF/MLX inference | `search`, `download`, `list`, `delete` |

## Complexity-adaptive limits

Do not use one fixed turn/timeout budget for every task. Classify the work before launch:

| Complexity | Typical scope | `--max-turns` | Host timeout |
|---|---|---:|---:|
| Small | Read-only review, one-file fix | 5–10 | 3–5 min |
| Medium | One subsystem with focused tests | 15–25 | 5–10 min |
| Large | One repository with full verification | 30–50 | 10–20 min |

**Performance characteristics:**

⚠️ **Note:** These timings were measured when the MCP router extension was NOT failing. With the current MCP router hang (pitfall #13), cold starts can take 3+ minutes or hang indefinitely. Use `--no-profile --with-builtin developer` for reliable timing.

| Metric | Value (no MCP hang) | With MCP hang |
|--------|---------------------|---------------|
| Cold start (first run in session) | ~55s | 3+ min or hangs |
| Warm start (subsequent runs) | ~12–15s | May still hang |
| Time to first token | ~2.5s | N/A if hanging |
| Tokens/sec | ~6.4 | N/A if hanging |

Keep host timeout above expected model budget. First-run tasks need extra headroom for cold start. Split multi-repository work into separate invocations.

## Pitfalls

1. **No `--dangerously-skip-permissions`.** Goose headless mode does not have a permission bypass flag. Extensions execute tools directly when invoked non-interactively. Ensure the `developer` extension is enabled in config.

2. **No `--max-budget-usd`.** There is no cost cap flag. Bound unattended work with `--max-turns` and host timeout instead.

3. **Exit code 0 does not mean success.** Goose returns exit code 0 even for invalid models (404 errors), max-turns exhaustion ("Would you like me to continue?"), and tasks where tools were unavailable (`--no-profile`). Always inspect `metadata.status` from `--output-format json` output and verify artifacts externally. Only exit code 1 reliably indicates failure (e.g. unknown provider).

4. **Cold start penalty.** First goose run in a new session takes ~55s due to extension initialization. Subsequent runs are ~14s. Set host timeouts accordingly.

5. **Concurrent writers race.** Two simultaneous `goose run` invocations writing to the same file both report success but the final content is non-deterministic (last write wins). Use separate worktrees or isolated directories for concurrent writers. Keep one integration owner per file path.

6. **`--no-profile` disables tools silently.** Without extensions, goose cannot write files or run shell commands. It will report the inability and suggest manual commands, but still exits 0. Only use `--no-profile` when all required extensions are supplied explicitly via `--with-extension` or `--with-builtin`.

7. **Workspace file reader restriction.** The MCP file reader extension cannot access files outside the project root. Goose falls back to shell commands (`test -f`, `sed`) for verification. This is expected behavior, not an error.

8. **JSON output includes banner lines.** The `--output-format json` output is prefixed with goose's ASCII art banner and session info lines. Parse only the JSON object (starts with `{`), not the full stdout. Always use `-q` when parsing JSON programmatically.

9. **`goose review` requires git repo.** Review operates on git diffs. It fails outside git repositories and cannot review files outside the repo boundary. Review exits 0 even when HIGH severity findings exist — inspect the JSONL output, not just the exit code.

10. **Keyring-based auth.** Credentials are stored in macOS Keychain, not environment variables. If auth fails, check with `security find-generic-password -s "goose"`.

11. **Provider override requires matching model.** When using `--provider`, the model must be configured for that provider in config.yaml. Passing a model not registered for the provider causes a runtime error (which may still return exit code 0).

12. **`goose doctor` is NOT a quick health check.** It launches a full model-backed diagnostic session, consumes provider tokens, and can take minutes. Do not use it as a readiness probe. Use `goose --version` and a simple `goose run -t "Reply OK" --no-session -q --max-turns 1` instead.

13. **MCP router extension causes hangs.** The `mcp-router` stdio extension (`npx -y @mcp_router/cli@latest connect`) consistently fails to start in goose's extension context — even when the same command works under Hermes. This is not a transient failure. It causes goose to hang indefinitely (tested: 3+ minutes without response). **Mitigation:** Use `--no-profile --with-builtin developer` to skip mcp-router entirely, or rely on shell fallbacks. The MCP tool count (136) documented in this skill applies to Hermes, not to goose — goose cannot access MCP tools while this extension fails. If MCP tools are required, investigate the incompatibility separately.

14. **`--no-session` and `--name` are mutually exclusive.** Passing both produces an error. To create a named session for later resume, omit `--no-session`. To run a disposable one-shot, use `--no-session` without `--name`.

15. **Skills count is context-dependent.** `goose skills list` scans `.agents/skills/` in the CWD and parent directories. The count varies from 1 (built-in only) to 100+ (workspace with many skill directories). Do not treat any count as a stable fact.

## Verification checklist

1. Record `goose --version`, `goose info`, and inspect provider config in `~/.config/goose/config.yaml`.
2. Test connectivity with a simple prompt: `goose run -t "Reply OK" --no-session -q --max-turns 1`.
3. **Always check `metadata.status` from `--output-format json` output** — exit code 0 does not guarantee success.
4. Use `-q --no-session` for clean delegation without session noise.
5. Set Hermes `workdir` for the filesystem workspace.
6. Use `--max-turns` and host timeout as bounds (no cost cap available). Note: max-turns exhaustion still returns exit 0.
7. For writes, require absolute paths and verify files externally with `cat`/`git diff`.
8. For reviews, inspect JSONL output — review exits 0 even with HIGH severity findings.
9. Use separate worktrees for concurrent writers to avoid race conditions.
10. Never use `goose doctor` as a readiness check — it consumes tokens and takes minutes.

## Official sources

- [Documentation](https://goose-docs.ai)
- [GitHub](https://github.com/aaif-goose/goose)
- [ACP Clients](https://goose-docs.ai/docs/guides/acp-clients)
- [CI/CD Guide](https://goose-docs.ai/docs/tutorials/cicd)
- [Providers](https://goose-docs.ai/docs/getting-started/providers)
- [Extensions](https://goose-docs.ai/docs/category/mcp-servers)
- [Recipes](https://goose-docs.ai/docs/guides/recipes/session-recipes)
