## Context

See `proposal.md` for motivation and the four delta specs for normative behavior.

The current ecosystem already has the intended core pattern: `tdt-core` accepts the canonical provider/model/default catalog, resolves an immutable profile with exact routes, and builds a process-local model-construction context; `agent-core` consumes that context through one public model factory.

## Goals / Non-Goals

**Goals:**
- Establish one semantically coherent current provider, consumer-configuration, CLI projection, and evidence contract.
- Make every enabled native `ai-review` reviewer depend atomically on a valid canonical mapping.
- Keep harness and docs-sync domain configuration model-free.
- Prove the two normative public live boundaries independently.

**Non-Goals:**
- No compatibility schema, consumer-local fallback, or implicit provider inference.
- No provider credential or native authentication store changes.
- No historical archive edits.

## Decisions

### 1. Current main contracts choose the live consumers
The required matrix remains exactly: installed `ai-harness-skills` and installed `ai-review review ...`.

### 2. Provider schema follows the implemented clean-break route model
All providers declare explicit transport, typed protocol, and provider-bound credential reference. Legacy-only and mixed LLM schemas fail before profile resolution.

### 3. Harness and docs-sync use model-free domain configuration
No model/settings/profile shortcut is added to domain configuration. Harness `status`/`report` and docs-sync standalone commands compose without canonical LLM resolution.

### 4. ai-review validates the complete enabled native reviewer set atomically
The review composition transaction determines enabled native reviewers, resolves canonical profile, and validates every enabled mapping before constructing any native reviewer.

### 5. Evidence uses one parameterized comparison engine
Every field comparison is tagged `historical` or `current_reuse`. Historical authenticity verification needs Git object/manifest verification.

## Migration Plan

1. Revalidate store, repository heads, branches, dirt
2. Assign one writer per repository, create dedicated worktrees
3. Capture frozen RED baseline, apply narrow fixes
4. Run focused and complete gates with isolated caches
5. Commit one accepted packet per repository
6. Before applying downstream changes, recapture all identities
