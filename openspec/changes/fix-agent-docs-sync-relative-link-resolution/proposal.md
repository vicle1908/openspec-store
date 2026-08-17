# Proposal: Fix agent-docs-sync relative link resolution

## Why

The `docs-sync validate` command reports false-positive broken links because
relative Markdown links are resolved against the repository root instead of
the containing document's directory.

Evidence from CLI acceptance verification (2026-08-17):

- `docs-sync validate --repo ~/Developer/agent-core` reported 31 broken links.
- 26 of those targets exist under `docs/` (e.g., `docs/README.md → guide.md`
  resolves to `<repo>/guide.md` instead of `<repo>/docs/guide.md`).
- A disposable fixture confirmed the defect: `docs/README.md → guide.md`
  where `docs/guide.md` exists was reported as broken.
- Nested relative links (`docs/guide/start.md → ../api.md`) are also affected.

Root cause: `_find_broken_links()` in `full_pipeline.py` passes
`base_dir=str(repo_path)` for every individual Markdown file. `_check_link()`
then resolves every relative link as `base_dir / href`, overriding the
correct `source_file.parent` resolution.

## What Changes

- Fix `_check_link()` to resolve ordinary relative links from
  `source_file.parent` (the containing document's directory).
- Redefine `base_dir` as a safety/root containment boundary for
  preventing path traversal, not as the origin for every relative link.
- Callers (`_find_broken_links`, `cli.py` validate) continue passing
  the repository root as `base_dir` — this now supplies the intended
  security boundary rather than overriding resolution origin.
- Use `Path.is_relative_to()` (Python 3.12+) for safe containment checks
  instead of string prefix matching.
- Add regression tests covering sibling links, nested `../` links,
  fragment links, genuinely missing targets, image links, boundary
  escape, and no-explicit-boundary cases.

## Scope

- `src/agent_docs_sync/tools/check_links.py` — resolution semantics
- `src/agent_docs_sync/workflows/full_pipeline.py` — caller fix
- `tests/test_tools/test_check_links.py` — regression tests

## Non-Goals

- No changes to external URL checking behavior.
- No changes to anchor-only link behavior.
- No changes to image link behavior (same resolution rule applies).
- No changes to the approval lifecycle, write tools, or generation agents.
- No changes to `~/.tdt` configuration or skill profiles.

## Impact

- **Blast radius:** LOW — `_check_link` is a leaf method called by
  `_check_file` within the same class. Callers pass `base_dir` and it
  is retained as a containment boundary; only the resolution origin changes.
- **Consumers:** `full_pipeline.py` (audit + validate paths),
  `cli.py` (validate command), `generation.py` (agent tool registration).
- **Risk:** Two existing tests (`test_check_links_local_file` and
  `test_check_links_broken_link`) pass `base_dir` and resolve links
  against the same directory as `source_file.parent`, so they will pass
  unchanged. The defect is in the multi-directory case where `base_dir`
  differs from `source_file.parent`.
