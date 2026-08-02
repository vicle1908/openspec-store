# ECC Commands Disposition

Source: `audit/raw-commands.csv` (84 entries)

| command | classification | tdt_workflow | rationale | notes |
|---|---|---|---|---|
| `/aside` | keep-optional | n/a | No immediate TDT overlap | description: Answer a quick side question without interrupting or losing context |
| `/auto-update` | keep-optional | n/a | Helper command | description: Pull the latest ECC repo changes and reinstall the current managed  |
| `/build-fix` | keep-optional | n/a | Trigger-point command; available on demand | description: Detect the project build system and incrementally fix build/type er |
| `/checkpoint` | keep-optional | n/a | Helper command | description: Create, verify, or list workflow checkpoints after running verifica |
| `/code-review` | keep-optional | n/a | Trigger-point command; available on demand | description: Code review — local uncommitted changes or GitHub PR (pass PR numbe |
| `/cost-report` | keep-optional | n/a | Helper command | description: Generate a local Claude Code cost report from a cost-tracker SQLite |
| `/cpp-build` | keep-optional | n/a | Helper command | description: Fix C++ build errors, CMake issues, and linker problems incremental |
| `/cpp-review` | keep-optional | n/a | Helper command | description: Comprehensive C++ code review for memory safety, modern C++ idioms, |
| `/cpp-test` | keep-optional | n/a | Helper command | description: Enforce TDD workflow for C++. Write GoogleTest tests first, then im |
| `/ecc-guide` | keep-optional | n/a | Helper command | description: Navigate ECC's current agents, skills, commands, hooks, install pro |
| `/evolve` | keep-optional | n/a | No immediate TDT overlap | name: evolve |
| `/fastapi-review` | keep-optional | n/a | Helper command | description: Review a FastAPI application for architecture, async correctness, d |
| `/feature-dev` | keep-optional | n/a | Helper command | description: Guided feature development with codebase understanding and architec |
| `/flutter-build` | keep-optional | n/a | Helper command | description: Fix Dart analyzer errors and Flutter build failures incrementally.  |
| `/flutter-review` | keep-optional | n/a | Helper command | description: Review Flutter/Dart code for idiomatic patterns, widget best practi |
| `/flutter-test` | keep-optional | n/a | Helper command | description: Run Flutter/Dart tests, report failures, and incrementally fix test |
| `/gan-build` | keep-optional | n/a | Helper command | description: Run a generator/evaluator build loop for implementation tasks with  |
| `/gan-design` | keep-optional | n/a | Helper command | description: Run a generator/evaluator design loop for frontend or visual work w |
| `/go-build` | keep-optional | n/a | Helper command | description: Fix Go build errors, go vet warnings, and linter issues incremental |
| `/go-review` | keep-optional | n/a | Helper command | description: Comprehensive Go code review for idiomatic patterns, concurrency sa |
| `/go-test` | keep-optional | n/a | Helper command | description: Enforce TDD workflow for Go. Write table-driven tests first, then i |
| `/gradle-build` | keep-optional | n/a | Helper command | description: Fix Gradle build errors for Android and KMP projects |
| `/harness-audit` | keep-optional | n/a | Trigger-point command; available on demand | description: Run a deterministic repository harness audit and return a prioritiz |
| `/hookify` | keep-optional | n/a | No immediate TDT overlap | description: Create hooks to prevent unwanted behaviors from conversation analys |
| `/hookify-configure` | keep-optional | n/a | Helper command | description: Enable or disable hookify rules interactively |
| `/hookify-help` | keep-optional | n/a | No immediate TDT overlap | description: Get help with the hookify system |
| `/hookify-list` | keep-optional | n/a | Helper command | description: List all configured hookify rules |
| `/instinct-export` | keep-optional | n/a | No immediate TDT overlap | name: instinct-export |
| `/instinct-import` | keep-optional | n/a | No immediate TDT overlap | name: instinct-import |
| `/instinct-status` | keep-optional | n/a | No immediate TDT overlap | name: instinct-status |
| `/jira` | keep-optional | n/a | Helper command | description: Retrieve a Jira ticket, analyze requirements, update status, or add |
| `/kotlin-build` | keep-optional | n/a | Helper command | description: Fix Kotlin/Gradle build errors, compiler warnings, and dependency i |
| `/kotlin-review` | keep-optional | n/a | Helper command | description: Comprehensive Kotlin code review for idiomatic patterns, null safet |
| `/kotlin-test` | keep-optional | n/a | Helper command | description: Enforce TDD workflow for Kotlin. Write Kotest tests first, then imp |
| `/learn` | keep-optional | n/a | Helper command | description: Extract reusable patterns from the current session and save them as |
| `/learn-eval` | keep-optional | n/a | Helper command | description: "Extract reusable patterns from the session, self-evaluate quality  |
| `/loop-start` | keep-optional | n/a | Trigger-point command; available on demand | description: Start a managed autonomous loop pattern with safety defaults and ex |
| `/loop-status` | keep-optional | n/a | Trigger-point command; available on demand | description: Inspect active loop state, progress, failure signals, and recommend |
| `/marketing-campaign` | keep-optional | n/a | Helper command | description: Plan and execute a full marketing campaign. Accepts a product brief |
| `/model-route` | keep-optional | n/a | Trigger-point command; available on demand | description: Recommend the best model tier for the current task based on complex |
| `/multi-backend` | keep-optional | n/a | Trigger-point command; available on demand | description: Run a backend-focused multi-model workflow for APIs, algorithms, da |
| `/multi-execute` | keep-optional | n/a | Trigger-point command; available on demand | description: Execute a multi-model implementation plan while preserving Claude a |
| `/multi-frontend` | keep-optional | n/a | Trigger-point command; available on demand | description: Run a frontend-focused multi-model workflow for components, layouts |
| `/multi-plan` | keep-optional | n/a | Trigger-point command; available on demand | description: Create a multi-model implementation plan without modifying producti |
| `/multi-workflow` | keep-optional | n/a | Trigger-point command; available on demand | description: Run a full multi-model development workflow with research, planning |
| `/orch-add-feature` | keep-optional | n/a | Helper command | description: Orchestrate building a brand-new feature end to end — research, pla |
| `/orch-build-mvp` | keep-optional | n/a | Helper command | description: Orchestrate bootstrapping a working MVP from a design/spec doc — in |
| `/orch-change-feature` | keep-optional | n/a | Helper command | description: Orchestrate altering an existing, working feature to new desired be |
| `/orch-fix-defect` | keep-optional | n/a | Helper command | description: Orchestrate fixing a bug — reproduce it as a failing regression tes |
| `/orch-refine-code` | keep-optional | n/a | Helper command | description: Orchestrate a behavior-preserving refactor — confirm tests green, r |
| `/plan` | keep-optional | n/a | Trigger-point command; available on demand | description: Restate requirements, assess risks, and create step-by-step impleme |
| `/plan-prd` | keep-optional | n/a | Helper command | description: "Generate a lean, problem-first PRD and hand off to /plan for imple |
| `/pm2` | keep-optional | n/a | Trigger-point command; available on demand | description: Analyze a project and generate PM2 service commands for detected fr |
| `/pr` | keep-optional | n/a | Helper command | description: "Create a GitHub PR from current branch with unpushed commits — dis |
| `/project-init` | keep-optional | n/a | Helper command | description: Detect a project's stack and produce a dry-run ECC onboarding plan  |
| `/projects` | keep-optional | n/a | Trigger-point command; available on demand | name: projects |
| `/promote` | keep-optional | n/a | No immediate TDT overlap | name: promote |
| `/prp-commit` | keep-optional | n/a | No immediate TDT overlap | description: "Quick commit with natural language file targeting — describe what  |
| `/prp-implement` | keep-optional | n/a | Helper command | description: Execute an implementation plan with rigorous validation loops |
| `/prp-plan` | keep-optional | n/a | Helper command | description: Create comprehensive feature implementation plan with codebase anal |
| `/prp-pr` | keep-optional | n/a | Helper command | description: "Create a GitHub PR from current branch with unpushed commits — dis |
| `/prp-prd` | keep-optional | n/a | No immediate TDT overlap | description: "Interactive PRD generator - problem-first, hypothesis-driven produ |
| `/prune` | keep-optional | n/a | No immediate TDT overlap | name: prune |
| `/python-review` | keep-optional | n/a | Helper command | description: Comprehensive Python code review for PEP 8 compliance, type hints,  |
| `/quality-gate` | keep-optional | n/a | Helper command | description: Run the ECC formatter quality gate for a single file and report rem |
| `/react-build` | keep-optional | n/a | Helper command | description: Fix React build failures (Vite, webpack, Next.js, CRA, Parcel, esbu |
| `/react-review` | keep-optional | n/a | Helper command | description: Comprehensive React/JSX code review for hook correctness, render pe |
| `/react-test` | keep-optional | n/a | Helper command | description: Enforce TDD workflow for React. Write React Testing Library tests f |
| `/refactor-clean` | keep-optional | n/a | Trigger-point command; available on demand | description: Safely identify and remove dead code with verification after each c |
| `/review-pr` | keep-optional | n/a | Helper command | description: Comprehensive PR review using specialized agents |
| `/rust-build` | keep-optional | n/a | Helper command | description: Fix Rust build errors, borrow checker issues, and dependency proble |
| `/rust-review` | keep-optional | n/a | Helper command | description: Comprehensive Rust code review for ownership, lifetimes, error hand |
| `/rust-test` | keep-optional | n/a | Helper command | description: Enforce TDD workflow for Rust. Write tests first, then implement. V |
| `/santa-loop` | keep-optional | n/a | Helper command | description: Adversarial dual-review convergence loop — two independent model re |
| `/security-scan` | keep-optional | n/a | No immediate TDT overlap | description: Run AgentShield against agent, hook, MCP, permission, and secret su |
| `/sessions` | keep-optional | n/a | Helper command | description: Manage Claude Code session history, aliases, and session metadata. |
| `/setup-pm` | keep-optional | n/a | Trigger-point command; available on demand | description: Configure your preferred package manager (npm/pnpm/yarn/bun) |
| `/skill-create` | keep-optional | n/a | Helper command | name: skill-create |
| `/skill-health` | keep-optional | n/a | Trigger-point command; available on demand | name: skill-health |
| `/test-coverage` | keep-optional | n/a | Helper command | description: Analyze coverage, identify gaps, and generate missing tests toward  |
| `/resume-session` | redundant-to-tdt-skill | recall (tdt session restore) | TDT has equivalent (recall (tdt session restore)) | description: Load the most recent session file from ~/.claude/session-data/ and  |
| `/save-session` | redundant-to-tdt-skill | recall (tdt session saving) | TDT has equivalent (recall (tdt session saving)) | description: Save current session state to a dated file in ~/.claude/session-dat |
| `/update-codemaps` | redundant-to-tdt-skill | doc-updater (do not auto-mutate in TDT repos) | TDT has equivalent (doc-updater (do not auto-mutate in TDT repos)) | description: Scan project structure and generate token-lean architecture codemap |
| `/update-docs` | redundant-to-tdt-skill | doc-updater (do not auto-mutate in TDT repos) | TDT has equivalent (doc-updater (do not auto-mutate in TDT repos)) | description: Sync documentation from source-of-truth files such as scripts, sche |

## Summary

Total: 84 commands

- keep-optional: 80
- redundant-to-tdt-skill: 4
