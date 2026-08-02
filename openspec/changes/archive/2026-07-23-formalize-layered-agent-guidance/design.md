## Context

The outer workspace contains a multi-module Go platform, deployment and GitOps
assets, OpenSpec planning, operational scripts, generated agent integrations,
and an independently versioned pnpm/Electron repository at `mcp-router/`.
Seven `AGENTS.md` files currently provide a root entry point plus scoped
guidance for services, platform, deployment, OpenSpec, scripts, and MCP Router.

The hierarchy is useful but only conventionally enforced. The existing
`operational-readiness` requirements govern agent configuration and MCP wiring;
they do not define which contributor-instruction files must exist, how
precedence works, or how command and path drift is detected. The workspace also
contains more than one hundred generated OpenSpec skill copies and
bootstrap-created agentmemory links, so hand-authored guidance needs a clear
ownership boundary.

## Goals / Non-Goals

**Goals:**

- Make the root guide a concise entry point and keep specialized rules close to
  the code or operations they govern.
- Define deterministic discovery, precedence, required scopes, content, and
  generated-file ownership.
- Detect missing guides, invalid paths or commands, malformed Markdown,
  credential exposure, and nested-repository coverage regressions in PR
  verification.
- Preserve user-owned dirty worktrees and keep validation non-mutating.

**Non-Goals:**

- Configure MCP servers, agentmemory, editor integrations, or tool permissions.
- Standardize every coding agent's private/global instruction files.
- Change service APIs, deployment resources, runtime behavior, or production
  state.
- Create a guide in every service when one shared `services/AGENTS.md` remains
  accurate.

## Decisions

### 1. Use a root router plus scoped guides

The root `AGENTS.md` defines universal workflow and repository boundaries.
Guides in `services/`, `platform/`, `deploy/`, `openspec/`, and `scripts/`
refine it for materially different work. `mcp-router/AGENTS.md` is also
required because MCP Router is a separate Git repository and must remain
self-describing when opened independently.

A single comprehensive root file was rejected because every task would receive
irrelevant operational detail and localized rules would drift into generic
prose. Per-service guides were rejected because the eight services currently
share the same architectural contract and local Makefiles already express
their small verification differences.

### 2. Keep guidance separate from generated agent surfaces

Hand-authored `AGENTS.md` files are the contributor-instruction source of
truth. Bootstrap-created agentmemory links, mirrored OpenSpec skills and
commands, validation artifacts, coverage output, and files declaring
`generatedBy` remain generator-owned. Guides may explain how to regenerate
them but must not direct agents to patch every generated copy.

Folding guidance into editor-specific settings was rejected because it would
duplicate policy across clients and would not cover tools that natively
discover `AGENTS.md`.

### 3. Add a dedicated, non-mutating validation command

Introduce a standard-library Go validator under `tools/agentguide/`, following
the existing isolated-tool pattern in `tools/workflowaudit/`. Expose it as
`make validate-agent-guidance` and make `verify-pr` depend on it.

The validator will:

- enumerate the seven required guides and their expected discovery chains;
- require one H1, valid Markdown structure, bounded word counts, no conflict
  markers or trailing whitespace, and the commands/safety markers owned by
  each scope;
- resolve referenced repository paths and verify Make/package-script targets
  without executing mutating commands;
- confirm generated-surface ownership language and reject credential-like
  literals while redacting matched values;
- report every violation with guide, category, and remediation, and support
  deterministic JSON output for CI.

Embedding this check in deployment validation was rejected because repository
instruction health is a PR concern even when deployment files are untouched.
A prose-only review was rejected because it cannot prevent drift.

### 4. Treat MCP health claims as end-to-end claims

The MCP Router guide must require live verification of tool/resource
discovery, configured server identity, process/listener state, authentication,
and an MCP handshake. Configuration presence or a successful restart alone is
insufficient. Tokens and credentials must never appear in guide text,
validator output, or retained diagnostics.

## Risks / Trade-offs

- **[Risk] Text validation becomes brittle during harmless rewrites.**
  → Validate required commands and safety concepts rather than exact paragraphs,
  and cover the validator with fixture-based tests.
- **[Risk] Root and scoped guidance contradict each other.**
  → Keep universal rules at the root, make scoped ownership explicit, and test
  expected discovery chains.
- **[Risk] The nested repository is validated against unrelated outer rules.**
  → Give MCP Router its own guide and validate its commands from its own
  `package.json` and Git root.
- **[Risk] Secret detection echoes sensitive text.**
  → Report only file, line, and category; never return the matched value.
- **[Trade-off] Seven guides add maintenance surface.**
  → Bound guide size and validate only scopes with genuinely distinct rules.

## Migration Plan

1. Land the capability spec and align the existing seven guides with it.
2. Add the isolated validator, fixtures, root Make target, and CI/`verify-pr`
   integration.
3. Run focused validator tests, the new Make target, both Git diff checks, and
   strict validation of this OpenSpec change.
4. Roll back by removing the validation integration and scoped guides in one
   reviewed change; no data, contract, or deployment migration is required.

## Open Questions

None. Additional scoped guides require a future capability change only when a
subtree develops materially different commands, ownership, or safety rules.
