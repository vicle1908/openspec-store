# Spec Delta

## ADDED Requirements

### Requirement: Upgrade endpoint gate SHALL verify Muse Code catalog routes under opt-out catalog authentication

During `~/Omniroute/scripts/update.sh` Gate 8 (`endpoints`), `/v1/muse-code/models` and `/muse-code/models` SHALL be validated under the configured opt-out catalog authentication policy (`requireAuthForModels`) rather than requiring unauthenticated static catalog responses.

#### Scenario: Gate 8 validates Muse Code catalog routes when catalog authentication is enabled or disabled
- **WHEN** `~/Omniroute/scripts/update.sh` runs Gate 8 (`endpoints`) against the deployed OmniRoute container
- **THEN** Gate 8 SHALL accept anonymous HTTP `200` with a parsed JSON `data` array containing `id === "muse-spark-1.3"` when catalog authentication is disabled
- **AND** when anonymous `GET /v1/muse-code/models` or `GET /muse-code/models` returns HTTP `401` (catalog authentication enabled), Gate 8 SHALL execute an authenticated in-container probe using the decrypted active API key from `/app/data/storage.sqlite` and require HTTP `200` with a parsed JSON `data` array containing `id === "muse-spark-1.3"` on both routes
- **AND** if either route returns an unexpected status or omits `muse-spark-1.3` from `data[]`, Gate 8 SHALL fail closed and retain `~/.omniroute/update-available`
