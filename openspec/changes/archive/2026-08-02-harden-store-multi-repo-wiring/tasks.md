# Tasks: Harden Multi-Repo Store Wiring

## 1. Machine-Level Default Store

- [x] 1.1 Run `openspec config set defaultStore openspec-store`.
- [x] 1.2 Verify `openspec config get defaultStore` returns `openspec-store`.
- [x] 1.3 From `go-microservices`, verify `openspec list` resolves to the store.
- [x] 1.4 From `tdt-core`, verify `openspec list` resolves to the store.

## 2. Workspace OpenSpec Skills

- [x] 2.1 Copy the 12 canonical `go-microservices/.agents/skills/openspec-*`
  directories to `~/Developer/.codex/skills/`.
- [x] 2.2 Verify every workspace copy has the same `SKILL.md` hash as its
  canonical `.agents` source.
- [x] 2.3 Verify the tracked Go `.agents`/`.codex` mirror pairs remain
  byte-for-byte identical.
- [x] 2.4 Verify `go-microservices/.claude/skills/graphify` remains a real
  repo-specific directory and every other entry is a resolving relative link
  to the canonical `.agents/skills` surface.
- [x] 2.5 From `tdt-core`, verify the workspace skill surface is readable.

## 3. Workspace Instructions

- [x] 3.1 Verify `~/Developer/AGENTS.md` contains shared-store practices.
- [x] 3.2 Verify `~/Developer/.claude/CLAUDE.md` references `../AGENTS.md`.
- [x] 3.3 Verify `~/Developer/.codex/AGENTS.md` exists and references the
  workspace instructions.

## 4. Store Hygiene and Rules

- [x] 4.1 Confirm `openspec/openspec/` contains no tracked files.
- [x] 4.2 Remove the spurious nested directory tree.
- [x] 4.3 Add the four artifact rule groups to `openspec/config.yaml`.
- [x] 4.4 Verify the change and all main specs validate.

## 5. Final Verification

- [x] 5.1 Run `openspec store doctor openspec-store`.
- [x] 5.2 Run `make validate-agent-guidance` in `go-microservices`.
- [x] 5.3 Re-run `openspec list` from both Go and Python repos.
- [x] 5.4 Confirm no unintended skill duplicates or deleted managed mirrors.
- [x] 5.5 Commit the active change and all store modifications.
