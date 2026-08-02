## ADDED Requirements

### Requirement: Extract text from downloaded documents to agent-readable markdown
The skill SHALL provide a post-processing step that converts downloaded binary documents (PDF, DOCX) into markdown files suitable for agent consumption.

#### Scenario: Extract PDF to markdown
- **WHEN** agent has a downloaded PDF file and invokes the extraction helper
- **THEN** the system produces a companion `.md` file with page-by-page text content, preserving headings, lists, and table-like structures

#### Scenario: Extract DOCX to markdown
- **WHEN** agent has a downloaded .docx file and invokes the extraction helper with pandoc or python-docx
- **THEN** the system produces a companion `.md` file with structured content including tables, headings, and lists

#### Scenario: Extraction output placed alongside source
- **WHEN** extraction completes
- **THEN** the `.md` file is written to the same directory as the source binary with a matching filename (e.g., `URS_v1.3.pdf` → `URS_v1.3.md`)

#### Scenario: Extraction includes metadata header
- **WHEN** the `.md` file is generated
- **THEN** it includes a header with: document title, source filename, page count, and extraction date

### Requirement: Support URS document registration in docs/urs/
The skill SHALL document the convention for storing URS documents locally and registering them in `docs/urs/INDEX.md` for agent discovery.

#### Scenario: New URS document added
- **WHEN** a new URS document is downloaded or placed in `docs/urs/<feature>/`
- **THEN** the agent creates a companion `.md` extraction and updates `docs/urs/INDEX.md` with: Jira epic link, source URL, local paths, page count, version, and scope summary

#### Scenario: URS document updated
- **WHEN** a newer version of an existing URS is downloaded
- **THEN** the agent overwrites the binary, re-runs extraction, and updates INDEX.md with new version/date

### Requirement: Extraction uses bundled Python runtime
The skill SHALL use the workspace bundled Python (`/Users/lekhanhvinh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`) with `pypdf` for PDF extraction, avoiding external tool dependencies.

#### Scenario: pypdf available in bundled runtime
- **WHEN** agent invokes PDF extraction
- **THEN** it uses the bundled Python with `pypdf.PdfReader` to extract text page-by-page

#### Scenario: DOCX extraction fallback
- **WHEN** agent needs to extract a .docx and `pandoc` is not installed
- **THEN** it uses `python-docx` via the bundled Python, or instructs user to install pandoc via `brew install pandoc`

### Requirement: Quality validation of extracted text
The skill SHALL validate that extraction produced usable content before registering the document.

#### Scenario: Extraction produces readable text
- **WHEN** extraction completes and the output contains >100 non-whitespace characters per page on average
- **THEN** the extraction is considered successful

#### Scenario: Extraction produces empty or garbled output
- **WHEN** extraction produces <100 characters per page (indicating scanned/image PDF)
- **THEN** the skill warns "PDF appears to be image-based; text extraction failed" and suggests OCR alternatives or manual .docx download
