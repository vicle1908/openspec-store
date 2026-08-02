# Spec delta for android-plugin

This delta is applied to
`openspec/changes/unified-code-daily-scan/specs/android-plugin/spec.md`
when the `collapse-feature-routing` change is archived.

## MODIFIED Requirements

### Requirement: Android Path-Based Tab Resolution

The system SHALL resolve the spreadsheet tab for an Android finding
from `finding.feature` using `FEATURE_TAB_MAP`. The system SHALL NOT
maintain a separate, plugin-local feature-to-tab mapping. The set of
tabs is the cross-platform unified taxonomy: `Auth`, `Home`,
`WatchList`, `Market`, `Trade`, `Community`, `Me/Settings`,
`Deposit/Withdraw`, `Form`, `Common`, `Others`. Any unmapped feature
SHALL resolve to `Others`.

#### Scenario: Known module path

- **WHEN** a finding's `feature` is `Trade` (resolved by the
  platform-aware `FeatureResolver` during scan)
- **THEN** `resolve_finding_tab` SHALL return `"Trade"`

#### Scenario: Resource file with feature=Common

- **WHEN** a finding's `file_path` is
  `PoemsUIComponents/src/main/res/values/styles.xml` and
  `feature` is `Common`
- **THEN** `resolve_finding_tab` SHALL return `"Common"`. The
  resource-file extension check is a last-resort fallback and SHALL
  NOT mask the resolver's answer.

#### Scenario: Unknown module path

- **WHEN** a finding's `feature` is `Others` (no module prefix
  matched by the resolver)
- **THEN** `resolve_finding_tab` SHALL return `"Others"`. There is
  no `Infrastructure` tab; the system SHALL NOT route to a
  fabricated tab name.

## REMOVED Requirements

### Requirement: Android 11 Infrastructure Tabs

**Reason:** The implementation never built the 11 infrastructure
tabs (`Adapter`, `Ui`, `CounterDetail`, `Network`, `Extensions`,
`Utils`, `Viewmodels`, `Dashboard`, `Infrastructure`, `Local`,
`App`). The cross-platform unified taxonomy was the explicit Phase 9
goal (see VERIFICATION.md:16: "Cross-platform: Both platforms use
identical 10-feature taxonomy") and the iOS plugin spec already
commits to the 10+1 taxonomy. The phantom infrastructure tabs are
removed from the Android spec to match the implementation and the
iOS spec.

**Migration:** Any operator who relied on the
`Infrastructure`-as-fallback contract should route unmapped findings
to the `Others` tab. The `feature_to_tab` mapping already does this
when the feature is the empty string or an unmapped value.
