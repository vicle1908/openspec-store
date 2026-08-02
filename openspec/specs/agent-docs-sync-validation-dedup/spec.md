# Agent Docs Sync Validation Dedup Specification

## Purpose

Define validation and deduplication for docs-sync: link integrity checking, duplicate detection across documentation files, and enforcement of documentation quality gates.

## Requirements

### Requirement: Link check result caching
Link check results SHALL be cached per file + content hash to eliminate duplicate validation.

#### Scenario: Cache hit skips link check
- **WHEN** `CheckLinksTool` is called on a file whose content hash matches the cached hash
- **THEN** the cached link check result SHALL be returned
- **AND** the HTTP link checks SHALL NOT be performed

#### Scenario: Cache miss triggers full check
- **WHEN** `CheckLinksTool` is called on a file whose content hash differs from cache
- **THEN** full link checking SHALL be performed
- **AND** the result SHALL be cached with the current content hash

### Requirement: Diataxis enforcement result caching
Diataxis enforcement results SHALL be cached per file + content hash.

#### Scenario: Cache hit skips enforcement
- **WHEN** `EnforcerTool` is called on a file whose content hash matches the cached hash
- **THEN** the cached enforcement result SHALL be returned
- **AND** the Diataxis rule checks SHALL NOT be performed

#### Scenario: Cache miss triggers full enforcement
- **WHEN** `EnforcerTool` is called on a file whose content hash differs from cache
- **THEN** full Diataxis enforcement SHALL be performed
- **AND** the result SHALL be cached with the current content hash

### Requirement: Cache stored in Memory context layer
Validation caches SHALL use the Memory context layer with content-hash invalidation.

#### Scenario: Cache key format
- **WHEN** a validation result is cached
- **THEN** the key SHALL be `{file_path}:{content_hash}`
- **AND** the value SHALL contain the validation result and the hash used for invalidation

#### Scenario: Cache eviction
- **WHEN** the Memory context layer exceeds its max_messages limit
- **THEN** oldest entries SHALL be evicted automatically
- **AND** the pipeline SHALL re-validate affected files on next run
