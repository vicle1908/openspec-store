# Spec Delta

## Purpose

Define normative behavior for automated, fail-closed synchronization of workspace wiki pages, OpenSpec catalogs, and knowledge health matrices into Notion sub-pages via the Notion CLI.

## ADDED Requirements

### Requirement: Fail-closed credential and path sanitization

The synchronization engine SHALL sanitize all Markdown documents and generated tables before transmission to the Notion API. Any token matching known credential patterns MUST be replaced with `REDACTED`, and machine-specific home directory prefixes MUST be normalized to portable references.

#### Scenario: Sensitive tokens and secrets are redacted
- **WHEN** an input document contains an API key, bearer token, password, or sensitive environment variable assignment matching credential patterns
- **THEN** the transmitted content SHALL replace the value with `REDACTED`
- **AND** the unredacted credential SHALL NOT appear in Notion API payloads or log files

#### Scenario: User home paths are normalized
- **WHEN** an input document contains absolute local filesystem paths containing `/Users/androidteam/`
- **THEN** the transmitted content SHALL normalize the prefix to `~/Developer/` or relative paths

#### Scenario: Empty or corrupted input handled gracefully
- **WHEN** an input markdown file is 0 bytes or unreadable
- **THEN** the synchronizer SHALL record a warning
- **AND** SHALL NOT overwrite an existing Notion page with empty content

### Requirement: Idempotent content-addressed synchronization

The synchronization engine SHALL track the SHA-256 hash of each synchronized document within a local state manifest (`notion-sync-manifest.json`). Pages whose content hash matches the recorded state MUST NOT generate redundant Notion API write calls.

#### Scenario: Unchanged document yields fresh_noop
- **WHEN** a source document is evaluated and its current SHA-256 matches the manifest digest
- **THEN** the synchronizer SHALL skip the update
- **AND** log the status as `fresh_noop`

#### Scenario: Modified document triggers in-place edit
- **WHEN** a source document has a different SHA-256 than recorded in the manifest
- **THEN** the synchronizer SHALL invoke `ntn pages edit <page-id>` with the updated sanitized content
- **AND** update the manifest with the new SHA-256 upon successful response

#### Scenario: New document creates sub-page and updates manifest
- **WHEN** a source document has no recorded Notion page ID in the manifest
- **THEN** the synchronizer SHALL create a new page under the designated section parent via `ntn pages create --parent page:<section-id>`
- **AND** record the resulting page ID and SHA-256 digest in the manifest

### Requirement: Four-section hierarchical Notion organization

The synchronizer SHALL organize ecosystem knowledge under the Knowledge Root page (`3d7c4b21-deb4-8100-99c0-cfe30ef437ee`) into four distinct section sub-pages: `Ecosystem Concepts & Architecture`, `Ecosystem Component Entities`, `OpenSpec Architecture & Specifications`, and `Knowledge Health & Freshness Matrix`.

#### Scenario: Section parents exist or are bootstrapped
- **WHEN** the synchronizer executes
- **THEN** it SHALL verify that the 4 section sub-pages exist under the Knowledge Root
- **AND** if any section page is missing, it SHALL bootstrap the section page before publishing child documents

#### Scenario: Child documents map to correct section parent
- **WHEN** a document from `wiki/concepts/` is synchronized
- **THEN** it SHALL be placed as a child of `Ecosystem Concepts & Architecture`
- **AND** documents from `wiki/entities/` SHALL be placed under `Ecosystem Component Entities`

### Requirement: Hybrid execution and operational resilience

The synchronizer SHALL support both dry-run execution, targeted single-section execution, full manual execution, and automated non-interactive execution within the nightly knowledge refresh pipeline.

#### Scenario: Dry-run execution makes no network mutations
- **WHEN** the synchronizer is executed with the `--dry-run` flag
- **THEN** it SHALL compute content digests, identify required creates and updates, and print the planned operations
- **AND** it SHALL NOT execute `ntn pages create` or `ntn pages edit`

#### Scenario: Targeted section execution
- **WHEN** the synchronizer is executed with `--section concepts`
- **THEN** it SHALL evaluate and sync only documents within the concepts category
- **AND** skip documents in other sections

#### Scenario: Transient API failure retry and reporting
- **WHEN** the Notion API returns a transient error (e.g. rate limit HTTP 429 or network timeout)
- **THEN** the synchronizer SHALL log the failure with error classification
- **AND** exit with non-zero status without corrupting the local manifest
