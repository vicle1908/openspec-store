# code-scan-android-rules Specification

## Purpose
Defines the code scan android rules contract: code-scan-android-rules contract SHALL declare the delta for this change. (governing requirement: Android code-daily-scan SHALL distinguish real cleartext HTTP from XML namespace false positives).


## Requirements
### Requirement: Android code-daily-scan SHALL distinguish real cleartext HTTP from XML namespace false positives

The code-scan-android-rules contract SHALL declare the delta for this change. The pre-existing capability surface is preserved; this delta is the canonical OpenSpec declaration. Operators SHALL follow this contract for code-scan-android-rules work.

#### Scenario: code-scan-android-rules is implemented per the contract above

The code-scan-android-rules runtime SHALL pass the contract above when the implementation is invoked through the supported entry points.

