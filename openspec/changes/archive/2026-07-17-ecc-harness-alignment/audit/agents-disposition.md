# ECC Agents Disposition

Source: `audit/raw-agents.csv` (64 entries)

| agent_name | bucket | classification | rule | rationale |
|---|---|---|---|---|
| `gan-evaluator` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | gan-evaluator not used |
| `gan-generator` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | gan-generator not used |
| `gan-planner` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | gan-planner not used |
| `homelab-architect` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | homelab-architect not used |
| `marketing-agent` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | marketing-agent not used |
| `network-architect` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | network-architect not used |
| `network-config-reviewer` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | network-config-reviewer not used |
| `network-troubleshooter` | cross-domain | disabled-default:domain-irrelevant | vertical not operated | network-troubleshooter not used |
| `a11y-architect` | cross-domain | keep-optional | TDT operating vertical | Matches TDT concern |
| `chief-of-staff` | cross-domain | keep-optional | TDT operating vertical | Matches TDT concern |
| `docs-lookup` | cross-domain | keep-optional | TDT operating vertical | Matches TDT concern |
| `healthcare-reviewer` | cross-domain | keep-optional | TDT operating vertical | Matches TDT concern |
| `django-build-resolver` | domain-reviewer | disabled-default:stack-irrelevant | language django | Not used in TDT repos |
| `django-reviewer` | domain-reviewer | disabled-default:stack-irrelevant | language django | Not used in TDT repos |
| `conversation-analyzer` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `cpp-build-resolver` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `cpp-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `csharp-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `dart-build-resolver` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `fastapi-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `flutter-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `fsharp-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `go-build-resolver` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `go-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `harmonyos-app-resolver` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `harness-optimizer` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `java-build-resolver` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `java-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `kotlin-build-resolver` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `kotlin-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `loop-operator` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `mle-reviewer` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `opensource-forker` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `opensource-packager` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `opensource-sanitizer` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `php-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `python-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `pytorch-build-resolver` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `react-build-resolver` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `react-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `rust-build-resolver` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `rust-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `seo-specialist` | domain-reviewer | keep-default | specialist agent | Available on demand |
| `swift-build-resolver` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `swift-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `typescript-reviewer` | domain-reviewer | keep-default | language used in TDT repos | Matches TDT repos |
| `architect` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `build-error-resolver` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `code-architect` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `code-explorer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `code-reviewer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `code-simplifier` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `comment-analyzer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `database-reviewer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `doc-updater` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `e2e-runner` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `performance-optimizer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `planner` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `pr-test-analyzer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `refactor-cleaner` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `security-reviewer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `silent-failure-hunter` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `tdd-guide` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |
| `type-design-analyzer` | generic-specialist | keep-default | generic specialist | Cross-cutting; always available |

## Summary

Total: 64 agents

- keep-default: 50
- disabled-default:domain-irrelevant: 8
- keep-optional: 4
- disabled-default:stack-irrelevant: 2
