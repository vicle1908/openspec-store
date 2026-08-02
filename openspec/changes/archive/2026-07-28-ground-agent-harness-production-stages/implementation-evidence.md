# Implementation evidence

## Transport and service composition

- `GitNexusTransport` is an injected read-only protocol exposing only
  query/context/impact/status. Missing, empty, stale, cross-repository, or
  oversized responses raise `CodeIntelligenceUnavailableError`; no shell or
  mutation fallback exists.
- `GraphifyTool` reads only approved-root JSON artifacts with schema version,
  repository, source identity, freshness, byte, and result-count validation.
- Immutable `HarnessServices` and narrowed `StageServices` keep Jira, code
  intelligence, artifact storage, clocks, and gateways outside checkpoint state.
  CLI production composition always constructs these services; the explicit
  `HARNESS_REQUIRE_EVIDENCE=false` rollback switch disables evidence-dependent
  stages to `needs_input` and never restores an ungrounded successful graph.
- Jira access remains factory-owned through `tdt_core.clients.JiraClientFactory`
  with bounded ticket fields and read-only operations.

## Graph, validation, and artifacts

- `build_graph(..., services=...)` closes stage nodes over narrowed services,
  injects Jira/code evidence, persists validated artifact revisions, and never
  advances after service/evidence failure. Gate topology and checkpoint types
  remain unchanged.
- `StageDefinition` declares required/optional evidence and freshness policy.
  Validation rejects stale or cross-repository evidence. Grounded plan review
  derives pass/fail from requirements, mappings, and evidence; provider
  `passes_review` values are not authoritative.
- `ArtifactStore` rejects revision overwrite, writes a companion digest, and
  verifies digest before returning immutable content. Graph stage persistence
  records artifact, validation, source identity, and evidence references.
- The fabricated no-tools sentinel is removed; the completed core explicit-empty
  allowlist now expresses deny-all tool visibility.

## Verification and rollback

- Refreshed impacts: `build_graph` CRITICAL across nine lifecycle paths;
  `run_validation`, `GitNexusTool`, and `GraphifyTool` LOW. Post-change
  detection reports the expected graph/stage/service fan-out.
- The CLI resolver and production service factory impacts are LOW; both now
  enforce service-backed composition by default.
- `uv sync --frozen`, Ruff check/format, strict mypy, full pytest/coverage,
  CLI tests, and full-history Gitleaks all pass: 238 tests, 90.26% coverage,
  no leaks.
- Grounded fixture tests produce non-empty requirements/evidence, persist all
  artifact revisions, and complete traceability review. Failure fixtures cover
  unavailable/malformed/stale evidence, digest mismatch, and artifact-store
  failure.
- Rollback leaves the graph/checkpoint topology and readable immutable artifact
  revisions intact; disabling `HARNESS_REQUIRE_EVIDENCE` preserves historical
  deterministic inspection while never restoring an empty successful provider.
