# Design: Harden Goose Runtime Configuration

## Current Evidence Baseline

Validated on 2026-08-09 against goose v1.45.0:

| Area | Evidence | Status |
|---|---|---|
| Active provider | `openai/gpt-5.6-luna` isolated sentinel, 7,778 tokens, `completed` | Healthy |
| Shopapikey | `custom_shopapikey/fable-5` isolated sentinel, 4,921 tokens | Healthy |
| Giaoduc | `custom_giaoduc/Advance` isolated sentinel, 4,647 tokens | Healthy in this probe |
| Omniroute | `custom_omniroute/dlg/deepseek-v4-pro`; 404 missing `dlg` credentials; zero usage; misleading `completed` | Unavailable |
| Offline docs | Runtime tool trace read `/opt/goose-docs/goose-docs-map.md` and mapped page; 60/60 map links exist | Healthy |
| MCP transport | Direct stdio initialize/list: MCP Router v0.2.0, protocol 2025-11-25, 132 tools | Healthy |
| MCP from goose | Real `list_directory` call succeeded | Healthy call path |
| MCP startup | Separate goose runs failed before initialization | Intermittent/degraded |
| Least-privilege coding | `--no-profile --with-builtin developer` write/read marker passed | Functional |
| Default profile cost | Offline-doc proof: ~193K tokens/$0.157; MCP call: ~37K/$0.0395 | Too expensive |
| Config permissions | `~/.config/goose/config.yaml` mode 0644 | Hardening candidate |
| Source checkout | Exact tag v1.45.0, clean, shallow tag-only refspec | Reproducible now; update workflow fragile |
| Deployed docs | 1,481 files; source has one extra `.nojekyll`; map hash matches; 60/60 map links valid | Healthy with minor copy-semantic gap |

## Design Decisions

### 1. Health verification contract

A probe passes only when all applicable checks pass:

- process exit code is expected;
- structured status is expected;
- exact sentinel or expected artifact exists;
- assistant output contains no provider/tool error;
- token usage is nonzero for model calls;
- writes are verified outside goose.

### 2. Invocation profiles

Define documented profiles without immediately changing global extension state:

- **Chat/docs:** `--no-profile`, no file or shell tools unless local docs are required.
- **Coding:** `--no-profile --with-builtin developer`, isolated worktree, external diff/tests.
- **MCP-dependent:** current profile plus a preflight read-only MCP call; fail closed if it cannot initialize.
- **Interactive full profile:** human-supervised only.

### 3. MCP stabilization

Investigate duplicate bridge parentage and goose initialization timing. After review, replace mutable `@mcp_router/cli@latest` with the validated `@mcp_router/cli@0.2.0`, then verify initialize, tools/list, and one read-only goose tool call. Pinning is a live config mutation and requires explicit apply approval.

### 4. Provider state

Keep Omniroute recorded as configured but unavailable until `dlg` credentials are restored and a real sentinel succeeds. Do not silently switch its model or provider. Preserve the three healthy provider entries.

### 5. Offline-doc lifecycle

Future builds SHALL:

1. compare installed goose version to desired docs tag;
2. explicitly fetch the target tag into the shallow checkout;
3. use `npm ci`;
4. build into source `documentation/build`;
5. stage a deployment candidate;
6. validate map existence, 100% map-link resolution, source tag/commit, and expected file inventory;
7. retain a rollback copy;
8. cut over with deletion-aware or atomic semantics;
9. verify a runtime local-doc read after cutover.

### 6. Permission and exposure hardening

Before mutation, confirm Goose Desktop tolerates config mode 0600 and that deployed docs remain readable. Keep `goose serve` loopback-bound and authenticated. Gate any gateway or schedule creation separately; current state has none.

## Rollback

Restore the prior config backup and prior docs directory, then rerun:

- three healthy provider sentinels;
- Omniroute status probe;
- MCP direct handshake and goose MCP call;
- least-privilege marker probe;
- offline-doc local-read proof.

## Risks

- Provider availability can change independently of config.
- Goose may report exit 0 and `completed` for provider errors.
- Default-profile prompts are costly.
- Multiple long-lived MCP bridge processes may amplify resource pressure.
- A copy-only docs deployment may retain stale files across versions.
