# ECC Rules Policy

Source: `audit/raw-rules.csv` (19 dirs)

## TDT Repo Language Map

| Language | TDT Repos |
|---|---|
| Python | tdt-core, webhook-receiver, ai-review, agent-core, jira-* |
| Swift | poems-mobile3-ios |
| Kotlin | poems-mobile3-android |
| TypeScript | (web frontend if any) |
| React | (web frontend if any) |

## Rules Disposition Table

| rules_dir | language | classification | files | rationale |
|---|---|---|---|---|
| `angular` | angular | disabled-default:stack-irrelevant | 5 | Language angular not used in any TDT repo (5 files) |
| `arkts` | arkts | disabled-default:stack-irrelevant | 5 | Language arkts not used in any TDT repo (5 files) |
| `cpp` | cpp | disabled-default:stack-irrelevant | 5 | Language cpp not used in any TDT repo (5 files) |
| `csharp` | csharp | disabled-default:stack-irrelevant | 5 | Language csharp not used in any TDT repo (5 files) |
| `dart` | dart | disabled-default:stack-irrelevant | 5 | Language dart not used in any TDT repo (5 files) |
| `fsharp` | fsharp | disabled-default:stack-irrelevant | 5 | Language fsharp not used in any TDT repo (5 files) |
| `golang` | golang | disabled-default:stack-irrelevant | 5 | Language golang not used in any TDT repo (5 files) |
| `java` | java | disabled-default:stack-irrelevant | 5 | Language java not used in any TDT repo (5 files) |
| `perl` | perl | disabled-default:stack-irrelevant | 5 | Language perl not used in any TDT repo (5 files) |
| `php` | php | disabled-default:stack-irrelevant | 5 | Language php not used in any TDT repo (5 files) |
| `ruby` | ruby | disabled-default:stack-irrelevant | 5 | Language ruby not used in any TDT repo (5 files) |
| `rust` | rust | disabled-default:stack-irrelevant | 5 | Language rust not used in any TDT repo (5 files) |
| `web` | web | disabled-default:stack-irrelevant | 7 | Language web not used in any TDT repo (7 files) |
| `kotlin` | kotlin | surface | 5 | Language kotlin used in TDT repos (5 files) |
| `python` | python | surface | 6 | Language python used in TDT repos (6 files) |
| `react` | react | surface | 5 | Language react used in TDT repos (5 files) |
| `swift` | swift | surface | 5 | Language swift used in TDT repos (5 files) |
| `typescript` | typescript | surface | 5 | Language typescript used in TDT repos (5 files) |
| `common` | common | surface:common | 10 | Language-agnostic rules (10 files); useful for any TDT repo |

## Summary

Total: 19 rules dirs

- disabled-default:stack-irrelevant: 13
- surface: 5
- surface:common: 1
