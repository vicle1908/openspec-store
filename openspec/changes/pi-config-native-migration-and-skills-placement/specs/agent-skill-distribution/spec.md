# Spec Delta

## ADDED Requirements

### Requirement: Managed product roots MUST NOT duplicate the canonical shared surface

A managed product-specific skill root SHALL NOT hold content that is already available through the canonical shared `.agents/skills` surface. When a product root exists only to expose shared or workspace skills to one agent, that exposure SHALL be provided by supported standard `.agents/skills` discovery or by a link, not by copied files. Removing a product-specific root SHALL proceed only when every entry is either already available through standard discovery or is deliberately promoted, and the removal SHALL be reversible.

#### Scenario: A product-specific root is a subset of the canonical surface

- **GIVEN** a managed product root such as `~/.pi/agent/skills` contains only entries that also exist in the canonical shared surface
- **WHEN** the product root is evaluated for removal
- **THEN** the evaluation SHALL confirm that no entry is unique to the product root
- **AND** removal SHALL be performed only after that confirmation

#### Scenario: A product root holds a unique entry

- **GIVEN** a managed product root contains an entry that does not exist in the canonical shared surface
- **WHEN** removal is evaluated
- **THEN** the unique entry SHALL be promoted or explicitly reported before removal
- **AND** the entry MUST NOT be discarded silently

#### Scenario: Relocation preserves provenance

- **GIVEN** an entry is promoted from a product-specific root into the canonical shared surface
- **WHEN** the promotion is recorded
- **THEN** the resulting surface SHALL distinguish lockfile-tracked skills from untracked local additions
- **AND** a pre-change copy of both surfaces SHALL be retained until verification passes
