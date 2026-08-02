# Diátaxis Classification

## Purpose

Classify documentation into four Diátaxis quadrants (tutorial, how-to, explanation, reference) using rule-based classification with LLM fallback for ambiguous cases.

## Requirements

### Requirement: Classify documentation into Diátaxis quadrants
The system SHALL classify all documentation into four Diátaxis quadrants: tutorial, how-to, explanation, and reference.

#### Scenario: Tutorial classification
- **WHEN** a document contains numbered steps, prerequisites, and learning objectives
- **THEN** the system classifies it as `tutorial` quadrant
- **AND** maps it to `docs/tutorials/` directory

#### Scenario: How-to classification
- **WHEN** a document contains task-oriented steps, verification, and troubleshooting
- **THEN** the system classifies it as `how-to` quadrant
- **AND** maps it to `docs/how-to/` directory

#### Scenario: Explanation classification
- **WHEN** a document contains context, decisions, tradeoffs, and "why" content
- **THEN** the system classifies it as `explanation` quadrant
- **AND** maps it to `docs/explanation/` directory

#### Scenario: Reference classification
- **WHEN** a document contains API signatures, parameters, return types, and examples
- **THEN** the system classifies it as `reference` quadrant
- **AND** maps it to `docs/reference/` directory

### Requirement: Rule-based classification cascade
The system SHALL use a cascade of rules to classify documents, starting with file location heuristics.

#### Scenario: File location heuristic
- **WHEN** a file is in `examples/` directory
- **THEN** the system classifies it as `tutorial` (default)

#### Scenario: File name heuristic
- **WHEN** a file is named `README*`
- **THEN** the system classifies it as `tutorial` (default)

### Requirement: LLM fallback for ambiguous classification
The system SHALL use LLM classification when rule-based classification is ambiguous (confidence < 0.7).

#### Scenario: Ambiguous artifact
- **WHEN** a config file could be either reference (schema) or how-to (example)
- **THEN** the system invokes LLM classification with `--use-llm` flag
- **AND** stores the LLM result with confidence score

### Requirement: Handle hybrid documents (multi-quadrant)
The system SHALL support documents that serve multiple Diátaxis quadrants with primary classification.

#### Scenario: Multi-quadrant document
- **WHEN** a README.md contains tutorial steps, API reference, and project explanation
- **THEN** the system assigns primary quadrant (tutorial) and secondary quadrants (reference, explanation)
- **AND** stores classification in state file

### Requirement: Track classification history
The system SHALL maintain a history of classifications for each document.

#### Scenario: New classification
- **WHEN** a document is classified for the first time
- **THEN** the system creates a classification_history entry with date, quadrant, and reason

### Requirement: Enforce Diátaxis rules with soft thresholds
The system SHALL validate documentation against Diátaxis rules with configurable thresholds.

#### Scenario: Required sections missing
- **WHEN** a tutorial is missing required sections (prerequisites, steps)
- **AND** less than 70% of required sections are present
- **THEN** the system emits a WARNING
- **AND** allows the document to pass validation

#### Scenario: Forbidden element present
- **WHEN** a tutorial contains API signatures (forbidden in tutorial quadrant)
- **THEN** the system emits an ERROR
- **AND** fails validation

### Requirement: Tier-based enforcement strictness
The system SHALL apply different enforcement thresholds based on node importance tier.

#### Scenario: Tier 1 (CRITICAL) node
- **WHEN** a document is for a Tier 1 node (score >= 0.8)
- **THEN** the system uses 80% required sections threshold
- **AND** uses 120% max words threshold

#### Scenario: Tier 2 (IMPORTANT) node
- **WHEN** a document is for a Tier 2 node (score 0.5-0.8)
- **THEN** the system uses 70% required sections threshold
- **AND** uses 150% max words threshold

### Requirement: Implement ClassifierTool with classification rules
The system SHALL provide a ClassifierTool that implements Diátaxis classification using deterministic rules.

#### Scenario: ClassifierTool classifies deployment file
- **WHEN** ClassifierTool.execute() is called with file_path="Dockerfile"
- **THEN** the tool returns quadrant="how-to", confidence=0.95, source="name_heuristic"

### Requirement: Implement EnforcerTool with enforcement rules
The system SHALL provide an EnforcerTool that validates documents against Diátaxis rules.

#### Scenario: EnforcerTool validates tutorial
- **WHEN** EnforcerTool.execute() is called with doc_path and quadrant="tutorial"
- **THEN** the tool checks required sections (prerequisites, steps, what_you_learned)
- **AND** returns valid=true if >= 70% present, valid=false otherwise

### Requirement: Implement ValidationAgent for comprehensive validation
The system SHALL provide a ValidationAgent that composes EnforcerTool, CheckLinksTool, and ReadDocTool.

#### Scenario: ValidationAgent validates single doc
- **WHEN** ValidationAgent.run() is called with doc_path and quadrant
- **THEN** the agent reads doc, enforces rules, checks links
- **AND** returns AgentResult with validation report
