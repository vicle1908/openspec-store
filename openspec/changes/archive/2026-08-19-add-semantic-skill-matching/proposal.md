# Proposal: Add Semantic Skill Matching

## Why

`agent_core/skill_system/matcher.py` uses a purely lexical algorithm: `0.6 * keyword_score + 0.4 * token_overlap_score`. Skills described with different terminology (e.g. "code review" vs "MR analysis") won't match even when semantically equivalent. The existing `memory/embedding.py` already provides `EmbeddingProvider` with LRU caching, OpenAI and LiteLLM providers — the infrastructure exists but isn't used for skill matching.

## What Changes

1. Add optional `EmbeddingProvider` parameter to `SkillMatcher`
2. When provided, compute cosine similarity between query embedding and skill description embeddings (cached at load time)
3. Blend lexical and semantic scores: `0.4 * lexical + 0.6 * semantic` (configurable weights)
4. Semantic matching is opt-in — default behavior unchanged (purely lexical)

## Scope

- `agent_core/skill_system/matcher.py` — add semantic scoring path
- `openspec/specs/skill-scope-profiles/spec.md` — MODIFIED: add semantic matching requirement
- No changes to skill loading, filtering, or profiles

## Out of Scope

- Skill auto-generation or embedding generation at load time (batch embedding is a separate concern)
- Changes to `align-jti-skill-runtime-contract` (different scope: JTI skill surface)
