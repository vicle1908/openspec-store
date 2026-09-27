# shb-browser-cli Specification

## Purpose
Provides automated browser interactions, Chrome DevTools Protocol (CDP) session attach, and multi-format document extraction for Saigon - Hanoi Bank (SHB) workflows.

## Requirements

### Requirement: CDP Browser Attach and Session Persistence
The `shb-browser-cli` package SHALL support connecting to running browser instances via Chrome DevTools Protocol (CDP) and persisting authenticated session state across invocations.

#### Scenario: Attach to existing browser session
- **WHEN** an operator invokes the browser CLI with a remote debugging CDP URL
- **THEN** the CLI attaches to the active browser context without launching a new isolated browser instance

### Requirement: Document Extraction Pipeline
The system SHALL extract clean text and tabular data from PDF, DOCX, and web page formats, returning structured output suitable for agent consumption.

#### Scenario: PDF document text extraction
- **WHEN** a PDF file path or URL is supplied to the extraction command
- **THEN** the CLI extracts the text content with page number demarcations and outputs clean markdown

### Requirement: Command-Line Interface Entrypoint
The package SHALL provide an executable command-line interface named `shb-browser-cli` exposing commands for navigation, snapshot capture, and document parsing.

#### Scenario: Execution of snapshot command
- **WHEN** an operator runs `shb-browser-cli snapshot --url <target-url>`
- **THEN** the CLI renders the page, captures the DOM snapshot, and outputs the structured content
