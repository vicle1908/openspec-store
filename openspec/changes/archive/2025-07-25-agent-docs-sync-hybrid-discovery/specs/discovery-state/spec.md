## ADDED Requirements

### Requirement: Cache state in .docs-sync-state.yaml
The system SHALL store discovery results in `.docs-sync-state.yaml` committed to version control.

#### Scenario: State file created
- **WHEN** discovery runs for the first time
- **THEN** the system creates `.docs-sync-state.yaml` with all discovery sections
- **AND** the file is committed to git

#### Scenario: State file updated
- **WHEN** discovery runs and state file exists
- **THEN** the system updates the state file with new results
- **AND** preserves history sections (classification_history, removed_mappings)

### Requirement: Dual-key cache invalidation
The system SHALL invalidate cache using git commit hash and gitnexus/graphify manifest timestamps.

#### Scenario: Git commit changed
- **WHEN** the current git commit differs from `invalidation.git_commit`
- **THEN** the system re-runs discovery
- **AND** updates the state file with new results

#### Scenario: GitNexus index updated
- **WHEN** `gitnexus_status().indexed_at` is newer than `invalidation.gitnexus_indexed_at`
- **THEN** the system re-runs discovery
- **AND** updates structural analysis section

#### Scenario: Graphify graph rebuilt
- **WHEN** `graphify_manifest().built_at` is newer than `invalidation.graphify_built_at`
- **THEN** the system re-runs discovery
- **AND** updates community analysis section

#### Scenario: Cache fresh
- **WHEN** git commit matches and timestamps are not newer
- **THEN** the system uses cached state
- **AND** does not re-run discovery (unless `--force` flag)

### Requirement: Track structural changes
The system SHALL track which files have structural changes (ast_hash) vs cosmetic changes (mtime only).

#### Scenario: Structural change detected
- **WHEN** a file's ast_hash changes between gitnexus indexes
- **THEN** the system adds the file to `structural.file_changes`
- **AND** sets `change_type: "structural"`

#### Scenario: Cosmetic change only
- **WHEN** a file's mtime changes but ast_hash remains the same
- **THEN** the system does not add the file to `structural.file_changes`
- **AND** does not trigger documentation re-evaluation

### Requirement: Report documentation coverage gaps
The system SHALL report which Diátaxis quadrants are populated and which are missing.

#### Scenario: Coverage report generated
- **WHEN** discovery completes
- **THEN** the state file contains `diataxis` section with coverage percentages
- **AND** lists existing and recommended docs per quadrant

#### Scenario: Isolated nodes reported
- **WHEN** graphify identifies isolated nodes (<= 1 connection)
- **THEN** the system adds them to `doc_gaps.isolated_nodes`
- **AND** prioritizes by importance score (edges + centrality)

### Requirement: Detect orphaned documentation
The system SHALL detect documentation files that exist but have no source mapping.

#### Scenario: Orphaned doc detected
- **WHEN** a `.md` file exists in `docs/` but no source file maps to it
- **THEN** the system adds it to `orphaned_docs`
- **AND** sets recommendation to `review_or_remove`

#### Scenario: Orphaned doc with no references
- **WHEN** an orphaned doc has not been referenced in 30+ days
- **THEN** the system sets recommendation to `archive_or_remove`

### Requirement: Track cross-references between documents
The system SHALL track links between documents across Diátaxis quadrants.

#### Scenario: Cross-reference detected
- **WHEN** `tutorials/getting-started.md` links to `reference/cli.md`
- **THEN** the system adds an entry to `cross_references`
- **AND** validates that the target exists

#### Scenario: Broken cross-reference
- **WHEN** a cross-reference points to a non-existent document
- **THEN** the system marks `valid: false`
- **AND** adds a warning to the validation report

### Requirement: Track removed mappings
The system SHALL preserve history of source files that were removed from mappings.

#### Scenario: Source file removed
- **WHEN** a source file is deleted from the repository
- **THEN** the system moves its mapping to `removed_mappings`
- **AND** records the removal date and original doc target

#### Scenario: Mapping restored
- **WHEN** a removed source file is re-added
- **THEN** the system creates a new mapping entry
- **AND** does not restore the old removed_mappings entry

### Requirement: State file is human-readable
The system SHALL store state in YAML format that is easy to read and debug.

#### Scenario: State file inspection
- **WHEN** a user opens `.docs-sync-state.yaml`
- **THEN** the file is formatted YAML with clear section headers
- **AND** includes comments explaining each section

#### Scenario: State file diff
- **WHEN** discovery runs and state file changes
- **THEN** the git diff shows clear, readable changes
- **AND** does not show noise from timestamp-only updates

### Requirement: Implement StateTool with atomic writes
The system SHALL provide a StateTool that manages state file operations with atomic writes.

#### Scenario: StateTool atomic write
- **WHEN** StateTool.execute() is called with action="save"
- **THEN** the tool writes to .docs-sync-state.yaml.tmp first
- **AND** renames to .docs-sync-state.yaml (atomic on POSIX)
- **AND** returns ToolResult(success=True, bytes_written=N)

#### Scenario: StateTool preserves history
- **WHEN** StateTool.execute() is called with action="save" and new state
- **THEN** the tool preserves classification_history and removed_mappings from old state
- **AND** appends new entries to history sections

#### Scenario: StateTool checks staleness
- **WHEN** StateTool.execute() is called with action="check_stale"
- **THEN** the tool runs `git rev-parse HEAD` to get current commit
- **AND** reads .gitnexus/meta.json for indexed_at timestamp
- **AND** reads graphify-out/manifest.json for built_at timestamp
- **AND** compares with state.invalidation values
- **AND** returns ToolResult(success=True, output={is_stale: bool, reasons: list})

### Requirement: Implement GitNexusLoaderTool with hash comparison
The system SHALL provide a GitNexusLoaderTool that loads gitnexus.json and compares file hashes.

#### Scenario: GitNexusLoaderTool loads file hashes
- **WHEN** GitNexusLoaderTool.execute() is called with repo_root
- **THEN** the tool reads .gitnexus/gitnexus.json
- **AND** returns ToolResult(success=True, output={file_hashes: dict, meta: dict})

#### Scenario: GitNexusLoaderTool compares hashes
- **WHEN** GitNexusLoaderTool.compare_hashes(old_hashes, new_hashes) is called
- **THEN** the tool returns list of files where ast_hash changed
- **AND** marks each as change_type="structural" or "cosmetic"

#### Scenario: GitNexusLoaderTool loads meta stats
- **WHEN** GitNexusLoaderTool.execute() is called with repo_root
- **THEN** the tool reads .gitnexus/meta.json
- **AND** returns ToolResult(success=True, output={stats: {files, symbols, relationships, communities}})

### Requirement: Implement GraphifyLoaderTool with report parsing
The system SHALL provide a GraphifyLoaderTool that loads graphify manifest.json and parses GRAPH_REPORT.md.

#### Scenario: GraphifyLoaderTool loads manifest
- **WHEN** GraphifyLoaderTool.execute() is called with repo_root
- **THEN** the tool reads graphify-out/manifest.json
- **AND** returns ToolResult(success=True, output={stats: {files, nodes, edges, communities}})

#### Scenario: GraphifyLoaderTool parses god nodes
- **WHEN** GraphifyLoaderTool.execute() is called with repo_root
- **THEN** the tool reads GRAPH_REPORT.md and extracts "God Nodes" section
- **AND** returns list of nodes with edge counts >= 10

#### Scenario: GraphifyLoaderTool parses isolated nodes
- **WHEN** GraphifyLoaderTool.execute() is called with repo_root
- **THEN** the tool reads GRAPH_REPORT.md and extracts "Knowledge Gaps" section
- **AND** returns list of isolated nodes with <= 1 connection

#### Scenario: GraphifyLoaderTool parses communities
- **WHEN** GraphifyLoaderTool.execute() is called with repo_root
- **THEN** the tool reads GRAPH_REPORT.md and extracts "Communities" section
- **AND** returns list of communities with name, nodes, cohesion, god_nodes
