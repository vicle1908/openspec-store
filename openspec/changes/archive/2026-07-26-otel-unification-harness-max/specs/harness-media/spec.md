## ADDED Requirements

### Requirement: Media store utilities SHALL be available for media offloading
The `pydantic_ai_harness.media` module SHALL provide `DiskMediaStore`, `S3MediaStore`, `SqliteMediaStore`, `externalize_media`, and `restore_media` for offloading `BinaryContent` to content-addressed stores. These are utility classes, NOT a drop-in capability class.

#### Scenario: DiskMediaStore stores binary content
- **WHEN** `DiskMediaStore(directory=Path("/tmp/media"))` is instantiated
- **THEN** it SHALL implement the `MediaStore` protocol and store binary content on disk with content-addressed keys

#### Scenario: S3MediaStore stores binary content
- **WHEN** `S3MediaStore(...)` is instantiated with S3-compatible storage parameters
- **THEN** it SHALL implement the `MediaStore` protocol and store binary content in S3/MinIO

### Requirement: Media offloading SHALL be deferred to a future change
Since there is no built-in `Media` capability class in harness v0.10.0, media offloading SHALL NOT be automatically applied in this change. A custom Media capability using `externalize_media` and a `MediaStore` implementation SHALL be built in a future change.

#### Scenario: Media offloading not applied
- **WHEN** the agent processes tool outputs containing large `BinaryContent`
- **THEN** media offloading SHALL NOT be automatically applied in this change

### Requirement: MediaSettings SHALL be added for future use
`MediaSettings` with `content_store_url: str = ""` SHALL be added to `foundation/settings.py` to prepare for the future custom Media capability implementation.

#### Scenario: Media settings configured
- **WHEN** `MEDIA_CONTENT_STORE_URL=s3://bucket/content` is set
- **THEN** `Settings.media.content_store_url` SHALL contain the URL
