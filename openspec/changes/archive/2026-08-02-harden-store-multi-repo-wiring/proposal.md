# Proposal: Harden Multi-Repo Store Wiring

## Why

The shared `openspec-store` is registered on this machine, but code repos do
not resolve to it automatically, and OpenSpec Codex skills are available only
inside `go-microservices`. The store also contains an accidental nested
`openspec/openspec/` tree and has no artifact-quality rules.

## What Changes

1. Set the OpenSpec machine-level `defaultStore` to `openspec-store`.
2. Copy the 12 canonical OpenSpec skills from
   `go-microservices/.agents/skills/openspec-*` into the workspace Codex skill
   surface at `~/Developer/.codex/skills/openspec-*`.
3. Preserve the Go repository's tracked `.agents`/`.codex` mirror pair; its
   documentation-currency contract requires those files to remain identical.
4. Verify the workspace `AGENTS.md`, `.codex/AGENTS.md`, and
   `.claude/CLAUDE.md` instruction chain. Verify the repo Claude surface keeps
   its repo-specific `graphify` directory and uses resolving relative links to
   the repo's canonical shared skills rather than duplicate copies.
5. Remove the spurious nested `openspec/openspec/` directory.
6. Add proposal, specs, design, and task rules to `openspec/config.yaml`.

## Non-Goals

- No application or service code changes.
- No new repo-local `openspec/` directories or per-repo `store:` pointers.
- No git remote setup or push; the destination and authorization are not part
  of this continuation.
- No relocation of existing governance documents or reports.
- No deletion of generated or managed per-repo skill mirrors.

## Impact

- Interactive OpenSpec commands from code repos can resolve the registered
  shared store without an explicit flag; explicit `--store` remains supported
  and is still used by deterministic workspace scripts.
- OpenSpec Codex skills are discoverable at workspace scope while existing
  project-level parity checks remain intact.
- New artifacts receive consistent quality guidance from the store config.

## Ownership Boundary

Changes are limited to the OpenSpec store, machine/workspace agent
configuration, and the non-application skill surface. No service runtime,
dependency, deployment, or API contract is affected.
