# Design: Goose Coding Agent Skill

## Context

Goose v1.45.0 (AAIF/Linux Foundation) is installed and configured on this Mac. All features below were verified through actual execution on 2026-08-08.

## Validated Configuration

**Install path:** `/opt/homebrew/bin/goose`
**Config:** `~/.config/goose/config.yaml`
**Sessions DB:** `~/.local/share/goose/sessions/sessions.db`
**Credentials:** macOS Keychain (`security find-generic-password -s "goose"`)

### Providers (all verified working)

| Provider | Model | Status | Notes |
|----------|-------|--------|-------|
| `openai` (active) | `fable-5.6-luna` | ✅ | Via localhost:51006 proxy, Responses API path |
| `custom_shopapikey` | `fable-5` | ✅ | Via api.phanmemvip.shop |
| `custom_giaoduc` | `Advance` | ✅ | Via api.giaoduc.online |
| `custom_omniroute` | `dlg/fable-5-v4-pro` | ✅ | Via Omniroute |

### Extensions (all enabled)

| Extension | Type | Purpose |
|-----------|------|---------|
| developer | platform | File read/write/edit, shell commands |
| analyze | platform | Tree-sitter code structure analysis |
| orchestrator | platform | Subagent management |
| todo | platform | Task tracking |
| memory | builtin | Preference learning |
| skills | builtin | Skill discovery and loading |
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
| mcp-router | stdio | 136 MCP tools via npx @mcp_router/cli |

### Global Settings

| Setting | Value |
|---------|-------|
| `GOOSE_CONTEXT_LIMIT` | 1000000 (1M tokens) |
| `GOOSE_PLANNER_CONTEXT_LIMIT` | 1000000 |
| `GOOSE_THINKING_EFFORT` | max |
| `GOOSE_TELEMETRY_ENABLED` | false |

## Validated Headless Mode

### Core Command

```bash
goose run -t "prompt text" --no-session -q --max-turns N
```

### Verified Flags

| Flag | Tested | Result |
|------|--------|--------|
| `-t "text"` | ✅ | Inline prompt works |
| `-i file` | ✅ | Instructions from file (not tested directly, but documented) |
| `-q` | ✅ | Quiet mode — only output text, no session banner |
| `--no-session` | ✅ | No session persistence |
| `--max-turns N` | ✅ | Bounded agent turns |
| `--provider X` | ✅ | Provider override (tested: custom_shopapikey, custom_giaoduc) |
| `--model Y` | ✅ | Model override (used with --provider) |
| `--system "text"` | ✅ | System prompt override — was followed correctly |
| `--stats` | ✅ | Shows Time to first token, Tokens/sec, Output tokens |
| `--output-format json` | ✅ | JSON envelope with messages + metadata |
| `--output-format stream-json` | ✅ | Streaming JSON events |
| `--output-format text` | ✅ | Default text output |
| `--debug` | ⚠️ | Shows full tool responses (not tested in isolation) |
| `--no-profile` | ✅ | Skips all extensions |
| `--recipe <name>` | ⚠️ | Recipe system exists, no recipes installed yet |

### NOT Available (verified absent from --help)

| Flag | Status |
|------|--------|
| `--dangerously-skip-permissions` | ❌ Does not exist |
| `--max-budget-usd` | ❌ Does not exist |
| `--bypass-permissions` | ❌ Does not exist |

**Note:** Headless mode (`goose run`) does not require permission bypass — extensions execute tools directly when invoked non-interactively.

### Performance Characteristics

| Metric | First Run | Subsequent Runs |
|--------|-----------|-----------------|
| Cold start | ~55s | ~12-15s |
| Time to first token | — | ~2.5s |
| Tokens/sec | — | ~6.4 |
| Simple prompt total | ~55s | ~14s |
| Coding task (write+verify) | — | ~120s |

**Key finding:** First goose run in a session has significant cold-start overhead (~55s). Subsequent runs are fast (~14s). Factor this into host timeouts.

## Validated Output Formats

### Text (default)
```
OK
```

### JSON
```json
{
  "messages": [
    {"id": "...", "role": "user", "content": [{"type": "text", "text": "..."}], "metadata": {...}},
    {"id": "...", "role": "assistant", "content": [{"type": "text", "text": "..."}], "metadata": {...}}
  ],
  "metadata": {
    "total_tokens": 13442,
    "input_tokens": 13437,
    "output_tokens": 5,
    "cache_read_input_tokens": 9984,
    "cache_write_input_tokens": 0,
    "cost_usd": 0.0044814,
    "status": "completed"
  }
}
```

### Stream-JSON
```
{"type":"message","message":{"id":"...","role":"assistant","content":[{"type":"text","text":"Hi"}],...}}
{"type":"complete","total_tokens":14366,"input_tokens":14353,"output_tokens":13,...}
```

## Validated Coding Task

Goose successfully:
1. Created `/tmp/goose-test/test.py` with a Python function
2. Attempted MCP file reader (failed due to workspace restriction)
3. Fell back to shell `test -f` + `sed` to verify
4. Reported the final file contents

**Tool chain observed:** `write` → `read_file (mcp-router)` → `shell` → final response

## Validated Code Review

`goose review` works:
- `--dry-run` prints the review prompt and discovered checks
- Discovers `.agents/checks/*.md` subagent reviewers
- Outputs structured JSON findings with severity, path, line range, summary
- Requires files to be inside the git repository

## Validated Skills System

Goose has 14 built-in/discoverable skills:
- `brightdata-cli`, `convert-documents-to-markdown`, `data-feeds`, `docker-patterns`, `docker-persistence`, `golang-documentation`, `goose-doc-guide` (builtin), `graphify`, `multi-stage-dockerfile`, `python-design-patterns`, `python-performance-optimization`, `python-testing-patterns`, `search`

## Invocation Patterns (validated)

### Simple one-shot
```python
terminal(
    command='goose run -t "Reply OK" --no-session -q --max-turns 1',
    workdir="/path/to/project",
    timeout=120,
)
```

### With provider override
```python
terminal(
    command='goose run -t "task" --provider custom_shopapikey --model fable-5 --no-session -q --max-turns 20',
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True,
)
```

### With system prompt
```python
terminal(
    command='goose run -t "Analyze the architecture" --system "Focus on security patterns" --no-session -q',
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True,
)
```

### With stats
```python
terminal(
    command='goose run -t "task" --no-session -q --max-turns 20 --stats',
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True,
)
```

### Code review
```python
terminal(
    command='goose review main...HEAD --model fable-5 -q',
    workdir="/path/to/project",
    timeout=300,
)
```

### JSON output for parsing
```python
terminal(
    command='goose run -t "task" --no-session --output-format json --max-turns 20',
    workdir="/path/to/project",
    background=True,
    notify_on_complete=True,
)
# Parse: skip banner lines, find first {, then json.loads
# parsed = json.loads(output[output.index('{'):])
# answer = parsed["messages"][-1]["content"][0]["text"]
```

## Complexity-Adaptive Limits

| Complexity | Typical scope | `--max-turns` | Host timeout |
|---|---|---:|---:|
| Small | Read-only review, one-file fix | 5–10 | 3–5 min |
| Medium | One subsystem with focused tests | 15–25 | 5–10 min |
| Large | One repository with full verification | 30–50 | 10–20 min |

**Note:** These are tighter than other agents because goose's cold start is ~55s but subsequent turns are fast (~14s). First-run tasks need extra headroom.

## Trade-offs

### Advantages over other agents
- **136 MCP tools** via mcp-router (more than any other agent)
- **Built-in code review** with parallel orchestrator and custom checks
- **Recipes** for portable, shareable YAML workflow configs
- **ACP server mode** for IDE integration (already in Zed)
- **1M token context** (configurable)
- **Multi-provider** support with runtime override
- **Skills system** with 14 built-in skills

### Limitations
- **No cost cap** — use `--max-turns` and host timeout
- **No permission bypass flag** — headless mode handles this via extension config
- **Cold start penalty** — ~55s first run vs ~14s subsequent
- **JSON output is conversation-style** — not a simple response object like agy
- **Workspace file reader restriction** — cannot read outside project root (falls back to shell)
- **No recipes installed** — recipe system exists but unused
