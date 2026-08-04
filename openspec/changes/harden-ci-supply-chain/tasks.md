## 1. Pin all actions to SHAs

- [ ] 1.1 Resolve current SHA for each action used across all workflows
- [ ] 1.2 Update verify.yml — pin all actions with version comments
- [ ] 1.3 Update k8s-deploy.yaml — pin all actions with version comments
- [ ] 1.4 Update deployment-validation.yml — pin all actions
- [ ] 1.5 Update integration.yml — pin all actions
- [ ] 1.6 Update lgtm-e2e.yml — pin all actions
- [ ] 1.7 Update release-evidence.yml — pin all actions
- [ ] 1.8 Update gitops-reconcile.yml — pin all actions
- [ ] 1.9 Update gitops-rollback.yml — pin all actions

## 2. Add OpenSSF Scorecard workflow

- [ ] 2.1 Create .github/workflows/scorecard.yml
- [ ] 2.2 Configure with weekly schedule + push to main
- [ ] 2.3 Set up SARIF upload to GitHub Security tab

## 3. Add gitleaks secret scanning

- [ ] 3.1 Add gitleaks step to verify.yml (CI gate)

## 4. Add go mod verify

- [ ] 4.1 Add go mod verify step to verify.yml

## 5. Shorten artifact retention

- [ ] 5.1 Reduce all retention-days: 90 to 30
- [ ] 5.2 Reduce retention-days: 365 to 30

## 6. Validate

- [ ] 6.1 actionlint passes on all workflows
- [ ] 6.2 CI passes on PR
- [ ] 6.3 CI passes on main
